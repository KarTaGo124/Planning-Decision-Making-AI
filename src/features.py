"""Ingeniería de características temporales (PDF sección 3.2)."""
import pandas as pd

SECONDS_PER_DAY = 24 * 60 * 60


def add_time_features(df: pd.DataFrame, dt_col: str = "TransactionDT") -> pd.DataFrame:
    """Deriva features tipo calendario a partir de TransactionDT (segundos
    relativos a un punto de referencia, no un timestamp real).

    `day` se normaliza para empezar en 0 (día relativo al inicio del
    dataset), evitando que quede un día suelto al final por el offset
    original de TransactionDT."""
    df = df.copy()
    day_raw = (df[dt_col] // SECONDS_PER_DAY).astype(int)
    df["day"] = day_raw - day_raw.min()
    df["hour_of_day"] = (df[dt_col] % SECONDS_PER_DAY) // 3600
    df["day_of_week"] = df["day"] % 7
    return df


def add_rolling_user_features(
    df: pd.DataFrame,
    user_key: str,
    dt_col: str = "TransactionDT",
    amount_col: str = "TransactionAmt",
    window_seconds: int = SECONDS_PER_DAY,
) -> pd.DataFrame:
    """Agrega conteo y monto promedio de transacciones pasadas por entidad
    (ej. card1, dispositivo, email) en una ventana temporal. Son las
    variables rezagadas o agregadas por periodo que pide el PDF (sección 3.2)."""
    df = df.sort_values(dt_col).copy()
    df["_dt"] = pd.to_datetime(df[dt_col], unit="s")
    df = df.set_index("_dt")

    grouped = df.groupby(user_key)[amount_col]
    window = f"{window_seconds}s"
    df[f"{user_key}_txn_count_{window_seconds}s"] = grouped.transform(
        lambda s: s.rolling(window).count()
    )
    df[f"{user_key}_amt_mean_{window_seconds}s"] = grouped.transform(
        lambda s: s.rolling(window).mean()
    )
    return df.reset_index(drop=True)


def chronological_split(df: pd.DataFrame, dt_col: str = "TransactionDT",
                         train_frac: float = 0.6, val_frac: float = 0.2):
    """Split train/val/test respetando estrictamente el orden temporal
    (sin aleatorizar), evitando fugas de información (PDF sección 3.2)."""
    df = df.sort_values(dt_col).reset_index(drop=True)
    n = len(df)
    train_end = int(n * train_frac)
    val_end = int(n * (train_frac + val_frac))
    return df.iloc[:train_end], df.iloc[train_end:val_end], df.iloc[val_end:]
