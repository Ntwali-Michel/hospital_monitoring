#!/usr/bin/env python3
"""
Pipeline:
1) Load logs (CSV preferred). If a legacy TXT format sneaks in, we try to parse it too.
2) Clean (drop missing, IQR outlier filter per device).
3) Feature engineering for time series: hour/minute, lag-1..lag-5, rolling mean/std.
4) Scale numeric features, train/test split by time, train LinearRegression to predict next heart_rate.
5) Save model + scaler + feature metadata to ./models/.
"""
import os, re, joblib, argparse
import numpy as np, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from pathlib import Path

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

def try_load_any(path_csv="heart_rate_log.csv", path_txt="heart_rate_log.txt"):
    if os.path.exists(path_csv):
        df = pd.read_csv(path_csv, parse_dates=["timestamp"])
        return df
    if os.path.exists(path_txt):
        # attempt to parse legacy: "YYYY-mm-dd HH:MM:SS DEVICE? NUMBER"
        ts_re = r"^\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})"
        num_re = r"(\d+)\s*$"
        rows = []
        with open(path_txt, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                mts = re.search(ts_re, line)
                mhr = re.search(num_re, line)
                if not (mts and mhr): 
                    continue
                ts = pd.to_datetime(mts.group(1), errors="coerce")
                hr = int(mhr.group(1))
                # try to grab a device token between ts and hr if present
                middle = line[mts.end():mhr.start()].strip()
                device = middle.split()[:1][0] if middle else "Unknown"
                rows.append((ts, device, hr))
        if rows:
            return pd.DataFrame(rows, columns=["timestamp","device","heart_rate"])
    raise FileNotFoundError("No log file found. Expected heart_rate_log.csv or heart_rate_log.txt")

def iqr_filter(group: pd.DataFrame, col="heart_rate"):
    q1 = group[col].quantile(0.25)
    q3 = group[col].quantile(0.75)
    iqr = q3 - q1
    lo = q1 - 1.5*iqr
    hi = q3 + 1.5*iqr
    return group[(group[col] >= lo) & (group[col] <= hi)]

def add_time_features(df: pd.DataFrame):
    df = df.sort_values("timestamp").copy()
    df["hour"] = df["timestamp"].dt.hour
    df["minute"] = df["timestamp"].dt.minute
    df["second"] = df["timestamp"].dt.second
    return df

def add_lags_rolls(df: pd.DataFrame, max_lag=5, roll_window=10):
    df = df.sort_values("timestamp").copy()
    for k in range(1, max_lag+1):
        df[f"hr_lag_{k}"] = df.groupby("device")["heart_rate"].shift(k)
    df["hr_roll_mean"] = df.groupby("device")["heart_rate"].rolling(roll_window, min_periods=3).mean().reset_index(level=0, drop=True)
    df["hr_roll_std"]  = df.groupby("device")["heart_rate"].rolling(roll_window, min_periods=3).std().reset_index(level=0, drop=True)
    # target: next step heart rate
    df["hr_next"] = df.groupby("device")["heart_rate"].shift(-1)
    return df

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test_size", type=float, default=0.2)
    ap.add_argument("--random_state", type=int, default=42)
    ap.add_argument("--max_lag", type=int, default=5)
    ap.add_argument("--roll_window", type=int, default=10)
    args = ap.parse_args()

    df = try_load_any()
    # basic cleanup
    df = df.dropna(subset=["timestamp", "heart_rate"])
    df["heart_rate"] = pd.to_numeric(df["heart_rate"], errors="coerce")
    df = df.dropna(subset=["heart_rate"])
    df["device"] = df.get("device", pd.Series(["Unknown"]*len(df)))

    # IQR outlier removal per device
    df = df.groupby("device", group_keys=False).apply(iqr_filter)

    # features
    df = add_time_features(df)
    df = add_lags_rolls(df, max_lag=args.max_lag, roll_window=args.roll_window)

    # drop rows with NaN from lags/rolls/target
    df = df.dropna(subset=[f"hr_lag_{k}" for k in range(1, args.max_lag+1)] + ["hr_roll_mean","hr_roll_std","hr_next"])

    feature_cols = ["hour","minute","second"] + [f"hr_lag_{k}" for k in range(1, args.max_lag+1)] + ["hr_roll_mean","hr_roll_std"]
    X = df[feature_cols].values
    y = df["hr_next"].values

    # time-aware split: keep chronological order
    split_idx = int(len(df)*(1-args.test_size))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    model = LinearRegression()
    model.fit(X_train_s, y_train)
    r2 = model.score(X_test_s, y_test)
    mae = np.mean(np.abs(model.predict(X_test_s) - y_test))

    meta = {
        "feature_cols": feature_cols,
        "max_lag": args.max_lag,
        "roll_window": args.roll_window,
        "r2": float(r2),
        "mae": float(mae),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }
    print("Model evaluation:", meta)

    joblib.dump(model, MODEL_DIR / "linear_regression_hr.joblib")
    joblib.dump(scaler, MODEL_DIR / "scaler.joblib")
    pd.Series(meta).to_json(MODEL_DIR / "metrics.json", indent=2)
    print("Saved model + scaler + metrics to ./models/")

if __name__ == "__main__":
    main()
