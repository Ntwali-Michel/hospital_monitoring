import random
import time

# -------------------------------
# Heart Rate Detector Program
# -------------------------------

# Define safe range (you can adjust these numbers)
MIN_HEART_RATE = 60  # too low if less than this
MAX_HEART_RATE = 100  # too high if more than this

# This will keep a history of readings
heart_rate_log = []


def get_heart_rate():
    """
    Fake heart rate sensor.
    In real life this would connect to hardware.
    Here we just simulate a random number.
    """
    return random.randint(40, 130)


def check_heart_rate(rate):
    """
    Check if the heart rate is safe, too low, or too high.
    """
    if rate < MIN_HEART_RATE:
        return "⚠️ Warning: Heart rate too LOW!"
    elif rate > MAX_HEART_RATE:
        return "⚠️ Warning: Heart rate too HIGH!"
    else:
        return "✅ Heart rate is normal."


def display_summary():
    """
    Show the average, highest, and lowest heart rates recorded.
    """
    if len(heart_rate_log) == 0:
        print("No heart rate data recorded yet.")
        return

    avg_rate = sum(heart_rate_log) / len(heart_rate_log)
    highest = max(heart_rate_log)
    lowest = min(heart_rate_log)

    print("\n--- Session Summary ---")
    print(f"Readings taken: {len(heart_rate_log)}")
    print(f"Average heart rate: {avg_rate:.1f} bpm")
    print(f"Highest recorded: {highest} bpm")
    print(f"Lowest recorded: {lowest} bpm")
    print("------------------------\n")


def main():
    print("🫀 Heart Rate Detector Started")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Get simulated heart rate
            current_rate = get_heart_rate()

            # Save it to history
            heart_rate_log.append(current_rate)

            # Print result
            print(f"Current heart rate: {current_rate} bpm")
            message = check_heart_rate(current_rate)
            print(message)

            # Small pause before next reading
            time.sleep(1.5)

    except KeyboardInterrupt:
        print("\n\nProgram stopped by user.")
        display_summary()


# Run the program
if __name__ == "__main__":
    main()