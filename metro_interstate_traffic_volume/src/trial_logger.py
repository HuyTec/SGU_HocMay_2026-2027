import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


class TrialProgressLogger:
    FIELDS = [
        "timestamp_utc7",
        "run_id",
        "config",
        "model",
        "candidate",
        "candidate_count",
        "fold",
        "status",
        "params_json",
        "fold_mae",
        "mean_cv_mae",
        "validation_mae",
        "validation_rmse",
        "validation_r2",
        "fit_start",
        "fit_end",
        "score_start",
        "score_end",
        "error",
    ]

    def __init__(self, path, run_id):
        self.path = Path(path)
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)

        needs_header = not self.path.exists() or self.path.stat().st_size == 0
        self.file = self.path.open(
            "a",
            newline="",
            encoding="utf-8-sig",
        )
        self.writer = csv.DictWriter(
            self.file,
            fieldnames=self.FIELDS,
            extrasaction="ignore",
        )

        if needs_header:
            self.writer.writeheader()
            self.file.flush()

    def __call__(self, event):
        row = {field: "" for field in self.FIELDS}
        row.update(event)
        row["run_id"] = self.run_id
        row["timestamp_utc7"] = datetime.now(
            timezone(timedelta(hours=7))
        ).isoformat()

        params = row.get("params_json")
        if isinstance(params, dict):
            row["params_json"] = json.dumps(
                params,
                ensure_ascii=False,
                sort_keys=True,
                default=str,
            )

        self.writer.writerow(row)
        self.file.flush()

    def close(self):
        self.file.close()
