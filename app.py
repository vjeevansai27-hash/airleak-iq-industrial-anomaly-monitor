# =============================================================================
# AirLeak IQ — Industrial Energy Anomaly Monitor
# app.py — Main Streamlit Application
#
# WHAT THIS APP DOES:
#   - Simulates pressure and energy sensor readings (like a virtual factory)
#   - Displays interactive charts of the readings
#   - Automatically flags "suspicious" readings using simple rules (thresholds)
#   - Shows you a table of normal vs anomalous readings
#   - Explains WHY a reading was flagged
#
# NOTE: All data here is SIMULATED for learning purposes only.
#       This is NOT real factory data, and NOT affiliated with any company.
# =============================================================================

import streamlit as st          # Streamlit: builds the web app UI
import pandas as pd              # Pandas: works with tables of data
import numpy as np               # NumPy: generates random numbers
import plotly.graph_objects as go  # Plotly: draws interactive charts
from datetime import datetime, timedelta  # For creating timestamps

# =============================================================================
# SECTION 1: PAGE CONFIGURATION
# This sets the browser tab title, icon, and layout before anything else.
# =============================================================================
st.set_page_config(
    page_title="AirLeak IQ — Energy Anomaly Monitor",
    page_icon="⚡",
    layout="wide",   # "wide" uses the full browser width
    initial_sidebar_state="expanded"
)

# =============================================================================
# SECTION 2: CUSTOM CSS (VISUAL STYLING)
# This injects CSS into the page to make it look modern and colorful.
# You don't need to understand every line — just know it controls colors/fonts.
# =============================================================================
st.markdown("""
<style>
/* Import Google Font 'Inter' for a clean, modern look */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Apply the font to the whole page */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Dark gradient background for the main app */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 40%, #0a1628 100%);
    color: #e2e8f0;
}

/* Style the sidebar */
.css-1d391kg, [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a2744 100%) !important;
    border-right: 1px solid rgba(99,179,237,0.2);
}

/* Custom metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(99,179,237,0.1), rgba(154,105,236,0.1));
    border: 1px solid rgba(99,179,237,0.3);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 30px rgba(99,179,237,0.2);
}
.metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #63b3ed, #9a69ec);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 4px;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* Anomaly alert box */
.anomaly-alert {
    background: linear-gradient(135deg, rgba(252,129,74,0.15), rgba(245,101,101,0.15));
    border: 1px solid rgba(245,101,101,0.5);
    border-left: 4px solid #fc814a;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* Normal reading box */
.normal-box {
    background: linear-gradient(135deg, rgba(72,187,120,0.1), rgba(56,178,172,0.1));
    border: 1px solid rgba(72,187,120,0.4);
    border-left: 4px solid #48bb78;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 8px 0;
}

/* Section header style */
.section-header {
    font-size: 1.4rem;
    font-weight: 700;
    color: #63b3ed;
    border-bottom: 2px solid rgba(99,179,237,0.3);
    padding-bottom: 8px;
    margin: 20px 0 16px 0;
}

/* Hero title styling */
.hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #63b3ed 0%, #9a69ec 50%, #fc814a 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 8px;
}
.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    margin-bottom: 28px;
}

/* Explanation box */
.explain-box {
    background: rgba(99,179,237,0.07);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 12px;
    padding: 16px 20px;
    font-size: 0.92rem;
    color: #cbd5e0;
    line-height: 1.7;
    margin: 12px 0;
}

/* Streamlit button overrides */
.stButton > button {
    background: linear-gradient(90deg, #4299e1, #9a69ec) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover {
    opacity: 0.85 !important;
}

/* Table styling */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SECTION 3: DATA SIMULATION FUNCTION
#
# This function creates FAKE (simulated) sensor readings.
# In a real factory, you would replace this with actual sensor API calls.
#
# HOW IT WORKS:
#   - We create timestamps every 15 minutes
#   - We generate random pressure and energy values using NumPy
#   - We intentionally inject a few "spike" anomalies so we can detect them
# =============================================================================
def generate_sensor_data(num_readings: int = 96, seed: int = None) -> pd.DataFrame:
    """
    Generate simulated industrial sensor readings.

    Parameters:
        num_readings : int  — how many sensor readings to create (default 96 = 1 day at 15-min intervals)
        seed         : int  — optional random seed for reproducibility

    Returns:
        pd.DataFrame — a table with timestamps, pressure, energy, and status columns
    """

    # If a seed is given, fix the random number generator so results are repeatable
    if seed is not None:
        np.random.seed(seed)

    # --- Create Timestamps ---
    # Start from 24 hours ago, add one timestamp every 15 minutes
    start_time = datetime.now() - timedelta(hours=num_readings * 0.25)
    timestamps = [start_time + timedelta(minutes=15 * i) for i in range(num_readings)]

    # --- Simulate Pressure Readings (in PSI — Pounds per Square Inch) ---
    # Normal factory pressure: around 80–100 PSI
    # We use np.random.normal(mean, std_dev, count) for realistic variation
    pressure = np.random.normal(loc=90.0, scale=5.0, size=num_readings)

    # Simulate "shift changes" — slight pressure dips during shift handover
    # Every 32 readings ≈ every 8 hours (3 shifts/day)
    for i in range(0, num_readings, 32):
        if i + 4 < num_readings:
            pressure[i:i+4] -= np.random.uniform(5, 12, 4)  # small dip

    # --- Simulate Energy Consumption (in kWh — kilowatt-hours) ---
    # Normal energy: around 45–55 kWh per 15-minute slot
    energy = np.random.normal(loc=50.0, scale=4.0, size=num_readings)

    # Energy typically correlates with pressure — if pressure drops, energy may spike
    # (machines work harder to maintain pressure when there's a leak)
    energy = energy + (90.0 - pressure) * 0.3

    # --- Inject Artificial Anomalies ---
    # We randomly pick a few indices and create "spikes" in pressure/energy
    # This simulates what a real air leak or equipment fault might look like
    num_anomalies = max(3, num_readings // 20)   # about 5% of readings are anomalous
    anomaly_indices = np.random.choice(num_readings, size=num_anomalies, replace=False)

    for idx in anomaly_indices:
        anomaly_type = np.random.choice(["pressure_drop", "pressure_spike", "energy_spike"])
        if anomaly_type == "pressure_drop":
            pressure[idx] -= np.random.uniform(18, 30)  # sudden pressure drop (air leak!)
        elif anomaly_type == "pressure_spike":
            pressure[idx] += np.random.uniform(18, 28)  # sudden pressure surge
        else:
            energy[idx] += np.random.uniform(20, 40)    # energy consumption spike

    # --- Clip values to realistic bounds ---
    # Even with noise, values should stay within plausible industrial ranges
    pressure = np.clip(pressure, 40.0, 140.0)   # PSI between 40 and 140
    energy   = np.clip(energy,   20.0, 120.0)   # kWh between 20 and 120

    # --- Build a DataFrame (a structured table) ---
    df = pd.DataFrame({
        "timestamp":       timestamps,
        "pressure_psi":    np.round(pressure, 2),
        "energy_kwh":      np.round(energy, 2),
    })

    return df


# =============================================================================
# SECTION 4: ANOMALY DETECTION FUNCTION
#
# THRESHOLD-BASED ANOMALY DETECTION — the simplest and most transparent method.
#
# HOW IT WORKS:
#   - We calculate the MEAN (average) and STANDARD DEVIATION (spread) of each sensor
#   - A reading is flagged as anomalous if it goes too far from the average
#   - "Too far" = more than (threshold_multiplier × std_dev) away from the mean
#   - This is called the "Z-score" method in simple form
#
# EXAMPLE: If average pressure is 90 PSI and std dev is 5 PSI,
#          and threshold is 2.5 × std dev = 12.5 PSI,
#          then anything below 77.5 or above 102.5 PSI is flagged.
# =============================================================================
def detect_anomalies(df: pd.DataFrame, threshold_multiplier: float = 2.5) -> pd.DataFrame:
    """
    Flag anomalous sensor readings using a threshold-based rule.

    Parameters:
        df                   : pd.DataFrame  — sensor data table
        threshold_multiplier : float         — how many std deviations = "anomalous" (default 2.5)

    Returns:
        pd.DataFrame — same table with added columns for anomaly flag and reason
    """

    df = df.copy()   # Work on a copy so we don't modify the original

    # --- Calculate statistics for Pressure ---
    p_mean  = df["pressure_psi"].mean()    # average pressure
    p_std   = df["pressure_psi"].std()     # standard deviation of pressure
    p_upper = p_mean + threshold_multiplier * p_std   # upper limit
    p_lower = p_mean - threshold_multiplier * p_std   # lower limit

    # --- Calculate statistics for Energy ---
    e_mean  = df["energy_kwh"].mean()
    e_std   = df["energy_kwh"].std()
    e_upper = e_mean + threshold_multiplier * e_std
    e_lower = e_mean - threshold_multiplier * e_std

    # --- Create boolean (True/False) flags for each condition ---
    pressure_high = df["pressure_psi"] > p_upper
    pressure_low  = df["pressure_psi"] < p_lower
    energy_high   = df["energy_kwh"]   > e_upper
    energy_low    = df["energy_kwh"]   < e_lower

    # Combine: a reading is anomalous if ANY sensor is out of range
    is_anomaly = pressure_high | pressure_low | energy_high | energy_low

    # --- Build a human-readable reason for each flagged reading ---
    def build_reason(row):
        """Return a short text explaining WHY this reading was flagged."""
        reasons = []
        if row["pressure_psi"] > p_upper:
            reasons.append(f"Pressure too HIGH ({row['pressure_psi']:.1f} PSI > {p_upper:.1f} limit)")
        if row["pressure_psi"] < p_lower:
            reasons.append(f"Pressure too LOW ({row['pressure_psi']:.1f} PSI < {p_lower:.1f} limit) — possible air leak!")
        if row["energy_kwh"] > e_upper:
            reasons.append(f"Energy too HIGH ({row['energy_kwh']:.1f} kWh > {e_upper:.1f} limit)")
        if row["energy_kwh"] < e_lower:
            reasons.append(f"Energy too LOW ({row['energy_kwh']:.1f} kWh < {e_lower:.1f} limit)")
        return " | ".join(reasons) if reasons else "Normal"

    # Apply the function to every row in the table
    df["is_anomaly"] = is_anomaly
    df["status"]     = df["is_anomaly"].map({True: "🔴 Anomaly", False: "🟢 Normal"})
    df["reason"]     = df.apply(build_reason, axis=1)

    # Store the computed limits in the dataframe's metadata (useful for the UI)
    df.attrs["p_mean"]  = p_mean
    df.attrs["p_std"]   = p_std
    df.attrs["p_upper"] = p_upper
    df.attrs["p_lower"] = p_lower
    df.attrs["e_mean"]  = e_mean
    df.attrs["e_std"]   = e_std
    df.attrs["e_upper"] = e_upper
    df.attrs["e_lower"] = e_lower

    return df


# =============================================================================
# SECTION 5: CHART DRAWING FUNCTIONS
#
# Plotly is used here for interactive charts (hover to see values, zoom, pan).
# Each chart shows the readings over time and marks anomalies in red/orange.
# =============================================================================
def make_pressure_chart(df: pd.DataFrame) -> go.Figure:
    """Create an interactive pressure-over-time line chart."""

    normal  = df[~df["is_anomaly"]]   # rows where is_anomaly is False
    anomaly = df[df["is_anomaly"]]    # rows where is_anomaly is True

    fig = go.Figure()

    # --- Draw the threshold bands (safe zone shading) ---
    p_upper = df.attrs.get("p_upper", 110)
    p_lower = df.attrs.get("p_lower", 70)

    fig.add_hrect(
        y0=p_lower, y1=p_upper,
        fillcolor="rgba(72,187,120,0.06)",
        line_width=0,
        annotation_text="Safe Zone",
        annotation_font_color="#48bb78",
        annotation_position="top left"
    )

    # Upper limit dashed line
    fig.add_hline(y=p_upper, line_dash="dot", line_color="rgba(245,101,101,0.5)",
                  annotation_text=f"Upper limit ({p_upper:.1f} PSI)",
                  annotation_font_color="#f56565")
    # Lower limit dashed line
    fig.add_hline(y=p_lower, line_dash="dot", line_color="rgba(245,101,101,0.5)",
                  annotation_text=f"Lower limit ({p_lower:.1f} PSI)",
                  annotation_font_color="#f56565",
                  annotation_position="bottom right")

    # --- Normal readings: blue line ---
    fig.add_trace(go.Scatter(
        x=df["timestamp"], y=df["pressure_psi"],
        mode="lines",
        name="Pressure",
        line=dict(color="#63b3ed", width=1.8),
        hovertemplate="<b>%{x|%H:%M}</b><br>Pressure: %{y:.1f} PSI<extra></extra>"
    ))

    # --- Anomaly points: red markers ---
    if not anomaly.empty:
        fig.add_trace(go.Scatter(
            x=anomaly["timestamp"], y=anomaly["pressure_psi"],
            mode="markers",
            name="⚠️ Anomaly",
            marker=dict(color="#fc8181", size=10, symbol="circle-open",
                        line=dict(color="#fc8181", width=2)),
            hovertemplate="<b>⚠️ ANOMALY</b><br>%{x|%H:%M}<br>Pressure: %{y:.1f} PSI<extra></extra>"
        ))

    # Chart layout settings (dark background, axis labels, etc.)
    fig.update_layout(
        title=dict(text="🔵 Pressure Readings (PSI) Over Time", font=dict(color="#63b3ed", size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,27,42,0.7)",
        font=dict(color="#e2e8f0", family="Inter"),
        xaxis=dict(
            title="Time", gridcolor="rgba(255,255,255,0.05)",
            color="#94a3b8", showline=True, linecolor="rgba(255,255,255,0.1)"
        ),
        yaxis=dict(
            title="Pressure (PSI)", gridcolor="rgba(255,255,255,0.05)",
            color="#94a3b8", showline=True, linecolor="rgba(255,255,255,0.1)"
        ),
        legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def make_energy_chart(df: pd.DataFrame) -> go.Figure:
    """Create an interactive energy consumption bar chart."""

    e_upper = df.attrs.get("e_upper", 65)
    e_lower = df.attrs.get("e_lower", 35)

    # Color each bar: orange if anomaly, blue-teal if normal
    bar_colors = df["is_anomaly"].map({True: "#fc8181", False: "#4fd1c5"})

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df["timestamp"],
        y=df["energy_kwh"],
        name="Energy",
        marker_color=bar_colors,
        hovertemplate="<b>%{x|%H:%M}</b><br>Energy: %{y:.1f} kWh<extra></extra>"
    ))

    # Upper limit line
    fig.add_hline(y=e_upper, line_dash="dot", line_color="rgba(245,101,101,0.6)",
                  annotation_text=f"Upper limit ({e_upper:.1f} kWh)",
                  annotation_font_color="#f56565")

    fig.update_layout(
        title=dict(text="⚡ Energy Consumption (kWh) Over Time", font=dict(color="#4fd1c5", size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,27,42,0.7)",
        font=dict(color="#e2e8f0", family="Inter"),
        xaxis=dict(title="Time", gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
        yaxis=dict(title="Energy (kWh)", gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
        bargap=0.1,
        hovermode="x unified",
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


def make_scatter_chart(df: pd.DataFrame) -> go.Figure:
    """
    Scatter plot: Pressure (x-axis) vs Energy (y-axis).
    This helps visualize the RELATIONSHIP between the two sensors.
    If a point is far from the cluster, it's likely an anomaly.
    """
    normal  = df[~df["is_anomaly"]]
    anomaly = df[df["is_anomaly"]]

    fig = go.Figure()

    # Normal points in teal
    fig.add_trace(go.Scatter(
        x=normal["pressure_psi"], y=normal["energy_kwh"],
        mode="markers",
        name="🟢 Normal",
        marker=dict(color="#4fd1c5", size=7, opacity=0.7),
        hovertemplate="Pressure: %{x:.1f} PSI<br>Energy: %{y:.1f} kWh<extra></extra>"
    ))

    # Anomaly points in red
    if not anomaly.empty:
        fig.add_trace(go.Scatter(
            x=anomaly["pressure_psi"], y=anomaly["energy_kwh"],
            mode="markers",
            name="🔴 Anomaly",
            marker=dict(color="#fc8181", size=12, symbol="x",
                        line=dict(color="#fc8181", width=2)),
            hovertemplate="<b>⚠️ ANOMALY</b><br>Pressure: %{x:.1f} PSI<br>Energy: %{y:.1f} kWh<extra></extra>"
        ))

    fig.update_layout(
        title=dict(text="🔍 Pressure vs Energy (anomalies appear as outliers)", font=dict(color="#9a69ec", size=16)),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,27,42,0.7)",
        font=dict(color="#e2e8f0", family="Inter"),
        xaxis=dict(title="Pressure (PSI)", gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
        yaxis=dict(title="Energy (kWh)", gridcolor="rgba(255,255,255,0.05)", color="#94a3b8"),
        margin=dict(l=10, r=10, t=50, b=10)
    )

    return fig


# =============================================================================
# SECTION 6: SESSION STATE MANAGEMENT
#
# Streamlit reruns the entire script every time the user clicks a button.
# st.session_state is a dictionary that PERSISTS between reruns.
# We use it to store the current dataset so it doesn't change on every rerun.
# =============================================================================
if "df" not in st.session_state:
    # First load: generate data with a fixed seed so the first view is consistent
    raw_df              = generate_sensor_data(num_readings=96, seed=42)
    st.session_state.df = detect_anomalies(raw_df, threshold_multiplier=2.5)
    st.session_state.seed = 42


# =============================================================================
# SECTION 7: SIDEBAR (Settings & Info Panel)
# =============================================================================
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")

    # Slider: how many readings to generate
    num_readings = st.slider(
        "📊 Number of Readings",
        min_value=48,
        max_value=192,
        value=96,
        step=12,
        help="96 readings = 1 day at 15-min intervals"
    )

    # Slider: how sensitive the anomaly detector is
    threshold = st.slider(
        "🎯 Anomaly Sensitivity",
        min_value=1.5,
        max_value=3.5,
        value=2.5,
        step=0.1,
        format="%.1f σ",
        help="Lower = more sensitive (flags more readings). Higher = less sensitive."
    )

    st.markdown("---")

    # Button: generate a NEW random dataset
    if st.button("🔄 Generate Fresh Data", key="refresh_btn"):
        new_seed            = np.random.randint(0, 9999)   # random seed every click
        raw_df              = generate_sensor_data(num_readings=num_readings, seed=new_seed)
        st.session_state.df = detect_anomalies(raw_df, threshold_multiplier=threshold)
        st.session_state.seed = new_seed
        st.success(f"✅ New dataset generated! (seed={new_seed})")

    # Button: save current data to CSV
    csv_data = st.session_state.df.to_csv(index=False)
    st.download_button(
        label="💾 Download Data as CSV",
        data=csv_data,
        file_name="airleak_sensor_data.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Info box about the app
    st.markdown("""
    <div class="explain-box">
    <b>📖 How Anomaly Detection Works</b><br><br>
    We compute the <b>mean (μ)</b> and <b>standard deviation (σ)</b> of each sensor.<br><br>
    Any reading beyond <b>μ ± (threshold × σ)</b> is flagged as an anomaly.<br><br>
    This is called <b>Z-score thresholding</b> — a standard technique in industrial monitoring.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("⚠️ All data is simulated for educational purposes. Not affiliated with any company.")


# =============================================================================
# SECTION 8: MAIN PAGE CONTENT
# =============================================================================

# --- Hero Header ---
st.markdown("""
<div style="text-align:center; padding: 10px 0 5px 0;">
    <div class="hero-title">⚡ AirLeak IQ</div>
    <div class="hero-subtitle">Industrial Energy Anomaly Monitor — Simulated Sensor Dashboard</div>
</div>
""", unsafe_allow_html=True)

# Retrieve current data from session state
df = st.session_state.df

# --- Summary Metrics Row ---
total      = len(df)
anomalies  = df["is_anomaly"].sum()
normal_cnt = total - anomalies
anomaly_pct = (anomalies / total * 100) if total > 0 else 0
avg_pressure = df["pressure_psi"].mean()
avg_energy   = df["energy_kwh"].mean()

# Display 5 metric cards in a row (using Streamlit columns)
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total}</div>
        <div class="metric-label">Total Readings</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="background:linear-gradient(90deg,#48bb78,#38b2ac);-webkit-background-clip:text;background-clip:text;">
            {normal_cnt}</div>
        <div class="metric-label">Normal Readings</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value" style="background:linear-gradient(90deg,#fc814a,#f56565);-webkit-background-clip:text;background-clip:text;">
            {anomalies}</div>
        <div class="metric-label">Anomalies Detected</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_pressure:.1f} <span style="font-size:1rem;font-weight:400;">PSI</span></div>
        <div class="metric-label">Avg Pressure</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{avg_energy:.1f} <span style="font-size:1rem;font-weight:400;">kWh</span></div>
        <div class="metric-label">Avg Energy</div>
    </div>""", unsafe_allow_html=True)


# --- Alert Banner (if anomalies found) ---
if anomalies > 0:
    st.markdown(f"""
    <div class="anomaly-alert">
        ⚠️ <b>{anomalies} anomalous readings detected</b> ({anomaly_pct:.1f}% of total).
        Scroll down to see flagged readings with explanations.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="normal-box">
        ✅ <b>All readings are within normal range.</b> No anomalies detected.
    </div>""", unsafe_allow_html=True)


# =============================================================================
# SECTION 9: CHARTS
# =============================================================================
st.markdown('<div class="section-header">📈 Sensor Charts</div>', unsafe_allow_html=True)

# Explanation box before charts
st.markdown("""
<div class="explain-box">
<b>📖 Reading the Charts:</b><br>
• <b>Blue line</b> = pressure over time. <b>Red circles</b> = anomalous pressure readings.<br>
• <b>Teal bars</b> = energy consumption per 15-min slot. <b>Red bars</b> = energy anomalies.<br>
• <b>Dashed red lines</b> mark the safe-zone boundaries. Anything outside them is flagged.<br>
• Use your mouse to <b>hover, zoom, and pan</b> the charts.
</div>
""", unsafe_allow_html=True)

# Two charts side-by-side
col_left, col_right = st.columns(2)
with col_left:
    st.plotly_chart(make_pressure_chart(df), use_container_width=True, key="pressure_chart")
with col_right:
    st.plotly_chart(make_energy_chart(df), use_container_width=True, key="energy_chart")

# Scatter chart below (full width)
st.plotly_chart(make_scatter_chart(df), use_container_width=True, key="scatter_chart")


# =============================================================================
# SECTION 10: ANOMALY DETAILS TABLE
# =============================================================================
st.markdown('<div class="section-header">🔍 Anomaly Details</div>', unsafe_allow_html=True)

anomaly_df = df[df["is_anomaly"]].copy()

if anomaly_df.empty:
    st.markdown('<div class="normal-box">✅ No anomalies found in this dataset.</div>', unsafe_allow_html=True)
else:
    # Show each anomaly as an expandable card with explanation
    for _, row in anomaly_df.iterrows():
        time_str = row["timestamp"].strftime("%Y-%m-%d %H:%M")
        with st.expander(f"⚠️ {time_str}  |  Pressure: {row['pressure_psi']:.1f} PSI  |  Energy: {row['energy_kwh']:.1f} kWh"):
            st.markdown(f"""
            <div class="anomaly-alert">
                <b>🕐 Time:</b> {time_str}<br>
                <b>🔵 Pressure:</b> {row['pressure_psi']:.2f} PSI
                &nbsp;(normal range: {df.attrs['p_lower']:.1f} – {df.attrs['p_upper']:.1f} PSI)<br>
                <b>⚡ Energy:</b> {row['energy_kwh']:.2f} kWh
                &nbsp;(normal range: {df.attrs['e_lower']:.1f} – {df.attrs['e_upper']:.1f} kWh)<br>
                <b>📋 Reason:</b> {row['reason']}
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# SECTION 11: FULL DATA TABLE
# =============================================================================
st.markdown('<div class="section-header">📋 Full Readings Table</div>', unsafe_allow_html=True)

# Filter controls
col_f1, col_f2 = st.columns([1, 3])
with col_f1:
    filter_choice = st.selectbox(
        "Show:",
        ["All Readings", "🟢 Normal Only", "🔴 Anomalies Only"],
        key="filter_select"
    )

# Apply the chosen filter
if filter_choice == "🟢 Normal Only":
    display_df = df[~df["is_anomaly"]]
elif filter_choice == "🔴 Anomalies Only":
    display_df = df[df["is_anomaly"]]
else:
    display_df = df

# Prepare the display table (rename columns to be more human-friendly)
show_cols = display_df[["timestamp", "pressure_psi", "energy_kwh", "status", "reason"]].copy()
show_cols.columns = ["Timestamp", "Pressure (PSI)", "Energy (kWh)", "Status", "Reason"]
show_cols["Timestamp"] = show_cols["Timestamp"].dt.strftime("%Y-%m-%d %H:%M")

st.dataframe(
    show_cols,
    use_container_width=True,
    height=350,
    hide_index=True
)


# =============================================================================
# SECTION 12: BEGINNER EXPLANATION BOX
# Educates the student on how the detection logic works.
# =============================================================================
st.markdown('<div class="section-header">📚 How It Works — For Beginners</div>', unsafe_allow_html=True)

p_upper = df.attrs['p_upper']
p_lower = df.attrs['p_lower']
e_upper = df.attrs['e_upper']
e_lower = df.attrs['e_lower']
p_mean  = df.attrs['p_mean']
p_std   = df.attrs['p_std']
e_mean  = df.attrs['e_mean']
e_std   = df.attrs['e_std']

st.markdown(f"""
<div class="explain-box">
<b>🧮 Current Anomaly Thresholds (based on this dataset):</b><br><br>

<b>Pressure (PSI):</b><br>
&nbsp;&nbsp;• Mean = <b>{p_mean:.2f} PSI</b>, Std Dev = <b>{p_std:.2f} PSI</b><br>
&nbsp;&nbsp;• Safe zone: <b>{p_lower:.2f}</b> to <b>{p_upper:.2f} PSI</b><br>
&nbsp;&nbsp;• Formula: {p_mean:.2f} ± ({threshold:.1f} × {p_std:.2f})<br><br>

<b>Energy (kWh):</b><br>
&nbsp;&nbsp;• Mean = <b>{e_mean:.2f} kWh</b>, Std Dev = <b>{e_std:.2f} kWh</b><br>
&nbsp;&nbsp;• Safe zone: <b>{e_lower:.2f}</b> to <b>{e_upper:.2f} kWh</b><br>
&nbsp;&nbsp;• Formula: {e_mean:.2f} ± ({threshold:.1f} × {e_std:.2f})<br><br>

<b>💡 Key Concept — Standard Deviation (σ):</b><br>
Standard deviation tells you how "spread out" your data is. If most readings are close
to the mean, the std dev is small. The threshold rule says: if a reading is more than
{threshold:.1f} standard deviations away from the mean, it's unusual enough to flag.

<br><br><b>🔧 What could cause real anomalies?</b><br>
• <b>Pressure drop</b> → possible air leak in the pneumatic line<br>
• <b>Pressure spike</b> → blockage or valve failure<br>
• <b>Energy spike</b> → compressor working overtime to compensate for a leak<br>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align:center; margin-top:40px; padding:20px; color:#4a5568; font-size:0.8rem; border-top:1px solid rgba(255,255,255,0.05);">
    ⚡ AirLeak IQ — Built for learning purposes only &nbsp;|&nbsp;
    All sensor data is <b>simulated</b> and does not represent any real factory or company.
</div>
""", unsafe_allow_html=True)
