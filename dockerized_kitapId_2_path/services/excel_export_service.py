import pandas as pd
from typing import List, Optional, Tuple
from models.book_models import BookInfo
from datetime import datetime
import logging
from io import BytesIO

class ExcelExportService:
    """Memory-based Excel export işlemleri için servis sınıfı"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_books_to_excel(self, books: List[BookInfo], filename: Optional[str] = None) -> Tuple[BytesIO, str]:
        """Kitap bilgilerini memory'de Excel olarak oluştur ve BytesIO + filename döndür"""
        if not books:
            raise ValueError("Export edilecek kitap bilgisi bulunamadı")
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kitap_bilgileri_{timestamp}.xlsx"
        
        # Dosya uzantısını kontrol et
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        try:
            # BookInfo objelerini dict'e çevir
            data = [book.to_dict() for book in books]
            
            # DataFrame oluştur
            df = pd.DataFrame(data)
            
            # Sütun sıralaması
            column_order = [
                'Kitap ID', 'Ders ID', 'Kitap Adı', 'Ders Adı', 
                'Seviye', 'Path', 'Domain', 'Kurumsal Ad', 'Zip Versiyon'
            ]
            
            # Mevcut sütunları sırala
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            # Memory buffer oluştur
            excel_buffer = BytesIO()
            
            # Excel'i memory'de oluştur
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Kitap Bilgileri', index=False)
                
                # Çalışma sayfasını al ve formatla
                worksheet = writer.sheets['Kitap Bilgileri']
                
                # Sütun genişliklerini ayarla
                column_widths = {
                    'A': 12,  # Kitap ID
                    'B': 12,  # Ders ID
                    'C': 30,  # Kitap Adı
                    'D': 25,  # Ders Adı
                    'E': 15,  # Seviye
                    'F': 50,  # Path
                    'G': 20,  # Domain
                    'H': 25,  # Kurumsal Ad
                    'I': 15   # Zip Versiyon
                }
                
                for column, width in column_widths.items():
                    worksheet.column_dimensions[column].width = width
            
            # Buffer'ı başa al
            excel_buffer.seek(0)
            
            self.logger.info(f"Excel dosyası memory'de oluşturuldu: {filename}")
            return excel_buffer, filename
            
        except Exception as e:
            self.logger.error(f"Excel export hatası: {str(e)}")
            raise Exception(f"Excel dosyası oluşturulamadı: {str(e)}")
    
    def get_export_filename(self, kitap_ids: List[int]) -> str:
        """Export dosya adını oluştur"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if len(kitap_ids) == 1:
            return f"kitap_{kitap_ids[0]}_{timestamp}.xlsx"
        else:
            return f"kitaplar_{len(kitap_ids)}_adet_{timestamp}.xlsx" 