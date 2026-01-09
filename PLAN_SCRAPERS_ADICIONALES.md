# Plan: Scrapers Adicionales (Tarea 2.4)

## Objetivo
Implementar 2 scrapers adicionales para diversificar las fuentes de datos del sistema.

## Scraper 1: Datos de Lluvia (INAMHI)

### Fuente
- **Organizacion**: Instituto Nacional de Meteorologia e Hidrologia (INAMHI)
- **URL**: https://www.inamhi.gob.ec
- **Tipo de datos**: Precipitaciones, alertas meteorologicas

### Datos a extraer
- Alertas de lluvia intensa
- Nivel de precipitacion
- Zona afectada
- Fecha y hora
- Duracion estimada

### Implementacion
- Scraper similar a IGEPN
- Parseo de boletines meteorologicos
- Clasificacion de severidad segun mm de lluvia

## Scraper 2: Cortes Programados (CNEL)

### Fuente
- **Organizacion**: CNEL (Corporacion Nacional de Electricidad)
- **URL**: https://www.cnel.gob.ec
- **Tipo de datos**: Cortes programados de energia

### Datos a extraer
- Fecha y hora del corte
- Duracion estimada
- Sectores afectados
- Razon del corte (mantenimiento, emergencia)

### Implementacion
- Scraper para avisos de cortes
- Extraccion de horarios y zonas
- Clasificacion por tipo de corte

## Integracion

### Actualizaciones necesarias
1. Agregar nuevos scrapers a `services/scraper/src/scrapers/`
2. Actualizar `main.py` para incluir nuevos scrapers
3. Insertar nuevas fuentes en BD
4. Actualizar Normalizer para manejar nuevos tipos

### Tipos de evento
- `lluvia` - Eventos de precipitacion
- `corte` - Cortes de energia

## Verificacion
- Probar scraping de cada fuente
- Verificar normalizacion
- Confirmar notificaciones

---

**Nota**: Si las fuentes oficiales no tienen datos estructurados accesibles, se usaran fuentes alternativas o se simularan datos de prueba para demostrar la funcionalidad.
