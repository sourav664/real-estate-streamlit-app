import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


FLOOR_LIMITS = {
    "multistorey apartment": 60,
    "builder floor apartment": 4,
    "residential house": 5,
    "villa": 4,
    "penthouse": 60
}

df = pd.read_csv(Path("data/raw/real_estate.csv"))
# preprocessor = joblib.load(Path("models/preprocesser.joblib"))
# model = joblib.load(Path("models/model.joblib"))

def get_similar_properties(
    df,
    region,
    propertytype,
    bedrooms,
    superbuiltupareasqft
):
    similar = df[
        (df["region"] == region) &
        (df["propertytype"] == propertytype) &
        (df["bedrooms"] == bedrooms)
    ]

    # Area tolerance ±20%
    lower_area = superbuiltupareasqft * 0.8
    upper_area = superbuiltupareasqft * 1.2

    similar = similar[
        (similar["superbuiltupareasqft"] >= lower_area) &
        (similar["superbuiltupareasqft"] <= upper_area)
    ]

    return similar


# ---------------------------
# Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Real Estate Price Predictor",
    page_icon="🏠",
    layout="wide"
)

# ---------------------------
# Load Model
# ---------------------------
@st.cache_resource
def load_model():
    return joblib.load("models/model.joblib")

model = load_model()

@st.cache_resource
def load_preprocessor():
    return joblib.load("models/preprocesser.joblib")

preprocessor = load_preprocessor()
# ---------------------------
# Header
# ---------------------------
st.title("🏠 Real Estate Price Predictor")
st.caption("Predict fair market value using machine learning")

st.divider()

# ---------------------------
# Sidebar Inputs
# ---------------------------
with st.sidebar:
    st.header("📌 Property Details")

    # -------- Property Type --------
    propertytype = st.selectbox(
    "Property Type",
    [
        "multistorey apartment",
        "builder floor apartment",
        "residential house",
        "villa",
        "penthouse"
    ]
)


    transactiontype = st.radio(
        "Transaction Type",
        sorted(df["transactiontype"].unique().tolist())
    )

    furnished = st.radio(
        "Furnishing Status",
        sorted(df["furnished"].unique().tolist())
    )

    st.divider()

    # -------- Property Configuration --------
    st.subheader("📐 Property Configuration")

    bedrooms = st.slider("Bedrooms", 1, int(df["bedrooms"].max()), 2)
    bathrooms = st.slider("Bathrooms", 1, int(df["bathrooms"].max()), 2)
    balconies = st.slider("Balconies", 0, int(df["balconies"].max()), 1)

    additional_room = st.selectbox("Additional Room", sorted(df['additionalRooms'].unique().tolist()))
    st.write("0: No, 1: Yes")
 

    st.divider()

    # -------- Location --------
    st.subheader("📍 Location Details")

    region = st.selectbox(
        "Region",
        df['region'].unique().tolist()
    )
    locality_data = df[df['region'] == region]['locality'].unique().tolist()
    locality = st.selectbox(
        "Locality",
        locality_data
    )

    st.divider()

    # -------- Building Info --------
    st.subheader("🏢 Building Information")

    superbuiltupareasqft = st.number_input(
        "Super Built-up Area (sqft)",
        min_value=450,
        max_value= 20000,
        step=50
    )

    max_floors = FLOOR_LIMITS[propertytype]

    totalfloornumber = st.number_input(
        "Total Floor Number",
        min_value=1,
        max_value=max_floors,
        value=min(1, max_floors),
        step=1
    )
    if totalfloornumber > max_floors:
        st.error(
            f"{propertytype.title()} cannot have more than {max_floors} floors."
        )
        st.stop()


    ageofcons = st.selectbox(
        "Age of Construction",
        sorted(df['ageofcons'].unique().tolist())
    )

    predict_btn = st.button("🔍 Predict Price", use_container_width=True)

# ---------------------------
# Prediction Section
# ---------------------------
if predict_btn:
    with st.spinner("Calculating best price..."):

        input_data = pd.DataFrame([{
        "propertytype": propertytype,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
        "balconies": balconies,
        "furnished": furnished,
        "transactiontype": transactiontype,
        "ageofcons": ageofcons,
        "additionalRooms": additional_room,
        "region": region,
        "locality": locality,
        "superbuiltupareasqft": superbuiltupareasqft,
        "totalfloornumber": totalfloornumber
          }])
        
        input_df = preprocessor.transform(input_data)
        base_price = model.predict(input_df)[0]
        lower_bound = round(base_price,2) - 0.25
        upper_bound = round(base_price,2) + 0.25

    st.success("Prediction generated successfully")

    # Price Metric
    st.metric(
        label="📈 Estimated Property Price",
        value=f"₹ {base_price:,.2f} crores",
    )

    st.divider()

    # ---------------------------
    # Explanation Section
    # ---------------------------
    st.subheader("🧠 Why this price?")
    st.write("""
    The estimated price is mainly influenced by:
    - **Region**
    - **Locality** (local market demand)
    - **SuperBuilt-up area**
    - **Number of bedrooms**
    - **Property type**
    """)

    st.divider()

    # ---------------------------
    # Market Insights (Placeholder)
    # ---------------------------
    st.subheader("📊 Market Insights")
    st.info("Price distribution and comparison charts will appear here.")
    similar_properties = get_similar_properties(
                                                df=df,
                                                region=region,
                                                propertytype=propertytype,
                                                bedrooms=bedrooms,
                                                superbuiltupareasqft=superbuiltupareasqft
                                            )
    
    if similar_properties.empty:
        st.warning("Not enough similar properties found for market comparison.")
        st.stop()
        
        

    # -------- Price Distribution --------
    

    fig = px.histogram(
    similar_properties,
    x="price",
    nbins=30,
    title="Price Distribution of Similar Properties"
    )

    # Add vertical line for predicted price
    fig.add_vline(
        x=base_price,
        line_width=3,
        line_dash="dash",
        annotation_text="Predicted Price",
        annotation_position="top"
    )

    fig.update_layout(
        xaxis_title="Price",
        yaxis_title="Number of Properties",
        bargap=0.05,
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------- Market Average --------
    market_avg = similar_properties["price"].mean()

    fig.add_vline(
        x=market_avg,
        line_width=3,
        line_dash="dot",
        annotation_text="Market Average",
        annotation_position="top"
    )
    diff = base_price - market_avg
    TOLERANCE = 0.01  # 0.01 crore ≈ 1 lakh

    if abs(diff) < TOLERANCE:
        delta_text = "At market average"
        delta_value = None
    else:
        delta_text = f"₹ {diff:,.2f} crores vs Market"
        delta_value = diff



    st.metric(
    label="Market Average Price",
    value=f"₹ {market_avg:,.2f} crores",
    delta=delta_text
   )


    # -------- Market Summary --------
    st.subheader("📌 Market Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Median Price", f"₹ {similar_properties['price'].median():,.2f} crores")
    col2.metric("Min Price", f"₹ {similar_properties['price'].min():,.2f} crores")
    col3.metric("Max Price", f"₹ {similar_properties['price'].max():,.2f} crores")




    st.divider()

    # ---------------------------
    # Model Information
    # ---------------------------
    st.subheader("📌 Model Information")
    st.write("""
            • **Model:** LightGBM Regressor  
            • **Training Data:** 31,784 properties  
            • **Test Data:** 7,946 properties  
            • **R² Score:** 0.89 (test set)  
            """)


else:
    st.info("👈 Enter property details from the sidebar to predict price.")
