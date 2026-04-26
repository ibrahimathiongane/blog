import os
from datetime import datetime, timezone
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, abort, current_app, jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt, limiter, cache
from app.models import Article, Tag, Category, Project, User, Comment
from app.forms import LoginForm, ArticleForm, ProjectForm, TagForm, CategoryForm
from app.utils import make_slug, estimate_read_time, render_markdown

admin_bp = Blueprint("admin_bp", __name__, template_folder="../templates/admin")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Auth ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin_bp.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Connecté avec succès.", "success")
            return redirect(url_for("admin_bp.dashboard"))
        flash("Identifiants incorrects.", "danger")
    return render_template("admin/login.html", form=form, title="Connexion Admin")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Déconnecté.", "info")
    return redirect(url_for("main.index"))


# ── Dashboard ─────────────────────────────────────────────────────────────────

@admin_bp.route("/")
@login_required
def dashboard():
    stats = {
        "articles_total": Article.query.count(),
        "articles_published": Article.query.filter_by(is_published=True).count(),
        "articles_draft": Article.query.filter_by(is_published=False).count(),
        "projects_total": Project.query.count(),
        "tags_total": Tag.query.count(),
        "categories_total": Category.query.count(),
        "comments_total": Comment.query.count(),
        "total_views": db.session.query(db.func.sum(Article.views)).scalar() or 0,
    }
    recent_articles = Article.query.order_by(Article.created_at.desc()).limit(5).all()
    return render_template("admin/dashboard.html", stats=stats, recent_articles=recent_articles, title="Dashboard")


# ── Markdown Preview ──────────────────────────────────────────────────────────

@admin_bp.route("/preview", methods=["POST"])
@login_required
def preview():
    data = request.get_json(silent=True) or {}
    md_text = data.get("content", "")
    return jsonify({"html": render_markdown(md_text)})


# ── Articles ──────────────────────────────────────────────────────────────────

@admin_bp.route("/articles")
@login_required
def articles():
    page = request.args.get("page", 1, type=int)
    arts = Article.query.order_by(Article.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
    return render_template("admin/articles.html", articles=arts, title="Articles")


@admin_bp.route("/articles/new", methods=["GET", "POST"])
@login_required
def article_new():
    form = ArticleForm()
    _populate_category_choices(form)
    if form.validate_on_submit():
        art = _article_from_form(form, Article())
        db.session.add(art)
        db.session.commit()
        cache.clear()
        flash(f'Article "{art.title}" créé.', "success")
        return redirect(url_for("admin_bp.articles"))
    return render_template("admin/article_form.html", form=form, title="Nouvel article", action="Créer")


@admin_bp.route("/articles/<int:id>/edit", methods=["GET", "POST"])
@login_required
def article_edit(id):
    art = db.session.get(Article, id) or abort(404)
    form = ArticleForm(obj=art)
    _populate_category_choices(form)
    if request.method == "GET":
        form.tags.data = ", ".join(t.name for t in art.tags)
        form.category_id.data = art.category_id or 0
    if form.validate_on_submit():
        art = _article_from_form(form, art)
        db.session.commit()
        cache.clear()
        flash(f'Article "{art.title}" mis à jour.', "success")
        return redirect(url_for("admin_bp.articles"))
    return render_template("admin/article_form.html", form=form, article=art, title="Modifier l'article", action="Modifier")


@admin_bp.route("/articles/<int:id>/delete", methods=["POST"])
@login_required
def article_delete(id):
    art = db.session.get(Article, id) or abort(404)
    db.session.delete(art)
    db.session.commit()
    cache.clear()
    flash(f'Article "{art.title}" supprimé.', "warning")
    return redirect(url_for("admin_bp.articles"))


def _article_from_form(form, art):
    art.title = form.title.data
    art.slug = form.slug.data.strip() or make_slug(form.title.data)
    art.summary = form.summary.data
    art.content = form.content.data
    art.cover_image = form.cover_image.data
    art.category_id = form.category_id.data if form.category_id.data else None
    art.meta_title = form.meta_title.data
    art.meta_description = form.meta_description.data
    art.read_time = estimate_read_time(form.content.data)
    art.is_published = form.is_published.data
    if form.is_published.data and not art.published_at:
        art.published_at = datetime.now(timezone.utc)
    # Tags
    tag_names = [t.strip() for t in form.tags.data.split(",") if t.strip()]
    art.tags = []
    for tname in tag_names:
        tslug = make_slug(tname)
        tag = Tag.query.filter_by(slug=tslug).first()
        if not tag:
            tag = Tag(name=tname, slug=tslug)
            db.session.add(tag)
        art.tags.append(tag)
    return art


def _populate_category_choices(form):
    cats = Category.query.order_by(Category.name).all()
    form.category_id.choices = [(0, "— Aucune —")] + [(c.id, c.name) for c in cats]


# ── Projects ──────────────────────────────────────────────────────────────────

@admin_bp.route("/projects")
@login_required
def projects_list():
    projs = Project.query.order_by(Project.order, Project.created_at.desc()).all()
    return render_template("admin/projects.html", projects=projs, title="Projets")


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@login_required
def project_new():
    form = ProjectForm()
    if form.validate_on_submit():
        proj = _project_from_form(form, Project())
        db.session.add(proj)
        db.session.commit()
        cache.clear()
        flash(f'Projet "{proj.title}" créé.', "success")
        return redirect(url_for("admin_bp.projects_list"))
    return render_template("admin/project_form.html", form=form, title="Nouveau projet", action="Créer")


@admin_bp.route("/projects/<int:id>/edit", methods=["GET", "POST"])
@login_required
def project_edit(id):
    proj = db.session.get(Project, id) or abort(404)
    form = ProjectForm(obj=proj)
    if form.validate_on_submit():
        proj = _project_from_form(form, proj)
        db.session.commit()
        cache.clear()
        flash(f'Projet "{proj.title}" mis à jour.', "success")
        return redirect(url_for("admin_bp.projects_list"))
    return render_template("admin/project_form.html", form=form, project=proj, title="Modifier le projet", action="Modifier")


@admin_bp.route("/projects/<int:id>/delete", methods=["POST"])
@login_required
def project_delete(id):
    proj = db.session.get(Project, id) or abort(404)
    db.session.delete(proj)
    db.session.commit()
    cache.clear()
    flash(f'Projet "{proj.title}" supprimé.', "warning")
    return redirect(url_for("admin_bp.projects_list"))


def _project_from_form(form, proj):
    proj.title = form.title.data
    proj.slug = form.slug.data.strip() or make_slug(form.title.data)
    proj.description = form.description.data
    proj.tech_stack = form.tech_stack.data
    proj.github_url = form.github_url.data
    proj.demo_url = form.demo_url.data
    proj.image_url = form.image_url.data
    proj.is_featured = form.is_featured.data
    try:
        proj.order = int(form.order.data) if form.order.data else 0
    except ValueError:
        proj.order = 0
    return proj


# ── Tags ──────────────────────────────────────────────────────────────────────

@admin_bp.route("/tags", methods=["GET", "POST"])
@login_required
def tags_list():
    form = TagForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip() or make_slug(form.name.data)
        tag = Tag(name=form.name.data, slug=slug, color=form.color.data or "#6366f1")
        db.session.add(tag)
        db.session.commit()
        flash(f'Tag "{tag.name}" créé.', "success")
        return redirect(url_for("admin_bp.tags_list"))
    
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("admin/tags.html", tags=tags, form=form, title="Tags")




@admin_bp.route("/tags/<int:id>/edit", methods=["GET", "POST"])
@login_required
def tag_edit(id):
    tag = db.session.get(Tag, id) or abort(404)
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.slug = form.slug.data.strip() or make_slug(form.name.data)
        tag.color = form.color.data or "#6366f1"
        db.session.commit()
        flash(f'Tag "{tag.name}" mis à jour.', "success")
        return redirect(url_for("admin_bp.tags_list"))
    return render_template("admin/tag_form.html", form=form, tag=tag, title="Modifier le tag")


@admin_bp.route("/tags/<int:id>/delete", methods=["POST"])
@login_required
def tag_delete(id):
    tag = db.session.get(Tag, id) or abort(404)
    db.session.delete(tag)
    db.session.commit()
    flash(f'Tag "{tag.name}" supprimé.', "warning")
    return redirect(url_for("admin_bp.tags_list"))


# ── Categories ────────────────────────────────────────────────────────────────

@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
def categories_list():
    form = CategoryForm()
    if form.validate_on_submit():
        slug = form.slug.data.strip() or make_slug(form.name.data)
        cat = Category(name=form.name.data, slug=slug, description=form.description.data)
        db.session.add(cat)
        db.session.commit()
        flash(f'Catégorie "{cat.name}" créée.', "success")
        return redirect(url_for("admin_bp.categories_list"))

    cats = Category.query.order_by(Category.name).all()
    return render_template("admin/categories.html", categories=cats, form=form, title="Catégories")




@admin_bp.route("/categories/<int:id>/edit", methods=["GET", "POST"])
@login_required
def category_edit(id):
    cat = db.session.get(Category, id) or abort(404)
    form = CategoryForm(obj=cat)
    if form.validate_on_submit():
        cat.name = form.name.data
        cat.slug = form.slug.data.strip() or make_slug(form.name.data)
        cat.description = form.description.data
        db.session.commit()
        flash(f'Catégorie "{cat.name}" mise à jour.', "success")
        return redirect(url_for("admin_bp.categories_list"))
    return render_template("admin/category_form.html", form=form, cat=cat, title="Modifier la catégorie")


@admin_bp.route("/categories/<int:id>/delete", methods=["POST"])
@login_required
def category_delete(id):
    cat = db.session.get(Category, id) or abort(404)
    db.session.delete(cat)
    db.session.commit()
    flash(f'Catégorie "{cat.name}" supprimée.', "warning")
    return redirect(url_for("admin_bp.categories_list"))


# ── Comments ──────────────────────────────────────────────────────────────────

@admin_bp.route("/comments")
@login_required
def comments_list():
    page = request.args.get("page", 1, type=int)
    coms = Comment.query.order_by(Comment.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    return render_template("admin/comments.html", comments=coms, title="Commentaires")


@admin_bp.route("/comments/<int:id>/delete", methods=["POST"])
@login_required
def comment_delete(id):
    com = db.session.get(Comment, id) or abort(404)
    db.session.delete(com)
    db.session.commit()
    flash("Commentaire supprimé.", "warning")
    return redirect(url_for("admin_bp.comments_list"))
