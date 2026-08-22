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
    
import os
import re
import smtplib
import logging
import traceback

from typing import Optional
from email.mime.text import MIMEText

logging.basicConfig(level=logging.INFO)

"machariaian044@gmail.com" = os.getenv("machariaian044@gmail.com")
"mdpg htvf roli jnkp" = os.getenv("mdpg htvf roli jnkp")

EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

OFF_TOPIC_KEYWORDS = {
    "weather",
    "temperature",
    "recipe",
    "cook",
    "joke",
    "funny",
    "math",
    "capital",
    "history",
    "science",
    "python",
    "programming",
    "code",
    "developer",
    "who is"
}

GUARDRAIL_REDIRECT = (
    "I'm sorry, but I can't help you with that, "
    "but let's get back to saving some money!"
)

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.match(email))

def enforce_guardrail_check(
    user_prompt: str
) -> Optional[str]:
    prompt = user_prompt.strip().lower()

    if any(word in prompt for word in OFF_TOPIC_KEYWORDS):
        return GUARDRAIL_REDIRECT

    return None

def send_price_alert_email(
    recipient_email: str,
    product_name: str,
    live_price: float,
    target_price: float
) -> bool:

    if not is_valid_email(recipient_email):
        return False

    if live_price < 0 or target_price < 0:
        raise ValueError("Prices cannot be negative")

    if live_price > target_price:
        return False

    if not 'machariaian@gmail.com' or not 'mdpg htvf roli jnkp':
        return False

    try:
        product_name = (
            product_name.replace("\n", " ")
            .replace("\r", " ")
        )

        body = (
            f"Great news!\n\n"
            f"{product_name} dropped to "
            f"${live_price:.2f}\n\n"
            f"Target Price: ${target_price:.2f}"
        )

        msg = MIMEText(body)
        msg["From"] = 'machariaian@gmail.com'
        msg["To"] = recipient_email
        msg["Subject"] = (
            f"Price Drop Alert: {product_name}"
        )

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465,
            timeout=30
        ) as server:
            server.login(
                'machariaian@gmail.com',
                'mdpg htvf roli jnkp'
            )
            server.send_message(msg)

        logging.info(
            "Price alert sent successfully."
        )
        return True

    except Exception:
        traceback.print_exc()
        return False 

import os
from dotenv import load_dotenv,dotenv_values

from member1_config import resolve_country_code
from member2_store import fetch_global_product_price
from member3_rag import analyze_deal_with_rag,email_alert
from member4_guardrail import enforce_guadrail_check,guardrail_check_test
from send_price_alert_email import send_price_alert_email

STORAGE_FILE = "tracked_products.json"

def load_tracked_items():
     if os.path.exists(STORAGE_FILE,"w") as f:
        json.dump(data, f, indents=4)

def main():
    items = load_tracked_items()

     while True:
           print("======================")
           print("   OMNISENTINEL ")
           print("GLOBAL PRICE TRACKER (5-PARTS)"
           print("======================")
           print("1. Track New Product")
           print("2. View Saved Products")
           print("3. Test Guardrail Interceptor")
           print("4.Exit")

          choice = input("Select Option (1-4);).strip()

          if == choice"1":
                user_input = input("Enter Product Nema or Link; ")

               guardrai_res = enforce_guardrail_check(user_input)
               if not guardrail_res:
                   print("\no Guardrail Intercept:")
                   print(guardrail_res)
                   continue
       
               country = input("Enter Country(e.g. Kenya,USA): ").strip()
               country_code = resolve_country_code(country)
         
                store = input("Enter Store Optional:").strip()
                
                try:
                   price_goal = float(input("Enter Target Price: "))
                except ValueError:
                   print("no Invalid price number!")
                   continue

                email = input("Alert Email (Optional): ").strip()
                
                print("\n  Fetching price data...")
                price_data = fetch_global_product_price(user_input,country_code,store)             
           
                if price_data:
                   live_price = price_data["extracted_price"]
                   ai_advice = analyze_deal_with_rag(price_data, target_price)

                   print(f"\n Result from {price_data['store']}: ${live_price}")
                   print(f"\n AI Recomendation: {ai_advice}")

                   if email and live_price <= target_price:
                       send_price_alert_email(email, price-data["title"], live_price, target_price)


