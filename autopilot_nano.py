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

# 👇 GANTI DENGAN URL WEBSITE LO YANG ASLI (JANGAN SALAH KETIK)
BASE_URL = "https://www.wisatapangalengan.my.id/" 

# 👇 PASTE KODE VERIFIKASI GOOGLE DARI GSC DI SINI (Cuma kodenya aja, yg ada di content="")
GOOGLE_VERIFICATION_CODE = "EM2BTQp-XvvFG9bK69Z0BQSYNLiSb3ryIzbr5jMUNqQ"

KEYWORD_PENCARIAN = "Tempat Wisata di Pangalengan"
FOLDER_IMG = "img"
FOLDER_ARTIKEL = "artikel" 
WA_ADMIN = "6285156098112" 
AUTO_UPLOAD_GITHUB = False 

KEYWORD_ARTIKEL = [
    "5 Spot Healing Terbaik di Kebun Teh Pangalengan",
    "Rekomendasi Tempat Camping Keluarga di Pinggir Danau Pangalengan",
    "Panduan Lengkap Liburan ke Nimo Highland dan Wayang Windu",
    "Daftar Harga Tiket Masuk Tempat Wisata di Pangalengan 2025"
]

# =======================================================
#               FUNGSI AI
# =======================================================

def call_ollama_nano(prompt):
    url = "http://127.0.0.1:11434/api/generate"
    full_prompt = f"Kamu adalah travel writer profesional. Jawab singkat padat menarik. {prompt}"
    payload = { "model": LOCAL_MODEL, "prompt": full_prompt, "stream": False }
    try:
        response = requests.post(url, json=payload, timeout=300) 
        if response.status_code == 200:
            hasil = response.json()['response']
            return hasil.strip().replace('**', '').replace('*', '').replace('## ', '').replace('### ', '')
        return None
    except: return None

def rewrite_deskripsi_dengan_ai(deskripsi_awal, nama_tempat):
    prompt = f"Buat deskripsi singkat 20 kata yang 'mengundang' untuk: {nama_tempat}. Data: {deskripsi_awal}."
    res = call_ollama_nano(prompt)
    return res if res else deskripsi_awal

def generate_seo_article(judul_artikel):
    prompt = f"Tulis artikel blog wisata 300 kata judul '{judul_artikel}'. Gunakan tag <h2> untuk subjudul."
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
        print(f"🚀 START AUTOPILOT (SEO MODE)...\n")
        
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
        
        stok_foto_online = [
            "https://images.unsplash.com/photo-1596401057633-56565355e1db?w=500&q=80",
            "https://images.unsplash.com/photo-1534234828563-02597793cba3?w=500&q=80", 
            "https://images.unsplash.com/photo-1629196914375-f7e48f477b6d?w=500&q=80", 
        ]
        
        for card in cards[:6]: 
            try:
                link_tag = card.find_element(By.TAG_NAME, "a")
                nama = link_tag.get_attribute("aria-label")
                if not nama: continue
                gambar = random.choice(stok_foto_online)
                data = {
                    "nama": nama,
                    "deskripsi": f"Nikmati keindahan {nama} di Pangalengan.",
                    "gambar": gambar,
                    "link_maps": link_tag.get_attribute("href"),
                    "wa_admin": WA_ADMIN
                }
                database_wisata.append(data)
            except: continue
        driver.quit() 

        data_paket = [
            {"nama": "Open Trip Nimo Highland", "harga": "Rp 350.000", "fasilitas": "Tiket + Transport + Makan", "desc": "Paket paling laku! Seharian puas main di jembatan kaca."},
            {"nama": "Camping Cileunca 2D1N", "harga": "Rp 250.000", "fasilitas": "Tenda + BBQ + Perahu", "desc": "Malam syahdu di pinggir danau, api unggun & jagung bakar."}
        ]
        
        # 2. AI ENRICHMENT
        print("\n🤖 [2/4] Mempercantik Kata-kata...")
        for data in database_wisata:
            data['deskripsi'] = rewrite_deskripsi_dengan_ai(data['deskripsi'], data['nama'])

        # 3. GENERATE HTML & SITEMAP
        print("\n⚙️  [3/4] Build Web & Sitemap XML...")
        
        # --- GENERATE SITEMAP XML ---
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url>
                <loc>{BASE_URL}/index.html</loc>
                <lastmod>{datetime.date.today()}</lastmod>
                <priority>1.0</priority>
            </url>
        """
        
        # List Artikel yang ada
        list_artikel = [f for f in os.listdir(FOLDER_ARTIKEL) if f.endswith('.html')]
        for f in list_artikel:
            sitemap_content += f"""
            <url>
                <loc>{BASE_URL}/artikel/{f}</loc>
                <lastmod>{datetime.date.today()}</lastmod>
                <priority>0.8</priority>
            </url>
            """
        sitemap_content += "</urlset>"
        
        with open("sitemap.xml", "w", encoding="utf-8") as f:
            f.write(sitemap_content)
        print("      ✅ Sitemap.xml berhasil dibuat.")

        # --- GENERATE INDEX HTML (WITH GOOGLE VERIFICATION) ---
        style_css = """
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
                body { font-family: 'Poppins', sans-serif; background-color: #f8fafc; margin: 0; padding: 0; color: #334155; }
                .hero {
                    background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), url('https://images.unsplash.com/photo-1544983220-4b21915df842?w=1600&q=80');
                    background-size: cover; background-position: center; color: white; text-align: center; padding: 120px 20px;
                    border-radius: 0 0 40px 40px; margin-bottom: 50px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }
                .hero h1 { font-size: 3rem; margin: 0; font-weight: 600; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }
                .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
                .section-title { font-size: 1.8rem; color: #0f172a; margin-bottom: 30px; border-left: 5px solid #10b981; padding-left: 15px; font-weight: 600; }
                .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 30px; margin-bottom: 60px; }
                .card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.05); transition: transform 0.3s ease; }
                .card:hover { transform: translateY(-5px); }
                .card img { width: 100%; height: 220px; object-fit: cover; }
                .card-body { padding: 25px; }
                .btn { display: block; width: 100%; text-align: center; padding: 12px 0; border-radius: 12px; font-weight: 600; text-decoration: none; margin-top: 15px; }
                .btn-wa { background: #22c55e; color: white; }
                footer { text-align: center; padding: 50px 20px; color: #94a3b8; font-size: 0.9rem; border-top: 1px solid #e2e8f0; }
            </style>
        """
        
        paket_html = ""
        for p in data_paket:
            paket_html += f"""
            <div class="card"><div class="card-body"><h3>{p['nama']}</h3><h2 style="color:#ef4444;">{p['harga']}</h2><p>{p['desc']}</p>
            <a href="https://wa.me/{WA_ADMIN}" class="btn btn-wa">📱 Booking</a></div></div>"""
            
        destinasi_html = ""
        for w in database_wisata:
            destinasi_html += f"""
            <div class="card"><img src="{w['gambar']}"><div class="card-body"><h3>{w['nama']}</h3><p>{w['deskripsi']}</p></div></div>"""

        full_html = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="google-site-verification" content="{GOOGLE_VERIFICATION_CODE}" />
            <title>Wisata Pangalengan - Healing Terbaik</title>
            {style_css}
        </head>
        <body>
            <div class="hero"><h1>🌲 Explore Pangalengan</h1><p>Update: {datetime.datetime.now().strftime("%d %B %Y")}</p></div>
            <div class="container">
                <h2 class="section-title">📦 Paket Wisata</h2><div class="grid">{paket_html}</div>
                <h2 class="section-title">🗺️ Destinasi</h2><div class="grid">{destinasi_html}</div>
            </div>
            <footer><p>© {datetime.datetime.now().year} Wisata Pangalengan.</p></footer>
        </body></html>
        """

        with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)
        print("\n✅ WEBSITE + SITEMAP BERHASIL DIBUAT!")

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
