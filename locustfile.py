import random
from locust import HttpUser, task, between

class GraphRankLoadTest(HttpUser):
    wait_time = between(0.5, 2)  # Wait 0.5 to 2 seconds between tasks

    @task(1)
    def test_health(self):
        """Minimal load on health check."""
        self.client.get("/api/health")

    @task(3)
    def test_top_influencers(self):
        """Moderate load on DB aggregated query."""
        self.client.get("/api/top-influencers?limit=10")

    @task(5)
    def test_cache_hits(self):
        """
        High load on specific users expected to be in Redis cache.
        Usually users 1-50 are the most active in our sample tests.
        """
        user_id = random.randint(1, 50)
        self.client.get(f"/api/recommendations/{user_id}", name="/api/recommendations/[cached]")

    @task(2)
    def test_cache_misses(self):
        """
        Force cache misses by querying wide random IDs, 
        testing PostgreSQL dynamic Join lookup speeds.
        """
        user_id = random.randint(1000, 99999) 
        self.client.get(f"/api/recommendations/{user_id}", name="/api/recommendations/[miss]")
