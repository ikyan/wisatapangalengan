import time
import json
import os
import re
import random
import datetime
import requests
import traceback
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# =======================================================
#               KONFIGURASI JURAGAN
# =======================================================
LOCAL_MODEL = "qwen2.5:1.5b" 
BASE_URL = "https://https://wisatapangalengan.my.id/" 

# 👇 1. KODE VERIFIKASI GOOGLE (WAJIB DIGANTI!)
GOOGLE_VERIFICATION_CODE = "EM2BTQp-XvvFG9bK69Z0BQSYNLiSb3ryIzbr5jMUNqQ"

# 👇 2. NOMOR WA ADMIN (Ganti dengan nomor lo, pakai 62)
WA_ADMIN = "6285156098112"

KEYWORD_PENCARIAN = "Tempat Wisata di Pangalengan"
FOLDER_IMG = "img"
FOLDER_ARTIKEL = "artikel" 
AUTO_UPLOAD_GITHUB = False 

KEYWORD_ARTIKEL = [
    "5 Spot Healing Terbaik di Kebun Teh Pangalengan",
    "Rekomendasi Tempat Camping Keluarga di Pinggir Danau Pangalengan",
    "Panduan Lengkap Liburan ke Nimo Highland dan Wayang Windu",
    "Daftar Harga Tiket Masuk Tempat Wisata di Pangalengan 2025"
]

# =======================================================
#               CSS & DESAIN PREMIUM (THE MAGIC)
# =======================================================
# Ini "Baju Mahal" buat website lo. Jangan diubah kalau gak ngerti CSS.
PREMIUM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    :root { --primary: #047857; --secondary: #064e3b; --accent: #10b981; --bg: #f0fdf4; --text: #1e293b; }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
    
    /* NAVIGATION */
    nav { background: white; padding: 15px 5%; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }
    .logo { font-weight: 800; font-size: 1.5rem; color: var(--primary); text-decoration: none; }
    .nav-btn { background: var(--primary); color: white; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: 600; transition: 0.3s; }
    .nav-btn:hover { background: var(--secondary); box-shadow: 0 5px 15px rgba(4, 120, 87, 0.3); }

    /* HERO SECTION */
    header { 
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1596401057633-56565355e1db?w=1600&q=80');
        background-size: cover; background-position: center; color: white; 
        padding: 100px 20px; text-align: center; border-radius: 0 0 50px 50px; margin-bottom: 50px;
    }
    header h1 { font-size: 2.5rem; margin-bottom: 15px; font-weight: 800; letter-spacing: -1px; }
    header p { font-size: 1.1rem; opacity: 0.9; max-width: 600px; margin: 0 auto 30px; }
    
    /* LAYOUT */
    .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
    .section-head { text-align: center; margin-bottom: 40px; }
    .section-head h2 { font-size: 2rem; color: var(--secondary); margin-bottom: 10px; }
    .section-head span { background: #d1fae5; color: var(--primary); padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; font-weight: 600; }

    /* GRID SYSTEM */
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 80px; }
    
    /* CARDS */
    .card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.05); transition: transform 0.3s, box-shadow 0.3s; border: 1px solid rgba(0,0,0,0.05); display: flex; flex-direction: column; }
    .card:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
    .card-img { height: 200px; width: 100%; object-fit: cover; }
    .card-body { padding: 25px; flex-grow: 1; display: flex; flex-direction: column; }
    .card-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 10px; color: var(--text); }
    .card-text { font-size: 0.95rem; color: #64748b; margin-bottom: 20px; flex-grow: 1; }
    .price { font-size: 1.5rem; color: #ef4444; font-weight: 800; margin-bottom: 15px; display: block; }
    
    /* BUTTONS */
    .btn { display: block; width: 100%; text-align: center; padding: 12px 0; border-radius: 12px; text-decoration: none; font-weight: 600; transition: 0.3s; }
    .btn-primary { background: var(--primary); color: white; }
    .btn-primary:hover { background: var(--secondary); }
    .btn-outline { border: 2px solid #cbd5e1; color: var(--text); background: transparent; }
    .btn-outline:hover { border-color: var(--primary); color: var(--primary); }

    /* FOOTER */
    footer { background: white; padding: 50px 20px; text-align: center; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.9rem; margin-top: 50px; }
    
    /* RESPONSIVE */
    @media (max-width: 768px) { header h1 { font-size: 2rem; } .grid { grid-template-columns: 1fr; } }
</style>
"""

# =======================================================
#               FUNGSI AI (OLLAMA)
# =======================================================
def call_ollama_nano(prompt):
    url = "http://127.0.0.1:11434/api/generate"
    # Prompt Engineering biar hasilnya kayak Sales Profesional
    full_prompt = f"Kamu adalah copywriter wisata profesional. Gunakan bahasa Indonesia yang persuasif, gaul, dan menjual. {prompt}"
    payload = { "model": LOCAL_MODEL, "prompt": full_prompt, "stream": False }
    try:
        response = requests.post(url, json=payload, timeout=300) 
        if response.status_code == 200:
            hasil = response.json()['response']
            return hasil.strip().replace('**', '').replace('*', '').replace('## ', '').replace('### ', '')
        return None
    except: return None

def rewrite_deskripsi_dengan_ai(deskripsi_awal, nama_tempat):
    prompt = f"Buat deskripsi singkat 25 kata yang bikin orang pengen banget liburan ke: {nama_tempat}. Data mentah: {deskripsi_awal}."
    res = call_ollama_nano(prompt)
    return res if res else deskripsi_awal

def generate_seo_article(judul_artikel):
    prompt = f"Tulis artikel blog wisata 350 kata dengan judul '{judul_artikel}'. Gunakan tag <h2> untuk subjudul. Fokus pada tips dan info harga."
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
        print(f"🚀 START AUTOPILOT (PREMIUM MODE)...\n")
        
        if not os.path.exists(FOLDER_ARTIKEL): os.makedirs(FOLDER_ARTIKEL)
        if not os.path.exists(FOLDER_IMG): os.makedirs(FOLDER_IMG)
        
        driver = setup_driver()
        
        # --- 1. SCRAPING GOOGLE MAPS ---
        print("🕵️  [1/4] Scraping Data Wisata...")
        url = f"https://www.google.com/maps/search/{KEYWORD_PENCARIAN.replace(' ', '+')}/"
        driver.get(url)
        time.sleep(5)
        
        cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
        database_wisata = []
        
        # Stok foto HD biar web gak burik
        stok_foto = [
            "https://images.unsplash.com/photo-1596401057633-56565355e1db?w=800&q=80",
            "https://images.unsplash.com/photo-1534234828563-02597793cba3?w=800&q=80", 
            "https://images.unsplash.com/photo-1629196914375-f7e48f477b6d?w=800&q=80",
            "https://images.unsplash.com/photo-1544983220-4b21915df842?w=800&q=80"
        ]
        
        for card in cards[:6]: 
            try:
                link_tag = card.find_element(By.TAG_NAME, "a")
                nama = link_tag.get_attribute("aria-label")
                if not nama: continue
                data = {
                    "nama": nama,
                    "deskripsi": f"Nikmati keindahan {nama} di Pangalengan.",
                    "gambar": random.choice(stok_foto),
                    "link_maps": link_tag.get_attribute("href"),
                }
                database_wisata.append(data)
            except: continue
        driver.quit() 

        # Data Paket (Lo bisa edit ini sesuka hati buat markup harga)
        data_paket = [
            {"nama": "Open Trip Nimo Highland", "harga": "Rp 350.000", "fasilitas": "Tiket + Transport + Makan", "desc": "Paket Best Seller! Seharian puas main di jembatan kaca viral."},
            {"nama": "Camping Cileunca 2D1N", "harga": "Rp 250.000", "fasilitas": "Tenda + BBQ + Perahu", "desc": "Malam syahdu di pinggir danau, lengkap dengan api unggun."}
        ]
        
        # --- 2. AI ENRICHMENT ---
        print("\n🤖 [2/4] Memoles Deskripsi...")
        for data in database_wisata:
            data['deskripsi'] = rewrite_deskripsi_dengan_ai(data['deskripsi'], data['nama'])

        # --- 3. BLOG GENERATOR ---
        print("\n📝 [3/4] Menulis Blog SEO...")
        list_artikel_html = ""
        sitemap_urls = ""
        
        for judul in KEYWORD_ARTIKEL:
            nama_file = re.sub(r'[^a-z0-9\-]', '', judul.lower().replace(' ', '-'))[:50] + ".html"
            path_file = f"{FOLDER_ARTIKEL}/{nama_file}"
            
            # Cek file biar gak generate ulang kalau udah ada
            if not os.path.exists(path_file):
                print(f"   -> Nulis: {judul}...")
                isi = generate_seo_article(judul)
                if isi:
                    # Template Halaman Artikel (Juga Premium)
                    html_artikel = f"""
                    <!DOCTYPE html><html lang="id"><head>
                    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>{judul}</title>{PREMIUM_CSS}
                    </head><body>
                    <nav><a href="../index.html" class="logo">🌲 Wisata Pangalengan</a><a href="https://wa.me/{WA_ADMIN}" class="nav-btn">Chat Admin</a></nav>
                    <div class="container" style="margin-top:50px; max-width:800px;">
                        <a href="../index.html" style="text-decoration:none; color:var(--primary); font-weight:600;">← Kembali</a>
                        <h1 style="font-size:2.5rem; margin-top:20px;">{judul}</h1>
                        <div class="card" style="padding:40px; margin-top:30px;">{isi}</div>
                        <div style="text-align:center; margin-top:50px;">
                            <h3>Tertarik liburan ke sini?</h3>
                            <a href="https://wa.me/{WA_ADMIN}" class="nav-btn" style="display:inline-block; margin-top:10px;">Booking Sekarang</a>
                        </div>
                    </div>
                    <footer>© 2025 Wisata Pangalengan.</footer>
                    </body></html>
                    """
                    with open(path_file, "w", encoding="utf-8") as f: f.write(html_artikel)

            # Masukkan ke list untuk Homepage & Sitemap
            if os.path.exists(path_file):
                judul_bersih = judul # Judul asli lebih bagus
                list_artikel_html += f"""
                <div class="card">
                    <div class="card-body">
                        <span style="font-size:0.8rem; color:var(--primary); font-weight:700;">TIPS & INFO</span>
                        <h3 class="card-title">{judul_bersih}</h3>
                        <p class="card-text">Baca panduan lengkap agar liburanmu makin seru...</p>
                        <a href="artikel/{nama_file}" class="btn btn-outline">📖 Baca Artikel</a>
                    </div>
                </div>
                """
                sitemap_urls += f"<url><loc>{BASE_URL}/artikel/{nama_file}</loc><lastmod>{datetime.date.today()}</lastmod></url>"

        # --- 4. BUILD HOMEPAGE & SITEMAP ---
        print("\n⚙️  [4/4] Finishing Touch...")
        
        # Buat Sitemap XML
        sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{BASE_URL}/index.html</loc><lastmod>{datetime.date.today()}</lastmod></url>{sitemap_urls}</urlset>"""
        with open("sitemap.xml", "w", encoding="utf-8") as f: f.write(sitemap_content)

        # Generate Kartu Paket
        paket_html = ""
        for p in data_paket:
            paket_html += f"""
            <div class="card" style="border-top: 5px solid var(--accent);">
                <div class="card-body">
                    <div style="background:#fee2e2; color:#b91c1c; font-size:0.8rem; font-weight:700; display:inline-block; padding:5px 10px; border-radius:50px; margin-bottom:15px;">🔥 TERLARIS</div>
                    <h3 class="card-title">{p['nama']}</h3>
                    <span class="price">{p['harga']}</span>
                    <p class="card-text">{p['desc']}</p>
                    <p style="font-size:0.9rem; margin-bottom:20px;">✅ {p['fasilitas']}</p>
                    <a href="https://wa.me/{WA_ADMIN}?text=Halo, saya mau booking {p['nama']}" class="btn btn-primary">📱 Booking via WhatsApp</a>
                </div>
            </div>
            """
            
        # Generate Kartu Destinasi
        destinasi_html = ""
        for w in database_wisata:
            destinasi_html += f"""
            <div class="card">
                <img src="{w['gambar']}" alt="{w['nama']}" class="card-img">
                <div class="card-body">
                    <h3 class="card-title">{w['nama']}</h3>
                    <p class="card-text">{w['deskripsi']}</p>
                    <a href="{w['link_maps']}" target="_blank" class="btn btn-outline">📍 Lihat Lokasi</a>
                </div>
            </div>
            """

        # HTML UTAMA (HOMEPAGE)
        full_html = f"""
        <!DOCTYPE html><html lang="id"><head>
            <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="google-site-verification" content="{GOOGLE_VERIFICATION_CODE}" />
            <meta name="description" content="Portal wisata Pangalengan terbaik. Temukan paket open trip, camping, dan info tiket masuk Nimo Highland 2025.">
            <title>Wisata Pangalengan - Healing Terbaik 2025</title>
            {PREMIUM_CSS}
        </head><body>
            <nav>
                <a href="#" class="logo">🌲 Wisata Pangalengan</a>
                <a href="https://wa.me/{WA_ADMIN}" class="nav-btn">Chat Admin</a>
            </nav>
            
            <header>
                <div class="container">
                    <h1>Temukan Surga Tersembunyi di Bandung Selatan</h1>
                    <p>Lupakan penat kota. Nikmati udara sejuk kebun teh, danau purba, dan petualangan seru bersama kami.</p>
                    <a href="#paket" class="nav-btn" style="background:white; color:var(--primary);">Lihat Paket Hemat ⬇️</a>
                </div>
            </header>
            
            <div class="container">
                <div id="paket" class="section-head">
                    <span>HEMAT & PRAKTIS</span>
                    <h2>📦 Paket Wisata Pilihan</h2>
                    <p>Tinggal bawa badan, semua kami yang urus.</p>
                </div>
                <div class="grid">{paket_html}</div>
                
                <div class="section-head">
                    <span>POPULER</span>
                    <h2>🗺️ Destinasi Wajib Dikunjungi</h2>
                </div>
                <div class="grid">{destinasi_html}</div>

                <div class="section-head">
                    <span>BLOG & TIPS</span>
                    <h2>📰 Info Terbaru 2025</h2>
                </div>
                <div class="grid">{list_artikel_html}</div>
                
                <div style="background: white; padding: 50px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 50px;">
                    <h2>Kenapa Booking di Sini?</h2>
                    <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 30px; margin-top: 30px;">
                        <div style="max-width: 250px;">
                            <h3 style="color:var(--primary);">⚡ Fast Respon</h3>
                            <p>Admin standby buat jawab semua pertanyaanmu.</p>
                        </div>
                        <div style="max-width: 250px;">
                            <h3 style="color:var(--primary);">💰 Harga Jujur</h3>
                            <p>Gak ada biaya tersembunyi. Apa yang dilihat, itu yang dibayar.</p>
                        </div>
                        <div style="max-width: 250px;">
                            <h3 style="color:var(--primary);">🤝 Lokal Partner</h3>
                            <p>Kami bekerjasama langsung dengan warga lokal Pangalengan.</p>
                        </div>
                    </div>
                </div>
            </div>
            
            <footer>
                <p>© {datetime.datetime.now().year} Wisata Pangalengan. Portal Resmi Partner Liburanmu.</p>
                <p style="font-size:0.8rem; margin-top:10px;">Powered by GitHub & AI Autopilot.</p>
            </footer>
        </body></html>
        """

        with open("index.html", "w", encoding="utf-8") as f: f.write(full_html)
        print("\n✅ WEBSITE PREMIUM BERHASIL DIUPDATE!")

    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    main()
