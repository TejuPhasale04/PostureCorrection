import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image

# Constants
API_URL = "https://api.thingspeak.com/channels/2858135/feeds.json?api_key=SKW4Z74VMRJ9LHVP"

# Page Setup
st.set_page_config(page_title="Smart Posture Correction App", layout="wide", page_icon="🧍")

# Sidebar Navigation
st.sidebar.image("https://en.pimg.jp/078/020/658/1/78020658.jpg", width=100)
st.sidebar.title("Posture Navigator")
page = st.sidebar.radio("Go to", ["🏠 Home", "📈 Dashboard", "📅 Data by Date", "💊 Health Remedies", "🧠 Suggestions"])

# Fetch data function
@st.cache_data(ttl=60)
def fetch_data():
    response = requests.get(API_URL)
    result = response.json()
    feeds = result.get("feeds", [])
    df = pd.DataFrame(feeds)
    if df.empty:
        return df
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['field1'] = pd.to_numeric(df['field1'], errors='coerce')  # Right Shoulder
    df['field2'] = pd.to_numeric(df['field2'], errors='coerce')  # Left Shoulder
    df['field3'] = pd.to_numeric(df['field3'], errors='coerce')  # Upper Back
    df['field4'] = pd.to_numeric(df['field4'], errors='coerce')  # Lower Back
    return df.dropna()

df = fetch_data()

# Pie Chart Calculation
def get_pie_data(df):
    counts = {
        "Right Shoulder": (df["field1"]).sum(),
        "Left Shoulder": (df["field2"]).sum(),
        "Upper Back": (df["field3"] >= 0).sum(),
        "Lower Back": (df["field4"] >= 0).sum()
    }
    total = sum(counts.values())
    if total == 0:
        return None
    data = pd.DataFrame({"Area": list(counts.keys()), "Count": list(counts.values())})
    data["Percentage"] = (data["Count"] / total) * 100
    return data

# Home Page
if page == "🏠 Home":
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>Smart Posture Correction App</h1>", unsafe_allow_html=True)
    st.image("https://cdn.dribbble.com/users/63407/screenshots/3577631/standing.gif", use_column_width=True)
    image_path = "C:/Users/DELL/Data Science/Projects/Posture Corection Smart device/src/posturecorrection/Images/belt.jpg"
    try:
        local_img = Image.open(image_path)
        st.image(local_img, caption="Smart Device Tracking Posture", use_column_width=True)
    except FileNotFoundError:
        st.warning("Local posture image not found at the specified path.")
    st.markdown("---")
    st.markdown("### 🎯 Purpose")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTAdcrufa7NK7xCriZT5I7c_FFVx_ywnt6SfQ&s", width=200)
    with col2:
        st.markdown("""
        Our system helps you maintain a healthy posture using **real-time sensor data** from your upper body.

        It identifies imbalances in:
        - Right Shoulder
        - Left Shoulder  
        - Upper Back  
        - Lower Back  

        It also offers **real-time suggestions and remedies**, and the smart belt provides **real-time haptic feedback** to correct poor posture habits and prevent long-term issues.
        """)
    st.markdown("---")
    st.markdown("### 🔍 What You Can Do")
    colA, colB = st.columns(2)
    with colA:
        st.success("📡 **Live Posture Monitoring**\n\nTrack your posture in real-time using smart sensors.")
        st.info("📊 **Interactive Dashboards**\n\nVisualize posture metrics for each body area with insights.")
    with colB:
        st.warning("📅 **Date-wise Reports**\n\nFilter data based on date and observe changes over time.")
        st.error("💡 **Health Tips & Remedies**\n\nReceive curated advice and daily posture improvement tips.")
    st.markdown("---")

elif page == "📈 Dashboard":
    st.title("📊 Posture Dashboard")
    pie_data = get_pie_data(df)
    if pie_data is not None:
        fig = px.pie(pie_data, values="Percentage", names="Area",
                     color_discrete_sequence=px.colors.qualitative.Set2,
                     title="Posture Imbalance Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Not enough data to show pie chart.")

    if not df.empty:
        latest = df.iloc[-1]
        if abs(latest['field1']) > 10:
            st.error("🚨 Alert: You are bending too much at the **Right Shoulder**!")
        elif abs(latest['field1']) > 5:
            st.warning("⚠️ Caution: Slight deviation at the **Right Shoulder**.")
        if abs(latest['field2']) > 10:
            st.error("🚨 Alert: You are bending too much at the **Left Shoulder**!")
        elif abs(latest['field2']) > 5:
            st.warning("⚠️ Caution: Slight deviation at the **Left Shoulder**.")
        if abs(latest['field3']) > 10:
            st.error("🚨 Alert: You are bending too much at the **Upper Back**!")
        elif abs(latest['field3']) > 5:
            st.warning("⚠️ Caution: Slight deviation at the **Upper Back**.")
        if abs(latest['field4']) > 10:
            st.error("🚨 Alert: You are bending too much at the **Lower Back**!")
        elif abs(latest['field4']) > 5:
            st.warning("⚠️ Caution: Slight deviation at the **Lower Back**.")
    else:
        st.info("No sensor data available for alerts.")

    for field, label in zip(['field1', 'field2', 'field3', 'field4'],
                            ['Right Shoulder', 'Left Shoulder', 'Upper Back', 'Lower Back']):
        st.subheader(f"📈 {label} Trend")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["created_at"], y=df[field],
                                 mode='lines+markers',
                                 name=label,
                                 line=dict(shape='spline')))
        fig.update_layout(title=label, xaxis_title="Timestamp", yaxis_title="Sensor Value")
        st.plotly_chart(fig, use_container_width=True)

elif page == "📅 Data by Date":
    st.title("📅 Posture Data by Date")
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=1))
    end_date = st.date_input("End Date", datetime.now())
    if start_date > end_date:
        st.error("Start date must be before end date.")
    else:
        mask = (df['created_at'].dt.date >= start_date) & (df['created_at'].dt.date <= end_date)
        filtered_df = df.loc[mask]
        st.write(f"Filtered Data from {start_date} to {end_date}")
        st.dataframe(filtered_df)
        for field, label in zip(['field1', 'field2', 'field3', 'field4'],
                                ['Right Shoulder', 'Left Shoulder', 'Upper Back', 'Lower Back']):
            st.subheader(f"📊 {label} Trend")
            fig = px.line(filtered_df, x="created_at", y=field, title=f"{label} Over Time")
            st.plotly_chart(fig, use_container_width=True)

elif page == "💊 Health Remedies":
    st.title("💊 Posture-Related Issues & Remedies")
    st.markdown("Choose your issue below to learn more:")
    remedies = {
        "🦴 Spine Curvature Issues": ["✔ Practice Proper Posture", "✔ Strengthen Core Muscles", "✔ Use Ergonomic Chairs"],
        "⚡ Back Pain": ["✔ Sit with Proper Support", "✔ Avoid Long Sitting", "✔ Strengthen Lower Back"],
        "💡 Neck Pain": ["✔ Keep Screen at Eye Level", "✔ Stretch Neck Muscles", "✔ Stay Hydrated"],
        "🌙 Poor Sleep": ["✔ Use a Firm Mattress", "✔ Stretch Before Bed", "✔ Reduce Screen Time"],
        "🍽️ Digestive Issues": ["✔ Sit Upright After Meals", "✔ Walk After Eating", "✔ Eat Fiber-Rich Foods"]
    }
    for issue, tips in remedies.items():
        with st.expander(issue):
            for tip in tips:
                st.markdown(f"- {tip}")

elif page == "🧠 Suggestions":
    st.title("🧠 Smart Suggestions Based on Your Data")
    st.markdown("We analyzed your recent posture trends and here are some suggestions:")
    insights = []
    if (df['field1'] > 1).mean() > 0.3:
        insights.append("🔹 You tend to lean your **Right Shoulder** often. Try shoulder alignment exercises.")
    if (df['field2'] > 1).mean() > 0.3:
        insights.append("🔹 Your **Left Shoulder** shows imbalance. Consider ergonomic adjustments.")
    if (df['field3'] >= 1).mean() > 0.4:
        insights.append("🔹 **Upper Back** tension detected. Include upper spine stretches in your routine.")
    if (df['field4'] >= 1).mean() > 0.4:
        insights.append("🔹 **Lower Back** stress noted. Maintain lumbar support while sitting.")

    if insights:
        for insight in insights:
            st.info(insight)
    else:
        st.success("🎉 Great posture habits detected! Keep it up!")
