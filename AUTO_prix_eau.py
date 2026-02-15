import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import os

#________________________________
#  CONFIGURATION 
#________________________________
# Utiliser le nom de ton fichier actuel
FICHIER_EAU = 'Prix_eau.csv'

def get_latest_water_price(year):
    """
    Scrape le prix moyen du m3 d'eau pour une année donnée
    """
    url = f"https://www.eaufrance.fr/chiffres-cles/prix-moyen-global-de-leau-au-1er-janvier-{year}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Recherche de la balise contenant le prix
            price_tag = soup.find('div', class_='figure')
            if price_tag:
                # On extrait "4,34" de "4,34 €/m3"
                price_text = price_tag.text.split('€')[0].replace(',', '.').strip()
                return float(price_text)
    except Exception as e:
        print(f"Erreur lors du scraping de {year} : {e}")
    return None

#________________________________

# CHARGEMENT ET NETTOYAGE INITIAL
#________________________________


if os.path.exists(FICHIER_EAU):
    # On lit le fichier existant
    df = pd.read_csv(FICHIER_EAU)
    
    # Sécurité : On s'assure que 'Annee' ne contient que le chiffre de l'année (ex: 2026)
    # On corrige  le format "2009-01-01" en "2009"
    df['Annee'] = pd.to_datetime(df['Annee']).dt.year
else:
    # Si le fichier n'existe pas, on crée une base vide
    df = pd.DataFrame(columns=['Annee', 'Prix_m3'])

#________________________________

# MISE À JOUR (SCRAPING)
#________________________________

current_year = datetime.now().year

# On vérifie si l'année en cours est déjà présente
if current_year not in df['Annee'].values:
    new_price = get_latest_water_price(current_year)
    
    if new_price:
        new_row = pd.DataFrame({'Annee': [current_year], 'Prix_m3': [new_price]})
        df = pd.concat([df, new_row], ignore_index=True)
        print(f"Prix {current_year} ajouté : {new_price} €/m3")
    else:
        print(f"Le prix pour {current_year} n'est pas encore publié sur le site.")
else:
    print(f"L'année {current_year} est déjà à jour dans le fichier.")

#________________________________

# CLEANING FINAL ET CALCULS
#________________________________


def finalize_cleaning(df_input):
    df_c = df_input.copy()
    
    # On s'assure que les types sont corrects
    df_c['Annee'] = df_c['Annee'].astype(int)
    df_c['Prix_m3'] = pd.to_numeric(df_c['Prix_m3'])
    
    # Suppression des doublons éventuels
    df_c = df_c.drop_duplicates(subset=['Annee'], keep='last')
    
    # Tri par année
    df_c = df_c.sort_values('Annee')
    
    # CRÉATION DE LA COLONNE PRIX_M2
    # Formule : Prix_m3 * 0.5 (basé sur 500L/m2 de potager)
    df_c['Prix_m2'] = (df_c['Prix_m3'] * 0.5).round(2)
    
    return df_c

df_final = finalize_cleaning(df)

#________________________________

# SAUVEGARDE
#________________________________

df_final.to_csv(FICHIER_EAU, index=False, sep=';')

print("Fichier eau mis à jour")
print(df_final.tail())