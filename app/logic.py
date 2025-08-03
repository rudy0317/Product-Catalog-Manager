import sqlite3
import os
import sys
import traceback
import pyqtgraph as pg
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QMessageBox, QFileDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

# Untuk trace error lebih detail
def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.exit(1)

sys.excepthook = excepthook

DB_PATH = "db/aap_store.db"

class ProdukLogic:
    def __init__(self, ui):
        self.ui = ui
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()
        self.selected_id = None
        self.foto_path = None

        self.setup_events()
        self.setup_ui_logic()

    def setup_events(self):
        self.ui.btnSimpan.clicked.connect(self.simpan_produk)
        self.ui.btnHapus.clicked.connect(self.hapus_produk)
        self.ui.btnReset.clicked.connect(self.reset_form)
        self.ui.btnUploadFoto.clicked.connect(self.pilih_foto)

        self.ui.tableProduk.cellClicked.connect(self.select_row)
        self.ui.tableProduk.horizontalHeader().setStretchLastSection(True)

        self.ui.btnFilter.clicked.connect(self.load_produk_with_filter)
        self.ui.filter_kategori.currentIndexChanged.connect(self.load_produk_with_filter)
        self.ui.filter_status.currentIndexChanged.connect(self.load_produk_with_filter)
        self.ui.input_search.returnPressed.connect(self.load_produk_with_filter)

    def setup_ui_logic(self):
        self.ui.input_kategori.addItems(["Pakaian", "Makanan", "Minuman", "Elektronik", "Aksesoris"])
        self.ui.filter_status.clear()
        self.ui.filter_status.addItem("Semua", None)
        self.ui.filter_status.addItem("Aktif", 1)
        self.ui.filter_status.addItem("Tidak Aktif", 0)
        self.load_kategori_dropdown()
        self.load_data()
        self.hitung_statistik()
        self.tampilkan_chart()

    def load_kategori_dropdown(self):
        self.ui.filter_kategori.clear()
        self.ui.filter_kategori.addItem("Semua")
        result = self.cursor.execute("SELECT DISTINCT kategori FROM produk").fetchall()
        for row in result:
            self.ui.filter_kategori.addItem(row[0])

    def load_data(self):
        self.ui.tableProduk.setColumnCount(9)
        self.ui.tableProduk.setHorizontalHeaderLabels([
            "Kode", "Nama", "Kategori", "Harga", "Stok",
            "Deskripsi", "Tanggal", "Status", "Foto"
        ])
        self.ui.tableProduk.setRowCount(0)
        self.cursor.execute("""
            SELECT kode_produk, nama, kategori, harga, stok, deskripsi, 
                   tanggal_ditambahkan, status, foto
            FROM produk
        """)
        self.populate_table(self.cursor.fetchall())

    def populate_table(self, data):
        self.ui.tableProduk.setRowCount(0)
        for row_num, row_data in enumerate(data):
            self.ui.tableProduk.insertRow(row_num)
            for col_num, value in enumerate(row_data):
                if col_num == 7:
                    display_value = "Aktif" if value == 1 else "Tidak Aktif"
                elif col_num == 8:
                    display_value = os.path.basename(str(value)) if value else ""
                else:
                    display_value = str(value)
                self.ui.tableProduk.setItem(row_num, col_num, QTableWidgetItem(display_value))

    def load_produk_with_filter(self):
        keyword = self.ui.input_search.text().strip()
        kategori = self.ui.filter_kategori.currentText()
        status_value = self.ui.filter_status.currentData()
        harga_min = self.ui.filter_harga_min.text().strip()
        harga_max = self.ui.filter_harga_max.text().strip()

        query = """
            SELECT kode_produk, nama, kategori, harga, stok, deskripsi, 
                   tanggal_ditambahkan, status, foto
            FROM produk
            WHERE 1=1
        """
        params = []

        if keyword:
            query += " AND (nama LIKE ? OR kode_produk LIKE ? OR deskripsi LIKE ?)"
            wild = f"%{keyword}%"
            params += [wild, wild, wild]

        if kategori != "Semua":
            query += " AND kategori = ?"
            params.append(kategori)

        if status_value is not None:
            query += " AND status = ?"
            params.append(status_value)

        if harga_min.isdigit():
            query += " AND harga >= ?"
            params.append(int(harga_min))
        if harga_max.isdigit():
            query += " AND harga <= ?"
            params.append(int(harga_max))

        result = self.cursor.execute(query, params).fetchall()
        self.populate_table(result)
        self.hitung_statistik()
        self.tampilkan_chart()

    def hitung_statistik(self):
        total = self.cursor.execute("SELECT COUNT(*) FROM produk").fetchone()[0]
        aktif = self.cursor.execute("SELECT COUNT(*) FROM produk WHERE status = 1").fetchone()[0]
        nonaktif = self.cursor.execute("SELECT COUNT(*) FROM produk WHERE status = 0").fetchone()[0]

        self.ui.label_total.setText(f"Total Produk: {total}")
        self.ui.label_aktif.setText(f"Produk Aktif: {aktif}")
        self.ui.label_nonaktif.setText(f"Produk Tidak Aktif: {nonaktif}")

    def tampilkan_chart(self):
        # Hapus isi sebelumnya (biar gak numpuk)
        if self.ui.chartWidget.layout() is not None:
            while self.ui.chartWidget.layout().count():
                item = self.ui.chartWidget.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            self.ui.chartWidget.setLayout(QtWidgets.QVBoxLayout())

        # Buat chart baru
        plot = pg.PlotWidget()
        plot.setBackground("w")
        plot.setTitle("Produk per Kategori")
        plot.showGrid(x=True, y=True)

        # Ambil data dari database
        result = self.cursor.execute("SELECT kategori, COUNT(*) FROM produk GROUP BY kategori").fetchall()
        if result:
            kategori = [r[0] for r in result]
            jumlah = [r[1] for r in result]
            bar = pg.BarGraphItem(x=range(len(kategori)), height=jumlah, width=0.6, brush='dodgerblue')
            plot.addItem(bar)
            plot.getAxis("bottom").setTicks([list(enumerate(kategori))])

        self.ui.chartWidget.layout().addWidget(plot)

    def get_form_data(self):
        kode = self.ui.input_kode.text().strip()
        nama = self.ui.input_nama.text().strip()
        harga = self.ui.input_harga.value()
        deskripsi = self.ui.input_deskripsi.toPlainText().strip()
        kategori = self.ui.input_kategori.currentText()
        status = self.ui.input_status.isChecked()
        stok = self.ui.input_stok.value()
        foto = self.foto_path or ""

        if not kode or not nama:
            QMessageBox.warning(None, "Validasi", "Kode dan Nama produk wajib diisi!")
            return None

        return {
            "kode_produk": kode,
            "nama": nama,
            "harga": harga,
            "deskripsi": deskripsi,
            "kategori": kategori,
            "status": status,
            "stok": stok,
            "foto": foto
        }

    def simpan_produk(self):
        data = self.get_form_data()
        if not data:
            return

        if self.selected_id is None:
            try:
                self.cursor.execute("""
                    INSERT INTO produk (kode_produk, nama, kategori, harga, stok, deskripsi, status, foto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data["kode_produk"], data["nama"], data["kategori"], data["harga"],
                    data["stok"], data["deskripsi"], int(data["status"]), data["foto"]
                ))
                self.conn.commit()
                QMessageBox.information(None, "Sukses", "Produk berhasil disimpan.")
            except sqlite3.IntegrityError:
                QMessageBox.warning(None, "Error", "Kode produk sudah terdaftar!")
                return
        else:
            self.cursor.execute("""
                UPDATE produk SET 
                    kode_produk=?, nama=?, kategori=?, harga=?, stok=?, 
                    deskripsi=?, status=?, foto=?
                WHERE id=?
            """, (
                data["kode_produk"], data["nama"], data["kategori"], data["harga"],
                data["stok"], data["deskripsi"], int(data["status"]), data["foto"],
                self.selected_id
            ))
            self.conn.commit()
            QMessageBox.information(None, "Sukses", "Produk berhasil diperbarui.")

        self.load_data()
        self.reset_form()

    def hapus_produk(self):
        if self.selected_id is None:
            QMessageBox.warning(None, "Peringatan", "Pilih data dulu yang mau dihapus.")
            return

        confirm = QMessageBox.question(None, "Konfirmasi", "Yakin ingin menghapus produk ini?",
                                       QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.cursor.execute("DELETE FROM produk WHERE id=?", (self.selected_id,))
            self.conn.commit()
            QMessageBox.information(None, "Sukses", "Produk berhasil dihapus.")
            self.load_data()
            self.reset_form()

    def pilih_foto(self):
        path, _ = QFileDialog.getOpenFileName(None, "Pilih Foto", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.foto_path = path
            self.tampilkan_foto(path)

    def tampilkan_foto(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.ui.preview_foto.width(),
                    self.ui.preview_foto.height(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.ui.preview_foto.setPixmap(scaled)
                self.ui.preview_foto.setAlignment(Qt.AlignCenter)
                self.ui.preview_foto.setText("")
            else:
                self.ui.preview_foto.setText("📻 Foto corrupt")
        else:
            self.ui.preview_foto.setText("📻 Foto tidak tersedia")

    def select_row(self, row, _):
        kode_produk = self.ui.tableProduk.item(row, 0).text()
        self.cursor.execute("SELECT * FROM produk WHERE kode_produk=?", (kode_produk,))
        data = self.cursor.fetchone()
        if data:
            self.selected_id = data[0]
            self.ui.input_kode.setText(data[1])
            self.ui.input_nama.setText(data[2])
            self.ui.input_kategori.setCurrentText(data[3])
            self.ui.input_harga.setValue(float(data[4]))
            self.ui.input_stok.setValue(int(data[5]))
            self.ui.input_deskripsi.setPlainText(data[6])
            self.ui.input_status.setChecked(bool(data[8]))
            self.foto_path = data[9]
            self.tampilkan_foto(self.foto_path)

    def reset_form(self):
        self.ui.input_kode.clear()
        self.ui.input_nama.clear()
        self.ui.input_harga.setValue(0.0)
        self.ui.input_stok.setValue(0)
        self.ui.input_deskripsi.clear()
        self.ui.input_kategori.setCurrentIndex(0)
        self.ui.input_status.setChecked(True)
        self.ui.preview_foto.clear()
        self.ui.preview_foto.setText("📻 Belum ada foto")
        self.selected_id = None
        self.foto_path = None