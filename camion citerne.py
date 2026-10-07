# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Outil de Simulation et d'Étude d'un Camion-Citerne ",
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
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Outil de Simulation et d'Étude d'un Camion-Citerne")
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
st.sidebar.header("Paramètres Fluide & Masse")
type_fluide = st.sidebar.selectbox("Type de fluide transporté", ["Eau / Lait (1000 kg/m³)", "Gazole / Essence (850 kg/m³)", "Acide (1400 kg/m³)"])
rho = 1000 if "Eau" in type_fluide else (850 if "Gazole" in type_fluide else 1400)

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
    "Étude de la Cuve", 
    "Étude Statique & Essieux", 
    "Étude Dynamique & Freinage"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]

def afficher_questions_dynamique_freinage(taux_remplissage, h_liquide, masse_fluide_actuelle, masse_totale_en_charge, deceleration, mu_sol, z_cg_total, f_ballottement, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_dynamique" not in st.session_state:
        base_quiz_dynamique = [
            {"id": "qd_1", "q": "Comment évolue le centre de gravité total (Z_CG) lors de l'ajout de liquide dans la cuve ?", "type": "menu", "options": ["Il s'élève", "Il s'abaisse", "Il reste fixe"], "rep": "Il s'élève"},
            {"id": "qd_2", "q": "Quelle est la valeur du taux de remplissage actuellement configurée ?", "type": "menu", "options": [f"{taux_remplissage} %", f"{taux_remplissage / 2} %", "100 %"], "rep": f"{taux_remplissage} %"},
            {"id": "qd_3", "q": "Quelle est la valeur de la hauteur de liquide calculée à l'intérieur de la cuve ?", "type": "menu", "options": [f"{h_liquide:.2f} m", f"{h_liquide * 2:.2f} m", "0.00 m"], "rep": f"{h_liquide:.2f} m"},
            {"id": "qd_4", "q": "La masse effective du fluide calculée selon vos réglages est de :", "type": "menu", "options": [f"{masse_fluide_actuelle/1000:.2f} Tonnes", f"{(masse_fluide_actuelle*2)/1000:.2f} Tonnes", "0.00 Tonnes"], "rep": f"{masse_fluide_actuelle/1000:.2f} Tonnes"},
            {"id": "qd_5", "q": "Quelle est la valeur de la Masse Totale en Charge Réelle calculée ?", "type": "menu", "options": [f"{masse_totale_en_charge/1000:.2f} Tonnes", f"{masse_totale_en_charge/100:.2f} Tonnes", "10.00 Tonnes"], "rep": f"{masse_totale_en_charge/1000:.2f} Tonnes"},
            {"id": "qd_6", "q": "Quelle est la valeur de la décélération demandée pour ce freinage ?", "type": "menu", "options": [f"{deceleration:.2f} m/s²", f"{deceleration + 2:.2f} m/s²", "9.81 m/s²"], "rep": f"{deceleration:.2f} m/s²"},
            {"id": "qd_7", "q": "Quel coefficient d'adhérence au sol a été retenu pour les pneumatiques ?", "type": "menu", "options": [f"{mu_sol:.2f}", f"{mu_sol * 2:.2f}", "1.00"], "rep": f"{mu_sol:.2f}"},
            {"id": "qd_8", "q": "La hauteur combinée calculée pour le Centre de Gravité global (Z_CG) est :", "type": "menu", "options": [f"{z_cg_total:.2f} m", f"{z_cg_total + 1:.2f} m", "0.50 m"], "rep": f"{z_cg_total:.2f} m"},
            {"id": "qd_9", "q": "Quelle est la fréquence de ballottement longitudinal mesurée pour votre configuration ?", "type": "menu", "options": [f"{f_ballottement:.3f} Hz", f"{f_ballottement * 2:.3f} Hz", "1.000 Hz"], "rep": f"{f_ballottement:.3f} Hz"},
            {"id": "qd_10", "q": "Lors du freinage, l'essieu qui subit une augmentation de charge verticale est :", "type": "menu", "options": ["L'essieu avant", "L'essieu arrière", "Aucun des deux"], "rep": "L'essieu avant"}
        ]
        copie_base = list(base_quiz_dynamique)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_dynamique = copie_base

    col_double_quiz_d, col_double_trous_d = st.columns(2)

    with col_double_quiz_d:
        st.markdown("##### Quiz d'analyse dynamique (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz_dynamique, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dyn_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_dyn_{q_data['id']}"
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

    with col_double_trous_d:
        st.markdown("##### Synthèse de la dynamique et du freinage (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le ballottement se produit lorsque le taux de remplissage est inférieur à")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "100 %", "50 %"], key="dyn_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le niveau de fluide atteint une hauteur intérieure de sécurité mesurée à")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", f"{h_liquide:.2f} m", f"{h_liquide * 2:.2f} m"], key="dyn_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La masse nette de liquide transportée pour cette session est estimée à")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", f"{masse_fluide_actuelle/1000:.2f} t", "50.00 t"], key="dyn_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La masse totale du camion en ordre de marche sous charge vaut")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", f"{masse_totale_en_charge/1000:.2f} t", "5.00 t"], key="dyn_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La valeur de la décélération linéaire appliquée lors de la simulation est de")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", f"{deceleration:.2f} m/s²", "20.00 m/s²"], key="dyn_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le coefficient d'adhérence caractérisant le contact entre le pneu et le sol vaut")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", f"{mu_sol:.2f}", "1.50"], key="dyn_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La hauteur globale calculée du centre de gravité par rapport au sol est de")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", f"{z_cg_total:.2f} m", "5.00 m"], key="dyn_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La fréquence propre de ballottement longitudinal calculée est égale à")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", f"{f_ballottement:.3f} Hz", "5.000 Hz"], key="dyn_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Lors d'un freinage d'urgence, la charge verticale migre vers l'essieu")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Avant", "Arrière", "Médian"], key="dyn_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Si la décélération dépasse la limite calculée, les roues subissent un")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Blocage", "Décollage", "Rupture"], key="dyn_t10_s1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_statique_dynamiques(materiau, rho_mat, epaisseur, nb_chicanes, taux_perforation, L_empattement, d_cg, masse_chassis, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_statique" not in st.session_state:
        base_quiz_statique = [
            {"id": "qs_1", "q": "Quel matériau a été choisi pour la fabrication de l'enveloppe de la cuve ?", "type": "menu", "options": ["Acier Inoxydable (7850 kg/m³)", "Aluminium (2700 kg/m³)", "Plastique renforcé"], "rep": materiau},
            {"id": "qs_2", "q": "Quelle est la masse volumique du matériau sélectionné ?", "type": "menu", "options": ["7850 kg/m³", "2700 kg/m³", "1000 kg/m³"], "rep": f"{rho_mat} kg/m³"},
            {"id": "qs_3", "q": "Quel principe de la mécanique est appliqué pour calculer les forces sur les essieux au repos ?", "type": "menu", "options": ["Le Principe Fondamental de la Statique", "L'équation de Bernoulli", "Le théorème de l'énergie cinétique"], "rep": "Le Principe Fondamental de la Statique"},
            {"id": "qs_4", "q": "Quelle est la distance du centre de gravité de la cuve par rapport à l'essieu avant ?", "type": "menu", "options": [f"{d_cg:.1f} m", f"{d_cg * 2:.1f} m", f"{d_cg / 2:.1f} m"], "rep": f"{d_cg:.1f} m"},
            {"id": "qs_5", "q": "Quel est l'empattement total choisi pour le châssis du véhicule ?", "type": "menu", "options": [f"{L_empattement:.1f} m", f"{L_empattement + 2:.1f} m", f"{L_empattement - 2:.1f} m"], "rep": f"{L_empattement:.1f} m"},
            {"id": "qs_6", "q": "Comment appelle-t-on les cloisons internes destinées à briser les vagues du liquide ?", "type": "menu", "options": ["Des chicanes perforées", "Des vannes de dépotage", "Des raidisseurs extérieurs"], "rep": "Des chicanes perforées"},
            {"id": "qs_7", "q": "Quelle est l'épaisseur de tôle retenue pour la paroi de la cuve ?", "type": "menu", "options": [f"{epaisseur * 1000:.0f} mm", f"{(epaisseur * 1000) + 2:.0f} mm", f"{(epaisseur * 1000) / 2:.0f} mm"], "rep": f"{epaisseur * 1000:.0f} mm"},
            {"id": "qs_8", "q": "Le nombre actuel de cloisons internes configuré est de :", "type": "menu", "options": ["0", f"{nb_chicanes}", "10"], "rep": f"{nb_chicanes}"},
            {"id": "qs_9", "q": "Quelle force s'exerce verticalement vers le bas au centre de gravité du véhicule ?", "type": "menu", "options": ["Le poids total", "La poussée d'Archimède", "La force centrifuge"], "rep": "Le poids total"},
            {"id": "qs_10", "q": "Si le centre de gravité se rapproche de l'essieu avant, la force sur l'essieu avant va :", "type": "menu", "options": ["Augmenter", "Diminuer", "Rester identique"], "rep": "Augmenter"}
        ]
        copie_base = list(base_quiz_statique)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_statique = copie_base

    col_double_quiz_s, col_double_trous_s = st.columns(2)

    with col_double_quiz_s:
        st.markdown("##### Quiz d'analyse statique (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz_statique, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"stat_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_stat_{q_data['id']}"
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

    with col_double_trous_s:
        st.markdown("##### Synthèse de la répartition des charges (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le matériau de construction retenu pour la structure est l'")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Acier Inoxydable (7850 kg/m³)", "Aluminium (2700 kg/m³)"], key="stat_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La masse volumique du métal choisi est égale à")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "7850 kg/m³", "2700 kg/m³"], key="stat_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'épaisseur nominale de la tôle de l'enveloppe est fixée à")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", f"{epaisseur * 1000:.0f} mm", f"{(epaisseur * 1000) + 2:.0f} mm"], key="stat_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Pour limiter les mouvements de fluide, la cuve comporte")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", f"{nb_chicanes}", "10"], key="stat_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le taux de perforation de ces parois internes est égal à")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", f"{taux_perforation * 100:.0f} %", "60 %"], key="stat_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. La distance séparant les deux groupes d'essieux s'appelle l'")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Empattement", "Voie", "Porte-à-faux"], key="stat_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Au repos, la somme des moments des forces par rapport à un point est")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Nulle", "Maximale", "Inconnue"], key="stat_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. La masse du châssis et du tracteur seul a été estimée à")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", f"{masse_chassis:.0f} kg", "15000 kg"], key="stat_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Plus le matériau choisi est dense, plus la masse à vide de la cuve sera")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Élevée", "Faible", "Invariante"], key="stat_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Le calcul de la répartition des charges sur les essieux s'effectue au")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Repos", "Freinage", "Virage"], key="stat_t10_s1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

def afficher_questions_cuve_dynamiques(forme, rayon, hauteur, aire_section, volume_total, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_cuve" not in st.session_state:
        base_quiz_cuve = [
            {"id": "qc_1", "q": "Quelle est la forme géométrique actuellement sélectionnée pour modéliser la citerne ?", "type": "menu", "options": ["Cylindre Parfait", "Cuve de Transport (Elliptique)", "Citerne Sphérique"], "rep": forme},
            {"id": "qc_2", "q": "Sur quel axe tridimensionnel la longueur de la cuve est-elle étirée dans le dessin 3D Plotly ?", "type": "menu", "options": ["L'axe X (largeur)", "L'axe Y (longueur)", "L'axe Z (hauteur)"], "rep": "L'axe Y (longueur)"},
            {"id": "qc_3", "q": "Quelle est la valeur exacte du rayon ou demi-grand axe horizontal choisi ?", "type": "menu", "options": [f"{rayon:.2f} m", f"{rayon * 2:.2f} m", f"{rayon / 2:.2f} m"], "rep": f"{rayon:.2f} m"},
            {"id": "qc_4", "q": "L'aire de la section transversale calculée pour cette géométrie vaut exactement :", "type": "menu", "options": [f"{aire_section:.2f} m²", f"{aire_section * 1.5:.2f} m²", f"{aire_section / 2:.2f} m²"], "rep": f"{aire_section:.2f} m²"},
            {"id": "qc_5", "q": "Le volume total utile résultant de vos réglages géométriques est de :", "type": "menu", "options": [f"{volume_total:.2f} m³", f"{volume_total * 1000:.2f} m³", f"{volume_total / 2:.2f} m³"], "rep": f"{volume_total:.2f} m³"},
            {"id": "qc_6", "q": "Quelle formule mathématique correspond à la section transversale de votre cuve ?", "type": "menu", "options": ["Surface = pi * R²", "Surface = pi * A * B", "Surface = 2 * pi * R"], "rep": "Surface = pi * R²" if forme == "Cylindre Parfait" else "Surface = pi * A * B"},
            {"id": "qc_7", "q": "Combien de surfaces distinctes Plotly superpose-t-il pour afficher cette cuve fermée ?", "type": "menu", "options": ["Une seule surface", "Deux surfaces de fond", "Trois surfaces (le corps et les deux fonds)"], "rep": "Trois surfaces (le corps et les deux fonds)"},
            {"id": "qc_8", "q": "Si la longueur de la cuve est doublée, comment évolue le volume total ?", "type": "menu", "options": ["Il reste identique", "Il est doublé", "Il augmente de façon quadratique"], "rep": "Il est doublé"},
            {"id": "qc_9", "q": "Quelle est l'unité de mesure standard du volume utile affichée dans vos résultats ?", "type": "menu", "options": ["Le mètre carré (m²)", "Le mètre cube (m³)", "Le kilonewton (kN)"], "rep": "Le mètre cube (m³)"},
            {"id": "qc_10", "q": "Quel paramètre géométrique influence de manière quadratique (au carré) la capacité de stockage ?", "type": "menu", "options": ["La longueur de la cuve", "Le rayon ou demi-grand axe", "L'opacité de la surface 3D"], "rep": "Le rayon ou demi-grand axe"}
        ]
        copie_base = list(base_quiz_cuve)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_cuve = copie_base

    col_double_quiz_c, col_double_trous_c = st.columns(2)

    with col_double_quiz_c:
        st.markdown("##### Quiz de géométrie de la cuve (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz_cuve, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"cuve_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_cuve_{q_data['id']}"
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

    with col_double_trous_c:
        st.markdown("##### Synthèse des propriétés de la citerne (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La forme actuellement configurée et visible sur le dessin tridimensionnel est un")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Cylindre Parfait", "Cuve de Transport (Elliptique)"], key="cuve_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le rayon horizontal ou demi-grand axe défini par le curseur de réglage est de")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", f"{rayon:.2f} m", f"{rayon * 2:.2f} m"], key="cuve_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La longueur de la structure cylindrique qui s'étend sur la coordonnée Y vaut")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", f"{hauteur:.2f} m", f"{hauteur / 2:.2f} m"], key="cuve_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La surface plane calculée pour la section de cette enveloppe extérieure s'élève à")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", f"{aire_section:.2f} m²", f"{aire_section * 1.1:.2f} m²"], key="cuve_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'espace volumétrique disponible à l'intérieur de la citerne représente")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", f"{volume_total:.2f} m³", f"{volume_total * 2:.2f} m³"], key="cuve_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Pour obtenir le volume de stockage, on multiplie la surface de la section par la")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Longueur", "Épaisseur"], key="cuve_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La bibliothèque Python utilisée pour tracer la surface bleue interactive s'appelle")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Plotly", "Matplotlib", "Seaborn"], key="cuve_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Une cuve dont l'axe vertical est plus petit que l'axe horizontal possède une section")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Elliptique", "Circulaire"], key="cuve_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le maillage géométrique 3D s'appuie sur une grille de points générée par la fonction")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Meshgrid", "Linspace", "Arange"], key="cuve_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. La capacité maximale en litres se déduit en multipliant les mètres cubes par")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "1000", "100", "10"], key="cuve_t10_s1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

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
    st.header("Dimensionnement Géométrique et Modélisation 3D")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        forme = st.radio("Géométrie de la cuve", ["Cylindre Parfait", "Cuve de Transport (Elliptique)"])
        rayon = st.slider("Rayon / Demi-grand axe horizontal (m)", 0.5, 1.5, 1.0, 0.05)
        
        if forme == "Cuve de Transport (Elliptique)":
            ratio_ellipse = st.slider("Ratio hauteur / largeur (Axe vertical / Axe horizontal)", 0.5, 1.0, 0.7, 0.05)
            r_vertical = rayon * ratio_ellipse
            st.caption(f"Axe vertical (Hauteur équivalente) : {r_vertical:.2f} m")
        else:
            r_vertical = rayon
            
        hauteur = st.slider("Longueur / Hauteur cylindrique (m)", 3.0, 15.0, 8.0, 0.5)

        # Calculs géométriques de base
        if forme == "Cylindre Parfait":
            aire_section = np.pi * (rayon ** 2)
        else:
            aire_section = np.pi * rayon * r_vertical

        volume_total = aire_section * hauteur

        st.subheader("Résultats Géométriques")
        st.metric(label="Surface de la section", value=f"{aire_section:.2f} m²")
        st.metric(label="Volume Total Utile", value=f"{volume_total:.2f} m³ ({volume_total*1000:.0f} Litres)")

    with col2:
        st.subheader("Visualisation 3D de la Cuve")
        
        # Génération du maillage 3D pour Plotly
        nombre_points_u = 50
        nombre_points_v = 50
        u = np.linspace(0, 2 * np.pi, nombre_points_u)
        v = np.linspace(0, hauteur, nombre_points_v)
        U, V = np.meshgrid(u, v)
        
        # Coordonnées du cylindre ou de l'ellipse en position couchée (longueur sur l'axe Y)
        X = rayon * np.cos(U)
        Y = V
        Z = r_vertical * np.sin(U)
        
        # Création de la figure 3D
        fig_3d = go.Figure()
        
        # Ajout de la surface de la cuve
        fig_3d.add_trace(go.Surface(
            x=X, y=Y, z=Z, 
            colorscale='Blues', 
            showscale=False, 
            opacity=0.8,
            name="Citerne"
        ))
        
        # Ajout des fonds (couvercles) pour fermer la cuve visuellement
        fig_3d.add_trace(go.Surface(x=X[0,:], y=np.zeros_like(X[0,:]), z=Z[0,:], colorscale='Blues', showscale=False, opacity=0.9))
        fig_3d.add_trace(go.Surface(x=X[-1,:], y=np.full_like(X[-1,:], hauteur), z=Z[-1,:], colorscale='Blues', showscale=False, opacity=0.9))
        
        # Configuration des axes pour garder des proportions carrées (isométrie)
        fig_3d.update_layout(
            scene=dict(
                xaxis=dict(title='Largeur (X) en m', range=[-2, 2]),
                yaxis=dict(title='Longueur (Y) en m', range=[0, 16]),
                zaxis=dict(title='Hauteur (Z) en m', range=[-2, 2]),
                aspectratio=dict(x=1, y=2, z=1)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=500
        )
        
        st.plotly_chart(fig_3d, use_container_width=True)

    verrou_cuve_1 = st.session_state.get("cuve_verrouille_tab1", False)

    # Appel de la fonction de questionnaire pour la géométrie de la cuve
    res_q1, res_t1 = afficher_questions_cuve_dynamiques(
        forme=forme, 
        rayon=rayon, 
        hauteur=hauteur, 
        aire_section=aire_section, 
        volume_total=volume_total, 
        verrouille=verrou_cuve_1
    )

    st.write("---")
    st.subheader("Généralités sur les dimensions et la géométrie de la cuve")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_cuve1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_cuve1_official", 
        disabled=verrou_cuve_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_cuve1_official_net", use_container_width=True, disabled=verrou_cuve_1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_cuve1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz de gauche mélangé (10 questions)
            score_q1 = 0.0
            if "ordre_quiz_cuve" in st.session_state:
                for q_item in st.session_state.ordre_quiz_cuve:
                    reponse_eleve = st.session_state.get(f"cuve_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous de droite (10 points)
            score_t1 = sum([
                st.session_state.get("cuve_t1_s1") == forme,
                st.session_state.get("cuve_t2_s1") == f"{rayon:.2f} m",
                st.session_state.get("cuve_t3_s1") == f"{hauteur:.2f} m",
                st.session_state.get("cuve_t4_s1") == f"{aire_section:.2f} m²",
                st.session_state.get("cuve_t5_s1") == f"{volume_total:.2f} m³",
                st.session_state.get("cuve_t6_s1") == "Longueur",
                st.session_state.get("cuve_t7_s1") == "Plotly",
                st.session_state.get("cuve_t8_s1") == "Elliptique",
                st.session_state.get("cuve_t9_s1") == "Meshgrid",
                st.session_state.get("cuve_t10_s1") == "1000"
            ])

            st.session_state.score_cuve1_p1 = round(float(score_q1), 1)
            st.session_state.score_cuve1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_cuve1 = round(float(score_q1 + score_t1), 1)
            st.session_state.cuve_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("cuve_verrouille_tab1", False):
        scr1 = st.session_state.get("score_cuve1_p1", 0.0)
        scr2 = st.session_state.get("score_cuve1_p2", 0.0)
        tot_s = st.session_state.get("score_final_cuve1", 0.0)

        from datetime import datetime
        timestamp_cuve1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DIMENSIONNEMENT CUVE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_cuve1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Géométrie Cuve - {n_eleve}</title>
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
                <p>Atelier 1 : Analyse géométrique et modélisation tridimensionnelle de la cuve</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_cuve1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz de Géométrie : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse de la citerne : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_cuve" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_cuve, 1):
                saisie = st.session_state.get(f"cuve_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_cuve1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cuve1 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_cuve = [
            ("1. La forme actuellement configurée et visible sur le dessin tridimensionnel est un", st.session_state.get("cuve_t1_s1"), forme),
            ("2. Le rayon horizontal ou demi-grand axe défini par le curseur de réglage est de", st.session_state.get("cuve_t2_s1"), f"{rayon:.2f} m"),
            ("3. La longueur de la structure cylindrique qui s'étend sur la coordonnée Y vaut", st.session_state.get("cuve_t3_s1"), f"{hauteur:.2f} m"),
            ("4. La surface plane calculée pour la section de cette enveloppe extérieure s'élève à", st.session_state.get("cuve_t4_s1"), f"{aire_section:.2f} m²"),
            ("5. L'espace volumétrique disponible à l'intérieur de la citerne représente", st.session_state.get("cuve_t5_s1"), f"{volume_total:.2f} m³"),
            ("6. Pour obtenir le volume de stockage, on multiplie la surface de la section par la", st.session_state.get("cuve_t6_s1"), "Longueur"),
            ("7. La bibliothèque Python utilisée pour tracer la surface bleue interactive s'appelle", st.session_state.get("cuve_t7_s1"), "Plotly"),
            ("8. Une cuve dont l'axe vertical est plus petit que l'axe horizontal possède une section", st.session_state.get("cuve_t8_s1"), "Elliptique"),
            ("9. Le maillage géométrique 3D s'appuie sur une grille de points générée par la fonction", st.session_state.get("cuve_t9_s1"), "Meshgrid"),
            ("10. La capacité maximale en litres se déduit en multipliant les mètres cubes par", st.session_state.get("cuve_t10_s1"), "1000")
        ]

        for num, (enonce, saisie, attendu) in enumerate(phrases_trous_cuve, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_cuve1 += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cuve1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px;">
                Application d'Etude de Camion-Citerne - Module de Validation Academique
            </div>
        </body>
        </html>
        """

        # Generation dynamique du nom de fichier
        nom_f1 = f"Rapport_Atelier1_Cuve_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace(" ", "_")

        # Bouton officiel de telechargement du rapport HTML
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_cuve1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Étude Statique, Répartition des Charges & Cloisonnement")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Choix des Matériaux & Châssis")
        materiau = st.selectbox("Matériau de la cuve", ["Acier Inoxydable (7850 kg/m³)", "Aluminium (2700 kg/m³)"])
        rho_mat = 7850 if "Acier" in materiau else 2700
        epaisseur = st.slider("Épaisseur de la tôle (mm)", 3, 10, 5) / 1000
        
        st.subheader("Paramètres des Chicanes Anti-bélier")
        nb_chicanes = st.slider("Nombre de cloisons / chicanes internes", 0, 8, 3)
        taux_perforation = st.slider("Taux de perforation de la chicane (%)", 10, 50, 30) / 100
        
        # Estimation de la masse à vide (Cylindre/Ellipse + Cloisons)
        perimetre = 2 * np.pi * np.sqrt(((rayon**2) + (r_vertical**2)) / 2)
        masse_enveloppe = perimetre * hauteur * epaisseur * rho_mat
        masse_cloisons = nb_chicanes * aire_section * (1 - taux_perforation) * epaisseur * rho_mat
        masse_cuve_vide = masse_enveloppe + masse_cloisons
        
        masse_chassis = st.number_input("Masse estimée du châssis + tracteur (kg)", value=7000)
        
        st.subheader("Configuration Géométrique du Véhicule")
        L_empattement = st.slider("Empattement entre Essieu Avant et Essieu Arrière (m)", 4.0, 10.0, 6.5, 0.5)
        d_cg = st.slider("Distance du Centre de Gravité de la cuve par rapport à l'essieu avant (m)", 1.0, L_empattement, L_empattement/2, 0.1)
        h_chassis = st.slider("Hauteur du châssis par rapport au sol (m)", 0.8, 1.4, 1.1, 0.05)

    with col2:
        st.subheader("Bilan des Masses (PFD Statique au repos)")
        st.write(f"Masse de l'enveloppe extérieure : {masse_enveloppe:.0f} kg")
        st.write(f"Masse des cloisons anti-bélier : {masse_cloisons:.0f} kg")
        st.markdown(f"**Masse totale de la cuve à vide :** `{masse_cuve_vide:.0f} kg`")

        # =========================================================================
        # SCHÉMA GRAPHIQUE INTERACTIF EN 3D DES FORCES (CORRIGÉ ET SÉCURISÉ)
        # =========================================================================
        # =========================================================================
        # APPAREIL DE RENDU ET ANIMATION 3D LIVE PLOTLY (TAB 3)
        # =========================================================================
        st.subheader("Animation 3D en temps réel de l'ondulation du fluide")
        
        # Bouton d'activation de la simulation dynamique
        run_animation = st.checkbox("Activer l'animation de la vague en direct", value=False)
        
        # Création d'un emplacement vide réactif Streamlit pour injecter les images en boucle
        conteneur_graphique_3d = st.empty()

        # Coordonnées de base (Axe Y longitudinal)
        x_centre = 0.0
        y_debut_cuve = 1.5
        y_fin_cuve = y_debut_cuve + hauteur
        y_essieu_avant = y_debut_cuve
        y_essieu_arriere = y_essieu_avant + L_empattement
        y_cg_stat = y_essieu_avant + d_cg
        z_sol_roues = 0.4

        # Maillage extérieur fixe de la citerne
        n_u, n_v = 20, 20
        u_arr = np.linspace(0, 2 * np.pi, n_u)
        v_arr = np.linspace(y_debut_cuve, y_fin_cuve, n_v)
        U_mesh, V_mesh = np.meshgrid(u_arr, v_arr)
        X_cuve = x_centre + rayon * np.cos(U_mesh)
        Y_cuve = V_mesh
        Z_cuve = (h_chassis + r_vertical) + r_vertical * np.sin(U_mesh)

        # Grille de calcul de la surface de la vague
        y_liq = np.linspace(y_debut_cuve, y_fin_cuve, 15)
        x_liq = np.linspace(-rayon * 0.95, rayon * 0.95, 15)
        X_liq, Y_liq = np.meshgrid(x_liq, y_liq)
        y_milieu = y_debut_cuve + (hauteur / 2.0)
        
        # Amplitude maximale de la pente (freinage)
        deceleration_statique = 0.0
        theta_max = 0.0
        pulsation = 0.0 

        # Boucle d'animation transitoire
        import time
        
        # Si le bouton n'est pas coché, on n'affiche qu'une seule image statique (pas de boucle)
        nombre_frames = 100 if run_animation else 1
        
        for frame in range(nombre_frames):
            # Calcul du pas de temps
            t = frame * 0.1
            pente_instantanee = theta_max * np.cos(pulsation * t)
            
            # 1. Calcul de la surface de la vraie vague ondulante
            r_hauteur_reference = r_vertical if 'r_vertical' in locals() or hasattr(self, 'r_vertical') else rayon
            Z_liq = (h_chassis + (2 * r_hauteur_reference)) + (Y_liq - y_milieu) * np.sin(0.0)
            Z_liq = np.clip(Z_liq, h_chassis, h_chassis + (2 * r_vertical))
            
            # 2. Calcul du transfert de charge dynamique lié à la position de la vague
            delta_y_cg = 0.0
            y_cg_dynamique = y_cg_stat if 'y_cg_stat' in locals() else (1.0 + d_cg)
            poids_secours = 25000.0 * 9.81
            if 'poids_calculer' in locals():
                poids_secours = poids_calculer

            # Définition des forces instantanées statiques sécurisées
            Poids_dynamique = poids_secours
            delta_y_cg = 0.0

            if 'F_avant_local' in locals():
                F_avant_instant = F_avant_local
            else:
                F_avant_instant = (poids_secours * (L_empattement - d_cg)) / L_empattement if ('L_empattement' in locals() and 'd_cg' in locals()) else (poids_secours / 2)

            if 'F_arriere_local' in locals():
                F_arriere_instant = F_arriere_local
            else:
                F_arriere_instant = poids_secours - F_avant_instant

            fig_3d_stat = go.Figure()

            # # Enveloppe transparente de la cuve
            fig_3d_stat.add_trace(go.Surface(x=X_cuve, y=Y_cuve, z=Z_cuve, colorscale='Blues', showscale=False, opacity=0.15, name="Cuve"))

            # # Surface du liquide au repos (Bleu cyan saturé)
            fig_3d_stat.add_trace(go.Surface(
                x=X_liq, y=Y_liq, z=Z_liq,
                colorscale=[[0, 'rgba(0, 180, 255, 0.7)'], [1, 'rgba(0, 180, 255, 0.7)']],
                showscale=False, name="Liquide"
            ))
            x_cab = [-0.8, 0.8, 0.8, -0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8]
            y_cab = [0.0, 0.0, 1.4, 1.4, 0.0, 0.0, 0.0, 1.4, 1.4, 0.0]
            z_cab = [h_chassis, h_chassis, h_chassis, h_chassis, h_chassis, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8]
            fig_3d_stat.add_trace(go.Scatter3d(x=x_cab, y=y_cab, z=z_cab, mode='lines', line=dict(color='gray', width=3), showlegend=False))

            # Châssis (Longerons noirs)
            fig_3d_stat.add_trace(go.Scatter3d(x=[-0.6, -0.6], y=[0.0, y_fin_cuve + 0.2], z=[h_chassis, h_chassis], mode='lines', line=dict(color='black', width=4), showlegend=False))
            fig_3d_stat.add_trace(go.Scatter3d(x=[0.6, 0.6], y=[0.0, y_fin_cuve + 0.2], z=[h_chassis, h_chassis], mode='lines', line=dict(color='black', width=4), showlegend=False))

            # Roues du véhicule
            fig_3d_stat.add_trace(go.Scatter3d(x=[-0.8, 0.8, -0.8, 0.8], y=[y_essieu_avant, y_essieu_avant, y_essieu_arriere, y_essieu_arriere], z=[z_sol_roues, z_sol_roues, z_sol_roues, z_sol_roues], mode='markers', marker=dict(size=5, color='black'), showlegend=False))

            # Vecteurs Forces Statiques (Symboles 'circle' sécurisés pour le Cloud)
            scale_f_3d = 0.00003
            
            # Poids constant au repos
            z_cg_total = z_cg_local if 'z_cg_local' in locals() else (h_chassis + r_vertical if hasattr(self, 'r_vertical') else 2.1)
            z_fin_poids = z_cg_total - (Poids_dynamique * scale_f_3d)
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre, x_centre], y=[y_cg_dynamique, y_cg_dynamique], z=[z_cg_total, z_fin_poids], mode='lines', line=dict(color='red', width=5), name="Poids", showlegend=True))
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre], y=[y_cg_dynamique], z=[z_fin_poids], mode='markers', marker=dict(size=7, color='red', symbol='circle'), showlegend=False))
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre], y=[y_cg_dynamique], z=[z_cg_total], mode='markers', marker=dict(size=5, color='red', symbol='cross'), showlegend=False))

            # Appui Avant Statique
            z_fin_favant = z_sol_roues + (F_avant_instant * scale_f_3d)
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre, x_centre], y=[y_essieu_avant, y_essieu_avant], z=[z_sol_roues, z_fin_favant], mode='lines', line=dict(color='green', width=5), name="F_Avant", showlegend=True))
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre], y=[y_essieu_avant], z=[z_fin_favant], mode='markers', marker=dict(size=7, color='green', symbol='circle'), showlegend=False))

            # Appui Arrière Statique
            z_fin_farriere = max(z_sol_roues, z_sol_roues + (F_arriere_instant * scale_f_3d))
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre, x_centre], y=[y_essieu_arriere, y_essieu_arriere], z=[z_sol_roues, z_fin_farriere], mode='lines', line=dict(color='green', width=5), name="F_Arrière", showlegend=True))
            fig_3d_stat.add_trace(go.Scatter3d(x=[x_centre], y=[y_essieu_arriere], z=[z_fin_farriere], mode='markers', marker=dict(size=7, color='green', symbol='circle'), showlegend=False))

            # Configuration de la scène fixe pour éviter les sauts de caméra
            fig_3d_stat.update_layout(
                scene=dict(
                    xaxis=dict(title="Largeur (X) m", range=[-3, 3]),
                    yaxis=dict(title="Longueur (Y) m", range=[-1, y_fin_cuve + 2]),
                    zaxis=dict(title="Hauteur (Z) m", range=[0, z_cg_total + 3]),
                    aspectratio=dict(x=1, y=2, z=1)
                ),
                margin=dict(l=0, r=0, b=0, t=0),
                height=550
            )

            # Injection en temps réel de la figure Plotly dans le bloc réactif Streamlit
            conteneur_graphique_3d.plotly_chart(fig_anim, use_container_width=True, key=f"slosh_f_{frame}")
            
            # Temporisation pour caler la fluidité visuelle (environ 15 images/sec)
            if run_animation:
                time.sleep(0.06)
        
        # Note : La masse totale en charge dépendra du taux de remplissage défini dans l'onglet 3
    verrou_statique_1 = st.session_state.get("stat_verrouille_tab2", False)

    st.write("---")
    res_qs2, res_ts2 = afficher_questions_statique_dynamiques(
        materiau=materiau,
        rho_mat=rho_mat,
        epaisseur=epaisseur,
        nb_chicanes=nb_chicanes,
        taux_perforation=taux_perforation,
        L_empattement=L_empattement,
        d_cg=d_cg,
        masse_chassis=masse_chassis,
        verrouille=verrou_statique_1
    )

    st.write("---")
    st.subheader("Validation de l'Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 2.", 
        key="check_certif_stat2_official", 
        disabled=verrou_statique_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_stat2_official_net", use_container_width=True, disabled=verrou_statique_1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Statique (10 questions)
            score_q2 = 0.0
            if "ordre_quiz_statique" in st.session_state:
                for q_item in st.session_state.ordre_quiz_statique:
                    reponse_eleve = st.session_state.get(f"stat_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction du Texte à trous Statique (10 points)
            score_t2 = sum([
                st.session_state.get("stat_t1_s1") == materiau,
                st.session_state.get("stat_t2_s1") == f"{rho_mat} kg/m³",
                st.session_state.get("stat_t3_s1") == f"{epaisseur * 1000:.0f} mm",
                st.session_state.get("stat_t4_s1") == f"{nb_chicanes}",
                st.session_state.get("stat_t5_s1") == f"{taux_perforation * 100:.0f} %",
                st.session_state.get("stat_t6_s1") == "Empattement",
                st.session_state.get("stat_t7_s1") == "Nulle",
                st.session_state.get("stat_t8_s1") == f"{masse_chassis:.0f} kg",
                st.session_state.get("stat_t9_s1") == "Élevée",
                st.session_state.get("stat_t10_s1") == "Repos"
            ])

            st.session_state.score_stat2_p1 = round(float(score_q2), 1)
            st.session_state.score_stat2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_stat2 = round(float(score_q2 + score_t2), 1)
            st.session_state.stat_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("stat_verrouille_tab2", False):
        scr1 = st.session_state.get("score_stat2_p1", 0.0)
        scr2 = st.session_state.get("score_stat2_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat2", 0.0)

        from datetime import datetime
        timestamp_stat2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ETUDE STATIQUE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_stat2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statique Essieux - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e3a8a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 2 : Etude statique, choix des materiaux et calcul des charges sur essieux</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_stat2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                &bull; Note obtenue au Quiz Statique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse des charges : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_statique" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_statique, 1):
                saisie = st.session_state.get(f"stat_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_stat2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat2 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_stat = [
            ("1. Le matériau de construction retenu pour la structure est l'", st.session_state.get("stat_t1_s1"), materiau),
            ("2. La masse volumique du métal choisi est égale à", st.session_state.get("stat_t2_s1"), f"{rho_mat} kg/m³"),
            ("3. L'épaisseur nominale de la tôle de l'enveloppe est fixée à", st.session_state.get("stat_t3_s1"), f"{epaisseur * 1000:.0f} mm"),
            ("4. Pour limiter les mouvements de fluide, la cuve comporte", st.session_state.get("stat_t4_s1"), f"{nb_chicanes}"),
            ("5. Le taux de perforation de ces parois internes est égal à", st.session_state.get("stat_t5_s1"), f"{taux_perforation * 100:.0f} %"),
            ("6. La distance séparant les deux groupes d'essieux s'appelle l'", st.session_state.get("stat_t6_s1"), "Empattement"),
            ("7. Au repos, la somme des moments des forces par rapport à un point est", st.session_state.get("stat_t7_s1"), "Nulle"),
            ("8. La masse du châssis et du tracteur seul a été estimée à", st.session_state.get("stat_t8_s1"), f"{masse_chassis:.0f} kg"),
            ("9. Plus le matériau choisi est dense, plus la masse à vide de la cuve sera", st.session_state.get("stat_t9_s1"), "Élevée"),
            ("10. Le calcul de la répartition des charges sur les essieux s'effectue au", st.session_state.get("stat_t10_s1"), "Repos")
        ]

        for num, (enonce, saisie, attendu) in enumerate(phrases_trous_stat, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat2 += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_stat2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px;">
                Application d'Etude de Camion-Citerne - Module de Validation Academique
            </div>
        </body>
        </html>
        """

        nom_f2 = f"Rapport_Atelier2_Statique_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace(" ", "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_stat2,
            file_name=f"{nom_f2}.html",
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Étude Dynamique, Ballottement & Transfert de Charge")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("État de Remplissage")
        taux_remplissage = st.slider("Taux de remplissage de la cuve (%)", 5, 95, 70, 5)
        
        # Calcul précis de la hauteur de liquide et de la surface libre via l'aire tronquée
        # Modélisation par angle paramétrique t pour une hauteur h = r_vertical * (1 - cos(t))
        t_remplissage = taux_remplissage / 100.0
        
        # Approximation numérique de l'angle d'ouverture pour le niveau du fluide
        # Résolution de l'aire d'un segment de cercle / ellipse : t - sin(t)*cos(t) = pi * taux
        angles = np.linspace(0, np.pi, 500)
        aires_relatives = (angles - np.sin(angles) * np.cos(angles)) / np.pi
        idx = np.abs(aires_relatives - t_remplissage).argmin()
        t_angle = angles[idx]
        
        h_liquide = r_vertical * (1 - np.cos(t_angle))
        
        # Calcul de la masse effective du fluide
        masse_fluide_actuelle = volume_total * t_remplissage * rho
        masse_totale_en_charge = masse_cuve_vide + masse_chassis + masse_fluide_actuelle
        
        st.subheader("Dynamique de Véhicule & Freinage")
        deceleration = st.slider("Décélération demandée au freinage (m/s²)", 0.0, 8.0, 3.0, 0.2)
        mu_sol = st.slider("Coefficient d'adhérence des pneumatiques (sec=0.8, mouillé=0.4)", 0.2, 0.9, 0.7, 0.05)

        # Calculs physiques dynamiques
        g = 9.81
        # Position du centre de gravité vertical combiné (approximation simplifiée avec liquide)
        z_cg_liquide = h_chassis + (h_liquide / 2) # Centre de gravité approché du fluide
        z_cg_total = ((masse_chassis * h_chassis) + (masse_cuve_vide * (h_chassis + r_vertical)) + (masse_fluide_actuelle * z_cg_liquide)) / masse_totale_en_charge

        # Poids total
        Poids_dynamique = masse_totale_en_charge * g
        
        # Transfert de charge dynamique au freinage (PFD longitudinal)
        # F_avant_dyn = Poids * (L - d_cg)/L + (Masse_totale * deceleration * z_cg_total) / L
        F_avant_stat = (Poids_dynamique * (L_empattement - d_cg)) / L_empattement
        F_arriere_stat = Poids_dynamique - F_avant_stat
        
        delta_F = (masse_totale_en_charge * deceleration * z_cg_total) / L_empattement
        
        F_avant_dyn = F_avant_stat + delta_F
        F_arriere_dyn = F_arriere_stat - delta_F
        
        # Limites dynamiques
        # 1. Limite de retournement / décollage essieu arrière (F_arriere_dyn = 0)
        deceleration_retournement = (F_arriere_stat * L_empattement) / (masse_totale_en_charge * z_cg_total)
        
        # 2. Limite de blocage des roues (liée à l'adhérence)
        deceleration_blocage = mu_sol * g

        # Calcul de la fréquence propre longitudinale de ballottement
        omega2 = (g * np.pi / hauteur) * np.tanh(np.pi * h_liquide / hauteur)
        f_ballottement = np.sqrt(omega2) / (2 * np.pi)

    with col2:
        st.subheader("Analyse des Limites Physiques")
        st.write(f"Masse effective du liquide : {masse_fluide_actuelle/1000:.2f} Tonnes")
        st.write(f"Masse Totale en Charge Réelle : {masse_totale_en_charge/1000:.2f} Tonnes")
        st.write(f"Hauteur combinée du Centre de Gravité (Z_CG) : {z_cg_total:.2f} m")
        
        st.subheader("Répartition Dynamique des Forces sous Décélération")
        st.write(f"Force Essieu Avant : Stat: {F_avant_stat/1000:.1f} kN -> Dyn: {F_avant_dyn/1000:.1f} kN")
        st.write(f"Force Essieu Arrière : Stat: {F_arriere_stat/1000:.1f} kN -> Dyn: {F_arriere_dyn/1000:.1f} kN")
        
        st.subheader("Diagnostics Critiques")
        
        # Alerte Adhérence / Blocage
        if deceleration > deceleration_blocage:
            st.error(f"Glissement / Blocage des roues détecté. La décélération maximale supportée par l'adhérence actuelle est de {deceleration_blocage:.2f} m/s².")
        else:
            st.success(f"Adhérence suffisante. Les pneus transmettent l'effort de freinage au sol.")
            
        # Alerte Retournement longitudinal
        if F_arriere_dyn <= 0:
            st.error("Danger de décollage de l'essieu arrière. Risque imminent de retournement du véhicule.")
        else:
            st.write(f"Décélération limite avant décollage de l'essieu arrière : {deceleration_retournement:.2f} m/s²")

        # Alerte Fréquence de Ballottement
        st.write(f"Fréquence de ballottement longitudinal : {f_ballottement:.3f} Hz")
        if 0.4 <= f_ballottement <= 0.7:
            st.warning("La fréquence de ballottement est proche de la zone critique routière (0.5 - 0.6 Hz). Risque accru d'amplification des oscillations en conduite transitoire.")


        # =========================================================================
        # SCHÉMA GRAPHIQUE INTERACTIF EN 3D DES FORCES DYNAMIQUES (TAB 3)
        # =========================================================================
        st.subheader("Visualisation Tridimensionnelle Dynamique et Transfert de Fluide")

        # Reprise sécurisée des coordonnées et dimensions longitudinales (Axe Y)
        x_centre = 0.0
        y_debut_cuve = 1.5
        y_fin_cuve = y_debut_cuve + hauteur
        y_essieu_avant = y_debut_cuve
        y_essieu_arriere = y_essieu_avant + L_empattement
        y_cg_stat = y_essieu_avant + d_cg
        z_sol_roues = 0.4

        fig_3d_dyn = go.Figure()

        # 1. Génération du maillage 3D de la citerne extérieure (Enveloppe bleue transparente)
        n_u, n_v = 30, 30
        u_arr = np.linspace(0, 2 * np.pi, n_u)
        v_arr = np.linspace(y_debut_cuve, y_fin_cuve, n_v)
        U_mesh, V_mesh = np.meshgrid(u_arr, v_arr)
        
        X_cuve = x_centre + rayon * np.cos(U_mesh)
        Y_cuve = V_mesh
        Z_cuve = (h_chassis + r_vertical) + r_vertical * np.sin(U_mesh)

        # Ajout de l'enveloppe de la citerne
        fig_3d_dyn.add_trace(go.Surface(x=X_cuve, y=Y_cuve, z=Z_cuve, colorscale='Blues', showscale=False, opacity=0.3, name="Cuve"))

        # 2. Modélisation de la surface libre inclinée du liquide (Effet de la décélération)
        # Angle d'inclinaison de la surface libre : tan(theta) = deceleration / g
        theta = np.arctan(deceleration / 9.81)
        
        # Grille de la surface du liquide à l'intérieur de la cuve
        y_liq = np.linspace(y_debut_cuve, y_fin_cuve, 20)
        x_liq = np.linspace(-rayon * 0.95, rayon * 0.95, 20)
        X_liq, Y_liq = np.meshgrid(x_liq, y_liq)
        
        # Calcul de l'altitude Z du fluide intégrant la hauteur moyenne et la pente de freinage
        # Le pivot de l'inclinaison se situe au centre longitudinal de la cuve : (y_debut_cuve + hauteur / 2)
        y_milieu = y_debut_cuve + (hauteur / 2.0)
        Z_liq = (h_chassis + h_liquide) + (Y_liq - y_milieu) * np.sin(theta)
        
        # Limitation stricte du tracé du liquide pour ne pas déborder du plafond ou du fond de la cuve
        z_plafond_max = h_chassis + (2 * r_vertical)
        Z_liq = np.clip(Z_liq, h_chassis, z_plafond_max)

        # Ajout de la surface du liquide en mouvement (Teinte aquatique)
        fig_3d_dyn.add_trace(go.Surface(
            x=X_liq, y=Y_liq, z=Z_liq, 
            colorscale=[[0, 'rgba(0, 128, 255, 0.6)'], [1, 'rgba(0, 128, 255, 0.6)']], 
            showscale=False, name="Surface Fluide"
        ))

        # 3. Dessin de la cabine avant du tracteur
        x_cab = [-0.8, 0.8, 0.8, -0.8, -0.8, -0.8, 0.8, 0.8, -0.8, -0.8]
        y_cab = [0.0, 0.0, 1.4, 1.4, 0.0, 0.0, 0.0, 1.4, 1.4, 0.0]
        z_cab = [h_chassis, h_chassis, h_chassis, h_chassis, h_chassis, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8, h_chassis + 1.8]
        fig_3d_dyn.add_trace(go.Scatter3d(x=x_cab, y=y_cab, z=z_cab, mode='lines', line=dict(color='gray', width=4), name="Cabine"))

        # 4. Dessin des longerons du Châssis (Double structure noire)
        fig_3d_dyn.add_trace(go.Scatter3d(x=[-0.6, -0.6], y=[0.0, y_fin_cuve + 0.2], z=[h_chassis, h_chassis], mode='lines', line=dict(color='black', width=5), showlegend=False))
        fig_3d_dyn.add_trace(go.Scatter3d(x=[0.6, 0.6], y=[0.0, y_fin_cuve + 0.2], z=[h_chassis, h_chassis], mode='lines', line=dict(color='black', width=5), showlegend=False))

        # 5. Dessin des roues du véhicule
        fig_3d_dyn.add_trace(go.Scatter3d(x=[-0.8, 0.8, -0.8, 0.8], y=[y_essieu_avant, y_essieu_avant, y_essieu_arriere, y_essieu_arriere], z=[z_sol_roues, z_sol_roues, z_sol_roues, z_sol_roues], mode='markers', marker=dict(size=6, color='black'), name="Roues"))

        # 6. Modélisation vectorielle des forces dynamiques (Lignes + Points terminaux fixes valides)
        scale_f_3d = 0.00003
        
        # --- VECTEUR POIDS COMBINÉ DYNAMIQUE (Rouge, vers le bas) ---
        z_fin_poids = z_cg_total - (Poids_dynamique * scale_f_3d)
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre, x_centre], y=[y_cg_stat, y_cg_stat], z=[z_cg_total, z_fin_poids],
            mode='lines', line=dict(color='red', width=6), name=f"Poids ({Poids_dynamique/1000:.1f} kN)"
        ))
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre], y=[y_cg_stat], z=[z_fin_poids],
            mode='markers', marker=dict(size=8, color='red', symbol='circle'), showlegend=False
        ))
        fig_3d_dyn.add_trace(go.Scatter3d(x=[x_centre], y=[y_cg_stat], z=[z_cg_total], mode='markers', marker=dict(size=6, color='red', symbol='cross'), showlegend=False))

        # --- VECTEUR RÉACTION ESSIEU AVANT MODIFIÉ (Vert, vers le haut, allongé par le transfert) ---
        z_fin_favant = z_sol_roues + (F_avant_dyn * scale_f_3d)
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre, x_centre], y=[y_essieu_avant, y_essieu_avant], z=[z_sol_roues, z_fin_favant],
            mode='lines', line=dict(color='green', width=6), name=f"F_Avant Dyn ({F_avant_dyn/1000:.1f} kN)"
        ))
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre], y=[y_essieu_avant], z=[z_fin_favant],
            mode='markers', marker=dict(size=8, color='green', symbol='circle'), showlegend=False
        ))

        # --- VECTEUR RÉACTION ESSIEU ARRIÈRE MODIFIÉ (Vert, vers le haut, raccourci par le transfert) ---
        z_fin_farriere = max(z_sol_roues, z_sol_roues + (F_arriere_dyn * scale_f_3d))
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre, x_centre], y=[y_essieu_arriere, y_essieu_arriere], z=[z_sol_roues, z_fin_farriere],
            mode='lines', line=dict(color='green', width=6), name=f"F_Arrière Dyn ({F_arriere_dyn/1000:.1f} kN)"
        ))
        fig_3d_dyn.add_trace(go.Scatter3d(
            x=[x_centre], y=[y_essieu_arriere], z=[z_fin_farriere],
            mode='markers', marker=dict(size=8, color='green', symbol='circle'), showlegend=False
        ))

        # Configuration de l'univers spatial tridimensionnel (Isométrie Y majeure)
        fig_3d_dyn.update_layout(
            scene=dict(
                xaxis=dict(title="Largeur (X) en m", range=[-3, 3]),
                yaxis=dict(title="Longueur (Y) en m", range=[-1, y_fin_cuve + 2]),
                zaxis=dict(title="Hauteur (Z) en m", range=[0, z_cg_total + 3]),
                aspectratio=dict(x=1, y=2, z=1)
            ),
            margin=dict(l=0, r=0, b=0, t=0),
            height=600
        )

        st.plotly_chart(fig_3d_dyn, use_container_width=True)


    verrou_dynamique_1 = st.session_state.get("dyn_verrouille_tab3", False)

    st.write("---")
    res_qd3, res_td3 = afficher_questions_dynamique_freinage(
        taux_remplissage=taux_remplissage,
        h_liquide=h_liquide,
        masse_fluide_actuelle=masse_fluide_actuelle,
        masse_totale_en_charge=masse_totale_en_charge,
        deceleration=deceleration,
        mu_sol=mu_sol,
        z_cg_total=z_cg_total,
        f_ballottement=f_ballottement,
        verrouille=verrou_dynamique_1
    )

    st.write("---")
    st.subheader("Validation de l'Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_dyn3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.", 
        key="check_certif_dyn3_official", 
        disabled=verrou_dynamique_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_dyn3_official_net", use_container_width=True, disabled=verrou_dynamique_1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_dyn3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Dynamique (10 questions)
            score_q3 = 0.0
            if "ordre_quiz_dynamique" in st.session_state:
                for q_item in st.session_state.ordre_quiz_dynamique:
                    reponse_eleve = st.session_state.get(f"dyn_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # 2. Correction du Texte à trous Dynamique (10 points)
            score_t3 = sum([
                st.session_state.get("dyn_t1_s1") == "100 %",
                st.session_state.get("dyn_t2_s1") == f"{h_liquide:.2f} m",
                st.session_state.get("dyn_t3_s1") == f"{masse_fluide_actuelle/1000:.2f} t",
                st.session_state.get("dyn_t4_s1") == f"{masse_totale_en_charge/1000:.2f} t",
                st.session_state.get("dyn_t5_s1") == f"{deceleration:.2f} m/s²",
                st.session_state.get("dyn_t6_s1") == f"{mu_sol:.2f}",
                st.session_state.get("dyn_t7_s1") == f"{z_cg_total:.2f} m",
                st.session_state.get("dyn_t8_s1") == f"{f_ballottement:.3f} Hz",
                st.session_state.get("dyn_t9_s1") == "Avant",
                st.session_state.get("dyn_t10_s1") == "Blocage"
            ])

            st.session_state.score_dyn3_p1 = round(float(score_q3), 1)
            st.session_state.score_dyn3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_dyn3 = round(float(score_q3 + score_t3), 1)
            st.session_state.dyn_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("dyn_verrouille_tab3", False):
        scr1 = st.session_state.get("score_dyn3_p1", 0.0)
        scr2 = st.session_state.get("score_dyn3_p2", 0.0)
        tot_s = st.session_state.get("score_final_dyn3", 0.0)

        from datetime import datetime
        timestamp_dyn3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ETUDE DYNAMIQUE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_dyn3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dynamique Freinage - {n_eleve}</title>
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
                <p>Atelier 3 : Etude dynamique, ballottement et transfert de charge sous deceleration</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_dyn3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Dynamique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse du freinage : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_dynamique" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_dynamique, 1):
                saisie = st.session_state.get(f"dyn_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dyn3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_dyn3 += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_dyn = [
            ("1. Le ballottement se produit lorsque le taux de remplissage est inférieur à", st.session_state.get("dyn_t1_s1"), "100 %"),
            ("2. Le niveau de fluide atteint une hauteur intérieure de sécurité mesurée à", st.session_state.get("dyn_t2_s1"), f"{h_liquide:.2f} m"),
            ("3. La masse nette de liquide transportée pour cette session est estimée à", st.session_state.get("dyn_t3_s1"), f"{masse_fluide_actuelle/1000:.2f} t"),
            ("4. La masse totale du camion en ordre de marche sous charge vaut", st.session_state.get("dyn_t4_s1"), f"{masse_totale_en_charge/1000:.2f} t"),
            ("5. La valeur de la décélération linéaire appliquée lors de la simulation est de", st.session_state.get("dyn_t5_s1"), f"{deceleration:.2f} m/s²"),
            ("6. Le coefficient d'adhérence caractérisant le contact entre le pneu et le sol vaut", st.session_state.get("dyn_t6_s1"), f"{mu_sol:.2f}"),
            ("7. La hauteur globale calculée du centre de gravité par rapport au sol est de", st.session_state.get("dyn_t7_s1"), f"{z_cg_total:.2f} m"),
            ("8. La fréquence propre de ballottement longitudinal calculée est égale à", st.session_state.get("dyn_t8_s1"), f"{f_ballottement:.3f} Hz"),
            ("9. Lors d'un freinage d'urgence, la charge verticale migre vers l'essieu", st.session_state.get("dyn_t9_s1"), "Avant"),
            ("10. Si la décélération dépasse la limite calculée, les roues subissent un", st.session_state.get("dyn_t10_s1"), "Blocage")
        ]

        for num, (enonce, saisie, attendu) in enumerate(phrases_trous_dyn, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_dyn3 += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_dyn3 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 10px;">
                Application d'Etude de Camion-Citerne - Module de Validation Academique
            </div>
        </body>
        </html>
        """
        nom_f3 = f"Rapport_Atelier3_Dynamique_{n_eleve}_{p_eleve}_{c_eleve}".replace("/", "_").replace(" ", "_")

        # Bouton officiel de telechargement du rapport HTML pour l'Atelier 3
        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 3 SUR VOTRE ORDINATEUR",
            data=html_export_dyn3,
            file_name=f"{nom_f3}.html",
            mime="text/html",
            use_container_width=True
        )










