# Python 3.11 slim imajını kullan
FROM python:3.11-slim

# Sistem güncellemeleri ve gerekli sistem paketlerini yükle
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /app

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Port'u expose et
EXPOSE 5010

# Uygulama kullanıcısı oluştur (güvenlik için)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Uygulama başlat
CMD ["python", "main.py"] 