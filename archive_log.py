#!/usr/bin/env python3
import os, shutil
from datetime import datetime

SRC = "heart_rate_log.csv"

def main():
    if not os.path.exists(SRC):
        print("No current log to archive.")
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    dst = f"heart_rate_log_{ts}.csv"
    shutil.move(SRC, dst)
    print(f"Log archived as {dst}")

if __name__ == "__main__":
    main()
