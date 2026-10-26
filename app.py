import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# 1. KONFIGURASI HALAMAN
# ---------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Operasional Penjualan",
    page_icon="📊",
    layout="wide"
)

# Custom CSS Sederhana (Clean & Klasik)
st.markdown("""
    <style>
    /* Styling Kartu KPI Klasik */
    .kpi-box {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 6px;
        padding: 16px;
        text-align: left;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-title {
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #111827;
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('dataset_penjualan.csv')
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df['Bulan'] = df['Tanggal'].dt.strftime('%B %Y')
    return df

df = load_data()

# ---------------------------------------------------------
# 3. HEADER
# ---------------------------------------------------------
st.title("📊 Laporan Operasional Penjualan")
st.caption("Bedah Kasus 1: Visualisasi Data Transaksi & Performa Barang")
st.divider()

# ---------------------------------------------------------
# 4. SIDEBAR FILTER
# ---------------------------------------------------------
st.sidebar.header("Filter Data")

kategori_filter = st.sidebar.multiselect(
    "Kategori Produk:",
    options=df['Kategori'].unique(),
    default=df['Kategori'].unique()
)

df_kat_selected = df[df['Kategori'].isin(kategori_filter)]
produk_filter = st.sidebar.multiselect(
    "Produk:",
    options=df_kat_selected['Produk'].unique(),
    default=df_kat_selected['Produk'].unique()
)

min_date = df['Tanggal'].min().date()
max_date = df['Tanggal'].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Terapkan Filter
if len(date_range) == 2:
    start_date, end_date = date_range
    df_filtered = df[
        (df['Kategori'].isin(kategori_filter)) &
        (df['Produk'].isin(produk_filter)) &
        (df['Tanggal'].dt.date >= start_date) &
        (df['Tanggal'].dt.date <= end_date)
    ]
else:
    df_filtered = df[(df['Kategori'].isin(kategori_filter)) & (df['Produk'].isin(produk_filter))]

# ---------------------------------------------------------
# 5. METRIK KPI
# ---------------------------------------------------------
tot_trans = len(df_filtered)
tot_revenue = df_filtered['Total Pendapatan (Rp)'].sum() if not df_filtered.empty else 0
tot_units = df_filtered['Jumlah Terjual'].sum() if not df_filtered.empty else 0
avg_val = df_filtered['Total Pendapatan (Rp)'].mean() if not df_filtered.empty else 0
top_prod = df_filtered.groupby('Produk')['Jumlah Terjual'].sum().idxmax() if not df_filtered.empty else "-"

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Total Transaksi</div>
            <div class="kpi-value">{tot_trans:,}</div>
        </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Total Pendapatan</div>
            <div class="kpi-value">Rp {tot_revenue:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Unit Terjual</div>
            <div class="kpi-value">{tot_units:,}</div>
        </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Rata-rata / Transaksi</div>
            <div class="kpi-value">Rp {avg_val:,.0f}</div>
        </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-title">Produk Terlaris</div>
            <div class="kpi-value" style="font-size: 1.1rem;">{top_prod}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# ---------------------------------------------------------
# 6. VISUALISASI CHART
# ---------------------------------------------------------
COLOR_THEME = ['#1E3A8A', '#475569', '#0284C7', '#94A3B8', '#334155']

c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Tren Pendapatan Harian")
    df_trend = df_filtered.groupby('Tanggal')['Total Pendapatan (Rp)'].sum().reset_index()
    
    fig_line = px.line(
        df_trend, x='Tanggal', y='Total Pendapatan (Rp)',
        color_discrete_sequence=['#1E3A8A']
    )
    fig_line.update_layout(
        plot_bgcolor='#F8FAFC',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="", yaxis_title="Pendapatan (Rp)"
    )
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("📊 Proporsi Pendapatan per Kategori")
    df_kat = df_filtered.groupby('Kategori')['Total Pendapatan (Rp)'].sum().reset_index()
    
    fig_pie = px.pie(
        df_kat, values='Total Pendapatan (Rp)', names='Kategori', hole=0.4,
        color_discrete_sequence=COLOR_THEME
    )
    fig_pie.update_layout(margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("📦 Total Unit Terjual per Produk")
    df_prod = df_filtered.groupby('Produk')['Jumlah Terjual'].sum().reset_index().sort_values('Jumlah Terjual', ascending=True)
    
    fig_bar = px.bar(
        df_prod, x='Jumlah Terjual', y='Produk', orientation='h',
        text_auto=True, color_discrete_sequence=['#1E3A8A']
    )
    fig_bar.update_layout(
        plot_bgcolor='#F8FAFC',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Unit", yaxis_title=""
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("⚖️ Hubungan Harga vs Jumlah Terjual")
    fig_scatter = px.scatter(
        df_filtered, x='Harga (Rp)', y='Jumlah Terjual',
        color='Kategori', hover_data=['Produk'], opacity=0.75,
        color_discrete_sequence=COLOR_THEME
    )
    fig_scatter.update_layout(
        plot_bgcolor='#F8FAFC',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Harga (Rp)", yaxis_title="Jumlah Terjual"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ---------------------------------------------------------
# 7. TABEL LAPORAN
# ---------------------------------------------------------
st.divider()
st.subheader("📋 Ringkasan Performa Produk")

summary_df = df_filtered.groupby(['Produk', 'Kategori']).agg(
    Total_Transaksi=('Harga (Rp)', 'count'),
    Total_Unit=('Jumlah Terjual', 'sum'),
    Total_Pendapatan=('Total Pendapatan (Rp)', 'sum'),
    Rata_Rata_Harga=('Harga (Rp)', 'mean')
).reset_index()

st.dataframe(
    summary_df.style.format({
        'Total_Pendapatan': 'Rp {:,.0f}',
        'Rata_Rata_Harga': 'Rp {:,.0f}'
    }),
    use_container_width=True
)

with st.expander("📄 Lihat Data Mentah (1.000 Transaksi)"):
    st.dataframe(df_filtered)

# ---------------------------------------------------------
# 8. FOOTER
# ---------------------------------------------------------
st.divider()
st.markdown(
    "<p style='text-align: center; color: #9CA3AF; font-size: 0.85rem;'>"
    "© 241051020 - <b>ANDRIQO MARIO IMANUEL MANOPO</b> | All Rights Reserved"
    "</p>",
    unsafe_allow_html=True
)