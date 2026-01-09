# Explicación de los Diagramas de Arquitectura - SACV

Este documento explica de forma verbal y didáctica cada uno de los diagramas de arquitectura del Sistema de Alertas Comunitarias Verificadas (SACV).

---

## 1. Diagrama de Contexto (C4 Level 1)

**¿Qué muestra este diagrama?**

Este es el diagrama más general del sistema. Imagina que estás viendo el sistema desde un helicóptero, a vista de pájaro. Aquí vemos tres grandes grupos:

### Los Usuarios
Tenemos tres tipos de personas que interactúan con el sistema:
- **Usuario Final**: Es la persona común que quiere recibir alertas sobre sismos, cortes de luz o lluvias en su zona
- **Administrador**: Es quien configura el sistema, define qué fuentes de información usar y gestiona a los usuarios
- **Operador**: Es quien revisa los eventos que el sistema no puede verificar automáticamente

### El Sistema SACV (el corazón)
Es la caja azul grande en el centro. Este es nuestro sistema completo. Los usuarios se conectan a él para consultar alertas y suscribirse a notificaciones. Los administradores lo configuran y los operadores revisan eventos dudosos.

### Las Fuentes Externas
Son las páginas web oficiales de donde el sistema obtiene información:
- **Instituto Geofísico**: Proporciona datos de sismos
- **INAMHI**: Informa sobre clima y lluvias
- **Empresa Eléctrica**: Publica los cortes de luz programados

El sistema hace "scraping" (extracción automática) de estas páginas periódicamente.

### Los Canales de Notificación
Una vez que el sistema verifica un evento, envía notificaciones a través de:
- **Telegram**: Mensajes instantáneos
- **Email**: Correos electrónicos
- **WhatsApp**: Mensajes vía Twilio API

**Flujo básico**: Las fuentes externas publican información → El sistema SACV la captura y verifica → Los usuarios reciben notificaciones por sus canales preferidos.

---

## 2. Diagrama de Contenedores (C4 Level 2)

**¿Qué muestra este diagrama?**

Ahora bajamos un nivel de detalle. Si en el diagrama anterior veíamos el sistema como una caja negra, aquí abrimos esa caja y vemos qué hay dentro. Es como abrir el capó de un carro para ver el motor y sus partes.

### Capa de Frontend
- **Admin Panel**: Una aplicación web hecha en Vue.js donde los administradores pueden gestionar el sistema. Corre en el puerto 8080.

### API Gateway
- **Traefik**: Es como el portero del edificio. Todo el tráfico que llega al sistema pasa por aquí primero. Traefik decide si una petición va al Admin Panel o al API Service. Usa los puertos 80 (HTTP) y 443 (HTTPS).

### Servicios de Aplicación (los trabajadores)
Aquí tenemos 5 microservicios, cada uno con una responsabilidad específica:

1. **API Service (FastAPI)**: Es la API REST que expone endpoints para que el frontend consulte alertas, gestione usuarios y suscripciones. Puerto 8000.

2. **Scraper Service**: Es el robot que visita las páginas oficiales periódicamente para extraer información. Usa Scrapy y Playwright.

3. **Normalizer Service**: Toma los datos crudos que extrajo el Scraper y los convierte a un formato estándar que el sistema entiende.

4. **Verifier Service**: Es el detective del sistema. Analiza cada evento normalizado, le asigna un puntaje de confianza y decide si es CONFIRMADO, EN_VERIFICACION o NO_VERIFICADO.

5. **Notifier Service**: Cuando un evento es confirmado, este servicio se encarga de enviar las notificaciones a los usuarios suscritos por Telegram, Email o WhatsApp.

### Capa de Datos
- **PostgreSQL**: La base de datos principal donde se almacena todo (usuarios, eventos, suscripciones, notificaciones). Puerto 5432.
- **Redis**: Cache en memoria para mejorar el rendimiento y controlar la frecuencia de scraping (rate limiting). Puerto 6379.

### Capa de Mensajería
- **RabbitMQ**: Es el sistema de colas de mensajes. Los servicios no se hablan directamente entre sí, sino que publican mensajes en colas y otros servicios los consumen. Esto hace el sistema más robusto. Puerto 5672.

### Observabilidad
- **Prometheus**: Recolecta métricas de todos los servicios (cuántas peticiones, errores, tiempos de respuesta). Puerto 9090.
- **Grafana**: Crea dashboards visuales con las métricas de Prometheus. Puerto 3000.

**Flujo de datos**: 
- Usuario → Traefik → Admin Panel/API Service
- API Service ↔ PostgreSQL/Redis
- Scraper → PostgreSQL/Redis/RabbitMQ
- RabbitMQ → Normalizer → PostgreSQL/RabbitMQ
- RabbitMQ → Verifier → PostgreSQL/RabbitMQ
- RabbitMQ → Notifier → PostgreSQL → Canales externos

---

## 3. Diagrama de Componentes - Scraper Service (C4 Level 3)

**¿Qué muestra este diagrama?**

Aquí hacemos zoom en uno de los servicios más importantes: el Scraper. Es como si tomáramos una lupa y miráramos en detalle cómo funciona por dentro.

### El Scheduler (el despertador)
**APScheduler** es el componente que programa las tareas. Cada cierto tiempo (definido en la configuración), despierta a los scrapers específicos para que hagan su trabajo.

### Los Scrapers (los recolectores)
Tenemos tres scrapers especializados, cada uno con su herramienta:

1. **Sismo Scraper (Scrapy)**: Extrae datos de sismos del Instituto Geofísico. Scrapy es ideal para páginas estáticas.

2. **Lluvia Scraper (Playwright)**: Extrae datos de INAMHI. Usa Playwright porque esta página puede tener contenido dinámico que se carga con JavaScript.

3. **Corte Scraper (BeautifulSoup)**: Extrae información de cortes programados. BeautifulSoup es simple y efectivo para HTML estático.

### El Parser Manager (el traductor)
Recibe los datos HTML crudos de los scrapers y los convierte en datos estructurados usando:
- **CSS Selectors**: Para encontrar elementos por clases CSS
- **XPath**: Para navegar el árbol HTML
- **Regex**: Para extraer patrones específicos de texto

### Los Componentes de Soporte

1. **Rate Limiter**: Controla que no hagamos demasiadas peticiones a las páginas oficiales. Usa Redis para llevar un contador. Si ya hicimos muchas peticiones en poco tiempo, espera antes de hacer otra.

2. **Retry Handler**: Si una petición falla (la página no responde, hay un error de red), este componente reintenta la operación con "exponential backoff" (espera cada vez más tiempo entre intentos).

3. **Raw Validator**: Valida que los datos extraídos tengan el formato mínimo esperado antes de guardarlos.

### Las Salidas
- **PostgreSQL**: Guarda los eventos crudos en la tabla `raw_events` y consulta la configuración de las fuentes en la tabla `sources`.
- **Redis**: Almacena los contadores de rate limiting.
- **RabbitMQ**: Publica los eventos crudos en la cola `raw_events` para que el Normalizer los procese.

**Flujo interno**:
Scheduler activa un scraper → Scraper extrae HTML → Parser Manager procesa → Rate Limiter verifica límites → Retry Handler maneja errores → Raw Validator valida → Guarda en PostgreSQL y publica en RabbitMQ.

---

## 4. Flujo de Datos Event-Driven

**¿Qué muestra este diagrama?**

Este diagrama es como una película que muestra el viaje completo de un evento desde que se detecta hasta que llega al usuario. Es un diagrama de secuencia que muestra el orden temporal de las operaciones.

### Acto 1: Captura (Scraper)
1. El **Scraper Service** se ejecuta según su programación
2. Extrae datos de una página oficial
3. Guarda el evento crudo en **PostgreSQL** (tabla `raw_events`)
4. Publica un mensaje en la cola **RabbitMQ: raw_events**

### Acto 2: Normalización (Normalizer)
1. El **Normalizer** consume mensajes de la cola `raw_events`
2. Transforma los datos crudos a un esquema estándar
3. Genera un hash de deduplicación para evitar eventos duplicados
4. Guarda/actualiza el evento en **PostgreSQL** (tabla `events`)
5. Publica en la cola **RabbitMQ: normalized_queue**

### Acto 3: Verificación (Verifier)
1. El **Verifier** consume mensajes de la cola `normalized_queue`
2. Aplica reglas de scoring (verifica dominio, busca duplicados, etc.)
3. Consulta **PostgreSQL** para verificar whitelist de dominios y duplicados
4. Calcula un puntaje de confianza (0-100)
5. Actualiza el estado del evento en **PostgreSQL**:
   - `CONFIRMADO` (score alto)
   - `EN_VERIFICACION` (score medio)
   - `NO_VERIFICADO` (score bajo)
6. Si el estado es `CONFIRMADO`, publica en **RabbitMQ: confirmed_queue**
7. Si es `EN_VERIFICACION`, lo marca para revisión manual

### Acto 4: Notificación (Notifier)
1. El **Notifier** consume mensajes de la cola `confirmed_queue`
2. Consulta **PostgreSQL** para obtener las suscripciones activas que coincidan con el evento
3. Envía notificaciones a través de los **Canales Externos** (Telegram, Email, WhatsApp)
4. Registra el estado de cada notificación en **PostgreSQL** (tabla `notifications`)

**Características clave del flujo**:
- **Asíncrono**: Los servicios no esperan respuestas, publican mensajes y continúan
- **Desacoplado**: Los servicios no se conocen entre sí, solo conocen las colas
- **Resiliente**: Si un servicio falla, los mensajes quedan en la cola esperando
- **Escalable**: Podemos tener múltiples workers consumiendo de la misma cola

---

## 5. Arquitectura de Despliegue - Docker Compose

**¿Qué muestra este diagrama?**

Este diagrama muestra cómo todos los componentes del sistema se despliegan en contenedores Docker y cómo se conectan entre sí. Es como el plano de un edificio que muestra dónde va cada habitación.

### El Docker Host (el edificio)
Es el servidor físico o virtual donde corre todo. Dentro de él tenemos:

### Capa de Proxy (la recepción)
- **traefik:3.0**: Contenedor que expone los puertos 80, 443 y 8080. Es el único punto de entrada desde Internet.

### Capa de Frontend (la interfaz)
- **admin-panel**: Contenedor con nginx:alpine que sirve la aplicación Vue.js compilada.

### Capa de Backend (los trabajadores)
Cinco contenedores Python 3.11-slim, cada uno ejecutando un servicio:
- **api-gateway**: FastAPI
- **scraper-service**: Scrapy + Playwright
- **normalizer**: Worker de normalización
- **verifier**: Worker de verificación
- **notifier**: Worker de notificación

### Capa de Datos (el almacenamiento)
- **postgres:15-alpine**: Base de datos con volumen persistente `pg_data`
- **redis:7-alpine**: Cache con volumen persistente `redis_data`

### Capa de Mensajería (el cartero)
- **rabbitmq:3-management**: Broker de mensajes con puertos 5672 (AMQP) y 15672 (UI de gestión). Volumen `rabbit_data`.

### Capa de Observabilidad (el panel de control)
- **prometheus:latest**: Recolector de métricas con volumen `prom_data`
- **grafana:latest**: Dashboards con volumen `grafana_data`

### La Red (sacv_network)
Todos los contenedores están conectados a la misma red Docker llamada `sacv_network`. Esto permite que:
- Se comuniquen entre sí usando nombres de contenedor como DNS
- Estén aislados de otras aplicaciones en el mismo host
- Traefik pueda enrutar tráfico a los servicios internos

### Volúmenes (la persistencia)
Los datos importantes se guardan en volúmenes Docker para que no se pierdan si un contenedor se reinicia:
- `pg_data`: Datos de PostgreSQL
- `redis_data`: Datos de Redis
- `rabbit_data`: Mensajes de RabbitMQ
- `prom_data`: Métricas históricas
- `grafana_data`: Configuración de dashboards

**Ventajas de esta arquitectura**:
- **Portabilidad**: Todo el sistema se puede mover a otro servidor con un solo comando
- **Aislamiento**: Cada servicio tiene su propio entorno
- **Escalabilidad**: Podemos aumentar réplicas de servicios fácilmente
- **Reproducibilidad**: El mismo `docker-compose.yml` crea el mismo ambiente siempre

---

## 6. Modelo de Datos Simplificado (ER Diagram)

> **Nota**: Este diagrama aún no ha sido creado en Excalidraw, pero aquí está la explicación de lo que mostraría.

**¿Qué muestra este diagrama?**

Este diagrama muestra las tablas principales de la base de datos PostgreSQL y cómo se relacionan entre sí. Es como el plano de una biblioteca que muestra qué estantes hay y cómo están organizados los libros.

### Entidades Principales

#### SOURCE (Fuentes de Información)
Almacena la configuración de cada fuente externa:
- `source_id`: Identificador único (UUID)
- `name`: Nombre de la fuente (ej: "Instituto Geofísico")
- `base_url`: URL base de la página
- `type`: Tipo de evento (SISMO, LLUVIA, CORTE)
- `domain`: Dominio de confianza
- `parser_config`: Configuración JSON de cómo parsear la página
- `frequency_sec`: Cada cuántos segundos hacer scraping
- `active`: Si está activa o no

**Relación**: Una SOURCE genera muchos RAW_EVENT (1:N)

#### RAW_EVENT (Eventos Crudos)
Almacena los datos tal como se extrajeron de la fuente:
- `raw_id`: Identificador único (UUID)
- `source_id`: Referencia a SOURCE (FK)
- `fetched_at`: Timestamp de cuándo se extrajo
- `raw_payload`: Datos crudos en formato JSON
- `raw_hash`: Hash para detectar duplicados

**Relación**: Un RAW_EVENT se normaliza a un EVENT (1:1)

#### EVENT (Eventos Normalizados)
Almacena eventos en formato estándar:
- `event_id`: Identificador único (UUID)
- `type`: Tipo (SISMO, LLUVIA, CORTE)
- `occurred_at`: Cuándo ocurrió el evento
- `zone`: Zona geográfica afectada
- `severity`: Severidad (BAJA, MEDIA, ALTA, CRITICA)
- `title`: Título del evento
- `description`: Descripción detallada
- `evidence_url`: URL de evidencia
- `source_id`: Referencia a SOURCE (FK)
- `dedup_hash`: Hash de deduplicación
- `status`: Estado (CONFIRMADO, EN_VERIFICACION, NO_VERIFICADO)
- `score`: Puntaje de confianza (0-100)

**Relación**: Un EVENT puede generar muchas NOTIFICATION (1:N)

#### USER (Usuarios)
Almacena información de usuarios:
- `user_id`: Identificador único (UUID)
- `email`: Correo electrónico
- `role`: Rol (USER, OPERATOR, ADMIN)
- `created_at`: Fecha de creación

**Relación**: Un USER puede crear muchas SUBSCRIPTION (1:N)

#### SUBSCRIPTION (Suscripciones)
Define qué notificaciones quiere recibir cada usuario:
- `sub_id`: Identificador único (UUID)
- `user_id`: Referencia a USER (FK)
- `type`: Tipo de evento de interés (SISMO, LLUVIA, CORTE)
- `zone`: Zona de interés
- `channel`: Canal preferido (TELEGRAM, EMAIL, WHATSAPP)
- `active`: Si está activa

**Relación**: Una SUBSCRIPTION puede recibir muchas NOTIFICATION (1:N)

#### NOTIFICATION (Notificaciones Enviadas)
Registro de cada notificación enviada:
- `notif_id`: Identificador único (UUID)
- `event_id`: Referencia a EVENT (FK)
- `sub_id`: Referencia a SUBSCRIPTION (FK)
- `channel`: Canal usado (TELEGRAM, EMAIL, WHATSAPP)
- `to`: Destinatario (chat_id, email, phone)
- `sent_at`: Timestamp de envío
- `status`: Estado (SENT, FAILED, PENDING)

#### VERIFICATION_RULE (Reglas de Verificación)
Define las reglas para calcular el score de confianza:
- `rule_id`: Identificador único (UUID)
- `name`: Nombre de la regla
- `weight`: Peso de la regla (1-100)
- `enabled`: Si está habilitada

**Flujo de datos en el modelo**:
1. SOURCE → RAW_EVENT: El scraper guarda datos crudos
2. RAW_EVENT → EVENT: El normalizer transforma a formato estándar
3. EVENT → NOTIFICATION: El notifier crea notificaciones
4. USER → SUBSCRIPTION: Los usuarios definen sus preferencias
5. SUBSCRIPTION → NOTIFICATION: Las notificaciones se envían según suscripciones

---

## Resumen: Cómo Todo Funciona Junto

Imagina que ocurre un sismo en Quito:

1. **Scraper** visita la página del Instituto Geofísico cada 5 minutos
2. Detecta un nuevo sismo, lo guarda en `raw_events` y publica en RabbitMQ
3. **Normalizer** consume el mensaje, lo convierte a formato estándar, guarda en `events`
4. **Verifier** analiza el evento, ve que viene de dominio oficial, le da score 95, marca como CONFIRMADO
5. **Notifier** busca todas las suscripciones activas para SISMO en zona QUITO
6. Envía notificaciones por Telegram/Email/WhatsApp a los usuarios suscritos
7. **Prometheus** registra métricas de todo el proceso
8. **Grafana** muestra en tiempo real cuántos eventos se procesaron

Todo esto ocurre de forma automática, asíncrona y escalable gracias a la arquitectura event-driven con microservicios en Docker.
