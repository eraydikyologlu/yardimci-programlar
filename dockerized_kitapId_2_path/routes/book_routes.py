from flask import Blueprint, request, jsonify, send_file
from typing import List
import logging
import os

# Servisleri import et
from services.database_service import DatabaseService
from services.book_service import BookService
from services.excel_export_service import ExcelExportService

# Blueprint oluştur
book_bp = Blueprint('book', __name__, url_prefix='/api/books')

# Global servisler (dependency injection için)
database_service = None
book_service = None
excel_service = None

def init_services(db_config: dict):
    """Servisleri başlat"""
    global database_service, book_service, excel_service
    
    database_service = DatabaseService(
        server=db_config['server'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    
    book_service = BookService(database_service)
    excel_service = ExcelExportService()

@book_bp.route('/export', methods=['POST'])
def export_books():
    """Kitap ID'lerini alıp Excel dosyası döndür"""
    try:
        # Request data'yı al
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body boş olamaz'
            }), 400
        
        # Kitap ID'lerini al
        kitap_ids = data.get('kitap_ids', [])
        
        if not kitap_ids:
            return jsonify({
                'success': False,
                'message': 'Kitap ID listesi gerekli'
            }), 400
        
        # ID'lerin integer olduğundan emin ol
        try:
            kitap_ids = [int(id_) for id_ in kitap_ids]
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Geçersiz kitap ID formatı'
            }), 400
        
        # Geçerli kitap ID'lerini kontrol et
        valid_ids = book_service.validate_book_ids(kitap_ids)
        
        if not valid_ids:
            return jsonify({
                'success': False,
                'message': 'Hiçbir geçerli kitap ID\'si bulunamadı'
            }), 404
        
        # Geçersiz ID'leri bildir
        invalid_ids = list(set(kitap_ids) - set(valid_ids))
        if invalid_ids:
            logging.warning(f"Geçersiz kitap ID'leri: {invalid_ids}")
        
        # Kitap bilgilerini al
        books = book_service.get_books_info(valid_ids)
        
        if not books:
            return jsonify({
                'success': False,
                'message': 'Kitap bilgileri alınamadı'
            }), 500
        
        # Excel dosyasını memory'de oluştur
        filename = excel_service.get_export_filename(valid_ids)
        excel_buffer, filename = excel_service.export_books_to_excel(books, filename)
        
        # Memory buffer'dan dosyayı döndür
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logging.error(f"Export hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Sunucu hatası: {str(e)}'
        }), 500

@book_bp.route('/info/<int:kitap_id>', methods=['GET'])
def get_book_info(kitap_id: int):
    """Tek kitap bilgisini Excel olarak döndür"""
    try:
        book = book_service.get_book_info(kitap_id)
        
        if not book:
            return jsonify({
                'success': False,
                'message': f'Kitap bulunamadı: ID={kitap_id}'
            }), 404
        
        # Excel dosyasını memory'de oluştur
        filename = excel_service.get_export_filename([kitap_id])
        excel_buffer, filename = excel_service.export_books_to_excel([book], filename)
        
        # Memory buffer'dan Excel dosyasını döndür
        return send_file(
            excel_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logging.error(f"Kitap export hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Sunucu hatası: {str(e)}'
        }), 500

@book_bp.route('/validate', methods=['POST'])
def validate_book_ids():
    """Kitap ID'lerini doğrula"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body boş olamaz'
            }), 400
        
        kitap_ids = data.get('kitap_ids', [])
        
        if not kitap_ids:
            return jsonify({
                'success': False,
                'message': 'Kitap ID listesi gerekli'
            }), 400
        
        try:
            kitap_ids = [int(id_) for id_ in kitap_ids]
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Geçersiz kitap ID formatı'
            }), 400
        
        valid_ids = book_service.validate_book_ids(kitap_ids)
        invalid_ids = list(set(kitap_ids) - set(valid_ids))
        
        return jsonify({
            'success': True,
            'data': {
                'valid_ids': valid_ids,
                'invalid_ids': invalid_ids,
                'total_requested': len(kitap_ids),
                'total_valid': len(valid_ids),
                'total_invalid': len(invalid_ids)
            }
        })
        
    except Exception as e:
        logging.error(f"Validation hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Sunucu hatası: {str(e)}'
        }), 500

@book_bp.route('/health', methods=['GET'])
def health_check():
    """API sağlık kontrolü"""
    try:
        # Database bağlantısını test et
        with database_service:
            test_result = database_service.execute_single_query("SELECT 1 as test")
            
        if test_result:
            return jsonify({
                'success': True,
                'message': 'API ve database bağlantısı çalışıyor',
                'status': 'healthy'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Database bağlantısı başarısız',
                'status': 'unhealthy'
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sağlık kontrolü başarısız: {str(e)}',
            'status': 'unhealthy'
        }), 503 

@book_bp.route('/debug/<int:kitap_id>', methods=['GET'])
def debug_book_detailed(kitap_id: int):
    """Detaylı kitap debug bilgileri"""
    try:
        result = {
            'kitap_id': kitap_id,
            'tests': {}
        }
        
        # Test 1: Validate methodu
        valid_ids = book_service.validate_book_ids([kitap_id])
        result['tests']['validate_method'] = {
            'success': kitap_id in valid_ids,
            'valid_ids': valid_ids
        }
        
        # Test 2: Debug exists methodu
        exists = book_service.debug_book_exists(kitap_id)
        result['tests']['debug_exists'] = {
            'exists': exists
        }
        
        # Test 3: Direkt database sorgusu
        with database_service:
            direct_result = database_service.execute_single_query(
                "SELECT Id, Adi, DersId, UstKurumId, Seviye FROM S_TestKitaplar WHERE Id = %s", 
                (kitap_id,)
            )
        result['tests']['direct_query'] = {
            'found': direct_result is not None,
            'data': direct_result if direct_result else None
        }
        
        # Test 4: get_books_info methodu
        books = book_service.get_books_info([kitap_id])
        result['tests']['get_books_info'] = {
            'count': len(books),
            'books': [book.to_dict() if book else None for book in books]
        }
        
        return jsonify({
            'success': True,
            'debug_info': result
        })
        
    except Exception as e:
        logging.error(f"Debug hatası: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Debug hatası: {str(e)}'
        }), 500 