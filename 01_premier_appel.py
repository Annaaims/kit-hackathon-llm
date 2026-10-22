"""
01_premier_appel.py — L'APPEL LE PLUS SIMPLE POSSIBLE

À quoi sert ce fichier ?
    Montrer la structure minimale d'un appel à un LLM. Si vous comprenez ce
    fichier, vous comprenez 80 % du kit : tous les autres en sont des variantes.

Ce qu'il faut observer en le lançant :
    La réponse est fluide et plausible… mais elle vient de la MÉMOIRE du modèle.
    Aucun document ne lui a été fourni. Rien ne garantit qu'elle corresponde au
    Code du travail gabonais. C'est précisément le problème qu'on résoudra à la fin.

Lancer :  python 01_premier_appel.py
"""

# On importe la connexion et le nom du modèle, tous deux préparés par config.py.
# Rien d'autre n'est nécessaire : config.py a déjà lu la clé et choisi l'adresse.
from config import client, MODEL

# La question, isolée dans une variable pour pouvoir la réutiliser à l'affichage.
QUESTION = "Qu'est-ce qu'une période d'essai dans un contrat de travail ? Réponds en 3 phrases."

# ─────────────────────────── L'appel à l'API ─────────────────────────────

reponse = client.chat.completions.create(
    # Quel modèle doit répondre. Le nom doit être exact, sinon erreur 404.
    model=MODEL,

    # TOUT ce que le modèle reçoit tient dans cette liste. Rien d'autre ne
    # traverse le réseau : ni vos fichiers, ni vos variables Python.
    messages=[
        # Le message "system" : votre consigne de développeur. L'utilisateur
        # final ne la voit jamais. C'est ici qu'on impose la langue, le ton,
        # le rôle — et plus tard, le document à lire.
        {"role": "system", "content": "Tu es un assistant juridique. Réponds en français, simplement."},

        # Le message "user" : la question posée.
        {"role": "user", "content": QUESTION},
    ],

    # temperature règle le hasard dans le choix des mots.
    #   0   → le modèle prend presque toujours le mot le plus probable :
    #         réponses stables et reproductibles (idéal pour extraire des données)
    #   0.8 → il prend des libertés (idéal pour trouver des idées)
    temperature=0.7,

    # max_tokens plafonne la LONGUEUR de la réponse.
    # Attention : c'est un couperet. Si le modèle n'a pas fini, la phrase est
    # coupée net. Ce n'est pas une consigne de concision, c'est une limite.
    max_tokens=300,
)

# ──────────────────────── Lire ce qui est revenu ─────────────────────────

print(f"Modèle utilisé : {MODEL}")
print(f"Question : {QUESTION}\n")

# Le texte de la réponse est TOUJOURS à cet endroit précis :
#   .choices     → une liste, car l'API peut renvoyer plusieurs propositions
#   [0]          → on prend la première
#   .message     → le message produit par le modèle
#   .content     → son texte
# Retenez cette ligne : vous l'écrirez des centaines de fois.
print(reponse.choices[0].message.content)

# reponse.usage contient les compteurs de consommation.
# Le "if" est une précaution : quelques fournisseurs ne les renvoient pas.
if reponse.usage:
    print(f"\nTokens : {reponse.usage.prompt_tokens} en entrée, "       # ce qu'on a envoyé
          f"{reponse.usage.completion_tokens} en sortie")               # ce qu'il a produit

# ─────────────────────── L'avertissement du jour ─────────────────────────

print("\n⚠️  Réponse produite de mémoire, sans aucun document.")
print("    Impossible de savoir d'où elle vient ni si elle vaut pour le Gabon.")
print("    C'est précisément le problème qu'on résoudra à l'étape finale.")
