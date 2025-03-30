from newspaper import Article
from bs4 import BeautifulSoup
import requests
from typing import Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_article_content(url: str) -> Dict[str, str]:
    """
    Extract article content using newspaper3k, falling back to BeautifulSoup if needed.
    Returns a dictionary containing the article title and content.
    """
    logger.info(f"Attempting to extract content from URL: {url}")
    
    try:
        # First, check if the URL is accessible
        response = requests.get(url)
        response.raise_for_status()  # This will raise an exception for 404, 500, etc.
        
        # Try newspaper3k first
        article = Article(url)
        article.download()
        article.parse()
        
        if not article.text:
            logger.warning("newspaper3k extracted empty content, falling back to BeautifulSoup")
            return fallback_scraper(url)
            
        logger.info("Successfully extracted content using newspaper3k")
        return {
            "title": article.title,
            "content": article.text,
            "source": url
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to access URL: {str(e)}")
        raise Exception(f"Could not access the article URL: {str(e)}")
    except Exception as e:
        logger.error(f"newspaper3k extraction failed: {str(e)}")
        logger.info("Attempting fallback scraper...")
        return fallback_scraper(url)

def fallback_scraper(url: str) -> Dict[str, str]:
    """
    Fallback scraper using BeautifulSoup for sites where newspaper3k fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find title
        title = soup.find('title')
        title_text = title.text if title else "Untitled"
        
        # Try to find main content
        # Common content containers
        content_tags = soup.find_all(['article', 'main', 'div'], class_=['content', 'article', 'post'])
        
        if not content_tags:
            # Fallback to all paragraphs
            content_tags = soup.find_all('p')
        
        content = '\n'.join([tag.get_text().strip() for tag in content_tags])
        
        if not content:
            logger.error("No content could be extracted from the page")
            raise Exception("Could not extract any content from the page")
            
        logger.info("Successfully extracted content using fallback scraper")
        return {
            "title": title_text,
            "content": content,
            "source": url
        }
    except Exception as e:
        logger.error(f"Fallback scraper failed: {str(e)}")
        raise Exception(f"Failed to scrape article: {str(e)}") 