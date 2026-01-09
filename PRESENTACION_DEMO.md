# Sistema de Alertas Comunitarias Verificadas (SACV)
## Presentación Demo

**Autor**: Charlie Cardenas Toledo  
**Institución**: UIDE - Laboratorio Arquitectura TI  
**Fecha**: Enero 2026  
**Versión**: 1.0 MVP

---

## 📋 Agenda

1. Introducción y Problema
2. Solución Propuesta
3. Arquitectura del Sistema
4. Funcionalidades Implementadas
5. Demostración en Vivo
6. Tecnologías Utilizadas
7. Resultados y Métricas
8. Trabajo Futuro
9. Conclusiones

---

## 1. Introducción y Problema

### El Problema

En Ecuador, la información sobre eventos críticos (sismos, lluvias intensas, cortes de energía) está dispersa en múltiples fuentes oficiales:

- **IGEPN** - Sismos
- **INAMHI** - Meteorología
- **CNEL** - Cortes de energía

**Desafíos**:
- ❌ Información fragmentada
- ❌ Sin verificación de confianza
- ❌ No hay notificaciones unificadas
- ❌ Difícil acceso para ciudadanos

### La Necesidad

Los ciudadanos necesitan:
- ✅ Información centralizada
- ✅ Alertas verificadas y confiables
- ✅ Notificaciones en tiempo real
- ✅ Acceso fácil vía Telegram

---

## 2. Solución Propuesta

### Sistema de Alertas Comunitarias Verificadas

**Objetivo**: Sistema automatizado que captura, verifica y notifica eventos críticos a ciudadanos ecuatorianos.

**Características Principales**:

1. **Scraping Automatizado** - Captura eventos de fuentes oficiales
2. **Verificación de Confianza** - Sistema de scoring (0-100 puntos)
3. **Notificaciones Telegram** - Alertas en tiempo real
4. **API REST** - Acceso programático a datos
5. **Event-Driven** - Arquitectura escalable

**Valor Agregado**:
- Información verificada y confiable
- Notificaciones instantáneas
- Filtrado por zona geográfica
- Clasificación por severidad

---

## 3. Arquitectura del Sistema

### Visión General

```
┌─────────────────┐
│ Fuentes Oficiales│
│ IGEPN, INAMHI,  │
│ CNEL            │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Scraper Service │ ──► PostgreSQL
│ (3 tipos)       │ ──► Redis (Rate Limiting)
└────────┬────────┘
         │
         ▼ RabbitMQ (raw_events)
         │
┌─────────────────┐
│ Normalizer      │ ──► PostgreSQL (events)
│ Service         │
└────────┬────────┘
         │
         ▼ RabbitMQ (normalized_events)
         │
┌─────────────────┐
│ Verifier        │ ──► PostgreSQL (scoring)
│ Service         │
└────────┬────────┘
         │
         ▼ RabbitMQ (confirmed_events)
         │
┌─────────────────┐
│ Notifier        │ ──► Telegram Bot
│ Service         │
└─────────────────┘
         │
         ▼
   👥 Usuarios
```

### Microservicios (8 servicios)

1. **PostgreSQL** - Base de datos principal
2. **Redis** - Cache y rate limiting
3. **RabbitMQ** - Message broker
4. **Scraper** - Captura de eventos
5. **Normalizer** - Transformación de datos
6. **Verifier** - Scoring de confianza
7. **Notifier** - Notificaciones
8. **API Gateway** - REST API

---

## 4. Funcionalidades Implementadas

### 4.1 Captura de Eventos (Scraper)

**Características**:
- ✅ 3 tipos de eventos: sismo, lluvia, corte
- ✅ Scraping periódico automatizado
- ✅ Deduplicación por hash
- ✅ Rate limiting con Redis
- ✅ Almacenamiento en PostgreSQL

**Fuentes Configuradas**:
- IGEPN (sismos) - cada 30s
- INAMHI (lluvia) - cada 5 min
- CNEL (cortes) - cada 10 min

### 4.2 Normalización

**Proceso**:
1. Consume eventos crudos de RabbitMQ
2. Extrae zona geográfica (provincias Ecuador)
3. Detecta severidad (Alta/Media/Baja)
4. Valida con Pydantic
5. Genera hash de deduplicación
6. Publica a siguiente queue

**Datos Extraídos**:
- Tipo de evento
- Zona geográfica
- Severidad
- Título y descripción
- URL de evidencia
- Timestamp

### 4.3 Verificación de Confianza

**Sistema de Scoring (5 reglas, max 100 puntos)**:

| Regla | Descripción | Puntos |
|-------|-------------|--------|
| R1 | Dominio en lista blanca oficial | +40 |
| R2 | URL válida y accesible | +15 |
| R3 | Timestamp reciente (<24h) | +15 |
| R4 | Campos completos | +10 |
| R5 | Corroboración cruzada | +20 |

**Estados Resultantes**:
- **CONFIRMADO**: score ≥ 70 (se notifica)
- **EN_VERIFICACIÓN**: 40-69 (requiere revisión)
- **NO_VERIFICADO**: < 40 (se descarta)

### 4.4 Notificaciones Telegram

**Bot**: @AlertasComunitariasBot

**Formato de Mensaje**:
```
🌍 ALERTA: SISMO

🔴 Severidad: Alta
📍 Zona: Pichincha
⭐ Confianza: 85/100

Sismo de magnitud 5.2 detectado en Quito

🔗 Ver fuente oficial

Sistema de Alertas Comunitarias Verificadas
```

**Características**:
- Emojis según tipo de evento
- Código de color por severidad
- Score de confianza visible
- Link a fuente oficial
- Filtrado por zona y tipo

### 4.5 API REST

**8 Endpoints Disponibles**:

```
GET  /                    - Info de la API
GET  /health              - Health check
GET  /api/stats           - Estadísticas
GET  /api/sources         - Fuentes configuradas
GET  /api/raw-events      - Eventos crudos
GET  /api/events          - Eventos normalizados
GET  /api/events/{id}     - Detalle de evento
GET  /docs                - Swagger UI
```

**Características**:
- Paginación (limit/offset)
- Filtros por tipo, zona, estado
- Documentación Swagger automática
- Validación Pydantic
- CORS configurado

---

## 5. Demostración en Vivo

### 5.1 Verificar Estado del Sistema

```bash
# Ver todos los servicios
docker-compose ps

# Resultado esperado: 8 servicios running
```

### 5.2 Consultar API

```bash
# Health check
curl http://localhost:8000/health

# Estadísticas del sistema
curl http://localhost:8000/api/stats

# Listar fuentes
curl http://localhost:8000/api/sources

# Ver eventos
curl http://localhost:8000/api/events
```

### 5.3 Ver Logs en Tiempo Real

```bash
# Scraper capturando eventos
docker logs sacv_scraper --tail 20 -f

# Normalizer procesando
docker logs sacv_normalizer --tail 20 -f

# Verifier calculando scores
docker logs sacv_verifier --tail 20 -f
```

### 5.4 Verificar Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it sacv_postgres psql -U sacv_user -d sacv_db

# Ver fuentes
SELECT name, type, active FROM sources;

# Ver eventos
SELECT type, zone, severity, score, status 
FROM events 
ORDER BY created_at DESC 
LIMIT 5;
```

### 5.5 Verificar Queues RabbitMQ

```bash
# Ver estado de queues
docker exec sacv_rabbitmq rabbitmqctl list_queues

# Acceder a UI
# http://localhost:15672 (guest/guest)
```

### 5.6 Telegram Bot

1. Abrir Telegram
2. Buscar: @AlertasComunitariasBot
3. Iniciar conversación
4. Esperar notificación de evento confirmado

---

## 6. Tecnologías Utilizadas

### Backend
- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web moderno
- **Pydantic** - Validación de datos
- **Scrapy** - Web scraping
- **BeautifulSoup** - Parsing HTML

### Bases de Datos
- **PostgreSQL 15** - Base de datos relacional
- **Redis 7** - Cache y rate limiting

### Mensajería
- **RabbitMQ 3.12** - Message broker
- **Pika** - Cliente Python para RabbitMQ

### Notificaciones
- **python-telegram-bot 20.7** - Telegram API

### DevOps
- **Docker** - Containerización
- **Docker Compose** - Orquestación
- **structlog** - Logging estructurado (JSON)

### Otras
- **APScheduler** - Scheduling de tareas
- **python-dateutil** - Parsing de fechas
- **requests** - HTTP client

---

## 7. Resultados y Métricas

### Código
- **Líneas de código**: ~4,500
- **Servicios**: 8 contenedores
- **Endpoints REST**: 8
- **Commits**: 15+

### Base de Datos
- **Tablas**: 8 (sources, raw_events, events, users, subscriptions, etc.)
- **Índices**: Optimizados para queries frecuentes
- **Triggers**: updated_at automático

### Queues
- **raw_events** - Eventos crudos capturados
- **normalized_events** - Eventos transformados
- **confirmed_events** - Eventos verificados

### Tipos de Eventos
- **sismo** - Eventos sísmicos
- **lluvia** - Alertas meteorológicas
- **corte** - Cortes de energía

### Progreso del Proyecto
- **Fase I**: 11/11 (100%) ✅
- **Fase II**: 5/7 (71%) ✅
- **Fase III**: 0/6 (0%)
- **Total**: 16/24 (67%)

---

## 8. Trabajo Futuro

### Fase II Pendiente

#### Admin Panel Vue.js
- Dashboard con estadísticas
- Gestión de fuentes
- Gestión de eventos
- Gestión de usuarios
- Configuración del sistema

#### Traefik API Gateway
- Reverse proxy
- SSL/TLS automático
- Load balancing
- Service discovery

### Fase III - Producción

#### Observabilidad
- **Prometheus** - Métricas del sistema
- **Grafana** - Dashboards visuales
- **Health checks** - Monitoreo avanzado

#### Calidad
- **Tests unitarios** - PyTest
- **Tests de integración** - Validación E2E
- **CI/CD** - GitHub Actions

#### Documentación
- **Documentación técnica** - Detallada
- **Guías de deployment** - Producción
- **Video demo** - Presentación

---

## 9. Conclusiones

### Logros Principales

✅ **Sistema Funcional**: MVP completo y operativo
✅ **Arquitectura Escalable**: Microservicios + Event-Driven
✅ **Verificación Automática**: Sistema de scoring robusto
✅ **Notificaciones Real-Time**: Telegram Bot funcional
✅ **API REST**: Acceso programático completo
✅ **Documentación Completa**: Código y arquitectura

### Impacto

El sistema demuestra:
- Integración de múltiples fuentes oficiales
- Procesamiento automatizado de eventos
- Verificación de confianza mediante reglas
- Notificaciones en tiempo real
- Arquitectura moderna y escalable

### Aprendizajes

- Diseño de microservicios
- Event-driven architecture
- Message brokers (RabbitMQ)
- Web scraping ético
- Containerización con Docker
- APIs REST con FastAPI
- Integración con Telegram Bot

### Valor Académico

Este proyecto demuestra competencias en:
- Arquitectura de software
- Desarrollo backend
- DevOps y containerización
- Integración de sistemas
- Documentación técnica

---

## 🎯 Demostración Final

### Sistema en Acción

1. **Scraper** captura evento de IGEPN
2. **Normalizer** transforma y extrae datos
3. **Verifier** calcula score (ej: 85/100)
4. **Notifier** envía a Telegram
5. **Usuario** recibe alerta verificada

### Tiempo de Respuesta

- Captura → Notificación: **< 1 minuto**
- Pipeline completo: **Automático**
- Disponibilidad: **24/7**

---

## 📞 Contacto

**Charlie Cardenas Toledo**
- GitHub: [@CharlieCardenasToledo](https://github.com/CharlieCardenasToledo)
- Repositorio: [sistema-alertas-comunitarias](https://github.com/CharlieCardenasToledo/sistema-alertas-comunitarias)

**UIDE - Universidad Internacional del Ecuador**
Laboratorio de Arquitectura de Tecnologías de Información
Enero 2026

---

## ¡Gracias!

### Preguntas y Respuestas

¿Preguntas sobre el sistema?

---

## Anexo: Comandos de Demo

### Inicio Rápido
```bash
git clone https://github.com/CharlieCardenasToledo/sistema-alertas-comunitarias.git
cd sistema-alertas-comunitarias
docker-compose up -d
```

### Verificación
```bash
docker-compose ps
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
```

### Monitoreo
```bash
docker logs sacv_scraper -f
docker logs sacv_normalizer -f
docker logs sacv_verifier -f
docker logs sacv_notifier -f
```

### Acceso
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- RabbitMQ: http://localhost:15672
