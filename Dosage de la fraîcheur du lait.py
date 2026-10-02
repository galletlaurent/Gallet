# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage de la fraîcheur du lait",
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
st.title("Application dosage de la fraîcheur du lait")
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
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.05
if "animation_active" not in st.session_state: st.session_state.animation_active = False
if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },

    }


def draw_burette(ax, v_verse, v_max, animation_active, tick, pas_goutte):
    """Dessine la burette graduée épurée et la goutte en chute libre (Fidèle à Tkinter)."""
    # Corps transparent de la burette
    ax.add_patch(patches.Rectangle((3.2, 4.4), 0.25, 4.2, facecolor="#ecf0f1", edgecolor="#34495e", linewidth=1.5)) 
    
    # Remplissage de la solution titrante (se vide dynamiquement)
    hauteur_b = 4.1 * (1.0 - (v_verse / v_max))
    ax.add_patch(patches.Rectangle((3.22, 4.42), 0.21, hauteur_b, facecolor="#aed6f1", alpha=0.9)) 
    
    # Graduations de la burette (Boucle for identique à votre logique)
    for y_g in np.linspace(4.6, 8.4, 10):
        ax.plot([3.2, 3.28], [y_g, y_g], color="#34495e", linewidth=0.8)
    
    # Robinet et pointe de la burette
    ax.add_patch(patches.Rectangle((3.3, 4.05), 0.05, 0.35, color="#2c3e50")) 
    
    # Animation de la goutte d'eau (Chute alternée basée sur le tick)
    if animation_active:
        y_goutte = 3.9 if (tick % 2 == 0) else 2.5
        ax.add_patch(patches.Circle((3.32, y_goutte), 0.05, color="#aed6f1"))


def draw_becher(ax, v_verse, v_max, couleur_sol, tick, ph_actuel):
    """Dessine le bécher droit, l'agitateur avec son bouton rouge, le barreau, la sonde et le boîtier pH."""
    # 1. L'Agitateur Magnétique Gris avec son bouton rouge ovale
    ax.add_patch(patches.Rectangle((2.0, 1.02), 2.6, 0.6, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=1.5)) 
    ax.add_patch(patches.Ellipse((3.3, 1.32), 0.3, 0.12, color="#e74c3c")) 
    
    # 2. Le Bécher droit classique (Tracé en lignes épaisses)
    ax.plot([2.3, 2.3, 4.3, 4.3], [3.8, 1.62, 1.62, 3.8], color="#34495e", linewidth=2.5) 
    
    # Remplissage progressif du bécher (monte avec v_verse)
    hauteur_liq = 0.5 + 1.2 * (v_verse / v_max)
    ax.add_patch(patches.Rectangle((2.32, 1.64), 1.96, hauteur_liq, facecolor=couleur_sol, alpha=0.8)) 
    
    # Barreau aimanté blanc rotatif au fond
    angle_barreau = 12 if (tick % 2 == 0) else -12
    ax.add_patch(patches.Rectangle((3.0, 1.68), 0.5, 0.08, facecolor="#ffffff", edgecolor="#7f8c8d", angle=angle_barreau))

    # 3. La Sonde pH-métrique noire plongée à droite
    ax.add_patch(patches.Rectangle((3.9, 1.8), 0.16, 3.0, color="#34495e")) # Corps de la sonde
    ax.plot([3.98, 3.98, 4.6], [4.8, 6.6, 6.6], color="#34495e", linewidth=2) # Fil de liaison

    # 4. Le Boîtier pH-mètre noir de contrôle en haut à droite
    ax.add_patch(patches.Rectangle((4.6, 6.0), 1.4, 1.2, facecolor="#2c3e50", edgecolor="#1a252f", linewidth=1.5))
    text_ph = f"pH: {ph_actuel:.2f}" if v_verse > 0 else "pH: --"
    ax.text(5.3, 6.5, text_ph, color="#2ecc71", weight="bold", fontsize=10, fontfamily="monospace", ha="center", va="center")
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
    "Généralités sur le lait",
    "Dosage colorimétrique de la lait",
    "Calcul théorique sur l'aspirine et vérification de l'inscription sur la boîte"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=False):
    import numpy as np
    import streamlit as st

    # Recouvrement des constantes calculees du moteur de paillasse pour l'acide lactique
    v_eq_attendu = st.session_state.get("lact_vrai_veq_calc", 12.5)
    c_base_session = st.session_state.get("c_base_lact", 0.10)
    v_acide_dose = 20.0 # Volume initial de solution d'acide lactique Va mis dans le becher

    # Calcul des moles de soude versees a l'equivalence : n = Cb * Ve
    n_soude_equiv = (c_base_session * v_eq_attendu) / 1000.0
    # A l'equivalence n_acide_lactique = n_base (reaction mole a mole)
    c_lact_dose_attendu = (c_base_session * v_eq_attendu) / v_acide_dose

    col_double_quiz_lact, col_double_trous_lact = st.columns(2)

    with col_double_quiz_lact:
        st.markdown("##### Quiz numerique sur VOTRE suivi de titrage (6 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        opts_q1 = ["Choisir...", f"{c_base_session:.3f} mol/L", "1.000 mol/L", "0.100 mol/L"]
        st.write("**1.** Quelle est la concentration molaire de la solution titrante de soude ($C_b$) utilisee ?")
        dict_reponses_quiz["q1"] = st.selectbox("", opts_q1, key="col_g_quiz_lact_q1_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q2 = ["Choisir...", f"{v_acide_dose:.1f} mL", "10.0 mL", "25.0 mL"]
        st.write("**2.** Quel volume de solution d'acide lactique titree ($V_a$) a ete introduit dans le becher ?")
        dict_reponses_quiz["q2"] = st.selectbox("", opts_q2, key="col_g_quiz_lact_q2_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q3 = ["Choisir...", f"{v_eq_attendu:.1f} mL", "10.0 mL", "15.0 mL"]
        st.write("**3.** Quel est le volume equivalent exact ($V_E$) de soude verse releve sur la courbe ?")
        dict_reponses_quiz["q3"] = st.selectbox("", opts_q3, key="col_g_quiz_lact_q3_tab2", disabled=verrouille, label_visibility="collapsed")

        st.write("**4.** Quelle est la relation stoechiometrique a l'equivalence pour ce titrage ?")
        dict_reponses_quiz["q4"] = st.selectbox("", ["Choisir...", "Ca * Va = Cb * Ve", "Ca * Cb = Va * Ve", "Ca / Va = Cb / Ve"], key="col_g_quiz_lact_q4_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q5 = ["Choisir...", f"{n_soude_equiv:.5f} mol", f"{n_soude_equiv * 10:.5f} mol", "0.01000 mol"]
        st.write("**5.** Quelle quantite de matiere d'ions hydroxyle $HO^-$ a ete apportee a l'equivalence ?")
        dict_reponses_quiz["q5"] = st.selectbox("", opts_q5, key="col_g_quiz_lact_q5_tab2", disabled=verrouille, label_visibility="collapsed")

        opts_q6 = ["Choisir...", f"{c_lact_dose_attendu:.4f} mol/L", "0.0100 mol/L", "0.2000 mol/L"]
        st.write("**6.** Deduisez-en la concentration molaire ($C_a$) de l'acide lactique dans le becher :")
        dict_reponses_quiz["q6"] = st.selectbox("", opts_q6, key="col_g_quiz_lact_q6_tab2", disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_lact:
        st.markdown("##### Synthese de cours (Texte a trous - 5 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La verrerie graduee verifiant l'ajout millilitre par millilitre de soude est la")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Burette", "Eprouvette graduee", "Pipette jaugee"], key="lact_t1_tab2", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour prelever de maniere precise le volume d'acide lactique a doser, on utilise une")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Pipette jaugee", "Eprouvette graduee", "Fioles"], key="lact_t2_tab2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour exploiter le volume equivalent dans les calculs de concentration, on doit le")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "diviser par 1000", "multiplier par 1000", "laisser en mL"], key="lact_t3_tab2", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au point equivalent, les reactifs acide et basique ont ete introduits dans les proportions")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "stoechiometriques", "inverses", "maximales"], key="lact_t4_tab2", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Sur un suivi pH-metrique d'acide faible, l'equivalence correspond a la rupture du")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Saut de pH", "Palier initial", "Debut du dosage"], key="lact_t5_tab2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_acidelactique1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz1_lact" not in st.session_state:
        base_quiz1_lact = [
            {"id": "q1_1", "q": "L'acide lactique est une molecule possedant des proprietes :", "type": "menu", "options": ["acides", "neutres", "basiques"], "rep": "acides"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire de l'acide lactique pure (C3H6O3) en g/mol :", "type": "menu", "options": ["90,08", "180,15", "60,05"], "rep": "90,08"},
            {"id": "q1_3", "q": "Quel est le nom chimique officiel de la molecule d'acide lactique ?", "type": "menu", "options": ["acide 2-hydroxypropanoique", "acide acetylsalicylique", "acide ethanoique"], "rep": "acide 2-hydroxypropanoique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atomes de carbone (C) dans un motif d'acide lactique ?", "type": "menu", "options": ["3", "6", "9"], "rep": "3"},
            {"id": "q1_5", "q": "Quel est le nombre d'atomes d'hydrogene (H) dans un motif d'acide lactique ?", "type": "menu", "options": ["6", "8", "4"], "rep": "6"},
            {"id": "q1_6", "q": "Quel est le nombre d'atomes d'oxygene (O) dans un motif d'acide lactique ?", "type": "menu", "options": ["3", "6", "4"], "rep": "3"},
            {"id": "q1_7", "q": "Quelle est la formule brute exacte de l'acide lactique du lait ?", "type": "menu", "options": ["C3H6O3", "C6H8O6", "C2H4O2"], "rep": "C3H6O3"},
            {"id": "q1_8", "q": "D'apres la classification atomique, le nombre de masse de l'element C vaut :", "type": "menu", "options": ["12 g/mol", "14 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "Quelle couleur conventionnelle represente l'atome d'oxygene sur les maquettes ?", "type": "menu", "options": ["Rouge", "Noir", "Blanc"], "rep": "Rouge"},
            {"id": "q1_10", "q": "Dans le lait, l'acide lactique provient principalement de la fermentation du :", "type": "menu", "options": ["Lactose (sucre du lait)", "Lipide (gras du lait)", "Caseine (proteine)"], "rep": "Lactose (sucre du lait)"}
        ]
        copie_base = list(base_quiz1_lact)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_lact = copie_base

    col_double_quiz_lact1, col_double_trous_lact1 = st.columns(2)

    with col_double_quiz_lact1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_lact, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"lact_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_lact_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = opts_copie
            
            opts_affichees = ["Choisir..."] + st.session_state[cle_shuff_opts]
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = opts_affichees.index(val_p) if val_p in opts_affichees else 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", opts_affichees, index=sel_idx, key=cle_select,
                disabled=verrouille, label_visibility="collapsed"
            )

    with col_double_trous_lact1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le principe actif responsable de l'acidite du lait est l'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "lactique", "ascorbique", "citrique"], key="lact_t1_tab1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Sa formule de structure brute globale s'ecrit")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "C3H6O3", "C6H8O6", "C2H4O2"], key="lact_t2_tab1", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse molaire calculee a partir de ses elements constitutifs vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "90,08 g/mol", "176,12 g/mol", "60,05 g/mol"], key="lact_t3_tab1", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Au sein de son squelette carbone, on compte un total de")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "3 atomes", "6 atomes", "9 atomes"], key="lact_t4_tab1", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre d'atomes d'Hydrogene presents dans la structure vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "6 atomes", "8 atomes", "4 atomes"], key="lact_t5_tab1", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le nombre d'atomes d'Oxygene repartis sur ses fonctions hydroxyles et carboxyle est de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "3 atomes", "6 atomes", "4 atomes"], key="lact_t6_tab1", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La constante de masse molaire de l'element atomique C est")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "12 g/mol", "1 g/mol", "16 g/mol"], key="lact_t7_tab1", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La constante de masse molaire de l'element oxygene O vaut")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "16 g/mol", "12 g/mol", "1 g/mol"], key="lact_t8_tab1", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors de la manipulation de réactifs corrosifs comme la soude, le port de gants est")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Obligatoire", "Facultatif", "Interdit"], key="lact_t9_tab1", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide concentree permet de rapprocher sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7 (neutre)", "0 (acide)", "14 (basique)"], key="lact_t10_tab1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous




def simuler_et_ajouter_goutte_dosage():
    import streamlit as st
    import numpy as np
    import math

    # Recupération securisee des parametres du flacon de la session
    v_max_ml = 25.0
    V_ini = 20.0
    pKa = 4.2
    M_vitC = 176
    
    C_base = st.session_state.get("c_base", 0.1)
    masse_g = st.session_state.get("masse_reelle_g", 0.0015)
    v_actuel = st.session_state.get("v_verse", 0.0)
    choix_ind = st.session_state.get("choix_ind_cle", "Phenolphtaleine")

    # Increment d'une goutte unique de 0.1 mL
    v_nouveau = round(min(v_max_ml, v_actuel + 0.1), 1)
    st.session_state.v_verse = v_nouveau

    # Calcul physico-chimique instantane du pH pour ce point précis
    n_acide_ini = masse_g / M_vitC
    n_b = (v_nouveau / 1000.0) * C_base
    v_tot = (V_ini / 1000.0) + (v_nouveau / 1000.0)

    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    if v_tot <= 0 or n_acide_ini <= 0:
        ph_point = 1.0
    elif n_b < n_acide_ini:
        if n_b == 0:
            ph_point = max(1.0, 0.5 * (pKa - math.log10(n_acide_ini / (V_ini / 1000.0))))
        else:
            ratio = n_b / n_acide_ini
            ph_point = max(1.0, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
    else:
        ratio = n_b / n_acide_ini
        if ratio == 1.0:
            ph_point = ph_eq_theorique
        else:
            ph_point = min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    # Synchronisation instantanee des etats de la paillasse numerique
    st.session_state.vin_vrai_ph_final = float(ph_point)
    
    # Historisation immediate de la goutte dans la matrice de suivi
    if "suivi_gouttes_session" not in st.session_state:
        st.session_state.suivi_gouttes_session = {}

    ind_d = st.session_state.indicateurs[choix_ind]
    if ph_point < ind_d["ph_min"]: 
        obs = ind_d["nom_acide"]
    elif ph_point > ind_d["ph_max"]: 
        obs = ind_d["nom_base"]
    else: 
        obs = ind_d["nom_zone"]

    st.session_state.suivi_gouttes_session[f"Goutte {int(v_nouveau * 10)}"] = {
        "Soude versee V_B (mL)": f"{v_nouveau:.1f}",
        "pH mesure": f"{ph_point:.2f}",
        "Observations / Teinte": obs
    }






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
            key="btn_validation_identité_maitre",
            disabled=st.session_state.get("vérrouillé", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("vérrouillé", False):
                st.rerun()

with tab1:
    st.header("Atelier 1 : Généralités la fraîcheur du lait ")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])

    with col_gauche:
        st.subheader("Document d'étude")
        texte_document = (  "Pour connaître la fraîcheur du lait, on mesure son degré Dornic (°D) qui correspond à la quantité "
            "d'acide lactique, sachant que 1°D correspond à 0,1 g d'acide lactique par litre de lait. Le lait cru est fragile, "
            "mais plus onctueux et aromatisé que les autres laits. Il est embouteillé directement à la ferme puis déposé en magasin "
            "au rayon frais. On le reconnaît à son bouchon jaune. Le lait cru se conserve au maximum 72 heures au frais après mise en bouteille. "
            "En magasin, on reconnaît les laits entier, demi-écrémé et écrémé (pasteurisé c'est-à-dire chauffé à 72 °C pendant 20 secondes, "
            "il peut être conservé pendant 7 jours à 4°C) grâce à la couleur de leur bouchon (respectivement rouge, bleu, vert). Ces trois "
            "catégories correspondent à la teneur en crème présente dans le lait ; en effet, à la laiterie, le lait est pasteurisé, "
            "puis séparé de la crème grâce à une écrémeuse centrifugeuse."
        )
            
        st.info(texte_document)
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        # Création de la figure Matplotlib pour remplacer le Canvas Tkinter
        fig_lait, ax_lait = plt.subplots(figsize=(6, 5.5), facecolor="white")
        ax_lait.set_facecolor("white")
        
        # Alignement strict sur le repère Tkinter de votre script (0 en haut)
        ax_lait.set_ylim(550, 0)
        ax_lait.set_xlim(0, 700)

        # 1. Le bouchon bleu vissé en haut et son effet relief
        ax_lait.add_patch(patches.Rectangle((230, 5), 80, 35, facecolor="#0066cc", edgecolor="none"))
        for i in range(240, 300, 10):
            ax_lait.plot([i, i], [5, 40], color="#004499", linewidth=1)

        # 2. Le col de la bouteille
        coords_col = np.array([[235, 40], [305, 40], [315, 75], [225, 75]])
        ax_lait.add_patch(patches.Polygon(coords_col, facecolor="white", edgecolor="#cccccc", linewidth=1))

        # 3. Le corps de la bouteille (Épaules, rectangle central et fond arrondi)
        ax_lait.add_patch(patches.Ellipse((270, 105), 180, 80, facecolor="white", edgecolor="none"))
        ax_lait.add_patch(patches.Rectangle((180, 105), 180, 390, facecolor="white", edgecolor="none"))
        ax_lait.add_patch(patches.Wedge((270, 490), 90, 0, 180, facecolor="white", edgecolor="none"))
        # Tracé des lignes de contour extérieures globales pour la cohérence
        ax_lait.plot([180, 180], [105, 490], color="#cccccc", linewidth=1)
        ax_lait.plot([360, 360], [105, 490], color="#cccccc", linewidth=1)

        # 4. La poignée creuse (Simulation du trou par couleur de fond lightblue)
        ax_lait.add_patch(patches.Rectangle((325, 110), 20, 180, facecolor="lightblue", edgecolor="#cccccc", linewidth=1))

        # 5. L'étiquette bleue et blanche centrale
        ax_lait.add_patch(patches.Rectangle((181, 280), 178, 180, facecolor="#0099ff", edgecolor="#0099ff"))

        # 6. Décoration de l'étiquette (Partie verte prairie et courbe blanche de laitage)
        coords_prairie = np.array([[181, 390], [359, 390], [359, 460], [181, 460]])
        ax_lait.add_patch(patches.Polygon(coords_prairie, facecolor="#00b050", edgecolor="none"))
        
        coords_chemin = np.array([[260, 390], [300, 390], [240, 460], [200, 460]])
        ax_lait.add_patch(patches.Polygon(coords_chemin, facecolor="#ffffff", edgecolor="none"))

        # 7. Logo "candia"
        ax_lait.add_patch(patches.Ellipse((270, 307.5), 60, 35, facecolor="white", edgecolor="#004499", linewidth=1))
        ax_lait.text(270, 306, "candia", fontname="Arial", fontsize=11, weight="bold", color="#004499", ha="center", va="center")

        # 8. Texte "Grandlait" principal en gras et italique
        ax_lait.text(275, 360, "Grandlait", fontname="Impact", fontsize=15, style="italic", color="#003366", ha="center", va="center")

        # 9. Mention "Demi-écrémé" orientée verticalement à gauche
        ax_lait.text(195, 370, "Demi-écrémé", fontname="Arial", fontsize=9, weight="bold", color="white", rotation=90, ha="center", va="center")

        # 10. Petite vache géométrique sur la prairie
        ax_lait.add_patch(patches.Ellipse((322.5, 430), 25, 20, facecolor="white", edgecolor="black", linewidth=1))
        ax_lait.add_patch(patches.Rectangle((315, 435), 5, 10, facecolor="black", edgecolor="none"))
        ax_lait.add_patch(patches.Rectangle((325, 435), 5, 10, facecolor="black", edgecolor="none"))
        
        ax_lait.axis("off")
        st.pyplot(fig_lait)   
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Données et Légendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphère noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.divider()

        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        import numpy as np

        fig_mol, ax_mol = plt.subplots(figsize=(6, 5), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # --- 1. Coordonnées géométriques des atomes de la chaîne carbonée principale ---
        c_methyl = np.array([2.4, 3.0])
        c_cent = np.array([3.6, 2.5])
        c_carboxy = np.array([4.8, 3.0])

        # --- 2. Coordonnées des substituants du carbone central ---
        oh_cent = np.array([3.4, 1.4])
        h_oh_cent = np.array([3.3, 0.8])
        h_cent = np.array([4.2, 1.9])

        # --- 3. Coordonnées des substituants du groupe carboxyle ---
        double_o = np.array([5.6, 2.4])
        oh_carb = np.array([5.0, 4.1])
        h_carb = np.array([5.7, 4.5])

        # --- 4. Coordonnées des hydrogènes du groupement méthyle (-CH3) ---
        h1_m = np.array([1.8, 2.2])
        h2_m = np.array([1.7, 3.4])
        h3_m = np.array([2.5, 4.0])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # --- TRACÉ DES LIAISONS DE LA CHAÎNE PRINCIPALE ---
        tracer_liaison(c_methyl, c_cent)
        tracer_liaison(c_cent, c_carboxy)
        
        # --- TRACÉ DES LIAISONS DES HYDROGÈNES DU MÉTHYLE ---
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        
        # --- TRACÉ DES LIAISONS DU -OH CENTRAL ET DE SON HYDROGÈNE ---
        tracer_liaison(c_cent, oh_cent)
        tracer_liaison(oh_cent, h_oh_cent)
        
        # --- TRACÉ DE LA LIAISON DE L'HYDROGÈNE DU CARBONE CENTRAL ---
        tracer_liaison(c_cent, h_cent)
        
        # --- TRACÉ DES LIAISONS DU GROUPEMENT CARBOXYLE ---
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_carb)
        tracer_liaison(oh_carb, h_carb)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, text_color = "#2b3e50", "white"
            elif symbole == 'O': couleur, text_color = "#e74c3c", "white"
            elif symbole == 'H': couleur, text_color = "#ecf0f1", "black"
            else: couleur, text_color = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=text_color, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # --- RENDU DE TOUS LES ATOMES (PAR-DESSUS) ---
        # Atomes de Carbone
        tracer_atome(c_methyl, 'C')
        tracer_atome(c_cent, 'C')
        tracer_atome(c_carboxy, 'C')
        
        # Atomes d'Oxygène
        tracer_atome(oh_cent, 'O')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_carb, 'O')
        
        # Atomes d'Hydrogène
        tracer_atome(h_oh_cent, 'H')
        tracer_atome(h_cent, 'H')
        tracer_atome(h_carb, 'H')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')

        ax_mol.set_xlim(1.2, 6.2)
        ax_mol.set_ylim(0.5, 4.8)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    res_q1, res_t1 = afficher_questions_acidelactique1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    st.write("---")
    st.subheader("Généralité sur le lait")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir completé les questions.", 
        key="check_certif_vin1", 
        disabled=st.session_state.vin_verrouille_tab1
    )

    verrou_vin1 = st.session_state.get("vin_verrouille_tab1", False)



with tab2:
    st.header("Dosage de la fraîcheur du lait")
    st.caption("Simulation interactive et animée goutte-à-goutte du titrage de l'acidité du lait par la soude")

    # Initialisation des etats de session specifiques a l'Atelier 2
    if "vin_verrouille_tab2" not in st.session_state: st.session_state.vin_verrouille_tab2 = False
    if "animation_active" not in st.session_state: st.session_state.animation_active = False
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "c_base" not in st.session_state: st.session_state.c_base = 0.1
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 0.5
    if "masse_reelle_g" not in st.session_state:
        import random
        st.session_state.masse_reelle_g = random.uniform(3, 7) 

    # Données physico-chimiques réglementaires de l'acide acétylsalicylique
    v_max_ml = 25.0
    V_ini = 20.0  
    pKa = 3.9     
    M_lait = 90
    C_base = st.session_state.c_base
    n_acide_ini = st.session_state.masse_reelle_g / (M_lait*50)

    # Calcul exact des reperes d'equivalence de la session
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        import math
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # --- TABLEAUX SIMPLIFIÉS UNIQUEMENT POUR L'ANIMATION ET LA COULEUR ---
    import numpy as np
    # Volume d'équivalence visuel calé sur la théorie (ou fixé à 12.0)
    v_eq_visuel = v_eq_theorique if v_eq_theorique < v_max_ml else 12.0
    
    # Création des volumes de 0 à v_max_ml par pas de 0.1 mL
    volumes_simules = np.arange(0.0, v_max_ml + 0.1, 0.1)
    
    # Génération des pH pour le virage de couleur (Acide -> Zone tampon -> Basique)
    phs_simules = []
    for v in volumes_simules:
        if v < (v_eq_visuel - 0.2):
            ph = 3.0  # Zone acide (couleur acide de l'indicateur)
        elif abs(v - v_eq_visuel) <= 0.2:
            ph = 7.0  # Zone de virage (couleur de zone)
        else:
            ph = 11.0 # Zone basique (couleur base)
        phs_simules.append(ph)
        
    phs_simules = np.array(phs_simules)
    # ---------------------------------------------------------------------

    # --- ZONE DES REGLAGES SUPERIEURS ---
    with st.container(border=True):
        st.subheader("Paramètres de la solution titrante et du goutte-a-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.session_state.c_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :", 
                min_value=0.001, max_value=2.0, value=st.session_state.c_base, step=0.001,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_input_cb_base"
            )
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte / Volume de la goutte (mL) :", 
                min_value=0.1, max_value=2.0, value=st.session_state.pas_ml, step=0.1,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_slider_pas_ml"
            )
        with col_p3:
            liste_indicateurs = list(st.session_state.indicateurs.keys())
            choix_ind = st.selectbox(
                "Sélectionner un indicateur coloré :", 
                options=liste_indicateurs, index=0,
                disabled=st.session_state.vin_verrouille_tab2, key="cfg_select_ind_colore"
            )

    st.info(f"Compose : Acide lactique | Masse pesée (aléatoire) : {st.session_state.masse_reelle_g * 1000 :.1f} mg | Soude titrante : {C_base} mol/L")
    st.divider()

    if "v_verse" not in st.session_state:
        st.session_state.v_verse = 0.0
    if "tick_animation" not in st.session_state:
        st.session_state.tick_animation = 0

    # --- BARRE DE COMMANDE DE L'ANIMATION DU TP ---
    st.subheader("Ajout progressif de la solution titrante")
    col_b1, col_stop, col_b2, col_sl = st.columns([1.1, 0.8, 0.9, 1.8], vertical_alignment="bottom")
    
    with col_b1:
        if st.button("Demarrer", key="btn_run_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2 or st.session_state.animation_active):
            st.session_state.animation_active = True
            st.rerun()
            
    with col_stop:
        if st.button("Pause", key="btn_stop_auto_soude", use_container_width=True, disabled=not st.session_state.animation_active):
            st.session_state.animation_active = False
            st.rerun()
            
    with col_b2:
        if st.button("Effacer", key="btn_clear_auto_soude", use_container_width=True, disabled=st.session_state.vin_verrouille_tab2):
            st.session_state.v_verse = 0.0
            st.session_state.animation_active = False
            st.rerun()
            
    with col_sl:
        v_manuel = st.slider(
            "Volume de soude total verse V_B (mL) :", 
            min_value=0.0, 
            max_value=v_max_ml, 
            value=float(st.session_state.v_verse), 
            step=0.1, 
            disabled=st.session_state.vin_verrouille_tab2
        )
        if not st.session_state.animation_active: 
            st.session_state.v_verse = float(v_manuel)

        if not st.session_state.animation_active: 
            st.session_state.v_verse = float(v_manuel)

    # --- ENCAPSULATION DE VOS MÉTHODES MATHÉMATIQUES TKINTER ---
    def calculer_ph_lactique(v_b_ml):
        """Calcule le vrai pH théorique basé sur vos équations de l'acide lactique."""
        if v_b_ml == 0:
            # Calcul du pH initial exact issu de votre code
            import math
            try:
                # Constante Ka calculée à partir de votre pKa
                Ka = 10**(-pKa)
                return -math.log10(-Ka + (Ka*Ka + 4*Ka*(n_acide_ini / (V_ini / 1000.0)))**0.5)
            except:
                return 0.5 * (pKa - math.log10(n_acide_ini / (V_ini / 1000.0)))
                
        v_b = v_b_ml / 1000.0
        v_a_total = V_ini / 1000.0
        n_b = v_b * C_base
        v_tot = v_a_total + v_b

        if v_tot <= 0 or n_acide_ini <= 0:
            return 1.0
            
        import math
        if n_b < n_acide_ini:
            ratio = n_b / n_acide_ini
            return max(1.0, min(13.0, pKa + math.log10(ratio / (1 - ratio))))
        else:
            ratio = n_b / n_acide_ini
            if (ratio - 1) <= 0: return ph_eq_theorique
            return min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1))

    # --- MOTEUR D'ANIMATION STREAMLIT ---
    if st.session_state.animation_active:
        if st.session_state.v_verse < v_max_ml:
            import time
            time.sleep(0.06) 
            st.session_state.v_verse = round(min(v_max_ml, st.session_state.v_verse + st.session_state.pas_ml), 1)
            st.session_state.tick_animation += 1
            st.rerun()
        else:
            st.session_state.animation_active = False
            st.rerun()

    # --- EXÉCUTION DU CALCUL ET DES SEUILS DE COULEURS ISSUS DE VOS MÉTHODES ---
    ph_actuel = calculer_ph_lactique(st.session_state.v_verse)

    # Logique get_indicateur_couleur issue de votre script Tkinter
    if np.isclose(st.session_state.v_verse, v_eq_theorique, atol=0.5):
        couleur_sol = "#ebf5fb" # Couleur Équivalence intermédiaire proche du neutre
        nom_teinte = "Équivalence"
    elif ph_actuel < 7.2:
        couleur_sol = "#fcf3cf" # Le Jaune clair de votre méthode dessiner_montage_initial
        nom_teinte = "Teinte : Jaune"
    elif 7.2 <= ph_actuel < 8.8:
        couleur_sol = "#f9ebe8" # Le Rose clair (ph_actuel >= 8.2 de votre animation)
        nom_teinte = "Teinte : Rose"
    else:
        couleur_sol = "#f5b7b1" # Le Pourpre/Rose foncé (ph_actuel >= 10.0 de votre animation)
        nom_teinte = "Teinte : Pourpre"

    # --- RENDU DE LA SCÈNE ET AFFICHAGE ---
    fig_m, ax_mo = plt.subplots(figsize=(2.5, 4.2), facecolor="white")
    ax_mo.set_facecolor("white")
    
    # Dessin du support de la potence de laboratoire en arrière-plan
    ax_mo.add_patch(patches.Rectangle((0.6, 1.0), 0.12, 7.8, color="#7f8c8d")) # Tige
    ax_mo.add_patch(patches.Rectangle((0.72, 7.8), 2.5, 0.06, color="#95a5a6")) # Potence transversale

    # Appels coordonnés des fonctions globales de dessin
    draw_burette(ax_mo, st.session_state.v_verse, v_max_ml, st.session_state.animation_active, st.session_state.tick_animation, st.session_state.pas_ml)
    draw_becher(ax_mo, st.session_state.v_verse, v_max_ml, couleur_sol, st.session_state.tick_animation, ph_actuel)

    # Affichage de la légende textuelle de l'indicateur
    ax_mo.text(3.3, 0.3, nom_teinte, color="#34495e", fontsize=9, ha="center", weight="bold")
    
    ax_mo.set_xlim(0.1, 6.2)
    ax_mo.set_ylim(0.0, 9.5)
    ax_mo.axis("off")
    
    st.pyplot(fig_m, clear_figure=True)
    plt.close(fig_m)

    # --- SYNCHRONISATION DES VARIABLES POUR LES TRACÉS SUIVANTS ---
    try:
        st.session_state.vin_vrai_ph_final = float(ph_actuel)
        st.session_state.vin_vrai_veq_calc = float(v_eq_theorique)
        st.session_state.input_at2_ve_lu_eleve = float(v_eq_theorique)
        st.session_state.vin_vrai_total_points = float(st.session_state.tick_animation + 1)
    except (ValueError, TypeError, NameError):
        pass

    

    st.write("---")
    st.subheader("Formulaire d'évaluation numérique - Atelier 2")

    # Calculs automatiques des veritables attendus pour la correction automatique du bouton
    v_acide_dose = 20.0
    n_soude_equiv = (C_base * v_eq_theorique) / 1000.0
    c_vinaigre_dose_attendu = (C_base * v_eq_theorique) / v_acide_dose

    verrou_vin2 = st.session_state.get("vin_verrouille_tab2", False)

    # Execution propre de l'affichage bicolonne defini dans votre fonction prof
    if not st.session_state.get("animation_active", False):
        try:
            # Appel dynamique de votre def prof existante
            generer_le_quiz_analytique_atelier_deux(df_donnees=None, verrouille=verrou_vin2)
        except NameError:
            # Securite si votre def porte encore l'ancien nom dans votre fichier
            afficher_questions_titrage_dynamiques(df_donnees=None, verrouille=verrou_vin2)
    else:
        st.info("Le versement de la soude est en cours... Le formulaire d'evaluation s'affichera des que l'animation sera terminee.")

    # --- ACTIONNEUR DE NOTATION ET VERROUILLAGE ACADÉMIQUE ---
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()



    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

            
        ax_rp.set_xlim(0, v_max_ml + 1)
        ax_rp.set_ylim(0, 14)
        ax_rp.grid(True, linestyle=":")
        
        tampon_memoire = io.BytesIO()
        fig_rep.savefig(tampon_memoire, format="png", bbox_inches="tight")
        tampon_memoire.seek(0)
        base64_image_courbe = base64.b64encode(tampon_memoire.read()).decode("utf-8")
        plt.close(fig_rep)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    st.write("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    case_certif_asp2 = st.checkbox("Je certifie avoir complete l'integralite du questionnaire de l'Atelier 2.", key="check_certif_asp2_final_net", disabled=st.session_state.get("verrouille_tab2_asp", False))




            

with tab3:
    st.header("Calcul theorique & Verification de la boîte")
    st.caption("Verification de la conformite de la fraîcheur du lait")

    if "vin_verrouille_tab3" not in st.session_state: st.session_state.vin_verrouille_tab3 = False

    # Récupération dynamique des constantes calculées et des états de paillasse de l'Atelier 2
    c_base_session = st.session_state.get("c_base", 0.1)
    v_eq_session = st.session_state.get("input_at2_ve_lu_eleve", 12.0)
    ph_eq_session = st.session_state.get("input_at2_phe_lu_eleve", 8.7)
    v_titre_session = 20.0
    M_lait = 90
    facteur_dilution = 1
    V_fiole = 1

    # --- BANDEAU DE RAPPEL DES RÉSULTATS EXPÉRIMENTAUX DE L'ATELIER 2 ---
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <span style="background-color: black; color: #ef4444; padding: 4px 15px; font-weight: bold; font-size: 15px; border-radius: 2px;">
                Rappels sur les resultats de votre dosage
            </span>
            <div style="background-color: #bae6fd; color: black; padding: 8px 15px; font-weight: bold; font-size: 13px; margin-top: 5px; border-radius: 2px; border: 1px solid #7dd3fc;">
                On dose 20 mL de lait d'une bouteille d'un litre avec que l'on prélève à l'aide aide d'une pipette jaugée.
            </div>

        </div>
    """, unsafe_allow_html=True)

    col_rap1, col_rap2 = st.columns(2)
    with col_rap1:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; V_eq = {v_eq_session:.2f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; pH_eq = {ph_eq_session:.2f}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; concentration titrante = {c_base_session:.2f} mol/L</p>", unsafe_allow_html=True)
    with col_rap2:
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; Volume titre = {v_titre_session:.1f} mL</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; M = {M_lait:.2f} g/mol</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; n = C x V </p>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: blue; font-weight: bold; font-size: 13px;'>&rarr; m = n x M</p>", unsafe_allow_html=True)


    st.write("---")




























