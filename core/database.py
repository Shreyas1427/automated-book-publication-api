import chromadb
from chromadb.types import Collection
import logging


def get_db_collection() -> Collection:
    try:
        client = chromadb.PersistentClient(path="./data")
        collection = client.get_or_create_collection(name="the_gates_of_morning")
        return collection
    except Exception as e:
        logging.error(f"Failed to get or create collection: {e}")
        raise

def add_content_to_db(text: str, doc_id: str, metadata: dict):
    try:
        collection = get_db_collection() 
        collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        logging.info(f"Successfully added document '{doc_id}' to the database.")
    except Exception as e:
        logging.error(f"Could not add document '{doc_id}' to the database: {e}")
        raise

def get_document(doc_id: str) -> dict | None:
    try:
        collection = get_db_collection() 
        result = collection.get(ids=[doc_id], include=["metadatas", "documents"])
        
        if not result or not result['ids']:
            logging.warning(f"Document with ID '{doc_id}' not found in the database.")
            return None
        
        retrieved_doc = {
            "id": result["ids"][0],
            "text": result["documents"][0],
            "metadata": result["metadatas"][0]
        }
        logging.info(f"Successfully retrieved document: '{doc_id}'")
        return retrieved_doc
    except Exception as e:
        logging.error(f"Could not retrieve document '{doc_id}': {e}")
        return None

def search_documents(query_text: str, n_results: int = 3) -> list:
   
    try:
        collection = get_db_collection()
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=["metadatas", "documents", "distances"]
        )
        
        if not results['ids'][0]:
            return []
            
        result_list = []
        for i in range(len(results['ids'][0])):
            result_list.append({
                "id": results['ids'][0][i],
                "distance": results['distances'][0][i], 
                "metadata": results['metadatas'][0][i],
                "document": results['documents'][0][i]
            })
        
        logging.info(f"Search for '{query_text}' found {len(result_list)} results.")
        return result_list

    except Exception as e:
        logging.error(f"An error occurred during search: {e}")
        return []    

def get_preference_dataset() -> list:
   
    collection = get_db_collection()
    dataset = []

    human_edits = collection.get(
        where={"status": "human_edited"},
        include=["metadatas", "documents"]
    )

    if not human_edits['ids']:
        logging.info("No human edits found in the database to create a dataset.")
        return []

    for i in range(len(human_edits['ids'])):
        chosen_doc = {
            "id": human_edits['ids'][i],
            "text": human_edits['documents'][i],
            "metadata": human_edits['metadatas'][i]
        }
        
        rejected_id = chosen_doc["metadata"].get("parent_id")
        if not rejected_id:
            continue 

        rejected_doc = get_document(rejected_id)
        if not rejected_doc:
            continue 

        prompt_doc = rejected_doc
        while prompt_doc and prompt_doc['metadata'].get('status') != 'raw':
            parent_id = prompt_doc['metadata'].get('parent_id')
            if not parent_id:
                prompt_doc = None 
                break
            prompt_doc = get_document(parent_id)

        if prompt_doc:
            dataset.append({
                "prompt": prompt_doc['text'],
                "chosen": chosen_doc['text'],
                "rejected": rejected_doc['text']
            })

    logging.info(f"Generated preference dataset with {len(dataset)} entries.")
    return dataset

