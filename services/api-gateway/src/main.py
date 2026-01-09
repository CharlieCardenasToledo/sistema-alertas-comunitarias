"""
API Gateway - Sistema de Alertas Comunitarias Verificadas
FastAPI REST API para consulta de eventos y gestión del sistema
"""
import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import RealDictCursor
import structlog

# Configurar logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
logger = structlog.get_logger()

# Configuración
DATABASE_URL = os.getenv('DATABASE_URL')

# Pool de conexiones simple
db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida de la aplicación"""
    global db_pool
    logger.info("api_gateway_starting")
    # Aquí podríamos inicializar un pool de conexiones
    yield
    logger.info("api_gateway_stopping")

# Crear aplicación FastAPI
app = FastAPI(
    title="SACV API",
    description="Sistema de Alertas Comunitarias Verificadas - API REST",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Modelos Pydantic
# ============================================================================

class RawEventResponse(BaseModel):
    """Modelo de respuesta para eventos crudos"""
    raw_id: str
    source_id: str
    fetched_at: datetime
    raw_hash: str
    title: Optional[str] = None
    url: Optional[str] = None

class EventResponse(BaseModel):
    """Modelo de respuesta para eventos normalizados"""
    event_id: str
    type: str
    occurred_at: datetime
    zone: Optional[str] = None
    severity: Optional[str] = None
    title: str
    description: Optional[str] = None
    evidence_url: Optional[str] = None
    status: str
    score: int
    created_at: datetime

class SourceResponse(BaseModel):
    """Modelo de respuesta para fuentes"""
    source_id: str
    name: str
    type: str
    domain: str
    active: bool
    frequency_sec: int

class StatsResponse(BaseModel):
    """Modelo de respuesta para estadísticas"""
    total_sources: int
    active_sources: int
    total_raw_events: int
    total_events: int
    events_by_status: dict
    last_scraping: Optional[datetime] = None

# ============================================================================
# Dependencias
# ============================================================================

def get_db():
    """Obtener conexión a la base de datos"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", tags=["Health"])
def read_root():
    """Endpoint raíz - Health check"""
    return {
        "message": "SACV API v1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Health check detallado"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        db_status = "healthy"
    except Exception as e:
        logger.error("health_check_db_failed", error=str(e))
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/raw-events", response_model=List[RawEventResponse], tags=["Events"])
def get_raw_events(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """Obtener eventos crudos (raw) capturados por los scrapers"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                raw_id::text,
                source_id::text,
                fetched_at,
                raw_hash,
                raw_payload->>'title' as title,
                raw_payload->>'url' as url
            FROM raw_events
            ORDER BY fetched_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        events = cursor.fetchall()
        
        logger.info("raw_events_fetched", count=len(events))
        
        return [dict(event) for event in events]
        
    except Exception as e:
        logger.error("get_raw_events_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching raw events")
    finally:
        cursor.close()

@app.get("/api/raw-events/{raw_id}", response_model=dict, tags=["Events"])
def get_raw_event_detail(raw_id: str, db = Depends(get_db)):
    """Obtener detalle completo de un evento crudo"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                raw_id::text,
                source_id::text,
                fetched_at,
                raw_payload,
                raw_hash
            FROM raw_events
            WHERE raw_id = %s
        """, (raw_id,))
        
        event = cursor.fetchone()
        
        if not event:
            raise HTTPException(status_code=404, detail="Raw event not found")
        
        return dict(event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_raw_event_detail_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching event detail")
    finally:
        cursor.close()

@app.get("/api/events", response_model=List[EventResponse], tags=["Events"])
def get_events(
    type: Optional[str] = Query(None),
    zone: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db = Depends(get_db)
):
    """Obtener eventos normalizados con filtros opcionales"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT 
                event_id::text,
                type,
                occurred_at,
                zone,
                severity,
                title,
                description,
                evidence_url,
                status,
                score,
                created_at
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
        
        query += " ORDER BY occurred_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        events = cursor.fetchall()
        
        logger.info("events_fetched", count=len(events), filters={
            "type": type, "zone": zone, "status": status
        })
        
        return [dict(event) for event in events]
        
    except Exception as e:
        logger.error("get_events_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching events")
    finally:
        cursor.close()

@app.get("/api/events/{event_id}", response_model=EventResponse, tags=["Events"])
def get_event_detail(event_id: str, db = Depends(get_db)):
    """Obtener detalle de un evento normalizado"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                event_id::text,
                type,
                occurred_at,
                zone,
                severity,
                title,
                description,
                evidence_url,
                status,
                score,
                created_at
            FROM events
            WHERE event_id = %s
        """, (event_id,))
        
        event = cursor.fetchone()
        
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return dict(event)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_event_detail_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching event detail")
    finally:
        cursor.close()

@app.get("/api/sources", response_model=List[SourceResponse], tags=["Sources"])
def get_sources(
    active_only: bool = Query(True),
    db = Depends(get_db)
):
    """Obtener lista de fuentes configuradas"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        query = """
            SELECT 
                source_id::text,
                name,
                type,
                domain,
                active,
                frequency_sec
            FROM sources
        """
        
        if active_only:
            query += " WHERE active = true"
        
        query += " ORDER BY name"
        
        cursor.execute(query)
        sources = cursor.fetchall()
        
        logger.info("sources_fetched", count=len(sources))
        
        return [dict(source) for source in sources]
        
    except Exception as e:
        logger.error("get_sources_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching sources")
    finally:
        cursor.close()

@app.get("/api/stats", response_model=StatsResponse, tags=["Statistics"])
def get_stats(db = Depends(get_db)):
    """Obtener estadísticas del sistema"""
    cursor = db.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Estadísticas de fuentes
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE active = true) as active
            FROM sources
        """)
        sources_stats = cursor.fetchone()
        
        # Estadísticas de eventos crudos
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                MAX(fetched_at) as last_fetch
            FROM raw_events
        """)
        raw_stats = cursor.fetchone()
        
        # Estadísticas de eventos normalizados
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE status = 'CONFIRMADO') as confirmados,
                COUNT(*) FILTER (WHERE status = 'EN_VERIFICACION') as en_verificacion,
                COUNT(*) FILTER (WHERE status = 'NO_VERIFICADO') as no_verificados
            FROM events
        """)
        events_stats = cursor.fetchone()
        
        return {
            "total_sources": sources_stats['total'],
            "active_sources": sources_stats['active'],
            "total_raw_events": raw_stats['total'],
            "total_events": events_stats['total'] if events_stats else 0,
            "events_by_status": {
                "confirmados": events_stats['confirmados'] if events_stats else 0,
                "en_verificacion": events_stats['en_verificacion'] if events_stats else 0,
                "no_verificados": events_stats['no_verificados'] if events_stats else 0
            },
            "last_scraping": raw_stats['last_fetch']
        }
        
    except Exception as e:
        logger.error("get_stats_failed", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching statistics")
    finally:
        cursor.close()

# ============================================================================
# Eventos de inicio
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Evento de inicio de la aplicación"""
    logger.info("api_gateway_started", version="1.0.0")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento de cierre de la aplicación"""
    logger.info("api_gateway_shutdown")
