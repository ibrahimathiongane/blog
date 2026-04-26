from datetime import datetime, timezone
from flask_login import UserMixin
from app import db, login_manager

# ── Many-to-many: Article ↔ Tag ──────────────────────────────────────────────
article_tags = db.Table(
    "article_tags",
    db.Column("article_id", db.Integer, db.ForeignKey("article.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tag.id"), primary_key=True),
)


# ── Models ────────────────────────────────────────────────────────────────────

class Category(db.Model):
    __tablename__ = "category"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, default="")
    articles = db.relationship("Article", back_populates="category", lazy="dynamic")

    def __repr__(self):
        return f"<Category {self.name}>"


class Tag(db.Model):
    __tablename__ = "tag"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(60), nullable=False, unique=True, index=True)
    color = db.Column(db.String(20), default="#6366f1")  # indigo default

    def __repr__(self):
        return f"<Tag {self.name}>"


class Article(db.Model):
    __tablename__ = "article"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    content = db.Column(db.Text, nullable=False, default="")
    summary = db.Column(db.String(500), default="")
    cover_image = db.Column(db.String(300), default="")
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_published = db.Column(db.Boolean, default=False, index=True)
    read_time = db.Column(db.Integer, default=1)  # minutes
    views = db.Column(db.Integer, default=0)
    # SEO
    meta_title = db.Column(db.String(200), default="")
    meta_description = db.Column(db.String(300), default="")

    # Relations
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=True)
    category = db.relationship("Category", back_populates="articles")
    tags = db.relationship("Tag", secondary=article_tags, backref="articles", lazy="subquery")

    def __repr__(self):
        return f"<Article {self.slug}>"

    @property
    def effective_meta_title(self):
        return self.meta_title or self.title

    @property
    def effective_meta_description(self):
        return self.meta_description or self.summary


class Project(db.Model):
    __tablename__ = "project"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(220), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, default="")
    tech_stack = db.Column(db.String(500), default="")  # comma-separated
    github_url = db.Column(db.String(300), default="")
    demo_url = db.Column(db.String(300), default="")
    image_url = db.Column(db.String(300), default="")
    is_featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def tech_list(self):
        return [t.strip() for t in self.tech_stack.split(",") if t.strip()]

    def __repr__(self):
        return f"<Project {self.title}>"


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<User {self.username}>"


class Comment(db.Model):
    __tablename__ = "comment"
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    author_email = db.Column(db.String(120), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_approved = db.Column(db.Boolean, default=True)

    article_id = db.Column(db.Integer, db.ForeignKey("article.id"), nullable=False)
    article = db.relationship("Article", back_populates="comments")


Article.comments = db.relationship("Comment", back_populates="article", cascade="all, delete-orphan", order_by="Comment.created_at.desc()")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
