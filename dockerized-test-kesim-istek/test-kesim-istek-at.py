from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/mark-acquisition', methods=['GET'])
def mark_acquisition_api():
    # Query parametresinden book_id alınıyor
    book_id = request.args.get('book_id')
    
    if not book_id:
        return jsonify({"error": "book_id parametresi gerekli"}), 400
    
    try:
        book_id = int(book_id)
    except ValueError:
        return jsonify({"error": "book_id bir tam sayı olmalıdır"}), 400
    
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
    successful_books = []

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
            successful_books.append({
                "bookId": book_id,
                "confidence": conf,
                "response": response.json()
            })
        else:
            print(f"Hata: bookId {book_id}:", response.status_code, response.text)
            failed_books.append({
                "bookId": book_id,
                "confidence": conf,
                "status_code": response.status_code,
                "error_message": response.text,
            })

    # API yanıtını hazırla
    result = {
        "bookId": book_id,
        "total_attempts": len(confidences),
        "successful_attempts": len(successful_books),
        "failed_attempts": len(failed_books)
    }
    
    if successful_books:
        result["successful_results"] = successful_books
        
    if failed_books:
        result["failed_results"] = failed_books
        # Başarısız sonuçları dosyaya da kaydet
        with open("failed_books.json", "w", encoding="utf-8") as f:
            json.dump(failed_books, f, indent=2, ensure_ascii=False)

    # Başarılı varsa 200, hepsi başarısızsa 500
    status_code = 200 if successful_books else 500
    
    return jsonify(result), status_code

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "API çalışıyor"}), 200

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=7001)
