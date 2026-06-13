from groq import Groq
from app.core.config import get_settings
from app.services.embeddings import embed_text
from app.db.client import get_db
import json

settings = get_settings()

def get_groq_client() -> Groq:
    return Groq(api_key=settings.groq_api_key)

def retrieve_relevant_suttas(question: str, top_k: int = 8) -> list[dict]:
    db = get_db()
    question_embedding = embed_text(question)
    result = db.rpc(
        'match_suttas',
        {
            'query_embedding': question_embedding,
            'match_threshold': 0.05,
            'match_count': top_k
        }
    ).execute()
    return result.data or []

def generate_response(question: str, suttas: list[dict]) -> dict:
    if not suttas:
        return {
            "answer": "I was unable to find relevant teachings for your question. Please try rephrasing it.",
            "sources": []
        }

    context = ""
    for sutta in suttas:
        ref = sutta.get('reference', '')
        title = sutta.get('title', 'Unknown')
        collection = sutta.get('collection', '')
        context += f"\n[{ref} · {title} · {collection}]\n"
        context += f"Text: {sutta.get('content', '')}\n"

    system_prompt = """You are a wise guide who answers questions by drawing directly from the Buddha's recorded teachings in the Pali Canon.

Your role:
- Respond with warmth, depth, and calm clarity
- Ground every part of your response in the specific teachings provided
- When citing a teaching, use the actual sutta reference in parentheses — for example: (Dhammapada 1-20), (MN 10 · Majjhima Nikaya), (AN 5.57 · Anguttara Nikaya)
- Do not use generic labels like "Teaching 1" or "Teaching 2" — always use the real sutta name and reference
- Do not invent teachings or paraphrase beyond what the texts support
- Speak in clear, accessible language — not overly academic, not overly mystical
- If the question involves suffering, anxiety, or difficulty, respond with compassion first
- End with one short reflection question for the person to sit with"""

    user_prompt = f"""The person has asked: "{question}"

Here are the most relevant teachings from the Pali Canon:
{context}

Please respond to their question drawing from these specific teachings. 
When referencing a teaching inline, cite it by its actual name and reference code — for example: 
"The Buddha taught that the mind precedes all actions (Dhammapada 1-20, Theravāda Canon)"
Never say "Teaching 1" or "Teaching 2" — use the real sutta title and reference shown above."""

    client = get_groq_client()
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    answer = completion.choices[0].message.content
    sources = [
        {
            "title": s.get("title", ""),
            "reference": s.get("reference", ""),
            "collection": s.get("collection", ""),
            "similarity": round(s.get("similarity", 0), 3)
        }
        for s in suttas
    ]
    return {"answer": answer, "sources": sources}

def expand_question(question: str) -> str:
    """Expand modern conversational questions into richer semantic queries."""
    expansion_map = [
        (["what should i do", "course of action", "figure out", "decide", "choice"],
         "right action decision making path forward discernment wisdom"),
        (["anxious", "anxiety", "worried", "worry", "stress", "overwhelmed"],
         "anxiety worry restless mind suffering mental agitation peace calm"),
        (["angry", "anger", "frustrated", "resentment"],
         "anger aversion hatred ill will resentment mind training"),
        (["sad", "depressed", "grief", "loss", "mourning"],
         "grief sorrow suffering impermanence loss attachment"),
        (["purpose", "meaning", "why am i here", "what is life"],
         "purpose meaning life noble search liberation suffering cessation"),
        (["relationship", "people", "friend", "family", "difficult person"],
         "friendship companionship good company association noble friends"),
        (["past", "regret", "mistake", "guilt"],
         "past dwelling regret impermanence present moment mindfulness"),
        (["future", "uncertain", "fear", "scared"],
         "uncertainty fear future impermanence equanimity peace"),
        (["meditation", "mind", "focus", "concentrate"],
         "meditation mindfulness concentration right effort mind training"),
    ]
    
    expanded = question
    q_lower = question.lower()
    for keywords, expansion in expansion_map:
        if any(kw in q_lower for kw in keywords):
            expanded = f"{question} {expansion}"
            break
    
    return expanded

def ask_sathya(question: str, user_id: str) -> dict:
    expanded = expand_question(question)
    suttas = retrieve_relevant_suttas(expanded)
    response = generate_response(question, suttas)
    db = get_db()
    db.table("questions").insert({
        "user_id": user_id,
        "question": question,
        "answer": response["answer"],
        "sources": json.dumps(response["sources"])
    }).execute()
    return response