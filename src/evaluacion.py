"""Auditoría reproducible de LOGISMART: umbrales en validación y comunas en test.

No reentrena, no cambia el modelo ni el umbral seleccionado en H4-T1.
Ejecutar desde raíz: python -m src.evaluacion
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from src.modelado import dividir_temporalmente, separar_xy, metricas
from src.pipeline_datos import FECHA


def tabla_umbrales(y_val, probabilidades, umbrales=None):
    """Compara decisiones usando únicamente VALIDACIÓN, nunca test."""
    if umbrales is None:
        umbrales = np.round(np.arange(0.05, 0.51, 0.05), 2)
    filas = []
    for u in umbrales:
        met = metricas(y_val, probabilidades, umbral=float(u))
        tn, fp = met["matriz_confusion"][0]
        fn, tp = met["matriz_confusion"][1]
        filas.append({"umbral": round(float(u), 4), "precision": met["precision"],
                      "recall": met["recall"], "f1": met["f1"],
                      "tasa_alertas": met["tasa_alertas"],
                      "tp": tp, "fp": fp, "fn": fn, "tn": tn})
    return pd.DataFrame(filas)


def tabla_comunas(test, probabilidades, umbral, minimo_positivos=30):
    """Audita el destino en TEST: métricas descriptivas, no selecciona umbral."""
    if len(test) != len(probabilidades):
        raise ValueError("Test y probabilidades tienen longitudes distintas")
    datos = test[["comuna_destino", "retraso"]].copy().reset_index(drop=True)
    datos["p"] = np.asarray(probabilidades)
    datos["alerta"] = datos["p"].ge(float(umbral)).astype(int)
    datos["tp"] = ((datos["retraso"] == 1) & (datos["alerta"] == 1)).astype(int)
    datos["fp"] = ((datos["retraso"] == 0) & (datos["alerta"] == 1)).astype(int)
    grupos = datos.groupby("comuna_destino", observed=True).agg(
        operaciones=("retraso", "size"), retrasos=("retraso", "sum"),
        alertas=("alerta", "sum"), tp=("tp", "sum"), fp=("fp", "sum"),
    )
    grupos["tasa_retrasos"] = grupos["retrasos"] / grupos["operaciones"]
    grupos["tasa_alertas"] = grupos["alertas"] / grupos["operaciones"]
    grupos["precision"] = grupos["tp"] / grupos["alertas"].replace(0, np.nan)
    grupos["recall"] = grupos["tp"] / grupos["retrasos"].replace(0, np.nan)
    grupos["retrasos_sin_alerta"] = grupos["retrasos"] - grupos["tp"]
    grupos["muestra_suficiente_recall"] = grupos["retrasos"] >= minimo_positivos
    return grupos.reset_index().sort_values("operaciones", ascending=False)


def evaluar(entrada="data/processed/logismart_modelado.csv", carpeta_modelos="models"):
    """Regenera auditoría a partir de pipeline guardado y división temporal fija."""
    carpeta = Path(carpeta_modelos)
    ruta_json = carpeta / "resultados_modelado.json"
    ruta_modelo = carpeta / "modelo_logismart.joblib"
    if not ruta_json.exists() or not ruta_modelo.exists():
        raise FileNotFoundError("Ejecuta primero: python main.py --proceso entrenar")
    resumen = json.loads(ruta_json.read_text(encoding="utf-8"))
    if resumen.get("modo_rapido"):
        raise ValueError("La auditoría oficial requiere entrenamiento completo, no modo rápido")
    modelo = joblib.load(ruta_modelo)  # archivo local de confianza; nunca cargar joblib ajenos
    df = pd.read_csv(entrada, parse_dates=[FECHA])
    _, val, test = dividir_temporalmente(df)
    if (len(val) != resumen["filas_utilizadas"]["validacion"] or
            len(test) != resumen["filas_utilizadas"]["test"]):
        raise ValueError("Los períodos del CSV no coinciden con los del entrenamiento guardado")
    X_val, y_val = separar_xy(val)
    X_test, y_test = separar_xy(test)
    proba_val = modelo.predict_proba(X_val)[:, 1]
    proba_test = modelo.predict_proba(X_test)[:, 1]
    umbral = float(resumen["umbral_elegido_en_validacion"])
    # Protege contra desalineación accidental modelo/JSON o CSV sustituido.
    auc = roc_auc_score(y_test, proba_test)
    pr_auc = average_precision_score(y_test, proba_test)
    if not (np.isclose(auc, resumen["resultado_test"]["roc_auc"], atol=1e-8) and
            np.isclose(pr_auc, resumen["resultado_test"]["pr_auc"], atol=1e-8)):
        raise ValueError("Modelo/CSV no corresponden con las métricas oficiales del JSON")
    umbrales = tabla_umbrales(y_val, proba_val, umbrales=sorted(set(
        np.round(np.arange(0.05, 0.51, 0.05), 2).tolist() + [round(umbral, 4)])))
    comunas = tabla_comunas(test, proba_test, umbral)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_u = carpeta / "auditoria_umbrales_validacion.json"
    ruta_c = carpeta / "auditoria_comunas_test.json"
    ruta_u.write_text(umbrales.to_json(orient="records", indent=2, force_ascii=False), encoding="utf-8")
    ruta_c.write_text(comunas.to_json(orient="records", indent=2, force_ascii=False), encoding="utf-8")
    print("Auditoría LOGISMART (modelo sin reentrenamiento)")
    print(f"Umbral oficial: {umbral:.2f} | AUC test: {auc:.4f} | PR-AUC test: {pr_auc:.4f}")
    print("\nUmbrales en VALIDACIÓN:")
    print(umbrales[["umbral", "precision", "recall", "f1", "tasa_alertas"]].round(3).to_string(index=False))
    print("\nComunas en TEST (primeras 10 por operaciones):")
    print(comunas[["comuna_destino", "operaciones", "retrasos", "precision", "recall", "tasa_alertas"]].head(10).round(3).to_string(index=False))
    print(f"\nGuardado: {ruta_u} y {ruta_c}")
    return {"umbrales_validacion": umbrales, "comunas_test": comunas}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auditoría de umbrales y comunas de LOGISMART")
    parser.add_argument("--entrada", default="data/processed/logismart_modelado.csv")
    parser.add_argument("--carpeta-modelos", default="models")
    args = parser.parse_args()
    evaluar(entrada=args.entrada, carpeta_modelos=args.carpeta_modelos)
