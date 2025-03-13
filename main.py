from Database.db_connection import build_engine, build_dburl
from Database.models.monitoring import Base
import os

# Création des tables
if __name__ == "__main__":
    print("Création des tables...")
    engine, _ = build_engine()
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")