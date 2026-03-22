# Reglas de Negocio (RN) - Sistema Hospitalario Integrado

Este documento detalla las reglas de negocio (RN) que rigen el comportamiento del sistema HIS/RIS/PACS en la red interna del hospital.

## 1. Gestión de Pacientes e Identidad (HIS Básico)

- **RN-01 (Identidad Única):** Todo paciente debe estar registrado con un código de historia clínica único (DNI o código interno). No pueden existir duplicados en el sistema.
- **RN-02 (Registro Universal):** Cualquier terminal en la red hospitalaria (LAN) puede registrar un paciente, dado que el hospital prioriza la agilidad en la atención.
- **RN-03 (Acceso a Datos):** La consulta de datos básicos de pacientes es libre dentro de la red interna para facilitar la interoperabilidad entre áreas (Emergencia, Hospitalización).

## 2. Ciclo de Vida del Examen (RIS)

- **RN-04 (Vínculo Obligatorio):** Un examen médico no puede existir en el sistema si no está asociado a un paciente previamente registrado.
- **RN-05 (Clasificación Estándar):** Todo examen debe clasificarse obligatoriamente por un Tipo (ej. Tomografía) y Sub-tipo (ej. Tórax) basado en un catálogo maestro legal.
- **RN-06 (Flujo de Estados):** Un examen debe seguir el siguiente flujo de estados:
  - `Pendiente`: Examen registrado, pero sin imágenes asociadas.
  - `Incompleto`: Imágenes cargadas pero el examen no ha sido validado técnicamente o le faltan proyecciones.
  - `Completo`: El examen tiene todas las imágenes requeridas y está listo para ser informado por un médico.
  - `Informado`: El médico ha firmado el reporte legal del examen.
- **RN-07 (Equipos Desconectados):** Se permite registrar un examen manualmente antes de que las imágenes lleguen al sistema, soportando equipos de adquisición no integrados (equipos offline).

## 3. Gestión de Imágenes Diagnósticas (PACS)

- **RN-08 (Restricción de Carga):** La subida de imágenes médicas (DICOM o formatos estándar) está estrictamente limitada a máquinas clasificadas como `ADQUISICION`.
- **RN-09 (Visualización Libre):** Dentro de la red interna, las imágenes de exámenes finalizados o en proceso pueden ser visualizadas y descargadas desde cualquier terminal sin requerir login de usuario.

## 4. Informes Médicos y Firma Electrónica (RIS Legal)

- **RN-10 (Exclusividad de Elaboración):** Solo los usuarios con rol **"Médico"** autenticados pueden redactar informes médicos.
- **RN-11 (Firma Digital Obligatoria):** Un informe médico solo tiene validez legal si está firmado electrónicamente por un médico autenticado.
- **RN-12 (Perfil Profesional):** Solo pueden firmar informes los médicos que tengan registrados su Especialidad y Número de Colegiatura (CMP/RNE) en su perfil de usuario. (RN-16 original mejorada).
- **RN-13 (Plantillas Obligatorias):** Cada informe debe generarse a partir de una plantilla de texto predefinida por el administrador según el tipo de examen.
- **RN-14 (Inmutabilidad y Versionado):** Una vez firmado, el informe original es ineditable. Cualquier corrección genera una **nueva versión**, manteniendo el historial completo para auditoría (RN-06 original).
- **RN-15 (Trazabilidad Legal):** Al momento de la firma, el sistema inyecta automáticamente el Nombre, Especialidad y Colegiatura del médico firmante, además del timestamp y la IP de origen.

## 5. Control de Hardware y Red

- **RN-16 (Clasificación de Máquinas):** Toda terminal conectada al hospital debe estar identificada por su IP/MAC y clasificada como:
  - `ADQUISICION`: Permite registrar pacientes, exámenes y subir imágenes.
  - `VISUALIZACION`: Solo permite la consulta de información sin login.
- **RN-17 (Habilitación de Terminales):** Para que una máquina pueda registrar datos o permitir login de médicos (Firma), debe ser previamente habilitada por un Administrador (RN-08 original).
- **RN-18 (Auditoría de Origen):** Toda acción en el sistema (ver imagen, descargar reporte, firmar) debe registrar obligatoriamente: `ID de Usuario` (si lo hay), `ID de Máquina`, `Dirección IP` y `Timestamp`.

## 6. Gestión Administrativa

- **RN-19 (Control de Acceso):** Solo el Administrador puede crear cuentas de médicos, asignar roles y configurar catálogos de exámenes y plantillas (RN-14 original).
- **RN-20 (Mantenimiento de Sistema):** El administrador puede desactivar usuarios o terminales para revocar su acceso a funciones críticas (Registro/Firma) por razones de seguridad (RN-17 original).
