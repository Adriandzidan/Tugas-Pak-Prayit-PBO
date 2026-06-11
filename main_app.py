# main_app.py
import streamlit as st
import datetime
import pandas as pd
import locale

from model import Transaksi
from manajer_anggaran import AnggaranHarian
from konfigurasi import KATEGORI_PENGELUARAN


try:
    locale.setlocale(locale.LC_ALL, "id_ID.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "Indonesian_Indonesia.1252")
    except:
        print("Locale Indonesia tidak tersedia.")


def format_rp(angka):
    try:
        return locale.currency(angka or 0, grouping=True, symbol="Rp ")[:-3]
    except:
        return f"Rp {angka or 0:,.0f}".replace(",", ".")


st.set_page_config(
    page_title="Catatan Pengeluaran",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def get_anggaran_manager():
    return AnggaranHarian()


anggaran = get_anggaran_manager()


def halaman_input(anggaran: AnggaranHarian):
    st.header("💸 Tambah Pengeluaran Baru")

    with st.form("form_transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            deskripsi = st.text_input(
                "Deskripsi*",
                placeholder="Contoh: Makan siang"
            )

        with col2:
            kategori = st.selectbox(
                "Kategori*:",
                KATEGORI_PENGELUARAN,
                index=0
            )

        col3, col4 = st.columns([1, 1])

        with col3:
            jumlah = st.number_input(
                "Jumlah (Rp)*:",
                min_value=0.01,
                step=1000.0,
                format="%.0f",
                value=None,
                placeholder="Contoh: 25000"
            )

        with col4:
            tanggal = st.date_input(
                "Tanggal*:",
                value=datetime.date.today()
            )

        submitted = st.form_submit_button("💾 Simpan Transaksi")

        if submitted:
            if not deskripsi:
                st.warning("Deskripsi wajib diisi!", icon="⚠️")
            elif jumlah is None or jumlah <= 0:
                st.warning("Jumlah wajib lebih dari 0!", icon="⚠️")
            else:
                tx = Transaksi(deskripsi, float(jumlah), kategori, tanggal)

                if anggaran.tambah_transaksi(tx):
                    st.success("Transaksi berhasil disimpan.", icon="✅")
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Transaksi gagal disimpan.", icon="❌")


def halaman_riwayat(anggaran: AnggaranHarian):
    st.header("📋 Riwayat Lengkap")

    if st.button("🔄 Refresh Riwayat"):
        st.cache_data.clear()
        st.rerun()

    df_transaksi = anggaran.get_dataframe_transaksi()

    if df_transaksi is None or df_transaksi.empty:
        st.info("Belum ada transaksi.")
    else:
        st.dataframe(
            df_transaksi,
            use_container_width=True,
            hide_index=True
        )

        st.divider()
        st.subheader("🗑️ Hapus Transaksi")

        id_hapus = st.number_input(
            "ID Transaksi Hapus:",
            min_value=1,
            step=1
        )

        if "konfirmasi_hapus" not in st.session_state:
            st.session_state.konfirmasi_hapus = False

        if st.button("Hapus Transaksi Terpilih"):
            st.session_state.konfirmasi_hapus = True

        if st.session_state.konfirmasi_hapus:
            st.warning(f"Yakin ingin menghapus transaksi dengan ID {id_hapus}?")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Ya, Hapus"):
                    if anggaran.hapus_transaksi(int(id_hapus)):
                        st.success("Transaksi berhasil dihapus.", icon="✅")
                        st.session_state.konfirmasi_hapus = False
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Gagal menghapus transaksi.", icon="❌")

            with col2:
                if st.button("❌ Batal"):
                    st.session_state.konfirmasi_hapus = False
                    st.rerun()


def halaman_ringkasan(anggaran: AnggaranHarian):
    st.header("📊 Ringkasan Pengeluaran")

    pilihan_periode = st.selectbox(
        "Filter Periode:",
        ["Semua Waktu", "Hari Ini", "Pilih Tanggal"]
    )

    tanggal_filter = None
    label_periode = "(Semua Waktu)"

    if pilihan_periode == "Hari Ini":
        tanggal_filter = datetime.date.today()
        label_periode = f"({tanggal_filter.strftime('%d-%m-%Y')})"

    elif pilihan_periode == "Pilih Tanggal":
        tanggal_filter = st.date_input(
            "Pilih Tanggal:",
            value=datetime.date.today()
        )
        label_periode = f"({tanggal_filter.strftime('%d-%m-%Y')})"

    total_pengeluaran = anggaran.hitung_total_pengeluaran(tanggal_filter)

    st.metric(
        label=f"Total Pengeluaran {label_periode}",
        value=format_rp(total_pengeluaran)
    )

    st.divider()

    st.subheader(f"Pengeluaran per Kategori {label_periode}")

    dict_per_kategori = anggaran.get_pengeluaran_per_kategori(tanggal_filter)

    if not dict_per_kategori:
        st.info("Tidak ada data untuk periode ini.")
    else:
        data_kategori = [
            {"Kategori": kat, "Total": jml}
            for kat, jml in dict_per_kategori.items()
        ]

        df_kategori = pd.DataFrame(data_kategori)
        df_kategori = df_kategori.sort_values(
            by="Total",
            ascending=False
        ).reset_index(drop=True)

        df_kategori["Total (Rp)"] = df_kategori["Total"].apply(format_rp)

        col1, col2 = st.columns(2)

        with col1:
            st.write("Tabel:")
            st.dataframe(
                df_kategori[["Kategori", "Total (Rp)"]],
                hide_index=True,
                use_container_width=True
            )

        with col2:
            st.write("Grafik:")
            st.bar_chart(
                df_kategori.set_index("Kategori")["Total"],
                use_container_width=True
            )


def main():
    st.sidebar.title("💰 Catatan Pengeluaran")
    menu_pilihan = st.sidebar.radio(
        "Pilih Menu:",
        ["Tambah", "Riwayat Lengkap", "Ringkasan"]
    )

    st.sidebar.markdown("---")
    st.sidebar.info("Jobsheet 11 - Aplikasi Keuangan")

    if menu_pilihan == "Tambah":
        halaman_input(anggaran)
    elif menu_pilihan == "Riwayat Lengkap":
        halaman_riwayat(anggaran)
    elif menu_pilihan == "Ringkasan":
        halaman_ringkasan(anggaran)

    st.markdown("---")
    st.caption("Pengembangan Aplikasi Berbasis OOP")


if __name__ == "__main__":
    main()