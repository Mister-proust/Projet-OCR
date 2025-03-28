from sqlalchemy import inspect
from graphviz import Digraph
from Database.db_connection import SQLClient
from Database.models.table_database import Base, Utilisateur, Facture, Article

# Connexion à la base de données
client = SQLClient()
client.test_connection()  # Vérification de la connexion à la base de données

# Créer un objet Digraph pour Graphviz
dot = Digraph(comment='Diagramme de base de données')

# Obtenir un inspecteur pour obtenir les métadonnées des tables
inspector = inspect(client.engine)

# Ajouter les tables au diagramme
tables = inspector.get_table_names(schema='maximilien')  # Récupérer les tables dans le schéma 'maximilien'

for table_name in tables:
    dot.node(table_name, table_name)

# Ajouter les relations entre les tables
# Exemple d'ajout d'une relation entre Utilisateur et Facture
dot.edge('Utilisateur', 'Facture', label='a')  # 'a' ici représente la relation entre les tables

# Sauvegarder le diagramme en fichier PNG
dot.render('database_schema', format='png', cleanup=True)

print("Le diagramme a été généré et sauvegardé sous 'database_schema.png'.")
