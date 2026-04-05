import streamlit as st
import pickle
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time

# ---------------- LOAD MODEL ----------------
model = pickle.load(open("classifier.pickle", "rb"))

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")

# ---------------- DEFAULT BACKGROUND ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #1e293b, #6366f1);
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;'>
📊 Customer Churn Prediction Dashboard
</h1>
""", unsafe_allow_html=True)

st.write("---")

# ---------------- PLAN DATA ----------------
plans = {
    "₹149 - Basic": {"price":149, "max_months":1},
    "₹199 - Lite": {"price":199, "max_months":2},
    "₹299 - Popular": {"price":299, "max_months":4},
    "₹399 - Value": {"price":399, "max_months":6},
    "₹599 - Heavy": {"price":599, "max_months":12},
    "₹719 - Unlimited": {"price":719, "max_months":18},
    "₹839 - Pro": {"price":839, "max_months":24},
    "₹999 - Ultra": {"price":999, "max_months":36}
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

    plan_selected = st.selectbox("Select Telecom Plan", list(plans.keys()))
    monthly_charges = plans[plan_selected]["price"]
    max_tenure = plans[plan_selected]["max_months"]

    st.info(f"📦 Plan Price: ₹{monthly_charges}")
    st.warning(f"⏳ Max Tenure: {max_tenure} month(s)")

    if max_tenure == 1:
        tenure = 1
        st.info("📅 Fixed tenure: 1 month")
    else:
        tenure = st.slider("Tenure (months)", 1, max_tenure, min(3, max_tenure))

    total_charges = tenure * monthly_charges
    st.success(f"💰 Total Charges: ₹{total_charges}")

with col3:
    st.subheader("⚙️ Action")
    predict_btn = st.button("🚀 Predict Churn")

# ---------------- ENCODING ----------------
gender_enc = 1 if gender == "Male" else 0
partner_enc = 1 if partner == "Yes" else 0
dependents_enc = 1 if dependents == "Yes" else 0

# ---------------- PREDICTION ----------------
if predict_btn:

    input_data = np.array([[tenure, gender_enc, partner_enc,
                            total_charges, dependents_enc, monthly_charges]])

    prob = model.predict_proba(input_data)[0][1]

    # 🎨 SOFT COLORS (EYE-FRIENDLY)
    if prob < 0.40:
        theme_color = "#34d399"   # soft green
        status_text = "Customer will STAY ✅"
        risk_level = "Low"
    elif prob < 0.65:
        theme_color = "#fbbf24"   # soft yellow
        status_text = "Customer MAY STAY ⚠️"
        risk_level = "Medium"
    else:
        theme_color = "#f87171"   # soft red
        status_text = "Customer will CHURN ❌"
        risk_level = "High"

    # ---------------- DYNAMIC BG ----------------
    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, {theme_color}, #0f172a);
    }}
    </style>
    """, unsafe_allow_html=True)

    st.write("---")

    # ---------------- RESULT ----------------
    st.markdown(f"""
    <div style="
    padding:30px;
    border-radius:20px;
    text-align:center;
    font-size:32px;
    font-weight:bold;
    background: rgba(255,255,255,0.1);
    animation: pulse 2s infinite;">
    {status_text}
    </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # ---------------- METRICS ----------------
    colA, colB, colC = st.columns(3)
    colA.metric("Risk Level", risk_level)
    colB.metric("Probability", f"{prob:.2f}")
    colC.metric("Total Charges", f"₹{total_charges}")

    # ---------------- INSIGHT PLOT 1 ----------------
    st.subheader("📈 Churn Probability Breakdown")

    fig_prob = px.pie(
        names=["Stay", "Churn"],
        values=[1-prob, prob],
        hole=0.5
    )
    st.plotly_chart(fig_prob, use_container_width=True)

    # ---------------- INSIGHT PLOT 2 ----------------
    st.subheader("📊 Customer Risk Profile")

    df_plot = {
        "Feature": ["Tenure", "Monthly Charges", "Total Charges"],
        "Value": [tenure, monthly_charges, total_charges]
    }

    fig_bar = px.bar(df_plot, x="Feature", y="Value", text_auto=True)
    st.plotly_chart(fig_bar, use_container_width=True)

    # ---------------- GAUGE ----------------
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=prob * 100,
        title={'text': "Churn Risk (%)"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': theme_color},
            'steps': [
                {'range': [0, 40], 'color': "#bbf7d0"},
                {'range': [40, 65], 'color': "#fde68a"},
                {'range': [65, 100], 'color': "#fecaca"}
            ],
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

# ---------------- FOOTER ----------------
st.write("---")
st.markdown("""
<div style='text-align:center; font-size:16px; color:#e5e7eb;'>
✨ Made by <b>Aryan Sharma</b> | AI & Data Science Enthusiast 🚀
</div>
""", unsafe_allow_html=True)