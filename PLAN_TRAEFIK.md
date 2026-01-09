# Plan de Implementacion - Traefik API Gateway

**Tarea**: 2.6 - Configurar Traefik
**Estado**: PLANIFICADO (No implementado)
**Prioridad**: Media

## Objetivo

Implementar Traefik como reverse proxy y API gateway avanzado para el sistema, proporcionando routing, load balancing, SSL/TLS, y service discovery automatico.

## Que es Traefik

Traefik es un reverse proxy y load balancer moderno diseñado para microservicios. Caracteristicas:
- Service discovery automatico
- Configuracion dinamica
- SSL/TLS automatico con Let's Encrypt
- Middleware para autenticacion, rate limiting, etc.
- Dashboard de monitoreo
- Metricas para Prometheus

## Arquitectura Propuesta

```
Internet
    |
    v
Traefik (puerto 80/443)
    |
    ├─> Admin Panel (sacv.local/admin)
    ├─> API Gateway (sacv.local/api)
    ├─> RabbitMQ UI (sacv.local/rabbitmq)
    └─> Traefik Dashboard (sacv.local/dashboard)
```

## Configuracion

### Docker Compose

```yaml
traefik:
  image: traefik:v2.10
  container_name: sacv_traefik
  command:
    - "--api.dashboard=true"
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
    - "--certificatesresolvers.letsencrypt.acme.email=admin@sacv.local"
    - "--certificatesresolvers.letsencrypt.acme.storage=/letsencrypt/acme.json"
    - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    - "--metrics.prometheus=true"
  ports:
    - "80:80"
    - "443:443"
    - "8080:8080"
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
    - ./letsencrypt:/letsencrypt
  networks:
    - sacv_network
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.dashboard.rule=Host(`sacv.local`) && (PathPrefix(`/api`) || PathPrefix(`/dashboard`))"
    - "traefik.http.routers.dashboard.service=api@internal"
```

### Labels para API Gateway

```yaml
api-gateway:
  # ... configuracion existente
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.api.rule=Host(`sacv.local`) && PathPrefix(`/api`)"
    - "traefik.http.routers.api.entrypoints=web,websecure"
    - "traefik.http.routers.api.tls.certresolver=letsencrypt"
    - "traefik.http.services.api.loadbalancer.server.port=8000"
    - "traefik.http.middlewares.api-ratelimit.ratelimit.average=100"
    - "traefik.http.middlewares.api-ratelimit.ratelimit.burst=50"
    - "traefik.http.routers.api.middlewares=api-ratelimit"
```

### Labels para Admin Panel

```yaml
admin-panel:
  # ... configuracion existente
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.admin.rule=Host(`sacv.local`) && PathPrefix(`/admin`)"
    - "traefik.http.routers.admin.entrypoints=web,websecure"
    - "traefik.http.routers.admin.tls.certresolver=letsencrypt"
    - "traefik.http.services.admin.loadbalancer.server.port=80"
    - "traefik.http.middlewares.admin-auth.basicauth.users=admin:$$apr1$$..."
    - "traefik.http.routers.admin.middlewares=admin-auth"
```

## Funcionalidades

### 1. Routing Dinamico
- Rutas basadas en host y path
- Service discovery automatico
- Configuracion via labels de Docker

### 2. SSL/TLS
- Certificados automaticos con Let's Encrypt
- Redireccion HTTP a HTTPS
- Renovacion automatica

### 3. Load Balancing
- Distribucion de carga entre replicas
- Health checks
- Sticky sessions si necesario

### 4. Middleware

#### Rate Limiting
```yaml
- "traefik.http.middlewares.ratelimit.ratelimit.average=100"
- "traefik.http.middlewares.ratelimit.ratelimit.burst=50"
```

#### CORS
```yaml
- "traefik.http.middlewares.cors.headers.accesscontrolallowmethods=GET,POST,PUT,DELETE"
- "traefik.http.middlewares.cors.headers.accesscontrolalloworigin=*"
```

#### Autenticacion Basica
```yaml
- "traefik.http.middlewares.auth.basicauth.users=admin:password"
```

### 5. Monitoreo
- Dashboard web en puerto 8080
- Metricas para Prometheus
- Logs de acceso

## Beneficios

1. **Seguridad**: SSL/TLS automatico, autenticacion
2. **Escalabilidad**: Load balancing, service discovery
3. **Observabilidad**: Dashboard, metricas, logs
4. **Simplicidad**: Configuracion declarativa via labels
5. **Flexibilidad**: Middleware para diferentes necesidades

## Configuracion Local

### /etc/hosts (Windows: C:\Windows\System32\drivers\etc\hosts)
```
127.0.0.1 sacv.local
```

### Acceso
- Dashboard Traefik: http://sacv.local:8080
- API: http://sacv.local/api
- Admin: http://sacv.local/admin
- RabbitMQ: http://sacv.local/rabbitmq

## Estimacion

- **Tiempo**: 1-2 dias
- **Complejidad**: Media
- **Dependencias**: Admin Panel (opcional)

## Archivo de Configuracion Estatica (Opcional)

### traefik.yml
```yaml
api:
  dashboard: true

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    exposedByDefault: false
  file:
    filename: /etc/traefik/dynamic.yml

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@sacv.local
      storage: /letsencrypt/acme.json
      httpChallenge:
        entryPoint: web

metrics:
  prometheus: {}
```

## Notas

Traefik simplificaria significativamente el routing y agregaria capacidades enterprise al sistema. Es especialmente util cuando se tienen multiples servicios y se necesita SSL/TLS automatico.

**Estado**: Documentado para implementacion futura
