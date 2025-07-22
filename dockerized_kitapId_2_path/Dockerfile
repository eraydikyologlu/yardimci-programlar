# Python 3.11 slim imajını kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

# Sistem güncellemeleri ve temel paketleri yükle
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    gcc \
    g++ \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
 && rm -rf /var/lib/apt/lists/*

# Microsoft ODBC deposu ekle
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
     | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] \
     https://packages.microsoft.com/debian/12/prod bookworm main" \
     > /etc/apt/sources.list.d/mssql-release.list

# ODBC sürücüsü yükle
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev \
 && rm -rf /var/lib/apt/lists/*

# Requirements dosyasını kopyala ve bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Port'u expose et
EXPOSE 7003

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7003/api/books/health || exit 1

# Uygulama kullanıcısı oluştur (güvenlik için)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Uygulama başlat
CMD ["python", "main.py"] 