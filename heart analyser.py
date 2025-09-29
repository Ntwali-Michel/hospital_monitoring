#!/usr/bin/env python3
import argparse, time, csv, os
from statistics import mean

MIN_HR = 60
MAX_HR = 100

def read_last_n(path, n=60):
    if not os.path.exists(path): return []
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[-n:]

def classify(hr):
    hr = int(hr)
    if hr < MIN_HR: return "LOW"
    if hr > MAX_HR: return "HIGH"
    return "NORMAL"

def main():
    ap = argparse.ArgumentParser(description="Analyse latest heart rate readings.")
    ap.add_argument("--log", default="heart_rate_log.csv")
    ap.add_argument("--window", type=int, default=60, help="number of recent rows to analyse")
    ap.add_argument("--watch", action="store_true", help="stream updates")
    args = ap.parse_args()

    def once():
        rows = read_last_n(args.log, args.window)
        if not rows:
            print("No data yet.")
            return
        vals = [int(r["heart_rate"]) for r in rows if r.get("heart_rate")]
        if not vals:
            print("No numeric values found.")
            return
        avg, lo, hi = mean(vals), min(vals), max(vals)
        state = classify(vals[-1])
        print(f"Readings: {len(vals)}  avg={avg:.1f}  min={lo}  max={hi}  latest={vals[-1]}({state})")

    if args.watch:
        try:
            while True:
                once()
                time.sleep(2.0)
        except KeyboardInterrupt:
            print("\nstopped.")
    else:
        once()

if __name__ == "__main__":
    main()
    main()
