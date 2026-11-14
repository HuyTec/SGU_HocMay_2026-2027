"""Build Lasso, XGBoost and SVR models for House Prices."""

from typing import TYPE_CHECKING

from sklearn.linear_model import Lasso
from sklearn.svm import SVR

if TYPE_CHECKING:
    from xgboost import XGBRegressor


def make_lasso(*, alpha: float = 0.001, max_iter: int = 10000) -> Lasso:
    """Create a Lasso model for the standardized features and log target."""
    return Lasso(alpha=alpha, max_iter=max_iter)


def make_xgboost(
    *,
    n_estimators: int = 200,
    max_depth: int = 4,
    learning_rate: float = 0.05,
    random_state: int = 42,
    n_jobs: int = 2,
) -> "XGBRegressor":
    """Create a CPU XGBoost regressor for squared-error regression."""
    from xgboost import XGBRegressor

    return XGBRegressor(
        objective="reg:squarederror",
        tree_method="hist",
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        random_state=random_state,
        n_jobs=n_jobs,
    )


def make_svr(
    *, C: float = 10.0, epsilon: float = 0.05, gamma: str | float = "scale"
) -> SVR:
    """Create an RBF SVR for the standardized features and log target."""
    return SVR(kernel="rbf", C=C, epsilon=epsilon, gamma=gamma)
