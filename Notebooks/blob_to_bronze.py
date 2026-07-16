# Databricks notebook source
# DBTITLE 1,Load CSV files from blob to bronze using Auto Loader
# Auto Loader configuration to read CSV files from blob source
source_path = "/Volumes/retail_q/volumes/blob_source/transations_source/"
target_table = "retail_q.blob_bronze.transations"

# Read CSV files using Auto Loader (cloudFiles)
df = (spark.readStream
  .format("cloudFiles")
  .option("cloudFiles.format", "csv")
  .option("header", "true")
  .option("inferSchema", "true")
  .option("cloudFiles.schemaLocation", "/Volumes/retail_q/volumes/blob_source/_schema/transations")
  .load(source_path)
)

# Write to bronze table using Auto Loader
query = (df.writeStream
  .format("delta")
  .option("checkpointLocation", "/Volumes/retail_q/volumes/blob_source/_checkpoint/transations")
  .option("mergeSchema", "true")
  .trigger(availableNow=True)
  .toTable(target_table)
)

# Wait for the stream to process all available data and stop
query.awaitTermination()

print(f"✓ Successfully loaded data to {target_table}")

# COMMAND ----------

# MAGIC %sql
# MAGIC select count(*) from retail_q.blob_bronze.transations