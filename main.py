from Database.db_connection import build_engine, build_dburl
from Database.models.table_database import Utilisateur, Facture, Article
from faker import Faker
from Database.db_connection import SQLClient

path = build_dburl

def generated_data(n=1):

    datas = []
    f=Faker()
    for _ in range(n):
        
        email = f.email()
        nom_facture = f.bothify(text = 'FAC/####/??')
        datas.append( {
            "utilisateur" : {
                "email_personne" : email,
                "nom_personne" : f.name(),
                "gender" : f.bothify(text = '?') ,
                "rue_num_personne" : f.street_address(),
                "ville_personne" : f.city() ,
                "code_postal_personne" : f.postalcode() ,
            }, 
            "facture" : {
                "nom_facture" : nom_facture ,
                "date_facture" : f.date(),
                "total_facture" : f.pydecimal(left_digits=4, right_digits=2, positive=True, min_value=1, max_value=1000),
                "email_personne" : email,

            },
            "article" : {
                "nom_facture"  : nom_facture ,
                "nom_article" : f.bothify(text = 'article ????????????????????????') ,
                "quantite" : int(f.bothify(text = '#')) ,
                "prix" : float(f.bothify(text = '##.##')) ,

            }
        })
    return datas

def create_tables():
    print("Création des tables...")
    engine, _ = build_engine()
    #Base.metadata.create_all(bind=engine)
    print("Tables créées avec succès !")

def add_data(client, data ):

    #Onglet utilisateur
    utilisateur = Utilisateur(**data["utilisateur"])
    client.insert(utilisateur)

    #Onglet facture
    facture = Facture(**data["facture"])
    client.insert(facture)

    #Onglet article
    article = Article(**data["article"])
    client.insert(article)

    print("Tables complétées avec succès !")


def get_facture(client):
    engine, SessionLocal = build_engine()
    session = SessionLocal
    try:
        users = session.query(Facture).all()
        for user in users:
            print(f"ID: {user.id}, Name: {user.name}, Age: {user.age}")
    finally:
        session.close()


# Mettre à jour un utilisateur
def update_facture(client, user_id, new_name):
    engine, SessionLocal = build_engine()
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
def delete_facture(client, user_id):
    engine, SessionLocal = build_engine()
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
    client = SQLClient()
    #client.drop_all()
    print("Options disponibles :")
    print("1 : Créer les tables")
    print("2 : Ajouter des factures")
    print("3 : Lire les factures")
    print("4 : Mettre à jour un utilisateur")
    print("5 : Supprimer un utilisateur")
    datas =generated_data(10)
    for data in datas : add_data(client, data)
    """

    choice = input("Entrez le numéro de l'opération : ")

    if choice == "1":
        create_tables()
    elif choice == "2":
        add_factures()
    elif choice == "3":
        get_facture()
    elif choice == "4":
        user_id = int(input("ID de l'utilisateur à mettre à jour : "))
        new_name = input("Nouveau nom : ")
        update_facture(user_id, new_name)
    elif choice == "5":
        user_id = int(input("ID de l'utilisateur à supprimer : "))
        delete_facture(user_id)
    else:
        print("Choix invalide.")

"""