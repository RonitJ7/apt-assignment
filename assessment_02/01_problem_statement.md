# ⚠️ Problem 2: Race Condition Replay

You're tasked with analyzing a real-time stream processing system for a high-frequency trading platform. Rare race conditions are introducing silent duplicates in the output.

---

## 📂 Files Provided (Expanded Description)

The following files are included in the assessment bundle:

### 📝 `raw_tick_events.log`
- Format: newline-delimited JSON (JSONL)
- Represents the **original stream** of market tick events arriving in real-time.
- Each line contains:
  - `event_id`: Unique ID for the tick
  - `timestamp`: ISO timestamp of event creation (server time)
  - `symbol`: Stock symbol (e.g., TCS, INFY)
  - `price`: Event price at the tick
  - `source`: Always `stream-1` for this dataset
- This is your **source of truth** for what events should be processed exactly once.

### 🛠 `worker_logs.csv`
- Format: CSV
- Contains execution metadata for the distributed worker system.
- Fields include:
  - `event_id`: ID of the event being processed
  - `worker_id`: One of `worker-1`, `worker-2`, or `worker-3`
  - `start_time`: When the worker started processing the event
  - `end_time`: When it finished (may be `null` if it crashed)
  - `status`: `success` or `timeout`
- You’ll use this to reconstruct **processing timelines**, identify **crashes**, and detect **retries** or **races**.

### 📉 `final_output.csv`
- Format: CSV
- Represents the **actual output** emitted by the system after processing.
- Contains:
  - `symbol`
  - `timestamp`
  - `price`
- This file **should ideally match** the tick stream, but due to race conditions and retry logic, you may find:
  - Duplicates (same symbol and timestamp more than once)
  - Slight price variations (due to reprocessing)
  - Timestamp jitter (same event appearing at different times)
- This is the **corrupted end product** that your scripts must clean and explain.

---

## 🎯 Tasks (Expanded Description)

Your objective is to reverse-engineer and debug how silent data duplication and corruption occurred in a high-throughput event stream processing system. The system comprises multiple workers processing tick data events in parallel, but rare race conditions and retry behavior are leading to anomalies in the final output.

Use the three provided datasets to carry out the following tasks:

### 🔍 1. Reconstruct Event Timelines
- Parse the `worker_logs.csv` to create a timeline of which worker processed which event and when.
- Identify:
  - Overlapping processing windows
  - Retried jobs
  - Events that failed (e.g., due to timeouts)
- Bonus: Visualize this timeline using plots (e.g., Gantt chart per worker).

### 📊 2. Detect and Quantify Duplicates
- Analyze `final_output.csv` to:
  - Count how many duplicated records exist (based on `symbol` and `timestamp`).
  - Determine if duplicates have the **same** or **slightly different** price/timestamp values.
  - Create a summary table showing:
    - Count of duplicates per symbol
    - Price shift range across duplicates
    - Time differences (if any)
- Output this as `duplication_analysis.csv`.

### 🧹 3. Write a De-duplication Script
- Implement `deduplicate_stream.py` that takes `final_output.csv` as input and produces a clean version as `deduplicated_output.csv`.
- Use logical rules like:
  - Keep only the last processed record per `(symbol, timestamp)`
  - Or retain record with highest confidence/price if applicable
- Make the script generic and reproducible.

### 💡 4. (Optional Bonus) Suggest Prevention Strategies
- Think like a systems engineer. If you had to prevent this in production:
  - What safeguards would you introduce?
  - Examples: Idempotency, Kafka keys, TTL windows, coordination protocols, stream joins, etc.
- Document your ideas in `future_improvements.md`.

---

## ✅ Deliverables (Expanded Description)

Please include the following artifacts in your submission, clearly named and organized:

### 📊 `timeline_visualization.ipynb`
- A Jupyter notebook that reconstructs how events flowed through the worker system.
- Should include:
  - Plots or Gantt-style charts showing worker activity timelines.
  - Markers where retries, crashes, or overlaps occurred.
  - Commentary explaining observed patterns and potential replay windows.
- Should demonstrate your ability to interpret the raw logs into meaningful processing timelines.

### 📈 `duplication_analysis.csv`
- A structured CSV output containing a summary of duplication detection.
- Columns must include at least:
  - `symbol`
  - `timestamp`
  - `occurrences` (how many times this event appeared in final_output)
  - `price_shift` (difference between min and max price for that timestamp)
- Additional fields like deviation in timestamp (if applicable) can be included.
- Should help quantify the impact of race conditions on the output.

### 🧹 `deduplicate_stream.py`
- A standalone Python script that:
  - Reads the `final_output.csv`
  - Cleans up duplicates or corrupted entries
  - Outputs a clean CSV (`deduplicated_output.csv`)
- Should include:
  - A method to resolve multiple entries (e.g., keep latest, average price, etc.)
  - Simple CLI invocation with input/output path as arguments


### 💡 (Optional) `future_improvements.md`
- Describe possible architectural improvements to prevent such race conditions in a real system.
- Example suggestions:
  - Enforcing stream ordering
  - Idempotent event processing
  - Use of Kafka keys or checkpointing strategies
- Bonus points for creative or technically sound ideas.

---

## 🧪 Scoring Breakdown

| Component                        | Points |
|----------------------------------|--------|
| Timeline Reconstruction          | 10     |
| Duplication Quantification       | 10     |
| Root Cause Explanation           | 10     |
| `deduplicate_stream.py` Accuracy | 10     |
| Thought Process Report           | 5      |
| Bonus Suggestions                | +5     |

Minimum passing: **22/40**
