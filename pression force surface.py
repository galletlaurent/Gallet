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
            st.image("histoire_pression_reelle.jpg", caption="Image réelle : Documents historiques d'époque")
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour descendre la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Affichage de la caricature de bande dessinée (Largeur fixe 300px)
        if os.path.exists("bd_choc_fluides.jpg"):
            st.image("bd_choc_fluides.jpg", caption="Caricature de l'incident historique")
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
            st.image("mecanique_forces_reelle.jpg", caption="Image réelle : Banc de traction et dynamomètre")
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour repousser la caricature vers le bas
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists("bd_mecanique_forces.jpg"):
            st.image("bd_mecanique_forces.jpg", caption="Caricature de l'incident mécanique vectoriel")
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
            st.image("pression_reelle_contexte.jpg", caption="Image réelle : Dispositif de mesure barométrique d'époque")
        else:
            st.caption("Image réelle de contexte manquante")

        # Insertion des 20 lignes d'espacement réglementaires pour repousser la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature des vases communicants (Largeur fixe 300px)
        if os.path.exists("bd_vases_communicants.jpg"):
            st.image("bd_vases_communicants.jpg", caption="Caricature de l'équilibre hydrostatique")
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

    # 2. SYSTÈME DE TIRAGE AU SORT PAR BOUTON
    if "cas_aleatoire_tab5" not in st.session_state:
        st.session_state.cas_aleatoire_tab5 = 1

    col_tirage_maint, col_statut_maint = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage_maint:
        if st.button("GÉNÉRER UN EXERCICE DE MAINTENANCE AU HASARD", key="btn_tirage_hasard_at5_officiel_final", use_container_width=True, disabled=verrou_at5):
            import random
            actuel_maint = st.session_state.cas_aleatoire_tab5
            possibles_maint = [1, 2, 3, 4]
            filtrés_maint = [c for c in possibles_maint if c != actuel_maint]
            st.session_state.cas_aleatoire_tab5 = random.choice(filtrés_maint)
            
            # Nettoyage des anciennes sélections pour forcer la mise à jour sans conflit
            if "ordre_quiz_tab5_maint_aleatoire" in st.session_state:
                del st.session_state.ordre_quiz_tab5_maint_aleatoire
            if "champs_therm5_maint_clean" in st.session_state:
                del st.session_state.champs_therm5_maint_clean
            st.rerun()

    id_cas_maint = st.session_state.cas_aleatoire_tab5
    st.write(f"Dossier technique de maintenance attribué : **Anomalie mécanique n°{id_cas_maint}**")

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
            st.image(fichier_reel_maint, caption="Image réelle : Constat en atelier")
        else:
            st.caption("Image réelle manquante")

        # Les 20 lignes d'espacement réglementaires pour repousser la caricature vers le bas
        for _ in range(20):
            st.write("")
        
        # 2. Affichage inférieur : Caricature (Largeur fixe 300px)
        if os.path.exists(fichier_caricature_maint):
            st.image(fichier_caricature_maint, caption="Bande dessinée de l'incident")
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
    # LABORATOIRE VIRTUEL SPÉCIFIQUE ET ADAPTÉ À CHAQUE CAS DE PANNE
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de calcul en direct")
    
    col_p1_m5, col_p2_m5 = st.columns(2)
    
    # ---------------------------------------------------------------------
    # SCÉNARIO 1 : FORCE ET PRESSION SUR LE DISQUE DU PISTON (LA PRESSE)
    # ---------------------------------------------------------------------
    if id_cas_maint == 1:
        with col_p1_m5:
            st.markdown("**Paramètres géométriques du Vérin**")
            diametre_piston_mm = st.slider("Diamètre du piston de la presse (mm) :", min_value=50, max_value=250, value=120, step=5, key="lab_c1_p1")
            pression_circuit_bar = st.slider("Pression de compactage mesurée (bars) :", min_value=10, max_value=350, value=160, step=10, key="lab_c1_p2")
        
        # Calculs : F = P * S
        rayon_m = (float(diametre_piston_mm) / 2.0) / 1000.0
        surface_m2 = 3.14159265 * (rayon_m ** 2)
        pression_pa = float(pression_circuit_bar) * 100000.0
        force_n = pression_pa * surface_m2
        force_kn = force_n / 1000.0
        
        with col_p2_m5:
            st.metric(label="Force de compactage développée (F)", value=f"{force_kn:.1f} kN")
            st.latex(rf"F = P \cdot S = ({pression_circuit_bar} \cdot 10^5) \cdot ({surface_m2:.5f}) = {force_n:,.0f}\text{{ N}}")
            st.info("L'huile contournant le piston réduit la force réelle par rapport à cette valeur théorique.")

    # ---------------------------------------------------------------------
    # SCÉNARIO 2 : CONTRAINTE MÉCANIQUE DANS LA CONDUITE EN ACIER (RONTURE)
    # ---------------------------------------------------------------------
    elif id_cas_maint == 2:
        with col_p1_m5:
            st.markdown("**Caractéristiques de la Canalisation Rigide**")
            pression_pic_bar = st.slider("Pression de pointe lors du choc (bars) :", min_value=50, max_value=500, value=220, step=10, key="lab_c2_p1")
            epaisseur_paroi_mm = st.slider("Épaisseur de la paroi en acier (mm) :", min_value=1.0, max_value=5.0, value=2.0, step=0.5, key="lab_c2_p2")
        
        # Formule simplifiée de Barlow pour la contrainte circonférentielle (Diamètre moyen fixé à 40mm)
        diametre_exterieur_mm = 40.0
        pression_mpa = float(pression_pic_bar) / 10.0
        contrainte_mpa = (pression_mpa * diametre_exterieur_mm) / (2.0 * float(epaisseur_paroi_mm))
        
        with col_p2_m5:
            st.metric(label="Contrainte mécanique dans l'acier (Sigma)", value=f"{contrainte_mpa:.1f} MPa")
            st.latex(rf"\sigma = \frac{{P \cdot D_e}}{{2 \cdot e}} = \frac{{{pression_mpa:.1f} \cdot {diametre_exterieur_mm}}}{{2 \cdot {epaisseur_paroi_mm}}} = {contrainte_mpa:.1f}\text{{ MPa}}")
            if contrainte_mpa > 200:
                st.error("DANGER : La contrainte dépasse le seuil élastique admissible de l'acier. Risque de rupture brute !")
            else:
                st.success("Zone de sécurité théorique avant fatigue de la matière solide.")

    # ---------------------------------------------------------------------
    # SCÉNARIO 3 : DÉPRESSION CRITIQUE À L'ASPIRATION (CAVITATION)
    # ---------------------------------------------------------------------
    elif id_cas_maint == 3:
        with col_p1_m5:
            st.markdown("**Calcul du Vide Relatif à l'Aspiration**")
            debit_pompe_lmin = st.slider("Débit de circulation de la pompe (L/min) :", min_value=10, max_value=150, value=60, step=5, key="lab_c3_p1")
            section_aspiration_cm2 = st.slider("Section interne de la conduite d'entrée (cm²) :", min_value=2.0, max_value=15.0, value=4.5, step=0.5, key="lab_c3_p2")
        
        # Modélisation simplifiée de la dépression générée à l'aspiration (P relative en bar)
        vitesse_m_s = (float(debit_pompe_lmin) / 60.0 / 1000.0) / (float(section_aspiration_cm2) / 10000.0)
        pression_aspiration_relative_bar = -0.05 * (vitesse_m_s ** 2)
        
        with col_p2_m5:
            st.metric(label="Vitesse du fluide", value=f"{vitesse_m_s:.2f} m/s")
            st.metric(label="Pression relative d'aspiration", value=f"{pression_aspiration_relative_bar:.2f} bar")
            if pression_aspiration_relative_bar < -0.30:
                st.error("ALERTE : Pression inférieure à la tension de vapeur saturante ! Ébullition de l'huile et cavitation destructrice.")
            else:
                st.success("Dépression modérée : Flux laminaire stable.")

    # ---------------------------------------------------------------------
    # SCÉNARIO 4 : LAMINAGE THERMIQUE DU FLUIDE AU LIMITEUR (SURCHAUFFE)
    # ---------------------------------------------------------------------
    else:
        with col_p1_m5:
            st.markdown("**Énergie thermique dissipée par frottement visqueux**")
            pression_perdue_bar = st.slider("Chute de pression à travers l'étranglement (bars) :", min_value=50, max_value=300, value=210, step=10, key="lab_c4_p1")
            debit_lamine_lmin = st.slider("Débit continu fuyant vers le réservoir (L/min) :", min_value=5, max_value=80, value=35, step=5, key="lab_c4_p2")
        
        # Formule de puissance thermique perdue : P_thermique (Watts) = Delta_P (Pascals) * Débit (m3/s)
        pression_pa_c4 = float(pression_perdue_bar) * 100000.0
        debit_m3_s = (float(debit_lamine_lmin) / 60.0) / 1000.0
        puissance_thermique_w = pression_pa_c4 * debit_m3_s
        puissance_thermique_kw = puissance_thermique_w / 1000.0
        
        with col_p2_m5:
            st.metric(label="Puissance thermique transformée en calories", value=f"{puissance_thermique_kw:.2f} kW")
            st.latex(rf"W = \Delta P \cdot Q = ({pression_perdue_bar} \cdot 10^5) \cdot ({debit_m3_s:.5f}) = {puissance_thermique_w:,.0f}\text{{ W}}")
            st.error(f"Friction moléculaire intense : Cette centrale dissipe {puissance_thermique_kw:.1f} kJ de chaleur sensible par seconde dans l'huile.")

    st.write("---")

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


with tab6:
    st.header("Application dans le domaine des Travaux Publics")
    st.write("Explorez les contraintes de pression mécanique appliquées aux engins de terrassement et ouvrages d'art.")

    # Styles CSS pour les légendes, bandeaux et alertes de l'Atelier 6
    st.markdown("""
    <style>
    .legende-tp { color: #d97706; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-tp { background-color: #fffbeb; border-left: 5px solid #f59e0b; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #78350f; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # =============================================================================
    # 1. DÉCLARATION DE SÉCURITÉ ABSOLUE DU VERROU TOUT EN HAUT
    # =============================================================================
    if "suite_verrouille_tab6_tp" not in st.session_state:
        st.session_state.suite_verrouille_tab6_tp = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_tp

    # Initialisation de l'id du cas par défaut si absent
    if "cas_aleatoire_tab6" not in st.session_state:
        st.session_state.cas_aleatoire_tab6 = 1
    id_cas_tp = st.session_state.cas_aleatoire_tab6

    # =============================================================================
    # 2. BOUTON DYNAMIQUEMENT LIÉ POUR GÉNÉRER UN EXERCICE AU HASARD
    # =============================================================================
    col_tirage_tp, col_statut_tp = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage_tp:
        if st.button("GÉNÉRER UN EXERCICE DE TRAVAUX PUBLICS AU HASARD", key="btn_tirage_hasard_at6_officiel_final", use_container_width=True, disabled=verrou_at6):
            import random
            actuel_tp = st.session_state.cas_aleatoire_tab6
            possibles_tp = [1, 2, 3, 4]
            filtrés_tp = [c for c in possibles_tp if c != actuel_tp]
            st.session_state.cas_aleatoire_tab6 = random.choice(filtrés_tp)
            
            # Nettoyage des anciennes sélections pour forcer la mise à jour sans conflit
            if "ordre_quiz_tab6_tp_aleatoire" in st.session_state:
                del st.session_state.ordre_quiz_tab6_tp_aleatoire
            if "champs_therm6_tp_clean" in st.session_state:
                del st.session_state.champs_therm6_tp_clean
            st.rerun()

    id_cas_tp = st.session_state.cas_aleatoire_tab6
    st.write(f"Dossier technique Travaux Publics attribué : **Anomalie mécanique n°{id_cas_tp}**")

    # =============================================================================
    # 3. CONFIGURATION DES BANQUES DE DONNÉES ET ÉNONCÉS TEXTUELS PAR CAS
    # =============================================================================
    if id_cas_tp == 1:
        titre_tp = "Pression d'appui des chenilles d'une pelle de 32 tonnes sur sol meuble"
        enonce_tp = (
            "**Case 1 :** Une pelle mécanique sur chenilles de fort tonnage effectue une phase de terrassement en zone marécageuse.\n\n"
            "**Case 2 :** L'opérateur constate une amorce d'enlisement de la structure solide sur le profil meuble instable.\n\n"
            "**Case 3 :** Le calcul métrologique cible l'aire totale de contact développée par la section des tuiles métalliques.\n\n"
            "**Case 4 :** L'élargissement des chenilles augmente la surface d'appui, provoquant l'effondrement de la pression exercée."
        )
        texte_bd_tp = (
            "**Bande Caricaturale de l'Incident : L'Enlisement Évité**\n\n"
            "**Case 1 :** Alarme terrain : « Le monstre de 32 tonnes s'enfonce, la portance de la boue liquide est dépassée ! ».\n\n"
            "**Case 2 :** Analyse physique : « C'est la loi de Pascal, la force du poids s'exerce sur une aire trop étroite ! ».\n\n"
            "**Case 3 :** Correctif : « Montage immédiat de patins larges pour multiplier la surface géométrique d'appui S ! ».\n\n"
            "**Case 4 :** Résolution : « La pression P chute de moitié ! La machine flotte sur le chantier des fluides ! »"
        )
        img_reelle_tp, img_bd_tp = "pelle_reelle.jpg", "bd_pelle.jpg"
        
        questions_sources_tp = [
            {"id": "tp_q1_c1", "q": "Pour empêcher un engin de chantier lourd de s'enfoncer dans un sol meuble, il faut :", "options": ["Augmenter sa surface d'appui au sol", "Réduire la largeur de ses chenilles", "Augmenter sa masse de lestage"], "rep": "Augmenter sa surface d'appui au sol"},
            {"id": "tp_q2_c1", "q": "Dans la relation P = F / S, si l'aire des tuiles (S) double, la pression d'appui (P) :", "options": ["Est divisée par deux", "Est multipliée par deux", "Reste strictement inchangée"], "rep": "Est divisée par deux"},
            {"id": "tp_q3_c1", "q": "Quelle unité normalisée du SI exprime la force du poids s'exerçant verticalement ?", "options": ["Le Newton (N)", "Le Pascal (Pa)", "Le Kilogramme (kg)"], "rep": "Le Newton (N)"},
            {"id": "tp_q4_c1", "q": "Le poids d'un corps solide dépend directement de sa masse et de :", "options": ["L'accélération de la pesanteur (g)", "La surface de contact", "La température ambiante"], "rep": "L'accélération de la pesanteur (g)"},
            {"id": "tp_q5_c1", "q": "Une pression de 1 kiloPascal (kPa) équivaut sur le plan métrologique à :", "options": ["1 000 Pa", "100 Pa", "10 bars"], "rep": "1 000 Pa"},
            {"id": "tp_q6_c1", "q": "Sur des chenilles, la force pressante se répartit sur la surface de manière :", "options": ["Uniforme", "Ponctuelle", "Nulle"], "rep": "Uniforme"},
            {"id": "tp_q7_c1", "q": "Si la boue devient plus liquide, sa capacité mécanique de portance :", "options": ["Diminue", "Augmente", "Reste maximale"], "rep": "Diminue"},
            {"id": "tp_q8_c1", "q": "Modifier l'aire géométrique des tuiles métalliques permet de faire varier :", "options": ["La pression d'appui", "La masse de la pelle", "La gravité locale"], "rep": "La pression d'appui"},
            {"id": "tp_q9_c1", "q": "Une mauvaise estimation de la nature du sol avant terrassement est une erreur :", "options": ["Humaine de préparation", "Strictement accidentelle incontournable", "Métrologique d'étalonnage"], "rep": "Humaine de préparation"},
            {"id": "tp_q10_c1", "q": "L'action orthogonale exercée par le patin rigide sur le sol meuble est une action de :", "options": ["Contact répartie", "Contact ponctuelle", "Distance pure"], "rep": "Contact répartie"}
        ]
        trous_sources_tp = [
            ("1. Répartir le poids sur une plus grande section diminue la .......... au sol.", ["Choisir...", "pression", "vitesse"], "pression", "tp_t1_c1"),
            ("2. L'intensité de la force verticale exercée par l'engin dépend de son ..........", ["Choisir...", "poids", "volume"], "poids", "tp_t2_c1"),
            ("3. Les patins élargis augmentent l'aire géométrique .......... globale.", ["Choisir...", "d'appui", "de frottement"], "dappui", "tp_t3_c1"),
            ("4. La force mécanique due à la gravité reste parfaitement .......... lors du changement.", ["Choisir...", "identique", "doublée"], "identique", "tp_t4_c1"),
            ("5. La relation fondamentale simulée dans ce cas est la loi de ..........", ["Choisir...", "Pascal", "Fourier"], "Pascal", "tp_t5_c1"),
            ("6. Le risque majeur pour la pelle sur cette plateforme est l'..........", ["Choisir...", "enlisement", "laminage"], "enlisement", "tp_t6_c1"),
            ("7. La contrainte répartie s'exprime dans le système légal en ..........", ["Choisir...", "Pascals", "Joules"], "Pascals", "tp_t7_c1"),
            ("8. Une surface deux fois plus grande divise la contrainte par ..........", ["Choisir...", "deux", "quatre"], "deux", "tp_t8_c1"),
            ("9. Maintenir la machine stable assure la continuité des opérations de ..........", ["Choisir...", "terrassement", "climatisation"], "terrassement", "tp_t9_c1"),
            ("10. Ce soin technique prévient le basculement structurel de l'.......... solide.", ["Choisir...", "engin", "fluide"], "engin", "tp_t10_c1")
        ]

    elif id_cas_tp == 2:
        titre_tp = "Stabilisateurs hydrauliques d'une grue mobile en levage lourd"
        enonce_tp = (
            "**Case 1 :** Une grue mobile de levage déploie ses poutres télescopiques stabilisatrices en bordure de fouille.\n\n"
            "**Case 2 :** Les patins d'ancrage en acier appliquent un effort ponctuel immense lors du levage d'une poutre béton.\n\n"
            "**Case 3 :** Sans calage d'interposition étendu, la contrainte mécanique excède la résistance élastique du goudron.\n\n"
            "**Case 4 :** L'ajout de madriers de grande section répartit la charge orthogonale et sécurise l'assise structurelle."
        )
        texte_bd_tp = (
            "**Bande Caricaturale de l'Incident : Le Poinçonnement des Chaussées**\n\n"
            "**Case 1 :** Levage critique : « La poutre de pont oscille, les vérins hydrauliques descendent sous charge ! ».\n\n"
            "**Case 2 :** Risque de poinçonnement : « Si l'aire du patin noir est trop petite, le bitume va percer comme du carton ! ».\n\n"
            "**Case 3 :** Répartition : « Insérez des madriers de bois dense pour élargir l'aire de la face réceptrice ! ».\n\n"
            "**Case 4 :** Stabilité : « Pression répartie, tassement différentiel évité, la grue reste d'équerre ! »"
        )
        img_reelle_tp, img_bd_tp = "grue_reelle.jpg", "bd_grue.jpg"

        questions_sources_tp = [
            {"id": "tp_q1_c2", "q": "Quel risque présente un patin stabilisateur appliqué sur une surface trop restreinte ?", "options": ["Le poinçonnement du revêtement routier", "Une baisse du débit de la pompe", "Le gel de l'huile hydraulique"], "rep": "Le poinçonnement du revêtement routier"},
            {"id": "tp_q2_c2", "q": "Si le sol se dérobe localement sous un seul des quatre vérins, la grue subit un tassement :", "options": ["Différentiel (rupture d'équilibre)", "Uniforme et parallèle", "Strictement permanent isotherme"], "rep": "Différentiel (rupture d'équilibre)"},
            {"id": "tp_q3_c2", "q": "Pour diviser par 4 la pression sous un patin, il faut multiplier sa surface par :", "options": ["4", "2", "16"], "rep": "4"},
            {"id": "tp_q4_c2", "q": "La force d'appui du vérin hydraulique sur son patin est une force de type :", "options": ["Contact", "Distance", "Magnétique"], "rep": "Contact"},
            {"id": "tp_q5_c2", "q": "L'aire d'un patin de calage carré se calcule par la relation géométrique :", "options": ["Côté × Côté", "2 × pi × Rayon", "Longueur × Largeur × Hauteur"], "rep": "Côté × Côté"},
            {"id": "tp_q6_c2", "q": "Le bitume chaud en été présente quelle caractéristique mécanique défavorable ?", "options": ["Une résistance au poinçonnement affaiblie", "Une rigidité élastique accrue", "Une conductivité infinie"], "rep": "Une résistance au poinçonnement affaiblie"},
            {"id": "tp_q7_c2", "q": "Le compensateur électronique de la grue alerte l'opérateur en cas de perte de :", "options": ["Verticalité ou niveau", "Pression des pneus", "Débit de carburant"], "rep": "Verticalité ou niveau"},
            {"id": "tp_q8_c2", "q": "Interposer du bois dense sous le vérin permet de transformer une force ponctuelle en action :", "options": ["Répartie surfacique", "À distance", "Nulle"], "rep": "Répartie surfacique"},
            {"id": "tp_q9_c2", "q": "Le levage d'une charge engendre un déplacement du centre de :", "options": ["Gravité de la structure", "Pression atmosphérique", "Célérité laser"], "rep": "Gravité de la structure"},
            {"id": "tp_q10_c2", "q": "L'unité industrielle couramment lue sur les abaques de calage des grues est le :", "options": ["bar (ou daN/cm²)", "Joule", "Watt"], "rep": "bar (ou daN/cm²)"}
        ]
        trous_sources_tp = [
            ("1. Les plaques de calage augmentent l'.......... de contact avec le terrain.", ["Choisir...", "aire", "hauteur"], "aire", "tp_t1_c2"),
            ("2. Pourcer la répartition d'effort empêche la rupture par .......... de l'asphalte.", ["Choisir...", "poinçonnement", "laminage"], "poinçonnement", "tp_t2_c2"),
            ("3. Un effondrement local du terrain crée un tassement .......... dangereux.", ["Choisir...", "différentiel", "homogène"], "différentiel", "tp_t3_c2"),
            ("4. Les vérins d'ancrage déploient une action mécanique de .......... solide.", ["Choisir...", "contact", "distance"], "contact", "tp_t4_c2"),
            ("5. La pièce en bois dense élargit la face solide de .......... du fluide.", ["Choisir...", "réception", "vaporisation"], "réception", "tp_t5_c2"),
            ("6. Plus le côté de la plaque carrée augmente, plus la contrainte .......... .", ["Choisir...", "s'effondre", "s'élève"], "seffondre", "tp_t6_c2"),
            ("7. La force d'appui se transmet orthogonalement, donc .......... au revêtement.", ["Choisir...", "perpendiculairement", "tangentiellement"], "perpendiculairement", "tp_t7_c2"),
            ("8. Vérifier la stabilité de l'assise protège la flèche contre tout ..........", ["Choisir...", "basculement", "échauffement"], "basculement", "tp_t8_c2"),
            ("9. Les charges lourdes amplifient le moment de la force de ..........", ["Choisir...", "levage", "conduction"], "levage", "tp_t9_c2"),
            ("10. Ce contrôle métrologique strict valide la conformité du plan de .......... .", ["Choisir...", "calage", "séchage"], "calage", "tp_t10_c2")
        ]

    elif id_cas_tp == 3:
        titre_tp = "Fléchissement de coffrage d'ouvrage d'art sous poussée du béton frais"
        enonce_tp = (
            "**Case 1 :** Lors du coulage des piles d'un viaduc, le béton fluide exerce une pression hydrostatique intense à la base.\n\n"
            "**Case 2 :** Les banches métalliques subissent des forces pressantes proportionnelles à la hauteur de la colonne liquide.\n\n"
            "**Case 3 :** Un défaut de rigidité des tirants engendre un fléchissement structurel de la paroi réceptrice solide.\n\n"
            "**Case 4 :** L'ajustement du maillage de serrage équilibre les actions fluides et fige la géométrie de l'ouvrage."
        )
        texte_bd_tp = (
            "**Bande Caricaturale de l'Incident : La Poussée Hydrostatique**\n\n"
            "**Case 1 :** Coulage continu : « Le malaxeur déverse le béton fluide, la colonne grimpe à 6 mètres de haut ! ».\n\n"
            "**Case 2 :** Pression hydrostatique : « C'est la loi des fluides, plus on descend profond, plus les Pascals écrasent la bâche ! ».\n\n"
            "**Case 3 :** Alerte déformation : « Les banches se courbent, la force pressante orthogonale est en train de tout arracher ! ».\n\n"
            "**Case 4 :** Confinement : « Verrous resserrés, les actions mécaniques se compensent, le béton est dompté ! »"
        )
        img_reelle_tp, img_bd_tp = "coffrage_reel.jpg", "bd_coffrage.jpg"

        questions_sources_tp = [
            {"id": "tp_q1_c3", "q": "La pression exercée par le béton fluide à la base du coffrage dépend surtout de :", "options": ["La hauteur de coulage et la densité du fluide", "Le volume total du malaxeur", "La nuance d'acier des banches"], "rep": "La hauteur de coulage et la densité du fluide"},
            {"id": "tp_q2_c3", "q": "La force pressante exercée par le béton frais sur la paroi verticale agit de façon :", "options": ["Strictement perpendiculaire à la paroi", "Parallèle à l'axe vertical", "Oblique descendante"], "rep": "Strictement perpendiculaire à la paroi"},
            {"id": "tp_q3_c3", "q": "Quelle formule régit la pression hydrostatique exercée par un fluide au repos ?", "options": ["P = rho * g * h", "P = F / S", "F = P * S"], "rep": "P = rho * g * h"},
            {"id": "tp_q4_c3", "q": "Le béton fluide est considéré dans les premières heures comme un fluide pratiquement :", "options": ["Incompressible et lourd", "Compressible et volatile", "Strictement gazeux"], "rep": "Incompressible et lourd"},
            {"id": "tp_q5_c3", "q": "Si le rythme de coulage s'accélère et la hauteur double instantanément, la pression à la base :", "options": ["Double", "Reste constante", "Divise par quatre"], "rep": "Double"},
            {"id": "tp_q6_c3", "q": "Pour mesurer cette pression hydrostatique en cours de chantier, on utilise des capteurs de :", "options": ["Pression (manomètres de coffrage)", "Débit", "Température latente"], "rep": "Pression (manomètres de coffrage)"},
            {"id": "tp_q7_c3", "q": "Le fléchissement géométrique des banches traduit un dépassement de la limite :", "options": ["De déformation élastique de la structure", "De viscosité du béton", "De conductivité du métal"], "rep": "De déformation élastique de la structure"},
            {"id": "tp_q8_c3", "q": "Les tirants en acier qui maintiennent le coffrage travaillent sous une contrainte de :", "options": ["Traction mécanique", "Laminage fluide", "Cavitation gazeuse"], "rep": "Traction mécanique"},
            {"id": "tp_q9_c3", "q": "Quelle unité SI quantifie l'aire d'appui d'une banche soumise à l'action pressante ?", "options": ["Le mètre carré (m²)", "Le Pascal", "Le Newton"], "rep": "Le mètre carré (m²)"},
            {"id": "tp_q10_c3", "q": "L'équilibre hydrostatique est atteint lorsque la poussée interne du béton est :", "options": ["Entièrement compensée par la résistance mécanique des tirants", "Supérieure à la limite de rupture", "Strictement nulle"], "rep": "Entièrement compensée par la résistance mécanique des tirants"}
        ]
        trous_sources_tp = [
            ("1. Le béton liquide applique une action mécanique de .......... hydrostatique.", ["Choisir...", "pression", "conduction"], "pression", "tp_t1_c3"),
            ("2. Cette contrainte se déploie de façon normale, donc .......... aux panneaux.", ["Choisir...", "perpendiculaire", "parallèle"], "perpendiculaire", "tp_t2_c3"),
            ("3. L'intensité de l'effort croît linéairement avec la .......... de coulage.", ["Choisir...", "profondeur", "surface"], "profondeur", "tp_t3_c3"),
            ("4. La déformation des banches solides traduit un défaut de .......... des cadres.", ["Choisir...", "rigidité", "température"], "rigidité", "tp_t4_c3"),
            ("5. Pour calibrer l'ouvrage, la surface réceptrice est mesurée en .......... carrés.", ["Choisir...", "mètres", "bars"], "mètres", "tp_t5_c3"),
            ("6. Le béton frais se comporte initialement comme un liquide .......... .", ["Choisir...", "incompressible", "extensible"], "incompressible", "tp_t6_c3"),
            ("7. Les forces pressantes se transmettent fidèlement dans toutes les ..........", ["Choisir...", "directions", "lignes"], "directions", "tp_t7_c3"),
            ("8. Resserre le maillage des barres de blocage empêche le .......... des parois.", ["Choisir...", "fléchissement", "gel"], "fléchissement", "tp_t8_c3"),
            ("9. L'effort total de poussée est égal au produit de l'aire par la .......... moyenne.", ["Choisir...", "pression", "vitesse"], "pression", "tp_t9_c3"),
            ("10. Ce diagnostic assure la parfaite conformité géométrique de la pile du ..........", ["Choisir...", "viaduc", "vérin"], "viaduc", "tp_t10_c3")
        ]
    else:
        titre_tp = "Pression hydraulique de poussée du bouclier d'un tunnelier"
        enonce_tp = (
            "**Case 1 :** Le tunnelier géant progresse en sous-sol en exerçant une force titanesque pour broyer la roche solide.\n\n"
            "**Case 2 :** Les vérins hydrauliques périphériques reçoivent de l'huile sous très haute pression (jusqu'à 350 bars).\n\n"
            "**Case 3 :** La force pressante totale dépend du produit de cette pression de service par la large section des pistons.\n\n"
            "**Case 4 :** Le calage des patins sur les voussoirs en béton transmet l'action mécanique nécessaire à l'avancement."
        )
        texte_bd_tp = (
            "**Bande Caricaturale de l'Incident : La Poussée du Tunnelier**\n\n"
            "**Case 1 :** Excavation : « La roue de coupe tourne, mais pour mordre le granit, il faut pousser fort derrière ! ».\n\n"
            "**Case 2 :** Puissance fluide : « Les pompes crachent l'huile à 350 bars, les chambres des vérins s'échauffent ! ».\n\n"
            "**Case 3 :** Multiplication : « En combinant une pression extrême avec une immense surface solide S, la force F devient colossale ! ».\n\n"
            "**Case 4 :** Avancement : « Les voussoirs tiennent bon, le bouclier avance d'un metro dans les entrailles de la Terre ! »"
        )
        img_reelle_tp, img_bd_tp = "tunnelier_reel.jpg", "bd_tunnelier.jpg"

        questions_sources_tp = [
            {"id": "tp_q1_c4", "q": "Pour générer la force monumentale d'avancement d'un tunnelier, le système combine :", "options": ["Une très haute pression et une large surface cumulée de pistons", "Une basse pression et des petits pistons", "Un fluide gazeux compressible"], "rep": "Une très haute pression et une large surface cumulée de pistons"},
            {"id": "tp_q2_c4", "q": "Quelle unité de pression industrielle correspond à la haute pression de 350 bars ?", "options": ["35 MPa", "3.5 MPa", "350 Pascals"], "rep": "35 MPa"},
            {"id": "tp_q3_c4", "q": "L'effort de réaction mécanique s'exerce en prenant appui sur les anneaux de béton nommés :", "options": ["Voussoirs", "Banches", "Tirants"], "rep": "Voussoirs"},
            {"id": "tp_q4_c4", "q": "Si un circuit de tunnelier subit une fuite d'huile interne dans un vérin, la force d'avancement :", "options": ["Chute localement car la pression s'effondre", "Reste maximale", "Augmente par compensation"], "rep": "Chute localement car la pression s'effondre"},
            {"id": "tp_q5_c4", "q": "La relation physique fondamentale qui régit la poussée du piston est :", "options": ["F = P * S", "P = F * S", "S = P / F"], "rep": "F = P * S"},
            {"id": "tp_q6_c4", "q": "L'huile hydraulique utilisée dans les circuits de tunnelier est choisie pour son :", "options": ["Incompressibilité et pouvoir lubrifiant", "Pouvoir volatile", "Coefficient de dilatation nul"], "rep": "Incompressibilité et pouvoir lubrifiant"},
            {"id": "tp_q7_c4", "q": "La surface transversale utile du piston du vérin de poussée est de géométrie :", "options": ["Circulaire", "Carrée", "Triangulaire"], "rep": "Circulaire"},
            {"id": "tp_q8_c4", "q": "Un surtarage accidentel des valves de sécurité de la centrale présente un risque de :", "options": ["Rupture ou éclatement mécanique des conduites", "Chute de température", "Cavitation à l'échappement"], "rep": "Rupture ou éclatement mécanique des conduites"},
            {"id": "tp_q9_c4", "q": "L'action mécanique de poussée exercée sur le front de taille est une action de :", "options": ["Contact répartie", "Distance pure", "Gravitation lunaire"], "rep": "Contact répartie"},
            {"id": "tp_q10_c4", "q": "L'appareil métrologique qui surveille la pression dans chaque groupe de vérins est :", "options": ["Un manomètre électronique", "Un dynamomètre à ressort", "Un baromètre à mercure"], "rep": "Un manomètre électronique"}
        ]
        trous_sources_tp = [
            ("1. Le tunnelier progresse grâce à la force développée par des vérins ..........", ["Choisir...", "hydrauliques", "pneumatiques"], "hydrauliques", "tp_t1_c4"),
            ("2. La centrale injecte l'huile sous une très haute .......... de service.", ["Choisir...", "pression", "vitesse"], "pression", "tp_t2_c4"),
            ("3. L'effort mécanique axial dépend du produit de la pression par la ..........", ["Choisir...", "surface", "hauteur"], "surface", "tp_t3_c4"),
            ("4. L'action de poussée solide se déploie de manière .......... au front de taille.", ["Choisir...", "perpendiculaire", "tangentielle"], "perpendiculaire", "tp_t4_c4"),
            ("5. La pression industrielle de 350 bars équivaut à 35 ..........", ["Choisir...", "MégaPascals", "Bars"], "MégaPascals", "tp_t5_c4"),
            ("6. Pour reculer les pistons, le fluide est inversé dans la .......... de retour.", ["Choisir...", "chambre", "bâche"], "chambre", "tp_t6_c4"),
            ("7. L'huile transmet intégralement les efforts car elle est .......... .", ["Choisir...", "incompressible", "volatile"], "incompressible", "tp_t7_c4"),
            ("8. L'appui mécanique s'effectue sur des blocs de béton appelés ..........", ["Choisir...", "voussoirs", "banches"], "voussoirs", "tp_t8_c4"),
            ("9. Maintenir un profil de poussée symétrique empêche toute déviation de ..........", ["Choisir...", "trajectoire", "température"], "trajectoire", "tp_t9_c4"),
            ("10. Ce diagnostic hydraulique strict garantit la sécurité des travaux de .......... .", ["Choisir...", "percement", "nivellement"], "percement", "tp_t10_c4")
        ]

    # Enregistrement final et synchronisation immédiate des variables en session
    if "ordre_quiz_tab6_tp_aleatoire" not in st.session_state:
        st.session_state.ordre_quiz_tab6_tp_aleatoire = questions_sources_tp
    if "champs_therm6_tp_clean" not in st.session_state:
        st.session_state.champs_therm6_tp_clean = trous_sources_tp

    col_g_tp, col_d_tp = st.columns([0.3, 0.7])
    
    with col_g_tp:
        st.markdown(f"##### Dossier Technique : {titre_tp}")
        st.info(enonce_tp)
        st.info(texte_bd_tp)
        
    with col_d_tp:
        st.markdown("##### Visualisation Technique")
        import os
        
        # 1. Rendu supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists(img_reelle_tp):
            st.image(img_reelle_tp, caption="Image réelle : Constat sur site ou ouvrage", width=300)
        else:
            st.caption("Illustration réelle indisponible ou manquante")
        
        # Boucle d'espacement des 20 lignes réglementaires pour descendre la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Rendu inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists(img_bd_tp):
            st.image(img_bd_tp, caption="Bande dessinée humoristique du cas", width=300)
        else:
            st.caption("Illustration caricaturale indisponible ou manquante")

    st.write("---")
    st.subheader("Laboratoire Virtuel : Simulateur d'Ouvrages et d'Engins de Terrassement")
    
    col_p1_tp, col_p2_tp = st.columns(2)
    
    # ---------------------------------------------------------------------
    # CAS 1 : PRESSE ET CHENILLES DE PELLE SUR SOL MEUBLE
    # ---------------------------------------------------------------------
    if id_cas_tp == 1:
        with col_p1_tp:
            m_pelle = st.slider("Masse de la pelle mécanique (tonnes) :", 10, 50, 32, 2, key="sl_tp_c1_1_s6")
            w_chenille = st.slider("Largeur des tuiles de chenille (mm) :", 500, 900, 600, 5, key="sl_tp_c1_2_s6")
        poids_n = float(m_pelle) * 1000.0 * 9.81
        surf_sol = 2.0 * (float(w_chenille) / 1000.0) * 4.5  # Longueur fixée à 4.5m
        pres_sol_kpa = (poids_n / surf_sol) / 1000.0
        with col_p2_tp:
            st.metric("Pression d'appui moyenne sur le terrain", f"{pres_sol_kpa:.1f} kPa")
            st.latex(rf"P = \frac{{F}}{{S}} = \frac{{{poids_n:,.0f}}}{{{surf_sol:.3f}}} = {pres_sol_kpa * 1000:,.0f}\text{{ Pa}}")

    # ---------------------------------------------------------------------
    # CAS 2 : VÉRINS STABILISATEURS ET POINÇONNEMENT DE CHAUSSÉE
    # ---------------------------------------------------------------------
    elif id_cas_tp == 2:
        with col_p1_tp:
            f_patin = st.slider("Force d'appui verticale sur le vérin (kN) :", 50, 400, 150, 10, key="sl_tp_c2_1_s6")
            c_patin = st.slider("Côté de la plaque carrée de calage (cm) :", 30, 100, 60, 5, key="sl_tp_c2_2_s6")
        surf_p = (float(c_patin) / 100.0) ** 2
        pres_sol_bar = (float(f_patin * 1000) / surf_p) / 100000.0
        with col_p2_tp:
            st.metric("Pression répartie sous le patin stabilisateur", f"{pres_sol_bar:.2f} bar")
            st.latex(rf"P = \frac{{F}}{{S}} = \frac{{{f_patin * 1000:,.0f}}}{{{surf_p:.4f}}} = {pres_sol_bar * 100000:,.0f}\text{{ Pa}}")

    # ---------------------------------------------------------------------
    # CAS 3 : POUSSÉE HYDROSTATIQUE SUR COFFRAGE DE VIADUC
    # ---------------------------------------------------------------------
    elif id_cas_tp == 3:
        with col_p1_tp:
            h_beton = st.slider("Hauteur du béton frais coulé dans la pile (m) :", 1.0, 12.0, 6.0, 0.5, key="sl_tp_c3_1_s6")
        # Pression hydrostatique béton : masse volumique moyenne rho = 2400 kg/m3
        pres_hydro_pa = 2400.0 * 9.81 * float(h_beton)
        pres_hydro_bar = pres_hydro_pa / 100000.0
        with col_p2_tp:
            st.metric("Pression hydrostatique maximale à la base", f"{pres_hydro_bar:.2f} bar")
            st.latex(rf"P = \rho \cdot g \cdot h = 2400 \cdot 9{{,}}81 \cdot {h_beton} = {pres_hydro_pa:,.0f}\text{{ Pa}}")

    # ---------------------------------------------------------------------
    # CAS 4 : FORCE DE POUSSÉE HYDRAULIQUE DU TUNNELIER
    # ---------------------------------------------------------------------
    else:
        with col_p1_tp:
            p_tun_bar = st.slider("Pression hydraulique de poussée des vérins (bars) :", 100, 400, 250, 10, key="sl_tp_c4_1_s6")
            d_verin_mm = st.slider("Diamètre utile d'un piston de poussée (mm) :", 150, 400, 280, 10, key="sl_tp_c4_2_s6")
        r_m = (float(d_verin_mm) / 2.0) / 1000.0
        surf_v_m2 = 3.141592653589793 * (r_m ** 2)
        f_poussee_n = (float(p_tun_bar) * 100000.0) * surf_v_m2
        f_poussee_kn = f_poussee_n / 1000.0
        with col_p2_tp:
            st.metric("Force de poussée par vérin individuel", f"{f_poussee_kn:.1f} kN")
            st.latex(rf"F = P \cdot S = ({p_tun_bar} \cdot 10^5) \cdot ({surf_v_m2:.4f}) = {f_poussee_n:,.0f}\text{{ N}}")

    st.write("---")

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique du Scénario TP (10 pts)")
        if "ordre_quiz_tab6_tp_aleatoire" in st.session_state:
            for idx, q_d in enumerate(st.session_state.ordre_quiz_tab6_tp_aleatoire, 1):
                st.write(f"**{idx}.** {q_d['q']}")
                st.selectbox(
                    "", 
                    options=["Choisir..."] + q_d["options"], 
                    key=f"tp_q_{q_d['id']}_{idx}", 
                    disabled=verrou_at6, 
                    label_visibility="collapsed"
                )
    with col_t:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 pts)")
        if "champs_therm6_tp_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_therm6_tp_clean, 1):
                enonce, choix, attendu, cle = ligne
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox(
                        "", 
                        choix, 
                        key=f"tp_t_{cle}_{idx}", 
                        disabled=verrou_at6, 
                        label_visibility="collapsed"
                    )

    # =============================================================================
    # 7. MODULE DE VALIDATION TECHNIQUE ET COMPILATION DU BILAN HTML
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_tp = st.checkbox(
        "Je certifie avoir complété l'Atelier d'application des Travaux Publics.", 
        key="chk_certif_at6_final_official", 
        disabled=verrou_at6
    )
    
    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", 
        key="btn_valider_at6_official_ultimate", 
        use_container_width=True, 
        disabled=verrou_at6
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tp: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz
            score_q = 0.0
            if "ordre_quiz_tab6_tp_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_tab6_tp_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tp_q_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q += 1.0
            
            # 2. Correction automatique du Texte à trous
            score_t = 0.0
            if "champs_therm6_tp_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_therm6_tp_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne[2]
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tp_t_{cle}_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t += 1.0
            
            # Sauvegarde des notes globales sur 20 points
            st.session_state.score_suite6_tp_p1 = round(float(score_q), 1)
            st.session_state.score_suite6_tp_p2 = round(float(score_t), 1)
            st.session_state.score_final_at6 = round(float(score_q + score_t), 1)
            st.session_state.suite_verrouille_tab6_tp = True
            st.rerun()

    # --- ARCHIVAGE DU RAPPORT ELECTRONIQUE SCELLÉ HTML ---
    if st.session_state.get("suite_verrouille_tab6_tp", False):
        from datetime import datetime
        scr1_t6 = st.session_state.get("score_suite6_tp_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_tp_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_at6", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TP SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_tp6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Travaux Publics - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #d97706; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 6 : Applications mécaniques et répartition des pressions aux Travaux Publics</p>
                <p>Scénario résolu : {titre_tp}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        if "ordre_quiz_tab6_tp_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_tp_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tp_q_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tp6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tp6 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm6_tp_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm6_tp_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tp_t_{cle_variable}_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tp6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tp6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tp6 = preparer_nom_fichier("Rapport_Application_TP").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 6 (.HTML)",
            data=html_export_tp6,
            file_name=nom_fichier_html_tp6,
            mime="text/html",
            use_container_width=True,
        )


with tab7:
    st.header("Application dans le domaine du Transport Routier")
    st.write("Analysez les systèmes de freinage pneumatique et la répartition des masses par essieu routier.")

    # Styles CSS pour les légendes, bandeaux et alertes de l'Atelier 7
    st.markdown("""
    <style>
    .legende-tr { color: #2563eb; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-tr { background-color: #eff6ff; border-left: 5px solid #3b82f6; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #1e3a8a; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # 1. DÉCLARATION DE SÉCURITÉ ABSOLUE DU VERROU TOUT EN HAUT
    if "suite_verrouille_tab7_tr" not in st.session_state:
        st.session_state.suite_verrouille_tab7_tr = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_tr

    # 2. INITIALISATION ET TIRAGE AU SORT D'EXERCICE MULTI-CAS AUTONOME
    if "cas_aleatoire_tab7" not in st.session_state:
        st.session_state.cas_aleatoire_tab7 = 1

    col_tirage_tr, col_statut_tr = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage_tr:
        if st.button("GÉNÉRER UN EXERCICE DE TRANSPORT ROUTIER AU HASARD", key="btn_tirage_hasard_at7_officiel_final", use_container_width=True, disabled=verrou_at7):
            import random
            actuel_tr = st.session_state.cas_aleatoire_tab7
            possibles_tr = [1, 2, 3, 4]
            filtrés_tr = [c for c in possibles_tr if c != actuel_tr]
            st.session_state.cas_aleatoire_tab7 = random.choice(filtrés_tr)
            
            # Nettoyage des sélections pour forcer la mise à jour synchrone
            if "ordre_quiz_tab7_tr_aleatoire" in st.session_state: del st.session_state.ordre_quiz_tab7_tr_aleatoire
            if "champs_therm7_tr_clean" in st.session_state: del st.session_state.champs_therm7_tr_clean
            st.rerun()

    id_cas_tr = st.session_state.cas_aleatoire_tab7
    st.write(f"Dossier technique Transport Routier attribué : **Cas n°{id_cas_tr}**")

    # =============================================================================
    # 3. BASE DE DONNÉES DYNAMIQUES DES QUESTIONS, TROUS ET TEXTES (PAR CAS)
    # =============================================================================
    if id_cas_tr == 1:
        titre_tr = "Vase de freinage pneumatique d'un semi-remorque en pleine charge"
        enonce_tr = (
            "**Case 1 :** L'effort de serrage mécanique sur les garnitures de freins dépend directement de la pression d'air comprimé injectée.\n\n"
            "**Case 2 :** Le diaphragme souple interne convertit la pression relative pneumatique P en une force axiale rectiligne F.\n\n"
            "**Case 3 :** En cas de micro-fissure de l'enveloppe, une fuite d'air externe fait chuter la pression, compromettant le freinage.\n\n"
            "**Case 4 :** Le maintien d'une étanchéité parfaite garantit le déploiement de la force de poussée nominale requise."
        )
        texte_bd_tr = (
            "**Bande Caricaturale de l'Incident : Les Freins Pneumatiques**\n\n"
            "**Case 1 :** Commande : « Pied sur la pédale, les valves s'ouvrent, l'air sous pression se rue vers les roues ! ».\n\n"
            "**Case 2 :** Transformation : « Le vase de frein reçoit les bars et pousse la tige métallique comme un vérin ! ».\n\n"
            "**Case 3 :** Relation P=F/S : « Plus l'aire de la membrane S est grande, plus la force de serrage F est titanesque ! ».\n\n"
            "**Case 4 :** Sécurité : « Circuit étanche, le poids lourd de 44 tonnes s'arrête pile sur la ligne de stop ! »"
        )
        img_reelle_tr, img_bd_tr = "frein_reel.jpg", "bd_frein.jpg"
        
        questions_sources_tr = [
            {"id": "tr_q1_c1", "q": "Quel fluide compressible anime les actionneurs de freinage d'un poids lourd ?", "options": ["L'air comprimé", "L'huile minérale", "L'eau distillée"], "rep": "L'air comprimé"},
            {"id": "tr_q2_c1", "q": "Si la membrane souple interne du vase de frein se déchire, la force mécanique développée :", "options": ["S'annule par fuite d'air", "Reste maximale", "Est doublée par sécurité"], "rep": "S'annule par fuite d'air"},
            {"id": "tr_q3_c1", "q": "Dans l'unité usuelle industrielle, à combien de Pascals correspond 1 bar ?", "options": ["100 000 Pa", "1 000 Pa", "100 Pa"], "rep": "100 000 Pa"},
            {"id": "tr_q4_c1", "q": "L'effort mécanique F transmis par la tige de commande agit de façon :", "options": ["Perpendiculaire à la surface", "Parallèle à la surface", "Oblique"], "rep": "Perpendiculaire à la surface"},
            {"id": "tr_q5_c1", "q": "Quel organe mécanique génère l'air comprimé à bord du tracteur routier ?", "options": ["Le compresseur bicylindre", "La pompe d'injection", "L'alternateur d'arbre"], "rep": "Le compresseur bicylindre"},
            {"id": "tr_q6_c1", "q": "Le relâchement de la pédale de frein provoque une évacuation d'air qualifiée de :", "options": ["Échappement à l'atmosphère", "Aspiration de sécurité", "Laminage thermique"], "rep": "Échappement à l'atmosphère"},
            {"id": "tr_q7_c1", "q": "La surface utile de la membrane souple d'un récepteur de frein s'exprime en :", "options": ["Mètres carrés (ou pouces)", "Bars", "Newtons par mètre"], "rep": "Mètres carrés (ou pouces)"},
            {"id": "tr_q8_c1", "q": "Un temps de réponse trop long lors du freinage indique généralement :", "options": ["Une fuite ou une restriction de ligne", "Une huile trop visqueuse", "Une surpression du compresseur"], "rep": "Une fuite ou une restriction de ligne"},
            {"id": "tr_q9_c1", "q": "Pour garantir l'arrêt d'un véhicule articulé de 44 tonnes, la force de freinage totale doit être :", "options": ["Proportionnelle à la masse totale en charge", "Strictement égale à 100 N", "Indépendante de la vitesse"], "rep": "Proportionnelle à la masse totale en charge"},
            {"id": "tr_q10_c1", "q": "La jauge rouge du tableau de bord d'un camion indique une alerte critique si la pression pneumatique est :", "options": ["Inférieure au seuil de sécurité de 5.5 bars", "Supérieure à 1 bar", "Strictement stable"], "rep": "Inférieure au seuil de sécurité de 5.5 bars"}
        ]
        trous_sources_tr = [
            ("1. Le compresseur de bord stocke l'énergie sous forme de .......... pneumatique.", ["Choisir...", "pression", "chaleur"], "pression", "tr_t1_c1"),
            ("2. La section utile de la membrane conditionne l'intensité de la .......... .", ["Choisir...", "force", "vitesse"], "force", "tr_t2_c1"),
            ("3. L'évacuation de l'air lors du relâchement correspond à une baisse de .......... .", ["Choisir...", "pression", "masse"], "pression", "tr_t3_c1"),
            ("4. La force pressante se déploie de manière orthogonale aux .......... .", ["Choisir...", "parois", "tubes"], "parois", "tr_t4_c1"),
            ("5. La loi fondamentale appliquée aux actionneurs du circuit est le principe de ..........", ["Choisir...", "Pascal", "Newton"], "Pascal", "tr_t5_c1"),
            ("6. Une fuite d'air comprimé vers l'extérieur constitue une anomalie ..........", ["Choisir...", "externe", "interne"], "externe", "tr_t6_c1"),
            ("7. Convertir les bars en Pascals exige de multiplier la valeur lue par ..........", ["Choisir...", "100 000", "1 000"], "100 000", "tr_t7_c1"),
            ("8. L'effort axial pousse fermement les garnitures contre le .......... solide.", ["Choisir...", "tambour", "réservoir"], "tambour", "tr_t8_c1"),
            ("9. L'étanchéité des raccords souples garantit la sécurité du ..........", ["Choisir...", "transport", "moteur"], "transport", "tr_t9_c1"),
            ("10. Ce diagnostic prévient tout risque de perte de contrôle du .......... routier.", ["Choisir...", "camion", "fluide"], "camion", "tr_t10_c1")
        ]
    else:
        titre_tr = "Régulation des suspensions pneumatiques et impact de la surcharge"
        enonce_tr = (
            "**Case 1 :** Les coussins d'essieux en élastomère s'adaptent pour maintenir le châssis routier à hauteur constante.\n\n"
            "**Case 2 :** Une surcharge localisée augmente de manière critique le poids (Force) s'exerçant sur la surface d'appui.\n\n"
            "**Case 3 :** La centrale électronique doit injecter plus d'air pour faire grimper la pression P et équilibrer le pont.\n\n"
            "**Case 4 :** Si la pression franchit la limite mécanique élastique, le boudin explose par surpression brutale."
        )
        texte_bd_tr = (
            "**Bande Caricaturale de l'Incident : Les Coussins de Suspension**\n\n"
            "**Case 1 :** Chargement lourd : « On empile les palettes à l'arrière, les coussins s'écrasent sous la force ! ».\n\n"
            "**Case 2 :** Réaction : « Les capteurs crient ! Il faut gonfler les ballons pour contrer le tassement ! ».\n\n"
            "**Case 3 :** Calcul : « La pression grimpe à 7 bars pour maintenir l'assiette du plateau à l'horizontale ! ».\n\n"
            "**Case 4 :** Alerte Surcharge : « Trop de Newtons ! Le boudin sature, attention à la hernie mécanique ! »"
        )
        img_reelle_tr, img_bd_tr = "susp_reelle.jpg", "bd_susp.jpg"

        questions_sources_tr = [
            {"id": "tr_q1_c2", "q": "Quelle grandeur physique varie dans le coussin pour compenser un surcroît de poids ?", "options": ["La pression de l'air insuflé", "La masse volumique du caoutchouc", "La constante gravitationnelle"], "rep": "La pression de l'air insuflé"},
            {"id": "tr_q2_c2", "q": "L'éclatement d'un boudin pneumatique de suspension constitue une rupture :", "options": ["Brute par dépassement de la limite élastique", "Thermique transitoire", "Isotherme permanente"], "rep": "Brute par dépassement de la limite élastique"},

            {"id": "tr_q3_c2", "q": "Quel appareil permet de vérifier la pression de gonflage des circuits pneumatiques ?", "options": ["Un manomètre", "Un dynamomètre", "Un débitmètre"], "rep": "Un manomètre"},
            {"id": "tr_q4_c2", "q": "Quand le camion roule sur une bosse, la force dynamique subie par la suspension :", "options": ["Augmente instantanément", "Reste parfaitement stable", "S'annule"], "rep": "Augmente instantanément"},
            {"id": "tr_q5_c2", "q": "La suspension pneumatique offre par rapport aux ressorts métalliques l'avantage d'une :", "options": ["Correction d'assiette constante", "Masse totale réduite de moitié", "Suppression totale de la gravité"], "rep": "Correction d'assiette constante"},
            {"id": "tr_q6_c2", "q": "Une mauvaise répartition de la cargaison dans la remorque génère une surcharge localisée sur :", "options": ["Un essieu spécifique", "Le pare-brise", "Le réservoir de gazole"], "rep": "Un essieu spécifique"},
            {"id": "tr_q7_c2", "q": "L'unité légale du système international pour mesurer l'aire d'appui du coussin est :", "options": ["Le mètre carré (m²)", "Le Pascal", "Le bar"], "rep": "Le mètre carré (m²)"},
            {"id": "tr_q8_c2", "q": "Si un boudin de suspension fuit en continu, le camion va présenter une assiette :", "options": ["Inclinée ou déséquilibrée", "Strictement parfaite", "Totalement surélevée"], "rep": "Inclinée ou déséquilibrée"},
            {"id": "tr_q9_c2", "q": "Pour doubler la force de levée d'un coussin sans modifier sa pression, il faut :", "options": ["Doubler sa surface active", "Réduire sa hauteur", "Changer le type d'acier"], "rep": "Doubler sa surface active"},
            {"id": "tr_q10_c2", "q": "La valve de nivellement automatique réagit directement aux variations géométriques de :", "options": ["La garde au sol du châssis", "La température extérieure", "La vitesse de rotation des roues"], "rep": "La garde au sol du châssis"}
        ]
        trous_sources_tr = [
            ("1. Les suspensions absorbent les chocs du profil de la .......... .", ["Choisir...", "route", "bâche"], "route", "tr_t1_c2"),
            ("2. Équilibrer une charge lourde exige d'augmenter le flux d'.......... comprimé.", ["Choisir...", "air", "fluide"], "air", "tr_t2_c2"),
            ("3. La pression répartie sur la surface interne développe le vecteur .......... d'assiette.", ["Choisir...", "force", "vitesse"], "force", "tr_t3_c2"),
            ("4. Maintenir le niveau horizontal évite un comportement routier .......... .", ["Choisir...", "instable", "parfait"], "instable", "tr_t4_c2"),
            ("5. Les boudins souples s'adaptent selon les contraintes de la .......... solidifiée.", ["Choisir...", "charge", "vitesse"], "charge", "tr_t5_c2"),
            ("6. Une surpression trop brutale sur l'enveloppe cause un risque d'..........", ["Choisir...", "éclatement", "laminage"], "éclatement", "tr_t6_c2"),
            ("7. L'effort s'exerce de façon normale, donc .......... à l'aire interne.", ["Choisir...", "perpendiculaire", "tangentielle"], "perpendiculaire", "tr_t7_c2"),
            ("8. L'unité normalisée lue sur le cadran d'atelier est le ..........", ["Choisir...", "bar", "Pascal"], "bar", "tr_t8_c2"),
            ("9. La régulation automatique garantit la sécurité active du .......... routier.", ["Choisir...", "convoi", "manomètre"], "convoi", "tr_t9_c2"),
            ("10. Ce diagnostic prévient la détérioration prématurée des liaisons au ..........", ["Choisir...", "sol", "vide"], "sol", "tr_t10_c2")
        ]

    # Enregistrement final et synchronisation immédiate des variables en session
    if "ordre_quiz_tab7_tr_aleatoire" not in st.session_state:
        st.session_state.ordre_quiz_tab7_tr_aleatoire = questions_sources_tr
    if "champs_therm7_tr_clean" not in st.session_state:
        st.session_state.champs_therm7_tr_clean = trous_sources_tr
    col_g_tr, col_d_tr = st.columns([0.3, 0.7])
    
    with col_g_tr:
        st.markdown(f"##### Dossier Technique : {titre_tr}")
        st.info(enonce_tr)
        st.info(texte_bd_tr)
        
    with col_d_tr:
        st.markdown("##### Visualisation Technique")
        import os
        
        # 1. Rendu supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists(img_reelle_tr):
            st.image(img_reelle_tr, caption="Image réelle : Organe technique du convoi routier", width=300)
        else:
            st.caption("Illustration réelle indisponible ou manquante")
        
        # Boucle d'espacement des 20 lignes réglementaires pour descendre la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Rendu inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists(img_bd_tr):
            st.image(img_bd_tr, caption="Bande dessinée humoristique de l'incident routier", width=300)
        else:
            st.caption("Illustration caricaturale indisponible ou manquante")

    st.write("---")

    st.subheader("Laboratoire Virtuel : Simulateur de calcul Pneumatique")
    
    col_p1_tr, col_p2_tr = st.columns(2)
    if id_cas_tr == 1:
        with col_p1_tr:
            p_frein_bar = st.slider("Pression de freinage injectée (bars) :", 2.0, 10.0, 6.5, 0.5, key="sl_tr_c1_1_s7")
            diam_vase_type = st.slider("Taille de la membrane utile (cm²) :", 100, 300, 150, 10, key="sl_tr_c1_2_s7")
        f_frein_n = (p_frein_bar * 100000.0) * (diam_vase_type / 10000.0)
        with col_p2_tr:
            st.metric("Force de poussée sur la tige de commande (F)", f"{f_frein_n:.0f} N")
            st.latex(rf"F = P \cdot S = ({p_frein_bar} \cdot 10^5) \cdot ({diam_vase_type / 10000:.4f}) = {f_frein_n:,.0f}\text{{ N}}")
    else:
        with col_p1_tr:
            poids_essieu_kg = st.slider("Masse reposant sur l'essieu routier arrière (kg) :", 4000, 13000, 8000, 500, key="sl_tr_c2_1_s7")
        f_coussin = (float(poids_essieu_kg) * 9.81) / 2.0 # Réparti sur 2 coussins d'essieu
        pres_coussin_bar = (f_coussin / 0.045) / 100000.0  # Aire de contact moyenne fixée à 0.045 m²
        with col_p2_tr:
            st.metric("Pression interne requise par coussin de suspension", f"{pres_coussin_bar:.2f} bar")
            st.latex(rf"P = \frac{{F}}{{S}} = \frac{{{f_coussin:.0f}}}{{0{{,}}045}} = {pres_coussin_bar * 100000:,.0f}\text{{ Pa}}")

    st.write("---")

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique du Scénario Routier (10 pts)")
        if "ordre_quiz_tab7_tr_aleatoire" in st.session_state:
            for idx, q_d in enumerate(st.session_state.ordre_quiz_tab7_tr_aleatoire, 1):
                st.write(f"**{idx}.** {q_d['q']}")
                st.selectbox("", options=["Choisir..."] + q_d["options"], key=f"tr_q_{q_d['id']}_{idx}", disabled=verrou_at7, label_visibility="collapsed")
    with col_t:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 pts)")
        if "champs_therm7_tr_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_therm7_tr_clean, 1):
                enonce, choix, attendu, cle = ligne
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"tr_t_{cle}_{idx}", disabled=verrou_at7, label_visibility="collapsed")

    # =============================================================================
    # 7. LOGIQUE DE VALIDATION TECHNIQUE ET COMPILATION DU BILAN HTML
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_tr = st.checkbox("Je certifie avoir complété l'Atelier du Transport Routier.", key="chk_certif_at7_final_official_final", disabled=verrou_at7)
    
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_valider_at7_official_ultimate_final", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tr: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz
            score_q = 0.0
            if "ordre_quiz_tab7_tr_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_tab7_tr_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tr_q_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q += 1.0
            
            # 2. Correction automatique du Texte à trous
            score_t = 0.0
            if "champs_therm7_tr_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_therm7_tr_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tr_t_{cle}_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t += 1.0
            
            st.session_state.score_suite7_tr_p1 = round(float(score_q), 1)
            st.session_state.score_suite7_tr_p2 = round(float(score_t), 1)
            st.session_state.score_final_at7 = round(float(score_q + score_t), 1)
            st.session_state.suite_verrouille_tab7_tr = True
            st.rerun()

    # --- ARCHIVAGE DU RAPPORT ELECTRONIQUE SCELLÉ HTML ---
    if st.session_state.get("suite_verrouille_tab7_tr", False):
        from datetime import datetime
        scr1_t7 = st.session_state.get("score_suite7_tr_p1", 0.0)
        scr2_t7 = st.session_state.get("score_suite7_tr_p2", 0.0)
        tot_s_t7 = st.session_state.get("score_final_at7", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRANSPORT SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        html_export_tr7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Transport Routier - {n_eleve}</title>
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
                <p>Atelier 7 : Applications pneumatiques, freinage et répartition des masses au Transport Routier</p>
                <p>Scénario résolu : {titre_tr}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t7:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t7:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t7:.1f} / 10</strong><br>
                Note Totale de l'Atelier 7 : <strong>{tot_s_t7:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab7_tr_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_tr_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tr_q_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tr7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tr7 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm7_tr_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm7_tr_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]
                
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tr_t_{cle_variable}_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_tr7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tr7 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_tr7 = preparer_nom_fichier("Rapport_Application_Transport").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 7 (.HTML)",
            data=html_export_tr7,
            file_name=nom_fichier_html_tr7,
            mime="text/html",
            use_container_width=True,
        )



with tab8:
    st.header("Application dans le domaine Topographe Géomètre")
    st.write("Gérez les corrections d'erreurs systématiques liées à la dilatation thermique linéaire et la réfraction des signaux optiques.")

    # Styles CSS pour les légendes, bandeaux et alertes de l'Atelier 8
    st.markdown("""
    <style>
    .legende-geo { color: #1e3a8a; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-geo { background-color: #f1f5f9; border-left: 5px solid #475569; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #334155; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # 1. DÉCLARATION DE SÉCURITÉ ABSOLUE DU VERROU TOUT EN HAUT
    if "suite_verrouille_tab8_geo" not in st.session_state:
        st.session_state.suite_verrouille_tab8_geo = False
    verrou_at8 = st.session_state.suite_verrouille_tab8_geo

    # 2. INITIALISATION ET TIRAGE AU SORT D'EXERCICE MULTI-CAS AUTONOME
    if "cas_aleatoire_tab8" not in st.session_state:
        st.session_state.cas_aleatoire_tab8 = 1

    col_tirage_geo, col_statut_geo = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage_geo:
        if st.button("GÉNÉRER UN EXERCICE DE TOPOGRAPHIE AU HASARD", key="btn_tirage_hasard_at8_officiel_final", use_container_width=True, disabled=verrou_at8):
            import random
            actuel_geo = st.session_state.cas_aleatoire_tab8
            possibles_geo = [1, 2]
            filtrés_geo = [c for c in possibles_geo if c != actuel_geo]
            st.session_state.cas_aleatoire_tab8 = random.choice(filtrés_geo)
            
            # Nettoyage des anciennes clés pour forcer la mise à jour synchrone
            if "ordre_quiz_tab8_geo_aleatoire" in st.session_state: del st.session_state.ordre_quiz_tab8_geo_aleatoire
            if "champs_therm8_geo_clean" in st.session_state: del st.session_state.champs_therm8_geo_clean
            st.rerun()

    id_cas_geo = st.session_state.cas_aleatoire_tab8
    st.write(f"Dossier technique Topographie attribué : **Cas n°{id_cas_geo}**")

    # =============================================================================
    # 3. BASE DE DONNÉES DYNAMIQUES DES QUESTIONS, TROUS ET TEXTES (PAR CAS)
    # =============================================================================
    if id_cas_geo == 1:
        titre_geo = "Dilatation thermique linéaire de rubans d'arpentage en acier au soleil"
        enonce_geo = (
            "**Case 1 :** Un ruban d'arpentage métallique en acier subit un fort rayonnement solaire direct lors d'un chaînage de précision.\n\n"
            "**Case 2 :** L'élévation de température provoque un allongement millimétrique systématique de la structure solide par rapport à sa longueur nominale.\n\n"
            "**Case 3 :** Cette dérive géométrique non corrigée fausse la mesure bout à bout en sous-estimant la distance réelle du terrain.\n\n"
            "**Case 4 :** L'application du coefficient d'allongement linéaire (11.5 ppm/°C) corrige la mesure et valide le plan de bornage."
        )
        texte_bd_geo = (
            "**Bande Caricaturale de l'Incident : Le Ruban Élastique**\n\n"
            "**Case 1 :** Canicule : « Le thermomètre grimpe à 35 °C sur le goudron, les atomes du ruban solide s'agitent et s'écartent ! ».\n\n"
            "**Case 2 :** Piège métrologique : « Comme l'acier s'est allongé, ton ruban de 50 m mesure en fait 50.01 m sans que tu le saches ! ».\n\n"
            "**Case 3 :** Erreur : « En reportant plusieurs fois ce ruban trop long, ton calcul final affichera une distance trop courte ! ».\n\n"
            "**Case 4 :** Correction : « On injecte le Delta T dans l'équation linéaire, les millimètres parasites sont recalibrés ! »"
        )
        img_reelle_geo, img_bd_geo = "ruban_reel.jpg", "bd_ruban.jpg"
        
        questions_sources_geo = [
            {"id": "geo_q1_c1", "q": "Quel phénomène physique provoque l'augmentation de longueur d'un ruban d'acier exposé au soleil ?", "options": ["La dilatation thermique linéaire", "La réfraction atmosphérique", "La compressibilité fluide"], "rep": "La dilatation thermique linéaire"},
            {"id": "geo_q2_c1", "q": "À quelle température réglementaire standard de référence sont étalonnés les rubans en usine ?", "options": ["20 °C", "0 °C", "25 °C"], "rep": "20 °C"},
            {"id": "geo_q3_c1", "q": "Si un ruban s'allonge sous l'effet de la chaleur, la distance brute lue sur le terrain est :", "options": ["Inférieure à la distance réelle (sous-estimation)", "Supérieure à la distance réelle", "Strictement exacte"], "rep": "Inférieure à la distance réelle (sous-estimation)"},
            {"id": "geo_q4_c1", "q": "Quel alliage métallique stable est privilégié en topographie pour son coefficient de dilatation quasi nul ?", "options": ["L'Invar (acier-nickel)", "L'aluminium pur", "Le cuivre rouge"], "rep": "L'Invar (acier-nickel)"},
            {"id": "geo_q5_c1", "q": "Le coefficient d'allongement linéaire de l'acier standard est proche de :", "options": ["11.5 ppm/°C (ou 11.5×10⁻⁶ K⁻¹)", "1.2 ppm/°C", "150 ppm/°C"], "rep": "11.5 ppm/°C (ou 11.5×10⁻⁶ K⁻¹)"},
            {"id": "geo_q6_c1", "q": "L'erreur systématique due à la température relève d'une grandeur d'influence :", "options": ["Environnementale", "Humaine d'alignement", "Strictement accidentelle"], "rep": "Environnementale"},
            {"id": "geo_q7_c1", "q": "Un écart thermique positif (T > T_ref) engendre sur le ruban une correction numérique :", "options": ["Positive à rajouter", "Négative à retrancher", "Nulle"], "rep": "Positive à rajouter"},
            {"id": "geo_q8_c1", "q": "L'unité métrologique légale du système international pour exprimer une longueur est :", "options": ["Le mètre (m)", "Le millimètre (mm)", "Le pouce (inch)"], "rep": "Le mètre (m)"},
            {"id": "geo_q9_c1", "q": "Chaîner de manière répétée sans thermomètre introduit une incertitude de type :", "options": ["Systématique cumulable", "Aléatoire gaussienne", "Nulle"], "rep": "Systématique cumulable"},
            {"id": "geo_q10_c1", "q": "La contrainte de tension appliquée par le géomètre sur le ruban sert à contrer l'effet de :", "options": ["La flèche (ou chaînette due à la gravité)", "La réfraction optique", "La tension de vapeur"], "rep": "La flèche (ou chaînette due à la gravité)"}
        ]
        trous_sources_geo = [
            ("1. La hausse de température engendre la .......... thermique linéaire de l'acier.", ["Choisir...", "dilatation", "contraction"], "dilatation", "geo_t1_c1"),
            ("2. Les rubans de précision sont étalonnés en usine à la température de .......... °C.", ["Choisir...", "20", "0"], "20", "geo_t2_c1"),
            ("3. Un ruban dilaté devient trop long, ce qui .......... la distance brute lue.", ["Choisir...", "sous-estime", "surentend"], "sous-estime", "geo_t3_c1"),
            ("4. Pour s'affranchir de cette dérive, on utilise des mires en alliage d'..........", ["Choisir...", "Invar", "Laiton"], "Invar", "geo_t4_c1"),
            ("5. La correction métrologique calculée est directement proportionnelle au .......... L.", ["Choisir...", "Delta T", "Volume"], "Delta T", "geo_t5_c1"),
            ("6. Cette fluctuation physique de la matière modifie la longueur de la barre ..........", ["Choisir...", "solide", "fluide"], "solide", "geo_t6_c1"),
            ("7. La constante de dilatation de l'acier s'exprime en parties par .......... (ppm).", ["Choisir...", "million", "mille"], "million", "geo_t7_c1"),
            ("8. Appliquer la formule de recalibrage élimine l'erreur .......... systématique.", ["Choisir...", "thermique", "optique"], "thermique", "geo_t8_c1"),
            ("9. Un bornage officiel exige une précision rigoureuse des mesures de ..........", ["Choisir...", "distance", "pression"], "distance", "geo_t9_c1"),
            ("10. Ce soin garantit la parfaite exactitude géométrique des limites de .......... .", ["Choisir...", "propriété", "vitesse"], "propriété", "geo_t10_c1")
        ]
    else:
        titre_geo = "Déviation des faisceaux lasers par gradient de réfraction atmosphérique"
        enonce_geo = (
            "**Case 1 :** Le faisceau laser infrarouge d'une station totale traverse un gradient thermique vertical au-dessus du bitume.\n\n"
            "**Case 2 :** La variation de densité optique de l'air surchauffé courbe la trajectoire lumineuse rectiligne du signal.\n\n"
            "**Case 3 :** Ce phénomène de réfraction atmosphérique modifie infimement la célérité de l'onde et fausse la distance EDM.\n\n"
            "**Case 4 :** Le calcul de correction basé sur la pression (hPa) et la température rétablit l'indice de réfraction exact."
        )
        texte_bd_geo = (
            "**Bande Caricaturale de l'Incident : Le Laser Courbé**\n\n"
            "**Case 1 :** Mirage : « Le goudron surchauffé agit comme un miroir, l'air chaud ascendant tremble dans l'objectif ! ».\n\n"
            "**Case 2 :** Réfraction : « Les photons traversent des couches d'air de densités différentes, le rayon courbe sa course ! ».\n\n"
            "**Case 3 :** Erreur laser : « L'indice de réfraction n a changé, la vitesse du signal varie, le calcul de distance est faussé ! ».\n\n"
            "**Case 4 :** Calibrage : « Station météo lue ! Pression et température encodées, la station totale corrige sa visée ! »"
        )
        img_reelle_geo, img_bd_geo = "laser_reel.jpg", "bd_laser.jpg"

        questions_sources_geo = [
            {"id": "geo_q1_c2", "q": "Quel effet le gradient thermique de l'air a-t-il sur le faisceau laser de visée ?", "options": ["Il courbe sa trajectoire par réfraction", "Il augmente sa fréquence lumineuse", "Il stoppe totalement les photons"], "rep": "Il courbe sa trajectoire par réfraction"},
            {"id": "geo_q2_c2", "q": "Quelle grandeur physique de l'atmosphère modifie directement la vitesse de l'onde laser ?", "options": ["La densité optique de l'air (liée à T et P)", "La conductivité du sol en acier", "L'émissivité du prisme réflecteur"], "rep": "La densité optique de l'air (liée à T et P)"},
            {"id": "geo_q3_c2", "q": "Quel instrument météo portatif le topographe utilise-t-on pour corriger l'indice n ?", "options": ["Un thermo-baromètre", "Un dynamomètre", "Un manomètre hydraulique"], "rep": "Un thermo-baromètre"},
            {"id": "geo_q4_c2", "q": "La vitesse de la lumière dans le vide absolu (c) est une constante égale à environ :", "options": ["300 000 km/s", "1 500 m/s", "340 m/s"], "rep": "300 000 km/s"},
            {"id": "geo_q5_c2", "q": "Dans un air plus chaud et moins dense à pression constante, la vitesse du signal laser :", "options": ["Augmente légèrement", "Diminue fortement", "Reste parfaitement identique au vide"], "rep": "Augmente légèrement"},
            {"id": "geo_q6_c2", "q": "L'abréviation EDM intégrée aux stations totales de topographie signifie :", "options": ["Electronic Distance Measurement", "Équilibre Des Masses", "Érosion Des Molécules"], "rep": "Electronic Distance Measurement"},
            {"id": "geo_q7_c2", "q": "La correction atmosphérique appliquée par l'appareil s'exprime généralement en :", "options": ["ppm (parties par million)", "Pascals", "Newtons"], "rep": "ppm (parties par million)"},
            {"id": "geo_q8_c2", "q": "Une forte réfraction courbe le rayon vers le bas, faisant apparaître la cible :", "options": ["Plus haute qu'elle ne l'est réellement", "Plus basse qu'elle ne l'est réellement", "Strictement à sa vraie cote"], "rep": "Plus haute qu'elle ne l'est réellement"},
            {"id": "geo_q9_c2", "q": "L'indice de réfraction de l'air standard au niveau de la mer est de l'ordre de :", "options": ["1.0003", "1.33", "2.42"], "rep": "1.0003"},
            {"id": "geo_q10_c2", "q": "Travailler au-dessus d'une surface asphaltée en plein après-midi accentue les erreurs de :", "options": ["Scintillation et mirage optique", "Pesanteur locale", "Fléchissement de flèche"], "rep": "Scintillation et mirage optique"}
        ]
        trous_sources_geo = [
            ("1. Le goudron surchauffé modifie l'indice de .......... de l'air de surface.", ["Choisir...", "réfraction", "conduction"], "réfraction", "geo_t1_c2"),
            ("2. L'air chaud ascendant modifie la vitesse du faisceau .......... de visée.", ["Choisir...", "laser", "sonore"], "laser", "geo_t2_c2"),
            ("3. La variation de la densité moléculaire courbe la trajectoire de l'.......... optique.", ["Choisir...", "onde", "fluide"], "onde", "geo_t3_c2"),
            ("4. Pour corriger l'EDM, le technicien relève la pression avec un .......... .", ["Choisir...", "baromètre", "dynamomètre"], "baromètre", "geo_t4_c2"),
            ("5. La déviation due à l'indice n de l'air constitue une erreur .......... .", ["Choisir...", "atmosphérique", "humaine"], "atmosphérique", "geo_t5_c2"),
            ("6. Le signal infrarouge traverse un milieu gazeux non .......... verticalement.", ["Choisir...", "homogène", "liquide"], "homogène", "geo_t6_c2"),
            ("7. Entrer la température de service permet à la station de recalculer la ..........", ["Choisir...", "célérité", "viscosité"], "célérité", "geo_t7_c2"),
            ("8. La correction d'indice s'injecte de façon automatique en .......... par million.", ["Choisir...", "parties", "grammes"], "parties", "geo_t8_c2"),
            ("9. Un relevé de nivellement l'après-midi subit les effets de .......... visuelle.", ["Choisir...", "scintillation", "cavitation"], "scintillation", "geo_t9_c2"),
            ("10. Ce traitement élimine l'erreur systématique pour stabiliser les cotes de .......... .", ["Choisir...", "visée", "calage"], "visée", "geo_t10_c2")
        ]

    # Enregistrement final et synchronisation immédiate des variables en session
    if "ordre_quiz_tab8_geo_aleatoire" not in st.session_state:
        st.session_state.ordre_quiz_tab8_geo_aleatoire = questions_sources_geo
    if "champs_therm8_geo_clean" not in st.session_state:
        st.session_state.champs_therm8_geo_clean = trous_sources_geo

    col_g_geo, col_d_geo = st.columns([0.3, 0.7])
    
    with col_g_geo:
        st.markdown(f"##### Dossier Technique : {titre_geo}")
        st.info(enonce_geo)
        st.info(texte_bd_geo)
        
    with col_d_geo:
        st.markdown("##### Visualisation Technique")
        import os
        
        # 1. Rendu supérieur : Image réelle (Largeur fixe 300px)
        if os.path.exists(img_reelle_geo):
            st.image(img_reelle_geo, caption="Image réelle : Relevé instrumental sur le terrain", width=300)
        else:
            st.caption("Illustration réelle indisponible ou manquante")
        
        # Boucle d'espacement des 20 lignes réglementaires pour descendre la caricature
        for _ in range(20):
            st.write("")
        
        # 2. Rendu inférieur : Caricature de BD (Largeur fixe 300px)
        if os.path.exists(img_bd_geo):
            st.image(img_bd_geo, caption="Bande dessinée humoristique de l'arpentage", width=300)
        else:
            st.caption("Illustration caricaturale indisponible ou manquante")

    st.write("---")

    st.subheader("Laboratoire Virtuel : Simulateur Topographique Éléments d'Influence")
    
    col_p1_geo, col_p2_geo = st.columns(2)
    if id_cas_geo == 1:
        with col_p1_geo:
            temp_sol_c = st.slider("Température mesurée sur le ruban d'acier (°C) :", 10, 60, 35, 1, key="sl_geo_c1_1_s8")
            dist_nominale_m = st.slider("Distance nominale mesurée de la ligne (m) :", 20, 200, 100, 10, key="sl_geo_c1_2_s8")
        # Formule : Delta L = L0 * alpha * (T - T_ref) avec alpha = 11.5 ppm/K
        delta_l = float(dist_nominale_m) * 11.5e-6 * (float(temp_sol_c) - 20.0)
        with col_p2_geo:
            st.metric("Allongement thermique cumulé du ruban (Delta L)", f"+{delta_l*1000:.1f} mm")
            st.latex(rf"\Delta L = L_0 \cdot \alpha \cdot \Delta T = {dist_nominale_m} \cdot (11{{,}}5 \cdot 10^{{-6}}) \cdot ({temp_sol_c} - 20) = {delta_l*1000:.2f}\text{{ mm}}")
    else:
        with col_p1_geo:
            temp_air_c = st.slider("Température moyenne sur l'axe de visée (°C) :", -10, 45, 15, 1, key="sl_geo_c2_1_s8")
            pres_atm_hpa = st.slider("Pression atmosphérique relevée (hPa) :", 950, 1050, 1013, 5, key="sl_geo_c2_2_s8")
        # Formule simplifiée de Barrel & Sears pour l'indice n de l'air
        ppm_corr = 273.15 - (0.2924 * float(pres_atm_hpa)) / (1.0 + 0.00366 * float(temp_air_c))
        with col_p2_geo:
            st.metric("Correction d'indice atmosphérique EDM", f"{ppm_corr:.1f} ppm (mm/km)")
            st.latex(rf"\text{{Corr}} = 273{{,}}15 - \frac{{0{{,}}2924 \cdot {pres_atm_hpa}}}{{1 + 0{{,}}00366 \cdot {temp_air_c}}} = {ppm_corr:.1f}\text{{ ppm}}")

    st.write("---")

    col_q, col_t = st.columns(2)
    with col_q:
        st.markdown("##### Quiz Technique du Scénario Géomètre (10 pts)")
        if "ordre_quiz_tab8_geo_aleatoire" in st.session_state:
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab8_geo_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox(
                    "", 
                    options=["Choisir..."] + q_data["options"], 
                    key=f"geo_q_{q_data['id']}_{idx}", 
                    disabled=verrou_at8, 
                    label_visibility="collapsed"
                )
    with col_t:
        st.markdown("##### Synthèse de l'Atelier 8 (Texte à trous - 10 pts)")
        if "champs_therm8_geo_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_therm8_geo_clean, 1):
                enonce, choix, attendu, cle = ligne
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox(
                        "", 
                        choix, 
                        key=f"geo_t_{cle}_{idx}", 
                        disabled=verrou_at8, 
                        label_visibility="collapsed"
                    )

    # =============================================================================
    # 7. LOGIQUE DE VALIDATION TECHNIQUE ET COMPILATION DU BILAN HTML
    # =============================================================================
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 8")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_geo = st.checkbox(
        "Je certifie avoir complété l'Atelier d'application Topographie.", 
        key="chk_certif_at8_final_official_final", 
        disabled=verrou_at8
    )
    
    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", 
        key="btn_valider_at8_official_ultimate_final", 
        use_container_width=True, 
        disabled=verrou_at8
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_geo: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz
            score_q = 0.0
            if "ordre_quiz_tab8_geo_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_tab8_geo_aleatoire, 1):
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"geo_q_{q_item['id']}_"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q += 1.0
            
            # 2. Correction automatique du Texte à trous
            score_t = 0.0
            if "champs_therm8_geo_clean" in st.session_state:
                for idx, ligne in enumerate(st.session_state.champs_therm8_geo_clean, 1):
                    cle = ligne[-1]
                    attendu = ligne
                    saisie_t = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"geo_t_{cle}_"):
                            saisie_t = st.session_state[k]
                            break
                    if str(saisie_t).strip() == str(attendu).strip(): 
                        score_t += 1.0
            
            st.session_state.score_suite8_geo_p1 = round(float(score_q), 1)
            st.session_state.score_suite8_geo_p2 = round(float(score_t), 1)
            st.session_state.score_final_at8 = round(float(score_q + score_t), 1)
            st.session_state.suite_verrouille_tab8_geo = True
            st.rerun()

    # --- ARCHIVAGE DU RAPPORT ELECTRONIQUE SCELLÉ HTML ---
    if st.session_state.get("suite_verrouille_tab8_geo", False):
        from datetime import datetime
        scr1_t8 = st.session_state.get("score_suite8_geo_p1", 0.0)
        scr2_t8 = st.session_state.get("score_suite8_geo_p2", 0.0)
        tot_s_t8 = st.session_state.get("score_final_at8", 0.0)
        timestamp_suite8 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TOPOGRAPHIE SCELLÉ | Note de session : {tot_s_t8:.1f} / 20")

        html_export_geo8 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Topographe Géomètre - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #475569; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 8 : Métrologie appliquée, corrections linéaires et réfraction chez le Géomètre</p>
                <p>Scénario résolu : {titre_geo}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t8:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t8:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t8:.1f} / 10</strong><br>
                Note Totale de l'Atelier 8 : <strong>{tot_s_t8:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab8_geo_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab8_geo_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"geo_q_{q_item['id']}_"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_geo8 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_geo8 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm8_geo_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm8_geo_clean, 1):
                enonce_texte, choix_texte, attendu_texte, cle_variable = ligne
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"geo_t_{cle_variable}_"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_geo8 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_geo8 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_geo8 = preparer_nom_fichier("Rapport_Application_Topographie").replace(".txt", ".html")
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 8 (.HTML)",
            data=html_export_geo8,
            file_name=nom_fichier_html_geo8,
            mime="text/html",
            use_container_width=True,
        )






















    




















