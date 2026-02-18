# Utiliser une image Python légère
FROM python:3.9-slim

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le reste du code
COPY . .

# Exposer le port utilisé par Streamlit
EXPOSE 8080

# Commande pour lancer l'application
CMD ["streamlit", "run", "app_ecoyield.py", "--server.port=8080", "--server.address=0.0.0.0"]