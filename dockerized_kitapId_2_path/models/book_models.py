from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class BookInfo:
    """Kitap bilgileri data model"""
    id: int
    ders_id: Optional[int]
    ust_kurum_id: int
    adi: str
    seviye: Optional[str]
    ders_adi: Optional[str]
    path: Optional[str]
    domain: Optional[str]
    kurumsalad: Optional[str]
    zip_versiyon: Optional[str]
    
    def to_dict(self) -> dict:
        """Dict formatına çevir"""
        return {
            'Kitap ID': self.id,
            'Ders ID': self.ders_id,
            'Kitap Adı': self.adi,
            'Ders Adı': self.ders_adi,
            'Seviye': self.seviye,
            'Path': self.path,
            'Domain': self.domain,
            'Kurumsal Ad': self.kurumsalad,
            'Zip Versiyon': self.zip_versiyon
        }

@dataclass
class DersInfo:
    """Ders bilgileri data model"""
    id: int
    seviye_id: Optional[int]
    adi: str
    
@dataclass
class UstKurumInfo:
    """Üst kurum bilgileri data model"""
    id: int
    kurumsalad: str
    domain: str

@dataclass
class ZKitapAyarInfo:
    """ZKitap ayar bilgileri data model"""
    kitap_id: int
    zip_versiyon: str 