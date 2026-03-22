import requests
import random
import time
import json

API_URL = "http://localhost:8000"

def stream_interactions(interval=2):
    print("🌟 Starting GraphRank Live Stream Simulator 🌟")
    print(f"Sending 1 random interaction every {interval} seconds...\n")
    
    # Wait for API to be ready
    while True:
        try:
            r = requests.get(f"{API_URL}/health")
            if r.status_code == 200:
                print("✅ API is ready. Commencing stream...")
                break
        except Exception:
            print("⏳ Waiting for API to become available...")
            time.sleep(5)
            
    # Continuously simulate random users connecting
    while True:
        try:
            # Picking random users based on our usual dataset size (assumed 500 max id)
            user_a = random.randint(0, 499)
            user_b = random.randint(0, 499)
            
            if user_a != user_b:
                interaction = {"user_a": user_a, "user_b": user_b}
                response = requests.post(f"{API_URL}/interactions", json=interaction)
                
                if response.status_code == 200:
                    print(f"📡 [LIVE] User {user_a} connected to User {user_b} -> Real-time API OK")
                else:
                    print(f"⚠️ [LIVE ERROR] API returned {response.status_code}: {response.text}")
                    
        except Exception as e:
            print(f"🛑 [LIVE STREAM HALTED] Error connecting to API: {e}")
            
        time.sleep(interval)

if __name__ == "__main__":
    stream_interactions()
