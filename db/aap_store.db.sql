BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS produk (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kode_produk TEXT UNIQUE NOT NULL,
    nama TEXT NOT NULL,
    kategori TEXT NOT NULL,
    harga REAL NOT NULL,
    stok INTEGER NOT NULL,
    deskripsi TEXT,
    tanggal_ditambahkan TEXT DEFAULT (DATE('now')),
    status INTEGER DEFAULT 1,
    foto TEXT
);
INSERT INTO "produk" ("id","kode_produk","nama","kategori","harga","stok","deskripsi","tanggal_ditambahkan","status","foto") VALUES (1,'AAP001','Kaos Polos Hitam','Pakaian',75000.0,20,'Kaos bahan cotton combed 30s','2025-07-29',1,'C:/Users/rudy2/PycharmProjects/Product Catalog Manager/foto/kaos1.jpg'),
 (2,'AAP002','Celana Chino Abu','Pakaian',120000.0,15,'Celana model slim fit','2025-07-29',1,'C:/Users/rudy2/PycharmProjects/Product Catalog Manager/foto/celana1.jpeg'),
 (3,'AAP003','Teh Botol 350ml','Minuman',5000.0,99,'Teh manis dalam botol','2025-07-29',1,'C:/Users/rudy2/PycharmProjects/Product Catalog Manager/foto/teh1.jpeg'),
 (4,'AAP004','Powerbank 10.000mAh','Elektronik',150000.0,30,'Fast charging support','2025-07-29',1,'C:/Users/rudy2/PycharmProjects/Product Catalog Manager/foto/pb1.jpeg'),
 (5,'AAP005','Sambal Terasi Pedas','Makanan',20000.0,50,'Sambal homemade original','2025-07-29',1,'C:/Users/rudy2/PycharmProjects/Product Catalog Manager/foto/sambal1.jpg');
COMMIT;
