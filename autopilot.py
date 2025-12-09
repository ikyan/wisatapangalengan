import os
import re
import random
import datetime

# =======================================================
#               DATA JURAGAN (SUDAH DIUPDATE)
# =======================================================
# 👇 DOMAIN BARU LO
BASE_URL = "https://www.wisatapangalengan.my.id" 

WA_ADMIN = "6285156098112"
GOOGLE_VERIFICATION_CODE = "EM2BTQp-XvvFG9bK69Z0BQSYNLiSb3ryIzbr5jMUNqQ"

FOLDER_ARTIKEL = "artikel"

# DAFTAR 20 JUDUL ARTIKEL (SIAP SEO)
LIST_JUDUL = [
    "Panduan Lengkap Wisata Nimo Highland 2025",
    "Harga Tiket Masuk Wayang Windu Panenjoan Terbaru",
    "Spot Sunrise Terbaik di Cukul Sunrise Point",
    "Paket Rafting Sungai Palayangan Murah Aman",
    "Rekomendasi Camping Pinggir Danau Cileunca",
    "Wisata Hutan Pinus Rahong yang Instagramable",
    "Pesona Taman Langit Pangalengan 360 Derajat",
    "Jelajah Kawah Wayang dan Pemandian Air Panas",
    "Nuansa Riung Gunung Swiss nya Bandung Selatan",
    "Sejarah dan Keindahan Kebun Teh Malabar",
    "5 Tempat Makan Enak dan Murah di Pangalengan",
    "Tips Liburan Hemat ke Pangalengan untuk Pemula",
    "Daftar Penginapan Villa Murah di Pangalengan",
    "Rute Jalan ke Pangalengan Bebas Macet",
    "Oleh oleh Khas Pangalengan yang Wajib Dibeli",
    "Kampung Singkur Wisata Air Viral",
    "Curug Panganten Air Terjun Tersembunyi",
    "Situ Datar Spot Healing Tenang",
    "Rumah Pengabdi Setan Lokasi Syuting Horror",
    "Paket Prewedding Outdoor di Pangalengan"
]

# STOK GAMBAR PREMIUM
STOK_FOTO = [
    "https://images.unsplash.com/photo-1596401057633-56565355e1db?w=800&q=80", # Kebun Teh
    "https://images.unsplash.com/photo-1534234828563-02597793cba3?w=800&q=80", # Danau
    "https://images.unsplash.com/photo-1629196914375-f7e48f477b6d?w=800&q=80", # Camping
    "https://images.unsplash.com/photo-1544983220-4b21915df842?w=800&q=80", # Kabut
    "https://images.unsplash.com/photo-1478131143081-80f7f84ca84d?w=800&q=80", # Camping 2
    "https://images.unsplash.com/photo-1501785888041-af3ef285b470?w=800&q=80"  # Alam
]

# =======================================================
#               DESAIN MEWAH (CSS PREMIUM)
# =======================================================
PREMIUM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700&display=swap');
    :root { --primary: #047857; --secondary: #064e3b; --accent: #10b981; --bg: #f8fafc; --text: #1e293b; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); line-height: 1.8; }
    
    /* NAVIGASI */
    nav { background: white; padding: 15px 5%; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 20px rgba(0,0,0,0.05); position: sticky; top: 0; z-index: 100; }
    .logo { font-weight: 800; font-size: 1.4rem; color: var(--primary); text-decoration: none; }
    .nav-btn { background: var(--primary); color: white; padding: 10px 20px; border-radius: 50px; text-decoration: none; font-weight: 600; transition: 0.3s; font-size: 0.9rem; }
    
    /* STYLE ARTIKEL */
    .article-header { 
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1596401057633-56565355e1db?w=1600&q=80');
        background-size: cover; background-position: center; color: white; 
        padding: 100px 20px; text-align: center; border-radius: 0 0 40px 40px; margin-bottom: -60px;
    }
    .container { max-width: 900px; margin: 0 auto; padding: 0 20px; position: relative; z-index: 10; }
    .content-box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); margin-bottom: 50px; }
    
    h1 { font-size: 2rem; margin-bottom: 10px; line-height: 1.3; }
    h2 { color: var(--primary); margin-top: 30px; margin-bottom: 15px; border-left: 5px solid var(--accent); padding-left: 15px; }
    p { margin-bottom: 15px; color: #475569; font-size: 1.05rem; }
    ul { margin-bottom: 20px; padding-left: 20px; color: #475569; }
    li { margin-bottom: 8px; }
    img.feat-img { width: 100%; border-radius: 15px; margin-bottom: 30px; height: 350px; object-fit: cover; }
    
    .cta-box { background: #ecfdf5; padding: 30px; border-radius: 15px; text-align: center; border: 2px dashed var(--accent); margin-top: 40px; }
    
    /* HOMEPAGE GRID */
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; }
    .card { background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 10px 20px rgba(0,0,0,0.03); border: 1px solid #e2e8f0; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.1); }
    .card-body { padding: 25px; }
    .card-title { font-size: 1.2rem; font-weight: 700; color: var(--text); margin-bottom: 10px; display: block; text-decoration: none; }
    .btn-outline { display: inline-block; padding: 8px 20px; border: 1px solid #cbd5e1; border-radius: 8px; text-decoration: none; color: var(--text); font-weight: 600; margin-top: 10px; }

    footer { text-align: center; padding: 40px; color: #94a3b8; border-top: 1px solid #e2e8f0; margin-top: 50px; }
</style>
"""

# =======================================================
#               ISIAN KONTEN PINTAR (TEMPLATE)
# =======================================================
def generate_content(judul):
    """Membuat isi artikel otomatis berdasarkan topik judul"""
    
    topik = "wisata alam"
    if "Tiket" in judul or "Harga" in judul: topik = "info tiket"
    elif "Rafting" in judul: topik = "rafting"
    elif "Camping" in judul: topik = "camping"
    elif "Penginapan" in judul or "Villa" in judul: topik = "penginapan"
    elif "Makan" in judul or "Kuliner" in judul: topik = "kuliner"

    intro = f"<p>Sedang mencari informasi lengkap tentang <strong>{judul}</strong>? Anda berada di halaman yang tepat. Pangalengan kini menjadi primadona wisata di Bandung Selatan yang menawarkan udara sejuk dan pemandangan kebun teh yang memanjakan mata.</p>"

    body_content = ""
    
    if topik == "info tiket":
        body_content = """
        <h2>Harga Tiket Masuk Terbaru 2025</h2>
        <p>Untuk menikmati destinasi ini, harga tiketnya masih sangat terjangkau bagi wisatawan lokal. Berikut estimasi biayanya:</p>
        <ul>
            <li><strong>Tiket Masuk:</strong> Rp 10.000 - Rp 35.000 per orang</li>
            <li><strong>Parkir Motor:</strong> Rp 5.000</li>
            <li><strong>Parkir Mobil:</strong> Rp 10.000</li>
        </ul>
        <p><em>Catatan: Harga bisa berubah sewaktu-waktu terutama saat High Season (Lebaran/Tahun Baru).</em></p>
        """
    elif topik == "rafting":
        body_content = """
        <h2>Keseruan Arung Jeram Sungai Palayangan</h2>
        <p>Sungai Palayangan menawarkan trek rafting sepanjang 5KM dengan grade aman untuk pemula maupun keluarga. Sumber air berasal dari Danau Cileunca sehingga debitnya stabil sepanjang tahun.</p>
        <h2>Fasilitas Paket Rafting</h2>
        <ul>
            <li>Perahu Karet Standard Safety (Avon/Zebec)</li>
            <li>Pelampung & Helm SNI</li>
            <li>Guide Profesional & Rescue Team</li>
            <li>Makan Siang & Dokumentasi Foto</li>
            <li>Asuransi Wisata</li>
        </ul>
        """
    elif topik == "camping":
        body_content = """
        <h2>Sensasi Camping di Tepi Danau</h2>
        <p>Bayangkan bangun pagi disambut kabut tipis yang menari di atas air danau. Camping di sini sangat cocok untuk <em>healing</em> sejenak dari hiruk pikuk kota. Tersedia pilihan tenda biasa hingga Glamping mewah.</p>
        <h2>Tips Camping Nyaman</h2>
        <ul>
            <li>Bawa jaket tebal (suhu malam bisa mencapai 15 derajat Celcius).</li>
            <li>Bawa lotion anti nyamuk.</li>
            <li>Booking tempat jauh hari jika berencana datang saat weekend.</li>
        </ul>
        """
    else: # Default Wisata Alam
        body_content = f"""
        <h2>Daya Tarik Utama</h2>
        <p>Tempat ini menawarkan spot foto yang sangat <em>instagramable</em>. Dikelilingi oleh hamparan kebun teh hijau yang luas, suasana di sini sangat tenang dan menyejukkan hati. Sangat cocok untuk liburan keluarga atau sekadar melepas penat bersama teman-teman.</p>
        <h2>Waktu Terbaik Berkunjung</h2>
        <p>Kami sangat menyarankan Anda datang pagi hari sekitar pukul 07.00 - 10.00 WIB. Pada jam ini, matahari pagi memberikan pencahayaan terbaik untuk foto, dan udara masih sangat segar. Hindari datang terlalu sore karena kawasan ini sering turun kabut tebal.</p>
        """

    closing = f"""
    <h2>Cara Menuju Lokasi</h2>
    <p>Akses jalan menuju lokasi {judul} sudah cukup baik dan bisa dilalui kendaraan roda dua maupun roda empat. Dari pusat Kota Bandung, perjalanan memakan waktu sekitar 2 jam melalui jalur Soreang - Banjaran - Pangalengan.</p>
    
    <div class="cta-box">
        <h3>Ingin Liburan Tanpa Ribet?</h3>
        <p>Jangan pusing mengatur itinerary! Kami sediakan paket wisata lengkap (Transport + Tiket + Makan + Guide). Terima beres, tinggal duduk manis.</p>
        <a href="https://wa.me/{WA_ADMIN}?text=Halo Admin, saya baca artikel '{judul}', mau tanya paket wisata dong." class="nav-btn" style="display:inline-block; margin-top:10px;">Hubungi Admin via WhatsApp</a>
    </div>
    """
    
    return intro + body_content + closing

# =======================================================
#               MAIN PROGRAM (GENERATOR)
# =======================================================
def main():
    print("🚀 MEMULAI GENERASI 20 ARTIKEL PREMIUM (HARDCODE)...")

    if not os.path.exists(FOLDER_ARTIKEL): os.makedirs(FOLDER_ARTIKEL)

    # 1. GENERATE 20 ARTIKEL HTML
    list_artikel_cards = ""
    sitemap_urls = ""

    for judul in LIST_JUDUL:
        slug = re.sub(r'[^a-z0-9\-]', '', judul.lower().replace(' ', '-'))
        filename = f"{slug}.html"
        filepath = os.path.join(FOLDER_ARTIKEL, filename)
        
        gambar = random.choice(STOK_FOTO)
        konten = generate_content(judul)
        
        # HTML Artikel
        html_artikel = f"""
        <!DOCTYPE html>
        <html lang="id">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{judul} - Wisata Pangalengan</title>
            {PREMIUM_CSS}
        </head>
        <body>
            <nav>
                <a href="../index.html" class="logo">🌲 Wisata Pangalengan</a>
                <a href="https://wa.me/{WA_ADMIN}" class="nav-btn">Chat Admin</a>
            </nav>

            <div class="article-header">
                <div class="container">
                    <h1>{judul}</h1>
                    <p>Update Terakhir: {datetime.date.today().strftime('%d %B %Y')}</p>
                </div>
            </div>

            <div class="container">
                <div class="content-box">
                    <a href="../index.html" style="font-weight:bold; color:var(--primary); text-decoration:none;">← Kembali ke Beranda</a>
                    <hr style="margin:20px 0; border:0; border-top:1px solid #eee;">
                    <img src="{gambar}" class="feat-img" alt="{judul}">
                    {konten}
                </div>
            </div>

            <footer>
                <p>© 2025 Wisata Pangalengan. Portal Resmi Partner Liburanmu.</p>
            </footer>
        </body>
        </html>
        """
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_artikel)
        print(f"✅ Artikel dibuat: {filename}")
        
        # Data untuk Index & Sitemap
        list_artikel_cards += f"""
        <div class="card">
            <img src="{gambar}" style="height:180px; width:100%; object-fit:cover;">
            <div class="card-body">
                <span style="font-size:0.8rem; color:var(--primary); font-weight:700;">TIPS & INFO</span>
                <a href="artikel/{filename}" class="card-title">{judul}</a>
                <a href="artikel/{filename}" class="btn-outline">📖 Baca Selengkapnya</a>
            </div>
        </div>
        """
        sitemap_urls += f"<url><loc>{BASE_URL}/artikel/{filename}</loc><lastmod>{datetime.date.today()}</lastmod></url>"

    # 2. GENERATE SITEMAP.XML
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>{BASE_URL}/index.html</loc><lastmod>{datetime.date.today()}</lastmod></url>
        {sitemap_urls}
    </urlset>"""
    
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
    print("✅ Sitemap.xml berhasil diupdate.")

    # 3. GENERATE HOMEPAGE (INDEX.HTML)
    homepage_html = f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="google-site-verification" content="{GOOGLE_VERIFICATION_CODE}" />
        <title>Wisata Pangalengan - Paket Tour & Info Terlengkap 2025</title>
        {PREMIUM_CSS}
    </head>
    <body>
        <nav>
            <a href="#" class="logo">🌲 Wisata Pangalengan</a>
            <a href="https://wa.me/{WA_ADMIN}" class="nav-btn">Chat Admin</a>
        </nav>

        <div class="article-header" style="background-image: url('https://images.unsplash.com/photo-1544983220-4b21915df842?w=1600&q=80');">
            <div class="container">
                <h1>Explore Surga Bandung Selatan</h1>
                <p>Temukan paket liburan hemat, spot healing terbaik, dan panduan wisata lengkap di Pangalengan.</p>
                <br>
                <a href="#paket" class="nav-btn" style="background:white; color:var(--primary);">Pilih Paket Hemat ⬇️</a>
            </div>
        </div>

        <div class="container" style="margin-top: 80px;">
            
            <div id="paket" style="text-align:center; margin-bottom:40px;">
                <span style="background:#dcfce7; color:var(--primary); padding:5px 15px; border-radius:20px; font-weight:700; font-size:0.9rem;">REKOMENDASI KAMI</span>
                <h2 style="border:none; padding:0; margin-top:10px;">📦 Paket Wisata Terlaris</h2>
            </div>
            
            <div class="grid">
                <div class="card" style="border-top: 5px solid #10b981;">
                    <div class="card-body">
                        <h3>Open Trip Nimo Highland</h3>
                        <span style="font-size:1.5rem; color:#ef4444; font-weight:800;">Rp 350.000</span>
                        <p>Paket seharian penuh! Main di jembatan kaca viral, kebun teh, dan makan siang enak.</p>
                        <hr style="margin:15px 0; border:0; border-top:1px solid #eee;">
                        <ul style="list-style:none; padding:0; color:#64748b;">
                            <li>✅ Tiket Masuk Nimo</li>
                            <li>✅ Transport AC</li>
                            <li>✅ Makan Siang & Snack</li>
                        </ul>
                        <a href="https://wa.me/{WA_ADMIN}?text=Info Paket Nimo Highland" class="nav-btn" style="display:block; text-align:center; margin-top:20px;">Booking Sekarang</a>
                    </div>
                </div>
                <div class="card" style="border-top: 5px solid #10b981;">
                    <div class="card-body">
                        <h3>Camping Danau Cileunca</h3>
                        <span style="font-size:1.5rem; color:#ef4444; font-weight:800;">Rp 250.000</span>
                        <p>Menginap 2 hari 1 malam di tepi danau. Api unggun, BBQ, dan perahu keliling danau.</p>
                        <hr style="margin:15px 0; border:0; border-top:1px solid #eee;">
                        <ul style="list-style:none; padding:0; color:#64748b;">
                            <li>✅ Tenda Dome Nyaman</li>
                            <li>✅ Makan Malam BBQ</li>
                            <li>✅ Perahu Jelajah Danau</li>
                        </ul>
                        <a href="https://wa.me/{WA_ADMIN}?text=Info Paket Camping Cileunca" class="nav-btn" style="display:block; text-align:center; margin-top:20px;">Booking Sekarang</a>
                    </div>
                </div>
                 <div class="card" style="border-top: 5px solid #10b981;">
                    <div class="card-body">
                        <h3>Rafting Adventure</h3>
                        <span style="font-size:1.5rem; color:#ef4444; font-weight:800;">Rp 175.000</span>
                        <p>Pacu adrenalin di Sungai Palayangan! Aman untuk pemula & keluarga.</p>
                        <hr style="margin:15px 0; border:0; border-top:1px solid #eee;">
                        <ul style="list-style:none; padding:0; color:#64748b;">
                            <li>✅ Gear Rafting Lengkap</li>
                            <li>✅ Guide & Rescue Team</li>
                            <li>✅ Dokumentasi Foto</li>
                        </ul>
                        <a href="https://wa.me/{WA_ADMIN}?text=Info Paket Rafting" class="nav-btn" style="display:block; text-align:center; margin-top:20px;">Booking Sekarang</a>
                    </div>
                </div>
            </div>

            <div style="text-align:center; margin:60px 0 40px;">
                <span style="background:#e0f2fe; color:#0369a1; padding:5px 15px; border-radius:20px; font-weight:700; font-size:0.9rem;">BLOG & TIPS</span>
                <h2 style="border:none; padding:0; margin-top:10px;">📰 Info Wisata Terbaru</h2>
            </div>
            
            <div class="grid">
                {list_artikel_cards}
            </div>
            
            <div style="background:white; padding:40px; border-radius:20px; text-align:center; box-shadow:0 5px 20px rgba(0,0,0,0.05); margin-top:60px;">
                <h2 style="border:none; padding:0;">Kenapa Memilih Kami?</h2>
                <div class="grid" style="margin-top:30px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));">
                    <div>
                        <h3 style="color:var(--primary);">⭐ Terpercaya</h3>
                        <p>Partner resmi warga lokal Pangalengan.</p>
                    </div>
                    <div>
                        <h3 style="color:var(--primary);">⚡ Fast Respon</h3>
                        <p>Admin siap bantu 24/7 via WhatsApp.</p>
                    </div>
                    <div>
                        <h3 style="color:var(--primary);">💰 Harga Jujur</h3>
                        <p>Transparan tanpa biaya tersembunyi.</p>
                    </div>
                </div>
            </div>

        </div>

        <footer>
            <p>© 2025 Wisata Pangalengan. All Rights Reserved.</p>
            <p style="font-size:0.8rem; margin-top:10px;">Powered by AutoPilot System.</p>
        </footer>
    </body>
    </html>
    """
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(homepage_html)
    print("✅ Homepage (index.html) berhasil diupdate.")

if __name__ == "__main__":
    main()
