# nexatech-sn - Blog Tech

Ce projet est le blog officiel de **nexatech-sn**, conçu pour partager des articles techniques, des projets et des réflexions sur le développement logiciel.

## 🚀 Fonctionnalités

- **Articles** : Système de blog complet avec support Markdown.
- **Projets** : Vitrine des réalisations techniques.
- **Admin** : Interface de gestion complète (articles, catégories, tags, projets).
- **SEO & Social** :
  - Flux RSS (`/rss.xml`)
  - Sitemap XML (`/sitemap.xml`)
  - Balises OpenGraph et Twitter Cards.
- **Design** : Interface moderne avec Tailwind CSS et mode sombre automatique.
- **Performance** : Système de cache intégré avec Flask-Caching.

## 🛠️ Stack Technique

- **Backend** : Flask (Python 3.10+)
- **Base de données** : SQLAlchemy (compatible SQLite, PostgreSQL, MySQL/MariaDB)
- **Frontend** : Jinja2, Tailwind CSS
- **Serveur WSGI** : Passenger (Phusion) pour PlanetHoster

## 💻 Installation Locale

1. **Cloner le projet** :
   ```bash
   git clone <votre-repo>
   cd blog
   ```

2. **Créer un environnement virtuel** :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer l'environnement** :
   Copiez `.env.example` vers `.env` et remplissez les valeurs.

5. **Lancer l'application** :
   ```bash
   python run.py
   ```

## 🌍 Déploiement sur PlanetHoster (N0C)

### 1. Préparation sur N0C
- Accédez à votre panneau **N0C** > **Hébergement** > **Applications** > **Python**.
- Créez une application avec les paramètres suivants :
  - **Répertoire** : `/blog` (ou votre dossier racine)
  - **Domaine** : `blog.nexatech-sn.online`
  - **Fichier de démarrage** : `passenger_wsgi.py`

### 2. Configuration des Variables d'Environnement
Ajoutez ces variables dans l'interface de l'application Python sur N0C :
- `FLASK_ENV`: `production`
- `SECRET_KEY`: (une clé secrète sécurisée)
- `DATABASE_URL`: `mysql+pymysql://user:password@localhost/dbname`
- `BLOG_TITLE`: `nexatech-sn`
- `BLOG_URL`: `https://blog.nexatech-sn.online`

### 3. Finalisation
- Cliquez sur **Run Pip Install** dans l'interface N0C.
- Assurez-vous que le dossier `static/uploads` possède les droits d'écriture pour l'upload d'images.

## 📧 Contact

- **Auteur** : Ibrahima Thiongane
- **Site Principal** : [nexatech-sn.online](https://nexatech-sn.online)
- **LinkedIn** : [ibrahima-thiongane](https://www.linkedin.com/in/ibrahima-thiongane-813758276/)
