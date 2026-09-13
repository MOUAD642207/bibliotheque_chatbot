# 📚 BiblioBot - Chatbot Bibliothèque

## Description générale

BiblioBot est un chatbot permettant d'interroger une bibliothèque de 100 livres. L'utilisateur peut rechercher un ouvrage par **auteur**, **genre** ou **mot-clé**, et obtenir en réponse la liste des livres correspondants avec leur disponibilité.

Le projet expose une **API REST** et propose une **interface web de chat** pour tester le chatbot directement dans le navigateur.

Fonctionnalités principales :
- Recherche de livres par auteur, genre ou mot-clé
- Gestion des salutations, remerciements et demandes d'aide
- API documentée automatiquement (Swagger)
- Interface web de chat responsive

## Stack technique utilisée

- **Python 3.10+**
- **FastAPI** — framework API
- **Uvicorn** — serveur ASGI
- **Pydantic** — validation des données
- **JSON** — stockage des données des livres
- **HTML / CSS / JavaScript** — interface utilisateur
- **Git / GitHub** — versioning







## Comment lancer et tester

### 1. Cloner le dépôt

bash
git clone https://github.com/MOUAD642207/bibliotheque_chatbot.git
cd bibliotheque_chatbot

###2. Créer et activer un environnement virtuel
Windows :
python -m venv venv
venv\Scripts\activate
macOS / Linux :
python3 -m venv venv
source venv/bin/activate

###3. Installer les dépendances

pip install -r requirements.txt
###4. Lancer le serveur
uvicorn app.main:app --reload

###5. Tester le chatbot
Interface web de chat : http://127.0.0.1:8000/chat-ui

Documentation API (Swagger) : http://127.0.0.1:8000/docs

Exemples de questions à poser :

Un livre de Victor Hugo

Un roman de science-fiction

Un livre sur la politique

Aide






