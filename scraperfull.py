import time
import json
import os
import requests
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- KONFIGURASI ---
KEYWORD = "Tempat Wisata di Pangalengan"
FOLDER_IMG = "img"
WA_ADMIN = "62812345678"

# Pastikan folder img ada
if not os.path.exists(FOLDER_IMG):
    os.makedirs(FOLDER_IMG)

def bersihkan_nama_file(nama):
    # Biar nama filenya gak aneh-aneh (hapus spasi & simbol)
    return re.sub(r'[\\/*?:"<>|]', "", nama).replace(" ", "_").lower()

def download_gambar(url, nama_file):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            path = f"{FOLDER_IMG}/{nama_file}.jpg"
            with open(path, 'wb') as f:
                f.write(response.content)
            return f"{nama_file}.jpg"
    except:
        return None
    return None

def main():
    print("🚀 MEMULAI FULL SCRAPING (DATA + GAMBAR)...")
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Headless off dulu biar lo bisa liat prosesnya
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    url = f"https://www.google.com/maps/search/{KEYWORD.replace(' ', '+')}/"
    driver.get(url)
    time.sleep(5)

    # --- SCROLLING ---
    print("⬇️  Sedang scroll untuk memuat banyak tempat...")
    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        for i in range(5): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
    except:
        pass

    # --- AMBIL ELEMENT KARTU (CONTAINER) ---
    # Class 'Nv2PK' adalah container umum kartu di Maps (per Update 2025)
    cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    
    print(f"🔎 Ditemukan {len(cards)} lokasi. Mulai download gambar...")
    
    database_wisata = []

    for card in cards:
        try:
            # 1. Ambil Link & Nama (biasanya ada di tag <a> paling atas)
            link_tag = card.find_element(By.TAG_NAME, "a")
            nama = link_tag.get_attribute("aria-label")
            link_maps = link_tag.get_attribute("href")
            
            if not nama: continue

            print(f"   📸 Memproses: {nama}...")

            # 2. Ambil Gambar
            # Cari tag img di dalam kartu ini
            try:
                img_tag = card.find_element(By.TAG_NAME, "img")
                src_gambar = img_tag.get_attribute("src")
                
                # Download gambarnya
                nama_file_bersih = bersihkan_nama_file(nama)
                filename = download_gambar(src_gambar, nama_file_bersih)
                
                if not filename:
                    filename = "default.jpg" # Fallback kalau gagal download
            except:
                filename = "default.jpg"

            # 3. Susun Data
            data = {
                "nama": nama,
                "deskripsi": f"Wisata {nama} di Pangalengan. Klik tombol chat untuk booking dan info harga tiket.",
                "tiket": "Tanya Admin",
                "gambar": filename, # Ini nama file lokal yg udah didownload
                "link_maps": link_maps,
                "wa_admin": WA_ADMIN
            }
            database_wisata.append(data)

        except Exception as e:
            # print(f"Error: {e}")
            continue

    driver.quit()

    # --- GENERATE HTML ---
    print(f"\n⚙️  Merakit HTML dengan {len(database_wisata)} data...")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Wisata Pangalengan - Info & Booking</title>
        <style>
            body {{ font-family: sans-serif; background: #f0f2f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            .header {{ grid-column: 1/-1; text-align: center; margin-bottom: 30px; color: #2c3e50; }}
            .card {{ background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            .card img {{ width: 100%; height: 200px; object-fit: cover; }}
            .content {{ padding: 15px; }}
            .btn {{ display: block; background: #25D366; color: white; text-align: center; padding: 10px; text-decoration: none; border-radius: 5px; margin-top: 10px; font-weight: bold;}}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🌲 Pangalengan Trip Planner</h1>
            <p>Klik tombol WA untuk Booking / Info Tiket</p>
        </div>
        <div class="container">
    """

    for w in database_wisata:
        pesan = f"Halo admin, mau tanya info {w['nama']} dong."
        link_wa = f"https://wa.me/{w['wa_admin']}?text={pesan.replace(' ', '%20')}"
        
        # Penting: src gambarnya sekarang ngambil dari folder img/
        html_content += f"""
        <div class="card">
            <img src="img/{w['gambar']}" alt="{w['nama']}" onerror="this.src='https://via.placeholder.com/400?text=No+Image'">
            <div class="content">
                <h3>{w['nama']}</h3>
                <p>{w['deskripsi']}</p>
                <a href="{link_wa}" class="btn">📱 Chat via WhatsApp</a>
            </div>
        </div>
        """

    html_content += "</div></body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print("✅ SELESAI! Cek folder 'img', foto-foto wisata udah kesedot semua.")

if __name__ == "__main__":
    main()