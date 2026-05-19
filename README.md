<<<<<<< HEAD
# test10
=======
# DataPulse v4 — Analytics Engine

Plateforme d'analyse de données e-commerce avec authentification, exports, et gestion avancée des imports.

## 🆕 Nouveautés v4

### Authentification
- Login / Register / Logout avec sessions sécurisées (Flask-Login)
- Chaque utilisateur voit uniquement ses propres imports
- Mots de passe hashés (Werkzeug PBKDF2)

### Gestion des imports
- ✅ Supprimer un import (bouton ✕ dans l'historique)
- ✅ Renommer un import (bouton ✏️)
- ✅ Pagination (10 imports par page)

### Filtres dashboard
- ✅ Filtrer l'historique par période (date début → date fin)
- ✅ Comparer 2 imports côte à côte (bouton ⇄)
- ✅ Filtrer la tendance de CA par période

### Exports
- ✅ Exporter les KPIs + données en **Excel** (`/export/excel/<id>`)
- ✅ Exporter un rapport en **PDF** (`/export/pdf/<id>`) — nécessite `reportlab`
- ✅ Exporter le graphique en **PNG** (bouton ↓ PNG)

### Sécurité
- ✅ Protection CSRF sur tous les formulaires et appels API (Flask-WTF)
- ✅ Rate limiting : 30 uploads/heure, 10 tentatives login/minute (Flask-Limiter)
- ✅ Variables d'environnement propres via `.env`
- ✅ Cookie de session `HttpOnly` + `SameSite=Lax`

### Gestion des erreurs
- ✅ Validation fichier vide
- ✅ Format invalide bloqué côté serveur et client
- ✅ Messages d'erreur clairs (colonnes manquantes, format incorrect)

## 🚀 Installation

```bash
# 1. Cloner / dézipper le projet
cd analytics_app_v4

# 2. Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env
# Éditer .env et définir SECRET_KEY

# 5. Lancer
python app.py
```

Ouvrir http://localhost:5000 → créer un compte → importer un fichier Excel/CSV.

## 📦 Structure

```
analytics_app_v4/
├── app.py              # Routes Flask, modèles SQLAlchemy, auth
├── analytics.py        # Traitement fichiers, calcul KPIs
├── requirements.txt
├── .env.example
├── templates/
│   ├── auth.html       # Login / Register
│   ├── index.html      # Page d'upload
│   └── dashboard.html  # Dashboard analytics
└── uploaded_files/     # Fichiers originaux sauvegardés (créé auto)
```

## 🌐 Déploiement Production

### Railway / Render
1. Pousser sur GitHub
2. Lier le repo sur Railway/Render
3. Ajouter les variables d'env (`DATABASE_URL` PostgreSQL, `SECRET_KEY`)
4. Le service détecte `requirements.txt` automatiquement

### Variables d'environnement obligatoires en prod
```
DATABASE_URL=postgresql://...
SECRET_KEY=<token aléatoire 32+ caractères>
```

### SQLite → PostgreSQL
Changer uniquement `DATABASE_URL` dans `.env` — SQLAlchemy gère le reste.

## 📋 Format fichier attendu

Colonnes requises : `Date`, `Produit`, `Prix`, `Quantité`, `Ville`, `Statut`

Télécharger le template : http://localhost:5000/template

## 🔜 Roadmap (à venir)
- [ ] Celery pour traitement asynchrone des gros fichiers
- [ ] Cache Redis sur les KPIs
- [ ] Notifications email
- [ ] 2FA
>>>>>>> d47b0c7 (test10)
