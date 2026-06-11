# model.py
import datetime


class Transaksi:
    """Merepresentasikan satu transaksi pengeluaran."""

    def __init__(
        self,
        deskripsi: str,
        jumlah: float,
        kategori: str,
        tanggal: datetime.date | str,
        id_transaksi: int | None = None
    ):
        self.id = id_transaksi
        self.deskripsi = str(deskripsi) if deskripsi else "Tanpa Deskripsi"

        try:
            jumlah_float = float(jumlah)
            self.jumlah = jumlah_float if jumlah_float > 0 else 0.0
        except (ValueError, TypeError):
            self.jumlah = 0.0

        self.kategori = str(kategori) if kategori else "Lainnya"

        if isinstance(tanggal, datetime.date):
            self.tanggal = tanggal
        elif isinstance(tanggal, str):
            try:
                self.tanggal = datetime.datetime.strptime(tanggal, "%Y-%m-%d").date()
            except ValueError:
                self.tanggal = datetime.date.today()
        else:
            self.tanggal = datetime.date.today()

    def __repr__(self):
        return (
            f"Transaksi(ID:{self.id}, "
            f"Tanggal:{self.tanggal}, "
            f"Jumlah:{self.jumlah}, "
            f"Kategori:{self.kategori}, "
            f"Deskripsi:{self.deskripsi})"
        )

    def to_dict(self):
        return {
            "deskripsi": self.deskripsi,
            "jumlah": self.jumlah,
            "kategori": self.kategori,
            "tanggal": self.tanggal.strftime("%Y-%m-%d")
        }