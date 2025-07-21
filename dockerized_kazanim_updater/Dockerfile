# Python 3.10 slim imajını kullan
FROM python:3.10-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem paketlerini güncelle ve gerekli paketleri yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    && rm -rf /var/lib/apt/lists/*

# Python requirements dosyasını kopyala
COPY requirements.txt .

# Python paketlerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY kazanim_update.py .

# 7002 portunu expose et
EXPOSE 7002

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7002/health || exit 1

# Uygulamayı başlat
CMD ["python", "kazanim_update.py"] 