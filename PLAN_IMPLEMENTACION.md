# Plan de Implementación - Sistema de Alertas Comunitarias Verificadas (SACV)

## 📋 Índice
1. [Preparación del Entorno](#1-preparación-del-entorno)
2. [Fase I - Fundamentos](#2-fase-i---fundamentos-semanas-1-2)
3. [Fase II - Pipeline Completo](#3-fase-ii---pipeline-completo-semanas-3-4)
4. [Fase III - Producción](#4-fase-iii---producción-semanas-5-6)
5. [Verificación y Testing](#5-verificación-y-testing)
6. [Despliegue](#6-despliegue)

---

## 1. Preparación del Entorno

### 1.1 Requisitos del Sistema

**Hardware mínimo:**
- CPU: 4 cores
- RAM: 8 GB
- Disco: 50 GB SSD
- Red: Conexión estable a Internet

**Software requerido:**
- Sistema Operativo: Ubuntu 22.04 LTS / Windows 11 con WSL2 / macOS
- Docker Desktop 24+ o Docker Engine
- Docker Compose 2.23+
- Git 2.40+
- Editor de código (VS Code recomendado)

### 1.2 Instalación de Herramientas

#### En Ubuntu/WSL2:
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo apt install docker-compose-plugin

# Instalar Git
sudo apt install git

# Verificar instalaciones
docker --version
docker compose version
git --version
```

#### En Windows (con WSL2):
1. Instalar WSL2: `wsl --install`
2. Instalar Docker Desktop desde https://www.docker.com/products/docker-desktop
3. Habilitar integración con WSL2 en Docker Desktop

### 1.3 Crear Estructura del Proyecto

```bash
# Crear directorio del proyecto
mkdir -p ~/sistema_alertas
cd ~/sistema_alertas

# Inicializar repositorio Git
git init

# Crear estructura de directorios
mkdir -p services/{scraper,normalizer,verifier,notifier,api-gateway,admin-panel}
mkdir -p config/{traefik,prometheus,grafana}
mkdir -p data/{postgres,redis,rabbitmq}
mkdir -p docs
mkdir -p scripts

# Crear archivos base
touch docker-compose.yml
touch .env.example
touch .gitignore
touch README.md
```

### 1.4 Configurar .gitignore

```bash
cat > .gitignore << 'EOF'
# Environment variables
.env

# Data directories
data/postgres/*
data/redis/*
data/rabbitmq/*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Docker
*.pid
EOF
```

---

## 2. Fase I - Fundamentos (Semanas 1-2)

### 2.1 Configurar Base de Datos PostgreSQL

#### Crear schema SQL inicial

```bash
mkdir -p services/database
cat > services/database/init.sql << 'EOF'
-- Crear extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de fuentes
CREATE TABLE sources (
    source_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    base_url TEXT NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('sismo', 'lluvia', 'corte')),
    domain VARCHAR(255) NOT NULL,
    parser_config JSONB NOT NULL,
    frequency_sec INTEGER NOT NULL DEFAULT 300,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de eventos crudos
CREATE TABLE raw_events (
    raw_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_id UUID REFERENCES sources(source_id),
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_payload JSONB NOT NULL,
    raw_hash VARCHAR(64) UNIQUE NOT NULL
);

-- Tabla de eventos normalizados
CREATE TABLE events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    type VARCHAR(50) NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    zone VARCHAR(255),
    severity VARCHAR(50),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    evidence_url TEXT,
    source_id UUID REFERENCES sources(source_id),
    dedup_hash VARCHAR(64) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'NO_VERIFICADO' CHECK (status IN ('CONFIRMADO', 'EN_VERIFICACION', 'NO_VERIFICADO')),
    score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de reglas de verificación
CREATE TABLE verification_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    weight INTEGER NOT NULL,
    enabled BOOLEAN DEFAULT true
);

-- Tabla de usuarios
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'operator', 'user')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de suscripciones
CREATE TABLE subscriptions (
    sub_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    type VARCHAR(50),
    zone VARCHAR(255),
    channel VARCHAR(50) NOT NULL CHECK (channel IN ('telegram', 'email', 'whatsapp')),
    channel_id VARCHAR(255) NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de notificaciones
CREATE TABLE notifications (
    notif_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID REFERENCES events(event_id),
    sub_id UUID REFERENCES subscriptions(sub_id),
    channel VARCHAR(50) NOT NULL,
    to_address VARCHAR(255) NOT NULL,
    sent_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    error_message TEXT
);

-- Tabla de auditoría
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),
    action VARCHAR(255) NOT NULL,
    entity VARCHAR(100) NOT NULL,
    entity_id UUID,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Índices para optimización
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_occurred_at ON events(occurred_at);
CREATE INDEX idx_raw_events_source ON raw_events(source_id);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_notifications_event ON notifications(event_id);

-- Insertar reglas de verificación por defecto
INSERT INTO verification_rules (name, weight, enabled) VALUES
    ('Dominio en lista blanca', 40, true),
    ('Evidencia URL válida', 15, true),
    ('Timestamp reciente', 15, true),
    ('Campos completos', 10, true),
    ('Corroboración cruzada', 20, true);

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para updated_at
CREATE TRIGGER update_sources_updated_at BEFORE UPDATE ON sources
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
EOF
```

### 2.2 Crear Docker Compose Base

```yaml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # Base de datos PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: sacv_postgres
    environment:
      POSTGRES_DB: sacv_db
      POSTGRES_USER: sacv_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./services/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - sacv_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sacv_user -d sacv_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Cache Redis
  redis:
    image: redis:7-alpine
    container_name: sacv_redis
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
    ports:
      - "6379:6379"
    networks:
      - sacv_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    restart: unless-stopped

  # Message Broker RabbitMQ
  rabbitmq:
    image: rabbitmq:3.12-management-alpine
    container_name: sacv_rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: sacv
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - ./data/rabbitmq:/var/lib/rabbitmq
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - sacv_network
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
    restart: unless-stopped

networks:
  sacv_network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  rabbitmq_data:
EOF
```

### 2.3 Crear archivo .env.example

```bash
cat > .env.example << 'EOF'
# Database
DB_PASSWORD=change_this_password

# RabbitMQ
RABBITMQ_PASSWORD=change_this_password

# JWT Secret
JWT_SECRET=change_this_to_random_secret_key

# Telegram Bot (obtener de @BotFather)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Email SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Grafana
GRAFANA_PASSWORD=admin
EOF
```

### 2.4 Desarrollar Primer Scraper (Instituto Geofísico)

#### Estructura del servicio scraper

```bash
cd services/scraper
cat > requirements.txt << 'EOF'
scrapy==2.11.0
playwright==1.40.0
beautifulsoup4==4.12.2
requests==2.31.0
psycopg2-binary==2.9.9
redis==5.0.1
pika==1.3.2
python-dotenv==1.0.0
APScheduler==3.10.4
structlog==23.2.0
EOF
```

#### Crear Dockerfile

```dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores para Playwright (solo Chromium)
RUN playwright install chromium
RUN playwright install-deps chromium

# Copiar código
COPY src/ ./src/

# Comando por defecto
CMD ["python", "src/main.py"]
EOF
```

#### Crear scraper básico

```bash
mkdir -p src/scrapers
cat > src/scrapers/igepn_scraper.py << 'EOF'
"""
Scraper para Instituto Geofísico - Sismos
URL: https://www.igepn.edu.ec/servicios/noticias
"""
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()

class IGEPNScraper:
    def __init__(self, source_config: Dict):
        self.source_id = source_config['source_id']
        self.base_url = source_config['base_url']
        self.parser_config = source_config['parser_config']
        
    def scrape(self) -> Optional[Dict]:
        """Ejecuta el scraping y retorna evento crudo"""
        try:
            logger.info("scraping_started", source="IGEPN", url=self.base_url)
            
            # Hacer request
            response = requests.get(
                self.base_url,
                headers={'User-Agent': 'Mozilla/5.0 (compatible; SACV/1.0)'},
                timeout=30
            )
            response.raise_for_status()
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información (ajustar selectores según sitio real)
            title_elem = soup.select_one(self.parser_config.get('title_selector', 'h1'))
            date_elem = soup.select_one(self.parser_config.get('date_selector', '.date'))
            content_elem = soup.select_one(self.parser_config.get('content_selector', '.content'))
            
            if not title_elem:
                logger.warning("no_title_found", url=self.base_url)
                return None
            
            # Construir payload crudo
            raw_payload = {
                'title': title_elem.get_text(strip=True),
                'date': date_elem.get_text(strip=True) if date_elem else None,
                'content': content_elem.get_text(strip=True) if content_elem else None,
                'url': self.base_url,
                'html_snippet': str(title_elem)[:500]
            }
            
            # Generar hash único
            raw_hash = hashlib.sha256(
                json.dumps(raw_payload, sort_keys=True).encode()
            ).hexdigest()
            
            event = {
                'source_id': self.source_id,
                'fetched_at': datetime.utcnow().isoformat(),
                'raw_payload': raw_payload,
                'raw_hash': raw_hash
            }
            
            logger.info("scraping_completed", source="IGEPN", hash=raw_hash[:8])
            return event
            
        except Exception as e:
            logger.error("scraping_failed", source="IGEPN", error=str(e))
            return None
EOF
```

#### Crear main.py del scraper

```bash
cat > src/main.py << 'EOF'
import os
import time
import json
from datetime import datetime
import psycopg2
import pika
import redis
import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from scrapers.igepn_scraper import IGEPNScraper

# Configurar logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Configuración
DATABASE_URL = os.getenv('DATABASE_URL')
REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://sacv:password@rabbitmq:5672')

class ScraperService:
    def __init__(self):
        self.db_conn = None
        self.redis_client = None
        self.rabbitmq_conn = None
        self.rabbitmq_channel = None
        self.scheduler = BlockingScheduler()
        
    def connect_db(self):
        """Conectar a PostgreSQL"""
        try:
            self.db_conn = psycopg2.connect(DATABASE_URL)
            logger.info("database_connected")
        except Exception as e:
            logger.error("database_connection_failed", error=str(e))
            raise
    
    def connect_redis(self):
        """Conectar a Redis"""
        try:
            self.redis_client = redis.from_url(REDIS_URL)
            self.redis_client.ping()
            logger.info("redis_connected")
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            raise
    
    def connect_rabbitmq(self):
        """Conectar a RabbitMQ"""
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            self.rabbitmq_conn = pika.BlockingConnection(params)
            self.rabbitmq_channel = self.rabbitmq_conn.channel()
            
            # Declarar queue
            self.rabbitmq_channel.queue_declare(queue='raw_events', durable=True)
            logger.info("rabbitmq_connected")
        except Exception as e:
            logger.error("rabbitmq_connection_failed", error=str(e))
            raise
    
    def get_active_sources(self):
        """Obtener fuentes activas de la BD"""
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT source_id, name, base_url, type, domain, parser_config, frequency_sec
            FROM sources
            WHERE active = true
        """)
        sources = []
        for row in cursor.fetchall():
            sources.append({
                'source_id': str(row[0]),
                'name': row[1],
                'base_url': row[2],
                'type': row[3],
                'domain': row[4],
                'parser_config': row[5],
                'frequency_sec': row[6]
            })
        cursor.close()
        return sources
    
    def save_raw_event(self, event):
        """Guardar evento crudo en BD"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO raw_events (source_id, fetched_at, raw_payload, raw_hash)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (raw_hash) DO NOTHING
                RETURNING raw_id
            """, (
                event['source_id'],
                event['fetched_at'],
                json.dumps(event['raw_payload']),
                event['raw_hash']
            ))
            result = cursor.fetchone()
            self.db_conn.commit()
            
            if result:
                logger.info("raw_event_saved", raw_id=str(result[0]))
                return str(result[0])
            else:
                logger.info("raw_event_duplicate", hash=event['raw_hash'][:8])
                return None
        except Exception as e:
            self.db_conn.rollback()
            logger.error("save_raw_event_failed", error=str(e))
            return None
        finally:
            cursor.close()
    
    def publish_to_queue(self, event):
        """Publicar evento a RabbitMQ"""
        try:
            self.rabbitmq_channel.basic_publish(
                exchange='',
                routing_key='raw_events',
                body=json.dumps(event),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Mensaje persistente
                )
            )
            logger.info("event_published_to_queue", hash=event['raw_hash'][:8])
        except Exception as e:
            logger.error("publish_failed", error=str(e))
    
    def scrape_source(self, source_config):
        """Ejecutar scraping de una fuente"""
        logger.info("scraping_job_started", source=source_config['name'])
        
        # Verificar rate limit en Redis
        rate_key = f"rate_limit:{source_config['source_id']}"
        if self.redis_client.exists(rate_key):
            logger.warning("rate_limited", source=source_config['name'])
            return
        
        # Ejecutar scraper según tipo
        if source_config['type'] == 'sismo':
            scraper = IGEPNScraper(source_config)
            event = scraper.scrape()
            
            if event:
                # Guardar en BD
                raw_id = self.save_raw_event(event)
                
                if raw_id:
                    # Publicar a queue
                    self.publish_to_queue(event)
                    
                    # Setear rate limit (60 segundos)
                    self.redis_client.setex(rate_key, 60, "1")
    
    def schedule_sources(self):
        """Programar scrapers según frecuencia"""
        sources = self.get_active_sources()
        
        for source in sources:
            self.scheduler.add_job(
                self.scrape_source,
                'interval',
                seconds=source['frequency_sec'],
                args=[source],
                id=source['source_id'],
                replace_existing=True
            )
            logger.info("source_scheduled", 
                       source=source['name'], 
                       frequency=source['frequency_sec'])
    
    def run(self):
        """Iniciar servicio"""
        logger.info("scraper_service_starting")
        
        # Conectar a servicios
        self.connect_db()
        self.connect_redis()
        self.connect_rabbitmq()
        
        # Programar fuentes
        self.schedule_sources()
        
        # Iniciar scheduler
        logger.info("scheduler_started")
        self.scheduler.start()

if __name__ == "__main__":
    service = ScraperService()
    service.run()
EOF
```

### 2.5 Crear API Gateway Básico

```bash
cd ../api-gateway
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.25.0
psycopg2-binary==2.9.9
pydantic==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
structlog==23.2.0
EOF
```

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

```bash
mkdir -p src
cat > src/main.py << 'EOF'
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import psycopg2
import os
from pydantic import BaseModel

app = FastAPI(
    title="SACV API",
    description="Sistema de Alertas Comunitarias Verificadas",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# Models
class AlertResponse(BaseModel):
    event_id: str
    type: str
    occurred_at: datetime
    zone: Optional[str]
    severity: Optional[str]
    title: str
    description: Optional[str]
    evidence_url: Optional[str]
    status: str
    score: int
    created_at: datetime

# Endpoints
@app.get("/")
def read_root():
    return {"message": "SACV API v1.0", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/alerts", response_model=List[AlertResponse])
def get_alerts(
    type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    status: Optional[str] = Query("CONFIRMADO"),
    limit: int = Query(50, le=100),
    db = Depends(get_db)
):
    """Obtener lista de alertas"""
    cursor = db.cursor()
    
    query = """
        SELECT event_id, type, occurred_at, zone, severity, 
               title, description, evidence_url, status, score, created_at
        FROM events
        WHERE 1=1
    """
    params = []
    
    if type:
        query += " AND type = %s"
        params.append(type)
    
    if zone:
        query += " AND zone = %s"
        params.append(zone)
    
    if status:
        query += " AND status = %s"
        params.append(status)
    
    query += " ORDER BY occurred_at DESC LIMIT %s"
    params.append(limit)
    
    cursor.execute(query, params)
    
    alerts = []
    for row in cursor.fetchall():
        alerts.append(AlertResponse(
            event_id=str(row[0]),
            type=row[1],
            occurred_at=row[2],
            zone=row[3],
            severity=row[4],
            title=row[5],
            description=row[6],
            evidence_url=row[7],
            status=row[8],
            score=row[9],
            created_at=row[10]
        ))
    
    cursor.close()
    return alerts

@app.get("/api/alerts/{event_id}", response_model=AlertResponse)
def get_alert_detail(event_id: str, db = Depends(get_db)):
    """Obtener detalle de una alerta"""
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT event_id, type, occurred_at, zone, severity, 
               title, description, evidence_url, status, score, created_at
        FROM events
        WHERE event_id = %s
    """, (event_id,))
    
    row = cursor.fetchone()
    cursor.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return AlertResponse(
        event_id=str(row[0]),
        type=row[1],
        occurred_at=row[2],
        zone=row[3],
        severity=row[4],
        title=row[5],
        description=row[6],
        evidence_url=row[7],
        status=row[8],
        score=row[9],
        created_at=row[10]
    )

@app.get("/api/stats")
def get_stats(db = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    cursor = db.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) FILTER (WHERE status = 'CONFIRMADO') as confirmados,
            COUNT(*) FILTER (WHERE status = 'EN_VERIFICACION') as en_verificacion,
            COUNT(*) FILTER (WHERE status = 'NO_VERIFICADO') as no_verificados,
            COUNT(DISTINCT source_id) as fuentes_activas
        FROM events
        WHERE created_at > NOW() - INTERVAL '7 days'
    """)
    
    row = cursor.fetchone()
    cursor.close()
    
    return {
        "confirmados": row[0],
        "en_verificacion": row[1],
        "no_verificados": row[2],
        "fuentes_activas": row[3]
    }
EOF
```

### 2.6 Actualizar Docker Compose con nuevos servicios

```bash
cd ../..
cat >> docker-compose.yml << 'EOF'

  # Scraper Service
  scraper:
    build: ./services/scraper
    container_name: sacv_scraper
    environment:
      DATABASE_URL: postgresql://sacv_user:${DB_PASSWORD}@postgres:5432/sacv_db
      REDIS_URL: redis://redis:6379
      RABBITMQ_URL: amqp://sacv:${RABBITMQ_PASSWORD}@rabbitmq:5672
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
    networks:
      - sacv_network
    restart: unless-stopped

  # API Gateway
  api-gateway:
    build: ./services/api-gateway
    container_name: sacv_api
    environment:
      DATABASE_URL: postgresql://sacv_user:${DB_PASSWORD}@postgres:5432/sacv_db
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - sacv_network
    restart: unless-stopped
EOF
```

### 2.7 Insertar fuente de prueba

```bash
cat > scripts/insert_test_source.sql << 'EOF'
INSERT INTO sources (name, base_url, type, domain, parser_config, frequency_sec, active)
VALUES (
    'Instituto Geofísico - Sismos',
    'https://www.igepn.edu.ec/servicios/noticias',
    'sismo',
    'igepn.edu.ec',
    '{
        "title_selector": "h1.title",
        "date_selector": ".date",
        "content_selector": ".content"
    }'::jsonb,
    300,
    true
);
EOF
```

### 2.8 Probar Fase I

```bash
# Copiar .env.example a .env y configurar
cp .env.example .env
nano .env  # Editar con valores reales

# Iniciar servicios
docker-compose up -d postgres redis rabbitmq

# Esperar a que estén listos
sleep 10

# Insertar fuente de prueba
docker exec -i sacv_postgres psql -U sacv_user -d sacv_db < scripts/insert_test_source.sql

# Iniciar scraper y API
docker-compose up -d scraper api-gateway

# Ver logs
docker-compose logs -f scraper

# Probar API
curl http://localhost:8000/
curl http://localhost:8000/api/alerts
```

---

## 3. Fase II - Pipeline Completo (Semanas 3-4)

### 3.1 Desarrollar Normalizer Service

```bash
cd services/normalizer
cat > requirements.txt << 'EOF'
pika==1.3.2
psycopg2-binary==2.9.9
pydantic==2.5.0
python-dateutil==2.8.2
structlog==23.2.0
EOF
```

```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

CMD ["python", "src/main.py"]
EOF
```

```bash
mkdir -p src
cat > src/main.py << 'EOF'
import os
import json
import hashlib
from datetime import datetime
from dateutil import parser as date_parser
import psycopg2
import pika
import structlog
from pydantic import BaseModel, ValidationError

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

DATABASE_URL = os.getenv('DATABASE_URL')
RABBITMQ_URL = os.getenv('RABBITMQ_URL')

class NormalizedEvent(BaseModel):
    type: str
    occurred_at: datetime
    zone: str = None
    severity: str = None
    title: str
    description: str = None
    evidence_url: str
    source_id: str
    dedup_hash: str

class NormalizerService:
    def __init__(self):
        self.db_conn = psycopg2.connect(DATABASE_URL)
        
        params = pika.URLParameters(RABBITMQ_URL)
        self.rabbitmq_conn = pika.BlockingConnection(params)
        self.channel = self.rabbitmq_conn.channel()
        
        # Declarar queues
        self.channel.queue_declare(queue='raw_events', durable=True)
        self.channel.queue_declare(queue='normalized_events', durable=True)
        
        logger.info("normalizer_service_started")
    
    def normalize_event(self, raw_event):
        """Normalizar evento crudo"""
        try:
            payload = raw_event['raw_payload']
            
            # Extraer y normalizar fecha
            occurred_at = datetime.utcnow()
            if payload.get('date'):
                try:
                    occurred_at = date_parser.parse(payload['date'])
                except:
                    pass
            
            # Construir evento normalizado
            normalized = {
                'type': 'sismo',  # Determinar según fuente
                'occurred_at': occurred_at.isoformat(),
                'zone': self.extract_zone(payload),
                'severity': self.extract_severity(payload),
                'title': payload.get('title', 'Sin título'),
                'description': payload.get('content'),
                'evidence_url': payload.get('url'),
                'source_id': raw_event['source_id']
            }
            
            # Generar hash de deduplicación
            dedup_str = f"{normalized['type']}_{normalized['zone']}_{normalized['occurred_at'][:10]}"
            normalized['dedup_hash'] = hashlib.sha256(dedup_str.encode()).hexdigest()
            
            # Validar con Pydantic
            event = NormalizedEvent(**normalized)
            
            logger.info("event_normalized", hash=event.dedup_hash[:8])
            return event.dict()
            
        except ValidationError as e:
            logger.error("validation_failed", error=str(e))
            return None
        except Exception as e:
            logger.error("normalization_failed", error=str(e))
            return None
    
    def extract_zone(self, payload):
        """Extraer zona del evento"""
        # Lógica específica según fuente
        content = payload.get('content', '') + payload.get('title', '')
        
        # Buscar provincias ecuatorianas
        provincias = ['Pichincha', 'Guayas', 'Azuay', 'Manabí', 'Esmeraldas']
        for prov in provincias:
            if prov.lower() in content.lower():
                return prov
        
        return 'Nacional'
    
    def extract_severity(self, payload):
        """Extraer severidad del evento"""
        content = (payload.get('content', '') + payload.get('title', '')).lower()
        
        if any(word in content for word in ['fuerte', 'alto', 'severo']):
            return 'Alta'
        elif any(word in content for word in ['moderado', 'medio']):
            return 'Media'
        else:
            return 'Baja'
    
    def save_normalized_event(self, event):
        """Guardar evento normalizado en BD"""
        cursor = self.db_conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO events (
                    type, occurred_at, zone, severity, title, description,
                    evidence_url, source_id, dedup_hash, status, score
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'NO_VERIFICADO', 0)
                ON CONFLICT (dedup_hash) DO UPDATE
                SET updated_at = CURRENT_TIMESTAMP
                RETURNING event_id
            """, (
                event['type'],
                event['occurred_at'],
                event['zone'],
                event['severity'],
                event['title'],
                event['description'],
                event['evidence_url'],
                event['source_id'],
                event['dedup_hash']
            ))
            
            result = cursor.fetchone()
            self.db_conn.commit()
            
            if result:
                event_id = str(result[0])
                logger.info("event_saved", event_id=event_id)
                return event_id
            
        except Exception as e:
            self.db_conn.rollback()
            logger.error("save_failed", error=str(e))
            return None
        finally:
            cursor.close()
    
    def publish_normalized(self, event):
        """Publicar evento normalizado a queue"""
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key='normalized_events',
                body=json.dumps(event),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info("event_published", hash=event['dedup_hash'][:8])
        except Exception as e:
            logger.error("publish_failed", error=str(e))
    
    def callback(self, ch, method, properties, body):
        """Callback para procesar mensajes de la queue"""
        try:
            raw_event = json.loads(body)
            logger.info("processing_raw_event", hash=raw_event.get('raw_hash', '')[:8])
            
            # Normalizar
            normalized = self.normalize_event(raw_event)
            
            if normalized:
                # Guardar en BD
                event_id = self.save_normalized_event(normalized)
                
                if event_id:
                    normalized['event_id'] = event_id
                    # Publicar a siguiente queue
                    self.publish_normalized(normalized)
            
            # Acknowledge
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            logger.error("callback_error", error=str(e))
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def run(self):
        """Iniciar consumidor"""
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue='raw_events',
            on_message_callback=self.callback
        )
        
        logger.info("waiting_for_messages")
        self.channel.start_consuming()

if __name__ == "__main__":
    service = NormalizerService()
    service.run()
EOF
```

### 3.2 Desarrollar Verifier Service

*(Código similar al normalizer, aplicando reglas de scoring)*

### 3.3 Desarrollar Notifier Service con Telegram

```bash
cd ../notifier
cat > requirements.txt << 'EOF'
pika==1.3.2
psycopg2-binary==2.9.9
python-telegram-bot==20.7
aiosmtplib==3.0.1
structlog==23.2.0
EOF
```

*(Implementación del servicio de notificaciones)*

### 3.4 Desarrollar Admin Panel con Vue.js

```bash
cd ../admin-panel
npm init -y
npm install vue@3 vuetify@3 vite axios
```

*(Estructura básica de Vue.js con Vuetify)*

---

## 4. Fase III - Producción (Semanas 5-6)

### 4.1 Configurar Prometheus

```yaml
cat > config/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api-gateway'
    static_configs:
      - targets: ['api-gateway:8000']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
EOF
```

### 4.2 Configurar Grafana

*(Dashboards predefinidos para métricas del sistema)*

### 4.3 Implementar Tests

```bash
cat > services/scraper/tests/test_scraper.py << 'EOF'
import pytest
from scrapers.igepn_scraper import IGEPNScraper

def test_scraper_initialization():
    config = {
        'source_id': 'test-id',
        'base_url': 'https://example.com',
        'parser_config': {}
    }
    scraper = IGEPNScraper(config)
    assert scraper.source_id == 'test-id'
EOF
```

---

## 5. Verificación y Testing

### 5.1 Tests Unitarios

```bash
# En cada servicio
pytest tests/
```

### 5.2 Tests de Integración

```bash
# Probar pipeline completo
./scripts/test_pipeline.sh
```

### 5.3 Tests de Carga

```bash
# Usar locust o similar
locust -f tests/load_test.py
```

---

## 6. Despliegue

### 6.1 Despliegue en Laboratorio

```bash
# Iniciar todos los servicios
docker-compose up -d

# Verificar estado
docker-compose ps

# Ver logs
docker-compose logs -f
```

### 6.2 Acceso a Servicios

- **API**: http://localhost:8000
- **Admin Panel**: http://localhost:8080
- **RabbitMQ Management**: http://localhost:15672
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### 6.3 Monitoreo

```bash
# Ver métricas en tiempo real
docker stats

# Ver logs de un servicio específico
docker-compose logs -f scraper
```

---

## 7. Documentación Final

### 7.1 README.md

```markdown
# Sistema de Alertas Comunitarias Verificadas (SACV)

## Inicio Rápido

1. Clonar repositorio
2. Configurar .env
3. Ejecutar: `docker-compose up -d`
4. Acceder a: http://localhost:8000

## Arquitectura

Ver `architecture_overview.md`

## Desarrollo

Ver `PLAN_IMPLEMENTACION.md`
```

---

## 8. Checklist de Implementación

### Fase I
- [ ] Configurar entorno de desarrollo
- [ ] Crear estructura del proyecto
- [ ] Configurar PostgreSQL con schema
- [ ] Configurar Redis y RabbitMQ
- [ ] Desarrollar primer scraper (IGEPN)
- [ ] Desarrollar API Gateway básico
- [ ] Probar scraping y almacenamiento

### Fase II
- [ ] Desarrollar Normalizer Service
- [ ] Desarrollar Verifier Service
- [ ] Desarrollar Notifier Service (Telegram)
- [ ] Desarrollar 2 scrapers adicionales
- [ ] Desarrollar Admin Panel (Vue.js)
- [ ] Configurar Traefik
- [ ] Probar pipeline completo

### Fase III
- [ ] Implementar corroboración cruzada
- [ ] Agregar notificaciones Email
- [ ] Configurar Prometheus + Grafana
- [ ] Implementar health checks
- [ ] Desarrollar tests unitarios
- [ ] Desarrollar tests de integración
- [ ] Documentación completa
- [ ] Preparar demo

---

## 9. Recursos Adicionales

### Documentación
- FastAPI: https://fastapi.tiangolo.com/
- Scrapy: https://docs.scrapy.org/
- Vue.js: https://vuejs.org/
- Docker: https://docs.docker.com/

### Tutoriales
- Event-Driven Architecture: https://microservices.io/patterns/data/event-driven-architecture.html
- RabbitMQ: https://www.rabbitmq.com/getstarted.html

---

**Fin del Plan de Implementación**
