# -*- coding: utf-8 -*-
"""
Created on Thu Feb 26 16:52:30 2026

@author: lerij
"""

import pandas as pd
import numpy as np
import yfinance as yf

def parkinson_vol(data, window):
    rang = np.log(data['High']/data['Low'])**2
    sigma = np.sqrt(rang.rolling(window = window).sum() / (4*window*np.log(2)))
    return sigma *np.sqrt(252) * 100                            # annualizing it

def YZ_vol(data, window, annualize = 252,  pct = True):
    o = data['Open']
    h = data["High"]
    l = data['Low']
    c = data['Close']
    c_prev = c.shift(1)
    
    ro = np.log(o / c_prev)
    rc = np.log(c / o)
    
    rs = np.log(h/c)*np.log(h/o) + np.log(l/c)*np.log(l/o)
    
    sigma_o = ro.rolling(window=window).var(ddof=1) #ddof corresponds to 1/(N-1)
    sigma_c = rc.rolling(window=window).var(ddof=1)
    sigma_rs = rs.rolling(window=window).mean()
    
    k = 0.34/(1.34 + (window+1) / (window-1))
    sigma = np.sqrt(sigma_o + k * sigma_c + (1-k) * sigma_rs)
    sigma = sigma * np.sqrt(annualize)
    if pct:
        sigma = sigma * 100
    return sigma

def make_vol_cone(data: pd.DataFrame, quantiles= [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]):
    col = len(data.columns)
    vol_cone = pd.DataFrame(index = data.columns)
    for q in quantiles:
        vol_cone[f'{int(q*100)}%'] = [np.nanquantile(data.iloc[:,i], q) for i in range(col)]
    
    return vol_cone

def make_nonoverlapping_var(vol_data):
    nonover = pd.DataFrame()
    for i in range(len(vol_data.columns)):
        nonover[f'{vol_data.columns[int(i)]}'] = vol_data.iloc[:,i] * np.sqrt( 1 / (1 - int(vol_data.columns[i])/(len(vol_data.iloc[:,i])-int(vol_data.columns[i])+1) + (int(vol_data.columns[i])**2 - 1)/(3 * (len(vol_data.iloc[:,i])-int(vol_data.columns[i])+1)**2)))
    
    return nonover

    