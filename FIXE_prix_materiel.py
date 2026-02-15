import pandas as pd

# Données d'investissement avec la colonne Type_Cout
# Fixe = Achat unique (Outil, tuyau, etc.)
# Variable = A multiplier par les m2 (Carré potager, terreau)
data = [
    ["Bêche / Fourche-bêche", "Outil", 25.0, 10, 2.5, "Fixe"],
    ["Râteau", "Outil", 20.0, 10, 2.0, "Fixe"],
    ["Sécateur", "Outil", 15.0, 5, 3.0, "Fixe"],
    ["Transplantoir", "Outil", 10.0, 10, 0.5, "Fixe"], # Ajusté à 10 pour l'exemple
    ["Arrosoir (10L)", "Arrosage", 12.0, 10, 1.2, "Fixe"],
    ["Tuyau d'arrosage (20m)", "Arrosage", 30.0, 8, 3.75, "Fixe"],
    ["Terreau de démarrage (100L)", "Consommable", 20.0, 1, 20.0, "Variable"],
    ["Carré potager bois (1m2)", "Structure", 35.0, 5, 7.0, "Variable"],
    ["Gants de jardinage", "Protection", 8.0, 2, 4.0, "Fixe"],
    ["Récupérateur eau de pluie (300L)", "Optimisation", 60.0, 10, 6.0, "Fixe"],
    ["Serre de semis", "Structure", 60.0, 8, 7.5, "Fixe"] 
]

# Création du DataFrame avec la nouvelle colonne
columns = ["Item", "Categorie", "Prix_Estime", "Duree_Vie_Ans", "Amortissement_Annuel", "Type_Cout"]
df_invest = pd.DataFrame(data, columns=columns)

# Exportation en CSV
file_name = "Investissement_Materiel.csv"
df_invest.to_csv(file_name, index=False, sep=';', encoding='utf-8-sig')
