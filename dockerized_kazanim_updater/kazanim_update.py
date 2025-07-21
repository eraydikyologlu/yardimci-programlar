import logging
import pymssql
from elasticsearch import Elasticsearch, helpers
from fastapi import FastAPI, HTTPException
from typing import Optional
import uvicorn

# ====================== FUNCTIONS ======================
import requests
# ====================== CONFIG ======================
MSSQL_CONFIG = {
    "server": "sql.impark.local",
    "user": "enes.karatas",
    "password": "Exkaratas2021!*",
    "database": "olcme_db"
}

ES_HOST = "http://elastic.dijidemi.com:80"
ES_USER = "elastic"
ES_PASS = "123654-"
ES_INDEX = "question_bank"

# ====================== LOGGING ======================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KazanimGuncelleyici")

# ====================== FASTAPI APP ======================
app = FastAPI(title="Kazanim Updater API", version="1.0.0")

# ====================== DB & ES CONNECTION ======================
es = Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS))

db = pymssql.connect(
    server=MSSQL_CONFIG["server"],
    user=MSSQL_CONFIG["user"],
    password=MSSQL_CONFIG["password"],
    database=MSSQL_CONFIG["database"]
)
cursor = db.cursor(as_dict=True)

def tahmin_et_kazanimid(dersId , question_content):
    if dersId is None or question_content is None:
        return 0

    url = f"http://bcaicpu.impark.local:5005/api/kazanim_isaretleme?soru_metni={question_content}&ders_id={dersId}"
    headers = {
        "x-api-key": "rMGgnVjOyQizdhwYRTcZuxFkIZUanumJ"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            response_json = response.json()
            if "result" in response_json and "kazanim_id" in response_json["result"]:
                return response_json["result"]["kazanim_id"]
            else:
                logger.warning(f"Model yanıtında 'result' veya 'kazanim_id' yok → JSON: {response_json}")
                return 0
        else:
            logger.warning(f"Model API hatası: {response.status_code} → {response.text}")
            return 0
    except Exception as e:
        logger.error(f"Model istek hatası: {e}")
        return 0

def veritabani_kazanim_getir(kitap_id, test_id, soru_id):
    try:
        cursor.execute("""
            SELECT TOP 1 KazanimId 
            FROM S_CaprazGorevHistoryKazanim
            WHERE KitapId = %s AND TestId = %s AND SoruId = %s
              AND KazanimId IS NOT NULL AND KazanimId != 0
        """, (kitap_id, test_id, soru_id))
        row = cursor.fetchone()
        return row["KazanimId"] if row else None
    except Exception as e:
        logger.error(f"DB hatası (KitapId={kitap_id}, TestId={test_id}, SoruId={soru_id}): {e}")
        return None

def kazanim_guncelle(doc_id, kazanim_id):
    try:
        es.update(index=ES_INDEX, id=doc_id, body={"doc": {"KazanimId": kazanim_id}})
        logger.info(f"Güncellendi: {doc_id} → KazanimId={kazanim_id}")
        return True
    except Exception as e:
        logger.error(f"Elastic update hatası {doc_id}: {e}")
        return False

def build_query(ders_id=None, kitap_id=None):
    filters = [
        {
            "bool": {
                "should": [
                    {"term": {"KazanimId": 0}},
                    {"bool": {"must_not": {"exists": {"field": "KazanimId"}}}}
                ]
            }
        }
    ]
    if ders_id:
        filters.append({"term": {"DersId": ders_id}})
    if kitap_id:
        filters.append({"term": {"KitapId": kitap_id}})
    return {"bool": {"filter": filters}}

def process_kazanim_update(ders_id=None, kitap_id=None):
    """Ana işlem fonksiyonu"""
    query = {
        "query": build_query(ders_id, kitap_id)
    }

    results = helpers.scan(
        es,
        index=ES_INDEX,
        query=query,
        _source=["DersId", "KitapId", "TestId", "SoruNo", "SoruMetin"]
    )

    processed_count = 0
    updated_count = 0

    for doc in results:
        _id = doc["_id"]
        src = doc["_source"]

        kitap_id_ = src.get("KitapId")
        test_id = src.get("TestId")
        soru_no = src.get("SoruNo")
        ders_id_ = src.get("DersId")
        soru_metin = src.get("SoruMetin", "")
        
        processed_count += 1
        
        if not (kitap_id_ and test_id is not None and soru_no is not None):
            logger.warning(f"Veri eksik: {_id}")
            continue

        # 1. DB kontrolü
        kazanim_db = veritabani_kazanim_getir(kitap_id_, test_id, soru_no)
        if kazanim_db:
            if kazanim_guncelle(_id, kazanim_db):
                updated_count += 1
        else:
            # 2. Tahmin et
            if not ders_id_:
                logger.warning(f"DersId eksik, model kullanılamaz: {_id}")
                continue
            
            tahmin = tahmin_et_kazanimid(ders_id_, soru_metin)
            if kazanim_guncelle(_id, tahmin):
                updated_count += 1

    return processed_count, updated_count

# ====================== API ENDPOINTS ======================
@app.get("/")
async def root():
    return {"message": "Kazanim Updater API çalışıyor!", "version": "1.0.0"}

@app.post("/update-kazanim")
async def update_kazanim(ders_id: Optional[int] = None, kitap_id: Optional[int] = None):
    """
    Kazanım güncelleme işlemini başlatır
    
    - **ders_id**: Sadece bu DersId'deki sorular işlenir (opsiyonel)
    - **kitap_id**: Sadece bu KitapId'deki sorular işlenir (opsiyonel)
    """
    try:
        logger.info(f"Kazanım güncelleme başlatıldı - DersId: {ders_id}, KitapId: {kitap_id}")
        
        processed_count, updated_count = process_kazanim_update(ders_id, kitap_id)
        
        return {
            "success": True,
            "message": "Kazanım güncelleme tamamlandı",
            "processed_count": processed_count,
            "updated_count": updated_count,
            "ders_id": ders_id,
            "kitap_id": kitap_id
        }
    except Exception as e:
        logger.error(f"API hatası: {e}")
        raise HTTPException(status_code=500, detail=f"İşlem sırasında hata oluştu: {str(e)}")

@app.get("/health")
async def health_check():
    """Sistem sağlık kontrolü"""
    try:
        # Elasticsearch bağlantı kontrolü
        es_status = es.ping()
        
        # MSSQL bağlantı kontrolü
        cursor.execute("SELECT 1")
        db_status = True
        
        return {
            "status": "healthy",
            "elasticsearch": "connected" if es_status else "disconnected",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# ====================== SERVER START ======================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7002)
