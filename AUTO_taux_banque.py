import requests
import pandas as pd
import os

#___________________________________
# CONNEXION FICHIER SECRETS
#___________________________________


def get_api_key(path="secrets.txt"):
    with open(path, "r") as f:
        for line in f:
            if line.startswith("cle_api_banque"):
                return line.split("=", 1)[1].strip().strip('"')

api_key = get_api_key()

# URL de base pour l'API Webstat
BASE_URL = "https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets/observations/exports/json"

#___________________________________
# CONFIGURATION
#___________________________________

session = requests.Session()


# Configuration des en-têtes avec l'API key 
headers = {
    'Authorization':api_key,  
    'accept': "application/json"
}

# Fonction pour interroger l'API Webstat et récupérer une série avec la clause WHERE
def get_series(series_key):
    params = {
        "select": "time_period_end,obs_value",  # Colonnes à récupérer
        "where": f"series_key='{series_key}'"   # Filtrer par la série spécifiée avec la clause WHERE
    }
    
    # Requête via session avec en-têtes et proxy
    response = session.get(BASE_URL, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        # Conversion en DataFrame pandas
        df = pd.DataFrame(data)
        # Convertir les dates en format datetime pour faciliter la manipulation
        df['time_period_end'] = pd.to_datetime(df['time_period_end'])
        return df
    else:
        print(f"Erreur lors de la requête : {response.status_code}")
        return None

# Récupérer deux séries depuis l'API
serie_key_1 = "MIR1.M.FR.B.L23FRLA.D.R.A.2230U6.EUR.O"  # Taux du Livret A
serie_key_2 = "MIR1.M.FR.B.L22FRSP.H.R.A.2250U6.EUR.N" #Taux du Livret LDDS
serie_key_3 = "MIR1.M.FR.B.L23FRLP.H.R.A.2250U6.EUR.O" #Taux du Livret LEP
serie_key_4 = "ICP.M.FR.N.000000.4.ANR"  # France, Taux d'inflation

# Obtenir les deux séries
df_serie_1 = get_series(serie_key_1)
df_serie_2 = get_series(serie_key_2)
df_serie_3 = get_series(serie_key_3)
df_serie_4 = get_series(serie_key_4)

if all(df is not None for df in [df_serie_1, df_serie_2, df_serie_3, df_serie_4]):
    
    # On renomme les colonnes 'obs_value' pour les identifier
    df_serie_1 = df_serie_1.rename(columns={'obs_value': 'Livret_A'})
    df_serie_2 = df_serie_2.rename(columns={'obs_value': 'LDDS'})
    df_serie_3 = df_serie_3.rename(columns={'obs_value': 'LEP'})
    df_serie_4 = df_serie_4.rename(columns={'obs_value': 'Inflation'})

    # Fusion successive
    df_merged = df_serie_1.merge(df_serie_2, on='time_period_end', how='outer')
    df_merged = df_merged.merge(df_serie_3, on='time_period_end', how='outer')
    df_merged = df_merged.merge(df_serie_4, on='time_period_end', how='outer')

    # Filtrage à partir de 2020 (plus pertinent pour ton projet)
    df_filtered = df_merged[df_merged['time_period_end'] >= '2020-01-01'].sort_values('time_period_end')

    #___________________________________
    # SAUVEGARDE
    #___________________________________

    df_filtered.to_csv("Taux_bancaires_clean.csv", index=False)
    print("Fichier taux bancaires mis à jour")