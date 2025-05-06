from elasticsearch import Elasticsearch, helpers
from datetime import datetime
from elasticsearch.helpers import BulkIndexError
import base64

es = Elasticsearch("http://localhost:9200", timeout=30)

def encode_file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

file_path = r"C:\Users\HP\Downloads\VolunteerUserManual (3).pdf"
file_base64 = encode_file_to_base64(file_path)
index_name = "questions"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"🗑️ تم حذف index القديم: {index_name}")

es.indices.create(
    index=index_name,
    body={
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "paragraph": {"type": "text"},
                "files": {"type": "text"},
                "file_base64": {"type": "text"},
                "keywords": {"type": "keyword"},
                "question_type": {"type": "keyword"},
                "changes": {"type": "text"},
                "related_questions": {
                    "type": "nested",
                    "properties": {
                        "q_id": {"type": "integer", "null_value": -1},
                        "q_title": {"type": "text"},
                        "type": {"type": "keyword"}
                    }
                },
                "category": {"type": "keyword"},
                "timestamp": {"type": "date"}
            }
        }
    }
)

print(f"✅ تم إنشاء index: {index_name} مع mapping مناسب")

raw_documents = [
    {
        "title": "ما هي أزمة المياه في العراق؟",
        "paragraph": "يعاني العراق من شح متزايد في الموارد المائية بسبب قلة الأمطار وسدود دول الجوار.",
        "files": ["iraq_water_crisis.pdf"],
        "file_base64": file_base64,
        "keywords": ["مياه", "العراق", "شح", "أنهار"],
        "question_type": "رئيسي",
        "changes": "إضافة بيانات حديثة عن نسب المياه",
        "related_questions": [
            "ما هي أسباب شح المياه في العراق؟",
            "ما تأثير سدود تركيا وإيران على العراق؟"
        ],
        "category": "موارد مائية"
    },
    {
        "title": "ما دور سد الموصل في الأمن المائي؟",
        "paragraph": "يعد سد الموصل أحد أكبر السدود في العراق وله دور استراتيجي في خزن المياه وتوليد الكهرباء.",
        "files": ["mosul_dam_info.pdf"],
        "file_base64": file_base64,
        "keywords": ["سد", "الموصل", "مياه", "العراق"],
        "question_type": "فرعي",
        "changes": "تحديث معلومات عن وضع السد",
        "related_questions": [
            "ما المخاطر المحتملة لانهيار سد الموصل؟"
        ],
        "category": "بنية تحتية مائية"
    }
]

existing_titles = set(doc["title"] for doc in raw_documents)
additional_docs = []

for doc in raw_documents:
    for rq_title in doc.get("related_questions", []):
        if rq_title not in existing_titles:
            additional_docs.append({
                "title": rq_title,
                "paragraph": "",  
                "files": [],
                "file_base64": "",
                "keywords": [],
                "question_type": "مرتبط",
                "changes": "تمت إضافته تلقائياً كعنصر مرتبط",
                "related_questions": [],
                "category": ["غير مصنف"]
            })
            existing_titles.add(rq_title)

full_documents = raw_documents + additional_docs

title_to_meta = {
    doc["title"]: {"q_id": idx, "type": doc["question_type"]}
    for idx, doc in enumerate(full_documents)
}

documents = []
for idx, doc in enumerate(full_documents):
    related = []
    for rq_title in doc.get("related_questions", []):
        if rq_title in title_to_meta:
            related.append({
                "q_id": title_to_meta[rq_title]["q_id"],
                "q_title": rq_title,
                "type": title_to_meta[rq_title]["type"]
            })
    doc["related_questions"] = related
    doc["timestamp"] = datetime.now().isoformat()
    documents.append(doc)

actions = [
    {
        "_index": index_name,
        "_source": doc
    }
    for doc in documents
]

try:
    response = helpers.bulk(es, actions)
    print(f"✅ تم إدخال {response[0]} مستند(ات) بنجاح في index: {index_name}")
except BulkIndexError as e:
    print("❌ حدثت أخطاء أثناء الإدخال:")
    for error in e.errors:
        print(error)
