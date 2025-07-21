#!/usr/bin/env python3
"""
Kitap Bilgileri Export Sistemi Test Scripti
Bu script temel API endpoint'lerini test eder
"""

import requests
import json

BASE_URL = "http://localhost:5010"

def test_health_check():
    """API sağlık kontrolünü test et"""
    try:
        response = requests.get(f"{BASE_URL}/api/books/health")
        print(f"🏥 Sağlık Kontrolü: {response.status_code}")
        print(f"   Yanıt: {response.json()}")
        return response.status_code == 200
    except requests.ConnectionError:
        print("❌ Bağlantı hatası! Flask uygulaması çalışıyor mu?")
        return False
    except Exception as e:
        print(f"❌ Sağlık kontrolü hatası: {e}")
        return False

def test_validation():
    """ID doğrulama endpoint'ini test et"""
    test_ids = [30305, 30306, 99999]  # Son ID muhtemelen geçersiz
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/books/validate",
            json={"kitap_ids": test_ids}
        )
        print(f"\n🔍 ID Doğrulama: {response.status_code}")
        result = response.json()
        print(f"   Toplam İstenen: {result['data']['total_requested']}")
        print(f"   Geçerli: {result['data']['total_valid']}")
        print(f"   Geçersiz: {result['data']['total_invalid']}")
        print(f"   Geçerli ID'ler: {result['data']['valid_ids']}")
        print(f"   Geçersiz ID'ler: {result['data']['invalid_ids']}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Doğrulama testi hatası: {e}")
        return False

def test_book_info():
    """Tekil kitap bilgisi endpoint'ini test et"""
    test_id = 30305
    
    try:
        response = requests.get(f"{BASE_URL}/api/books/info/{test_id}")
        print(f"\n📖 Kitap Bilgisi (ID: {test_id}): {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            data = result['data']
            print(f"   Kitap Adı: {data.get('Kitap Adı', 'N/A')}")
            print(f"   Ders Adı: {data.get('Ders Adı', 'N/A')}")
            print(f"   Seviye: {data.get('Seviye', 'N/A')}")
            print(f"   Path: {data.get('Path', 'N/A')[:50]}..." if data.get('Path') else "   Path: N/A")
        else:
            print(f"   Hata: {response.json().get('message', 'Bilinmeyen hata')}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Kitap bilgisi testi hatası: {e}")
        return False

def test_export():
    """Excel export endpoint'ini test et (dosya indirmez, sadece yanıt kontrol eder)"""
    test_ids = [30305]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/books/export",
            json={"kitap_ids": test_ids}
        )
        print(f"\n📊 Excel Export: {response.status_code}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            print(f"   Content-Type: {content_type}")
            print(f"   Dosya Boyutu: {content_length} bytes")
            print(f"   ✅ Excel dosyası başarıyla oluşturuldu!")
        else:
            try:
                error = response.json()
                print(f"   Hata: {error.get('message', 'Bilinmeyen hata')}")
            except:
                print(f"   HTTP Hata: {response.status_code}")
                
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Export testi hatası: {e}")
        return False

def main():
    """Ana test fonksiyonu"""
    print("🚀 Kitap Bilgileri Export Sistemi Test Suite")
    print("=" * 50)
    
    # Test sonuçları
    results = []
    
    # Testleri çalıştır
    results.append(("Sağlık Kontrolü", test_health_check()))
    
    if results[0][1]:  # Sağlık kontrolü başarılıysa diğer testleri çalıştır
        results.append(("ID Doğrulama", test_validation()))
        results.append(("Kitap Bilgisi", test_book_info()))
        results.append(("Excel Export", test_export()))
    else:
        print("\n⚠️  API erişilemediği için diğer testler atlandı.")
        print("Flask uygulamasının çalıştığından emin olun: python main.py")
    
    # Sonuçları göster
    print("\n" + "=" * 50)
    print("📊 Test Sonuçları:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ BAŞARILI" if result else "❌ BAŞARISIZ"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Sonuç: {passed}/{total} test başarılı")
    
    if passed == total:
        print("🎉 Tüm testler başarılı! Sistem hazır.")
    else:
        print("⚠️  Bazı testler başarısız. Logları kontrol edin.")

if __name__ == "__main__":
    main() 