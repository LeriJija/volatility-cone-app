# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 16:54:17 2026

@author: lerij
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st
from datetime import date

from functions import YZ_vol, make_vol_cone

st.set_page_config(page_title="Volatility Cone", layout="centered")
st.title("Volatility Cone")

# Sidebar inputs
ticker_name = st.sidebar.text_input("Ticker", value="SPY").upper()

use_custom_dates = st.sidebar.checkbox("Enter start/end dates", value=False)
if use_custom_dates:
    start = st.sidebar.text_input("Start (YYYY-MM-DD)", value="2020-01-01")
    end = st.sidebar.text_input("End (YYYY-MM-DD)", value=str(date.today()))
else:
    start = "2020-01-01"
    end = str(date.today())

use_custom_days = st.sidebar.checkbox("Specify maturities", value=False)
if use_custom_days:
    h_raw = st.sidebar.text_input("Days (space-separated)", value="30 60 90 240")
    try:
        h_list = list(map(int, h_raw.split()))
    except:
        st.error("Could not parse maturities. Use space-separated integers, e.g. 30 60 90 240")
        st.stop()
else:
    h_list = [30, 60, 90, 240]

quantiles = st.sidebar.multiselect(
    "Quantiles",
    options=[0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0],
    default=[0.0, 0.1, 0.25, 0.5, 0.75, 0.9],
)

@st.cache_data(ttl=3600)
def load_data(ticker_name: str, start: str, end: str) -> pd.DataFrame:
    t = yf.Ticker(ticker_name)
    df = pd.DataFrame(t.history(start=start, end=end, interval="1d")).iloc[:, :4]
    df["log_r"] = np.log(df["Close"] / df["Close"].shift(1))
    return df

if st.button("Generate cone"):
    try:
        data = load_data(ticker_name, start, end)
        if data.empty:
            st.error("No data returned. Check ticker or date range.")
            st.stop()

        # YZ vols
        YZ = pd.DataFrame()
        for h in h_list:
            YZ[str(h)] = YZ_vol(data, h)

        vol_cone = make_vol_cone(YZ, quantiles=quantiles)

        # Plot
        fig, ax = plt.subplots()
        plt.style.use('default') 
        n = len(vol_cone.columns)
        grays = np.linspace(0.2, 0.8, n)
        
        for i, col in enumerate(vol_cone.columns):
            color = str(grays[i])
            plt.plot(vol_cone.index, 
                     vol_cone[col], 
                     label = col,
                     color = color,
                     linewidth = 2 if i == 0 else 1.5)
        plt.legend(loc = 'center right')
        plt.xlabel('Maturity (days)')
        plt.ylabel('Volatility')
        plt.title(f'{ticker_name} Volatility Cone')
        plt.show()

        st.pyplot(fig)

        with st.expander("Show cone table"):
            st.dataframe(vol_cone)

    except Exception as e:
        st.exception(e)
else:
    st.info("Set inputs on the left and click **Generate cone**.")