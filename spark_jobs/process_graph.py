from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("GraphRank Processing") \
    .getOrCreate()

connections = spark.read.csv("data/connections.csv", header=True, inferSchema=True)

# Count degree of each node
degree = connections.groupBy("user_a").count()

degree.show()

degree.write.csv("processed/user_degree", mode="overwrite")