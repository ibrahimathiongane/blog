import os
import random
from datetime import datetime, timezone, timedelta
from app import create_app, db, bcrypt
from app.models import User, Category, Tag, Article, Project, Comment
from app.utils import make_slug, estimate_read_time
from dotenv import load_dotenv

load_dotenv()

def seed():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        print("── Purge de la base de données...")
        db.drop_all()
        db.create_all()

        # 1. Admin User
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_email = "ibrahima@example.com"
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        
        hashed_pw = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        admin = User(username=admin_username, email=admin_email, password_hash=hashed_pw)
        db.session.add(admin)
        print(f"── Admin créé : {admin_email}")

        # 2. Categories
        cat_data = [
            ("Frontend", "Design system, React, CSS et UI/UX."),
            ("Backend", "Python, Rust, Architecture API et Bases de données."),
            ("DevOps", "CI/CD, Docker, Kubernetes et Cloud."),
            ("Intelligence Artificielle", "LLMs, Machine Learning et Automatisation."),
            ("Carrière", "Conseils pour les développeurs et Productivité.")
        ]
        categories = []
        for name, desc in cat_data:
            cat = Category(name=name, slug=make_slug(name), description=desc)
            db.session.add(cat)
            categories.append(cat)
        db.session.commit()

        # 3. Tags
        tag_data = [
            ("Python", "#3776AB"), ("JavaScript", "#F7DF1E"), ("Rust", "#000000"),
            ("React", "#61DAFB"), ("Docker", "#2496ED"), ("AWS", "#FF9900"),
            ("Next.js", "#000000"), ("Tailwind", "#38B2AC"), ("AI", "#6366f1"),
            ("Tutorial", "#10b981"), ("Architecture", "#f59e0b")
        ]
        tags = []
        for name, color in tag_data:
            tag = Tag(name=name, slug=make_slug(name), color=color)
            db.session.add(tag)
            tags.append(tag)
        db.session.commit()

        # 4. Projects
        project_titles = [
            ("Sygost Analytics", "Plateforme de monitoring pour startups."),
            ("Ghostwriter AI", "Assistant de rédaction basé sur GPT-4."),
            ("Quantum Vault", "Gestionnaire de mots de passe décentralisé."),
            ("Neon CSS", "Bibliothèque de composants UI cyberpunk."),
            ("DevFlow CLI", "Outil en ligne de commande pour automatiser le workflow dev."),
            ("EduTrack", "Système de gestion d'apprentissage pour écoles tech."),
            ("PixelPulse", "Moteur de rendu 2D ultra-rapide en Rust."),
            ("CloudKeeper", "Optimiseur de coûts pour infrastructure AWS.")
        ]
        projects = []
        for i, (title, desc) in enumerate(project_titles):
            proj = Project(
                title=title,
                slug=make_slug(title),
                description=desc,
                tech_stack=", ".join(random.sample([t.name for t in tags], 3)),
                github_url="https://github.com",
                demo_url="https://demo.com" if i % 2 == 0 else "",
                image_url=f"https://images.unsplash.com/photo-{1500000000000 + i*1000}?auto=format&fit=crop&w=800&q=80",
                is_featured=(i < 3),
                order=i
            )
            db.session.add(proj)
            projects.append(proj)
        db.session.commit()

        # 5. Articles
        article_topics = [
            ("Maîtriser Python en 2026", "Backend", ["Python", "Tutorial"]),
            ("L'ascension de Rust dans le Web", "Backend", ["Rust", "Architecture"]),
            ("Tailwind CSS : Pourquoi tout le monde l'aime ?", "Frontend", ["Tailwind", "Next.js"]),
            ("Déployer Kubernetes sans douleur", "DevOps", ["Docker", "AWS"]),
            ("Le futur des interfaces avec l'IA", "Intelligence Artificielle", ["AI", "React"]),
            ("Productivité : Le guide du développeur serein", "Carrière", ["Tutorial"]),
            ("Architecture Microservices vs Monolithe", "Backend", ["Architecture", "Docker"]),
            ("Next.js 15 : Les nouveautés à ne pas manquer", "Frontend", ["Next.js", "React"]),
            ("Sécuriser ses APIs avec OAuth 2.1", "Backend", ["Architecture", "Python"]),
            ("Pourquoi j'ai quitté VS Code pour Neovim", "Carrière", ["Tutorial"]),
            ("Optimiser le SEO d'une SPA", "Frontend", ["Next.js", "Architecture"]),
            ("Introduction au Deep Learning", "Intelligence Artificielle", ["AI", "Python"]),
            ("CI/CD : Automatiser tout, tout de suite", "DevOps", ["Docker", "Tutorial"]),
            ("Travailler en remote : Pièges et astuces", "Carrière", []),
            ("Le guide complet de SQL avancé", "Backend", ["Tutorial"]),
            ("Web3 : Au-delà de la hype", "Architecture", ["JavaScript"]),
            ("Créer un Design System robuste", "Frontend", ["Tailwind", "React"]),
            ("Monitoring : Prometheus et Grafana", "DevOps", ["Docker", "AWS"]),
            ("Prompt Engineering pour développeurs", "Intelligence Artificielle", ["AI"]),
            ("Bâtir un portfolio qui convertit", "Carrière", ["Next.js", "Tailwind"])
        ]
        
        articles = []
        now = datetime.now(timezone.utc)
        for i, (title, cat_name, tag_names) in enumerate(article_topics):
            content = f"# {title}\n\n" + "Ceci est un article de test généré automatiquement pour illustrer le nouveau design premium. " * 20
            content += "\n\n## Un sous-titre intéressant\n\n" + "On continue avec encore plus de contenu technique passionnant. " * 15
            content += "\n\n```python\ndef hello_world():\n    print('Hello from " + title + "!')\n```\n"
            
            pub_date = now - timedelta(days=i*2)
            art = Article(
                title=title,
                slug=make_slug(title),
                content=content,
                summary=f"Un aperçu passionnant sur {title.lower()}. Découvrez les meilleures pratiques et astuces.",
                category=[c for c in categories if c.name == cat_name][0],
                cover_image=f"https://images.unsplash.com/photo-{1600000000000 + i*1111}?auto=format&fit=crop&w=1200&q=80",
                is_published=True,
                published_at=pub_date,
                created_at=pub_date,
                read_time=estimate_read_time(content),
                views=random.randint(50, 1500)
            )
            art.tags = [t for t in tags if t.name in tag_names]
            db.session.add(art)
            articles.append(art)
        db.session.commit()

        # 6. Comments
        commenters = [
            ("Alice Durand", "alice@test.com"),
            ("Marc Technophile", None),
            ("Sarah Dev", "sarah@dev.io"),
            ("Admin (Test)", "ibrahima@example.com"),
            ("Julien Codeur", "julien@code.fr")
        ]
        
        messages = [
            "Super article ! Très instructif.",
            "J'ai une question sur l'implémentation de la partie 2...",
            "Merci pour ce partage, je vais tester ça tout de suite.",
            "C'est exactement ce que je cherchais, top !",
            "Je ne suis pas tout à fait d'accord sur le point 3, mais le reste est génial.",
            "Est-ce que tu penses faire un tutoriel sur la suite ?",
            "Design du blog incroyable au passage !",
            "Bravo pour la clarté des explications."
        ]

        for art in articles:
            num_comments = random.randint(1, 5)
            for _ in range(num_comments):
                author, email = random.choice(commenters)
                msg = random.choice(messages)
                comm = Comment(
                    author_name=author,
                    author_email=email,
                    content=msg,
                    article_id=art.id,
                    created_at=art.published_at + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(comm)
        
        db.session.commit()
        print(f"── Seed terminé ! 20 articles, 8 projets, et {Comment.query.count()} commentaires créés. ✅")

if __name__ == "__main__":
    seed()
