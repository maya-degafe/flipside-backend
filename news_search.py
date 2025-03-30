from typing import Dict, Optional
import requests
from datetime import datetime, timedelta
from bias_utils import get_source_bias

class NewsAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"

    def search_articles(self, query: str, bias: str, days: int = 7) -> Optional[Dict]:
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            from_date = start_date.strftime("%Y-%m-%d")
            to_date = end_date.strftime("%Y-%m-%d")

            params = {
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": "en",
                "sortBy": "relevancy",
                "apiKey": self.api_key
            }

            response = requests.get(f"{self.base_url}/everything", params=params)
            #print(f"NewsAPI response status: {response.status_code}")
            #print(f"NewsAPI response body: {response.text}")
            response.raise_for_status()

            data = response.json()
            if data["status"] == "ok" and data["articles"]:
                best_match = None

                for article in data["articles"]:
                    source_url = article.get("url", "")
                    source_bias = get_source_bias(source_url)

                    if source_bias == bias:
                        return {
                            "title": article["title"],
                            "content": article["description"],
                            "url": article["url"],
                            "source": article["source"]["name"],
                            "bias": source_bias,
                            "biasMatch": True
                        }

                    # Save the first article as fallback if nothing matches exactly
                    if not best_match:
                        best_match = {
                            "title": article["title"],
                            "content": article["description"],
                            "url": article["url"],
                            "source": article["source"]["name"],
                            "bias": source_bias,
                            "biasMatch": False  # Bias doesn't match exactly
                        }

                # If no exact match, return best available
                if best_match:
                    return best_match
            return None

        except Exception as e:
            print(f"Error searching articles: {str(e)}")
            return None
        
    def _matches_bias(self, source_name: str, target_bias: str) -> bool:
        source_name = source_name.lower()

        bias_sources = {
            "left": ["cnn", "msnbc", "huffpost", "vox",'apnews','buzzfeed','dailybeast','democracynow'
                                                 ,'washingtonpost','nytimes','politico'],
            "right": ["fox", "breitbart", "daily wire", "newsmax","dailywire","dailymail","nationalreview","newsmax","thedailycaller","thefederalist","washingtonfreebeacon"],
            "center": ['reuters','bbc','forbes','thehill','reason']
        }

        for keyword in bias_sources.get(target_bias, []):
            if keyword in source_name:
                return True
        return False
    
# For development/testing, we can use a stub version
def get_stub_counter_article(topic: str, bias: str) -> Dict:
    """
    Return a stub counter article for development/testing.
    """
    return {
        "title": f"Counter Article About {topic}",
        "content": f"This is a sample counter article about {topic} from a {bias}-leaning source.",
        "url": "https://example.com/counter-article",
        "source": "Example News",
        "bias": bias
    } 
