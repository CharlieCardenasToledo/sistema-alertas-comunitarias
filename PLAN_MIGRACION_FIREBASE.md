# Plan de Migración a Firebase

**Fecha**: 09-ene-2026  
**Objetivo**: Evaluar y planificar migración del sistema a Firebase (Firestore/Realtime Database)

---

## Análisis de Viabilidad

### ¿Es posible migrar a Firebase?

**Respuesta: SÍ, es completamente viable** ✅

Firebase puede reemplazar varios componentes del stack actual:
- **Firestore/Realtime Database** → Reemplaza PostgreSQL
- **Firebase Cloud Functions** → Puede reemplazar algunos servicios
- **Firebase Cloud Messaging** → Alternativa a Telegram (opcional)
- **Firebase Authentication** → Para usuarios
- **Firebase Hosting** → Para Admin Panel

---

## Comparación: PostgreSQL vs Firebase

### PostgreSQL (Actual)

**Ventajas**:
- Relacional, ACID compliant
- Queries SQL complejas
- Transacciones robustas
- Joins eficientes
- Triggers y stored procedures
- Control total de datos

**Desventajas**:
- Requiere servidor/Docker
- Mantenimiento de infraestructura
- Escalado manual
- Backups manuales

### Firestore (Propuesto)

**Ventajas**:
- Serverless, sin infraestructura
- Escalado automático
- Realtime listeners (datos en tiempo real)
- Offline support
- Backups automáticos
- Free tier generoso
- SDK para múltiples lenguajes
- Integración con otros servicios Firebase

**Desventajas**:
- NoSQL (sin joins nativos)
- Queries limitadas vs SQL
- Costo por operaciones (reads/writes)
- Vendor lock-in
- Menos control sobre datos

### Realtime Database (Alternativa)

**Ventajas**:
- Más simple que Firestore
- Excelente para datos en tiempo real
- Latencia muy baja
- Sincronización automática

**Desventajas**:
- Estructura JSON plana
- Queries muy limitadas
- Menos escalable que Firestore
- No recomendado para datos complejos

### Recomendación: **FIRESTORE**

Firestore es mejor opción porque:
- Estructura de datos más flexible
- Mejor para queries complejas
- Más escalable
- Colecciones y documentos (similar a tablas)

---

## Arquitectura Propuesta con Firebase

### Opción 1: Migración Completa (Serverless)

```
Fuentes Oficiales
       ↓
Cloud Scheduler (Firebase)
       ↓
Cloud Function (Scraper)
       ↓
Firestore (eventos)
       ↓
Cloud Function (Normalizer)
       ↓
Firestore (eventos normalizados)
       ↓
Cloud Function (Verifier)
       ↓
Firestore (eventos verificados)
       ↓
Cloud Function (Notifier)
       ↓
Telegram Bot / FCM
```

**Ventajas**:
- 100% serverless
- Sin Docker, sin servidores
- Escalado automático
- Pago por uso

**Desventajas**:
- Costos pueden aumentar con volumen
- Menos control
- Dependencia total de Firebase

---

### Opción 2: Migración Híbrida (Recomendada)

```
Fuentes Oficiales
       ↓
Scraper Service (Docker/local)
       ↓
Firestore (raw_events)
       ↓
Normalizer Service (Docker/local)
       ↓
Firestore (events)
       ↓
Verifier Service (Docker/local)
       ↓
Firestore (verified_events)
       ↓
Notifier Service (Docker/local)
       ↓
Telegram Bot
```

**Ventajas**:
- Mantiene lógica de negocio en servicios
- Firestore solo como base de datos
- Más control sobre procesamiento
- Costos predecibles
- Fácil migración gradual

**Desventajas**:
- Aún requiere Docker para servicios
- No es 100% serverless

---

## Mapeo de Datos: PostgreSQL → Firestore

### Estructura Actual (PostgreSQL)

```sql
-- Tablas relacionales
sources (source_id, name, type, domain, active, ...)
raw_events (raw_id, source_id, raw_payload, raw_hash, ...)
events (event_id, type, zone, severity, score, status, ...)
users (user_id, telegram_id, username, ...)
subscriptions (subscription_id, user_id, event_type, zone, ...)
notifications (notification_id, event_id, user_id, status, ...)
```

### Estructura Propuesta (Firestore)

```
/sources/{sourceId}
  - name: string
  - type: string
  - domain: string
  - active: boolean
  - frequency_sec: number
  - created_at: timestamp

/raw_events/{rawEventId}
  - source_id: string (reference)
  - raw_payload: map
  - raw_hash: string
  - fetched_at: timestamp

/events/{eventId}
  - type: string
  - zone: string
  - severity: string
  - score: number
  - status: string
  - title: string
  - description: string
  - evidence_url: string
  - source_id: string (reference)
  - dedup_hash: string
  - occurred_at: timestamp
  - created_at: timestamp

/users/{userId}
  - telegram_id: number
  - username: string
  - active: boolean
  - created_at: timestamp
  
  /users/{userId}/subscriptions/{subscriptionId}
    - event_type: string
    - zone: string
    - active: boolean

/notifications/{notificationId}
  - event_id: string (reference)
  - user_id: string (reference)
  - status: string
  - sent_at: timestamp
```

**Nota**: Firestore usa subcolecciones para relaciones 1-N (ej: user → subscriptions)

---

## Plan de Implementación

### Fase 1: Preparación (1-2 días)

**Tareas**:
1. Crear proyecto en Firebase Console
2. Configurar Firestore
3. Instalar Firebase Admin SDK
4. Configurar credenciales de servicio

**Comandos**:
```bash
# Instalar Firebase CLI
npm install -g firebase-tools

# Login
firebase login

# Inicializar proyecto
firebase init firestore
```

**Dependencias Python**:
```bash
pip install firebase-admin
```

---

### Fase 2: Migración de Datos (2-3 días)

**Tareas**:
1. Crear colecciones en Firestore
2. Script de migración de datos existentes
3. Validar integridad de datos

**Script de Migración**:
```python
import firebase_admin
from firebase_admin import credentials, firestore
import psycopg2

# Inicializar Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Conectar a PostgreSQL
pg_conn = psycopg2.connect(DATABASE_URL)
cursor = pg_conn.cursor()

# Migrar sources
cursor.execute("SELECT * FROM sources")
for row in cursor.fetchall():
    db.collection('sources').document(str(row[0])).set({
        'name': row[1],
        'type': row[3],
        'domain': row[4],
        'active': row[8],
        # ... otros campos
    })

# Migrar events
cursor.execute("SELECT * FROM events")
for row in cursor.fetchall():
    db.collection('events').document(str(row[0])).set({
        'type': row[1],
        'zone': row[3],
        'severity': row[4],
        # ... otros campos
    })
```

---

### Fase 3: Actualizar Servicios (1 semana)

#### 3.1 Scraper Service

**Cambios**:
```python
# Antes (PostgreSQL)
cursor.execute("""
    INSERT INTO raw_events (source_id, raw_payload, raw_hash)
    VALUES (%s, %s, %s)
""", (source_id, payload, hash))

# Después (Firestore)
db.collection('raw_events').add({
    'source_id': source_id,
    'raw_payload': payload,
    'raw_hash': hash,
    'fetched_at': firestore.SERVER_TIMESTAMP
})
```

#### 3.2 Normalizer Service

**Cambios**:
```python
# Antes (PostgreSQL)
cursor.execute("""
    INSERT INTO events (type, zone, severity, ...)
    VALUES (%s, %s, %s, ...)
""", (...))

# Después (Firestore)
db.collection('events').add({
    'type': event_type,
    'zone': zone,
    'severity': severity,
    'score': 0,
    'status': 'NO_VERIFICADO',
    'created_at': firestore.SERVER_TIMESTAMP
})
```

#### 3.3 Verifier Service

**Cambios**:
```python
# Antes (PostgreSQL)
cursor.execute("""
    UPDATE events SET score = %s, status = %s
    WHERE event_id = %s
""", (score, status, event_id))

# Después (Firestore)
event_ref = db.collection('events').document(event_id)
event_ref.update({
    'score': score,
    'status': status,
    'verified_at': firestore.SERVER_TIMESTAMP
})
```

#### 3.4 Notifier Service

**Cambios**:
```python
# Antes (PostgreSQL)
cursor.execute("""
    SELECT * FROM users u
    JOIN subscriptions s ON u.user_id = s.user_id
    WHERE s.event_type = %s AND s.zone = %s
""", (event_type, zone))

# Después (Firestore)
users = db.collection('users').where('active', '==', True).stream()
for user in users:
    subscriptions = user.reference.collection('subscriptions')\
        .where('event_type', '==', event_type)\
        .where('zone', '==', zone)\
        .where('active', '==', True)\
        .stream()
```

---

### Fase 4: Reemplazar RabbitMQ (Opcional)

**Opción A: Mantener RabbitMQ**
- Firestore solo reemplaza PostgreSQL
- RabbitMQ sigue manejando queues

**Opción B: Firestore Listeners (Recomendado)**
```python
# Escuchar nuevos eventos en tiempo real
def on_snapshot(col_snapshot, changes, read_time):
    for change in changes:
        if change.type.name == 'ADDED':
            process_event(change.document.to_dict())

# Listener
db.collection('raw_events')\
    .where('processed', '==', False)\
    .on_snapshot(on_snapshot)
```

**Ventajas**:
- Elimina RabbitMQ
- Datos en tiempo real
- Menos infraestructura

**Desventajas**:
- Acoplamiento más fuerte
- Costos por listeners

---

### Fase 5: API Gateway (2-3 días)

**Cambios en Endpoints**:
```python
# Antes (PostgreSQL)
@app.get("/api/events")
def get_events():
    cursor.execute("SELECT * FROM events LIMIT 10")
    return cursor.fetchall()

# Después (Firestore)
@app.get("/api/events")
def get_events(limit: int = 10):
    events = db.collection('events')\
        .order_by('created_at', direction=firestore.Query.DESCENDING)\
        .limit(limit)\
        .stream()
    return [event.to_dict() for event in events]
```

---

### Fase 6: Testing y Validación (3-5 días)

**Tareas**:
1. Tests unitarios con Firestore emulator
2. Tests de integración
3. Validar performance
4. Comparar costos

**Firestore Emulator**:
```bash
# Instalar emulator
firebase setup:emulators:firestore

# Ejecutar
firebase emulators:start
```

---

## Costos Estimados

### Firebase Free Tier (Spark Plan)

**Firestore**:
- 50,000 reads/día
- 20,000 writes/día
- 20,000 deletes/día
- 1 GB almacenamiento

**Cloud Functions**:
- 2M invocaciones/mes
- 400,000 GB-segundos
- 200,000 GHz-segundos

### Estimación para el Proyecto

**Supuestos**:
- 100 eventos/día
- 50 usuarios
- 200 notificaciones/día

**Operaciones Firestore**:
- Writes: ~500/día (eventos + notificaciones)
- Reads: ~2,000/día (queries, listeners)
- **Resultado**: Dentro del free tier ✅

**Conclusión**: El proyecto puede correr GRATIS en Firebase

---

## Ventajas de Migrar a Firebase

1. **Sin Infraestructura**
   - No Docker
   - No servidores
   - No mantenimiento

2. **Escalabilidad Automática**
   - Crece con demanda
   - Sin configuración

3. **Datos en Tiempo Real**
   - Listeners automáticos
   - Sincronización instantánea

4. **Desarrollo Más Rápido**
   - Menos código de infraestructura
   - SDKs bien documentados

5. **Integración con Ecosistema**
   - Authentication
   - Cloud Functions
   - Hosting
   - Analytics

6. **Costo Inicial Cero**
   - Free tier generoso
   - Pago por uso

---

## Desventajas de Migrar a Firebase

1. **Vendor Lock-in**
   - Dependencia de Google
   - Difícil migrar después

2. **Queries Limitadas**
   - No SQL complejo
   - No joins nativos
   - Requiere denormalización

3. **Costos Variables**
   - Puede crecer con escala
   - Menos predecible

4. **Menos Control**
   - No acceso directo a BD
   - Limitado por APIs

5. **Curva de Aprendizaje**
   - Paradigma NoSQL diferente
   - Patrones de diseño distintos

---

## Recomendación Final

### Para Proyecto Académico: **MANTENER PostgreSQL**

**Razones**:
1. Demuestra conocimiento de arquitectura completa
2. Control total sobre datos
3. Aprenden Docker, microservicios, SQL
4. No dependen de servicios externos
5. Funciona offline

### Para Proyecto Real/Startup: **MIGRAR A FIREBASE**

**Razones**:
1. Lanzamiento más rápido
2. Sin costos de infraestructura
3. Escalado automático
4. Menos mantenimiento
5. Más tiempo para features

---

## Plan de Migración Gradual (Si se decide migrar)

### Semana 1: Preparación
- Crear proyecto Firebase
- Configurar Firestore
- Instalar SDKs

### Semana 2: Migración de Datos
- Diseñar estructura Firestore
- Script de migración
- Validar datos

### Semana 3: Actualizar Scraper y Normalizer
- Reemplazar queries PostgreSQL
- Probar con Firestore

### Semana 4: Actualizar Verifier y Notifier
- Implementar listeners
- Eliminar RabbitMQ (opcional)

### Semana 5: Actualizar API Gateway
- Nuevos endpoints con Firestore
- Documentación

### Semana 6: Testing y Deployment
- Tests completos
- Validación de costos
- Deploy a producción

---

## Conclusión

**Es completamente viable migrar a Firebase**, pero para un proyecto académico como este, **recomiendo mantener PostgreSQL** porque:

1. Demuestra más conocimientos técnicos
2. Arquitectura más completa
3. Independiente de servicios cloud
4. Mejor para aprendizaje

**Sin embargo**, si el objetivo es crear un producto real que escale, Firebase es una excelente opción que reduciría significativamente la complejidad operacional.

---

**Decisión**: ¿Quieres que implemente la migración a Firebase o mantenemos PostgreSQL?

**Tiempo estimado de migración completa**: 4-6 semanas
**Complejidad**: Media-Alta
**Costo**: $0 (dentro de free tier)
