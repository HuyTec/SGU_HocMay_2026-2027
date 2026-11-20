"""Tuning A12/B27/C30 trên cùng cohort/fold và ma trận của FE, không chấm holdout."""
import hashlib
import json
import platform
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
import xgboost
from sklearn.model_selection import ParameterSampler
from threadpoolctl import threadpool_limits

from src import feature_experiments as fe
from src.evaluation import clip_prediction, regression_metrics
from src.features import CONFIG_A, CONFIG_B, CONFIG_C
from src.model import MODEL_NAMES, SEARCH_SPACE, make_cv_model

CONFIGS = {"A12": list(CONFIG_A), "B27": list(CONFIG_B), "C30": list(CONFIG_C)}
SEED, N_CANDIDATES, N_SPLITS = 42, 6, 3
BASELINES = ("Mean weekday-hour", "Seasonal naive 168h")


def _digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()


def _write(path, value):
    """Ghi JSON bằng thay thế file tạm, tránh đọc kết quả đang ghi dở."""
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False,default=str),encoding="utf-8")
    # Windows readers/antivirus can briefly deny replacing an open file.
    for attempt in range(30):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt==29:
                raise
            time.sleep(.1)


def candidate_bank():
    """Đúng sáu ứng viên mỗi mô hình, cùng danh sách giữa các cấu hình.

    Lấy trực tiếp đúng ngân sách bằng ParameterSampler, không lấy toàn grid
    rồi cắt phần đầu. Không chèn bộ FE thay cho một lượt tìm kiếm. RF cố
    định ở FE chỉ là tham chiếu ngoài vòng chọn sáu ứng viên này.
    """
    bank = {}
    for name in MODEL_NAMES:
        bank[name] = list(ParameterSampler(SEARCH_SPACE[name],n_iter=N_CANDIDATES,random_state=SEED))
        if len(bank[name])!=N_CANDIDATES or len({_digest(p) for p in bank[name]})!=N_CANDIDATES:
            raise ValueError(f"Ngân sách hoặc ứng viên trùng: {name}")
    return bank


def load_context(root=None):
    """Dùng nguyên load_protocol/prepare_fold của FE; chỉ lấy train cho tuning."""
    root = Path(root) if root else Path(__file__).resolve().parents[1]
    context = fe.load_protocol(root)
    prepared = []
    for number,(fit_idx,score_idx) in enumerate(context["folds"],1):
        fit,score = context["cohort"].iloc[fit_idx],context["cohort"].iloc[score_idx]
        x_fit,x_score,stats = fe.prepare_fold(context["train"],context["featured"],fit.date_time,score.date_time)
        for matrix in (x_fit,x_score):
            matrix["weekday_hour"] = (matrix.day_of_week*24+matrix.hour).astype("int16")
        prepared.append(dict(fold=number,fit=fit,score=score,x_fit=x_fit,x_score=x_score,stats=stats))
    if len(prepared)!=N_SPLITS:
        raise ValueError("Phải dùng đúng ba fold của FE.")
    source_files = [Path(__file__), *(root/"src"/name for name in
                    ["model.py","feature_experiments.py","features.py","preprocessing.py","evaluation.py"])]
    protocol = dict(version=1,fe_protocol_id=context["protocol_id"],data_sha256=context["metadata"]["data_sha256"],
        cohort_hash=context["metadata"]["cohort_hash"],n_train=len(context["train"]),n_cohort=len(context["cohort"]),
        n_oof=int(context["manifest"].n.sum()),folds=context["manifest"].to_dict("records"),
        prepared=[dict(fold=p["fold"],**p["stats"]) for p in prepared],
        configs=CONFIGS,model_names=list(MODEL_NAMES),search_space=SEARCH_SPACE,candidates=candidate_bank(),
        n_candidates=N_CANDIDATES,n_splits=N_SPLITS,seed=SEED,
        selection="mean fold MAE; then mean fold RMSE; then candidate index",clip_min=0,
        ridge="one-hot weekday_hour/month and scaled noncalendar numeric columns; fit only fold-train",
        missing="FE prepare_fold only; no median imputation for lag or second imputer",
        baselines=list(BASELINES),scope="train CV only; no validation/test scoring",
        prediction="sequential hourly; past observed traffic may be used within score fold",
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files},
        versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,
                      sklearn=sklearn.__version__,xgboost=xgboost.__version__))
    protocol = json.loads(json.dumps(protocol,default=str))
    return dict(**context,prepared=prepared,tuning_protocol=protocol,protocol_hash=_digest(protocol),
                tuning_output=root/"notebooks/tuning/outputs")


def describe_folds(context):
    return context["manifest"].copy()


def budget_table(context):
    return pd.DataFrame([dict(model=name,candidates=N_CANDIDATES,folds=N_SPLITS,
        fits_per_config=N_CANDIDATES*N_SPLITS,n=len(context["cohort"])) for name in MODEL_NAMES])


def _fold_metrics(context, number, target, predicted, **extra):
    return dict(**context["manifest"].iloc[number-1].to_dict(),**regression_metrics(target,predicted),**extra)


def _observations(context):
    rows=[]
    for p in context["prepared"]:
        rows.extend(dict(fold=p["fold"],date_time=str(r.date_time),y_true=float(r.traffic_volume))
                    for r in p["score"].itertuples())
    return rows


def baseline_results(context):
    """Hai baseline học/chấm trên cùng các timestamp như mô hình tuning."""
    records=[]
    for name in BASELINES:
        metrics,predictions=[],[]
        for p in context["prepared"]:
            if name==BASELINES[0]:
                means=p["fit"].assign(weekday_hour=p["x_fit"].weekday_hour.to_numpy()).groupby("weekday_hour").traffic_volume.mean()
                pred=p["x_score"].weekday_hour.map(means).fillna(p["fit"].traffic_volume.mean()).to_numpy()
            else:
                pred=p["score"].lag_168h.to_numpy()
            pred=clip_prediction(pred)
            metrics.append(_fold_metrics(context,p["fold"],p["score"].traffic_volume,pred))
            predictions.extend(pred.tolist())
        records.append(dict(model=name,folds=metrics,oof_prediction=predictions))
    return records


def run_configuration(context, config):
    """Chạy một cấu hình. Điểm từng ứng viên và OOF tốt nhất ghi một JSON.

    Mỗi lần gọi huấn luyện lại, không âm thầm đọc cache. protocol.json của
    A/B/C giống nhau. results.json chỉ complete khi đủ mọi mô hình/ngân sách.
    """
    if config not in CONFIGS:
        raise ValueError(f"Cấu hình không hỗ trợ: {config}")
    folder=context["tuning_output"]/config
    folder.mkdir(parents=True,exist_ok=True)
    _write(folder/"protocol.json",context["tuning_protocol"])
    record=dict(config=config,features=CONFIGS[config],protocol_hash=context["protocol_hash"],complete=False,
                oof_observations=_observations(context),baselines=baseline_results(context),results=[])
    for name in MODEL_NAMES:
        trials,best_predictions,best_key=[],None,None
        for candidate,params in enumerate(context["tuning_protocol"]["candidates"][name],1):
            metrics,predictions=[],[]
            for p in context["prepared"]:
                start=time.monotonic()
                pipeline=make_cv_model(name,CONFIGS[config]).set_params(**params)
                with warnings.catch_warnings(record=True) as caught, threadpool_limits(limits=1):
                    warnings.simplefilter("always")
                    pipeline.fit(p["x_fit"],p["fit"].traffic_volume.to_numpy())
                    predicted=clip_prediction(pipeline.predict(p["x_score"]))
                row=_fold_metrics(context,p["fold"],p["score"].traffic_volume,predicted,
                                  seconds=time.monotonic()-start,warnings=sorted({str(w.message) for w in caught}))
                metrics.append(row)
                predictions.extend(predicted.tolist())
                progress=dict(config=config,model=name,candidate=candidate,fold=p["fold"],MAE=row["MAE"],seconds=row["seconds"])
                _write(folder/"progress.json",progress)
                print(f"{config} | {name} | candidate {candidate}/{N_CANDIDATES} | fold {p['fold']}: MAE={row['MAE']:.3f}",flush=True)
            trial=dict(candidate=candidate,parameters=params,folds=metrics,
                       MAE_mean=float(np.mean([r["MAE"] for r in metrics])),
                       RMSE_mean=float(np.mean([r["RMSE"] for r in metrics])))
            trials.append(trial)
            key=(trial["MAE_mean"],trial["RMSE_mean"],candidate)
            if best_key is None or key<best_key:
                best_key,best_predictions=key,predictions
        best=min(trials,key=lambda t:(t["MAE_mean"],t["RMSE_mean"],t["candidate"]))
        record["results"].append(dict(model=name,best_params=best["parameters"],best_candidate=best["candidate"],
                                      folds=best["folds"],candidates=trials,oof_prediction=best_predictions))
        _write(folder/"results.json",record)
    record["complete"]=True
    _write(folder/"results.json",record)
    (folder/"progress.json").unlink(missing_ok=True)
    return record


def _summary_row(config, model, folds):
    row=dict(config=config,model=model,n=int(sum(r["n"] for r in folds)))
    for metric in ["MAE","RMSE","R2"]:
        values=[r[metric] for r in folds]
        row[metric+"_mean"]=float(np.mean(values))
        row[metric+"_std"]=float(np.std(values,ddof=1))
    return row


def results_table(record):
    return pd.DataFrame([_summary_row(record["config"],r["model"],r["folds"])
                         for r in [*record["baselines"],*record["results"]]])


def validate_records(protocols, records):
    """Dừng nếu protocol/ứng viên/fold/OOF lệch; không chỉ so số dòng."""
    if set(records)!=set(CONFIGS) or set(protocols)!=set(CONFIGS):
        raise ValueError("Cần đủ A12, B27, C30.")
    signatures={_digest(p) for p in protocols.values()}
    if len(signatures)!=1:
        raise ValueError("Protocol hash khác nhau giữa A/B/C.")
    signature=next(iter(signatures))
    reference=None
    for config,record in records.items():
        protocol=protocols[config]
        if record["protocol_hash"]!=signature or not record["complete"] or record["config"]!=config:
            raise ValueError("Kết quả chưa hoàn tất hoặc sai protocol.")
        if record["features"]!=protocol["configs"][config]:
            raise ValueError("Sai danh sách feature.")
        observations=record["oof_observations"]
        if reference is None:reference=observations
        if observations!=reference or len(observations)!=protocol["n_oof"]:
            raise ValueError("OOF khác timestamp/target/fold.")
        if len({r['date_time'] for r in observations})!=len(observations):
            raise ValueError("OOF trùng timestamp.")
        if [r["model"] for r in record["results"]]!=protocol["model_names"]:
            raise ValueError("Khác danh sách mô hình.")
        if [r["model"] for r in record["baselines"]]!=protocol["baselines"]:
            raise ValueError("Thiếu baseline.")
        for model in [*record["results"],*record["baselines"]]:
            pred=np.asarray(model["oof_prediction"])
            if len(pred)!=len(observations) or not np.isfinite(pred).all():
                raise ValueError("OOF dự đoán thiếu/không hữu hạn.")
            if "candidates" in model:
                if [r["parameters"] for r in model["candidates"]]!=protocol["candidates"][model["model"]]:
                    raise ValueError("Khác danh sách ứng viên/ngân sách.")
                expected=min(model["candidates"],key=lambda t:(t["MAE_mean"],t["RMSE_mean"],t["candidate"]))
                if model["best_params"]!=expected["parameters"] or model["folds"]!=expected["folds"]:
                    raise ValueError("Tham số được chọn không khớp tiêu chí.")
            for row in model["folds"]:
                manifest=protocol["folds"][row["fold"]-1]
                if any(row[k]!=v for k,v in manifest.items()):
                    raise ValueError("Fold lệch mốc thời gian/hash/số mẫu.")
                take=np.array([r["fold"]==row["fold"] for r in observations])
                actual=np.array([r["y_true"] for r in observations])[take]
                recalculated=regression_metrics(actual,pred[take])
                if any(not np.isclose(row[k],v,rtol=0,atol=1e-8) for k,v in recalculated.items()):
                    raise ValueError("Điểm đã lưu không khớp OOF.")
    return signature


def load_comparison(root=None):
    """Chỉ đọc kết quả; không gọi load_protocol, fit hoặc prepare_fold."""
    root=Path(root) if root else Path(__file__).resolve().parents[1]
    output=root/"notebooks/tuning/outputs"
    protocols={c:json.loads((output/c/"protocol.json").read_text(encoding="utf-8")) for c in CONFIGS}
    records={c:json.loads((output/c/"results.json").read_text(encoding="utf-8")) for c in CONFIGS}
    signature=validate_records(protocols,records)
    frames=[results_table(r).loc[lambda t:~t.model.isin(BASELINES)] for r in records.values()]
    common=pd.DataFrame([_summary_row("common",r["model"],r["folds"]) for r in records["C30"]["baselines"]])
    return dict(root=root,protocol_hash=signature,protocol=protocols["C30"],records=records,
                summary=pd.concat([*frames,common],ignore_index=True))


def paired_fold_deltas(comparison):
    rows=[]
    for before,after in [("A12","B27"),("B27","C30")]:
        left={r["model"]:r for r in comparison["records"][before]["results"]}
        for right in comparison["records"][after]["results"]:
            for a,b in zip(left[right["model"]]["folds"],right["folds"]):
                rows.append(dict(model=right["model"],comparison=f"{after} - {before}",fold=a["fold"],n=a["n"],
                                 **{f"delta_{m}":b[m]-a[m] for m in ["MAE","RMSE","R2"]}))
    return pd.DataFrame(rows)


def block_bootstrap_deltas(comparison, reps=2000, block_days=7):
    """Bootstrap khối ngày lịch trong từng fold; không nối qua biên fold.

    Gain=MAE(before)-MAE(after), dương là cấu hình sau tốt hơn. Giữ ngày không
    có mẫu bằng tổng/n=0 để không nối giả các giờ qua gaps. CI có điều kiện
    theo tham số được chọn bằng chính CV, chưa hiệu chỉnh selection bias.
    """
    rows=[]
    for before,after in [("A12","B27"),("B27","C30")]:
        a=comparison["records"][before];b=comparison["records"][after]
        observations=pd.DataFrame(a["oof_observations"])
        observations["day"]=pd.to_datetime(observations.date_time).dt.normalize()
        y=observations.y_true.to_numpy()
        for left,right in zip(a["results"],b["results"]):
            gain=np.abs(y-np.asarray(left["oof_prediction"]))-np.abs(y-np.asarray(right["oof_prediction"]))
            rng=np.random.default_rng(SEED)
            samples=np.zeros(reps);valid=np.ones(reps,dtype=bool)
            for fold,part in observations.assign(gain=gain).groupby("fold"):
                daily=part.groupby("day").gain.agg(total="sum",n="size")
                daily=daily.reindex(pd.date_range(daily.index.min(),daily.index.max(),freq="D"),fill_value=0)
                width=min(block_days,len(daily));blocks=int(np.ceil(len(daily)/width))
                starts=rng.integers(0,len(daily)-width+1,size=(reps,blocks))
                indices=(starts[:,:,None]+np.arange(width)).reshape(reps,-1)[:,:len(daily)]
                totals=daily.total.to_numpy()[indices].sum(axis=1)
                counts=daily.n.to_numpy()[indices].sum(axis=1)
                valid &= counts>0
                samples+=np.divide(totals,counts,out=np.zeros(reps),where=counts>0)*len(part)/len(observations)
            if valid.sum()<reps*.9:
                raise ValueError("Quá ít mẫu bootstrap hợp lệ.")
            low,high=np.quantile(samples[valid],[.025,.975])
            rows.append(dict(model=left["model"],comparison=f"{after} vs {before}",MAE_gain=float(gain.mean()),
                             CI95_low=float(low),CI95_high=float(high),block_days=block_days,
                             valid_replicates=int(valid.sum()),n=len(observations)))
    return pd.DataFrame(rows)


def plot_comparison(comparison):
    import matplotlib.pyplot as plt
    frame=comparison["summary"]
    fig,ax=plt.subplots(figsize=(12,5))
    x=np.arange(len(MODEL_NAMES));width=.25
    for i,config in enumerate(CONFIGS):
        data=frame.loc[frame.config.eq(config)].set_index("model").loc[list(MODEL_NAMES)]
        ax.bar(x+(i-1)*width,data.MAE_mean,width,yerr=data.MAE_std,capsize=3,label=config)
    ax.set(xticks=x,xticklabels=MODEL_NAMES,xlabel="Mô hình",ylabel="MAE CV (xe/giờ)",
           title="MAE sau tuning thay đổi theo mô hình và cấu hình")
    ax.legend();fig.tight_layout()
    folder=comparison["root"]/"figures";folder.mkdir(exist_ok=True)
    fig.savefig(folder/"tuning_01_mae_comparison.png",dpi=160,bbox_inches="tight")
    plt.show();plt.close(fig)


def conclusion(comparison):
    """Nhận xét từ bảng; không suy ra ý nghĩa thống kê từ SD giữa ba fold."""
    frame=comparison["summary"].loc[lambda t:~t.model.isin(BASELINES)]
    best=frame.sort_values(["MAE_mean","RMSE_mean"]).iloc[0]
    c30=frame.loc[frame.config.eq("C30")].sort_values(["MAE_mean","RMSE_mean"]).iloc[0]
    rf=frame.loc[frame.model.eq("Random Forest")].sort_values(["MAE_mean","RMSE_mean"]).iloc[0]
    text=(f"Thấp nhất toàn bảng: {best['model']} / {best['config']}, MAE {best.MAE_mean:.3f}, RMSE {best.RMSE_mean:.3f} xe/giờ. "
          f"Trong C30, chọn {c30['model']} theo MAE CV {c30.MAE_mean:.3f} xe/giờ để chuyển sang ensemble/validation; chưa phải mô hình cuối sau holdout. "
          f"C30 {'vẫn' if best['config']=='C30' else 'không còn'} là cấu hình của kết quả tốt nhất toàn bảng sau tuning. "
          f"Riêng RF sau tuning, cấu hình tốt nhất là {rf['config']}.")
    fe_path=comparison["root"]/"notebooks/features/feature_comparison.csv"
    if fe_path.exists():
        old=pd.read_csv(fe_path);fixed=float(old.loc[old.config.eq("V5_C30"),"MAE_mean"].iloc[0])
        tuned=float(frame.loc[frame.model.eq("Random Forest") & frame.config.eq("C30"),"MAE_mean"].iloc[0])
        text+=f" RF C30 cố định ở FE: {fixed:.3f}; RF C30 sau tuning: {tuned:.3f} xe/giờ."
    text+=(" Ba fold là ít và phủ khoảng lịch khác nhau; ngân sách sáu ứng viên/mô hình còn nhỏ. "
           "SD mô tả biến động theo giai đoạn, không phải kiểm định chênh lệch. Bootstrap OOF dùng lại CV đã chọn tham số, "
           "nên CI chỉ mô tả bất định có điều kiện và chưa phải bằng chứng kiểm định độc lập. Chưa chấm validation/test.")
    return text
