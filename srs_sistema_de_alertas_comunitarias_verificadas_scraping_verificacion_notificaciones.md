# SRS – Especificación de Requisitos de Software (IEEE 830)

## 0. Control del documento
- **Proyecto:** Sistema de Alertas Comunitarias Verificadas (SACV)
- **Versión:** 1.0
- **Fecha:** 09-ene-2026
- **Autor:** (Tu nombre)
- **Asignatura:** Arquitectura e Integración de Plataformas de TI
- **Institución:** (Tu institución)

---

## 1. Introducción

### 1.1 Propósito
Este documento especifica de forma completa los requisitos funcionales y no funcionales del **Sistema de Alertas Comunitarias Verificadas (SACV)**, una plataforma que **detecta eventos** (sismos/lluvias/cortes programados) mediante **scraping de fuentes oficiales**, **normaliza** la información, calcula un **nivel de confianza** por verificación de evidencia y **publica/notifica** alertas a usuarios y administradores.

El documento está dirigido a: docentes evaluadores, equipo de desarrollo, testers y cualquier stakeholder institucional o comunitario.

### 1.2 Alcance
El SACV provee:
- **Ingesta** periódica (scraping) desde páginas oficiales.
- **Normalización** de eventos a un esquema común.
- **Verificación** mediante reglas (lista blanca de dominios, vigencia temporal, deduplicación, corroboración cruzada opcional).
- **Publicación** de alertas en una API y panel web.
- **Notificaciones** (MVP: Telegram/email; opcional: WhatsApp Business Platform en fase final).
- **Auditoría** (quién/qué/cuándo) y observabilidad (logs/métricas).

Fuera de alcance (v1):
- App móvil nativa.
- Integración oficial por API con redes sociales como fuente primaria.
- Reconocimiento OCR de capturas/imágenes de rumores.
- Analítica avanzada con ML (se reemplaza por reglas explicables).

### 1.3 Definiciones, acrónimos y abreviaturas
- **SACV:** Sistema de Alertas Comunitarias Verificadas.
- **Scraping:** extracción automatizada de información desde páginas web.
- **Evento:** registro normalizado de sismo/lluvia/corte.
- **Evidencia:** enlace oficial y/o contenido verificable del evento.
- **Score de confianza:** puntuación que determina el estado (Confirmado/En verificación/No verificado).
- **Allowlist/Lista blanca:** dominios/fuentes permitidos como oficiales.
- **Deduplicación:** detección de eventos repetidos.
- **MVP:** Producto mínimo viable.

### 1.4 Referencias
- IEEE 830 – Recommended Practice for Software Requirements Specifications (SRS).
- Políticas internas de seguridad y uso responsable de datos (si aplica).

### 1.5 Visión general del documento
- Sección 2 describe el producto y su contexto.
- Sección 3 detalla requisitos específicos (funcionales, datos, interfaces, NFR).
- Sección 4 incluye criterios de aceptación y trazabilidad.

---

## 2. Descripción general

### 2.1 Perspectiva del producto
El SACV es un sistema web con arquitectura orientada a servicios/microservicios. Sus componentes principales:
- **Scrapers por fuente** (workers) → detectan eventos.
- **Normalizador** → estandariza datos.
- **Verificador** → calcula confianza y estado.
- **API de Alertas** → consulta y publicación.
- **Servicio de Notificaciones** → envíos.
- **Panel Web** → monitoreo y administración.

### 2.2 Funciones del producto (alto nivel)
1. Configurar fuentes oficiales y parámetros de scraping.
2. Ejecutar scraping automático y manual.
3. Transformar eventos a esquema común.
4. Calcular nivel de confianza (reglas + corroboración opcional).
5. Publicar alertas y exponerlas vía API.
6. Notificar a usuarios suscritos por canales.
7. Proveer historial, filtros, exportación y auditoría.

### 2.3 Características de los usuarios
- **Administrador del sistema:** configura fuentes, reglas, usuarios, canales.
- **Operador/Moderador:** revisa alertas en verificación, aprueba/rechaza si se habilita revisión humana.
- **Usuario final (comunidad):** consulta alertas, se suscribe a categorías/zonas, recibe notificaciones.
- **Docente evaluador:** revisa documentación, arquitectura, evidencias y demo.

### 2.4 Restricciones
- Respeto a términos de uso y buenas prácticas de scraping (rate limit, no saturación).
- Limitaciones de disponibilidad de fuentes externas.
- Para WhatsApp oficial: requerimientos de configuración/aprobación y políticas del proveedor.
- Cumplimiento básico de seguridad: protección de credenciales, HTTPS, control de acceso.

### 2.5 Suposiciones y dependencias
- Las fuentes oficiales publican información accesible vía web.
- El sistema tendrá conectividad a Internet.
- La infraestructura soportará contenedores (Docker).

---

## 3. Requisitos específicos

### 3.1 Requisitos funcionales (RF)

#### 3.1.1 Gestión de fuentes
- **RF-01:** El sistema permitirá registrar una **fuente oficial** con: nombre, URL base, tipo de evento (sismo/lluvia/corte), dominio, método de extracción (CSS/XPath/regex), frecuencia de consulta y estado (activo/inactivo).
- **RF-02:** El sistema permitirá mantener una **lista blanca de dominios** permitidos por tipo de evento.
- **RF-03:** El sistema permitirá ejecutar un **scraping manual** por fuente desde el panel.

#### 3.1.2 Scraping e ingesta
- **RF-04:** Los scrapers ejecutarán consultas periódicas según la frecuencia configurada.
- **RF-05:** El sistema almacenará el **evento crudo** (raw) con timestamp de captura y referencia de fuente.
- **RF-06:** El sistema aplicará **control de tasa** (rate limit) y reintentos con backoff ante fallos temporales.
- **RF-07:** El sistema detectará y registrará cambios de estructura (parsing fallido) para revisión.

#### 3.1.3 Normalización
- **RF-08:** El sistema convertirá eventos crudos a un **esquema normalizado** común.
- **RF-09:** El sistema validará campos obligatorios (tipo, fecha/hora, ubicación/zona, descripción mínima, URL evidencia).
- **RF-10:** El sistema generará un **hash de deduplicación** para identificar eventos repetidos.

#### 3.1.4 Verificación y scoring
- **RF-11:** El sistema calculará un **score de confianza** basado en reglas (ver 3.2.3).
- **RF-12:** El sistema clasificará eventos en estados:
  - **CONFIRMADO** (publicable + notifica)
  - **EN_VERIFICACION** (visible en panel; notificación configurable)
  - **NO_VERIFICADO** (no se notifica; visible solo para admin)
- **RF-13:** El sistema implementará **deduplicación**: si un evento equivalente ya existe, se actualiza el historial en vez de crear un duplicado (configurable).
- **RF-14 (Opcional):** Corroboración cruzada: si un evento coincide con otra fuente oficial dentro de una ventana temporal, aumenta el score.

#### 3.1.5 Publicación y consulta
- **RF-15:** El sistema publicará eventos confirmados y permitirá consultarlos vía API REST.
- **RF-16:** El panel permitirá filtrar por: tipo, fecha, zona, estado, fuente, severidad.
- **RF-17:** El sistema permitirá ver el **detalle** del evento con evidencia (URL) y trazabilidad.
- **RF-18:** El sistema permitirá exportar listados en CSV.

#### 3.1.6 Suscripciones y notificaciones
- **RF-19:** El usuario podrá suscribirse por tipo de evento y zona.
- **RF-20:** El sistema enviará notificaciones por canal configurado cuando un evento pase a CONFIRMADO.
- **RF-21 (MVP):** Soportar al menos 1 canal: **Telegram** o **Email**.
- **RF-22 (Fase III opcional):** Soportar **WhatsApp** mediante proveedor oficial.

#### 3.1.7 Seguridad y administración
- **RF-23:** El sistema soportará autenticación y roles (Admin, Operador, Usuario).
- **RF-24:** El sistema registrará auditoría de acciones administrativas (alta/edición de fuentes, cambios de reglas, gestión de usuarios).

#### 3.1.8 Observabilidad
- **RF-25:** El sistema registrará logs estructurados por servicio (requestId, eventoId, fuente, estado).
- **RF-26:** El sistema expondrá métricas mínimas (eventos detectados, confirmados, fallos de scraping, latencia de pipeline).

---

### 3.2 Modelo de datos

#### 3.2.1 Entidades principales
- **Source**(source_id, name, base_url, type, domain, parser_config, frequency_sec, active, created_at)
- **RawEvent**(raw_id, source_id, fetched_at, raw_payload, raw_hash)
- **Event**(event_id, type, occurred_at, zone, severity, title, description, evidence_url, source_id, dedup_hash, status, score, created_at, updated_at)
- **VerificationRule**(rule_id, name, weight, enabled)
- **Subscription**(sub_id, user_id, type, zone, channel, active)
- **Notification**(notif_id, event_id, channel, to, sent_at, status)
- **AuditLog**(audit_id, user_id, action, entity, entity_id, timestamp, metadata)

#### 3.2.2 Estados
- Event.status ∈ {CONFIRMADO, EN_VERIFICACION, NO_VERIFICADO}

#### 3.2.3 Reglas de scoring (ejemplo base)
> Ajustable por el docente/equipo.
- **R1 Dominio en lista blanca**: +40
- **R2 Evidencia URL válida (https) y accesible**: +15
- **R3 Timestamp reciente (<= X horas)**: +15
- **R4 Campos mínimos completos**: +10
- **R5 Corroboración cruzada (si habilitada)**: +20

Umbrales sugeridos:
- **CONFIRMADO:** score ≥ 70
- **EN_VERIFICACION:** 40–69
- **NO_VERIFICADO:** < 40

---

### 3.3 Requisitos de interfaces externas

#### 3.3.1 Interfaces de usuario (UI)
- **UI-01:** Panel web responsive con:
  - Dashboard (últimas alertas)
  - Gestión de fuentes
  - Vista de scraping (estado/errores)
  - Reglas de verificación
  - Suscripciones (usuario)

#### 3.3.2 Interfaces de software (API)
- **API-01:** `GET /alerts?type=&zone=&from=&to=&status=`
- **API-02:** `GET /alerts/{id}`
- **API-03:** `POST /admin/sources` (admin)
- **API-04:** `POST /admin/sources/{id}/run` (admin/operador)
- **API-05:** `POST /subscriptions` (usuario)

#### 3.3.3 Interfaces de comunicaciones
- Uso de HTTPS para comunicaciones externas.
- Canales de notificación (Telegram/email/WhatsApp) vía APIs del proveedor.

---

### 3.4 Requisitos no funcionales (NFR)

#### 3.4.1 Rendimiento
- **NFR-01:** El sistema debe procesar un evento desde detección hasta publicación en ≤ 60 s (promedio) en ambiente de laboratorio.
- **NFR-02:** El sistema soportará al menos 1000 eventos almacenados y consultas concurrentes básicas (≥ 20 usuarios).

#### 3.4.2 Disponibilidad y tolerancia a fallos
- **NFR-03:** Ante caída de una fuente, el sistema debe continuar operando con las restantes.
- **NFR-04:** Los scrapers deben reintentar con backoff hasta N veces antes de marcar error.

#### 3.4.3 Seguridad
- **NFR-05:** Autenticación con JWT (o sesión segura) para panel.
- **NFR-06:** Gestión de secretos (tokens/credenciales) por variables de entorno o vault.
- **NFR-07:** Control de acceso por rol.
- **NFR-08:** Sanitización de entradas (evitar inyección en filtros y manejo seguro de archivos si hubiera uploads).

#### 3.4.4 Privacidad
- **NFR-09:** El sistema no almacenará datos sensibles personales; suscripciones solo guardarán identificadores mínimos.

#### 3.4.5 Mantenibilidad
- **NFR-10:** Cada fuente tendrá un scraper desacoplado con pruebas unitarias de parsing.
- **NFR-11:** Documentación de configuración de scrapers y reglas.

#### 3.4.6 Portabilidad
- **NFR-12:** Despliegue mediante Docker Compose.

#### 3.4.7 Observabilidad
- **NFR-13:** Logs estructurados y métricas exportables.

---

### 3.5 Requisitos de calidad de datos
- **DQ-01:** Campos obligatorios no nulos en eventos normalizados.
- **DQ-02:** Deduplicación basada en (tipo + zona + occurred_at ventana + fuente).
- **DQ-03:** Registro de evidencia URL para eventos publicados.

---

## 4. Casos de uso (resumen)

### CU-01: Configurar fuente oficial (Admin)
- **Pre:** Admin autenticado.
- **Flujo:** Admin crea fuente → define frecuencia y parser → activa.
- **Post:** Fuente lista para scraping.

### CU-02: Ejecutar scraping y publicar alerta
- **Pre:** Fuente activa.
- **Flujo:** Scraper detecta evento → normaliza → verifica → publica → notifica.
- **Post:** Evento visible y notificado si CONFIRMADO.

### CU-03: Suscribirse a alertas (Usuario)
- **Pre:** Usuario registrado.
- **Flujo:** Usuario selecciona tipo/zona/canal → guarda.
- **Post:** Recibe notificaciones futuras.

### CU-04: Revisar evento en verificación (Operador)
- **Pre:** Operador autenticado.
- **Flujo:** Filtra EN_VERIFICACION → revisa evidencia → (opcional) marca como CONFIRMADO/NO_VERIFICADO.
- **Post:** Se actualiza estado y auditoría.

---

## 5. Criterios de aceptación (por entregable)

### 5.1 MVP (Fase II)
- Scraping funcionando para 2 fuentes.
- Normalización + deduplicación.
- Panel con listado/filtros.
- Verificación por reglas básicas + estados.

### 5.2 Versión final (Fase III)
- 3 fuentes integradas.
- Corroboración cruzada (al menos para 1 tipo de evento).
- Notificaciones operativas (Telegram/email).
- Docker Compose + documentación + demo reproducible.

---

## 6. Matriz de trazabilidad (ejemplo)
| Requisito | Caso de uso | Módulo |
|---|---|---|
| RF-01 | CU-01 | Panel Admin / Sources |
| RF-04 | CU-02 | Scrapers |
| RF-11 | CU-02 | Verification Service |
| RF-20 | CU-02 | Notification Service |
| RF-19 | CU-03 | Subscriptions |

---

## 7. Apéndices

### 7.1 Riesgos y mitigaciones
- **Cambio de HTML en fuentes:** parsers con tests; alertas de parsing fallido; fallback.
- **Bloqueos por scraping agresivo:** rate limit, caching, frecuencia razonable.
- **Falsos positivos:** reglas explicables, umbrales ajustables, revisión humana opcional.

### 7.2 Supuestos de despliegue (laboratorio)
- 1 VM o PC con Docker.
- Base de datos (PostgreSQL) en contenedor.
- Servicios en contenedores separados.

### 7.3 Glosario de severidad (sugerido)
- Baja / Media / Alta según fuente.

---

**Fin del documento**