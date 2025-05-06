from elasticsearch import Elasticsearch, helpers
from datetime import datetime
from elasticsearch.helpers import BulkIndexError
import base64
import os

es = Elasticsearch("http://localhost:9200", timeout=30)

def encode_file_to_base64(file_path):
    """تحويل ملف إلى base64"""
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

def delete_and_create_index(index_name):
    """حذف وإعادة إنشاء index بمخطط مخصص"""
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
        print(f"🗑️ تم حذف index القديم: {index_name}")

    mapping = {
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

    es.indices.create(index=index_name, body=mapping)
    print(f"✅ تم إنشاء index: {index_name} مع mapping مناسب")

def prepare_documents(raw_documents):
    """إعداد المستندات وضبط الأسئلة المرتبطة"""
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

    return documents

def bulk_insert(index_name, documents):
    """إدخال المستندات دفعة واحدة في Elasticsearch"""
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



def delete_document(index_name, doc_id):
    """حذف مستند باستخدام معرّف المستند"""
    try:
        response = es.delete(index=index_name, id=doc_id)
        print(f"✅ تم حذف المستند: {doc_id}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الحذف: {e}")
def add_document(index_name, document):
    """إضافة مستند جديد إلى الفهرس"""
    try:
        response = es.index(index=index_name, document=document)
        print(f"✅ تم إضافة المستند الجديد: {document['title']}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء الإضافة: {e}")
def update_document(index_name, doc_id, updated_fields):
    """تعديل مستند بناءً على معرّف المستند"""
    try:
        response = es.update(index=index_name, id=doc_id, body={"doc": updated_fields})
        print(f"✅ تم تعديل المستند: {doc_id}")
    except Exception as e:
        print(f"❌ حدث خطأ أثناء التعديل: {e}")
