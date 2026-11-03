# LOGISMART — Dataset sintético y preparación de datos

Proyecto académico de predicción de retrasos en entregas de última milla, organizado con CRISP-DM.
Incluye la **generación del dataset sintético** (H2-T1) y su **preparación para modelado** (H2-T4 a H3-T4).
No entrena modelos ni se conecta a bases de datos productivas.

## Procedencia y supuestos

Según el Caso 3 LOGISMART, la empresa ficticia realiza aproximadamente **75.000 entregas mensuales**, cuenta con cerca de **1.800.000 registros históricos** y presenta un aumento de retrasos desde aproximadamente **8 % a 15 %** en seis meses. Para generar un histórico sintético algo mayor que la mitad del volumen disponible, se simulan **1.050.000 registros de operaciones de reparto**, como volumen sintético de referencia para **14 meses** (promedio aproximado de 75.000 operaciones mensuales). El período se extiende de **agosto de 2025 a septiembre de 2026**. La evolución de retrasos descrita en el caso se reproduce específicamente durante **abril–septiembre de 2026**, mientras que los ocho meses anteriores representan una línea base sintética.

**Importante:** una fila puede contener varios paquetes y paradas; es una **operación de reparto**, no necesariamente un envío individual. La cifra de 75.000 envíos mensuales del caso es referencia de magnitud, no equivalencia directa con el número de filas. Se conserva `id_entrega` por compatibilidad.

Las comunas, conductores, distancias, congestión, probabilidades, valores faltantes y demás distribuciones se simulan con supuestos definidos por el equipo; **no son datos reales ni estadísticas medidas de LOGISMART**. La semilla fija (`42`) permite repetir los resultados con el mismo entorno y parámetros. La selección aleatoria de meses produce volúmenes mensuales cercanos a 75.000, no exactamente idénticos.

## Requisitos

- Python 3.10 o superior
- Dependencias en `requirements.txt` (NumPy, pandas, scikit-learn y pytest, entre otras)

## Ejecutar desde la raíz del repositorio

```bash
python -m venv .venv
```

En Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

En Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

Por defecto, guarda `data/raw/logismart_entregas_simuladas.csv` y presenta un resumen mensual de entregas y tasas de retraso, un conteo de nulos y validaciones básicas.

### Prueba rápida

```bash
python main.py --registros 1000 --salida data/prueba.csv
```

### Cambiar parámetros (opcional)

El comando `python main.py` **ya utiliza** 1.050.000 registros y semilla 42. Para cambiar esos valores de forma explícita:

```bash
python main.py --registros 200000 --semilla 123 --salida data/alternativo.csv
```

## Preparación de datos (H2-T4 a H3-T4)

Las transformaciones están en `src/pipeline_datos.py`. Los datos de `data/raw/` no se modifican.

```bash
python -m pytest -q                              # pruebas
python -m src.pipeline_datos --muestra 20000     # prueba rápida
python -m src.pipeline_datos                     # dataset completo
```

Genera en `data/processed/` (local, no se sube a GitHub):

- `logismart_preparado.csv`: datos validados, conductores seudonimizados y variables derivadas (25 columnas).
- `logismart_modelado.csv`: predictores, `fecha` y `retraso`, sin identificadores (19 columnas).

**Decisiones**

- **Seudonimización:** `id_conductor` se reemplaza por un código estable `COND-xxxx`, sin tabla de correspondencia. Es una medida de protección básica: no garantiza anonimato irreversible (el código puede recalcularse si se conoce el ID original y la clave) ni acredita cumplimiento legal; al ser datos sintéticos, demuestra una práctica de minimización.
- **Limpieza:** 8 reglas de validación (0 incumplimientos); no se eliminan filas. Los nulos de `experiencia_conductor_anios` (1,51 %) y `peso_kg` (1,01 %) se conservan en los datos preparados. `construir_preprocesador()` define la imputación por mediana (con indicador de nulo); su ajuste se realizará exclusivamente con los datos de entrenamiento durante el modelado, para evitar fuga de información. Un test comprueba que la mediana aprendida proviene solo del conjunto de entrenamiento.
- **Minimización:** se excluyen `id_entrega`, `id_conductor` y las variables posteriores al despacho (`retraso_salida_min`, `duracion_real_min`, `incidencias`, `estado_final`).
- **Balanceo:** decisión provisional de no rebalancear, porque la comuna con menos datos (Quintero) tiene 3.341 operaciones. Eso permite analizarla, pero no asegura un buen desempeño en todas las comunas: se verificará el rendimiento por comuna (con su tamaño muestral) durante el modelado y la auditoría de equidad, y solo se evaluará ponderar sobre entrenamiento si se detecta un desempeño claramente peor.
- **Características:** `es_fin_de_semana`, `es_hora_punta`, `franja_horaria` y `paquetes_por_parada`.

## Organización

```text
main.py                       # Entrada, validación y exportación CSV
src/generador_dataset.py      # Reglas de generación sintética
src/pipeline_datos.py         # Preparación de datos (seudonimización, limpieza, características)
tests/test_pipeline_datos.py  # Pruebas del pipeline
requirements.txt              # Dependencias
.gitignore                    # Evita versionar datasets grandes
```

## Evidencia para GitHub Projects

Issue **H2-T1 — Obtención de datos**: registrar el commit de este código, la salida de consola (filas, columnas, resumen mensual, validaciones OK) y, si hace falta, una muestra pequeña del CSV. El CSV completo se genera localmente y no se incluye en Git por defecto.

## Limitaciones

El generador modela distancias y asignaciones mediante distribuciones supuestas; no representa rutas geográficas reales. Algunas variables como duración real e incidencias son posteriores a la operación y **no deben utilizarse como predictoras antes del despacho**. El hecho de que el dataset reproduzca aproximadamente la tendencia del caso no valida un modelo predictivo.

## Nota metodológica

El histórico de 14 meses es una **muestra sintética ampliada** respecto de los 1.800.000 registros mencionados por el caso; no corresponde a una extracción real de PostgreSQL. Los 8 meses previos a abril de 2026 usan una tasa de riesgo base aproximada, como **supuesto del generador**, no como antecedente explícito del caso. Al aumentar el número de filas se requiere más RAM y espacio en disco; para un ensayo rápido usar `--registros 1000`.

## Selección de variables y modelado

Consultar [`DICCIONARIO_Y_MODELADO.md`](DICCIONARIO_Y_MODELADO.md) para conocer la unidad de análisis, las columnas disponibles antes del despacho, las columnas prohibidas para predicción preventiva y la partición temporal sugerida. **El generador no implementa aún el modelo.**
