# 📚 Automated Book Publication Workflow (Backend API)

This project is a complete, multi-agent backend system designed to automate the initial stages of book publication. It features a robust API to scrape content from a web URL, leverage AI agents for rewriting and reviewing, and support a full human-in-the-loop (HITL) workflow with versioning, semantic search, and voice command capabilities.

---

## 🚀 Features

- **Multi-Agent AI Pipeline**  
  Sequentially uses an AI Writer and an AI Reviewer to process content, ensuring higher quality output.

- **Semantic Search**  
  Leverages a vector database (ChromaDB) to allow for searching by meaning and concept, not just keywords.

- **Human-in-the-Loop (HITL)**  
  Provides API endpoints for human editors to review, edit, and approve content, with all versions tracked.

- **RLHF Data Pipeline**  
  Automatically generates a preference dataset from human edits, ready to be used for fine-tuning AI models.

- **Voice-to-Text Commands**  
  Includes an endpoint that uses OpenAI's Whisper model to transcribe voice commands for hands-free searching.

---

## 📡 API Endpoints

| Method | Endpoint              | Description                                                                 |
|--------|-----------------------|-----------------------------------------------------------------------------|
| POST   | `/process-chapter/`   | Triggers the full, end-to-end automated workflow from scraping to AI review. |
| GET    | `/search/`            | Performs a semantic search across all document versions using a text query. |
| POST   | `/search/voice`       | Performs a semantic search by uploading a recorded audio file.              |
| POST   | `/edit-chapter/`      | Allows a human to submit a final, edited version of a chapter.              |
| GET    | `/dataset/preference` | Generates a preference dataset from human edits for RLHF training.          |

---

## 🛠 Project Setup & How to Run

### ✅ Prerequisites

- Python 3.10+
- Git
- ffmpeg (required for Whisper audio processing)

Install `ffmpeg`:
- **Windows:** `choco install ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Linux:** `sudo apt update && sudo apt install ffmpeg`

---

### 📥 Step-by-Step Instructions

#### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd automated-book-publication
```

#### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 3. Install dependencies
```bash
pip install -r requirements.txt
playwright install
```

---
### 🔐 Set Up Environment Variables
- 1. Create a .env file in the root directory.
- 2. Get your API key from the Groq Console (free signup).
-3. Add your key to .env:
```env
GROQ_API_KEY="your-groq-api-key-goes-here"
```
- **Note:** .env is ignored by Git for security.

---
### ▶️ Start the Backend Server
```bash
uvicorn main:app --reload
```
- The --reload flag enables hot-reloading for development.

---
### Access the Application
- Open your browser and visit: http://127.0.0.1:8000/docs
- Explore and test all API endpoints through Swagger UI.

---
### Stop the Application
- To stop the server, press CTRL + C in the terminal where Uvicorn is running.

---
## License
MIT

---
## 🙌 Contributing
- Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change 


