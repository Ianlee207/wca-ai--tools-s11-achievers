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

import json
import os


def retrieve_rag_knowledge(product_name: str) -> str:
    """Retrieves buying advice context from knowledge_base.json"""
    kb_file = "knowledge_base.json"
    if not os.path.exists(kb_file):
        return "General Strategy: Cross-check prices across multiple global retailers."

    try:
        with open(kb_file, "r", encoding="utf-8") as f:
            kb_data = json.load(f)
    except Exception:
        return "General Strategy: Cross-check prices across multiple global retailers."

    name_lower = (product_name or "").lower()
    for entry in kb_data:
        keywords = entry.get("keywords", [])
        if any(kw.lower() in name_lower for kw in keywords):
            return f"Category: {entry.get('category','N/A')}. Tip: {entry.get('tip','') }"

    return "General Strategy: Cross-check prices across multiple global retailers."


def analyze_deal_with_rag(product_data: dict, target_price: float) -> str:
    """Evaluates product deal using RAG context and Gemini 2.5 Flash."""
    client = None
    try:
        client = get_gemini_client()
    except Exception:
        client = None

    title = product_data.get("title", "Product")
    rag_tip = retrieve_rag_knowledge(title)
    live_price = float(product_data.get("extracted_price", 0.0) or 0.0)

    prompt = (
        f"Evaluate this deal:\n"
        f"- Product: {title}\n"
        f"- Store: {product_data.get('store')}\n"
        f"- Live Price: ${live_price}\n"
        f"- Target Price: ${target_price}\n"
        f"- RAG Tip: {rag_tip}\n"
        f"Give brief advice: [BUY NOW/WAIT] and a 1-sentence reason."
    )

    if client is not None:
        try:
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return getattr(response, "text", str(response)).strip()
        except Exception:
            pass

    # Fallback deterministic decision if client unavailable or generation failed
    return (f"Target Met (${live_price})" if live_price <= target_price else "Target Not Met")

