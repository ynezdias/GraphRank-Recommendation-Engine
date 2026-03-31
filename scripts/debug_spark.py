from pyspark.sql import SparkSession
import sys

print("Python version:", sys.version)
try:
    spark = SparkSession.builder.appName("Debug").getOrCreate()
    print("Spark context initialized successfully")
    spark.stop()
except Exception as e:
    print("Error initializing Spark:", str(e))
