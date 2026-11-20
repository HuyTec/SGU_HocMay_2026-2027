"""API tuning báo cáo. Toàn bộ vòng CV dùng chung nằm trong tuning_cv.py.

Thí nghiệm lịch sử dùng tuning_exp.py; notebook báo cáo dùng cohort/fold FE.
"""
from src.tuning_cv import (
    CONFIGS, MODEL_NAMES, N_CANDIDATES, N_SPLITS, SEED, BASELINES,
    load_context, describe_folds, budget_table, candidate_bank, run_configuration,
    results_table, load_comparison, validate_records, paired_fold_deltas,
    block_bootstrap_deltas, plot_comparison, conclusion,
)
