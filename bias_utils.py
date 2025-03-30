import json
from typing import Dict, Optional
from urllib.parse import urlparse

def load_bias_sources() -> Dict[str, str]:
    """
    Load the bias sources mapping from JSON file.
    """
    try:
        with open('bias_sources.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def get_source_bias(url: str) -> Optional[str]:
    """
    Determine the political bias of a news source based on its domain.
    Returns 'left', 'right', or 'center' if known, None if unknown.
    """
    domain = urlparse(url).netloc.lower()
    bias_sources = load_bias_sources()
    
    # Remove 'www.' if present
    domain = domain.replace('www.', '')
    
    # Check if domain is in our bias mapping
    if domain in bias_sources:
        return bias_sources[domain]
    
    # Check common patterns
    # Source for patterns: https://www.allsides.com/media-bias/ratings
    if any(domain.endswith(site) for site in ['foxnews.com', 'breitbart.com', 'dailywire.com','dailymail.com','nationalreview.com','newsmax.com','thedaillycaller.com','thefederalist.com','washingtonfreebeacon.com']):
        return 'right'
    elif any(domain.endswith(site) for site in ['cnn.com', 'msnbc.com', 'huffpost.com','apnews.com','buzzfeed.com','dailybeast.com','democracynow.org' ,'nytimes.com','politico.com','vox.com']):
        return 'left'
    elif any(domain.endswith(site) for site in ['reuters.com', 'bloomberg.com','bbc.com','forbes.com','thehill.com']):
        return 'center'
    
    return None

def find_opposing_bias(current_bias: str) -> str:
    """
    Given a current bias, return the opposing bias.
    """
    if current_bias == 'left':
        return 'right'
    elif current_bias == 'right':
        return 'left'
    else:
        return 'center'  # Default to center if bias is unknown or center 