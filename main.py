"""Punto de entrada LOGISMART: generar, preparar, entrenar o ejecutar todo.

Sin argumentos conserva el comportamiento anterior: genera el dataset sintético.
"""
import argparse
from pathlib import Path

import pandas as pd

from src.generador_dataset import generar_dataset

FECHA_INICIO = pd.Timestamp("2025-08-01")
FECHA_FIN = pd.Timestamp("2026-09-30")
COLUMNAS_ESPERADAS = 21


def validar(df: pd.DataFrame, n: int) -> None:
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


def generar(registros: int, semilla: int, salida: Path) -> None:
    if registros <= 0:
        raise ValueError("--registros debe ser mayor que cero")
    print(f"Generando {registros:,} operaciones sintéticas (semilla {semilla})...")
    df = generar_dataset(n=registros, semilla=semilla)
    validar(df, registros)
    salida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(salida, index=False, date_format="%Y-%m-%d")
    recuperado = pd.read_csv(salida, parse_dates=["fecha"])
    validar(recuperado, registros)
    if list(recuperado.columns) != list(df.columns):
        raise ValueError("Orden o nombres de columnas no coinciden tras exportar")
    resumen = recuperado.groupby(recuperado["fecha"].dt.to_period("M")).agg(
        operaciones=("id_entrega", "size"), retrasos=("retraso", "sum"), tasa_retraso=("retraso", "mean")
    )
    resumen["tasa_retraso_pct"] = (resumen["tasa_retraso"] * 100).round(2)
    nulos = recuperado.isna().sum()
    print(f"\nArchivo: {salida.resolve()}")
    print(f"Filas: {len(recuperado):,} | Columnas: {recuperado.shape[1]}")
    print(f"Meses representados: {len(resumen)} de 14")
    print(f"Promedio por mes representado: {len(recuperado) / len(resumen):,.0f} operaciones")
    print("\nResumen mensual (tasas calculadas, no impuestas):")
    print(resumen[["operaciones", "retrasos", "tasa_retraso_pct"]].to_string())
    print("\nNulos por columna:")
    print(nulos[nulos > 0].to_string() if (nulos > 0).any() else "Ninguno")
    print("\nValidaciones básicas: OK")


def ejecutar() -> None:
    ap = argparse.ArgumentParser(description="LOGISMART: generación, preparación y modelado")
    ap.add_argument("--proceso", choices=["generar", "preparar", "entrenar", "completo"], default="generar")
    ap.add_argument("--registros", type=int, default=1_050_000)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--salida", type=Path, default=Path("data/raw/logismart_entregas_simuladas.csv"),
                    help="Ruta CSV de generación, conserva la CLI anterior")
    ap.add_argument("--modo-rapido", action="store_true", help="Limitar train/val/test para una prueba rápida")
    args = ap.parse_args()

    if args.proceso in ("generar", "completo"):
        generar(args.registros, args.semilla, args.salida)
    if args.proceso in ("preparar", "completo"):
        from src.pipeline_datos import preparar_datos
        preparar_datos(entrada=args.salida)
    if args.proceso in ("entrenar", "completo"):
        from src.modelado import entrenar
        entrenar(modo_rapido=args.modo_rapido, semilla=args.semilla)


if __name__ == "__main__":
    ejecutar()
