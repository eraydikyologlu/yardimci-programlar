import requests
import json
import sys

def mark_acquisition(book_id):
    # API URL ve header bilgileri
    url = "https://api.yayincilik.net/api/v1/Books/books/{}/acquisition-marking"
    headers = {
        "accept": "application/json",
        "x-correlationId": "93a20cf7-7b94-45f8-88b8-58706c2b8bf3",
        "x-istemci": "swagger",
        "Client": "WEB",
        "Content-Type": "application/json",
    }

    confidences = [0.97]
    failed_books = []

    for conf in confidences:
        print(f"Gönderilen istek: bookId={book_id}, confidence={conf}")

        payload = {
            "bookId": book_id,
            "marking": False,
            "Confidence": conf,
            "ExcelFolderPath": "F:/PROJECTS/EXE/kazanim_isaretleme_testler",
        }

        response = requests.post(url.format(book_id), headers=headers, json=payload)

        if response.status_code == 200:
            print(f"Başarılı: bookId {book_id}:", response.json())
        else:
            print(f"Hata: bookId {book_id}:", response.status_code, response.text)
            failed_books.append({
                "bookId": book_id,
                "confidence": conf,
                "status_code": response.status_code,
                "error_message": response.text,
            })

    if failed_books:
        with open("failed_books.json", "w", encoding="utf-8") as f:
            json.dump(failed_books, f, indent=2, ensure_ascii=False)
        print(f"\n{len(failed_books)} kitap başarısız oldu. 'failed_books.json' dosyasına kaydedildi.")
    else:
        print("\nTüm işlemler başarıyla tamamlandı.")

# Komut satırından kitap ID alınıyor
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python script.py <book_id>")
        sys.exit(1)

    try:
        book_id_input = int(sys.argv[1])
    except ValueError:
        print("Hata: book_id bir tam sayı olmalıdır.")
        sys.exit(1)

    mark_acquisition(book_id_input)
