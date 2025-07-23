from flask import Flask, send_file, jsonify
from flask_cors import CORS
from elasticsearch import Elasticsearch
import pandas as pd
from sqlalchemy import create_engine
import tempfile
import os

app = Flask(__name__)
CORS(app)

@app.route('/eksik-kitaplar', methods=['GET'])
def eksik_kitaplar():
    try:
        # Elastic'ten unique kitap id'lerini çek
        es = Elasticsearch("http://elastic.dijidemi.com:80", basic_auth=("elastic", "123654-"))
        index_name = "question_bank"
        agg_name = "all_unique_ids"
        all_ids = []
        after_key = None
        while True:
            body = {
                "size": 0,
                "aggs": {
                    agg_name: {
                        "composite": {
                            "size": 1000,
                            "sources": [
                                {"KitapId": {"terms": {"field": "KitapId"}}}
                            ]
                        }
                    }
                }
            }
            if after_key:
                body["aggs"][agg_name]["composite"]["after"] = after_key
            response = es.search(index=index_name, body=body)
            buckets = response["aggregations"][agg_name]["buckets"]
            for bucket in buckets:
                all_ids.append(bucket["key"]["KitapId"])
            after_key = response["aggregations"][agg_name].get("after_key")
            if not after_key:
                break
        elastic_kitap_ids = set(all_ids)

        # SQL Server'dan kitapları çek
        engine = create_engine("mssql+pymssql://muzaffer.yalcin:Impark2025!*@sql.impark.local/olcme_db")
        sql_query = """
        SELECT 
            u.Id AS UstKurumId, u.Adi AS UstKurumAdi, u.Domain,
            k.Id AS KitapId, k.Adi AS KitapAdi,
            d.DenemeOlustur,
            k.ZKitapId, z.ZipVersiyon, z.ZKitap,
            z.ZKitapVersion
        FROM S_TestKitaplar k
        INNER JOIN S_UstKurumlar u ON u.Id = k.UstKurumId
        INNER JOIN S_TestKitaplarZKitapAyar z ON z.KitapId = k.Id
        INNER JOIN S_TestKitaplarDetay d ON d.KitapId = k.Id
        INNER JOIN S_Testler t ON t.KitapId = k.Id
        WHERE 
            u.Aktif = 1 AND k.Silindi = 0 AND u.Id <> 117
            AND t.Silindi = 0 AND t.SoruSayisi > 0
            AND k.Id NOT IN (SELECT DISTINCT EskiKitapId FROM S_TestEskiKitaplar)
            AND z.ZKitapVersion IS NOT NULL 
            AND d.PaketExe IS NULL
        GROUP BY 
            u.Id, u.Adi, u.Domain,
            k.Id, k.Adi,
            d.DenemeOlustur,
            k.ZKitapId, z.ZipVersiyon, z.ZKitap,
            z.ZKitapVersion
        ORDER BY u.Id, k.Id
        """
        sql_df = pd.read_sql(sql_query, engine)
        sql_kitap_ids = set(sql_df["KitapId"].tolist())

        # Eksik kitapları bul
        eksik_ids = sql_kitap_ids - elastic_kitap_ids
        eksik_df = sql_df[sql_df["KitapId"].isin(eksik_ids)]

        # Geçici dosyaya yaz
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
            eksik_df.to_excel(tmp.name, index=False)
            tmp_path = tmp.name
        return send_file(tmp_path, as_attachment=True, download_name="elasticte_olmayan_kitaplar.xlsx")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Geçici dosyayı sil
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004) 