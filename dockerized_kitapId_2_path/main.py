from flask import Flask, jsonify
from flask_cors import CORS
import logging
from typing import List, Optional
from models.book_models import BookInfo
from datetime import datetime
import logging

# Konfigürasyon ve route'ları import et
from config import Config
from routes.book_routes import book_bp, init_services

def create_app():
    """Flask Web API uygulamasını oluştur ve konfigüre et"""
    app = Flask(__name__)
    
    # CORS'u etkinleştir (React frontend için)
    CORS(app)
    
    # Konfigürasyonu yükle
    app.config.from_object(Config)
    Config.init_app(app)
    
    # Servisleri başlat
    init_services(Config.DATABASE_CONFIG)
    
    # Blueprint'leri kaydet
    app.register_blueprint(book_bp)
    
    # API ana endpoint'i
    @app.route('/')
    def index():
        """API bilgileri"""
        return jsonify({
            'success': True,
            'message': 'Kitap Bilgileri Export API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/books/health',
                'validate': 'POST /api/books/validate',
                'export': 'POST /api/books/export',
                'book_info': 'GET /api/books/info/{id}'
            }
        })
    
    # Hata handler'ları
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'message': 'Endpoint bulunamadı'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'message': 'Sunucu hatası'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Web API'yi çalıştır
    app.run(
        host='0.0.0.0',
        port=5010,
        debug=app.config['DEBUG']
    ) 