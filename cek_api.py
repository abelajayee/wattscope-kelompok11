"""
import json
import time
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

# ---------- TES 1: cari cerita ----------
url = "https://www.wattpad.com/api/v3/stories"
params = {
    "query": "romance",   
    "language": 20,      
    "limit": 3,          
    "fields": "stories(id,title,user(name),readCount,voteCount,commentCount,"
              "numParts,completed,tags,mature,modifyDate,url,language,parts(id,title))",
}
r = requests.get(url, params=params, headers=HEADERS, timeout=20)
print("TES 1 - status:", r.status_code)   
data = r.json()
for s in data.get("stories", []):
    print("-", s["id"], "|", s["title"], "| penulis:", s["user"]["name"],
          "| dibaca:", s["readCount"], "| bahasa:", s.get("language"))

# ---------- TES 2: komentar chapter pertama ----------
time.sleep(1)  # jeda 1 detik, sesuai rancangan
if data.get("stories"):
    part_id = data["stories"][0]["parts"][0]["id"]
    for kandidat in [
        f"https://www.wattpad.com/v5/comments/namespaces/parts/resources/{part_id}/comments",
        f"https://www.wattpad.com/api/v3/story_parts/{part_id}/comments",
    ]:
        r2 = requests.get(kandidat, headers=HEADERS, timeout=20)
        print("\nTES 2 -", kandidat, "\nstatus:", r2.status_code)
        print(r2.text[:600])   
        time.sleep(1)

print("\nContoh 1 cerita lengkap (untuk lihat nama-nama kolom):")
print(json.dumps(data.get("stories", [{}])[0], indent=2, ensure_ascii=False)[:1500])
