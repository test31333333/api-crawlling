import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from elasticsearch import Elasticsearch , helpers


app = FastAPI()

rigins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


es = Elasticsearch("http://localhost:9200")
index_name = "answer"

# REPO_PATH = os.path.abspath(".")
# if not os.path.exists(os.path.join(REPO_PATH, ".git")):
#     Repo.init(REPO_PATH)
# repo = Repo(REPO_PATH)

index_mapping = {
    "mappings": {
        "properties": {
            "question": {"type": "text"},
            "question_relation": {
                "properties": {
                    "relations": {"type": "text"},
                    "Province": {"type": "keyword"},
                    "city": {"type": "keyword"},
                    "files": {"type": "keyword"},
                    "q_id": {"type": "keyword"},
                    "relation_type": {"type": "keyword"}
                }
            },
            "q_type": {"type": "keyword"},
            "title": {"type": "text"},
            "subject": {"type": "text"},
            "keyword": {"type": "keyword"},
            "paragraphs": {
                "type": "nested",
                "properties": {
                    "content": {"type": "text"},
                    "change_state": {"type": "keyword"},
                    "files": {"type": "keyword"}
                }
            },
            "author": {
                "properties": {
                    "name": {"type": "text"},
                    "refrens_type": {"type": "keyword"},
                    "tel": {"type": "keyword"},
                    "email": {"type": "keyword"},
                    "place": {"type": "text"}
                }
            }
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_mapping)

class Author(BaseModel):
    name: str
    refrens_type: Optional[str]
    tel: Optional[str]
    email: Optional[EmailStr]
    place: Optional[str]

class Paragraph(BaseModel):
    content: str
    change_state: Optional[str]
    files: Optional[List[str]]

class QuestionRelation(BaseModel):
    relations: Optional[str]
    Province: Optional[str]
    city: Optional[str]
    files: Optional[str]
    q_id: Optional[str]
    relation_type: Optional[str]

class AnswerDoc(BaseModel):
    question: str
    question_relation: Optional[QuestionRelation]
    q_type: Optional[str]
    title: Optional[str]
    subject: Optional[str]
    keyword: Optional[str]
    paragraphs: Optional[List[Paragraph]]
    author: Optional[Author]
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())
class SearchQuery(BaseModel):
    must: Optional[List[dict]] = []
    should: Optional[List[dict]] = []
    must_not: Optional[List[dict]] = []
    filter: Optional[List[dict]] = []


# def commit_git(message: str):
#     repo.git.add(A=True)
#     repo.index.commit(message)

@app.get("/answer")
def root():
    return {"message": "API is running"}


@app.post("/answer/search")
def search_answer(
    must: List[str] = Query(default=[]),
    should: List[str] = Query(default=[]),
    filter: List[str] = Query(default=[]),
    must_not: List[str] = Query(default=[])
):
    es_query = {
        "bool": {
            "must": [{"multi_match": {"query": q, "fields": ["title", "question", "keyword"]}} for q in must],
            "should": [{"multi_match": {"query": q, "fields": ["title", "question", "keyword"]}} for q in should],
            "filter": [{"term": {"keyword": f}} for f in filter],
            "must_not": [{"match": {"title": q}} for q in must_not],
        }
    }

    res = es.search(index=index_name, query=es_query)
    return [hit["_source"] | {"id": hit["_id"]} for hit in res["hits"]["hits"]]



@app.post("/answer/")
def create_answer(answer: AnswerDoc):
    generated_id = str(uuid.uuid4())
    if es.exists(index=index_name, id=generated_id):
        raise HTTPException(status_code=400, detail="Generated ID already exists (rare case)")
    es.index(index=index_name, id=generated_id, document=answer.dict())
    # commit_git(f"Created answer {generated_id}")
    return {"message": "Document created", "id": generated_id}

@app.post("/answer/bulk/")
def bulk_create_answers(answers: List[AnswerDoc]):
    actions = [
        {
            "_index": index_name,
            "_id": str(uuid.uuid4()),
            "_source": answer.dict()
        }
        for answer in answers
    ]

    try:
        success, _ = helpers.bulk(es, actions)
        return {"message": "تم إدخال البيانات بنجاح", "عدد العناصر المدخلة": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطأ في الإدخال الجماعي: {str(e)}")




@app.get("/answer/{answer_id}")
def read_answer(answer_id: str):
    if not es.exists(index=index_name, id=answer_id):
        raise HTTPException(status_code=404, detail="Document not found")
    result = es.get(index=index_name, id=answer_id)
    return result["_source"]





@app.put("/answer/{answer_id}")
def update_answer(answer_id: str, updated_data: AnswerDoc):
    if not es.exists(index=index_name, id=answer_id):
        raise HTTPException(status_code=404, detail="Document not found")
    es.index(index=index_name, id=answer_id, document=updated_data.dict())
    # commit_git(f"Updated answer {answer_id}")
    return {"message": "Document updated", "id": answer_id}



@app.delete("/answer/{answer_id}")
def delete_answer(answer_id: str):
    if not es.exists(index=index_name, id=answer_id):
        raise HTTPException(status_code=404, detail="Document not found")
    es.delete(index=index_name, id=answer_id)
    # commit_git(f"Deleted answer {answer_id}")
    return {"message": "Document deleted", "id": answer_id}


