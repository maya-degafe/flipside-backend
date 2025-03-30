from typing import Dict, List
import openai
from dotenv import load_dotenv
import os

load_dotenv(override=True)

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_article(article_text: str) -> Dict[str, List[str]]:
    """
    Analyze article content using GPT-3.5-turbo to generate summary and pros/cons.
    """
    prompt = f"""
    Analyze the following article and provide:
    1. A concise 3-sentence summary
    2. Three key pros from the article's perspective
    3. Three key cons from the article's perspective
    
    Article:
    {article_text}
    
    Format your response as JSON with the following structure:
    {{
        "summary": "3-sentence summary",
        "pros": ["pro1", "pro2", "pro3"],
        "cons": ["con1", "con2", "con3"]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an impartial political news analyzer."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        raise Exception(f"Failed to analyze article: {str(e)}")

def extract_topic(article_text: str) -> str:
    """
    Extract the main topic/theme of the article using GPT-3.5-turbo.
    """
    prompt = f"""
    Extract the main topic or theme of the following article in 2-3 words:
    
    Article:
    {article_text}
    
    Respond with just the topic, nothing else.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a topic extractor."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        raise Exception(f"Failed to extract topic: {str(e)}") 
