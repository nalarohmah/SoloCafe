import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Generate Stok Barang (Coffee Shop Context)
stok_data = {
    'ID_Barang': ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'F01', 'F02'],
    'Nama_Barang': ['Espresso', 'Americano (Iced/Hot)', 'Cafe Latte', 'Cappuccino', 'Matcha Latte (Iced)', 'Caramel Macchiato', 'Butter Croissant', 'Red Velvet Cake'],
    'Kategori': ['Kopi', 'Kopi', 'Kopi', 'Kopi', 'Non-Kopi', 'Kopi', 'Pastry', 'Kue'],
    'Harga_Satuan': [15000, 18000, 22000, 22000, 25000, 28000, 20000, 30000],
    'Stok_Saat_Ini': [200, 150, 120, 110, 80, 90, 25, 10], # Asumsi stok bahan baku dalam satuan porsi
    'Batas_Aman': [50, 40, 30, 30, 20, 25, 10, 5]
}
df_stok = pd.DataFrame(stok_data)
df_stok.to_csv('stok_barang_coffee.csv', index=False)

# Generate Penjualan
start_date = datetime.now() - timedelta(days=365)
dates = [start_date + timedelta(days=i) for i in range(365)]

penjualan_records = []
for d in dates:
    # Simulate weather effect (weekends sell more, rain affects types of drinks)
    is_weekend = d.weekday() >= 5
    is_rainy = np.random.choice([True, False], p=[0.4, 0.6])
    
    for _, row in df_stok.iterrows():
        base_sales = np.random.randint(5, 30)
        
        # Adjust based on logic
        if is_weekend:
            base_sales = int(base_sales * 1.6) # Akhir pekan ramai
            
        if is_rainy:
            # Minuman dingin turun saat hujan, minuman hangat naik, kue naik
            if 'Iced' in row['Nama_Barang']:
                base_sales = int(base_sales * 0.4)
            elif row['Kategori'] == 'Kopi' and 'Iced' not in row['Nama_Barang']:
                base_sales = int(base_sales * 1.5)
            elif row['Kategori'] in ['Pastry', 'Kue']:
                base_sales = int(base_sales * 1.3)
                
        penjualan_records.append({
            'Tanggal': d.strftime('%Y-%m-%d'),
            'Nama_Barang': row['Nama_Barang'],
            'Terjual': base_sales,
            'Total_Pendapatan': base_sales * row['Harga_Satuan']
        })

df_penjualan = pd.DataFrame(penjualan_records)
df_penjualan.to_csv('penjualan_coffee.csv', index=False)

print("Data Coffee Shop berhasil di-generate!")
