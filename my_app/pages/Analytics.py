import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt


class AnalysisApp:

    def __init__(self):
        st.set_page_config(
            page_title="Real Estate Analytics",
            layout="wide"
        )

        st.title("📊 Real Estate Analytics Dashboard")

        self.df = self.load_data()
        self.filtered_df, self.selected_propertytype = self.sidebar_filters(self.df)
        self.show_kpi_cards(self.filtered_df, self.selected_propertytype)
        self.map_plot()
        self.plot_scatter()
        self.plot_pie()
        self.plot_boxplot()
        self.plot_furnishing_analysis()
        self.plot_age_analysis()
        self.plot_histogram()
        self.plot_hist_kde()

    # -------------------- DATA --------------------
    @staticmethod
    @st.cache_data
    def load_data():
        return pd.read_csv("data/raw/real_estate.csv")

    # -------------------- SIDEBAR FILTERS --------------------
    
    def sidebar_filters(self, df):

        with st.sidebar:
            st.header("🔎 Filters")

            # Region filter
            regions = ["overall"] + sorted(df["region"].unique().tolist())
            selected_region = st.selectbox("Region", regions)

            if selected_region != "overall":
                df = df[df["region"] == selected_region]

            # Locality filter
            localities = ["overall"] + sorted(df["locality"].unique().tolist())
            selected_locality = st.selectbox("Locality", localities)

            if selected_locality != "overall":
                df = df[df["locality"] == selected_locality]

            # Property type filter
            property_types = ["overall"] + sorted(df["propertytype"].unique().tolist())
            selected_propertytype = st.selectbox("Property Type", property_types)

            if selected_propertytype != "overall":
                df = df[df["propertytype"] == selected_propertytype]

        return df, selected_propertytype

    
    
    def show_kpi_cards(self, df, selected_propertytype):
        """
        Display KPI cards based on selected property type.
        """

        if df.empty:
            st.warning("No data available for selected filters.")
            return

        # Dynamic title
        title = (
            f"📌 Market Overview ({selected_propertytype.title()})"
            if selected_propertytype != "overall"
            else "📌 Market Overview (All Property Types)"
        )

        st.subheader(title)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            label="🏘 Total Listings",
            value=f"{len(df):,}"
        )

        col2.metric(
            label="💰 Avg Price",
            value=f"₹ {df['price'].mean():,.2f} Cr"
        )

        col3.metric(
            label="📐 Avg Price / Sqft",
            value=f"₹ {df['price_per_sqft'].mean():,.0f}"
        )

        low = int(df["totalfloornumber"].quantile(0.25))
        high = int(df["totalfloornumber"].quantile(0.75))

        if low == high:
            floor_display = f"{low}"
            label = "🏢 Typical Floors"
        else:
            floor_display = f"{low}–{high}"
            label = "🏢 Common Floor Range"

        col4.metric(
            label=label,
            value=floor_display
        )


    # -------------------- MAP --------------------
    def map_plot(self):
        st.header("📍 Price per Sqft Geomap")

        # Case 1: Single locality selected → show ALL points
        if self.filtered_df["locality"].nunique() == 1:

            fig = px.scatter_mapbox(
                self.filtered_df,
                lat="latitude",
                lon="longitude",
                color="price_per_sqft",
                size="superbuiltupareasqft",
                hover_name="locality",
                hover_data=["price", "bedrooms"],
                mapbox_style="open-street-map",
                zoom=13
            )

        # Case 2: Multiple localities → show aggregated points
        else:
            group_df = (
                self.filtered_df
                .groupby("locality", as_index=False)
                .agg({
                    "price_per_sqft": "mean",
                    "superbuiltupareasqft": "mean",
                    "latitude": "mean",
                    "longitude": "mean"
                })
            )

            fig = px.scatter_mapbox(
                group_df,
                lat="latitude",
                lon="longitude",
                color="price_per_sqft",
                size="superbuiltupareasqft",
                color_continuous_scale=px.colors.cyclical.IceFire,
                hover_name="locality",
                mapbox_style="open-street-map",
                zoom=10
            )

        st.plotly_chart(fig, use_container_width=True)
        st.caption(
                    "Map automatically switches between aggregated and individual property views based on selected filters."
                )



    # -------------------- SCATTER --------------------
    def plot_scatter(self):
        st.header("📈 Area vs Price")

        fig = px.scatter(
            self.filtered_df,
            x="superbuiltupareasqft",
            y="price",
            color="bedrooms",
            title="Area vs Price"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------- PIE --------------------
    def plot_pie(self):
        st.header("🥧 BHK Distribution")

        fig = px.pie(
            self.filtered_df,
            names="bedrooms",
            title="Bedroom Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------- BOX --------------------
    def plot_boxplot(self):
        st.header("📦 BHK Price Comparison")

        fig = px.box(
            self.filtered_df[self.filtered_df["bedrooms"] <= 4],
            x="bedrooms",
            y="price",
            title="BHK Price Range"
        )

        st.plotly_chart(fig, use_container_width=True)
        
        
    def plot_furnishing_analysis(self):
        st.header("🛋 Furnishing Status vs Price")

        fig = px.box(
            self.filtered_df,
            x="furnished",
            y="price",
            title="Price Distribution by Furnishing Status"
        )

        st.plotly_chart(fig, use_container_width=True)
        
    def plot_age_analysis(self):
        st.header("🏗 Age of Construction vs Price")

        fig = px.box(
            self.filtered_df,
            x="ageofcons",
            y="price",
            title="Price Distribution by Age of Construction"
        )

        st.plotly_chart(fig, use_container_width=True)



    # -------------------- HISTOGRAM --------------------
    def plot_histogram(self):
        st.header("📊 Avg Price per Sqft by Property Type")

        fig = px.histogram(
            self.filtered_df,
            x="propertytype",
            y="price_per_sqft",
            histfunc="avg",
            color="propertytype",
            title="Avg Price per Sqft"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -------------------- KDE --------------------
    def plot_hist_kde(self):
        st.header("📉 Price Distribution by Property Type")

        fig, ax = plt.subplots(figsize=(12, 6))

        for ptype in self.filtered_df["propertytype"].unique():
            sns.kdeplot(
                self.filtered_df[self.filtered_df["propertytype"] == ptype]["price"],
                label=ptype,
                ax=ax
            )

        ax.legend()
        st.pyplot(fig)


if __name__ == "__main__":
    AnalysisApp()
