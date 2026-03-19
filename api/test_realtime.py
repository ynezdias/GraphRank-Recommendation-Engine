import requests
import time

API_URL = "http://localhost:8000"

def test_realtime():
    print("Wait for API to be ready...")
    for _ in range(10):
        try:
            r = requests.get(f"{API_URL}/health")
            if r.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(1)

    # 1. Fetch current top influencers to find a target
    print("Fetching top influencers...")
    r = requests.get(f"{API_URL}/top-influencers")
    influencers = r.json().get("top_influencers", [])
    if not influencers:
        print("No influencers found.")
        return

    # Let user_a be 1000 and user_b be the top influencer
    user_a = 1000
    user_b = influencers[0]
    user_b_id = user_b['user_id']
    old_pr = user_b['pagerank_score']
    
    print(f"Top influencer is {user_b['username']} (ID: {user_b_id}) with PR: {old_pr}")
    
    # 2. Add an interaction
    print(f"\nUser {user_a} is connecting with User {user_b_id}...")
    interaction = {"user_a": user_a, "user_b": user_b_id}
    r = requests.post(f"{API_URL}/interactions", json=interaction)
    print("Response:", r.json())
    
    # 3. Verify PageRank increased
    r = requests.get(f"{API_URL}/top-influencers")
    new_influencers = r.json().get("top_influencers", [])
    new_pr = next((x['pagerank_score'] for x in new_influencers if x['user_id'] == user_b_id), None)
    
    print(f"\nNew PR for {user_b['username']}: {new_pr}")
    if new_pr and new_pr > old_pr:
        print("✅ SUCCESS: PageRank increased in real-time!")
    else:
        print("❌ FAILED: PageRank did not increase.")
        
    # 4. Verify Recommendations for user_a
    print(f"\nChecking recommendations for User {user_a}...")
    r = requests.get(f"{API_URL}/recommendations/{user_a}")
    recs = r.json().get("recommendations", [])
    print(f"Recommendations found: {len(recs)}")
    for rec in recs:
        print(f" - ID: {rec.get('recommended_user_id', rec.get('username'))} (Score: {rec['score']})")

    if len(recs) > 0:
         print("✅ SUCCESS: Real-time recommendations generated via Triadic Closure!")
    else:
         print("❌ FAILED: No recommendations generated.")

if __name__ == "__main__":
    test_realtime()
