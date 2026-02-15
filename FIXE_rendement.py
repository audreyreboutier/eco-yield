import pandas as pd
import re


#___________
# SCRAPING 
#___________

url = "https://nopanic.fr/rendements-legumes/"

# 1. Récupérer tous les tableaux
tableaux = pd.read_html(url)

# Vérifier si on a bien au moins 3 tableaux avant de continuer
if len(tableaux) >= 3:
    # 2. On ne garde que les indices 0, 1 et 2 (les 3 premiers)
    selection = tableaux[:3]
    
    # 3. Fusionner la sélection
    df_final = pd.concat(selection, ignore_index=True)

    # 4. Sauvegarder
    df_final.to_csv("rendement_3_tableaux.csv", index=False)
    print("Succès : Les 3 premiers tableaux ont été fusionnés.")
else:
    print(f"Attention : Seulement {len(tableaux)} tableau(x) trouvé(s).")


#___________
# CLEANING 
#___________

df_rendement = pd.read_csv("rendement_3_tableaux.csv")

# 1 . MERGE LES COLONNES LEGUMES

# Identifier les colonnes "Légumes"
# On cherche toutes les colonnes qui commencent par 'Légumes'
cols_legumes = [c for c in df_rendement.columns if c.startswith('Légumes')]

# Identifier les autres colonnes (celles qu'on veut garder telles quelles)
cols_fixes = [c for c in df_rendement.columns if not c.startswith('Légumes')]

# Fusionner les colonnes
df_fusion = pd.melt(df_rendement, 
                    id_vars=cols_fixes,       # Les colonnes qui restent fixes 
                    value_vars=cols_legumes,  # Les colonnes à fusionner
                    var_name='Type_ok',  # Nom de la colonne qui contiendra l'ancien nom de la colonne
                    value_name='Legume')      # Nom de la clonne


# Nettoyer les lignes vides
# Comme on a fusionné 3 colonnes, on a créé beaucoup de lignes vides (NaN)
df_fusion = df_fusion.dropna(subset=['Legume'])

#Renommer les colonnes
df_fusion.columns = ['Type_supp', 'Rendement_kg_m2', 'Densite_pied_m2', 'Levée_jours', 'Recolte_jours', 'qté_1pers', 'Type','Legumes']
df_fusion = df_fusion.drop(columns=['Type_supp'])

#__________________________________________

#  NORMALISER LES VALEURS
#__________________________________________


#Creer une fonction pour faire une moyenne
def extraire_moyenne_num(valeur):
    """
    Prend n'importe quel texte, extrait les chiffres (fourchettes incluses)
    et retourne la moyenne.
    """
    if pd.isna(valeur) or valeur == '–' or valeur == '':
        return None
    
    # On nettoie le texte (gestion des virgules françaises)
    texte = str(valeur).replace(',', '.')
    
    # La Regex magique qui trouve tous les nombres (entiers et décimaux)
    nombres = [float(n) for n in re.findall(r'\d+\.?\d*', texte)]
    
    # On gère le résultat
    if not nombres:
        return None
    
    # On retourne la moyenne (si c'est '10-20', ça donne 15.0)
    return sum(nombres) / len(nombres)

# Appliquer la fonction :

df_fusion['Densite_pied_m2'] = df_fusion['Densite_pied_m2'].apply(extraire_moyenne_num)
df_fusion['Levée_jours'] = df_fusion['Levée_jours'].apply(extraire_moyenne_num)
df_fusion['Recolte_jours'] = df_fusion['Recolte_jours'].apply(extraire_moyenne_num)
df_fusion['qté_1pers'] = df_fusion['qté_1pers'].apply(extraire_moyenne_num)


# 3 . TRAITEMENT DE LA COLONNE RENDEMENT

#creation de la fonction

def convertir_en_kg_m2(row):
    texte = str(row['Rendement_kg_m2']).replace(',', '.') # On gère les virgules françaises
    densite = row['Densite_pied_m2']
    
    if pd.isna(texte) or texte in ['nan', '–', '']:
        return None
    
    # Extraire tous les nombres (pour gérer les fourchettes comme 0.8-2)
    nombres = [float(n) for n in re.findall(r'\d+\.?\d*', texte)]
    if not nombres:
        return None
    
    # On fait la moyenne de la fourchette
    moyenne_rendement = sum(nombres) / len(nombres)
    
    # --- LOGIQUE DE CONVERSION ---
    if "kg / pied" in texte or "kg/pied" in texte:
        # Si c'est au pied, on multiplie par la densité
        return round(moyenne_rendement * densite, 2)
    
    elif "kg / m²" in texte or "kg/m²" in texte:
        # Si c'est déjà au m2, on garde la valeur telle quelle
        return round(moyenne_rendement, 2)
    
    elif "fruits / pied" in texte:
        # Cas particulier (courges) : cela donne un nombre de fruits au m2
        # Pour ton ROI, tu pourras multiplier par un poids moyen par fruit plus tard
        return round(moyenne_rendement * densite, 2)
    
    return round(moyenne_rendement, 2)

#Application de la fonction
df_fusion['Rendement_kg_m2'] = df_fusion.apply(convertir_en_kg_m2, axis=1)

# 4. DIVISER LA COLONNE 2 PERSONNES
df_fusion['qté_1pers']= df_fusion['qté_1pers']/2

# 5. ORGANISER ET SAUVEGARDER 

df_rendement_clean = df_fusion.copy()
df_rendement_clean = df_rendement_clean.drop(columns=['Type'])

# On définit l'ordre que tu souhaites dans une liste
ordre_colonne = ['Legumes', 'Rendement_kg_m2', 'Densite_pied_m2', 'Levée_jours', 'Recolte_jours','qté_1pers']

# On réassigne le dataframe avec ce nouvel ordre
df_rendement_clean = df_rendement_clean[ordre_colonne]

#__________________________________________
# SAUVEGARDE 
#__________________________________________

df_rendement_clean.to_csv("Rendement_clean.csv", index=False)
print("Le fichier Rendement_clean.csv a été créé avec succès.")