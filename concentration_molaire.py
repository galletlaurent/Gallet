# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP la concentration molaire",
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
st.title("TP la concentration molaire ")
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
    
import random

# Initialisation de la banque de données anti-triche de 25 produits différents
if "banque_produits" not in st.session_state:
    st.session_state.banque_produits = [
        {"nom": "Hydroxyde de sodium (Soude)", "formule": "NaOH", "img": "hydroxyde de sodium.jpg", "cm_mere": 400.0, "danger": "Corrosif (GHS05)"},
        {"nom": "Acide chlorhydrique", "formule": "HCl", "img": "acide_chlorhydrique.jpg", "cm_mere": 365.0, "danger": "Corrosif et Irritant (GHS05, GHS07)"},
        {"nom": "Sulfate de cuivre", "formule": "CuSO4", "img": "sulfate_cuivre.jpg", "cm_mere": 160.0, "danger": "Nocif et Dangereux pour l'environnement (GHS07, GHS09)"},
        {"nom": "Permanganate de potassium", "formule": "KMnO4", "img": "permanganate.jpg", "cm_mere": 32.0, "danger": "Comburant et Corrosif (GHS03, GHS05)"},
        {"nom": "Acide sulfurique", "formule": "H2SO4", "img": "acide_sulfurique.jpg", "cm_mere": 980.0, "danger": "Corrosif majeur (GHS05)"},
        {"nom": "Nitrate d'argent", "formule": "AgNO3", "img": "nitrate_argent.jpg", "cm_mere": 170.0, "danger": "Corrosif et Toxique environnement (GHS05, GHS09)"},
        {"nom": "Ethanol", "formule": "C2H5OH", "img": "ethanol.jpg", "cm_mere": 789.0, "danger": "Inflammable (GHS02)"},
        {"nom": "Méthanol", "formule": "CH3OH", "img": "methanol.jpg", "cm_mere": 792.0, "danger": "Inflammable et Toxique aigu (GHS02, GHS06)"},
        {"nom": "Acide acétique", "formule": "CH3COOH", "img": "acide_acetique.jpg", "cm_mere": 105.0, "danger": "Inflammable et Corrosif (GHS02, GHS05)"},
        {"nom": "Chlorure de sodium", "formule": "NaCl", "img": "chlorure_sodium.jpg", "cm_mere": 300.0, "danger": "Aucun pictogramme requis (Faible risque)"},
        {"nom": "Glucose", "formule": "C6H12O6", "img": "glucose.jpg", "cm_mere": 200.0, "danger": "Aucun pictogramme requis (Faible risque)"},
        {"nom": "Iode (Solution de Lugol)", "formule": "I2", "img": "iode.jpg", "cm_mere": 25.0, "danger": "Nocif pour la santé (GHS07, GHS08)"},
        {"nom": "Eau oxygénée", "formule": "H2O2", "img": "eau_oxygenee.jpg", "cm_mere": 110.0, "danger": "Comburant et Corrosif (GHS03, GHS05)"},
        {"nom": "Ammoniaque", "formule": "NH3", "img": "ammoniaque.jpg", "cm_mere": 250.0, "danger": "Corrosif et Toxique aquatique (GHS05, GHS09)"},
        {"nom": "Cyclohexane", "formule": "C6H12", "img": "cyclohexane.jpg", "cm_mere": 778.0, "danger": "Inflammable, Toxique et Dangereux environnement (GHS02, GHS08, GHS09)"},
        {"nom": "Acétone", "formule": "CH3COCH3", "img": "acetone.jpg", "cm_mere": 784.0, "danger": "Inflammable et Irritant (GHS02, GHS07)"},
        {"nom": "Chlorure de potassium", "formule": "KCl", "img": "chlorure_potassium.jpg", "cm_mere": 150.0, "danger": "Aucun pictogramme requis (Faible risque)"},
        {"nom": "Nitrate de potassium", "formule": "KNO3", "img": "nitrate_potassium.jpg", "cm_mere": 130.0, "danger": "Comburant (GHS03)"},
        {"nom": "Sulfate de magnésium", "formule": "MgSO4", "img": "sulfate_magnesium.jpg", "cm_mere": 260.0, "danger": "Aucun pictogramme requis (Faible risque)"},
        {"nom": "Dichromate de potassium", "formule": "K2Cr2O7", "img": "dichromate.jpg", "cm_mere": 49.0, "danger": "Toxique, Cancérogène, Mutagène, Reprotoxique (GHS03, GHS06, GHS08)"},
        {"nom": "Chlorure de baryum", "formule": "BaCl2", "img": "chlorure_baryum.jpg", "cm_mere": 250.0, "danger": "Toxique aigu par ingestion (GHS06)"},
        {"nom": "Acide citrique", "formule": "C6H8O7", "img": "acide_citrique.jpg", "cm_mere": 590.0, "danger": "Irritant oculaire (GHS07)"},
        {"nom": "Sulfate de zinc", "formule": "ZnSO4", "img": "sulfate_zinc.jpg", "cm_mere": 220.0, "danger": "Corrosif et Toxique environnement (GHS05, GHS09)"},
        {"nom": "Essence de térébenthine", "formule": "C10H16", "img": "terebenthine.jpg", "cm_mere": 860.0, "danger": "Inflammable, Toxique et Nocif (GHS02, GHS07, GHS08)"},
        {"nom": "Glycérol", "formule": "C3H8O3", "img": "glycerol.jpg", "cm_mere": 1260.0, "danger": "Aucun pictogramme requis (Faible risque)"}
    ]

if "syn_prod_index" not in st.session_state:
    st.session_state.syn_prod_index = random.randint(0, 24)
    st.session_state.syn_v_fille = random.choice([100.0, 250.0, 500.0])
    st.session_state.syn_facteur = random.choice([5.0, 10.0, 20.0, 50.0])
    # Données aléatoires pour la partie dissolution
    st.session_state.syn_cm_diss = random.choice([5.0, 10.0, 15.0, 25.0])
    st.session_state.syn_v_diss = random.choice([100.0, 200.0, 250.0])

prod_actif = st.session_state.banque_produits[st.session_state.syn_prod_index]
cm_mere_hasard = prod_actif["cm_mere"]
v_fille_ml_hasard = st.session_state.syn_v_fille
facteur_hasard = st.session_state.syn_facteur

cm_diss_cible = st.session_state.syn_cm_diss
v_fiole_diss = st.session_state.syn_v_diss

# Valeurs théoriques attendues pour la correction automatique
m_diss_attendue = cm_diss_cible * (v_fiole_diss / 1000.0)
cm_fille_attendue = cm_mere_hasard / facteur_hasard
v_mere_attendu_ml = v_fille_ml_hasard / facteur_hasard


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
        st.rerun()

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
    "La masse, le volume",
    "la mole et la masse molaire moléculaire", 
    "La concentration molaire C", 
    "Préparation d'une solution de concentration molaire précise",
    "Dilution et concentration molaire",
    "Exemple"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_questions_synthese_laboratoire(prod_nom, cm_mere, v_fille_choisi, facteur_choisi, m_diss_attendue, v_fiole_diss, cm_diss_cible, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_tab5" not in st.session_state:
        base_quiz_tab5 = [
            {
                "id": "syn_1",
                "q": f"Pour l'étape de pesée de la dissolution, quelle masse de solide devez-vous mesurer pour obtenir une concentration de {cm_diss_cible:.1f} g/L dans {v_fiole_diss:.0f} mL ?",
                "options": [f"{m_diss_attendue:.3f} g", f"{m_diss_attendue * 1000:.1f} g", f"{m_diss_attendue / 10:.3f} g"],
                "rep": f"{m_diss_attendue:.3f} g"
            },
            {
                "id": "syn_2",
                "q": "Dans le protocole de dissolution, quel est le rôle crucial du rinçage quantitatif à la pissette d'eau distillée ?",
                "options": ["Garantir le transfert de la totalité du soluté solide pesé sans perte de matière", "Nettoyer l'entonnoir pour le ranger proprement", "Diluer le solide avant de l'introduire dans le col"],
                "rep": "Garantir le transfert de la totalité du soluté solide pesé sans perte de matière"
            },
            {
                "id": "syn_3",
                "q": "Pour la partie dissolution, quel récipient jaugé de précision devez-vous employer pour réaliser la solution ?",
                "options": ["La fiole jaugée", "L'éprouvette graduée", "Le bécher gradué"],
                "rep": "La fiole jaugée"
            },
            {
                "id": "syn_4",
                "q": "Pour la partie dilution, quel instrument de précision permet de prélever le volume de solution mère sans erreur ?",
                "options": ["La pipette jaugée", "La pipette Pasteur", "L'éprouvette graduée"],
                "rep": "La pipette jaugée"
            },
            {
                "id": "syn_5",
                "q": f"Dans votre exercice de dilution, la solution mère commerciale de {prod_nom} est à {cm_mere:.1f} g/L. Si vous la diluez {facteur_choisi:.0f} fois, quelle sera la concentration de votre solution fille ?",
                "options": [f"{cm_mere / facteur_choisi:.2f} g/L", f"{(cm_mere / facteur_choisi) * 10:.2f} g/L", f"{(cm_mere / facteur_choisi) / 10:.2f} g/L"],
                "rep": f"{cm_mere / facteur_choisi:.2f} g/L"
            },
            {
                "id": "syn_6",
                "q": f"Pour préparer un volume final de solution fille de {v_fille_choisi:.0f} mL avec votre facteur de dilution de {facteur_choisi:.0f}x, quel volume de solution mère faut-il prélever ?",
                "options": [f"{v_fille_choisi / facteur_choisi:.2f} mL", f"{(v_fille_choisi / facteur_choisi) * 10:.1f} mL", f"{(v_fille_choisi / facteur_choisi) / 10:.3f} mL"],
                "rep": f"{v_fille_choisi / facteur_choisi:.2f} mL"
            },
            {
                "id": "syn_7",
                "q": "À quel moment précis doit-on boucher et retourner la fiole jaugée pour homogénéiser définitivement le mélange ?",
                "options": ["Une fois que le liquide a été complété goutte à goutte jusqu'au trait de jauge", "Dès l'introduction de la solution mère au fond du récipient", "Lorsque la fiole est remplie aux deux tiers environ avant l'ajustement"],
                "rep": "Une fois que le liquide a été complété goutte à goutte jusqu'au trait de jauge"
            },
            {
                "id": "syn_8",
                "q": "Comment doit-on positionner son regard par rapport au trait de jauge pour éviter l'erreur de parallaxe ?",
                "options": ["Strictement horizontal et aligné en face du trait de jauge", "Légèrement au-dessus pour observer la courbure", "Légèrement en dessous pour voir le col"],
                "rep": "Strictement horizontal et aligné en face du trait de jauge"
            },
            {
                "id": "syn_9",
                "q": "Quelle partie de la surface incurvée du liquide (ménisque) doit effleurer la ligne de graduation gravée sur le col ?",
                "options": ["La base inférieure du ménisque", "La bordure supérieure externe", "Le milieu exact de la courbure"],
                "rep": "La base inférieure du ménisque"
            },
            {
                "id": "syn_10",
                "q": "Si vous dépassez accidentellement le trait de jauge en ajoutant l'eau distillée, quelle est l'action corrective ?",
                "options": ["La solution est gâchée car trop diluée, il faut impérativement recommencer la manipulation", "Il suffit de retirer l'excès d'eau à l'aide d'une pipette Pasteur", "Le volume reste acceptable car l'erreur est minime"],
                "rep": "La solution est gâchée car trop diluée, il faut impérativement recommencer la manipulation"
            }
        ]
        copie_base = list(base_quiz_tab5)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_tab5 = copie_base

    col_q5, col_t5 = st.columns(2)

    with col_q5:
        st.markdown("##### Quiz de synthèse : Matériel et calculs (10 questions - 10 pts)")
        dict_rep_q5 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"syn_quiz_q_{q_data['id']}"
            cle_opts = f"opts_syn_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q5[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t5:
        st.markdown("##### Synthèse de cours à trous : Dissolution & Dilution (10 trous - 10 pts)")
        dict_trous_5 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La préparation d'une solution à partir d'un composé solide s'appelle la")
        with c2: dict_trous_5["t1"] = st.selectbox("", ["Choisir...", "Dissolution", "Dilution", "Pesee"], key="syn_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La préparation consistant à rajouter du solvant dans une solution concentrée est la")
        with c4: dict_trous_5["t2"] = st.selectbox("", ["Choisir...", "Dilution", "Dissolution", "Fusion"], key="syn_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour prélever la poudre solide de son flacon sans contamination, on utilise une")
        with c6: dict_trous_5["t3"] = st.selectbox("", ["Choisir...", "Spatule", "Pipette", "Coupelle"], key="syn_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. L'accessoire de sécurité indispensable placé sur la pipette pour aspirer est la")
        with c8: dict_trous_5["t4"] = st.selectbox("", ["Choisir...", "Propipette", "Pissette", "Balance"], key="syn_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le liquide à ajouter pour compléter les fioles de préparation est l'eau")
        with c10: dict_trous_5["t5"] = st.selectbox("", ["Choisir...", "Distillee", "Robinet", "Minerale"], key="syn_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. La solution initiale très concentrée utilisée au début d'une dilution est la solution")
        with c12: dict_trous_5["t6"] = st.selectbox("", ["Choisir...", "Mere", "Fille", "Pure"], key="syn_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La solution finale moins concentrée obtenue à la fin de la dilution est la solution")
        with c14: dict_trous_5["t7"] = st.selectbox("", ["Choisir...", "Fille", "Mere", "Saturee"], key="syn_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Lors de l'ajout d'eau distillée, la masse totale du soluté dissous se")
        with c16: dict_trous_5["t8"] = st.selectbox("", ["Choisir...", "Conserve", "Détruit", "Divise"], key="syn_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La ligne horizontale gravée de repère de volume sur la fiole est le trait de")
        with r18: dict_trous_5["t9"] = st.selectbox("", ["Choisir...", "Jauge", "Graduation", "Niveau"], key="syn_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour ajuster le niveau avec une extrême minutie goutte à goutte, on utilise une pipette")
        with c20: dict_trous_5["t10"] = st.selectbox("", ["Choisir...", "Pasteur", "Jaugee", "Graduee"], key="syn_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q5, dict_trous_5


def afficher_questions_dilution(c_mere, c_fille, v_fille, v_mere, facteur_f, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_dil" not in st.session_state:
        base_quiz_dil = [
            {
                "id": "dl_1", 
                "q": "Quelle grandeur physique reste rigoureusement conservée au cours d'une dilution ?", 
                "options": ["La masse de soluté", "Le volume total de liquide", "La concentration massique"], 
                "rep": "La masse de soluté"
            },
            {
                "id": "dl_2", 
                "q": f"Pour préparer votre solution fille (Cm = {c_fille:.2f} g/L) à partir de la solution mère (Cm = {c_mere:.2f} g/L), quel est le facteur de dilution F ?", 
                "options": [f"{facteur_f:.1f}", f"{facteur_f * 10:.1f}", f"{facteur_f / 10:.2f}"], 
                "rep": f"{facteur_f:.1f}"
            },
            {
                "id": "dl_3", 
                "q": f"Pour obtenir un volume de solution fille de {v_fille:.0f} mL, quel volume de solution mère (V_mère) devez-vous prélever ?", 
                "options": [f"{v_mere:.1f} mL", f"{v_mere * 10:.1f} mL", f"{v_mere / 10:.2f} mL"], 
                "rep": f"{v_mere:.1f} mL"
            },
            {
                "id": "dl_4", 
                "q": "Quelle est la verrerie de précision indispensable pour prélever le volume de solution mère ?", 
                "options": ["La pipette jaugée", "L'éprouvette graduée", "Le bécher jaugé"], 
                "rep": "La pipette jaugée"
            },
            {
                "id": "dl_5", 
                "q": "Quel accessoire de sécurité doit-on obligatoirement adapter sur une pipette pour aspirer la solution ?", 
                "options": ["Une propipette ou une poire à pipeter", "Un bouchon en caoutchouc", "Une pince métallique"], 
                "rep": "Une propipette ou une poire à pipeter"
            },
            {
                "id": "dl_6", 
                "q": "Où doit-on verser la solution mère prélevée pour fabriquer la solution fille ?", 
                "options": ["Dans une fiole jaugée", "Dans un bécher propre", "Dans une éprouvette graduée"], 
                "rep": "Dans une fiole jaugée"
            },
            {
                "id": "dl_7", 
                "q": "Pourquoi la concentration de la solution fille est-elle toujours inférieure à celle de la solution mère ?", 
                "options": ["Car on ajoute du solvant, ce qui augmente le volume total sans ajouter de matière", "Car une partie du soluté s'évapore pendant le mélange", "Car le solvant détruit les molécules de soluté"], 
                "rep": "Car on ajoute du solvant, ce qui augmente le volume total sans ajouter de matière"
            },
            {
                "id": "dl_8", 
                "q": "La formule mathématique fondamentale de la dilution est :", 
                "options": ["C_mère * V_mère = C_fille * V_fille", "C_mère * C_fille = V_mère * V_fille", "C_mère / V_mère = C_fille / V_fille"], 
                "rep": "C_mère * V_mère = C_fille * V_fille"
            },
            {
                "id": "dl_9", 
                "q": "Si le bas du ménisque dépasse le trait de jauge de la fiole fille lors de l'ajout d'eau distillée :", 
                "options": ["La concentration est trop faible, le protocole est manqué", "La solution est correcte car le volume est plus grand", "Il suffit de prélever l'excès d'eau à la pipette"], 
                "rep": "La concentration est trop faible, le protocole est manqué"
            },
            {
                "id": "dl_10", 
                "q": "Si on dilue 5 fois une solution mère de concentration 10 g/L, quelle sera la concentration de la solution fille ?", 
                "options": ["2.0 g/L", "50.0 g/L", "5.0 g/L"], 
                "rep": "2.0 g/L"
            }
        ]
        copie_base = list(base_quiz_dil)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_dil = copie_base

    col_q4, col_t4 = st.columns(2)

    with col_q4:
        st.markdown("##### Quiz sur le protocole de dilution (10 questions - 10 pts)")
        dict_rep_q4 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_dil, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dil_quiz_q_{q_data['id']}"
            cle_opts = f"opts_dil_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q4[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t4:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_4 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Diluer une solution consiste à diminuer sa concentration en y ajoutant du")
        with c2: dict_trous_4["t1"] = st.selectbox("", ["Choisir...", "Solvant", "Solute", "Concentre"], key="dil_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La solution de départ, qui possède la concentration la plus élevée, est la solution")
        with c4: dict_trous_4["t2"] = st.selectbox("", ["Choisir...", "Mere", "Fille", "Saturee"], key="dil_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La solution finale obtenue après l'ajout d'eau distillée est la solution")
        with c6: dict_trous_4["t3"] = st.selectbox("", ["Choisir...", "Fille", "Mere", "Pure"], key="dil_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Le prélèvement rigoureux du volume de solution mère s'effectue avec une pipette")
        with c8: dict_trous_4["t4"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Pasteur"], key="dil_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le nombre de fois que la solution a été diluée est caractérisé par le facteur de")
        with c10: dict_trous_4["t5"] = st.selectbox("", ["Choisir...", "Dilution", "Dissolution", "Saturation"], key="dil_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Au cours de la manipulation, la quantité et la masse de soluté se")
        with c12: dict_trous_4["t6"] = st.selectbox("", ["Choisir...", "Conservent", "Detruisent", "Multiplient"], key="dil_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La solution fille est préparée dans un récipient jaugé appelé une fiole")
        with c14: dict_trous_4["t7"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Erlenmeyer"], key="dil_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour aspirer le liquide en toute sécurité sans contact, on utilise une")
        with c16: dict_trous_4["t8"] = st.selectbox("", ["Choisir...", "Propipette", "Spatule", "Pissette"], key="dil_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le rapport des concentrations indique que le facteur F est égal à C_mère divisé par")
        with r18: dict_trous_4["t9"] = st.selectbox("", ["Choisir...", "C_fille", "V_fille", "V_mere"], key="dil_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Le rapport des volumes indique que le facteur F est égal à V_fille divisé par")
        with c20: dict_trous_4["t10"] = st.selectbox("", ["Choisir...", "V_mere", "V_fille", "C_mere"], key="dil_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q4, dict_trous_4


def afficher_questions_dissolution(m_solide, v_fiole, cm_cible, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_diss" not in st.session_state:
        base_quiz_diss = [
            {
                "id": "ds_1", 
                "q": "Quelle est la toute première étape incontournable lors de la préparation d'une solution par dissolution ?", 
                "options": ["Peser le soluté solide à l'aide d'une balance et d'une coupelle", "Remplir la fiole jaugée jusqu'au trait de jauge avec de l'eau", "Agiter la solution pour homogénéiser"], 
                "rep": "Peser le soluté solide à l'aide d'une balance et d'une coupelle"
            },
            {
                "id": "ds_2", 
                "q": f"Pour préparer votre solution actuelle (Cm = {cm_cible:.2f} g/L) dans une fiole de {v_fiole:.0f} mL, quelle masse exacte devez-vous peser ?", 
                "options": [f"{m_solide:.3f} g", f"{m_solide * 1000:.1f} g", f"{m_solide / 10:.3f} g"], 
                "rep": f"{m_solide:.3f} g"
            },
            {
                "id": "ds_3", 
                "q": "Quel récipient de haute précision utilise-t-on obligatoirement pour réaliser une dissolution ?", 
                "options": ["La fiole jaugée", "Le bécher gradué", "L'erlenmeyer"], 
                "rep": "La fiole jaugée"
            },
            {
                "id": "ds_4", 
                "q": "Pourquoi doit-on rincer la coupelle de pesée et l'entonnoir avec de l'eau distillée au-dessus de la fiole ?", 
                "options": ["Pour introduire la totalité du soluté pesé dans la fiole et éviter les pertes", "Pour nettoyer le matériel avant de le ranger", "Pour accélérer la réaction chimique de dissolution"], 
                "rep": "Pour introduire la totalité du soluté pesé dans la fiole et éviter les pertes"
            },
            {
                "id": "ds_5", 
                "q": "À quel moment précis doit-on procéder à l'agitation finale pour rendre la solution parfaitement homogène ?", 
                "options": ["Après avoir ajusté le liquide exactement jusqu'au trait de jauge", "Dès que le solide est introduit, avant d'ajouter de l'eau", "Au bout de 24 heures de repos au laboratoire"], 
                "rep": "Après avoir ajusté le liquide exactement jusqu'au trait de jauge"
            },
            {
                "id": "ds_6", 
                "q": "Si des grains de solide restent visibles au fond de la fiole jaugée après avoir rempli aux deux tiers, que faut-il faire ?", 
                "options": ["Agiter de manière circulaire pour dissoudre tout le solide avant d'ajuster au trait de jauge", "Ajouter immédiatement de l'eau jusqu'au col", "Chauffer la fiole jaugée au bec Bunsen"], 
                "rep": "Agiter de manière circulaire pour dissoudre tout le solide avant d'ajuster au trait de jauge"
            },
            {
                "id": "ds_7", 
                "q": "Quelle erreur commet-on si le bas du ménisque dépasse le trait de jauge lors du remplissage ?", 
                "options": ["La solution est trop diluée, il faut la jeter et recommencer", "La solution est trop concentrée, il faut ajouter du solide", "Le volume est correct car le haut du ménisque touche le trait"], 
                "rep": "La solution est trop diluée, il faut la jeter et recommencer"
            },
            {
                "id": "ds_8", 
                "q": "Quel accessoire de laboratoire permet d'ajuster goutte à goutte le niveau du liquide au niveau du trait de jauge ?", 
                "options": ["Une pipette simple ou une pipette Pasteur", "Un entonnoir large", "Une éprouvette graduée"], 
                "rep": "Une pipette simple ou une pipette Pasteur"
            },
            {
                "id": "ds_9", 
                "q": "Une solution aqueuse obtenue par dissolution complète de cristaux de sucre est un mélange de type :", 
                "options": ["Homogène", "Hétérogène", "Saturé d'office"], 
                "rep": "Homogène"
            },
            {
                "id": "ds_10", 
                "q": "La masse maximale de soluté que l'on peut dissoudre dans un litre de solvant à une température donnée s'appelle :", 
                "options": ["La solubilité", "La concentration massique", "Le facteur de dilution"], 
                "rep": "La solubilité"
            }
        ]
        copie_base = list(base_quiz_diss)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_diss = copie_base

    col_q3, col_t3 = st.columns(2)

    with col_q3:
        st.markdown("##### Quiz sur le protocole de dissolution (10 questions - 10 pts)")
        dict_rep_q3 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_diss, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ds_quiz_q_{q_data['id']}"
            cle_opts = f"opts_ds_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q3[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t3:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_3 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La méthode consistant à préparer une solution à partir d'un soluté solide s'appelle la")
        with c2: dict_trous_3["t1"] = st.selectbox("", ["Choisir...", "Dissolution", "Dilution", "Fusion"], key="ds_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour introduire proprement le solide sans perte dans la fiole, on utilise un")
        with c4: dict_trous_3["t2"] = st.selectbox("", ["Choisir...", "Entonnoir", "Agitateur", "Filtre"], key="ds_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Le prélèvement du solide dans le flacon d'origine s'effectue proprement avec une")
        with c6: dict_trous_3["t3"] = st.selectbox("", ["Choisir...", "Spatule", "Pipette", "Éprouvette"], key="ds_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La verrerie jaugée servant de contenant pour cette préparation est la fiole")
        with c8: dict_trous_3["t4"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Conique"], key="ds_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Avant d'ajuster au trait supérieur, on remplit la fiole aux deux tiers et on l'")
        with c10: dict_trous_3["t5"] = st.selectbox("", ["Choisir...", "Agite", "Pese", "Chauffe"], key="ds_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le liquide ajouté pour dissoudre le solide et compléter la fiole est l'eau")
        with c12: dict_trous_3["t6"] = st.selectbox("", ["Choisir...", "Distillee", "Robinet", "Minerale"], key="ds_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La marque gravée sur le col de la fiole indiquant le volume exact est le trait de")
        with c14: dict_trous_3["t7"] = st.selectbox("", ["Choisir...", "Jauge", "Graduation", "Repere"], key="ds_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour ajuster le ménisque sans dépasser la ligne, on termine le remplissage au goutte à")
        with c16: dict_trous_3["t8"] = st.selectbox("", ["Choisir...", "Goutte", "Bouchon", "Filet"], key="ds_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Une fois fermée par son bouchon, on retourne la fiole plusieurs fois pour la rendre")
        with r18: dict_trous_3["t9"] = st.selectbox("", ["Choisir...", "Homogene", "Heterogene", "Saturee"], key="ds_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Si le niveau dépasse la ligne de repère, la concentration de la solution est faussée par")
        with c20: dict_trous_3["t10"] = st.selectbox("", ["Choisir...", "Dilution", "Dissolution", "Pesee"], key="ds_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q3, dict_trous_3


def afficher_questions_tab2_completes(verrouille=False):
    import random
    
    if "ordre_quiz_tab2_10q" not in st.session_state:
        base_quiz = [
            {"id": "t2_q1", "q": "Quelle est l'unité officielle de la quantité de matière ?", "options": ["La mole (mol)", "Le gramme (g)", "Le litre (L)"], "rep": "La mole (mol)"},
            {"id": "t2_q2", "q": "Quelle est l'unité de la masse molaire moléculaire ?", "options": ["g/mol", "mol/g", "g/L"], "rep": "g/mol"},
            {"id": "t2_q3", "q": "Que représente précisément la constante d'Avogadro ?", "options": ["Le nombre d'entités chimiques dans une mole", "La masse d'un atome de carbone", "Le volume d'un gaz parfait"], "rep": "Le nombre d'entités chimiques dans une mole"},
            {"id": "t2_q4", "q": "Quelle formule relie la masse (m), la quantité de matière (n) et la masse molaire (M) ?", "options": ["n = m / M", "n = m * M", "n = M / m"], "rep": "n = m / M"},
            {"id": "t2_q5", "q": "Comment calcule-t-on la masse molaire moléculaire d'un composé ?", "options": ["En additionnant les masses molaires atomiques de tous ses atomes", "En multipliant sa masse par son volume", "En mesurant la température d'ébullition"], "rep": "En additionnant les masses molaires atomiques de tous ses atomes"},
            {"id": "t2_q6", "q": "Quelle formule dérivée permet d'isoler la masse (m) d'un échantillon ?", "options": ["m = n * M", "m = n / M", "m = M / n"], "rep": "m = n * M"},
            {"id": "t2_q7", "q": "Quelle masse de carbone (M = 12,0 g/mol) correspond à une quantité de matière de 2,0 mol ?", "options": ["24,0 g", "6,0 g", "12,0 g"], "rep": "24,0 g"},
            {"id": "t2_q8", "q": "Quelle est la quantité de matière contenue dans 18,0 g d'eau (H2O de masse molaire M = 18,0 g/mol) ?", "options": ["1,0 mol", "2,0 mol", "0,5 mol"], "rep": "1,0 mol"},
            {"id": "t2_q9", "q": "L'abréviation réglementaire écrite de l'unité de quantité de matière est :", "options": ["mol", "m", "M"], "rep": "mol"},
            {"id": "t2_q10", "q": "Si un échantillon de fer possède une quantité de matière de 0,5 mol, cela signifie qu'il contient :", "options": ["0,5 fois la constante d'Avogadro en atomes", "Exactement 0,5 atome de fer", "Le double du nombre d'Avogadro"], "rep": "0,5 fois la constante d'Avogadro en atomes"}
        ]
        random.shuffle(base_quiz)
        st.session_state.ordre_quiz_tab2_10q = base_quiz

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Quiz : La Mole et la Masse Molaire (10 questions - 10 pts)")
        rep_q2 = {}
        for idx, item in enumerate(st.session_state.ordre_quiz_tab2_10q, 1):
            st.write(f"**{idx}.** {item['q']}")
            opts_key = f"opts_t2_10q_{item['id']}"
            if opts_key not in st.session_state:
                opts = list(item["options"])
                random.shuffle(opts)
                st.session_state[opts_key] = ["Choisir..."] + opts
            val = st.session_state.get(f"sel_t2_10q_{item['id']}", "Choisir...")
            sel_idx = st.session_state[opts_key].index(val) if val in st.session_state[opts_key] else 0
            rep_q2[item["id"]] = st.selectbox("", st.session_state[opts_key], index=sel_idx, key=f"sel_t2_10q_{item['id']}", disabled=verrouille, label_visibility="collapsed")
            
    with col2:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        trous_q2 = {}
        
        c1, c2 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c1: st.write("1. Le regroupement d'atomes en paquets s'appelle la quantité de")
        with c2: trous_q2["t1"] = st.selectbox("", ["Choisir...", "Matiere", "Masse", "Volume"], key="t2_10t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c3: st.write("2. Un paquet contenant 6,02 x 10^23 entités chimiques est une")
        with c4: trous_q2["t2"] = st.selectbox("", ["Choisir...", "Mole", "Masse", "Solution"], key="t2_10t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c5: st.write("3. La constante fixant le nombre d'atomes dans une mole est la constante d'")
        with c6: trous_q2["t3"] = st.selectbox("", ["Choisir...", "Avogadro", "Mariotte", "Celsius"], key="t2_10t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c7: st.write("4. La masse d'une mole de molécules est la masse molaire")
        with c8: trous_q2["t4"] = st.selectbox("", ["Choisir...", "Moleculaire", "Atomique", "Volumique"], key="t2_10t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c9: st.write("5. L'unité de la masse molaire s'exprime en gramme par")
        with c10: trous_q2["t5"] = st.selectbox("", ["Choisir...", "Mole", "Litre", "Kilogramme"], key="t2_10t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c11: st.write("6. Dans l'expression n = m / M, la lettre m désigne la")
        with c12: trous_q2["t6"] = st.selectbox("", ["Choisir...", "Masse", "Mole", "Molarite"], key="t2_10t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c13: st.write("7. Pour calculer n, la masse mesurée doit être convertie en")
        with c14: trous_q2["t7"] = st.selectbox("", ["Choisir...", "Grammes", "Milligrammes", "Litres"], key="t2_10t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c15: st.write("8. Si la masse est donnée en mg, il faut la diviser par")
        with c16: trous_q2["t8"] = st.selectbox("", ["Choisir...", "Mille", "Cent", "Dix"], key="t2_10t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c17: st.write("9. La formule retournée pour isoler m est m = n multiplié par")
        with r18: trous_q2["t9"] = st.selectbox("", ["Choisir...", "M", "V", "Cm"], key="t2_10t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c19: st.write("10. L'unité de la quantité de matière n s'écrit de façon abrégée")
        with c20: trous_q2["t10"] = st.selectbox("", ["Choisir...", "mol", "g", "g/mol"], key="t2_10t_t10", disabled=verrouille, label_visibility="collapsed")

    return rep_q2, trous_q2


def afficher_questions_masse_volume(masse_actuelle, volume_actuel, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_mv" not in st.session_state:
        base_quiz_mv = [
            {
                "id": "mv_1", 
                "q": "Quelle est la définition physique de la masse d'un échantillon ?", 
                "options": ["La quantité de matière contenue dans l'échantillon", "L'espace à trois dimensions occupé par l'échantillon", "La force d'attraction exercée par la Terre"], 
                "rep": "La quantité de matière contenue dans l'échantillon"
            },
            {
                "id": "mv_2", 
                "q": "Quelle est la valeur de votre masse actuelle de sucre convertie en milligrammes (mg) ?", 
                "options": [f"{masse_actuelle * 1000:.1f}", f"{masse_actuelle / 1000:.4f}", f"{masse_actuelle * 100:.1f}"], 
                "rep": f"{masse_actuelle * 1000:.1f}"
            },
            {
                "id": "mv_3", 
                "q": "Quelle est la valeur de votre volume actuel de solution exprimé en Litres (L) ?", 
                "options": [f"{volume_actuel / 1000:.4f}", f"{volume_actuel * 1000:.1f}", f"{volume_actuel / 100:.2f}"], 
                "rep": f"{volume_actuel / 1000:.4f}"
            },
            {
                "id": "mv_4", 
                "q": "Quel appareil de laboratoire permet de mesurer un volume de liquide avec la plus haute précision ?", 
                "options": ["La fiole jaugée", "L'éprouvette graduée", "Le bécher"], 
                "rep": "La fiole jaugée"
            },
            {
                "id": "mv_5", 
                "q": "Pour effectuer correctement la lecture d'un volume sur une éprouvette graduée, l'oeil doit être aligné avec :", 
                "options": ["La base du ménisque", "Le haut des bords incurvés du liquide", "Le milieu exact de la verrerie"], 
                "rep": "La base du ménisque"
            },
            {
                "id": "mv_6", 
                "q": "Quelle est la valeur de votre masse actuelle de sucre convertie en kilogrammes (kg) ?", 
                "options": [f"{masse_actuelle / 1000:.4f}", f"{masse_actuelle * 1000:.1f}", f"{masse_actuelle / 100:.3f}"], 
                "rep": f"{masse_actuelle / 1000:.4f}"
            },
            {
                "id": "mv_7", 
                "q": "Avant de peser un solide dans un récipient sur la balance, sur quel bouton faut-il appuyer pour annuler le poids du récipient ?", 
                "options": ["Le bouton TARE", "Le bouton ON/OFF", "Le bouton CALIBRATE"], 
                "rep": "Le bouton TARE"
            },
            {
                "id": "mv_8", 
                "q": "L'unité officielle de la masse dans le Système International est le :", 
                "options": ["Kilogramme", "Gramme", "Milligramme"], 
                "rep": "Kilogramme"
            },
            {
                "id": "mv_9", 
                "q": "L'unité de volume usuelle en chimie équivalente à 1 décimètre cube (1 dm³) est :", 
                "options": ["Le litre", "Le millilitre", "Le mètre cube"], 
                "rep": "Le litre"
            },
            {
                "id": "mv_10", 
                "q": "Quelle méthode utilise-t-on pour mesurer le volume d'un solide de forme irrégulière ?", 
                "options": ["Le déplacement de liquide", "La pesée différentielle", "La formule mathématique standard"], 
                "rep": "Le déplacement de liquide"
            }
        ]
        copie_base = list(base_quiz_mv)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_mv = copie_base

    col_q1, col_t1 = st.columns(2)

    with col_q1:
        st.markdown("##### Quiz sur la masse, le volume et les mesures (10 questions - 10 pts)")
        dict_rep_q1 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_mv, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"mv_quiz_q_{q_data['id']}"
            cle_opts = f"opts_mv_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q1[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t1:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_1 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La grandeur qui caractérise l'espace tridimensionnel occupé par un corps est le")
        with c2: dict_trous_1["t1"] = st.selectbox("", ["Choisir...", "Volume", "Masse", "Surface"], key="mv_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Pour éliminer la masse du récipient vide posé sur la balance, on réalise la")
        with c4: dict_trous_1["t2"] = st.selectbox("", ["Choisir...", "Tare", "Mesure", "Pesee"], key="mv_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Au laboratoire de chimie, la masse d'un soluté solide s'exprime couramment en")
        with c6: dict_trous_1["t3"] = st.selectbox("", ["Choisir...", "Gramme", "Litre", "Kilogramme"], key="mv_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La verrerie graduée de forme allongée servant a mesurer grossièrement un liquide est l'")
        with c8: dict_trous_1["t4"] = st.selectbox("", ["Choisir...", "Eprouvette", "Fiole", "Becher"], key="mv_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La surface incurvée d'un liquide observée dans un tube étroit s'appelle un")
        with col_t1: 
            # Suite des colonnes alignées dans le même bloc de script
            pass
        with c10: dict_trous_1["t5"] = st.selectbox("", ["Choisir...", "Menisque", "Niveau", "Disque"], key="mv_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un litre équivaut précisément à un volume de un décimètre")
        with c12: dict_trous_1["t6"] = st.selectbox("", ["Choisir...", "Cube", "Carre", "Lineaire"], key="mv_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. L'erreur de lecture liée à une mauvaise position de l'oeil face aux graduations est l'erreur de")
        with c14: dict_trous_1["t7"] = st.selectbox("", ["Choisir...", "Parallaxe", "Calibrage", "Pesee"], key="mv_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour mesurer la masse d'un gaz libéré, on effectue une pesée de type")
        with c16: dict_trous_1["t8"] = st.selectbox("", ["Choisir...", "Differentielle", "Directe", "Standard"], key="mv_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Un millilitre correspond exactement à une fraction de litre égale à un")
        with r18: dict_trous_1["t9"] = st.selectbox("", ["Choisir...", "Millieme", "Centieme", "Dixieme"], key="mv_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour préparer un volume rigoureux de solution, on utilise une fiole")
        with c20: dict_trous_1["t10"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Erlenmeyer"], key="mv_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q1, dict_trous_1




def generer_simulateur_pesee(cle_suffixe):
    import streamlit as st
    import random
    
    st.markdown("### Module de manipulation interactive")
    st.markdown("""
    Une masse mystère de sucre a été déposée sur le plateau de gauche. 
    Ajoutez les masses marquées nécessaires sur le plateau de droite pour trouver l'équilibre exact et découvrir son poids.
    """)

    # Initialisation de la masse au hasard (multiples de 5g correspondant à des morceaux de sucre)
    cle_masse_hasard = f"masse_mystere_{cle_suffixe}"
    if cle_masse_hasard not in st.session_state:
        st.session_state[cle_masse_hasard] = random.randint(3, 25) * 5.0

    # Option d'appareil de mesure
    choix_balance = st.radio(
        "Sélectionnez l'appareil de pesée :",
        ["Balance de Roberval (Mécanique à aiguille)", "Balance électronique (Affichage digital moderne)"],
        key=f"choix_balance_{cle_suffixe}"
    )

    # Récupération de la masse fixe générée au hasard
    masse_solute_g = st.session_state[cle_masse_hasard]
    nb_cubes_sucre = int(masse_solute_g / 5.0)

    poids_boite = st.checkbox("Ajouter le récipient de pesée vide (20,0 g)", value=False, key=f"pesee_solide_boite_{cle_suffixe}")
    masse_totale_gauche = masse_solute_g
    if poids_boite:
        masse_totale_gauche += 20.0

    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.markdown("**Plateau Gauche : Échantillon mystère**")
        
        # Dessin des morceaux de sucre sous forme de cubes textuels
        st.markdown("Cubes de sucre déposés :")
        sucre_visuel = ""
        for i in range(nb_cubes_sucre):
            sucre_visuel += "[ 5g ] "
            if (i + 1) % 5 == 0:  # Aligner par lignes de 5 cubes max
                sucre_visuel += "\n"
        
        st.code(sucre_visuel if sucre_visuel else "[ Vide ]", language="text")
        
        if poids_boite:
            st.code("[--- Récipient : 20g ---]", language="text")

    with col_sim2:
        st.markdown("**Plateau Droite : Boîte de masses marquées**")
        
        m_100 = st.number_input("Masses de 100 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m100_{cle_suffixe}")
        m_50 = st.number_input("Masses de 50 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m50_{cle_suffixe}")
        m_20 = st.number_input("Masses de 20 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m20_{cle_suffixe}")
        m_10 = st.number_input("Masses de 10 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m10_{cle_suffixe}")
        m_5 = st.number_input("Masses de 5 g :", min_value=0, max_value=5, value=0, step=1, key=f"pesee_m5_{cle_suffixe}")
        
        masse_totale_droite = (m_100 * 100.0) + (m_50 * 50.0) + (m_20 * 20.0) + (m_10 * 10.0) + (m_5 * 5.0)
        
        # Dessin des masses métalliques empilées avec la valeur inscrite dessus
        st.markdown("Masses déposées sur le plateau :")
        masses_visuelles = ""
        for _ in range(m_100): masses_visuelles += "(=== 100g ===)\n"
        for _ in range(m_50):  masses_visuelles += "(=== 50g ===)\n"
        for _ in range(m_20):  masses_visuelles += "(=== 20g ===)\n"
        for _ in range(m_10):  masses_visuelles += "(=== 10g ===)\n"
        for _ in range(m_5):   masses_visuelles += "(=== 5g ===)\n"
        
        st.code(masses_visuelles if masses_visuelles else "( Aucun contrepoids )", language="text")

    st.markdown("---")
    
    if choix_balance == "Balance de Roberval (Mécanique à aiguille)":
        st.markdown("**État visuel du fléau de la balance de Roberval**")
        if masse_totale_gauche > masse_totale_droite:
            st.warning("La balance penche vers la gauche. Le sucre est plus lourd que vos masses marquées.")
            st.image("balance_gauche.jpg", caption="Le plateau gauche descend. Ajoutez des contrepoids à droite.", use_container_width=True)
            return 0.0, False
        elif masse_totale_droite > masse_totale_gauche:
            st.warning("La balance penche vers la droite. Vos masses marquées sont trop lourdes.")
            st.image("balance_droite.jpg", caption="Le plateau droit descend. Retirez des masses marquées.", use_container_width=True)
            return 0.0, False
        else:
            st.success("L'équilibre de la balance est parfait.")
            st.image("balance_equilibre.jpg", caption="Aiguille centrale au zéro. L'équilibre mécanique est atteint.", use_container_width=True)
            st.metric(label="Masse nette du sucre découverte (m)", value=f"{masse_solute_g:.1f} g")
            
            if st.button("Générer une nouvelle masse mystère", key=f"btn_reset_{cle_suffixe}"):
                del st.session_state[cle_masse_hasard]
                st.rerun()
            return masse_solute_g, True
    else:
        # Mode balance électronique digitale moderne
        st.markdown("**Visuel de la balance électronique**")
        st.image("balance_electronique.jpg", caption="Balance électronique de précision numérique", use_container_width=True)
        
        bouton_tare = st.checkbox("Activer la fonction TARE électronique (Remise à zéro)", value=False, key=f"tare_digitale_{cle_suffixe}")
        masse_affichee = masse_solute_g if bouton_tare else masse_totale_gauche
        
        if not bouton_tare:
            st.warning("Attention : L'affichage inclut la masse du récipient de pesée.")
        
        st.metric(label="Valeur affichée sur l'écran numérique", value=f"{masse_affichee:.1f} g")
        
        if bouton_tare:
            if st.button("Générer une nouvelle masse mystère", key=f"btn_reset_elec_{cle_suffixe}"):
                del st.session_state[cle_masse_hasard]
                st.rerun()
        return masse_solute_g if bouton_tare else 0.0, bouton_tare

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
    st.header("Rappels et mesures : Masse et Volume")
    
    # ------------------------------------------
    # SECTION MASSE
    # ------------------------------------------
    st.subheader("1. La Masse (m)")

    col_texte_masse, col_img_masse = st.columns(2)
    with col_texte_masse:
        st.markdown("""
        La masse correspond à la quantité de matière contenue dans un échantillon.
        L'unité officielle du Système International est le kilogramme (kg), mais en chimie, l'unité usuelle est le gramme (g) ou le milligramme (mg).
         On la mesure à l'aide d'une balance électronique de précision. """)
        
    with col_img_masse:
        st.image(
            "balance.jpg", 
            caption="Balance au laboratoire", 
            width=500
        )
        
    st.subheader("Différences de mesure de la masse selon l'état physique")

    col_texte_phys, col_img_phys = st.columns(2)

    with col_texte_phys:
        st.markdown("""
        * **Pour un solide :** La mesure est directe. On place une coupelle de pesée vide sur la balance, on appuie sur le bouton TARE pour remettre l'affichage à zéro, puis on introduit le solide à la spatule.
        * **Pour un liquide :** Un liquide n'a pas de forme propre. On pose obligatoirement le récipient de stockage (bécher, fiole) vide sur la balance, on réalise la TARE, puis on verse le liquide. La valeur affichée correspond exclusivement à la masse du liquide transféré.
        * **Pour un gaz :** Un gaz occupe tout l'espace disponible et sa masse est très faible. On réalise une pesée différentielle. On pèse le récipient plein de gaz (masse m1), on laisse s'échapper un volume précis de gaz, puis on repèse le contenant (masse m2). La masse du gaz extrait vaut m = m1 - m2.
        """)

    with col_img_phys:
        st.image(
            "etats_physiques_masse.jpg", 
            caption="Techniques de pesée pour les solides, liquides et gaz au laboratoire", 
            width=500
        )
    # Tableau interactif de conversion pour la Masse
    st.markdown("---")
    st.markdown("**Tableau de conversion interactif des masses**")
    st.markdown("Saisissez une valeur pour voir sa conversion automatique dans les autres unités :")
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        valeur_m = st.number_input("Valeur à convertir (masse) :", min_value=0.0, value=1.0, step=0.1, key="input_masse_val")
    with col_m2:
        unite_m = st.selectbox("Unité de saisie :", ["kg", "hg", "dag", "g", "dg", "cg", "mg"], index=3, key="input_masse_unit")
    
    # Calcul de la valeur pivot en grammes (g)
    if unite_m == "kg":
        masse_en_g = valeur_m * 1000.0
    elif unite_m == "hg":
        masse_en_g = valeur_m * 100.0
    elif unite_m == "dag":
        masse_en_g = valeur_m * 10.0
    elif unite_m == "dg":
        masse_en_g = valeur_m / 10.0
    elif unite_m == "cg":
        masse_en_g = valeur_m / 100.0
    elif unite_m == "mg":
        masse_en_g = valeur_m / 1000.0
    else:
        masse_en_g = valeur_m
        
    st.markdown("Correspondances obtenues :")
    st.markdown(f"* Kilogramme (kg) : **{masse_en_g / 1000.0:.6f}** kg")
    st.markdown(f"* Hectogramme (hg) : **{masse_en_g / 100.0:.4f}** hg")
    st.markdown(f"* Décagramme (dag) : **{masse_en_g / 10.0:.2f}** dag")
    st.markdown(f"* Gramme (g) : **{masse_en_g:.3f}** g")
    st.markdown(f"* Décigramme (dg) : **{masse_en_g * 10.0:.1f}** dg")
    st.markdown(f"* Centigramme (cg) : **{masse_en_g * 100.0:.1f}** cg")
    st.markdown(f"* Milligramme (mg) : **{masse_en_g * 1000.0:.1f}** mg")

    st.divider()

    # ------------------------------------------
    # SECTION VOLUME
    # ------------------------------------------
    st.subheader("2. Le Volume (V)")
    col_texte_vol, col_img_vol = st.columns(2)
    with col_texte_vol:

        st.markdown("""
        Le volume représente l'espace à trois dimensions occupé par un corps ou une solution.
        L'unité officielle est le mètre cube (m³), mais en chimie, on utilise presque exclusivement le litre (L) et le millilitre (mL).
        
        **Différences de mesure selon l'état physique :**
        *   **Pour un liquide :** On utilise de la verrerie graduée (éprouvette graduée) pour une mesure courante, ou jaugée (fiole jaugée, pipette jaugée) pour une haute précision. L'oeil doit être au niveau du liquide pour éviter l'erreur de parallaxe, et la mesure se lit à la **base du ménisque**.
        *   **Pour un solide :** 
            *   *S'il est géométrique et régulier :* On mesure ses dimensions linéaires (longueur, rayon, etc.) et on applique une formule mathématique de volume.
            *   *S'il est irrégulier :* On utilise la méthode de **déplacement de liquide**. On verse un volume d'eau V1 dans une éprouvette, on y plonge le solide, on lit le nouveau volume V2. Le volume du solide vaut V = V2 - V1.
        *   **Pour un gaz :** Un gaz n'a pas de volume propre, il est compressible et expansible. On mesure son volume à l'aide d'une **seringue à gaz** étanche ou par la méthode du **déplacement d'eau** (on piège le gaz dans une éprouvette initialement remplie d'eau et retournée sur une cuve à eau).
        """)
        
    with col_img_vol:

        st.image(
            "verrerie_precision.jpg", 
            caption="Verrerie graduée et jaugée pour les mesures de volumes", 
            width=500
        )

    # Tableau interactif de conversion pour le Volume
    st.markdown("**Tableau de conversion interactif des volumes**")
    st.markdown("Saisissez une valeur pour voir sa conversion automatique dans toutes les unités :")

    col_v1, col_v2 = st.columns(2)
    with col_v1:
        valeur_v = st.number_input("Valeur à convertir (volume) :", min_value=0.0, value=1.0, step=0.1, key="input_vol_val")
    with col_v2:
        unite_v = st.selectbox(
            "Unité de saisie :", 
            ["m3", "hL", "daL", "L", "dL", "cL", "mL", "dm3", "cm3"], 
            index=3, 
            key="input_vol_unit"
        )
        
    # Calcul de la valeur pivot en Litres (L)
    if unite_v == "m3":
        vol_en_l = valeur_v * 1000.0
    elif unite_v == "hL":
        vol_en_l = valeur_v * 100.0
    elif unite_v == "daL":
        vol_en_l = valeur_v * 10.0
    elif unite_v == "dL":
        vol_en_l = valeur_v / 10.0
    elif unite_v == "cL":
        vol_en_l = valeur_v / 100.0
    elif unite_v == "mL" or unite_v == "cm3":
        vol_en_l = valeur_v / 1000.0
    elif unite_v == "dm3":
        vol_en_l = valeur_v
    else:
        vol_en_l = valeur_v
        
    st.markdown("Correspondances obtenues :")
    st.markdown(f"* Mètre cube (m³) : **{vol_en_l / 1000.0:.6f}** m³")
    st.markdown(f"* Hectolitre (hL) : **{vol_en_l / 100.0:.4f}** hL")
    st.markdown(f"* Décalitre (daL) : **{vol_en_l / 10.0:.2f}** daL")
    st.markdown(f"* Litre (L) ou Décimètre cube (dm³) : **{vol_en_l:.4f}** L / dm³")
    st.markdown(f"* Décilitre (dL) : **{vol_en_l * 10.0:.2f}** dL")
    st.markdown(f"* Centilitre (cL) : **{vol_en_l * 100.0:.1f}** cL")
    st.markdown(f"* Millilitre (mL) ou Centimètre cube (cm³) : **{vol_en_l * 1000.0:.0f}** mL / cm³")

    masse_dynamique, pesee_reussie = generer_simulateur_pesee(cle_suffixe="cours")
    
    st.divider()
    
    # Variables pour votre bloc de questionnaire
    masse_actuelle = float(masse_dynamique) if pesee_reussie else 10.0
    volume_actuel = 100.0  
    cm_actuelle = masse_actuelle / (volume_actuel / 1000.0)
    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)

    res_q1, res_t1 = afficher_questions_masse_volume(
        masse_actuelle=masse_actuelle,
        volume_actuel=volume_actuel,
        verrouille=verrou_v1
    )

    st.write("---")

    case_certif_mv = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_mv_official", 
        disabled=verrou_v1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_mv_official", use_container_width=True, disabled=verrou_v1):
        st.session_state.id_nom = st.session_state.get("id_nom") or st.session_state.get("nom_var") or "INCONNU"
        st.session_state.id_prenom = st.session_state.get("id_prenom") or st.session_state.get("prenom_var") or "INCONNU"
        st.session_state.id_classe = st.session_state.get("id_classe") or st.session_state.get("classe_var") or "INCONNU"
        
        p_validation = str(st.session_state.id_prenom).upper()
        n_validation = str(st.session_state.id_nom).upper()

        if n_validation == "INCONNU" or p_validation == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_mv:
            st.error("Action refusee : Cochez la case de certification.")
        elif not pesee_reussie:
            st.error("Action refusee : Vous devez réussir l'équilibre de la balance avant de pouvoir soumettre vos réponses.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_mv" in st.session_state:
                for q_item in st.session_state.ordre_quiz_mv:
                    reponse_eleve = st.session_state.get(f"mv_quiz_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction de la Synthese a trous (10 points)
            score_t1 = sum([
                st.session_state.get("mv_t_t1") == "Volume",
                st.session_state.get("mv_t_t2") == "Tare",
                st.session_state.get("mv_t_t3") == "Gramme",
                st.session_state.get("mv_t_t4") == "Eprouvette",
                st.session_state.get("mv_t_t5") == "Menisque",
                st.session_state.get("mv_t_t6") == "Cube",
                st.session_state.get("mv_t_t7") == "Parallaxe",
                st.session_state.get("mv_t_t8") == "Differentielle",
                st.session_state.get("mv_t_t9") == "Millieme",
                st.session_state.get("mv_t_t10") == "Jaugee"
            ])

            st.session_state.score_mv_p1 = round(float(score_q1), 1)
            st.session_state.score_mv_p2 = round(float(score_t1), 1)
            st.session_state.score_final_mv = round(float(score_q1 + score_t1), 1)
            st.session_state.v_verrouille_tab1 = True
            st.rerun()

    # 2. Le bloc d'exportation s'exécute SEULEMENT si l'atelier est scellé
    if st.session_state.get("v_verrouille_tab1", False):
        scr1 = st.session_state.get("score_mv_p1", 0.0)
        scr2 = st.session_state.get("score_mv_p2", 0.0)
        tot_s = st.session_state.get("score_final_mv", 0.0)

        p_eleve = str(st.session_state.get("id_prenom", "INCONNU")).upper()
        n_eleve = str(st.session_state.get("id_nom", "INCONNU")).upper()
        c_eleve = str(st.session_state.get("id_classe", "INCONNU")).upper()

        from datetime import datetime
        timestamp_mv = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MASSE ET VOLUME SCELLÉ | Note de session : {tot_s:.1f} / 20")

        # Ligne 1233 sécurisée : n_eleve existe bel et bien à cet endroit du script
        html_export_mv = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Masse et Volume - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier 1 : Definition, mesures et unites de la masse et du volume</p>
                <p>Configuration personnalisee resolue : m = {masse_actuelle:.1f} g | V = {volume_actuel:.1f} mL</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_mv}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_mv" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_mv, 1):
                saisie = st.session_state.get(f"mv_quiz_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mv += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mv += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_mv = [
            ("1. La grandeur qui caracterise l'espace tridimensionnel occupe par un corps est le", st.session_state.get("mv_t_t1"), "Volume"),
            ("2. Pour eliminer la masse du recipient vide pose sur la balance, on realise la", st.session_state.get("mv_t_t2"), "Tare"),
            ("3. Au laboratoire de chimie, la masse d'un solute solide s'exprime couramment en", st.session_state.get("mv_t_t3"), "Gramme"),
            ("4. La verrerie graduee de forme allongee servant a mesurer grossierement un liquide est l'", st.session_state.get("mv_t_t4"), "Eprouvette"),
            ("5. La surface incurvee d'un liquide observee dans un tube etroit s'appelle un", st.session_state.get("mv_t_t5"), "Menisque"),
            ("6. Un litre equivaut precisement a un volume de un decimetre", st.session_state.get("mv_t_t6"), "Cube"),
            ("7. L'erreur de lecture liee a une mauvaise position de l'oeil face aux graduations est l'erreur de", st.session_state.get("mv_t_t7"), "Parallaxe"),
            ("8. Pour mesurer la masse d'un gaz libere, on effectue une pesee de type", st.session_state.get("mv_t_t8"), "Differentielle"),
            ("9. Un millilitre correspond exactement a une fraction de litre egale a un", st.session_state.get("mv_t_t9"), "Millieme"),
            ("10. Pour preparer un volume rigoureux de solution, on utilise une fiole", st.session_state.get("mv_t_t10"), "Jaugee")
        ]

        for num, (phrase, saisie, attendu) in enumerate(phrases_trous_mv, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_mv += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mv += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE SESSION EN HTML",
            data=html_export_mv,
            file_name=f"Rapport_Masse_Volume_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




with tab2:

    col_mole, col_massemolaire = st.columns(2)
    with col_mole:
        st.subheader("La mole")        
        st.markdown("""
        La mole est l'unité de mesure qui permet aux chimistes de compter l'infiniment petit. Dans le monde qui nous entoure, les atomes et les molécules sont beaucoup trop minuscules et nombreux pour être manipulés un par un. Pour dépasser cette difficulté, les scientifiques ont créé un outil astucieux : le regroupement en paquets.
        Pour comprendre le principe, on peut imaginer des objets du quotidien. Si vous achetez des œufs, vous parlez en douzaines (des paquets de 12). Si vous achetez des feuilles de papier, vous parlez en ramettes (des paquets de 500). En chimie, pour compter les particules, on parle en moles. Une mole est tout simplement un paquet géant contenant exactement \(6,022 \times 10^{23}\) entités élémentaires, qu'il s'agisse d'atomes, d'ions ou de molécules. Ce nombre astronomique, qui s'écrit avec 23 chiffres, s'appelle la constante d'Avogadro.
        Cette unité sert de pont indispensable entre l'échelle microscopique et notre échelle humaine. Comme il est impossible de compter les atomes à l'œil nu, les chimistes utilisent la balance grâce à une correspondance parfaite : la masse molaire. Il s'agit du poids exact d'une mole d'un élément donné. Par exemple, une mole d'atomes de carbone pèse précisément 12 grammes. Ainsi, en pesant simplement 12 grammes de carbone sur sa balance, le chimiste sait avec certitude qu'il a entre les mains un paquet contenant exactement \(6,022 \times 10^{23}\) atomes.



        La masse molaire moléculaire

        La masse molaire atomique est la brique de base de tous les calculs en chimie. C'est en additionnant ces masses atomiques que l'on obtient la masse molaire moléculaire (le poids d'un paquet de molécules). Par exemple, pour l'eau (\(H_{2}O\)), on prend deux masses atomiques d'hydrogène (\(2 \times 1\)) et une d'oxygène (\(16\)) pour obtenir \(18\text{ g/mol}\).


        """)

        st.divider()
        
        st.subheader("La masse molaire atomique et moléculaire")
        st.markdown("""
        La masse molaire atomique est la masse d'une mole d'atomes d'un même élément chimique.Elle correspond à la masse d'un paquet contenant précisément \(6,022 \times 10^{23}\) atomes identiques. Son symbole est \(M\) et elle s'exprime en grammes par mole (g/mol).
        • Où la trouve-t-on ? Elle est indiquée directement dans le tableau périodique des éléments (la table de Mendeleïev). C'est le nombre décimal qui figure généralement en bas ou en haut de la case de chaque élément.
        •  Chaque atome a sa propre masse molaire car les atomes n'ont pas tous la même taille ni la même constitution (nombre de protons et de neutrons).

        La masse molaire moléculaire : 
        La masse molaire atomique est la brique de base de tous les calculs en chimie. C'est en additionnant ces masses atomiques que l'on obtient la masse molaire moléculaire (le poids d'un paquet de molécules). Par exemple, pour l'eau (\(H_{2}O\)), on prend deux masses atomiques d'hydrogène (\(2 \times 1\)) et une d'oxygène (\(16\)) pour obtenir \(18\text{ g/mol}\).

        La métaphore du panier de fruits !
        Pour comprendre facilement, on peut comparer la molécule à un panier de fruits :
        • Si une molécule est un panier contenant 2 pommes et 1 orange, sa masse totale dépend du poids de chaque fruit.
        • En chimie, pour trouver la masse d'un paquet (une mole) de ces paniers, on additionne le poids d'un paquet de pommes et d'un paquet d'oranges.

        """)

        st.divider()

    with col_massemolaire:
        
        st.image(
            "mole_taupe.jpg", 
            caption="pesée d'une mole de carbone", 
            width=700
        )

        st.image(
            "masse_molaire_taupe.jpg", 
            caption="pesée d'une mole de molécule", 
            width=700
        )

    verrou_v2 = st.session_state.get("v_verrouille_tab2", False)
    res_q2, res_t2 = afficher_questions_tab2_completes(verrouille=verrou_v2)

    st.write("---")
    st.session_state.id_nom = st.session_state.get("nom_var") or "INCONNU"
    st.session_state.id_prenom = st.session_state.get("prenom_var") or "INCONNU"
    st.session_state.id_classe = st.session_state.get("classe_var") or "INCONNU"
    
    n_eleve = str(st.session_state.id_nom).upper()
    p_eleve = str(st.session_state.id_prenom).upper()
    c_eleve = str(st.session_state.id_classe).upper()

    case_certif_n = st.checkbox("Je certifie avoir complete les questions de l'Atelier 2.", key="check_certif_n_10", disabled=verrou_v2)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_n_10", use_container_width=True, disabled=verrou_v2):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_n:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q2 = 0.0
            if "ordre_quiz_tab2_10q" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_10q:
                    ans = st.session_state.get(f"sel_t2_10q_{q_item['id']}", "Choisir...")
                    if str(ans).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction de la Synthese (10 points)
            score_t2 = sum([
                st.session_state.get("t2_10t_t1") == "Matiere",
                st.session_state.get("t2_10t_t2") == "Mole",
                st.session_state.get("t2_10t_t3") == "Avogadro",
                st.session_state.get("t2_10t_t4") == "Moleculaire",
                st.session_state.get("t2_10t_t5") == "Mole",
                st.session_state.get("t2_10t_t6") == "Masse",
                st.session_state.get("t2_10t_t7") == "Grammes",
                st.session_state.get("t2_10t_t8") == "Mille",
                st.session_state.get("t2_10t_t9") == "M",
                st.session_state.get("t2_10t_t10") == "mol"
            ])

            st.session_state.score_n_p1 = round(float(score_q2), 1)
            st.session_state.score_n_p2 = round(float(score_t2), 1)
            st.session_state.score_final_n = round(float(score_q2 + score_t2), 1)
            st.session_state.v_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab2", False):
        scr1_n = st.session_state.get("score_n_p1", 0.0)
        scr2_n = st.session_state.get("score_n_p2", 0.0)
        tot_s_n = st.session_state.get("score_final_n", 0.0)
        timestamp_n = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MOLE ET MASSE MOLAIRE SCELLÉ | Note de session : {tot_s_n:.1f} / 20")

        html_export_n = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Quantite de Matiere - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #2563eb; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier 2 : La mole et la masse molaire moléculaire</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_n}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_n:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #2563eb;">
                - Note obtenue au Quiz : <strong>{scr1_n:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2_n:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 2 : <strong>{tot_s_n:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_10q" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_10q, 1):
                saisie = st.session_state.get(f"sel_t2_10q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_n += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_n += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_n = [
            ("1. Le regroupement d'atomes en paquets s'appelle la quantite de", st.session_state.get("t2_10t_t1"), "Matiere"),
            ("2. Un paquet contenant 6,02 x 10^23 entites chimiques est une", st.session_state.get("t2_10t_t2"), "Mole"),
            ("3. La constante fixant le nombre d'atomes dans une mole est la constante d'", st.session_state.get("t2_10t_t3"), "Avogadro"),
            ("4. La masse d'une mole de molecules est la masse molaire", st.session_state.get("t2_10t_t4"), "Moleculaire"),
            ("5. L'unite de la masse molaire s'exprime en gramme par", st.session_state.get("t2_10t_t5"), "Mole"),
            ("6. Dans l'expression n = m / M, la lettre m designe la", st.session_state.get("t2_10t_t6"), "Masse"),
            ("7. Pour calculer n, la masse mesuree doit etre convertie en", st.session_state.get("t2_10t_t7"), "Grammes"),
            ("8. Si la masse est donnee en mg, il faut la diviser par", st.session_state.get("t2_10t_t8"), "Mille"),
            ("9. La formule retournee pour isoler m est m = n multiplie par", st.session_state.get("t2_10t_t9"), "M"),
            ("10. L'unite de la quantite de matiere n s'ecrit de facon abregee", st.session_state.get("t2_10t_t10"), "mol")
        ]

        for num, (phrase, saisie, attendu) in enumerate(phrases_trous_n, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_n += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_n += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE L'ATELIER 2 EN HTML",
            data=html_export_n,
            file_name=f"Rapport_Quantite_Matiere_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




with tab3:
    st.header("Comment caculer le nombre de mole?")
    col_solide, col_liquide, col_gaz = st.columns(3)
    with col_solide:

        st.markdown(""" Pour un solide de masse m en gramme et de masse molaire M en gramme par mol, le nombre de mole est définie par  la formule fondamentale suivante :
        """)
        st.latex(r"n = \frac{m}{M}")
        
        st.divider()

        st.subheader("Simulateur de calcul : De la masse à la mole")
        m_echantillon = st.number_input("Masse de l'échantillon m (g) :", min_value=0.001, value=10.0, step=0.1, key="t2_m_sim_10")
        m_molaire_espece = st.number_input("Masse molaire moléculaire M (g/mol) :", min_value=1.0, value=180.0, step=0.1, key="t2_M_sim_10")
        
        n_resultat = m_echantillon / m_molaire_espece
        st.metric(label="Quantité de matière calculée (n)", value=f"{n_resultat:.4f} mol")

        st.divider()
        
    with col_liquide:

        st.markdown(""" Pour un liquide de concentration molaire C en mole par litre et de volume V en litre , le nombre de mole est définie par  la formule fondamentale suivante :
        """)
        st.latex(r"n = \{C} * {V}")
        
        st.divider()

        st.subheader("Simulateur de calcul : De la concentration molaire à la mole")
        V_echantillon = st.number_input("Volume V (L) :", min_value=0.001, value=10.0, step=0.1, key="t3_V_sim_10")
        C_molaire_espece = st.number_input("Masse molaire moléculaire M (g/mol) :", min_value=1.0, value=180.0, step=0.1, key="t3_C_sim_10")
        
        n_resultat = V_echantillon * C_molaire_espece
        st.metric(label="Quantité de matière calculée (n)", value=f"{n_resultat:.4f} mol")

        st.divider()

    with col_gaz:

        st.markdown(""" Pour un gaz de volume  V en litre et de volume molaire Vm en litre par mol , le nombre de mole est définie par  la formule fondamentale suivante :
        """)
        st.latex(r"n = \{V} * {Vm}")
        
        st.divider()



with tab4:
    st.header("La concentration molaire C")
    
    st.markdown("""
    La concentration massique (ou concentration en masse) représente la masse de soluté dissous par unité de volume de solution totale.
    Elle se calcule à l'aide de la formule mathématique fondamentale :
    """)
    st.latex(r"C_m = \frac{m}{V}")
    st.markdown("""
    * **Cm** : Concentration massique exprimée en grammes par litre (g/L).
    * **m** : Masse du soluté dissous exprimée en grammes (g).
    * **V** : Volume total de la solution obtenu exprimé en litres (L).
    """)

    st.divider()

    st.subheader("Simulateur d'entraînement aux calculs")
    st.markdown("Utilisez ce module interactif pour basculer la formule selon la grandeur que vous recherchez :")

    mode_calcul = st.selectbox(
        "Que souhaitez-vous calculer ?",
        ["La concentration massique (Cm)", "La masse du soluté (m)", "Le volume de la solution (V)"],
        key="cm_mode_calcul"
    )

    col_c1, col_c2 = st.columns(2)

    if mode_calcul == "La concentration massique (Cm)":
        with col_c1:
            m_input = st.number_input("Masse du soluté (g) :", min_value=0.001, value=5.0, step=0.1, key="calc_cm_m")
            v_input_ml = st.number_input("Volume de la fiole (mL) :", min_value=1.0, value=250.0, step=10.0, key="calc_cm_v")
        with col_c2:
            v_litres = v_input_ml / 1000.0
            cm_resultat = m_input / v_litres
            st.metric(label="Concentration massique calculée (Cm)", value=f"{cm_resultat:.2f} g/L")
            st.code(f"Cm = {m_input} g / {v_litres:.3f} L = {cm_resultat:.2f} g/L", language="python")

    elif mode_calcul == "La masse du soluté (m)":
        with col_c1:
            cm_input = st.number_input("Concentration massique ciblée (g/L) :", min_value=0.001, value=10.0, step=0.5, key="calc_m_cm")
            v_input_ml = st.number_input("Volume de solution souhaité (mL) :", min_value=1.0, value=100.0, step=10.0, key="calc_m_v")
        with col_c2:
            v_litres = v_input_ml / 1000.0
            m_resultat = cm_input * v_litres
            st.metric(label="Masse de soluté à peser (m)", value=f"{m_resultat:.3f} g")
            st.code(f"m = {cm_input} g/L * {v_litres:.3f} L = {m_resultat:.3f} g", language="python")

    else:
        with col_c1:
            m_input = st.number_input("Masse de soluté disponible (g) :", min_value=0.001, value=2.0, step=0.1, key="calc_v_m")
            cm_input = st.number_input("Concentration massique ciblée (g/L) :", min_value=0.001, value=5.0, step=0.5, key="calc_v_cm")
        with col_c2:
            v_resultat_l = m_input / cm_input
            v_resultat_ml = v_resultat_l * 1000.0
            st.metric(label="Volume de solution à fabriquer (V)", value=f"{v_resultat_ml:.1f} mL")
            st.code(f"V = {m_input} g / {cm_input} g/L = {v_resultat_l:.3f} L (soit {v_resultat_ml:.1f} mL)", language="python")

    st.divider()

    st.subheader("Exercice : Calcul complet à partir de l'étiquette d'eau minérale")

    st.markdown("""
    À l'aide de la formule dérivée $m = C_m \\times V$, calculez la masse de matière ingérée en milligrammes (mg) pour chacun des ions de l'étiquette selon le volume choisi.
    Convertissez le volume en Litres (L) avant d'effectuer votre produit.
    """)

    col_etiquette, col_verre = st.columns(2)

    with col_etiquette:
        st.caption("Étiquette de la bouteille d'eau :")
        st.image(
            "eau_minerale.jpg", 
            caption="Composition physico-chimique moyenne de votre échantillon", 
            width=320
        )

    with col_verre:
        st.markdown("**1. Choix du volume du verre :**")
        volume_verre_ml = st.slider(
            "Volume du verre d'eau (mL) :", 
            min_value=50, 
            max_value=500, 
            value=250, 
            step=10, 
            key="eau_vol_verre_complet"
        )
        v_verre_l = volume_verre_ml / 1000.0
        st.info(f"Volume de calcul : {v_verre_l:.3f} L (soit {volume_verre_ml} mL)")

    st.markdown("---")
    st.markdown("**2. Vos calculs (en mg) :**")

    # Dictionnaire complet des concentrations de votre image (mg/L)
    ions_exercice = {
        "Calcium (Ca2+)": 176.0,
        "Magnésium (Mg2+)": 46.0,
        "Sodium (Na+)": 28.0,
        "Potassium (K+)": 5.0,
        "Sulfates (SO4 2-)": 372.0,
        "Bicarbonates (HCO3-)": 312.0,
        "Chlorures (Cl-)": 37.0,
        "Fluor (F-)": 1.3
    }

    # Génération des champs de saisie pour chaque ion
    reponses_eleve = {}
    col_saisie1, col_saisie2 = st.columns(2)

    for index, (nom_ion, cm_val) in enumerate(ions_exercice.items()):
        # Répartition équilibrée sur deux colonnes de saisie
        with col_saisie1 if index % 2 == 0 else col_saisie2:
            reponses_eleve[nom_ion] = st.number_input(
                f"Masse de {nom_ion} (mg) :",
                min_value=0.0,
                step=0.01,
                format="%.2f",
                key=f"input_exo_all_{index}"
            )

    # Bouton de correction globale
    if st.button("Vérifier l'ensemble de mes réponses", key="btn_verif_all_ions"):
        sans_erreur = True
        st.markdown("### Rapport de correction analytique :")
        
        for nom_ion, cm_val in ions_exercice.items():
            masse_attendue = cm_val * v_verre_l
            saisie_eleve = reponses_eleve[nom_ion]
            
            # Tolérance de 0.15 mg pour couvrir les écarts d'arrondis des élèves
            if abs(saisie_eleve - masse_attendue) <= 0.15:
                st.success(f"Correct pour {nom_ion} : Votre valeur {saisie_eleve:.2f} mg est valide. (Attendu : {masse_attendue:.2f} mg)")
            else:
                st.error(f"Erreur pour {nom_ion} : Vous avez saisi {saisie_eleve:.2f} mg. Calcul attendu : {cm_val} mg/L × {v_verre_l:.3f} L = {masse_attendue:.2f} mg")
                sans_erreur = False
                
        if sans_erreur:
            st.success("Félicitations, vous avez calculé parfaitement la totalité des composants de l'étiquette.")

    st.divider()


    # Définition des variables fixes de session pour personnaliser le questionnaire de l'Atelier 2
    # On fige des valeurs d'exercices cohérentes
    m_exercice = 4.0
    v_exercice = 200.0 # en mL
    cm_exercice = m_exercice / (v_exercice / 1000.0) # 20.0 g/L
    verrou_v2 = st.session_state.get("v_verrouille_tab2", False)

    # L'appel à afficher_questions_concentration_massique doit être présent juste au-dessus
    st.write("---")

    case_certif_cm = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 2.", 
        key="check_certif_cm_official", 
        disabled=verrou_v2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_cm_official", use_container_width=True, disabled=verrou_v2):
        st.session_state.id_nom = st.session_state.get("id_nom") or st.session_state.get("nom_var") or "INCONNU"
        st.session_state.id_prenom = st.session_state.get("id_prenom") or st.session_state.get("prenom_var") or "INCONNU"
        st.session_state.id_classe = st.session_state.get("id_classe") or st.session_state.get("classe_var") or "INCONNU"
        
        p_validation = str(st.session_state.id_prenom).upper()
        n_validation = str(st.session_state.id_nom).upper()

        if n_validation == "INCONNU" or p_validation == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_cm:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q2 = 0.0
            if "ordre_quiz_cm" in st.session_state:
                for q_item in st.session_state.ordre_quiz_cm:
                    reponse_eleve = st.session_state.get(f"cm_quiz_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction de la Synthese a trous (10 points)
            score_t2 = sum([
                st.session_state.get("cm_t_t1") == "Volume",
                st.session_state.get("cm_t_t2") == "Solute",
                st.session_state.get("cm_t_t3") == "Solvant",
                st.session_state.get("cm_t_t4") == "Aqueuse",
                st.session_state.get("cm_t_t5") == "Litre",
                st.session_state.get("cm_t_t6") == "Gramme",
                st.session_state.get("cm_t_t7") == "Litres",
                st.session_state.get("cm_t_t8") == "Saturee",
                st.session_state.get("cm_t_t9") == "Volume",
                st.session_state.get("cm_t_t10") == "Dilution"
            ])

            st.session_state.score_cm_p1 = round(float(score_q2), 1)
            st.session_state.score_cm_p2 = round(float(score_t2), 1)
            st.session_state.score_final_cm = round(float(score_q2 + score_t2), 1)
            st.session_state.v_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab2", False):
        scr1_cm = st.session_state.get("score_cm_p1", 0.0)
        scr2_cm = st.session_state.get("score_cm_p2", 0.0)
        tot_s_cm = st.session_state.get("score_final_cm", 0.0)

        p_eleve = str(st.session_state.get("id_prenom", "INCONNU")).upper()
        n_eleve = str(st.session_state.get("id_nom", "INCONNU")).upper()
        c_eleve = str(st.session_state.get("id_classe", "INCONNU")).upper()

        from datetime import datetime
        timestamp_cm = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER CONCENTRATION MASSIQUE SCELLÉ | Note de session : {tot_s_cm:.1f} / 20")

        # Code d'exportation HTML autonome pour l'Atelier 2
        html_export_cm = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Concentration Massique - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier 2 : Calculs de la concentration massique, relations de masse et de volume</p>
                <p>Donnees resolues : m = {m_exercice:.1f} g | V = {v_exercice:.1f} mL &rarr; Cm = {cm_exercice:.1f} g/L</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_cm}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_cm:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                - Note obtenue au Quiz : <strong>{scr1_cm:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2_cm:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 2 : <strong>{tot_s_cm:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_cm" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_cm, 1):
                saisie = st.session_state.get(f"cm_quiz_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_cm += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cm += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_cm = [
            ("1. La concentration massique represente la masse de solute dissous par unite de", st.session_state.get("cm_t_t1"), "Volume"),
            ("2. L'espece chimique solide ou liquide que l'on dissout dans le liquide s'appelle le", st.session_state.get("cm_t_t2"), "Solute"),
            ("3. Le liquide majoritaire dans lequel s'effectue la dissolution s'appelle le", st.session_state.get("cm_t_t3"), "Solvant"),
            ("4. Lorsque le solvant utilise pour fabriquer la solution est l'eau, on obtient une solution", st.session_state.get("cm_t_t4"), "Aqueuse"),
            ("5. L'unite réglementaire de la concentration massique dans le systeme usuel est le gramme par", st.session_state.get("cm_t_t5"), "Litre"),
            ("6. Pour calculer la concentration massique, la masse saisie doit obligatoirement etre exprimee en", st.session_state.get("cm_t_t6"), "Gramme"),
            ("7. Si le volume initial est donne en mL, il faut le diviser par mille pour obtenir des", st.session_state.get("cm_t_t7"), "Litres"),
            ("8. Lorsque l'on ne peut plus dissoudre de solute car la limite est atteinte, la solution est", st.session_state.get("cm_t_t8"), "Saturee"),
            ("9. La formule retournee permettant de calculer la masse de solute est m = Cm multiplie par", st.session_state.get("cm_t_t9"), "Volume"),
            ("10. L'action consistant a rajouter du solvant pur pour diminuer la concentration s'appelle la", st.session_state.get("cm_t_t10"), "Dilution")
        ]

        for num, (phrase, saisie, attendu) in enumerate(phrases_trous_mv, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_cm += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cm += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE L'ATELIER 2 EN HTML",
            data=html_export_cm,
            file_name=f"Rapport_Concentration_Massique_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )
                


with tab4:
    st.header("Préparation d'une solution de concentration molaire précise")
    
    # 1. DÉCLARATION IMPÉRATIVE DES VARIABLES AU DÉBUT DE L'ONGLET
    cm_cible_ds = st.number_input("Concentration massique Cm souhaitée (g/L) :", min_value=0.1, value=12.0, step=0.5, key="ds_cm_input")
    v_fiole_ml_ds = st.selectbox("Volume de la fiole jaugée disponible V (mL) :", [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0], index=3, key="ds_v_input")
    
    # Le calcul qui génère la variable manquante
    v_fiole_l_ds = v_fiole_ml_ds / 1000.0
    masse_calculee_ds = cm_cible_ds * v_fiole_l_ds
    
    st.metric(label="Masse de soluté à peser (m)", value=f"{masse_calculee_ds:.3f} g")
    
    st.write("---")
    st.subheader("Protocole expérimental officiel : Dissolution étape par étape")
    
    st.markdown("### Étape 1 : Pesée du soluté solide")
    col_l1, col_i1 = st.columns([0.6, 0.4])
    with col_l1:
        st.markdown(f"Allumer la balance, poser la coupelle et réaliser la TARE. Prélever le solide à la spatule pour atteindre précisément la masse calculée : **{masse_calculee_ds:.3f} g**.")
    with col_i1:
        st.image("etape1.jpg", caption="Pesée précise du soluté solide", width=250)

    st.divider()

    # Étape 2
    st.markdown("### Étape 2 : Introduction dans la fiole jaugée")
    col_l2, col_i2 = st.columns([0.6, 0.4])
    with col_l2:
        st.markdown(f"Placer un entonnoir sur le col d'une fiole jaugée de **{v_fiole_ml_ds:.0f} mL** et y transférer délicatement l'intégralité du solide pesé.")
    with col_i2:
        st.image("etape2.jpg", caption="Introduction du solide par l'entonnoir", width=250)

    st.divider()

    # Étape 3
    st.markdown("### Étape 3 : Rinçage quantitatif du matériel")
    col_l3, col_i3 = st.columns([0.6, 0.4])
    with col_l3:
        st.markdown("À l'aide d'une pissette d'eau distillée, rincer soigneusement la coupelle et l'entonnoir au-dessus de la fiole pour récupérer toutes les particules solides.")
    with col_i3:
        st.image("etape3.jpg", caption="Rinçage à l'eau distillée", width=250)

    st.divider()

    # Étape 4
    st.markdown("### Étape 4 : Dissolution initiale par agitation")
    col_l4, col_i4 = st.columns([0.6, 0.4])
    with col_l4:
        st.markdown("Remplir la fiole aux deux tiers avec de l'eau distillée, mettre le bouchon et agiter par mouvements réguliers jusqu'à disparition totale des cristaux.")
    with col_i4:
        st.image("etape4.jpg", caption="Agitation pour dissoudre le solide", width=250)

    st.divider()

    # Étape 5
    st.markdown("### Étape 5 : Ajustement final au trait de jauge")
    col_l5, col_i5 = st.columns([0.6, 0.4])
    with col_l5:
        st.markdown("Compléter à la pissette puis à la pipette Pasteur goutte à goutte. Le bas du ménisque doit s'aligner avec le trait de jauge.")
    with col_i5:
        st.image("etape5.jpg", caption="Lecture alignée du ménisque", width=250)

    st.divider()

    # Étape 6
    st.markdown("### Étape 6 : Agiter la fiole après avoir mis un bouchon")
    col_l6, col_i6 = st.columns([0.6, 0.4])
    with col_l6:
        st.markdown("Boucher et retourner la fiole pour homogénéiser.")
    with col_i6:
        st.image("etape6.jpg", caption="Agitation pour homogénéiser la solution", width=250)

    st.divider()

    # Variables de verrouillage et de contrôle pour le questionnaire de l'Atelier 3
    verrou_v3 = st.session_state.get("v_verrouille_tab3", False)

    # L'appel à afficher_questions_dissolution doit être présent juste au-dessus
    st.write("---")

    case_certif_ds = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 3.", 
        key="check_certif_ds_official", 
        disabled=verrou_v3
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_ds_official", use_container_width=True, disabled=verrou_v3):
        st.session_state.id_nom = st.session_state.get("id_nom") or st.session_state.get("nom_var") or "INCONNU"
        st.session_state.id_prenom = st.session_state.get("id_prenom") or st.session_state.get("prenom_var") or "INCONNU"
        st.session_state.id_classe = st.session_state.get("id_classe") or st.session_state.get("classe_var") or "INCONNU"
        
        p_validation = str(st.session_state.id_prenom).upper()
        n_validation = str(st.session_state.id_nom).upper()

        if n_validation == "INCONNU" or p_validation == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_ds:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q3 = 0.0
            if "ordre_quiz_diss" in st.session_state:
                for q_item in st.session_state.ordre_quiz_diss:
                    reponse_eleve = st.session_state.get(f"ds_quiz_q_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # 2. Correction de la Synthese a trous (10 points)
            score_t3 = sum([
                st.session_state.get("ds_t_t1") == "Dissolution",
                st.session_state.get("ds_t_t2") == "Entonnoir",
                st.session_state.get("ds_t_t3") == "Spatule",
                st.session_state.get("ds_t_t4") == "Jaugee",
                st.session_state.get("ds_t_t5") == "Agite",
                st.session_state.get("ds_t_t6") == "Distillee",
                st.session_state.get("ds_t_t7") == "Jauge",
                st.session_state.get("ds_t_t8") == "Goutte",
                st.session_state.get("ds_t_t9") == "Homogene",
                st.session_state.get("ds_t_t10") == "Dilution"
            ])

            st.session_state.score_ds_p1 = round(float(score_q3), 1)
            st.session_state.score_ds_p2 = round(float(score_t3), 1)
            st.session_state.score_final_ds = round(float(score_q3 + score_t3), 1)
            st.session_state.v_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab3", False):
        scr1_ds = st.session_state.get("score_ds_p1", 0.0)
        scr2_ds = st.session_state.get("score_ds_p2", 0.0)
        tot_s_ds = st.session_state.get("score_final_ds", 0.0)

        p_eleve = str(st.session_state.get("id_prenom", "INCONNU")).upper()
        n_eleve = str(st.session_state.get("id_nom", "INCONNU")).upper()
        c_eleve = str(st.session_state.get("id_classe", "INCONNU")).upper()

        from datetime import datetime
        timestamp_ds = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DISSOLUTION SCELLÉ | Note de session : {tot_s_ds:.1f} / 20")

        # Code d'exportation HTML autonome pour l'Atelier 3 (Style Sarcelle/Teal)
        html_export_ds = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dissolution - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier 3 : Preparation d'une solution de concentration precise par dissolution de solide</p>
                <p>Donnees manipulees : Cm cible = {cm_cible_ds:.1f} g/L | Fiole jaugé utilisee = {v_fiole_ml_ds:.0f} mL &rarr; Masse pesee = {masse_calculee_ds:.3f} g</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ds}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_ds:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                - Note obtenue au Quiz : <strong>{scr1_ds:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2_ds:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 3 : <strong>{tot_s_ds:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_diss" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_diss, 1):
                saisie = st.session_state.get(f"ds_quiz_q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ds += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_ds += """
                    </tbody>
                </table>

                <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
                <table>
                    <thead>
                        <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                    </thead>
                    <tbody>
            """

            phrases_trous_ds = [
                ("1. La methode consistant a preparer une solution a partir d'un solute solide s'appelle la", st.session_state.get("ds_t_t1"), "Dissolution"),
                ("2. Pour introduire proprement le solide sans perte dans la fiole, on utilise un", st.session_state.get("ds_t_t2"), "Entonnoir"),
                ("3. Le prelevement du solide dans le flacon d'origine s'effectue proprement avec une", st.session_state.get("ds_t_t3"), "Spatule"),
                ("4. La verrerie jaugee servant de contenant pour cette preparation est la fiole", st.session_state.get("ds_t_t4"), "Jaugee"),
                ("5. Avant d'ajuster au trait superieur, on remplit la fiole aux deux tiers et on l'", st.session_state.get("ds_t_t5"), "Agite"),
                ("6. Le liquide ajoute pour dissoudre le solide et completer la fiole est l'eau", st.session_state.get("ds_t_t6"), "Distillee"),
                ("7. La marque gravee sur le col de la fiole indiquant le volume exact est le trait de", st.session_state.get("ds_t_t7"), "Jauge"),
                ("8. Pour ajuster le menisque sans depasser la ligne, on termine le remplissage au goutte a", st.session_state.get("ds_t_t8"), "Goutte"),
                ("9. Une fois fermee par son bouchon, on retourne la fiole plusieurs fois pour la rendre", st.session_state.get("ds_t_t9"), "Homogene"),
                ("10. Si le niveau depasse la ligne de repere, la concentration de la solution est faussee par", st.session_state.get("ds_t_t10"), "Dilution")
            ]

            for num, (phrase, saisie, attendu) in enumerate(phrases_trous_ds, 1):
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ds += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_ds += """
                    </tbody>
                </table>
            </body>
            </html>
            """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE L'ATELIER 3 EN HTML",
            data=html_export_ds,
            file_name=f"Rapport_Dissolution_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




with tab5:
    st.header("Dilution et concentration molaire")
    
    st.markdown("""
    La dilution est un protocole de laboratoire qui consiste à ajouter du solvant (eau distillée) à une solution initiale, 
    appelée **solution mère**, afin d'obtenir une solution finale moins concentrée, appelée **solution fille**.
    Puisque la masse de soluté ne change pas pendant l'ajout d'eau, on applique l'équation de conservation :
    """)
    st.latex(r"C_{\text{mère}} \times V_{\text{mère}} = C_{\text{fille}} \times V_{\text{fille}}")
    st.markdown("Le **facteur de dilution** (F) représente le nombre de fois que la solution a été diluée :")
    st.latex(r"F = \frac{C_{\text{mère}}}{C_{\text{fille}}} = \frac{V_{\text{fille}}}{V_{\text{mère}}}")

    st.subheader("Simulateur de préparation par dilution")
    st.markdown("Configurez les concentrations de vos solutions pour déterminer la verrerie nécessaire :")

    c1, c2, c3 = st.columns(3)
    with c1:
        c_mere = st.number_input("Concentration de la solution mère C_mère (g/L) :", min_value=0.1, value=20.0, step=0.5, key="dil_cmere_in")
    with c2:
        c_fille = st.number_input("Concentration voulue de la solution fille C_fille (g/L) :", min_value=0.01, value=2.0, step=0.1, key="dil_cfille_in")
    with c3:
        v_fille_ml = st.selectbox("Volume de solution fille souhaité V_fille (mL) :", [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0], index=1, key="dil_vfille_in")
        
    if c_fille >= c_mere:
        st.error("Action impossible : La concentration de la solution fille doit être strictement inférieure à celle de la solution mère.")
    else:
        facteur_f = c_mere / c_fille
        v_mere_ml = v_fille_ml / facteur_f
        
        st.subheader("Calcul des volumes de verrerie")
        st.metric(label="Facteur de dilution à appliquer (F)", value=f"{facteur_f:.1f} x")
        st.info(f"Volume de solution mère à prélever obligatoirement : V_mère = **{v_mere_ml:.2f} mL**")

        st.write("---")
        st.subheader("Protocole expérimental officiel : Dilution étape par étape")

        # Étape 1 : Prélèvement de la solution mère
        st.markdown("### Étape 1 : Prélèvement de la solution mère")
        col_t1, col_i1 = st.columns([0.6, 0.4])
        with col_t1:
            st.markdown(f"""
            * **Manipulation :** Verser un peu de solution mère dans un bécher propre (ne jamais pipeter directement dans le flacon d'origine).
            * **Action de précision :** À l'aide d'une pipette jaugée de **{v_mere_ml:.2f} mL** (ou graduée) munie d'une propipette, aspirer le liquide.
            * **Ajustement :** Aligner précisément le bas du ménisque avec le trait de jauge supérieur de la pipette.
            """)
        with col_i1:
            st.image("dilution1.jpg", caption="Prélèvement de la solution mère à la pipette jaugée", width=250)

        st.divider()

        # Étape 2 : Introduction dans la fiole
        st.markdown("### Étape 2 : Introduction dans la fiole jaugée fille")
        col_t2, col_i2 = st.columns([0.6, 0.4])
        with col_t2:
            st.markdown(f"""
            * **Manipulation :** Placer la pointe de la pipette jaugée dans le col d'une fiole jaugée de **{v_fille_ml:.0f} mL**.
            * **Action de précision :** Laisser le liquide s'écouler librement le long de la paroi inclinée de la fiole.
            * **Règle de précision :** Si la pipette possède un seul trait, laisser la petite goutte rester dans la pointe (elle est prise en compte dans le calibrage).
            """)
        with col_i2:
            st.image("dilution2.jpg", caption="Transfert du prélèvement dans la fiole jaugée fille", width=250)

        st.divider()

        # Étape 3 : Ajout initial de solvant
        st.markdown("### Étape 3 : Ajout initial de solvant et dissolution")
        col_t3, col_i3 = st.columns([0.6, 0.4])
        with col_t3:
            st.markdown("""
            * **Manipulation :** Ajouter de l'eau distillée à l'aide d'une pissette de laboratoire.
            * **Volume :** Remplir le corps de la fiole jaugée aux deux tiers environ de sa capacité totale.
            * **Action :** Ne pas remplir jusqu'au col immédiatement afin de laisser un espace d'air suffisant pour mélanger le liquide.
            """)
        with col_i3:
            st.image("dilution3.jpg", caption="Ajout d'eau distillée aux deux tiers", width=250)

        st.divider()

        # Étape 4 : Homogénéisation intermédiaire
        st.markdown("### Étape 4 : Homogénéisation intermédiaire")
        col_t4, col_i4 = st.columns([0.6, 0.4])
        with col_t4:
            st.markdown("""
            * **Manipulation :** Mettre le bouchon hermétique sur le col de la fiole jaugée.
            * **Mouvement :** Secouer délicatement la fiole par des mouvements circulaires réguliers.
            * **Objectif :** Commencer à répartir de manière uniforme les molécules de soluté dans tout le volume d'eau distillée ajouté.
            """)
        with col_i4:
            st.image("dilution4.jpg", caption="Première agitation circulaire de la solution", width=250)

        st.divider()

        # Étape 5 : Remplissage final au trait de jauge
        st.markdown("### Étape 5 : Remplissage final au trait de jauge")
        col_t5, col_i5 = st.columns([0.6, 0.4])
        with col_t5:
            st.markdown("""
            * **Manipulation :** Ajouter à nouveau de l'eau distillée pour faire monter le niveau dans le col de la fiole.
            * **Action de précision :** Terminer le remplissage très lentement, goutte par goutte, à l'aide d'une pipette Pasteur.
            * **Règle de lecture :** Placer l'œil strictement au niveau de la ligne gravée pour éliminer l'erreur de parallaxe. Stopper l'ajout dès que la base incurvée du ménisque affleure le trait de jauge.
            """)
        with col_i5:
            st.image("dilution5.jpg", caption="Ajustement final précis au goutte-à-goutte", width=250)

        st.divider()

        # Étape 6 : Homogénéisation finale
        st.markdown("### Étape 6 : Homogénéisation finale par retournement")
        col_t6, col_i6 = st.columns([0.6, 0.4])
        with col_t6:
            st.markdown("""
            * **Manipulation :** Placer fermement le bouchon sur la fiole jaugée.
            * **Mouvement de laboratoire :** Retourner complètement la fiole plusieurs fois de haut en bas en maintenant le bouchon.
            * **Résultat :** La solution fille obtenue est maintenant parfaitement homogène. Sa concentration finale est rigoureusement égale à la valeur ciblée.
            """)
        with col_i6:
            st.image("dilution6.jpg", caption="Retournement final pour uniformiser la concentration", width=250)

        st.divider()

        # DÉCLARATION IMPÉRATIVE DES VARIABLES DE CONTRÔLE DE L'ATELIER 4
        verrou_v4 = st.session_state.get("v_verrouille_tab4", False)

        # Ligne 2237 sécurisée : verrou_v4 existe désormais obligatoirement en mémoire
        case_certif_dil = st.checkbox(
            "Je certifie avoir complete les questions de l'Atelier 4.", 
            key="check_certif_dil_official", 
            disabled=verrou_v4
        )

        st.write("---")

        if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_dil_official", use_container_width=True, disabled=verrou_v4):
            st.session_state.id_nom = st.session_state.get("id_nom") or st.session_state.get("nom_var") or "INCONNU"
            st.session_state.id_prenom = st.session_state.get("id_prenom") or st.session_state.get("prenom_var") or "INCONNU"
            st.session_state.id_classe = st.session_state.get("id_classe") or st.session_state.get("classe_var") or "INCONNU"
            
            p_validation = str(st.session_state.id_prenom).upper()
            n_validation = str(st.session_state.id_nom).upper()

            if n_validation == "INCONNU" or p_validation == "INCONNU":
                st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
            elif not case_certif_dil:
                st.error("Action refusee : Cochez la case de certification.")
            else:
                # 1. Correction du Quiz (10 points)
                score_q4 = 0.0
                if "ordre_quiz_dil" in st.session_state:
                    for q_item in st.session_state.ordre_quiz_dil:
                        reponse_eleve = st.session_state.get(f"dil_quiz_q_{q_item['id']}", "Choisir...")
                        if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                            score_q4 += 1.0

                # 2. Correction de la Synthese a trous (10 points)
                score_t4 = sum([
                    st.session_state.get("dil_t_t1") == "Solvant",
                    st.session_state.get("dil_t_t2") == "Mere",
                    st.session_state.get("dil_t_t3") == "Fille",
                    st.session_state.get("dil_t_t4") == "Jaugee",
                    st.session_state.get("dil_t_t5") == "Dilution",
                    st.session_state.get("dil_t_t6") == "Conservent",
                    st.session_state.get("dil_t_t7") == "Jaugee",
                    st.session_state.get("dil_t_t8") == "Propipette",
                    st.session_state.get("dil_t_t9") == "C_fille",
                    st.session_state.get("dil_t_t10") == "V_mere"
                ])

                st.session_state.score_dil_p1 = round(float(score_q4), 1)
                st.session_state.score_dil_p2 = round(float(score_t4), 1)
                st.session_state.score_final_dil = round(float(score_q4 + score_t4), 1)
                st.session_state.v_verrouille_tab4 = True
                st.rerun()

        if st.session_state.get("v_verrouille_tab4", False):
            scr1_dil = st.session_state.get("score_dil_p1", 0.0)
            scr2_dil = st.session_state.get("score_dil_p2", 0.0)
            tot_s_dil = st.session_state.get("score_final_dil", 0.0)

            p_eleve = str(st.session_state.get("id_prenom", "INCONNU")).upper()
            n_eleve = str(st.session_state.get("id_nom", "INCONNU")).upper()
            c_eleve = str(st.session_state.get("id_classe", "INCONNU")).upper()

            from datetime import datetime
            timestamp_dil = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

            st.success(f"ATELIER DILUTION SCELLÉ | Note de session : {tot_s_dil:.1f} / 20")
            html_export_dil = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport Dilution - {n_eleve}</title>
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
                    <h1>Rapport d'Evaluation de Chimie</h1>
                    <p>Atelier 4 : Preparation d'une solution fille par dilution d'une solution mere</p>
                    <p>Donnees manipulees : C_mere = {c_mere:.1f} g/L &rarr; C_fille = {c_fille:.1f} g/L | Fiole fille = {v_fille_ml:.0f} mL | Pipette prelevement = {v_mere_ml:.2f} mL</p>
                    <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                    <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_dil}</p>
                    <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_dil:.1f}</span> / 20</div>
                </div>
                
                <div class="sub-title">Recapitulatif des Notes Generees</div>
                <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #6d28d9;">
                    - Note obtenue au Quiz : <strong>{scr1_dil:.1f} / 10</strong><br>
                    - Note obtenue a la Synthese de cours : <strong>{scr2_dil:.1f} / 10</strong><br>
                    - Note Totale de l'Atelier 4 : <strong>{tot_s_dil:.1f} / 20</strong>
                </p>

                <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
                <table>
                    <thead>
                        <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                    </thead>
                    <tbody>
            """

            if "ordre_quiz_dil" in st.session_state:
                for num, q_item in enumerate(st.session_state.ordre_quiz_dil, 1):
                    saisie = st.session_state.get(f"dil_quiz_q_{q_item['id']}", "Choisir...")
                    attendu = q_item["rep"]
                    v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                    v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                    html_export_dil += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_dil += """
                    </tbody>
                </table>

                <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
                <table>
                    <thead>
                        <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                    </thead>
                    <tbody>
            """

            phrases_trous_dil = [
                ("1. Diluer une solution consiste a diminuer sa concentration en y ajoutant du", st.session_state.get("dil_t_t1"), "Solvant"),
                ("2. La solution de depart, qui possede la concentration la plus elevee, est la solution", st.session_state.get("dil_t_t2"), "Mere"),
                ("3. La solution finale obtenue apres l'ajout d'eau distillee est la solution", st.session_state.get("dil_t_t3"), "Fille"),
                ("4. Le prelevement rigoureux du volume de solution mere s'effectue avec une pipette", st.session_state.get("dil_t_t4"), "Jaugee"),
                ("5. Le nombre de fois que la solution a ete diluee est caracterise par le facteur de", st.session_state.get("dil_t_t5"), "Dilution"),
                ("6. Au cours de la manipulation, la quantite et la masse de solute se", st.session_state.get("dil_t_t6"), "Conservent"),
                ("7. La solution fille est preparee dans un recipient jauge appele une fiole", st.session_state.get("dil_t_t7"), "Jaugee"),
                ("8. Pour aspirer le liquide en toute securite sans contact, on utilise une", st.session_state.get("dil_t_t8"), "Propipette"),
                ("9. Le rapport des concentrations indique que le facteur F est egal a C_mere divise par", st.session_state.get("dil_t_t9"), "C_fille"),
                ("10. Le rapport des volumes indique que le facteur F est egal a V_fille divise par", st.session_state.get("dil_t_t10"), "V_mere")
            ]

            for num, (phrase, saisie, attendu) in enumerate(phrases_trous_dil, 1):
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_dil += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

            html_export_dil += """
                    </tbody>
                </table>
            </body>
            </html>
            """

            st.download_button(
                label="TELECHARGER LE RAPPORT DE L'ATELIER 4 EN HTML",
                data=html_export_dil,
                file_name=f"Rapport_Dilution_{n_eleve}.html",
                mime="text/html",
                use_container_width=True
            )


with tab6:
    st.header("Atelier6 : Évaluation globale de synthèse")
    st.markdown("""
    Cette épreuve finale regroupe une partie pratique de **Dissolution** et une partie pratique de **Dilution** 
    basée sur un flacon commercial attribué au hasard. Aucun émoji n'est toléré, résolvez vos calculs méthodiquement.
    """)
    
    col_p1, col_p2 = st.columns([0.4, 0.6])
    with col_p1:
        st.caption("Flacon de solution mère assigné :")
        try:
            st.image(prod_actif["img"], caption=f"Flacon de {prod_actif['nom']}", width=250)
        except Exception:
            st.warning("Visuel indisponible. Fiez-vous aux caractéristiques de l'étiquette.")
            
    with col_p2:
        st.markdown("**Données techniques de l'étiquette :**")
        st.markdown(f"""
        * **Nom chimique du composé :** {prod_actif['nom']}
        * **Formule brute :** {prod_actif['formule']}
        * **Concentration massique initiale C_mère :** **{cm_mere_hasard:.1f} g/L**
        * **Risques SGH et sécurité :** {prod_actif['danger']}
        """)

    st.write("---")
    
    # PARTIE A : DISSOLUTION
    st.subheader("Partie A : Protocole expérimental de Dissolution")
    st.markdown(f"""
    Le professeur vous demande de préparer un volume $V$ = **{v_fiole_diss:.0f} mL** d'une solution aqueuse de {prod_actif['nom']} 
    à une concentration massique précise de $C_m$ = **{cm_diss_cible:.1f} g/L** par dissolution d'une poudre solide.
    """)
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        saisie_m_diss = st.number_input("Quelle masse m de solide devez-vous peser sur la balance (en g) ?", min_value=0.0, step=0.001, format="%.3f", key="syn_in_m_diss")
    with col_a2:
        saisie_verre_diss = st.selectbox("Dans quelle verrerie de précision devez-offset cette dissolution ?", ["Choisir...", "Fiole jaugée", "Éprouvette graduée", "Bécher gradué"], key="syn_in_verre_diss")

    st.write("---")

    # PARTIE B : DILUTION
    st.subheader("Partie B : Protocole expérimental de Dilution")
    
    st.markdown(f"En utilisant le flacon commercial de solution mère donné au début du sujet ({cm_mere_hasard:.1f} g/L), vous devez maintenant préparer une solution fille moins concentrée.")
    
    # Isolation propre de la formule mathématique en LaTeX
    st.latex(rf"V_{{\text{{fille}}}} = {v_fille_ml_hasard:.0f}\text{{ mL}}")
    
    st.markdown(f"Le protocole stipule que cette solution doit être exactement **{facteur_hasard:.0f} fois moins concentrée** (facteur de dilution F = {facteur_hasard:.0f}x).")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        saisie_cm_fille = st.number_input("Quelle sera la concentration de votre solution fille obtenue C_fille (en g/L) ?", min_value=0.0, step=0.01, format="%.2f", key="syn_in_cm_fille")
        saisie_verre_mere = st.selectbox("Quelle verrerie sert à prélever la solution mère ?", ["Choisir...", "Pipette jaugée", "Éprouvette graduée", "Bécher"], key="syn_in_verre_mere")
    with col_b2:
        saisie_v_mere = st.number_input("Quel volume de solution mère V_mère faut-il prélever à la pipette (en mL) ?", min_value=0.0, step=0.01, format="%.2f", key="syn_in_v_mere")
        saisie_verre_fille = st.selectbox("Dans quel récipient jaugé final prépare-t-on la solution fille ?", ["Choisir...", "Fiole jaugée", "Erlenmeyer", "Éprouvette graduée"], key="syn_in_verre_fille")

    st.write("---")
    verrou_v5 = st.session_state.get("v_verrouille_tab5", False)

    # L'appel à afficher_questions_synthese_laboratoire doit être présent juste au-dessus
    st.write("---")

    case_certif_ex = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 5.", 
        key="check_certif_ex_official", 
        disabled=verrou_v5
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_ex_official", use_container_width=True, disabled=verrou_v5):
        # Synchronisation de l'identité Nom, Prénom, Classe
        st.session_state.id_nom = st.session_state.get("id_nom") or st.session_state.get("nom_var") or "INCONNU"
        st.session_state.id_prenom = st.session_state.get("id_prenom") or st.session_state.get("prenom_var") or "INCONNU"
        st.session_state.id_classe = st.session_state.get("id_classe") or st.session_state.get("classe_var") or "INCONNU"
        
        p_validation = str(st.session_state.id_prenom).upper()
        n_validation = str(st.session_state.id_nom).upper()

        if n_validation == "INCONNU" or p_validation == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_ex:
            st.error("Action refusee : Cochez la case de certification.")
        elif "Choisir..." in [saisie_verre_diss, saisie_verre_mere, saisie_verre_fille]:
            st.error("Action refusee : Veuillez sélectionner la verrerie pour l'ensemble des questions.")
        else:
            # 1. Correction de la manipulation de Dissolution (5 points)
            v_m_diss_lbl = "CORRECT" if abs(saisie_m_diss - m_diss_attendue) <= 0.005 else "INCORRECT"
            v_v_diss_lbl = "CORRECT" if saisie_verre_diss == "Fiole jaugée" else "INCORRECT"
            
            # 2. Correction de la manipulation de Dilution (5 points)
            v_cm_fille_lbl = "CORRECT" if abs(saisie_cm_fille - cm_fille_attendue) <= 0.1 else "INCORRECT"
            v_v_mere_lbl = "CORRECT" if saisie_verre_mere == "Pipette jaugée" else "INCORRECT"
            v_v_fille_lbl = "CORRECT" if saisie_verre_fille == "Fiole jaugée" else "INCORRECT"
            v_v_mere_vol_lbl = "CORRECT" if abs(saisie_v_mere - v_mere_attendu_ml) <= 0.1 else "INCORRECT"

            # 3. Correction du Quiz (5 points)
            score_q5 = 0.0
            if "ordre_quiz_tab5" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5:
                    rep_el = st.session_state.get(f"syn_quiz_q_{q_item['id']}", "Choisir...")
                    if str(rep_el).strip() == str(q_item["rep"]).strip():
                        score_q5 += 0.5

            # 4. Correction de la Synthèse à trous (5 points)
            score_t5 = sum([
                st.session_state.get("syn_t_t1") == "Dissolution",
                st.session_state.get("syn_t_t2") == "Dilution",
                st.session_state.get("syn_t_t3") == "Spatule",
                st.session_state.get("syn_t_t4") == "Propipette",
                st.session_state.get("syn_t_t5") == "Distillee",
                st.session_state.get("syn_t_t6") == "Mere",
                st.session_state.get("syn_t_t7") == "Fille",
                st.session_state.get("syn_t_t8") == "Conserve",
                st.session_state.get("syn_t_t9") == "Jauge",
                st.session_state.get("syn_t_t10") == "Pasteur"
            ]) * 0.5

            # Calcul des points des manipulations
            pts_diss = (2.5 if v_m_diss_lbl == "CORRECT" else 0.0) + (2.5 if v_v_diss_lbl == "CORRECT" else 0.0)
            pts_dil = (1.25 if v_cm_fille_lbl == "CORRECT" else 0.0) + (1.25 if v_v_mere_lbl == "CORRECT" else 0.0) + (1.25 if v_v_fille_lbl == "CORRECT" else 0.0) + (1.25 if v_v_mere_vol_lbl == "CORRECT" else 0.0)
            
            st.session_state.score_ex_final = round(float(pts_diss + pts_dil + score_q5 + score_t5), 1)
            st.session_state.v_m_diss_lbl = v_m_diss_lbl
            st.session_state.v_v_diss_lbl = v_v_diss_lbl
            st.session_state.v_cm_fille_lbl = v_cm_fille_lbl
            st.session_state.v_v_mere_lbl = v_v_mere_lbl
            st.session_state.v_v_fille_lbl = v_v_fille_lbl
            st.session_state.v_v_mere_vol_lbl = v_v_mere_vol_lbl
            st.session_state.score_q5_save = round(float(score_q5), 1)
            st.session_state.score_t5_save = round(float(score_t5), 1)
            st.session_state.v_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab5", False):
        tot_s_ex = st.session_state.get("score_ex_final", 0.0)
        v_m_diss_lbl = st.session_state.get("v_m_diss_lbl", "INCORRECT")
        v_v_diss_lbl = st.session_state.get("v_v_diss_lbl", "INCORRECT")
        v_cm_fille_lbl = st.session_state.get("v_cm_fille_lbl", "INCORRECT")
        v_v_mere_lbl = st.session_state.get("v_v_mere_lbl", "INCORRECT")
        v_v_fille_lbl = st.session_state.get("v_v_fille_lbl", "INCORRECT")
        v_v_mere_vol_lbl = st.session_state.get("v_v_mere_vol_lbl", "INCORRECT")
        scr_q5 = st.session_state.get("score_q5_save", 0.0)
        scr_t5 = st.session_state.get("score_t5_save", 0.0)

        p_eleve = str(st.session_state.get("id_prenom", "INCONNU")).upper()
        n_eleve = str(st.session_state.get("id_nom", "INCONNU")).upper()
        c_eleve = str(st.session_state.get("id_classe", "INCONNU")).upper()

        from datetime import datetime
        timestamp_ex = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ÉVALUATION FINALE SCELLÉ | Note de session : {tot_s_ex:.1f} / 20")
        
        html_export_ex = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Evaluation Finale - {n_eleve}</title>
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
                <h1>Rapport de Bilan de Laboratoire</h1>
                <p>Atelier 5 : Synthese complete - Dissolution et Dilution</p>
                <p>Produit de reference : {prod_actif['nom']} | Solution mere d'exercice : C_mere = {cm_mere_hasard:.1f} g/L</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ex}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_ex:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                - Evaluation de la manipulation Partie A (Dissolution) : <strong>{(2.5 if v_m_diss_lbl == "CORRECT" else 0.0) + (2.5 if v_v_diss_lbl == "CORRECT" else 0.0):.1f} / 5.0</strong><br>
                - Evaluation de la manipulation Partie B (Dilution) : <strong>{(1.25 if v_cm_fille_lbl == "CORRECT" else 0.0) + (1.25 if v_v_mere_lbl == "CORRECT" else 0.0) + (1.25 if v_v_fille_lbl == "CORRECT" else 0.0) + (1.25 if v_v_mere_vol_lbl == "CORRECT" else 0.0):.2f} / 5.0</strong><br>
                - Note obtenue au Quiz : <strong>{scr_q5:.1f} / 5.0</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr_t5:.1f} / 5.0</strong><br>
                - Note globale de l'Atelier 5 : <strong>{tot_s_ex:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction detaillee de votre fiole commerciale</div>
            <table>
                <thead>
                    <tr><th>Grandeur ou Choix evalue</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Masse a peser (Dissolution)</strong></td>
                        <td>{saisie_m_diss:.3f} g</td>
                        <td>{m_diss_attendue:.3f} g</td>
                        <td class='{"status-correct" if v_m_diss_lbl == "CORRECT" else "status-incorrect"}'>{v_m_diss_lbl}</td>
                    </tr>
                    <tr>
                        <td><strong>Verrerie de dissolution</strong></td>
                        <td>{saisie_verre_diss}</td>
                        <td>Fiole jaugée</td>
                        <td class='{"status-correct" if v_v_diss_lbl == "CORRECT" else "status-incorrect"}'>{v_v_diss_lbl}</td>
                    </tr>
                    <tr>
                        <td><strong>Concentration fille C_fille (Dilution)</strong></td>
                        <td>{saisie_cm_fille:.2f} g/L</td>
                        <td>{cm_fille_attendue:.2f} g/L</td>
                        <td class='{"status-correct" if v_cm_fille_lbl == "CORRECT" else "status-incorrect"}'>{v_cm_fille_lbl}</td>
                    </tr>
                    <tr>
                        <td><strong>Volume de solution mere V_mere</strong></td>
                        <td>{saisie_v_mere:.2f} mL</td>
                        <td>{v_mere_attendu_ml:.2f} mL</td>
                        <td class='{"status-correct" if v_v_mere_vol_lbl == "CORRECT" else "status-incorrect"}'>{v_v_mere_vol_lbl}</td>
                    </tr>
                    <tr>
                        <td><strong>Verrerie de prelevement mere</strong></td>
                        <td>{saisie_verre_mere}</td>
                        <td>Pipette jaugée</td>
                        <td class='{"status-correct" if v_v_mere_lbl == "CORRECT" else "status-incorrect"}'>{v_v_mere_lbl}</td>
                    </tr>
                    <tr>
                        <td><strong>Récipient final solution fille</strong></td>
                        <td>{saisie_verre_fille}</td>
                        <td>Fiole jaugée</td>
                        <td class='{"status-correct" if v_v_fille_lbl == "CORRECT" else "status-incorrect"}'>{v_v_fille_lbl}</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE L'ATELIER 5 EN HTML",
            data=html_export_ex,
            file_name=f"Rapport_Atelier5_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )

        if st.button("Effacer le scellé et générer une nouvelle évaluation", key="btn_reset_final_session"):
            if "syn_prod_index" in st.session_state:
                del st.session_state.syn_prod_index
                del st.session_state.syn_v_fille
                del st.session_state.syn_facteur
                del st.session_state.syn_cm_diss
                del st.session_state.syn_v_diss
                if "v_verrouille_tab5" in st.session_state:
                    del st.session_state.v_verrouille_tab5
            st.rerun()






                        
