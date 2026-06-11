# database.py
import sqlite3
import pandas as pd
from konfigurasi import DB_PATH


def get_db_connection():
    """Membuka koneksi ke database SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"ERROR koneksi database: {e}")
        return None


def execute_query(query: str, params: tuple = None):
    """Menjalankan query INSERT, UPDATE, DELETE."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()

        # Untuk INSERT, akan mengembalikan id.
        # Untuk DELETE, tetap dianggap berhasil jika tidak error.
        return cursor.lastrowid if cursor.lastrowid != 0 else True

    except sqlite3.Error as e:
        print(f"ERROR query gagal: {e}")
        conn.rollback()
        return None

    finally:
        conn.close()


def fetch_query(query: str, params: tuple = None, fetch_all: bool = True):
    """Menjalankan query SELECT."""
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return cursor.fetchall() if fetch_all else cursor.fetchone()

    except sqlite3.Error as e:
        print(f"ERROR fetch gagal: {e}")
        return None

    finally:
        conn.close()


def get_dataframe(query: str, params: tuple = None) -> pd.DataFrame:
    """Mengambil data SELECT menjadi DataFrame Pandas."""
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()

    try:
        return pd.read_sql_query(query, conn, params=params)

    except Exception as e:
        print(f"ERROR dataframe gagal: {e}")
        return pd.DataFrame()

    finally:
        conn.close()


def setup_database_initial():
    """Membuat tabel transaksi jika belum ada."""
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        sql_create_table = """
        CREATE TABLE IF NOT EXISTS transaksi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            deskripsi TEXT NOT NULL,
            jumlah REAL NOT NULL CHECK(jumlah > 0),
            kategori TEXT,
            tanggal DATE NOT NULL
        );
        """

        cursor.execute(sql_create_table)
        conn.commit()
        print("Tabel transaksi siap.")
        return True

    except sqlite3.Error as e:
        print(f"ERROR setup database: {e}")
        return False

    finally:
        conn.close()