import streamlit as st

# -------------------- Page Config --------------------
st.set_page_config(
    page_title="Real Estate Analytics & Price Prediction",
    page_icon="🏠",
    layout="wide"
)

# -------------------- Header --------------------
st.title("🏠 Real Estate Analytics & Price Prediction")
st.caption(
    "An interactive analytics and machine learning application to explore real estate trends "
    "and estimate fair property prices."
)

st.divider()

# -------------------- Overview --------------------
st.header("📌 What does this app do?")
st.write(
    """
    This application helps users **analyze real estate market trends** and 
    **predict property prices** using a machine learning model trained on thousands of property listings.

    It is designed for:
    - 🧑‍💼 Buyers & sellers
    - 📊 Data analysts
    - 🏢 Real estate professionals
    """
)

# -------------------- Features --------------------
st.header("✨ Key Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ✅ Interactive **market analytics**  
        ✅ Region & locality-based filtering  
        ✅ Visual insights (maps, distributions, comparisons)  
        """
    )

with col2:
    st.markdown(
        """
        ✅ **Price prediction** using ML models  
        ✅ Market comparison & benchmarks  
        ✅ Clean, professional dashboard experience  
        """
    )

st.divider()

# -------------------- Navigation Help --------------------
st.header("🧭 How to use the app")

st.write(
    """
    Use the **sidebar navigation** to explore different sections of the application:
    
    - **🏠 Home** → Overview of the application  
    - **📊 Analytics** → Explore market trends and visual insights  
    - **📈 Price Predictor** → Predict property prices using ML  
    """
)

st.info("👈 Use the sidebar on the left to navigate between pages.")

# -------------------- Data & Model Info --------------------
st.header("📌 Data & Model Information")

st.write(
    """
    - **Dataset Size:** ~40,000 property listings  
    - **Features Used:** Location, property type, size, configuration, furnishing, age  
    - **Model:** LightGBM Regressor  
    - **Evaluation Metric:** R² Score ≈ 0.90 (best-performing model on test data)
    """
)

st.divider()

# -------------------- Footer --------------------
st.caption(
    "⚠️ Disclaimer: Price predictions are estimates based on historical data and "
    "should not be considered as final market valuations."
)
