"""Build fresh regression models for House Prices experiments."""

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge


def make_dummy(*, strategy: str = "mean") -> DummyRegressor:
    """Create the baseline that predicts the training target mean by default."""
    return DummyRegressor(strategy=strategy)


def make_ridge(*, alpha: float = 1.0, solver: str = "lsqr") -> Ridge:
    """Create a Ridge model with the baseline notebook's defaults."""
    return Ridge(alpha=alpha, solver=solver)


def make_random_forest(
    *,
    n_estimators: int = 200,
    min_samples_leaf: int = 2,
    max_depth: int | None = None,
    random_state: int | None = 42,
    n_jobs: int | None = -1,
) -> RandomForestRegressor:
    """Create a Random Forest model with the baseline notebook's defaults."""
    return RandomForestRegressor(
        n_estimators=n_estimators,
        min_samples_leaf=min_samples_leaf,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=n_jobs,
    )
