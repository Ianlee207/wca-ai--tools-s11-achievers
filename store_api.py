import os
import re
import requests
from bs4 import BeautifulSoup

try:
    from serpapi import GoogleSearch
except ImportError:
    GoogleSearch = None

# Global environment variables
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")


def fetch_global_product_price(product_name: str, country_code: str, preferred_store: str = ""):
    """Queries SerpApi Google Shopping engine for live product prices."""
    if SERPAPI_API_KEY and GoogleSearch:
        query = f"{preferred_store} {product_name}".strip() if preferred_store else product_name
        params = {
            "engine": "google_shopping",
            "q": query,
            "gl": country_code,
            "api_key": SERPAPI_API_KEY,
        }
        try:
            search = GoogleSearch(params)
            results = search.get_dict()
            shopping = results.get("shopping_results", [])
            if shopping:
                top_match = shopping[0]
                return {
                    "title": top_match.get("title", product_name),
                    "price_raw": str(top_match.get("price", "0")),
                    "extracted_price": float(top_match.get("extracted_price", 0.0)),
                    "store": top_match.get("source", preferred_store or "Online Store"),
                    "link": top_match.get("link", "")
                }
        except Exception as e:
            print(f"⚠️ SerpApi Warning: {e}")

    # Fallback web scrape if API key is unverified or returns no results
    return fallback_web_scrape(product_name, preferred_store)


def fallback_web_scrape(product_name: str, store_name: str = ""):
    """Fallback DuckDuckGo web scraping when API is unavailable."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        search_query = f"{product_name} {store_name} price".strip()
        search_url = f"https://html.duckduckgo.com/html/?q={search_query}"
        
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            snippets = soup.find_all("a", class_="result__snippet")
            
            for snippet in snippets:
                text = snippet.text
                # Match prices formatted with $, KSh, or numbers with commas/decimals
                match = re.search(r"(?:[\$\bKSh\b]\s?)([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
                if match:
                    clean_price = float(match.group(1).replace(",", ""))
                    return {
                        "title": product_name,
                        "price_raw": f"${clean_price}",
                        "extracted_price": clean_price,
                        "store": store_name or "Web Retailer",
                        "link": search_url,
                        "details": text
                    }
    except Exception as e:
        print(f"⚠️ Scraper Warning: {e}")
    
    return {
        "title": product_name,
        "price_raw": "N/A",
        "extracted_price": 0.0,
        "store": store_name or "Web Retailer",
        "link": ""
    }
