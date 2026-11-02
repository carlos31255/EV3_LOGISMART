"""Entrada de generación, control de calidad y exportación CSV LOGISMART."""

import argparse
from pathlib import Path

import pandas as pd

from src.generador_dataset import generar_dataset

FECHA_INICIO = pd.Timestamp("2025-08-01")
FECHA_FIN = pd.Timestamp("2026-09-30")
COLUMNAS_ESPERADAS = 21


def validar(df: pd.DataFrame, n: int) -> None:
    """Validaciones de estructura, período, integridad y objetivo."""
    if len(df) != n:
        raise ValueError(f"Filas inesperadas: {len(df)} (esperadas: {n})")
    if df.shape[1] != COLUMNAS_ESPERADAS:
        raise ValueError(f"Columnas inesperadas: {df.shape[1]}")
    if df["id_entrega"].isna().any() or not df["id_entrega"].is_unique:
        raise ValueError("Identificadores nulos o duplicados")
    if df["fecha"].isna().any() or not df["fecha"].between(FECHA_INICIO, FECHA_FIN).all():
        raise ValueError("Hay fechas inválidas o fuera del período")
    if df["retraso"].isna().any() or not df["retraso"].isin([0, 1]).all():
        raise ValueError("Indicador de retraso inválido o nulo")
    if df["estado_final"].isna().any() or not (
        df["estado_final"] == df["retraso"].map({0: "Entregada a tiempo", 1: "Entregada con retraso"})
    ).all():
        raise ValueError("Estado final incoherente con el objetivo")
    if (df["n_paradas"] < 1).any() or (df["n_paquetes"] < 1).any():
        raise ValueError("Paquetes o paradas fuera de rango")


def ejecutar() -> None:
    parser = argparse.ArgumentParser(description="Genera y valida datos sintéticos LOGISMART")
    parser.add_argument("--registros", type=int, default=1_050_000,
                        help="Número de operaciones sintéticas (por defecto: 1050000)")
    parser.add_argument("--semilla", type=int, default=42,
                        help="Semilla aleatoria (por defecto: 42)")
    parser.add_argument("--salida", type=Path,
                        default=Path("data/raw/logismart_entregas_simuladas.csv"),
                        help="Ruta del CSV de salida")
    args = parser.parse_args()
    if args.registros <= 0:
        parser.error("--registros debe ser mayor que cero")

    print(f"Generando {args.registros:,} operaciones sintéticas (semilla {args.semilla})...")
    df = generar_dataset(n=args.registros, semilla=args.semilla)
    validar(df, args.registros)

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.salida, index=False, date_format="%Y-%m-%d")

    # Verificar que la exportación completa puede recuperarse.
    recuperado = pd.read_csv(args.salida, parse_dates=["fecha"])
    validar(recuperado, args.registros)
    if list(recuperado.columns) != list(df.columns):
        raise ValueError("Orden o nombres de columnas no coinciden tras exportar")

    resumen = recuperado.groupby(recuperado["fecha"].dt.to_period("M")).agg(
        operaciones=("id_entrega", "size"),
        retrasos=("retraso", "sum"),
        tasa_retraso=("retraso", "mean"),
    )
    resumen["tasa_retraso_pct"] = (resumen["tasa_retraso"] * 100).round(2)
    nulos = recuperado.isna().sum()

    print(f"\nArchivo: {args.salida.resolve()}")
    print(f"Filas: {len(recuperado):,} | Columnas: {recuperado.shape[1]}")
    print(f"Meses representados: {len(resumen)} de 14")
    print(f"Promedio por mes representado: {len(recuperado) / len(resumen):,.0f} operaciones")
    print("\nResumen mensual (tasas calculadas, no impuestas):")
    print(resumen[["operaciones", "retrasos", "tasa_retraso_pct"]].to_string())
    print("\nNulos por columna:")
    print(nulos[nulos > 0].to_string() if (nulos > 0).any() else "Ninguno")
    print("\nValidaciones básicas: OK")


if __name__ == "__main__":
    ejecutar()
