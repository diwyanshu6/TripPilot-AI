from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

try:
    if TAVILY_API_KEY:
        client = TavilyClient(api_key=TAVILY_API_KEY)
    else:
        client = None
except Exception:
    client = None


def tavily_search(query: str, max_results: int = 5):
    if not client:
        return get_mock_search_results(query)

    try:
        response = client.search(
            query=query,
            max_results=max_results
        )
        results = []
        for r in response.get("results", []):
            results.append({
                "title": r.get("title", "Unknown"),
                "url": r.get("url", ""),
                "snippet": r.get("content", "").strip()
            })
        return results
    except Exception as e:
        return get_mock_search_results(query)


def get_mock_search_results(query: str):
    q = query.lower()
    if "hotel" in q:
        return [
            {
                "title": "Grand Hyatt Goa",
                "url": "https://www.hyatt.com/grand-hyatt/goa",
                "snippet": "Luxurious 5-star hotel in Bambolim, Goa. Offers stunning views, multiple dining options, a world-class spa, and outdoor pools close to tourist hubs."
            },
            {
                "title": "Taj Exotica Resort & Spa, Goa",
                "url": "https://www.tajhotels.com/taj-exotica-goa",
                "snippet": "Mediterranean-style resort in Benaulim, South Goa. Features private beach access, golf course, spa facilities, and premium fine dining options."
            },
            {
                "title": "Novotel Goa Resort & Spa",
                "url": "https://www.accor.com/novotel-goa",
                "snippet": "Family-friendly resort located in Candolim, North Goa. Close to popular beaches, nightlife, and features a pool, gym, and kid play areas."
            }
        ]
    elif "attractions" in q or "tourist" in q or "places to visit" in q or "sightseeing" in q:
        return [
            {
                "title": "Baga Beach and Calangute Beach",
                "url": "https://goatourism.gov.in/baga",
                "snippet": "Famous sandy beaches in North Goa known for water sports like parasailing, jet skiing, banana boat rides, and lively beach shacks with nightlife."
            },
            {
                "title": "Basilica of Bom Jesus",
                "url": "https://goatourism.gov.in/bom-jesus",
                "snippet": "A UNESCO World Heritage site in Old Goa holding the mortal remains of St. Francis Xavier. Standard example of baroque architecture in India."
            },
            {
                "title": "Dudhsagar Falls",
                "url": "https://goatourism.gov.in/dudhsagar",
                "snippet": "Four-tiered waterfall on the Mandovi River, surrounded by lush deciduous forests. A highly popular day trek destination from Goa."
            }
        ]
    else:
        return [
            {
                "title": f"Travel details for {query}",
                "url": "https://example.com/travel",
                "snippet": f"Here are search results with dynamic information regarding {query}. Ideal guide for sightseeing, packing lists, and regional guidelines."
            }
        ]
