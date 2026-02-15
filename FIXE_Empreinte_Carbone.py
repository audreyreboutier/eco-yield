import requests
import pandas as pd
import time

# __________________________________________
# LA FONCTION DE RÉCUPÉRATION
# __________________________________________

def recuperer_tableau_impact(nom_du_legume):

    # Cas particulier : l'URL de la pomme de terre est différente sur le site
    if nom_du_legume == "pomme-de-terre":
        url = "https://impactco2.fr/outils/alimentation/pommedeterre"
    else:
        url = f"https://impactco2.fr/outils/fruitsetlegumes/{nom_du_legume}"
        
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # pd.read_html lit tous les tableaux présents sur la page
        tous_les_tableaux = pd.read_html(response.text)
        
        if not tous_les_tableaux:
            return None
        
        # On récupère le premier tableau de la page
        tableau_brut = tous_les_tableaux[0]
        
        # Nettoyage : si le tableau a 3 colonnes, on supprime celle du milieu (le visuel)
        if tableau_brut.shape[1] >= 3:
            tableau_brut = tableau_brut.iloc[:, [0, -1]]
        
        tableau_brut.columns = ['Etape', 'Valeur']
        
        # On ajoute le nom du légume dans une colonne pour s'en souvenir
        tableau_brut.insert(0, 'Legume', nom_du_legume.capitalize())
        return tableau_brut
            
    except Exception as e:
        print(f"Erreur sur {nom_du_legume}: {e}")
    return None

# __________________________________________
# LA BOUCLE PRINCIPALE
# __________________________________________

def lancer_le_scraping():
    # Voici ta liste de légumes
    liste_des_legumes = [
        "tomate", "carotte", "courgette", "concombre", 
        "poireau", "pomme-de-terre", "laitue", 
        "potiron", "courge"
    ]
    
    toutes_les_lignes_finales = []
    
    # Boucle qui parcourt chaque nom de la liste
    for chaque_legume in liste_des_legumes:
        
        # On appelle la fonction avec le nom du legume
        resultat_tableau = recuperer_tableau_impact(chaque_legume)
        
        if resultat_tableau is not None:
            # On transforme le tableau vertical en une seule ligne horizontale
            try:
                # On enlève les doublons si besoin
                resultat_tableau = resultat_tableau.drop_duplicates(subset=['Legume', 'Etape'])
                
                # On "pivote" pour mettre les étapes en colonnes
                ligne_horizontale = resultat_tableau.pivot(index='Legume', columns='Etape', values='Valeur')
                toutes_les_lignes_finales.append(ligne_horizontale)
            except:
                print(f"Problème de format pour {chaque_legume}")
        
        # Pause de 0.5 seconde pour le site web
        time.sleep(0.5)

    # Une fois la boucle finie, on rassemble tout
    if toutes_les_lignes_finales:
        df_final = pd.concat(toutes_les_lignes_finales)
        
        # On organise les colonnes dans l'ordre que tu voulais
        ordre_colonnes = [
            'Agriculture', 'Transformation', 'Transport', 
            'Supermarché et distribution', 'Consommation', 'Total'
        ]
        
        # On vérifie lesquelles existent vraiment pour ne pas avoir d'erreur
        colonnes_presentes = [c for c in ordre_colonnes if c in df_final.columns]
        df_final = df_final[colonnes_presentes]
        
        # On remet le nom du légume comme colonne normale
        df_final.reset_index(inplace=True)
        
        # On enregistre le tout dans un CSV
        df_final.to_csv("impact_co2_complet.csv", index=False, sep=";", encoding='utf-8-sig')
        print("\n Succès ! Ton fichier 'impact_co2_complet.csv' est prêt.")
    else:
        print("Aucune donnée n'a pu être récupérée.")

# Lancement du programme
if __name__ == "__main__":
    lancer_le_scraping()

#__________________________________________
#  CLEANING DU DF
#__________________________________________

df_co2 = pd.read_csv("impact_co2_complet.csv", sep=";")
df_co2_clean = df_co2.copy()
df_co2_clean = df_co2_clean.rename(columns={'Supermarché et distribution': 'Distribution'})

def supprimer_unite(nom_colonne):
    # 1. On supprime le texte qu'on ne veut plus
    # 2. Remplace ',' avec '.' pour pouvoir le transformer un float
    df_co2_clean[nom_colonne] = (
        df_co2_clean[nom_colonne]
        .str.strip(" g CO₂e")
        .str.replace(",", ".")
    )
    # 3. Je converti en  float
    df_co2_clean[nom_colonne] = df_co2_clean[nom_colonne].astype(float)


 # On applique la fonction sur toutes les colonnes sauf 'Legume'
colonnes_impact = [c for c in df_co2_clean.columns if c != 'Legume']
for col in colonnes_impact:
    supprimer_unite(col)

# remplacer les vides
moyenne_transformation = df_co2_clean['Transformation'].mean()
moyenne_consommation = df_co2_clean['Consommation'].mean()

df_co2_clean['Transformation'] = df_co2_clean['Transformation'].fillna(moyenne_transformation).round(1)
df_co2_clean['Consommation'] = df_co2_clean['Consommation'].fillna(moyenne_consommation).round(1)


#Changer le nom des legumes 
def modifier_legume(legume):
  if legume == 'Potiron':
    return 'Potimarron'
  if legume == 'Pomme-de-terre':
    return 'Pomme de terre'
  elif legume == 'Courge':
    return 'Butternut'
  else: 
    return legume


df_co2_clean['Legume'] = df_co2_clean['Legume'].apply(modifier_legume)

#__________________________________________
# SAUVEGARDE DU DF FINAL
#__________________________________________

df_co2_clean.to_csv("Impact_co2_Clean.csv", index=False, sep=";", encoding='utf-8-sig')
print(" Le fichier 'Impact_co2_Clean.csv' est prêt.")