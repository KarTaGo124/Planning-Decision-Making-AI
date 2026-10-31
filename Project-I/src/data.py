"""Carga de datos para IEEE-CIS Fraud Detection.

Dataset: https://www.kaggle.com/c/ieee-fraud-detection/data
Colocar train_transaction.csv y train_identity.csv en data/raw/.
"""
from pathlib import Path
from typing import Optional

import pandas as pd

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def load_transaction_data(raw_dir: Path = RAW_DIR, sample_frac: Optional[float] = None) -> pd.DataFrame:
    """Carga y fusiona las tablas transaction + identity de IEEE-CIS.

    Parameters
    ----------
    raw_dir: carpeta con train_transaction.csv y train_identity.csv.
    sample_frac: si se indica, devuelve una submuestra aleatoria (útil para
        iterar rápido antes de correr sobre el dataset completo).

    Returns
    -------
    DataFrame fusionado por TransactionID (left join: no todas las
    transacciones tienen datos de identidad asociados), ordenado por
    TransactionDT (orden cronológico).
    """
    transaction_path = raw_dir / "train_transaction.csv"
    identity_path = raw_dir / "train_identity.csv"

    if not transaction_path.exists():
        raise FileNotFoundError(
            f"No se encontró {transaction_path}. Descarga el dataset de "
            "https://www.kaggle.com/c/ieee-fraud-detection/data y colócalo en data/raw/."
        )

    transactions = pd.read_csv(transaction_path)
    if identity_path.exists():
        identity = pd.read_csv(identity_path)
        df = transactions.merge(identity, on="TransactionID", how="left")
    else:
        df = transactions

    df = df.sort_values("TransactionDT").reset_index(drop=True)

    if sample_frac is not None:
        df = (
            df.sample(frac=sample_frac, random_state=42)
            .sort_values("TransactionDT")
            .reset_index(drop=True)
        )

    return df


def reduce_memory_usage(df: pd.DataFrame) -> pd.DataFrame:
    """Reduce el tamaño en memoria haciendo downcast de columnas numéricas."""
    for col in df.select_dtypes(include=["int64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="integer")
    for col in df.select_dtypes(include=["float64"]).columns:
        df[col] = pd.to_numeric(df[col], downcast="float")
    return df
