-- Koe Analytics — BigQuery Table Setup
-- Run once before deploying.
-- Replace YOUR_PROJECT and YOUR_DATASET with your values (default dataset: koe_analytics).
--
-- gcloud bigquery mk --dataset YOUR_PROJECT:koe_analytics
-- bq query --use_legacy_sql=false < setup/bigquery_tables.sql

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.koe_analytics.gesture_events` (
  event_id        STRING    NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  sign_label      STRING    NOT NULL,
  confidence_score FLOAT64  NOT NULL,
  recognized      BOOL      NOT NULL,
  language_selected STRING  NOT NULL,
  session_hash    STRING    NOT NULL,
  country_code    STRING
)
PARTITION BY DATE(event_timestamp)
OPTIONS (
  description = "Anonymized gesture recognition events — no user identity stored"
);

CREATE TABLE IF NOT EXISTS `YOUR_PROJECT.koe_analytics.tool_events` (
  event_id        STRING    NOT NULL,
  event_timestamp TIMESTAMP NOT NULL,
  tool_name       STRING    NOT NULL,
  confirmed       BOOL      NOT NULL,
  session_hash    STRING    NOT NULL
)
PARTITION BY DATE(event_timestamp)
OPTIONS (
  description = "MCP tool invocation events — tracks confirmation rate"
);
