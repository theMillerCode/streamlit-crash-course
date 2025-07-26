import streamlit as st
import pandas as pd

# Streamlit app
st.title("Swing Trading Journal MVP")
st.write("Upload your trades CSV (Webull/Tastytrade format)")

# File upload
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)
   
    # Ensure required columns
    required_cols = ['Symbol', 'Trade_Type', 'Entry_Date', 'Exit_Date',
                     'Entry_Premium', 'Exit_Premium', 'Quantity']
    if not all(col in df.columns for col in required_cols):
        st.error("CSV must include: Symbol, Trade_Type, Entry_Date, Exit_Date, "
                 "Entry_Premium, Exit_Premium, Quantity")
    else:
        # Convert dates
        df['Entry_Date'] = pd.to_datetime(df['Entry_Date'])
        df['Exit_Date'] = pd.to_datetime(df['Exit_Date'], errors='coerce')
       
        # Calculate P/L for closed trades
        df['P/L'] = df.apply(
            lambda row: (row['Exit_Premium'] - row['Entry_Premium']) * row['Quantity'] * 100
            if pd.notnull(row['Exit_Premium']) else 0, axis=1
        )
       
        # Identify open trades
        open_trades = df[df['Exit_Date'].isna() | (df['Exit_Premium'].isna())]
        closed_trades = df[df['P/L'] != 0]
       
        # Metrics
        total_pl = closed_trades['P/L'].sum()
        win_trades = len(closed_trades[closed_trades['P/L'] > 0])
        win_pct = (win_trades / len(closed_trades) * 100) if len(closed_trades) > 0 else 0
        avg_pl = closed_trades['P/L'].mean() if len(closed_trades) > 0 else 0
       
        # Display metrics
        st.subheader("Trade Analytics")
        st.write(f"**Total P/L**: ${total_pl:.2f}")
        st.write(f"**Win Percentage**: {win_pct:.2f}%")
        st.write(f"**Average P/L per Trade**: ${avg_pl:.2f}")
        st.write(f"**Open Trades**: {len(open_trades)}")
       
        # Show open trades
        if not open_trades.empty:
            st.subheader("Open Trades")
            st.dataframe(open_trades[['Symbol', 'Trade_Type', 'Entry_Date',
                                    'Entry_Premium', 'Quantity']])
       
        # Basic AI insight (rule-based)
        if 'Support_Resistance' in df.columns:
            resistance_trades = closed_trades[closed_trades['Support_Resistance'].str.contains('Resistance', na=False)]
            support_trades = closed_trades[closed_trades['Support_Resistance'].str.contains('Support', na=False)]
            res_win_pct = (len(resistance_trades[resistance_trades['P/L'] > 0]) / len(resistance_trades) * 100) if len(resistance_trades) > 0 else 0
            sup_win_pct = (len(support_trades[support_trades['P/L'] > 0]) / len(support_trades) * 100) if len(support_trades) > 0 else 0
            st.subheader("AI Insight")
            st.write(f"Credit spreads/PMCCs at resistance have a {res_win_pct:.2f}% win rate.")
            st.write(f"Credit spreads/PMCCs at support have a {sup_win_pct:.2f}% win rate.") 
