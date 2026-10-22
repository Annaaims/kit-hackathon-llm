"""
05_json_structure.py — DU TEXTE JURIDIQUE VERS DES DONNÉES

À quoi sert ce fichier ?
    C'est LE TOURNANT du TP, pour deux raisons.

    1. Pour la première fois, on donne au modèle quelque chose À LIRE : un
       article du Code du travail, écrit juste en dessous. Il ne répond plus
       de mémoire. Vous pouvez relire l'article et vérifier chaque champ.

    2. Au lieu d'une réponse en texte libre, on exige un JSON. Une phrase bien
       tournée peut masquer une approximation ; un champ chiffré, non. Soit il
       correspond au texte, soit il n'y correspond pas.

Pourquoi c'est le script le plus rentable en hackathon :
    Il transforme du texte libre en lignes de base de données. Appliqué à un
    corpus entier, il vous donne un tableau de bord en quelques minutes.

Lancer :  python 05_json_structure.py
"""

# json fait partie de Python, rien à installer.
# Il sert à transformer la chaîne de caractères renvoyée par le modèle
# en véritable dictionnaire Python, utilisable par le reste du programme.
import json

from config import client, MODEL

# ────────────────── Le document fourni au modèle ─────────────────────────

# Extrait réel du Code du travail gabonais, utilisé pour la démonstration.
# C'est ce texte que le modèle va lire — et rien d'autre.
ARTICLE = """
Article 49 : La durée de la période d'essai, renouvellement compris, ne peut
dépasser six mois pour les cadres, trois mois pour les techniciens et agents
de maîtrise, et un mois pour les employés et autres travailleurs.
"""

# ─────────────────────────── L'appel à l'API ─────────────────────────────

reponse = client.chat.completions.create(
    model=MODEL,
    messages=[
        # La consigne énumère les clés attendues, le plus précisément possible.
        # Règle d'or : plus la consigne est explicite, plus le JSON est fiable.
        {"role": "system", "content": (
            "Tu analyses un article de loi. Réponds UNIQUEMENT en JSON, avec les clés : "
            "numero_article, sujet, "
            "durees (un objet avec une clé par catégorie de travailleur et la durée en mois), "
            "renouvellement_inclus (true ou false)."
        )},

        # Le message "user" ne contient pas une question, mais LE DOCUMENT.
        # C'est une façon tout à fait normale d'utiliser ce rôle.
        {"role": "user", "content": ARTICLE},
    ],

    # ★ Force le modèle à produire du JSON syntaxiquement valide.
    #   Sans cette option, il a tendance à l'enrober de politesses du type
    #   « Voici le JSON demandé : », ce qui fait échouer la lecture ensuite.
    response_format={"type": "json_object"},

    # ★ Température à 0 : on veut un résultat fiable et reproductible.
    #   C'est le cas d'usage typique de la température zéro. Lancez le script
    #   deux fois : vous devez obtenir exactement le même JSON.
    temperature=0,
)

# ──────────────────── Transformer le texte en données ────────────────────

# Attention : à ce stade, "brut" est encore une simple chaîne de caractères.
# Elle RESSEMBLE à du JSON, mais Python ne sait pas encore la manipuler.
brut = reponse.choices[0].message.content

# try / except est indispensable ici : même avec response_format, un modèle
# peut échouer. On préfère un message clair à un plantage en pleine démo.
try:
    # json.loads() = « load string » : transforme la chaîne en dictionnaire
    # Python. À partir d'ici, donnees["durees"] fonctionne.
    donnees = json.loads(brut)

    # json.dumps() fait l'inverse, pour l'affichage.
    #   indent=2          → mise en forme lisible, avec retraits
    #   ensure_ascii=False → garde les accents au lieu de les transformer en é
    print(json.dumps(donnees, indent=2, ensure_ascii=False))

    print("\n✅ Du texte juridique transformé en données exploitables.")
    print("   Imaginez cela sur les 88 pages du Code : vous obtenez une base de données.")

# Ce bloc ne s'exécute QUE si json.loads() a échoué.
except json.JSONDecodeError:
    # On affiche la réponse brute, pour comprendre ce que le modèle a renvoyé.
    print("⚠️ Le modèle n'a pas renvoyé un JSON valide :\n", brut)
