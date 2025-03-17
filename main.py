from Database.db_connection import build_engine, build_dburl
from Database.models.table_database import Base, Utilisateur, Facture, Article

path = build_dburl

def create_tables():
    print("Création des tables...")
    engine, _ = build_engine()
    Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

def add_users(path='../../config/.env'):
    engine, SessionLocal = build_engine()
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

def get_users():
    SessionLocal = build_engine()
    session = SessionLocal
    try:
        users = session.query(Utilisateur).all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Age: {user.age}")
    finally:
        session.close()


# Mettre à jour un utilisateur
def update_user(user_id, new_name):
    SessionLocal = build_engine()
    session = SessionLocal
    try:
        user = session.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        if user:
            user.name = new_name
            session.commit()
            print(f"Utilisateur {user_id} mis à jour avec succès !")
        else:
            print(f"Aucun utilisateur trouvé avec l'ID {user_id}")
    finally:
        session.close()

# Supprimer un utilisateur
def delete_user(user_id):
    SessionLocal = build_engine()
    session = SessionLocal
    try:
        user = session.query(Utilisateur).filter(Utilisateur.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
            print(f"Utilisateur {user_id} supprimé avec succès !")
        else:
            print(f"Aucun utilisateur trouvé avec l'ID {user_id}")
    finally:
        session.close()

# Menu principal
if __name__ == "__main__":
    print("Options disponibles :")
    print("1 : Créer les tables")
    print("2 : Ajouter des utilisateurs")
    print("3 : Lire les utilisateurs")
    print("4 : Mettre à jour un utilisateur")
    print("5 : Supprimer un utilisateur")

    choice = input("Entrez le numéro de l'opération : ")

    if choice == "1":
        create_tables()
    elif choice == "2":
        add_users()
    elif choice == "3":
        get_users()
    elif choice == "4":
        user_id = int(input("ID de l'utilisateur à mettre à jour : "))
        new_name = input("Nouveau nom : ")
        update_user(user_id, new_name)
    elif choice == "5":
        user_id = int(input("ID de l'utilisateur à supprimer : "))
        delete_user(user_id)
    else:
        print("Choix invalide.")

