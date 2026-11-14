"""
jalankan_scraping.py
--------------------
Menggabungkan scraper + database:
ambil cerita per genre -> simpan -> ambil komentar chapter pertama -> simpan.

Jalankan dari folder WattScope:
    python jalankan_scraping.py
"""
from scraper.wattpad import ambil_cerita, ambil_komentar
from database import db

GENRE = ["romance", "horor", "teen fiction", "fantasi"]   # sesuai rancangan
JUMLAH_PER_GENRE = 50                                     # 4 x 50 = 200 cerita


def main(genre_list=GENRE, jumlah=JUMLAH_PER_GENRE):
    db.buat_tabel()

    for genre in genre_list:
        print(f"\n=== Genre: {genre} ===")
        cerita = ambil_cerita(genre, jumlah=jumlah)
        db.simpan_cerita(cerita)
        print(f"{len(cerita)} cerita disimpan. Mengambil komentar...")

        for i, c in enumerate(cerita, start=1):
            if not c["first_part_id"]:
                continue
            komentar = ambil_komentar(c["id"], c["first_part_id"])
            db.simpan_komentar(komentar)
            print(f"  [{i}/{len(cerita)}] {c['title'][:40]:<40} -> {len(komentar)} komentar")

    print(f"\nSELESAI. Isi database: {db.hitung('stories')} cerita, "
          f"{db.hitung('comments')} komentar.")


if __name__ == "__main__":
    main()
