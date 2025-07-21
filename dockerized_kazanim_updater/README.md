# Kazanım Updater API

Bu proje, kazanım güncelleme işlemlerini REST API olarak sunan bir FastAPI uygulamasıdır.

## Özellikler

- 🚀 FastAPI tabanlı REST API
- 🔍 Elasticsearch entegrasyonu
- 💾 MSSQL veritabanı bağlantısı
- 🤖 AI modeli ile kazanım tahmini
- 🐳 Docker desteği
- 📊 Health check endpoint'i
- ⚙️ Environment variables desteği

## Kurulum ve Yapılandırma

### 1. Environment Variables

Proje environment variables'ları kullanır. Docker ile çalıştırmadan önce `.env` dosyası oluşturun:

```bash
# .env dosyası oluştur (config.env'den kopyala)
cp config.env .env
```

**Yapılandırma Dosyası (config.env):**
```env
# SQL Server Yapılandırması
MSSQL_SERVER=sql.impark.local
MSSQL_USER=enes.karatas
MSSQL_PASSWORD=Exkaratas2021!*
MSSQL_DATABASE=olcme_db

# Elasticsearch Yapılandırması
ES_HOST=http://elastic.dijidemi.com:80
ES_USER=elastic
ES_PASSWORD=123654-
ES_INDEX=question_bank

# API Yapılandırması
API_HOST=0.0.0.0
API_PORT=7002

# ML Model API Yapılandırması
MODEL_API_URL=http://bcaicpu.impark.local:5005/api/kazanim_isaretleme
MODEL_API_KEY=rMGgnVjOyQizdhwYRTcZuxFkIZUanumJ
```

### 2. Gereksinimler
```bash
pip install -r requirements.txt
```

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

## Çalıştırma

### Manuel Çalıştırma
```bash
python kazanim_update.py
```

### Docker ile Çalıştırma

#### 1. Docker Build
```bash
docker build -t kazanim-updater-api .
```

#### 2. Docker Run (Environment Variables ile)
```bash
docker run -p 7002:7002 --env-file .env kazanim-updater-api
```

#### 3. Docker Compose (Önerilen)
```bash
docker-compose up -d
```

API `http://localhost:7002` adresinde çalışacaktır.

## API Dokümantasyonu

FastAPI otomatik olarak API dokümantasyonu oluşturur:

- **Swagger UI:** `http://localhost:7002/docs`
- **ReDoc:** `http://localhost:7002/redoc`

## Environment Variables Detayları

| Değişken | Açıklama | Varsayılan Değer |
|----------|----------|------------------|
| `MSSQL_SERVER` | SQL Server adresi | `sql.impark.local` |
| `MSSQL_USER` | SQL Server kullanıcı adı | `enes.karatas` |
| `MSSQL_PASSWORD` | SQL Server şifresi | - |
| `MSSQL_DATABASE` | SQL Server veritabanı adı | `olcme_db` |
| `ES_HOST` | Elasticsearch host adresi | `http://elastic.dijidemi.com:80` |
| `ES_USER` | Elasticsearch kullanıcı adı | `elastic` |
| `ES_PASSWORD` | Elasticsearch şifresi | - |
| `ES_INDEX` | Elasticsearch index adı | `question_bank` |
| `API_HOST` | API host adresi | `0.0.0.0` |
| `API_PORT` | API port numarası | `7002` |
| `MODEL_API_URL` | ML Model API URL'si | `http://bcaicpu.impark.local:5005/api/kazanim_isaretleme` |
| `MODEL_API_KEY` | ML Model API anahtarı | - |

## Docker Commands

### Makefile ile Kolay Kullanım (Önerilen)

```bash
# Yardım
make help

# Production
make build          # Image build et
make run            # Container'ı çalıştır
make logs           # Logları göster
make stop           # Container'ı durdur
make clean          # Temizle

# Development (Hot Reload)
make dev-build      # Dev image build et
make dev-run        # Dev container çalıştır
make dev-logs       # Dev logları göster
make dev-stop       # Dev container durdur
```

### Manuel Docker Commands

```bash
# Production
docker-compose build
docker-compose up -d
docker-compose logs -f
docker-compose down

# Development (Hot Reload)
docker-compose -f docker-compose.dev.yml build
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f
docker-compose -f docker-compose.dev.yml down

# Manual Docker Build/Run
docker build -t kazanim-updater-api .
docker run -d -p 7002:7002 --env-file .env --name kazanim-api kazanim-updater-api
```

## Docker Dosya Yapısı

```
dockerized_kazanim_updater/
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image (hot reload)
├── docker-compose.yml      # Production compose config
├── docker-compose.dev.yml  # Development compose config
├── .dockerignore           # Docker ignore dosyası
├── Makefile               # Docker komutları için kısayollar
├── config.env             # Environment variables şablonu
├── .env                   # Docker için environment variables (config.env'den kopyala)
├── requirements.txt       # Python dependencies
├── kazanim_update.py      # Ana uygulama
└── README.md              # Dokümantasyon
```

### Dosya Açıklamaları

| Dosya | Açıklama |
|-------|----------|
| `Dockerfile` | Production için optimize edilmiş Docker image |
| `Dockerfile.dev` | Development için hot-reload destekli image |
| `docker-compose.yml` | Production ortamı compose konfigürasyonu |
| `docker-compose.dev.yml` | Development ortamı compose konfigürasyonu |
| `.dockerignore` | Docker build sırasında ignore edilecek dosyalar |
| `Makefile` | Docker komutları için kısayollar |
| `config.env` | Environment variables şablonu |
| `.env` | Docker için environment variables (config.env'den kopyalanır) |

## Güvenlik Notları

- Hassas bilgileri (şifreler, API anahtarları) `config.env` dosyasında tutun
- `config.env` dosyasını `.gitignore`'a ekleyin
- Production ortamında environment variables'ları sistem düzeyinde tanımlayın 