# Thought Process 

Repository : https://github.com/RonitJ7/apt-assignment

## The Challenge

Presented with a dataset containing financial time series data. All the column names are masked with cryptic names like 'neuronCount', 'deltaX', 'flux', and 'pulse'. Task was to identify which columns represented the OHLCVP (Open, High, Low, Close, Volume, Price) financial metrics.

---

### The Dataset: First Impressions

The dataset consists of 500,000 rows of financial time series data. Most columns containnegative and positive values, except for `neutronCount`, which includes only large positive values ranging from 1,000 to 99,999. Much higher in scale than the other features (which range roughly from -211 to 286). The relatively consistent means and standard deviations across the remaining columns suggest that this is likely price-related financial data.

A key insight came from visualizing each column using a **Savitzky–Golay filter**. The filter was able to **smooth and perfectly approximate local patterns** using a **2nd-degree polynomial**, which strongly indicates **continuity in the data**. This observation confirms that:

* **The data is sequential in nature**, and
* **Time snapshots are in correct chronological order**, rather than being randomly shuffled.

This continuity is essential for any downstream time series modeling or forecasting tasks.

A key challenge was the absence of information about the time bar duration (e.g., hourly, daily, etc.).
Challenges Due to Missing Time Bar Duration:
- Unable to determine whether each data point represents an hour, day, or another interval
- Makes it difficult to assess the inherent noisiness of the data
- Prevents effective use of sliding window techniques for time series analysis


## The Investigation Process

### 1. Finding Volume Column

**Why neuronCount has to be Volume:**
- Always positive integers (assets cannot be fractional or negative)
- Significantly higher magnitude than other columns
- No decimal points
- Least correlated column to other columns when using `Pearson` and `Spearman` correlation matrices.
- Highest standard deviation implying unlikely for being an asset price indicator
- Confidence: 100%

### 2. Figuring out the High and Low columns

**The Logic:**
- High must be ≥ all other columns in the same time period (except price)
- Low must be ≤ all other columns in the same time period (except price)
    - This is because the relation for price is not explicitly stated, and may be outside [low, high].
    - This might also be due to the inherent noisiness in the data.
    - Used denoising on the data to smoothen the data using `Exponential Moving Window`

**The Method:**
1. For each column, count how often it's the maximum in its row
2. For each column, count how often it's the minimum in its row

deltaX >= omega for all rows
<br>gamma >= deltaX for all rows
<br>gamma >= omega for all rows
<br>gamma >= flux for all rows
<br>gamma >= pulse for all rows
<br>flux >= omega for all rows

`Most incoming column: ['omega'] with 3 incoming connections`
<br>`Most outgoing column: ['gamma'] with 4 outgoing connections`

Column deltaX is largest 0 times and smallest 0 times
<br>Column gamma is largest 500000 times and smallest 0 times
<br>Column omega is largest 0 times and smallest 499846 times
<br>Column flux is largest 0 times and smallest 0 times
<br>Column pulse is largest 0 times and smallest 154 times

**Gamma: high, confidence 100%**
<br>**Omega: low, confidence 99.97%**


### 3. Open vs Close vs Price

A major breakthrough was realizing that Price is likely a derived metric from the other columns.
To test this, we performed leave-one-out linear regression, predicting each column from the others and observing how the number of exact matches changed.


| Column Left Out   | Exact Matches | Change from Baseline  |
|-------------------|---------------|-----------------------|
| Baseline          | 28146         | +0                    |
| deltaX            | 27307         | -839                  |
| gamma             | 28141         | -5                    |
| omega             | 28138         | -8                    |
| flux              | 27276         | -870                  |
| neutronCount      | 28145         | -1                    |


The largest accuracy was when Pulse was left out, suggesting that **Pulse is the most likely candidate for price**.

---

We also brute-forced possible Open-Close column pairs using denoised data. By summing the error of `(previous close - current open)`:

* The lowest error occurred with **deltaX and flux**, at a shift of **7,200**.
* The next best combination had a significantly higher error (\~95,807),

This strongly supports that Open and Close values are encoded in deltaX and flux.


**Analysis Results:**
- Pulse: Price, confidence 99.97%
---

Here's a clean and concise rewrite of your section **with improved structure**, clarity, and formatting. I've preserved all the content and formatted the results into readable sub-sections and percentages, using bullet points and light explanation where needed.

---

### 4. Differentiating Open vs Close

We explored multiple strategies to determine which columns represent Open and Close prices, primarily between `deltaX` and `flux`.

#### **Approach 1: Sliding Window (Size 2)**

* Used simple momentum-based rules:

  * Let `o1`, `c1`, `o2`, `c2` be open and close values for consecutive entries.
  * If `o1 > c2`, then the trend is decreasing; in such cases, both opens should be greater than their respective closes, and vice versa.

**Results:**


| Mapping             | Match %   |
|---------------------|-----------|
| deltaX = Open       | 65.89%    |
| flux = Open         | 64.29%    |


---

#### **Approach 2: Trend Windows (Size 1000)**

* For sampled windows (length = 1000), we:

  * Computed `o1 - c1000` to capture long-range trend.
  * Compared it to prefix sum of `(Close - Open)` to validate the trend.

**Results:**

| Mapping             | Matches (out of 500) | Match %   |
|---------------------|----------------------|-----------|
| deltaX = Open       | 258                  | 51.6%     |
| flux = Open         | 242                  | 48.4%     |

---

####  **Approach 3: Momentum-Based Brute Force**

* For each row:

  * Checked whether **previous close** is closer to **current price** than **previous open**, as would typically be expected in trending data.

**Results:**


| Mapping             | Match %   |
|---------------------|-----------|
| deltaX = Open       | 49.82%    |
| flux = Open         | 50.18%    |


* This method **contradicts** earlier ones by weakly suggesting that **deltaX = Close**, but with **very low confidence (only 50.18%)**.

---


## Validation

Validation is based on basic OCLVH properties such as High being greater than every other metric (other than volume). Volume must be a positive integer. Low must be less than every other metric. 

## Confidence

1. For Volume, the confidence is 1.0 because the neutronCount satsified the constraint of large positive integer in every row.
2. For High, it was larger than all of OCLP data for every single row. So the confidence is 1.0
3. For Low, it was smaller than all of OCLP for mostrows. So, the confidence is 0.9997.
4. For Price, price can be the only one whose value doesn't fall between Low and High. So, as there is no information gain the confidence is minimum of high and low which is 0.9997.
5. Using the third technique described earlier to distinguish open and close, we get confidence of 0.5018 for both (as they are a pair)



