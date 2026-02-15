import requests
from bs4 import BeautifulSoup
import csv
import time
from datetime import datetime
from datetime import timedelta
import pandas as pd

#___________________________________
#SCRAPING
#___________________________________

# Configuration
BASE_URL = "https://grainesdefolie.com"
SEARCH_URL = "https://grainesdefolie.com/recherche"

# Votre liste exacte
LEGUMES_RECHERCHE = ["CAROTTE", "TOMATE", "COURGETTE", "CONCOMBRE", "POIREAU", "POMME DE TERRE", "LAITUE", "POTIMARRON","BUTTERNUT", "HARICOTS VERTS"]


def scrape_graines():
    resultats_finaux = []
    headers = {'User-Agent': 'Mozilla/5.0'}

    for legume in LEGUMES_RECHERCHE:
        page = 1
        print(f"\n--- Recherche en cours pour : {legume} ---")
        
        while True:
            # On utilise l'URL de recherche universelle du site
            # format : https://grainesdefolie.com/recherche?s=CAROTTE&page=1
            params = {
                's': legume,
                'page': page
            }
            
            try:
                response = requests.get(SEARCH_URL, params=params, headers=headers)
                if response.status_code != 200:
                    break
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # On cible les blocs produits
                produits = soup.find_all('div', class_='product-description')
                
                # Si la page est vide (pas de produits), on passe au légume suivant
                if not produits:
                    break
                
                for produit in produits:
                    # Extraction du nom
                    nom_tag = produit.find('h2', class_='product-title')
                    nom = nom_tag.get_text(strip=True) if nom_tag else "N/A"
                    
                    # Extraction du prix
                    prix_tag = produit.find('span', class_='price') or produit.find('span', class_='regular-price')
                    prix = prix_tag.get_text(strip=True) if prix_tag else "N/A"
                    
                    # Filtrage de sécurité : on vérifie que le mot clé est bien dans le nom
                    # (pour éviter d'avoir des "engrais" quand on cherche "carotte")
                    if legume.split()[0].upper() in nom.upper():
                        resultats_finaux.append([legume, nom, prix])
                        print(f"Trouvé : {nom} - {prix}")

                # Pagination : vérifier s'il y a une page suivante
                # Si le nombre de produits trouvés est faible, on peut s'arrêter
                page += 1
                time.sleep(1) # Pause pour le site
                
                if page > 5: # Sécurité pour ne pas boucler trop longtemps par légume
                    break
                    
            except Exception as e:
                print(f"Erreur sur {legume}: {e}")
                break

    return resultats_finaux

#________________________________

# SCRAPING - Exécution et Sauvegarde 
#________________________________

data = scrape_graines()

csv_file = "Prix_graines.csv"
with open(csv_file, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["Categorie", "Nom Produit", "Prix"])
    writer.writerows(data)

print(f"\nExtraction terminée ! Fichier disponible : {csv_file}")


#________________________________
# CLEANING 
#________________________________

df_prix_graines = pd.read_csv("prix_graines.csv")
df_pg_clean = df_prix_graines.copy()

#Renommer les colonnes 
df_pg_clean = df_pg_clean.rename(columns={'Nom Produit': 'Legume'})

#supprimer les euros
df_pg_clean["Prix"]=df_pg_clean["Prix"].str.strip(" €")

#remplacer les , par un . pour pouvoir convertir en float
df_pg_clean["Prix"]=df_pg_clean["Prix"].str.replace(",", ".")

#convertir en float
df_pg_clean["Prix"]=df_pg_clean["Prix"].astype(float)

#Gerer les cases
df_pg_clean['Categorie'] = df_pg_clean['Categorie'].str.strip().str.capitalize()
df_pg_clean['Legume'] = df_pg_clean['Legume'].str.strip().str.capitalize()

#Supprimer les doublons et les outsiders
df_pg_clean.drop_duplicates()
df_pg_clean = df_pg_clean[df_pg_clean["Prix"] < 4]

#Exporter le DF en csv (sauvergarder)
df_pg_clean.to_csv('Prix_graines_clean.csv', index=False)

#________________________________
#CREATION D'UN DATA FRAME MOYENNE
#________________________________

    
df_moyenne = df_pg_clean.copy()
df_moyenne = df_moyenne.groupby('Categorie')['Prix'].mean().round(2).reset_index()

#Exporter le Df en csv (sauvergarder)
df_moyenne.to_csv('Prix_graine_moyen.csv', index=False)

print("Fichier prix graine mis à jour")