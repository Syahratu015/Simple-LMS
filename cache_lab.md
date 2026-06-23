Redis Caching Exercise
Tujuan
Mengimplementasikan Redis sebagai cache untuk menyimpan hasil panggilan API guna mengurangi waktu respons pada permintaan berikutnya.

1. Konsep Caching
Caching adalah teknik penyimpanan data sementara di media yang lebih cepat diakses. Redis digunakan sebagai cache layer untuk menyimpan respons API cuaca selama 5 menit (300 detik).

Alur kerja:

Aplikasi menerima request data cuaca

Sistem mengecek Redis terlebih dahulu

Jika data tersedia di cache → langsung dikembalikan

Jika tidak tersedia → panggil API eksternal

Hasil API disimpan ke Redis

Data dikembalikan ke pengguna

2. Implementasi Redis
Koneksi Redis:

python
import redis
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)
Logika Caching:

python
import time
import json
import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def get_weather(city):
    cache_key = f"weather:{city.lower()}"
    
    # Cek cache
    cached_data = redis_client.get(cache_key)
    if cached_data:
        print("✅ Data dari Redis cache")
        return json.loads(cached_data)
    
    # Panggil API
    print("⏳ Memanggil API...")
    time.sleep(2)  # Simulasi delay
    
    result = {
        "city": city,
        "temperature": 30,
        "condition": "Sunny"
    }
    
    # Simpan ke cache
    redis_client.set(cache_key, json.dumps(result))
    redis_client.expire(cache_key, 300)
    return result
3. Testing
Script pengujian:

python
import time
from weather_api import get_weather

start = time.time()
result1 = get_weather("Jakarta")
print(f"First call: {time.time() - start:.2f}s")

start = time.time()
result2 = get_weather("Jakarta")
print(f"Second call (cached): {time.time() - start:.2f}s")
Output terminal:

text
⏳ Memanggil API...
First call: 2.02s

✅ Data dari Redis cache
Second call (cached): 0.00s

🔁 Panggilan ketiga setelah 5 menit akan lambat lagi karena cache expired.
4. Screenshot
Redis Running:

bash
docker compose up -d redis
https://Screenshots/redisrunning.png

Redis Ping:

bash
docker exec -it redis-cache redis-cli ping
Output: PONG
https://Screenshots/redis-ping.png

Hasil Testing:

bash
python test_cache.py
https://Screenshots/cache-test.png

5. Perintah Redis
Perintah	Fungsi
GET weather:jakarta	Mengambil data dari Redis
SET weather:jakarta "{...}"	Menyimpan data ke Redis
EXPIRE weather:jakarta 300	Menentukan masa berlaku cache
TTL weather:jakarta	Melihat sisa waktu cache

6. Analisis
Kenapa response time berbeda?

 a. Pertama (2 detik): Data belum di cache → harus panggil API

 b. Kedua (instan): Data sudah di Redis → langsung dari cache

Keuntungan caching:

⚡ Response time lebih cepat

🖥️ Mengurangi beban server

📉 Mengurangi jumlah API call

💰 Menghemat resource

😊 Meningkatkan user experience

Kapan tidak pakai cache:

a. Data yang harus real-time

b. Data yang sering berubah

c. Data sensitif (transaksi keuangan)

d. Informasi yang harus selalu akurat

7. Kesimpulan
Redis berhasil diimplementasikan sebagai cache layer untuk menyimpan hasil API call. Pengujian membuktikan request pertama membutuhkan ~2 detik, sedangkan request berikutnya hampir instan karena data sudah tersedia di Redis. Implementasi caching terbukti efektif mengurangi response time dan meningkatkan performa aplikasi.