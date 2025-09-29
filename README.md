# Hospital Monitoring + ML (Python)

## What changed
- Replaced shell scripts with Python equivalents.
- Logs now use **CSV** (`heart_rate_log.csv`: `timestamp,device,heart_rate`) for clean ML.
- Added ML pipeline:
  - `ml_prep_train.py` cleans (IQR), engineers features (lags/rolling/time), trains **Linear Regression**, saves model.
  - `ml_predict_realtime.py` tails the log and predicts the **next** heart rate for early warnings.

## Quick start

```bash
# 1) start monitoring (writes CSV)
python3 heart_rate_monitor.py --device Monitor_A --interval 1.0

# 2) (optional) rotate/backup logs
python3 archive_log.py
python3 backup_archives.py --group 1 --remote username@host:/home/youruser/backups

# 3) train model (reads CSV or legacy TXT if CSV not found)
python3 ml_prep_train.py
# -> saves ./models/linear_regression_hr.joblib, ./models/scaler.joblib, ./models/metrics.json

# 4) realtime prediction/early warning
python3 ml_predict_realtime.py --low 60 --high 100
