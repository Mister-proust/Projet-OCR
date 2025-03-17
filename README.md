# Projet-OCR
Projet réalisé dans le cadre de la formation Développeur en Intelligence Artificielle.


## Installation

1.  Création de l'environnement virtuel

```bash
python3 -m venv env
```

2. Activation de l'environnement virtuel

```bash
# Linux/MacOS
source env/bin/activate

# Windows
env\Scripts\activate
```

3. Installation des dépendances

```bash
pip install -r requirements.txt
```

4. Connexion à la base de données et fichier caché

Les paramètres de connexion à la base de données ainsi que les données sensibles doivent être mises dans un fichier ```.env```. Dans `load_dotenv()` mettre override=True en paramètre sur windows. 

```
# fichier .env

DB_HOST="database_host"
DB_PORT="server_port"
DB_USER="username"
DB_PASS="password"
DB_NAME="database_name"
DB_SCHEMA = "you_re_schema_name"

URL_SERVEUR = "URL du serveur"
SAS_SERVEUR = "SAS de l'entreprise"