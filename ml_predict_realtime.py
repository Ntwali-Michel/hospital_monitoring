#!/usr/bin/env python3
import time, os, csv, joblib, argparse, pandas as pd
from collections import deque
from datetime import datetime

MODEL_PATH = "models/linear_regression_hr.joblib"
SCALER_PATH = "models/scaler.joblib"

def build_features(history_rows, max_lag=5, roll_window=10):
    # history_rows: list of dicts with keys timestamp, device, heart_rate
    df = pd.DataFrame(history_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    # time features from the latest row
    last = df.iloc[-1]
    hour, minute, second = last["timestamp"].hour, last["timestamp"].minute, last["timestamp"].second
    # lags from last k values
    hr_series = df["heart_rate"].astype(int).values
    feats = [hour, minute, second]
    for k in range(1, max_lag+1):
        feats.append(hr_series[-k] if len(hr_series) >= k else hr_series[0])
    # rolling window
    roll_vals = hr_series[-roll_window:] if len(hr_series) >= roll_window else hr_series
    feats.append(roll_vals.mean())
    feats.append(roll_vals.std() if len(roll_vals) > 1 else 0.0)
    return feats

def stream_csv(path):
    # naive tail: re-open each cycle; robust and simple
    last_size = 0
    while True:
        try:
            size = os.path.getsize(path)
            if size < last_size:  # rotated
                last_size = 0
            if size > last_size:
                with open(path, newline="", encoding="utf-8") as f:
                    f.seek(last_size)
                    # read remainder
                    chunk = f.read()
                    last_size = size
                # parse rows
                lines = chunk.strip().splitlines()
                for line in lines:
                    yield line
        except FileNotFoundError:
            pass
        time.sleep(1.0)

def main():
    ap = argparse.ArgumentParser(description="Realtime HR predictor")
    ap.add_argument("--log", default="heart_rate_log.csv")
    ap.add_argument("--max_lag", type=int, default=5)
    ap.add_argument("--roll_window", type=int, default=10)
    ap.add_argument("--min_history", type=int, default=20)
    ap.add_argument("--low", type=int, default=60)
    ap.add_argument("--high", type=int, default=100)
    args = ap.parse_args()

    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)

    # buffer of last ~few dozen rows
    buf = deque(maxlen=max(200, args.min_history + args.roll_window + args.max_lag + 5))

    # prime existing file
    if os.path.exists(args.log):
        with open(args.log, newline="", encoding="utf-8") as f:
            rdr = csv.DictReader(f)
            for row in rdr:
                buf.append({"timestamp": row["timestamp"], "device": row.get("device","Unknown"), "heart_rate": int(row["heart_rate"])})

    # header detection for new lines
    header_seen = False

    print("🔮 realtime prediction running (Ctrl+C to stop)")
    try:
        for raw in stream_csv(args.log):
            parts = [p.strip() for p in raw.split(",")]
            if not parts or len(parts) < 3:
                # maybe header line
                if "timestamp" in raw and "heart_rate" in raw:
                    header_seen = True
                continue
            if not header_seen and "timestamp" in raw:
                header_seen = True
                continue
            ts, dev, hr = parts[0], parts[1], parts[2]
            try:
                hr_i = int(hr)
            except:
                continue
            buf.append({"timestamp": ts, "device": dev, "heart_rate": hr_i})

            if len(buf) >= args.min_history:
                feats = build_features(list(buf), args.max_lag, args.roll_window)
                X = scaler.transform([feats])
                pred = float(model.predict(X)[0])
                label = "ok"
                if pred < args.low: label = "⚠️ predicted LOW"
                elif pred > args.high: label = "⚠️ predicted HIGH"
                print(f"{ts} dev={dev} current={hr_i} → next≈{pred:.1f} bpm  [{label}]")
    except KeyboardInterrupt:
        print("\nstopped.")

if __name__ == "__main__":
    main()
