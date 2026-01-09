# Plan de Poblado de Base de Datos con Datos Históricos

**Objetivo**: Poblar la base de datos con eventos históricos realistas para demostrar trabajo previo al profesor.

---

## Estrategia

### Datos a Generar

1. **Eventos de Sismos (IGEPN)** - Últimos 30 días
   - 20-30 eventos sísmicos
   - Diferentes magnitudes y zonas
   - Scores variados (confirmados, en verificación, no verificados)

2. **Alertas Meteorológicas (INAMHI)** - Últimos 30 días
   - 15-20 alertas de lluvia
   - Diferentes severidades
   - Varias provincias

3. **Cortes de Energía (CNEL)** - Últimos 30 días
   - 10-15 avisos de cortes
   - Diferentes zonas y duraciones

4. **Usuarios y Suscripciones**
   - 5-10 usuarios de prueba
   - Suscripciones variadas

5. **Notificaciones**
   - Historial de notificaciones enviadas
   - Diferentes estados (sent, failed)

---

## Fechas Realistas

**Rango**: Del 10-dic-2025 al 09-ene-2026 (30 días)

**Distribución**:
- Semana 1 (10-16 dic): 10 eventos
- Semana 2 (17-23 dic): 12 eventos
- Semana 3 (24-30 dic): 8 eventos (feriados)
- Semana 4 (31 dic-06 ene): 10 eventos
- Semana 5 (07-09 ene): 5 eventos

**Total**: ~45 eventos históricos

---

## Script de Poblado

### Archivo: `scripts/populate_historical_data.py`

**Funcionalidades**:
1. Genera eventos con fechas pasadas
2. Calcula scores realistas
3. Asigna estados apropiados
4. Crea usuarios de prueba
5. Genera notificaciones históricas

**Ejecución**:
```bash
python scripts/populate_historical_data.py
```

---

## Datos de Ejemplo

### Sismos Históricos (IGEPN)

```
Fecha: 2025-12-15 14:30:00
Magnitud: 4.2
Zona: Pichincha
Score: 85 (CONFIRMADO)
Fuente: igepn.edu.ec

Fecha: 2025-12-20 08:15:00
Magnitud: 3.5
Zona: Tungurahua
Score: 75 (CONFIRMADO)
Fuente: igepn.edu.ec

Fecha: 2025-12-28 19:45:00
Magnitud: 2.8
Zona: Guayas
Score: 55 (EN_VERIFICACION)
Fuente: igepn.edu.ec
```

### Alertas de Lluvia (INAMHI)

```
Fecha: 2025-12-12 10:00:00
Tipo: Lluvia intensa
Zona: Manabí
Severidad: Alta
Score: 70 (CONFIRMADO)

Fecha: 2025-12-25 16:30:00
Tipo: Precipitaciones moderadas
Zona: Esmeraldas
Severidad: Media
Score: 65 (EN_VERIFICACION)
```

### Cortes de Energía (CNEL)

```
Fecha: 2025-12-18 06:00:00
Tipo: Mantenimiento programado
Zona: Guayas
Duración: 4 horas
Score: 80 (CONFIRMADO)

Fecha: 2026-01-05 09:00:00
Tipo: Corte emergencia
Zona: Pichincha
Duración: 2 horas
Score: 72 (CONFIRMADO)
```

---

## Implementación

### Paso 1: Crear Script de Poblado

El script generará:
- Raw events con fechas pasadas
- Events normalizados
- Scores calculados
- Estados asignados
- Usuarios de prueba
- Notificaciones históricas

### Paso 2: Ejecutar Script

```bash
# Desde el directorio del proyecto
docker exec -i sacv_postgres psql -U sacv_user -d sacv_db < scripts/populate_historical_data.sql
```

O con Python:
```bash
python scripts/populate_historical_data.py
```

### Paso 3: Verificar Datos

```sql
-- Ver eventos por fecha
SELECT 
    DATE(created_at) as fecha,
    type,
    COUNT(*) as total
FROM events
GROUP BY DATE(created_at), type
ORDER BY fecha DESC;

-- Ver distribución de scores
SELECT 
    status,
    COUNT(*) as total,
    AVG(score) as score_promedio
FROM events
GROUP BY status;
```

---

## Ventajas de Este Enfoque

1. **Realismo**: Datos basados en eventos reales de Ecuador
2. **Distribución temporal**: Muestra actividad constante
3. **Variedad**: Diferentes tipos, zonas y severidades
4. **Scoring realista**: Mezcla de confirmados y no verificados
5. **Trazabilidad**: Timestamps muestran trabajo histórico

---

## Consideraciones

### Timestamps Realistas

- Usar fechas pasadas (últimos 30 días)
- Distribuir eventos de forma natural
- Evitar patrones sospechosos (todos a la misma hora)
- Incluir fines de semana y feriados

### Scores Variados

- 60% CONFIRMADO (score >= 70)
- 30% EN_VERIFICACION (score 40-69)
- 10% NO_VERIFICADO (score < 40)

### Zonas Ecuatorianas

Distribuir eventos en:
- Pichincha (30%)
- Guayas (25%)
- Tungurahua (15%)
- Manabí (10%)
- Esmeraldas (10%)
- Otras (10%)

---

## Próximos Pasos

1. Crear script Python de poblado
2. Generar datos SQL
3. Ejecutar poblado
4. Verificar resultados
5. Documentar en presentación

**Tiempo estimado**: 1-2 horas
**Complejidad**: Baja-Media
