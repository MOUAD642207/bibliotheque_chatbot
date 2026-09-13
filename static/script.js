// ---------- Configuration ----------
const API_URL = "/chat";

// ---------- Récupération des éléments ----------
const chatForm = document.getElementById("chatForm");
const userInput = document.getElementById("userInput");
const chatMessages = document.getElementById("chatMessages");
const sendBtn = document.getElementById("sendBtn");
const suggestions = document.getElementById("suggestions");

// ---------- Fonctions ----------

/**
 * Ajoute un message dans la zone de chat.
 * @param {string} texte - Le contenu du message
 * @param {string} type - "user" | "bot" | "error"
 */
function ajouterMessage(texte, type = "bot") {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", `${type}-message`);

  const content = document.createElement("div");
  content.classList.add("message-content");
  content.innerHTML = texte;

  messageDiv.appendChild(content);
  chatMessages.appendChild(messageDiv);

  // Scroll automatique en bas
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

/**
 * Affiche l'indicateur "en train d'écrire..."
 * @returns {HTMLElement} L'élément à retirer après
 */
function afficherTyping() {
  const typingDiv = document.createElement("div");
  typingDiv.classList.add("message", "bot-message", "typing");
  typingDiv.id = "typingIndicator";
  typingDiv.innerHTML = `
        <div class="message-content">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot"></span>
        </div>
    `;
  chatMessages.appendChild(typingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return typingDiv;
}

/**
 * Retire l'indicateur de frappe.
 */
function retirerTyping() {
  const el = document.getElementById("typingIndicator");
  if (el) el.remove();
}

/**
 * Envoie un message à l'API et affiche la réponse.
 * @param {string} message - Le message de l'utilisateur
 */
async function envoyerMessage(message) {
  // Afficher le message utilisateur
  ajouterMessage(escapeHtml(message), "user");

  // Désactiver l'input pendant la requête
  userInput.disabled = true;
  sendBtn.disabled = true;
  afficherTyping();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message }),
    });

    retirerTyping();

    if (!response.ok) {
      throw new Error(`Erreur serveur (${response.status})`);
    }

    const data = await response.json();
    // On remplace les \n par <br> pour un rendu correct
    const reponseHtml = escapeHtml(data.reponse).replace(/\n/g, "<br>");
    ajouterMessage(reponseHtml, "bot");
  } catch (err) {
    retirerTyping();
    ajouterMessage(
      "❌ Désolé, une erreur est survenue. Vérifie que le serveur est bien lancé.",
      "error",
    );
    console.error(err);
  } finally {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
  }
}

/**
 * Empêche l'injection HTML basique.
 */
function escapeHtml(texte) {
  const div = document.createElement("div");
  div.textContent = texte;
  return div.innerHTML;
}

// ---------- Événements ----------

// Soumission du formulaire
chatForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  userInput.value = "";
  envoyerMessage(message);
});

// Boutons de suggestion
suggestions.addEventListener("click", (e) => {
  if (e.target.classList.contains("suggestion-btn")) {
    const message = e.target.dataset.message;
    envoyerMessage(message);
  }
});

// Focus au chargement
window.addEventListener("load", () => {
  userInput.focus();
});
