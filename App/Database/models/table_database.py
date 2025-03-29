from sqlalchemy import Column, MetaData, ForeignKey, PrimaryKeyConstraint, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import VARCHAR, INTEGER, FLOAT
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base


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
    genre = Column(VARCHAR(1))
    rue_num_personne = Column(VARCHAR(128))
    ville_personne = Column(VARCHAR(128))
    code_postal_personne = Column(VARCHAR(12))
    date_anniversaire = Column(VARCHAR(12))

    #facture = relationship("Facture", back_populates="Utilisateur")

   

class Facture(Base):
     __tablename__ = 'Facture'
     nom_facture = Column(VARCHAR(24), primary_key = True, nullable = False)
     date_facture = Column(VARCHAR(12))
     total_facture = Column(FLOAT)
     email_personne = Column(VARCHAR(120), ForeignKey("maximilien.Utilisateur.email_personne"), nullable=False)

     #utilisateur = relationship("Utilisateur", back_populates="Facture")
     #article = relationship("Article", back_populates="Facture")

class Article(Base):
     __tablename__ = 'Article'

     nom_facture = Column(VARCHAR(24), ForeignKey("maximilien.Facture.nom_facture"), primary_key = True, nullable = False)
     nom_article = Column(VARCHAR(256), primary_key = True)
     quantite = Column(INTEGER)
     prix = Column(FLOAT)

     #facture = relationship("Facture", back_populates="Article")

     __table_args__ = (PrimaryKeyConstraint("nom_facture", "nom_article"),)


class Monitoring(Base):
    __tablename__ = "monitoring"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metric_name = Column(String(255))
    value = Column(Float, nullable=True)
    status = Column(String(50), nullable=True)
    details = Column(String, nullable=True)