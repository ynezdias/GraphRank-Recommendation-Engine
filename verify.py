import requests
import json
import time

def main():
    print("Simulating Engagements via Nginx Load Balancer (http://localhost:8000)...")
    
    # 1. Health check
    try:
        r = requests.get("http://localhost:8000/health")
        print(f"Health Check: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return

    # 2. Get recommendations
    print("\nGetting Recommendations for User 2 (Treatment)...")
    r2 = requests.get("http://localhost:8000/recommendations/2")
    if r2.status_code == 200:
        print(r2.json())
        
    print("\nGetting Recommendations for User 4 (Control)...")
    r4 = requests.get("http://localhost:8000/recommendations/4")
    if r4.status_code == 200:
        print(r4.json())

    # 3. Simulate Impressions & Clicks
    print("\nSimulating Interactions...")
    headers = {"Content-Type": "application/json"}
    
    interactions = [
        # Treatment: 1 impression, 1 click (100% CTR)
        {"user_id": 2, "recommended_user_id": 10, "experiment_variant": "treatment", "interaction_type": "impression"},
        {"user_id": 2, "recommended_user_id": 10, "experiment_variant": "treatment", "interaction_type": "click"},
        # Control: 2 impressions, 1 click (50% CTR)
        {"user_id": 4, "recommended_user_id": 12, "experiment_variant": "control", "interaction_type": "impression"},
        {"user_id": 4, "recommended_user_id": 12, "experiment_variant": "control", "interaction_type": "click"},
        {"user_id": 6, "recommended_user_id": 15, "experiment_variant": "control", "interaction_type": "impression"}
    ]
    
    for i in interactions:
        r = requests.post("http://localhost:8000/engagement", json=i, headers=headers)
        print(f"Logged {i['interaction_type']} for {i['experiment_variant']} - Status: {r.status_code}")
        time.sleep(0.1)

if __name__ == "__main__":
    main()
