import os
import feedparser
from newspaper import Article as NewsArticle
from datetime import datetime, timezone
from app import create_app, db
from app.models import Article, Category, Tag
from app.utils import make_slug, estimate_read_time
from dotenv import load_dotenv
import random

load_dotenv()

# THÉMATIQUES CIBLÉES
TOPICS = {
    "Intelligence Artificielle": ["IA", "AI", "ChatGPT", "métier", "remplacer", "emploi", "automatisation"],
    "Développement & Frameworks": ["JavaScript", "React", "Vue", "Next.js", "Framework", "mise à jour", "TypeScript"],
    "Gadgets & Hardware": ["Smartphone", "iPhone", "Nvidia", "Processeur", "gadget", "appareil", "console"]
}

# SOURCES DE QUALITÉ
RSS_FEEDS = [
    "https://www.frandroid.com/feed",
    "https://www.journaldugeek.com/feed/",
    "https://www.lemondeinformatique.fr/flux-rss/thematique/toute-l-actualite/rss.xml",
    "https://www.numerama.com/feed/"
]

def get_category_and_tags(title, content):
    text = (title + " " + content).lower()
    for cat_name, keywords in TOPICS.items():
        if any(kw.lower() in text for kw in keywords):
            return cat_name
    return "Veille Techno"

def generate_editorial_content(news_art, cat_name):
    paragraphs = news_art.text.split('\n\n')
    intro = paragraphs[0] if len(paragraphs) > 0 else ""
    body = "\n\n".join(paragraphs[1:6]) if len(paragraphs) > 1 else ""
    
    content = f"""# {news_art.title}

> **L'essentiel :** {news_art.meta_description or "Analyse des impacts de l'innovation technologique sur le marché actuel."}

{intro}

## Pourquoi c'est important ?
Dans le secteur **{cat_name}**, cette annonce marque un tournant. L'évolution des usages et des outils demande une veille constante pour anticiper les transformations de demain.

## Analyse de la rédaction
{body}

## Points clés à retenir
* **Innovation :** Une avancée concrète dans le domaine de la technologie.
* **Impact :** Des conséquences directes pour les utilisateurs et les professionnels.
* **Futur :** Une tendance à suivre de près dans les prochains mois.

---
*Source originale : [Article complet sur {news_art.source_url.split('//')[-1].split('/')[0]}]({news_art.url})*
"""
    return content

def fetch_and_publish():
    app = create_app(os.environ.get("FLASK_ENV", "development"))
    with app.app_context():
        articles_added = 0

        for url in RSS_FEEDS:
            print(f"🔍 Analyse : {url}")
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:8]:
                title = entry.title.strip()
                slug = make_slug(title)
                
                # Check doublon avant tout
                if Article.query.filter_by(slug=slug).first():
                    continue

                try:
                    news_art = NewsArticle(entry.link, language='fr')
                    news_art.download()
                    news_art.parse()
                    
                    cat_name = get_category_and_tags(news_art.title, news_art.text)
                    
                    # Filtres qualité
                    if any(x in news_art.title.lower() for x in ["promo", "bon plan", "test :"]):
                        continue
                    if len(news_art.text) < 800:
                        continue

                    category = Category.query.filter_by(name=cat_name).first()
                    if not category:
                        category = Category(name=cat_name, slug=make_slug(cat_name))
                        db.session.add(category)
                        db.session.commit()

                    cover_image = news_art.top_image or "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80"

                    new_article = Article(
                        title=news_art.title,
                        slug=slug,
                        content=generate_editorial_content(news_art, cat_name),
                        summary=news_art.meta_description or (news_art.text[:200] + "..."),
                        category=category,
                        is_published=True,
                        published_at=datetime.now(timezone.utc),
                        read_time=estimate_read_time(news_art.text),
                        cover_image=cover_image
                    )
                    
                    db.session.add(new_article)
                    db.session.commit()
                    articles_added += 1
                    print(f"✅ Publié : {news_art.title}")

                except Exception as e:
                    db.session.rollback() # CRITIQUE : évite de bloquer la session
                    print(f"⚠️ Ignoré ou Erreur : {news_art.title if 'news_art' in locals() else entry.link}")
                    continue

        print(f"🚀 Terminé : {articles_added} nouveaux articles éditoriaux.")

if __name__ == "__main__":
    fetch_and_publish()
