# Sistema de Alertas Comunitarias Verificadas (SACV)

Sistema de detección, verificación y notificación de eventos críticos (sismos, lluvias, cortes programados) mediante scraping de fuentes oficiales.

## 🚀 Inicio Rápido

```bash
# 1. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Iniciar servicios
docker-compose up -d

# 3. Verificar estado
docker-compose ps

# 4. Ver logs
docker-compose logs -f
```

## 📋 Acceso a Servicios

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672 (user: sacv, pass: ver .env)
- **Grafana**: http://localhost:3000 (user: admin, pass: ver .env)
- **Prometheus**: http://localhost:9090

## 🏗️ Arquitectura

Ver documentación completa en:
- `SRS_COMPLETO_v2.md` - Especificación de requisitos
- `architecture_overview.md` - Diagramas de arquitectura
- `PLAN_IMPLEMENTACION.md` - Plan de implementación

## 📦 Stack Tecnológico

- **Backend**: Python 3.11 + FastAPI
- **Scraping**: Scrapy + Playwright
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Message Broker**: RabbitMQ 3.12
- **Frontend**: Vue.js 3 + Vuetify
- **Deployment**: Docker + Docker Compose

## 📊 Estado del Proyecto

Ver `KANBAN.md` para el estado actual de implementación.

## 📝 Licencia

Proyecto académico - UIDE 2026
