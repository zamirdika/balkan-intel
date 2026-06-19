import time
import subprocess
import sys

# Set the interval for how often you want to scrape new data (e.g., 900 seconds = 15 minutes)
FETCH_INTERVAL_SECONDS = 900 

def run_aggregator():
    """Executes the main pipeline script as a separate system process."""
    print(f"\n🚀 [{time.strftime('%H:%M:%S')}] Waking up aggregator engine...")
    try:
        # Runs 'python main.py' just like you do in the terminal
        result = subprocess.run([sys.executable, "main.py"], check=True)
        print(f"✅ [{time.strftime('%H:%M:%S')}] Cycle complete. Database updated.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error occurred during execution: {e}")

if __name__ == "__main__":
    print("🤖 News Aggregator Automation Daemon is active.")
    print(f"⏱️ The engine will scan for updates every {FETCH_INTERVAL_SECONDS // 60} minutes.")
    print("Press Ctrl+C at any time to halt the scheduler.")
    print("-" * 60)
    
    # Run once immediately on startup
    run_aggregator()
    
    # Enter the infinite automation loop
    while True:
        print(f"💤 Sleeping for {FETCH_INTERVAL_SECONDS // 60} minutes until next update...")
        time.sleep(FETCH_INTERVAL_SECONDS)
        run_aggregator()