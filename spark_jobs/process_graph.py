from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("GraphRank Processing") \
    .getOrCreate()

connections = spark.read.csv("connections.csv", header=True, inferSchema=True)

degree = connections.groupBy("user_a").count()

degree.show()

degree.write.csv("user_degree")