import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

TARGET_URL = "https://en.wikisource.org/wiki/The_Gates_of_Morning/Book_1/Chapter_1"