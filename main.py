from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from concept_data import CONCEPT_DB

app = FastAPI(title="Govt Exam Tutor API", version="1.0")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/topic-quiz")
def get_topic_quiz(topic: str = Query(..., description="Topic name like 'profit and loss', 'percentage', etc.")) -> Dict:
    topic_lower = topic.lower()
    if topic_lower in CONCEPT_DB:
        return CONCEPT_DB[topic_lower]
    return {"concept": "No data found for this topic.", "quiz": []}

@app.get("/topics")
def list_topics():
    return {"topics": sorted([k.title() for k in CONCEPT_DB.keys()])}
