from bs4 import BeautifulSoup
import os
import requests
from serpapi import GoogleSearch


def fallback_web_scrape(product_name: str, preferred_store: str = ""):
    """Fallback web scraping when API is unavailable."""
    pass


def fetch_global_product_price(
         product_name:str,country_code:str,preferred_currency:str,preferred_store:str =""
):
    """Queries google shopping API for live product prices in ANY specified country."""
    api_key = os.getenv()

    if not api_key:
        return fallback_web_scrape(product_name, preferred_store)
    query = (
        f"{preferred_store} {product_name}".strip()
        if preferred_store
        else product_name        
    ) 
    params = {
        "engine": "google_shopping",
        "q": query,
        "gl": country_code,
        "api_key": api_key,
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        shopping = results.get("shopping_results", [])
        if shopping:
            top_match = shopping[0]
            return {
                "title": top_match.get("title", product_name),
                "price_raw": top_match.get("price"),
            }
        return None
    except Exception as e:
        print(f"Error fetching store data: {e}")
        return None


def fallback_web_scrape(product_name: str, store_name: str):
    """demonstrate beautifulsoup html parsing for custom product links."""
    try:
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        search_url = f"https://html.duckduckgo.com/html/?q={product_name}+{store_name}+price"
        response = requests.get(search_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("a", class_="result__snippet")
            snippet_text = (
                results[0].text if results else "Price available on product page"
            )
            return {
                "title": product_name,
                "price_raw": "Check Store Link",
                "extracted_price": 0.0,
                "store": store_name or "Web Store",
                "link": search_url,
                "details": snippet_text,
            }
    except Exception as e:
        print(f"❌ BeautifulSoup Scraper Warning: {e}")
    return None
