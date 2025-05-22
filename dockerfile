FROM python:3.11-slim

# On reste à la racine du projet
WORKDIR /code

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tous les fichiers (code + templates + static + sql etc.)
COPY . .

# Lancer l'application Flask
CMD ["python", "Main.py"]
