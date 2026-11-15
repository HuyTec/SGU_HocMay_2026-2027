"""Train and use the selected House Prices ensemble."""

import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline

FOLDER = Path(__file__).resolve().parent
sys.path.insert(0, str(FOLDER.parent))

from src.model import make_lasso, make_xgboost
from src.prepare_data import DATA_DIR, ID, TARGET, extract_features, make_preprocessor


def feature_sets(frame, config):
    original = extract_features(frame)
    expanded = original.assign(
        TotalSF=original["TotalBsmtSF"] + original["1stFlrSF"] + original["2ndFlrSF"],
        TotalBath=original["FullBath"] + original["BsmtFullBath"]
        + 0.5 * (original["HalfBath"] + original["BsmtHalfBath"]),
        AgeAtSale=original["YrSold"] - original["YearBuilt"],
    )
    features_by_model = {}
    for name in config["weights"]:
        settings = config[name]
        columns = [*original.columns, *settings["extra_features"]]
        features = expanded[columns].copy()
        log_columns = settings.get("log1p_features", [])
        if log_columns:
            features[log_columns] = np.log1p(features[log_columns])
        features_by_model[name] = features
    return features_by_model


def train(config):
    try:
        import xgboost
    except ModuleNotFoundError as error:
        if error.name != "xgboost":
            raise
        raise SystemExit("Install dependencies: python -m pip install -r final_model/requirements.txt") from error

    raw = pd.read_csv(DATA_DIR / "raw" / "train.csv")
    prices = raw[TARGET]
    if not np.isfinite(prices).all() or not prices.gt(0).all():
        raise ValueError("SalePrice must be finite and positive.")
    rule = config["outlier_rule"]
    removed = raw["GrLivArea"].gt(rule["GrLivArea_gt"]) & prices.lt(rule["SalePrice_lt"])
    clean = raw.loc[~removed].copy()
    target = np.log(clean[TARGET])
    clean.to_csv(FOLDER / "train_filtered.csv", index=False)
    pipelines = {}
    for name, features in feature_sets(clean, config).items():
        factory = {"xgboost": make_xgboost, "lasso": make_lasso}[name]
        pipeline = make_pipeline(make_preprocessor(features), factory(**config[name]["params"]))
        pipeline.fit(features, target)
        processed = pipeline.steps[0][1].transform(features)
        processed.insert(0, ID, clean[ID])
        processed["ln_SalePrice"] = target
        processed.to_csv(FOLDER / f"train_{name}_processed.csv", index=False)
        pipelines[name] = pipeline

    joblib.dump({"config": config, "pipelines": pipelines}, FOLDER / "ensemble.joblib", compress=3)
    packages = ["numpy", "pandas", "scipy", "scikit-learn", "joblib"]
    requirements = [f"{package}=={version(package)}" for package in packages]
    try:
        cpu_version = version("xgboost-cpu")
    except PackageNotFoundError:
        requirements.append(f"xgboost=={xgboost.__version__}")
    else:
        requirements.append(f"xgboost-cpu=={cpu_version}")
    (FOLDER / "requirements.txt").write_text("\n".join(requirements) + "\n", encoding="utf-8")
    print(f"Training rows: {len(clean)}. Removed IDs: {raw.loc[removed, ID].tolist()}")


def predict(frame, bundle):
    config = bundle["config"]
    features = feature_sets(frame, config)
    log_prices = sum(
        weight * bundle["pipelines"][name].predict(features[name]).astype(float)
        for name, weight in config["weights"].items()
    )
    return pd.DataFrame({ID: frame[ID], TARGET: np.exp(log_prices)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["train", "predict"])
    parser.add_argument("--input", type=Path, default=DATA_DIR / "raw" / "test.csv")
    parser.add_argument("--output", type=Path, default=FOLDER / "submission.csv")
    args = parser.parse_args()
    if args.action == "train":
        train(json.loads((FOLDER / "config.json").read_text(encoding="utf-8")))
    else:
        bundle = joblib.load(FOLDER / "ensemble.joblib")
        predict(pd.read_csv(args.input), bundle).to_csv(args.output, index=False)
        print(args.output)


if __name__ == "__main__":
    main()
