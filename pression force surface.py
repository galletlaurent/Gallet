# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application force pressante",
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
st.title("Application force pressante")
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
        try: 
            return Image.open(chemin_secours)
        except Exception: 
            pass
    return None

# --- TOUS LES CORRECTIFS SÉCURISÉS (RERUN, COLUMNS, CONTAINER, IMAGE) ---

# 1. Sauvegarde STRICTE des fonctions d'origine AVANT modification
_vrai_st_rerun = st.rerun if hasattr(st, "rerun") else (st.experimental_rerun if hasattr(st, "experimental_rerun") else None)
_vrai_st_image = st.image
_vrai_st_columns = st.columns
_vrai_st_container = st.container

# 2. Correctif pour st.rerun
def safe_rerun():
    if _vrai_st_rerun is not None:
        try: 
            _vrai_st_rerun()
        except Exception:
            from streamlit.runtime.scriptrunner import RerunData, RerunException
            raise RerunException(RerunData())
st.rerun = safe_rerun

import matplotlib as mpl
mpl.rcParams['text.usetex'] = False
mpl.rcParams['mathtext.default'] = 'regular'

# 3. Correctif pour st.image (Résolution de la boucle infinie)
def safe_image(image, *args, **kwargs):
    if "use_container_width" in kwargs:
        kwargs["use_column_width"] = kwargs.pop("use_container_width")
    if isinstance(image, str) and not image.startswith(("http://", "https://", "data:image")):
        nom_fichier = os.path.basename(image)
        img_pil = charger_image(nom_fichier)
        if img_pil is not None: 
            image = img_pil
    return _vrai_st_image(image, *args, **kwargs)  # Utilise la vraie fonction d'origine
st.image = safe_image

# 4. Interception pour st.columns (vertical_alignment)
def safe_columns(*args, **kwargs):
    if "vertical_alignment" in kwargs:
        kwargs.pop("vertical_alignment")
    return _vrai_st_columns(*args, **kwargs)
st.columns = safe_columns

# 5. Interception pour st.container (border)
def safe_container(*args, **kwargs):
    if "border" in kwargs:
        kwargs.pop("border")
    return _vrai_st_container(*args, **kwargs)
st.container = safe_container

# 6. Rétrocompatibilité st.toggle -> st.checkbox
if not hasattr(st, "toggle"):
    def safe_toggle(label, value=False, key=None, **kwargs):
        return st.checkbox(label, value=value, key=key)
    st.toggle = safe_toggle

# 7. Rétrocompatibilité st.dialog
if not hasattr(st, "dialog"):
    def safe_dialog(*args, **kwargs):
        return st.container()
    st.dialog = safe_dialog

# 8. Décorateur pour sécuriser l'état des widgets (Session State)
def securiser_widget_factory(fonction_origine):
    def safe_widget(*args, **kwargs):
        cle = kwargs.get("key")
        if cle and cle in st.session_state:
            kwargs.pop("value", None)
        return fonction_origine(*args, **kwargs)
    return safe_widget



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


onglets = st.tabs([
    "Identification",
    "Historique",
    "Forces",
    "Pression",
    "Surface",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine topographe géomètre"
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]
tab6 = onglets[6] 
tab7 = onglets[7] 
tab8 = onglets[8]

def afficher_atelier_surface(verrouille=False):
    import random
    import math
    import streamlit as st

    # Déclaration de la base de données des 10 questions du Quiz Surface
    questions_surf_sources = [
        {"id": "qsu1", "q": "Quelle est l'unité légale du système international (SI) pour mesurer une surface ou une aire ?", "options": ["Le mètre carré (m²)", "Le centimètre carré (cm²)", "Le millimètre carré (mm²)"], "rep": "Le mètre carré (m²)"},
        {"id": "qsu2", "q": "Par quelle formule mathématique calcule-t-on la surface d'un piston circulaire de diamètre D ?", "options": ["S = (pi * D²) / 4", "S = pi * D", "S = 2 * pi * D"], "rep": "S = (pi * D²) / 4"},
        {"id": "qsu3", "q": "Combien de centimètres carrés (cm²) contient un mètre carré (m²) ?", "options": ["10 000 cm²", "100 cm²", "1 000 cm²"], "rep": "10 000 cm²"},
        {"id": "qsu4", "q": "Dans la relation P = F / S, si la force F reste fixe et que la surface S augmente, la pression P :", "options": ["Diminue", "Augmente", "Reste identique"], "rep": "Diminue"},
        {"id": "qsu5", "q": "Pour obtenir une pression très élevée à partir d'une force modérée, la surface d'appui doit être :", "options": ["La plus petite possible", "La plus grande possible", "Parfaitement infinie"], "rep": "La plus petite possible"},
        {"id": "qsu6", "q": "Quel mathématicien antique de Syracuse a formalisé les premières méthodes de calcul des aires de cercles et de disques ?", "options": ["Archimède", "Thalès", "Pythagore"], "rep": "Archimède"},
        {"id": "qsu7", "q": "Dans un système de vérins hydrauliques (presse de Pascal), pour multiplier la force, le vérin récepteur doit avoir :", "options": ["Une surface plus grande que le vérin émetteur", "Une surface plus petite que le vérin émetteur", "La même surface que le vérin émetteur"], "rep": "Une surface plus grande que le vérin émetteur"},
        {"id": "qsu8", "q": "Quelle est la valeur numérique abrégée de la constante Pi couramment utilisée pour le calcul des surfaces circulaires ?", "options": ["3,1416", "1,414", "2,718"], "rep": "3,1416"},
        {"id": "qsu9", "q": "Si un diamètre de piston est exprimé en millimètres (mm), sa surface calculée sera directement en :", "options": ["Millimètres carrés (mm²)", "Mètres carrés (m²)", "Centimètres carrés (cm²)"], "rep": "Millimètres carrés (mm²)"},
        {"id": "qsu10", "q": "Le terme 'section normale' d'un conduit ou d'un vérin désigne une surface qui coupe l'axe de manière :", "options": ["Perpendiculaire", "Parallèle", "Oblique à 45 degrés"], "rep": "Perpendiculaire"}
    ]

    if "ordre_quiz_surf4_aleatoire" not in st.session_state:
        random.shuffle(questions_surf_sources)
        st.session_state.ordre_quiz_surf4_aleatoire = questions_surf_sources

    if "champs_surf4_clean" not in st.session_state:
        st.session_state.champs_surf4_clean = [
            ("1. L'aire d'une paroi en contact direct avec un fluide constitue sa ..........", ["Choisir...", "surface", "force"], "surface", "surf4_t1"),
            ("2. Pour l'application des formules SI, l'aire s'exprime obligatoirement en ..........", ["Choisir...", "mètre carré", "millimètre"], "mètre carré", "surf4_t2"),
            ("3. Multiplier le rayon d'un disque par lui-même et par la constante Pi donne son ..........", ["Choisir...", "aire", "périmètre"], "aire", "surf4_t3"),
            ("4. Dans une presse hydraulique, la force est multipliée si le grand vérin possède une large ..........", ["Choisir...", "section", "course"], "section", "surf4_t4"),
            ("5. Une pointe acérée s'enfonce facilement car sa surface de contact est extrêmement ..........", ["Choisir...", "réduite", "étendue"], "réduite", "surf4_t5"),
            ("6. Diviser une force mécanique par la valeur de la section permet d'obtenir la ..........", ["Choisir...", "pression", "puissance"], "pression", "surf4_t6"),
            ("7. Un centimètre carré représente une fraction d'un mètre carré égale à un ..........", ["Choisir...", "dix-millième", "centième"], "dix-millième", "surf4_t7"),
            ("8. À pression constante, l'effort développé par un piston augmente proportionnellement à sa ..........", ["Choisir...", "surface", "longueur"], "surface", "surf4_t8"),
            ("9. L'étude de la géométrie plane et du calcul des surfaces remonte à l'..........", ["Choisir...", "Antiquité", "Époque moderne"], "Antiquité", "surf4_t9"),
            ("10. La section transversale interne d'un cylindre de guidage est une surface ..........", ["Choisir...", "circulaire", "rectangulaire"], "circulaire", "surf4_t10")
        ]

    # SEPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES (MOTEUR BI-COLONNE SCELLÉ)
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_surf4_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"surf_at4_final_g_{q_data['id']}_{idx}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for idx, ligne in enumerate(st.session_state.champs_surf4_clean, 1):
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_surf4_clean_{idx}", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )



def afficher_atelier_pression(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour l'Atelier 3."""
    import random
    import streamlit as st
    import os

    # Déclaration de la base de données des 10 questions du Quiz Pression
    questions_pres_sources = [
        {"id": "qpr1", "q": "Quelle unité de mesure du système international correspond exactement à un Pascal (Pa) ?", "options": ["1 N/m²", "1 kg/m²", "1 J/m²"], "rep": "1 N/m²"},
        {"id": "qpr2", "q": "Quelle est l'unité usuelle utilisée dans l'industrie équivalente à 100 000 Pascals ?", "options": ["Le bar", "L'atmosphère", "Le millimètre de mercure"], "rep": "Le bar"},
        {"id": "qpr3", "q": "Quel instrument de mesure spécifique utilise-t-on pour relever la pression à l'intérieur d'un circuit hydraulique fermé ?", "options": ["Un manomètre", "Un baromètre", "Un anémomètre"], "rep": "Un manomètre"},
        {"id": "qpr4", "q": "Comment évolue la pression atmosphérique lorsque l'on s'élève en altitude ?", "options": ["Elle diminue", "Elle augmente", "Elle reste constante"], "rep": "Elle diminue"},
        {"id": "qpr5", "q": "La pression exercée au fond d'une cuve par une colonne de liquide dépend principalement de :", "options": ["La hauteur du liquide et sa densité", "La forme de la cuve", "Le volume total du réservoir"], "rep": "La hauteur du liquide et sa densité"},
        {"id": "qpr6", "q": "Quel fluide lourd Torricelli a-t-il retenu pour créer le premier baromètre à colonne ?", "options": ["Le mercure", "L'eau déminéralisée", "L'huile hydraulique"], "rep": "Le mercure"},
        {"id": "qpr7", "q": "Quelle valeur moyenne standard caractérise la pression atmosphérique au niveau de la mer ?", "options": ["1013 hPa", "100 000 Pa", "1 bar"], "rep": "1013 hPa"},
        {"id": "qpr8", "q": "Dans une canalisation, comment se nomme un point où la pression du fluide devient inférieure à la pression atmosphérique ?", "options": ["Une dépression (ou vide relatif)", "Une surpression", "Une zone d'équilibre"], "rep": "Une dépression (ou vide relatif)"},
        {"id": "qpr9", "q": "Pourquoi les liquides sont-ils privilégiés dans les transmissions de puissance industrielle ?", "options": ["Parce qu'ils sont incompressibles", "Parce qu'ils sont expansibles", "Parce qu'ils n'ont pas de poids"], "rep": "Parce qu'ils sont incompressibles"},
        {"id": "qpr10", "q": "Quelle loi stipule qu'une variation de pression appliquée en un point d'un fluide enfermé se transmet intégralement ?", "options": ["Le principe de Pascal", "La poussée d'Archimède", "La loi de Newton"], "rep": "Le principe de Pascal"}
    ]

    if "ordre_quiz_pres3_aleatoire" not in st.session_state:
        random.shuffle(questions_pres_sources)
        st.session_state.ordre_quiz_pres3_aleatoire = questions_pres_sources

    if "champs_pres3_clean" not in st.session_state:
        st.session_state.champs_pres3_clean = [
            ("1. La pression traduit la répartition d'une force pressante sur une ..........", ["Choisir...", "surface", "vitesse"], "surface", "pres3_t1"),
            ("2. L'instrument destiné à évaluer la valeur de la pression atmosphérique est le ..........", ["Choisir...", "baromètre", "manomètre"], "baromètre", "pres3_t2"),
            ("3. En hydraulique, le manomètre indique souvent une pression relative par rapport à l'..........", ["Choisir...", "atmosphère", "vide"], "atmosphère", "pres3_t3"),
            ("4. La pression hydrostatique au sein d'un liquide au repos croît avec la ..........", ["Choisir...", "profondeur", "surface"], "profondeur", "pres3_t4"),
            ("5. Un fluide transmettant fidèlement les pressions subies est qualifié d'..........", ["Choisir...", "incompressible", "gazeux"], "incompressible", "pres3_t5"),
            ("6. L'unité légale du système international pour quantifier la pression est le ..........", ["Choisir...", "Pascal", "Bar"], "Pascal", "pres3_t6"),
            ("7. Un bar correspond à une valeur de pression équivalente à cent mille ..........", ["Choisir...", "Pascals", "Newtons"], "Pascals", "pres3_t7"),
            ("8. À force constante, si la section d'appui est divisée par deux, la pression ..........", ["Choisir...", "double", "diminue"], "double", "pres3_t8"),
            ("9. La force pressante générée agit de façon normale, c'est-à-dire .......... aux parois.", ["Choisir...", "perpendiculaire", "tangentielle"], "perpendiculaire", "pres3_t9"),
            ("10. L'absence totale de molécules de gaz ou de matière définit l'état de ..........", ["Choisir...", "vide", "surpression"], "vide", "pres3_t10")
        ]

    # SEPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES
    col_gauche_globale, col_droite_globale = st.columns(2)

    # ---------------------------------------------------------------------
    # COLONNE GAUCHE (PAGES 1 ET 3 : CONTEXTE ET QUIZ TECHNIQUE)
    # ---------------------------------------------------------------------
    with col_gauche_globale:
        # PAGE 1 : CONTEXTE HISTORIQUE DU BAROMÈTRE
        st.subheader("La Galerie des Génies : L'Équilibre des Pressions")
        st.markdown("""
        <div class="bandeau-pression">
            <b>Repères Historiques :</b> En 1648, Florin Périer réalise sur les conseils de Blaise Pascal l'expérience scientifique du Puy de Dôme. Il prouve de manière définitive que la hauteur de la colonne de mercure dépend de l'altitude, validant l'existence du poids de l'air.
        </div>
        """, unsafe_allow_html=True)

        sub_col_hist1, sub_col_hist2 = st.columns(2)
        with sub_col_hist1:
            if os.path.exists("Pascal.jpg"):
                st.image("Pascal.jpg", caption="Blaise Pascal (1623 - 1662)", use_container_width=True)
            else:
                st.caption("Illustration Pascal manquante")
        with sub_col_hist2:
            if os.path.exists("pressionatmos.jpg"):
                st.image("pressionatmos.jpg", caption="Expérimentation barométrique", use_container_width=True)
            else:
                st.caption("Illustration de contexte manquante")

        st.markdown("<br>", unsafe_allow_html=True)

        # PAGE 3 : QUIZ TECHNIQUE DE LA PRESSION
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_pres3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"pres_at3_final_g_{q_data['id']}_{idx}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    # ---------------------------------------------------------------------
    # COLONNE DROITE (PAGES 2 ET 4 : SYNTHÈSE DE COURS À TROUS INDEXÉE)
    # ---------------------------------------------------------------------
    with col_droite_globale:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for idx, ligne in enumerate(st.session_state.champs_pres3_clean, 1):
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_pres3_clean_{idx}", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )


def afficher_atelier_forces(verrouille=False):
    import random

    # Déclaration de la base de données des 10 questions du Quiz des Forces
    questions_forces_sources = [
        {"id": "qf1", "q": "Quelle est l'unité légale de mesure d'une force dans le Système International ?", "options": ["Le Pascal", "Le Newton", "Le Joule"], "rep": "Le Newton"},
        {"id": "qf2", "q": "Quel instrument de mesure utilise-t-on couramment en laboratoire pour mesurer l'intensité d'une force ?", "options": ["Un manomètre", "Un dynamomètre", "Un baromètre"], "rep": "Un dynamomètre"},
        {"id": "qf3", "q": "Par quel objet mathématique représente-t-on graphiquement une force physique ?", "options": ["Une droite infinie", "Un vecteur (une flèche)", "Une courbe sinusoïdale"], "rep": "Un vecteur (une flèche)"},
        {"id": "qf4", "q": "Laquelle de ces options ne constitue PAS une caractéristique essentielle d'un vecteur force ?", "options": ["Le point d'application", "La couleur de la flèche", "La direction et le sens"], "rep": "La couleur de la flèche"},
        {"id": "qf5", "q": "Quelle force attire tous les objets massifs vers le centre de la Terre ?", "options": ["La force magnétique", "La force de gravitation (le poids)", "La force d'Archimède"], "rep": "La force de gravitation (le poids)"},
        {"id": "qf6", "q": "Comment qualifie-t-on une force qui s'exerce sans qu'il n'y ait de contact direct entre les objets ?", "options": ["Une force de contact", "Une force à distance", "Une force hydraulique"], "rep": "Une force à distance"},
        {"id": "qf7", "q": "La force pressante exercée par un liquide sur une paroi solide est toujours :", "options": ["Parallèle à la paroi", "Perpendiculaire à la paroi", "Oblique par rapport à la paroi"], "rep": "Perpendiculaire à la paroi"},
        {"id": "qf8", "q": "Si un solide reste parfaitement immobile au repos, que peut-on dire des forces qui s'appliquent sur lui ?", "options": ["Aucune force ne s'applique", "Les forces se compensent (équilibre)", "La force du poids est nulle"], "rep": "Les forces se compensent (équilibre)"},
        {"id": "qf9", "q": "Dans la formule P = F / S, si la force F double sur une même surface, la pression P :", "options": ["Reste la même", "Double", "Est divisée par deux"], "rep": "Double"},
        {"id": "qf10", "q": "Sur la Lune, la force du poids d'un astronaute est plus faible que sur Terre car :", "options": ["Sa masse a diminué", "La gravité lunaire est plus faible", "L'atmosphère y est absente"], "rep": "La gravité lunaire est plus faible"}
    ]

    # Déclaration de la base de données de la Synthèse (Texte à trous)
    trous_forces_sources = [
        ("1. Une action mécanique capable de modifier le mouvement est une ..........", ["Choisir...", "force", "surface"], "force", "forc_t1"),
        ("2. L'intensité d'une force s'exprime en Newtons, de symbole ..........", ["Choisir...", "N", "Pa"], "N", "forc_t2"),
        ("3. Le dynamomètre mesure les forces grâce à la déformation d'un ..........", ["Choisir...", "ressort", "piston"], "ressort", "forc_t3"),
        ("4. La droite selon laquelle s'exerce une force est appelée sa ..........", ["Choisir...", "direction", "intensité"], "direction", "forc_t4"),
        ("5. Le point de la paroi où commence le vecteur d'action est le point d'..........", ["Choisir...", "application", "équilibre"], "application", "forc_t5"),
        ("6. L'attraction gravitationnelle est une action mécanique s'exerçant à ..........", ["Choisir...", "distance", "contact"], "distance", "forc_t6"),
        ("7. La force pressante est proportionnelle à la grandeur de la ..........", ["Choisir...", "surface", "viscosité"], "surface", "forc_t7"),
        ("8. Deux forces de même direction, de sens opposés et de même intensité sont en ..........", ["Choisir...", "équilibre", "mouvement"], "équilibre", "forc_t8"),
        ("9. La longueur d'une flèche force est proportionnelle à son ..........", ["Choisir...", "intensité", "poids"], "intensité", "forc_t9"),
        ("10. La poussée d'un fluide s'exerce de manière normale, c'est-à-dire ..........", ["Choisir...", "perpendiculaire", "tangente"], "perpendiculaire", "forc_t10")
    ]

    if "ordre_quiz_forces_aleatoire" not in st.session_state:
        random.shuffle(questions_forces_sources)
        st.session_state.ordre_quiz_forces_aleatoire = questions_forces_sources

    if "champs_forces_clean" not in st.session_state:
        st.session_state.champs_forces_clean = trous_forces_sources

    # SÉPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES (MOTEUR BI-COLONNE)
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_forces_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"forc_at2_final_g_{q_data['id']}_{idx}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for idx, ligne in enumerate(st.session_state.champs_forces_clean, 1):
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_forces_clean_{idx}", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )


def afficher_atelier_histoire_pression(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page."""
    import random

    st.subheader("Atelier Interactif : Modélisation Mathématique de la Pression")

    questions_pression_sources = [
        {"id": "qp1", "q": "Dans la relation mathématique P = F / S, que représente la lettre P ?", "options": ["La Pression", "La Puissance", "Le Poids"], "rep": "La Pression"},
        {"id": "qp2", "q": "Dans la relation mathématique P = F / S, que représente la lettre F ?", "options": ["La Force pressante", "Le Fluide", "Le Frottement"], "rep": "La Force pressante"},
        {"id": "qp3", "q": "Dans la relation mathématique P = F / S, que représente la lettre S ?", "options": ["La Surface de contact", "La Section du cylindre", "Le Système international"], "rep": "La Surface de contact"},
        {"id": "qp4", "q": "Quelle est l'unité légale dans le système international pour mesurer la force (F) ?", "options": ["Le Newton (N)", "Le Kilogramme (kg)", "Le Pascal (Pa)"], "rep": "Le Newton (N)"},
        {"id": "qp5", "q": "Quelle est l'unité légale dans le système international pour mesurer la surface (S) ?", "options": ["Le mètre carré (m²)", "Le centimètre carré (cm²)", "Le litre (L)"], "rep": "Le mètre carré (m²)"},
        {"id": "qp6", "q": "Quelle unité de pression équivaut exactement à un Newton par mètre carré (1 N/m²) ?", "options": ["Le Pascal (Pa)", "Le Bar (bar)", "L'Atmosphère (atm)"], "rep": "Le Pascal (Pa)"},
        {"id": "qp7", "q": "Si la force reste identique mais que la surface de contact double, que devient la pression ?", "options": ["Elle est divisée par deux", "Elle double", "Elle reste inchangée"], "rep": "Elle est divisée par deux"},
        {"id": "qp8", "q": "Si la surface reste identique mais que la force pressante double, que devient la pression ?", "options": ["Elle double", "Elle est divisée par deux", "Elle est quadruplée"], "rep": "Elle double"},
        {"id": "qp9", "q": "Quelle expérience historique a démontré qu'une infime force sur une toute petite surface brisait des structures ?", "options": ["Le crève-tonneau de Pascal", "Le tube de Torricelli", "Les hémisphères de Magdebourg"], "rep": "Le crève-tonneau de Pascal"},
        {"id": "qp10", "q": "Quel fluide lourd Torricelli a-t-il utilisé pour valider la mesure de la force atmosphérique ?", "options": ["Le mercure", "L'eau distillée", "L'huile de lin"], "rep": "Le mercure"}
    ]

    if "ordre_quiz_pression_aleatoire" not in st.session_state:
        random.shuffle(questions_pression_sources)
        st.session_state.ordre_quiz_pression_aleatoire = questions_pression_sources

    if "champs_pression_clean" not in st.session_state:
        st.session_state.champs_pression_clean = [
            ("1. La pression est définie comme le rapport d'une force sur une ..........", ["Choisir...", "surface", "hauteur"], "surface", "pres_t1"),
            ("2. L'unité de mesure de la force pressante est le ..........", ["Choisir...", "Newton", "Pascal"], "Newton", "pres_t2"),
            ("3. Pour calculer la pression en Pascals, la surface doit être exprimée en ..........", ["Choisir...", "mètre carré", "centimètre carré"], "mètre carré", "pres_t3"),
            ("4. À force égale, plus la surface diminue, plus la pression ..........", ["Choisir...", "augmente", "diminue"], "augmente", "pres_t4"),
            ("5. À surface égale, la pression est directement proportionnelle à la ..........", ["Choisir...", "force", "masse"], "force", "pres_t5"),
            ("6. Le physicien qui a laissé son nom à l'unité de pression est Blaise ..........", ["Choisir...", "Pascal", "Torricelli"], "Pascal", "pres_t6"),
            ("7. La force exercée par un fluide sur une paroi est toujours .......... à celle-ci.", ["Choisir...", "perpendiculaire", "parallèle"], "perpendiculaire", "pres_t7"),
            ("8. L'appareil inventé par Torricelli pour évaluer la force de l'atmosphère est le ..........", ["Choisir...", "baromètre", "manomètre"], "baromètre", "pres_t8"),
            ("9. Un fluide comme l'eau transmet intégralement les forces car il est ..........", ["Choisir...", "incompressible", "extensible"], "incompressible", "pres_t9"),
            ("10. 1 bar est une unité usuelle qui correspond à cent mille ..........", ["Choisir...", "Pascals", "Newtons"], "Pascals", "pres_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_pression_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"pres_at1_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_pression_clean:
            # Extraction correcte par index du tuple pour éviter les erreurs d'affectation
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_pres_clean", disabled=verrouille, label_visibility="collapsed")

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
    st.header("L'Histoire de la Pression et de l'Hydraulique")
    st.write("Découvrez les grands esprits qui ont marqué l'histoire de la physique, suivis d'une courte aventure humoristique.")

    # -------------------------------------------------------------------------
    # PARTIE 1 : LES GRANDS PERSONNAGES SCIENTIFIQUES (P = F / S)
    # -------------------------------------------------------------------------
    st.subheader("La Galerie des Génies")
    
    col_pascal, col_torricelli = st.columns(2)
    
    with col_pascal:
        st.markdown("### Blaise Pascal (1623 - 1662)")
        if os.path.exists("Pascal.jpg"):
            st.image("Pascal.jpg", caption="Blaise Pascal", use_container_width=True)
        else:
            st.warning("Fichier 'Pascal.jpg' absent du serveur.")

        st.markdown("""
        * **Sa Trouvaille :** La formulation de la pression comme le rapport d'une force sur une surface (**P = F / S**). Il démontre qu'une même force répartie sur une surface plus petite engendre une pression bien plus élevée.
        * **L'Expérience Célèbre :** *Le crève-tonneau de Pascal (1646)*. En appliquant le poids d'un faible volume d'eau (Force) au sommet d'un long tube de très fine section (Surface minuscule), il génère une pression hydrostatique immense capable de faire éclater le bois.
        """)
        if os.path.exists("crevetonneau.jpg"):
            st.image("crevetonneau.jpg", caption="Le crève-tonneau de Pascal", use_container_width=True)
        else:
            st.warning("Fichier 'crevetonneau.jpg' absent du serveur.")

    with col_torricelli:
        st.markdown("### Evangelista Torricelli (1608 - 1647)")
        if os.path.exists("Torricelli.jpg"):
            st.image("Torricelli.jpg", caption="Evangelista Torricelli", use_container_width=True)
        else:
            st.warning("Fichier 'Torricelli.jpg' absent du serveur.")
       
        st.markdown("""
        * **Sa Trouvaille :** La mesure de la force pressante de l'air. Il est le premier à quantifier la force colossale exercée par le poids de l'atmosphère sur chaque unité de surface terrestre.
        * **L'Expérience Célèbre :** *Le tube de Torricelli (1643)*. Il équilibre la force du poids de l'atmosphère s'exerçant sur la surface d'un bassin avec le poids d'une colonne de mercure de 76 centimètres de hauteur.
        """)
        if os.path.exists("pressionatmos.jpg"):
            st.image("pressionatmos.jpg", caption="Expérience de Torricelli", use_container_width=True)
        else:
            st.warning("Fichier 'pressionatmos.jpg' absent du serveur.")

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # PARTIE 2 : BANDE DESSINÉE RESTRUCTURÉE (0.3 GAUCHE TEXTES, 0.7 DROITE IMAGES)
    # -------------------------------------------------------------------------
    st.subheader("Bande Dessinée : Le Choc des Fluides")
    st.write("Une histoire imaginaire pour comprendre leurs discussions scientifiques.")

    st.markdown("""
    <style>
    .bulles { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px; }
    .narrateur { font-style: italic; color: #555555; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

    col_bd_texte, col_bd_image = st.columns([0.3, 0.7])

    with col_bd_texte:
        st.markdown("##### Enoncé de l'exercice et contexte")
        
        enonce_histoire = (
            "**Case 1 : À la taverne de la Science (Paris, 1648)**\n\n"
            "Pascal et Torricelli s'installent à une table. Torricelli pose un lourd tube de mercure sur le comptoir, l'air fatigué : "
            "« Mon cher Blaise, j'ai mal au dos... L'air pèse des tonnes aujourd'hui ! Les gens croient que la nature a horreur du vide, mais c'est faux, c'est juste l'atmosphère qui applique sa force sur chaque unité de surface terrestre ! ».\n\n"
            "**Case 2 : L'illumination de Pascal**\n\n"
            "Pascal regarde son verre, prend une paille, et tape du poing sur la table : "
            "« Tu as raison Evangelista ! Et regarde ça : la pression dépend directement du rapport P = F / S. Si j'appuie sur mon verre ici, la pression pushes le liquide partout en même temps ! C'est comme cela que j'ai brisé mon tonneau ! ».\n\n"
            "**Case 3 : La panique au laboratoire**\n\n"
            "Le serveur de la taverne recule, inquiet des théories des deux physiciens et des formules mathématiques : "
            "« Messieurs, calmez-vous avec vos calculs de force et de surface. Vous voulez régler l'addition ou vous allez aussi faire éclater ma cave avec votre relation P = F / S ? »"
        )
        st.info(enonce_histoire)

        texte_bd_bleu_h = (
            "**La BD humoristique : Le Choc des Fluides**\n\n"
            "**Case 1 :** Torricelli : « L'atmosphère applique sa force invisible partout sur nos têtes ! ».\n\n"
            "**Case 2 :** Pascal : « La force pressante agit de manière perpendiculaire sur l'aire du récepteur ! ».\n\n"
            "**Case 3 :** Le Serveur : « Moins de physique des fluides et plus de sous pour régler la table ! ».\n\n"
            "**Case 4 :** En chœur : « C'est pour l'avancement de la Science ! »"
        )
        st.info(texte_bd_bleu_h)

    with col_bd_image:
        st.markdown("##### Illustration caricaturale du cas")
        
        # 1. Affichage de la première image réelle du cas (Largeur fixe 300px)
        if os.path.exists("histoire_pression_reelle.jpg"):
            st.image("histoire_pression_reelle.jpg", caption="Image réelle : Documents historiques d'époque", width=300)
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour descendre la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Affichage de la caricature de bande dessinée (Largeur fixe 300px)
        if os.path.exists("bd_choc_fluides.jpg"):
            st.image("bd_choc_fluides.jpg", caption="Caricature de l'incident historique", width=300)
        else:
            st.caption("Caricature de l'incident historique")

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
    # -------------------------------------------------------------------------
    if "suite_verrouille_tab1_pression" not in st.session_state:
        st.session_state.suite_verrouille_tab1_pression = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_pression

    # Rendu des questionnaires d'évaluation de l'Atelier 1
    afficher_atelier_histoire_pression(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique sur la relation P = F / S.",
        key="check_certif_pres1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_pres_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q1 = 0.0
            if "ordre_quiz_pression_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_pression_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"pres_at1_final_g_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t1 = 0.0
            if "champs_pression_clean" in st.session_state:
                for ligne in st.session_state.champs_pression_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_pression_clean_"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t1 += 1.0

            st.session_state.score_suite1_pres_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_pres_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_pres = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_pression = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab1_pression", False):
        from datetime import datetime
        scr1_t1 = st.session_state.get("score_suite1_pres_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_pres_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_pres", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_pres1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Pression - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 1 : Fondements Historiques de la relation Pression-Force-Surface</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Historique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_pression_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_pression_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"pres_at1_final_g_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pres1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_pres1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_pression_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pression_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_pression_clean_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pres1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_pres1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pres1 = preparer_nom_fichier("Rapport_Atelier_1_Histoire").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 1 (.HTML)",
            data=html_export_pres1,
            file_name=nom_fichier_html_pres1,
            mime="text/html",
            use_container_width=True,
        )





        
        
with tab2:
    st.header("Étude des Forces Physiques et Pressantes")
    st.write("Explorez les fondements mécaniques des actions réciproques, manipulez les vecteurs, puis complétez l'évaluation de l'Atelier 2.")

    st.markdown("""
    <style>
    .legende-forces { color: #2563eb; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-forces { background-color: #e0f2fe; border-left: 5px solid #0284c7; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #1e3a8a; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # =============================================================================
    # 2. RENDU ASYMÉTRIQUE DU COURS ET DES IMAGES [0.3 GAUCHE, 0.7 DROITE]
    # =============================================================================
    col_gauche_bd_forces, col_droite_cours_forces = st.columns([0.3, 0.7])

    with col_gauche_bd_forces:
        st.markdown("##### Enoncé de l'exercice et contexte")
        enonce_forces = (
            "**Case 1 : Le défi du laboratoire.** Un opérateur cherche à déplacer une lourde charge solide au repos : "
            "« Sans action mécanique extérieure, la masse reste immobile, le vecteur force motrice appliqué doit contrer la résistance ! ».\n\n"
            "**Case 2 : L'équilibrage des forces.** Le dynamomètre à ressort étalonné affiche une déformation linéaire stable : "
            "« À 100 Newtons d'intensité, le système trouve sa position d'équilibre, la somme vectorielle des forces opposées s'annule ! ».\n\n"
            "**Case 3 : La force pressante.** Le fluide interne ést mis sous contrainte mécanique par une face plane : "
            "« C'est mathématique, la poussée du fluide s'exerce de manière normale, c'est-à-dire perpendiculaire à l'aire de la paroi ! »."
        )
        st.info(enonce_forces)

        texte_bd_bleu_f = (
            "**La BD humoristique : Le Vecteur Fou du Laboratoire**\n\n"
            "**Case 1 :** Galilée : « Sans frottement, un corps lancé poursuit sa trajectoire en ligne droite à l'infini ! ».\n\n"
            "**Case 2 :** Newton : « Toute modification du mouvement traduit l'action d'un vecteur force net non nul ! ».\n\n"
            "**Case 3 :** Le Technicien : « Attention à l'intensité sur le manomètre, la force pressante va arracher la jante ! ».\n\n"
            "**Case 4 :** Résolution : « Forces équilibrées, structures stabilisées, le laboratoire est hors de danger ! »"
        )
        st.info(texte_bd_bleu_f)

    with col_droite_cours_forces:
        st.markdown("##### Illustration caricaturale du cas")
        # 1. Affichage supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists("mecanique_forces_reelle.jpg"):
            st.image("mecanique_forces_reelle.jpg", caption="Image réelle : Banc de traction et dynamomètre", width=300)
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour repousser la caricature vers le bas
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists("bd_mecanique_forces.jpg"):
            st.image("bd_mecanique_forces.jpg", caption="Caricature de l'incident mécanique vectoriel", width=300)
        else:
            st.caption("Caricature de l'incident mécanique vectoriel")

    st.markdown("---")

    st.subheader("Laboratoire Virtuel : Simulateur interactif de vecteurs force")
    
    col_p1_f2, col_p2_f2 = st.columns(2)
    with col_p1_f2:
        valeur_force = st.slider("Ajuster l'intensité de la Force Motrice (en Newtons) :", min_value=0, max_value=200, value=100, step=10, key="slider_force_motrice_at2_officiel")
    
    with col_p2_f2:
        if valeur_force == 100:
            st.info("État du système : Les forces opposées se compensent (100 N). Le système est en équilibre mécanique.")
        elif valeur_force > 100:
            st.warning(f"État du système : Rupture d'équilibre. La force motrice ({valeur_force} N) surpasse la résistance.")
        else:
            st.error(f"État du système : Force motrice insuffisante ({valeur_force} N). La charge reste immobile.")

    st.write("---")

    # =============================================================================
    # 4. APPEL OPÉRATIONNEL DE L'ÉVALUATION COMPOSÉE COMPATIBLE
    # =============================================================================
    if "suite_verrouille_tab2_forces" not in st.session_state:
        st.session_state.suite_verrouille_tab2_forces = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_forces

    # Rendu des formulaires Quiz + Trous indexés de sécurité
    afficher_atelier_forces(verrouille=verrou_at2)

    # =============================================================================
    # 5. SYSTÈME DE CORRECTION SUR 20 ET PROTOCOLE D'EXPORTATION HTML SCELLÉE
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions d'évaluation sur l'Étude des Forces Physiques.",
        key="check_certif_forces2_final_official",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_forces_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identity dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz par parcours sécurisé
            score_q2 = 0.0
            if "ordre_quiz_forces_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_forces_aleatoire, 1):
                    saisie = st.session_state.get(f"forc_at2_final_g_{q_item['id']}_{idx}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q2 += 1.0

            # 2. Correction automatique du Texte à trous par parcours sécurisé
            score_t2 = 0.0
            if "champs_forces_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_forces_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = st.session_state.get(f"{cle}_forces_clean_{idx}", "Choisir...")
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t2 += 1.0

            st.session_state.score_suite2_forces_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_forces_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_forces = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_forces = True
            st.rerun()

    # =============================================================================
    # 6. COMPILATION DU BILAN HTML DE L'ATELIER 2 SCELLÉ
    # =============================================================================
    if st.session_state.get("suite_verrouille_tab2_forces", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_forces_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_forces_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_forces", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FORCES ET VECTEURS SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_forces2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport d'Application Forces - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 2 : Étude des Forces Physiques, Modélisation Vectorielle et Actions Fluides</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_forces_aleatoire" in st.session_state:
            for idx, q_item in enumerate(st.session_state.ordre_quiz_forces_aleatoire, 1):
                saisie = st.session_state.get(f"forc_at2_final_g_{q_item['id']}_{idx}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_forces2 += f"<tr><td>{idx}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_forces2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_forces_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_forces_clean, 1):
                enonce_texte, choix_texte, attendu_texte, cle_variable = ligne
                saisie_texte = st.session_state.get(f"{cle_variable}_forces_clean_{idx}", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_forces2 += f"<tr><td>{idx}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_forces2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_forces2 = preparer_nom_fichier("Rapport_Atelier_2_Forces").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 2 (.HTML)",
            data=html_export_forces2,
            file_name=nom_fichier_html_forces2,
            mime="text/html",
            use_container_width=True,
        )







with tab3:
    st.header("Étude de la Pression et des Phénomènes Barométriques")
    st.write("Explorez les lois régissant l'équilibre des pressions fluides, manipulez les paramètres manométriques, puis complétez l'évaluation de l'Atelier 3.")

    # Styles CSS pour les légendes, bandeaux et textes spécifiques à l'Atelier 3
    st.markdown("""
    <style>
    .legende-pression { color: #059669; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-pression { background-color: #ecfdf5; border-left: 5px solid #10b981; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #065f46; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # =============================================================================
    # 1. RENDU ASYMÉTRIQUE DU COURS ET DES IMAGES [0.3 GAUCHE, 0.7 DROITE]
    # =============================================================================
    col_gauche_bd_pres, col_droite_cours_pres = st.columns([0.3, 0.7])

    with col_gauche_bd_pres:
        st.markdown("##### Enoncé de l'exercice et contexte")
        st.info(
            "**La Galerie des Génies : L'Équilibre des Pressions**\n\n"
            "En 1648, Florin Périer réalise sur les conseils de Blaise Pascal l'expérience scientifique du Puy de Dôme. Il prouve de manière définitive que la hauteur de la colonne de mercure dépend de l'altitude, validant l'existence du poids de l'air.\n\n"
            "**Observations Hydrostatiques (Les Vases Communicants) :**\n\n"
            "**Case 1 :** Plusieurs réservoirs de formes et de sections totalement différentes sont reliés à leur base.\n\n"
            "**Case 2 :** Lorsque l'on verse le liquide, les molécules se répartissent librement d'un contenant à un autre.\n\n"
            "**Case 3 :** À l'équilibre, la hauteur du fluide atteint strictement le même niveau horizontal dans chaque colonne.\n\n"
            "**Case 4 :** Ce phénomène confirme que la pression en un point ne dépend pas du volume de fluide mais uniquement de la profondeur."
        )

        texte_bd_bleu_p3 = (
            "**La BD humoristique : Le Mystère de la Colonne de Mercure**\n\n"
            "**Case 1 :** Torricelli : « Plus on monte haut sur la montagne, moins le poids de l'atmosphère pèse sur notre bassin ! ».\n\n"
            "**Case 2 :** Pascal : « C'est l'expérience du Puy de Dôme ! Le vide s'agrandit dans le tube car l'air se raréfie ! ».\n\n"
            "**Case 3 :** Le Serveur : « Peu importe la géométrie ou la section de vos verres, le niveau se stabilise toujours à l'horizontale ! ».\n\n"
            "**Case 4 :** En chœur : « C'est la loi des vases communicants, l'équilibre hydrostatique parfait ! »"
        )
        st.info(texte_bd_bleu_p3)

    with col_droite_cours_pres:
        st.markdown("##### Illustration caricaturale du cas")
        # 1. Affichage supérieur : Image réelle du baromètre (Largeur fixe 300px)
        if os.path.exists("pression_reelle_contexte.jpg"):
            st.image("pression_reelle_contexte.jpg", caption="Image réelle : Dispositif de mesure barométrique d'époque", width=300)
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour repousser la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature des vases communicants (Largeur fixe 300px)
        if os.path.exists("bd_vases_communicants.jpg"):
            st.image("bd_vases_communicants.jpg", caption="Caricature de l'équilibre hydrostatique", width=300)
        else:
            st.caption("Caricature de l'équilibre hydrostatique")

    st.markdown("---")

    # =============================================================================
    # 2. SIMULATEUR INTERACTIF DE PRESSION HYDROSTATIQUE
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de Pression Hydrostatique (P = rho * g * h)")
    
    if "suite_verrouille_tab3_pression" not in st.session_state:
        st.session_state.suite_verrouille_tab3_pression = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_pression

    col_p1_p3, col_p2_p3 = st.columns(2)
    with col_p1_p3:
        hauteur_fluide = st.slider("Ajuster la profondeur de mesure dans la cuve (en mètres) :", min_value=0.0, max_value=10.0, value=5.0, step=0.5, disabled=verrou_at3, key="slider_profondeur_cuve_at3")
    
    with col_p2_p3:
        # Calcul théorique simplifié de la pression hydrostatique (pression = rho * g * h avec rho=1000 et g=9.81)
        pression_calculee_bar = (1000 * 9.81 * hauteur_fluide) / 100000
        st.metric(label="Pression relative mesurée au manomètre", value=f"{pression_calculee_bar:.3f} bar")
        formule_hydro = rf"P = \rho \cdot g \cdot h = 1000 \cdot 9{{,}}81 \cdot {hauteur_fluide} = {1000 * 9.81 * hauteur_fluide:,.0f}\text{{ Pa}}"
        st.latex(formule_hydro)

    st.write("---")

    # =============================================================================
    # 3. RENDU DES FORMULAIRES D'ÉVALUATION COMPOSÉS ET COMPATIBLES (BI-COLONNE)
    # =============================================================================
    col_gauche_globale, col_droite_globale = st.columns(2)

    with col_gauche_globale:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_pres3_aleatoire" in st.session_state:
            for idx, q_data in enumerate(st.session_state.ordre_quiz_pres3_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox(
                    "", 
                    options=["Choisir..."] + q_data["options"], 
                    key=f"pres3_at3_final_g_{q_data['id']}_{idx}", 
                    disabled=verrou_at3, 
                    label_visibility="collapsed"
                )

    with col_droite_globale:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        if "champs_pres3_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_pres3_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox(
                        "", 
                        choix, 
                        key=f"{cle}_pres3_clean_{idx}", 
                        disabled=verrou_at3, 
                        label_visibility="collapsed"
                    )

    # =============================================================================
    # 4. MOTEUR DE NOTATION AUTOMATIQUE SUR 20 ET EXPORTATION HTML SCELLÉE
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier d'Étude de la Pression.",
        key="check_certif_pres3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_pres_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatique du Quiz par parcours sécurisé
            score_q3 = 0.0
            if "ordre_quiz_pres3_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_pres3_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"pres_at3_final_g_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # Correction automatique du Texte à trous par parcours sécurisé
            score_t3 = 0.0
            if "champs_pres3_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_pres3_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle}_pres3_clean_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_pres_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_pres_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_pres = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_pression = True
            st.rerun()

    # --- ENCAPSULATION DU RAPPORT ELECTRONIQUE HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab3_pression", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_pres_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_pres_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_pres", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PRESSION SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_pres3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport d'Étude de la Pression - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0284c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 3 : Étude Expérimentale de la Pression Hydrostatique et Loi des Fluides</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_pres3_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_pres3_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"pres3_at3_final_g_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pres3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_pres3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_pres3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_pres3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_pres3_clean_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pres3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_pres3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pres3 = preparer_nom_fichier("Rapport_Atelier_3_Pression").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 3 (.HTML)",
            data=html_export_pres3,
            file_name=nom_fichier_html_pres3,
            mime="text/html",
            use_container_width=True,
        )



        

with tab4:
    st.header("Étude des Surfaces de Contact et Sections Géométriques")
    st.write("Explorez l'impact du dimensionnement des surfaces sur la transmission des efforts, manipulez le simulateur géométrique, puis complétez l'évaluation de l'Atelier 4.")

    # Styles CSS pour les légendes, bandeaux et textes spécifiques à l'Atelier 4
    st.markdown("""
    <style>
    .legende-surface { color: #b45309; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-surface { background-color: #fffbeb; border-left: 5px solid #f59e0b; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #78350f; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    if "suite_verrouille_tab4_surface" not in st.session_state:
        st.session_state.suite_verrouille_tab4_surface = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_surface

    # =============================================================================
    # 1. RENDU ASYMÉTRIQUE DU COURS ET DES IMAGES [0.3 GAUCHE, 0.7 DROITE]
    # =============================================================================
    col_gauche_bd_surf, col_droite_cours_surf = st.columns([0.3, 0.7])

    with col_gauche_bd_surf:
        st.markdown("##### Enoncé de l'exercice et contexte")
        st.info(
            "**La Galerie des Génies : La Mesure des Aires**\n\n"
            "Dès l'Antiquité, Archimède de Syracuse développe la méthode d'exhaustion pour encadrer précisément la valeur de Pi et calculer l'aire du disque. Cette maîtrise géométrique s'avérera indispensable des siècles plus tard pour concevoir les pistons des premières machines hydrauliques.\n\n"
            "**Observations Techniques (Le Paradoxe des Raquettes à Neige) :**\n\n"
            "**Case 1 :** Un randonneur équipé de bottes classiques s'enfonce profondément au premier pas dans la neige poudreuse.\n\n"
            "**Case 2 :** Son poids (Force) se concentre sur la faible section de ses semelles, créant une forte pression locale.\n\n"
            "**Case 3 :** Il chausse des raquettes de grande section. La force de son poids reste rigoureusement inchangée.\n\n"
            "**Case 4 :** En multipliant la surface d'appui par dix, la pression s'effondre. Il marche à la surface sans s'enfoncer."
        )

        texte_bd_bleu_s4 = (
            "**La BD humoristique : Le Paradoxe des Raquettes à Neige**\n\n"
            "**Case 1 :** Randonneur : « Je m'enfonce jusqu'aux genoux ! La neige ne porte rien du tout aujourd'hui ! ».\n\n"
            "**Case 2 :** Archimède : « C'est une simple question de répartition ! Ta force pressante est concentrée sur une aire trop restreinte ! ».\n\n"
            "**Case 3 :** Pascal : « Chausse ces raquettes ! Ta surface d'appui va décupler, forçant la pression P à s'effondrer instantanément ! ».\n\n"
            "**Case 4 :** Randonneur : « Miracle ! Je flotte sur la poudreuse alors que mon poids lourd n'a pas bougé d'un Newton ! »"
        )
        st.info(texte_bd_bleu_s4)

    with col_droite_cours_surf:
        st.markdown("##### Illustration caricaturale du cas")
        # 1. Affichage supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists("geometrie_surface_reelle.jpg"):
            st.image("geometrie_surface_reelle.jpg", caption="Image réelle : Vérification de la surface géométrique d'un support mécanique", width=300)
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour repousser la caricature vers le bas
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists("bd_calcul_surfaces.jpg"):
            st.image("bd_calcul_surfaces.jpg", caption="Caricature de la répartition des pressions surfaciques", width=300)
        else:
            st.caption("Caricature de la répartition des pressions surfaciques")

    st.markdown("---")

    # =============================================================================
    # 2. SIMULATEUR INTERACTIF DE SECTION DE VÉRIN
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de Dimensionnement de Surface Circulaire")
    
    col_p1_surf4, col_p2_surf4 = st.columns(2)
    with col_p1_surf4:
        diametre_mm = st.slider("Ajuster le diamètre utile du piston (en millimètres) :", min_value=10, max_value=200, value=50, step=5, disabled=verrou_at4, key="slider_diametre_piston_at4")
    
    with col_p2_surf4:
        # Calcul en mm² puis conversion en m²
        surface_mm2 = (math.pi * (diametre_mm ** 2)) / 4
        surface_m2 = surface_mm2 / 1_000_000
        st.metric(label="Surface d'appui utile calculée", value=f"{surface_mm2:.1f} mm²")
        st.info(f"Équivalence dans le Système International : {surface_m2:.6f} m².")

    st.write("---")

    # =============================================================================
    # 3. RENDU DES FORMULAIRES D'ÉVALUATION BI-COLONNES COMPATIBLES ET ENTIÈREMENT INDEXÉS
    # =============================================================================
    col_gauche_globale, col_droite_globale = st.columns(2)

    with col_gauche_globale:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        if "ordre_quiz_surf4_aleatoire" in st.session_state:
            for idx, q_data in enumerate(st.session_state.ordre_quiz_surf4_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox(
                    "", 
                    options=["Choisir..."] + q_data["options"], 
                    key=f"surf4_at4_final_g_{q_data['id']}_{idx}", 
                    disabled=verrou_at4, 
                    label_visibility="collapsed"
                )

    with col_droite_globale:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        if "champs_surf4_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_surf4_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox(
                        "", 
                        choix, 
                        key=f"{cle}_surf4_clean_{idx}", 
                        disabled=verrou_at4, 
                        label_visibility="collapsed"
                    )

    # =============================================================================
    # 4. MOTEUR DE NOTATION AUTOMATIQUE SUR 20 POINTS
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier d'Étude des Surfaces.",
        key="check_certif_surf4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_surf_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatique du Quiz par parcours sécurisé
            score_q4 = 0.0
            if "ordre_quiz_surf4_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_surf4_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"surf4_at4_final_g_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # Correction automatique du Texte à trous par parcours sécurisé
            score_t4 = 0.0
            if "champs_surf4_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_surf4_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle}_surf4_clean_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t4 += 1.0

            st.session_state.score_suite4_surf_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_surf_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_surf = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_surface = True
            st.rerun()

    # =============================================================================
    # 5. COMPILATION DU BILAN HTML DE L'ATELIER 4 SCELLÉ
    # =============================================================================
    if st.session_state.get("suite_verrouille_tab4_surface", False):

        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_surf_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_surf_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_surf", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER SURFACES SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_surf4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport d'Étude des Surfaces - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b45309; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 4 : Étude de l'impact des Sections Géométriques et Surfaces d'Appui</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_surf4_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_surf4_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"surf4_at4_final_g_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_surf4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_surf4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_surf4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_surf4_clean, 1):
                enonce_texte, choix_texte, attendu_texte, cle_variable = ligne
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_surf4_clean_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_surf4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_surf4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_surf4 = preparer_nom_fichier("Rapport_Atelier_4_Surface").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 4 (.HTML)",
            data=html_export_surf4,
            file_name=nom_fichier_html_surf4,
            mime="text/html",
            use_container_width=True,
        )


      

with tab5:
    st.header("Application professionnelle : Diagnostic et Maintenance")
    
    # 1. DÉCLARATION DE SÉCURITÉ ABSOLUE TOUT EN HAUT DE L'ONGLET
    if "suite_verrouille_tab5_maint" not in st.session_state:
        st.session_state.suite_verrouille_tab5_maint = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_maint
    
    if "cas_aleatoire_tab5" not in st.session_state:
        st.session_state.cas_aleatoire_tab5 = 1
    id_cas_maint = st.session_state.cas_aleatoire_tab5

    # --- CONFIGURATION DYNAMIQUE DES QUIZ ET DES TROUS SELON LE SCÉNARIO ---
    if id_cas_maint == 1:
        # CAS 1 : VÉRIN DE PRESSE HYDRAULIQUE
        questions_sources = [
            {"id": "qm1_c1", "q": "Quel appareil de mesure permet de valider la valeur de pression dans le circuit ?", "options": ["Un manomètre", "Un débitmètre", "Un thermomètre"], "rep": "Un manomètre"},
            {"id": "qm2_c1", "q": "Si l'huile contourne le piston à cause d'un joint usé, comment qualifie-t-on cette défaillance ?", "options": ["Une fuite interne", "Une fuite externe", "Une cavitation"], "rep": "Une fuite interne"},
            {"id": "qm3_c1", "q": "Dans la relation P = F / S, si l'huile fuit et la pression s'effondre, la force développée :", "options": ["Chute proportionnellement", "Reste maximale", "Augmente subitement"], "rep": "Chute proportionnellement"},
            {"id": "qm4_c1", "q": "Quelle unité normalisée est généralement lue sur le cadran d'un manomètre industriel ?", "options": ["Le bar", "Le Newton", "Le mètre par seconde"], "rep": "Le bar"},
            {"id": "qm5_c1", "q": "Pour augmenter la force d'une presse sans modifier sa pression de service, il faut :", "options": ["Augmenter la section du vérin", "Réduire le diamètre du piston", "Allonger la course"], "rep": "Augmenter la section du vérin"},
            {"id": "qm6_c1", "q": "Un fluide hydraulique industriel est utilisé dans les circuits car il est pratiquement :", "options": ["Incompressible", "Compressible", "Volatile"], "rep": "Incompressible"},
            {"id": "qm7_c1", "q": "La force pressante s'exerçant sur la face plane d'un piston de vérin agit toujours de façon :", "options": ["Perpendiculaire", "Parallèle", "Oblique"], "rep": "Perpendiculaire"},
            {"id": "qm8_c1", "q": "Quel risque présente une huile contenant des impuretés ou des particules métalliques ?", "options": ["Abrasion des joints de section", "Augmentation de la viscosité", "Chute de la gravité"], "rep": "Abrasion des joints de section"},
            {"id": "qm9_c1", "q": "Quelle opération préventive permet de limiter l'usure prématurée des composants hydrauliques ?", "options": ["La filtration périodique", "Le surtarage des valves", "L'augmentation du débit"], "rep": "La filtration périodique"},
            {"id": "qm10_c1", "q": "L'unité de pression du système international équivalente à 1 N/m² est :", "options": ["Le Pascal", "Le Bar", "Le Joule"], "rep": "Le Pascal"}
        ]
        trous_sources = [
            ("1. Un manque de force sur un actionneur traduit une perte de .......... hydraulique.", ["Choisir...", "pression", "vitesse"], "pression", "m5_t1_c1"),
            ("2. Le manomètre mesure l'effort réparti par le fluide sur l'unité de ..........", ["Choisir...", "surface", "longueur"], "surface", "m5_t2_c1"),
            ("3. Le contournement du piston par le fluide constitue une fuite ..........", ["Choisir...", "interne", "externe"], "interne", "m5_t3_c1"),
            ("4. La force pressante se déploie de manière orthogonale, donc .......... à la paroi.", ["Choisir...", "perpendiculaire", "tangente"], "perpendiculaire", "m5_t4_c1"),
            ("5. L'unité courante lue sur les cadrans des techniciens est le ..........", ["Choisir...", "bar", "Pascal"], "bar", "m5_t5_c1"),
            ("6. Pour restaurer l'étanchéité, il faut remplacer le .......... d'usure.", ["Choisir...", "joint", "piston"], "joint", "m5_t6_c1"),
            ("7. Un fluide sous pression transmet son action dans toutes les ..........", ["Choisir...", "directions", "lignes"], "directions", "m5_t7_c1"),
            ("8. L'huile de maintenance est choisie pour ses propriétés d'..........", ["Choisir...", "incompressibilité", "dilatation"], "incompressibilité", "m5_t8_c1"),
            ("9. Modifier l'aire de poussée modifie l'intensité du vecteur .......... développé.", ["Choisir...", "force", "vitesse"], "force", "m5_t9_c1"),
            ("10. Le maintien d'une pression stable garantit le bon fonctionnement mécanique de la ..........", ["Choisir...", "presse", "pompe"], "presse", "m5_t10_c1")
        ]

    elif id_cas_maint == 2:
        # CAS 2 : RUPTURE DE CANALISATION
        questions_sources = [
            {"id": "qm1_c2", "q": "Comment qualifie-t-on une onde de surpression brutale provoquée par la fermeture rapide d'une vanne ?", "options": ["Un coup de bélier", "Une cavitation", "Un effet Venturi"], "rep": "Un coup de bélier"},
            {"id": "qm2_c2", "q": "Quelle unité SI définit la contrainte mécanique maximale admissible par l'acier du tube ?", "options": ["Le Pascal (ou MPa)", "Le Newton", "Le Bar"], "rep": "Le Pascal (ou MPa)"},
            {"id": "qm3_c2", "q": "Pour dissiper les ondes de choc de pression dans un circuit, quel composant ajoute-t-on ?", "options": ["Un accumulateur hydropneumatique", "Une pompe de gavage", "Un limiteur de débit"], "rep": "Un accumulateur hydropneumatique"},
            {"id": "qm4_c2", "q": "La force de rupture appliquée sur la paroi du tube dépend de la pression et de :", "options": ["La surface intérieure exposée", "La longueur de la ligne", "La température ambiante"], "rep": "La surface intérieure exposée"},
            {"id": "qm5_c2", "q": "Une rupture par application répétée de contraintes inférieures à la limite élastique est appelée :", "options": ["Rupture par fatigue", "Rupture ductile", "Arrachement thermique"], "rep": "Rupture par fatigue"},
            {"id": "qm6_c2", "q": "Quelle formule de base lie l'épaisseur du tube à sa résistance à la pression ?", "options": ["La formule de Barlow", "La loi de Fourier", "Le principe d'Archimède"], "rep": "La formule de Barlow"},
            {"id": "qm7_c2", "q": "Si l'épaisseur de la paroi du tube est doublée, sa résistance à l'éclatement mécanique :", "options": ["Augmente nettement", "Diminue de moitié", "Reste parfaitement identique"], "rep": "Augmente nettement"},
            {"id": "qm8_c2", "q": "Les vibrations d'une tuyauterie mal fixée engendrent un phénomène d'usure par :", "options": ["Fatigue mécanique", "Laminage", "Sublimation"], "rep": "Fatigue mécanique"},
            {"id": "qm9_c2", "q": "En cas d'éclatement, le fluide s'échappe vers l'extérieur. C'est une fuite :", "options": ["Externe", "Interne", "Convective"], "rep": "Externe"},
            {"id": "qm10_c2", "q": "Quelle est l'équivalence d'une contrainte mécanique de 1 MégaPascal (MPa) en Pascals ?", "options": ["1 000 000 Pa", "1 000 Pa", "100 bars"], "rep": "1 000 000 Pa"}
        ]
        trous_sources = [
            ("1. La surpression transitoire maximale a provoqué l'.......... du tube d'acier.", ["Choisir...", "éclatement", "laminage"], "éclatement", "m5_t1_c2"),
            ("2. L'onde acoustique violente provoquée par une vanne fermée s'appelle coup de ..........", ["Choisir...", "bélier", "piston"], "bélier", "m5_t2_c2"),
            ("3. La contrainte de rupture du métal solide s'exprime rigoureusement en ..........", ["Choisir...", "Pascals", "Newtons"], "Pascals", "m5_t3_c2"),
            ("4. Le fluide sous pression s'échappe dans l'atelier, créant une fuite ..........", ["Choisir...", "externe", "interne"], "externe", "m5_t4_c2"),
            ("5. Les cycles de sollicitations répétées fatiguent la .......... de la canalisation.", ["Choisir...", "structure", "viscosité"], "structure", "m5_t5_c2"),
            ("6. Pour absorber les chocs de fluide, on installe un .......... amortisseur.", ["Choisir...", "accumulateur", "débitmètre"], "accumulateur", "m5_t6_c2"),
            ("7. L'effort d'éclatement est le produit de la pression par l'.......... interne projetée.", ["Choisir...", "aire", "longueur"], "aire", "m5_t7_c2"),
            ("8. Isoler le tronçon défaillant exige de fermer les .......... de sectionnement.", ["Choisir...", "vannes", "clapets"], "vannes", "m5_t8_c2"),
            ("9. Une conduite neuve munie d'une lyre flexible amortit les .......... parasites.", ["Choisir...", "vibrations", "températures"], "vibrations", "m5_t9_c2"),
            ("10. Ce diagnostic de défaillance structurelle assure la sécurité des .......... d'usinage.", ["Choisir...", "opérateurs", "fluides"], "opérateurs", "m5_t10_c2")
        ]

    elif id_cas_maint == 3:
        # CAS 3 : CAVITATION DANS LA POMPE
        questions_sources = [
            {"id": "qm1_c3", "q": "Où se forment principalement les micro-bulles de vapeur lors de la cavitation ?", "options": ["À l'aspiration (zone de basse pression)", "Au refoulement (haute pression)", "Dans le réservoir"], "rep": "À l'aspiration (zone de basse pression)"},
            {"id": "qm2_c3", "q": "La cavitation se produit lorsque la pression locale du liquide descend sous :", "options": ["Sa tension de vapeur saturante", "La pression de tarage", "Zéro absolu"], "rep": "Sa tension de vapeur saturante"},
            {"id": "qm3_c3", "q": "Quel bruit caractéristique indique qu'une pompe hydraulique subit de la cavitation ?", "options": ["Un crépitement métallique (bruit de graviers)", "Un sifflement aigu constant", "Un silence total"], "rep": "Un crépitement métallique (bruit de graviers)"},
            {"id": "qm4_c3", "q": "L'érosion des dents d'engrenages ou des aubes par cavitation découle de :", "options": ["L'implosion violente des micro-bulles", "La corrosion chimique pure", "Le frottement mécanique direct"], "rep": "L'implosion violente des micro-bulles"},
            {"id": "qm5_c3", "q": "Pour supprimer la cavitation à l'entrée d'une pompe, il faut impérativement :", "options": ["Augmenter la section du tube d'aspiration", "Réduire le diamètre d'entrée", "Augmenter la vitesse de rotation"], "rep": "Augmenter la section du tube d'aspiration"},
            {"id": "qm6_c3", "q": "Quelle modification physique subit le fluide lors de sa vaporisation locale dans la pompe ?", "options": ["Un changement d'état (liquide vers gaz)", "Une hausse de densité", "Une solidification"], "rep": "Un changement d'état (liquide vers gaz)"},
            {"id": "qm7_c3", "q": "Les micro-jets de liquide projetés lors de l'implosion détruisent le métal par :", "options": ["Fatigue mécanique de surface (piqûres)", "Fusion thermique", "Laminage fluide"], "rep": "Fatigue mécanique de surface (piqûres)"},
            {"id": "qm8_c3", "q": "Une restriction ou un colmatage du filtre d'aspiration a pour conséquence de :", "options": ["Faire chuter la pression d'entrée", "Augmenter le débit utile", "Stabiliser les vibrations"], "rep": "Faire chuter la pression d'entrée"},
            {"id": "qm9_c3", "q": "La chute de pression en dessous de la pression atmosphérique crée un vide :", "options": ["Relatif (ou dépression)", "Absolu parfait", "Hydrostatique stable"], "rep": "Relatif (ou dépression)"},
            {"id": "qm10_c3", "q": "À température ambiante, l'huile hydraulique peut bouillir si la pression devient :", "options": ["Extrêmement basse", "Supérieure à 200 bars", "Strictement constante"], "rep": "Extrêmement basse"}
        ]
        trous_sources = [
            ("1. Le phénomène de .......... érode prématurément le corps métallique de la pompe.", ["Choisir...", "cavitation", "laminage"], "cavitation", "m5_t1_c3"),
            ("2. Les bulles naissent car la pression locale descend sous la tension de ..........", ["Choisir...", "vapeur", "surface"], "vapeur", "m5_t2_c3"),
            ("3. Le retour en zone de haute pression provoque l'.......... brutale de ces bulles.", ["Choisir...", "implosion", "dilatation"], "implosion", "m5_t3_c3"),
            ("4. Les micro-jets de fluide frappent la surface active et créent des .......... profondes.", ["Choisir...", "piqûres", "fissures"], "piqûres", "m5_t4_c3"),
            ("5. Ce bombardement mécanique détruit l'acier par fatigue de ..........", ["Choisir...", "surface", "volume"], "surface", "m5_t5_c3"),
            ("6. Le crépitement sonore de l'aspiration évoque un transfert de ..........", ["Choisir...", "graviers", "vapeur"], "graviers", "m5_t6_c3"),
            ("7. Élargir le conduit d'entrée permet de réduire la .......... du fluide.", ["Choisir...", "vitesse", "densité"], "vitesse", "m5_t7_c3"),
            ("8. Nettoyer la crépine empêche la formation d'une .......... d'entrée critique.", ["Choisir...", "dépression", "surpression"], "dépression", "m5_t8_c3"),
            ("9. Ramener le profil au-dessus du seuil critique stabilise le .......... de fluide.", ["Choisir...", "débit", "poids"], "débit", "m5_t9_c3"),
            ("10. Ce diagnostic prévient la destruction totale de l'actionneur .......... de l'usine.", ["Choisir...", "principal", "externe"], "principal", "m5_t10_c3")
        ]

    # =============================================================================
    # CAS 4 : LAMINAGE DU FLUIDE DANS LE LIMITEUR
    # =============================================================================
    else:
        questions_sources = [
            {"id": "qm1_c4", "q": "Comment appelle-t-on le passage forcé d'un fluide à grande vitesse à travers une section minuscule ?", "options": ["Le laminage", "La cavitation", "La conduction hydrostatique"], "rep": "Le laminage"},
            {"id": "qm2_c4", "q": "Lors d'un laminage permanent intense, en quelle forme d'énergie se convertit la puissance mécanique du fluide ?", "options": ["En énergie thermique (calories)", "En énergie potentielle", "En force pressante pure"], "rep": "En énergie thermique (calories)"},
            {"id": "qm3_c4", "q": "Quel est le symptôme direct mesurable sur le réservoir en cas de laminage continu au limiteur ?", "options": ["Une élévation continue de la température de l'huile", "Une baisse de la viscosité cinématique", "Une hausse immédiate du niveau"], "rep": "Une élévation continue de la température de l'huile"},
            {"id": "qm4_c4", "q": "Pourquoi un limiteur de pression bloqué ouvert empêche-t-il la presse d'atteindre sa force maximale ?", "options": ["Le débit fuit en continu directement au réservoir", "La viscosité augmente trop", "Le fluide devient compressible"], "rep": "Le débit fuit en continu directement au réservoir"},
            {"id": "qm5_c4", "q": "Le frottement visqueux des molécules d'huile lors du laminage génère une chaleur dite :", "options": ["Sensible", "Latente de fusion", "Chimique parasite"], "rep": "Sensible"},
            {"id": "qm6_c4", "q": "Quelle caractéristique physique de l'huile se dégrade fortement si sa température dépasse 85 °C ?", "options": ["Sa viscosité (le fluide devient trop fluide)", "Sa masse volumique", "Sa compressibilité"], "rep": "Sa viscosité (le fluide devient trop fluide)"},
            {"id": "qm7_c4", "q": "Le clapet du limiteur de pression s'ouvre normalement pour protéger le circuit contre :", "options": ["Les surpressions accidentelles", "Les chutes de débit", "Le gel de l'huile"], "rep": "Les surpressions accidentelles"},
            {"id": "qm8_c4", "q": "La friction thermique moléculaire au passage de l'étranglement relève d'un transfert par :", "options": ["Frottement visqueux mécanique", "Rayonnement direct", "Changement de phase"], "rep": "Frottement visqueux mécanique"},
            {"id": "qm9_c4", "q": "Pour stopper le laminage thermique parasite, le technicien doit procéder au :", "options": ["Nettoyage du tiroir et calibrage du ressort", "Remplacement de la pompe", "Surdimensionnement du moteur"], "rep": "Nettoyage du tiroir et calibrage du ressort"},
            {"id": "qm10_c4", "q": "L'indicateur visuel de la panne montre un retour massif et permanent de fluide vers :", "options": ["Le réservoir (ou bâche)", "Le vérin de compactage", "Le manomètre"], "rep": "Le réservoir (ou bâche)"}
        ]
        trous_sources = [
            ("1. Forcer l'huile à travers un orifice minuscule engendre un .......... intense.", ["Choisir...", "laminage", "éclatement"], "laminage", "m5_t1_c4"),
            ("2. Cette friction interne convertit instantanément la pression en .......... de frottement.", ["Choisir...", "calories", "Pascals"], "calories", "m5_t2_c4"),
            ("3. Le symptôme majeur mesuré en cuve est une élévation .......... continue.", ["Choisir...", "thermique", "statique"], "thermique", "m5_t3_c4"),
            ("4. L'énergie perdue correspond à une production parasite de chaleur .......... .", ["Choisir...", "sensible", "latente"], "sensible", "m5_t4_c4"),
            ("5. Le coupable identifié est le clapet du .......... de pression bloqué ouvert.", ["Choisir...", "limiteur", "débitmètre"], "limiteur", "m5_t5_c4"),
            ("6. Le fluide s'échappe en continu et retourne directement au .......... principal.", ["Choisir...", "réservoir", "piston"], "réservoir", "m5_t6_c4"),
            ("7. Une huile surchauffée perd son pouvoir lubrifiant car sa .......... s'effondre.", ["Choisir...", "viscosité", "densité"], "viscosité", "m5_t7_c4"),
            ("8. Pour résoudre l'anomalie, il faut démonter le .......... coulissant grippé.", ["Choisir...", "tiroir", "tube"], "tiroir", "m5_t8_c4"),
            ("9. Nettoyer et régler le ressort restaure la section d'.......... normale.", ["Choisir...", "fermeture", "laminage"], "fermeture", "m5_t9_c4"),
            ("10. Ce soin préventif stabilise la température de service de la .......... hydraulique.", ["Choisir...", "centrale", "pompe"], "centrale", "m5_t10_c4")
        ]

    # Enregistrement immédiat dans la session pour garantir la synchronisation
    st.session_state.ordre_quiz_tab5_maint_aleatoire = questions_sources
    st.session_state.champs_therm5_maint_clean = trous_sources
    if id_cas_maint == 1:
        titre_maint = "Défaut d'étanchéité du piston sur un vérin hydraulique de presse"
        enonce_maint = (
            "**Case 1 :** La presse hydraulique n'atteint plus sa force nominale de compactage lors des cycles de production.\n\n"
            "**Case 2 :** Le technicien connecte un manomètre en dérivation et constate une chute de pression en fin de course.\n\n"
            "**Case 3 :** Le diagnostic confirme un passage d'huile interne entre la chambre de travail et la chambre de retour.\n\n"
            "**Case 4 :** Après remplacement du joint composite de section, le profil de pression redevient conforme aux spécifications."
        )
        texte_bd_maint = (
            "**Bande Caricaturale de l'Incident : Défaut d'étanchéité du vérin**\n\n"
            "**Case 1 :** Perte de poussée : « On écrase la matière mais les Watts manquent, la force F plafonne ! ».\n\n"
            "**Case 2 :** Fuite interne : « L'huile s'échappe en douce à travers le piston défaillant vers le retour ! ».\n\n"
            "**Case 3 :** Chute de pression : « Le fluide s'égalise entre les deux chambres, la pression P s'effondre ! ».\n\n"
            "**Case 4 :** Résolution : « Nouveau joint scellé, l'étanchéité est parfaite, la presse retrouve ses performances ! »"
        )
    elif id_cas_maint == 2:
        titre_maint = "Rupture par fatigue d'une canalisation rigide de distribution"
        enonce_maint = (
            "**Case 1 :** Une canalisation en acier éclate brutalement lors d'une phase de surpression transitoire.\n\n"
            "**Case 2 :** L'équipe de maintenance balise la zone et isole le tronçon en fermant les vannes de sectionnement.\n\n"
            "**Case 3 :** L'expertise révèle une fragilisation du métal due à des vibrations répétées et des coups de bélier.\n\n"
            "**Case 4 :** Une nouvelle conduite avec lyre de dilatation et amortisseurs de pulsations est mise en service."
        )
        texte_bd_maint = (
            "**Bande Caricaturale de l'Incident : Éclatement de canalisation**\n\n"
            "**Case 1 :** Éclatement : « La surpression instantanée a dépassé la limite de rupture de l'enveloppe acier ! ».\n\n"
            "**Case 2 :** Isolation : « Fermeture immédiate des vannes, on stoppe le flux de fluide perdu ! ».\n\n"
            "**Case 3 :** Diagnostic : « Les ondes de choc répétées ont fatigué la structure interne de la matière solidifiée ! ».\n\n"
            "**Case 4 :** Réparation : « Nouvelle ligne posée avec lyre flexible, les coups de bélier sont maîtrisés ! »"
        )
    elif id_cas_maint == 3:
        titre_maint = "Cavitation destructive au corps d'aspiration d'une pompe principale"
        enonce_maint = (
            "**Case 1 :** La pompe principale émet un bruit de crépitement métallique intense évoquant un pompage de graviers.\n\n"
            "**Case 2 :** Les techniciens relèvent une chute irrégulière du débit de fluide conjuguée à de fortes vibrations de ligne.\n\n"
            "**Case 3 :** Le démontage du corps révèle une érosion par piqûres profondes sur les faces actives des engrenages.\n\n"
            "**Case 4 :** L'aspiration est nettoyée, la section d'entrée élargie pour ramener la dépression sous le seuil de tension de vapeur."
        )
        texte_bd_maint = (
            "**Bande Caricaturale de l'Incident : Phénomène de cavitation**\n\n"
            "**Case 1 :** Crépitement : « On dirait que la pompe avale des cailloux, l'implosion des micro-bulles fait rage ! ».\n\n"
            "**Case 2 :** Analyse : « La dépression d'entrée fait bouillir l'huile à température ambiante ! ».\n\n"
            "**Case 3 :** Constat : « Les micro-jets de fluide frappent le métal à haute vitesse, la surface s'érode ! ».\n\n"
            "**Case 4 :** Solution : « Section élargie, la vitesse diminue, la pression remonte au-dessus du point critique ! »"
        )
    else:
        titre_maint = "Surchauffe d'huile par laminage intense dans un limiteur de pression bloqué"
        enonce_maint = (
            "**Case 1 :** La centrale hydraulique subit une élévation thermique continue, l'huile franchit le seuil des 85 °C.\n\n"
            "**Case 2 :** L'indicateur visuel montre un retour massif et permanent de fluide vers le réservoir sans action mécanique.\n\n"
            "**Case 3 :** Le diagnostic confirme le blocage en position ouverte du clapet du limiteur de pression principal.\n\n"
            "**Case 4 :** Après nettoyage du tiroir et calibrage du ressort, le fluide cesse de laminer et la température se stabilise."
        )
        texte_bd_maint = (
            "**Bande Caricaturale de l'Incident : Laminage et surchauffe**\n\n"
            "**Case 1 :** Surchauffe : « L'huile est bouillante, l'énergie mécanique se transforme entièrement en calories ! ».\n\n"
            "**Case 2 :** Fuite permanente : « Le clapet refuse de se fermer, tout le débit repart au réservoir en continu ! ».\n\n"
            "**Case 3 :** Laminage : « Forcer le fluide à traverser une section minuscule génère une friction thermique intense ! ».\n\n"
            "**Case 4 :** Recalibrage : « Tiroir nettoyé, le clapet se ferme, l'huile retrouve sa circulation normale ! »"
        )

    # =============================================================================
    # RENDU ASYMÉTRIQUE DU COURS ET DES IMAGES [0.3 GAUCHE, 0.7 DROITE]
    # =============================================================================
    col_gauche_bd_maint, col_droite_cours_maint = st.columns([0.3, 0.7])

    with col_gauche_bd_maint:
        st.markdown(f"##### Dossier Technique : {titre_maint}")
        st.info(enonce_maint)
        st.info(texte_bd_maint)

    with col_droite_cours_maint:
        st.markdown("##### Illustration caricaturale du cas")
        import os
        
        # Détermination des fichiers images selon le cas actif
        if id_cas_maint == 1:
            fichier_reel_maint = "pressehydraulique.jpg"
            fichier_caricature_maint = "maint_verin.jpg"
        elif id_cas_maint == 2:
            fichier_reel_maint = "rupturecanalisation.jpg"
            fichier_caricature_maint = "maint_tube.jpg"
        elif id_cas_maint == 3:
            fichier_reel_maint = "cavitationpompe.jpg"
            fichier_caricature_maint = "maint_pompe.jpg"
        else:
            fichier_reel_maint = "laminagehuile.jpg"
            fichier_caricature_maint = "maint_laminage.jpg"

        # 1. Affichage supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists(fichier_reel_maint):
            st.image(fichier_reel_maint, caption="Image réelle : Constat en atelier", width=300)
        else:
            st.caption("Image réelle manquante")

        # Les 20 lignes d'espacement réglementaires pour repousser la caricature vers le bas
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature (Largeur fixe 300px)
        if os.path.exists(fichier_caricature_maint):
            st.image(fichier_caricature_maint, caption="Bande dessinée de l'incident", width=300)
        else:
            st.caption("Caricature manquante")
            
    st.write("---")

    # =============================================================================
    # LABORATOIRE VIRTUEL INTERACTIF (ATELIER 5)
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur d'effort et de pression sur piston")
    
    col_p1_m5, col_p2_m5 = st.columns(2)
    with col_p1_m5:
        diametre_piston_mm = st.slider("Diamètre du piston de la presse (mm) :", min_value=50, max_value=250, value=120, step=5, key="l5_maint_p1_new")
        pression_circuit_bar = st.slider("Pression lue au manomètre (bars) :", min_value=10, max_value=350, value=160, step=10, key="l5_maint_p2_new")
    
    # Calculs physiques précis : Aire en m², Pression en Pa, Force en N et kN
    rayon_m = (diametre_piston_mm / 2.0) / 1000.0
    surface_m2 = 3.14159265 * (rayon_m ** 2)
    pression_pa = pression_circuit_bar * 100000.0
    force_n = pression_pa * surface_m2
    force_kn = force_n / 1000.0
    
    with col_p2_m5:
        st.metric(label="Force théorique développée par la presse", value=f"{force_kn:.1f} kN")
        formule_pression_at5 = rf"F = P \cdot S = ({pression_circuit_bar} \cdot 10^5) \cdot ({surface_m2:.5f}) = {force_n:,.0f}\text{{ N}}"
        st.latex(formule_pression_at5)
        if pression_circuit_bar > 250:
            st.error("Seuil de surpression : Risque de fatigue accélérée ou d'éclatement des canalisations rigides.")
        else:
            st.info("L'action mécanique s'exerce de façon uniformément répartie sur l'aire du disque solide.")

    st.write("---")

    # =============================================================================
    # RENDU DES FORMULAIRES D'ÉVALUATION BI-COLONNE ENTIÈREMENT INDEXÉS
    # =============================================================================
    col_q_m, col_t_m = st.columns(2)
    
    with col_q_m:
        st.markdown("##### Quiz Technique du Scénario Maintenance (10 questions - 10 pts)")
        if "ordre_quiz_tab5_maint_aleatoire" in st.session_state:
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_maint_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox(
                    "", 
                    options=["Choisir..."] + q_data["options"], 
                    key=f"widget_at5_maint_q_{q_data['id']}_{idx}", 
                    disabled=verrou_at5,
                    label_visibility="collapsed"
                )

    with col_t_m:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        if "champs_therm5_maint_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_therm5_maint_clean, 1):
                enonce, choix, attendu, cle = ligne
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox(
                        "", 
                        choix, 
                        key=f"widget_at5_maint_t_{cle}_{idx}", 
                        disabled=verrou_at5,
                        label_visibility="collapsed"
                    )

    # =============================================================================
    # 5. SYSTÈME DE CORRECTION SUR 20 ET PROTOCOLE D'EXPORTATION HTML SCELLÉE
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")

    # DÉCLARATION ADAPTÉE DE SÉCURITÉ DE LA VARIABLE DE VERROUILLAGE
    if "suite_verrouille_tab5_maint" not in st.session_state:
        st.session_state.suite_verrouille_tab5_maint = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_maint

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de diagnostic de l'Atelier Maintenance.",
        key="check_certif_maint5_final_net_official",
        disabled=verrou_at5,
    )
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_maint_official_final", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz par parcours sécurisé
            score_q5 = 0.0
            if "ordre_quiz_tab5_maint_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_tab5_maint_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"widget_at5_maint_q_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q5 += 1.0

            # 2. Correction automatique du Texte à trous par parcours sécurisé
            score_t5 = 0.0
            if "champs_therm5_maint_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_therm5_maint_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"widget_at5_maint_t_{cle}_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t5 += 1.0

            # Enregistrement des notes globales de session
            st.session_state.score_suite5_maint_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_maint_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_maint = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_maint = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML DE L'ATELIER 5 SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab5_maint", False):
        from datetime import datetime
        scr1_t5 = st.session_state.get("score_suite5_maint_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_maint_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_maint", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_maint5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport d'Application Maintenance - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #dc2626; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 5 : Applications industrielles, diagnostics de pannes et maintenance des systèmes hydrauliques</p>
                <p>Scénario résolu : {titre_maint}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5_maint_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_maint_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"widget_at5_maint_q_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_maint5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_maint5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm5_maint_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm5_maint_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"widget_at5_maint_t_{cle_variable}_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_maint5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_maint5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_maint5 = preparer_nom_fichier("Rapport_Application_Maintenance").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 5 (.HTML)",
            data=html_export_maint5,
            file_name=nom_fichier_html_maint5,
            mime="text/html",
            use_container_width=True,
        )




























