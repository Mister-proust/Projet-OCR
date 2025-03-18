import os
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from Database.models.table_database import Base
import sqlalchemy 


def build_dburl(path):
    """load_params"""
    load_dotenv(dotenv_path=path, override=True)
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

def build_engine(path='.env', echo=True):
    """make_engine"""
    url_object = build_dburl(path)
    print(url_object)
    engine = create_engine(url=url_object)
    
    return engine


class SQLClient:
    def __init__(self):
        self.engine = build_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine, checkfirst=True)

    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()
    
    def drop_all(self):
        """ Supprime toute les tables """
        Base.metadata.drop_all(bind=self.engine)

    def test_connection(self):
        try:
            with self.get_session() as session:
                result = session.execute(text("SELECT version();"))
                print("✅ Connexion réussie à PostgreSQL !")
                for row in result:
                    print(f"Version PostgreSQL : {row[0]}")
        except Exception as e:
            print(f"❌ Erreur de connexion : {e}")
    
    def insert(self, row):
        with self.get_session() as session:
            try :
                session.add(row)
                session.commit()
            except sqlalchemy.exc.IntegrityError : 
                print(f"❌ {row} already exists.")

if __name__ == "__main__" :
    client = SQLClient()
    client.test_connection()