Automated Book Publication Workflow (Backend API)
This project provides a complete, multi-agent backend system designed to automate the initial stages of book publication. It features a robust API to scrape content from a web URL, leverage AI agents for rewriting and reviewing, and support a full human-in-the-loop (HITL) workflow with versioning, semantic search, and voice command capabilities.

System Architecture
The workflow is designed as a sequential pipeline of agents and data stores, managed by a central FastAPI application. This modular architecture ensures that each component is independent and responsible for a single task.

Data Flow:
URL ➔ Scraper Agent ➔ ChromaDB (Raw) ➔ AI Writer ➔ ChromaDB (Spun) ➔ AI Reviewer ➔ ChromaDB (Reviewed) ➔ Human Editor ➔ ChromaDB (Edited)

Core Technologies
Backend: Python, FastAPI

Web Scraping: Playwright

AI Agents: Groq API (Llama 3)

Speech-to-Text: OpenAI Whisper

Vector Database: ChromaDB (for versioning & semantic search)

Process Management: Python's multiprocessing for robust, isolated task execution.

Prerequisites
Before you begin, ensure you have the following installed on your system:

Python 3.10+

Git

ffmpeg (a system dependency for audio processing with Whisper)

Windows: choco install ffmpeg

macOS: brew install ffmpeg

Linux: sudo apt update && sudo apt install ffmpeg

Setup and Installation
Follow these steps to get the project running locally.

Step 1: Clone the Repository

git clone <your-repository-url>
cd automated-book-publication

Step 2: Create and Activate a Virtual Environment
This isolates the project's dependencies from your system's Python installation.

python -m venv venv
# On Windows:
# venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Step 3: Install Dependencies
Install all required Python libraries and download the necessary browser binaries for Playwright.

pip install -r requirements.txt
playwright install

Step 4: Set Up Environment Variables

Create a file named .env in the root directory of the project.

Sign up for a free API key from the Groq Console.

Add your key to the .env file. This file is included in .gitignore and will not be committed to the repository.

GROQ_API_KEY="your-groq-api-key-goes-here"

How to Run the Application
Step 1: Start the Backend Server
With your virtual environment activated, run the following command from the project's root directory:

uvicorn main:app --reload

The server will start and be accessible at http://127.0.0.1:8000. The --reload flag enables hot-reloading for development, automatically restarting the server when you save changes to a file.

Step 2: Access the API Documentation
This project uses FastAPI's automatically generated interactive documentation as its primary interface. Open your web browser and navigate to:
http://127.0.0.1:8000/docs

You can now use this interactive page to explore and test all the API endpoints.

API Endpoints
The following endpoints are available for interaction via the /docs page:

POST /process-chapter/: Triggers the full, end-to-end automated workflow from scraping to AI review.

GET /search/: Performs a semantic search across all document versions using a text query.

POST /search/voice: Performs a semantic search by uploading a recorded audio file.

POST /edit-chapter/: Allows a human to submit a final, edited version of a chapter, completing the HITL workflow.

GET /dataset/preference: Generates a preference dataset from all human edits, formatted for use in RLHF training pipelines.