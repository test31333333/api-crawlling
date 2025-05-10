import base64
import uuid
import os
from elasticsearch import Elasticsearch
from pydantic import BaseModel,Field , EmailStr
from typing import List, Optional
from datetime import datetime
from fastapi import FastAPI 
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

es = Elasticsearch("http://192.168.10.102:9200")

index_name = "answer"

index_mapping = {
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
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

# if es.indices.exists(index=index_name):
#     # es.indices.delete(index=index_name)
#     # print(f"Index '{index_name}' deleted.")



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
    id: str
    question: str
    question_relation: Optional[QuestionRelation]
    q_type: Optional[str]
    title: Optional[str]
    subject: Optional[str]
    keyword: Optional[str]
    paragraphs: Optional[List[Paragraph]]
    author: Optional[Author]
    timestamp :Optional[datetime] = Field(default_factory=lambda: datetime.now().isoformat())


