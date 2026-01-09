"""
Normalizer Service - Sistema de Alertas Comunitarias Verificadas
Consume eventos crudos, transforma a schema normalizado y publica
"""
import os
import json
import hashlib
from datetime import datetime
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import pika
import structlog
from dateutil import parser as date_parser
from models import NormalizedEvent

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

class NormalizerService:
    """Servicio de normalizacion de eventos"""
    
    def __init__(self):
        self.db_conn = None
        self.rabbitmq_conn = None
        self.channel = None
        
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
                
                # Declarar queues
                self.channel.queue_declare(queue='raw_events', durable=True)
                self.channel.queue_declare(queue='normalized_events', durable=True)
                
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
    
    def extract_zone(self, raw_payload):
        """Extraer zona geografica del payload"""
        content = str(raw_payload.get('content', '')) + str(raw_payload.get('title', ''))
        content_lower = content.lower()
        
        # Provincias ecuatorianas
        provincias = {
            'pichincha': 'Pichincha',
            'quito': 'Pichincha',
            'guayas': 'Guayas',
            'guayaquil': 'Guayas',
            'azuay': 'Azuay',
            'cuenca': 'Azuay',
            'manabi': 'Manabi',
            'esmeraldas': 'Esmeraldas',
            'tungurahua': 'Tungurahua',
            'ambato': 'Tungurahua',
            'chimborazo': 'Chimborazo',
            'riobamba': 'Chimborazo'
        }
        
        for keyword, provincia in provincias.items():
            if keyword in content_lower:
                return provincia
        
        return 'Nacional'
    
    def extract_severity(self, raw_payload):
        """Extraer severidad del evento"""
        content = str(raw_payload.get('content', '')) + str(raw_payload.get('title', ''))
        content_lower = content.lower()
        
        # Palabras clave para severidad alta
        high_keywords = ['fuerte', 'intenso', 'severo', 'grave', 'critico', 'emergencia']
        # Palabras clave para severidad media
        medium_keywords = ['moderado', 'medio', 'considerable']
        
        for keyword in high_keywords:
            if keyword in content_lower:
                return 'Alta'
        
        for keyword in medium_keywords:
            if keyword in content_lower:
                return 'Media'
        
        return 'Baja'
    
    def parse_occurred_at(self, raw_payload):
        """Parsear fecha del evento"""
        date_str = raw_payload.get('date')
        
        if date_str:
            try:
                return date_parser.parse(date_str)
            except:
                logger.warning("date_parse_failed", date_str=date_str)
        
        # Usar fecha de scraping como fallback
        scraped_at = raw_payload.get('scraped_at')
        if scraped_at:
            try:
                return datetime.fromisoformat(scraped_at)
            except:
                pass
        
        return datetime.utcnow()
    
    def generate_dedup_hash(self, normalized_data):
        """Generar hash para deduplicacion"""
        # Combinar tipo, zona y fecha (solo dia)
        occurred_date = normalized_data['occurred_at'].date().isoformat()
        dedup_str = f"{normalized_data['type']}_{normalized_data['zone']}_{occurred_date}"
        return hashlib.sha256(dedup_str.encode()).hexdigest()
    
    def normalize_event(self, raw_event):
        """Normalizar evento crudo"""
        try:
            raw_payload = raw_event['raw_payload']
            
            # Obtener tipo de evento desde la fuente
            # Consultar tipo de la fuente en BD
            cursor = self.db_conn.cursor()
            cursor.execute("""
                SELECT type FROM sources WHERE source_id = %s
            """, (raw_event['source_id'],))
            result = cursor.fetchone()
            cursor.close()
            
            event_type = result[0] if result else 'sismo'
            
            # Extraer datos
            occurred_at = self.parse_occurred_at(raw_payload)
            zone = self.extract_zone(raw_payload)
            severity = self.extract_severity(raw_payload)
            
            # Manejar titulo vacio
            raw_title = raw_payload.get('title', '').strip()
            if not raw_title:
                raw_title = f"Evento {event_type} detectado"
            title = raw_title[:500]
            
            description = raw_payload.get('content', '')[:1000] if raw_payload.get('content') else None
            evidence_url = raw_payload.get('url', '')
            
            # Construir evento normalizado
            normalized_data = {
                'type': event_type,
                'occurred_at': occurred_at,
                'zone': zone,
                'severity': severity,
                'title': title,
                'description': description,
                'evidence_url': evidence_url,
                'source_id': raw_event['source_id']
            }
            
            # Generar hash de deduplicacion
            normalized_data['dedup_hash'] = self.generate_dedup_hash(normalized_data)
            
            # Validar con Pydantic
            validated_event = NormalizedEvent(**normalized_data)
            
            logger.info("event_normalized",
                       type=event_type,
                       zone=zone,
                       severity=severity,
                       dedup_hash=validated_event.dedup_hash[:8])
            
            return validated_event.dict()
            
        except Exception as e:
            logger.error("normalization_failed",
                        error=str(e),
                        error_type=type(e).__name__)
            return None
    
    def save_normalized_event(self, event):
        """Guardar evento normalizado en BD"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (
                    type, occurred_at, zone, severity, title, description,
                    evidence_url, source_id, dedup_hash, status, score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'NO_VERIFICADO', 0)
                ON CONFLICT (dedup_hash) DO UPDATE
                SET updated_at = CURRENT_TIMESTAMP
                RETURNING event_id
            """, (
                event['type'],
                event['occurred_at'],
                event['zone'],
                event['severity'],
                event['title'],
                event['description'],
                event['evidence_url'],
                event['source_id'],
                event['dedup_hash']
            ))
            
            result = cursor.fetchone()
            self.db_conn.commit()
            
            if result:
                event_id = str(result[0])
                logger.info("event_saved", event_id=event_id)
                return event_id
            else:
                logger.info("event_duplicate", dedup_hash=event['dedup_hash'][:8])
                return None
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error("save_failed", error=str(e))
            return None
        finally:
            cursor.close()
    
    def publish_normalized(self, event):
        """Publicar evento normalizado a queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='normalized_events',
                body=json.dumps(event, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            logger.info("event_published", dedup_hash=event['dedup_hash'][:8])
        except Exception as e:
            logger.error("publish_failed", error=str(e))
    
    def callback(self, ch, method, properties, body):
        """Callback para procesar mensajes de la queue"""
        try:
            raw_event = json.loads(body)
            logger.info("processing_raw_event",
                       raw_hash=raw_event.get('raw_hash', '')[:8])
            
            # Normalizar
            normalized = self.normalize_event(raw_event)
            
            if normalized:
                # Guardar en BD
                event_id = self.save_normalized_event(normalized)
                
                if event_id:
                    normalized['event_id'] = event_id
                    # Publicar a siguiente queue
                    self.publish_normalized(normalized)
            
            # Acknowledge
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error("callback_error", error=str(e))
            # No requeue para evitar loops infinitos
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def run(self):
        """Iniciar servicio"""
        logger.info("normalizer_service_starting")
        
        # Conectar a servicios
        self.connect_db()
        self.connect_rabbitmq()
        
        # Configurar consumidor
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='raw_events',
            on_message_callback=self.callback
        )
        
        logger.info("waiting_for_messages")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("normalizer_service_stopping")
            self.channel.stop_consuming()
        finally:
            if self.rabbitmq_conn:
                self.rabbitmq_conn.close()
            if self.db_conn:
                self.db_conn.close()

if __name__ == "__main__":
    service = NormalizerService()
    service.run()
