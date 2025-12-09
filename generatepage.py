import datetime

# Data Pura-pura (Nanti kita ganti jadi data real hasil scraping)
data_wisata = [
    {"nama": "Nimo Highland", "status": "Buka", "tiket": "Rp 35.000"},
    {"nama": "Wayang Windu", "status": "Buka", "tiket": "Rp 10.000"},
    {"nama": "Kampung Singkur", "status": "Buka", "tiket": "Rp 20.000"},
    {"nama": "Sunrise Point Cukul", "status": "Ramai", "tiket": "Rp 10.000"},
]

waktu_sekarang = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

html = f"""
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wisata Pangalengan - Update Realtime</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f0f2f5; }}
        .header {{ text-align: center; background: #008080; color: white; padding: 20px; border-radius: 10px; }}
        .card {{ background: white; padding: 15px; margin-top: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .status {{ color: green; font-weight: bold; font-size: 0.9em; }}
        .footer {{ text-align: center; margin-top: 30px; font-size: 0.8em; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌲 Wisata Pangalengan</h1>
        <p>Pantauan Langsung dari Lokasi</p>
    </div>

    {''.join([f'''
    <div class="card">
        <h3>{w['nama']}</h3>
        <p>Status: <span class="status">✅ {w['status']}</span></p>
        <p>Tiket: {w['tiket']}</p>
        <a href="#">Lihat Detail & Lokasi</a>
    </div>
    ''' for w in data_wisata])}

    <div class="footer">
        <p>Di-generate otomatis oleh Python pada: {waktu_sekarang}</p>
        <p>&copy; 2025 WisataPangalengan.my.id</p>
    </div>
</body>
</html>
"""

# Simpan hasilnya jadi file HTML
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Sukses! File index.html sudah jadi.")