# Python 3.11 slim imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem paketlerini güncelle ve gerekli araçları yükle
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıklarını kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Çıktı dizinini oluştur
RUN mkdir -p /app/output

# Python scriptinin çalıştırılması için varsayılan komut
# Kullanım: docker run <image_name> <book_id>
ENTRYPOINT ["python", "test-kesim-istek-at.py"]

# Varsayılan parametre (isteğe bağlı)
CMD ["--help"] 