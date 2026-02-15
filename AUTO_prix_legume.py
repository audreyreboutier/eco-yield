import pandas as pd
import time
import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

#___________________________________
# CONFIGURATION 
#___________________________________

LEGUMES_RECHERCHE = ["CAROTTE", "TOMATE", "COURGETTE", "CONCOMBRE", "POIREAU", "POMME DE TERRE", "LAITUE", "COURGE", "HARICOTS VERTS"]
FICHIER_MASTER = "Prix_legumes_historique_clean.csv"

def nettoyer_data(df):
    """Appliquer le même nettoyage avec dissociation des courges"""
    # 1. Split initial pour le nom et l'unité
    df_split = df['Produit'].str.split("(", expand=True)
    df['Legume'] = df_split[0].str.strip()
    df['Unite'] = df_split[1].str.replace(")", "", regex=False).str.strip()

    #___________________________________
    # LOGIQUE POUR LA CATÉGORIE 
    #___________________________________
    # On définit les conditions
    conditions = [
        df['Produit'].str.contains('BUTTERNUT', case=False, na=False),
        df['Produit'].str.contains('POTIMARRON', case=False, na=False),
        df['Produit'].str.contains('POMME', case=False, na=False)
    ]
    
    # On définit les noms de catégories correspondants
    choix = ['Butternut', 'Potimarron', 'Pomme de terre']
    
    # Par défaut, on prend le premier mot 
    par_defaut = df['Produit'].str.split(" ").str[0].str.capitalize()

    # On applique la logique
    df['Categorie'] = np.select(conditions, choix, default=par_defaut)
    # ------------------------------------------

    # 2. Nettoyage textes
    df['Unite'] = df['Unite'].str.replace(r'^(la |le |l\'|les )', '', regex=True, case=False)
    df['Legume'] = df['Legume'].str.replace(r' France biologique|France|biologique', '', regex=True, case=False)

    # 3. Suppression Bottes
    df = df[df['Unite'] != "botte"].copy()

    # 4. Normalisation 
    def normaliser(df, cat, poids):
        mask = (df['Unite'] == "pièce") & (df['Categorie'] == cat)
        df.loc[mask, 'Prix'] = df.loc[mask, 'Prix'] * 1000 / poids
        df.loc[mask, 'Unite'] = "kg"
        return df

    df = normaliser(df, "Concombre", 400)
    df = normaliser(df, "Laitue", 450)

    # 5. Finition
    df['Prix'] = df['Prix'].round(2)
    df['Categorie'] = df['Categorie'].str.strip()
    df["Legume"] = df['Legume'].str.strip().str.capitalize()

    return df[['Date', 'Categorie', 'Legume', 'Prix', 'Unite']]



def scan_recent():
    print("Lancement du scraping (12 derniers mois)")
    url = "https://rnm.franceagrimer.fr/prix?M3027:12MOIS"
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    time.sleep(5)
    
    nouveaux_prix = []
    liens = driver.find_elements(By.TAG_NAME, "a")
    
    # On filtre les liens selon la liste LEGUMES_RECHERCHE
    noms_valides = [l.text.strip() for l in liens if any(leg in l.text.upper() for leg in LEGUMES_RECHERCHE)]
    
    for nom in noms_valides:
        try:
            driver.find_element(By.LINK_TEXT, nom).click()
            time.sleep(2)
            lignes = driver.find_elements(By.CSS_SELECTOR, "table.tabcot tr")
            for ligne in lignes[1:]:
                cols = ligne.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 3:
                    nouveaux_prix.append({
                        "Date": pd.to_datetime(cols[0].text.strip(), format='%d/%m/%y'),
                        "Produit": nom,
                        "Prix": float(cols[2].text.strip().replace(',', '.'))
                    })
            driver.back()
        except: continue
    
    driver.quit()
    return pd.DataFrame(nouveaux_prix)

#___________________________________
#  EXECUTION 
#___________________________________
if os.path.exists(FICHIER_MASTER):
    # 1. Récupérer le récent
    df_nouveau_sale = scan_recent()
    
    if not df_nouveau_sale.empty:
        # 2. Nettoyer le récent pour qu'il ressemble à l'historique
        df_nouveau_propre = nettoyer_data(df_nouveau_sale)
        
        # 3. Charger l'historique
        df_hist = pd.read_csv(FICHIER_MASTER, sep=";")
        df_hist['Date'] = pd.to_datetime(df_hist['Date'])
        
        # 4. Fusionner et supprimer les doublons
        df_final = pd.concat([df_hist, df_nouveau_propre])
        df_final = df_final.drop_duplicates(subset=['Date', 'Legume'], keep='last')
        
        # 5. Sauvegarder
        df_final.sort_values(by=['Categorie', 'Date']).to_csv(FICHIER_MASTER, index=False, sep=";")
        print(f" Mise à jour réussie ! Le fichier {FICHIER_MASTER} contient maintenant {len(df_final)} lignes.")
    else:
        print("Aucun nouveau prix trouvé sur le site.")
else:
    print("Erreur : Le fichier historique n'existe pas. Lance d'abord ton premier code !")



    #________________________________
    #CREATION D'UN DATA FRAME MOYENNE
    #________________________________

    
df_moyenne = pd.read_csv(FICHIER_MASTER, sep=";")
df_moyenne = df_moyenne.sort_values(by='Date')
df_moyenne = df_moyenne.groupby(['Date', 'Categorie'])['Prix'].mean().round(2).reset_index()

#Exporter le Df en csv (sauvergarder)
df_moyenne.to_csv('Prix_legume_moyen.csv', index=False)
print("Fichier prix legumes mis à jour")