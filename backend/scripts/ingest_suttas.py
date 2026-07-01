"""
Sutta ingestion script — run this ONCE to populate your vector database.
Fetches real suttas from the SuttaCentral API (Bhikkhu Sujato translations)
and embeds them using sentence-transformers.

Usage: python scripts/ingest_suttas.py
"""

import sys
import os
import requests
import time
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.client import get_db
from app.services.embeddings import embed_texts
from dotenv import load_dotenv
load_dotenv()

# Curated list of sutta UIDs from SuttaCentral
# These are Bhikkhu Sujato's modern English translations
# Covers the most human-relevant teachings across major collections
SUTTA_UIDS = [
    # Dhammapada — most famous Buddhist text
    "dhp1-20", "dhp21-32", "dhp33-43", "dhp44-59",
    "dhp60-75", "dhp76-89", "dhp90-99", "dhp100-115",
    "dhp116-128", "dhp129-145", "dhp146-156", "dhp157-166",
    "dhp167-178", "dhp179-196", "dhp197-208", "dhp209-220",
    "dhp221-234", "dhp235-255", "dhp256-272", "dhp273-289",
    "dhp290-305", "dhp306-319", "dhp320-333", "dhp334-359",
    "dhp360-382", "dhp383-423",

    # Majjhima Nikaya — middle length discourses
    "mn2", "mn7", "mn8", "mn10", "mn19", "mn20",
    "mn21", "mn22", "mn26", "mn36", "mn44", "mn63",
    "mn72", "mn95", "mn117", "mn118", "mn119", "mn131",
    "mn135", "mn139",

    # Samyutta Nikaya — connected discourses
    "sn1.1", "sn3.1", "sn4.1", "sn12.15", "sn22.59",
    "sn35.28", "sn45.8", "sn46.51", "sn47.10", "sn56.11",

    # Anguttara Nikaya — numerical discourses
    "an3.65", "an3.70", "an4.113", "an5.57", "an5.161",
    "an6.10", "an7.64", "an8.6", "an10.48", "an11.2",

    # Udana and Itivuttaka — inspired sayings
    "ud1.1", "ud1.10", "ud2.1", "ud3.10", "ud4.1",
    "ud5.5", "ud8.1", "ud8.4",
    "iti1", "iti22", "iti27", "iti43", "iti49",

    # Sutta Nipata — some of the oldest teachings
    "snp1.1", "snp1.8", "snp2.1", "snp2.4", "snp3.11",
    "snp4.1", "snp4.14", "snp4.15", "snp5.1",

    # Additional high-value suttas for common life questions
    "an3.65",   # Kalama sutta - on knowing for yourself
    "an5.161",  # Five subjects for frequent reflection  
    "mn21",     # Kakacupama - on anger (the saw simile)
    "mn62",     # Advice to Rahula - on reflection
    "mn86",     # Angulimala - on transformation and redemption
    "sn3.4",    # On aging
    "sn55.7",   # On the factors of stream-entry
    "an8.6",    # On the bases of sympathy
    "an4.197",  # On equanimity
    "dhp1-20",  # Already have this but key
    "an6.55",   # Sona - on effort and balance
    "mn19",     # Two kinds of thought
    "mn20",     # Removal of distracting thoughts
    "an5.49",   # On the five subjects
    "sn1.20",   # On the path
    "ud8.2",    # On nibbana
    "snp1.3",   # The rhinoceros - on solitude
    "snp2.14",  # On right conduct
    "mn7",      # On mental effluents
    "an10.61",  # On the basis of merit

]

def fetch_sutta(uid: str) -> dict | None:
    """Fetch a single sutta from SuttaCentral API."""
    url = f"https://suttacentral.net/api/bilarasuttas/{uid}/sujato"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            print(f"  Skipping {uid} — status {res.status_code}")
            return None
        data = res.json()

        # Extract the translated text segments
        translation_data = data.get("translation_text", {})
        if not translation_data:
            print(f"  Skipping {uid} — no translation found")
            return None

        # Join all text segments into one readable passage
        segments = []
        for key, value in sorted(translation_data.items()):
            if value and isinstance(value, str):
                text = value.strip()
                if text and len(text) > 10:
                    segments.append(text)

        if not segments:
            print(f"  Skipping {uid} — empty content")
            return None

        full_text = " ".join(segments)

        # Truncate if too long (keep first 1500 chars for embedding quality)
        if len(full_text) > 1500:
            full_text = full_text[:1500] + "..."

        # Get metadata
        blurb_data = data.get("suttaplex", {})
        title = blurb_data.get("translated_title") or blurb_data.get("original_title") or uid
        collection = uid.split(".")[0].upper() if "." in uid else uid[:2].upper()

        return {
            "reference": uid.upper(),
            "title": title,
            "collection": collection,
            "content": full_text,
        }

    except Exception as e:
        print(f"  Error fetching {uid}: {e}")
        return None

def ingest():
    db = get_db()

    print(f"Fetching {len(SUTTA_UIDS)} suttas from SuttaCentral...")
    print("This will take a few minutes due to API rate limiting.\n")

    suttas = []
    for i, uid in enumerate(SUTTA_UIDS):
        print(f"[{i+1}/{len(SUTTA_UIDS)}] Fetching {uid}...")
        sutta = fetch_sutta(uid)
        if sutta:
            suttas.append(sutta)
        # Be respectful to SuttaCentral's servers
        time.sleep(0.5)

    print(f"\nFetched {len(suttas)} suttas successfully.")
    print("Generating embeddings (this takes ~1 minute)...")

    texts = [f"{s['title']}. {s['content']}" for s in suttas]
    embeddings = embed_texts(texts)

    print("Storing in Supabase pgvector...")
    success = 0
    for sutta, embedding in zip(suttas, embeddings):
        try:
            db.table("suttas").upsert({
                "reference": sutta["reference"],
                "title": sutta["title"],
                "collection": sutta["collection"],
                "content": sutta["content"],
                "embedding": embedding
            }, on_conflict="reference").execute()
            success += 1
        except Exception as e:
            print(f"  Error storing {sutta['reference']}: {e}")

    print(f"\nDone. {success} suttas ingested into Supabase.")
    print("Your RAG pipeline now has real Pali Canon teachings to search from.")

if __name__ == "__main__":
    ingest()