import os
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker
from Database.models.table_database import Utilisateur, Facture, Article

load_dotenv()

def build_dburl(path):
    """load_params"""
    load_dotenv(dotenv_path=path)
    DB_HOST = os.getenv("DB_HOST", None)
    DB_PORT = os.getenv("DB_PORT", 5432)
    DB_USER = os.getenv("DB_USER", None)
    DB_PASS = os.getenv("DB_PASS", None)
    DB_NAME = os.getenv("DB_NAME", "postgres")

    return  URL.create(
        "postgresql+psycopg2",
        username = DB_USER,
        password = DB_PASS,  
        host = DB_HOST,
        port = DB_PORT,
        database = DB_NAME,
    )

def build_engine(path='../../config/.env'):
    """make_engine"""
    url_object = build_dburl(path)
    print(url_object)
    engine = create_engine(url_object)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def add_users(path='../../config/.env'):
    url_object = build_dburl(path)
    print(url_object)
    engine = create_engine(url_object)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        #Onglet utilisateur
        utilisateur = Utilisateur(nom_personne="Alice", email_personne="test@test.com")
        mail = Utilisateur(nom_personne = "Bob", email_personne="blalfsf@fg.fr")

        db.add_all([utilisateur, mail ])
        db.commit()

        #Onglet facture
        facture = Facture(nom_facture="Alice", email_personne=utilisateur.email_personne)
        facture2 = Facture(nom_facture="LHUI", email_personne = mail.email_personne)

        db.add_all([facture, facture2])
        db.commit()

        #Onglet article
        article1 = Article(nom_facture=facture.nom_facture, nom_article="Chaussures", quantite=1, prix=50)
        user2 = Article(nom_facture=facture2.nom_facture, nom_article="nom_article")

        db.add_all([article1, user2])
        db.commit()


        print("Tables complétées avec succès !")
    finally:
        db.close()
