import streamlit as st
import pandas as pd

# --- App Header ---
st.title("🚀 StarCheck Demo")
st.write("Welcome! This is the first live version of StarCheck.")

# --- Simple Button Example ---
if st.button("Run Compliance Check"):
    st.success("✅ Compliance scan complete!")

# --- Demo Compliance Table ---
st.subheader("Compliance Risks (Demo Data)")
df = pd.DataFrame({
    "Clause": ["GDPR", "HIPAA", "SOC2"],
    "Risk": ["High", "Medium", "Low"]
})
st.table(df)
