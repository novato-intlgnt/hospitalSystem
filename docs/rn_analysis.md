# Análisis de Reglas de Negocio (RN) - Sistema HIS/RIS/PACS

Este documento presenta el análisis de las reglas de negocio actuales frente al contexto global del proyecto (Minimundo, Objetivos y Operaciones).

## 📊 1. Alineación con el Contexto (HIS/RIS/PACS)

El sistema propuesto no es un sistema monolítico tradicional, sino una integración de tres dominios:

- **HIS (Hospital Information System):** Registro de pacientes y gestión de datos básicos.
- **RIS (Radiology Information System):** Flujo de trabajo radiológico (estados del examen, informes).
- **PACS (Picture Archiving and Communication System):** Almacenamiento y visualización de imágenes.

### Observaciones sobre el Análisis:

1.  **Acceso Universal en LAN:** El requerimiento funcional indica que **no es obligatorio login** para registrar, visualizar o descargar exámenes en la red interna. Las RN actuales (RN-11, RN-12, RN-16) son consistentes, pero deben enfatizar que el login es **exclusivo para médicos** que firman.
2.  **Flujo de Estados:** Existe una discrepancia entre las RN actuales y la descripción operativa.
    - _Actual:_ `Pendiente` -> `En Proceso` -> `Informado` -> `Entregado`.
    - _Operativo:_ `Pendiente` -> `Incompleto` -> `Completo`.
    - _Mejora:_ Se debe unificar en un flujo que refleje tanto la carga de imágenes como la firma médica.
3.  **Trazabilidad de Hardware:** El requerimiento de auditoría exige IP e Identificador de máquina. La RN-13 es correcta, pero se debe reforzar el concepto de "Máquina Autorizada" para acciones legales (Firma).
4.  **Inmutabilidad y Versionado:** La RN-06 es vital. Se debe aclarar que el "Informado" actual es una versión `1.0` y cualquier cambio genera una `1.x`.
5.  **Equipos Offline:** Se debe permitir la creación del examen _antes_ de la llegada de imágenes (RN-04) para soportar equipos de adquisición no integrados directamente.

## 🔍 2. Gaps Identificados

- **Plantillas (Templates):** Las operaciones mencionan plantillas por tipo de examen, pero no hay una RN que rija su uso o asociación obligatoria.
- **Responsabilidad Legal:** El requerimiento legal (colegiatura, especialidad) debe ser verificado no solo al firmar, sino en el estado del perfil del médico.
- **Clasificación de Exámenes:** Falta una RN que obligue a la clasificación por Tipo y Sub-tipo (catálogo maestro) para garantizar la interoperabilidad.
- **Privacidad en LAN:** Aunque el acceso es libre en la LAN, se debe considerar una RN sobre la integridad: "Cualquier terminal puede ver, pero solo ADQUISICION puede alternar estados críticos".

## 🚀 3. Propuesta de Mejora

Se propone reestructurar las RN en bloques lógicos:

1.  **Identidad y Pacientes** (HIS)
2.  **Ciclo de Vida del Examen** (RIS/PACS)
3.  **Gestión de Imágenes** (PACS)
4.  **Informes y Firma Médica** (RIS Legal)
5.  **Hardware y Auditoría** (Control de Red)
6.  **Gestión Administrativa** (Control de Acceso)
