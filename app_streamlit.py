"""
app_streamlit.py — L'APPLICATION FINALE : « Pose tes questions à un document »

À quoi sert ce fichier ?
    Réunir les quatre notions des scripts précédents dans une application
    utilisable : l'appel de base, le streaming, la mémoire de conversation,
    et un document fourni au modèle.

LE POINT LE PLUS MAL COMPRIS — à lire avant tout :
    AUCUN FICHIER N'EST ENVOYÉ À L'API. Voici la chaîne réelle :
        1. st.file_uploader  → l'utilisateur dépose son PDF dans l'application
                               Streamlit, qui tourne sur VOTRE machine
        2. lire_document     → Python ouvre le PDF et en extrait le texte,
                               toujours sur VOTRE machine
        3. consigne += ...   → ce texte est COLLÉ dans une chaîne de caractères
        4. messages=[...]    → cette chaîne part comme message "system"
    L'API ne reçoit donc pas un fichier, mais un très long message texte.
    C'est pour cette raison qu'un PDF scanné échoue : à l'étape 2 il n'y a
    aucun texte à extraire, et le message part vide.

DEUXIÈME PARTICULARITÉ — Streamlit réexécute TOUT le script :
    À chaque clic, à chaque question, ce fichier est relancé de haut en bas.
    Vos variables normales seraient donc perdues. C'est le rôle de
    st.session_state : un dictionnaire qui survit à ces relances.

Lancer :  streamlit run app_streamlit.py
"""

# ──────────────────────────── 1. Les librairies ──────────────────────────

import streamlit as st                   # l'interface web, sans écrire de HTML
from pypdf import PdfReader              # pour extraire le texte d'un PDF
from openai import APIError, RateLimitError, AuthenticationError   # les erreurs à rattraper

from config import client, MODEL, PROVIDER   # notre connexion, préparée par config.py

# Limite de sécurité : environ 5 pages. Deux raisons :
#   - le modèle ne peut lire qu'un nombre limité de tokens d'un coup
#   - le compte gratuit plafonne à environ 8 000 tokens par minute
MAX_CARACTERES = 15_000


# ─────────────────────── 2. L'habillage de la page ───────────────────────

# Titre de l'onglet du navigateur et icône. Doit être appelé en premier.
st.set_page_config(page_title="Chat avec un document", page_icon="📄")

# Le grand titre affiché en haut de la page.
st.title("📄 Discute avec ton document")

# Une ligne grise sous le titre. Afficher le fournisseur et le modèle est très
# utile en démonstration : le public voit ce qui tourne réellement.
st.caption(f"Fournisseur : {PROVIDER} · Modèle : {MODEL}")


# ──────────────────── 3. Lire le fichier, en local ───────────────────────

def lire_document(fichier) -> str:
    """Transforme le fichier déposé en une simple chaîne de caractères."""

    # Cas 1 : c'est un PDF. On teste l'extension, en minuscules pour
    # accepter aussi « RAPPORT.PDF ».
    if fichier.name.lower().endswith(".pdf"):
        lecteur = PdfReader(fichier)

        # On parcourt chaque page et on extrait son texte, puis on colle le
        # tout avec un retour à la ligne entre chaque page.
        # Le « or "" » est important : extract_text() renvoie None sur une page
        # sans texte (une image), et on ne peut pas coller None à du texte.
        return "\n".join(page.extract_text() or "" for page in lecteur.pages)

    # Cas 2 : c'est un .txt ou un .md. On lit les octets et on les décode.
    # errors="ignore" évite un plantage sur un caractère mal encodé.
    return fichier.read().decode("utf-8", errors="ignore")


# ────────────────────── 4. La barre latérale gauche ──────────────────────

# Tout ce qui est écrit dans ce bloc s'affiche dans la colonne de gauche.
with st.sidebar:
    st.header("1. Charge un document")

    # Crée le bouton de dépôt de fichier. type=[...] filtre les extensions.
    # Renvoie None tant que rien n'a été déposé.
    fichier = st.file_uploader("PDF, TXT ou MD", type=["pdf", "txt", "md"])

    # Deux conditions :
    #   fichier                      → quelque chose a bien été déposé
    #   nom_doc != fichier.name      → c'est un NOUVEAU fichier
    # Sans le second test, on relirait le PDF à chaque clic, puisque Streamlit
    # réexécute tout le script en permanence.
    if fichier and st.session_state.get("nom_doc") != fichier.name:
        texte = lire_document(fichier)

        # Garde-fou contre les PDF scannés. .strip() enlève espaces et retours
        # à la ligne : un PDF d'images donne une chaîne vide ou presque.
        if len(texte.strip()) < 50:
            st.error("Ce PDF ne contient pas de texte lisible : c'est sans doute un scan (des images). "
                     "Passe-le d'abord dans un outil d'OCR, ou charge une version texte.")
            # st.stop() interrompt immédiatement l'exécution du script.
            st.stop()

        # On range le texte dans session_state pour qu'il survive aux relances.
        # [:MAX_CARACTERES] coupe le document s'il est trop long.
        st.session_state.doc = texte[:MAX_CARACTERES]

        # On mémorise le nom, pour détecter un changement de fichier au tour suivant.
        st.session_state.nom_doc = fichier.name

        # Nouveau document = nouvelle conversation. On vide l'historique,
        # sinon les questions sur l'ancien document resteraient affichées.
        st.session_state.messages = []

        # On prévient honnêtement l'utilisateur si le document a été tronqué.
        if len(texte) > MAX_CARACTERES:
            st.warning("Document long : seule la première partie est utilisée.")

    # Message vert de confirmation, affiché à chaque relance tant qu'un
    # document est en mémoire.
    if st.session_state.get("doc"):
        st.success(f"✅ {st.session_state.nom_doc} chargé")

    # st.button() renvoie True uniquement lors du clic. On vide l'historique,
    # mais on garde le document chargé.
    if st.button("🗑️ Nouvelle conversation"):
        st.session_state.messages = []


# ────────────────── 5. Réafficher la conversation ────────────────────────

# Au tout premier lancement, la clé "messages" n'existe pas encore.
# On la crée vide pour éviter une erreur juste après.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Comme le script est relancé entièrement à chaque interaction, il faut
# REDESSINER toute la conversation à chaque fois. C'est le rôle de cette boucle.
for msg in st.session_state.messages:
    # st.chat_message() crée une bulle. Le rôle ("user" ou "assistant")
    # détermine l'avatar et l'alignement.
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ──────────────────── 6. La zone de saisie en bas ────────────────────────

# Affiche le champ de saisie. Renvoie None tant que rien n'est envoyé,
# et le texte tapé au moment de l'envoi.
question = st.chat_input("Pose ta question…")

# Tout le bloc suivant ne s'exécute que lorsqu'une question vient d'être posée.
if question:

    # On ajoute la question à l'historique — exactement comme au script 04.
    st.session_state.messages.append({"role": "user", "content": question})

    # Et on l'affiche tout de suite, sans attendre la réponse.
    with st.chat_message("user"):
        st.markdown(question)

    # ─────────── Construire la consigne, avec le document dedans ──────────

    # La consigne de base, utilisée si aucun document n'est chargé.
    consigne = "Tu es un assistant qui répond en français, de façon claire et concise."

    # ★ LE CŒUR DE L'APPLICATION. Si un document est en mémoire, on l'ajoute
    #   à la consigne, encadré par des balises qui aident le modèle à voir où
    #   il commence et où il finit.
    #
    #   Trois exigences y sont formulées, et chacune compte :
    #     1. « UNIQUEMENT sur le document »  → impose la source
    #     2. « Cite systématiquement        → rend la réponse VÉRIFIABLE.
    #         le numéro de l'article »         Sans cette ligne, le modèle
    #                                          répond juste, mais sans dire d'où.
    #     3. « Je ne trouve pas cette       → AUTORISE l'aveu d'ignorance.
    #         information… »                   Phrase imposée mot pour mot :
    #                                          sans elle, le modèle comble le
    #                                          vide en inventant.
    if st.session_state.get("doc"):
        consigne += (
            " Réponds en t'appuyant UNIQUEMENT sur le document ci-dessous. "
            "Cite systématiquement le numéro de l'article sur lequel tu t'appuies. "
            "Si l'information ne figure pas dans le document, réponds exactement : "
            "« Je ne trouve pas cette information dans le document fourni. »\n\n"
            f"--- DOCUMENT ---\n{st.session_state.doc}\n--- FIN ---"
        )

    # ───────────────────── Appeler le modèle ──────────────────────────────

    with st.chat_message("assistant"):
        try:
            flux = client.chat.completions.create(
                model=MODEL,

                # On place la consigne (document compris) en tête, puis tout
                # l'historique. C'est la combinaison du script 04 et du script 05.
                messages=[{"role": "system", "content": consigne}] + st.session_state.messages,

                # Le streaming du script 03, pour l'affichage progressif.
                stream=True,
            )

            # st.write_stream() affiche les fragments au fur et à mesure ET
            # renvoie le texte complet une fois terminé. Il reçoit ici un
            # générateur : la même logique que la boucle for du script 03,
            # écrite en une seule expression.
            reponse = st.write_stream(
                m.choices[0].delta.content      # le fragment à afficher
                for m in flux                   # pour chaque morceau du flux
                if m.choices and m.choices[0].delta.content   # en ignorant les vides
            )

            # On range la réponse complète dans l'historique, pour le tour suivant.
            st.session_state.messages.append({"role": "assistant", "content": reponse})

        # ──────────── Transformer les erreurs en messages clairs ──────────

        # Clé absente, fausse, ou révoquée.
        except AuthenticationError:
            st.error("Clé API invalide. Vérifie ton fichier .env.")

        # Trop de requêtes, ou trop de tokens dans la minute.
        except RateLimitError:
            st.error("Limite gratuite atteinte. Attends une minute et réessaie.")

        # Toutes les autres erreurs de l'API. À placer en DERNIER : les blocs
        # except sont testés dans l'ordre, et celui-ci est le plus général.
        except APIError as e:
            st.error(f"Erreur de l'API : {e}")
