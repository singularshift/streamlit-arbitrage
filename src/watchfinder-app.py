import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV files
latest_prices_file_path = './data/latest_prices.csv'
latest_prices_df = pd.read_csv(latest_prices_file_path, sep=';')

watches_file_path = './data/watchfinder_scraping_results.csv'
df = pd.read_csv(watches_file_path)
# Filter df to keep only rows where the reference code exists in latest_prices_df
df = df[df['Reference Code'].isin(latest_prices_df['reference_code'])]

# # Set Streamlit layout to wide
# st.set_page_config(layout="wide")

# Streamlit App
st.title('Tag Heuer Opportunity Finder 🤖⌚️')
st.subheader('Find the best deals on Tag Heuer watches on watchfinder.com')

# Step 1: Select Collection and Reference Code
col1, col2 = st.columns(2)

with col1:
    collections = df['Model'].unique().tolist()
    selected_collection = st.selectbox('Select a collection:', collections)

# Filter DataFrame by selected collection
df_filtered = df[df['Model'] == selected_collection]

with col2:
    reference_codes = df_filtered['Reference Code'].unique().tolist()
    selected_reference = st.selectbox('Select a reference code:', reference_codes)

# Create new DataFrame with selected reference code
df_selected = df_filtered[df_filtered['Reference Code'] == selected_reference].sort_values(by='Price', ascending=True)

# Check if the selected reference code exists in latest_prices_df and display the price
if selected_reference in latest_prices_df['reference_code'].values:
    price = latest_prices_df[latest_prices_df['reference_code'] == selected_reference]['price_in_usd'].values[0]

st.subheader(f'Latest price: ${price}')

# Step 3: Display DataFrame
st.subheader('Query results')
# Drop unnecessary columns
df_selected.drop(columns=['Model', 'Product code', 'Bracelet', 'Dial type'], inplace=True)

# Move 'URL' column to the rightmost position
url_column = df_selected.pop('URL')
df_selected['URL'] = url_column

# Compute the percent difference between the price variable and the Price column
df_selected['Percent Difference'] = ((df_selected['Price'] - price) / price) * 100

# Set the formatting to two decimal points using .2f technique
df_selected['Percent Difference'] = df_selected['Percent Difference'].map('{:.2f}'.format)

# Reorder columns to make 'Percent Difference' the third column
cols = df_selected.columns.tolist()
cols.insert(2, cols.pop(cols.index('Percent Difference')))
df_selected = df_selected[cols]

# Create a Styler object for df_selected with conditional formatting for the Percent Difference column
def color_percent_difference(val):
    val = float(val)
    if val < 0:
        return 'background-color: rgba(0, 255, 0, 0.5); color: white;'
    elif val > 0:
        return 'background-color: rgba(255, 0, 0, 0.5); color: white;'
    else:
        return 'background-color: white; color: black;'

styled_df = df_selected.style.applymap(color_percent_difference, subset=['Percent Difference'])

# Set the text size larger
styled_df = styled_df.set_table_styles(
    [{'selector': 'td', 'props': [('font-size', '16px')]}]
)

st.dataframe(styled_df, hide_index=True)
