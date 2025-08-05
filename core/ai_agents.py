import logging
import asyncio
from groq import AsyncGroq, RateLimitError 

from app_config import GROQ_API_KEY

async def spin_chapter(original_text: str) -> dict:
    
    if not GROQ_API_KEY:
        raise ValueError("Groq API Key not found. Please set it in your .env file.")
    
    client = AsyncGroq(api_key=GROQ_API_KEY) 
    
    logging.info("AI Writer Agent (Groq): Spinning chapter...")
    
    system_prompt = (
        "You are an expert fiction author with a knack for modernizing classic prose. "
        "Your task is to rewrite the chapter provided by the user. "
        "Instructions: "
        "1. Style: Change the style to be more modern, fast-paced, and descriptive. Use vivid language. "
        "2. Preserve Core: Do NOT change the plot, characters, settings, or key events. "
        "3. Meaning: Retain the original meaning and narrative arc. "
        "4. Output: Provide only the full rewritten chapter text. Do not add any commentary or introductions."
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": original_text},
                ],
                model="llama3-8b-8192",
            )
            spun_text = chat_completion.choices[0].message.content
            if not spun_text:
                raise ValueError("AI model returned an empty response.")
            
            logging.info("AI Writer Agent (Groq): Chapter spun successfully.")
            return {"status": "success", "spun_text": spun_text}
        except RateLimitError as e:
            logging.warning(f"Groq Rate limit exceeded. Attempt {attempt + 1}/{max_retries}.")
            if attempt + 1 == max_retries:
                return {"status": "failure", "error": str(e)}
            await asyncio.sleep(20)
        except Exception as e:
            logging.error(f"AI Writer Agent (Groq): An unexpected error occurred: {e}")
            return {"status": "failure", "error": str(e)}
            
    return {"status": "failure", "error": "Exceeded max retries."}

async def review_chapter(original_text: str, spun_text: str) -> dict:
    """
    Uses the Groq API to review and refine the spun chapter by comparing
    it against the original text.
    """
    if not GROQ_API_KEY:
        raise ValueError("Groq API Key not found. Please set it in your .env file.")
    client = AsyncGroq(api_key=GROQ_API_KEY)
    
    logging.info("AI Reviewer Agent (Groq): Reviewing chapter...")

    system_prompt = (
        "You are a meticulous book editor. You have been given an original chapter and a rewritten version of it. "
        "Your task is to refine the rewritten version. "
        "Instructions: "
        "1. Compare: Read both the original and the rewritten text carefully. "
        "2. Fact-Check: Ensure the rewritten version has not lost any key plot points, character details, or settings from the original. "
        "3. Improve Flow: Correct any grammatical errors, awkward phrasing, or stylistic inconsistencies in the rewritten version. Make it read more smoothly. "
        "4. Final Output: Provide only the final, polished text of the reviewed chapter. Do not add any extra commentary."
    )
    
    user_content = (
        f"**Original Text:**\n---\n{original_text}\n---\n\n"
        f"**Rewritten Text to Review:**\n---\n{spun_text}\n---"
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            chat_completion = await client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                model="llama3-8b-8192",
            )
            reviewed_text = chat_completion.choices[0].message.content
            if not reviewed_text:
                raise ValueError("AI model returned an empty response during review.")
            
            logging.info("AI Reviewer Agent (Groq): Chapter reviewed successfully.")
            return {"status": "success", "reviewed_text": reviewed_text}
        except RateLimitError as e:
            logging.warning(f"Groq Rate limit exceeded during review. Attempt {attempt + 1}/{max_retries}.")
            if attempt + 1 == max_retries:
                return {"status": "failure", "error": str(e)}
            await asyncio.sleep(20)
        except Exception as e:
            logging.error(f"AI Reviewer Agent (Groq): An unexpected error occurred during review: {e}")
            return {"status": "failure", "error": str(e)}
            
    return {"status": "failure", "error": "Exceeded max retries during review."}