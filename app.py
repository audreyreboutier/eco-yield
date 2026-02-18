import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# =============================
# ⚙️ CONFIG PAGE
# =============================
st.set_page_config(page_title="Eco-Yield", page_icon="🌱", layout="wide")

# =============================
# 🔁 Gestion navigation
# =============================
if "page" not in st.session_state:
    st.session_state.page = "home"

def aller_app():
    st.session_state.page = "app"

def retour_accueil():
    st.session_state.page = "home"

# =============================
# 📂 Charger légumes
# =============================
@st.cache_data
def charger_legumes():
    fichier = "FACT_potager.csv"

    if not os.path.exists(fichier):
        return {
            "Tomate": {"rendement": 9, "prix": 6, "co2": 4, "eau": 2, "graines": 2},
            "Carotte": {"rendement": 6, "prix": 3, "co2": 2, "eau": 1, "graines": 2},
            "Courgette": {"rendement": 15, "prix": 4, "co2": 5, "eau": 2, "graines": 2},
        }

    df = pd.read_csv(fichier)
    df.columns = df.columns.str.strip()

    donnees = {}
    for _, ligne in df.iterrows():
        nom = ligne["Nom_Legume"]
        rendement = float(ligne["Rendement_kg_m2"])
        co2_par_kg = (float(ligne["CO2_Economise_m2"]) / 1000) / rendement

        donnees[nom] = {
            "rendement": rendement,
            "prix": float(ligne["Prix_Marche_kg"]),
            "co2": co2_par_kg,
            "eau": float(ligne["Cout_Eau_m2"]),
            "graines": float(ligne["Prix_graine"]),
        }

    return donnees

LEGUMES = charger_legumes()

# =====================================================
# 🎨 CSS DESIGN PREMIUM
# =====================================================
st.markdown(
    """
<style>
/* Cartes KPI */
[data-testid="stMetric"] {
    background-color: #f9ecde;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #ffffff;
    text-align: center;
}

[data-testid="stMetricLabel"] > div {
    color: #022601 !important;
    justify-content: center !important;
}

[data-testid="stMetricValue"] > div {
    color: #022601 !important;
    justify-content: center !important;
    font-weight: bold !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
}

/* bouton centré */
div.stButton > button:first-child {
    display: block;
    margin: 0 auto;
}

/* Sidebar padding */
[data-testid="stSidebar"] {
    padding-top: 1rem;
    padding-left: 1rem;
    padding-right: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# =============================
# 🏠 PAGE DE BIENVENUE
# =============================
if st.session_state.page == "home":
    st.markdown("<br><br>", unsafe_allow_html=True)

    # --- Logo centré ---
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        if os.path.exists("logo_eco-yield.png"):
            st.image("logo_eco-yield.png", use_container_width=True)

    st.markdown("""
        <h1 style='text-align: center; color: #022601;'>Bienvenue sur Eco-Yield Simulator</h1>
        <p style='text-align: center; font-size: 1.3rem; color: #31333F;'>
            L'outil intelligent pour simuler les gains de vos récoltes <br>
            et mesurer votre impact écologique et bientôt planifier votre potager.
        </p>
        <br>
    """, unsafe_allow_html=True)

    st.button("Commencer mon potager 🌱", on_click=aller_app, use_container_width=True)

# =============================
# 🧮 PAGE SIMULATEUR
# =============================
else:

    # =============================
    # LOGO EN HAUT DE SIDEBAR
    # =============================
    side_c1, side_c2, side_c3 = st.sidebar.columns([1, 4, 1])
    with side_c2:
        if os.path.exists("logo_eco-yield.png"):
            st.image("logo_eco-yield.png", use_container_width=True)

    # =============================
    # PARAMÈTRES
    # =============================
    st.sidebar.header("Paramètres")
    surface_totale = st.sidebar.number_input("Surface totale (m²)", 1, 200, 30)
    annees = st.sidebar.slider("Nombre d'années", 1, 5, 3)
    taux_banque = st.sidebar.number_input("Taux bancaire (%)", value=1.7)
    investissement = st.sidebar.number_input("Investissement initial (€)", value=200.0)

    # =============================
    # CHOIX LÉGUMES
    # =============================
    st.sidebar.header("Vos légumes")
    selection = st.sidebar.multiselect("Choisis tes légumes", list(LEGUMES.keys()), default=list(LEGUMES.keys())[:2])
    allocations = {}
    surface_restante = surface_totale
    for legume in selection:
        m2 = st.sidebar.slider(f"{legume} (m²)", 0, surface_totale, 0)
        allocations[legume] = m2
        surface_restante -= m2

    if surface_restante < 0:
        st.sidebar.error(f"Dépassement de {abs(surface_restante)} m²")
    else:
        st.sidebar.success(f"Surface restante : {surface_restante} m²")

    # bouton retour
    st.sidebar.button("Retour accueil", on_click=retour_accueil, use_container_width=True)

    # =============================
    # CALCULS
    # =============================
    profit_cumule = 0
    valeur_banque = investissement
    production_kg = 0
    co2_total = 0
    valeur_annuelle = 0
    historique = []
    details = []

    for annee in range(annees + 1):
        if annee == 0:
            historique.append({"Année": 0, "Potager": -investissement, "Banque": investissement})
            continue

        valeur, couts, kg_annee, co2_annee = 0, 0, 0, 0

        for legume, m2 in allocations.items():
            if m2 == 0:
                continue

            d = LEGUMES[legume]
            kg = m2 * d["rendement"]
            val = kg * d["prix"]
            co2 = kg * d["co2"]
            cout = m2 * (d["eau"] + d["graines"])

            kg_annee += kg
            valeur += val
            co2_annee += co2
            couts += cout

            if annee == 1:
                details.append({
                    "Légume": legume,
                    "Surface (m²)": m2,
                    "Production (kg/an)": int(kg),
                    "Valeur (€/an)": int(val),
                    "CO2 économisé (kg/an)": int(co2),
                })

        profit_cumule += (valeur - couts)
        valeur_banque *= (1 + taux_banque / 100)

        production_kg = kg_annee
        co2_total = co2_annee * annee
        valeur_annuelle = valeur

        historique.append({
            "Année": annee,
            "Potager": profit_cumule - investissement,
            "Banque": valeur_banque
        })

    df = pd.DataFrame(historique)

    # =============================
    # AFFICHAGE
    # =============================
    st.title("Votre Simulateur Eco-Yield")
    col1, col2, col3 = st.columns(3)
    col1.metric("Valeur récolte / an", f"{int(valeur_annuelle)} €")
    col2.metric("CO₂ économisé", f"{int(co2_total)} kg")
    col3.metric("Production / an", f"{int(production_kg)} kg")

    # graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Année"], y=df["Potager"], name="Potager",
                             line=dict(color="#022601", width=4), fill="tozeroy", fillcolor="rgba(2,38,1,0.1)"))
    fig.add_trace(go.Scatter(x=df["Année"], y=df["Banque"], name="Banque",
                             line=dict(color="#f59e0b", width=3, dash="dash")))
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Années"),
        yaxis=dict(title="Valeur (€)")
    )
    st.plotly_chart(fig, use_container_width=True)

    # tableau
    if details:
        st.subheader("Détail par légume")
        st.dataframe(pd.DataFrame(details), use_container_width=True)
