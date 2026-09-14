"""Políticas de olvido / ventanas deslizantes (checkpoint 1, sección 7:
Escenario A = ventana fija deslizante, Escenario B = time-decay ponderado)."""
import numpy as np
import pandas as pd


def sliding_window_split(df: pd.DataFrame, dt_col: str, window_size: int, step_size: int):
    """Genera pares sucesivos (ventana_train, ventana_eval) de tamaño fijo,
    avanzando en el tiempo — Escenario A (olvido abrupto)."""
    df = df.sort_values(dt_col).reset_index(drop=True)
    n = len(df)
    start = 0
    while start + window_size + step_size <= n:
        train_window = df.iloc[start: start + window_size]
        eval_window = df.iloc[start + window_size: start + window_size + step_size]
        yield train_window, eval_window
        start += step_size


def time_decay_weights(dt_values: pd.Series, half_life: float) -> np.ndarray:
    """Pesos de muestra con decaimiento exponencial según antigüedad, para
    reentrenamiento ponderado — Escenario B (olvido ponderado)."""
    t_max = dt_values.max()
    age = t_max - dt_values.to_numpy()
    return 0.5 ** (age / half_life)
