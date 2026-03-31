
# 📌 GraphRank

### Distributed Social Graph Influence & Recommendation Engine
[![Tech Stack](https://img.shields.io/badge/Stack-PySpark%20|%20FastAPI%20|%20Redis%20-blue.svg)](https://github.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

GraphRank is a high-performance distributed systems project designed to simulate the "social brain" of professional networking platforms. It processes millions of data points to identify influencers, detect communities, and rank content feeds in real-time.

---

## 📖 Overview
In modern social networks, "who you know" and "what you see" are determined by massive graph computations. **GraphRank** tackles this challenge by combining big data engineering with graph theory. 

The system processes:
* **100,000+** Synthetic Users
* **1,000,000+** Social Edges (Connections)
* **500,000+** Interaction Logs (Likes, Shares, Comments)

---

## 🛠 Tech Stack

| Category | Technology |
| :--- | :--- |
| **Data Processing** | PySpark (Distributed Batch Processing) |
| **Backend API** | FastAPI (Asynchronous Python) |
| **Graph Logic** | NetworkX & Custom Adjacency Optimizations |
| **Databases** | PostgreSQL (Structured), Redis (Caching Layer) |
| **DevOps** | Docker, Docker Compose |

---

## 🧠 Core Algorithms & Logic

### 1. Influence Scoring
We calculate user "importance" using a multi-factor weighted formula:
$$Influence = 0.4(PageRank) + 0.3(Engagement) + 0.2(Centrality) + 0.1(Recency)$$

### 2. Feed Ranking Engine
Posts are ranked dynamically to ensure high-quality content discovery using a time-decay model:
$$Score = (Weight \cdot Engagement) \times e^{-\lambda \cdot \Delta t}$$
*Where $\lambda$ represents the decay constant for content freshness.*

### 3. Recommendation System
"People You May Know" is driven by:
* **Jaccard Similarity:** To find overlap in mutual connections.
* **Community Detection:** Using the **Louvain Algorithm** to identify industry clusters.

---

## 🏗 System Architecture

1.  **Synthetic Layer:** Generates pseudo-realistic social data.
2.  **Spark Layer:** Aggregates raw logs and builds the weighted graph.
3.  **Graph Engine:** Calculates PageRank and clustering coefficients.
4.  **API Layer:** Serves ranked feeds and recommendations via **REST endpoints**.

---

## 👥 The Team & Responsibilities

### **Sania (Data Analyst)**
* **Algorithm Design:** Lead on PageRank implementation and similarity metrics.
* **Feature Engineering:** Defining interaction weights and engagement scoring.
* **Validation:** Evaluating model performance using **Precision@K** and **Recall**.

### **Ynez (SDE)**
* **System Infrastructure:** Dockerization, Redis integration, and API architecture.
* **Data Pipelines:** Optimizing PySpark jobs for large-scale joins and broadcast variables.
* **Latency Optimization:** Ensuring sub-150ms response times for feed generation.

---

## 🚀 Quick Start (Development)

1. **Clone the repo:**
   ```bash
   git clone 
   cd graphrank

```

2. **Spin up the environment:**
```bash
docker-compose up --build

```


3. **Run the Spark Pipeline:**
```bash
docker exec -it graphrank_spark spark-submit /jobs/process_graph.py

```



---

## 📊 Performance Targets

* **Scale:** Support up to 1.5M interaction records.
* **Latency:** < 150ms for recommendation API calls.
* **Efficiency:** 40% reduction in processing time through Spark parallelization.

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

## 🌐 API Reference

Base URL (Local Sandbox): `http://localhost:8000`

### Get Health
```http
GET /api/health
```
Returns pipeline and API status metric.

### Top Influencers
```http
GET /api/top-influencers?limit=10
```
Queries PostgreSQL for users sorted rapidly by `pagerank_score`.

### Recommendations
```http
GET /api/recommendations/{user_id}
```
Queries people-you-may-know logic relying heavily on a Redis Cache layer to serve predictions < 10ms.

---

## 🏗 Operations & Load Testing

### Environment Variables
Configure `.env` in root with the following definitions matching your local Docker mapping:
```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_DB=graphrank
DB_HOST=postgres
REDIS_HOST=redis
REDIS_PORT=6379
```

### Load Testing with Locust
To certify the Redis layer performs under high concurrency, initiate the swarm logic:
```bash
locust -f locustfile.py --host=http://localhost:8000
```
Navigate to `http://localhost:8089` to launch the tests.
