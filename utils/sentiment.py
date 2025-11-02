import requests as req
import pandas as pd
import time 
from plyer import notification
from typing import Union, List, Dict

BASE_URL = "http://127.0.0.1:8000/v1/api/sentiment"


def get_top_k_sentiments(
    sentiments: List[Dict[str,float]], /, 
    k: int=3
) -> List[Dict[str,float]]:
    """
    Return the top-k sentiments sorted by confidence (descending).
    """
    # Sort the list by "confidence" descending and slice the first k
    return sorted(sentiments, key=lambda x: x.get("confidence"), reverse=True)[:k]


def get_sentiment(
    text: Union[str, List[str]],
    label_group: str = None
) -> List[Dict[str,float]]:
    """
    Sends text (or list of texts) to the local sentiment API and returns the JSON response.
    
    Args:
        text: Single string or list of strings to analyze.
        label_group: Optional label group path parameter (e.g., 'emotions', 'topics').
    
    Returns:
        List of sentiment results in the same structure as SentimentResponse.
    """
    # Normalize input to a list
    prompts = text if isinstance(text, list) else [text]

    # Prepare URL with optional path param
    url = f"{BASE_URL}/{label_group}" if label_group else BASE_URL

    # The API expects { "prompts": [...] }
    payload = {"prompts": prompts}

    try:
        res = req.post(url, json=payload, timeout=30)
        res.raise_for_status()
        return res.json()
    except req.exceptions.RequestException as e:
        raise SystemExit(f"❌ Request failed: {e}")
    
    
def show_notification(title: str, message: str, timeout: int = 15) -> None:
    """Display a desktop notification."""
    notification.notify(
        title=title,
        message=message,
        timeout=timeout
    )


if __name__ == "__main__":
    result = get_sentiment("I'm going to teach a lesson on Python best practices.")
    sentiments = result[0]["sentiments"]

    top_3 = get_top_k_sentiments(sentiments, k=1)
    top = top_3[0]

    print(sentiments)
    print("\nTop 3:", top_3)

    show_notification("Results Are In!", f"Top result:\n{top['label']} ({top['confidence']:.2%})")
    
    
