# LOGISMART — Predicción de retrasos en entregas de última milla

Proyecto académico (Gestión de Proyectos de Datos, SCY1102 · EV3) organizado con CRISP-DM. Genera un dataset sintético de operaciones de reparto, lo prepara, entrena y evalúa modelos de predicción de retraso, audita la equidad territorial, ejecuta inferencia por lotes con respaldo local y entrega un **dashboard simple** que carga archivos JSON para mostrar las alertas y el seguimiento del proyecto.

Todo el trabajo usa **datos sintéticos**: no hay conexión a datos productivos, PostgreSQL ni AWS.

## Entregable funcional: dashboard

`dashboard/index.html` es una página autocontenida (sin servidor ni librerías externas). Se abre con doble clic o desde GitHub Pages.

- **Alertas:** botón «Cargar archivo JSON» con `output/resultados/visualizacion/h6_t2_indicadores.json` (lo genera `python main.py --proceso completo` o, si ya existe una corrida, `python main.py --proceso visualizar`). Actualiza indicadores, distribución por prioridad y escenarios de umbral. Un JSON inválido se rechaza con un mensaje y no cambia la pantalla.
- **Seguimiento del backlog:** el mismo botón acepta `seguimiento.json` (formato con lista `tareas`). Muestra tareas completadas / en proceso, avance por fase CRISP-DM y la tabla de las 24 tareas.
- Ejemplos para probar la carga en `dashboard/ejemplos/` (el escenario 02 es ficticio, solo demostración).
- Lectura local en el navegador: ningún archivo se envía a Internet.

Limitación: las predicciones exportadas no incluyen ID de entrega, comuna ni fecha, por lo que el dashboard muestra alertas agregadas, no una consola de despacho.

## Seguimiento de tareas y backlog

El backlog vive en el tablero de GitHub Projects (Planificación · Backlog LOGISMART). Para actualizar el dashboard necesitas GitHub CLI (`gh`) con sesión iniciada y permiso de proyectos (`gh auth refresh -s project`):

```bash
gh project item-list 1 --owner carlos31255 --limit 100 --format json > seguimiento/backlog_github.json
python seguimiento/generar_seguimiento.py
```

El script genera `dashboard/ejemplos/03_seguimiento_backlog.json` y actualiza los datos incrustados en `dashboard/index.html`. Estado: «Completado» si el tablero lo marca así; cualquier otro estado se muestra como «En proceso». Las fechas son el cronograma planificado (simulado, 16 semanas).

## Reproducción desde cero

El repositorio no incluye los CSV ni el modelo entrenado (`models/*.joblib`): se generan con los pasos siguientes. El dashboard sí viene listo en `dashboard/index.html` con datos de ejemplo incrustados, así que solo necesitas ejecutar el paso 2 para regenerar las alertas y los indicadores desde el pipeline. Los pasos 3 y 4 permiten repetir esas etapas por separado; no son necesarios después de un `completo` exitoso.

### Prerrequisitos

- Python 3.10 o superior y `pip` (entorno de referencia: Python 3.12, NumPy 2.3, pandas 2.2, scikit-learn 1.8, XGBoost 3.4).
- `git` para clonar el repositorio.
- Espacio libre en disco: se generan 1.050.000 filas y los CSV pesan cientos de MB.
- Un navegador actual para abrir el dashboard.
- Opcional: [GitHub CLI](https://cli.github.com/) (`gh`) con sesión iniciada y permiso de proyectos (`gh auth refresh -s project`), solo para actualizar el seguimiento del backlog.
- No requiere GPU, base de datos ni cuentas en la nube.

### 1. Clonar, instalar y probar

```bash
git clone https://github.com/carlos31255/EV3_LOGISMART.git
cd EV3_LOGISMART
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest -q                # 42 pruebas
```

### 2. Ejecutar el flujo completo, incluido el respaldo y la visualización

```bash
python main.py --proceso completo
```

Ejecuta en orden: **generar → preparar → entrenar → evaluar → explicar (SHAP) → automatizar → visualizar**. Si una etapa falla, la ejecución se detiene y no continúa con las siguientes.

Produce:

- Los CSV de `data/raw/` y `data/processed/`.
- El modelo `models/modelo_logismart.joblib`, el resumen `output/resultados/modelado/resultados_modelado.json` y los resultados de evaluación y SHAP.
- Las predicciones y la bitácora en `output/ejecuciones/<id_de_corrida>/`.
- Un respaldo ZIP local verificado en `output/respaldos/`.
- Los indicadores JSON/CSV/PNG y el panel HTML descritos en el paso 4.

La visualización usa el registro de la corrida recién generada, salvo que indiques otro con `--registro-visualizacion`. Al finalizar correctamente, pasa directamente al paso 5 para abrir el dashboard. El seguimiento de GitHub Projects se actualiza por separado, con los comandos de la sección de backlog.

Si usas `--salida` para cambiar la ruta del CSV, `completo` utiliza ese mismo archivo en la automatización. Puedes indicar otra entrada con `--entrada-automatizacion`.

Para llegar solo al dashboard no hacen falta `evaluar` ni `explicar`. Ejecuta esta alternativa y luego los pasos 3 y 4:

```bash
python main.py --proceso generar
python main.py --proceso preparar
python main.py --proceso entrenar
```

### 3. Inferencia por lotes y respaldo (opcional si ya ejecutaste completo)

```bash
python main.py --proceso automatizar
```

Guarda `predicciones.csv` y `registro.json` en `output/ejecuciones/<id_de_corrida>/` y el respaldo ZIP en `output/respaldos/`. Requiere el modelo y `resultados_modelado.json` del paso 2, y que el modelo elegido sea XGBoost entrenado sin `--modo-rapido`. Ejecuta su propia preparación en una carpeta temporal, por lo que no depende de `data/processed/`.

Cada ejecución crea una carpeta con un identificador nuevo (fecha, hora y sufijo aleatorio), por lo que su nombre no coincidirá con el citado en el notebook. Para verificar la reproducción compara el número de alertas (161.875 de 1.050.000 operaciones) y el SHA-256 de `predicciones.csv` (campo `sha256_predicciones` de `registro.json`), no el nombre de la carpeta.

### 4. Indicadores del dashboard (opcional si ya ejecutaste completo)

```bash
python main.py --proceso visualizar
```

Ejecutado individualmente, lee la última corrida exitosa (o la indicada con `--registro-visualizacion`) y genera `output/resultados/visualizacion/h6_t2_indicadores.json` (más CSV y PNG) y el panel `output/visualizacion/panel_h6_t2.html`. Requiere una corrida exitosa de `automatizar`, ejecutada individualmente o dentro de `completo`.

### 5. Abrir el dashboard

Abre `dashboard/index.html` con doble clic, pulsa «Cargar archivo JSON» y selecciona `output/resultados/visualizacion/h6_t2_indicadores.json`. Para el seguimiento del backlog, carga `seguimiento.json` (ver la sección anterior).

### Ejecución uno a uno (todas las evidencias)

`completo` incluye `generar`, `preparar`, `entrenar`, `evaluar`, `explicar`, `automatizar` y `visualizar`, en ese orden. No incluye `optimizar`, `sesgos`, `evaluacion-final`, `batch`, `equidad` ni `validacion-negocio`; estos procesos se solicitan individualmente. Para reproducir todas las evidencias del notebook `notebooks/02_Modelado_LogiSmart.ipynb` (que solo lee resultados ya generados), ejecuta los procesos en este orden, que respeta las dependencias del código y sigue el del backlog (H4-T3 a H6-T2):

```bash
python main.py --proceso generar
python main.py --proceso preparar
python main.py --proceso entrenar
python main.py --proceso evaluar              # antes de sesgos, equidad y validacion-negocio
python main.py --proceso explicar             # SHAP
python main.py --proceso optimizar            # H4-T3
python main.py --proceso sesgos               # H4-T4
python main.py --proceso evaluacion-final     # H5-T1
python main.py --proceso batch                # H5-T2
python main.py --proceso equidad              # H5-T3
python main.py --proceso validacion-negocio   # H5-T4 (después de evaluar y equidad)
python main.py --proceso automatizar          # H6-T1
python main.py --proceso visualizar           # H6-T2 (después de automatizar)
```

La lista anterior es una alternativa desde cero a `completo`, no una secuencia que debas repetir después de él. Si ya ejecutaste `completo` correctamente, solo faltan los seis procesos adicionales indicados arriba para completar esta lista de evidencias.

Qué necesita cada proceso antes de ejecutarse:

| Proceso | Requiere |
|---|---|
| `preparar` | `generar` |
| `entrenar`, `optimizar` | `preparar` (`optimizar` no modifica el modelo oficial) |
| `evaluar`, `explicar`, `evaluacion-final`, `batch` | `entrenar` |
| `sesgos` | `evaluar` |
| `equidad` | `evaluar` |
| `validacion-negocio` | `evaluar` y `equidad` |
| `automatizar` | `generar` y `entrenar` |
| `visualizar` | `automatizar` |

No uses `--modo-rapido` para reproducir resultados: limita el entrenamiento y, en `completo`, solo ejecuta `generar`, `preparar` y `entrenar`: omite evaluación, SHAP, automatización y visualización; además, `automatizar`, `batch`, `evaluar`, `explicar` y `evaluacion-final` rechazan un modelo entrenado en ese modo. Tampoco cambies `--registros` si quieres obtener las cifras del informe.

### Reproducibilidad

El generador usa la semilla 42. Con otras versiones de las librerías, las cifras pueden diferir levemente de las reportadas aquí (por ejemplo, una referencia reentrenada produjo 20.070 alertas frente a 20.581 de la ejecución histórica). Compara siempre entre ejecuciones del mismo entorno.

## Ejecución

Procesos disponibles con `python main.py --proceso <nombre>`:

| Proceso | Qué hace |
|---|---|
| `generar` (por defecto) | Genera 1.050.000 operaciones sintéticas (semilla 42) en `data/raw/` |
| `preparar` | Validación, seudonimización y variables derivadas → `data/processed/` |
| `entrenar` | Entrena Random Forest y XGBoost con partición temporal |
| `optimizar` | Búsqueda de hiperparámetros (H4-T3) |
| `explicar` | Explicabilidad SHAP |
| `sesgos`, `equidad` | Diagnóstico de sesgos y auditoría de equidad territorial |
| `evaluacion-final`, `evaluar` | Evaluación en test y auditoría de umbrales |
| `validacion-negocio` | Escenarios de umbral de alerta (0,10 / 0,15 / 0,20) |
| `batch` | Pruebas de inferencia por lotes (tiempo y memoria) |
| `automatizar` | Preparación + inferencia por lotes + respaldo ZIP verificable |
| `visualizar` | Genera los indicadores JSON/CSV/PNG de la última corrida |
| `completo` | Generar → preparar → entrenar → evaluar → explicar → automatizar con respaldo → visualizar |

Sin argumentos, `python main.py` sigue ejecutando únicamente `generar`.

Prueba rápida: `python main.py --registros 1000 --salida data/prueba.csv`. Los CSV grandes se generan localmente y no se versionan.

## Resultados principales (datos sintéticos)

División temporal: entrenamiento ago 2025–jun 2026 (825.299 filas), validación jul 2026 (74.766) y test ago–sep 2026 (149.935). Selección de modelo y umbral en validación; el test no se usó para elegir.

| Modelo (test) | Umbral | ROC-AUC | PR-AUC | Precisión | Recall |
|---|---|---|---|---|---|
| Random Forest | 0,10 | 0,7021 | 0,2980 | 25,91 % | 57,53 % |
| XGBoost (oficial) | 0,15 | 0,7074 | 0,3044 | 34,56 % | 30,95 % |

La discriminación es limitada. En la corrida H6-T1 se procesaron 1.050.000 operaciones y se emitieron 161.875 alertas (15,42 %) en 19,89 s. Las alertas son prioridades de revisión humana: no demuestran retrasos evitados ni la meta de reducir 20 % los retrasos.

## Organización

```text
main.py                  # Punto de entrada (--proceso)
src/                     # Generador, pipeline, modelado, explicabilidad, equidad, batch, automatización, visualización
tests/                   # Pruebas con pytest
notebooks/               # 01 EDA · 02 Modelado y evidencias H4–H6
dashboard/               # Dashboard HTML y ejemplos JSON
seguimiento/             # Export del backlog y generador de seguimiento.json
docs/                    # Documentación H6-T1 y H6-T2
output/                  # Resultados, gráficos, ejecuciones y respaldos
models/                  # Modelo oficial (.joblib)
```

CI en `.github/workflows/`: `tests.yml` (pytest) y `dashboard-pages.yml` (publica `dashboard/` en GitHub Pages).

## Procedencia y supuestos del dataset

Según el Caso 3, LogiSmart realiza ~75.000 entregas mensuales, tiene ~1.800.000 registros históricos y los retrasos subieron de ~8 % a ~15 % en seis meses. Se simulan **1.050.000 operaciones de reparto** entre agosto de 2025 y septiembre de 2026; la tendencia del caso se reproduce en abril–septiembre de 2026 y los meses previos son una línea base sintética (supuesto del generador). Una fila es una operación de reparto, que puede incluir varios paquetes y paradas. Comunas, conductores, distancias, faltantes y demás distribuciones son supuestos del equipo, no estadísticas medidas de LOGISMART.

## Preparación de datos

`src/pipeline_datos.py` no modifica `data/raw/`.

- **Seudonimización:** `id_conductor` → código `COND-xxxx` sin tabla de correspondencia. Es una medida básica de minimización, no garantiza anonimato irreversible.
- **Limpieza:** 8 reglas de validación (0 incumplimientos); no se eliminan filas. Los nulos de experiencia del conductor (1,51 %) y peso (1,01 %) se imputan por mediana ajustada solo con entrenamiento, para evitar fuga de información.
- **Minimización:** se excluyen identificadores y variables posteriores al despacho (`retraso_salida_min`, `duracion_real_min`, `incidencias`, `estado_final`).
- **Balanceo:** no se rebalanceó el modelo oficial; el rendimiento por comuna se audita en la equidad territorial.

## Limitaciones

- Datos sintéticos: los resultados no son evidencia de desempeño real.
- Sin integración con PostgreSQL ni S3; el respaldo es un ZIP local, no una copia externa.
- Las probabilidades no están calibradas como riesgo real y no hay dotación confirmada para atender las alertas.
- El modelo no debe usarse como sanción automática ni evaluación laboral de conductores.

Más detalle en `docs/H6_T1_AUTOMATIZACION_Y_RESPALDOS.md`, `docs/H6_T1_RESULTADOS_EJECUCION.md` y `docs/H6_T2_VISUALIZACION.md`.
