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
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du javel")
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

BASE_DIR = os.path.abspath(".")

def charger_image(nom_fichier):
    nom_fichier = os.path.basename(nom_fichier)
    
    # Python scanne automatiquement tous les dossiers présents à côté du script
    for element in os.listdir(BASE_DIR):
        chemin_dossier = os.path.join(BASE_DIR, element)
        if os.path.isdir(chemin_dossier) and element.startswith("image"):
            chemin_image = os.path.join(chemin_dossier, nom_fichier)
            if os.path.exists(chemin_image):
                try:
                    return Image.open(chemin_image)
                except Exception:
                    pass
                    
    # Sécurité si l'application est déjà masquée dans fichiers_systemes
    chemin_secours = os.path.join(BASE_DIR, "image", nom_fichier)
    if os.path.exists(chemin_secours):
        try: return Image.open(chemin_secours)
        except Exception: pass
    return None

# --- TOUS VOS CORRECTIFS (RERUN, COLUMNS, CONTAINER, IMAGE) ---
if hasattr(st, "rerun"): _original_rerun = st.rerun
elif hasattr(st, "experimental_rerun"): _original_rerun = st.experimental_rerun
else: _original_rerun = None

def safe_rerun():
    if _original_rerun is not None:
        try: _original_rerun()
        except Exception:
            from streamlit.runtime.scriptrunner import RerunData, RerunException
            raise RerunException(RerunData())
st.rerun = safe_rerun

_original_image = st.image
def safe_image(image, *args, **kwargs):
    if "use_container_width" in kwargs:
        kwargs["use_column_width"] = kwargs.pop("use_container_width")
    if isinstance(image, str) and not image.startswith(("http://", "https://", "data:image")):
        nom_fichier = os.path.basename(image)
        img_pil = charger_image(nom_fichier)
        if img_pil is not None: 
            image = img_pil
    return _original_image(image, *args, **kwargs)
st.image = safe_image

# 2. Interception pour st.columns (vertical_alignment)
_original_columns = st.columns
def safe_columns(*args, **kwargs):
    if "vertical_alignment" in kwargs:
        kwargs.pop("vertical_alignment")
    return _original_columns(*args, **kwargs)
st.columns = safe_columns

# 3. Interception pour st.container (border)
_original_container = st.container
def safe_container(*args, **kwargs):
    if "border" in kwargs:
        kwargs.pop("border")
    return _original_container(*args, **kwargs)
st.container = safe_container

# 4. Interception pour le changement de nom st.toggle -> st.checkbox
# Utile si vous utilisez des boutons bascules récents non supportés par Python 3.7
if not hasattr(st, "toggle"):
    def safe_toggle(label, value=False, key=None, **kwargs):
        return st.checkbox(label, value=value, key=key)
    st.toggle = safe_toggle

# 5. Interception pour st.dialog (non supporté sur les vieilles versions)
if not hasattr(st, "dialog"):
    def safe_dialog(*args, **kwargs):
        # Redirige proprement vers un container d'avertissement classique
        return st.container()
    st.dialog = safe_dialog

def securiser_widget_factory(fonction_origine):
    def safe_widget(*args, **kwargs):
        cle = kwargs.get("key")
        # Si le widget a une clé et que cette clé est déjà dans la mémoire Session State
        if cle and cle in st.session_state:
            # On retire l'argument 'value' en double pour éviter l'encadré jaune de Streamlit
            kwargs.pop("value", None)
        return fonction_origine(*args, **kwargs)
    return safe_widget




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

liste_onglets = [
    "Identification",
    "Généralités sur les forces",
    "Equlibre en rotation",
    "Théorème des moments",
    "Applications en mécanique",  
    "Exemple 1",               
    "Exemple 2"               
]

onglets = st.tabs(liste_onglets)

# Affectation automatique des variables d'onglets selon leur index
tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_questions_moments_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz3_moments" not in st.session_state:
        base_quiz3_moments = [
            {"id": "q3_1", "q": "Le moment d'une force mesure l'efficacité de cette force à provoquer :", "type": "menu", "options": ["Une rotation", "Une translation", "Une déformation élastique"], "rep": "Une rotation"},
            {"id": "q3_2", "q": "Quelle est l'unité officielle du moment d'une force ?", "type": "menu", "options": ["Newton-mètre (N.m)", "Newton (N)", "Mètre par seconde (m/s)"], "rep": "Newton-mètre (N.m)"},
            {"id": "q3_3", "q": "Dans la formule du moment, que représente la grandeur notée 'd' ?", "type": "menu", "options": ["Le bras de levier", "Le diamètre de l'objet", "La distance parcourue"], "rep": "Le bras de levier"},
            {"id": "q3_4", "q": "Le bras de levier correspond à la distance mesurée de façon :", "type": "menu", "options": ["Perpendiculaire à la droite d'action", "Parallèle à la force", "Oblique par rapport à l'axe"], "rep": "Perpendiculaire à la droite d'action"},
            {"id": "q3_5", "q": "Si le bras de levier double et que la force reste identique, le moment :", "type": "menu", "options": ["Double", "Est divisé par deux", "Reste inchangé"], "rep": "Double"},
            {"id": "q3_6", "q": "Si la droite d'action d'une force est parallèle à l'axe de rotation, son moment est :", "type": "menu", "options": ["Nul", "Maximal", "Négatif"], "rep": "Nul"},
            {"id": "q3_7", "q": "Pour dessiner un bras de levier sur un schéma, on repère l'angle droit entre l'axe et :", "type": "menu", "options": ["La droite d'action de la force", "Le vecteur vitesse", "Le point d'application uniquement"], "rep": "La droite d'action de la force"},
            {"id": "q3_8", "q": "L'expression algébrique exacte du théorème des moments à l'équilibre est :", "type": "menu", "options": ["Somme des moments = 0", "Force x distance = 0", "Somme des forces = 0"], "rep": "Somme des moments = 0"},
            {"id": "q3_9", "q": "Une force de 50 N appliquée avec un bras de levier de 2 m génère un moment de :", "type": "menu", "options": ["100 N.m", "25 N.m", "10 N.m"], "rep": "100 N.m"},
            {"id": "q3_10", "q": "Pour dévisser un écrou grippé plus facilement, il est préférable de :", "type": "menu", "options": ["Rallonger le manche du outil", "Raccourcir le manche du outil", "Changer le point d'application vers l'axe"], "rep": "Rallonger le manche du outil"}
        ]
        copie_base = list(base_quiz3_moments)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz3_moments = copie_base

    col_double_quiz_m3, col_double_trous_m3 = st.columns(2)

    with col_double_quiz_m3:
        st.markdown("##### Quiz sur le calcul des moments (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz3_moments, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"moments_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_moments_{q_data['id']}"
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

    with col_double_trous_m3:
        st.markdown("##### Synthèse mathématique du théorème (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le moment d'une force par rapport à un axe est le produit de la force par le")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Bras de levier", "Rayon", "Vecteur"], key="mom_t1_s3", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Ce bras de levier correspond à la distance la plus courte, mesurée de façon")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Perpendiculaire", "Parallèle", "Horizontale"], key="mom_t2_s3", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. entre l'axe de rotation Delta et la ligne d'action du vecteur")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Force", "Moment", "Poids"], key="mom_t3_s3", disabled=verrouille, label_visibility="collapsed")
        
        c47, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c47: st.write("4. L'unité de mesure combinée s'écrit sous la forme mathématique du")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Newton-mètre", "Newton par mètre", "Joule"], key="mom_t4_s3", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Si la droite d'action d'une force coupe directement l'axe, la distance est")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Nulle", "Maximale", "Inconnue"], key="mom_t5_s3", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Dans ce cas spécifique, l'action mécanique ne produit aucun effet de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Rotation", "Translation", "Glissement"], key="mom_t6_s3", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. À l'équilibre, la somme des moments qui font tourner dans le sens")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Horloger", "Horaire", "Trigonométrique"], key="mom_t7_s3", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. compense les moments opposés. On affecte un signe moins aux rotations du sens")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Horaire", "Anti-horaire", "Direct"], key="mom_t8_s3", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La somme algébrique totale de ces grandeurs est représentée par le symbole")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Sigma", "Delta", "Alpha"], key="mom_t9_s3", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. L'application pratique directe de cette loi se retrouve dans l'utilisation des")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Leviers", "Poulies", "Rampes"], key="mom_t10_s3", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous


def afficher_questions_rotation_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz2_rotation" not in st.session_state:
        base_quiz2_rotation = [
            {"id": "q2_1", "q": "Un objet est en rotation s'il tourne autour d'une ligne fixe appelée :", "type": "menu", "options": ["Axe de rotation Delta", "Centre de gravité", "Vecteur force"], "rep": "Axe de rotation Delta"},
            {"id": "q2_2", "q": "Quelle grandeur physique mesure l'aptitude d'une force à faire tourner un système ?", "type": "menu", "options": ["Le moment de la force", "L'intensité de la force", "La masse du système"], "rep": "Le moment de la force"},
            {"id": "q2_3", "q": "Si un solide ne tourne pas et reste immobile, on dit qu'il est en :", "type": "menu", "options": ["Équilibre en rotation", "Mouvement circulaire", "Translation rectiligne"], "rep": "Équilibre en rotation"},
            {"id": "q2_4", "q": "Par convention, le sens des aiguilles d'une montre est généralement considéré comme :", "type": "menu", "options": ["Négatif", "Positif", "Nul"], "rep": "Négatif"},
            {"id": "q2_5", "q": "Le sens inverse des aiguilles d'une montre est appelé sens :", "type": "menu", "options": ["Trigonométrique ou positif", "Horaire ou négatif", "Neutre"], "rep": "Trigonométrique ou positif"},
            {"id": "q2_6", "q": "Pour obtenir l'équilibre de rotation, la somme algébrique des moments doit être :", "type": "menu", "options": ["Nulle", "Supérieure à 1", "Infinie"], "rep": "Nulle"},
            {"id": "q2_7", "q": "Quel symbole mathématique est utilisé pour représenter la somme des moments ?", "type": "menu", "options": ["Sigma (S)", "Delta (D)", "Pi (P)"], "rep": "Sigma (S)"},
            {"id": "q2_8", "q": "Si deux forces opposées créent des effets de rotation qui se compensent, le solide :", "type": "menu", "options": ["Reste immobile", "Tourne de plus en plus vite", "Se déforme"], "rep": "Reste immobile"},
            {"id": "q2_9", "q": "Un solide pivotant autour d'un axe fixe possède combien de degrés de liberté en rotation ?", "type": "menu", "options": ["Un seul", "Deux", "Trois"], "rep": "Un seul"},
            {"id": "q2_10", "q": "L'expression mathématique de la condition d'équilibre en rotation est :", "type": "menu", "options": ["Sum M = 0", "Sum F = 0", "M = F x d"], "rep": "Sum M = 0"}
        ]
        copie_base = list(base_quiz2_rotation)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz2_rotation = copie_base

    col_double_quiz_r2, col_double_trous_r2 = st.columns(2)

    with col_double_quiz_r2:
        st.markdown("##### Quiz sur les conditions de rotation (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz2_rotation, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"rotation_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_rotation_{q_data['id']}"
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

    with col_double_trous_r2:
        st.markdown("##### Synthèse sur l'équilibre (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Un solide mobile autour d'un axe fixe est en")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Équilibre", "Mouvement", "Tension"], key="rot_t1_s2", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. si la somme algébrique des forces ne provoque aucun changement et que la somme des")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Moments", "Masses", "Vecteurs"], key="rot_t2_s2", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. de toutes les forces appliquées est nulle. Le choix du sens de rotation")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Positif", "Nul", "Identique"], key="rot_t3_s2", disabled=verrouille, label_visibility="collapsed")
        
        c47, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c47: st.write("4. est défini de manière arbitraire. Les forces agissant dans ce sens ont un moment")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Positif", "Négatif", "Nul"], key="rot_t4_s2", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. tandis que les forces agissant dans le sens opposé possèdent un moment")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Négatif", "Positif", "Inconnu"], key="rot_t5_s2", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'axe autour duquel s'effectue le pivotement est noté par la lettre grecque")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Delta", "Sigma", "Omega"], key="rot_t6_s2", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Une force dont la ligne d'action est parallèle à cet axe engendre un moment")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Nul", "Maximum", "Variable"], key="rot_t7_s2", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Une action mécanique qui coupe l'axe de rotation ne peut pas faire")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Tourner", "Glisser", "Accélérer"], key="rot_t8_s2", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'état d'immobilité empêche le système de subir une modification de sa vitesse")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Angulaire", "Linéaire", "Initiale"], key="rot_t9_s2", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Cette loi physique fondamentale régit le fonctionnement de tous les types de")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Leviers", "Moteurs", "Pistons"], key="rot_t10_s2", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous



def afficher_questions_forces_dynamiques(verrouille=False):
    import random
    
    if "ordre_quiz1_forces" not in st.session_state:
        base_quiz1_forces = [
            {"id": "q1_1", "q": "L'unité légale du système international pour mesurer la valeur d'une force est le :", "type": "menu", "options": ["Newton", "Joule", "Kilogramme"], "rep": "Newton"},
            {"id": "q1_2", "q": "La droite qui indique l'orientation d'un vecteur force s'appelle :", "type": "menu", "options": ["La droite d'action ou direction", "Le sens du mouvement", "Le point d'application"], "rep": "La droite d'action ou direction"},
            {"id": "q1_3", "q": "Parmi ces exemples, laquelle est une force s'exerçant à distance ?", "type": "menu", "options": ["Le poids d'un corps", "La tension d'un câble", "Le frottement du sol"], "rep": "Le poids d'un corps"},
            {"id": "q1_4", "q": "Parmi ces exemples, laquelle est une force s'exerçant par contact ?", "type": "menu", "options": ["La réaction d'un support", "L'attraction d'un aimant", "La pesanteur terrestre"], "rep": "La réaction d'un support"},
            {"id": "q1_5", "q": "La pointe de la flèche d'un vecteur force représente quelle caractéristique ?", "type": "menu", "options": ["Le sens", "La direction", "La norme"], "rep": "Le sens"},
            {"id": "q1_6", "q": "L'origine de la flèche représentant un vecteur force correspond au :", "type": "menu", "options": ["Point d'application", "Centre de la Terre", "Ligne de terre"], "rep": "Point d'application"},
            {"id": "q1_7", "q": "Quelle est la notation correcte pour désigner l'intensité (valeur numérique) d'une force ?", "type": "menu", "options": ["F = 50 N", "vec(F) = 50 N", "F = 50 kg"], "rep": "F = 50 N"},
            {"id": "q1_8", "q": "Quelle action mécanique modélise une force capable de freiner un objet glissant ?", "type": "menu", "options": ["Le frottement mécanique", "La tension d'un ressort", "L'attraction magnétique"], "rep": "Le frottement mécanique"},
            {"id": "q1_9", "q": "Le poids d'un objet dépend directement de quelle autre grandeur physique ?", "type": "menu", "options": ["La masse de l'objet", "Le volume de l'objet", "La vitesse de l'objet"], "rep": "La masse de l'objet"},
            {"id": "q1_10", "q": "Si la droite d'action d'une force coupe l'axe de rotation d'un objet, son moment est :", "type": "menu", "options": ["Nul", "Positif", "Négatif"], "rep": "Nul"}
        ]
        copie_base = list(base_quiz1_forces)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1_forces = copie_base

    col_double_quiz_f1, col_double_trous_f1 = st.columns(2)

    with col_double_quiz_f1:
        st.markdown("##### Quiz sur les caractéristiques des forces (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1_forces, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"forces_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_forces_{q_data['id']}"
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

    with col_double_trous_f1:
        st.markdown("##### Synthèse sur la mesure et la typologie (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Une action mécanique capable de modifier le mouvement est modélisée par une")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Force", "Énergie", "Vitesse"], key="forces_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'appareil de mesure utilisé pour quantifier l'intensité d'une force s'appelle un")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Dynamomètre", "Balance", "Manomètre"], key="forces_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Les dispositifs traditionnels utilisaient la déformation mécanique d'un")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Ressort", "Aimant", "Piston"], key="forces_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c47, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c47: st.write("4. Les capteurs modernes convertissent l'effort en un signal")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Électronique", "Chimique", "Thermique"], key="forces_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le poids d'un objet is une action mécanique s'exerçant à")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Distance", "Contact", "L'infini"], key="forces_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'action d'une corde tirant sur une charge constitue une force de")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Contact", "Distance", "Frottement"], key="forces_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La longueur du segment fléché représentant une force est proportionnelle à sa")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Valeur", "Direction", "Masse"], key="forces_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Pour tracer correctement ce vecteur sur un graphique, on utilise une")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Échelle", "Équation", "Boussole"], key="forces_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La droite verticale passant par le centre de gravité d'un corps correspond à la direction du")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Poids", "Frottement", "Vent"], key="forces_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Sur Terre, l'intensité de la pesanteur g vaut environ 9,81 N par")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Kilogramme", "Mètre", "Seconde"], key="forces_t10_s1", disabled=verrouille, label_visibility="collapsed")

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
    st.header("Généralités sur les forces")
    
    # --- SECTION HISTORIQUE EN PREMIER ---
    st.subheader("1. Historique de la mesure des forces : Du ressort au connecté")
    
    col_hist_txt, col_hist_img = st.columns([1, 1])
    
    with col_hist_txt:
        st.write("**La bande dessinée humoristique : L'évolution de la mesure mécanique**")
        st.info(
            "**Case 1 : Le dynamomètre traditionnel (Passé) :** Un technicien manipule un peson mécanique massif à ressort en acier. Ses collègues le regardent avec étonnement, car l'appareil est lourd à transporter d'un chantier à un autre.\n\n"
            "**Case 2 : L'ancien système de lecture (Passé) :** À l'autre bout de l'atelier, un opérateur doit plisser les yeux pour lire la valeur de la force sur une graduation rectiligne en métal usée, peu précise et difficile à déchiffrer.\n\n"
            "**Case 3 : L'arrivée de l'électronique (Années 2000) :** Les capteurs de force deviennent miniatures. Les données de traction ou de compression sont converties en signaux électriques et transmises proprement par des câbles ou des liaisons sans fil.\n\n"
            "**Case 4 : Le technicien moderne (Aujourd'hui) :** Un jeune apprenti utilise un dynamomètre numérique de poche connecté en Bluetooth. Il regarde les anciens appareils à ressort et s'étonne : Comment faisaient-ils avant pour enregistrer les variations de force en temps réel, stocker les données sur ordinateur et tracer automatiquement des graphiques d'équilibre sans écran ?"
        )
            
    with col_hist_img:
        if os.path.exists("caricature_forces.jpg"):
            st.image("caricature_forces.jpg", caption="Évolution technologique des systèmes de mesure", use_container_width=True)
        else:
            st.warning("L'image 'caricature_forces.jpg' contenant la bande dessinée est introuvable dans le dossier.")

    st.divider()

    # --- SECTION COURS ET THÉORIE ---
    st.subheader("2. Définition et rappel")
    st.write(
        "Une force modélise une action mécanique exercée par un objet sur un autre. "
        "Elle est capable de mettre un corps en mouvement, de modifier sa trajectoire ou de le déformer."
    )
    
    st.subheader("3. Caractéristiques et représentation")
    st.write(
        "Une force se représente graphiquement par un segment fléché nommé vecteur force. "
        "Elle possède quatre caractéristiques fondamentales :"
    )
    st.markdown(
        """
        *   **Le point d'application** : Lieu exact où la force s'exerce sur l'objet.
        *   **La droite d'action (ou direction)** : Ligne droite suivant laquelle la force agit (horizontale, verticale, oblique).
        *   **Le sens** : Orientation de l'action (vers la droite, vers la gauche, vers le haut, vers le bas).
        *   **La norme (ou intensité)** : Valeur numérique de la force.
        """
    )
    
    st.subheader("4. Typologie des forces")
    col_forces_a, col_forces_b = st.columns(2)
    
    with col_forces_a:
        st.markdown("**Forces de contact**")
        st.write("L'action nécessite un contact physique entre l'auteur et le receveur.")
        st.markdown("- Tension d'un câble ou d'une corde\n- Force de frottement sur le sol\n- Réaction d'un support")
        if os.path.exists("force_contact.jpg"):
            st.image("force_contact.jpg", caption="Illustration d'une action mécanique de contact", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : force_contact.jpg")

    with col_forces_b:
        st.markdown("**Forces à distance**")
        st.write("L'action s'exerce sans qu'il n'y ait de contact physique entre les objets.")
        st.markdown("- Force gravitationnelle (Poids d'un corps)\n- Force magnétique (Aimant)\n- Force électrostatique")
        if os.path.exists("force_distance.jpg"):
            st.image("force_distance.jpg", caption="Illustration d'une action mécanique à distance", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : force_distance.jpg")
            
    st.divider()

    st.subheader("5. Unités et appareils de mesure")
    st.write(
        "L'unité légale du système international pour mesurer l'intensité d'une force est le **Newton (N)**. "
        "L'appareil utilisé pour mesurer une force est le dynamomètre."
    )
    
    col_img1, col_img2 = st.columns(2)
    
    with col_img1:
        st.markdown("**Appareil ancien (Dynamomètre mécanique à ressort)**")
        if os.path.exists("ancien_appareil.jpg"):
            st.image("ancien_appareil.jpg", caption="Dynamomètre traditionnel à aiguille ou à graduation rectiligne", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : ancien_appareil.jpg")

    with col_img2:
        st.markdown("**Appareil nouveau (Dynamomètre numérique ou capteur électronique)**")
        if os.path.exists("nouveau_appareil.jpg"):
            st.image("nouveau_appareil.jpg", caption="Dynamomètre digital moderne avec affichage électronique", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : nouveau_appareil.jpg")

     # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES (FORCES)
    # =========================================================================
    verrou_forces_1 = st.session_state.get("forces_verrouille_tab1", False)

    # Appel de la fonction de questionnaire pour les Généralités sur les forces
    res_q1, res_t1 = afficher_questions_forces_dynamiques(verrouille=verrou_forces_1)

    st.write("---")
    st.subheader("Validation de la section sur les forces")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_forces1 = st.checkbox(
        "Je certifie avoir complété les questions de l'évaluation sur les forces.", 
        key="check_certif_forces1_official", 
        disabled=verrou_forces_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ÉVALUATION DES FORCES", key="btn_export_forces1_official_net", use_container_width=True, disabled=verrou_forces_1):
        if not st.session_state.get("identifie", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_forces1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique adaptative liée à l'ordre mélangé du Quiz Forces
            score_q1 = 0.0
            if "ordre_quiz1_forces" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_forces:
                    reponse_eleve = st.session_state.get(f"forces_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatique du Texte à trous sur la mécanique (10 points)
            score_t1 = sum([
                st.session_state.get("forces_t1_s1") == "Force",
                st.session_state.get("forces_t2_s1") == "Dynamomètre",
                st.session_state.get("forces_t3_s1") == "Ressort",
                st.session_state.get("forces_t4_s1") == "Électronique",
                st.session_state.get("forces_t5_s1") == "Distance",
                st.session_state.get("forces_t6_s1") == "Contact",
                st.session_state.get("forces_t7_s1") == "Valeur",
                st.session_state.get("forces_t8_s1") == "Échelle",
                st.session_state.get("forces_t9_s1") == "Poids",
                st.session_state.get("forces_t10_s1") == "Kilogramme"
            ])

            st.session_state.score_forces1_p1 = round(float(score_q1), 1)
            st.session_state.score_forces1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_forces1 = round(float(score_q1 + score_t1), 1)
            st.session_state.forces_verrouille_tab1 = True
            st.rerun()

    if st.session_state.get("forces_verrouille_tab1", False):
        scr1 = st.session_state.get("score_forces1_p1", 0.0)
        scr2 = st.session_state.get("score_forces1_p2", 0.0)
        tot_s = st.session_state.get("score_final_forces1", 0.0)

        from datetime import datetime
        timestamp_forces1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"SECTION DES FORCES SCELLÉE | Note de session : {tot_s:.1f} / 20")

        html_export_forces1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Généralités sur les forces - {n_eleve}</title>
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
                <p>Évaluation : Généralités sur les forces et les systèmes de mesure</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_forces1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des notes générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz sur les caractéristiques des forces : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse sur la mesure et la typologie : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de la section : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction détaillée du Quiz (ordre d'affichage de la session)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz1_forces" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz1_forces, 1):
                saisie = st.session_state.get(f"forces_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_forces1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_forces1 += """
                </tbody>
            </table>

            <div class="sub-title">Correction détaillée des trous de synthèse</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous1 = [
            "1. Une action mécanique capable de modifier le mouvement est modélisée par une",
            "2. L'appareil de mesure utilisé pour quantifier l'intensité d'une force s'appelle un",
            "3. Les dispositifs traditionnels utilisaient la déformation mécanique d'un",
            "4. Les capteurs modernes convertissent l'effort en un signal",
            "5. Le poids d'un objet est une action mécanique s'exerçant à",
            "6. L'action d'une corde tirant sur une charge constitue une force de",
            "7. La longueur du segment fléché représentant une force est proportionnelle à sa",
            "8. Pour tracer correctement ce vecteur sur un graphique, on utilise une",
            "9. La droite verticale passant par le centre de gravité d'un corps correspond à la direction du",
            "10. Sur Terre, l'intensité de la pesanteur g vaut environ 9,81 N par"
        ]
        attendus_trous1 = ["Force", "Dynamomètre", "Ressort", "Électronique", "Distance", "Contact", "Valeur", "Échelle", "Poids", "Kilogramme"]
        cles_trous1 = ["forces_t1_s1", "forces_t2_s1", "forces_t3_s1", "forces_t4_s1", "forces_t5_s1", "forces_t6_s1", "forces_t7_s1", "forces_t8_s1", "forces_t9_s1", "forces_t10_s1"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous1, attendus_trous1, cles_trous1), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_forces1 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_forces1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendre le bouton de téléchargement du rapport HTML disponible une fois le questionnaire scellé
        nom_fichier_html = preparer_nom_fichier("rapport_forces") + ".html"
        st.download_button(
            label="Télécharger le fichier de rapport officiel (HTML)",
            data=html_export_forces1,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Équilibre en rotation")
    
    st.subheader("1. Définition de la rotation autour d'un axe fixe")
    st.write(
        "Un solide est en mouvement de rotation autour d'un axe fixe Delta si tous ses points "
        "décrivent des trajectoires circulaires centrées sur cet axe. Lorsque le solide ne bouge pas, "
        "malgré les forces qui s'exercent sur lui, il est dit en équilibre de rotation."
    )
    
    st.subheader("2. Notion de sens de rotation et convention")
    st.write(
        "Pour étudier l'effet des forces sur un objet pivotant, il est obligatoire de choisir un sens "
        "de rotation considéré comme positif. Par convention :"
    )
    st.markdown(
        """
        *   **Le sens positif (ou trigonométrique)** : Sens inverse des aiguilles d'une montre.
        *   **Le sens négatif (ou horaire)** : Sens des aiguilles d'une montre.
        """
    )
    st.write(
        "Une force qui tend à faire tourner le système dans le sens positif aura un effet positif, "
        "tandis qu'une force qui tend à le faire tourner dans le sens inverse aura un effet négatif."
    )

    st.subheader("3. Condition d'équilibre d'un système en rotation")
    st.write(
        "Pour qu'un objet soumis à un axe fixe reste en parfait équilibre de rotation, il faut que les "
        "actions qui le font tourner dans un sens compensent exactement celles qui le font tourner dans l'autre. "
        "La somme algébrique des effets de rotation de toutes les forces appliquées doit donc être égale à zéro."
    )

    # --- LOGIQUE DE COUPLAGE ET VALIDATION DE L'ONGLET 2 ---
    st.divider()
    st.subheader("4. Évaluation sur l'équilibre en rotation")
    
    verrou_rotation_2 = st.session_state.get("rotation_verrouille_tab2", False)
    res_q2, res_t2 = afficher_questions_rotation_dynamiques(verrouille=verrou_rotation_2)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_rotation2 = st.checkbox(
        "Je certifie avoir complété les questions de l'évaluation sur l'équilibre en rotation.", 
        key="check_certif_rotation2_official", 
        disabled=verrou_rotation_2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ÉVALUATION DE LA ROTATION", key="btn_export_rotation2_official_net", use_container_width=True, disabled=verrou_rotation_2):
        if not st.session_state.get("identifie", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_rotation2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz2_rotation" in st.session_state:
                for q_item in st.session_state.ordre_quiz2_rotation:
                    reponse_eleve = st.session_state.get(f"rotation_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = sum([
                st.session_state.get("rot_t1_s2") == "Équilibre",
                st.session_state.get("rot_t2_s2") == "Moments",
                st.session_state.get("rot_t3_s2") == "Positif",
                st.session_state.get("rot_t4_s2") == "Positif",
                st.session_state.get("rot_t5_s2") == "Négatif",
                st.session_state.get("rot_t6_s2") == "Delta",
                st.session_state.get("rot_t7_s2") == "Nul",
                st.session_state.get("rot_t8_s2") == "Tourner",
                st.session_state.get("rot_t9_s2") == "Angulaire",
                st.session_state.get("rot_t10_s2") == "Leviers"
            ])

            st.session_state.score_rotation2_p1 = round(float(score_q2), 1)
            st.session_state.score_rotation2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_rotation2 = round(float(score_q2 + score_t2), 1)
            st.session_state.rotation_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("rotation_verrouille_tab2", False):
        scr1 = st.session_state.get("score_rotation2_p1", 0.0)
        scr2 = st.session_state.get("score_rotation2_p2", 0.0)
        tot_s = st.session_state.get("score_final_rotation2", 0.0)

        timestamp_rotation2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"SECTION ROTATION SCELLÉE | Note de session : {tot_s:.1f} / 20")

        html_export_rotation2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Équilibre en rotation - {n_eleve}</title>
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
                <p>Évaluation : Lois fondamentales de l'équilibre en rotation autour d'un axe fixe</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_rotation2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des notes générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz sur les conditions de rotation : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse sur l'équilibre : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de la section : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction détaillée du Quiz (ordre d'affichage de la session)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz2_rotation" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz2_rotation, 1):
                saisie = st.session_state.get(f"rotation_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_rotation2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_rotation2 += """
                </tbody>
            </table>

            <div class="sub-title">Correction détaillée des trous de synthèse</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            "1. Un solide mobile autour d'un axe fixe est en",
            "2. si la somme algébrique des forces ne provoque aucun changement et que la somme des",
            "3. de toutes les forces appliquées est nulle. Le choix du sens de rotation",
            "4. est défini de manière arbitraire. Les forces agissant dans ce sens ont un moment",
            "5. tandis que les forces agissant dans le sens opposé possèdent un moment",
            "6. L'axe autour duquel s'effectue le pivotement est noté par la lettre grecque",
            "7. Une force dont la ligne d'action est parallèle à cet axe engendre un moment",
            "8. Une action mécanique qui coupe l'axe de rotation ne peut pas faire",
            "9. L'état d'immobilité empêche le système de subir une modification de sa vitesse",
            "10. Cette loi physique fondamentale régit le fonctionnement de tous les types de"
        ]
        attendus_trous2 = ["Équilibre", "Moments", "Positif", "Positif", "Négatif", "Delta", "Nul", "Tourner", "Angulaire", "Leviers"]
        cles_trous2 = ["rot_t1_s2", "rot_t2_s2", "rot_t3_s2", "rot_t4_s2", "rot_t5_s2", "rot_t6_s2", "rot_t7_s2", "rot_t8_s2", "rot_t9_s2", "rot_t10_s2"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous2, attendus_trous2, cles_trous2), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_rotation2 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_rotation2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html2 = preparer_nom_fichier("rapport_rotation") + ".html"
        st.download_button(
            label="Télécharger le fichier de rapport officiel de l'Atelier 2 (HTML)",
            data=html_export_rotation2,
            file_name=nom_fichier_html2,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Théorème des moments")

    st.subheader("1. Rappel de cours sur le moment d'une force")
    st.markdown("Formule fondamentale : $M_{\\Delta}(\\vec{F}) = F \\times d$")
    st.write(
        "Le moment est exprimé en Newton-mètre (N.m). L'intensité de la force F est en Newtons (N) "
        "et la distance d, représentant le bras de levier, est impérativement convertie en mètres (m)."
    )
        
        st.subheader("2. Laboratoire virtuel d'expérimentation")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Configuration des actions")
            f1 = st.slider("Force gauche (F1 en N)", 10, 200, 100, step=10)
            d1 = st.slider("Bras de levier gauche (d1 en m)", 0.5, 4.0, 2.0, step=0.1)
            
            st.divider()
            
            f2 = st.slider("Force droite (F2 en N)", 10, 200, 50, step=10)
            d2_cible = round((f1 * d1) / f2, 2)
            
            st.info(f"Objectif : Pour obtenir l'équilibre parfait, la distance théorique d2 doit être de {d2_cible} m.")
            d2_user = st.slider("Ajustez votre position réelle (d2 en m)", 0.5, 4.0, 3.5, step=0.1)

        with col2:
            st.subheader("Schéma de la situation")
            
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot([-4.5, 4.5], [0, 0], color="brown", lw=6)
            ax.plot([0, -0.3, 0.3, 0], [0, -0.5, -0.5, 0], color="black", lw=3)
            ax.text(-0.3, -0.9, "Axe D", fontsize=10, weight='bold')

            # Force GAUCHE
            ax.annotate('', xy=(-d1, -1), xytext=(-d1, 0), arrowprops=dict(facecolor='red', width=3, headwidth=10))
            ax.text(-d1 - 0.5, -1.3, f"F1: {f1}N", color='red', weight='bold')
            ax.text(-d1/2, 0.2, f"{d1}m", color='red')

            # Force DROITE
            ax.annotate('', xy=(d2_user, -1), xytext=(d2_user, 0), arrowprops=dict(facecolor='green', width=3, headwidth=10))
            ax.text(d2_user - 0.2, -1.3, f"F2: {f2}N", color='green', weight='bold')
            ax.text(d2_user/2, 0.2, f"{d2_user}m", color='green')

            ax.set_xlim(-5, 5)
            ax.set_ylim(-2, 1)
            ax.axis('off')
            
            mom_gauche = f1 * d1
            mom_droite = f2 * d2_user
            
            if abs(mom_gauche - mom_droite) < 1.0:
                ax.title.set_text("PARFAIT ÉQUILIBRE !")
                ax.title.set_color("green")
                st.success("Bravo ! L'équilibre des moments est respecté.")
            elif mom_gauche > mom_droite:
                ax.title.set_text("BASCULE A GAUCHE")
                ax.title.set_color("red")
                st.error("Le moment à gauche est supérieur. Augmentez d2 ou diminuez d1.")
            else:
                ax.title.set_text("BASCULE A DROITE")
                ax.title.set_color("red")
                st.error("Le moment à droite est supérieur. Rapprochez la force F2.")

            st.pyplot(fig)
            
            nom_image = preparer_nom_fichier("theoreme_moments") + ".jpg"
            plt.savefig("temp_schema.jpg", format="jpg", dpi=150, bbox_inches='tight')
            with open("temp_schema.jpg", "rb") as file:
                st.download_button(label="Télécharger le schéma (JPG)", data=file, file_name=nom_image, mime="image/jpeg")

        # --- LOGIQUE DE COUPLAGE ET VALIDATION DE L'ONGLET 3 ---
        st.divider()
        st.subheader("3. Évaluation sur le théorème des moments")
        
        verrou_moments_3 = st.session_state.get("moments_verrouille_tab3", False)
        res_q3, res_t3 = afficher_questions_moments_dynamiques(verrouille=verrou_moments_3)

        st.write("---")
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        case_certif_moments3 = st.checkbox(
            "Je certifie avoir complété les questions de l'évaluation sur le théorème des moments.", 
            key="check_certif_moments3_official", 
            disabled=verrou_moments_3
        )

        if st.button("VALIDER ET EXPORTER LE BILAN DU THÉORÈME DES MOMENTS", key="btn_export_moments3_official_net", use_container_width=True, disabled=verrou_moments_3):
            if not st.session_state.get("identifie", False):
                st.error("Action refusée : Saisissez votre identity dans l'onglet 'Identification'.")
            elif not case_certif_moments3:
                st.error("Action refusée : Cochez la case de certification.")
            else:
                score_q3 = 0.0
                if "ordre_quiz3_moments" in st.session_state:
                    for q_item in st.session_state.ordre_quiz3_moments:
                        reponse_eleve = st.session_state.get(f"moments_cl_g_{q_item['id']}", "Choisir...")
                        if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                            score_q3 += 1.0

                score_t3 = sum([
                    st.session_state.get("mom_t1_s3") == "Bras de levier",
                    st.session_state.get("mom_t2_s3") == "Perpendiculaire",
                    st.session_state.get("mom_t3_s3") == "Force",
                    st.session_state.get("mom_t4_s3") == "Newton-mètre",
                    st.session_state.get("mom_t5_s3") == "Nulle",
                    st.session_state.get("mom_t6_s3") == "Rotation",
                    st.session_state.get("mom_t7_s3") == "Trigonométrique",
                    st.session_state.get("mom_t8_s3") == "Horaire",
                    st.session_state.get("mom_t9_s3") == "Sigma",
                    st.session_state.get("mom_t10_s3") == "Leviers"
                ])

                st.session_state.score_moments3_p1 = round(float(score_q3), 1)
                st.session_state.score_moments3_p2 = round(float(score_t3), 1)
                st.session_state.score_final_moments3 = round(float(score_q3 + score_t3), 1)
                st.session_state.moments_verrouille_tab3 = True
                st.rerun()

        if st.session_state.get("moments_verrouille_tab3", False):
            scr1 = st.session_state.get("score_moments3_p1", 0.0)
            scr2 = st.session_state.get("score_moments3_p2", 0.0)
            tot_s = st.session_state.get("score_final_moments3", 0.0)

            timestamp_moments3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
            st.success(f"SECTION THÉORÈME DES MOMENTS SCELLÉE | Note de session : {tot_s:.1f} / 20")

            html_export_moments3 = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Rapport Théorème des moments - {n_eleve}</title>
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
                    <p>Évaluation : Modélisation des actions mécaniques et théorème des moments</p>
                    <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                    <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_moments3}</p>
                    <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
                </div>
                
                <div class="sub-title">Récapitulatif des notes générées</div>
                <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                    &bull; Note obtenue au Quiz sur le calcul des moments : <strong>{scr1:.1f} / 10</strong><br>
                    &bull; Note obtenue à la Synthèse mathématique : <strong>{scr2:.1f} / 10</strong><br>
                    &bull; Note Totale de la section : <strong>{tot_s:.1f} / 20</strong>
                </p>

                <div class="sub-title">Correction détaillée du Quiz (ordre d'affichage de la session)</div>
                <table>
                    <thead>

                    <tr>
                        <th>N°</th>
                        <th>Question Posée</th>
                        <th>Saisie Élève</th>
                        <th>Attendu Académique</th>
                        <th>Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz3_moments" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz3_moments, 1):
                saisie = st.session_state.get(f"moments_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_moments3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_moments3 += """
                </tbody>
            </table>

            <div class="sub-title">Correction détaillée des trous de synthèse</div>
            <table>
                <thead>
                    <tr>
                        <th>N°</th>
                        <th>Énoncé de cours</th>
                        <th>Saisie Élève</th>
                        <th>Attendu Académique</th>
                        <th>Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        phrases_trous3 = [
            "1. Le moment d'une force par rapport à un axe est le produit de la force par le",
            "2. Ce bras de levier correspond à la distance la plus courte, mesurée de façon",
            "3. entre l'axe de rotation Delta et la ligne d'action du vecteur",
            "4. L'unité de mesure combinée s'écrit sous la forme mathématique du",
            "5. Si la droite d'action d'une force coupe directement l'axe, la distance est",
            "6. Dans ce cas spécifique, l'action mécanique ne produit aucun effet de",
            "7. À l'équilibre, la somme des moments qui font tourner dans le sens",
            "8. compense les moments opposés. On affecte un signe moins aux rotations du sens",
            "9. La somme algébrique totale de ces grandeurs est représentée par le symbole",
            "10. L'application pratique directe de cette loi se retrouve dans l'utilisation des"
        ]
        attendus_trous3 = ["Bras de levier", "Perpendiculaire", "Force", "Newton-mètre", "Nulle", "Rotation", "Trigonométrique", "Horaire", "Sigma", "Leviers"]
        cles_trous3 = ["mom_t1_s3", "mom_t2_s3", "mom_t3_s3", "mom_t4_s3", "mom_t5_s3", "mom_t6_s3", "mom_t7_s3", "mom_t8_s3", "mom_t9_s3", "mom_t10_s3"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous3, attendus_trous3, cles_trous3), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_moments3 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_moments3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html3 = preparer_nom_fichier("rapport_moments") + ".html"
        st.download_button(
            label="Télécharger le fichier de rapport officiel de l'Atelier 3 (HTML)",
            data=html_export_moments3,
            file_name=nom_fichier_html3,
            mime="text/html",
            use_container_width=True
        )































