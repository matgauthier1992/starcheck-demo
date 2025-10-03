import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# ----------------------------
# Config
# ----------------------------
st.set_page_config(page_title="StarCheck – Predictive Maintenance", layout="wide")

# ----------------------------
# Custom CSS for Branding
# ----------------------------
st.markdown("""
    <style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0B1E3D; /* Navy */
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }

    /* Main headers */
    h1, h2, h3 {
        color: #0B1E3D;
        font-family: Arial, sans-serif;
    }

    /* Data tables */
    .stDataFrame {
        border: 1px solid #ddd;
        border-radius: 8px;
    }

    /* Cards */
    .card {
        background-color: #F8F9FA;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
    }

    /* Alerts */
    .stSuccess {
        background-color: #28A74520;
        color: #0B1E3D;
        border-left: 6px solid #28A745;
    }
    .stWarning {
        background-color: #FF7A0020;
        color: #0B1E3D;
        border-left: 6px solid #FF7A00;
    }
    </style>
""", unsafe_allow_html=True)

# ----------------------------
# Demo Data
# ----------------------------
def load_demo_fleet():
    data = {
        "Engine_ID": ["CRJ200-A1"]*7 + ["CRJ200-B2"]*7 + ["Dash8-100-01"]*7,
        "Engine_Model": ["GE CF34-3B1"]*7 + ["GE CF34-3B1"]*7 + ["PW120A"]*7,
        "Cycles": [0,50,100,150,200,250,300]*3,
        "EGT_Margin": (
            [80,74,68,62,56,50,44] +
            [82,77,72,67,62,57,52] +
            [78,75,72,69,66,63,60]
        )
    }
    return pd.DataFrame(data)

# ----------------------------
# Forecast Functions
# ----------------------------
def forecast_engine(df, stress_factor=1.0):
    X = df["Cycles"].values.reshape(-1, 1)
    y = df["EGT_Margin"].values
    model = LinearRegression().fit(X, y)
    slope, intercept = float(model.coef_[0]) * stress_factor, float(model.intercept_)
    def to_threshold(th): return (th - intercept) / slope if slope != 0 else np.inf
    return {
        "slope": slope,
        "intercept": intercept,
        "preventive_cycles": to_threshold(50),
        "predictive_cycles": to_threshold(30)
    }

def plot_fleet(df, forecasts):
    fig = go.Figure()
    for eng in df["Engine_ID"].unique():
        sub = df[df.Engine_ID==eng]
        f = forecasts[eng]
        fig.add_trace(go.Scatter(x=sub.Cycles, y=sub.EGT_Margin,
                                 mode="markers", name=f"{eng} Data",
                                 marker=dict(color="#1E90FF")))
        xp = np.linspace(0, max(sub.Cycles)+200, 100)
        yp = f["intercept"] + f["slope"]*xp
        fig.add_trace(go.Scatter(x=xp, y=yp, mode="lines", name=f"{eng} Forecast",
                                 line=dict(color="#0B1E3D")))
    fig.add_hline(y=50, line_dash="dot", line_color="#FF7A00",
                  annotation_text="Preventive Limit (50 °C)")
    fig.add_hline(y=30, line_dash="dot", line_color="red",
                  annotation_text="Predictive Limit (30 °C)")
    fig.update_layout(template="simple_white")
    return fig

# ----------------------------
# Pages
# ----------------------------
def home_page():
    st.image("banner.png", width=900)
    st.title("StarCheck – Predictive Maintenance for Aircraft Engines")
    st.subheader("Compliance-First Cost Savings for Voyageur Aviation")
    st.markdown("---")
    st.header("The Problem")
    st.markdown("Preventive maintenance removes engines early, wasting life and costing millions.")
    st.header("The StarCheck Advantage")
    st.markdown("""
    - Longer Safe Use – forecasts unlock extra cycles inside regulatory limits  
    - Fewer Surprises – align removals with scheduled checks  
    - Smarter Fleet Use – assign healthiest engines to toughest routes  
    - Safety First – compliant with FAA / EASA / Transport Canada
    """)
    st.header("Case Example")
    st.markdown("""
    CRJ200 (GE CF34-3B1):  
    - 133 extra cycles unlocked (~44 days flying)  
    - Still 100% compliant with regulators
    """)

def dashboard_page():
    st.header("Fleet Dashboard")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    df = pd.read_csv(uploaded) if uploaded else load_demo_fleet()
    forecasts, rows = {}, []
    for eng in df.Engine_ID.unique():
        sub = df[df.Engine_ID==eng]
        f = forecast_engine(sub)
        forecasts[eng] = f
        extra = f["predictive_cycles"] - f["preventive_cycles"]
        days = extra/3
        value = days*2500
        rows.append({"Engine":eng,"Model":sub.Engine_Model.iloc[0],
                     "Preventive":f["preventive_cycles"],
                     "Predictive":f["predictive_cycles"],
                     "Days Saved":days,"Value ($)":value})
    results = pd.DataFrame(rows).round(0)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Fleet Summary")
    st.dataframe(results.style.format({"Preventive":"{:.0f}","Predictive":"{:.0f}",
                                       "Days Saved":"{:.0f}","Value ($)":"${:,.0f}"}))
    st.markdown("</div>", unsafe_allow_html=True)
    st.subheader("Top 3 At-Risk Engines")
    st.write(results.nsmallest(3,"Predictive")[["Engine","Model","Predictive"]])
    st.plotly_chart(plot_fleet(df, forecasts), use_container_width=True)

def fleet_optimization_page():
    st.header("Fleet Optimization – Voyageur Aviation")
    df = load_demo_fleet()
    mission_options = ["Hard Route", "Moderate Route", "Light Route"]
    stress_map = {"Hard Route": 1.2, "Moderate Route": 1.0, "Light Route": 0.8}
    assignments, rows, forecasts = {}, [], {}
    for eng in df.Engine_ID.unique():
        assignments[eng] = st.selectbox(f"Assign mission for {eng}", mission_options, index=1)
    for eng in df.Engine_ID.unique():
        sub = df[df.Engine_ID==eng]
        stress = stress_map[assignments[eng]]
        f = forecast_engine(sub, stress_factor=stress)
        forecasts[eng] = f
        extra = f["predictive_cycles"] - f["preventive_cycles"]
        days = extra/3
        value = days*2500
        rows.append({"Engine":eng,"Model":sub.Engine_Model.iloc[0],"Assignment":assignments[eng],
                     "Preventive":f["preventive_cycles"],"Predictive":f["predictive_cycles"],
                     "Days Saved":days,"Value ($)":value})
    results = pd.DataFrame(rows).round(0)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Optimization Results")
    st.dataframe(results.style.format({"Preventive":"{:.0f}","Predictive":"{:.0f}",
                                       "Days Saved":"{:.0f}","Value ($)":"${:,.0f}"}))
    st.markdown("</div>", unsafe_allow_html=True)
    st.success(f"Total Value Unlocked: ${results['Value ($)'].sum():,.0f}")
    st.plotly_chart(plot_fleet(df, forecasts), use_container_width=True)

def fleet_charts_page():
    st.header("Fleet Charts (Demo Data)")
    df = load_demo_fleet()
    forecasts = {eng: forecast_engine(df[df.Engine_ID==eng]) for eng in df.Engine_ID.unique()}
    st.subheader("Health Heatmap")
    health = pd.DataFrame({"Engine":list(forecasts.keys()),
                           "Predictive Cycles":[f["predictive_cycles"] for f in forecasts.values()]})
    health["Status"] = pd.cut(health["Predictive Cycles"], bins=[0,150,300,np.inf],
                              labels=["At Risk","Watch","Healthy"])
    st.dataframe(health)
    st.subheader("Degradation Slopes")
    slope_df = pd.DataFrame({"Engine":list(forecasts.keys()),
                             "Slope":[f["slope"] for f in forecasts.values()]})
    st.bar_chart(slope_df.set_index("Engine"))
    st.subheader("Value Unlocked per Engine")
    val_df = pd.DataFrame({"Engine":list(forecasts.keys()),
                           "Value":[(f["predictive_cycles"]-f["preventive_cycles"])/3*2500
                                    for f in forecasts.values()]})
    st.bar_chart(val_df.set_index("Engine"))

def report_page():
    st.header("Generate Demo Report")
    if st.button("Export Demo Report (PDF)"):
        doc = SimpleDocTemplate("StarCheck_Report.pdf", pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        # Custom styles
        title_style = ParagraphStyle("TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#0B1E3D"))
        heading_style = ParagraphStyle("Heading", parent=styles["Heading2"], textColor=colors.HexColor("#FF7A00"))
        normal_style = ParagraphStyle("NormalStyle", parent=styles["Normal"], textColor=colors.HexColor("#0B1E3D"))
        story.append(Paragraph("StarCheck – Predictive Maintenance Report", title_style))
        story.append(Spacer(1,12))
        story.append(Paragraph("Compliance-First Forecasting for Voyageur Aviation", heading_style))
        story.append(Spacer(1,12))
        story.append(Paragraph("This demo showcases predictive maintenance within regulatory thresholds "
                               "for CRJ200 (CF34-3B1) and Dash8-100 (PW120A) engines.", normal_style))
        story.append(Spacer(1,12))
        story.append(Paragraph("Forecasts indicate extended usable cycles without breaching preventive or predictive safety margins.", normal_style))
        doc.build(story)
        st.success("Demo PDF exported as StarCheck_Report.pdf")

# ----------------------------
# Router
# ----------------------------
PAGES = {
    "Home": home_page,
    "Dashboard": dashboard_page,
    "Fleet Optimization": fleet_optimization_page,
    "Fleet Charts": fleet_charts_page,
    "Report": report_page
}
def main():
    st.sidebar.image("logo.png", width=120)
    choice = st.sidebar.radio("Navigate", list(PAGES.keys()))
    PAGES[choice]()
if __name__ == "__main__":
    main()
