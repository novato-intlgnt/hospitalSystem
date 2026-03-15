## Business Rules

### Gestión de Pacientes y Exámenes

- **RN-01 (Identidad Única):** Todo paciente debe estar registrado con un código de historia clínica único. No pueden existir dos pacientes con el mismo ID.
- **RN-02 (Vínculo Obligatorio):** Un examen médico no puede existir en el sistema si no está asociado a un paciente previamente registrado.
- **RN-03 (Estados del Examen):** Un examen debe seguir un flujo de estados: `Pendiente` (creado), `En Proceso` (imágenes cargadas), `Informado` (médico firmó) y `Entregado`.
- **RN-04 (Integridad de Imágenes):** Un examen puede registrarse sin imágenes inicialmente (para equipos offline), pero no puede marcarse como `Completo` hasta que se asocien los archivos correspondientes.

### Informes y Firmas

- **RN-05 (Exclusividad de Firma):** Solo los usuarios con rol "Médico" debidamente autenticados pueden redactar y firmar informes.
- **RN-06 (Inmutabilidad de Informes):** Una vez que un informe es firmado y guardado, el original no se puede borrar ni editar. Cualquier corrección debe generar una **nueva versión** manteniendo el historial (versionado).
- **RN-07 (Responsabilidad Legal):** Cada informe debe incluir el nombre, especialidad y número de colegiatura del médico firmante de forma automática al momento de la firma.

### Estaciones de trabajo

- **RN-08 (Peticion de habilitacion de maquina):** Las maquinas hacen una solicitud de habilitacion al administrador, ademas de enviar su direccion IP y MAC, ubicacion fisica y tipo (adquisicion o visualizacion)
- **RN-09 (Clasificación de Terminales):** Toda máquina en la red debe estar identificada y clasificada como `ADQUISICION` (pueden subir datos) o `VISUALIZACION` (solo lectura).
- **RN-10 (Restricción de Carga):** La creación de exámenes y la subida de imágenes DICOM está restringida exclusivamente a máquinas de tipo `ADQUISICION`.
- **RN-11 (Restricción de Operaciones Legales):** El login de médicos para la elaboración y firma de informes solo se permitirá en máquinas autorizadas (pueden ser de adquisición o estaciones de trabajo médicas específicas).
- **RN-12 (Visualización de Red):** Las máquinas de `VISUALIZACION` permiten la consulta de exámenes e informes ya finalizados sin login, pero bloquean cualquier intento de edición o creación.
- **RN-13 (Trazabilidad de Hardware):** Toda acción registrada en el sistema debe auditar la dirección IP y el identificador de la máquina de origen, además del usuario (si lo hay).

### Usuarios y Roles

- **RN-14 (Creacion de usuarios):** Solo el administrador puede crear cuentas de usuario, asignar roles.
- **RN-15 (Usuario Medico):** El medico puede ver solo pacientes y examenes, redactar y firmar informes
- **RN-16 (Firmar reporte):** Puede firmar solo si tiene sus credenciales registradas(CMP y RNE) y se loguea desde una maquina autorizada.(revisar userQueryGateway)

---

## 🛠️ 2. Rol del Administrador (Módulo de Auditoría y Control)

El administrador no ve pacientes, **ve el sistema**. Sus funciones principales serían:

### Gestión de Usuarios

- **Creación de Cuentas:** Alta de médicos, personal administrativo y técnicos.
- **Gestión de Credenciales:** Resetear contraseñas y desactivar cuentas (no borrarlas, por trazabilidad).
- **Asignación de Roles:** Definir quién puede solo ver imágenes y quién puede firmar.

### Módulo de Auditoría (El "Log")

El Admin debe tener una vista donde pueda filtrar acciones por:

- **¿Quién?** (Usuario que realizó la acción).
- **¿Qué?** (Ver imagen, descargar informe, modificar datos de paciente).
- **¿Cuándo?** (Fecha y hora exacta).
- **¿Desde dónde?** (Dirección IP de la máquina de la LAN).

### Gestión de Maestros (Configuración)

- **Catálogo de Exámenes:** El admin es quien ingresa los Tipos y Subtipos acordados en la reunión con los médicos.
- **Gestión de Plantillas:** Cargar y editar los esqueletos de texto para cada tipo de informe.
