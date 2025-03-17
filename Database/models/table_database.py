from sqlalchemy import Column, MetaData, ForeignKey
from sqlalchemy.dialects.postgresql import VARCHAR, INTEGER
from sqlalchemy.orm import declarative_base


#######################################################################
####                      Declarative Base                          ### 
#######################################################################


# DB schema 
schema='maximilien'

# Metadata
metadata_obj = MetaData(schema=schema)

Base = declarative_base(metadata=metadata_obj)

#######################################################################
####                   Table Declarative Models                     ### 
#######################################################################

class Utilisateur(Base):
    __tablename__ = 'Utilisateur'

    email_personne = Column(VARCHAR(120), primary_key=True)
    nom_personne = Column(VARCHAR(128))
    gender = Column(VARCHAR(1))
    rue_num_personne = Column(VARCHAR(128))
    ville_personne = Column(VARCHAR(128))
    code_postal_personne = Column(VARCHAR(12))

   

class Facture(Base):
     __tablename__ = 'Facture'
     nom_facture = Column(VARCHAR(24), primary_key = True, nullable = False)
     date_facture = Column(VARCHAR(12))
     total_facture = Column(INTEGER)
     email_personne = Column(VARCHAR(120), ForeignKey("maximilien.Utilisateur.email_personne"), nullable=False)

class Article(Base):
     __tablename__ = 'Article'

     nom_facture = Column(VARCHAR(24), ForeignKey("maximilien.Facture.nom_facture"), primary_key = True, nullable = False)
     nom_article = Column(VARCHAR(256))
     quantite = Column(INTEGER)
     prix = Column(INTEGER)
