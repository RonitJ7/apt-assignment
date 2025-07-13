🧠 The Great Data Shuffle

## Objective
You are given a dataset of time-series telemetry with misleading column names. Your task is to reverse-engineer the actual meaning of each column by analyzing patterns, relationships, and statistical clues in the data.

## Data Details
You are provided with a CSV containing the following fabricated fields:
- deltaX
- gamma
- omega
- flux
- pulse
- neutronCount

These DO NOT represent their real-world meaning. Instead they represent one of the following values regarding some stock: open, high, low, close, price, volume.

---

## Deliverables (All Mandatory)

1. 📌 **Final Mapping File (`mapping.json`)**
   - A JSON file specifying your mapping from fabricated names to real field names.

2. 📊 **Justification Notebook (`analysis.ipynb`)**
   - Must include:
     - Summary statistics for all columns
     - Visualizations (histograms, correlations, candlestick reconstructions)
     - Clear explanation of how you mapped each column

3. 🧪 **Validation Script (`validate_mapping.py`)**
   - Should read your mapping and verify integrity (e.g., `low ≤ close ≤ high`, `volume` should be largest magnitude, etc.)

4. 📄 **Short Write-up (`thought_process.md`)**
   - 300–500 words summarizing your reasoning, confidence, and process. What rules did you use? What were your doubts?

5. (Bonus - Optional) ⭐ **Confidence Scores**
   - Include in `mapping.json` a confidence score between 0.0 and 1.0 for each guess:
     ```json
     {
       "deltaX": {"mapping": "open", "confidence": 0.8},
       ...
     }
     ```

---

## Evaluation Rubric

| Category                     | Max Points | Notes |
|------------------------------|------------|-------|
| Final Mapping Accuracy       | 30         | Based on correct field identification |
| Justification Quality        | 20         | Reasoning must be rigorous, not guesses |
| Visual & Statistical Analysis| 15         | Effective use of plots and summaries |
| Validation Script Logic      | 15         | Script catches structural errors properly |
| Thought Process Write-up     | 10         | Structured, clear, insightful |
| (Opt) Confidence Calibration | +10        | Rewarded for well-calibrated guesses |

---

## Constraints
- Do NOT rely on column names.
- The dataset contains only 25% of the full data on which it will be finally evaluated. Your logic should generalize.
- No internet access or external data allowed.
- Auto-generated or random guesses without justification will be penalized.

---

## Submission Format
Please submit a ZIP file containing:
- `mapping.json`
- `analysis.ipynb`
- `validate_mapping.py`
- `thought_process.md`
