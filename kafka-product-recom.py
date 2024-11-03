from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StringType, StructType, StructField

# Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaProductRecommendation") \
    .getOrCreate()

# Define schema for incoming data
schema = StructType([
    StructField("product_id", StringType(), True)
])

# Read stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "idpushtopic") \
    .load()

# Convert the value column (from Kafka) to a string and apply schema
df = df.selectExpr("CAST(value AS STRING)") \
       .select(from_json(col("value"), schema).alias("data")) \
       .select("data.*")

# Example processing - here, you would integrate your recommendation logic
# For demonstration, we'll just output the product_id received
recommendations = df.withColumn("recommendation", col("product_id"))  # Placeholder for recommendation logic

# Write the output back to Kafka (to the prodRecommSend topic)
query = recommendations.selectExpr("CAST(product_id AS STRING) AS key", "CAST(recommendation AS STRING) AS value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("topic", "prodRecommSend") \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .start()

query.awaitTermination()
