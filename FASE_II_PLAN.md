# Plan de Implementación - Fase II: Pipeline Completo

## Objetivo
Implementar el pipeline completo de procesamiento de eventos, desde la normalización hasta la notificación, incluyendo la verificación de confianza y el envío de alertas a usuarios suscritos.

## Arquitectura de la Fase II

```
┌─────────────┐
│ raw_events  │ (RabbitMQ Queue)
│   queue     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Normalizer  │ (Python Service)
│  Service    │ - Consume raw_events
└──────┬──────┘ - Transforma a schema común
       │        - Valida con Pydantic
       │        - Genera dedup_hash
       ▼
┌─────────────┐
│ normalized_ │ (RabbitMQ Queue)
│   events    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Verifier   │ (Python Service)
│  Service    │ - Aplica reglas de scoring
└──────┬──────┘ - Calcula estado
       │        - Actualiza BD
       │
       ▼
┌─────────────┐
│ confirmed_  │ (RabbitMQ Queue)
│   events    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Notifier   │ (Python Service)
│  Service    │ - Lee suscripciones
└─────────────┘ - Envía Telegram/Email
```

## Tarea 2.1: Normalizer Service

### Responsabilidades
- Consumir eventos crudos de RabbitMQ
- Transformar a esquema normalizado
- Extraer zona, severidad, tipo
- Generar hash de deduplicación
- Validar campos obligatorios
- Almacenar en tabla `events`
- Publicar a queue `normalized_events`

### Tecnologías
- Python 3.11
- Pika (RabbitMQ client)
- Pydantic (validación)
- python-dateutil (parsing de fechas)
- structlog (logging)

### Archivos a crear
- `services/normalizer/requirements.txt`
- `services/normalizer/Dockerfile`
- `services/normalizer/src/main.py`
- `services/normalizer/src/models.py`

## Tarea 2.2: Verifier Service

### Responsabilidades
- Consumir eventos normalizados
- Aplicar reglas de verificación:
  - R1: Dominio en lista blanca (+40)
  - R2: URL válida y accesible (+15)
  - R3: Timestamp reciente (+15)
  - R4: Campos completos (+10)
  - R5: Corroboración cruzada (+20)
- Calcular score total
- Determinar estado según umbrales:
  - CONFIRMADO: score >= 70
  - EN_VERIFICACION: 40-69
  - NO_VERIFICADO: < 40
- Actualizar evento en BD
- Publicar eventos CONFIRMADO a queue

### Tecnologías
- Python 3.11
- Pika, psycopg2, requests
- structlog

### Archivos a crear
- `services/verifier/requirements.txt`
- `services/verifier/Dockerfile`
- `services/verifier/src/main.py`
- `services/verifier/src/rules.py`

## Tarea 2.3: Notifier Service

### Responsabilidades
- Consumir eventos confirmados
- Leer suscripciones activas de BD
- Filtrar por tipo y zona
- Enviar notificaciones por:
  - Telegram Bot API
  - Email SMTP (opcional)
- Registrar estado de envío
- Implementar retry con backoff

### Tecnologías
- Python 3.11
- python-telegram-bot 20.7+
- aiosmtplib (email)
- Pika, psycopg2
- structlog

### Configuración requerida
- Token de Telegram Bot (obtener de @BotFather)
- Credenciales SMTP (Gmail/Mailgun/SendGrid)

### Archivos a crear
- `services/notifier/requirements.txt`
- `services/notifier/Dockerfile`
- `services/notifier/src/main.py`
- `services/notifier/src/telegram_client.py`
- `services/notifier/src/email_client.py`

## Orden de Implementación

1. **Normalizer Service** (Tarea 2.1)
   - Más simple, sin dependencias externas
   - Permite probar transformación de datos
   
2. **Verifier Service** (Tarea 2.2)
   - Depende de Normalizer
   - Implementa lógica de negocio core
   
3. **Notifier Service** (Tarea 2.3)
   - Depende de Verifier
   - Requiere configuración externa (Telegram)

## Verificación de Cada Servicio

### Normalizer
```bash
# Verificar consumo de queue
docker logs sacv_normalizer

# Verificar eventos normalizados en BD
docker exec sacv_postgres psql -U sacv_user -d sacv_db \
  -c "SELECT COUNT(*) FROM events;"
```

### Verifier
```bash
# Verificar scoring
docker exec sacv_postgres psql -U sacv_user -d sacv_db \
  -c "SELECT event_id, status, score FROM events LIMIT 5;"
```

### Notifier
```bash
# Verificar notificaciones enviadas
docker exec sacv_postgres psql -U sacv_user -d sacv_db \
  -c "SELECT COUNT(*) FROM notifications WHERE status='sent';"
```

## Actualización de Docker Compose

Agregar los 3 nuevos servicios:
```yaml
  normalizer:
    build: ./services/normalizer
    depends_on: [postgres, rabbitmq]
    
  verifier:
    build: ./services/verifier
    depends_on: [postgres, rabbitmq]
    
  notifier:
    build: ./services/notifier
    depends_on: [postgres, rabbitmq]
    environment:
      TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN}
```

## Próximos Pasos

Una vez completadas las tareas 2.1-2.3, continuaremos con:
- 2.4: Scrapers adicionales (lluvia, cortes)
- 2.5: Admin Panel Vue.js
- 2.6: Traefik
- 2.7: Prueba end-to-end completa

---

**Inicio**: Tarea 2.1 - Normalizer Service
