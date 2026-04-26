





CAHIER DES CHARGES
Blog Tech Personnel

Projet	Blog Tech Personnel
Stack	Flask + HTML/CSS/TailwindCSS
Version	1.0
Date	26/04/2026
Auteur	Développeur Backend
Hébergement	Railway (~5-10€/mois)





1. Présentation du projet
1.1 Contexte
Ce projet consiste à concevoir et développer un blog tech personnel permettant de partager des projets informatiques, des réflexions et des articles de fond sur les technologies. Le blog est destiné à la communauté tech et aux recruteurs potentiels.

1.2 Objectifs
–	Créer une vitrine numérique pour les projets informatiques personnels
–	Partager des articles techniques, tutoriels et retours d'expérience
–	Exprimer des réflexions sur les tendances et l'écosystème tech
–	Construire une présence en ligne professionnelle durable
–	Contribuer à la communauté des développeurs

1.3 Public cible
–	Développeurs et étudiants en informatique
–	Recruteurs tech et entreprises
–	Passionnés de technologie francophones

2. Stack technique
Choix volontairement minimaliste : pas de framework JS front-end. Le rendu côté serveur via Jinja2 et une petite dose de Vanilla JS suffisent pour un blog performant et maintenable.

Composant	Technologie	Justification
Backend	Python Flask	Léger, maîtrisé, idéal pour un blog
ORM / BDD	SQLAlchemy + PostgreSQL	SQLite en dev, Postgres en prod
Templating	Jinja2	Natif Flask, logique de rendu claire
CSS	TailwindCSS (CDN)	Aucun build step JS requis
Markdown	python-markdown + Pygments	Rédaction et coloration syntaxique
Auth Admin	Flask-Login	Simple, suffisant pour un seul admin
Hébergement	Railway.app	PostgreSQL inclus, ~5-10€/mois
CI/CD	GitHub + Railway Auto-deploy	Push = déploiement automatique

3. Architecture de l'application
3.1 Structure des fichiers
blog/
├── app/
│   ├── __init__.py          # Factory Flask + extensions
│   ├── routes.py            # Routes publiques
│   ├── admin.py             # Routes admin protégées
│   ├── models.py            # Article, Tag, Category
│   └── templates/
│       ├── base.html        # Layout principal
│       ├── index.html       # Liste articles
│       ├── article.html     # Page article
│       ├── projects.html    # Vitrine projets
│       └── admin/           # Interface admin
├── static/
│   ├── css/                 # Styles custom
│   └── js/                  # Vanilla JS minimal
├── migrations/              # Alembic
├── config.py               # Config dev/prod
├── requirements.txt
└── run.py

3.2 Modèle de données
Modèle	Champs principaux	Relations
Article	id, title, slug, content (MD), summary, published_at, is_published	N tags, 1 catégorie
Tag	id, name, slug, color	N articles
Category	id, name, slug, description	N articles
Project	id, title, slug, description, tech_stack, github_url, demo_url, image_url	—

4. Fonctionnalités
4.1 MVP — Phase 1 (indispensable)
Côté public
–	Home : Page d'accueil
Liste paginée des articles avec titre, résumé, date, tags et catégorie.
–	Article : Page article
Rendu Markdown complet avec coloration syntaxique du code, temps de lecture estimé.
–	Projets : Page projets
Grille de cartes avec description, stack technique, liens GitHub/démo.
–	Filtrage par tag et catégorie
–	Page À propos
–	Flux RSS (lecture seule, très simple à implémenter avec Flask)

Interface Admin
–	Authentification sécurisée (Flask-Login + hash bcrypt)
–	CRUD complet pour Articles, Projets, Tags, Catégories
–	Éditeur Markdown avec prévisualisation en temps réel
–	Gestion du statut publié/brouillon
–	Upload d'images pour les projets

4.2 Phase 2 — Améliorations
–	Recherche fulltext (SQLite FTS5 ou PostgreSQL tsvector)
–	Commentaires via Giscus (GitHub Discussions, zéro base de données)
–	Mode sombre / clair (CSS variables + Vanilla JS)
–	Partage social automatique (OpenGraph tags)
–	Statistiques de lecture simples (vues par article)
–	Sitemap XML pour le SEO

4.3 Phase 3 — Nice to have
–	Newsletter (intégration Resend ou Mailgun)
–	Séries d'articles (tutoriels en plusieurs parties)
–	API REST pour les articles (consommable depuis d'autres projets)

5. Design et expérience utilisateur
5.1 Principes
–	Minimaliste et orienté contenu — le texte prime sur tout
–	Typographie soignée (police lisible, hiérarchie claire)
–	Performance maximale — pas de JS inutile, images optimisées
–	Responsive mobile-first
–	Accessibilité WCAG AA minimum

5.2 Pages à créer
Page	URL	Description
Accueil	/	Liste articles + présentation courte
Article	/blog/<slug>	Rendu Markdown complet
Projets	/projets	Grille des projets
À propos	/about	Bio, compétences, liens
Catégorie	/categorie/<slug>	Articles filtrés
Tag	/tag/<slug>	Articles filtrés par tag
Admin	/admin/	Dashboard protégé

6. SEO et performance
6.1 SEO technique
–	URLs propres avec slugs (ex: /blog/mon-premier-article)
–	Balises meta title et description uniques par page
–	OpenGraph et Twitter Card pour le partage social
–	Données structurées JSON-LD (Article, Person)
–	Sitemap XML généré automatiquement
–	Flux RSS pour les agrégateurs

6.2 Performance
–	Pas de framework JS front : zéro bundle à charger
–	TailwindCSS via CDN (acceptable pour un blog à faible trafic)
–	Mise en cache Flask-Caching sur les pages populaires
–	Images servies avec attribut loading=lazy

7. Sécurité
La sécurité est critique même pour un blog personnel : une compromission du compte admin permet de défigurer le site public.

–	Mots de passe hashés avec bcrypt (Flask-Bcrypt)
–	Protection CSRF sur tous les formulaires admin (Flask-WTF)
–	Sanitisation du HTML généré depuis le Markdown (bleach)
–	Variables sensibles dans .env (Flask-Dotenv), jamais en dur
–	HTTPS obligatoire en production (Railway gère le certificat TLS)
–	Rate limiting sur la route de login (Flask-Limiter)
–	En-têtes de sécurité HTTP (Content-Security-Policy, X-Frame-Options)

8. Déploiement et infrastructure
8.1 Environnements
Env.	Hébergement	Base de données	Coût
Développement	Local (127.0.0.1:5000)	SQLite	Gratuit
Production	Railway.app	PostgreSQL managé	~5-10€/mois

8.2 Pipeline CI/CD
–	Code versionné sur GitHub (dépôt privé ou public)
–	Railway surveille la branche main et déploie automatiquement à chaque push
–	Variables d'environnement gérées dans le dashboard Railway
–	Migrations Alembic exécutées au démarrage (flask db upgrade)

8.3 Domaine custom
Un domaine personnalisé (ex: monnom.dev) est recommandé. Railway permet de configurer un domaine custom avec certificat TLS automatique. Budget estimé : 10-15€/an pour un .dev.

9. Planning de développement
Phase	Contenu	Durée estimée
Phase 0 — Setup	Initialisation Flask, modèles, BDD, config Railway	2-3 jours
Phase 1 — Public	Templates Jinja2/Tailwind, routes publiques, rendu Markdown	1 semaine
Phase 2 — Admin	Auth, CRUD articles/projets, éditeur Markdown	1 semaine
Phase 3 — SEO	Meta tags, OpenGraph, RSS, sitemap	2-3 jours
Phase 4 — Finition	Tests, optimisation, déploiement prod, domaine custom	2-3 jours
Phase 5 — Extras	Recherche, commentaires Giscus, mode sombre	À définir

Conseil : publier dès la fin de la Phase 2, même avec peu d'articles. Le blog vivant vaut mieux que le blog parfait.

10. Livrables attendus
–	Code source complet versionné sur GitHub
–	Blog déployé et accessible sur Railway avec domaine custom
–	Base de données PostgreSQL en production
–	Documentation README avec instructions d'installation et de déploiement
–	Au moins 3 articles publiés au lancement

11. Dépendances Python principales
Package	Usage
flask	Framework web principal
flask-sqlalchemy	ORM et gestion de la BDD
flask-login	Authentification admin
flask-wtf	Formulaires + protection CSRF
flask-migrate	Migrations de schéma (Alembic)
flask-bcrypt	Hashage des mots de passe
flask-caching	Mise en cache des pages
flask-limiter	Rate limiting (login)
python-markdown	Rendu Markdown vers HTML
Pygments	Coloration syntaxique du code
bleach	Sanitisation HTML
python-dotenv	Variables d'environnement
psycopg2-binary	Connecteur PostgreSQL
gunicorn	Serveur WSGI en production

Cahier des Charges v1.0 — Blog Tech Personnel
