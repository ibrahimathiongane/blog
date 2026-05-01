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
        admin_email = "admin@example.com"
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
            ("Carrière", "Conseils pour les développeurs et Productivité."),
            ("Architecture", "Conception logicielle, microservices et patterns."),
            ("Cybersécurité", "Sécurité offensive/défensive et bonnes pratiques."),
            ("Data Science", "Analyse de données, Big Data et Visualisation.")
        ]
        categories = {}
        for name, desc in cat_data:
            cat = Category(name=name, slug=make_slug(name), description=desc)
            db.session.add(cat)
            categories[name] = cat
        db.session.commit()

        # 3. Tags
        tag_data = [
            ("Python", "#3776AB"), ("JavaScript", "#F7DF1E"), ("Rust", "#000000"),
            ("React", "#61DAFB"), ("Docker", "#2496ED"), ("AWS", "#FF9900"),
            ("Next.js", "#000000"), ("Tailwind", "#38B2AC"), ("AI", "#6366f1"),
            ("Tutorial", "#10b981"), ("Architecture", "#f59e0b"), ("Security", "#ef4444"),
            ("TypeScript", "#3178C6"), ("Kubernetes", "#326CE5"), ("PostgreSQL", "#336791"),
            ("Machine Learning", "#ff6f61"), ("Vue.js", "#4FC08D"), ("Go", "#00ADD8")
        ]
        tags = {}
        for name, color in tag_data:
            tag = Tag(name=name, slug=make_slug(name), color=color)
            db.session.add(tag)
            tags[name] = tag
        db.session.commit()

        # 4. Articles Topics (50 items)
        article_topics = [
            # Backend
            ("Maîtriser Python 3.12 en 2026", "Backend", ["Python", "Tutorial"], "code"),
            ("L'ascension de Rust dans le Web", "Backend", ["Rust", "Architecture"], "rust"),
            ("Architecture Microservices vs Monolithe", "Backend", ["Architecture", "Docker"], "structure"),
            ("Le guide complet de SQL avancé", "Backend", ["PostgreSQL", "Tutorial"], "database"),
            ("Sécuriser ses APIs avec OAuth 2.1", "Backend", ["Architecture", "Python", "Security"], "security"),
            ("Introduction au langage Go pour les dev Python", "Backend", ["Go", "Python"], "gopher"),
            ("Optimiser les performances Django en production", "Backend", ["Python", "Architecture"], "speed"),
            ("Pourquoi FastAPI détrône Flask ?", "Backend", ["Python", "Architecture"], "fast"),
            ("Comprendre Event Sourcing en 5 minutes", "Backend", ["Architecture"], "events"),
            ("GraphQL vs REST : Le match final", "Backend", ["Architecture", "JavaScript"], "api"),
            
            # Frontend
            ("Tailwind CSS : Pourquoi tout le monde l'aime ?", "Frontend", ["Tailwind", "Next.js"], "design"),
            ("Next.js 15 : Les nouveautés à ne pas manquer", "Frontend", ["Next.js", "React"], "react"),
            ("Optimiser le SEO d'une SPA", "Frontend", ["Next.js", "Architecture"], "seo"),
            ("Créer un Design System robuste", "Frontend", ["Tailwind", "React"], "system"),
            ("React Server Components : La révolution", "Frontend", ["React", "Next.js"], "server"),
            ("TypeScript : Les types avancés à connaître", "Frontend", ["TypeScript", "Tutorial"], "typescript"),
            ("Vue 3 et le Composition API", "Frontend", ["Vue.js"], "vue"),
            ("Web Components : L'avenir du web ?", "Frontend", ["JavaScript"], "web"),
            ("Accessibilité Web (a11y) pour les développeurs", "Frontend", ["Tutorial"], "accessibility"),
            ("State Management en 2026 : Au-delà de Redux", "Frontend", ["React", "JavaScript"], "state"),

            # DevOps
            ("Déployer Kubernetes sans douleur", "DevOps", ["Docker", "Kubernetes", "AWS"], "cloud"),
            ("CI/CD : Automatiser tout, tout de suite", "DevOps", ["Docker", "Tutorial"], "pipeline"),
            ("Monitoring : Prometheus et Grafana", "DevOps", ["Docker", "AWS"], "monitoring"),
            ("Infrastructure as Code avec Terraform", "DevOps", ["AWS", "Architecture"], "infrastructure"),
            ("Docker Desktop vs Podman : Le comparatif", "DevOps", ["Docker"], "containers"),
            ("Serverless : FaaS ou pas ?", "DevOps", ["AWS", "Architecture"], "serverless"),
            ("Sécuriser sa supply chain logicielle", "DevOps", ["Security", "Docker"], "supplychain"),
            ("GitOps : La nouvelle norme du déploiement", "DevOps", ["Kubernetes"], "gitops"),
            ("Optimiser ses coûts AWS en 2026", "DevOps", ["AWS"], "money"),
            ("Introduction à Ansible pour l'automatisation", "DevOps", ["Tutorial"], "ansible"),

            # AI
            ("Le futur des interfaces avec l'IA", "Intelligence Artificielle", ["AI", "React"], "ai"),
            ("Introduction au Deep Learning", "Intelligence Artificielle", ["AI", "Python", "Machine Learning"], "brain"),
            ("Prompt Engineering pour développeurs", "Intelligence Artificielle", ["AI"], "prompt"),
            ("Déployer son propre LLM localement", "Intelligence Artificielle", ["AI", "Python", "Docker"], "robot"),
            ("L'impact de l'IA sur le métier de développeur", "Intelligence Artificielle", ["AI", "Tutorial"], "future"),
            ("RAG (Retrieval Augmented Generation) expliqué", "Intelligence Artificielle", ["AI", "Python"], "search"),
            ("Fine-tuning de modèles Llama 3", "Intelligence Artificielle", ["AI", "Machine Learning"], "training"),
            ("Agents IA : L'autonomie arrive", "Intelligence Artificielle", ["AI"], "agents"),
            ("Éthique et IA : Les défis de demain", "Intelligence Artificielle", ["AI"], "ethics"),
            ("Copilot vs Cursor : Quel IDE choisir ?", "Intelligence Artificielle", ["AI", "Tutorial"], "editor"),

            # Career & Other
            ("Productivité : Le guide du développeur serein", "Carrière", ["Tutorial"], "productivity"),
            ("Pourquoi j'ai quitté VS Code pour Neovim", "Carrière", ["Tutorial"], "terminal"),
            ("Travailler en remote : Pièges et astuces", "Carrière", [], "remote"),
            ("Bâtir un portfolio qui convertit", "Carrière", ["Next.js", "Tailwind"], "portfolio"),
            ("Devenir Senior : Ce n'est pas que du code", "Carrière", ["Architecture"], "senior"),
            ("Apprendre à apprendre : La compétence ultime", "Carrière", ["Tutorial"], "learning"),
            ("Le burnout dans la tech : Prévenir et guérir", "Carrière", [], "health"),
            ("Contribution Open Source : Par où commencer ?", "Carrière", ["Tutorial"], "opensource"),
            ("Négocier son salaire de développeur", "Carrière", [], "salary"),
            ("L'importance du Personal Branding", "Carrière", [], "brand")
        ]
        
        # Image IDs for Unsplash to have varied and relevant images
        # Using keywords instead of IDs for easier generation
        image_keywords = {
            "code": "1498050105902-1329527a6f44",
            "rust": "1550751827-4bd374c3f58b",
            "structure": "1486406146926-c627a92ad1ab",
            "database": "1544383835-3b91a93e36e3",
            "security": "1550751827-4bd374c3f58b",
            "gopher": "1516251193007-45ef944ab8c6",
            "speed": "1461727823508-590cc41efa39",
            "fast": "1555066939-1ee7121b91c7",
            "events": "1504386106331-c0671e5170d3",
            "api": "1558494947-c93d0d89c024",
            "design": "1507237953261-1254086350e9",
            "react": "1633356122544-f134324a6cee",
            "seo": "1432888494042-5ec621293b04",
            "system": "1581291518857-ee8228305f62",
            "server": "1558494947-c93d0d89c024",
            "typescript": "1516116216644-cda99d779b62",
            "vue": "1551033406-8bb075021616",
            "web": "1547658719-2f50d7590de6",
            "accessibility": "1517048676354-2b2a196d27df",
            "state": "1508780703483-424a180d196f",
            "cloud": "1451187580459-43490279c0fa",
            "pipeline": "1518770660439-4636190af475",
            "monitoring": "1551288049-14300f340058",
            "infrastructure": "1487058123284-db7280ad35d0",
            "containers": "1605747514701-0b3323064b86",
            "serverless": "1496062031047-53f064a3a114",
            "supplychain": "1586528116311-59914436792b",
            "gitops": "1618409834874-323147817454",
            "money": "1553729450-99d1d1b090bf",
            "ansible": "1518433966027-466f9ccfd162",
            "ai": "1677442136034-03708ef1092e",
            "brain": "1558494947-c93d0d89c024",
            "prompt": "1526374962758-45a4726ea08d",
            "robot": "1485827404700-47cb52e3b4a4",
            "future": "1485827404700-47cb52e3b4a4",
            "search": "1488190211463-b9351573f3c7",
            "training": "1555942800-4525091e944b",
            "agents": "1531746020759-4ebb82a17692",
            "ethics": "1507413241721-3d4414a3b357",
            "editor": "1542831041-53c7a93072ec",
            "productivity": "1484480974632-7a252ce28b9e",
            "terminal": "1629654271607-4912fb6614c6",
            "remote": "1527689354783-0feb4c1d4a39",
            "portfolio": "1460925895230-f4296a9ef9d5",
            "senior": "1521733020294-266190067673",
            "learning": "1456518563968-16ef05c93530",
            "health": "1506126613410-c2a297f2e77c",
            "opensource": "1533709752244-46c07738f87f",
            "salary": "1589753191725-12df5ae40f25",
            "brand": "1493612273091-3dca055bf0fd"
        }

        articles = []
        now = datetime.now(timezone.utc)
        
        # Helper for varied content
        def generate_content(title, cat_name):
            paragraphs = [
                f"Bienvenue dans cet article approfondi sur **{title}**. Dans le paysage technologique de 2026, comprendre ces concepts est devenu crucial pour tout développeur souhaitant rester à la pointe.",
                f"Le domaine du **{cat_name}** évolue à une vitesse fulgurante. Ce qui était considéré comme une 'best practice' il y a deux ans est aujourd'hui souvent remis en question par de nouveaux paradigmes.",
                "Abordons maintenant les aspects techniques. Voici un exemple concret de ce dont nous parlons :",
                "```python\n# Exemple d'implémentation\ndef master_tech_2026(concept):\n    status = 'Learning' if concept.is_new else 'Mastering'\n    print(f'Currently {status} {concept.name}')\n    return True\n\nmaster_tech_2026({'name': '" + title + "', 'is_new': True})\n```",
                "En conclusion, l'adoption de ces outils et méthodologies demande du temps, mais le retour sur investissement en termes de qualité de code et de scalabilité est indéniable.",
                "N'hésitez pas à partager vos retours en commentaires ou à me contacter pour approfondir certains points !"
            ]
            return "\n\n".join(paragraphs)

        for i, (title, cat_name, tag_names, img_key) in enumerate(article_topics):
            content = generate_content(title, cat_name)
            
            # Scatter publication dates over the last 100 days
            pub_date = now - timedelta(days=random.randint(0, 100), hours=random.randint(0, 23))
            
            # Image selection
            photo_id = image_keywords.get(img_key, "1498050105902-1329527a6f44")
            cover_url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=1200&q=80"
            
            art = Article(
                title=title,
                slug=make_slug(title),
                content=content,
                summary=f"Tout ce qu'il faut savoir sur {title.lower()}. Un guide complet pour les développeurs modernes.",
                category=categories[cat_name],
                cover_image=cover_url,
                is_published=True,
                published_at=pub_date,
                created_at=pub_date - timedelta(days=1),
                read_time=random.randint(3, 12),
                views=random.randint(100, 5000),
                meta_title=f"{title} | Mon Blog Tech",
                meta_description=f"Apprenez-en plus sur {title} dans cet article détaillé."
            )
            db.session.add(art)
            art.tags = [tags[tn] for tn in tag_names]
            articles.append(art)
        
        db.session.commit()

        # 5. Projects (Optional but good to have)
        project_titles = [
            ("Sygost Analytics", "Plateforme de monitoring pour startups.", "Python, React, AWS"),
            ("Ghostwriter AI", "Assistant de rédaction basé sur GPT-4.", "Python, OpenAI, FastAPI"),
            ("Quantum Vault", "Gestionnaire de mots de passe décentralisé.", "Rust, WebAssembly"),
            ("Neon CSS", "Bibliothèque de composants UI cyberpunk.", "Tailwind, CSS"),
            ("DevFlow CLI", "Outil CLI pour automatiser le workflow dev.", "Go, Cobra"),
            ("EduTrack", "Système de gestion d'apprentissage tech.", "Python, Flask, PostgreSQL")
        ]
        for i, (pt, pd, ps) in enumerate(project_titles):
            proj = Project(
                title=pt,
                slug=make_slug(pt),
                description=pd,
                tech_stack=ps,
                github_url="https://github.com",
                image_url=f"https://images.unsplash.com/photo-{1500000000000 + i*1000}?auto=format&fit=crop&w=800&q=80",
                is_featured=(i < 3),
                order=i
            )
            db.session.add(proj)
        db.session.commit()

        # 6. Comments
        commenters = [
            ("Alice Durand", "alice@test.com"), ("Marc Technophile", None),
            ("Sarah Dev", "sarah@dev.io"), ("Julien Codeur", "julien@code.fr"),
            ("Thomas Backend", "thomas@tech.com"), ("Léa Design", None)
        ]
        
        messages = [
            "Super article ! Très instructif.",
            "J'ai une question sur l'implémentation...",
            "Merci pour ce partage, je vais tester ça tout de suite.",
            "C'est exactement ce que je cherchais, top !",
            "Bravo pour la clarté des explications.",
            "Le blog est super fluide, j'aime beaucoup le design."
        ]

        for art in random.sample(articles, 30): # Add comments to 30 articles
            num_comments = random.randint(1, 4)
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
        print(f"── Seed terminé avec succès ! ✅")
        print(f"── {Article.query.count()} articles créés.")
        print(f"── {Project.query.count()} projets créés.")
        print(f"── {Comment.query.count()} commentaires créés.")

if __name__ == "__main__":
    seed()
