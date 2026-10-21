# AirLeak IQ — Industrial Energy Anomaly Monitor

> **Educational & Research Prototype**  
> Developed as a BTech Computer Science & Engineering (AI/ML) student project exploring statistical anomaly detection on simulated industrial time-series data.

---

## 📌 Disclaimer
**SIMULATED DATA ONLY**: All sensor signals, timestamps, pressure levels, and energy consumption metrics utilized in this application are synthetically generated for demonstration and educational purposes.  
**NO AFFILIATION**: This project is an independent academic learning artifact. It is **NOT** an official, sponsored, or affiliated project of DRDO, Samsung, ISRO, IIT, NIT, Renault, Nissan, Apollo Tyres, or any other industrial or governmental entity. It must not be deployed for mission-critical industrial process control or life-safety applications.

---

## 🏭 Problem Statement
In modern manufacturing facilities, compressed air systems account for up to **20% to 30% of total electrical energy consumption**. Pneumatic distribution networks frequently suffer from:
- Undetected pipe leaks and joint degradations.
- Valve sticking or pressure line blockages.
- Motor/compressor overdrive, where machines consume excess power attempting to compensate for systemic pressure drops.

Traditional manual inspections using ultrasonic detectors or soap-bubble tests are periodic, labor-intensive, and reactive. A data-driven monitoring solution is needed to continuously analyze line pressure and power draw, flag deviations in real time, and explain the root cause in accessible terms without requiring proprietary hardware or expensive software licenses.

---

## 🎯 Objectives
1. **Simulate Realistic Telemetry**: Generate multi-sensor time-series streams (pneumatic pressure in PSI and electrical power consumption in kWh) with natural noise, operational shift dips, and injected anomaly patterns.
2. **Implement Explainable Anomaly Detection**: Apply an interpretable statistical thresholding rule based on sample mean and standard deviation ($Z$-score principles) rather than opaque black-box models.
3. **Interactive Visual Dashboard**: Provide operators with synchronized time-series charts, threshold boundary overlays, correlation scatter plots, and summary KPI metrics.
4. **Transparent Diagnosis**: Output human-readable natural language diagnostic explanations for every flagged sensor reading.
5. **No External Overhead**: Deliver a completely self-contained web application using open-source Python, Pandas, and Streamlit with zero external hardware or paid API dependencies.

---

## 💻 Technologies Used
| Component | Technology | Version | Purpose |
|---|---|---|---|
| **Language** | Python | 3.11+ | Core logic and mathematical computations |
| **Web Framework** | Streamlit | 1.40.1 | Interactive web dashboard and user controls |
| **Data Manipulation** | Pandas | 2.2.3 | Tabular data structures and time-series indexing |
| **Numerical Processing** | NumPy | 2.4.6 | Vectorized random generation and statistical calculations |
| **Data Visualization** | Plotly | 5.24.1 | Interactive, hardware-accelerated time-series and scatter plots |
| **Data Serialization** | PyArrow | 26.0.0 | High-performance columnar memory backend for Streamlit dataframes |

---

## 🔬 Methodology
The system architecture follows an end-to-end data pipeline:

```
┌─────────────────────────────────┐
│     Synthetic Sensor Engine     │
│  - Pressure: N(μ=90, σ=5) PSI   │
│  - Shift Dips & Compressor Work │
│  - Injected Air Leaks & Spikes  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│   Statistical Anomaly Engine    │
│  - Compute Sample Mean (μ)      │
│  - Compute Std Deviation (σ)    │
│  - Evaluate Upper & Lower Bands │
│  - Generate Diagnostic Reasons  │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Interactive Streamlit UI     │
│  - KPI Metric Cards (5 Cards)   │
│  - Dual Time-Series Charts      │
│  - Pressure vs Energy Scatter   │
│  - Filterable Anomaly Dataframe │
│  - CSV Export Engine            │
└─────────────────────────────────┘
```

1. **Synthetic Telemetry Generation**:
   - Generates timestamps at uniform 15-minute intervals.
   - Computes baseline pneumatic pressure with Gaussian noise $\mathcal{N}(90, 5^2)$.
   - Simulates physical compressor coupling: energy consumption increases when line pressure drops ($E_{\text{load}} \propto 90 - P$).
   - Injects realistic industrial fault scenarios (abrupt pressure drops simulating leaks, pressure surges, and compressor over-draws).
2. **Statistical Filtering**:
   - Computes instantaneous statistical moments across the active sample window.
   - Classifies readings exceeding dynamic deviation limits as anomalous.
   - Assigns a detailed explanatory flag indicating which sensor violated bounds and by how much.
3. **Interactive Visualization & Export**:
   - Renders charts with visual safe-zone bands and distinct outlier glyphs.
   - Allows parameter tuning (sample count and sensitivity multipliers) on the fly.

---

## 🧮 Anomaly Detection Algorithm

The detector implements a parametric **Standard Deviation / $Z$-Score Threshold Rule**.

### 1. Statistical Equations
For a given sensor series $X = \{x_1, x_2, \dots, x_N\}$ (e.g., Pressure or Energy):

- **Sample Mean ($\mu$)**:
  $$\mu = \frac{1}{N} \sum_{i=1}^{N} x_i$$

- **Sample Standard Deviation ($\sigma$)**:
  $$\sigma = \sqrt{\frac{1}{N - 1} \sum_{i=1}^{N} (x_i - \mu)^2}$$

- **Dynamic Operating Envelope**:
  Given a user-selected sensitivity multiplier $k$ (default $k = 2.5\sigma$):
  $$\text{Upper Limit } (T_{\text{upper}}) = \mu + k \cdot \sigma$$
  $$\text{Lower Limit } (T_{\text{lower}}) = \mu - k \cdot \sigma$$

### 2. Decision Logic
For each reading $(p_i, e_i)$ at timestamp $t_i$:
$$\text{Anomaly Flag } A_i = 
\begin{cases} 
1 & \text{if } p_i > T_{\text{upper}}^{(P)} \lor p_i < T_{\text{lower}}^{(P)} \lor e_i > T_{\text{upper}}^{(E)} \lor e_i < T_{\text{lower}}^{(E)} \\
0 & \text{otherwise}
\end{cases}$$

### 3. Root Cause Classification
- **Pneumatic Leak**: $p_i < T_{\text{lower}}^{(P)}$ (Pneumatic line pressure drops drastically; high likelihood of orifice rupture).
- **Line Surge / Blockage**: $p_i > T_{\text{upper}}^{(P)}$ (Downstream valve closure or regulator failure).
- **Compressor Overload**: $e_i > T_{\text{upper}}^{(E)}$ (Electrical demand exceeds standard operation limits).

---

## ✨ Features
- **Simulated Industrial Telemetry**: Realistic baseline variations, shift handovers, and physical coupling between pressure and energy.
- **Dynamic Parameter Tuning**: Live sidebar sliders to adjust dataset length (48 to 192 observations) and sensitivity multiplier ($1.5\sigma$ to $3.5\sigma$).
- **One-Click Regenerator**: "🔄 Generate Fresh Data" button instantiates a new stochastic dataset with a random seed.
- **5 High-Level KPI Metric Cards**: Real-time summary of Total Readings, Normal Readings, Anomalies Detected, Average Pressure, and Average Energy.
- **Interactive Plotly Visualizations**:
  - Pressure Line Chart with green safe-band shading and red anomaly markers.
  - Energy Bar Chart with dynamic color coding.
  - Pressure vs Energy 2D Scatter Plot highlighting multivariate outliers.
- **Deep Anomaly Diagnostic Cards**: Collapsible detail views showing exact timestamp, sensor values, active limits, and natural-language explanations.
- **Filterable Data Table**: Toggle between "All Readings", "🟢 Normal Only", and "🔴 Anomalies Only".
- **CSV Data Export**: Download current simulated telemetry directly to disk.

---

## 🧪 Testing Results

Unit and integration tests were executed directly in the project environment:

| Test Case | Scope | Method | Result | Notes |
|---|---|---|---|---|
| **TC-01** | Data Simulation | `generate_sensor_data(96, seed=42)` | **PASSED** | Correct shape $(96, 3)$, bounded within realistic limits (40–140 PSI, 20–120 kWh). |
| **TC-02** | Anomaly Engine | `detect_anomalies(df, 2.5)` | **PASSED** | 4 anomalies flagged with correct boolean flags and non-null diagnostic reason strings. |
| **TC-03** | Visualization Engine | `make_pressure_chart`, `make_energy_chart`, `make_scatter_chart` | **PASSED** | All figures initialized with valid Plotly JSON structures and annotation coordinates. |
| **TC-04** | Backend Serialization | `pyarrow.Table.from_pandas(df)` | **PASSED** | Fixed PyArrow/NumPy 2.x compatibility; table serialization executed without warnings. |
| **TC-05** | Web Server Execution | `streamlit run app.py --server.headless true --server.port 8501` | **PASSED** | Server started, bound to port 8501, and returned HTTP 200 `ok` on `/_stcore/health`. |

---

## ⚠️ Limitations
1. **Synthetic Telemetry**: Readings are generated using pseudorandom distributions rather than physical piezoelectric or RTD industrial sensors.
2. **Univariate Thresholding**: While pressure and energy are coupled in generation, the detection algorithm applies independent boundary conditions rather than full multivariate covariance modeling (e.g., Mahalanobis distance or Isolation Forests).
3. **Batch Window Context**: Baseline statistics ($\mu$ and $\sigma$) are computed across the active batch window rather than via streaming exponential moving averages (EMA).
4. **Static Factory Configuration**: Does not model multi-compressor staging cascades or variable-frequency drive (VFD) modulating states.

---

## 🚀 Future Scope
- **Advanced Machine Learning**: Implement unsupervised learning models (Isolation Forests, One-Class SVM, and Autoencoders) for complex multivariate anomaly detection.
- **Streaming Pipeline**: Integrate MQTT / OPC-UA protocol listeners to ingest live telemetry from Modbus PLCs or edge gateways.
- **Real-Time Edge Deployment**: Containerize the pipeline using Docker and test on embedded edge hardware (Raspberry Pi, NVIDIA Jetson).
- **Automated Alerting**: Add Webhook and email dispatching via alert handlers when anomalies persist over consecutive reading cycles.

---

## 🛠️ How to Run (Windows PowerShell)

### Step 1: Open PowerShell and Navigate to the Directory
```powershell
cd "C:\Users\jeevan official\.gemini\antigravity-ide\scratch\airleak-iq"
```

### Step 2: Set Up Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
*(If you encounter an execution policy warning in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Application
```powershell
streamlit run app.py
```

Streamlit will launch and print your local URL:
```text
  Local URL: http://localhost:8501
```
Open **`http://localhost:8501`** in any modern web browser (Chrome, Edge, Firefox).

---

## 📄 License
This project is open-source under the MIT License for educational and learning purposes.
