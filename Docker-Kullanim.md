# Docker Kullanım Kılavuzu

Bu proje için Docker dosyaları ve kullanım yöntemleri.

## Dosyalar

- `Dockerfile` - Production ortamı için ana Docker dosyası
- `Dockerfile.dev` - Geliştirme ortamı için Docker dosyası
- `docker-compose.yml` - Container yönetimi için Docker Compose dosyası
- `requirements.txt` - Python bağımlılıkları
- `.dockerignore` - Docker build sırasında hariç tutulacak dosyalar

## Kullanım

### 1. Docker Image Oluşturma

```bash
# Production image oluştur
docker build -t yardimci-program .

# Development image oluştur
docker build -f Dockerfile.dev -t yardimci-program:dev .
```

### 2. Container Çalıştırma

```bash
# Production container'ı çalıştır (book_id parametresi ile)
docker run --rm yardimci-program 123

# Çıktı dosyalarını kaydetmek için volume kullan
docker run --rm -v $(pwd)/output:/app/output yardimci-program 123

# Development container'ı interaktif modda çalıştır
docker run -it --rm -v $(pwd):/app yardimci-program:dev
```

### 3. Docker Compose ile Kullanım

```bash
# Container'ları başlat
docker-compose up --build

# Belirli bir book_id ile çalıştır
docker-compose run --rm yardimci-program 123

# Development modunda çalıştır
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 4. Development Ortamı

Development container'ında şu araçlar mevcut:
- IPython (interaktif Python)
- Jupyter Notebook
- Black (kod formatlama)
- Flake8 (kod analizi)
- pytest (test çalıştırma)

```bash
# Development container'ına gir
docker run -it --rm -v $(pwd):/app yardimci-program:dev

# Container içinde:
python test-kesim-istek-at.py 123
black *.py  # Kod formatlama
flake8 *.py  # Kod analizi
```

### 5. Yararlı Komutlar

```bash
# Çalışan container'ları listele
docker ps

# Tüm container'ları durdur
docker stop $(docker ps -q)

# Image'ları listele
docker images

# Kullanılmayan image'ları temizle
docker image prune

# Sistem temizliği
docker system prune
```

## Çıktı Dosyaları

Script çalıştığında `failed_books.json` dosyası oluşturulabilir. Bu dosya:
- Container içinde `/app/failed_books.json` konumunda oluşur
- Volume mount ile host makineye kopyalanabilir
- Docker Compose kullanılırsa otomatik olarak `./output/` dizininde görünür

## Ortam Değişkenleri

Gerekli ortam değişkenlerini docker-compose.yml dosyasında tanımlayabilirsiniz:

```yaml
environment:
  - API_URL=https://api.yayincilik.net
  - TIMEOUT=30
  - DEBUG=true
```

## Sorun Giderme

### Container başlamıyor
```bash
# Log'ları kontrol et
docker logs <container_id>

# Image'ı yeniden oluştur
docker build --no-cache -t yardimci-program .
```

### Permission hatası
```bash
# Linux/Mac için user ID'yi ayarla
docker run --user $(id -u):$(id -g) --rm -v $(pwd):/app yardimci-program
```

### Network sorunu
```bash
# DNS ayarlarını kontrol et
docker run --rm --dns=8.8.8.8 yardimci-program
``` 