import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Konfigurasi halaman
st.set_page_config(
    page_title="Dashboard Saham Realtime",
    page_icon="📈",
    layout="wide"
)

# Judul dashboard
st.title("📊 Dashboard Realtime Pergerakan Saham Dunia")

# Sidebar untuk input pengguna
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    
    # Pilihan saham dunia
    stock_options = {
        "Apple (AAPL)": "AAPL",
        "Microsoft (MSFT)": "MSFT",
        "Tesla (TSLA)": "TSLA",
        "Amazon (AMZN)": "AMZN",
        "Google (GOOGL)": "GOOGL",
        "NVIDIA (NVDA)": "NVDA",
        "Alibaba (BABA)": "BABA",
        "Samsung (005930.KS)": "005930.KS",
        "Toyota (7203.T)": "7203.T",
        "Sony (6758.T)": "6758.T",
        "HSBC (HSBC)": "HSBC",
        "BP (BP)": "BP"
    }
    
    selected_stock = st.selectbox(
        "Pilih Saham:",
        list(stock_options.keys()),
        index=0
    )
    
    ticker = stock_options[selected_stock]
    
    # Rentang waktu
    time_period = st.selectbox(
        "Rentang Waktu:",
        ["1 Hari", "1 Minggu", "1 Bulan", "3 Bulan", "6 Bulan", "1 Tahun"],
        index=2
    )
    
    # Interval data
    interval_options = {
        "1 Hari": "1m",
        "1 Minggu": "15m",
        "1 Bulan": "1h",
        "3 Bulan": "1d",
        "6 Bulan": "1d",
        "1 Tahun": "1d"
    }
    interval = interval_options[time_period]
    
    # Konversi time_period ke days
    period_map = {
        "1 Hari": 1,
        "1 Minggu": 7,
        "1 Bulan": 30,
        "3 Bulan": 90,
        "6 Bulan": 180,
        "1 Tahun": 365
    }
    period = f"{period_map[time_period]}d"

# Fungsi untuk mendapatkan data saham
@st.cache_data(ttl=60)  # Cache data selama 1 menit
def get_stock_data(ticker, period, interval):
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        return data
    except Exception as e:
        st.error(f"Error mendapatkan data: {e}")
        return None

# Dapatkan data saham
stock_data = get_stock_data(ticker, period, interval)

if stock_data is not None and not stock_data.empty:
    # Tampilkan informasi saham
    stock_info = yf.Ticker(ticker)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Saham Terpilih", f"{selected_stock} ({ticker})")
    
    with col2:
        current_price = stock_data['Close'].iloc[-1]
        prev_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else current_price
        price_change = current_price - prev_price
        percent_change = (price_change / prev_price) * 100
        st.metric(
            "Harga Terakhir", 
            f"${current_price:.2f}", 
            f"{price_change:.2f} ({percent_change:.2f}%)",
            delta_color="inverse"
        )
    
    with col3:
        market_cap = stock_info.info.get('marketCap', 'N/A')
        if isinstance(market_cap, (int, float)):
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:.2f}"
        else:
            market_cap_str = market_cap
        st.metric("Market Cap", market_cap_str)
    
    # Tab untuk berbagai visualisasi
    tab1, tab2, tab3 = st.tabs(["📈 Grafik Harga", "📊 Volume Perdagangan", "📌 Analisis Teknikal"])
    
    with tab1:
        # Grafik harga
        fig = go.Figure()
        
        # Candlestick chart untuk interval harian atau lebih kecil
        if interval in ['1m', '15m', '1h', '1d']:
            fig.add_trace(go.Candlestick(
                x=stock_data.index,
                open=stock_data['Open'],
                high=stock_data['High'],
                low=stock_data['Low'],
                close=stock_data['Close'],
                name="Candlestick"
            ))
        else:
            fig.add_trace(go.Scatter(
                x=stock_data.index,
                y=stock_data['Close'],
                mode='lines',
                name='Harga Penutupan',
                line=dict(color='royalblue', width=2)
            ))
        
        # Rata-rata bergerak
        ma_periods = [20, 50]
        for period in ma_periods:
            if len(stock_data) > period:
                ma = stock_data['Close'].rolling(window=period).mean()
                fig.add_trace(go.Scatter(
                    x=stock_data.index,
                    y=ma,
                    mode='lines',
                    name=f'MA {period}',
                    line=dict(width=1)
                ))
        
        fig.update_layout(
            title=f'Pergerakan Harga {selected_stock}',
            xaxis_title='Tanggal',
            yaxis_title='Harga (USD)',
            hovermode="x unified",
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Grafik volume
        fig_volume = go.Figure()
        
        colors = ['green' if close >= open else 'red' 
                 for close, open in zip(stock_data['Close'], stock_data['Open'])]
        
        fig_volume.add_trace(go.Bar(
            x=stock_data.index,
            y=stock_data['Volume'],
            name='Volume',
            marker_color=colors
        ))
        
        fig_volume.update_layout(
            title=f'Volume Perdagangan {selected_stock}',
            xaxis_title='Tanggal',
            yaxis_title='Volume',
            height=500
        )
        
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with tab3:
        # Analisis teknikal sederhana
        st.subheader("Indikator Teknikal")
        
        # Hitung indikator
        if len(stock_data) > 14:
            # RSI
            delta = stock_data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            # MACD
            ema12 = stock_data['Close'].ewm(span=12, adjust=False).mean()
            ema26 = stock_data['Close'].ewm(span=26, adjust=False).mean()
            macd = ema12 - ema26
            signal = macd.ewm(span=9, adjust=False).mean()
            
            # Buat grafik
            fig_tech = go.Figure()
            
            # RSI
            fig_tech.add_trace(go.Scatter(
                x=stock_data.index,
                y=rsi,
                name='RSI (14)',
                line=dict(color='purple', width=2)
            ))
            fig_tech.add_hline(y=70, line_dash="dash", line_color="red")
            fig_tech.add_hline(y=30, line_dash="dash", line_color="green")
            
            fig_tech.update_layout(
                title='Relative Strength Index (RSI)',
                height=300
            )
            
            st.plotly_chart(fig_tech, use_container_width=True)
            
            # MACD
            fig_macd = go.Figure()
            
            fig_macd.add_trace(go.Scatter(
                x=stock_data.index,
                y=macd,
                name='MACD',
                line=dict(color='blue', width=2)
            ))
            
            fig_macd.add_trace(go.Scatter(
                x=stock_data.index,
                y=signal,
                name='Signal Line',
                line=dict(color='orange', width=2)
            ))
            
            fig_macd.update_layout(
                title='Moving Average Convergence Divergence (MACD)',
                height=300
            )
            
            st.plotly_chart(fig_macd, use_container_width=True)
        else:
            st.warning("Data tidak cukup untuk analisis teknikal (minimal 14 periode)")
        
        # Tampilkan data mentah
        st.subheader("Data Mentah")
        st.dataframe(stock_data.sort_index(ascending=False), height=300)
else:
    st.warning("Tidak dapat mengambil data saham. Silakan coba lagi atau pilih saham lain.")

# Catatan kaki
st.markdown("---")
st.caption("""
    **Sumber Data:** Yahoo Finance (yfinance)  
    **Update:** Realtime (dengan delay 15 menit untuk data pasar AS)  
    ⚠️ Data ini hanya untuk tujuan edukasi, bukan rekomendasi investasi
""")
