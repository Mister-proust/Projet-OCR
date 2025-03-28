# Étape 1 : Utiliser une image Python officielle
FROM python:3.13-slim

# Étape 2 : Définir les arguments de construction qui recevront les secrets
# ARG DATABASE_URL
# ARG OCR_API
# ARG VISION_KEY
# ARG VISION_ENDPOINT
# ARG DISCORD_WEBHOOK

# Étape 3 : Transformer les arguments en variables d'environnement
ENV DATABASE_URL=
ENV OCR_API=
ENV VISION_KEY=
ENV VISION_ENDPOINT=
ENV DISCORD_WEBHOOK=

# Étape 4 : Installer Tesseract OCR et ses dépendances système
RUN apt-get update && apt-get install -y tesseract-ocr imagemagick zbar-tools && apt-get clean && rm -rf /var/lib/apt/lists/*

# Étape 5 : Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Étape 6 : Copier les fichiers nécessaires dans le conteneur
COPY . .

# Étape 7 : Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Étape 8 : Exposer le port utilisé par FastAPI
EXPOSE 8000

# Étape 9 : Commande pour exécuter l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]