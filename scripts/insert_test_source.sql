-- Script para insertar fuente de prueba del Instituto Geofísico

-- Insertar fuente IGEPN
INSERT INTO sources (name, base_url, type, domain, parser_config, frequency_sec, active)
VALUES (
    'Instituto Geofísico - Sismos',
    'https://www.igepn.edu.ec/servicios/noticias',
    'sismo',
    'igepn.edu.ec',
    '{
        "title_selector": "h1, h2.title",
        "date_selector": ".date, .fecha, time",
        "content_selector": ".content, .contenido, .entry-content, p"
    }'::jsonb,
    300,
    true
)
ON CONFLICT DO NOTHING;

-- Verificar inserción
SELECT source_id, name, type, active, frequency_sec 
FROM sources 
WHERE domain = 'igepn.edu.ec';
