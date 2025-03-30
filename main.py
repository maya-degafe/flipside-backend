from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from scraper import extract_article_content
from ai import analyze_article, extract_topic
from dotenv import load_dotenv
import os
import json
import logging
from urllib.parse import urlparse
from news_search import NewsAPI
from scraper import extract_article_content

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="FlipSide API", description="API for analyzing political news articles")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5183", "https://localhost:5176", "https://localhost:5175", "https://hoosflips.tech", "https://flipside-backend.onrender.com"],  # Added port 5174
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ArticleRequest(BaseModel):
    url: str

class ArticleAnalysis(BaseModel):
    original_article: dict
    ai_analysis: dict
    counter_article: Optional[dict] = None
     
def get_source_bias(url: str) -> str:
    """
    Determine the bias of a news source based on its domain.
    """
    domain = urlparse(url).netloc.lower()
    
    left_sources = ["cnn.com", "msnbc.com", "huffpost.com", "vox.com", "theguardian.com", "nytimes.com"]
    right_sources = ["foxnews.com", "breitbart.com", "dailywire.com", "newsmax.com", "washingtonexaminer.com"]
    
    if any(source in domain for source in left_sources):
        return "left"
    elif any(source in domain for source in right_sources):
        return "right"
    else:
        return "center"

def analyze_url_article(url: str) -> dict:
    """
    Fully analyze an article given its URL.
    """
    try:
        logger.info(f"Starting analysis for URL: {url}")
        
        # Step 1: Extract content
        article = extract_article_content(url)
        logger.info("Successfully extracted article content")
        
        # Step 2: Get bias from domain
        bias = get_source_bias(url)
        logger.info(f"Determined source bias: {bias}")
        
        # Step 3: Analyze with GPT
        ai_analysis_str = analyze_article(article["content"])
        ai_analysis = json.loads(ai_analysis_str)
        logger.info("Successfully completed AI analysis")
        
        # Step 4: Extract topic
        topic = extract_topic(article["content"])
        logger.info(f"Extracted topic: {topic}")
        
        # Step 5: Search for counterpoint article
        news_api = NewsAPI(api_key=os.getenv("NEWS_API_KEY"))
        opposite_bias = "left" if bias == "right" else "right"

        print(f"🔍 Searching for counter article on topic: {topic}, with bias: {opposite_bias}")
        counter_article_data = news_api.search_articles(topic, opposite_bias)
        counter_analysis = None

        if counter_article_data:
            print(f"✅ Found counter article: {counter_article_data['title']}")
            try:
                # Analyze counter article content
                counter_analysis_str = analyze_article(counter_article_data["content"])
                counter_analysis = json.loads(counter_analysis_str)
                logger.info("✅ Completed counter article AI analysis")
            except Exception as e:
                logger.warning(f"⚠️ Failed to analyze counter article: {e}")
        else:
            print("❌ No counterpoint article found.")

        # Step 6: Return results
        result = {
            "original_article": {
                "title": article["title"],
                "source": article["source"],
                "bias": bias,
                "topic": topic
            },
            "ai_analysis": ai_analysis,
        }

        if counter_article_data and counter_analysis:
            result["counter_article"] = {
                "title": counter_article_data["title"],
                "content": counter_article_data["content"],
                "source": counter_article_data["source"],
                "url": counter_article_data.get("url"),
                "ai_analysis": counter_analysis
            }

        return result

    except Exception as e:
        logger.error(f"Error analyzing article: {str(e)}")
        raise
    
@app.get("/")
async def root():
    return {"message": "Welcome to FlipSide API"}

@app.post("/analyze", response_model=ArticleAnalysis)
async def analyze_article_endpoint(request: ArticleRequest):
    """
    Analyze a news article and return its content and AI analysis.
    """
    try:
        # Add more detailed logging
        logger.info(f"Starting analysis for URL: {request.url}")
        
        result = analyze_url_article(request.url)
        
        # Validate the result structure
        if not result or 'original_article' not in result or 'ai_analysis' not in result:
            raise HTTPException(
                status_code=500,
                detail="Invalid analysis result structure"
            )
            
        return result
    except Exception as e:
        logger.error(f"Failed to analyze article: {str(e)}")
        # Return more specific error message
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze article: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 
