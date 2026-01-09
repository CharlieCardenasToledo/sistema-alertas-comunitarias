# Sistema de Alertas Comunitarias Verificadas (SACV)

Sistema de alertas comunitarias con scraping automatico, verificacion de confianza y notificaciones via Telegram para Ecuador.

## Estado del Proyecto

**Version**: 1.0 MVP
**Progreso**: 16/24 tareas (67%)
**Estado**: Funcional y listo para demostracion

## Arquitectura

Sistema de microservicios con event-driven architecture:

```
Fuentes Oficiales → Scraper → Normalizer → Verifier → Notifier → Telegram
                       ↓          ↓           ↓           ↓
                   PostgreSQL  RabbitMQ   RabbitMQ   RabbitMQ
```

## Servicios

- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y rate limiting
- **RabbitMQ**: Message broker
- **Scraper**: Captura eventos de fuentes oficiales
- **Normalizer**: Transforma eventos a schema comun
- **Verifier**: Calcula score de confianza
- **Notifier**: Envia notificaciones Telegram
- **API Gateway**: REST API con 8 endpoints

## Tecnologias

- Python 3.11
- FastAPI
- PostgreSQL 15
- Redis 7
- RabbitMQ 3.12
- Docker & Docker Compose
- Telegram Bot API

## Inicio Rapido

### Prerequisitos

- Docker Desktop
- Git
- 8GB RAM minimo

### Instalacion

```bash
# Clonar repositorio
git clone https://github.com/CharlieCardenasToledo/sistema-alertas-comunitarias.git
cd sistema-alertas-comunitarias

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# Iniciar servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### Acceso

- **API**: http://localhost:8000
- **Swagger**: http://localhost:8000/docs
- **RabbitMQ**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432 (sacv_user/password)

## Endpoints API

- `GET /` - Informacion de la API
- `GET /health` - Health check
- `GET /api/stats` - Estadisticas del sistema
- `GET /api/sources` - Fuentes configuradas
- `GET /api/raw-events` - Eventos crudos
- `GET /api/events` - Eventos normalizados
- `GET /api/events/{id}` - Detalle de evento

## Tipos de Eventos

- **sismo**: Eventos sismicos (IGEPN)
- **lluvia**: Alertas meteorologicas (INAMHI)
- **corte**: Cortes de energia (CNEL)

## Sistema de Scoring

Eventos verificados con 5 reglas (max 100 puntos):

- Dominio oficial: +40
- URL valida: +15
- Evento reciente: +15
- Campos completos: +10
- Corroboracion cruzada: +20

**Estados**:
- CONFIRMADO: >= 70 puntos
- EN_VERIFICACION: 40-69 puntos
- NO_VERIFICADO: < 40 puntos

## Telegram Bot

**Bot**: @AlertasComunitariasBot

Recibe notificaciones de eventos confirmados con:
- Tipo de evento con emoji
- Severidad (Alta/Media/Baja)
- Zona geografica
- Score de confianza
- Link a fuente oficial

## Desarrollo

### Estructura del Proyecto

```
sistema_alertas/
├── services/
│   ├── database/
│   ├── scraper/
│   ├── normalizer/
│   ├── verifier/
│   ├── notifier/
│   └── api-gateway/
├── scripts/
├── docker-compose.yml
├── .env.example
└── README.md
```

### Agregar Nueva Fuente

1. Crear scraper en `services/scraper/src/scrapers/`
2. Registrar en `main.py`
3. Insertar fuente en BD:

```sql
INSERT INTO sources (name, base_url, type, domain, frequency_sec, active)
VALUES ('Nombre', 'URL', 'tipo', 'dominio', 300, true);
```

## Comandos Utiles

```bash
# Ver logs de un servicio
docker logs sacv_scraper --tail 50

# Reiniciar servicio
docker-compose restart scraper

# Acceder a PostgreSQL
docker exec -it sacv_postgres psql -U sacv_user -d sacv_db

# Ver queues RabbitMQ
docker exec sacv_rabbitmq rabbitmqctl list_queues

# Detener todo
docker-compose down

# Limpiar volumenes
docker-compose down -v
```

## Documentacion

- `SRS_COMPLETO_v2.md` - Especificacion completa
- `architecture_overview.md` - Diagramas C4
- `PLAN_IMPLEMENTACION.md` - Plan detallado
- `KANBAN.md` - Progreso del proyecto
- `RESUMEN_EJECUTIVO_FINAL.md` - Resumen ejecutivo

## Trabajo Futuro

### Fase II Pendiente
- Admin Panel Vue.js
- Traefik API Gateway

### Fase III
- Prometheus + Grafana
- Tests automatizados
- Documentacion tecnica completa
- Demo y presentacion

## Contribuir

Este es un proyecto academico para UIDE - Laboratorio Arquitectura TI.

## Licencia

Proyecto academico - UIDE 2026

## Autor

Charlie Cardenas Toledo
- GitHub: [@CharlieCardenasToledo](https://github.com/CharlieCardenasToledo)

## Agradecimientos

- Instituto Geofisico del Ecuador (IGEPN)
- INAMHI
- CNEL
- UIDE - Universidad Internacional del Ecuador
