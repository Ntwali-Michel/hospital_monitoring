#!/usr/bin/env python3
import argparse, glob, os, shutil, subprocess, sys

def main():
    ap = argparse.ArgumentParser(description="Backup archived logs.")
    ap.add_argument("--group", type=int, default=1, help="Group number")
    ap.add_argument("--remote", help="user@host:/path (optional scp destination)")
    args = ap.parse_args()

    folder = f"archived_logs_group{args.group}"
    os.makedirs(folder, exist_ok=True)

    files = glob.glob("heart_rate_log_*.csv")
    if not files:
        print("No archived logs found.")
        return

    for fp in files:
        dst = os.path.join(folder, os.path.basename(fp))
        shutil.move(fp, dst)
        print(f"moved -> {dst}")

    if args.remote:
        try:
            subprocess.check_call(["scp", *glob.glob(f"{folder}/*"), args.remote])
            print("remote backup complete.")
        except subprocess.CalledProcessError as e:
            print("scp failed:", e, file=sys.stderr)

    print(f"local backup complete in {folder}/")

if __name__ == "__main__":
    main()
