# Kazanim Updater API - Docker Commands

.PHONY: help build run stop clean logs shell dev-build dev-run dev-stop

help: ## Bu yardım mesajını göster
	@echo "Kullanılabilir komutlar:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Production image'ını build et
	docker-compose build

run: ## Production container'ını çalıştır
	docker-compose up -d

stop: ## Container'ı durdur
	docker-compose down

clean: ## Container'ları ve image'ları temizle
	docker-compose down --volumes --remove-orphans
	docker system prune -f

logs: ## Container loglarını göster
	docker-compose logs -f

shell: ## Container'a bash ile bağlan
	docker-compose exec kazanim-updater-api bash

dev-build: ## Development image'ını build et
	docker-compose -f docker-compose.dev.yml build

dev-run: ## Development container'ını çalıştır (hot reload ile)
	docker-compose -f docker-compose.dev.yml up -d

dev-stop: ## Development container'ını durdur
	docker-compose -f docker-compose.dev.yml down

dev-logs: ## Development container loglarını göster
	docker-compose -f docker-compose.dev.yml logs -f

restart: ## Container'ı yeniden başlat
	docker-compose restart

status: ## Container durumunu göster
	docker-compose ps 