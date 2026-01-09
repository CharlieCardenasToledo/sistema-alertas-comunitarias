-- Script SQL para poblar base de datos con eventos históricos
-- Ejecutar: docker exec -i sacv_postgres psql -U sacv_user -d sacv_db < scripts/populate_historical_data.sql

-- Eventos de Sismos (IGEPN) - Últimos 30 días
-- Diciembre 2025
INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-10 14:30:00'::timestamp,
    'Pichincha',
    'Alta',
    'Sismo de magnitud 4.5',
    'Sismo de magnitud 4.5 registrado en Quito',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_pichincha_2025-12-10_1'),
    'CONFIRMADO',
    85,
    '2025-12-10 14:30:00'::timestamp,
    '2025-12-10 14:30:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-12 08:15:00'::timestamp,
    'Tungurahua',
    'Media',
    'Sismo de magnitud 3.8',
    'Sismo de magnitud 3.8 cerca de Ambato',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_tungurahua_2025-12-12_1'),
    'CONFIRMADO',
    75,
    '2025-12-12 08:15:00'::timestamp,
    '2025-12-12 08:15:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-15 19:45:00'::timestamp,
    'Esmeraldas',
    'Alta',
    'Sismo de magnitud 5.2',
    'Sismo de magnitud 5.2 en costa norte',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_esmeraldas_2025-12-15_1'),
    'CONFIRMADO',
    92,
    '2025-12-15 19:45:00'::timestamp,
    '2025-12-15 19:45:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-18 11:20:00'::timestamp,
    'Chimborazo',
    'Media',
    'Sismo de magnitud 3.2',
    'Sismo de magnitud 3.2 en Riobamba',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_chimborazo_2025-12-18_1'),
    'EN_VERIFICACION',
    62,
    '2025-12-18 11:20:00'::timestamp,
    '2025-12-18 11:20:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-20 16:30:00'::timestamp,
    'Guayas',
    'Media',
    'Sismo de magnitud 4.0',
    'Sismo de magnitud 4.0 en Guayaquil',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_guayas_2025-12-20_1'),
    'CONFIRMADO',
    78,
    '2025-12-20 16:30:00'::timestamp,
    '2025-12-20 16:30:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-22 09:10:00'::timestamp,
    'Pichincha',
    'Baja',
    'Sismo de magnitud 2.8',
    'Sismo leve registrado en Quito',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_pichincha_2025-12-22_1'),
    'EN_VERIFICACION',
    55,
    '2025-12-22 09:10:00'::timestamp,
    '2025-12-22 09:10:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-25 14:00:00'::timestamp,
    'Manabí',
    'Alta',
    'Sismo de magnitud 4.7',
    'Sismo de magnitud 4.7 en zona costera',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_manabi_2025-12-25_1'),
    'CONFIRMADO',
    87,
    '2025-12-25 14:00:00'::timestamp,
    '2025-12-25 14:00:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2025-12-28 07:45:00'::timestamp,
    'Tungurahua',
    'Media',
    'Sismo de magnitud 3.5',
    'Sismo de magnitud 3.5 cerca del Tungurahua',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_tungurahua_2025-12-28_1'),
    'CONFIRMADO',
    70,
    '2025-12-28 07:45:00'::timestamp,
    '2025-12-28 07:45:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

-- Enero 2026
INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2026-01-02 10:20:00'::timestamp,
    'Pichincha',
    'Media',
    'Sismo de magnitud 3.9',
    'Sismo de magnitud 3.9 en Quito',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_pichincha_2026-01-02_1'),
    'CONFIRMADO',
    76,
    '2026-01-02 10:20:00'::timestamp,
    '2026-01-02 10:20:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2026-01-05 15:30:00'::timestamp,
    'Guayas',
    'Alta',
    'Sismo de magnitud 4.8',
    'Sismo de magnitud 4.8 en Guayaquil',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_guayas_2026-01-05_1'),
    'CONFIRMADO',
    88,
    '2026-01-05 15:30:00'::timestamp,
    '2026-01-05 15:30:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'sismo',
    '2026-01-07 12:15:00'::timestamp,
    'Chimborazo',
    'Baja',
    'Sismo de magnitud 2.5',
    'Sismo leve en Riobamba',
    'https://www.igepn.edu.ec/servicios/noticias',
    source_id,
    md5('sismo_chimborazo_2026-01-07_1'),
    'NO_VERIFICADO',
    35,
    '2026-01-07 12:15:00'::timestamp,
    '2026-01-07 12:15:00'::timestamp
FROM sources WHERE type = 'sismo' LIMIT 1;

-- Alertas de Lluvia (INAMHI)
INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2025-12-11 10:00:00'::timestamp,
    'Manabí',
    'Alta',
    'Alerta meteorológica - Manabí',
    'Lluvias intensas en zona costera',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_manabi_2025-12-11_1'),
    'CONFIRMADO',
    82,
    '2025-12-11 10:00:00'::timestamp,
    '2025-12-11 10:00:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2025-12-14 16:30:00'::timestamp,
    'Esmeraldas',
    'Media',
    'Alerta meteorológica - Esmeraldas',
    'Precipitaciones moderadas',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_esmeraldas_2025-12-14_1'),
    'EN_VERIFICACION',
    65,
    '2025-12-14 16:30:00'::timestamp,
    '2025-12-14 16:30:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2025-12-17 08:00:00'::timestamp,
    'Guayas',
    'Alta',
    'Alerta meteorológica - Guayas',
    'Alerta por lluvias fuertes',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_guayas_2025-12-17_1'),
    'CONFIRMADO',
    78,
    '2025-12-17 08:00:00'::timestamp,
    '2025-12-17 08:00:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2025-12-21 12:00:00'::timestamp,
    'Pichincha',
    'Baja',
    'Alerta meteorológica - Pichincha',
    'Llovizna en Quito',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_pichincha_2025-12-21_1'),
    'EN_VERIFICACION',
    58,
    '2025-12-21 12:00:00'::timestamp,
    '2025-12-21 12:00:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2025-12-26 14:30:00'::timestamp,
    'Manabí',
    'Alta',
    'Alerta meteorológica - Manabí',
    'Lluvias intensas continúan',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_manabi_2025-12-26_1'),
    'CONFIRMADO',
    80,
    '2025-12-26 14:30:00'::timestamp,
    '2025-12-26 14:30:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2026-01-03 09:00:00'::timestamp,
    'Esmeraldas',
    'Media',
    'Alerta meteorológica - Esmeraldas',
    'Precipitaciones moderadas',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_esmeraldas_2026-01-03_1'),
    'CONFIRMADO',
    72,
    '2026-01-03 09:00:00'::timestamp,
    '2026-01-03 09:00:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'lluvia',
    '2026-01-06 11:30:00'::timestamp,
    'Guayas',
    'Alta',
    'Alerta meteorológica - Guayas',
    'Lluvias fuertes en Guayaquil',
    'https://www.inamhi.gob.ec/alertas/',
    source_id,
    md5('lluvia_guayas_2026-01-06_1'),
    'CONFIRMADO',
    85,
    '2026-01-06 11:30:00'::timestamp,
    '2026-01-06 11:30:00'::timestamp
FROM sources WHERE type = 'lluvia' LIMIT 1;

-- Cortes de Energía (CNEL)
INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2025-12-13 06:00:00'::timestamp,
    'Guayas',
    'Media',
    'Corte programado - 4 horas',
    'Mantenimiento programado sector norte',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_guayas_2025-12-13_1'),
    'CONFIRMADO',
    88,
    '2025-12-13 06:00:00'::timestamp,
    '2025-12-13 06:00:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2025-12-16 09:00:00'::timestamp,
    'Pichincha',
    'Media',
    'Corte programado - 2 horas',
    'Corte por emergencia en Quito',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_pichincha_2025-12-16_1'),
    'CONFIRMADO',
    82,
    '2025-12-16 09:00:00'::timestamp,
    '2025-12-16 09:00:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2025-12-19 07:30:00'::timestamp,
    'Manabí',
    'Media',
    'Corte programado - 3 horas',
    'Mantenimiento en subestación',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_manabi_2025-12-19_1'),
    'CONFIRMADO',
    85,
    '2025-12-19 07:30:00'::timestamp,
    '2025-12-19 07:30:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2025-12-23 08:00:00'::timestamp,
    'Guayas',
    'Media',
    'Corte programado - 5 horas',
    'Mantenimiento preventivo',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_guayas_2025-12-23_1'),
    'CONFIRMADO',
    90,
    '2025-12-23 08:00:00'::timestamp,
    '2025-12-23 08:00:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2026-01-04 06:30:00'::timestamp,
    'Pichincha',
    'Media',
    'Corte programado - 3 horas',
    'Mantenimiento zona sur',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_pichincha_2026-01-04_1'),
    'CONFIRMADO',
    87,
    '2026-01-04 06:30:00'::timestamp,
    '2026-01-04 06:30:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

INSERT INTO events (type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
SELECT 
    'corte',
    '2026-01-08 10:00:00'::timestamp,
    'Esmeraldas',
    'Media',
    'Corte programado - 2 horas',
    'Reparación de líneas',
    'https://www.cnelep.gob.ec/cortes-programados/',
    source_id,
    md5('corte_esmeraldas_2026-01-08_1'),
    'CONFIRMADO',
    83,
    '2026-01-08 10:00:00'::timestamp,
    '2026-01-08 10:00:00'::timestamp
FROM sources WHERE type = 'corte' LIMIT 1;

-- Usuarios de prueba
INSERT INTO users (telegram_id, username, active, created_at)
VALUES 
    (123456789, 'Juan Pérez', true, '2025-12-10 00:00:00'),
    (987654321, 'María González', true, '2025-12-15 00:00:00'),
    (456789123, 'Carlos Rodríguez', true, '2025-12-20 00:00:00'),
    (789123456, 'Ana Martínez', true, '2025-12-25 00:00:00'),
    (321654987, 'Luis Torres', true, '2026-01-01 00:00:00')
ON CONFLICT (telegram_id) DO NOTHING;

-- Mostrar resumen
SELECT 
    'Eventos insertados' as descripcion,
    COUNT(*) as total
FROM events
WHERE created_at >= '2025-12-10'::timestamp;

SELECT 
    type as tipo_evento,
    COUNT(*) as total,
    ROUND(AVG(score), 2) as score_promedio
FROM events
WHERE created_at >= '2025-12-10'::timestamp
GROUP BY type
ORDER BY type;

SELECT 
    status,
    COUNT(*) as total
FROM events
WHERE created_at >= '2025-12-10'::timestamp
GROUP BY status
ORDER BY status;
