"""
Verifier Service - Sistema de Alertas Comunitarias Verificadas
Consume eventos normalizados, aplica reglas de scoring y determina estado
"""
import os
import json
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import pika
import structlog
from rules import VerificationRules

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

class VerifierService:
    """Servicio de verificacion de eventos"""
    
    def __init__(self):
        self.db_conn = None
        self.rabbitmq_conn = None
        self.channel = None
        self.rules = None
        
    def connect_db(self):
        """Conectar a PostgreSQL con retry"""
        max_retries = 5
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.db_conn = psycopg2.connect(DATABASE_URL)
                logger.info("database_connected", attempt=attempt + 1)
                
                # Inicializar reglas con conexion DB
                self.rules = VerificationRules(self.db_conn)
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
                
                # Declarar queues
                self.channel.queue_declare(queue='normalized_events', durable=True)
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
    
    def update_event_verification(self, event_id, score, status):
        """Actualizar score y status del evento en BD"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                UPDATE events
                SET score = %s,
                    status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE event_id = %s
                RETURNING event_id
            """, (score, status, event_id))
            
            result = cursor.fetchone()
            self.db_conn.commit()
            
            if result:
                logger.info("event_updated",
                           event_id=event_id,
                           score=score,
                           status=status)
                return True
            else:
                logger.warning("event_not_found", event_id=event_id)
                return False
                
        except Exception as e:
            self.db_conn.rollback()
            logger.error("update_failed", error=str(e))
            return False
        finally:
            cursor.close()
    
    def publish_confirmed(self, event):
        """Publicar evento confirmado a queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='confirmed_events',
                body=json.dumps(event, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info("confirmed_event_published", event_id=event.get('event_id'))
        except Exception as e:
            logger.error("publish_failed", error=str(e))
    
    def verify_event(self, event):
        """Verificar evento aplicando reglas"""
        try:
            event_id = event.get('event_id')
            
            logger.info("verifying_event", event_id=event_id)
            
            # Calcular score
            score = self.rules.calculate_score(event)
            
            # Determinar status
            status = self.rules.determine_status(score)
            
            # Actualizar en BD
            updated = self.update_event_verification(event_id, score, status)
            
            if updated:
                # Si esta confirmado, publicar a queue
                if status == 'CONFIRMADO':
                    event['score'] = score
                    event['status'] = status
                    self.publish_confirmed(event)
                
                logger.info("verification_completed",
                           event_id=event_id,
                           score=score,
                           status=status)
                return True
            else:
                return False
                
        except Exception as e:
            logger.error("verification_failed",
                        error=str(e),
                        error_type=type(e).__name__)
            return False
    
    def callback(self, ch, method, properties, body):
        """Callback para procesar mensajes de la queue"""
        try:
            event = json.loads(body)
            logger.info("processing_normalized_event",
                       event_id=event.get('event_id'))
            
            # Verificar evento
            success = self.verify_event(event)
            
            if success:
                # Acknowledge
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # No requeue para evitar loops
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            
        except Exception as e:
            logger.error("callback_error", error=str(e))
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def run(self):
        """Iniciar servicio"""
        logger.info("verifier_service_starting")
        
        # Conectar a servicios
        self.connect_db()
        self.connect_rabbitmq()
        
        # Configurar consumidor
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='normalized_events',
            on_message_callback=self.callback
        )
        
        logger.info("waiting_for_normalized_events")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("verifier_service_stopping")
            self.channel.stop_consuming()
        finally:
            if self.rabbitmq_conn:
                self.rabbitmq_conn.close()
            if self.db_conn:
                self.db_conn.close()

if __name__ == "__main__":
    service = VerifierService()
    service.run()
