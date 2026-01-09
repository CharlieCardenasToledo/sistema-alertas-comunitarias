# Plan de Implementacion - Admin Panel Vue.js

**Tarea**: 2.5 - Desarrollar Admin Panel
**Estado**: PLANIFICADO (No implementado)
**Prioridad**: Media

## Objetivo

Crear una interfaz web de administracion para gestionar el sistema de alertas, monitorear scrapers, configurar fuentes y visualizar estadisticas.

## Tecnologias Propuestas

- **Frontend**: Vue.js 3 con Composition API
- **UI Framework**: Vuetify 3 o Element Plus
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Charts**: Chart.js o Apache ECharts
- **Build**: Vite

## Funcionalidades Principales

### 1. Dashboard
- Estadisticas en tiempo real
- Graficos de eventos por tipo
- Eventos recientes
- Estado de servicios
- Metricas de scrapers

### 2. Gestion de Fuentes
- Listar fuentes configuradas
- Agregar nueva fuente
- Editar configuracion
- Activar/Desactivar fuentes
- Ver historial de scraping

### 3. Gestion de Eventos
- Listar eventos capturados
- Filtrar por tipo, zona, estado
- Ver detalles de evento
- Cambiar estado manualmente
- Ver score de confianza

### 4. Gestion de Usuarios
- Listar usuarios suscritos
- Ver suscripciones activas
- Gestionar permisos (admin)

### 5. Configuracion
- Reglas de verificacion
- Parametros del sistema
- Configuracion de notificaciones
- Logs del sistema

### 6. Monitoreo
- Estado de scrapers
- Queues RabbitMQ
- Metricas de base de datos
- Logs en tiempo real

## Estructura del Proyecto

```
services/admin-panel/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── Sources/
│   │   ├── Events/
│   │   ├── Users/
│   │   └── Common/
│   ├── views/
│   │   ├── DashboardView.vue
│   │   ├── SourcesView.vue
│   │   ├── EventsView.vue
│   │   ├── UsersView.vue
│   │   └── SettingsView.vue
│   ├── router/
│   ├── stores/
│   ├── services/
│   │   └── api.js
│   ├── App.vue
│   └── main.js
├── Dockerfile
├── nginx.conf
├── package.json
└── vite.config.js
```

## Integracion con API

### Endpoints a consumir
- GET /api/stats - Dashboard
- GET /api/sources - Gestion de fuentes
- GET /api/events - Gestion de eventos
- GET /api/users - Gestion de usuarios
- GET /health - Monitoreo

### Autenticacion
- JWT tokens
- Login con usuario admin
- Refresh tokens
- Proteccion de rutas

## Deployment

### Docker
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### Docker Compose
```yaml
admin-panel:
  build: ./services/admin-panel
  container_name: sacv_admin
  ports:
    - "3000:80"
  depends_on:
    - api-gateway
  networks:
    - sacv_network
```

## Pantallas Principales

### 1. Dashboard
- Cards con metricas clave
- Grafico de eventos por dia
- Mapa de eventos por zona
- Lista de ultimos eventos

### 2. Fuentes
- Tabla con todas las fuentes
- Botones de accion (editar, activar/desactivar)
- Modal para agregar/editar
- Indicador de ultima ejecucion

### 3. Eventos
- Tabla con filtros
- Badges de estado (confirmado, verificacion, no verificado)
- Vista detalle con toda la informacion
- Acciones (cambiar estado, ver fuente)

## Estimacion

- **Tiempo**: 2-3 semanas
- **Complejidad**: Media-Alta
- **Dependencias**: API Gateway completo

## Notas

Este panel seria la interfaz principal para administradores del sistema. Permitiria gestion completa sin necesidad de acceder a la base de datos directamente.

**Estado**: Documentado para implementacion futura
