"""
03_streaming.py — AFFICHER LA RÉPONSE AU FUR ET À MESURE

À quoi sert ce fichier ?
    Montrer l'option stream=True, qui fait arriver la réponse morceau par morceau
    au lieu d'attendre qu'elle soit entièrement rédigée. C'est l'effet
    « machine à écrire » que vous connaissez sur ChatGPT.

ATTENTION, le point le plus mal compris du kit :
    Le streaming ne concerne QUE LA SORTIE. Il ne sert pas à envoyer un fichier,
    et il ne change rien à ce que le modèle reçoit. Le temps total est d'ailleurs
    identique à un appel normal : seule la perception change.

    Et surtout : une réponse FAUSSE s'affiche exactement aussi joliment qu'une
    réponse juste. Le streaming rend une application plus agréable, jamais plus fiable.

Lancer :  python 03_streaming.py
"""

from config import client, MODEL

# ─────────────────────────── L'appel à l'API ─────────────────────────────

# Noter le nom de la variable : ce n'est plus une "reponse" mais un "flux".
# L'objet renvoyé n'est pas un résultat fini, c'est un robinet qu'on va vider.
flux = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "Tu es un assistant juridique. Réponds en français, simplement."},
        {"role": "user", "content": "Quelle est la différence entre une démission et un licenciement ?"},
    ],

    # ★ LA SEULE LIGNE QUI CHANGE par rapport au script 01.
    stream=True,

    max_tokens=400,
)

# ──────────────────── Vider le flux, morceau par morceau ─────────────────

# Une boucle for sur le flux : à chaque tour, on reçoit un petit fragment.
for morceau in flux:

    # Deux précautions dans cette condition :
    #   morceau.choices          → certains fragments techniques arrivent vides
    #   ...delta.content         → et parfois le contenu lui-même est vide
    # Sans ce test, le script planterait sur un fragment vide.
    if morceau.choices and morceau.choices[0].delta.content:

        # ★ Le mot "delta" est essentiel : c'est LE NOUVEAU FRAGMENT UNIQUEMENT,
        #   pas le texte accumulé depuis le début. C'est à votre code de les
        #   coller bout à bout — ici, en les affichant les uns après les autres.
        #
        #   end=""      empêche Python de sauter une ligne après chaque fragment
        #   flush=True  force l'affichage immédiat au lieu d'attendre que le
        #               tampon de sortie se remplisse (sans lui, l'effet disparaît)
        print(morceau.choices[0].delta.content, end="", flush=True)

# Un print() vide pour terminer proprement par un retour à la ligne,
# puisque tous les fragments ont été affichés avec end="".
print()

print("\n⚠️  Toujours aucune source : le modèle parle encore de mémoire.")
