"""
02_lister_modeles.py — QUELS MODÈLES SONT DISPONIBLES ?

À quoi sert ce fichier ?
    Demander au fournisseur la liste des modèles auxquels votre clé donne droit,
    et relever leur nom EXACT. Un nom de modèle qui change, et toute votre
    application tombe avec une erreur 404.

Ce qu'il a de particulier :
    C'est le seul script qui n'appelle pas chat.completions. Il utilise un autre
    point d'entrée de l'API. Conséquence agréable : aucun modèle ne travaille,
    donc AUCUN TOKEN N'EST CONSOMMÉ. Vous pouvez le relancer autant que vous voulez.

Lancer :  python 02_lister_modeles.py
"""

# Ici on n'a besoin que de la connexion : aucun modèle n'est sollicité,
# donc la variable MODEL ne sert à rien dans ce fichier.
from config import client

# ─────────────────────────── L'appel à l'API ─────────────────────────────

# Un point d'entrée différent de chat.completions. Il répond en substance :
# « voici le catalogue auquel ta clé donne accès ».
modeles = client.models.list()

# modeles.data est une liste d'objets. Chaque objet a un attribut .id qui
# contient le nom exact du modèle (par exemple "openai/gpt-oss-20b").
# On extrait ces noms et on les trie par ordre alphabétique pour y voir clair.
noms = sorted(m.id for m in modeles.data)

# ──────────────────────────── L'affichage ────────────────────────────────

# len(noms) donne le nombre de modèles trouvés.
print(f"{len(noms)} modèles disponibles :\n")

# On parcourt la liste et on affiche un nom par ligne, précédé d'un tiret.
for nom in noms:
    print(" -", nom)

# Rappel pratique : le nom du modèle se change dans le .env, pas dans le code.
print("\n👉 Pour changer de modèle : ajoute MODEL=<nom> dans ton .env")
print("   Le code, lui, ne bouge pas d'une ligne.")
