import base64
import uuid
import os
from elasticsearch import Elasticsearch

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

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print(f"Index '{index_name}' deleted.")

es.indices.create(index=index_name, body=index_mapping)
print(f"Index '{index_name}' created successfully.")
