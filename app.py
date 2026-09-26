import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import os

DATA_FILE = "pengeluaran_keluarga.csv"

# Inisialisasi file CSV jika belum ada
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Tanggal", "Kategori", "Nama Barang", "Nominal"])
    df_init.to_csv(DATA_FILE, index=False)

st.set_page_config(page_title="Catatan Dapur Ibu", page_icon="📝", layout="centered")

st.title("📝 Catatan Pengeluaran Rumah Tangga")

# --- MENU UTAMA DI AWAL ---
menu_utama = st.radio(
    "Pilih Menu Utama:",
    ["➕ Masukin Pengeluaran Hari Ini", "📊 Lihat Total Pengeluaran"],
    horizontal=True
)

st.divider()

# Daftar 8 Kategori Sesuai Permintaan
LIST_KATEGORI = [
    "1. Kebutuhan Perut",
    "2. Kebutuhan Anak",
    "3. Tagihan (Listrik, Air, dsb)",
    "4. Kebutuhan Rumah Tangga",
    "5. Perawatan dan Kesehatan",
    "6. Ongkos",
    "7. Jajanan",
    "8. Lain-lain"
]

# ==========================================
# MENU 1: INPUT PENGELUARAN HARI INI
# ==========================================
if menu_utama == "➕ Masukin Pengeluaran Hari Ini":
    st.subheader("➕ Tambah Pengeluaran Baru")
    
    tgl = st.date_input("Tanggal Transaksi", value=date.today())
    kategori = st.selectbox("Pilih Kategori Kebutuhan:", LIST_KATEGORI)
    nama_barang = st.text_input("Nama Barang / Rincian:", placeholder="Contoh: Pampers, Beras 5kg, Token Listrik")
    nominal = st.number_input("Nominal Uang (Rp):", min_value=0, step=1000, value=0)
    
    if st.button("💾 Simpan Pengeluaran", type="primary", use_container_width=True):
        if nominal > 0 and nama_barang.strip() != "":
            new_data = pd.DataFrame([[tgl, kategori, nama_barang, nominal]], 
                                    columns=["Tanggal", "Kategori", "Nama Barang", "Nominal"])
            new_data.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success(f"Berhasil disimpan: **{nama_barang}** ({kategori}) sebesar **Rp {nominal:,.0f}**")
        elif nominal <= 0:
            st.warning("Nominal uang harus lebih besar dari 0!")
        else:
            st.warning("Mohon isi nama barang/rincian terlebih dahulu!")

# ==========================================
# MENU 2: LIHAT TOTAL PENGELUARAN
# ==========================================
elif menu_utama == "📊 Lihat Total Pengeluaran":
    df = pd.read_csv(DATA_FILE)
    
    if df.empty:
        st.info("Belum ada data pengeluaran yang dicatat. Silakan masukkan data di menu 'Masukin Pengeluaran Hari Ini'.")
    else:
        df["Tanggal"] = pd.to_datetime(df["Tanggal"])
        
        # Pilihan Tampilan Laporan (Per Hari / Per Bulan / Per Tahun)
        tab_hari, tab_bulan, tab_tahun = st.tabs(["📅 Per Hari", "🗓️ Per Bulan", "📆 Per Tahun"])
        
        # --- TAB PER HARI ---
        with tab_hari:
            st.subheader("📅 Pengeluaran Per Hari")
            
            search_date = st.text_input("🔍 Cari tanggal tertentu (Ketik YYYY-MM-DD, contoh: 2026-03-15):")
            
            df_hari = df.copy()
            if search_date:
                df_hari = df_hari[df_hari["Tanggal"].dt.strftime('%Y-%m-%d').str.contains(search_date)]
            
            # Urutkan dari yang paling lama sampai paling baru
            df_hari = df_hari.sort_values(by="Tanggal", ascending=True)
            
            if not df_hari.empty:
                # Diagram Lingkaran Kategori
                st.write("### 🍰 Diagram Persentase Kategori Terbanyak")
                fig_pie_hari = px.pie(df_hari, values='Nominal', names='Kategori', title='Proporsi Pengeluaran Harian', hole=0.3)
                st.plotly_chart(fig_pie_hari, use_container_width=True)
                
                st.write("### 📜 Riwayat Catatan (Paling Lama ➡️ Paling Baru)")
                df_show_hari = df_hari.copy()
                df_show_hari["Tanggal"] = df_show_hari["Tanggal"].dt.strftime('%Y-%m-%d')
                st.dataframe(df_show_hari, use_container_width=True)
                
                total_harian = df_hari["Nominal"].sum()
                st.metric(label="Total Pengeluaran (Tampilan Ini)", value=f"Rp {total_harian:,.0f}")
            else:
                st.warning("Data tanggal tidak ditemukan.")
                
        # --- TAB PER BULAN ---
        with tab_bulan:
            st.subheader("🗓️ Pengeluaran Per Bulan")
            
            df_bulan = df.copy()
            df_bulan["Bulan_Tahun"] = df_bulan["Tanggal"].dt.strftime('%Y-%m') # Otomatis grouping bulan kalender (28-31 hari)
            
            search_month = st.text_input("🔍 Cari Bulan/Tahun (Ketik YYYY-MM, contoh: 2026-03):")
            if search_month:
                df_bulan = df_bulan[df_bulan["Bulan_Tahun"].str.contains(search_month)]
            
            df_bulan = df_bulan.sort_values(by="Tanggal", ascending=True)
            
            if not df_bulan.empty:
                st.write("### 🍰 Diagram Persentase Kategori Terbanyak (Bulanan)")
                fig_pie_bulan = px.pie(df_bulan, values='Nominal', names='Kategori', title='Proporsi Pengeluaran Bulanan', hole=0.3)
                st.plotly_chart(fig_pie_bulan, use_container_width=True)
                
                st.write("### 📊 Rekap Total per Bulan")
                rekap_bulan = df_bulan.groupby("Bulan_Tahun")["Nominal"].sum().reset_index()
                rekap_bulan.columns = ["Bulan (YYYY-MM)", "Total Pengeluaran (Rp)"]
                st.dataframe(rekap_bulan, use_container_width=True)
                
                total_bulanan = df_bulan["Nominal"].sum()
                st.metric(label="Total Pengeluaran (Tampilan Ini)", value=f"Rp {total_bulanan:,.0f}")
            else:
                st.warning("Data bulan tidak ditemukan.")

        # --- TAB PER TAHUN ---
        with tab_tahun:
            st.subheader("📆 Pengeluaran Per Tahun")
            
            df_tahun = df.copy()
            df_tahun["Tahun"] = df_tahun["Tanggal"].dt.strftime('%Y')
            
            search_year = st.text_input("🔍 Cari Tahun (Ketik YYYY, contoh: 2026):")
            if search_year:
                df_tahun = df_tahun[df_tahun["Tahun"].str.contains(search_year)]
            
            df_tahun = df_tahun.sort_values(by="Tanggal", ascending=True)
            
            if not df_tahun.empty:
                st.write("### 🍰 Diagram Persentase Kategori Terbanyak (Tahunan)")
                fig_pie_tahun = px.pie(df_tahun, values='Nominal', names='Kategori', title='Proporsi Pengeluaran Tahunan', hole=0.3)
                st.plotly_chart(fig_pie_tahun, use_container_width=True)
                
                st.write("### 📊 Rekap Total per Tahun")
                rekap_tahun = df_tahun.groupby("Tahun")["Nominal"].sum().reset_index()
                rekap_tahun.columns = ["Tahun", "Total Pengeluaran (Rp)"]
                st.dataframe(rekap_tahun, use_container_width=True)
                
                total_tahunan = df_tahun["Nominal"].sum()
                st.metric(label="Total Pengeluaran (Tampilan Ini)", value=f"Rp {total_tahunan:,.0f}")
            else:
                st.warning("Data tahun tidak ditemukan.")
