# Databricks notebook source
# DBTITLE 1,Create and populate calendar dimension
# MAGIC %sql
# MAGIC -- =====================================================================
# MAGIC -- GOLD LAYER: Calendar Dimension Table
# MAGIC -- =====================================================================
# MAGIC -- Purpose: Comprehensive date dimension for time-series analytics
# MAGIC -- Target: retail_q.retail_gold.dim_calendar
# MAGIC -- 
# MAGIC -- This script:
# MAGIC -- 1. Drops existing table (if any)
# MAGIC -- 2. Creates calendar table with comprehensive attributes
# MAGIC -- 3. Populates with date range from parameters (start_date, end_date)
# MAGIC -- =====================================================================
# MAGIC
# MAGIC -- Drop existing table
# MAGIC DROP TABLE IF EXISTS retail_q.retail_gold.dim_calendar;
# MAGIC
# MAGIC -- Create and populate in one statement using CTAS (Create Table As Select)
# MAGIC CREATE TABLE retail_q.retail_gold.dim_calendar
# MAGIC COMMENT 'Calendar dimension table for time-series analysis and reporting'
# MAGIC TBLPROPERTIES (
# MAGIC   'delta.enableChangeDataFeed' = 'false',
# MAGIC   'quality' = 'gold',
# MAGIC   'domain' = 'dimension'
# MAGIC )
# MAGIC AS
# MAGIC
# MAGIC WITH date_spine AS (
# MAGIC   -- Generate sequence of dates between start_date and end_date parameters
# MAGIC   SELECT 
# MAGIC     explode(
# MAGIC       sequence(
# MAGIC         to_date('${start_date}'),
# MAGIC         to_date('${end_date}'),
# MAGIC         interval 1 day
# MAGIC       )
# MAGIC     ) AS date_key
# MAGIC ),
# MAGIC
# MAGIC calendar_base AS (
# MAGIC   SELECT
# MAGIC     date_key,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- YEAR ATTRIBUTES
# MAGIC     -- ===============================================================
# MAGIC     YEAR(date_key) AS year,
# MAGIC     CAST(YEAR(date_key) AS STRING) AS year_name,
# MAGIC     
# MAGIC     -- Leap year check
# MAGIC     CASE 
# MAGIC       WHEN (YEAR(date_key) % 4 = 0 AND YEAR(date_key) % 100 != 0) 
# MAGIC         OR (YEAR(date_key) % 400 = 0) 
# MAGIC       THEN TRUE 
# MAGIC       ELSE FALSE 
# MAGIC     END AS is_leap_year,
# MAGIC     
# MAGIC     CASE 
# MAGIC       WHEN (YEAR(date_key) % 4 = 0 AND YEAR(date_key) % 100 != 0) 
# MAGIC         OR (YEAR(date_key) % 400 = 0) 
# MAGIC       THEN 366 
# MAGIC       ELSE 365 
# MAGIC     END AS days_in_year,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- QUARTER ATTRIBUTES
# MAGIC     -- ===============================================================
# MAGIC     QUARTER(date_key) AS quarter,
# MAGIC     CONCAT('Q', QUARTER(date_key)) AS quarter_name,
# MAGIC     CONCAT(YEAR(date_key), '-Q', QUARTER(date_key)) AS year_quarter,
# MAGIC     DATE_TRUNC('QUARTER', date_key) AS quarter_start_date,
# MAGIC     LAST_DAY(DATE_TRUNC('QUARTER', date_key) + INTERVAL 2 MONTH) AS quarter_end_date,
# MAGIC     DATEDIFF(date_key, DATE_TRUNC('QUARTER', date_key)) + 1 AS day_of_quarter,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- MONTH ATTRIBUTES
# MAGIC     -- ===============================================================
# MAGIC     MONTH(date_key) AS month,
# MAGIC     DATE_FORMAT(date_key, 'MMMM') AS month_name,
# MAGIC     DATE_FORMAT(date_key, 'MMM') AS month_name_short,
# MAGIC     DATE_FORMAT(date_key, 'yyyy-MM') AS year_month,
# MAGIC     CONCAT(YEAR(date_key), ' ', DATE_FORMAT(date_key, 'MMMM')) AS year_month_name,
# MAGIC     DATE_TRUNC('MONTH', date_key) AS month_start_date,
# MAGIC     LAST_DAY(date_key) AS month_end_date,
# MAGIC     DAY(LAST_DAY(date_key)) AS days_in_month,
# MAGIC     DAY(date_key) AS day_of_month,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- WEEK ATTRIBUTES
# MAGIC     -- ===============================================================
# MAGIC     WEEKOFYEAR(date_key) AS week_of_year,
# MAGIC     EXTRACT(WEEK FROM date_key) AS iso_week,
# MAGIC     EXTRACT(YEAR FROM date_key) AS iso_year,
# MAGIC     DATE_TRUNC('WEEK', date_key) AS week_start_date,
# MAGIC     DATE_ADD(DATE_TRUNC('WEEK', date_key), 6) AS week_end_date,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- DAY ATTRIBUTES
# MAGIC     -- ===============================================================
# MAGIC     DAYOFYEAR(date_key) AS day_of_year,
# MAGIC     DAYOFWEEK(date_key) AS day_of_week,
# MAGIC     DATE_FORMAT(date_key, 'EEEE') AS day_name,
# MAGIC     DATE_FORMAT(date_key, 'EEE') AS day_name_short,
# MAGIC     
# MAGIC     -- ===============================================================
# MAGIC     -- FISCAL PERIOD (assuming fiscal year = calendar year)
# MAGIC     -- ===============================================================
# MAGIC     YEAR(date_key) AS fiscal_year,
# MAGIC     QUARTER(date_key) AS fiscal_quarter,
# MAGIC     MONTH(date_key) AS fiscal_month,
# MAGIC     WEEKOFYEAR(date_key) AS fiscal_week
# MAGIC     
# MAGIC   FROM date_spine
# MAGIC )
# MAGIC
# MAGIC SELECT
# MAGIC   -- Primary key
# MAGIC   date_key,
# MAGIC   
# MAGIC   -- Year attributes
# MAGIC   year,
# MAGIC   year_name,
# MAGIC   is_leap_year,
# MAGIC   days_in_year,
# MAGIC   
# MAGIC   -- Quarter attributes
# MAGIC   quarter,
# MAGIC   quarter_name,
# MAGIC   year_quarter,
# MAGIC   quarter_start_date,
# MAGIC   quarter_end_date,
# MAGIC   day_of_quarter,
# MAGIC   
# MAGIC   -- Month attributes
# MAGIC   month,
# MAGIC   month_name,
# MAGIC   month_name_short,
# MAGIC   year_month,
# MAGIC   year_month_name,
# MAGIC   month_start_date,
# MAGIC   month_end_date,
# MAGIC   days_in_month,
# MAGIC   day_of_month,
# MAGIC   
# MAGIC   -- Week attributes
# MAGIC   week_of_year,
# MAGIC   iso_week,
# MAGIC   iso_year,
# MAGIC   week_start_date,
# MAGIC   week_end_date,
# MAGIC   
# MAGIC   -- Day attributes
# MAGIC   day_of_year,
# MAGIC   day_of_week,
# MAGIC   day_name,
# MAGIC   day_name_short,
# MAGIC   
# MAGIC   -- Business day flags
# MAGIC   CASE WHEN day_of_week BETWEEN 2 AND 6 THEN TRUE ELSE FALSE END AS is_weekday,
# MAGIC   CASE WHEN day_of_week IN (1, 7) THEN TRUE ELSE FALSE END AS is_weekend,
# MAGIC   CASE WHEN date_key = month_start_date THEN TRUE ELSE FALSE END AS is_month_start,
# MAGIC   CASE WHEN date_key = month_end_date THEN TRUE ELSE FALSE END AS is_month_end,
# MAGIC   CASE WHEN date_key = quarter_start_date THEN TRUE ELSE FALSE END AS is_quarter_start,
# MAGIC   CASE WHEN date_key = quarter_end_date THEN TRUE ELSE FALSE END AS is_quarter_end,
# MAGIC   CASE WHEN day_of_year = 1 THEN TRUE ELSE FALSE END AS is_year_start,
# MAGIC   CASE WHEN day_of_year = days_in_year THEN TRUE ELSE FALSE END AS is_year_end,
# MAGIC   
# MAGIC   -- Fiscal attributes
# MAGIC   fiscal_year,
# MAGIC   fiscal_quarter,
# MAGIC   fiscal_month,
# MAGIC   fiscal_week,
# MAGIC   
# MAGIC   -- Relative date flags (computed at query time)
# MAGIC   CASE WHEN date_key = CURRENT_DATE() THEN TRUE ELSE FALSE END AS is_current_day,
# MAGIC   CASE WHEN date_key BETWEEN DATE_TRUNC('WEEK', CURRENT_DATE()) 
# MAGIC                          AND DATE_ADD(DATE_TRUNC('WEEK', CURRENT_DATE()), 6) 
# MAGIC        THEN TRUE ELSE FALSE END AS is_current_week,
# MAGIC   CASE WHEN YEAR(date_key) = YEAR(CURRENT_DATE()) 
# MAGIC         AND MONTH(date_key) = MONTH(CURRENT_DATE()) 
# MAGIC        THEN TRUE ELSE FALSE END AS is_current_month,
# MAGIC   CASE WHEN YEAR(date_key) = YEAR(CURRENT_DATE()) 
# MAGIC         AND QUARTER(date_key) = QUARTER(CURRENT_DATE()) 
# MAGIC        THEN TRUE ELSE FALSE END AS is_current_quarter,
# MAGIC   CASE WHEN YEAR(date_key) = YEAR(CURRENT_DATE()) 
# MAGIC        THEN TRUE ELSE FALSE END AS is_current_year,
# MAGIC   
# MAGIC   -- Metadata
# MAGIC   CURRENT_TIMESTAMP() AS created_timestamp
# MAGIC   
# MAGIC FROM calendar_base
# MAGIC
# MAGIC ORDER BY date_key;

# COMMAND ----------

# DBTITLE 1,Validate calendar table
# MAGIC %sql
# MAGIC -- =====================================================================
# MAGIC -- VALIDATION: Calendar Table Statistics and Sample Data
# MAGIC -- =====================================================================
# MAGIC
# MAGIC -- Summary statistics
# MAGIC SELECT
# MAGIC   'Total Days' AS metric,
# MAGIC   CAST(COUNT(*) AS STRING) AS value
# MAGIC FROM retail_q.retail_gold.dim_calendar
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Date Range' AS metric,
# MAGIC   CONCAT(MIN(date_key), ' to ', MAX(date_key)) AS value
# MAGIC FROM retail_q.retail_gold.dim_calendar
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Total Years' AS metric,
# MAGIC   CAST(COUNT(DISTINCT year) AS STRING) AS value
# MAGIC FROM retail_q.retail_gold.dim_calendar
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Weekdays' AS metric,
# MAGIC   CAST(SUM(CASE WHEN is_weekday THEN 1 ELSE 0 END) AS STRING) AS value
# MAGIC FROM retail_q.retail_gold.dim_calendar
# MAGIC
# MAGIC UNION ALL
# MAGIC
# MAGIC SELECT
# MAGIC   'Weekend Days' AS metric,
# MAGIC   CAST(SUM(CASE WHEN is_weekend THEN 1 ELSE 0 END) AS STRING) AS value
# MAGIC FROM retail_q.retail_gold.dim_calendar;

# COMMAND ----------

# DBTITLE 1,Sample calendar records
# MAGIC %sql
# MAGIC -- =====================================================================
# MAGIC -- SAMPLE DATA: View calendar attributes for recent dates
# MAGIC -- =====================================================================
# MAGIC
# MAGIC SELECT
# MAGIC   date_key,
# MAGIC   year,
# MAGIC   quarter_name,
# MAGIC   month_name,
# MAGIC   day_name,
# MAGIC   week_of_year,
# MAGIC   day_of_month,
# MAGIC   day_of_year,
# MAGIC   is_weekday,
# MAGIC   is_weekend,
# MAGIC   is_month_start,
# MAGIC   is_month_end,
# MAGIC   is_quarter_start,
# MAGIC   is_quarter_end
# MAGIC FROM retail_q.retail_gold.dim_calendar
# MAGIC WHERE year = YEAR(CURRENT_DATE())
# MAGIC ORDER BY date_key DESC
# MAGIC LIMIT 30;

# COMMAND ----------

# DBTITLE 1,View complete table schema
# MAGIC %sql
# MAGIC -- =====================================================================
# MAGIC -- SCHEMA: View all available columns in the calendar table
# MAGIC -- =====================================================================
# MAGIC
# MAGIC DESCRIBE retail_q.retail_gold.dim_calendar;