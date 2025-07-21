# Python 3.11 slim image kullan
FROM python:3.11-slim

# Çalışma dizinini ayarla
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    apt-transport-https \
    gcc \
    g++ \
 && rm -rf /var/lib/apt/lists/*
# ---------- 2. TABAKA: Microsoft ODBC deposu ----------
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
     | gpg --dearmor -o /usr/share/keyrings/microsoft.gpg \
 && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] \
     https://packages.microsoft.com/debian/12/prod bookworm main" \
     > /etc/apt/sources.list.d/mssql-release.list
# ---------- 3. TABAKA: ODBC sürücüsü (tek seferde) ----------
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql18 unixodbc-dev \
 && rm -rf /var/lib/apt/lists/*
# Requirements dosyasını kopyala
COPY requirements.txt .

# Python paketlerini yükle
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Port'u expose et
EXPOSE 7002

# Health check ekle
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7002/health || exit 1

# Uygulamayı başlat
CMD ["python", "kazanim_update.py"] 
#CMD ["tail", "-f", "/dev/null"]
