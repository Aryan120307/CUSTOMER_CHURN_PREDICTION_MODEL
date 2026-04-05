import streamlit as st
import pickle
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return pickle.load(open("classifier.pickle", "rb"))

model = load_model()

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# ---------------- DEFAULT THEME ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>📊 Customer Churn Dashboard</h1>", unsafe_allow_html=True)
st.write("---")

# ---------------- PLAN DATA ----------------
plans = {
    "₹149 - Basic":149,
    "₹199 - Lite":199,
    "₹299 - Popular":299,
    "₹399 - Value":399,
    "₹599 - Heavy":599,
    "₹719 - Unlimited":719,
    "₹839 - Pro":839,
    "₹999 - Ultra":999
}

# ---------------- INPUT ----------------
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("👤 Customer Info")
    gender = st.selectbox("Gender", ["Female", "Male"])
    partner = st.selectbox("Partner", ["No", "Yes"])
    dependents = st.selectbox("Dependents", ["No", "Yes"])

with col2:
    st.subheader("📅 Subscription")

    tenure = st.slider("Tenure (months)", 0, 72, 12)

    plan = st.selectbox("Select Plan", list(plans.keys()))
    monthly_charges = plans[plan]

    # realistic total charges
    noise = np.random.uniform(0.92, 1.05)
    total_charges = min(tenure * monthly_charges * noise, 10000)

    st.info(f"💰 Total Charges: ₹{total_charges:.2f}")

    # lifecycle
    if tenure < 3:
        st.caption("🆕 New Customer")
    elif tenure < 12:
        st.caption("📈 Growing Customer")
    else:
        st.caption("🏆 Loyal Customer")

with col3:
    st.subheader("⚙️ Action")
    predict = st.button("🚀 Predict Churn")

# ---------------- ENCODING ----------------
gender_enc = 1 if gender == "Male" else 0
partner_enc = 1 if partner == "Yes" else 0
dependents_enc = 1 if dependents == "Yes" else 0

# ---------------- PREDICTION ----------------
if predict:

    input_data = np.array([[tenure, gender_enc, partner_enc,
                            total_charges, dependents_enc, monthly_charges]])

    prob = model.predict_proba(input_data)[0][1]

    # -------- ML BASE --------
    if prob < 0.40:
        risk = "Low"
    elif prob < 0.65:
        risk = "Medium"
    else:
        risk = "High"

    # -------- BUSINESS OVERRIDE --------
    if monthly_charges >= 700 and tenure <= 3:
        risk = "High"
        status = "⚠️ New Premium User - High Risk"
    elif monthly_charges >= 700 and tenure >= 12:
        risk = "Low"
        status = "🏆 Loyal Premium Customer"
    elif tenure <= 2:
        risk = "High"
        status = "⚠️ Very New Customer"
    else:
        status = f"Customer Risk Level: {risk}"

    # -------- COLOR THEMES --------
    if risk == "Low":
        bg = "linear-gradient(135deg, #0f766e, #022c22)"
    elif risk == "Medium":
        bg = "linear-gradient(135deg, #b45309, #451a03)"
    else:
        bg = "linear-gradient(135deg, #991b1b, #1f2937)"

    # -------- APPLY THEME --------
    st.markdown(f"""
    <style>
    .stApp {{
        background: {bg};
        color: white;
    }}

    .card {{
        background: rgba(255,255,255,0.08);
        padding: 20px;
        border-radius: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0px 4px 20px rgba(0,0,0,0.4);
        margin-bottom: 15px;
    }}

    .big-card {{
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 30px;
        font-weight: bold;
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(15px);
        box-shadow: 0px 0px 25px rgba(0,0,0,0.5);
        animation: pulse 2s infinite;
    }}

    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.04); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)

    st.write("---")

    # -------- RESULT --------
    st.markdown(f"<div class='big-card'>{status}</div>", unsafe_allow_html=True)

    st.write("---")

    # -------- METRICS --------
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<div class='card'><h3>Risk</h3><h2>{risk}</h2></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='card'><h3>Probability</h3><h2>{prob:.2f}</h2></div>", unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='card'><h3>Monthly ₹</h3><h2>{monthly_charges}</h2></div>", unsafe_allow_html=True)

    # -------- INSIGHTS --------
    st.subheader("🧠 Insights")

    if tenure < 6:
        st.warning("New customers churn more")

    if monthly_charges > 500:
        st.warning("High-cost plans increase churn risk")

    if partner == "No":
        st.info("Single customers slightly more likely to churn")

    
  # ---------------- CHARTS (ENHANCED UI) ----------------

    chart_bg = "rgba(255,255,255,0.05)"   # glass effect
    plot_bg = "rgba(0,0,0,0)"

# ---------- PIE (DONUT STYLE) ----------
    fig1 = px.pie(
        names=["Stay", "Churn"],
        values=[1 - prob, prob],
        hole=0.65,
        color_discrete_sequence=["#4ade80", "#fb7185"]
    )

    fig1.update_traces(
        textinfo='percent+label',
        textfont_size=14
    )

    fig1.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font=dict(color="white"),
        showlegend=True,
        margin=dict(t=20, b=20)
    )

    st.plotly_chart(fig1, use_container_width=True)

# ---------- BAR (MODERN CLEAN) ----------
    fig2 = px.bar(
        x=["Tenure", "Monthly Charges", "Total Charges"],
        y=[tenure, monthly_charges, total_charges],
        text_auto=True,
        color=["Tenure", "Monthly Charges", "Total Charges"],
        color_discrete_map={
            "Tenure": "#60a5fa",
            "Monthly Charges": "#fbbf24",
            "Total Charges": "#34d399"
        }
    )

    fig2.update_layout(
        paper_bgcolor=plot_bg,
        plot_bgcolor=plot_bg,
        font=dict(color="white"),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
    )

    st.plotly_chart(fig2, use_container_width=True)

# ---------- GAUGE (PREMIUM LOOK) ----------
    fig3 = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        title={'text': "Churn Risk %", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#60a5fa"},
            'steps': [
                {'range': [0, 40], 'color': "rgba(74,222,128,0.4)"},
                {'range': [40, 65], 'color': "rgba(251,191,36,0.4)"},
                {'range': [65, 100], 'color': "rgba(248,113,113,0.4)"}
            ],
        }
    ))

    fig3.update_layout(
        paper_bgcolor=plot_bg,
        font=dict(color="white")
    )

    st.plotly_chart(fig3, use_container_width=True)

# ---------------- FOOTER ----------------
st.write("---")
st.markdown("<center>✨ Made by Aryan Sharma 🚀</center>", unsafe_allow_html=True)