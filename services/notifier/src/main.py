"""
Notifier Service - Sistema de Alertas Comunitarias Verificadas
Consume eventos confirmados y envia notificaciones a usuarios suscritos
"""
import os
import json
import time
import asyncio
import psycopg2
from psycopg2.extras import RealDictCursor
import pika
import structlog
from telegram_client import TelegramClient

# Configurar logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Configuracion
DATABASE_URL = os.getenv('DATABASE_URL')
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://sacv:password@rabbitmq:5672')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

class NotifierService:
    """Servicio de notificaciones"""
    
    def __init__(self):
        self.db_conn = None
        self.rabbitmq_conn = None
        self.channel = None
        self.telegram_client = None
        
    def connect_db(self):
        """Conectar a PostgreSQL con retry"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.db_conn = psycopg2.connect(DATABASE_URL)
                logger.info("database_connected", attempt=attempt + 1)
                return
            except Exception as e:
                logger.warning("database_connection_retry",
                             attempt=attempt + 1,
                             error=str(e))
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
    
    def connect_rabbitmq(self):
        """Conectar a RabbitMQ con retry"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                params = pika.URLParameters(RABBITMQ_URL)
                self.rabbitmq_conn = pika.BlockingConnection(params)
                self.channel = self.rabbitmq_conn.channel()
                
                # Declarar queue
                self.channel.queue_declare(queue='confirmed_events', durable=True)
                
                logger.info("rabbitmq_connected", attempt=attempt + 1)
                return
            except Exception as e:
                logger.warning("rabbitmq_connection_retry",
                             attempt=attempt + 1,
                             error=str(e))
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
    
    async def init_telegram(self):
        """Inicializar cliente de Telegram"""
        if not TELEGRAM_BOT_TOKEN:
            logger.error("telegram_token_missing")
            raise ValueError("TELEGRAM_BOT_TOKEN no configurado")
        
        self.telegram_client = TelegramClient(TELEGRAM_BOT_TOKEN)
        
        # Probar conexion
        connected = await self.telegram_client.test_connection()
        if not connected:
            raise Exception("No se pudo conectar con Telegram")
    
    def get_subscriptions(self, event):
        """Obtener suscripciones activas para el evento"""
        cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
        try:
            # Filtrar por tipo y zona
            cursor.execute("""
                SELECT s.subscription_id, s.user_id, s.telegram_chat_id, u.username
                FROM subscriptions s
                JOIN users u ON s.user_id = u.user_id
                WHERE s.active = true
                  AND (s.event_type = %s OR s.event_type IS NULL)
                  AND (s.zone = %s OR s.zone IS NULL)
            """, (event.get('type'), event.get('zone')))
            
            subscriptions = cursor.fetchall()
            
            logger.info("subscriptions_found",
                       count=len(subscriptions),
                       event_type=event.get('type'),
                       zone=event.get('zone'))
            
            return [dict(sub) for sub in subscriptions]
            
        except Exception as e:
            logger.error("get_subscriptions_failed", error=str(e))
            return []
        finally:
            cursor.close()
    
    def save_notification(self, subscription_id, event_id, status, error_message=None):
        """Guardar registro de notificacion"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO notifications (subscription_id, event_id, status, error_message)
                VALUES (%s, %s, %s, %s)
            """, (subscription_id, event_id, status, error_message))
            
            self.db_conn.commit()
            
            logger.info("notification_saved",
                       subscription_id=subscription_id,
                       status=status)
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error("save_notification_failed", error=str(e))
        finally:
            cursor.close()
    
    async def notify_subscribers(self, event):
        """Notificar a todos los suscriptores del evento"""
        event_id = event.get('event_id')
        subscriptions = self.get_subscriptions(event)
        
        if not subscriptions:
            logger.info("no_subscriptions_found", event_id=event_id)
            return
        
        success_count = 0
        failed_count = 0
        
        for subscription in subscriptions:
            subscription_id = str(subscription['subscription_id'])
            chat_id = subscription['telegram_chat_id']
            
            if not chat_id:
                logger.warning("no_chat_id", subscription_id=subscription_id)
                continue
            
            try:
                # Enviar notificacion
                sent = await self.telegram_client.send_notification(chat_id, event)
                
                if sent:
                    self.save_notification(subscription_id, event_id, 'sent')
                    success_count += 1
                else:
                    self.save_notification(subscription_id, event_id, 'failed', 'Send failed')
                    failed_count += 1
                
                # Delay para evitar rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error("notification_error",
                           subscription_id=subscription_id,
                           error=str(e))
                self.save_notification(subscription_id, event_id, 'failed', str(e))
                failed_count += 1
        
        logger.info("notifications_completed",
                   event_id=event_id,
                   success=success_count,
                   failed=failed_count)
    
    def callback(self, ch, method, properties, body):
        """Callback para procesar mensajes de la queue"""
        try:
            event = json.loads(body)
            event_id = event.get('event_id')
            
            logger.info("processing_confirmed_event", event_id=event_id)
            
            # Notificar suscriptores (async)
            asyncio.run(self.notify_subscribers(event))
            
            # Acknowledge
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error("callback_error", error=str(e))
            # No requeue para evitar loops
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def run(self):
        """Iniciar servicio"""
        logger.info("notifier_service_starting")
        
        # Conectar a servicios
        self.connect_db()
        self.connect_rabbitmq()
        
        # Inicializar Telegram
        asyncio.run(self.init_telegram())
        
        # Configurar consumidor
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='confirmed_events',
            on_message_callback=self.callback
        )
        
        logger.info("waiting_for_confirmed_events")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("notifier_service_stopping")
            self.channel.stop_consuming()
        finally:
            if self.rabbitmq_conn:
                self.rabbitmq_conn.close()
            if self.db_conn:
                self.db_conn.close()

if __name__ == "__main__":
    service = NotifierService()
    service.run()
