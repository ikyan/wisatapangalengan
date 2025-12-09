import time
import json
import os
import re
import random
import datetime
import requests
from bs4 import BeautifulSoup

# --- IMPORT KHUSUS ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from google import genai
# Note: APIError harus diimport dari 'google.generativeai.errors'
 

# =======================================================
#               KONFIGURASI PENTING
# =======================================================
KEYWORD_PENCARIAN = "Tempat Wisata di Pangalengan"
FOLDER_IMG = "img"
WA_ADMIN = "6285156098112"  # <<< GANTI DENGAN NOMOR WHATSAPP LO
AUTO_UPLOAD_GITHUB = False # <<< Ubah True kalau git di laptop sudah disetup

# =======================================================
#               FUNGSI BANTUAN
# =======================================================

def rewrite_deskripsi_dengan_ai(deskripsi_awal, nama_tempat):
    """Menggunakan Gemini AI untuk membuat deskripsi unik."""
    if not os.getenv("AIzaSyCLvHuYxuhMucfSDV-gnPQy_p5eDFYBRTA"):
        print(f"   [AI Skip] API Key tidak ditemukan. Menggunakan deskripsi mentah.")
        return deskripsi_awal
        
    try:
        client = genai.Client() 
        prompt = (
            f"Tulis ulang deskripsi ini menjadi 3 paragraf pendek (maks 50 kata). "
            f"Gunakan gaya bahasa santai dan fokus pada nilai jual 'healing' di area sejuk kebun teh. "
            f"Deskripsi awal: '{deskripsi_awal}'. Nama tempat: {nama_tempat}."
        )
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            safety_settings=None 
        )
        return response.text.strip().replace('**', '').replace('*', '') 
    except APIError:
        return deskripsi_awal
    except Exception:
        return deskripsi_awal

def setup_driver():
    """Setup Selenium WebDriver."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

# =======================================================
#               SCRAPER
# =======================================================

def scrape_google_maps(driver):
    """Scrape data lokasi dari Google Maps."""
    print("🕵️  [1/4] Scraping lokasi dari Google Maps...")
    
    url = f"https://www.google.com/maps/search/{KEYWORD_PENCARIAN.replace(' ', '+')}/"
    driver.get(url)
    time.sleep(5)

    try:
        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        for i in range(5): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2)
    except:
        pass

    cards = driver.find_elements(By.CLASS_NAME, "Nv2PK")
    database_wisata = []
    
    try:
        stok_foto = [f for f in os.listdir(FOLDER_IMG) if f.endswith(('.jpg', '.jpeg', '.png'))]
    except:
        stok_foto = []
        
    if not stok_foto:
        stok_foto = ["default.jpg"]

    for card in cards:
        try:
            link_tag = card.find_element(By.TAG_NAME, "a")
            nama = link_tag.get_attribute("aria-label")
            if not nama: continue

            data = {
                "nama": nama,
                "deskripsi": f"Destinasi wisata populer {nama} di kawasan Pangalengan.",
                "tiket": "Hubungi Admin",
                "gambar": random.choice(stok_foto),
                "link_maps": link_tag.get_attribute("href"),
                "wa_admin": WA_ADMIN
            }
            database_wisata.append(data)
        except:
            continue
            
    return database_wisata

def scrape_paket_kompetitor():
    """ATM Paket Wisata dari kompetitor menggunakan BeautifulSoup."""
    print("🕵️  [2/4] ATM Paket Wisata Kompetitor...")
    url = "https://wisatapangalengan.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except:
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    paket_list = []
    
    wa_buttons = soup.find_all('a', string=re.compile(r'WhatsApp Booking|Konsultasi WhatsApp', re.I))
    
    for button in wa_buttons:
        try:
            card = button.find_parent('div').find_parent('div') 
            
            nama_tag = card.find(['h3', 'h2', 'p', 'strong'], string=lambda t: t and len(t.strip()) > 5)
            nama_paket = nama_tag.text.strip() if nama_tag else "Nama Paket Tidak Ditemukan"
            
            harga_tag = card.find(string=re.compile(r'Rp\.[\d,\.]+', re.I))
            harga = harga_tag.strip() if harga_tag else "Harga Tidak Ditemukan"
            
            keterangan_mentah = [p.text.strip() for p in card.find_all(['p', 'li']) if p.text.strip() and not p.text.strip().lower().startswith(('rp', 'wa', 'whatsapp', 'mulai'))]
            keterangan_termasuk = " | ".join(keterangan_mentah[:5])
            
            paket_list.append({
                "nama_paket": nama_paket,
                "harga_mentah": harga,
                "keterangan_termasuk": keterangan_termasuk,
                "deskripsi_seo": f"Paket {nama_paket}. Harga {harga}. Item termasuk: {keterangan_termasuk}."
            })
        except:
            continue

    return paket_list


# =======================================================
#               FUNGSI UTAMA (MAIN)
# =======================================================

def main():
    # --- GLOBAL TRY-EXCEPT UNTUK MENCEGAH CRASH DIAM-DIAM ---
    try:
        print("🚀 MEMULAI SISTEM AUTOPILOT. Cek status di log...\n")
        
        # 0. Setup Awal
        # Inisialisasi driver hanya jika kita akan melakukan scraping Selenium
        driver = setup_driver()
        
        # 1. SCRAPING
        data_lokasi = scrape_google_maps(driver)
        driver.quit() # Tutup driver setelah selesai
        data_paket = scrape_paket_kompetitor()
        
        # 2. AI ENRICHMENT
        print("\n🤖 [3/4] Memperkaya deskripsi menggunakan Gemini AI...")
        
        # Rewrite Lokasi
        for data in data_lokasi:
            data['deskripsi'] = rewrite_deskripsi_dengan_ai(data['deskripsi'], data['nama'])
        
        # Rewrite Paket
        for paket in data_paket:
            prompt_paket = f"Tulis ulang deskripsi paket wisata '{paket['nama_paket']}' ini agar menarik, fokus pada nilai jual 'petualangan' dan 'healing' di Pangalengan. Termasuk: {paket['keterangan_termasuk']}."
            paket['deskripsi_seo'] = rewrite_deskripsi_dengan_ai(prompt_paket, paket['nama_paket'])

        print(f"✅ AI Enrichment selesai. {len(data_lokasi)} lokasi dan {len(data_paket)} paket siap.")


        # 3. GENERATE HTML (FIXED SYNTAX)
        print("\n⚙️  [4/4] Merakit HTML dan Deploy...")
        
        # --- GENERATE CARD HTML DILUAR F-STRING UTAMA ---
        
        # A. Paket Cards
        paket_cards_html = ""
        for p in data_paket:
            wa_message = f"Halo Admin, saya tertarik dengan paket {p['nama_paket']} ({p['harga_mentah']}). Mohon info detailnya."
            link_wa = f"https://wa.me/{WA_ADMIN}?text={wa_message.replace(' ', '%20')}"
            
            paket_cards_html += f"""
                <div class="package-card" style="width: 300px;">
                    <h3>{p['nama_paket']}</h3>
                    <p class="price">{p['harga_mentah']}</p>
                    <p style="font-size: 0.9em;">{p['deskripsi_seo']}</p>
                    <p style="margin-top: 10px;">✅ **Termasuk:** {p['keterangan_termasuk'].split('|')[0]}</p>
                    <a href="{link_wa}" class="btn">BOOKING SEKARANG</a>
                </div>
            """
        
        # B. Lokasi Cards
        lokasi_cards_html = ""
        for w in data_lokasi:
            pesan = f"Halo admin, mau tanya info tiket dan lokasi untuk {w['nama']}."
            link_wa = f"https://wa.me/{WA_ADMIN}?text={pesan.replace(' ', '%20')}"
            
            lokasi_cards_html += f"""
            <div class="card">
                <img src="{FOLDER_IMG}/{w['gambar']}" alt="Foto {w['nama']}" loading="lazy" onerror="this.src='https://via.placeholder.com/400?text=Foto+Menyusul'">
                <div class="card-body">
                    <h3>{w['nama']}</h3>
                    <p>{w['deskripsi']}</p>
                    <a href="{link_wa}" class="btn">📱 Chat Admin / Info</a>
                </div>
            </div>
            """

        # --- GABUNGKAN SEMUA KE HTML UTAMA ---
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Wisata Pangalengan - Portal Resmi {datetime.datetime.now().year}</title>
            <meta name="description" content="Kumpulan tempat wisata dan paket tour terbaik di Pangalengan, di-update otomatis dan di-rewrite AI.">
            <style>
                body {{ font-family: sans-serif; background: #f3f4f6; margin: 0; padding: 20px; }}
                .container {{ max-width: 1000px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
                .header {{ grid-column: 1/-1; text-align: center; margin-bottom: 30px; background: #008080; color: white; padding: 20px; border-radius: 10px; }}
                .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .card img {{ width: 100%; height: 200px; object-fit: cover; }}
                .card-body {{ padding: 20px; }}
                .btn {{ display: block; width: 100%; background: #25D366; color: white; text-align: center; padding: 12px 0; text-decoration: none; border-radius: 8px; font-weight: bold; margin-top: 15px; }}
                .packages-section {{ grid-column: 1 / -1; margin-top: 20px; padding: 20px; background: #e6fffb; border-radius: 12px; }}
                .package-card {{ background: #ffffff; border: 1px solid #008080; padding: 15px; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .price {{ font-weight: bold; color: #e74c3c; font-size: 1.2rem; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌲 Portal Wisata Pangalengan (AI Powered)</h1>
                    <p>Update Terakhir: {datetime.datetime.now().strftime("%d %B %Y")}</p>
                </div>
        """
        
        # SECTION PAKET
        if data_paket:
            html_content += f"""
            <div class="packages-section">
                <h2 style="text-align: center; color: #008080;">Paket Paling Diminati (WAJIB COBA!)</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; justify-content: center;">
                    {paket_cards_html} 
                </div>
            </div>
            """

        # SECTION LOKASI
        html_content += f"""
            <div style="grid-column: 1 / -1; margin-top: 40px; text-align: center;">
                <h2>Destinasi Hits Pangalengan</h2>
            </div>
            {lokasi_cards_html}
            """
        
        html_content += "</div></body></html>"

        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # 4. SAVE JSON & DEPLOY
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data_lokasi, f, indent=4)
            
        if AUTO_UPLOAD_GITHUB:
            print("☁️  Mengupload ke GitHub (Auto Deploy)...")
            os.system("git add .")
            os.system('git commit -m "Auto content update (AI)"')
            os.system("git push origin main")
            print("✅  DEPLOY SUKSES! Web live.")
        else:
            print("\n✅  Script Selesai! Upload file index.html, data.json, dan folder img ke GitHub.")

    except Exception as e:
        # Ini akan menangkap SEMUA error dan mencetaknya
        print("\n🛑 ---------------------------------- 🛑")
        print("🛑 SCRIPT GAGAL TOTAL. INI PESAN ERRORNYA: 🛑")
        print("🛑 ---------------------------------- 🛑")
        import traceback
        traceback.print_exc()
        print(f"\nKesalahan Utama: {e}")
        print("\nPeriksa: 1. Koneksi internet. 2. ChromeDriver terinstall. 3. Semua library terinstall. 4. GEMINI_API_KEY sudah diset.")
# --- END OF MAIN LOGIC ---


if __name__ == "__main__":
    main()