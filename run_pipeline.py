import subprocess
import time
import os

def run_step(command, step_name):
    print(f"\n{'='*50}")
    print(f"🚀 RUNNING STEP: {step_name}")
    print(f"{'='*50}")
    
    try:
        # We use shell=True for windows cross-compatibility and simple execution
        result = subprocess.run(command, shell=True, check=True)
        print(f"✅ STEP COMPLETED: {step_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ STEP FAILED: {step_name}")
        print(f"Command '{command}' returned non-zero exit status {e.returncode}.")
        return False

def main():
    print("🌟 GraphRank End-to-End Pipeline Execution 🌟\n")

    # 1. Generate Synthetic Data
    if not run_step("python data_gen/generate_data.py --num-users 500 --num-connections 2000 --num-posts 1000", "Synthetic Data Generation"): return

    # 2. Process Graph Structure (Spark)
    if not run_step("python spark_jobs/process_graph.py", "Spark Graph Processing (Metrics)"): return

    # 3. Compute Influence & Recommendations (Spark)
    if not run_step("python spark_jobs/graph_engine.py", "Spark Graph Engine (PageRank & Recs)"): return

    # 4. Offline Evaluation & Validation (Spark)
    if not run_step("python spark_jobs/evaluate_model.py", "Recommendation Evaluation (Precision & Recall)"): return

    # 5. Start Database & Cache Containers
    if not run_step("docker-compose up -d postgres redis", "Start Infrastructure Containers"): return
    
    print("\n⏳ Waiting 10 seconds for databases to initialize...")
    time.sleep(10)

    # 6. Load Data into Postgres & Redis
    # We run this on the host since the Python env is here, pointing to localhost mapped ports
    if not run_step("python load/load_data.py", "Database Ingestion & Cache Priming"): return

    # 7. Build and Start API Container
    if not run_step("docker-compose up -d --build api", "Deploy API Service"): return
    
    print("\n" + "="*50)
    print("🎉 GraphRank Pipeline Execution Complete! 🎉")
    print("API is available at: http://localhost:8000")
    print("Test endpoints:")
    print("  - http://localhost:8000/top-influencers")
    print("  - http://localhost:8000/recommendations/1")
    print("="*50)

if __name__ == "__main__":
    main()
