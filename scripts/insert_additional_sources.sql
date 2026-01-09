-- Script para insertar fuentes adicionales de datos

-- Fuente INAMHI - Alertas meteorologicas
INSERT INTO sources (
    name,
    base_url,
    type,
    domain,
    parser_config,
    frequency_sec,
    active
) VALUES (
    'INAMHI - Alertas Meteorologicas',
    'https://www.inamhi.gob.ec/alertas/',
    'lluvia',
    'inamhi.gob.ec',
    '{"selector": "div.alert", "fields": ["title", "content", "date"]}',
    300,
    true
) ON CONFLICT DO NOTHING;

-- Fuente CNEL - Cortes Programados
INSERT INTO sources (
    name,
    base_url,
    type,
    domain,
    parser_config,
    frequency_sec,
    active
) VALUES (
    'CNEL - Cortes Programados',
    'https://www.cnelep.gob.ec/cortes-programados/',
    'corte',
    'cnelep.gob.ec',
    '{"selector": "div.corte", "fields": ["sector", "fecha", "hora"]}',
    600,
    true
) ON CONFLICT DO NOTHING;
