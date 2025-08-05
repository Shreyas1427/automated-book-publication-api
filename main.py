from fastapi import FastAPI, HTTPException
import logging
import uuid
from fastapi.middleware.cors import CORSMiddleware 
import multiprocessing as mp

from core.database import add_content_to_db, get_document, search_documents, get_preference_dataset
from core.scraper import scrape_worker
from core.ai_agents import spin_chapter, review_chapter 
from app_config import TARGET_URL
from pydantic import BaseModel, Field
from fastapi import UploadFile, File
from core.voice import transcribe_audio_to_text
import shutil

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
app = FastAPI(title="Automated Book Publication Workflow")

origins = [
    "*",
]

@app.get("/")
def read_root():
    return {"message": "Welcome. Go to /docs for the main endpoint."}

@app.post("/process-chapter/", summary="Run the Full Chapter Processing Workflow")
async def process_full_chapter_workflow():
    
    logging.info("--- Workflow Step 1: Launching Scraper in Separate Process ---")
    queue = mp.Queue()
    process = mp.Process(target=scrape_worker, args=(TARGET_URL, queue))
    process.start()
    try:
        scrape_result = queue.get(timeout=90)
    finally:
        process.join()
    if scrape_result["status"] == "failure":
        raise HTTPException(status_code=500, detail=f"Scraping failed: {scrape_result['error']}")

    logging.info("--- Main process received data. Saving raw version to DB. ---")
    raw_doc_id = f"chapter_1_raw_{uuid.uuid4()}"
    metadata_raw = {"version": 0, "status": "raw", "source_url": scrape_result["source_url"], "screenshot_path": scrape_result["screenshot_path"]}
    add_content_to_db(scrape_result["text"], raw_doc_id, metadata_raw)

    logging.info("--- Workflow Step 3: Spinning with AI Writer ---")
    raw_document = get_document(raw_doc_id)
    if not raw_document:
        raise HTTPException(status_code=404, detail=f"Could not retrieve {raw_doc_id}")
    
    spin_result = await spin_chapter(raw_document["text"]) 
    if spin_result["status"] == "failure":
        raise HTTPException(status_code=500, detail=f"AI spinning failed: {spin_result['error']}")
    spun_text = spin_result["spun_text"]

    logging.info("--- Workflow Step 4: Saving Spun Version ---")
    spun_doc_id = f"chapter_1_spun_{uuid.uuid4()}"
    metadata_spun = {"version": 1, "status": "spun_ai", "parent_id": raw_doc_id, "model": "llama3-8b-8192"}
    add_content_to_db(spun_text, spun_doc_id, metadata_spun)

    logging.info("--- Workflow Step 5: Reviewing with AI Reviewer ---")
    review_result = await review_chapter(original_text=raw_document["text"], spun_text=spun_text) # Using the full text
    if review_result["status"] == "failure":
        raise HTTPException(status_code=500, detail=f"AI reviewing failed: {review_result['error']}")
    reviewed_text = review_result["reviewed_text"]

    logging.info("--- Workflow Step 6: Saving Reviewed Version ---")
    reviewed_doc_id = f"chapter_1_reviewed_{uuid.uuid4()}"
    metadata_reviewed = {"version": 2, "status": "reviewed_ai", "parent_id": spun_doc_id, "model": "llama3-8b-8192"}
    add_content_to_db(reviewed_text, reviewed_doc_id, metadata_reviewed)

    logging.info("--- Workflow Completed Successfully ---")
    
    return {
        "message": "Chapter processed and reviewed successfully!",
        "raw_document": {"id": raw_doc_id, "preview": raw_document["text"][:150] + "..."},
        "spun_document": {"id": spun_doc_id, "preview": spun_text[:150] + "..."},
        "reviewed_document": {"id": reviewed_doc_id, "preview": reviewed_text[:150] + "..."}
    }

@app.get("/search/", summary="Search for content across all chapter versions")
def search_in_documents(q: str):

    if not q:
        raise HTTPException(status_code=400, detail="Query parameter 'q' cannot be empty.")
    
    search_results = search_documents(query_text=q, n_results=5)
    
    if not search_results:
        return {"message": "No relevant documents found."}
        
    return {"results": search_results}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"], 
)

class EditPayload(BaseModel):
    parent_id: str = Field(..., description="The ID of the document version you are editing.")
    new_text: str = Field(..., description="The new, human-edited text content.")

@app.post("/edit-chapter/", summary="Submit a human-edited version of a chapter")
def submit_human_edit(payload: EditPayload):

    logging.info(f"--- Received human edit for parent document: {payload.parent_id} ---")
    
    parent_document = get_document(payload.parent_id)
    if not parent_document:
        raise HTTPException(status_code=404, detail=f"Parent document with ID {payload.parent_id} not found.")

    parent_version = parent_document["metadata"].get("version", 0)
    new_version = parent_version + 1

    human_edited_doc_id = f"chapter_1_human_v{new_version}_{uuid.uuid4()}"
    metadata = {
        "version": new_version,
        "status": "human_edited",
        "parent_id": payload.parent_id,
        "editor": "human_01" 
    }
    
    add_content_to_db(payload.new_text, human_edited_doc_id, metadata)
    
    logging.info(f"Successfully saved human-edited version with ID: {human_edited_doc_id}")
    
    return {
        "message": "Human edit saved successfully!",
        "new_document_id": human_edited_doc_id,
        "parent_document_id": payload.parent_id
    }

@app.get("/dataset/preference", summary="Generate a preference dataset for RLHF")
def create_preference_dataset():
   
    dataset = get_preference_dataset()
    if not dataset:
        return {"message": "No human edits found to create a dataset."}
    
    return {"preference_dataset": dataset}

@app.post("/search/voice", summary="Perform semantic search using a voice query")
async def voice_search(file: UploadFile = File(...)):
   
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    query_text = transcribe_audio_to_text(temp_file_path)

    if not query_text:
        raise HTTPException(status_code=500, detail="Could not transcribe audio. Please try again.")

    search_results = search_documents(query_text=query_text, n_results=3)

    if not search_results:
        return {"message": "No relevant documents found for your voice query.", "transcribed_text": query_text}
        
    return {"transcribed_text": query_text, "results": search_results}