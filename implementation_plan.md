# Complete SRS with Technologies and Architecture

## Overview

This plan outlines the generation of a comprehensive Software Requirements Specification (SRS) document for the Community Verified Alert System (SACV). The document will include modern technology stack recommendations, detailed architecture diagrams, and implementation guidelines based on current industry best practices for 2026.

## User Review Required

> [!IMPORTANT]
> **Technology Stack Selection**: The proposed stack prioritizes open-source, cloud-native technologies suitable for academic/laboratory environments. If you have specific infrastructure constraints (cloud provider, budget, existing systems), please provide feedback.

> [!IMPORTANT]
> **Architecture Complexity**: The proposed architecture follows microservices patterns with event-driven communication. For a simpler MVP, we can start with a monolithic approach and evolve later.

## Proposed Changes

### Technology Stack

#### Backend Services
- **Language**: Python 3.11+
  - **Justification**: Superior ecosystem for web scraping (Scrapy, BeautifulSoup, Playwright), data processing (Pandas), and rapid development
  - **Alternatives**: Node.js for real-time performance (if needed later)

- **Web Framework**: FastAPI
  - **Justification**: Modern async framework, automatic OpenAPI documentation, excellent performance, type hints support
  - **Use**: API Gateway, Admin Panel Backend

- **Web Scraping**: 
  - **Scrapy**: For structured, large-scale crawling with built-in middleware
  - **Playwright**: For JavaScript-heavy dynamic content
  - **BeautifulSoup + Requests**: For simple static pages

#### Database Layer
- **Primary Database**: PostgreSQL 15+
  - **Justification**: ACID compliance for event integrity, JSONB for flexible event payloads, LISTEN/NOTIFY for real-time updates, excellent for event sourcing
  - **Schema**: Relational for core entities, JSONB for event payloads

- **Cache Layer**: Redis 7+
  - **Justification**: Rate limiting, session management, pub/sub for real-time notifications
  - **Use**: Scraper rate limits, API response caching, message queue

#### Message Broker
- **Apache Kafka** (lightweight deployment) or **RabbitMQ**
  - **Justification**: Event-driven architecture, decoupling services, reliable message delivery
  - **Use**: Event streaming between scrapers → normalizer → verifier → notifier
  - **Recommendation**: RabbitMQ for simpler setup in lab environment

#### Notification Services
- **Telegram Bot API**: Primary channel (free, easy integration)
- **SMTP (SendGrid/Mailgun)**: Email notifications
- **Twilio API**: WhatsApp Business (Phase III, optional)

#### API Gateway & Reverse Proxy
- **Traefik 3.0**
  - **Justification**: Cloud-native, automatic service discovery, built-in Let's Encrypt, excellent for Docker/Kubernetes
  - **Alternative**: Kong (if advanced plugins needed)

#### Frontend
- **Framework**: Vue.js 3 + Vite
  - **Justification**: Progressive framework, excellent for admin panels, smaller learning curve
  - **UI Library**: Vuetify 3 (Material Design components)

#### Containerization & Orchestration
- **Docker + Docker Compose**: For development and lab deployment
- **Kubernetes** (optional): For production-grade scaling (Phase III)

#### Observability
- **Logging**: Structured JSON logs with Python `structlog`
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry (optional for Phase III)

---

### System Architecture

#### [NEW] [architecture_overview.md](file:///C:/Users/charlieact7/.gemini/antigravity/brain/bc03da87-7a2b-407c-9fda-df38611d7c7f/architecture_overview.md)

Comprehensive architecture document including:
- High-level system architecture diagram (C4 Context)
- Microservices component diagram
- Event-driven data flow
- Deployment architecture

#### [NEW] [technology_justification.md](file:///C:/Users/charlieact7/.gemini/antigravity/brain/bc03da87-7a2b-407c-9fda-df38611d7c7f/technology_justification.md)

Detailed justification for each technology choice with:
- Comparison matrices
- Trade-off analysis
- Scalability considerations

#### [MODIFY] [srs_sistema_de_alertas_comunitarias_verificadas_scraping_verificacion_notificaciones.md](file:///d:/PracticasClase/UIDE/Laboratorio_ArquitecturaTI/sistema_alertas/srs_sistema_de_alertas_comunitarias_verificadas_scraping_verificacion_notificaciones.md)

Enhanced SRS document with:
- Section 8: Technology Stack (detailed specifications)
- Section 9: System Architecture (diagrams and descriptions)
- Section 10: Deployment Strategy (Docker Compose configuration)
- Section 11: Development Roadmap (phased implementation)
- Updated NFRs with specific technology constraints

---

### Architecture Components

#### Microservices Breakdown

1. **Scraper Service** (Python + Scrapy/Playwright)
   - Configurable scrapers per source
   - Rate limiting and retry logic
   - Stores raw events to PostgreSQL
   - Publishes to message queue

2. **Normalizer Service** (Python + FastAPI)
   - Consumes raw events from queue
   - Transforms to common schema
   - Validates required fields
   - Generates deduplication hash
   - Publishes normalized events

3. **Verification Service** (Python)
   - Applies scoring rules
   - Checks domain whitelist
   - Cross-source corroboration
   - Updates event status
   - Triggers notifications for CONFIRMED events

4. **Notification Service** (Python)
   - Multi-channel dispatcher (Telegram, Email, WhatsApp)
   - Subscription management
   - Delivery tracking
   - Retry logic

5. **API Gateway** (FastAPI)
   - REST API endpoints
   - Authentication/Authorization (JWT)
   - Rate limiting
   - Request validation

6. **Admin Panel** (Vue.js 3)
   - Source management
   - Event monitoring
   - User management
   - Analytics dashboard

7. **Database Service** (PostgreSQL)
   - Event store
   - User/subscription data
   - Audit logs

8. **Cache Service** (Redis)
   - Session storage
   - Rate limit counters
   - Real-time pub/sub

---

### Deployment Architecture

#### Docker Compose Services

```yaml
services:
  - traefik (reverse proxy)
  - postgres (database)
  - redis (cache)
  - rabbitmq (message broker)
  - scraper-service
  - normalizer-service
  - verifier-service
  - notifier-service
  - api-gateway
  - admin-panel (nginx serving Vue.js build)
  - prometheus (metrics)
  - grafana (dashboards)
```

---

## Verification Plan

### Documentation Review
- **Manual Review**: User reviews the generated SRS document for completeness, accuracy, and alignment with project requirements
- **Architecture Validation**: User validates that the proposed architecture diagrams accurately represent the system design
- **Technology Approval**: User confirms the technology stack is appropriate for the academic/lab environment

### Diagram Validation
- **Mermaid Rendering**: Verify all Mermaid diagrams render correctly in the markdown viewer
- **C4 Model Compliance**: Ensure architecture diagrams follow C4 model conventions (Context, Container, Component)

### Completeness Check
- **IEEE 830 Compliance**: Verify the SRS follows IEEE 830 structure
- **All Sections Present**: Confirm all required sections are included (Technology Stack, Architecture, Deployment)
- **Traceability**: Ensure requirements are traceable to architectural components
