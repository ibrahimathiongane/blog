import os
from datetime import datetime, timezone
from app import create_app, db, bcrypt
from app.models import User, Category, Tag, Article, Project
from app.utils import make_slug, estimate_read_time
from dotenv import load_dotenv

load_dotenv()

def seed():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        print("── Initialisation de la base de données...")
        db.create_all()

        # 1. Admin User
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_email = os.environ.get("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")

        if not User.query.filter_by(username=admin_username).first():
            print(f"── Création de l'utilisateur admin : {admin_username}")
            hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
            user = User(username=admin_username, email=admin_email, password_hash=hashed_pw)
            db.session.add(user)
        else:
            print(f"── Utilisateur admin {admin_username} existe déjà.")

        # 2. Categories
        print("── Création des catégories...")
        cat_names = ["Développement Web", "Architecture", "DevOps", "Réflexions"]
        categories = {}
        for name in cat_names:
            cat = Category.query.filter_by(name=name).first()
            if not cat:
                cat = Category(name=name, slug=make_slug(name), description=f"Articles sur {name}")
                db.session.add(cat)
            categories[name] = cat

        # 3. Tags
        print("── Création des tags...")
        tag_data = [
            ("Python", "#3776AB"), ("Flask", "#000000"), ("SQLAlchemy", "#D71F00"),
            ("PostgreSQL", "#336791"), ("Docker", "#2496ED"), ("Tutorial", "#6366f1")
        ]
        tags = {}
        for name, color in tag_data:
            tag = Tag.query.filter_by(name=name).first()
            if not tag:
                tag = Tag(name=name, slug=make_slug(name), color=color)
                db.session.add(tag)
            tags[name] = tag

        db.session.commit()

        # 4. Projects
        print("── Création des projets...")
        if not Project.query.first():
            p1 = Project(
                title="Blog Tech Flask",
                slug="blog-tech-flask",
                description="Un blog personnel ultra-rapide avec interface admin et rendu Markdown.",
                tech_stack="Python, Flask, SQLAlchemy, TailwindCSS",
                github_url="https://github.com",
                is_featured=True,
                order=1
            )
            p2 = Project(
                title="API Dashboard",
                slug="api-dashboard",
                description="Dashboard moderne pour le monitoring d'APIs en temps réel.",
                tech_stack="FastAPI, Redis, PostgreSQL",
                github_url="https://github.com",
                order=2
            )
            db.session.add_all([p1, p2])

        # 5. Articles
        print("── Création des articles...")
        if not Article.query.first():
            a1_content = """# Pourquoi Flask en 2026 ?

Flask reste l'un des meilleurs choix pour construire des applications web robustes et légères. Sa philosophie "micro" permet une flexibilité totale.

## Les avantages
1. **Légèreté** : Pas de surplus inutile.
2. **Extensions** : Flask-SQLAlchemy, Flask-Migrate, etc.
3. **Contrôle** : Vous décidez de la structure de votre projet.

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"
```

### Conclusion
Flask est idéal pour les blogs, les APIs et les services spécialisés.
"""
            a1 = Article(
                title="Pourquoi choisir Flask pour votre blog tech ?",
                slug="pourquoi-flask-blog-tech",
                content=a1_content,
                summary="Découvrez pourquoi Flask est le framework idéal pour un blog personnel performant et personnalisable.",
                category=categories["Développement Web"],
                is_published=True,
                published_at=datetime.now(timezone.utc),
                read_time=estimate_read_time(a1_content)
            )
            a1.tags = [tags["Python"], tags["Flask"]]

            a2_content = """# Déploiement sur Railway

Railway est devenu la plateforme de prédilection pour les développeurs indépendants.

## Étape par étape
- Connectez votre repo GitHub
- Configurez vos variables d'environnement
- Déployez !

> Railway gère automatiquement les certificats SSL et les bases de données PostgreSQL.
"""
            a2 = Article(
                title="Déployer une app Flask sur Railway",
                slug="deployer-flask-railway",
                content=a2_content,
                summary="Guide complet pour mettre votre application Python en production en quelques minutes.",
                category=categories["DevOps"],
                is_published=True,
                published_at=datetime.now(timezone.utc),
                read_time=estimate_read_time(a2_content)
            )
            a2.tags = [tags["Docker"], tags["Tutorial"]]

            db.session.add_all([a1, a2])

        db.session.commit()
        print("── Seed terminé avec succès ! ✅")

if __name__ == "__main__":
    seed()
