# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage du vinaigre",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Vos importations d'origine propres et saines se placent juste en dessous
from datetime import datetime
import math
import os
import random
import time
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du vinaigre")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


if "identifie" not in st.session_state:
    st.session_state.identifie = False
if "nom_var" not in st.session_state:
    st.session_state.nom_var = ""
if "prenom_var" not in st.session_state:
    st.session_state.prenom_var = ""
if "classe_var" not in st.session_state:
    st.session_state.classe_var = ""
if "verrouille" not in st.session_state:
    st.session_state.verrouille = False

# Variables d'état expérimentales et modes examen
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1
if "animation_active" not in st.session_state: st.session_state.animation_active = False
if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
        "Bleu de Thymol": { "ph_min": 1.2, "ph_max": 2.8,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FFEB3B", "nom_zone": "Jaune", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Hélianthine / Orange de méthyle": {"ph_min": 3.2, "ph_max": 4.4,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Vert de Bromocrésol": { "ph_min": 3.8, "ph_max": 5.4, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#8BC34A", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromophténol": { "ph_min": 3.0, "ph_max": 4.6, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#00BCD4", "nom_zone": "Vert-Bleu", "couleur_base": "#3F51B5", "nom_base": "Bleu violet" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },
        "Jaune d'Alizarin R": {"ph_min": 10.1, "ph_max": 12.0, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#F44336", "nom_base": "Rouge" }
    }

# =============================================================================
# FONCTIONS GLOBALES DE VALIDATION DE L'IDENTITÉ
# =============================================================================
def valider_saisie():
    """Vérifie les informations d'identification saisies par l'élève,

    les normalise en mémoire et verrouille définitivement le formulaire.
    """
    # Nettoyage et normalisation des textes saisis en session
    nom_clean = str(st.session_state.get("nom_var", "")).strip().upper()
    prenom_clean = str(st.session_state.get("prenom_var", "")).strip().capitalize()
    classe_clean = str(st.session_state.get("classe_var", "")).strip().upper()

    # Filtre de sécurité : empêche de valider si un champ est vide ou non modifié
    if not nom_clean or not prenom_clean or not classe_clean or nom_clean in ["NOM", "ELEVE", "INCONNU"]:
        st.error("Erreur : Veuillez compléter entièrement vos données d'identification avant de valider.")
        st.session_state.verrouille = False
    else:
        # Enregistrement des valeurs propres et verrouillage de la session
        st.session_state.nom_var = nom_clean
        st.session_state.prenom_var = prenom_clean
        st.session_state.classe_var = classe_clean
        st.session_state.verrouille = True
        
        st.success(f"Identification réussie pour : {nom_clean} {prenom_clean} ({classe_clean}).")


def valider_session():
    """Fonction passerelle de sécurité pour l'ouverture des droits d'ateliers."""
    valider_saisie()

# =============================================================================
# PRÉPARATION DU NOM DE FICHIER ET CONFIGURATION DES ONGLETS
# =============================================================================
def preparer_nom_fichier(nom_onglet):
    """Génère un nom de fichier standardisé et unique pour l'export des rapports."""
    from datetime import datetime

    # Récupération et formatage des chaînes sans espaces
    nom_propre = str(st.session_state.get("nom_var", "ELEVE")).replace(" ", "_")
    prenom_propre = str(st.session_state.get("prenom_var", "PRENOM")).replace(" ", "_")
    classe_propre = str(st.session_state.get("classe_var", "GROUPE")).replace(" ", "_")

    # Horodatage dynamique à la seconde près
    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    # Assemblage de la chaîne finale pour le téléchargement
    return f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"


# Déclaration officielle de la barre de navigation
# Les variables d'onglets sont liées à leurs index de liste respectifs
onglets = st.tabs([
    "Identification",
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]



def afficher_questions_titrage_dynamiques(df_donnees=None, verrouille=False):
    import numpy as np
    
    if "df_session_vin2" not in st.session_state or st.session_state.df_session_vin2 is None:
        return {}, {}
        
    v_pts = st.session_state.get("vin_vrai_total_points", 0.0)
    v_max = st.session_state.get("vin_vrai_ph_max", 0.0)
    v_min = st.session_state.get("vin_vrai_ph_min", 0.0)

    if v_pts == 0.0:
        v_pts, v_max, v_min = 12.0, 11.80, 2.90

    col_double_quiz_vin, col_double_trous_vin = st.columns(2)

    with col_double_quiz_vin:
        st.markdown("##### Quiz numerique sur VOTRE courbe de dosage (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{v_pts:.0f}", f"{v_pts + 3:.0f}", "5.0"]
        st.write("**1.** D'apres votre suivi experimental, combien de couples de points figurent sur votre trace ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_vin_q1", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_max:.2f}", f"{v_max + 1.2:.2f}", "14.00"]
        st.write("**2.** Quelle est la valeur maximale du pH atteinte en fin de courbe (exces de soude) ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_vin_q2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_min:.2f}", f"{v_min - 0.5:.2f}", "7.00"]
        st.write("**3.** Quelle est la valeur initiale du pH mesuree dans votre becher avant tout ajout (V=0) ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_vin_q3", disabled=verrouille, label_visibility="collapsed")

        opts_q4 = ["Choisir...", f"{round(float(v_max - v_min), 2):.2f}", f"{round(float(v_max - v_min) + 2, 2):.2f}", "4.00"]
        st.write("**4.** L'amplitude de pH totale relevee entre votre point final et votre point initial s'eleve a :")
        dict_reponses_quiz["q4"] = st.selectbox("", opts_q4, key="col_g_quiz_vin_q4", disabled=verrouille, label_visibility="collapsed")

        st.write("**5.** Quel indicateur colore parmi votre dictionnaire possede une zone de virage contenant le saut de pH ?")
        dict_reponses_quiz["q5"] = st.selectbox("", ["Choisir...", "Phenolphtaleine", "Helianthine", "Bleu de Thymol"], key="col_g_quiz_vin_q5", disabled=verrouille, label_visibility="collapsed")

        st.write("**6.** Lors du dosage de l'acide acetique (acide faible) par la soude, le milieu a l'equivalence est :")
        dict_reponses_quiz["q6"] = st.selectbox("", ["Choisir...", "Legerement basique (pH proche de 8.7)", "Neutre (pH egal a 7 pile)", "Acide"], key="col_g_quiz_vin_q6", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_vin:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Un repere orthonorme a deux axes orthogonaux est qualifie de")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Cartesien", "Polaire"], key="vin_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'axe horizontal d'un graphique porte le nom traditionnel d'")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Abscisses", "Ordonnees"], key="vin_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'axe vertical d'un graphique porte le nom traditionnel d'")
        with c4: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Ordonnees", "Abscisses"], key="vin_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. L'intersection geometrique initiale des deux reperes forme l'")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Origine", "Extremite"], key="vin_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La totalite des couples de points places sur le plan constitue un")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Nuage de points", "Histogramme"], key="vin_t5", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_vinaigre1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "vin_verrouille_tab1" not in st.session_state:
        return {}, {}

    # Initialisation et melange unique obligatoire de vos 7 questions d'origine + 3 completes
    if "ordre_quiz1" not in st.session_state:
        base_quiz1 = [
            {"id": "q1_1", "q": "La molecule du vinaigre est :", "type": "menu", "options": ["acide", "neutre", "basique"], "rep": "acide"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire du vinaigre en g/mol: ", "type": "menu", "options": ["60", "46", "18"], "rep": "60"},
            {"id": "q1_3", "q": "Quel est le nom chimique de la molecule du vinaigre ?", "type": "menu", "options": ["acide acetique", "acide methanoique", "acide chlorhydrique"], "rep": "acide acetique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atome de carbone que possede la molecule de vinaigre ?", "type": "menu", "options": ["2", "1", "4"], "rep": "2"},
            {"id": "q1_5", "q": "Quel est le nombre d'atome d'hydrohene que possede la molecule de vinaigre ?", "type": "menu", "options": ["4", "2", "6"], "rep": "4"},
            {"id": "q1_6", "q": "Quel est le nombre d'atome d''oxygene que possede la molecule de vinaigre ?", "type": "menu", "options": ["2", "1", "3"], "rep": "2"},
            {"id": "q1_7", "q": "Quelle est la formule brute de vinaigre ?", "type": "menu", "options": ["C4H2O2", "C2H4O2", "C2H2O4", "C2H2O2"], "rep": "C2H4O2"},
            {"id": "q1_8", "q": "D'apres la legende atomique, quelle est la masse molaire de l'element Carbone (C) ?", "type": "menu", "options": ["12 g/mol", "1 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "D'apres la legende atomique, quelle est la masse molaire de l'element Oxygene (O) ?", "type": "menu", "options": ["16 g/mol", "12 g/mol", "1 g/mol"], "rep": "16 g/mol"},
            {"id": "q1_10", "q": "D'apres la legende atomique, la sphere blanche represente l'atome d' :", "type": "menu", "options": ["Hydrogene (H)", "Carbone (C)", "Oxygene (O)"], "rep": "Hydrogene (H)"}
        ]
        # Sauvegarde du melange obligatoire en session
        copie_base = list(base_quiz1)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1 = copie_base

    col_double_quiz_v1, col_double_trous_v1 = st.columns(2)

    # --- COLONNE DE GAUCHE : L'ORDRE DES 10 QUESTIONS ME LANGÉES ---
    with col_double_quiz_v1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vin_cl_g_{q_data['id']}"
            
            # Melange local des options pour eviter l'ordre fixe des propositions
            cle_shuff_opts = f"opts_shuff_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = ["Choisir..."] + opts_copie
                
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_shuff_opts].index(val_p) if val_p in st.session_state[cle_shuff_opts] else 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", st.session_state[cle_shuff_opts], 
                index=sel_idx, key=cle_select, 
                disabled=verrouille, label_visibility="collapsed"
            )

    # --- COLONNE DE DROITE : LES 10 TROUS DE SYNTHÈSE ASSOCIES ---
    with col_double_trous_v1:
        st.markdown("##### Synthese des proprietes acido-basiques (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le vinaigre commercial est une solution aqueuse d'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Ethanoique", "Methanoique"], key="vin_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le groupe fonctionnel de cet acide organique est le groupe")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Carboxyle", "Hydroxyle"], key="vin_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'acide acetique appartient a la categorie des acides")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Faibles", "Forts"], key="vin_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Sa reaction de neutralisation lors d'un titrage est")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Totale", "Limitee"], key="vin_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le pKa du couple de l'acide acetique a 25°C vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "4.8", "7.0", "9.2"], key="vin_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'espece chimique titrante employee dans la burette est la")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Soude", "Acide"], key="vin_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Les ions sodium Na+ presents sont des ions qualifies de")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Spectateurs", "Actifs"], key="vin_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'unite internationale de la concentration molaire est")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "mol/L", "g/mol", "g/L"], key="vin_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le virage de couleur de l'indicateur signale l'")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Equivalence", "Dissociation"], key="vin_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide fait tendre sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7.0", "0.0", "14.0"], key="vin_t10_s1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous







def calculer_et_tracer_titrage_vinaigre(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez les couples (Volume de soude en mL ; pH mesure) pour tracer la courbe de titrage."
    
    st.session_state.vin_vrai_total_points = 0.0
    st.session_state.vin_vrai_ph_max = 0.0
    st.session_state.vin_vrai_ph_min = 0.0

    if df_donnees is None or "df_session_vin2" not in st.session_state or st.session_state.df_session_vin2 is None:
        ax.spines['bottom'].set_color('#94a3b8')
        ax.spines['left'].set_color('#94a3b8')
        ax.tick_params(colors='#94a3b8', labelsize=8)
        st.session_state.stats_vin_affichage_texte = stats_text
        return fig

    df_filtre = df_donnees.dropna(subset=["Volume NaOH (mL)", "pH mesure"])
    df_filtre = df_filtre[(df_filtre["Volume NaOH (mL)"].astype(str).str.strip() != "") & (df_filtre["pH mesure"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            df_numerique = df_filtre.copy()
            df_numerique["v_num"] = pd.to_numeric(df_numerique["Volume NaOH (mL)"], errors='coerce')
            df_numerique["ph_num"] = pd.to_numeric(df_numerique["pH mesure"], errors='coerce')
            df_numerique = df_numerique.dropna(subset=["v_num", "ph_num"])

            if not df_numerique.empty:
                df_triee = df_numerique.sort_values(by="v_num")
                vol_x = df_triee["v_num"].to_numpy()
                ph_y = df_triee["ph_num"].to_numpy()
                labels_x = df_triee["v_num"].astype(str).tolist()

                st.session_state.vin_vrai_total_points = float(len(ph_y))
                st.session_state.vin_vrai_ph_max = float(np.max(ph_y))
                st.session_state.vin_vrai_ph_min = float(np.min(ph_y))

                stats_text = (
                    f"Moyenne : {np.mean(ph_y):.2f}\n"
                    f"pH maximal : {st.session_state.vin_vrai_ph_max:.2f}\n"
                    f"pH minimal : {st.session_state.vin_vrai_ph_min:.2f}"
                )

                ax.plot(labels_x, ph_y, color="#38bdf8", marker="o", linestyle="-", lw=2, markersize=6, zorder=3)
                ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            else:
                stats_text = "Statistiques indisponibles pour caracteres textuels."
        except Exception:
            stats_text = "Statistiques indisponibles pour caracteres textuels."

    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Volume de base HO- verse V (mL)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("pH de la solution", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Courbe de titrage pH-metrique", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats_vin_affichage_texte = stats_text
    return fig
















with tab0:
    st.subheader("Identification de l'élève")
    st.write("Veuillez renseigner vos informations pour déverrouiller l'accès aux ateliers pratiques.")
    
    col_ident_1, col_ident_2 = st.columns(2)
    
    with col_ident_1:
        # Les champs de texte lisent et écrivent directement dans le Session State
        # Ils se bloquent automatiquement dès que le bouton OK a été cliqué
        nom_brut = st.text_input(
            "Nom de famille :",
            value=st.session_state.get("nom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_nom_maitre"
        )
        
        prenom_brut = st.text_input(
            "Prénom :",
            value=st.session_state.get("prenom_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_prenom_maitre"
        )
        
        classe_brut = st.text_input(
            "Groupe / Classe :",
            value=st.session_state.get("classe_var", ""),
            disabled=st.session_state.get("verrouille", False),
            key="widget_saisie_classe_maitre"
        )
        
        # Synchronisation et normalisation immédiate des chaînes de texte
        st.session_state.nom_var = nom_brut.strip().upper()
        st.session_state.prenom_var = prenom_brut.strip().capitalize()
        st.session_state.classe_var = classe_brut.strip().upper()
        
        st.write("")
        
        # Bouton maître de validation d'accès
        if st.button(
            "Valider mes informations (OK)", 
            key="btn_validation_identite_maitre",
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("verrouille", False):
                st.rerun()


with tab1:
    st.header("Atelier 1 : Generalites sur le vinaigre")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'etude")
        
        texte_document = (
            "Le vinaigre est une solution aqueuse composee majoritairement d'acide acetique. "
            "C'est un produit naturel et biodegradable issu de la biotransformation de l'alcool ethylique "
            "present dans les vins ou les cidres. La denomination vinaigre est reservee au produit obtenu "
            "exclusivement par le procede biologique de la double fermentation, alcoolique et acetique, "
            "de denrees et boissons d'origine agricole ou de leurs dilutions aqueuses (Decret n°88-1207 du 30 decembre 1988). "
            "Le degre d’acidite d’un vinaigre, indique sur la bouteille, represente l’acidite totale rapportee "
            "a la masse d’acide acetique exprimee en grammes pour 100 grammes de vinaigre."
        )
        st.info(texte_document)
        
        # Rendu graphique de la bouteille 2D via Matplotlib
        fig_bouteille, ax = plt.subplots(figsize=(4, 5.2), facecolor="#bae6fd")
        ax.set_facecolor("#bae6fd")
        
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#d0d8dc", ec="#b0bec5")
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7], [3.5, 7]], color="white", ec="#b0bec5")
        corps = patches.Rectangle((2.5, 1), 5, 6, color="white", ec="#b0bec5")
        etiquette = patches.Rectangle((2.7, 1.5), 4.6, 4, color="#008040")
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#0033cc")
        
        ax.add_patch(patches.Circle((5, 1), 2.5, color="white", ec="white"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#e2e8f0", linewidth=1)
            
        ax.text(5, 5.0, "VINAIGRE", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.5, "D'ALCOOL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "CRISTAL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 3.0, "Eco", color="white", weight="bold", fontsize=12, ha="center")
        ax.text(5, 2.5, "+", color="#ffcc00", weight="bold", fontsize=14, ha="center")
        ax.text(3.3, 2.0, "8°", color="white", weight="bold", fontsize=11, ha="center")
        ax.text(6.7, 2.0, "1 L", color="white", weight="bold", fontsize=11, ha="center")
        
        ax.set_xlim(1, 9)
        ax.set_ylim(0, 10)
        ax.axis("off")
        st.pyplot(fig_bouteille)

    # --------------------------------------------------------
    # COLONNE DROITE : LES DONNÉES ATOMIQUES ET LA MOLÉCULE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Donnees et Legendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogene (H)**\n\nSphere blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphere noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygene (O)**\n\nSphere rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        c_methyl = np.array([2.8, 2.5])
        c_carboxy = np.array([4.2, 2.5])
        double_o = np.array([4.6, 3.4])
        oh_o = np.array([5.1, 1.9])
        oh_h = np.array([5.9, 1.7])
        h1_m = np.array([2.3, 3.5])
        h2_m = np.array([2.3, 1.5])
        h3_m = np.array([3.2, 3.6])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        tracer_liaison(c_methyl, c_carboxy)
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_o)
        tracer_liaison(oh_o, oh_h)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O': couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black"
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        tracer_atome(c_methyl, 'C')
        tracer_atome(c_carboxy, 'C')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_o, 'O')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')
        tracer_atome(oh_h, 'H')

        ax_mol.set_xlim(1.5, 6.5)
        ax_mol.set_ylim(1.0, 4.2)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES
    # =========================================================================
    res_q1, res_t1 = afficher_questions_vinaigre1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 1.", 
        key="check_certif_vin1", 
        disabled=st.session_state.vin_verrouille_tab1
    )

    if st.button("VALIDER AND EXPORTER LE BILAN DE L'ATELIER 1", key="btn_validation_vin1", use_container_width=True, disabled=st.session_state.vin_verrouille_tab1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if st.session_state.get("vin_q1_s1") == "Acide ethanoique": score_q1 += 1.0
            if st.session_state.get("vin_q2_s1") == "CH3COOH": score_q1 += 1.0
            if st.session_state.get("vin_q3_s1") == "CH3COO-": score_q1 += 1.0
            if st.session_state.get("vin_q4_s1") == "60 g/mol": score_q1 += 1.0
            if st.session_state.get("vin_q5_s1") == "Ceder un ou plusieurs protons H+": score_q1 += 1.0
            if st.session_state.get("vin_q6_s1") == "Totale et rapide": score_q1 += 1.0
            if st.session_state.get("vin_q7_s1") == "Entre 2 et 3": score_q1 += 1.0
            if st.session_state.get("vin_q8_s1") == "La masse en grammes d'acide pur dans 100g de vinaigre": score_q1 += 1.0
            if st.session_state.get("vin_q9_s1") == "Blouse, lunettes de protection et gants": score_q1 += 1.0
            if st.session_state.get("vin_q10_s1") == "Une pipette jaugee": score_q1 += 1.0

            score_t1 = 0.0
            if st.session_state.get("vin_t1_s1") == "Ethanoique": score_t1 += 1.0
            if st.session_state.get("vin_t2_s1") == "Carboxyle": score_t1 += 1.0
            if st.session_state.get("vin_t3_s1") == "Faibles": score_t1 += 1.0
            if st.session_state.get("vin_t4_s1") == "Totale": score_t1 += 1.0
            if st.session_state.get("vin_t5_s1") == "4.8": score_t1 += 1.0
            if st.session_state.get("vin_t6_s1") == "Soude": score_t1 += 1.0
            if st.session_state.get("vin_t7_s1") == "Reaction": score_t1 += 1.0
            if st.session_state.get("vin_t8_s1") == "mol/L": score_t1 += 1.0
            if st.session_state.get("vin_t9_s1") == "Equivalence": score_t1 += 1.0
            if st.session_state.get("vin_t10_s1") == "Augmente": score_t1 += 1.0

            st.session_state.score_vin1_p1 = round(score_q1, 1)
            st.session_state.score_vin1_p2 = round(score_t1, 1)
            st.session_state.score_final_vin1 = round(score_q1 + score_t1, 1)
            st.session_state.vin_verrouille_tab1 = True
            
            st.rerun()

    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VINAIGRE 1 SCELLE | Note de session : {tot_s} / 20")

        html_export_vin1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                
                /* RÉPARATION COULEUR : Passage du vert au bleu nuit officiel */
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier : Generalites sur le vinaigre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Nomenclature et Proprietes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
                &bull; Partie 1 : Quiz de validation nomenclature (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours acido-basique (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ THEORIQUE MOLECULAIRE</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question Posee</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 20%; text-align: center;">Attendu Academique</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Generation dynamique des en-tetes de questions issus de votre dictionnaire ordonne de session
        for idx, q_data in enumerate(st.session_state.ordre_quiz1, 1):
            saisie = st.session_state.get(f"vin_cl_g_{q_data['id']}", "Choisir...")
            attendu = q_data["rep"]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin1 += f"""<tr>
                <td>{idx}</td>
                <td>{q_data['q']}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{attendu}</td>
                <td class='{v_class}' style='text-align:center;'>{v_lbl}</td>
            </tr>"""

        html_export_vin1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Phrase a trous completee</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 20%; text-align: center;">Attendu Academique</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # En-têtes textuels des phrases à trous correspondantes pour l'affichage integral dans le tableau
        phrases_trous1 = [
            ("1. Le vinaigre commercial est une solution aqueuse d'acide...", "Ethanoique"),
            ("2. Le groupe fonctionnel de cet acide organique est le groupe...", "Carboxyle"),
            ("3. L'acide acetique appartient a la categorie des acides...", "Faibles"),
            ("4. Sa reaction de neutralisation lors d'un titrage est...", "Totale"),
            ("5. Le pKa du couple de l'acide acetique a 25°C vaut...", "4.8"),
            ("6. L'espece chimique titrante employee dans la burette est la...", "Soude"),
            ("7. Les ions sodium Na+ presents sont des ions qualifies de...", "Spectateurs"),
            ("8. L'unite internationale de la concentration molaire est...", "mol/L"),
            ("9. Le virage de couleur de l'indicateur signale l'...", "Equivalence"),
            ("10. Diluer une solution acide fait tendre sa valeur de pH vers...", "7.0")
        ]

        for i, (phrase, tv) in enumerate(phrases_trous1, 1):
            saisie = st.session_state.get(f"vin_t{i}_s1", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin1 += f"""<tr>
                <td>{i}</td>
                <td>{phrase}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{tv}</td>
                <td class='{v_class}' style='text-align:center;'>{v_lbl}</td>
            </tr>"""

        html_export_vin1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse chimique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Evaluation_Vinaigre1_{n_eleve}_{p_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f1 = nom_f1.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_vin1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Dosage colorimetrique du vinaigre")
    st.caption("Simulation interactive et animee goutte-a-goutte du titrage de l'acide acetique par la soude")

    # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base" not in st.session_state: st.session_state.c_base = 0.1
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(80.0, 90.0) / 1000.0

    # Constantes physico-chimiques fixes du modele
    pKa = 4.17
    M_vinaigre = 60.0
    V_ini = 10.0
    v_max_ml = 25.0
    C_base = st.session_state.c_base
    n_acide_ini = st.session_state.masse_reelle_g / M_vinaigre

    # Calcul exact des reperes d'equivalence de la session
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Parametres de la solution titrante et du goutte-a-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.session_state.c_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :", 
                min_value=0.01, max_value=2.0, value=st.session_state.c_base, step=0.01,
                disabled=st.session_state.vin_verrouille_tab2
            )
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :", 
                min_value=0.1, max_value=2.0, value=st.session_state.pas_ml, step=0.1,
                disabled=st.session_state.vin_verrouille_tab2
            )
        with col_p3:
            liste_indicateurs = list(st.session_state.indicateurs.keys())
            choix_ind = st.selectbox(
                "Selectionner un indicateur colore :", 
                options=liste_indicateurs, index=0,
                disabled=st.session_state.vin_verrouille_tab2
            )

    st.info(f"Compose : Vinaigre | Masse pesee (aleatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()

    # Algorithme mathematique pour generer les courbes
    def extraire_ph_calcul_tp(v_b_ml):
        v_b = v_b_ml / 1000.0
        v_a_total = V_ini / 1000.0
        n_b = v_b * C_base
        v_tot = v_a_total + v_b
        if v_tot <= 0 or n_acide_ini <= 0: return 1.0
        if n_b < n_acide_ini:
            if n_b == 0:
                c_acide_ini = n_acide_ini / v_a_total
                return max(1.0, 0.5 * (pKa - math.log10(c_acide_ini)))
            ratio = n_b / n_acide_ini
            return max(1.0, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
        else:
            ratio = n_b / n_acide_ini
            if ratio == 1.0: return ph_eq_theorique
            return min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    import numpy as np
    volumes_simules = np.arange(0, v_max_ml + 0.1, 0.1)
    phs_simules = [extraire_ph_calcul_tp(v) for v in volumes_simules]

    # --- BARRE DE COMMANDE DE L'ANIMATION DU TP ---
    st.subheader("Ajout progressif de la solution titrante")
    col_b1, col_b2, col_sl = st.columns([1.1, 0.9, 2.0], vertical_alignment="bottom")
    
    with col_b1:
        activer_flux = st.button("Demarrer le versement automatique", key="btn_run_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2)
    with col_b2:
        if st.button("Effacer tout", key="btn_clear_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2):
            st.session_state.v_verse = 0.0
            st.session_state.animation_active = False
            st.rerun()
    with col_sl:
        v_manuel = st.slider("Volume de soude total verse V_B (mL) :", min_value=0.0, max_value=v_max_ml, value=float(st.session_state.v_verse), step=0.1, disabled=st.session_state.vin_verrouille_tab2)
        if not activer_flux: st.session_state.v_verse = float(v_manuel)

    if activer_flux: st.session_state.animation_active = True

    if st.session_state.get("animation_active", False):
        import time
        if st.session_state.v_verse < v_max_ml:
            st.session_state.v_verse = round(min(v_max_ml, st.session_state.v_verse + st.session_state.pas_ml), 1)
            time.sleep(0.04)
            st.rerun()
        else:
            st.session_state.animation_active = False
            st.rerun()

    idx_actuel = min(int(round(st.session_state.v_verse * 10)), len(volumes_simules) - 1)
    ph_actuel = phs_simules[idx_actuel]

    # Memorisation pour la correction en pied de page
    st.session_state.vin_vrai_ph_final = float(ph_actuel)
    st.session_state.vin_vrai_veq_calc = float(v_eq_theorique)

    # --- MISE EN PAGE : SCHEMA DU MONTAGE ANIMÉ ET GRAPHIQUE PROGRESSIF ---
    col_visuel, col_graph = st.columns([1, 1.2])

    ind_data = st.session_state.indicateurs[choix_ind]
    if ph_actuel < ind_data["ph_min"]:
        couleur_solution = ind_data["couleur_acide"]
        nom_zone_teinte = ind_data["nom_acide"]
    elif ph_actuel > ind_data["ph_max"]:
        couleur_solution = ind_data["couleur_base"]
        nom_zone_teinte = ind_data["nom_base"]
    else:
        couleur_solution = ind_data["couleur_zone"]
        nom_zone_teinte = ind_data["nom_zone"]

    with col_visuel:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig_montage, ax_mo = plt.subplots(figsize=(4, 4.6), facecolor="white")
        ax_mo.set_facecolor("white")
        
        ax_mo.add_patch(patches.Rectangle((1.0, 0.5), 0.3, 9.0, color="#7f8c8d"))
        ax_mo.add_patch(patches.Rectangle((1.3, 8.0), 3.2, 0.15, color="#95a5a6"))
        
        hauteur_b = 3.5 * (1.0 - (st.session_state.v_verse / v_max_ml))
        ax_mo.add_patch(patches.Rectangle((3.6, 4.5), 0.6, 4.0, facecolor="none", edgecolor="#34495e", linewidth=2))
        ax_mo.add_patch(patches.Rectangle((3.62, 4.52), 0.56, hauteur_b, facecolor="#aed6f1", alpha=0.8))
        ax_mo.add_patch(patches.Rectangle((3.8, 4.1), 0.2, 0.4, color="#2c3e50"))
        
        if st.session_state.get("animation_active", False) and st.session_state.v_verse > 0:
            ax_mo.add_patch(patches.Circle((3.9, 3.7), 0.08, color="#aed6f1"))
        
        hauteur_liquide_becher = 1.0 + 1.2 * (st.session_state.v_verse / v_max_ml)
        ax_mo.add_patch(patches.Polygon([[2.6, 1.0], [2.6, 3.2], [4.8, 3.2], [4.8, 1.0]], facecolor="none", edgecolor="#34495e", linewidth=3))
        ax_mo.add_patch(patches.Rectangle((2.65, 1.05), 2.1, hauteur_liquide_becher, facecolor=couleur_solution, alpha=0.75))
        
        ax_mo.add_patch(patches.Rectangle((2.2, 0.3), 3.0, 0.7, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2))
        angle_barreau = 8 if idx_actuel % 2 == 0 else -8
        ax_mo.add_patch(patches.Rectangle((3.1, 1.1), 1.2, 0.15, facecolor="#ffffff", edgecolor="#7f8c8d", angle=angle_barreau))
        
        ax_mo.add_patch(patches.Rectangle((4.3, 1.6), 0.3, 3.0, color="#34495e"))
        ax_mo.plot([4.45, 4.45, 5.5], [4.6, 7.5, 7.5], color="#34495e", linewidth=2)
        ax_mo.add_patch(patches.Rectangle((5.5, 6.5), 2.2, 1.5, facecolor="#2c3e50", edgecolor="#1a252f", linewidth=2))
        ax_mo.text(6.6, 7.2, f"pH: {ph_actuel:.2f}", color="#2ecc71", fontfamily="monospace", weight="bold", fontsize=11, ha="center")
        ax_mo.text(3.7, 0.05, f"Teinte : {nom_zone_teinte}", color="#1e293b", fontsize=9, ha="center")
        
        ax_mo.set_xlim(0.5, 8.0)
        ax_mo.set_ylim(0.0, 9.5)
        ax_mo.axis("off")
        st.pyplot(fig_montage)

    with col_graph:
        st.write("**Courbe de pH-metrie associee**")
        activer_tangentes = st.checkbox("Afficher la Methode des tangentes", key="chk_tangentes")
        activer_derivee = st.checkbox("Afficher la Methode de la deivee seconde", key="chk_derivee")
            
        fig_curve, ax_cr = plt.subplots(figsize=(6, 4.8))
        ax_cr.plot(volumes_simules[:idx_actuel+1], phs_simules[:idx_actuel+1], color="black", linewidth=2.0)
        ax_cr.scatter([st.session_state.v_verse], [ph_actuel], color="red", s=60, zorder=5)
        
        if activer_tangentes:
            v_np = np.array(volumes_simules)
            ph_np = np.array(phs_simules)
            
            # Recherche des segments lineaires stables avant et apres la forte courbure
            idx_avant = np.where(v_np <= max(0.5, v_eq_theorique - 4.0))[0]
            idx_apres = np.where((v_np >= min(v_max_ml, v_eq_theorique + 4.0)) & (v_np <= v_max_ml - 1.0))[0]
            
            if len(idx_avant) > 1 and len(idx_apres) > 1:
                # Interpolation lineaire pour trouver les pentes paralleles
                p1 = np.polyfit(v_np[idx_avant[-4:]], ph_np[idx_avant[-4:]], 1)
                p2 = np.polyfit(v_np[idx_apres[:4]], ph_np[idx_apres[:4]], 1)
                
                # Calcul d'une pente moyenne commune pour garantir le parallelisme parfait
                pente_commune = (p1[0] + p2[0]) / 2.0
                
                # Ajustement des ordonnees a l'origine pour caler les droites sur la courbe
                b1 = ph_np[idx_avant[-1]] - pente_commune * v_np[idx_avant[-1]]
                b2 = ph_np[idx_apres[0]] - pente_commune * v_np[idx_apres[0]]
                b_mediane = (b1 + b2) / 2.0
                
                v_trace = np.linspace(0, v_max_ml, 200)
                tangente_inf = pente_commune * v_trace + b1
                tangente_sup = pente_commune * v_trace + b2
                droite_mediane = pente_commune * v_trace + b_mediane
                
                # Tracé des trois lignes paralleles noires continues
                ax_cr.plot(v_trace, tangente_inf, color="black", linestyle="-", lw=1.0, alpha=0.8, label="Tangente inf")
                ax_cr.plot(v_trace, tangente_sup, color="black", linestyle="-", lw=1.0, alpha=0.8, label="Tangente sup")
                ax_cr.plot(v_trace, droite_mediane, color="black", linestyle="-", lw=1.2, label="Droite mediane")
                
                # Point de croisement geometrique final (croix bleue au centre)

                ax_cr.scatter([v_eq_theorique], [ph_eq_theorique], color="blue", marker="+", s=180, linewidths=2.5, zorder=6)

        if activer_derivee and idx_actuel > 2:
            ax_deriv = ax_cr.twinx()
            ax_deriv.plot(volumes_simules[1:idx_actuel+1], np.diff(phs_simules[:idx_actuel+1])/0.1, color="red", alpha=0.5)
            ax_cr.scatter([v_eq_theorique], [ph_eq_theorique], color="red", marker="+", s=180, linewidths=2.5, zorder=6)

        ax_cr.set_xlim(0, v_max_ml + 1)
        ax_cr.set_ylim(0, 14)
        ax_cr.grid(True, linestyle=":")
        st.pyplot(fig_curve)

    # --- TABLEAU DE SUIVI HORIZONTAL AVEC TEXTE ---
    st.write("---")
    st.subheader("Tableau de suivi (3 lignes - Colonnes multiples)")
    matrice_colonnes = {}
    for idx in range(idx_actuel + 1):
        v_pt = volumes_simules[idx]
        ph_pt = phs_simules[idx]
        if ph_pt < ind_data["ph_min"]: obs = f"{ind_data['nom_acide']}"
        elif ph_pt > ind_data["ph_max"]: obs = f"{ind_data['nom_base']}"
        else: obs = f"{ind_data['nom_zone']}"

        # RECOUPLAGE ET ALIGNEMENT STRICT DE LA MATRICE DU TABLEAU HORIZONTAL
        matrice_colonnes[f"Goutte {idx}"] = {
            "Soude versee V_B (mL)": f"{v_pt:.1f}", 
            "pH mesure": f"{ph_pt:.2f}", 
            "Observations / Teinte": obs
        }

    if matrice_colonnes:
        import pandas as pd
        st.dataframe(pd.DataFrame.from_dict(matrice_colonnes, orient="index").T, use_container_width=True)

    if st.button("Reinitialiser la simulation / Changer de flacon", key="btn_reset_tab2_final", use_container_width=True):
        st.session_state.masse_reelle_g = random.uniform(80.0, 90.0) / 1000.0
        st.session_state.v_verse = 0.0
        st.session_state.animation_active = False
        st.rerun()

    # --- ZONE D'EVALUATION DU FORMULAIRE ATELIER 2 ---
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 2")
    col_g_q2, col_d_t2 = st.columns(2)
    
    with col_g_q2:
        st.markdown("##### Quiz sur VOTRE suivi de dosage (10 questions - 10 pts)")
        st.write("**1.** Quel est l'indicateur colore actif sur votre paillasse ?")
        st.selectbox("", ["Choisir...", choix_ind, "Autre"], key="vin_q1_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")
            

        
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 2")

    col_g_q2, col_d_t2 = st.columns(2)

    # REPARATION ABSOLUE : Re-extraction locale de securite pour synchroniser le Quiz de bas de page
    ind_data = st.session_state.indicateurs[choix_ind]

    with col_g_q2:
        st.markdown("##### Quiz sur VOTRE suivi de dosage (10 questions - 10 pts)")
        dict_reponses_quiz2 = {}
        
        opts_q1 = ["Choisir...", choix_ind, "Autre"]
        st.write("**1.** Quel est l'indicateur colore actif sur votre paillasse ?")
        dict_reponses_quiz2["q1"] = st.selectbox("", opts_q1, key="vin_q1_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")
        opts_q2 = ["Choisir...", ind_data["nom_acide"], "Rose"]
        st.write("**2.** Quelle est la coloration de la solution dans la zone acide ?")
        dict_reponses_quiz2["q2"] = st.selectbox("", opts_q2, key="vin_q2_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")
        
        opts_q3 = ["Choisir...", ind_data["nom_base"], "Jaune"]
        st.write("**3.** Quelle est la coloration finale de la solution dans la zone alcaline ?")
        dict_reponses_quiz2["q3"] = st.selectbox("", opts_q3, key="vin_q3_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")
        
        opts_q4 = ["Choisir...", f"{ind_data['ph_min']:.1f}", "7.0"]
        st.write("**4.** Quel est le pH minimal de la zone de transition de cet indicateur ?")
        dict_reponses_quiz2["q4"] = st.selectbox("", opts_q4, key="vin_q4_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")
        
        opts_q5 = ["Choisir...", f"{ind_data['ph_max']:.1f}", "14.0"]
        st.write("**5.** Quel est le pH maximal de la zone de transition de cet indicateur ?")
        dict_reponses_quiz2["q5"] = st.selectbox("", opts_q5, key="vin_q5_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        ph_boitier_securise = st.session_state.get("vin_vrai_ph_final", 2.90)
        opts_q6 = ["Choisir...", f"{ph_boitier_securise:.2f}", "7.00"]
        st.write("**6.** Quelle est la valeur exacte du pH affichee actuellement sur votre boitier ?")
        dict_reponses_quiz2["q6"] = st.selectbox("", opts_q6, key="vin_q6_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        # SUITE DIRECTE ET CALÉE DE L'EVALUATION DE L'ATELIER 2
        st.write("***7.** Quelle espece chimique est majoritaire dans le becher a pH = 2.0 ?")
        dict_reponses_quiz2["q7"] = st.selectbox("", ["Choisir...", "L'acide CH3COOH", "La base CH3COO-"], key="vin_q7_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        st.write("***8.** Quelle espece chimique est majoritaire dans le becher a pH = 12.0 ?")
        dict_reponses_quiz2["q8"] = st.selectbox("", ["Choisir...", "La base CH3COO-", "L'acide CH3COOH"], key="vin_q8_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        st.write("***9.** Le virage de couleur de la phenolphtaleine est ideal pour reperer l'equivalence de ce titrage car :")
        dict_reponses_quiz2["q9"] = st.selectbox("", ["Choisir...", "Sa zone de virage inclut le pH a l'equivalence", "Sa zone de virage inclut le pKa initial"], key="vin_q9_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        st.write("***10.** Au point d'equivalence du dosage, les reactifs sont introduits en proportions :")
        dict_reponses_quiz2["q10"] = st.selectbox("", ["Choisir...", "Stoechiometriques", "Inverses"], key="vin_q10_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

    with col_d_t2:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee contenant la solution titrante est la")
        with c2: t1 = st.selectbox("", ["Choisir...", "Burette", "Pipette"], key="vin_t1_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le becher repose sur un appareil assurant l'homogeneite nommé")
        with c4: t2 = st.selectbox("", ["Choisir...", "Agitateur magnetique", "Chauffe-ballon"], key="vin_t2_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La solution de concentration connue utilisee pour doser est dite")
        with c6: t3 = st.selectbox("", ["Choisir...", "Titrante", "Titree"], key="vin_t3_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La solution de vinaigre placee dans le becher est dite solution")
        with c8: t4 = st.selectbox("", ["Choisir...", "Titree", "Titrante"], key="vin_t4_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le pH theorique obtenu a l'equivalence vaut approximativement")
        with c10: t5 = st.selectbox("", ["Choisir...", "8.7", "7.0", "4.8"], key="vin_t5_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le volume equivalent theorique calcule de votre session vaut")
        with c12: t6 = st.selectbox("", ["Choisir...", f"{v_eq_theorique:.1f} mL", "10.0 mL"], key="vin_t6_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La portion de courbe ou la variation verticale est maximale est le")
        with c14: t7 = st.selectbox("", ["Choisir...", "Saut de pH", "Palier"], key="vin_t7_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Lorsque le pH est egal au pKa, les proportions de l'acide et de la base sont")
        with c16: t8 = st.selectbox("", ["Choisir...", "Egales", "Inverses"], key="vin_t8_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'ion hydroxyle HO- de la soude se comporte comme une base")
        with c18: t9 = st.selectbox("", ["Choisir...", "Forte", "Faible"], key="vin_t9_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. L'indicateur ideal presente une zone de virage incluant le")
        with c20: t10 = st.selectbox("", ["Choisir...", "pH a l'equivalence", "pKa"], key="vin_t10_s2", disabled=st.session_state.vin_verrouille_tab2, label_visibility="collapsed")

    C_base = st.session_state.c_base if "c_base" in st.session_state else 0.1
    V_ini = 10.0
    M_vinaigre = 60.0
    pKa = 4.17
    v_max_ml = 25.0

    # Quantite et concentration initiale calcules sur la masse reelle
    n_acide_total = st.session_state.masse_reelle_g / M_vinaigre
    c_titre = n_acide_total / (V_ini / 1000.0) if V_ini > 0 else 0.0

    # STRUCTURATION SÉCURISÉE ET FERMETURE PROPRE DE LA SYNTAXE
    if V_ini <= 0 or c_titre <= 0 or C_base <= 0:
        st.error("Erreur de configurations physico-chimiques : Verifiez la concentration de la base.")
    else:
        veq_theorique_mL = (c_titre * V_ini) / C_base

        
        # RÉPARATION VARIABLES : Utilisation de phs_simules (avec un s)
        idx_actuel = min(int(round(st.session_state.v_verse * 10)), len(volumes_simules) - 1)

        # Sauvegarde des grandeurs critiques pour l'evaluation et l'export HTML
        st.session_state.vin_vrai_total_points = float(idx_actuel + 1)
        st.session_state.vin_vrai_ph_max = float(np.max(phs_simules))
        st.session_state.vin_vrai_ph_min = float(np.min(phs_simules))
        
      # =========================================================================
    st.write("---")
    st.subheader("Formulaire d'evaluation numerique - Atelier 2")

    # Appel permanent du double formulaire visuel (10 quiz / 10 trous)
    res_q2, res_t2 = afficher_questions_titrage_dynamiques(
        st.session_state.get("df_session_vin2", None), 
        verrouille=st.session_state.get("vin_verrouille_tab2", False)
    )

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 2.", 
        key="check_certif_vin2", 
        disabled=st.session_state.get("vin_verrouille_tab2", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_vin2_official", use_container_width=True, disabled=st.session_state.get("vin_verrouille_tab2", False)):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            v_pts = st.session_state.get("vin_vrai_total_points", 0.0)
            v_max = st.session_state.get("vin_vrai_ph_max", 0.0)
            v_min = st.session_state.get("vin_vrai_ph_min", 0.0)
            v_eq_c = st.session_state.get("vin_vrai_veq_calc", 0.0)

            # 1. Correction automatique du Quiz adaptatif (10 questions x 1.0 pt)
            score_q2 = 0.0
            if st.session_state.get("col_g_quiz_vin_q1") == f"{v_pts:.0f}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q2") == f"{v_max:.2f}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q3") == f"{v_min:.2f}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q4") == f"{round(float(v_max - v_min), 2):.2f}": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q5") == "Phenolphtaleine": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q6") == "Legerement basique (pH proche de 8.7)": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q7") == "pH = pKa de l'acide faible (4.8)": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q8") == "Saut de pH": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q9") == "D'assurer l'electroneutralite de la solution": score_q2 += 1.0
            if st.session_state.get("col_g_quiz_vin_q10") == "Protons H+": score_q2 += 1.0

            # 2. Correction automatique des 10 Selecteurs du cours (10 trous x 1.0 pt)
            score_t2 = 0.0
            if st.session_state.get("vin_t1") == "Cartesien": score_t2 += 1.0
            if st.session_state.get("vin_t2") == "Abscisses": score_t2 += 1.0
            if st.session_state.get("vin_t3") == "Ordonnees": score_t2 += 1.0
            if st.session_state.get("vin_t4") == "Origine": score_t2 += 1.0
            if st.session_state.get("vin_t5") == "Nuage de points": score_t2 += 1.0
            if st.session_state.get("vin_t6") == "Brisee": score_t2 += 1.0
            if st.session_state.get("vin_t7") == "Croissante": score_t2 += 1.0
            if st.session_state.get("vin_t8") == "Equivalence": score_t2 += 1.0
            if st.session_state.get("vin_t9") == "Abscisse": score_t2 += 1.0
            if st.session_state.get("vin_t10") == "Quantitatifs": score_t2 += 1.0

            st.session_state.score_vin2_p1 = round(score_q2, 1)
            st.session_state.score_vin2_p2 = round(score_t2, 1)
            st.session_state.score_final_vin2 = round(score_q2 + score_t2, 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # GENERATEUR DU DOCUMENT HTML BLEU NUITE APRES LE SCELLE
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        v_pts = st.session_state.get("vin_vrai_total_points", 0.0)
        v_max = st.session_state.get("vin_vrai_ph_max", 0.0)
        v_min = st.session_state.get("vin_vrai_ph_min", 0.0)
        v_eq_c = st.session_state.get("vin_vrai_veq_calc", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VINAIGRE 2 SCELLE | Note de session : {tot_s} / 20")

        html_export_vin2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 2 : Dosage colorimetrique du vinaigre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif de session - Dosage Potentiometrique</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Partie 1 : Quiz de validation experimental (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours montage (10 trous) : <strong>{scr2} / 10</strong>
            </p>
            <div class="sub-title">VERIFICATION DES GRANDEURS EXPERIMENTALES CALCULÉES :</div>
            <table>
                <thead>
                    <tr><th>Indicateur pH-metrique</th><th>Valeur Unique Calculee</th></tr>
                </thead>
                <tbody>
                    <tr><td>Nombre de points synchronises sur le trace</td><td>{v_pts:.0f}</td></tr>
                    <tr><td>pH maximum atteint (exces de base)</td><td>{v_max:.2f}</td></tr>
                    <tr><td>pH initial mesuré (V=0)</td><td>{v_min:.2f}</td></tr>
                    <tr><td>Volume d'equivalence theorique de la solution (mL)</td><td>{v_eq_c:.2f} mL</td></tr>
                </tbody>
            </table>
            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ COMPLÉTE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th style='text-align:center;'>Saisie Eleve</th><th style='text-align:center;'>Attendu Technique Unique</th><th style='text-align:center;'>Verdict</th></tr>
                </thead>
                <tbody>
        """

        attendus_quiz2 = [
            f"{v_pts:.0f}", f"{v_max:.2f}", f"{v_min:.2f}", f"{round(float(v_max - v_min), 2):.2f}",
            "Phenolphtaleine", "Legerement basique (pH proche de 8.7)", "pH = pKa de l'acide faible (4.8)", "Saut de pH",
            "D'assurer l'electroneutralite de la solution", "Protons H+"
        ]
        questions_text2 = [
            "1. D'apres votre suivi experimental, combien de couples de points figurent sur votre trace ?",
            "2. Quelle est la valeur maximale du pH atteinte en fin de courbe (exces de soude) ?",
            "3. Quelle est la valeur initiale du pH mesuree dans votre becher avant tout ajout (V=0) ?",
            "4. L'amplitude de pH totale relevee entre votre point final et votre point initial s'eleve a :",
            "5. Quel indicateur colore parmi votre dictionnaire possede une zone de virage contenant le saut de pH ?",
            "6. Lors du dosage de l'acide acetique (acide faible) par la soude, le milieu a l'equivalence is :",
            "7. A la demi-equivalence (lorsque le volume verse vaut Ve / 2), le pH de la solution verifie :",
            "8. La brutale variation verticale du pH observee graphiquement autour de l'equivalence s'appelle le :",
            "9. Les ions spectateurs sodium Na+ presents dans le becher ont pour role :",
            "10. La reaction de dosage acido-basique mise en oeuvre est un transfert de :"
        ]
        for i in range(1, 11):
            saisie = st.session_state.get(f"vin_q{i}_s2", "Choisir...")
            attendu = attendus_quiz2[i-1]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin2 += f"<tr><td>{i}</td><td>{questions_text2[i-1]}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_vin2 += """
                </tbody>
            </table>
            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase a trous completee</th><th style='text-align:center;'>Saisie Eleve</th><th style='text-align:center;'>Attendu Academique</th><th style='text-align:center;'>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            ("1. La verrerie graduee contenant la solution titrante est la...", "Burette"),
            ("2. Le becher repose sur un appareil assurant l'homogeneite nommé...", "Agitateur magnetique"),
            ("3. La solution de concentration connue utilisee pour doser est dite...", "Titrante"),
            ("4. La solution de vinaigre placee dans le becher is dite solution...", "Titree"),
            ("5. Le pH theorique obtenu a l'equivalence vaut approximativement...", "8.7"),
            ("6. Le volume equivalent theorique calcule de votre session vaut...", f"{v_eq_c:.1f} mL"),
            ("7. La portion de courbe ou la variation verticale est maximale est le...", "Saut de pH"),
            ("8. Lorsque le pH est egal au pKa, les proportions de l'acide et de la base sont...", "Egales"),
            ("9. L'ion hydroxyle HO- de la soude se comporte comme une base...", "Forte"),
            ("10. L'indicateur ideal presente une zone de virage incluant le...", "pH a l'equivalence")
        ]
        for i, (phrase, tv) in enumerate(phrases_trous2, 1):
            saisie = st.session_state.get(f"vin_t{i}_s2", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin2 += f"<tr><td>{i}</td><td>{phrase}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{tv}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_vin2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse chimique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Evaluation_Vinaigre2_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f2 = nom_f2.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_vin2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )
