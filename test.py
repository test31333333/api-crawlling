from elasticsearch import Elasticsearch, helpers
from datetime import datetime


es = Elasticsearch("http://localhost:9200", timeout=30)

index_name = "questions"
documents = [
    {
        "title": "ما هي أزمة المياه في العراق؟",
        "paragraph": "يعاني العراق من شح متزايد في الموارد المائية بسبب قلة الأمطار وسدود دول الجوار.",
        "files": ["iraq_water_crisis.pdf"],
        "keywords": ["مياه", "العراق", "شح", "أنهار"],
        "question_type": "رئيسي",
        "changes": "إضافة بيانات حديثة عن نسب المياه",
        "related_questions": ["ما هي أسباب شح المياه في العراق؟", "ما تأثير سدود تركيا وإيران على العراق؟"],
        "category": "موارد مائية",
        "timestamp": datetime.now()
    },
    {
        "title": "ما دور سد الموصل في الأمن المائي؟",
        "paragraph": "يعد سد الموصل أحد أكبر السدود في العراق وله دور استراتيجي في خزن المياه وتوليد الكهرباء.",
        "files": ["mosul_dam_info.pdf"],
        "keywords": ["سد", "الموصل", "مياه", "العراق"],
        "question_type": "فرعي",
        "changes": "تحديث معلومات عن وضع السد",
        "related_questions": ["ما المخاطر المحتملة لانهيار سد الموصل؟"],
        "category": "بنية تحتية مائية",
        "timestamp": datetime.now()
    }
]
actions = [
    {
        "_index": index_name,
        "_source": doc
    }
    for doc in documents
]

response = helpers.bulk(es, actions)
print(f"تم إدخال {response[0]} مستندات بنجاح")
