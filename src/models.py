"""Definición de los 4 modelos candidatos (checkpoint 1, sección 6)."""
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMClassifier
from xgboost import XGBClassifier


def get_models(random_state: int = 42) -> dict:
    """2 modelos clásicos (línea base) + 2 modelos avanzados."""
    return {
        "logistic_regression": LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=random_state
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=12, class_weight="balanced",
            n_jobs=-1, random_state=random_state,
        ),
        "lightgbm": LGBMClassifier(
            n_estimators=500, learning_rate=0.05, class_weight="balanced",
            random_state=random_state,
        ),
        "xgboost": XGBClassifier(
            n_estimators=500, learning_rate=0.05, eval_metric="aucpr",
            random_state=random_state,
        ),
    }
