from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, abort, redirect, url_for,
    request, current_app, make_response,
)
from app import db, cache
from app.models import Article, Tag, Category, Project, Comment
from app.utils import render_markdown, build_rss_item
from app.forms import CommentForm

main_bp = Blueprint("main", __name__)

ARTICLES_PER_PAGE = 6


# ── Helpers ───────────────────────────────────────────────────────────────────

def _published_articles():
    return Article.query.filter_by(is_published=True).order_by(Article.published_at.desc())


# ── Public routes ─────────────────────────────────────────────────────────────

@main_bp.route("/")
@cache.cached(timeout=120, query_string=True)
def index():
    page = request.args.get("page", 1, type=int)
    articles = _published_articles().paginate(page=page, per_page=ARTICLES_PER_PAGE, error_out=False)
    tags = Tag.query.order_by(Tag.name).all()
    categories = Category.query.order_by(Category.name).all()
    return render_template(
        "index.html",
        articles=articles,
        tags=tags,
        categories=categories,
        title="Accueil",
    )


@main_bp.route("/blog/<slug>")
def article(slug):
    art = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    # Increment views (not cached)
    art.views += 1
    db.session.commit()
    
    form = CommentForm()
    html_content = render_markdown(art.content)
    
    # Comments are ordered by created_at desc in the relationship
    return render_template("article.html", article=art, content=html_content, form=form)


@main_bp.route("/blog/<slug>/comment", methods=["POST"])
def comment(slug):
    art = Article.query.filter_by(slug=slug, is_published=True).first_or_404()
    form = CommentForm()
    if form.validate_on_submit():
        new_comment = Comment(
            author_name=form.author_name.data,
            author_email=form.author_email.data,
            content=form.content.data,
            article_id=art.id
        )
        db.session.add(new_comment)
        db.session.commit()
        # Add a flash message
        from flask import flash
        flash("Merci ! Votre commentaire a été publié.", "success")
    else:
        from flask import flash
        flash("Erreur lors de l'envoi du commentaire. Veuillez vérifier les champs.", "danger")
        
    return redirect(url_for("main.article", slug=slug))


@main_bp.route("/projets")
@cache.cached(timeout=300)
def projects():
    projs = Project.query.order_by(Project.is_featured.desc(), Project.order, Project.created_at.desc()).all()
    return render_template("projects.html", projects=projs, title="Projets")


@main_bp.route("/about")
@cache.cached(timeout=600)
def about():
    return render_template("about.html", title="À propos")


@main_bp.route("/categorie/<slug>")
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    articles = (
        _published_articles()
        .filter_by(category_id=cat.id)
        .paginate(page=page, per_page=ARTICLES_PER_PAGE, error_out=False)
    )
    return render_template(
        "category.html",
        category=cat,
        articles=articles,
        title=f"Catégorie : {cat.name}",
    )


@main_bp.route("/tag/<slug>")
def tag(slug):
    t = Tag.query.filter_by(slug=slug).first_or_404()
    page = request.args.get("page", 1, type=int)
    articles = (
        _published_articles()
        .filter(Article.tags.contains(t))
        .paginate(page=page, per_page=ARTICLES_PER_PAGE, error_out=False)
    )
    return render_template(
        "tag.html",
        tag=t,
        articles=articles,
        title=f"Tag : {t.name}",
    )


@main_bp.route("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return redirect(url_for("main.index"))
    
    page = request.args.get("page", 1, type=int)
    # Simple search with LIKE for compatibility
    articles = (
        _published_articles()
        .filter(
            db.or_(
                Article.title.ilike(f"%{query}%"),
                Article.summary.ilike(f"%{query}%"),
                Article.content.ilike(f"%{query}%")
            )
        )
        .paginate(page=page, per_page=ARTICLES_PER_PAGE, error_out=False)
    )
    
    return render_template(
        "search.html",
        articles=articles,
        query=query,
        title=f"Résultats pour '{query}'"
    )


@main_bp.route("/rss.xml")
@cache.cached(timeout=600)
def rss():
    articles = _published_articles().limit(20).all()
    base_url = current_app.config["BLOG_URL"]
    items = [build_rss_item(a, base_url) for a in articles]
    response = make_response(
        render_template(
            "rss.xml",
            items=items,
            base_url=base_url,
            blog_title=current_app.config["BLOG_TITLE"],
            blog_description=current_app.config["BLOG_DESCRIPTION"],
            build_date=datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"),
        )
    )
    response.headers["Content-Type"] = "application/rss+xml; charset=utf-8"
    return response


@main_bp.route("/sitemap.xml")
@cache.cached(timeout=3600)
def sitemap():
    base_url = current_app.config["BLOG_URL"]
    articles = _published_articles().all()
    projects_all = Project.query.all()
    static_pages = [
        {"loc": base_url + "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": base_url + "/projets", "priority": "0.8", "changefreq": "weekly"},
        {"loc": base_url + "/about", "priority": "0.6", "changefreq": "monthly"},
    ]
    response = make_response(
        render_template(
            "sitemap.xml",
            base_url=base_url,
            articles=articles,
            projects=projects_all,
            static_pages=static_pages,
        )
    )
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response
