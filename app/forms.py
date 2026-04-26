from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField, TextAreaField, BooleanField, SelectField,
    PasswordField, SubmitField, URLField,
)
from wtforms.validators import DataRequired, Length, Optional, URL, Email


class LoginForm(FlaskForm):
    username = StringField("Nom d'utilisateur", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Se connecter")


class ArticleForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(max=200)])
    slug = StringField("Slug (auto-généré si vide)", validators=[Optional(), Length(max=220)])
    summary = TextAreaField("Résumé", validators=[Optional(), Length(max=500)])
    content = TextAreaField("Contenu (Markdown)", validators=[DataRequired()])
    cover_image = StringField("Image de couverture (URL)", validators=[Optional(), Length(max=300)])
    category_id = SelectField("Catégorie", coerce=int, validators=[Optional()])
    tags = StringField("Tags (séparés par virgule)", validators=[Optional()])
    is_published = BooleanField("Publier maintenant")
    meta_title = StringField("Meta Title SEO", validators=[Optional(), Length(max=200)])
    meta_description = TextAreaField("Meta Description SEO", validators=[Optional(), Length(max=300)])
    submit = SubmitField("Enregistrer")


class ProjectForm(FlaskForm):
    title = StringField("Titre", validators=[DataRequired(), Length(max=200)])
    slug = StringField("Slug (auto-généré si vide)", validators=[Optional(), Length(max=220)])
    description = TextAreaField("Description", validators=[DataRequired()])
    tech_stack = StringField("Stack technique (séparée par virgule)", validators=[Optional()])
    github_url = StringField("GitHub URL", validators=[Optional(), URL(), Length(max=300)])
    demo_url = StringField("Demo URL", validators=[Optional(), URL(), Length(max=300)])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=300)])
    is_featured = BooleanField("Projet mis en avant")
    order = StringField("Ordre d'affichage", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class TagForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(max=50)])
    slug = StringField("Slug (auto-généré si vide)", validators=[Optional(), Length(max=60)])
    color = StringField("Couleur hex (ex: #6366f1)", validators=[Optional(), Length(max=20)])
    submit = SubmitField("Enregistrer")


class CategoryForm(FlaskForm):
    name = StringField("Nom", validators=[DataRequired(), Length(max=80)])
    slug = StringField("Slug (auto-généré si vide)", validators=[Optional(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class CommentForm(FlaskForm):
    author_name = StringField("Nom", validators=[DataRequired(), Length(max=100)])
    author_email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    content = TextAreaField("Message", validators=[DataRequired(), Length(min=2)])
    submit = SubmitField("Envoyer")
