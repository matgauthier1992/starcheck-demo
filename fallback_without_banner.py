import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import io

# --- Page setup ---
st.set_page_config(page_title="StarCheck Demo (Safe Mode)", layout="wide")

# --- Sidebar Upload ---
st.sidebar.header("Upload Engine Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

# --- Demo Data Fallback ---
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Data uploaded successfully")
else:
    st.sidebar.info("Using demo dataset (no file uploaded)")
    data = pd.DataFrame({
        "cycles": [10, 20, 30, 40, 50, 60, 70],
        "actual_rul": [95, 80, 65, 50, 40, 25, 10],
        "predicted_rul": [92, 78, 70, 52, 38, 28, 12],
    })

# --- Data Preview ---
with st.expander("🔎 Data Preview"):
    st.dataframe(data.head())

# --- Chart ---
st.subheader("Predicted vs Actual Remaining Useful Life (RUL)")
fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(data["cycles"], data["actual_rul"], label="Actual RUL", marker="o", color="#FF6B6B")
ax.plot(data["cycles"], data["predicted_rul"], label="Predicted RUL", marker="x", color="#4D96FF")
ax.set_xlabel("Engine Cycles")
ax.set_ylabel("Remaining Useful Life")
ax.set_title("StarCheck Engine Prediction Demo", fontsize=14, fontweight="bold")
ax.legend()
ax.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

# --- Download Report ---
buf = io.BytesIO()
fig.savefig(buf, format="png")
st.download_button(
    "📥 Download RUL Report",
    buf.getvalue(),
    "starcheck_rul_report.png",
    mime="image/png",
)
