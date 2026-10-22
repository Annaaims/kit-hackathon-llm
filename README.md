# 🚀 Kit Hackathon — Utiliser un LLM open-weight via API

Ce kit te permet d'intégrer un modèle d'IA open-weight (GPT-OSS, Qwen…) dans ton projet
**en quelques minutes, sans GPU et gratuitement**.

## Ce qu'il faut comprendre

- Le modèle ne tourne **pas** sur ton PC : il tourne sur les serveurs d'un **fournisseur d'API**, et tu l'appelles par Internet.
- Par défaut, on utilise **Groq** : gratuit, sans carte bancaire, très rapide.
- L'API est **compatible OpenAI** : on utilise la librairie `openai` en changeant juste l'adresse.
- Changer de modèle ou de fournisseur = changer **une ligne** dans le fichier `.env`.

## Installation (10 min)

**Prérequis :** Python 3.9 ou plus.

1. **Récupère ta clé** : crée un compte sur [console.groq.com](https://console.groq.com), puis menu ☰ → **API Keys** → **Create API Key**. Copie-la tout de suite.

2. **Installe les dépendances** :
   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows : .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure ta clé** :
   ```bash
   cp .env.example .env             # Windows : copy .env.example .env
   ```
   Ouvre `.env` et colle ta clé à la place de `colle_ta_cle_ici` sur la ligne `GROQ_API_KEY`.

   > ⚠️ Ne publie **jamais** ton `.env` sur GitHub. Il est déjà dans `.gitignore`.

4. **Teste** :
   ```bash
   python 01_premier_appel.py
   ```

## Les exemples

| Fichier | Ce que tu apprends |
|---|---|
| `demo.py` | **Commence ici.** La démo en 2 min : la même question, avec et sans document |
| `01_premier_appel.py` | Envoyer une question, lire la réponse, voir les tokens consommés |
| `02_lister_modeles.py` | Voir tous les modèles accessibles avec ta clé |
| `03_streaming.py` | Afficher la réponse mot par mot (effet chatbot) |
| `04_conversation.py` | Garder l'historique pour une vraie discussion |
| `05_json_structure.py` | Transformer du texte libre en données JSON exploitables |
| `app_streamlit.py` | **Mini-app complète** : discuter avec un PDF |

Lancer l'app démo :
```bash
streamlit run app_streamlit.py
```

## Choisir un modèle

Ajoute une ligne `MODEL=...` dans `.env`. Sur Groq, les modèles de discussion sont notamment :

| Modèle | Quand l'utiliser |
|---|---|
| `openai/gpt-oss-20b` | Par défaut : rapide, bon pour la plupart des usages |
| `openai/gpt-oss-120b` | Plus puissant, pour le raisonnement ou les longs documents |
| `llama-3.3-70b-versatile` | Alternative solide, bonne en français |
| `llama-3.1-8b-instant` | Le plus rapide, pour du tri ou de la classification en volume |

Ces quatre-là sont des modèles **de production**. Groq propose aussi des modèles en
*preview* (dont `qwen/qwen3.8-27b`) : utilisables pour tester, mais ils peuvent
disparaître sans préavis — ne construis pas ton projet dessus.

La liste exacte évolue : lance `python 02_lister_modeles.py` pour voir celle de ta clé.
Bonus : `whisper-large-v3` transcrit l'audio en texte (idée de projet : assistant vocal).

## Changer d'hébergeur

Groq n'est pas un modèle, c'est un **hébergeur** : il fait tourner des modèles open-weight sur ses serveurs. Son API est **compatible OpenAI**, et c'est devenu le standard du secteur.

Conséquence : pour passer chez un autre hébergeur compatible, tu ajoutes **une ligne** dans `.env` —

```
BASE_URL=https://api.autre-hebergeur.com/v1
```

— et tu remplaces ta clé. **Aucune ligne de code ne change.** C'est précisément ce qui t'évite de dépendre d'une seule entreprise.

## Idées de projets

- Assistant qui répond aux questions sur un **règlement, une loi ou un cours**
- Analyse automatique d'**avis clients** ou de messages (JSON → tableau de bord)
- Chatbot d'**orientation** pour une administration ou une école
- Résumé et traduction de documents
- Générateur de quiz à partir d'un cours
- Assistant vocal (Whisper pour l'audio + LLM pour la réponse)

## Bonnes pratiques

- **Respecte les limites gratuites** : évite les boucles qui appellent l'API sans arrêt. Une erreur 429 = trop de requêtes, attends une minute.
- **`temperature`** : proche de `0` pour des réponses factuelles ou du JSON, vers `0.8` pour de la créativité.
- **`max_tokens`** : limite la longueur des réponses.
- **Gère les erreurs** (clé invalide, quota dépassé) : voir `app_streamlit.py`.
- Le modèle **n'a pas de mémoire** : c'est ton code qui renvoie l'historique.
- Le modèle **peut se tromper** : vérifie les informations importantes.
- **N'envoie pas de données personnelles réelles** : elles passent par les serveurs du fournisseur.

## Liens

- Clé API Groq : https://console.groq.com
- Documentation Groq : https://console.groq.com/docs
