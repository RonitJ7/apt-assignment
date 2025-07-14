# Readme

## Root Cause Identified

- Race conditions: Multiple workers process the same event simultaneously, leading to duplicates and inconsistent output.
- Lack of idempotency: Retried or overlapping jobs can emit duplicate or conflicting records.
- No event ownership: Events are not partitioned or locked, so any worker can process any event at any time.
- No deduplication layer: The output pipeline does not filter out duplicates or resolve conflicts.

## Future Improvements

### 1. Enforce Event Partitioning and Ownership
- Use a message queue (e.g., Kafka) with partitioning by event key (e.g., symbol or event_id).
- Ensure each partition is processed by only one worker at a time (consumer group semantics).
- This prevents two workers from processing the same event concurrently.
### 2. Distributed Locking 
- Use distributed locks (e.g., Redis, Zookeeper) to ensure only one worker processes a given event at a time.

### 3. Output Deduplication Layer
- Add a deduplication step before writing to the final output.
- For each (symbol, timestamp), keep only the latest, highest-confidence, or average record.
- Optionally, log or alert on detected duplicates for further investigation.

### 4. Monitoring and Alerting
- Set up alerts for abnormal patterns indicating race conditions or system stress.
- Could be just a simple alert system that could mail or update on active social medias.

### Use Exactly-Once Processing Frameworks
- Consider migrating to stream processing frameworks with built-in exactly-once guarantees (e.g., Kafka Streams, Flink, Spark Structured Streaming).
- These frameworks handle idempotency, ordering, and checkpointing natively.

## Example: Kafka + Idempotent Sink

- Use Kafka with event_id as the key.
- Each worker consumes a unique partition.
- Output sink (e.g., database) uses upsert on (symbol, timestamp) or event_id.
- Add a deduplication/validation job to scan for anomalies and alert.


