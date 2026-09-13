from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



app = FastAPI(title="API Bibliothèque Chatbot")
STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# Chemin vers le fichier de données
DATA_FILE = Path(__file__).parent.parent / "data" / "livres.json"

# Mots vides à ignorer dans la détection d'auteur
MOTS_VIDES = {"de", "la", "le", "les", "du", "des", "van", "von", "un", "une"}
@app.get("/chat-ui")
def page_chat():
    """Sert la page HTML du chatbot."""
    return FileResponse(STATIC_DIR / "index.html")

# ---------- Modèles Pydantic ----------
class MessageUtilisateur(BaseModel):
    message: str


# ---------- Fonctions utilitaires ----------
def charger_livres():
    """Lit le fichier JSON et renvoie la liste des livres."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- Routes ----------
@app.get("/")
def accueil():
    return {"message": "API Bibliothèque opérationnelle"}


@app.get("/livres")
def lister_livres():
    """Renvoie la liste complète des livres."""
    livres = charger_livres()
    return {"total": len(livres), "livres": livres}


# ⚠️ Routes FIXES d'abord
@app.get("/livres/recherche/auteur/{nom}")
def chercher_par_auteur(nom: str):
    """Cherche tous les livres d'un auteur (insensible à la casse)."""
    livres = charger_livres()
    resultats = [l for l in livres if nom.lower() in l["auteur"].lower()]
    if not resultats:
        raise HTTPException(status_code=404, detail=f"Aucun livre trouvé pour l'auteur : {nom}")
    return {"total": len(resultats), "livres": resultats}


@app.get("/livres/recherche/genre/{genre}")
def chercher_par_genre(genre: str):
    """Cherche tous les livres d'un genre (insensible à la casse)."""
    livres = charger_livres()
    resultats = [l for l in livres if genre.lower() in l["genre"].lower()]
    if not resultats:
        raise HTTPException(status_code=404, detail=f"Aucun livre trouvé pour le genre : {genre}")
    return {"total": len(resultats), "livres": resultats}


@app.get("/livres/recherche/mot-cle/{mot}")
def chercher_par_mot_cle(mot: str):
    """Cherche les livres contenant un mot-clé donné."""
    livres = charger_livres()
    resultats = [
        l for l in livres
        if any(mot.lower() in mc.lower() for mc in l["mots_cles"])
    ]
    if not resultats:
        raise HTTPException(status_code=404, detail=f"Aucun livre trouvé pour le mot-clé : {mot}")
    return {"total": len(resultats), "livres": resultats}


# ⚠️ Route DYNAMIQUE en dernier
@app.get("/livres/{livre_id}")
def obtenir_livre(livre_id: int):
    """Renvoie un livre par son identifiant."""
    livres = charger_livres()
    for livre in livres:
        if livre["id"] == livre_id:
            return livre
    raise HTTPException(status_code=404, detail=f"Aucun livre avec l'id {livre_id}")


# ---------- Chatbot ----------
@app.post("/chat")
def chatbot(msg: MessageUtilisateur):
    """Reçoit un message et renvoie une réponse du chatbot."""
    texte = msg.message.lower().strip()

    # --- 1. Gestion des messages vides ---
    if not texte:
        return {"reponse": "Je n'ai rien reçu. 😅 Pose-moi une question sur nos livres !", "type": "vide"}

    # --- 2. Intentions spéciales (avant recherche) ---
    if any(mot in texte for mot in ["bonjour", "salut", "coucou", "bonsoir", "hello"]):
        return {
            "reponse": "Bonjour ! 👋 Je suis le chatbot de la bibliothèque. Tu peux me demander un livre par auteur, genre ou thème.",
            "type": "salutation"
        }

    if any(mot in texte for mot in ["merci", "au revoir", "bye", "à bientôt"]):
        return {"reponse": "Avec plaisir ! 📚 À bientôt dans la bibliothèque !", "type": "remerciement"}

    if any(mot in texte for mot in ["qui es-tu", "qui es tu", "ton nom", "tu es qui"]):
        return {
            "reponse": "Je suis BiblioBot 🤖, l'assistant virtuel de la bibliothèque. Je peux t'aider à trouver un livre !",
            "type": "presentation"
        }

    if any(mot in texte for mot in ["aide", "help", "que peux-tu", "que peux tu"]):
        return {
            "reponse": "Tu peux me demander :\n- 'Un livre de Victor Hugo'\n- 'Un roman de science-fiction'\n- 'Un livre sur la politique'",
            "type": "aide"
        }

    # --- 3. Recherche dans les livres ---
    livres = charger_livres()
    mots_question = [m for m in texte.split() if len(m) >= 3 and m not in MOTS_VIDES]
    resultats = []
    type_recherche = "général"

    # 3a. Détection auteur (par mots)
    for livre in livres:
        mots_auteur = [m for m in livre["auteur"].lower().split() if len(m) >= 3 and m not in MOTS_VIDES]
        if any(m in mots_question for m in mots_auteur):
            resultats.append(livre)

    # 3b. Si rien trouvé par auteur, on essaie par mot-clé
    if not resultats:
        type_recherche = "mot-clé"
        for livre in livres:
            if any(mot in texte for mot in livre["mots_cles"]):
                resultats.append(livre)

    # 3c. Si toujours rien, on essaie par genre
    if not resultats:
        type_recherche = "genre"
        for livre in livres:
            if livre["genre"].lower() in texte:
                resultats.append(livre)

    # --- 4. Construction de la réponse ---
    if not resultats:
        return {
            "reponse": "Désolé, je n'ai rien trouvé pour ta demande. 😕 Essaie avec un auteur, un genre ou un thème.",
            "type": "aucun_resultat"
        }

    lignes = [
        f"- {l['titre']} ({l['auteur']}) — {'✅ disponible' if l['disponible'] else '❌ emprunté'}"
        for l in resultats[:5]
    ]
    reponse = f"J'ai trouvé {len(resultats)} livre(s) :\n" + "\n".join(lignes)

    if len(resultats) > 5:
        reponse += f"\n... et {len(resultats) - 5} autre(s)."

    return {
        "reponse": reponse,
        "type_recherche": type_recherche,
        "nb_resultats": len(resultats)
    }





