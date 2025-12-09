import time
import json
import os
import re
import random
import datetime
import requests
import traceback
from bs4 import BeautifulSoup

# --- IMPORT SELENIUM ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# =======================================================
#               KONFIGURASI
# =======================================================
LOCAL_MODEL = "qwen2.5:1.5b" 

KEYWORD_PENCARIAN = "Tempat Wisata di Pangalengan"
FOLDER_IMG = "img"
FOLDER_ARTIKEL = "artikel" 
WA_ADMIN = "6285156098112"  
# Kita set False karena GitHub Action yang akan melakukan push (lebih aman)
AUTO_UPLOAD_GITHUB = False 

KEYWORD_ARTIKEL = [
    "5 Spot Healing Terbaik di Kebun Teh Pangalengan",
    "Rekomendasi Tempat Camping Keluarga di Pinggir Danau Pangalengan",
    "Panduan Lengkap Liburan ke Nimo Highland dan Wayang Windu",
    "Daftar Harga Tiket Masuk Tempat Wisata di Pangalengan 2025"
]

# =======================================================
#               FUNGSI AI (CONNECT KE GITHUB SERVER)
# =======================================================

def call_ollama_nano(prompt):
    url = "http://127.0.0.1:11434/api/generate"
    full_prompt = f"Kamu adalah asisten travel writer bahasa Indonesia. Jawab langsung tanpa basa-basi. Tugas: {prompt}"
    payload = { "model": LOCAL_MODEL, "prompt": full_prompt, "stream": False }
    
    print(f"   📡 Nano AI ({LOCAL_MODEL}) sedang mikir...")
    try:
        response = requests.post(url, json=payload, timeout=300) 
        if response.status_code == 200:
            hasil = response.json()['response']
            return hasil.strip().replace('**', '').replace('*', '').replace('## ', '<h2>').replace('### ', '<h3>')
        return None
    except Exception as e:
        print(f"   ❌ Gagal konek ke Server AI: {e}")
        return None

def rewrite_deskripsi_dengan_ai(deskripsi_awal, nama_tempat):
    prompt = (f"Buat deskripsi singkat 2 kalimat yang menarik untuk tempat wisata '{nama_tempat}'. "
              f"Data mentah: {deskripsi_awal}. Gunakan bahasa santai dan mengajak.")
    res = call_ollama_nano(prompt)
    return res if res else deskripsi_awal

def generate_seo_article(judul_artikel):
    prompt = (
        f"Tulis artikel blog wisata bahasa Indonesia (sekitar 300 kata) dengan judul '{judul_artikel}'. "
        f"Gunakan tag <h2> untuk subjudul. Gaya bahasa santai, informatif, dan gaul."
    )
    return call_ollama_nano(prompt)

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# =======================================================
#               MAIN PROGRAM
# =======================================================

def main():
    try:
        print(f"🚀 START AUTOPILOT (MODE: NANO AI - {LOCAL_MODEL})...\n")
        
        if not os.path.exists(FOLDER_ARTIKEL): os.makedirs(FOLDER_ARTIKEL)
        if not os.path.exists(FOLDER_IMG): os.makedirs(FOLDER_IMG)
        
        driver = setup_driver()
        
        # 1. SCRAPING
        print("🕵️  [1/4] Scraping Google Maps...")
        url = f"https://www.google.com/maps/search/{KEYWORD_PENCARIAN.replace(' ', '+')}/"
        driver.get(url)
        time.sleep(5)
        
        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        database_wisata = []
        try: stok_foto = [f for f in os.listdir(FOLDER_IMG) if f.endswith(('.jpg', '.jpeg', '.png'))]
        except: stok_foto = []
        if not stok_foto: stok_foto = ["default.jpg"]
        
        for card in cards[:3]: 
            try:
                link_tag = card.find_element(By.TAG_NAME, "a")
                nama = link_tag.get_attribute("aria-label")
                if not nama: continue
                data = {
                    "nama": nama,
                    "deskripsi": f"Wisata {nama} di Pangalengan.",
                    "gambar": random.choice(stok_foto),
                    "link_maps": link_tag.get_attribute("href"),
                    "wa_admin": WA_ADMIN
                }
                database_wisata.append(data)
            except: continue
        driver.quit() 

        # Data Paket Dummy
        data_paket = [{
            "nama_paket": "Open Trip Nimo", "harga_mentah": "Rp 300rb",
            "keterangan_termasuk": "Tiket | Makan", "deskripsi_seo": "Paket murah."
        }]
        
        # 2. AI ENRICHMENT
        print("\n🤖 [3/5] Rewrite Deskripsi (Nano AI)...")
        for data in database_wisata:
            data['deskripsi'] = rewrite_deskripsi_dengan_ai(data['deskripsi'], data['nama'])
            
        # 3. AI ARTIKEL
        print("\n📝 [4/5] Menulis Artikel (Nano AI)...")
        for judul in KEYWORD_ARTIKEL:
            print(f"   -> Nulis: {judul}...")
            isi_artikel = generate_seo_article(judul)
            if isi_artikel:
                nama_file = re.sub(r'[^a-z0-9\-]', '', judul.lower().replace(' ', '-'))[:50]
                with open(f"{FOLDER_ARTIKEL}/{nama_file}.html", "w", encoding="utf-8") as f:
                    f.write(f"<h1>{judul}</h1>{isi_artikel}")
                print(f"      ✅ Berhasil.")

        # 4. GENERATE HTML
        print("\n⚙️  [5/5] Update Tampilan Web...")
        html = f"""
        <html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>body{{font-family:sans-serif;padding:20px}} .card{{border:1px solid #ccc;padding:10px;margin:10px;border-radius:8px}}</style>
        </head>
        <body><h1>Wisata Pangalengan (Update: {datetime.datetime.now()})</h1>
        <h2>Paket Wisata</h2>
        {''.join([f"<div class='card'><h3>{p['nama_paket']}</h3><p>{p['deskripsi_seo']}</p></div>" for p in data_paket])}
        <h2>Destinasi</h2>
        {''.join([f"<div class='card'><h3>{w['nama']}</h3><p>{w['deskripsi']}</p></div>" for w in database_wisata])}
        </body></html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)
        print("\n✅ Script Selesai. Menunggu GitHub menyimpan file...")

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
