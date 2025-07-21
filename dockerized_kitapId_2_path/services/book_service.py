from typing import List, Optional
from services.database_service import DatabaseInterface
from models.book_models import BookInfo
import logging

class BookService:
    """Kitap işlemleri için servis sınıfı"""
    
    def __init__(self, database_service: DatabaseInterface):
        self.database_service = database_service
        self.logger = logging.getLogger(__name__)
    
    def get_book_info(self, kitap_id: int) -> Optional[BookInfo]:
        """Tek kitap bilgisini getir"""
        books = self.get_books_info([kitap_id])
        return books[0] if books else None
    
    def debug_book_exists(self, kitap_id: int) -> bool:
        """Debug: Kitap veritabanında var mı kontrol et"""
        try:
            query = "SELECT Id, Adi FROM S_TestKitaplar WHERE Id = %s"
            result = self.database_service.execute_single_query(query, (kitap_id,))
            
            if result:
                self.logger.info(f"Debug - Kitap bulundu: ID={kitap_id}, Adı={result.get('Adi')}")
                return True
            else:
                self.logger.warning(f"Debug - Kitap bulunamadı: ID={kitap_id}")
                return False
        except Exception as e:
            self.logger.error(f"Debug - Kitap kontrol hatası: {str(e)}")
            return False
    
    def get_books_info(self, kitap_ids: List[int]) -> List[BookInfo]:
        """Çoklu kitap bilgilerini getir"""
        if not kitap_ids:
            return []
        
        # Debug: Her kitap ID'sinin varlığını kontrol et
        self.logger.info(f"Kitap ID'leri sorgulanıyor: {kitap_ids}")
        
        # Önce basit sorguyla kitapları kontrol et
        for kitap_id in kitap_ids:
            exists = self.debug_book_exists(kitap_id)
            if not exists:
                self.logger.warning(f"Kitap bulunamadı: {kitap_id}")
        
        # Kitap ID'lerini string formatına çevir
        ids_str = ','.join(map(str, kitap_ids))
        
        # Adım adım JOIN yapalım - önce temel kitap bilgileri
        base_query = f"""
        SELECT 
            k.Id as KitapId,
            k.DersId,
            k.UstKurumId,
            k.Adi as KitapAdi,
            d.SeviyeId as KitapSeviye
        FROM S_TestKitaplar k
        join S_TestDersler d on k.DersId = d.Id
        WHERE k.Id IN ({ids_str})
        """
        
        try:
            base_results = self.database_service.execute_query(base_query)
            self.logger.info(f"Temel kitap sorgusu sonucu: {len(base_results)} kayıt")
            
            if not base_results:
                return []
            
            books = []
            
            for result in base_results:
                kitap_id = result.get('KitapId')
                self.logger.info(f"İşleniyor: Kitap ID={kitap_id}, Adı={result.get('KitapAdi')}")
                
                # Ders bilgisini ayrı sorgula
                ders_adi = None
                ders_id = result.get('DersId')
                if ders_id:
                    try:
                        ders_query = "SELECT Adi FROM S_TestDersler WHERE Id = %s"
                        ders_result = self.database_service.execute_single_query(ders_query, (ders_id,))
                        if ders_result:
                            ders_adi = ders_result.get('Adi')
                    except Exception as e:
                        self.logger.warning(f"Ders bilgisi alınamadı (ID: {ders_id}): {str(e)}")
                
                # Üst kurum bilgisini ayrı sorgula
                domain = None
                kurumsalad = None
                ust_kurum_id = result.get('UstKurumId')
                if ust_kurum_id:
                    try:
                        kurum_query = "SELECT KurumsalAd, Domain FROM S_UstKurumlar WHERE Id = %s"
                        kurum_result = self.database_service.execute_single_query(kurum_query, (ust_kurum_id,))
                        if kurum_result:
                            domain = kurum_result.get('Domain')
                            kurumsalad = kurum_result.get('KurumsalAd')
                    except Exception as e:
                        self.logger.warning(f"Kurum bilgisi alınamadı (ID: {ust_kurum_id}): {str(e)}")
                
                # ZKitap bilgisini ayrı sorgula
                zip_versiyon = None
                try:
                    zkitap_query = "SELECT ZipVersiyon FROM S_TestKitaplarZKitapAyar WHERE KitapId = %s"
                    zkitap_result = self.database_service.execute_single_query(zkitap_query, (kitap_id,))
                    if zkitap_result:
                        zip_versiyon = zkitap_result.get('ZipVersiyon')
                except Exception as e:
                    self.logger.warning(f"ZKitap bilgisi alınamadı (Kitap ID: {kitap_id}): {str(e)}")
                
                # Path oluştur
                path = self._generate_book_path({
                    'Domain': domain,
                    'KitapId': kitap_id,
                    'ZipVersiyon': zip_versiyon
                })
                
                book = BookInfo(
                    id=kitap_id,
                    ders_id=ders_id,
                    ust_kurum_id=result.get('UstKurumId'),
                    adi=result.get('KitapAdi', ''),
                    seviye=result.get('KitapSeviye'),
                    ders_adi=ders_adi,
                    path=path,
                    domain=domain,
                    kurumsalad=kurumsalad,
                    zip_versiyon=zip_versiyon
                )
                books.append(book)
                
                self.logger.info(f"Kitap başarıyla işlendi: ID={kitap_id}")
            
            return books
            
        except Exception as e:
            self.logger.error(f"Kitap bilgileri alınırken hata: {str(e)}")
            return []
    
    def _generate_book_path(self, book_data: dict) -> Optional[str]:
        """Kitap path'ini oluştur"""
        try:
            domain = book_data.get('Domain')
            kitap_id = book_data.get('KitapId')
            zip_versiyon = book_data.get('ZipVersiyon')
            
            if not domain or not kitap_id or not zip_versiyon:
                missing = []
                if not domain: missing.append('Domain')
                if not kitap_id: missing.append('KitapId')  
                if not zip_versiyon: missing.append('ZipVersiyon')
                self.logger.warning(f"Path oluşturulamadı, eksik bilgi: {missing}")
                return None
            
            # Domain'den www. kaldır
            domain = domain.replace("www.", "")
            
            # Path oluştur
            if domain == "yayincilik.net":
                base_path = f"\\\\bcm.impark.local\\Store\\Root\\vhosts\\yayincilik.net\\{domain}\\Uploads\\ZKitapZip"
            else:
                base_path = f"\\\\bcm.impark.local\\Store\\Root\\vhosts\\{domain}\\httpdocs\\Uploads\\ZKitapZip"
            
            path = f"{base_path}\\{kitap_id}-{zip_versiyon}"
            self.logger.info(f"Path oluşturuldu: {path}")
            return path
            
        except Exception as e:
            self.logger.error(f"Path oluşturulurken hata: {str(e)}")
            return None
    
    def validate_book_ids(self, kitap_ids: List[int]) -> List[int]:
        """Geçerli kitap ID'lerini filtrele"""
        if not kitap_ids:
            return []
        
        ids_str = ','.join(map(str, kitap_ids))
        query = f"SELECT Id FROM S_TestKitaplar WHERE Id IN ({ids_str})"
        
        try:
            results = self.database_service.execute_query(query)
            valid_ids = [result['Id'] for result in results]
            self.logger.info(f"Geçerli ID'ler: {valid_ids}")
            return valid_ids
        except Exception as e:
            self.logger.error(f"Kitap ID'leri doğrulanırken hata: {str(e)}")
            return [] 