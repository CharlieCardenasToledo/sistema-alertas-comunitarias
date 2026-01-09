# Sistema de Alertas Comunitarias Verificadas (SACV)

Sistema de alertas comunitarias con scraping automático, verificación de confianza y notificaciones via Telegram para Ecuador.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Prerequisitos](#prerequisitos)
- [Instalación Paso a Paso](#instalación-paso-a-paso)
- [Verificación del Sistema](#verificación-del-sistema)
- [Uso del Sistema](#uso-del-sistema)
- [Arquitectura](#arquitectura)
- [Documentación](#documentación)
- [Troubleshooting](#troubleshooting)

---

## Descripción

Sistema completo de alertas comunitarias que:
- Captura eventos de fuentes oficiales ecuatorianas (IGEPN, INAMHI, CNEL)
- Verifica la confianza mediante sistema de scoring
- Notifica a usuarios via Telegram Bot
- Proporciona API REST para consultas

**Estado**: MVP Funcional (67% completado)  
**Servicios**: 8 microservicios  
**Tecnología**: Python, Docker, PostgreSQL, RabbitMQ, Redis

---

## Prerequisitos

### Software Requerido

1. **Docker Desktop**
   - Versión: 24.0 o superior
   - Descarga: https://www.docker.com/products/docker-desktop
   - **IMPORTANTE**: Debe estar corriendo antes de iniciar

2. **Git**
   - Versión: 2.0 o superior
   - Descarga: https://git-scm.com/downloads

3. **Sistema Operativo**
   - Windows 10/11 (64-bit)
   - macOS 10.15 o superior
   - Linux (Ubuntu 20.04+, Debian 10+)

### Recursos del Sistema

- **RAM**: Mínimo 8GB (recomendado 16GB)
- **Disco**: 10GB libres
- **CPU**: 4 cores recomendado

---

## Instalación Paso a Paso

### Paso 1: Clonar el Repositorio

Abre una terminal (PowerShell en Windows, Terminal en Mac/Linux) y ejecuta:

```bash
# Clonar el repositorio
git clone https://github.com/CharlieCardenasToledo/sistema-alertas-comunitarias.git

# Entrar al directorio
cd sistema-alertas-comunitarias
```

**Verificación**: Deberías ver los archivos del proyecto con `dir` (Windows) o `ls` (Mac/Linux)

---

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
```

**En Windows PowerShell**:
```powershell
Copy-Item .env.example .env
```

El archivo `.env` ya contiene valores por defecto que funcionan. **No necesitas modificarlo** para la demo.

**Contenido del .env**:
```bash
# Database
DB_PASSWORD=sacv_secure_password_2026

# RabbitMQ
RABBITMQ_PASSWORD=rabbitmq_secure_password_2026

# JWT Secret
JWT_SECRET=your_jwt_secret_key_change_this_in_production

# Telegram Bot
TELEGRAM_BOT_TOKEN=8580064066:AAFzYjfvy7LYjM3RofcxReTzu3o2OqTE01c

# Email SMTP (opcional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=

# Grafana (opcional)
GRAFANA_PASSWORD=admin
```

---

### Paso 3: Iniciar Docker Desktop

1. **Abrir Docker Desktop**
2. **Esperar** a que el ícono de Docker en la barra de tareas/menú muestre "Docker Desktop is running"
3. **Verificar** que Docker está corriendo:

```bash
docker --version
```

Deberías ver algo como: `Docker version 24.0.x`

---

### Paso 4: Construir e Iniciar los Servicios

Este paso puede tomar **5-10 minutos** la primera vez (descarga imágenes y construye contenedores).

```bash
# Construir e iniciar todos los servicios
docker-compose up -d
```

**Explicación del comando**:
- `docker-compose`: Herramienta para manejar múltiples contenedores
- `up`: Inicia los servicios
- `-d`: Modo "detached" (segundo plano)

**Salida esperada**:
```
[+] Running 8/8
 ✔ Container sacv_postgres    Started
 ✔ Container sacv_redis       Started
 ✔ Container sacv_rabbitmq    Started
 ✔ Container sacv_scraper     Started
 ✔ Container sacv_normalizer  Started
 ✔ Container sacv_verifier    Started
 ✔ Container sacv_notifier    Started
 ✔ Container sacv_api         Started
```

---

### Paso 5: Verificar que los Servicios Están Corriendo

```bash
# Ver estado de todos los servicios
docker-compose ps
```

**Todos los servicios deben mostrar "Up" o "healthy"**:

```
NAME                STATUS
sacv_api            Up
sacv_normalizer     Up
sacv_notifier       Up
sacv_postgres       Up (healthy)
sacv_rabbitmq       Up (healthy)
sacv_redis          Up (healthy)
sacv_scraper        Up
sacv_verifier       Up
```

---

## Verificación del Sistema

### Verificación 1: Health Check de la API

```bash
curl http://localhost:8000/health
```

**Respuesta esperada**:
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2026-01-09T21:33:05.573395"
}
```

**En Windows PowerShell**:
```powershell
Invoke-WebRequest -Uri http://localhost:8000/health | Select-Object -ExpandProperty Content
```

---

### Verificación 2: Estadísticas del Sistema

```bash
curl http://localhost:8000/api/stats
```

**Respuesta esperada**:
```json
{
  "total_sources": 3,
  "active_sources": 3,
  "total_raw_events": 0,
  "total_events": 0,
  "events_by_status": {
    "confirmados": 0,
    "en_verificacion": 0,
    "no_verificados": 0
  },
  "last_scraping": "2026-01-09T14:19:49.085337"
}
```

---

### Verificación 3: Listar Fuentes Configuradas

```bash
curl http://localhost:8000/api/sources
```

**Deberías ver 3 fuentes**:
1. Instituto Geofísico - Sismos (IGEPN)
2. INAMHI - Alertas Meteorológicas
3. CNEL - Cortes Programados

---

### Verificación 4: Ver Logs de los Servicios

Para ver qué está haciendo cada servicio:

```bash
# Scraper (captura eventos)
docker logs sacv_scraper --tail 20

# Normalizer (procesa eventos)
docker logs sacv_normalizer --tail 20

# Verifier (calcula confianza)
docker logs sacv_verifier --tail 20

# Notifier (envía a Telegram)
docker logs sacv_notifier --tail 20
```

**Logs esperados del Scraper**:
```json
{"event": "scraper_service_starting", "timestamp": "...", "level": "info"}
{"count": 3, "event": "sources_loaded", "timestamp": "...", "level": "info"}
{"jobs": 3, "event": "scheduler_started", "timestamp": "...", "level": "info"}
```

---

## Uso del Sistema

### Acceder a la Documentación Interactiva (Swagger)

Abre tu navegador y ve a:

```
http://localhost:8000/docs
```

Aquí puedes:
- Ver todos los endpoints disponibles
- Probar las APIs directamente
- Ver ejemplos de respuestas

---

### Endpoints Disponibles

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información de la API |
| `/health` | GET | Health check |
| `/api/stats` | GET | Estadísticas del sistema |
| `/api/sources` | GET | Fuentes configuradas |
| `/api/raw-events` | GET | Eventos crudos capturados |
| `/api/events` | GET | Eventos normalizados |
| `/api/events/{id}` | GET | Detalle de un evento |
| `/docs` | GET | Documentación Swagger |

---

### Acceder a RabbitMQ Management

Para ver las colas de mensajes:

```
http://localhost:15672
```

**Credenciales**:
- Usuario: `sacv`
- Contraseña: `rabbitmq_secure_password_2026` (o la que configuraste en tu `.env`)

**Queues a verificar**:
- `raw_events` - Eventos crudos
- `normalized_events` - Eventos normalizados
- `confirmed_events` - Eventos confirmados

---

### Acceder a la Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it sacv_postgres psql -U sacv_user -d sacv_db
```

**Consultas útiles**:

```sql
-- Ver fuentes configuradas
SELECT name, type, active FROM sources;

-- Ver eventos capturados
SELECT type, zone, severity, score, status 
FROM events 
ORDER BY created_at DESC 
LIMIT 5;

-- Ver estadísticas
SELECT 
  type,
  COUNT(*) as total,
  AVG(score) as avg_score
FROM events 
GROUP BY type;

-- Salir
\q
```

---

### Telegram Bot

**Bot**: @AlertasComunitariasBot

**Para recibir notificaciones**:
1. Abre Telegram
2. Busca: `@AlertasComunitariasBot`
3. Inicia conversación con `/start`
4. Espera eventos confirmados (score >= 70)

**Nota**: El bot enviará notificaciones solo cuando haya eventos confirmados con alta confianza.

---

## Arquitectura

### Diagrama del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Fuentes Oficiales                     │
│         IGEPN          INAMHI          CNEL             │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
         ┌───────────────┐
         │    Scraper    │──► PostgreSQL (raw_events)
         │   Service     │──► Redis (rate limiting)
         └───────┬───────┘
                 │
                 ▼ RabbitMQ (raw_events)
                 │
         ┌───────────────┐
         │  Normalizer   │──► PostgreSQL (events)
         │   Service     │
         └───────┬───────┘
                 │
                 ▼ RabbitMQ (normalized_events)
                 │
         ┌───────────────┐
         │   Verifier    │──► PostgreSQL (scoring)
         │   Service     │
         └───────┬───────┘
                 │
                 ▼ RabbitMQ (confirmed_events)
                 │
         ┌───────────────┐
         │   Notifier    │──► Telegram Bot
         │   Service     │
         └───────────────┘
                 │
                 ▼
           👥 Usuarios
```

### Servicios

1. **PostgreSQL** - Base de datos principal (puerto 5432)
2. **Redis** - Cache y rate limiting (puerto 6379)
3. **RabbitMQ** - Message broker (puertos 5672, 15672)
4. **Scraper** - Captura eventos de fuentes oficiales
5. **Normalizer** - Transforma eventos a schema común
6. **Verifier** - Calcula score de confianza (0-100)
7. **Notifier** - Envía notificaciones Telegram
8. **API Gateway** - REST API (puerto 8000)

---

## Documentación

### Documentos Principales

- **README.md** - Este archivo (guía de inicio)
- **PRESENTACION_DEMO.md** - Presentación completa del proyecto
- **RESUMEN_EJECUTIVO_FINAL.md** - Resumen ejecutivo
- **KANBAN.md** - Progreso del proyecto
- **TAREAS_PENDIENTES.md** - Tareas futuras
- **SRS_COMPLETO_v2.md** - Especificación completa
- **architecture_overview.md** - Diagramas de arquitectura

### Sistema de Scoring

Los eventos se verifican con 5 reglas (máximo 100 puntos):

| Regla | Descripción | Puntos |
|-------|-------------|--------|
| R1 | Dominio en lista blanca oficial | +40 |
| R2 | URL válida y accesible | +15 |
| R3 | Evento reciente (<24h) | +15 |
| R4 | Campos completos | +10 |
| R5 | Corroboración cruzada | +20 |

**Estados**:
- **CONFIRMADO**: score >= 70 (se notifica)
- **EN_VERIFICACIÓN**: 40-69 (requiere revisión)
- **NO_VERIFICADO**: < 40 (se descarta)

---

## Comandos Útiles

### Gestión de Servicios

```bash
# Ver estado de servicios
docker-compose ps

# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs de un servicio específico
docker logs sacv_scraper -f

# Reiniciar un servicio
docker-compose restart scraper

# Reiniciar todos los servicios
docker-compose restart

# Detener todos los servicios
docker-compose down

# Detener y eliminar volúmenes (limpieza completa)
docker-compose down -v
```

### Monitoreo

```bash
# Ver uso de recursos
docker stats

# Ver procesos en un contenedor
docker top sacv_scraper

# Ejecutar comando en contenedor
docker exec sacv_postgres psql -U sacv_user -d sacv_db -c "SELECT COUNT(*) FROM events;"
```

---

## Troubleshooting

### Problema: Docker Desktop no está corriendo

**Síntoma**: Error "Cannot connect to the Docker daemon"

**Solución**:
1. Abre Docker Desktop
2. Espera a que inicie completamente
3. Verifica con `docker --version`

---

### Problema: Puerto ya en uso

**Síntoma**: Error "port is already allocated"

**Solución**:
```bash
# Ver qué está usando el puerto
netstat -ano | findstr :8000

# Detener el proceso o cambiar puerto en docker-compose.yml
```

---

### Problema: Servicios no inician

**Síntoma**: Contenedores en estado "Exited"

**Solución**:
```bash
# Ver logs del servicio
docker logs sacv_scraper

# Reconstruir el servicio
docker-compose build scraper
docker-compose up -d scraper
```

---

### Problema: No hay eventos capturados

**Síntoma**: `total_raw_events: 0` en `/api/stats`

**Solución**:
1. Verificar que el scraper está corriendo: `docker logs sacv_scraper`
2. Las fuentes oficiales pueden no tener datos nuevos
3. Esperar 30-60 segundos para el primer scraping
4. Verificar conectividad a internet

---

### Problema: Base de datos no conecta

**Síntoma**: Error "could not connect to server"

**Solución**:
```bash
# Verificar que PostgreSQL está healthy
docker-compose ps

# Reiniciar PostgreSQL
docker-compose restart postgres

# Verificar logs
docker logs sacv_postgres
```

---

## Para Estudiantes

### Ejercicios Sugeridos

1. **Exploración de la API**
   - Prueba todos los endpoints en Swagger
   - Analiza las respuestas JSON
   - Identifica las relaciones entre datos

2. **Análisis de Logs**
   - Observa los logs de cada servicio
   - Identifica el flujo de un evento
   - Comprende el formato JSON estructurado

3. **Base de Datos**
   - Explora las tablas en PostgreSQL
   - Ejecuta consultas SQL
   - Analiza el schema de datos

4. **RabbitMQ**
   - Observa las queues en la UI
   - Identifica el patrón de mensajería
   - Comprende el event-driven architecture

5. **Modificaciones**
   - Agrega una nueva fuente de datos
   - Modifica las reglas de scoring
   - Personaliza los mensajes de Telegram

---

## Soporte

**Repositorio**: https://github.com/CharlieCardenasToledo/sistema-alertas-comunitarias

**Documentación adicional**: Ver carpeta `/docs` en el repositorio

**Issues**: Reportar problemas en GitHub Issues

---

## Licencia

Proyecto académico - UIDE 2026

---

## Autor

**Charlie Cardenas Toledo**
- GitHub: [@CharlieCardenasToledo](https://github.com/CharlieCardenasToledo)
- Institución: UIDE - Universidad Internacional del Ecuador
- Curso: Laboratorio de Arquitectura de Tecnologías de Información

---

## Agradecimientos

- Instituto Geofísico del Ecuador (IGEPN)
- Instituto Nacional de Meteorología e Hidrología (INAMHI)
- Corporación Nacional de Electricidad (CNEL)
- UIDE - Universidad Internacional del Ecuador

---

**Última actualización**: 09-ene-2026  
**Versión**: 1.0 MVP  
**Estado**: Funcional y Validado ✅
