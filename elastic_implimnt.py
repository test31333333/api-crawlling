from elastic import encode_file_to_base64, delete_and_create_index, prepare_documents, bulk_insert,update_document

index_name = "questions"
file_path = r"C:\Users\HP\Downloads\VolunteerUserManual (3).pdf"
file_base64 = encode_file_to_base64(file_path)

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

delete_and_create_index(index_name)
documents = prepare_documents(raw_documents)
bulk_insert(index_name, documents)


# doc_id = "J9J-pZYBNCSWuAdwLfUp" 
# updated_fields = {
#     "paragraph": "الذكاء الاصطناعي يشمل كل ما يتعلق بتعليم الآلات كيفية التعامل مع البيانات واتخاذ القرارات بناءً عليها.",
#     "keywords": ["ذكاء اصطناعي", "تعلم الآلة", "تعلم"]
# }

# update_document(index_name, doc_id, updated_fields)


# doc_id_to_delete = "KdJ-pZYBNCSWuAdwLfUp"  

# delete_document(index_name, doc_id_to_delete)
