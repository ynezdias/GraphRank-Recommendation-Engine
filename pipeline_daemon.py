import schedule
import time
import subprocess
import logging
from datetime import datetime

# Configure robust logging for the daemon
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GraphRank_Scheduler")

def run_step(command, step_name):
    logger.info(f"🚀 STARTING: {step_name}")
    try:
        # Capture output for the log
        result = subprocess.run(
            command, 
            shell=True, 
            check=True,
            capture_output=True,
            text=True
        )
        logger.info(f"✅ COMPLETED: {step_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FAILED: {step_name}")
        logger.error(f"Exit Code: {e.returncode}\nError Output: {e.stderr}")
        return False

def execute_pipeline():
    logger.info("="*50)
    logger.info("🔄 Initiating GraphRank Pipeline Execution")
    logger.info("="*50)

    # 1. Generate New Synthetic Data (Simulating arrival of new edges/nodes)
    if not run_step(
        "python data_gen/generate_data.py --num-users 500 --num-connections 2000 --num-posts 1000", 
        "Data Generation"
    ): return

    # 2. Process Graph Structure (Spark)
    if not run_step("python spark_jobs/process_graph.py", "Spark Structuring"): return

    # 3. Compute Influence & Recommendations (Spark)
    if not run_step("python spark_jobs/graph_engine.py", "PageRank Calculation"): return

    # 4. Ingest and Upsert into Postgres & Redis
    # Note: We assume the target DBs (Postgres/Redis via Docker) are already running.
    if not run_step("python load/load_data.py", "Database Upsert & Cache Priming"): return

    logger.info("🎉 Pipeline loop finished successfully. Waiting for next interval...")
    logger.info("="*50)


def main():
    logger.info("🌟 Starting GraphRank Production Daemon 🌟")
    
    # In a rapid demonstration scenario, we run every 5 minutes.
    # In real life, this might be .every().day.at("02:00")
    job = schedule.every(5).minutes.do(execute_pipeline)
    
    logger.info("⏰ Scheduler active. Next run scheduled for: " + str(job.next_run))
    
    # Execute immediately on start for the first batch
    execute_pipeline()

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Daemon stopped manually.")

if __name__ == "__main__":
    main()
