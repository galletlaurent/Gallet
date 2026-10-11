# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="TP la concentration massique",
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
st.title("TP la concentration massique ")
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
    "La masse et le volume", 
    "La concentration massique Cm", 
    "Préparation d'une solution de concentration précise",
    "Dilution et concentration massique",
    "Exemple"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]


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


def afficher_questions_concentration_massique(m_sim, v_sim, cm_sim, verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz_cm" not in st.session_state:
        base_quiz_cm = [
            {
                "id": "cm_1", 
                "q": "Quelle est la formule correcte reliant la concentration massique (Cm), la masse de soluté (m) et le volume de la solution (V) ?", 
                "options": ["Cm = m / V", "Cm = m * V", "Cm = V / m"], 
                "rep": "Cm = m / V"
            },
            {
                "id": "cm_2", 
                "q": f"Si vous dissolvez une masse exacte de {m_sim:.1f} g de soluté dans un volume de {v_sim / 1000.0:.3f} L, quelle est la concentration massique exacte ?", 
                "options": [f"{cm_sim:.2f} g/L", f"{cm_sim * 10.0:.2f} g/L", f"{cm_sim / 10.0:.2f} g/L"], 
                "rep": f"{cm_sim:.2f} g/L"
            },
            {
                "id": "cm_3", 
                "q": "Quelle est l'unité usuelle de la concentration massique couramment manipulée par le chimiste au laboratoire ?", 
                "options": ["Grammes par litre (g/L)", "Moles par litre (mol/L)", "Grammes (g)"], 
                "rep": "Grammes par litre (g/L)"
            },
            {
                "id": "cm_4", 
                "q": "Comment évolue la concentration massique d'une solution si on ajoute du solvant (eau distillée) sans rajouter de soluté ?", 
                "options": ["Elle diminue (c'est une dilution)", "Elle augmente (c'est une concentration)", "Elle reste rigoureusement identique"], 
                "rep": "Elle diminue (c'est une dilution)"
            },
            {
                "id": "cm_5", 
                "q": "Quelle est la formule mathématique dérivée permettant de trouver la masse (m) de soluté à peser ?", 
                "options": ["m = Cm * V", "m = Cm / V", "m = V / Cm"], 
                "rep": "m = Cm * V"
            },
            {
                "id": "cm_6", 
                "q": "Dans la formule de la concentration massique, que représente précisément le Volume V ?", 
                "options": ["Le volume total de la solution obtenue", "Le volume de solvant pur versé au début", "Le volume occupé par le soluté solide seul"], 
                "rep": "Le volume total de la solution obtenue"
            },
            {
                "id": "cm_7", 
                "q": "Si une solution a une concentration massique de 15 g/L, quelle masse de soluté contient un volume de 2 Litres ?", 
                "options": ["30 g", "7.5 g", "15 g"], 
                "rep": "30 g"
            },
            {
                "id": "cm_8", 
                "q": "Quelle est la formule mathématique dérivée permettant de déterminer le volume total V de la solution ?", 
                "options": ["V = m / Cm", "V = Cm / m", "V = Cm * m"], 
                "rep": "V = m / Cm"
            },
            {
                "id": "cm_9", 
                "q": "Quelle est la différence fondamentale entre la concentration massique et la masse volumique d'un corps pur ?", 
                "options": ["La concentration concerne un soluté dissous dans un mélange, la masse volumique concerne le corps pur seul", "Ce sont exactement deux synonymes mathématiques", "L'une s'exprime en g/L et l'autre obligatoirement en kg/m3"], 
                "rep": "La concentration concerne un soluté dissous dans un mélange, la masse volumique concerne le corps pur seul"
            },
            {
                "id": "cm_10", 
                "q": "Si on dissout 500 mg de gros sel dans 0.5 Litre d'eau, quelle est la concentration massique en g/L ?", 
                "options": ["1.0 g/L", "1000 g/L", "0.25 g/L"], 
                "rep": "1.0 g/L"
            }
        ]
        copie_base = list(base_quiz_cm)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_cm = copie_base

    col_q2, col_t2 = st.columns(2)

    with col_q2:
        st.markdown("##### Quiz sur la concentration massique (10 questions - 10 pts)")
        dict_rep_q2 = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_cm, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"cm_quiz_q_{q_data['id']}"
            cle_opts = f"opts_cm_{q_data['id']}"
            if cle_opts not in st.session_state:
                opts = list(q_data["options"])
                random.shuffle(opts)
                st.session_state[cle_opts] = ["Choisir..."] + opts
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_opts].index(val_p) if val_p in st.session_state[cle_opts] else 0
            dict_rep_q2[q_data["id"]] = st.selectbox("", st.session_state[cle_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_t2:
        st.markdown("##### Synthèse de cours à trous (10 trous - 10 pts)")
        dict_trous_2 = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La concentration massique représente la masse de soluté dissous par unité de")
        with c2: dict_trous_2["t1"] = st.selectbox("", ["Choisir...", "Volume", "Masse", "Pression"], key="cm_t_t1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'espèce chimique solide ou liquide que l'on dissout dans le liquide s'appelle le")
        with c4: dict_trous_2["t2"] = st.selectbox("", ["Choisir...", "Solute", "Solvant", "Melange"], key="cm_t_t2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Le liquide majoritaire dans lequel s'effectue la dissolution s'appelle le")
        with c6: dict_trous_2["t3"] = st.selectbox("", ["Choisir...", "Solvant", "Solute", "Distillat"], key="cm_t_t3", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Lorsque le solvant utilisé pour fabriquer la solution est l'eau, on obtient une solution")
        with c8: dict_trous_2["t4"] = st.selectbox("", ["Choisir...", "Aqueuse", "Organique", "Saturee"], key="cm_t_t4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. L'unité réglementaire de la concentration massique dans le système usuel est le gramme par")
        with c10: dict_trous_2["t5"] = st.selectbox("", ["Choisir...", "Litre", "Millilitre", "Kilogramme"], key="cm_t_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Pour calculer la concentration massique, la masse saisie doit obligatoirement être exprimée en")
        with c12: dict_trous_2["t6"] = st.selectbox("", ["Choisir...", "Gramme", "Kilogramme", "Milligramme"], key="cm_t_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Si le volume initial est donné en mL, il faut le diviser par mille pour obtenir des")
        with c14: dict_trous_2["t7"] = st.selectbox("", ["Choisir...", "Litres", "Grammes", "Metres"], key="cm_t_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Lorsque l'on ne peut plus dissoudre de soluté car la limite est atteinte, la solution est")
        with c16: dict_trous_2["t8"] = st.selectbox("", ["Choisir...", "Saturee", "Diluee", "Homogene"], key="cm_t_t8", disabled=verrouille, label_visibility="collapsed")

        c17, r18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La formule retournée permettant de calculer la masse de soluté est m = Cm multiplié par")
        with r18: dict_trous_2["t9"] = st.selectbox("", ["Choisir...", "Volume", "Masse", "Solvant"], key="cm_t_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. L'action consistant à rajouter du solvant pur pour diminuer la concentration s'appelle la")
        with c20: dict_trous_2["t10"] = st.selectbox("", ["Choisir...", "Dilution", "Dissolution", "Saturation"], key="cm_t_t10", disabled=verrouille, label_visibility="collapsed")

    return dict_rep_q2, dict_trous_2


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


def preparer_images_dissolution():
    # Liste des fichiers attendus pour l'Atelier 3
    fichiers_etapes = ["etape1.jpg", "etape2.jpg", "etape3.jpg", "etape4.jpg", "etape5.jpg"]
    
    # On vérifie si les images sont déjà présentes pour éviter de refaire le calcul à chaque rafraîchissement
    tous_presents = all(os.path.exists(f) for f in fichiers_etapes)
    
    if not tous_presents:
        try:
            # 1. Téléchargement de la fiche technique d'origine
            url_origine = "https://githubusercontent.com"
            image_path = "fiche_origine.jpg"
            urllib.request.urlretrieve(url_origine, image_path)
            
            # 2. Lecture de l'image avec OpenCV
            img = cv2.imread(image_path)
            if img is not None:
                h, w, _ = img.shape
                
                # 3. Définition des zones de découpe proportionnelles (coordonnées des 5 étapes)
                # Étape 1 : Balance et prélèvement (Bas gauche)
                etape1 = img[int(h*0.48):int(h*0.95), 0:int(w*0.25)]
                # Étape 2 : Introduction fiole (Haut gauche/milieu)
                etape2 = img[0:int(h*0.95), int(w*0.12):int(w*0.38)]
                # Étape 3 : Rinçage pissette (Haut milieu)
                etape3 = img[0:int(h*0.65), int(w*0.38):int(w*0.65)]
                # Étape 4 : Agitation fiole (Bas milieu)
                etape4 = img[int(h*0.55):h, int(w*0.45):int(w*0.65)]
                # Étape 5 : Ajustement trait de jauge (Toute la partie droite)
                etape5 = img[0:h, int(w*0.65):w]
                
                # 4. Sauvegarde des fichiers au format .jpg demandé
                cv2.imwrite("etape1.jpg", etape1)
                cv2.imwrite("etape2.jpg", etape2)
                cv2.imwrite("etape3.jpg", etape3)
                cv2.imwrite("etape4.jpg", etape4)
                cv2.imwrite("etape5.jpg", etape5)
        except Exception as e:
            # En cas de problème réseau, création de fichiers temporaires pour éviter le crash de l'application
            for f in fichiers_etapes:
                if not os.path.exists(f):
                    with open(f, "w") as empty_f:
                        empty_f.write("")

# Appel immédiat de la préparation des images au lancement
preparer_images_dissolution()

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
    verrou_v1 = st.session_state.get("v_verrouille_tab1", False)

    res_q1, res_t1 = afficher_questions_masse_volume(
        masse_actuelle=masse_actuelle,
        volume_actuel=volume_actuel,
        verrouille=verrou_v1
    )

    st.write("---")
    p_eleve = st.session_state.get("id_prenom", "INCONNU").upper()
    n_eleve = st.session_state.get("id_nom", "INCONNU").upper()
    c_eleve = st.session_state.get("id_classe", "INCONNU").upper()

    case_certif_mv = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 1.", 
        key="check_certif_mv_official", 
        disabled=verrou_v1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_mv_official", use_container_width=True, disabled=verrou_v1):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
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
            
    if st.session_state.get("v_verrouille_tab1", False):
        scr1 = st.session_state.get("score_mv_p1", 0.0)
        scr2 = st.session_state.get("score_mv_p2", 0.0)
        tot_s = st.session_state.get("score_final_mv", 0.0)

        from datetime import datetime
        timestamp_mv = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MASSE ET VOLUME SCELLÉ | Note de session : {tot_s:.1f} / 20")

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
    st.header("La concentration massique Cm")
    
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

    # Affichage du questionnaire sur la concentration massique
    res_q2, res_t2 = afficher_questions_concentration_massique(
        m_sim=m_exercice,
        v_sim=v_exercice,
        cm_sim=cm_exercice,
        verrouille=verrou_v2
    )

    st.write("---")
    p_eleve = st.session_state.get("id_prenom", "INCONNU").upper()
    n_eleve = st.session_state.get("id_nom", "INCONNU").upper()
    c_eleve = st.session_state.get("id_classe", "INCONNU").upper()

    case_certif_cm = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 2.", 
        key="check_certif_cm_official", 
        disabled=verrou_v2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_cm_official", use_container_width=True, disabled=verrou_v2):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
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
                .header-box {{ background-color: #0d9488; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                


with tab3:
    st.header("Préparation d'une solution de concentration précise")
    
    # 1. DÉCLARATION IMPÉRATIVE DES VARIABLES AU DÉBUT DE L'ONGLET
    cm_cible_ds = st.number_input("Concentration massique Cm souhaitée (g/L) :", min_value=0.1, value=12.0, step=0.5, key="ds_cm_input")
    v_fiole_ml_ds = st.selectbox("Volume de la fiole jaugée disponible V (mL) :", [50.0, 100.0, 200.0, 250.0, 500.0, 1000.0], index=3, key="ds_v_input")
    
    # Le calcul qui génère la variable manquante
    v_fiole_l_ds = v_fiole_ml_ds / 1000.0
    masse_calculee_ds = cm_cible_ds * v_fiole_l_ds
    
    st.metric(label="Masse de soluté à peser (m)", value=f"{masse_calculee_ds:.3f} g")
    
    st.write("---")
    st.subheader("Protocole expérimental officiel : Dissolution étape par étape")
    
    # Étape 1 : Pesée du soluté
    st.markdown("### Étape 1 : Pesée du soluté solide")
    col_t1, col_i1 = st.columns([0.6, 0.4])
    with col_t1:
        st.markdown(f"Allumer la balance, poser la coupelle et réaliser la TARE. Prélever le solide à la spatule pour atteindre précisément la masse calculée : **{masse_calculee_ds:.3f} g**.")
    with col_i1:
        # Lien web direct pour l'étape 1
        st.image("https://githubusercontent.com", caption="Pesée précise du soluté solide à la spatule", width=250)

    st.divider()

    # Étape 2 : Introduction dans la fiole
    st.markdown("### Étape 2 : Introduction dans la fiole jaugée")
    col_t2, col_i2 = st.columns([0.6, 0.4])
    with col_t2:
        st.markdown(f"Placer un entonnoir sur le col d'une fiole jaugée de **{v_fiole_ml_ds:.0f} mL** et y transférer délicatement l'intégralité du solide pesé.")
    with col_i2:
        # LIGNE 1386 CORRIGÉE : Utilisation de l'URL directe pour contourner le fichier corrompu
        st.image("https://githubusercontent.com", caption="Introduction du solide par l'entonnoir", width=250)

    st.divider()

    # Étape 3 : Rinçage quantitatif
    st.markdown("### Étape 3 : Rinçage quantitatif du matériel")
    col_t3, col_i3 = st.columns([0.6, 0.4])
    with col_t3:
        st.markdown("À l'aide d'une pissette d'eau distillée, rincer soigneusement la coupelle et l'entonnoir au-dessus de la fiole pour récupérer toutes les particules solides.")
    with col_i3:
        # Lien web direct pour l'étape 3
        st.image("https://githubusercontent.com", caption="Rinçage à l'eau distillée", width=250)

    st.divider()

    # Étape 4 : Dissolution initiale
    st.markdown("### Étape 4 : Dissolution initiale par agitation")
    col_t4, col_i4 = st.columns([0.6, 0.4])
    with col_t4:
        st.markdown("Remplir la fiole aux deux tiers avec de l'eau distillée, mettre le bouchon et agiter par mouvements réguliers jusqu'à disparition totale des cristaux.")
    with col_i4:
        # Lien web direct pour l'étape 4
        st.image("https://githubusercontent.com", caption="Agitation pour dissoudre le solide", width=250)

    st.divider()

    # Étape 5 : Ajustement final au trait de jauge
    st.markdown("### Étape 5 : Ajustement final au trait de jauge")
    col_t5, col_i5 = st.columns([0.6, 0.4])
    with col_t5:
        st.markdown("Compléter à la pissette puis à la pipette Pasteur goutte à goutte. Le bas du ménisque doit s'aligner avec le trait de jauge. Boucher et retourner la fiole pour homogénéiser.")
    with col_i5:
        # Lien web direct pour l'étape 5
        st.image("https://githubusercontent.com", caption="Lecture alignée du ménisque avec le trait de jauge", width=250)

    st.divider()

    # Variables de verrouillage et de contrôle pour le questionnaire de l'Atelier 3
    verrou_v3 = st.session_state.get("v_verrouille_tab3", False)

    # Appel de la fonction de questionnaire pour la dissolution
    res_q3, res_t3 = afficher_questions_dissolution(
        m_solide=masse_calculee_ds,
        v_fiole=v_fiole_ml_ds,
        cm_cible=cm_cible_ds,
        verrouille=verrou_v3
    )

    st.write("---")
    p_eleve = st.session_state.get("id_prenom", "INCONNU").upper()
    n_eleve = st.session_state.get("id_nom", "INCONNU").upper()
    c_eleve = st.session_state.get("id_classe", "INCONNU").upper()

    case_certif_ds = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 3.", 
        key="check_certif_ds_official", 
        disabled=verrou_v3
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_ds_official", use_container_width=True, disabled=verrou_v3):
        if n_eleve == "INCONNU" or p_eleve == "INCONNU":
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




with tab4:
    st.header("Dilution : Préparation à partir d'une solution mère")
    st.markdown("""
    Lors d'une dilution, la masse de soluté se conserve (\\(m_{\\text{{mère}}}} = m_{\\text{{fille}}}\\)). On applique la formule :
    \\[C_{\\text{{mère}}} \\times V_{\\text{{mère}}} = C_{\\text{{fille}}} \\times V_{\\text{{fille}}}\\]
    Le **facteur de dilution** F est donné par : \\[F = \\frac{{C_{\\text{{mère}}}}}{{C_{\\text{{fille}}}}} = \\frac{{V_{\\text{{fille}}}}}{{V_{\\text{{mère}}}}}\\]
    """)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        c_mere = st.number_input("Concentration de la solution mère C_mère (g/L) :", min_value=0.1, value=20.0, key="dil_cmere")
    with c2:
        c_fille = st.number_input("Concentration voulue pour la solution fille C_fille (g/L) :", min_value=0.01, value=2.0, key="dil_cfille")
    with c3:
        v_fille_ml = st.number_input("Volume de solution fille souhaité V_fille (mL) :", min_value=1.0, value=100.0, key="dil_vfille")
        
    if c_fille > c_mere:
        st.error("La concentration de la solution fille ne peut pas être supérieure à celle de la solution mère !")
    else:
        facteur_f = c_mere / c_fille
        v_mere_ml = v_fille_ml / facteur_f
        
        st.subheader("Résultats théoriques et matériels :")
        st.metric(label="Facteur de dilution (F)", value=f"{facteur_f:.1f} x")
        st.info(f"Volume de solution mère à prélever (V_mère) : {v_mere_ml:.2f} mL")
        
        st.markdown(f"""
        **Verrerie recommandée :**
        *   Prélever {v_mere_ml:.2f} mL de solution mère avec une pipette jaugée ou graduée adaptée.
        *   Introduire le prélèvement dans une fiole jaugée de {v_fille_ml:.0f} mL.
        *   Compléter avec de l'eau distillée jusqu'au trait de jauge, puis mélanger.
        """)










        
    # --- 4. EVALUATION ET EXPORTATION HTML COMPLÈTE ---
    st.markdown("---")
    if st.button("Valider et corriger ma copie d'examen", type="primary", key="btn_correction_tab4"):
        if not ident_verrouille:
            st.error("Action refusee : Veuillez d'abord completer vos informations d'identification dans le premier onglet.")
        else:
            score = 0
            lignes_html = ""
            
            for item in saisies_eleve:
                saisie = item["saisie"].strip().lower().replace("é", "e").replace("à", "a").replace(",", ".")
                attendu = item["attendu"].strip().lower().replace(",", ".")
                
                is_juste = False
                if attendu in ["oui", "non", "chasles", "pythagore", "vecteurs", "carre", "rectangle", "trapeze"]:
                    is_juste = (saisie == attendu)
                else:
                    try:
                        is_juste = (abs(float(saisie) - float(attendu)) <= 1.1)
                    except ValueError:
                        is_juste = False
                        
                if is_juste:
                    score += 1
                    verdict = "CORRECT"
                    lbl_style = "status-pass"
                else:
                    verdict = "INCORRECT"
                    lbl_style = "status-fail"
                    
                lignes_html += f"""<tr>
                    <td>{item['index']}</td>
                    <td>Question technique d'examen n°{item['index']}</td>
                    <td>{item['saisie']}</td>
                    <td>{item['attendu']}</td>
                    <td><span class="{lbl_style}">{verdict}</span></td>
                </tr>"""
                
            note_finale = float(score)
            
            if note_finale >= 10.0:
                st.success(f"Examen valide. Note obtenue : {note_finale:.1f} / 20.0")
            else:
                st.error(f"Examen non valide. Note obtenue : {note_finale:.1f} / 20.0")
                
            date_jour = datetime.now().strftime("%d/%m/%Y à %H:%M")
            html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Rapport d'Evaluation Complete - Atelier 4</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; font-weight: bold; font-size: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; margin-bottom: 30px; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px; font-size: 13px; text-align: left; }}
        td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ background-color: #dcfce7; color: #16a34a; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
        .status-fail {{ background-color: #fee2e2; color: #ef4444; padding: 4px 8px; border-radius: 4px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">{note_finale:.1f} / 20</div>
        <h2 style="margin: 0; padding-bottom: 8px;">Professeur Laurent GALLET</h2>
        <div class="meta-info" style="font-size: 13px; line-height: 1.5;">
            <strong>Atelier 4 :</strong> Evaluation de Synthese Vectorielle Multicriteres<br>
            <strong>Eleve :</strong> {prenom_eleve} {nom_eleve} | <strong>Classe :</strong> {classe_eleve}<br>
            <strong>Domaine Metier :</strong> {choix_metier}<br>
            <span style="font-size:11px; opacity:0.8;">Fige et scelle le : {date_jour}</span>
        </div>
    </div>
    
    <div class="section-title">DETAIL DES COMPTES RENDUS LOGISTIQUES ET GEOMETRIQUES</div>
    <table>
        <thead>
            <tr>
                <th style="width: 8%; text-align: center;">N°</th>
                <th style="width: 42%;">Indicateur de session verifie</th>
                <th style="width: 19%;">Saisie de l'eleve</th>
                <th style="width: 19%;">Correction Academique</th>
                <th style="width: 12%; text-align: center;">Verdict</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html}
        </tbody>
    </table>
</body>
</html>"""

            chemin_sauvegarde = os.path.join(os.path.expanduser("~"), "Documents", f"Vecteurs_Atelier4_{nom_eleve}_Streamlit.html")
            try:
                with open(chemin_sauvegarde, "w", encoding="utf-8") as f:
                    f.write(html_content)
                st.success(f"Copie scellee sauvegardee localement : `{chemin_sauvegarde}`")
            except Exception as e:
                st.error(f"Erreur d'ecriture : {str(e)}")

            st.download_button(
                label="Telecharger mon rapport d'evaluation HTML",
                data=html_content,
                file_name=f"Vecteurs_Atelier4_{nom_eleve}_Copie.html",
                mime="text/html",
                key="btn_download_tab4"
            )



with tab5:
    st.header("Exemple d'application concret")
    st.markdown("""
    ### Énoncé type :
    Un technicien de laboratoire souhaite préparer **200 mL** d'une solution aqueuse de sulfate de cuivre à une concentration de **5,0 g/L**.
    
    ### Résolution pas à pas :
    1. **Identification des données :**
       * Concentration visée : Cm = 5,0 g/L
       * Volume de la solution : V = 200 mL = 0,200 L
    
    2. **Calcul de la masse nécessaire :**
       \\[m = C_m \\times V\\]
       \\[m = 5,0 \\text{{ g/L}} \\times 0,200 \\text{{ L}} = 1,0 \\text{{ g}}\\]
       
    3. **Conclusion :**
       Le technicien devra peser précisément **1,0 gramme** de cristaux de sulfate de cuivre pour fabriquer sa solution.
    """)
    st.info("Vous pouvez tester ces valeurs exactes dans l'onglet 'Préparation d'une solution...' pour vérifier la cohérence du simulateur.")


    st.write("---")
    st.subheader("Espace d'expérimentation autonome")
    
    # Second appel indépendant exploitant les mêmes fichiers .jpg
    masse_libre, etat_libre = generer_simulateur_pesee(cle_suffixe="exemple")






