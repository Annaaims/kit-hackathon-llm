"""
demo.py — LA DÉMONSTRATION EN 5 MINUTES

Un seul fichier, qui raconte toute l'histoire du kit :
    Partie 1 — on pose une question SANS document  →  réponse plausible, sans source
    Partie 2 — on pose la MÊME question AVEC le document  →  réponse qui cite l'article

Le script s'arrête entre les deux parties : appuyez sur Entrée pour continuer.

    python demo.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# ══════════════════ 1. LA CONNEXION — c'est tout le secret ══════════════════

load_dotenv()                                   # lit la clé dans le fichier .env

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),          # votre clé, jamais dans le code
    base_url="https://api.groq.com/openai/v1",  # ★ la librairie d'OpenAI, mais chez Groq
)
MODEL = "openai/gpt-oss-20b"                    # un modèle open-weight

QUESTION = "Combien de temps peut durer une période d'essai ?"


def demander(messages):
    """Un appel à l'API, et on récupère le texte."""
    reponse = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,        # on veut un résultat stable pendant la démo
        max_tokens=350,
    )
    return reponse.choices[0].message.content


# ════════════════ 2. SANS DOCUMENT — le modèle parle de mémoire ═════════════

print("\n" + "═" * 70)
print("  PARTIE 1 — la même question, SANS document")
print("═" * 70 + "\n")

print(demander([
    {"role": "system", "content": "Tu es un assistant juridique. Réponds en 4 phrases maximum."},
    {"role": "user",   "content": QUESTION},
]))

print("\n⚠  Réponse produite de mémoire. Aucun document, aucune source.")
print("   Le modèle n'a jamais vu le Code du travail gabonais.\n")

input("   [Entrée pour la partie 2] ")


# ═══════════ 3. AVEC LE DOCUMENT — la réponse devient vérifiable ════════════

# Le document. Ici deux articles collés en clair ; dans l'application, ce sera
# le texte d'un PDF déposé par l'utilisateur. Le principe est identique.
DOCUMENT = """
Article 49 : La durée de la période d'essai, renouvellement compris, ne peut
dépasser six mois pour les cadres, trois mois pour les techniciens et agents
de maîtrise, et un mois pour les employés et autres travailleurs.

Article 179 : Le salaire minimum interprofessionnel garanti (SMIG) est fixé
par décret, après avis de la Commission nationale d'étude des salaires.
"""

# Les trois règles qui font toute la fiabilité de l'application.
CONSIGNE = (
    "Tu réponds UNIQUEMENT à partir du document ci-dessous.\n"
    "Tu cites systématiquement le numéro de l'article utilisé.\n"
    "Si l'information ne figure pas dans le document, tu réponds exactement : "
    "« Je ne trouve pas cette information dans le document fourni. »\n\n"
    "DOCUMENT :\n" + DOCUMENT
)

print("\n" + "═" * 70)
print("  PARTIE 2 — la même question, AVEC le document")
print("═" * 70 + "\n")

print(demander([
    {"role": "system", "content": CONSIGNE},   # ★ le document voyage ici
    {"role": "user",   "content": QUESTION},   # ★ la question, inchangée
]))

print("\n✅ Même modèle, même question. Il cite maintenant son article.\n")

input("   [Entrée pour la question piège] ")


# ═══════════════ 4. LA QUESTION PIÈGE — savoir dire « je ne sais pas » ══════

PIEGE = "Quel est le montant du SMIG ?"

print("\n" + "═" * 70)
print("  LA QUESTION PIÈGE — " + PIEGE)
print("═" * 70 + "\n")

print(demander([
    {"role": "system", "content": CONSIGNE},
    {"role": "user",   "content": PIEGE},
]))

print("\n✅ L'article 179 parle du SMIG, mais ne donne aucun montant.")
print("   Un chiffre ici serait une hallucination. « Je ne sais pas » est la bonne réponse.\n")
