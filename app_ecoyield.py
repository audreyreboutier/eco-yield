import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Eco-Yield Simulator", page_icon="🌱", layout="wide")

# --- 2. GESTION DE LA NAVIGATION (SESSION STATE) ---
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def start_app():
    st.session_state.page = 'app'

def go_home():
    st.session_state.page = 'home'

# --- 3. CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_garden_data():
    fact_file = "FACT_potager.csv"
    if not os.path.exists(fact_file):
        return {
            "Tomate": {"yield": 9, "price": 6, "co2": 4000, "water": 2, "seeds": 2},
            "Carotte": {"yield": 6, "price": 3, "co2": 2000, "water": 1, "seeds": 2},
            "Courgette": {"yield": 15, "price": 4, "co2": 5000, "water": 2, "seeds": 2},
        }
    df = pd.read_csv(fact_file)
    df.columns = df.columns.str.strip()
    data = {}
    for _, row in df.iterrows():
        name = str(row['Nom_Legume']).strip()
        y_val = float(row['Rendement_kg_m2'])
        # CONVERSION : On divise par 1000 pour passer de g à kg
        co2_kg_m2 = float(row['CO2_Economise_m2']) / 1000
        
        data[name] = {
            "yield": y_val,
            "price": float(row['Prix_Marche_kg']),
            "co2": co2_kg_m2 / y_val if y_val > 0 else 0,
            "water": float(row['Cout_Eau_m2']),
            "seeds": float(row['Prix_graine'])
        }
    return data

@st.cache_data
def calculate_default_investment(surface):
    inv_file = "Investissement_Materiel.csv"
    if not os.path.exists(inv_file):
        return float(int(round(150.0 + (surface * 5.0))))
    df_inv = pd.read_csv(inv_file, sep=';')
    df_inv.columns = df_inv.columns.str.strip()
    fixed = df_inv[df_inv['Type_Cout'] == 'Fixe']['Prix_Estime'].sum()
    var_items = df_inv[df_inv['Type_Cout'] == 'Variable']
    variable = var_items['Prix_Estime'].sum() * (surface / 10) if not var_items.empty else surface * 5.0
    return float(int(round(fixed + variable)))

VEGETABLE_DATA = load_garden_data()

# --- 4. CSS PERSONNALISÉ ---
st.markdown("""
    <style>
    [data-testid="stSidebarUserContent"] {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
            
    /* 1. Style de la carte Metric (Fond beige clair) */
    [data-testid="stMetric"] {
        background-color: #f9ecde; 
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffffff;
        text-align: center;
    }

    /* 2. Texte en vert foncé */
    [data-testid="stMetricLabel"] > div {
        color: #022601 !important;
        justify-content: center !important;
    }

    [data-testid="stMetricValue"] > div {
        color: #022601 !important;
        justify-content: center !important;
        font-weight: bold !important;
    }

    /* 3. Centrage forcé */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        display: flex;
        justify-content: center;
    }
            
    [data-testid="stMetric"] {
        background-color: f9ecde;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #f2e2ce;
    }
    div.stButton > button:first-child {
        display: block;
        margin: 0 auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. LOGIQUE D'AFFICHAGE ---

# --- A. PAGE DE BIENVENUE ---
if st.session_state.page == 'home':
    st.markdown("<br><br>", unsafe_allow_html=True)
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
    
    bc1, bc2, bc3 = st.columns([1, 1, 1])
    with bc2:
        st.button("Commencer mon potager", on_click=start_app, use_container_width=True)

# --- B. PAGE DU SIMULATEUR ---
else:
    # Sidebar : Logo en haut
    side_c1, side_c2, side_c3 = st.sidebar.columns([1, 4, 1])
    with side_c2:
        if os.path.exists("logo_eco-yield.png"):
            st.image("logo_eco-yield.png", use_container_width=True)
    
    st.sidebar.markdown("")

    st.sidebar.header("Paramètres du Projet")
    total_surface = st.sidebar.number_input("Surface totale (m²)", min_value=1, value=30)
    years = st.sidebar.slider("Simulation (Années)", 1, 5, 3)
    bank_rate = st.sidebar.number_input("Taux d'intérêt (%)", value=1.7, step=0.1)

    suggested_inv = calculate_default_investment(total_surface)
    initial_investment = st.sidebar.number_input(
        "Investissement Initial (€)", 
        min_value=0.0, 
        value=float(int(round(suggested_inv)))
    )

    st.sidebar.markdown("---")
    st.sidebar.header("Vos légumes")

    selected_vegs = st.sidebar.multiselect(
        "Choisissez vos légumes", 
        list(VEGETABLE_DATA.keys()),
        default=list(VEGETABLE_DATA.keys())[:2]
    )

    allocations = {}
    remaining_surface = int(total_surface)

    for veg in selected_vegs:
        val = st.sidebar.slider(f"{veg} (m²)", 0, int(total_surface), 1)
        allocations[veg] = val
        remaining_surface -= val

    if remaining_surface < 0:
        st.sidebar.error(f"Excès : {abs(remaining_surface)} m²")
    else:
        st.sidebar.success(f"Libre : {remaining_surface} m²")
        
    # Sidebar : Bouton retour en bas
    st.sidebar.markdown("<br>" * 5, unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.button(" Retour à l'accueil", on_click=go_home, use_container_width=True)

    # --- CALCULS ---
    chart_data = []
    cumul_profit_garden = 0
    bank_value = float(initial_investment)

    for yr in range(years + 1):
        if yr == 0:
            chart_data.append({"Année": 0, "Potager (Net)": int(-initial_investment), "Placement Bancaire": int(initial_investment), "CO2": 0, "Kilos": 0, "Valeur Annuelle": 0})
            continue

        y_val, y_co2, y_costs, y_kg = 0, 0, 0, 0
        for veg, surf in allocations.items():
            s = VEGETABLE_DATA[veg]
            kg = surf * s["yield"]
            y_kg += kg
            y_val += kg * s["price"]
            y_co2 += kg * s["co2"] # Déjà converti en kg dans load_garden_data
            y_costs += (surf * s["water"]) + (surf * s["seeds"])

        cumul_profit_garden += (y_val - y_costs)
        bank_value *= (1 + bank_rate / 100)

        chart_data.append({
            "Année": yr,
            "Potager (Net)": int(round(cumul_profit_garden - initial_investment)),
            "Placement Bancaire": int(round(bank_value)),
            "CO2": int(round(y_co2 * yr)),
            "Kilos": int(round(y_kg)),
            "Valeur Annuelle": int(round(y_val))
        })

    df = pd.DataFrame(chart_data)

    # --- AFFICHAGE PRINCIPAL ---


    st.title("Votre Simulateur Eco-Yield")
    st.markdown("")

    col1, col2, col3 = st.columns(3)
    col1.metric("Valeur récolte / an", f"{chart_data[-1]['Valeur Annuelle']} €")
    # Affichage en kg
    col2.metric("Économie CO₂ Totale", f"{chart_data[-1]['CO2']} kg")
    col3.metric("Production / an", f"{chart_data[-1]['Kilos']} kg")

    st.markdown("")
    st.markdown("")
    st.subheader("Performance Financière")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Année"], y=df["Potager (Net)"], name="Profit Potager", line=dict(color='#022601', width=4), fill='tozeroy', fillcolor='rgba(2, 38, 1, 0.1)'))
    fig.add_trace(go.Scatter(x=df["Année"], y=df["Placement Bancaire"], name="Épargne", line=dict(color='#f59e0b', width=3, dash='dash')))

    fig.update_layout(hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title="Années"), yaxis=dict(title="Valeur (€)"))
    st.plotly_chart(fig, use_container_width=True)

    if allocations:
        st.subheader("Rendements détaillés")
        details = [{"Légume": v, "Surface (m²)": s, "Poids (kg/an)": int(s*VEGETABLE_DATA[v]["yield"]), "Valeur (€/an)": int(s*VEGETABLE_DATA[v]["yield"]*VEGETABLE_DATA[v]["price"]), "CO2 économisé (kg/an)": int(s*VEGETABLE_DATA[v]["yield"]*VEGETABLE_DATA[v]["co2"])} for v, s in allocations.items() if s > 0]
        st.table(pd.DataFrame(details))