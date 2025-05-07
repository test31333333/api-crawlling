from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from elasticsearch import Elasticsearch
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
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
INDEX_NAME = "questions"

class Question(BaseModel):
    title: str
    paragraph: str
    files: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    question_type: Optional[str] = "غير محدد"
    changes: Optional[str] = ""
    related_questions: Optional[List[str]] = []
    category: Optional[str] = ""
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.now().isoformat())

@app.post("/questions/")
def add_question(question: Question):
    res = es.index(index=INDEX_NAME, document=question.dict())
    res = es.get(index=INDEX_NAME, id=res["_id"])
    return res["_source"]
    # return {"id": res["_id"], "status": res["result"]}

@app.get("/questions/{question_id}")
def get_question(question_id: str):
    try:
        res = es.get(index=INDEX_NAME, id=question_id)
        return res["_source"]
    except:
        raise HTTPException(status_code=404, detail="لم يتم العثور على المستند")

@app.get("/questions/")
def get_all_questions():
    res = es.search(index=INDEX_NAME, query={"match_all": {}})
    return [hit["_source"] | {"id": hit["_id"]} for hit in res["hits"]["hits"]]

@app.put("/questions/{question_id}")
def update_question(question_id: str, question: Question):
    if not es.exists(index=INDEX_NAME, id=question_id):
        raise HTTPException(status_code=404, detail="المستند غير موجود للتحديث")
    
    es.index(index=INDEX_NAME, id=question_id, document=question.dict())
    return {"id": question_id, "status": "تم التحديث"}

@app.delete("/questions/{question_id}")
def delete_question(question_id: str):
    if not es.exists(index=INDEX_NAME, id=question_id):
        raise HTTPException(status_code=404, detail="المستند غير موجود للحذف")
    
    es.delete(index=INDEX_NAME, id=question_id)
    return {"id": question_id, "status": "تم الحذف"}
