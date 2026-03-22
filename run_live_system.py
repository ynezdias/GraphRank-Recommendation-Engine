import subprocess
import time
import os
import sys

def run_step(command, step_name):
    print(f"\n{'='*50}")
    print(f"🚀 INITIALIZING: {step_name}")
    print(f"{'='*50}")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {step_name}")
        return False

def main():
    print("🔥 Starting GraphRank Fully Integrated Live System 🔥\n")

    # 1. Bring up Infrastructure (PostgreSQL, Redis, API)
    if not run_step("docker-compose up -d --build postgres redis api", "Starting Core Infrastructure"): 
        print("Failed to start docker. Ensure Docker Desktop is running.")
        return

    print("\n⏳ Allowing 10 seconds for databases and API to stabilize...")
    time.sleep(10)

    # 2. Run initial batch priming to ensure data exists
    if not run_step("python run_pipeline.py", "Priming Base Data Pipeline"):
        print("Warning: Base data pipeline failed, but starting live components anyway...")

    processes = []
    
    print("\n" + "="*50)
    print("🌐 STAGE 2: INITIATING LIVE PLATFORM COMPONENTS")
    print("="*50)
    
    try:
        # 3. Start the Batch Daemon in the background (Runs every 5 mins)
        print("▶️  Starting Background Batch Daemon (pipeline_daemon.py)")
        daemon_proc = subprocess.Popen([sys.executable, "pipeline_daemon.py"])
        processes.append(daemon_proc)
        
        # 4. Start the Live Stream Simulator in the background
        print("▶️  Starting Live Stream Simulator (stream_simulator.py)")
        stream_proc = subprocess.Popen([sys.executable, "stream_simulator.py"])
        processes.append(stream_proc)
        
        print("\n🎉 Both Batch and Real-Time components are now running continuously!")
        print("Press Ctrl+C to stop all services.\n")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down live platform...")
        for p in processes:
            p.terminate()
        print("🛑 Bringing down Docker containers...")
        subprocess.run("docker-compose down", shell=True)
        print("✅ Graceful shutdown complete.")

if __name__ == "__main__":
    main()
