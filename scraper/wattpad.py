"""
scraper/wattpad.py
------------------
Mengambil data CERITA Wattpad berbahasa Indonesia lewat API Wattpad.
(Bagian komentar akan ditambahkan di langkah berikutnya.)

Coba jalankan dari folder WattScope:
    python scraper/wattpad.py
"""
import time
import requests

# Pura-pura jadi browser, supaya request tidak ditolak
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

BAHASA_INDONESIA = 20   # kode bahasa dari Wattpad (sudah kita cek di TES 1)
JEDA = 1                # jeda 1 detik antar-request, biar tidak diblokir

# Kolom apa saja yang kita minta dari Wattpad
KOLOM_CERITA = (
    "stories(id,title,user(name),description,tags,readCount,voteCount,"
    "commentCount,numParts,completed,mature,modifyDate,url,parts(id,title))"
)


def ambil_cerita(kata_kunci, jumlah=50):
    """Cari cerita berdasarkan kata kunci (misal 'romance').
    Wattpad memberi data per 'halaman', jadi kita minta berulang-ulang
    sambil menggeser 'offset' sampai jumlah yang diminta terpenuhi."""
    hasil = []
    offset = 0
    per_halaman = 20

    while len(hasil) < jumlah:
        params = {
            "query": kata_kunci,
            "language": BAHASA_INDONESIA,
            "limit": per_halaman,
            "offset": offset,
            "fields": KOLOM_CERITA,
        }
        r = requests.get("https://www.wattpad.com/api/v3/stories",
                         params=params, headers=HEADERS, timeout=20)
        r.raise_for_status()                  # kalau error (bukan 200), langsung berhenti
        stories = r.json().get("stories", [])

        if not stories:                       # sudah tidak ada cerita lagi
            break

        for s in stories:
            if s.get("mature"):               # lewati cerita dewasa (sesuai rancangan)
                continue
            hasil.append(rapikan_cerita(s, kata_kunci))
            if len(hasil) >= jumlah:
                break

        offset += per_halaman                 # pindah ke "halaman" berikutnya
        time.sleep(JEDA)

    return hasil


def rapikan_cerita(s, genre):
    """Ubah data mentah dari Wattpad jadi bentuk rapi sesuai tabel `stories`."""
    parts = s.get("parts") or []
    return {
        "id": int(s["id"]),
        "title": s.get("title"),
        "author": (s.get("user") or {}).get("name"),
        "genre": genre,                               # genre = kata kunci yang kita cari
        "tags": ",".join(s.get("tags") or []),        # list -> teks "a,b,c"
        "description": s.get("description"),
        "reads": s.get("readCount", 0),
        "votes": s.get("voteCount", 0),
        "comments": s.get("commentCount", 0),
        "parts": s.get("numParts", 0),
        "completed": 1 if s.get("completed") else 0,  # True/False -> 1/0
        "updated_at": s.get("modifyDate"),
        "url": s.get("url"),
        "first_part_id": parts[0]["id"] if parts else None,  # dipakai nanti untuk ambil komentar
    }


def ambil_komentar(story_id, part_id):
    """Ambil komentar dari satu chapter (dipakai untuk chapter pertama tiap cerita).
    Alamat ini yang berhasil di TES 2 (status 200)."""
    url = f"https://www.wattpad.com/v5/comments/namespaces/parts/resources/{part_id}/comments"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:          # kalau gagal, jangan bikin program berhenti
        return []
    hasil = []
    for k in r.json().get("comments", []):
        hasil.append({
            "id": k["commentId"]["resourceId"],          # ID unik komentar
            "story_id": story_id,
            "part_id": part_id,
            "username": (k.get("user") or {}).get("name"),
            "body": k.get("text"),
            "created_at": k.get("created"),
        })
    time.sleep(JEDA)
    return hasil


# Bagian ini hanya jalan kalau file ini dijalankan langsung (untuk uji coba)
if __name__ == "__main__":
    cerita = ambil_cerita("horor", jumlah=5)
    print(f"Dapat {len(cerita)} cerita:\n")
    for c in cerita:
        status = "Tamat" if c["completed"] else "Belum tamat"
        print(f"- {c['title']} | {c['author']} | dibaca {c['reads']:,} | "
              f"{c['parts']} chapter | {status}")

    # uji ambil komentar dari cerita pertama
    if cerita and cerita[0]["first_part_id"]:
        komentar = ambil_komentar(cerita[0]["id"], cerita[0]["first_part_id"])
        print(f"\nKomentar di chapter pertama '{cerita[0]['title']}': {len(komentar)}")
        for k in komentar[:5]:
            print(f"  {k['username']}: {k['body']}")
