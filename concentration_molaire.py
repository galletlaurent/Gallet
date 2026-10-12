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

def afficher_questions_tab4_completes(m_solide, v_fiole, c_cible, M_solide, verrouille=False):
    import random
    
    if "ordre_quiz_tab4_10q" not in st.session_state:
        base_quiz = [
            {"id": "t4_q1", "q": "Quelle formule mathématique fondamentale relie la masse (m) à peser, la concentration molaire (C), le volume (V) et la masse molaire (M) ?", "options": ["m = C * V * M", "m = (C * V) / M", "m = C / (V * M)"], "rep": "m = C * V * M"},
            {"id": "t4_q2", "q": f"Pour préparer votre solution actuelle (C = {c_cible:.2f} mol/L, M = {M_solide:.1f} g/mol) dans une fiole de {v_fiole:.0f} mL, quelle masse exacte devez-vous peser ?", "options": [f"{m_solide:.3f} g", f"{m_solide * 1000:.1f} g", f"{m_solide / 10:.3f} g"], "rep": f"{m_solide:.3f} g"},
            {"id": "t4_q3", "q": "Quelle est la toute première étape de manipulation lors d'une dissolution au laboratoire ?", "options": ["Allumer la balance, poser la coupelle vide et réaliser la TARE", "Introduire le solide directement au fond de la fiole jaugée", "Remplir la fiole jaugée avec de l'eau distillée"], "rep": "Allumer la balance, poser la coupelle vide et réaliser la TARE"},
            {"id": "t4_q4", "q": "Quel récipient de haute précision utilise-t-on obligatoirement pour fabriquer une solution par dissolution ?", "options": ["La fiole jaugée", "Le bécher gradué", "L'erlenmeyer conique"], "rep": "La fiole jaugée"},
            {"id": "t4_q5", "q": "Quel ustensile de laboratoire permet de prélever proprement la poudre solide sans contamination ?", "options": ["Une spatule propre", "Une pipette graduée", "Une tige en verre"], "rep": "Une spatule propre"},
            {"id": "t4_q6", "q": "Pourquoi doit-on rincer la coupelle de pesée et l'entonnoir à la pissette d'eau distillée au-dessus de la fiole ?", "options": ["Pour transférer l'intégralité du soluté pesé et éviter les pertes", "Pour laver le matériel avant de le ranger sur la paillasse", "Pour accélérer la réaction chimique de dissolution"], "rep": "Pour transférer l'intégralité du soluté pesé et éviter les pertes"},
            {"id": "t4_q7", "q": "À quel niveau approximatif doit-on remplir la fiole d'eau distillée pour effectuer la première agitation ?", "options": ["Aux deux tiers environ du corps de la fiole", "Directement jusqu'au trait de jauge", "À ras bord du col de la fiole"], "rep": "Aux deux tiers environ du corps de la fiole"},
            {"id": "t4_q8", "q": "Quel outil permet d'ajuster avec une extrême minutie le liquide goutte à goutte jusqu'au trait de jauge ?", "options": ["Une pipette simple ou pipette Pasteur", "Un entonnoir large", "Une pissette d'eau distillée à plein débit"], "rep": "Une pipette simple ou pipette Pasteur"},
            {"id": "t4_q9", "q": "Quelle erreur commet-on si la base du ménisque dépasse la ligne gravée du trait de jauge ?", "options": ["La solution est trop diluée, le protocole est raté et il faut recommencer", "La solution est correcte car le volume est légèrement supérieur", "Il suffit d'aspirer le surplus de liquide avec une pissette vide"], "rep": "La solution est trop diluée, le protocole est raté et il faut recommencer"},
            {"id": "t4_q10", "q": "Comment élimine-t-on l'erreur de parallaxe lors de la lecture finale du niveau de liquide ?", "options": ["En plaçant son regard strictement horizontal en face du trait de jauge", "En regardant la fiole par-dessus en penchant la tête", "En soulevant la fiole jaugée bien au-dessus de ses yeux"], "rep": "En plaçant son regard strictement horizontal en face du trait de jauge"}
        ]
        random.shuffle(base_quiz)
        st.session_state.ordre_quiz_tab4_10q = base_quiz

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Quiz : Protocole de Dissolution Molaire (10 questions - 10 pts)")
        rep_q4 = {}
        for idx, item in enumerate(st.session_state.ordre_quiz_tab4_10q, 1):
            st.write(f"**{idx}.** {item['q']}")
            opts_key = f"opts_t4_10q_{item['id']}"
            if opts_key not in st.session_state:
                opts = list(item["options"])
                random.shuffle(opts)
                st.session_state[opts_key] = ["Choisir..."] + opts
            val = st.session_state.get(f"sel_t4_10q_{item['id']}", "Choisir...")
            sel_idx = st.session_state[opts_key].index(val) if val in st.session_state[opts_key] else 0
            rep_q4[item["id"]] = st.selectbox("", st.session_state[opts_key], index=sel_idx, key=f"sel_t4_10q_{item['id']}", disabled=verrouille, label_visibility="collapsed")
            
    with col2:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        trous_q4 = {}
        
        c1, c2 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c1: st.write("1. La préparation d'une solution à partir d'un soluté solide s'appelle la")
        with c2: trous_q4["t1"] = st.selectbox("", ["Choisir...", "Dissolution", "Dilution", "Fusion"], key="t4_10t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c3: st.write("2. Pour introduire proprement la poudre sans perte dans le col étroit, on utilise un")
        with c4: trous_q4["t2"] = st.selectbox("", ["Choisir...", "Entonnoir", "Agitateur", "Filtre"], key="t4_10t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c5: st.write("3. Le prélèvement de la poudre dans le flacon d'origine s'effectue avec une")
        with c6: trous_q4["t3"] = st.selectbox("", ["Choisir...", "Spatule", "Pipette", "Éprouvette"], key="t4_10t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c7: st.write("4. La verrerie jaugée servant de contenant pour cette préparation de précision est la fiole")
        with c8: trous_q4["t4"] = st.selectbox("", ["Choisir...", "Jaugee", "Graduee", "Conique"], key="t4_10t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c9: st.write("5. Avant d'ajuster au trait supérieur, on remplit aux deux tiers et on")
        with c10: trous_q4["t5"] = st.selectbox("", ["Choisir...", "Agite", "Pese", "Chauffe"], key="t4_10t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c11: st.write("6. Le liquide ajouté pour dissoudre le solide et compléter la fiole est l'eau")
        with c12: trous_q4["t6"] = st.selectbox("", ["Choisir...", "Distillee", "Robinet", "Minerale"], key="t4_10t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c13: st.write("7. La marque gravée sur le col de la fiole indiquant le volume exact est le trait de")
        with c14: trous_q4["t7"] = st.selectbox("", ["Choisir...", "Jauge", "Graduation", "Repere"], key="t4_10t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c15: st.write("8. Pour ajuster le ménisque sans dépasser la ligne, on termine le remplissage au goutte à")
        with c16: trous_q4["t8"] = st.selectbox("", ["Choisir...", "Goutte", "Bouchon", "Filet"], key="t4_10t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c17: st.write("9. Une fois fermée par son bouchon, on retourne la fiole plusieurs fois pour la rendre")
        with r18: trous_q4["t9"] = st.selectbox("", ["Choisir...", "Homogene", "Heterogene", "Saturee"], key="t4_10t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c19: st.write("10. Si le niveau dépasse la ligne de repère, la concentration de la solution est faussée par sur-")
        with c20: trous_q4["t10"] = st.selectbox("", ["Choisir...", "Dilution", "Dissolution", "Pesee"], key="t4_10t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep, trous_q4


def afficher_questions_tab3_completes(verrouille=False):
    import random
    
    if "ordre_quiz_tab3_10q" not in st.session_state:
        base_quiz = [
            {"id": "t3_q1", "q": "Quelle formule permet de calculer le nombre de moles (n) pour une espèce dissoute en solution ?", "options": ["n = C * V", "n = C / V", "n = V / C"], "rep": "n = C * V"},
            {"id": "t3_q2", "q": "Quelle relation mathématique définit la quantité de matière (n) pour un solide ?", "options": ["n = m / M", "n = m * M", "n = M / m"], "rep": "n = m / M"},
            {"id": "t3_q3", "q": "Quelle équation utilise-t-on pour trouver le nombre de moles (n) d'un échantillon de gaz ?", "options": ["n = V / Vm", "n = V * Vm", "n = Vm / V"], "rep": "n = V / Vm"},
            {"id": "t3_q4", "q": "Dans la formule des solutions liquides, quelle unité doit obligatoirement avoir le volume V ?", "options": ["Le Litre (L)", "Le Millilitre (mL)", "Le mètre cube (m³)"], "rep": "Le Litre (L)"},
            {"id": "t3_q5", "q": "Quelle est l'unité usuelle du volume molaire (Vm) des gaz ?", "options": ["Le litre par mole (L/mol)", "La mole par litre (mol/L)", "Le gramme par mole (g/mol)"], "rep": "Le litre par mole (L/mol)"},
            {"id": "t3_q6", "q": "Si on multiplie une concentration molaire (C) par un volume (V), quelle grandeur obtient-on ?", "options": ["Une quantité de matière (n)", "Une masse solide (m)", "Un volume molaire (Vm)"], "rep": "Une quantité de matière (n)"},
            {"id": "t3_q7", "q": "Au laboratoire, si un volume est donné en mL pour calculer n = C * V, il faut d'abord :", "options": ["Le diviser par 1000 pour le convertir en Litres", "Le multiplier par 1000 pour avoir des Litres", "Le laisser tel quel sans modification"], "rep": "Le diviser par 1000 pour le convertir en Litres"},
            {"id": "t3_q8", "q": "Un volume de 250 mL converti en Litres correspond à :", "options": ["0,250 L", "2,50 L", "0,025 L"], "rep": "0,250 L"},
            {"id": "t3_q9", "q": "Si un gaz occupe un volume V = 48 L dans des conditions où Vm = 24 L/mol, quelle est sa quantité de matière ?", "options": ["2,0 mol", "0,5 mol", "1152 mol"], "rep": "2,0 mol"},
            {"id": "t3_q10", "q": "Pour un solide, quelle formule dérivée permet d'isoler la masse m si l'on connaît n et M ?", "options": ["m = n * M", "m = n / M", "m = M / n"], "rep": "m = n * M"}
        ]
        random.shuffle(base_quiz)
        st.session_state.ordre_quiz_tab3_10q = base_quiz

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Quiz : Calculs de moles (10 questions - 10 pts)")
        rep_q3 = {}
        for idx, item in enumerate(st.session_state.ordre_quiz_tab3_10q, 1):
            st.write(f"**{idx}.** {item['q']}")
            opts_key = f"opts_t3_10q_{item['id']}"
            if opts_key not in st.session_state:
                opts = list(item["options"])
                random.shuffle(opts)
                st.session_state[opts_key] = ["Choisir..."] + opts
            val = st.session_state.get(f"sel_t3_10q_{item['id']}", "Choisir...")
            sel_idx = st.session_state[opts_key].index(val) if val in st.session_state[opts_key] else 0
            rep_q3[item["id"]] = st.selectbox("", st.session_state[opts_key], index=sel_idx, key=f"sel_t3_10q_{item['id']}", disabled=verrouille, label_visibility="collapsed")
            
    with col2:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        trous_q3 = {}
        
        c1, c2 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c1: st.write("1. Pour un composé solide, la quantité de matière s'obtient en divisant la masse par la masse")
        with c2: trous_q3["t1"] = st.selectbox("", ["Choisir...", "Molaire", "Volumique", "Atomique"], key="t3_10t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c3: st.write("2. Pour une solution, le nombre de moles est égal au produit de la concentration par le")
        with c4: trous_q3["t2"] = st.selectbox("", ["Choisir...", "Volume", "Soluté", "Solvant"], key="t3_10t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c5: st.write("3. Pour calculer le nombre de moles d'un gaz, on divise son volume par le volume")
        with c6: trous_q3["t3"] = st.selectbox("", ["Choisir...", "Molaire", "Total", "Massique"], key="t3_10t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c7: st.write("4. L'unité légale du volume V à introduire dans la relation n = C * V est le")
        with c8: trous_q3["t4"] = st.selectbox("", ["Choisir...", "Litre", "Millilitre", "Gramme"], key="t3_10t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c9: st.write("5. Le volume occupé par une mole de n'importe quel gaz s'appelle le volume")
        with c10: trous_q3["t5"] = st.selectbox("", ["Choisir...", "Molaire", "Massique", "Partiel"], key="t3_10t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c11: st.write("6. L'unité du volume molaire des gaz s'exprime en litres par")
        with c12: trous_q3["t6"] = st.selectbox("", ["Choisir...", "Mole", "Gramme", "Seconde"], key="t3_10t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c13: st.write("7. Si le volume d'une solution est fourni en mL, on doit impérativement le diviser par")
        with c14: trous_q3["t7"] = st.selectbox("", ["Choisir...", "Mille", "Cent", "Dix"], key="t3_10t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c15: st.write("8. La formule liant les grandeurs d'une solution liquide est n = C multiplié par")
        with c16: trous_q3["t8"] = st.selectbox("", ["Choisir...", "V", "M", "Vm"], key="t3_10t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c17: st.write("9. La formule pour déterminer la masse d'un solide à partir de ses moles est m = n fois")
        with r18: trous_q3["t9"] = st.selectbox("", ["Choisir...", "M", "V", "C"], key="t3_10t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c19: st.write("10. Quelle que soit la méthode (solide, liquide ou gaz), le résultat n s'exprime en")
        with c20: trous_q3["t10"] = st.selectbox("", ["Choisir...", "Moles", "Grammes", "Litres"], key="t3_10t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q3, dict_trous_3

def afficher_questions_tab2_completes(verrouille=False):
    import random
    
    if "ordre_quiz_tab2_10q" not in st.session_state:
        base_quiz = [
            {"id": "t2_q1", "q": "Quelle est la définition scientifique d'une mole d'atomes ?", "options": ["Un paquet contenant exactement 6,022 x 10^23 atomes", "Une masse de exactement un kilogramme de matière", "Le volume occupé par un gramme de gaz de cette espèce"], "rep": "Un paquet contenant exactement 6,022 x 10^23 atomes"},
            {"id": "t2_q2", "q": "Où trouve-t-on la valeur de la masse molaire atomique d'un élément chimique ?", "options": ["Dans le tableau périodique des éléments", "En la mesurant avec une éprouvette graduée", "Sur l'étiquette de sécurité de la pissette"], "rep": "Dans le tableau périodique des éléments"},
            {"id": "t2_q3", "q": "Quelle est l'unité légale de la masse molaire (qu'elle soit atomique ou moléculaire) ?", "options": ["Le gramme par mole (g/mol)", "Le mole par gramme (mol/g)", "Le gramme par litre (g/L)"], "rep": "Le gramme par mole (g/mol)"},
            {"id": "t2_q4", "q": "Comment calcule-t-on la masse molaire moléculaire du gaz contenu dans l'air (Dioxygène O2) ?", "options": ["En multipliant par deux la masse molaire atomique de l'atome d'oxygène", "En divisant la masse molaire de l'atome d'oxygène par deux", "En ajoutant la constante d'Avogadro à la masse de l'atome"], "rep": "En multipliant par deux la masse molaire atomique de l'atome d'oxygène"},
            {"id": "t2_q5", "q": "La masse molaire atomique de l'hydrogène est 1,0 g/mol, celle de l'oxygène est 16,0 g/mol. Quelle est la masse molaire moléculaire de l'eau H2O ?", "options": ["18,0 g/mol", "17,0 g/mol", "34,0 g/mol"], "rep": "18,0 g/mol"},
            {"id": "t2_q6", "q": "Que représente la masse molaire moléculaire d'un composé chimique ?", "options": ["La masse d'une mole de molécules de ce composé", "La masse d'une seule et unique molécule isolée", "Le nombre total de molécules présentes dans un gramme de poudre"], "rep": "La masse d'une mole de molécules de ce composé"},
            {"id": "t2_q7", "q": "Quelle formule mathématique permet de calculer la masse molaire moléculaire M à partir de la masse m et des moles n ?", "options": ["M = m / n", "M = n / m", "M = m * n"], "rep": "M = m / n"},
            {"id": "t2_q8", "q": "Quelle est la masse molaire moléculaire du dioxyde de carbone CO2 (C = 12,0 g/mol et O = 16,0 g/mol) ?", "options": ["44,0 g/mol", "28,0 g/mol", "38,0 g/mol"], "rep": "44,0 g/mol"},
            {"id": "t2_q9", "q": "Si la masse molaire de l'atome de carbone est de 12,0 g/mol, quelle est la masse d'une mole de carbone ?", "options": ["12,0 grammes", "1,0 gramme", "6,02 x 10^23 grammes"], "rep": "12,0 grammes"},
            {"id": "t2_q10", "q": "La masse molaire moléculaire dépend uniquement de :", "options": ["La nature et du nombre des atomes qui constituent la molécule", "De la température et de la pression de la pièce du laboratoire", "Du volume de solvant dans lequel la molécule est dissoute"], "rep": "La nature et du nombre des atomes qui constituent la molécule"}
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
        with c1: st.write("1. L'unité de mesure regroupant les entités en paquets géants s'appelle la")
        with c2: trous_q2["t1"] = st.selectbox("", ["Choisir...", "Mole", "Masse", "Volume"], key="t2_10t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c3: st.write("2. Le nombre fixe d'atomes contenus dans une mole est la constante d'")
        with c4: trous_q2["t2"] = st.selectbox("", ["Choisir...", "Avogadro", "Mariotte", "Celsius"], key="t2_10t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c5: st.write("3. La masse d'une mole d'un seul atome individuel est sa masse molaire")
        with c6: trous_q2["t3"] = st.selectbox("", ["Choisir...", "Atomique", "Moleculaire", "Volumique"], key="t2_10t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c7: st.write("4. La masse d'une mole de molécules assemblées est la masse molaire")
        with c8: trous_q2["t4"] = st.selectbox("", ["Choisir...", "Moleculaire", "Atomique", "Volumique"], key="t2_10t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c9: st.write("5. Les valeurs des masses molaires atomiques sont répertoriées dans le tableau")
        with c10: trous_q2["t5"] = st.selectbox("", ["Choisir...", "Periodique", "De conversion", "Des volumes"], key="t2_10t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c11: st.write("6. L'unité de la masse molaire moléculaire ou atomique est le gramme par")
        with c12: trous_q2["t6"] = st.selectbox("", ["Choisir...", "Mole", "Litre", "Kilogramme"], key="t2_10t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c13: st.write("7. Pour calculer la masse molaire d'une molécule, on fait la somme des masses")
        with c14: trous_q2["t7"] = st.selectbox("", ["Choisir...", "Atomiques", "Volumiques", "Molaires"], key="t2_10t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c15: st.write("8. L'écriture symbolique de l'unité de la quantité de matière s'écrit sans 'e' :")
        with c16: trous_q2["t8"] = st.selectbox("", ["Choisir...", "mol", "g", "g/mol"], key="t2_10t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c17: st.write("9. Le symbole de la grandeur de la masse molaire moléculaire est la lettre majuscule")
        with r18: trous_q2["t9"] = st.selectbox("", ["Choisir...", "M", "N", "C"], key="t2_10t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.7, 0.3], vertical_alignment="bottom")
        with c19: st.write("10. Pour une molécule, la valeur de M dépend uniquement des atomes de sa formule")
        with c20: trous_q2["t10"] = st.selectbox("", ["Choisir...", "Brute", "Developpee", "De calcul"], key="t2_10t_t10", disabled=verrouille, label_visibility="collapsed")

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

        """)

        st.divider()
        
        st.subheader("La masse molaire atomique et moléculaire")
        st.markdown("""
        La masse molaire atomique est la masse d'une mole d'atomes d'un même élément chimique.Elle correspond à la masse d'un paquet contenant précisément \(6,022 \times 10^{23}\) atomes identiques. Son symbole est \(M\) et elle s'exprime en grammes par mole (g/mol).
        Où la trouve-t-on ? Elle est indiquée directement dans le tableau périodique des éléments (la table de Mendeleïev). C'est le nombre décimal qui figure généralement en bas ou en haut de la case de chaque élément.
        Chaque atome a sa propre masse molaire car les atomes n'ont pas tous la même taille ni la même constitution (nombre de protons et de neutrons).

        La masse molaire moléculaire : 
        La masse molaire atomique est la brique de base de tous les calculs en chimie. C'est en additionnant ces masses atomiques que l'on obtient la masse molaire moléculaire (le poids d'un paquet de molécules). Par exemple, pour l'eau (\(H_{2}O\)), on prend deux masses atomiques d'hydrogène (\(2 \times 1\)) et une d'oxygène (\(16\)) pour obtenir \(18\text{ g/mol}\).

        La métaphore du panier de fruits !
        Pour comprendre facilement, on peut comparer la molécule à un panier de fruits :
         Si une molécule est un panier contenant 2 pommes et 1 orange, sa masse totale dépend du poids de chaque fruit.
        En chimie, pour trouver la masse d'un paquet (une mole) de ces paniers, on additionne le poids d'un paquet de pommes et d'un paquet d'oranges.

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
                st.session_state.get("t2_10t_t1") == "Mole",
                st.session_state.get("t2_10t_t2") == "Avogadro",
                st.session_state.get("t2_10t_t3") == "Atomique",
                st.session_state.get("t2_10t_t4") == "Moleculaire",
                st.session_state.get("t2_10t_t5") == "Periodique",
                st.session_state.get("t2_10t_t6") == "Mole",
                st.session_state.get("t2_10t_t7") == "Atomiques",
                st.session_state.get("t2_10t_t8") == "mol",
                st.session_state.get("t2_10t_t9") == "M",
                st.session_state.get("t2_10t_t10") == "Brute"
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
            ("1. L'unite de mesure regroupant les entites en paquets geants s'appelle la", st.session_state.get("t2_10t_t1"), "Mole"),
            ("2. Le nombre fixe d'atomes contenus dans une mole est la constante d'", st.session_state.get("t2_10t_t2"), "Avogadro"),
            ("3. La masse d'une mole d'un seul atome individuel est sa masse molaire", st.session_state.get("t2_10t_t3"), "Atomique"),
            ("4. La masse d'une mole de molecules assemblees est la masse molaire", st.session_state.get("t2_10t_t4"), "Moleculaire"),
            ("5. Les valeurs des masses molaires atomiques sont repertoriees dans le tableau", st.session_state.get("t2_10t_t5"), "Periodique"),
            ("6. L'unite de la masse molaire moleculaire ou atomique est le gramme par", st.session_state.get("t2_10t_t6"), "Mole"),
            ("7. Pour calculer la masse molaire d'une molecule, on fait la somme des masses", st.session_state.get("t2_10t_t7"), "Atomiques"),
            ("8. L'ecriture symbolique de l'unite de la quantite de matiere s'ecrit sans 'e' :", st.session_state.get("t2_10t_t8"), "mol"),
            ("9. Le symbole de la grandeur de la masse molaire moleculaire est la lettre majuscule", st.session_state.get("t2_10t_t9"), "M"),
            ("10. Pour une molecule, la valeur de M depend uniquement des atomes de sa formule", st.session_state.get("t2_10t_t10"), "Brute")
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
    st.header("Comment calculer le nombre de moles ?")
    
    col_solide, col_liquide, col_gaz = st.columns(3)
    
    with col_solide:
        st.subheader("Pour un solide")
        st.markdown("""Pour un solide de masse m en gramme et de masse molaire M en gramme par mol, le nombre de moles est défini par la formule fondamentale suivante :""")
        st.latex(r"n = \frac{m}{M}")
        st.markdown("""
        * **n** : Le nombre de moles exprimé en moles (mol).
        * **m** : La masse exprimée en grammes (g).
        * **M** : La masse molaire moléculaire (ou atomique) exprimée en grammes par mole (g/mol).
        """)  
        st.divider()

        st.subheader("Simulateur de calcul : De la masse à la mole")
        m_echantillon = st.number_input("Masse de l'échantillon m (g) :", min_value=0.001, value=10.0, step=0.1, key="t3_m_solide_sim")
        m_molaire_espece = st.number_input("Masse molaire moléculaire M (g/mol) :", min_value=1.0, value=180.0, step=0.1, key="t3_M_solide_sim")
        
        n_solide_res = m_echantillon / m_molaire_espece
        st.metric(label="Quantité de matière calculée (n)", value=f"{n_solide_res:.4f} mol")
        st.divider()
        
    with col_liquide:
        st.subheader("Pour un liquide")
        st.markdown("""Pour un liquide de concentration molaire C en moles par litre et de volume V en litres, le nombre de moles est défini par la formule fondamentale suivante :""")
        st.latex(r"n = C \times V")
        st.markdown("""
        * **n** : Le nombre de moles exprimé en moles (mol).
        * **V** : Le volume exprimé en litres (L).
        * **C** : La concentration molaire exprimée en moles par litre (mol/L).
        """)  
        st.divider()

        st.subheader("Simulateur : De la concentration à la mole")
        V_liquide_in = st.number_input("Volume V (L) :", min_value=0.001, value=2.0, step=0.1, key="t3_V_liquide_sim")
        C_molaire_in = st.number_input("Concentration molaire C (mol/L) :", min_value=0.001, value=0.500, step=0.05, key="t3_C_liquide_sim")
        
        n_liquide_res = V_liquide_in * C_molaire_in
        st.metric(label="Quantité de matière calculée (n)", value=f"{n_liquide_res:.4f} mol")
        st.divider()

    with col_gaz:
        st.subheader("Pour un gaz")
        st.markdown("""Pour un gaz de volume V en litres et de volume molaire Vm en litres par mol, le nombre de moles est défini par la formule fondamentale suivante :""")
        st.latex(r"n = \frac{V}{V_m}")
        st.markdown("""
        * **n** : Le nombre de moles exprimé en moles (mol).
        * **V** : Le volume exprimé en litres (L).
        * **Vm** : Le volume molaire exprimé en litres par mole (L/mol).
        """)        
        st.divider()

        st.subheader("Simulateur de calcul : Du volume à la mole")
        V_gaz_in = st.number_input("Volume du gaz V (L) :", min_value=0.001, value=2.0, step=0.1, key="t3_V_gaz_sim")
        V_molaire_in = st.number_input("Volume molaire Vm (L/mol) :", min_value=1.0, value=24.0, step=0.5, key="t3_Vm_gaz_sim")
        
        n_gaz_res = V_gaz_in / V_molaire_in
        st.metric(label="Quantité de matière calculée (n)", value=f"{n_gaz_res:.4f} mol")
        st.divider()

    verrou_v3 = st.session_state.get("v_verrouille_tab3", False)
    res_q3, res_t3 = afficher_questions_tab3_completes(verrouille=verrou_v3)

    st.write("---")
    st.session_state.id_nom = st.session_state.get("nom_var") or "INCONNU"
    st.session_state.id_prenom = st.session_state.get("prenom_var") or "INCONNU"
    st.session_state.id_classe = st.session_state.get("classe_var") or "INCONNU"
    
    n_eleve = str(st.session_state.id_nom).upper()
    p_eleve = str(st.session_state.id_prenom).upper()
    c_eleve = str(st.session_state.id_classe).upper()

    case_certif_c = st.checkbox("Je certifie avoir complete les questions de l'Atelier 3.", key="check_certif_c_10", disabled=verrou_v3)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_c_10", use_container_width=True, disabled=verrou_v3):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_c:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q3 = 0.0
            if "ordre_quiz_tab3_10q" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_10q:
                    ans = st.session_state.get(f"sel_t3_10q_{q_item['id']}", "Choisir...")
                    if str(ans).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # 2. Correction de la Synthese (10 points)
            score_t3 = sum([
                st.session_state.get("t3_10t_t1") == "Molaire",
                st.session_state.get("t3_10t_t2") == "Volume",
                st.session_state.get("t3_10t_t3") == "Molaire",
                st.session_state.get("t3_10t_t4") == "Litre",
                st.session_state.get("t3_10t_t5") == "Molaire",
                st.session_state.get("t3_10t_t6") == "Mole",
                st.session_state.get("t3_10t_t7") == "Mille",
                st.session_state.get("t3_10t_t8") == "V",
                st.session_state.get("t3_10t_t9") == "M",
                st.session_state.get("t3_10t_t10") == "Moles"
            ])

            st.session_state.score_c_p1 = round(float(score_q3), 1)
            st.session_state.score_c_p2 = round(float(score_t3), 1)
            st.session_state.score_final_c = round(float(score_q3 + score_t3), 1)
            st.session_state.v_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab3", False):
        scr1_c = st.session_state.get("score_c_p1", 0.0)
        scr2_c = st.session_state.get("score_c_p2", 0.0)
        tot_s_c = st.session_state.get("score_final_c", 0.0)
        timestamp_c = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER LES TROIS MÉTHODES DE CALCULS SCELLÉ | Note de session : {tot_s_c:.1f} / 20")

        html_export_c = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Calcul Moles - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 3 : Methodes de determination des quantites de matiere (Solide, Liquide, Gaz)</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_c}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_c:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                - Note obtenue au Quiz : <strong>{scr1_c:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2_c:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 3 : <strong>{tot_s_c:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3_10q" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_10q, 1):
                saisie = st.session_state.get(f"sel_t3_10q_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_c += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_c += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_c = [
            ("1. Pour un compose solide, la quantite de matiere s'obtient en divisant la masse par la masse", st.session_state.get("t3_10t_t1"), "Molaire"),
            ("2. Pour une solution, le nombre de moles est egal au produit de la concentration par le", st.session_state.get("t3_10t_t2"), "Volume"),
            ("3. Pour calculer le nombre de moles d'un gaz, on divise son volume par le volume", st.session_state.get("t3_10t_t3"), "Molaire"),
            ("4. L'unite legale du volume V a introduire dans la relation n = C * V est le", st.session_state.get("t3_10t_t4"), "Litre"),
            ("5. Le volume occupe par une mole de n'importe quel gaz s'appelle le volume", st.session_state.get("t3_10t_t5"), "Molaire"),
            ("6. L'unite du volume molaire des gaz s'exprime en litres par", st.session_state.get("t3_10t_t6"), "Mole"),
            ("7. Si le volume d'une solution est fourni en mL, on doit imperativement le diviser par", st.session_state.get("t3_10t_t7"), "Mille"),
            ("8. La formule liant les grandeurs d'une solution liquide est n = C multiplie par", st.session_state.get("t3_10t_t8"), "V"),
            ("9. La formule pour determiner la masse d'un solide a partir de ses moles est m = n fois", st.session_state.get("t3_10t_t9"), "M"),
            ("10. Quelle que soit la methode (solide, liquide ou gaz), le resultat n s'exprime en", st.session_state.get("t3_10t_t10"), "Moles")
        ]

        for num, (phrase, saisie, attendu) in enumerate(phrases_trous_c, 1):
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_c += f"<tr><td>{num}</td><td>{phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_c += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DE L'ATELIER 3 EN HTML",
            data=html_export_c,
            file_name=f"Rapport_Calcul_Moles_{n_eleve}.html",
            mime="text/html",
            use_container_width=True
        )




with tab4:
    st.header("La concentration molaire C")
    
    st.markdown("""
    La concentration massique (ou concentration en masse) représente la masse de soluté dissous par unité de volume de solution totale.
    Elle se calcule à l'aide de la formule mathématique fondamentale :
    """)
    st.latex(r"C_m = \frac{m}{V}")
    st.markdown("""
    * **** : Concentration massique exprimée en grammes par litre (g/L).
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
    st.markdown("""
    La dissolution est le protocole de laboratoire permettant de fabriquer un volume précis d'une solution aqueuse 
    à partir d'un soluté sous forme solide (poudre ou cristaux). 
    Pour connaître la masse exacte de solide à prélever, on applique la relation dérivée :
    """)
    st.latex(r"m = C \times V \times M")

    st.subheader("Simulateur de préparation par dissolution")
    st.markdown("Configurez les paramètres de la solution molaire que vous devez préparer :")

    col_ds1, col_ds2 = st.columns(2)
    with col_ds1:
        c_cible = st.number_input("Concentration molaire C souhaitée (mol/L) :", min_value=0.001, value=0.100, step=0.01, format="%.3f", key="ds_c_input_molaire")
        v_fiole = st.selectbox("Volume de la fiole jaugée disponible V (mL) :", [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0], index=3, key="ds_v_input_molaire")
    with col_ds2:
        m_sol_molaire = st.number_input("Masse molaire du soluté solide M (g/mol) :", min_value=1.0, value=180.0, step=0.1, key="ds_m_input_molaire")
        v_fiole_l = v_fiole / 1000.0
        m_attendue_ds = c_cible * v_fiole_l * m_sol_molaire
        st.metric(label="Masse de soluté solide à peser (m)", value=f"{m_attendue_ds:.3f} g")
        st.info(f"Calcul appliqué : {c_cible:.3f} mol/L × {v_fiole_l:.3f} L × {m_sol_molaire:.1f} g/mol = {m_attendue_ds:.3f} g")

    st.write("---")
    st.subheader("Protocole expérimental officiel étape par étape")

    # Étape 1 & 2
    st.markdown("### Étape 1 et 2 : Pesée du soluté solide")
    col_t1, col_i1 = st.columns([0.6, 0.4])
    with col_t1:
        st.markdown(f"Allumer la balance, poser la coupelle et réaliser la TARE. Prélever le solide à la spatule pour atteindre précisément la masse calculée : **{m_attendue_ds:.3f} g**.")
    with col_i1:
        st.image("etape1.jpg", caption="Étape 1 : Pesée précise du solide", width=250)

    st.divider()

    # Étape 3 & 4
    st.markdown("### Étape 3 et 4 : Transfert et rinçage quantitatif")
    col_t2, col_i2 = st.columns([0.6, 0.4])
    with col_t2:
        st.markdown(f"Placer un entonnoir sur le col d'une fiole jaugée de **{v_fiole:.0f} mL** et y transférer le solide. Rincer la coupelle et l'entonnoir à la pissette d'eau distillée en récupérant toutes les eaux de rinçage dans la fiole.")
    with col_i2:
        st.image("etape2.jpg", caption="Étape 2 : Introduction et rinçage", width=250)

    st.divider()

    # Étape 5 & 6
    st.markdown("### Étape 5 et 6 : Remplissage, ajustement et homogénéisation")
    col_t3, col_i3 = st.columns([0.6, 0.4])
    with col_t3:
        st.markdown("Remplir la fiole aux deux tiers, agiter de manière circulaire pour dissoudre. Compléter ensuite à la pipette Pasteur goutte à goutte jusqu'à ce que le bas du ménisque soit aligné avec le trait de jauge. Boucher et retourner la fiole plusieurs fois.")
    with col_i3:
        st.image("etape5.jpg", caption="Étape 3 : Ajustement final du ménisque", width=250)

    st.divider()

    # Gestion de l'évaluation du Tab 4
    verrou_v4 = st.session_state.get("v_verrouille_tab4", False)
    res_q4, res_t4 = afficher_questions_tab4_completes(
        m_solide=m_attendue_ds,
        v_fiole=v_fiole,
        c_cible=c_cible,
        M_solide=m_sol_molaire,
        verrouille=verrou_v4
    )

    st.write("---")
    st.session_state.id_nom = st.session_state.get("nom_var") or "INCONNU"
    st.session_state.id_prenom = st.session_state.get("prenom_var") or "INCONNU"
    st.session_state.id_classe = st.session_state.get("classe_var") or "INCONNU"
    
    n_eleve = str(st.session_state.id_nom).upper()
    p_eleve = str(st.session_state.id_prenom).upper()
    c_eleve = str(st.session_state.id_classe).upper()

    case_certif_ds = st.checkbox("Je certifie avoir complete les questions de l'Atelier 4.", key="check_certif_ds_10_molaire", disabled=verrou_v4)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_ds_10_molaire", use_container_width=True, disabled=verrou_v4):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_ds:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q4 = 0.0
            if "ordre_quiz_tab4_10q" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_10q:
                    ans = st.session_state.get(f"sel_t4_10q_{q_item['id']}", "Choisir...")
                    if str(ans).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            # 2. Correction de la Synthese (10 points)
            score_t4 = sum([
                st.session_state.get("t4_10t_t1") == "Dissolution",
                st.session_state.get("t4_10t_t2") == "Entonnoir",
                st.session_state.get("t4_10t_t3") == "Spatule",
                st.session_state.get("t4_10t_t4") == "Jaugee",
                st.session_state.get("t4_10t_t5") == "Agite",
                st.session_state.get("t4_10t_t6") == "Distillee",
                st.session_state.get("t4_10t_t7") == "Jauge",
                st.session_state.get("t4_10t_t8") == "Goutte",
                st.session_state.get("t4_10t_t9") == "Homogene",
                st.session_state.get("t4_10t_t10") == "Dilution"
            ])

            st.session_state.score_ds_p1 = round(float(score_q4), 1)
            st.session_state.score_ds_p2 = round(float(score_t4), 1)
            st.session_state.score_final_ds = round(float(score_q4 + score_t4), 1)
            st.session_state.v_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("v_verrouille_tab4", False):
        scr1_ds = st.session_state.get("score_ds_p1", 0.0)
        scr2_ds = st.session_state.get("score_ds_p2", 0.0)
        tot_s_ds = st.session_state.get("score_final_ds", 0.0)
        timestamp_ds = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER DISSOLUTION MOLAIRE SCELLÉ | Note de session : {tot_s_ds:.1f} / 20")

        # Code d'exportation HTML autonome pour l'Atelier 4 (Style Turquoise/Teal)
        html_export_ds = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Dissolution Molaire - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 4 : Préparation d'une solution de concentration molaire précise par dissolution</p>
                <p>Données de session : C cible = {c_cible:.3f} mol/L | Fiole = {v_fiole:.0f} mL | M = {m_sol_molaire:.1f} g/mol &rarr; Masse pesée = {m_attendue_ds:.3f} g</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ds}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_ds:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f766e;">
                - Note obtenue au Quiz : <strong>{scr1_ds:.1f} / 10</strong><br>
                - Note obtenue a la Synthese de cours : <strong>{scr2_ds:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 4 : <strong>{tot_s_ds:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4_10q" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_10q, 1):
                saisie = st.session_state.get(f"sel_t4_10q_{q_item['id']}", "Choisir...")
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
            ("1. La preparation d'une solution a partir d'un solute solide s'appelle la", st.session_state.get("t4_10t_t1"), "Dissolution"),
            ("2. Pour introduire proprement la poudre sans perte dans le col etroit, on utilise un", st.session_state.get("t4_10t_t2"), "Entonnoir"),
            ("3. Le prelevement de la poudre dans le flacon d'origine s'effectue avec une", st.session_state.get("t4_10t_t3"), "Spatule"),
            ("4. La verrerie jaugee servant de contenant pour cette preparation de precision est la fiole", st.session_state.get("t4_10t_t4"), "Jaugee"),
            ("5. Avant d'ajuster au trait superieur, on remplit aux deux tiers et on", st.session_state.get("t4_10t_t5"), "Agite"),
            ("6. Le liquide ajoute pour dissoudre le solide et completer la fiole est l'eau", st.session_state.get("t4_10t_t6"), "Distillee"),
            ("7. La marque gravee sur le col de la fiole indiquant le volume exact est le trait de", st.session_state.get("t4_10t_t7"), "Jauge"),
            ("8. Pour ajuster le menisque sans depasser la ligne, on termine le remplissage au goutte a", st.session_state.get("t4_10t_t8"), "Goutte"),
            ("9. Une fois fermee par son bouchon, on retourne la fiole plusieurs fois pour la rendre", st.session_state.get("t4_10t_t9"), "Homogene"),
            ("10. Si le niveau depasse la ligne de repere, la concentration de la solution est faussee par sur-", st.session_state.get("t4_10t_t10"), "Dilution")
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
            label="TELECHARGER LE RAPPORT DE L'ATELIER 4 EN HTML",
            data=html_export_ds,
            file_name=f"Rapport_Dissolution_Molaire_{n_eleve}.html",
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






                        
