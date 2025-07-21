# Kazanım Updater API

Bu proje, kazanım güncelleme işlemlerini REST API olarak sunan bir FastAPI uygulamasıdır.

## Özellikler

- 🚀 FastAPI tabanlı REST API
- 🔍 Elasticsearch entegrasyonu
- 💾 MSSQL veritabanı bağlantısı
- 🤖 AI modeli ile kazanım tahmini
- 🐳 Docker desteği
- 📊 Health check endpoint'i

## API Endpoints

### GET `/`
Ana sayfa ve API bilgileri

### POST `/update-kazanim`
Kazanım güncelleme işlemini başlatır

**Query Parametreleri:**
- `ders_id` (opsiyonel): Sadece belirtilen DersId'deki sorular işlenir
- `kitap_id` (opsiyonel): Sadece belirtilen KitapId'deki sorular işlenir

**Örnek İstek:**
```bash
curl -X POST "http://localhost:7002/update-kazanim?ders_id=1&kitap_id=5"
```

**Örnek Yanıt:**
```json
{
    "success": true,
    "message": "Kazanım güncelleme tamamlandı",
    "processed_count": 150,
    "updated_count": 142,
    "ders_id": 1,
    "kitap_id": 5
}
```

### GET `/health`
Sistem sağlık kontrolü

## Docker ile Çalıştırma

### 1. Docker Build
```bash
docker build -t kazanim-updater-api .
```

### 2. Docker Run
```bash
docker run -p 7002:7002 kazanim-updater-api
```

### 3. Docker Compose (Önerilen)
```bash
docker-compose up -d
```

## Manuel Çalıştırma

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Başlatma
```bash
python kazanim_update.py
```

API `http://localhost:7002` adresinde çalışacaktır.

## API Dokümantasyonu

FastAPI otomatik olarak API dokümantasyonu oluşturur:

- **Swagger UI:** `http://localhost:7002/docs`
- **ReDoc:** `http://localhost:7002/redoc`

## Yapılandırma

Veritabanı ve Elasticsearch ayarları `kazanim_update.py` dosyasındaki config bölümünden düzenlenebilir:

```python
MSSQL_CONFIG = {
    "server": "sql.impark.local",
    "user": "enes.karatas", 
    "password": "Exkaratas2021!*",
    "database": "olcme_db"
}

ES_HOST = "http://elastic.dijidemi.com:80"
ES_USER = "elastic"
ES_PASS = "123654-"
ES_INDEX = "question_bank"
```

## Docker Commands

```bash
# Image build etme
docker build -t kazanim-updater-api .

# Container çalıştırma
docker run -d -p 7002:7002 --name kazanim-api kazanim-updater-api

# Log'ları görme
docker logs kazanim-api

# Container'ı durdurma
docker stop kazanim-api

# Container'ı silme
docker rm kazanim-api
``` 