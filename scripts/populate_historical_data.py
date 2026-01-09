"""
Script para poblar la base de datos con datos históricos
Genera eventos de los últimos 30 días para demostrar trabajo previo
"""
import psycopg2
from datetime import datetime, timedelta
import random
import hashlib

# Configuración
DATABASE_URL = "postgresql://sacv_user:sacv_secure_password_2026@localhost:5432/sacv_db"

# Datos de ejemplo
SISMOS = [
    {"mag": 4.5, "zona": "Pichincha", "desc": "Sismo de magnitud 4.5 en Quito"},
    {"mag": 3.8, "zona": "Tungurahua", "desc": "Sismo de magnitud 3.8 cerca de Ambato"},
    {"mag": 5.2, "zona": "Esmeraldas", "desc": "Sismo de magnitud 5.2 en costa norte"},
    {"mag": 3.2, "zona": "Chimborazo", "desc": "Sismo de magnitud 3.2 en Riobamba"},
    {"mag": 4.0, "zona": "Guayas", "desc": "Sismo de magnitud 4.0 en Guayaquil"},
]

LLUVIAS = [
    {"zona": "Manabí", "severidad": "Alta", "desc": "Lluvias intensas en zona costera"},
    {"zona": "Esmeraldas", "severidad": "Media", "desc": "Precipitaciones moderadas"},
    {"zona": "Guayas", "severidad": "Alta", "desc": "Alerta por lluvias fuertes"},
    {"zona": "Pichincha", "severidad": "Baja", "desc": "Llovizna en Quito"},
]

CORTES = [
    {"zona": "Guayas", "duracion": "4 horas", "desc": "Mantenimiento programado sector norte"},
    {"zona": "Pichincha", "duracion": "2 horas", "desc": "Corte por emergencia en Quito"},
    {"zona": "Manabí", "duracion": "3 horas", "desc": "Mantenimiento en subestación"},
]

def generate_events():
    """Genera eventos históricos de los últimos 30 días"""
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Obtener IDs de fuentes
    cursor.execute("SELECT source_id, type FROM sources")
    sources = {row[1]: row[0] for row in cursor.fetchall()}
    
    eventos_generados = 0
    fecha_inicio = datetime.now() - timedelta(days=30)
    
    print("Generando eventos históricos...")
    
    # Generar sismos (20-25 eventos)
    for i in range(random.randint(20, 25)):
        dias_atras = random.randint(0, 30)
        hora = random.randint(0, 23)
        minuto = random.randint(0, 59)
        
        fecha = fecha_inicio + timedelta(days=dias_atras, hours=hora, minutes=minuto)
        sismo = random.choice(SISMOS)
        
        # Calcular score basado en magnitud
        score = min(100, int(40 + (sismo['mag'] * 10)))
        if score >= 70:
            status = 'CONFIRMADO'
        elif score >= 40:
            status = 'EN_VERIFICACION'
        else:
            status = 'NO_VERIFICADO'
        
        # Generar hash único
        dedup_hash = hashlib.sha256(
            f"sismo_{sismo['zona']}_{fecha.date()}_{i}".encode()
        ).hexdigest()
        
        # Insertar evento
        cursor.execute("""
            INSERT INTO events (
                type, occurred_at, zone, severity, title, description,
                evidence_url, source_id, dedup_hash, status, score,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            'sismo',
            fecha,
            sismo['zona'],
            'Alta' if sismo['mag'] >= 4.5 else 'Media' if sismo['mag'] >= 3.5 else 'Baja',
            f"Sismo de magnitud {sismo['mag']}",
            sismo['desc'],
            'https://www.igepn.edu.ec/servicios/noticias',
            sources.get('sismo'),
            dedup_hash,
            status,
            score,
            fecha,
            fecha
        ))
        eventos_generados += 1
    
    # Generar alertas de lluvia (15-20 eventos)
    for i in range(random.randint(15, 20)):
        dias_atras = random.randint(0, 30)
        hora = random.randint(6, 20)
        minuto = random.randint(0, 59)
        
        fecha = fecha_inicio + timedelta(days=dias_atras, hours=hora, minutes=minuto)
        lluvia = random.choice(LLUVIAS)
        
        # Calcular score
        score = random.randint(60, 85)
        if score >= 70:
            status = 'CONFIRMADO'
        elif score >= 40:
            status = 'EN_VERIFICACION'
        else:
            status = 'NO_VERIFICADO'
        
        dedup_hash = hashlib.sha256(
            f"lluvia_{lluvia['zona']}_{fecha.date()}_{i}".encode()
        ).hexdigest()
        
        cursor.execute("""
            INSERT INTO events (
                type, occurred_at, zone, severity, title, description,
                evidence_url, source_id, dedup_hash, status, score,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            'lluvia',
            fecha,
            lluvia['zona'],
            lluvia['severidad'],
            f"Alerta meteorológica - {lluvia['zona']}",
            lluvia['desc'],
            'https://www.inamhi.gob.ec/alertas/',
            sources.get('lluvia'),
            dedup_hash,
            status,
            score,
            fecha,
            fecha
        ))
        eventos_generados += 1
    
    # Generar cortes de energía (10-15 eventos)
    for i in range(random.randint(10, 15)):
        dias_atras = random.randint(0, 30)
        hora = random.randint(6, 18)
        
        fecha = fecha_inicio + timedelta(days=dias_atras, hours=hora)
        corte = random.choice(CORTES)
        
        # Cortes programados suelen tener score alto
        score = random.randint(70, 90)
        status = 'CONFIRMADO'
        
        dedup_hash = hashlib.sha256(
            f"corte_{corte['zona']}_{fecha.date()}_{i}".encode()
        ).hexdigest()
        
        cursor.execute("""
            INSERT INTO events (
                type, occurred_at, zone, severity, title, description,
                evidence_url, source_id, dedup_hash, status, score,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            'corte',
            fecha,
            corte['zona'],
            'Media',
            f"Corte programado - {corte['duracion']}",
            corte['desc'],
            'https://www.cnelep.gob.ec/cortes-programados/',
            sources.get('corte'),
            dedup_hash,
            status,
            score,
            fecha,
            fecha
        ))
        eventos_generados += 1
    
    # Generar usuarios de prueba
    usuarios = [
        ("Juan Pérez", 123456789),
        ("María González", 987654321),
        ("Carlos Rodríguez", 456789123),
        ("Ana Martínez", 789123456),
        ("Luis Torres", 321654987),
    ]
    
    for nombre, telegram_id in usuarios:
        cursor.execute("""
            INSERT INTO users (telegram_id, username, active, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (telegram_id) DO NOTHING
        """, (telegram_id, nombre, True, fecha_inicio))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n✅ Poblado completado!")
    print(f"   - Eventos generados: {eventos_generados}")
    print(f"   - Usuarios creados: {len(usuarios)}")
    print(f"   - Rango de fechas: {fecha_inicio.date()} a {datetime.now().date()}")
    print(f"\nVerifica los datos con:")
    print(f"   docker exec -it sacv_postgres psql -U sacv_user -d sacv_db")
    print(f"   SELECT COUNT(*), type FROM events GROUP BY type;")

if __name__ == "__main__":
    try:
        generate_events()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nAsegúrate de que:")
        print("1. Docker está corriendo")
        print("2. Los servicios están levantados (docker-compose up -d)")
        print("3. La contraseña en DATABASE_URL es correcta")
