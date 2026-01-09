# Sistema de Alertas Comunitarias Verificadas - Arquitectura

## 1. Diagrama de Contexto (C4 Level 1)

```mermaid
graph TB
    subgraph "Usuarios"
        U1[Usuario Final]
        U2[Administrador]
        U3[Operador]
    end
    
    subgraph "Sistema SACV"
        SACV[Sistema de Alertas<br/>Comunitarias Verificadas]
    end
    
    subgraph "Fuentes Externas"
        F1[Instituto Geofísico<br/>sismos]
        F2[INAMHI<br/>clima/lluvias]
        F3[Empresa Eléctrica<br/>cortes programados]
    end
    
    subgraph "Canales de Notificación"
        T[Telegram Bot API]
        E[Servicio SMTP<br/>Email]
        W[Twilio API<br/>WhatsApp]
    end
    
    U1 -->|Consulta alertas| SACV
    U1 -->|Se suscribe| SACV
    U2 -->|Configura fuentes| SACV
    U2 -->|Gestiona usuarios| SACV
    U3 -->|Revisa eventos| SACV
    
    SACV -->|Scraping periódico| F1
    SACV -->|Scraping periódico| F2
    SACV -->|Scraping periódico| F3
    
    SACV -->|Envía notificaciones| T
    SACV -->|Envía notificaciones| E
    SACV -->|Envía notificaciones| W
    
    T -->|Recibe alertas| U1
    E -->|Recibe alertas| U1
    W -->|Recibe alertas| U1
    
    style SACV fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style U1 fill:#50C878,stroke:#2E7D4E,color:#fff
    style U2 fill:#50C878,stroke:#2E7D4E,color:#fff
    style U3 fill:#50C878,stroke:#2E7D4E,color:#fff
```

## 2. Diagrama de Contenedores (C4 Level 2)

```mermaid
graph TB
    subgraph "Usuarios"
        U[Usuarios Web]
        M[Usuarios Móvil]
    end
    
    subgraph "Frontend Layer"
        WEB[Admin Panel<br/>Vue.js 3 + Vite<br/>Puerto 8080]
    end
    
    subgraph "API Gateway Layer"
        GW[API Gateway<br/>Traefik<br/>Puerto 80/443]
    end
    
    subgraph "Application Services"
        API[API Service<br/>FastAPI<br/>Puerto 8000]
        SCRAPER[Scraper Service<br/>Python + Scrapy<br/>Workers]
        NORM[Normalizer Service<br/>Python<br/>Workers]
        VERIF[Verifier Service<br/>Python<br/>Workers]
        NOTIF[Notifier Service<br/>Python<br/>Workers]
    end
    
    subgraph "Data Layer"
        DB[(PostgreSQL 15<br/>Puerto 5432)]
        CACHE[(Redis 7<br/>Puerto 6379)]
    end
    
    subgraph "Message Layer"
        MQ[RabbitMQ<br/>Puerto 5672]
    end
    
    subgraph "Observability"
        PROM[Prometheus<br/>Puerto 9090]
        GRAF[Grafana<br/>Puerto 3000]
    end
    
    U -->|HTTPS| GW
    M -->|HTTPS| GW
    GW -->|Proxy| WEB
    GW -->|Proxy| API
    
    WEB -->|REST API| API
    API -->|Read/Write| DB
    API -->|Cache| CACHE
    
    SCRAPER -->|Publish raw events| MQ
    SCRAPER -->|Store raw| DB
    SCRAPER -->|Rate limit| CACHE
    
    MQ -->|Consume raw| NORM
    NORM -->|Publish normalized| MQ
    NORM -->|Store events| DB
    
    MQ -->|Consume normalized| VERIF
    VERIF -->|Update status| DB
    VERIF -->|Publish confirmed| MQ
    
    MQ -->|Consume confirmed| NOTIF
    NOTIF -->|Read subscriptions| DB
    NOTIF -->|Track delivery| DB
    
    API -->|Metrics| PROM
    SCRAPER -->|Metrics| PROM
    NORM -->|Metrics| PROM
    VERIF -->|Metrics| PROM
    NOTIF -->|Metrics| PROM
    
    PROM -->|Visualize| GRAF
    
    style GW fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style API fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style SCRAPER fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style NORM fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style VERIF fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style NOTIF fill:#4A90E2,stroke:#2E5C8A,color:#fff
    style DB fill:#9B59B6,stroke:#6C3483,color:#fff
    style CACHE fill:#9B59B6,stroke:#6C3483,color:#fff
    style MQ fill:#F39C12,stroke:#B8860B,color:#fff
```

## 3. Diagrama de Componentes - Scraper Service (C4 Level 3)

```mermaid
graph TB
    subgraph "Scraper Service"
        SCHED[Scheduler<br/>APScheduler]
        
        subgraph "Scrapers"
            SC1[Sismo Scraper<br/>Scrapy]
            SC2[Lluvia Scraper<br/>Playwright]
            SC3[Corte Scraper<br/>BeautifulSoup]
        end
        
        PARSER[Parser Manager<br/>CSS/XPath/Regex]
        RATE[Rate Limiter<br/>Redis-based]
        RETRY[Retry Handler<br/>Exponential Backoff]
        VALID[Raw Validator]
    end
    
    DB[(PostgreSQL<br/>sources, raw_events)]
    CACHE[(Redis<br/>rate limits)]
    MQ[RabbitMQ<br/>raw_events queue]
    
    SCHED -->|Trigger by frequency| SC1
    SCHED -->|Trigger by frequency| SC2
    SCHED -->|Trigger by frequency| SC3
    
    SC1 -->|Extract| PARSER
    SC2 -->|Extract| PARSER
    SC3 -->|Extract| PARSER
    
    PARSER -->|Check rate| RATE
    RATE -->|Get/Set counters| CACHE
    
    PARSER -->|On failure| RETRY
    RETRY -->|Backoff| PARSER
    
    PARSER -->|Validate| VALID
    VALID -->|Store raw| DB
    VALID -->|Publish| MQ
    
    style SCHED fill:#4ECDC4,stroke:#2A9D8F,color:#fff
    style SC1 fill:#95E1D3,stroke:#38A3A5,color:#000
    style SC2 fill:#95E1D3,stroke:#38A3A5,color:#000
    style SC3 fill:#95E1D3,stroke:#38A3A5,color:#000
```

## 4. Flujo de Datos Event-Driven

```mermaid
sequenceDiagram
    participant S as Scraper Service
    participant MQ as RabbitMQ
    participant N as Normalizer
    participant V as Verifier
    participant NT as Notifier
    participant DB as PostgreSQL
    participant EXT as Canales Externos
    
    Note over S: Ejecución programada
    S->>S: Fetch página oficial
    S->>DB: Store raw_event
    S->>MQ: Publish(raw_events_queue)
    
    MQ->>N: Consume raw event
    N->>N: Transform to schema
    N->>N: Generate dedup_hash
    N->>DB: Store/Update event
    N->>MQ: Publish(normalized_queue)
    
    MQ->>V: Consume normalized
    V->>V: Apply scoring rules
    V->>DB: Check domain whitelist
    V->>DB: Check duplicates
    V->>V: Calculate confidence score
    V->>DB: Update event.status
    
    alt Status = CONFIRMADO
        V->>MQ: Publish(confirmed_queue)
        MQ->>NT: Consume confirmed
        NT->>DB: Get subscriptions
        NT->>EXT: Send Telegram
        NT->>EXT: Send Email
        NT->>DB: Log notification
    else Status = EN_VERIFICACION
        V->>DB: Mark for review
    end
```

## 5. Arquitectura de Despliegue - Docker Compose

```mermaid
graph TB
    subgraph "Docker Host"
        subgraph "Network: sacv_network"
            
            subgraph "Reverse Proxy"
                TRAEFIK[traefik:3.0<br/>Ports: 80, 443, 8080]
            end
            
            subgraph "Frontend"
                ADMIN[admin-panel<br/>nginx:alpine<br/>Vue.js build]
            end
            
            subgraph "Backend Services"
                API[api-gateway<br/>Python:3.11-slim<br/>FastAPI]
                SCRAPER[scraper-service<br/>Python:3.11-slim<br/>Scrapy + Playwright]
                NORM[normalizer<br/>Python:3.11-slim]
                VERIF[verifier<br/>Python:3.11-slim]
                NOTIF[notifier<br/>Python:3.11-slim]
            end
            
            subgraph "Data Services"
                PG[(postgres:15-alpine<br/>Volume: pg_data)]
                REDIS[(redis:7-alpine<br/>Volume: redis_data)]
            end
            
            subgraph "Message Broker"
                RABBIT[rabbitmq:3-management<br/>Ports: 5672, 15672<br/>Volume: rabbit_data]
            end
            
            subgraph "Monitoring"
                PROM[prometheus:latest<br/>Volume: prom_data]
                GRAF[grafana:latest<br/>Volume: grafana_data]
            end
        end
    end
    
    EXT[Internet] -->|HTTPS| TRAEFIK
    
    TRAEFIK -->|/admin| ADMIN
    TRAEFIK -->|/api| API
    TRAEFIK -->|/grafana| GRAF
    
    ADMIN -->|REST| API
    API --> PG
    API --> REDIS
    
    SCRAPER --> PG
    SCRAPER --> REDIS
    SCRAPER --> RABBIT
    
    RABBIT --> NORM
    NORM --> PG
    NORM --> RABBIT
    
    RABBIT --> VERIF
    VERIF --> PG
    VERIF --> RABBIT
    
    RABBIT --> NOTIF
    NOTIF --> PG
    
    API --> PROM
    SCRAPER --> PROM
    NORM --> PROM
    VERIF --> PROM
    NOTIF --> PROM
    
    PROM --> GRAF
    
    style TRAEFIK fill:#FF6B6B,stroke:#C92A2A,color:#fff
    style PG fill:#336791,stroke:#1A3A52,color:#fff
    style REDIS fill:#DC382D,stroke:#8B1E1E,color:#fff
    style RABBIT fill:#FF6600,stroke:#CC5200,color:#fff
```

## 6. Modelo de Datos Simplificado

```mermaid
erDiagram
    SOURCE ||--o{ RAW_EVENT : generates
    SOURCE {
        uuid source_id PK
        string name
        string base_url
        string type
        string domain
        jsonb parser_config
        int frequency_sec
        boolean active
    }
    
    RAW_EVENT ||--|| EVENT : normalizes_to
    RAW_EVENT {
        uuid raw_id PK
        uuid source_id FK
        timestamp fetched_at
        jsonb raw_payload
        string raw_hash
    }
    
    EVENT ||--o{ NOTIFICATION : triggers
    EVENT {
        uuid event_id PK
        string type
        timestamp occurred_at
        string zone
        string severity
        string title
        text description
        string evidence_url
        uuid source_id FK
        string dedup_hash
        string status
        int score
    }
    
    USER ||--o{ SUBSCRIPTION : creates
    USER {
        uuid user_id PK
        string email
        string role
        timestamp created_at
    }
    
    SUBSCRIPTION ||--o{ NOTIFICATION : receives
    SUBSCRIPTION {
        uuid sub_id PK
        uuid user_id FK
        string type
        string zone
        string channel
        boolean active
    }
    
    NOTIFICATION {
        uuid notif_id PK
        uuid event_id FK
        uuid sub_id FK
        string channel
        string to
        timestamp sent_at
        string status
    }
    
    VERIFICATION_RULE {
        uuid rule_id PK
        string name
        int weight
        boolean enabled
    }
```

## 7. Tecnologías y Versiones (100% Free/Open Source)

| Componente | Tecnología | Versión | Licencia | Justificación |
|------------|------------|---------|----------|---------------|
| **Backend** | Python | 3.11+ | PSF | Ecosistema scraping superior |
| **Web Framework** | FastAPI | 0.109+ | MIT | Async, OpenAPI, alto rendimiento |
| **Scraping** | Scrapy | 2.11+ | BSD | Framework completo para crawling |
| **Dynamic Scraping** | Playwright | 1.40+ | Apache 2.0 | Headless browser automation |
| **HTML Parsing** | BeautifulSoup4 | 4.12+ | MIT | Simple parsing estático |
| **Database** | PostgreSQL | 15+ | PostgreSQL | ACID, JSONB, event sourcing |
| **Cache** | Redis | 7+ | BSD | Pub/sub, rate limiting |
| **Message Broker** | RabbitMQ | 3.12+ | MPL 2.0 | AMQP, reliable messaging |
| **API Gateway** | Traefik | 3.0+ | MIT | Cloud-native, auto-discovery |
| **Frontend** | Vue.js | 3.3+ | MIT | Progressive framework |
| **UI Library** | Vuetify | 3.4+ | MIT | Material Design components |
| **Build Tool** | Vite | 5.0+ | MIT | Fast dev server |
| **Container** | Docker | 24+ | Apache 2.0 | Containerization |
| **Orchestration** | Docker Compose | 2.23+ | Apache 2.0 | Multi-container apps |
| **Metrics** | Prometheus | 2.48+ | Apache 2.0 | Time-series metrics |
| **Dashboards** | Grafana | 10.2+ | AGPL 3.0 | Visualization |
| **Logging** | Structlog | 23.2+ | MIT | Structured logging |
| **Scheduler** | APScheduler | 3.10+ | MIT | Job scheduling |
| **HTTP Client** | httpx | 0.25+ | BSD | Async HTTP |
| **Telegram** | python-telegram-bot | 20.7+ | LGPL 3.0 | Telegram Bot API |
| **Email** | aiosmtplib | 3.0+ | MIT | Async SMTP |

## 8. Patrones de Arquitectura Aplicados

### Event-Driven Architecture (EDA)
- **Pub/Sub**: RabbitMQ con exchanges y queues
- **Event Sourcing**: Almacenamiento inmutable de raw_events
- **CQRS**: Separación de escritura (eventos) y lectura (API)

### Microservices Patterns
- **Service per Concern**: Scraper, Normalizer, Verifier, Notifier
- **Database per Service**: Cada servicio accede a su schema
- **API Gateway**: Traefik como punto de entrada único
- **Circuit Breaker**: Retry con exponential backoff

### Resilience Patterns
- **Retry Logic**: Exponential backoff en scrapers
- **Rate Limiting**: Redis-based para evitar bloqueos
- **Health Checks**: Liveness/readiness probes
- **Graceful Degradation**: Continuar con fuentes disponibles

## 9. Escalabilidad y Rendimiento

### Escalado Horizontal
- **Scrapers**: Múltiples workers por fuente
- **Normalizers**: Pool de workers consumiendo de queue
- **Verifiers**: Procesamiento paralelo de eventos
- **Notifiers**: Workers por canal (Telegram, Email)

### Optimizaciones
- **Caching**: Redis para respuestas API frecuentes
- **Connection Pooling**: PostgreSQL pgbouncer (opcional)
- **Async I/O**: FastAPI + httpx para operaciones no bloqueantes
- **Batch Processing**: Normalización y verificación en lotes

### Límites del Sistema (Lab Environment)
- **Eventos/día**: ~10,000
- **Usuarios concurrentes**: ~100
- **Fuentes activas**: ~10
- **Latencia scraping→notificación**: <60s (promedio)
