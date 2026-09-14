"""Métricas técnicas, de negocio y evaluación temporal (checkpoint 1, sección 5)."""
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, precision_score, recall_score, roc_auc_score


def compute_metrics(y_true, y_pred, y_proba=None) -> dict:
    """F1, precision, recall y (si hay score) ROC-AUC."""
    metrics = {
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
    }
    if y_proba is not None:
        metrics["roc_auc"] = roc_auc_score(y_true, y_proba)
    return metrics


def business_cost(y_true, y_pred, fraud_amount: float = 120.0, friction_cost: float = 15.0) -> float:
    """Costo = FN x monto_promedio_fraude + FP x costo_fricción
    (fórmula de la métrica de decisión del checkpoint 1, sección 5)."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    return fn * fraud_amount + fp * friction_cost


def evaluate_by_time_block(
    df: pd.DataFrame, y_true_col: str, y_pred_col: str,
    dt_col: str = "TransactionDT", n_blocks: int = 10,
) -> pd.DataFrame:
    """Divide en bloques cronológicos y calcula métricas por bloque, para
    visualizar la degradación del modelo en el tiempo (PDF sección 3.3)."""
    df = df.sort_values(dt_col).copy()
    df["_block"] = pd.qcut(df[dt_col], q=n_blocks, labels=False, duplicates="drop")
    rows = []
    for block, group in df.groupby("_block"):
        m = compute_metrics(group[y_true_col], group[y_pred_col])
        m["block"] = block
        rows.append(m)
    return pd.DataFrame(rows)
