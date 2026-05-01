import os
import sys

# Ajouter le répertoire actuel au chemin de recherche des modules
sys.path.insert(0, os.path.dirname(__file__))

# Configurer l'environnement pour la production si ce n'est pas déjà fait via le panel N0C
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app

# PlanetHoster (via Passenger) cherche un objet nommé 'application'
application = create_app('default')
