import time
import subprocess
from datetime import datetime

def run_command(command, directory=None):
    """Executes a terminal command and prints the output cleanly."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚙️ Executing: {command}")
    try:
        # We use subprocess to run exact terminal commands
        subprocess.run(command, shell=True, cwd=directory, check=True)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Success.\n")
    except subprocess.CalledProcessError as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error running {command}: {e}\n")

def start_autopilot(interval_minutes=60):
    print("🚀 Balkan Intel Aggregator Autopilot Engaged!")
    print(f"Interval set to: {interval_minutes} minutes. Press Ctrl+C to stop.\n")
    
    while True:
        print("=" * 60)
        print(f"🔄 Starting new ingestion cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60 + "\n")
        
        # 1. Scrape Layer 2 (Bosnia)
        run_command("scrapy crawl klix", directory="balkan_news_crawler")
        
        # 2. Scrape Layer 1 (Albania/North Macedonia)
        run_command("scrapy crawl alsat", directory="balkan_news_crawler")
        
        # 3. Run the AI Clustering & Translation Engine
        run_command("python cluster_engine.py")
        
        # 4. Run the Divergent Perspectives AI
        run_command("python perspective_engine.py")
        
        # 5. Sleep until the next cycle
        sleep_seconds = interval_minutes * 60
        print(f"💤 Cycle complete! The Streamlit UI is now updated.")
        print(f"⏳ Sleeping for {interval_minutes} minutes...\n")
        time.sleep(sleep_seconds)

if __name__ == "__main__":
    # You can change the 60 here to run more or less frequently
    start_autopilot(interval_minutes=60)