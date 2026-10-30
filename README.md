# LOGISMART — Predicción de retrasos en entregas de última milla

Proyecto académico de **Gestión de Proyectos de Datos** (Duoc UC) basado en el caso ficticio **LOGISMART**. El objetivo es desarrollar y documentar un prototipo que permita **estimar el riesgo de retraso de entregas** y apoyar decisiones operacionales, aplicando la metodología **CRISP-DM**.

> **Estado:** proyecto en desarrollo. El generador del dataset sintético es la primera evidencia técnica; las tareas de análisis, modelado, evaluación y visualización se documentarán conforme se implementen. No se utiliza información real de clientes ni de conductores.

## Contexto del caso

LOGISMART es una empresa ficticia de distribución de última milla en las regiones Metropolitana y de Valparaíso. Según el caso académico, realiza aproximadamente **75.000 entregas mensuales** y la proporción de entregas fuera de plazo aumentó de alrededor de **8 % a 15 %** en seis meses. Se plantea anticipar los retrasos para facilitar la priorización de despachos y las alertas preventivas.

El caso establece un presupuesto inicial máximo de **CLP $20.000.000** y una duración de **16 semanas**. Estos valores corresponden al escenario de planificación, **no a gastos ni tiempos ejecutados**.

## Objetivo de esta etapa

Generar una base de datos sintética reproducible como punto de partida para las siguientes actividades de ciencia de datos.

- **Volumen configurado:** 450.000 entregas, equivalentes a 75.000 entregas mensuales durante seis meses.
- **Período simulado:** abril–septiembre de 2026.
- **Estructura esperada:** 21 columnas con características de las entregas, variables operacionales y estado final.
- **Semilla aleatoria:** `42` para reproducibilidad.
- **Salida:** `logismart_entregas_simuladas.csv`.

Los registros, la distribución territorial, las características de los conductores y el mecanismo de generación de retrasos son **simulados**. La cantidad mensual y el cambio aproximado en la tasa de retrasos se basan en el enunciado del caso; los demás parámetros son supuestos académicos y no constituyen estadísticas reales de LOGISMART.

## Metodología CRISP-DM

| Fase | Trabajo previsto |
| --- | --- |
| **1. Business Understanding** | Objetivos, alcance, indicadores y priorización MoSCoW. |
| **2. Data Understanding** | Generación/obtención de datos, análisis exploratorio y diagnóstico de calidad. |
| **3. Data Preparation** | Limpieza, protección de identificadores, tratamiento del desbalance e ingeniería de variables. |
| **4. Modeling** | Entrenamiento y análisis de modelos predictivos. |
| **5. Evaluation** | Métricas, validaciones y análisis de equidad territorial. |
| **6. Deployment** | Demostración de resultados, documentación y cierre del prototipo. |

**Seguimiento:** las actividades, responsables, plazos y evidencias se gestionan en [GitHub Projects — Backlog LOGISMART](https://github.com/users/carlos31255/projects) y en los Issues de este repositorio. El enlace es a la sección general de proyectos del perfil; seleccionar allí «Backlog LOGISMART».

## Requisitos para generar el dataset

- Python 3.10 o superior (recomendado).
- Bibliotecas `numpy` y `pandas`.
- Un entorno como Visual Studio Code, Google Colab o Jupyter Notebook.

Instalación de dependencias en una terminal:

```bash
python -m pip install numpy pandas
```

## Ejecución

Si el archivo `logismart_generacion_450k.py` está en la raíz del repositorio:

```bash
python logismart_generacion_450k.py
```

El script escribe `logismart_entregas_simuladas.csv` en el directorio desde el que se ejecuta. Al finalizar, muestra la cantidad de filas y columnas y una vista preliminar de los datos.

También es posible ejecutar la versión `LogiSmart_H2_T1_Dataset_450k.ipynb` en Colab o Jupyter, si se incorpora al repositorio.

### Comprobaciones esperadas

- 450.000 filas y 21 columnas.
- Registros fechados entre abril y septiembre de 2026.
- Campos como `comuna_origen`, `comuna_destino`, `distancia_km`, `tipo_vehiculo`, `n_paradas`, `duracion_estimada_min` y `retraso`.
- Valores faltantes introducidos deliberadamente en algunas variables, para trabajar posteriormente la calidad de datos.

> El archivo CSV puede superar los 50 MB; por ello se recomienda **no versionarlo directamente en Git**. Se puede regenerar desde el script y documentar la ejecución mediante sus resultados y capturas. Agrega `logismart_entregas_simuladas.csv` al `.gitignore` si trabajas con Git local.

## Alcance y limitaciones

- Los datos sintéticos **no representan operaciones reales** ni permiten atribuir resultados a la empresa ficticia.
- La simulación utiliza supuestos sobre distancias, carga, congestión, lluvia y retrasos; algunas relaciones no reflejan trayectos geográficos reales.
- Las variables generadas durante o después de una entrega deben distinguirse de las disponibles **antes del despacho**, para evitar fuga de información en una etapa posterior de modelado.
- La integración real con PostgreSQL o Amazon S3 y el formato final de visualización (**Python, Power BI, Looker Studio u otra alternativa**) están **pendientes de confirmación con la docente**.
- Las pruebas de modelos en notebooks anteriores se consideran **experimentales** y no se declaran aquí como entregables definitivos.

## Equipo de proyecto

| Integrante | Rol planificado |
| --- | --- |
| Bruno Miranda | Project Manager (PM) |
| Carlos Hidalgo | Data Scientist (DS) |
| Gabriel Caroca | Data Engineer (DE) |
| Keiny Navarro | Data Engineer (DE) |

Los responsables de cada actividad se detallan en el tablero de seguimiento del proyecto.

## Documentación y fuentes del escenario

- *CASO 3. LOGISMART — Predicción de retrasos en entregas de última milla* (material de la asignatura).
- *EP5 — Instrucciones y pauta de evaluación* (encargo de implementación, monitoreo y control).

La documentación de evaluaciones anteriores se utiliza como **línea base interna del proyecto**; no se presenta como fuente bibliográfica externa.

---

**Uso académico:** proyecto ficticio realizado con datos generados artificialmente, sin conexión con operaciones reales de una empresa.
