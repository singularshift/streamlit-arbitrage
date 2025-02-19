import streamlit as st
import pandas as pd
import altair as alt
from google.cloud import bigquery
from google.oauth2 import service_account

# Load Watch Catalogue
watch_catalogue = pd.read_csv("watch_catalogue.csv")

import streamlit as st
import pandas as pd
import altair as alt
from google.cloud import bigquery
from google.oauth2 import service_account

# ------------------------------------------------------------------------------
# Credentials via Streamlit secrets
# ------------------------------------------------------------------------------
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]
)
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# ------------------------------------------------------------------------------
# Load Watch Catalogue CSV (for Tag Heuer product names)
# ------------------------------------------------------------------------------
watch_catalogue = pd.read_csv("watch_catalogue.csv")  # Ensure the file exists

# ------------------------------------------------------------------------------
# Set Page Config (optional) - ensures wide layout, page title
# ------------------------------------------------------------------------------
st.set_page_config(page_title="TagTerminal - Bloomberg Style", layout="wide")

# ------------------------------------------------------------------------------
# App Title & Description
# ------------------------------------------------------------------------------
st.title("TagTerminal - Arbitrage Opportunity Explorer")
st.markdown(
    """
    <style>
    /* Make headings look more "terminal-like" */
    h1, h2, h3, h4, h5, h6 {
        font-family: monospace;
    }
    /* Make dataframes have a dark background */
    .dataframe tr, .dataframe td, .dataframe th {
        color: #F5F5F5 !important;
        background-color: #000000 !important;
        border-color: #1A1A1A !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.write(
    """
    Become rich EDHEC-style. This app lets you discover arbitrage opportunities within seconds for all luxury brands you can think about. All prices are converted to USD 
    for easy comparison and will use USD as a base currency. If there is no listing in USD, the script will use first EUR and next HKD next as a base currency. Enjoy hunting🫵📈!
    """
)

# ------------------------------------------------------------------------------
# Brand & Product Selections
# ------------------------------------------------------------------------------
query_brands = """
SELECT DISTINCT brand
FROM `edhec-business-manageme.luxurydata2502.price-monitoring-2022`
ORDER BY brand
"""
brands_df = client.query(query_brands).to_dataframe()
brand_options = brands_df["brand"].dropna().unique().tolist()

selected_brand = st.sidebar.selectbox("Select Brand", brand_options)

if selected_brand:
    query_products = f"""
    SELECT DISTINCT reference_code
    FROM `edhec-business-manageme.luxurydata2502.price-monitoring-2022`
    WHERE brand = '{selected_brand}'
    ORDER BY reference_code
    """
    products_df = client.query(query_products).to_dataframe()
    product_options = products_df["reference_code"].dropna().unique().tolist()

    # ✅ If Tag Heuer, replace reference_code with watch_name
    if selected_brand == "Tag Heuer":
        merged_df = products_df.merge(watch_catalogue, on="reference_code", how="left")
        merged_df["display_name"] = merged_df["watch_name"].fillna(merged_df["reference_code"])
        product_options = merged_df["display_name"].unique().tolist()

    selected_product = st.sidebar.selectbox("Select Product", product_options)
else:
    selected_product = None

# ------------------------------------------------------------------------------
# Data & Visualization
# ------------------------------------------------------------------------------
if selected_product:
    # ✅ If Tag Heuer, map watch_name back to reference_code
    if selected_brand == "Tag Heuer":
        reference_code_lookup = watch_catalogue[watch_catalogue["watch_name"] == selected_product]["reference_code"]
        if not reference_code_lookup.empty:
            selected_product = reference_code_lookup.iloc[0]  # Use reference_code for queries

    # 1) Get latest date
    query_latest_date = f"""
    SELECT MAX(life_span_date) as latest_date
    FROM `edhec-business-manageme.luxurydata2502.price-monitoring-2022`
    WHERE brand = '{selected_brand}' AND reference_code = '{selected_product}'
    """
    latest_date_df = client.query(query_latest_date).to_dataframe()

    if latest_date_df.empty or pd.isnull(latest_date_df["latest_date"].iloc[0]):
        st.error("No data found for the selected product.")
    else:
        latest_date = latest_date_df["latest_date"].iloc[0]

        # 2) Get price data for that date
        query_data = f"""
        SELECT
          reference_code,
          brand,
          life_span_date,
          country,
          currency,
          price
        FROM `edhec-business-manageme.luxurydata2502.price-monitoring-2022`
        WHERE brand = '{selected_brand}'
          AND reference_code = '{selected_product}'
          AND life_span_date = '{latest_date}'
        """
        data_df = client.query(query_data).to_dataframe()

        st.subheader(f"Data for {selected_brand} {selected_product} on {latest_date}")

        # 3) Convert all prices to USD
        exchange_rates = {
            'USD': 1.00,
            'CHF': 1.10,
            'CNY': 0.15,
            'EUR': 1.08,
            'GBP': 1.24,
            'HKD': 0.13,
            'JPY': 0.0074,
            'SGD': 0.75,
            'TWD': 0.033,
            'AED': 0.27,
            'KRW': 0.00076
        }
        data_df["price_usd"] = data_df.apply(
            lambda row: row["price"] * exchange_rates.get(row["currency"], 1.0),
            axis=1
        )

        # 4) Determine base currency (USD → EUR → HKD)
        base_currency = None
        base_price_usd = None
        if "USD" in data_df["currency"].values:
            base_currency = "USD"
            base_price_usd = data_df.loc[data_df["currency"] == "USD", "price_usd"].iloc[0]
        elif "EUR" in data_df["currency"].values:
            base_currency = "EUR"
            base_price_usd = data_df.loc[data_df["currency"] == "EUR", "price_usd"].iloc[0]
        elif "HKD" in data_df["currency"].values:
            base_currency = "HKD"
            base_price_usd = data_df.loc[data_df["currency"] == "HKD", "price_usd"].iloc[0]

        # 5) Build Altair Chart
        base_chart = alt.Chart(data_df).mark_bar().encode(
            x=alt.X("currency:N", title="Currency"),
            y=alt.Y("price_usd:Q", title="Price in USD"),
            tooltip=["currency", "price", "price_usd"]
        )

        if base_currency and base_price_usd is not None:
            color_scale = alt.condition(
                f"datum.price_usd > {base_price_usd}",
                alt.value("red"),
                alt.value("green")
            )
            chart = base_chart.encode(color=color_scale)
        else:
            chart = base_chart.encode(color=alt.value("steelblue"))

        chart = chart.configure(background="#000000").configure_axis(
            gridColor="#333333",
            labelColor="#F5F5F5",
            titleColor="#F5F5F5"
        ).configure_view(strokeOpacity=0)

        st.altair_chart(chart, use_container_width=True)

        # 6) Arbitrage Table
        st.subheader("Arbitrage Opportunity Details")
        if base_currency and base_price_usd is not None:
            st.write(f"**Base Currency:** {base_currency} — Converted to USD: {base_price_usd:.2f}")
            data_df["diff_vs_base"] = data_df["price_usd"] - base_price_usd
        else:
            st.write("No USD, EUR, or HKD listing found.")
            data_df["diff_vs_base"] = None

        st.dataframe(data_df[["currency", "price", "price_usd", "diff_vs_base"]].rename(
            columns={"currency": "Currency", "price": "Original Price", "price_usd": "Price in USD", "diff_vs_base": f"Difference vs. {base_currency if base_currency else 'None'}"}
        ))
