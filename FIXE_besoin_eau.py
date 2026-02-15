import pandas as pd

# 1. Préparation des données dans un dictionnaire
# Les catégories sont maintenant en Capitalize et le Butternut a été ajouté.
data = {
    'Categorie': [
        'Tomate', 'Carotte', 'Courgette', 'Concombre', 'Poireau', 
        'Pomme de terre', 'Laitue', 'Potimarron', 'Butternut', 'Haricots verts', 
        'Radis', 'Ail', 'Oignon', 'Poivron', 'Aubergine'
    ],
    # Besoin moyen par semaine en période de croissance (L/m2)
    'Besoin_Hebdo_L_m2': [25, 15, 30, 30, 18, 15, 20, 25, 25, 22, 12, 10, 10, 20, 25],
    
    # Besoin total sur TOUT le cycle de vie (L/m2)
    'Besoin_Total_Cycle_L_m2': [400, 200, 350, 380, 250, 250, 150, 350, 350, 180, 80, 100, 100, 380, 400]
}

# 2. Création du DataFrame
df_eau = pd.DataFrame(data)

# 3. Export en fichier CSV
# Utilisation du point-virgule pour Excel et utf-8-sig pour les accents
nom_fichier = "Besoins_eau_legumes.csv"
df_eau.to_csv(nom_fichier, index=False, sep=";", encoding='utf-8-sig')

print(f" Le fichier '{nom_fichier}' a été mis à jour.")
print(df_eau.tail())

