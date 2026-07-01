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
            'match_threshold': 0.01,
            'match_count': top_k
        }
    ).execute()
    
    if not result.data:
        fallback = db.table("suttas").select("reference, title, collection, content").limit(top_k).execute()
        return fallback.data or []
    
    return result.data

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

    system_prompt = """You are a wise guide who answers questions by drawing from the Buddha's recorded teachings in the Pali Canon.

Your role:
- Respond with warmth, depth, and calm clarity
- Draw from the teachings provided, even if they are only loosely related to the question
- If the teachings are not directly about the question, find the wisdom within them that speaks to the human experience being described
- Cite which teaching you are drawing from using its actual reference (e.g. MN 10, AN 5.57)
- Speak in clear, accessible language
- If the question involves suffering, anxiety, or difficulty, respond with compassion first
- End with one short reflection question for the person to sit with
- Never say you cannot help — always find a way to offer wisdom from the teachings provided"""

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
    q = question.lower()
    
    expansions = [
        # Anger / resentment
        (["angry", "anger", "furious", "rage", "resentment", "irritated", "frustrated", "annoyed", "hatred", "hate"],
         "anger aversion hatred ill will resentment mind training patience forbearance"),
        
        # Anxiety / worry / stress
        (["anxious", "anxiety", "worried", "worry", "stress", "stressed", "overwhelmed", "panic", "nervous", "fear", "afraid", "scared"],
         "anxiety worry restless mind suffering mental agitation peace calm equanimity fear"),
        
        # Sadness / depression / grief
        (["sad", "sadness", "depressed", "depression", "grief", "loss", "mourning", "crying", "hopeless", "despair"],
         "grief sorrow suffering impermanence loss attachment lamentation"),
        
        # Purpose / meaning
        (["purpose", "meaning", "why am i here", "what is life", "pointless", "meaningless", "direction", "lost"],
         "purpose meaning life noble search liberation suffering cessation right livelihood"),
        
        # Relationships / people
        (["relationship", "people", "friend", "friendship", "family", "difficult person", "conflict", "partner", "love", "lonely", "loneliness", "alone"],
         "friendship companionship good company association noble friends love compassion metta"),
        
        # Past / regret / guilt
        (["past", "regret", "mistake", "guilt", "shame", "embarrassed", "forgive", "forgiveness"],
         "past dwelling regret impermanence present moment mindfulness letting go"),
        
        # Future / uncertainty
        (["future", "uncertain", "uncertainty", "change", "unknown", "worry about", "what will happen"],
         "uncertainty impermanence equanimity peace present moment future planning"),
        
        # Meditation / mind / focus
        (["meditat", "mind", "focus", "concentrate", "distracted", "thoughts", "thinking", "mental", "attention"],
         "meditation mindfulness concentration right effort mind training breathing"),
        
        # Desire / attachment / craving
        (["want", "desire", "craving", "attachment", "letting go", "cant stop wanting", "obsessed", "addicted"],
         "desire craving attachment clinging letting go non-attachment liberation"),
        
        # Suffering / pain / hardship
        (["suffer", "suffering", "pain", "hardship", "difficult", "hard time", "struggle", "burden"],
         "suffering dukkha noble truth cessation path hardship endurance"),
        
        # Happiness / peace / contentment
        (["happy", "happiness", "peace", "peaceful", "content", "contentment", "joy", "wellbeing"],
         "happiness peace contentment joy wellbeing liberation nibbana"),
        
        # Death / impermanence
        (["death", "dying", "dead", "mortality", "impermanent", "impermanence", "nothing lasts"],
         "death impermanence mortality aging suffering cessation"),
        
        # Work / ambition / success
        (["work", "job", "career", "success", "failure", "ambition", "achieve", "money", "wealth"],
         "right livelihood work effort ambition wealth generosity duty"),
        
        # Ego / self / identity
        (["ego", "self", "identity", "who am i", "sense of self", "pride", "arrogant"],
         "self non-self ego identity aggregates emptiness pride conceit"),
        
        # Compassion / kindness
        (["compassion", "kind", "kindness", "help others", "generosity", "giving", "empathy"],
         "compassion kindness metta loving-kindness generosity giving dana"),
        
        # Spiritual practice / path
        (["spiritual", "practice", "path", "enlightenment", "awakening", "buddha", "dhamma", "dharma"],
         "spiritual path practice noble eightfold path awakening enlightenment dhamma"),
        
        # Decision making / what to do
        (["what should i do", "decision", "decide", "choice", "confused", "dont know", "figure out", "course of action"],
         "right action decision making path forward discernment wisdom skillful means"),
        
        # Sleep / rest / exhaustion
        (["sleep", "tired", "exhausted", "insomnia", "cant sleep", "rest"],
         "rest sleep heedfulness mind agitation calm peace body"),
        
        # Envy / jealousy / comparison
        (["jealous", "jealousy", "envy", "envious", "compare", "comparison", "better than", "worse than"],
         "envy jealousy comparison conceit equanimity contentment"),
        
        # Forgiveness
        (["forgive", "forgiveness", "let go", "move on", "holding grudge"],
         "forgiveness letting go ill will resentment compassion metta loving kindness"),
    ]
    
    for keywords, expansion in expansions:
        if any(kw in q for kw in keywords):
            return f"{question} {expansion}"
    
    # If no specific match, append general Buddhist terms to improve retrieval
    return f"{question} mind suffering peace wisdom teachings Buddha dhamma"

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