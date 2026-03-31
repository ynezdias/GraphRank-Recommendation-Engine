import psycopg2
import os

DB_HOST = os.getenv("DB_HOST", "localhost")
POSTGRES_DSN = f"dbname=graphrank user=admin password=admin host={DB_HOST} port=5432"

def main():
    print("Evaluating A/B Testing Results...")
    try:
        conn = psycopg2.connect(POSTGRES_DSN)
        with conn.cursor() as cur:
            # First check if the table exists
            cur.execute("SELECT to_regclass('public.recommendation_engagements');")
            if cur.fetchone()[0] is None:
                print("Error: Table 'recommendation_engagements' does not exist yet. Run the load script first.")
                return

            cur.execute("""
                SELECT 
                    experiment_variant,
                    COALESCE(SUM(CASE WHEN interaction_type = 'impression' THEN 1 ELSE 0 END), 0) as impressions,
                    COALESCE(SUM(CASE WHEN interaction_type = 'click' THEN 1 ELSE 0 END), 0) as clicks,
                    CASE WHEN SUM(CASE WHEN interaction_type = 'impression' THEN 1 ELSE 0 END) = 0 THEN 0.0
                         ELSE ROUND(SUM(CASE WHEN interaction_type = 'click' THEN 1.0 ELSE 0.0 END) * 100.0 / SUM(CASE WHEN interaction_type = 'impression' THEN 1.0 ELSE 0.0 END), 2)
                    END as ctr_percentage
                FROM recommendation_engagements
                GROUP BY experiment_variant
                ORDER BY ctr_percentage DESC;
            """)
            results = cur.fetchall()
            
            print("\n=== A/B Test Evaluation: Click-Through Rate ===")
            print(f"{'Variant':<15} | {'Impressions':<12} | {'Clicks':<10} | {'CTR (%)':<8}")
            print("-" * 55)
            if not results:
                print("No engagement data found.")
            for row in results:
                variant, imp, clicks, ctr = row
                print(f"{variant:<15} | {imp:<12} | {clicks:<10} | {ctr:<8.2f}")
                
    except Exception as e:
        print(f"Failed to evaluate A/B test: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    main()
