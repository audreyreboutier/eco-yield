import pandas as pd
import os
import numpy as np
import unicodedata

#__________________________________________

# CONFIGURATION 
#__________________________________________

LEGUMES_RECHERCHE = ["CAROTTE", "TOMATE", "COURGETTE", "CONCOMBRE", "POIREAU", "POMME DE TERRE", "LAITUE", "COURGE", "HARICOTS VERTS"]

def supprimer_accents(texte):
    if not texte: return ""
    nfkd_form = unicodedata.normalize('NFKD', texte)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper().strip()

toutes_les_lignes = []

if not os.path.exists("extractions"):
    print("Erreur : Le dossier 'extractions' n'a pas été trouvé.")
else:
    for nom_fichier in os.listdir("extractions"):
        if nom_fichier.endswith(".txt"):
            annee = nom_fichier.replace(".txt", "")
            print(f"--- Traitement de l'année {annee} ---")
            
            with open(f"extractions/{nom_fichier}", "r", encoding="utf-8") as f:
                for num_ligne, ligne in enumerate(f):
                    # CORRECTION ICI : On ne fait pas .strip() avant le split
                    # pour garder les colonnes vides du bout de ligne
                    colonnes = ligne.replace("\n", "").split("\t")
                    
                    if len(colonnes) > 0:
                        produit_brut = colonnes[0]
                        produit_normalise = supprimer_accents(produit_brut)
                        
                        if any(legume in produit_normalise for legume in LEGUMES_RECHERCHE):
                            # On prend toutes les colonnes après le nom du produit (jusqu'à 12 mois)
                            prix_mois = colonnes[1:] 
                            
                            for i, prix in enumerate(prix_mois):
                                if i >= 12: break # On s'arrête à décembre
                                
                                prix_clean = prix.strip().replace("\xa0", "").replace(",", ".")
                                
                                if prix_clean and prix_clean != "":
                                    try:
                                        toutes_les_lignes.append({
                                            "Date": f"01/{str(i+1).zfill(2)}/{annee}",
                                            "Produit": produit_brut,
                                            "Prix": float(prix_clean)
                                        })
                                    except ValueError:
                                        continue 
#__________________________________________

# CRÉATION DU DATAFRAME
#__________________________________________

df = pd.DataFrame(toutes_les_lignes)

if df.empty:
    print("Attention : Aucune donnée n'a été extraite.")
else:
    # --- NETTOYAGE (Idem précédent) ---
    df['Categorie'] = df['Produit'].str.split(" ").str[0].str.upper()
    df['Categorie'] = df['Categorie'].apply(supprimer_accents)

    df.loc[df['Produit'].str.contains("Butternut", case=False), 'Categorie'] = "BUTTERNUT"
    df.loc[df['Produit'].str.contains("Potimarron", case=False), 'Categorie'] = "POTIMARRON"
    df['Categorie'] = df['Categorie'].replace("POMME", "POMME DE TERRE")

    df_split = df['Produit'].str.split("(", expand=True)
    df['Legume'] = df_split[0].str.strip()
    df['Unite'] = df_split[1].str.replace(")", "", regex=False).str.strip().str.lower() if 1 in df_split.columns else "kg"

    df['Unite'] = df['Unite'].str.replace(r'^(la |le |l\'|les )', '', regex=True)
    df['Legume'] = df['Legume'].str.replace(r' France biologique|France|biologique', '', regex=True, case=False).str.strip()

    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df = df[df['Unite'] != "botte"]

    def normaliser_prix(df_in, categorie_cible, poids_g):
        mask = (df_in['Unite'] == "pièce") & (df_in['Categorie'] == categorie_cible.upper())
        df_in.loc[mask, 'Prix'] = (df_in.loc[mask, 'Prix'] * 1000) / poids_g
        df_in.loc[mask, 'Unite'] = "kg"
        return df_in

    df = normaliser_prix(df, "CONCOMBRE", 400)
    df = normaliser_prix(df, "LAITUE", 450)
    df = normaliser_prix(df, "TOMATE", 150) 

    df = df.drop(columns=['Produit'])
    df['Prix'] = df['Prix'].round(2)
    
    ordre_colonne = ['Date', 'Categorie', 'Legume', 'Prix', 'Unite']
    df = df[ordre_colonne]
    df['Categorie'] = df['Categorie'].str.capitalize()
    df["Legume"] = df['Legume'].str.capitalize()

    df.to_csv("Prix_legumes_historique_clean.csv", index=False, sep=";")
    print(f"Succès ! Lignes extraites : {len(df)}")
    # Vérification spécifique pour les tomates de 2023
    tomates_2023 = df[(df['Categorie'] == 'Tomate') & (df['Date'].dt.year == 2023)]
    print(f"Nombre de relevés pour Tomate en 2023 : {len(tomates_2023)}")