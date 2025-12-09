import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def scrape_google_maps():
    print("🤖 MEMULAI OPERASI SCRAPING PANGALENGAN...")
    
    # 1. Setup Chrome Driver
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Aktifkan ini kalau mau jalan di background (tanpa buka window)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # 2. Buka Link Pencarian
    keyword = "Tempat Wisata di Pangalengan"
    url = f"https://www.google.com/maps/search/{keyword.replace(' ', '+')}/"
    driver.get(url)
    
    print("⏳ Menunggu loading Maps...")
    time.sleep(5) 

    # 3. Logic Scroll Otomatis (Penting!)
    # Kita harus scroll panel kiri (role='feed') biar data lainnya keload
    try:
        # Cari panel yang bisa discroll
        scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
        
        print("⬇️ Sedang scroll ke bawah mencari harta karun...")
        # Scroll sebanyak 10 kali (bisa ditambah kalau mau lebih banyak data)
        for i in range(10): 
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
            time.sleep(2) # Kasih napas biar gak dikira robot jahat
            print(f"   Scroll {i+1}/10 selesai...")
    except Exception as e:
        print("⚠️ Gagal scroll otomatis (Mungkin layout Google berubah), mengambil data yang terlihat saja.")

    # 4. Mulai Panen Data
    print("🕵️ Mengambil detail tempat...")
    
    results = []
    # Selector "a.hfpxzc" adalah class link utama di list maps (bisa berubah sewaktu-waktu)
    items = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
    
    # Kita cari juga elemen rating (biasanya kelasnya 'MW4etd') - ini triky karena terpisah
    # Jadi kita ambil data basic dulu dari linknya
    
    for item in items:
        try:
            nama = item.get_attribute("aria-label")
            link_maps = item.get_attribute("href")
            
            # Filter: Jangan ambil yang gak ada namanya
            if not nama:
                continue

            print(f"   ✅ Dapat: {nama}")
            
            # Coba cari gambar thumbnail (opsional)
            # Karena struktur DOM Maps rumit, kita pake trik sederhana:
            # Biasanya gambar ada di parent element yang sama, tapi karena susah ditarik di list view,
            # Kita set placeholder dulu, atau lo bisa manual update fotonya nanti.
            
            data = {
                "nama": nama,
                "deskripsi": f"Destinasi hits di Pangalengan. Rating tinggi di Google Maps.",
                "tiket": "Hubungi Admin", # Maps gak kasih info tiket
                "gambar": "wayang.jpg",   # Default dulu (Nanti gw ajarin cara otomatis gambarnya)
                "rating_maps": "⭐ 4.5+", # Hardcode dulu biar cantik, atau scrape detail kalau mau berat
                "link_google": link_maps,
                "wa_admin": "62812345678" # Ganti nomor lo disini
            }
            results.append(data)
            
        except Exception as e:
            print(f"   ❌ Error ambil satu item: {e}")
            continue

    driver.quit()
    
    # 5. Simpan Hasil ke JSON
    print(f"\n💾 Menyimpan {len(results)} lokasi ke data.json...")
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print("🎉 MISI SUKSES! File 'data.json' siap dipakai di generator.")

if __name__ == "__main__":
    scrape_google_maps()