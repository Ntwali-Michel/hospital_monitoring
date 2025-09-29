#!/usr/bin/env python3
import argparse, csv, os, random, signal, sys, time
from datetime import datetime

LOG_PATH = "heart_rate_log.csv"  # new CSV format: timestamp,device,heart_rate

def open_writer(path):
    file_exists = os.path.exists(path)
    f = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(f)
    if not file_exists:
        w.writerow(["timestamp", "device", "heart_rate"])
    return f, w

def read_heart_rate(fake_min=40, fake_max=120):
    # TODO: replace with real sensor read when available
    return random.randint(fake_min, fake_max)

def main():
    ap = argparse.ArgumentParser(description="Heart rate monitor -> CSV")
    ap.add_argument("--device", required=True, help="Device name (e.g. Monitor_A)")
    ap.add_argument("--interval", type=float, default=1.0, help="Seconds between readings")
    args = ap.parse_args()

    f, writer = open_writer(LOG_PATH)
    running = True

    def handle_sigint(signum, frame):
        nonlocal running
        running = False
        print("\nStopping monitor...")

    signal.signal(signal.SIGINT, handle_sigint)

    print(f"🫀 monitoring started for '{args.device}' -> {LOG_PATH} (Ctrl+C to stop)")
    try:
        while running:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hr = read_heart_rate()
            writer.writerow([ts, args.device, hr])
            f.flush()
            print(f"{ts} {args.device} {hr} bpm")
            time.sleep(args.interval)
    finally:
        f.close()
        print("monitor closed.")

if __name__ == "__main__":
    main()

