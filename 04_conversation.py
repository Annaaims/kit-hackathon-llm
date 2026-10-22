"""
04_conversation.py — LE MODÈLE N'A AUCUNE MÉMOIRE

À quoi sert ce fichier ?
    Démonter une illusion. Beaucoup de gens croient que le modèle « apprend »
    d'eux au fil de la discussion. C'est faux : chaque appel à l'API est
    totalement indépendant, et rien n'est conservé entre deux requêtes.

    Quand le modèle semble se souvenir, c'est VOTRE CODE qui lui a relu toute
    la conversation. Le mécanisme tient en trois lignes, visibles ci-dessous.

Essayez cet enchaînement :
    Toi : Qu'est-ce qu'une période d'essai ?
    Toi : Et pour un cadre ?
    La deuxième question n'a aucun sens isolément. Elle ne fonctionne que parce
    que le modèle reçoit aussi la première.

Conséquence pratique à retenir :
    La liste grossit à chaque tour, donc on envoie de plus en plus de tokens,
    et on paie plusieurs fois pour les mêmes phrases. Dans une vraie application,
    on finit par résumer ou couper les anciens messages.

Lancer :  python 04_conversation.py     (puis 'quit' pour sortir)
"""

from config import client, MODEL

# ────────────────────── La mémoire, c'est cette liste ────────────────────

# On démarre l'historique avec le message system, qui restera en tête de liste
# pendant toute la conversation : la consigne s'applique à chaque tour.
historique = [
    {"role": "system", "content": "Tu es un assistant juridique. Réponds en français, en 3 phrases maximum."},
]

print("Posez vos questions sur le droit du travail. 'quit' pour sortir.\n")

# ───────────────────────── La boucle de dialogue ─────────────────────────

# while True = boucle infinie. On en sortira avec le "break" plus bas.
while True:

    # input() met le programme en pause et attend que l'utilisateur tape.
    # .strip() enlève les espaces et le retour à la ligne en trop.
    question = input("Toi : ").strip()

    # Condition de sortie. On teste en minuscules pour accepter "QUIT" aussi.
    # break interrompt la boucle while.
    if question.lower() in {"quit", "exit", "q"}:
        break

    # ÉTAPE 1 — on ajoute la question de l'utilisateur à la liste.
    historique.append({"role": "user", "content": question})

    # ÉTAPE 2 — on envoie TOUTE LA LISTE, pas seulement la dernière question.
    # C'est ici que se joue toute l'illusion de mémoire.
    reponse = client.chat.completions.create(
        model=MODEL,
        messages=historique,     # ← la liste entière, à chaque tour
        max_tokens=300,
    )

    # On extrait le texte, comme dans le script 01.
    texte = reponse.choices[0].message.content

    # ÉTAPE 3 — on ajoute aussi SA réponse à la liste, pour que le tour suivant
    # en dispose. Sans cette ligne, il oublierait ce qu'il vient de dire.
    historique.append({"role": "assistant", "content": texte})

    print(f"\nIA : {texte}")

    # On affiche la taille de la liste pour rendre le phénomène visible :
    # ce nombre augmente de 2 à chaque tour (votre question + sa réponse).
    print(f"     ({len(historique)} messages renvoyés au modèle)\n")

# ─────────────────────────── Après la boucle ─────────────────────────────

print("\n⚠️  Plus la conversation est longue, plus on envoie de tokens à chaque tour.")
print("    Et toujours aucune source : il faut maintenant lui donner le document.")
