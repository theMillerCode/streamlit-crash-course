import pandas as pd
import streamlit as st
from io import StringIO

st.title("📘 Options Trading Journal")
st.write("Upload your Webull transaction file to begin.")

# File uploader
uploaded_file = st.file_uploader("Choose a Webull .txt file", type="txt")
if uploaded_file:
    # Read and clean data
    string_data = StringIO(uploaded_file.getvalue().decode("utf-8"))
    df = pd.read_csv(string_data)

    df['Placed Time'] = pd.to_datetime(df['Placed Time'], errors='coerce')
    df['Filled Time'] = pd.to_datetime(df['Filled Time'], errors='coerce')
    df['Price'] = df['Price'].str.replace('@', '').astype(float)
    df['Strategy'] = df['Name'].fillna(method='ffill')
    df['Symbol'] = df['Symbol'].fillna('')
    df['Multiplier'] = df['Side'].map({'Buy': -1, 'Sell': 1})
    df['Net Value'] = df['Price'] * df['Total Qty'] * df['Multiplier']

    # Summary by strategy
    summary = df.groupby('Strategy').agg({
        'Net Value': 'sum',
        'Total Qty': 'sum'
    }).reset_index()
    summary['P/L'] = summary['Net Value'].round(2)

    # Dashboard view
    strategies = df['Strategy'].dropna().unique()
    selected_strategy = st.selectbox("Select a strategy", strategies)

    filtered_df = df[df['Strategy'] == selected_strategy]
    st.subheader(f"Trades for {selected_strategy}")
    st.dataframe(filtered_df)

    st.subheader("Strategy Summary")
    strategy_summary = summary[summary['Strategy'] == selected_strategy]
    st.write(strategy_summary)

    st.subheader("Trade Side Breakdown")
    trade_breakdown = filtered_df.groupby('Side')['Net Value'].sum()
    st.bar_chart(trade_breakdown)

    st.subheader("📈 All Strategy Performance")
    st.dataframe(summary.sort_values(by="P/L", ascending=False))
else:
    st.info("Upload a file to begin analyzing your trades.")