"""Prepare the original House Prices features for model training and prediction."""

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
OUTPUT_DIR = DATA_DIR / "processed"
ID = "Id"
TARGET = "SalePrice"


def extract_features(frame):
    """Remove identifiers and targets and set feature types without fitting."""
    features = frame.drop(columns=[ID, TARGET], errors="ignore")
    # MSSubClass is a category code, not a numerical measurement.
    features["MSSubClass"] = features["MSSubClass"].astype("object")
    return features


def make_preprocessor(features):
    """Build an unfitted transformer that can be fit inside each CV fold."""
    numeric = features.select_dtypes(include="number").columns.tolist()
    categorical = features.columns.difference(numeric, sort=False).tolist()
    return ColumnTransformer(
        [
            (
                "num",
                make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
                numeric,
            ),
            (
                "cat",
                make_pipeline(
                    SimpleImputer(strategy="constant", fill_value="Missing"),
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                ),
                categorical,
            ),
        ],
        verbose_feature_names_out=False,
    ).set_output(transform="pandas")


def main():
    train = pd.read_csv(DATA_DIR / "raw" / "train.csv")
    test = pd.read_csv(DATA_DIR / "raw" / "test.csv")

    for name, frame in (("train", train), ("test", test)):
        if frame[ID].isna().any() or not frame[ID].is_unique:
            raise ValueError(f"{name}: Id must be present and unique.")

    target = train[TARGET]
    if not np.isfinite(target).all() or not target.gt(0).all():
        raise ValueError("SalePrice must be finite and positive.")

    train_features = extract_features(train)
    test_features = extract_features(test)
    if set(train_features) != set(test_features):
        raise ValueError("Train and test must have the same input features.")

    # Fit on train only, then reuse its statistics and categories for test.
    preprocessor = make_preprocessor(train_features)
    train_ready = preprocessor.fit_transform(train_features)
    test_ready = preprocessor.transform(test_features)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, source, prepared in (
        ("train", train, train_ready),
        ("test", test, test_ready),
    ):
        prepared.insert(0, ID, source[ID])
        if name == "train":
            prepared[TARGET] = target
        output = OUTPUT_DIR / f"{name}_processed.csv"
        prepared.to_csv(output, index=False)
        print(f"{output.relative_to(DATA_DIR.parent)}: {len(prepared)} rows, "
              f"{len(prepared.columns)} columns")


if __name__ == "__main__":
    main()
