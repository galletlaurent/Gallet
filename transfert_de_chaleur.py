# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application transfert de chaleur",
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
import sys
from PIL import Image
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application thermo")
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
    "La température",
    "La chaleur",
    "Les modes de transfert thermique",
    "Les conducteurs et les isolants thermiques",
    "La quantité de chaleur",
    "Coefficient de transmission thermique",
    "La résistance thermique",
    "Transfert de chaleur à travers une paroi composée d'un seul matériau",
    "Transfert de chaleur à travers une paroi composée de plusieurs matériaux",
    "Application dans le domaine de la maintenance",
    "Application dans le domaine des TP",
    "Application dans le domaine de la conduite routière",
    "Application dans le domaine des géomètres",    
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
tab9 = onglets[9] 
tab10 = onglets[10]
tab11 = onglets[11] 
tab12 = onglets[12]
tab13 = onglets[13] 
tab14 = onglets[14]

def afficher_atelier_chaleur_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (La chaleur) sur deux colonnes."""
    import random

    # # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE ET HISTORIQUE DE LA CHALEUR
    questions_therm3_sources = [
        {
            "id": "qt3_1",
            "q": "Quelle est la définition scientifique exacte de la chaleur ?",
            "options": ["Un transfert d'énergie thermique entre deux corps", "Le degré d'agitation interne des molécules", "Un fluide immatériel pesable"],
            "rep": "Un transfert d'énergie thermique entre deux corps",
        },
        {
            "id": "qt3_2",
            "q": "Quelle unité historique mesurait la quantité de chaleur nécessaire pour élever d'un degré un gramme d'eau ?",
            "options": ["La calorie", "Le Joule", "Le Watt"],
            "rep": "La calorie",
        },
        {
            "id": "qt3_3",
            "q": "Quel savant a mis en évidence la chaleur latente lors de la fusion de la glace ?",
            "options": ["Joseph Black", "James Watt", "Joseph Fourier"],
            "rep": "Joseph Black",
        },
        {
            "id": "qt3_4",
            "q": "Quelle lettre majuscule symbolise universellement la quantité de chaleur dans les équations physiques ?",
            "options": ["Q", "T", "W"],
            "rep": "Q",
        },
        {
            "id": "qt3_5",
            "q": "Dans quelle expérience Joule a-t-il lié le travail mécanique à l'élévation de température ?",
            "options": ["L'expérience des palettes brassant l'eau", "L'observation du forage des canons", "L'invention de la machine à feu"],
            "rep": "L'expérience des palettes brassant l'eau",
        },
        {
            "id": "qt3_6",
            "q": "Comment qualifie-t-on un transfert de chaleur s'effectuant à température constante lors d'un changement d'état ?",
            "options": ["Un transfert de chaleur latente", "Un transfert de chaleur sensible", "Un flux par conduction pure"],
            "rep": "Un transfert de chaleur latente",
        },
        {
            "id": "qt3_7",
            "q": "Que subit la température d'un corps pur lors d'un apport de chaleur sensible sans changement d'état ?",
            "options": ["Elle augmente obligatoirement", "Elle reste strictement constante", "Elle diminue de moitié"],
            "rep": "Elle augmente obligatoirement",
        },
        {
            "id": "qt3_8",
            "q": "Quel physicien a réfuté le fluide calorique en observant la chaleur produite par le frottement mécanique lors du forage de canons ?",
            "options": ["Comte Rumford", "Antoine Lavoisier", "Sadi Carnot"],
            "rep": "Comte Rumford",
        },
        {
            "id": "qt3_9",
            "q": "Lorsque deux corps en contact atteignent la même température, le transfert thermique global est :",
            "options": ["Strictement nul (Équilibre)", "Infini et instantané", "Uniquement descendant"],
            "rep": "Strictement nul (Équilibre)",
        },
        {
            "id": "qt3_10",
            "q": "La formule reliant la chaleur sensible à la masse et à la capacité thermique s'exprime par :",
            "options": ["Q = m.c.(Tf - Ti)", "Q = m.L", "Q = U.A.dT"],
            "rep": "Q = m.c.(Tf - Ti)",
        }
    ]

    # Initialisation de l'ordre aléatoire des questions du Quiz
    if "ordre_quiz_tab3_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm3_sources)
        st.session_state.ordre_quiz_tab3_therm_aleatoire = questions_therm3_sources

    # # 2. BASE DE DONNÉES DU TEXTE À TROUS DE LA CHALEUR
    if "champs_therm3_clean" not in st.session_state:
        st.session_state.champs_therm3_clean = [
            (
                "1. La chaleur désigne un .......... d'énergie entre deux systèmes.",
                ["Choisir...", "transfert", "fluide"],
                "transfert",
                "therm3_t1",
            ),
            (
                "2. L'unité légale de la quantité de chaleur est le ..........",
                ["Choisir...", "Joule", "Calorie"],
                "Joule",
                "therm3_t2",
            ),
            (
                "3. Joseph Black a découvert la chaleur .......... liée aux changements d'état.",
                ["Choisir...", "latente", "sensible"],
                "latente",
                "therm3_t3",
            ),
            (
                "4. L'élévation de température d'un corps sans changement d'état met en jeu de la chaleur ..........",
                ["Choisir...", "sensible", "latente"],
                "sensible",
                "therm3_t4",
            ),
            (
                "5. L'expérience des .......... de Joule a prouvé la conservation de l'énergie.",
                ["Choisir...", "palettes", "vitres"],
                "palettes",
                "therm3_t5",
            ),
            (
                "6. La chaleur se déplace spontanément du corps chaud vers le corps ..........",
                ["Choisir...", "froid", "isole"],
                "froid",
                "therm3_t6",
            ),
            (
                "7. Le symbole mathématique de la quantité de chaleur est la lettre ..........",
                ["Choisir...", "Q", "W"],
                "Q",
                "therm3_t7",
            ),
            (
                "8. Le Comte Rumford a réfuté le calorique en forant des ..........",
                ["Choisir...", "canons", "tuyaux"],
                "canons",
                "therm3_t8",
            ),
            (
                "9. L'absence de transfert thermique entre deux corps en contact indique l'.......... thermique.",
                ["Choisir...", "équilibre", "blocage"],
                "équilibre",
                "therm3_t9",
            ),
            (
                "10. La constante 'c' de l'équation correspond à la .......... thermique massique.",
                ["Choisir...", "capacité", "conductivité"],
                "capacité",
                "therm3_t10",
            ),
        ]

    # # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 3 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at3_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm3_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm3_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )


def afficher_atelier_temperature_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (La température) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE ET HISTORIQUE DE LA TEMPÉRATURE
    questions_therm2_sources = [
        {
            "id": "qt2_1",
            "q": "Qui a inventé le premier instrument de mesure thermique de l'histoire, appelé le thermoscope ?",
            "options": ["Galilée", "Anders Celsius", "Lord Kelvin"],
            "rep": "Galilée",
        },
        {
            "id": "qt2_2",
            "q": "Quelle unité du Système International (SI) est l'unité légale et absolue de la température ?",
            "options": ["Le Kelvin", "Le degré Celsius", "Le degré Fahrenheit"],
            "rep": "Le Kelvin",
        },
        {
            "id": "qt2_3",
            "q": "Quelle température Celsius correspond exactement au zéro absolu (0 K) ?",
            "options": ["-273,15 °C", "0 °C", "-100 °C"],
            "rep": "-273,15 °C",
        },
        {
            "id": "qt2_4",
            "q": "Sur quel phénomène physique repose le fonctionnement des thermomètres analogiques à cadran ou à colonne ?",
            "options": ["La dilatation thermique", "La fusion moléculaire", "La conduction électrique"],
            "rep": "La dilatation thermique",
        },
        {
            "id": "qt2_5",
            "q": "Quelle température de référence fixe le point d'ébullition de l'eau pure sous une pression atmosphérique normale en échelle Celsius ?",
            "options": ["100 °C", "0 °C", "32 °C"],
            "rep": "100 °C",
        },
        {
            "id": "qt2_6",
            "q": "Pourquoi le mercure est-il aujourd'hui interdit dans la fabrication des thermomètres grand public ?",
            "options": ["En raison de sa haute toxicité", "Parce qu'il ne se dilate pas assez", "Parce qu'il coûte trop cher à produire"],
            "rep": "En raison de sa haute toxicité",
        },
        {
            "id": "qt2_7",
            "q": "Quel fluide coloré remplace très couramment le mercure dans les thermomètres domestiques classiques ?",
            "options": ["L'alcool (Éthanol)", "L'huile de moteur", "L'eau distillée"],
            "rep": "L'alcool (Éthanol)",
        },
        {
            "id": "qt2_8",
            "q": "Dans l'échelle Fahrenheit, à quelle valeur numérique correspond le point de fusion de la glace ?",
            "options": ["32 °F", "0 °F", "100 °F"],
            "rep": "32 °F",
        },
        {
            "id": "qt2_9",
            "q": "Au niveau microscopique, que mesure concrètement la température d'un corps ?",
            "options": ["Le degré d'agitation de ses molécules", "La quantité totale de matière", "Le volume de son enveloppe externe"],
            "rep": "Le degré d'agitation de ses molécules",
        },
        {
            "id": "qt2_10",
            "q": "Comment appelle-t-on le capteur électronique industriel qui utilise la variation de sa résistance avec la température (ex: Pt100) ?",
            "options": ["Une thermistance", "Un thermocouple", "Un pyromètre optique"],
            "rep": "Une thermistance",
        },
    ]

    if "ordre_quiz_tab2_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm2_sources)
        st.session_state.ordre_quiz_tab2_therm_aleatoire = questions_therm2_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DE LA TEMPÉRATURE
    if "champs_therm2_clean" not in st.session_state:
        st.session_state.champs_therm2_clean = [
            (
                "1. Galilée a conçu le premier appareil de repérage nommé le ..........",
                ["Choisir...", "thermoscope", "baromètre"],
                "thermoscope",
                "therm2_t1",
            ),
            (
                "2. Le thermomètre à mercure a été stabilisé par le physicien ..........",
                ["Choisir...", "Fahrenheit", "Celsius"],
                "Fahrenheit",
                "therm2_t2",
            ),
            (
                "3. L'échelle centésimale fixant le zéro sur la glace fondante revient à ..........",
                ["Choisir...", "Celsius", "Kelvin"],
                "Celsius",
                "therm2_t3",
            ),
            (
                "4. Au niveau atomique, la température traduit le niveau d'.......... des particules.",
                ["Choisir...", "agitation", "blocage"],
                "agitation",
                "therm2_t4",
            ),
            (
                "5. L'absence totale de mouvement moléculaire définit le zéro ..........",
                ["Choisir...", "absolu", "relatif"],
                "absolu",
                "therm2_t5",
            ),
            (
                "6. Le fonctionnement d'un thermomètre mécanique classique utilise la ..........",
                ["Choisir...", "dilatation", "compression"],
                "dilatation",
                "therm2_t6",
            ),
            (
                "7. L'éthanol coloré est un liquide employé pour mesurer les températures ..........",
                ["Choisir...", "domestiques", "industrielles"],
                "domestiques",
                "therm2_t7",
            ),
            (
                "8. Pour passer des degrés Celsius aux Kelvins, on ajoute la valeur ..........",
                ["Choisir...", "273,15", "100"],
                "273,15",
                "therm2_t8",
            ),
            (
                "9. Un capteur industriel basé sur la soudure de deux métaux est un ..........",
                ["Choisir...", "thermocouple", "pyromètre"],
                "thermocouple",
                "therm2_t9",
            ),
            (
                "10. La mesure sans contact à distance d'un corps chaud utilise le rayonnement ..........",
                ["Choisir...", "infrarouge", "ultraviolet"],
                "infrarouge",
                "therm2_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 2 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at2_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm2_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm2_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )




def afficher_atelier_histoire_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ HISTORIQUE THERMIQUE
    questions_therm1_sources = [
        {
            "id": "qth1",
            "q": "Quel célèbre chimiste français du 18e siècle considérait la chaleur comme un fluide immatériel nommé le calorique ?",
            "options": [
                "Antoine Lavoisier",
                "Sadi Carnot",
                "James Prescott Joule",
            ],
            "rep": "Antoine Lavoisier",
        },
        {
            "id": "qth2",
            "q": "Quelle grandeur physique Guillaume Amontons puis Lord Kelvin ont-ils théorisé en fixant l'absence totale d'agitation moléculaire ?",
            "options": ["Le zéro absolu", "La capacité thermique", "Le flux de conduction"],
            "rep": "Le zéro absolu",
        },
        {
            "id": "qth3",
            "q": "Quel ingénieur français a publié en 1824 l'ouvrage fondateur décrivant la puissance motrice du feu et le cycle des machines thermiques ?",
            "options": [
                "Sadi Carnot",
                "Joseph Fourier",
                "Anders Celsius",
            ],
            "rep": "Sadi Carnot",
        },
        {
            "id": "qth4",
            "q": "Quelle expérience célèbre de James Prescott Joule en 1843 a permis de lier définitivement le travail mécanique à la chaleur ?",
            "options": ["L'expérience des palettes brassant l'eau", "L'invention du thermomètre à mercure", "La découverte du rayonnement infrarouge"],
            "rep": "L'expérience des palettes brassant l'eau",
        },
        {
            "id": "qth5",
            "q": "Quel mathématicien et physicien français a formulé en 1822 la loi mathématique rigoureuse de la conduction thermique ?",
            "options": ["Joseph Fourier", "Antoine Lavoisier", "Benjamin Thompson"],
            "rep": "Joseph Fourier",
        },
        {
            "id": "qth6",
            "q": "Quel astronome suédois a proposé en 1742 une échelle de température centésimale basée sur les points de fusion et d'ébullition de l'eau ?",
            "options": ["Anders Celsius", "Daniel Gabriel Fahrenheit", "William John Macquorn Rankine"],
            "rep": "Anders Celsius",
        },
        {
            "id": "qth7",
            "q": "En quelle année Lord Kelvin a-t-il proposé son échelle de température thermodynamique absolue commençant à zéro ?",
            "options": ["1848", "1789", "1912"],
            "rep": "1848",
        },
        {
            "id": "qth8",
            "q": "Quel physicien germano-hollandais a perfectionné le thermomètre en utilisant du mercure et une échelle fixant la glace à 32 degrés ?",
            "options": ["Daniel Gabriel Fahrenheit", "Anders Celsius", "William Thomson"],
            "rep": "Daniel Gabriel Fahrenheit",
        },
        {
            "id": "qth9",
            "q": "Selon la thermodynamique moderne, quelle est la nature microscopique de la chaleur ?",
            "options": [
                "Une agitation désordonnée des atomes",
                "Un fluide pesant circulant entre les corps",
                "Un déplacement d'électrons libres",
            ],
            "rep": "Une agitation désordonnée des atomes",
        },
        {
            "id": "qth10",
            "q": "Quelle unité du Système International (SI), officielle depuis 1948, mesure à la fois le travail, l'énergie et la quantité de chaleur ?",
            "options": [
                "Le Joule",
                "La Calorie",
                "Le Watt",
            ],
            "rep": "Le Joule",
        },
    ]

    # Initialisation de l'ordre aléatoire des questions dans la session Streamlit
    if "ordre_quiz_tab1_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm1_sources)
        st.session_state.ordre_quiz_tab1_therm_aleatoire = questions_therm1_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS HISTORIQUE THERMIQUE
    if "champs_therm1_clean" not in st.session_state:
        st.session_state.champs_therm1_clean = [
            (
                "1. Au 18e siècle, Lavoisier définit la chaleur comme un fluide appelé ..........",
                ["Choisir...", "calorique", "phlogistique"],
                "calorique",
                "therm1_t1",
            ),
            (
                "2. La révolution industrielle du 19e siècle repose sur les machines ..........",
                ["Choisir...", "thermiques", "hydrauliques"],
                "thermiques",
                "therm1_t2",
            ),
            (
                "3. La découverte de Joule en 1843 montre que la chaleur est une ..........",
                ["Choisir...", "énergie", "matière"],
                "énergie",
                "therm1_t3",
            ),
            (
                "4. Le modèle de Fourier décrit mathématiquement le transfert par ..........",
                ["Choisir...", "conduction", "rayonnement"],
                "conduction",
                "therm1_t4",
            ),
            (
                "5. L'échelle de température absolue basée sur le zéro absolu revient à ..........",
                ["Choisir...", "Kelvin", "Celsius"],
                "Kelvin",
                "therm1_t5",
            ),
            (
                "6. Un corps chaud dont les molécules s'agitent possède de l'énergie ..........",
                ["Choisir...", "thermique", "potentielle"],
                "thermique",
                "therm1_t6",
            ),
            (
                "7. L'étude de la chaleur et de ses conversions en travail est la ..........",
                ["Choisir...", "thermodynamique", "cinématique"],
                "thermodynamique",
                "therm1_t7",
            ),
            (
                "8. Sadi Carnot a mis en évidence le rendement maximal d'un ..........",
                ["Choisir...", "cycle", "fluide"],
                "cycle",
                "therm1_t8",
            ),
            (
                "9. L'unité historique de la chaleur, avant le Joule, était la ..........",
                ["Choisir...", "calorie", "frigorie"],
                "calorie",
                "therm1_t9",
            ),
            (
                "10. La mesure de la température s'est développée grâce au ..........",
                ["Choisir...", "thermomètre", "manomètre"],
                "thermomètre",
                "therm1_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique et Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at1_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm1_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm1_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )

                
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
    st.header("Histoire et Découverte de la Thermique")
    st.write(
        "Découvrez comment l'humanité a compris la nature de la chaleur, passant d'un fluide imaginaire à une agitation microscopique :"
    )

    # =============================================================================
    # SECTION HISTORIQUE ET SCIENTIFIQUES CLÉS
    # =============================================================================
    col_hist_1, col_hist_img1 = st.columns(2)
    
    with col_hist_1:
        st.markdown("##### La théorie du « Calorique »")
        st.write(
            "Pendant longtemps, les scientifiques comme Antoine Lavoisier pensaient que la chaleur "
            "était un fluide invisible et immatériel appelé le **calorique**. Selon cette théorie, "
            "un corps chaud possédait simplement plus de ce fluide qu'un corps froid."
        )

    with col_hist_img1:

        if os.path.exists("Lavoisier.jpg"):
            st.image(
                "Lavoisier.jpg",
                caption="Antoine Lavoisier"
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    col_hist_2, col_hist_img2 = st.columns(2)
    
    with col_hist_2:
        st.markdown("##### La révolution thermodynamique")
        st.write(
            "Au XIXe siècle, des physiciens comme James Prescott Joule et Sadi Carnot démontrent que "
            "la chaleur n'est pas un fluide, mais une **forme d'énergie** liée à l'agitation des "
            "atomes. C'est la naissance de la thermodynamique moderne, essentielle pour l'industrie, "
            "le bâtiment et la maintenance."
        )
    with col_hist_img2:
        col_hist_img21, col_hist_img22 = st.columns(2)
        with col_hist_img21:
            if os.path.exists("Joule.jpg"):
                st.image(
                    "Joule.jpg",
                    caption="James Prescott Joule",
                )
            else:
                st.warning(
                    "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )

        with col_hist_img22:
            if os.path.exists("Carnot.jpg"):
                st.image(
                    "Carnot.jpg",
                    caption=" Sadi Carnot ",
                )
            else:
                st.warning(
                    "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )
                  
    st.write("---")

    # =============================================================================
    # BANDE DESSINÉE HUMORISTIQUE EN 4 CASES : LE DRAME DES CALORIES PERDUES
    # =============================================================================
    col_gauche_texte, col_droite_img = st.columns(2)

    with col_gauche_texte:
        st.write(
            "**La BD humoristique textuelle : Le drame des calories perdues**")
        
        st.info(
            "**Cas 1 :** Un groupe d'atomes à l'intérieur d'une maison chauffée est tranquillement installé "
            "dans la structure de la paroi. Ils vibrent joyeusement ensemble et discutent avec leurs voisins : "
            "« Tout va bien les gars, la parfaite cohésion est là, on forme un bloc d'isolation indestructible ! ».\n\n"
            
            "**Cas 2 :** Une baisse brutale des températures survient à l'extérieur. L'air froid hivernal, "
            "très gourmand, attrape l'atome de la paroi par le bras et crie : "
            "« Hé toi ! Donne-moi tes charges ! Tes précieux joules d'énergie m'intéressent grandement ! ».\n\n"
            
            "**Cas 3 :** L'atome de la paroi, dépouillé de son énergie de protection, commence à se refroidir "
            "et à se détacher du réseau. Il panique en voyant sa température baisser : "
            "« Oh non ! Je viens de subir un transfert thermique ! Je ne suis plus un atome chaud et agité, "
            "je me transforme en conducteur froid ! C'est la liquéfaction ! ».\n\n"
            
            "**Cas 4 :** La chaleur évadée désormais flotte dans l'atmosphère froide sous forme de perte pure, "
            "laissant un trou béant dans le bilan énergétique de la poutre. Les atomes de froid s'enfuient "
            "en ricanant avec leur butin : "
            "« Affaire classée ! Encore un système chauffé terrassé par notre pouvoir absorbant ! »."
        )

    with col_droite_img:

        if os.path.exists("chaleur_caricature.jpg"):
            st.image(
                "chaleur_caricature.jpg",
                caption="Illustration humoristique du drame des calories perdues",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
            
    st.write("---")
    if "suite_verrouille_tab1_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab1_therm = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_therm

    # Affichage du module de questions spécifique à l'histoire de la thermique
    afficher_atelier_histoire_verrouille(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique.",
        key="check_certif_therm1_final_net",
        disabled=verrou_at1,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1",
        key="btn_export_suite1_therm_official",
        use_container_width=True,
        disabled=verrou_at1,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz Technique
            score_q1 = 0.0
            if "ordre_quiz_tab1_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatisée sécurisée du Texte à trous
            score_t1 = 0.0
            if "champs_therm1_clean" in st.session_state:
                for ligne in st.session_state.champs_therm1_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm1_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t1 += 1.0

            # 3. Sauvegarde des scores et verrouillage automatique de la session
            st.session_state.score_suite1_therm_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_therm_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_therm = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_therm = True
            st.rerun()

    # --- COMPILATION DU BILAN FICHIER HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_therm", False):
        from datetime import datetime
        scr1_t1 = st.session_state.get("score_suite1_therm_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_therm_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_therm", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20"
        )

        html_export_therm1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 1 : Contexte historique des transferts thermiques et évolution des modèles</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
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

        if "ordre_quiz_tab1_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm1_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement natif pour le fichier HTML compilé (.html)
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 1 (.HTML)",
            data=html_export_therm1,
            file_name=preparer_nom_fichier("Atelier_1_Historique").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )



with tab2:
    st.header("La Température et la Mesure de l'Agitation Thermique")
    st.write(
        "Découvrez l'histoire des échelles de température, les inventeurs des premiers capteurs, "
        "et observez en direct le phénomène physique de la dilatation volumique des fluides :"
    )

    # =============================================================================
    # SECTION HISTORIQUE : LES ENCIENS MODÈLES ET LES HOMMES
    # =============================================================================
    col_t2_h1, col_t2_h2 = st.columns(2)
    
    with col_t2_h1:
        st.markdown("##### Les Pionniers du Thermomètre")
        st.write(
            "**Galilée (1592) :** Il invente le thermoscope, un tube de verre où l'air se dilate et déplace de l'eau, "
            "mais l'absence d'échelle graduée fixe empêche une mesure quantitative précise.\n\n"
            "**Daniel Gabriel Fahrenheit (1714) :** Il révolutionne la métrologie en fabriquant le premier "
            "thermomètre fiable à mercure. Il fixe son zéro en mélangeant de la glace, de l'eau et du sel d'ammonium."
        )

        col_t21_h11, col_t21_h21 = st.columns(2)
        
        with col_t21_h11:
            col_t21_h111, col_t21_h211 = st.columns(2)
            with col_t21_h111:
                if os.path.exists("Galilee.jpg"):
                    st.image(
                        "Galilee.jpg",
                        caption="Galilée",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Galilee.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

            with col_t21_h211:
                if os.path.exists("thermoscope.jpg"):
                    st.image(
                        "thermoscope.jpg",
                        caption="thermoscope de Galilée",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'thermoscope.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

        with col_t21_h21:
            col_t21_h311, col_t21_h411 = st.columns(2)
            with col_t21_h311:
                if os.path.exists("Fahrenheit.jpg"):
                    st.image(
                        "Fahrenheit.jpg",
                        caption="Daniel Gabriel Fahrenheit",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Fahrenheit.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

            with col_t21_h411:
                if os.path.exists("mercure.jpg"):
                    st.image(
                        "mercure.jpg",
                        caption="thermomètre à mercure",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'mercure.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )
            
    with col_t2_h2:
        st.markdown("##### L'Évolution des Unités")
        st.write(
            "**Anders Celsius (1742) :** Il propose une échelle centésimale inversée (0 pour l'eau bouillante, 100 pour la glace), "
            "remise dans le bon sens après sa mort : 0 degré pour la glace fondante et 100 degrés pour l'ébullition.\n\n"
            "**Lord Kelvin (1848) :** Il définit l'échelle thermodynamique absolue. Le zéro absolu (-273,15 degrés Celsius) "
            "représente l'état d'immobilisation totale de la matière."
        )

        col_t21_h31, col_t36_h36 = st.columns(2)
        
        with col_t21_h31:
            col_t21_c1, col_t21_c2 = st.columns(2)
            with col_t21_c1:
                if os.path.exists("Celsius.jpg"):
                    st.image(
                        "Celsius.jpg",
                        caption="Anders Celsius",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Celsius.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

            with col_t21_c2:
                if os.path.exists("thermomercure.jpg"):
                    st.image(
                        "thermomercure.jpg",
                        caption="thermomètre degré Celsius",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'thermomercure.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

        with col_t36_h36:
            col_t36_k1, col_t36_k2 = st.columns(2)
            with col_t36_k1:
                if os.path.exists("Kelvin.jpg"):
                    st.image(
                        "Kelvin.jpg",
                        caption="Lord Kelvin",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Kelvin.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

            with col_t36_k2:
                if os.path.exists("themokelvin.jpg"):
                    st.image(
                        "themokelvin.jpg",
                        caption="mesure et extrapolation pour trouver le 0K",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'themokelvin.jpg.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )




    st.write("---")
    st.subheader("Modélisation microscopique : À quoi correspond la température ?")
    st.write(
        "La température traduit graphiquement le niveau d'agitation cinétique désordonnée "
        "des particules au cœur de la matière :"
    )

    img_col_gauche, img_col_droite = st.columns(2)

    with img_col_gauche:
        # Affichage de l'image de gauche (Basse température)
        if os.path.exists("froid.jpg"):
            st.image(
                "froid.jpg",
                caption="Basse température : faible vitesse d'agitation",
                use_container_width=True
            )
        else:
            st.warning(
                "L'image 'froid.jpg' est introuvable. Placez l'illustration dans le répertoire de l'application."
            )

    with img_col_droite:
        # Affichage de l'image de droite (Haute température)
        if os.path.exists("chaud.jpg"):
            st.image(
                "chaud.jpg",
                caption="Haute température : grande vitesse d'agitation",
                use_container_width=True
            )
        else:
            st.warning(
                "L'image 'chaud.jpg' est introuvable. Placez l'illustration dans le répertoire de l'application."
            )

    st.write("---")
    st.subheader("Convertisseur interactif d'unités de température")
    st.write(
        "Utilisez les commandes ci-dessous pour convertir une valeur d'une échelle à une autre "
        "et observez les formules de transformation associées :"
    )

    # Grille de saisie à 3 colonnes pour configurer la conversion
    conv_col1, conv_col2, conv_col3 = st.columns([1.0, 1.0, 1.2])

    with conv_col1:
        unite_source = st.selectbox(
            "Unité de départ :",
            ["Degré Celsius (°C)", "Kelvin (K)", "Degré Fahrenheit (°F)"],
            key="t2_conv_unite_source"
        )

    with conv_col2:
        valeur_saisie = st.number_input(
            "Valeur à convertir :",
            value=20.0,
            step=0.5,
            format="%.2f",
            key="t2_conv_valeur_saisie"
        )

    with conv_col3:
        unite_cible = st.selectbox(
            "Unité d'arrivée :",
            ["Degré Celsius (°C)", "Kelvin (K)", "Degré Fahrenheit (°F)"],
            key="t2_conv_unite_cible"
        )

    # Initialisation des variables de calcul
    resultat_conv = valeur_saisie
    formule_latex = r"T_{\text{cible}} = T_{\text{source}}"

    # Logique mathématique des conversions
    if unite_source == "Degré Celsius (°C)":
        if unite_cible == "Kelvin (K)":
            resultat_conv = valeur_saisie + 273.15
            formule_latex = r"T(\text{K}) = T(°\text{C}) + 273{,}15"
        elif unite_cible == "Degré Fahrenheit (°F)":
            resultat_conv = (valeur_saisie * 9/5) + 32
            formule_latex = r"T(°\text{F}) = T(°\text{C}) \times \frac{9}{5} + 32"

    elif unite_source == "Kelvin (K)":
        # Sécurité pour le zéro absolu
        if valeur_saisie < 0:
            st.error("Erreur physique : Une température en Kelvin ne peut pas être négative (Zéro absolu).")
        if unite_cible == "Degré Celsius (°C)":
            resultat_conv = valeur_saisie - 273.15
            formule_latex = r"T(°\text{C}) = T(\text{K}) - 273{,}15"
        elif unite_cible == "Degré Fahrenheit (°F)":
            resultat_conv = ((valeur_saisie - 273.15) * 9/5) + 32
            formule_latex = r"T(°\text{F}) = (T(\text{K}) - 273{,}15) \times \frac{9}{5} + 32"

    elif unite_source == "Degré Fahrenheit (°F)":
        if unite_cible == "Degré Celsius (°C)":
            resultat_conv = (valeur_saisie - 32) * 5/9
            formule_latex = r"T(°\text{C}) = (T(°\text{F}) - 32) \times \frac{5}{9}"
        elif unite_cible == "Kelvin (K)":
            resultat_conv = ((valeur_saisie - 32) * 5/9) + 273.15
            formule_latex = r"T(\text{K}) = (T(°\text{F}) - 32) \times \frac{5}{9} + 273{,}15"

    # Affichage du résultat dans un encadré propre
    if not (unite_source == "Kelvin (K)" and valeur_saisie < 0):
        st.markdown("**Formule de conversion appliquée :**")
        st.latex(formule_latex)
        
        # Extraction propre du symbole d'unité (ex: '°C' au lieu de 'Degré Celsius (°C)')
        symb_src = unite_source.split(" (")[1][:-1] if " (" in unite_source else unite_source
        symb_cib = unite_cible.split(" (")[1][:-1] if " (" in unite_cible else unite_cible

        # Boîte de résultat finale purgée des arguments invalides
        st.markdown(
            f"<div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; border-left: 4px solid #1e3a8a; font-size: 16px; font-weight: bold; color: #0f172a;'>"
            f"Résultat de la conversion : {valeur_saisie:.2f} {symb_src} = {resultat_conv:.2f} {symb_cib}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.write("---")
    # =============================================================================
    # CONFIGURATION DOUBLE COLONNE : TEXTE BLEU A GAUCHE / IMAGE ET GRAPHISME A DROITE
    # =============================================================================
    col_gauche_texte_t2, col_droite_img_t2 = st.columns(2)

    with col_gauche_texte_t2:
        st.write(
            "**La BD humoristique textuelle : Le thermomètre en folie**"
        )
        
        st.info(
            "**Cas 1 :** À l'état initial, les molécules d'un fluide sont calmes et immobiles. "
            "Elles dorment paisiblement à la température de zéro absolu dans leur bulbe en verre : "
            "« Chut, aucun mouvement ici, l'immobilité thermodynamique est totale ! ».\n\n"
            
            "**Cas 2 :** Une source de chaleur extérieure arrive soudainement. Le feu attrape les molécules "
            "par le bras et injecte de l'énergie thermique en hurlant : "
            "« Debout là-dedans ! Donnez-moi vos mouvements ! Il est temps de vous agiter énergiquement ! ».\n\n"
            
            "**Cas 3 :** Les molécules, excitées par l'apport d'énergie, paniquent et commencent à vibrer "
            "dans tous les sens. Manquant de place, elles poussent les parois du thermomètre : "
            "« Oh non ! On subit une augmentation de température ! On a trop de joules, "
            "il faut qu'on s'écarte, c'est la dilatation volumique ! ».\n\n"
            
            "**Cas 4 :** La colonne de liquide s'est violemment élevée le long du tube en verre, "
            "brisant le sommet du thermomètre sous la pression de l'agitation. Les molécules de chaleur s'échappent "
            "en ricanant : "
            "« Affaire classée ! Encore un capteur en verre terrassé par notre puissance cinétique ! »."
        )

    with col_droite_img_t2:
        if os.path.exists("temperature_caricature.jpg"):
            st.image(
                "temperature_caricature.jpg",
                caption="Illustration humoristique du mécanisme de dilatation thermique",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'temperature_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
    # =============================================================================
    # SIMULATEUR DYNAMIQUE : DILATATION DES LIQUIDES THERMOMÉTRIQUES
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Dilatation et choix du liquide de mesure")
    st.write(
        "Sélectionnez le fluide de votre choix et ajustez la température pour observer "
        "la montée ou la descente de la colonne liquide dans le tube capillaire en verre :"
    )

    # Dictionnaire de configuration réelle des liquides thermométriques
    fluides_thermiques = {
        "Alcool coloré (Éthanol)": {
            "couleur": "#ef4444", 
            "usage": "Usage domestique standard. Utilisé pour les températures ambiantes et négatives.",
            "min_t": -50, "max_t": 70
        },
        "Mercure (Historique)": {
            "couleur": "#94a3b8", 
            "usage": "Interdit aujourd'tui en raison de sa toxicité. Grande précision, large plage de mesure.",
            "min_t": -35, "max_t": 350
        },
        "Huile minérale": {
            "couleur": "#eab308", 
            "usage": "Alternative écologique moderne pour les thermomètres de cuisine et de jardin.",
            "min_t": -10, "max_t": 120
        }
    }

    # Configuration des commandes par l'étudiant
    col_param_1, col_param_2 = st.columns([1.1, 1.0])
    
    with col_param_1:
        choix_fluide = st.selectbox(
            "Sélectionnez le liquide thermométrique :",
            list(fluides_thermiques.keys()),
            key="t2_choix_liquide_dilatation"
        )
        
        cfg_f = fluides_thermiques[choix_fluide]
        
        # Sélection de la température dynamique bridée selon les propriétés du fluide choisi
        temperature_saisie = st.slider(
            f"Ajustez la température (°C) :",
            min_value=int(cfg_f["min_t"]),
            max_value=int(cfg_f["max_t"]),
            value=20,
            step=1,
            key="t2_slider_temperature"
        )
        
    with col_param_2:
        st.markdown("**Propriétés de laboratoire du fluide sélectionné :**")
        st.info(f"**Application :** {cfg_f['usage']}\n\n**Plage d'état liquide sécurisée :** de {cfg_f['min_t']} °C à {cfg_f['max_t']} °C.")

    # =============================================================================
    # RENDU VISUEL SCIENTIFIQUE DU THERMOMÈTRE (MATPLOTLIB)
    # =============================================================================
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(6, 5))
    
    # 1. Dessin de la structure extérieure en verre du thermomètre
    # Le réservoir sphérique en bas
    ax.add_patch(patches.Circle((2.5, 1.2), radius=0.4, facecolor='#f8fafc', edgecolor='#1e293b', lw=2.5, zorder=1))
    # Le tube capillaire vertical de mesure
    ax.add_patch(patches.Rectangle((2.35, 1.2), 0.3, 4.8, facecolor='#f8fafc', edgecolor='#1e293b', lw=2.5, zorder=1))
    
    # 2. Calcul du niveau de dilatation linéaire (hauteur de la colonne)
    # On normalise la température choisie entre 0% et 100% de la hauteur du tube
    t_min_curseur = cfg_f["min_t"]
    t_max_curseur = cfg_f["max_t"]
    ratio = (temperature_saisie - t_min_curseur) / (t_max_curseur - t_min_curseur)
    
    # Hauteur minimale fixe du liquide = 1.2 (remplit le réservoir) + extension proportionnelle
    hauteur_remplissage_capillaire = 0.2 + (ratio * 4.3)

    # 3. Dessin du liquide en couleur réelle
    # Remplissage du bulbe bas
    ax.add_patch(patches.Circle((2.5, 1.2), radius=0.36, color=cfg_f["couleur"], zorder=2))
    # Remplissage de la colonne de dilatation dans le capillaire
    ax.add_patch(patches.Rectangle((2.39, 1.2), 0.22, hauteur_remplissage_capillaire, color=cfg_f["couleur"], zorder=2))

    # 4. Tracé précis des graduations de l'échelle à droite du verre
    for i in range(11):
        # Positionnement des paliers de 0 à 10
        pos_y = 1.4 + (i * 0.43)
        val_temp_grad = t_min_curseur + i * (t_max_curseur - t_min_curseur) / 10
        ax.plot([2.65, 2.75], [pos_y, pos_y], color='#1e293b', lw=1, zorder=3)
        ax.text(2.85, pos_y, f"{int(val_temp_grad)} °C", color='#475569', fontsize=8, va='center', zorder=3)

    # Graduations intermédiaires fines
    for i in range(50):
        pos_y_fine = 1.4 + (i * 0.086)
        ax.plot([2.65, 2.70], [pos_y_fine, pos_y_fine], color='#64748b', lw=0.5, zorder=3)

    # 5. Rendu textuel de la mesure actuelle
    ax.text(1.5, 5.5, f"TEMPÉRATURE : {temperature_saisie} °C", color='#0f172a', fontsize=12, fontweight='bold', bbox=dict(boxstyle="round,pad=0.4", fc="#f1f5f9", ec="#cbd5e1", lw=1.5))
    
    # Ajustements géométriques des axes
    ax.set_xlim(0.5, 4.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    # Affichage propre dans Streamlit
    st.write("")
    st.pyplot(fig)
    st.write("---")




    st.write("---")
    if "suite_verrouille_tab2_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab2_therm = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_therm

    # Affichage du module de questions
    afficher_atelier_temperature_verrouille(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Température.",
        key="check_certif_therm2_final_net",
        disabled=verrou_at2,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2",
        key="btn_export_suite2_therm_official",
        use_container_width=True,
        disabled=verrou_at2,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q2 = 0.0
            if "ordre_quiz_tab2_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t2 = 0.0
            if "champs_therm2_clean" in st.session_state:
                for ligne in st.session_state.champs_therm2_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm2_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t2 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite2_therm_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_therm_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_therm = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab2_therm", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_therm_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_therm_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_therm", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TEMPÉRATURE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_therm2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Température Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 2 : Échelles de température, principes de mesure et capteurs</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 2 (.HTML)",
            data=html_export_therm2,
            file_name=preparer_nom_fichier("Atelier_2_Temperature").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )



with tab3:
    st.header("La Chaleur et le Transfert d'Énergie Thermique")
    st.write(
        "Comprenez la différence fondamentale entre la température et la chaleur, découvrez "
        "les expériences historiques et observez les transferts d'énergie en direct :"
    )

    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE : LE DRAME DES CALORIES PERDUES
    # =============================================================================
    col_gauche_texte_t3, col_droite_img_t3 = st.columns(2)

    with col_gauche_texte_t2:  # Réutilisation de votre structure à deux colonnes symétriques
        st.write(
            "**La BD humoristique textuelle : Le drame des calories perdues**"
        )
        
        st.info(
            "**Cas 1 :** Un groupe d'atomes à l'intérieur d'une maison chauffée est tranquillement installé "
            "dans la structure de la paroi. Ils vibrent joyeusement ensemble et discutent avec leurs voisins : "
            "« Tout va bien les gars, la parfaite cohésion est là, on forme un bloc d'isolation indestructible ! ».\n\n"
            
            "**Cas 2 :** Une baisse brutale des températures survient à l'extérieur. L'air froid hivernal, "
            "très gourmand, attrape l'atome de la paroi par le bras et crie : "
            "« Hé toi ! Donne-moi tes charges ! Tes précieux joules d'énergie m'intéressent grandement ! ».\n\n"
            
            "**Cas 3 :** L'atome de la paroi, dépouillé de son énergie de protection, commence à se refroidir "
            "et à se détacher du réseau. Il panique en voyant sa température baisser : "
            "« Oh non ! Je viens de subir un transfert thermique ! Je ne suis plus un atome chaud et agité, "
            "je me transforme en conducteur froid ! C'est la dissipation ! ».\n\n"
            
            "**Cas 4 :** La chaleur évadée désormais flotte dans l'atmosphère froide sous forme de perte pure, "
            "laissant un trou béant dans le bilan énergétique de la poutre. Les atomes de froid s'enfuient "
            "en ricanant avec leur butin : "
            "« Affaire classée ! Encore un système chauffé terrassé par notre pouvoir absorbant ! »."
        )

    with col_droite_img_t3:
        if os.path.exists("chaleur_caricature.jpg"):
            st.image(
                "chaleur_caricature.jpg",
                caption="Illustration humoristique du drame des calories perdues",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # 2. COURS HISTORIQUE : LES SAVANTS ET LES EXPÉRIENCES
    # =============================================================================
    col_t3_h1, col_t3_h2 = st.columns(2)
    
    with col_t3_h1:
        st.markdown("##### Les Pionniers de la Quantification")
        st.write(
            "**Joseph Black (1761) :** Ce médecin écossais découvre la chaleur latente. Il remarque "
            "que l'apport de chaleur pour faire fondre de la glace n'augmente pas sa température tant "
            "que la fusion n'est pas totale. Il introduit ainsi la distinction entre intensité (température) et quantité (chaleur).\n\n"
            "**Benjamin Thompson / Comte Rumford (1798) :** En observant le forage des canons, il démontre "
            "que le frottement mécanique produit une quantité de chaleur infinie. Il assène le premier coup fatal à la théorie du fluide calorique."
        )

        col_t31_h11, col_t31_h21 = st.columns(2)
        with col_t31_h11:
            col_t31_c1, col_t31_c2 = st.columns(2)
            with col_t31_c1:
                if os.path.exists("Black.jpg"):
                    st.image("Black.jpg", caption="Joseph Black", use_container_width=True)
                else:
                    st.warning("L'image 'Black.jpg' est introuvable.")
            with col_t31_c2:
                if os.path.exists("calorimetreblack.jpg"):
                    st.image("calorimetreblack.jpg", caption="Calorimètre historique", use_container_width=True)
                else:
                    st.warning("L'image 'calorimetreblack.jpg' est introuvable.")
        with col_t31_h21:
            col_t31_c3, col_t31_c4 = st.columns(2)
            with col_t31_c3:
                if os.path.exists("Rumford.jpg"):
                    st.image("Rumford.jpg", caption="Comte Rumford", use_container_width=True)
                else:
                    st.warning("L'image 'Rumford.jpg' est introuvable.")
            with col_t31_c4:
                if os.path.exists("canon.jpg"):
                    st.image("canon.jpg", caption="Forage des canons", use_container_width=True)
                else:
                    st.warning("L'image 'canon.jpg' est introuvable.")
            
    with col_t3_h2:
        st.markdown("##### L'Équivalent Mécanique de la Chaleur")
        st.write(
            "**James Prescott Joule (1843) :** Grâce à sa célèbre expérience de la cuve munie de palettes en rotation "
            "actionnées par la chute de masses, il établit une équivalence stricte entre le travail mécanique et la chaleur.\n\n"
            "**L'Établissement du Joule :** Ses mesures rigoureuses prouvent qu'une quantité de travail mécanique "
            "fournie engendre toujours une élévation prévisible de température, fixant l'unité de la chaleur (le Joule)."
        )


        col_t32_c1, col_t32_c2 = st.columns(2)
        with col_t32_c1:
            if os.path.exists("Joule.jpg"):
                st.image("Joule.jpg", caption="James Joule", use_container_width=True)
            else:
                st.warning("L'image 'Joule.jpg' est introuvable.")
        with col_t32_c2:
            if os.path.exists("palettesjoule.jpg"):
                st.image("palettesjoule.jpg", caption="Expérience des palettes", use_container_width=True)
            else:
                st.warning("L'image 'palettesjoule.jpg' est introuvable.")



    st.write("---")
    st.subheader("Laboratoire Virtuel : Calorimétrie avancée et équilibres de phases")
    st.write(
        "Configurez jusqu'à 5 fluides parmi une bibliothèque de 24 corps réels. Le moteur "
        "de calcul intègre les capacités thermiques ainsi que les chaleurs latentes en cas "
        "de changement d'état (fusion, solidification, vaporisation) au cours du mélange :"
    )

    # DÉFINITION IMPÉRATIVE DU DICTIONNAIRE AVANT SON UTILISATION
    bibliotheque_24_liquides = {
        "Eau pure": {"c": 4180, "rho": 1.00, "T_f": 0, "T_e": 100, "L_f": 334000, "L_v": 2260000, "col": "#bae6fd"},
        "Lait entier": {"c": 3890, "rho": 1.03, "T_f": -0.5, "T_e": 100.5, "L_f": 320000, "L_v": 2240000, "col": "#f8fafc"},
        "Bière standard": {"c": 4050, "rho": 1.01, "T_f": -2, "T_e": 95, "L_f": 310000, "L_v": 1900000, "col": "#fef08a"},
        "Vin rouge": {"c": 3780, "rho": 0.99, "T_f": -5, "T_e": 85, "L_f": 280000, "L_v": 1500000, "col": "#7f1d1d"},
        "Vin blanc": {"c": 3790, "rho": 0.99, "T_f": -5, "T_e": 85, "L_f": 280000, "L_v": 1500000, "col": "#fef9c3"},
        "Éthanol (Alcool)": {"c": 2440, "rho": 0.79, "T_f": -114, "T_e": 78, "L_f": 109000, "L_v": 841000, "col": "#fecdd3"},
        "Huile végétale": {"c": 2000, "rho": 0.92, "T_f": -10, "T_e": 300, "L_f": 80000, "L_v": 350000, "col": "#fef08a"},
        "Glycérol": {"c": 2400, "rho": 1.26, "T_f": 18, "T_e": 290, "L_f": 200000, "L_v": 826000, "col": "#fed7aa"},
        "Acétone": {"c": 2160, "rho": 0.79, "T_f": -95, "T_e": 56, "L_f": 98000, "L_v": 525000, "col": "#ddd6fe"},
        "Méthanol": {"c": 2530, "rho": 0.79, "T_f": -97, "T_e": 65, "L_f": 99000, "L_v": 1100000, "col": "#e2e8f0"},
        "Benzène": {"c": 1740, "rho": 0.88, "T_f": 5.5, "T_e": 80, "L_f": 127000, "L_v": 394000, "col": "#cbd5e1"},
        "Mercure liquide": {"c": 139, "rho": 13.55, "T_f": -39, "T_e": 357, "L_f": 11400, "L_v": 295000, "col": "#94a3b8"},
        "Sodium fondu": {"c": 1380, "rho": 0.97, "T_f": 98, "T_e": 883, "L_f": 113000, "L_v": 426000, "col": "#64748b"},
        "Plomb liquide": {"c": 150, "rho": 10.66, "T_f": 327, "T_e": 1749, "L_f": 23000, "L_v": 858000, "col": "#475569"},
        "Huile de moteur": {"c": 1900, "rho": 0.89, "T_f": -20, "T_e": 250, "L_f": 70000, "L_v": 280000, "col": "#a1a1aa"},
        "Ammoniac liquide": {"c": 4700, "rho": 0.68, "T_f": -78, "T_e": -33, "L_f": 332000, "L_v": 1370000, "col": "#a5f3fc"},
        "Fluide R134a": {"c": 1420, "rho": 1.21, "T_f": -103, "T_e": -26, "L_f": 215000, "L_v": 217000, "col": "#cffafe"},
        "Azote cryogénique": {"c": 2040, "rho": 0.81, "T_f": -210, "T_e": -196, "L_f": 25700, "L_v": 199000, "col": "#ccfbf1"},
        "Essence standard": {"c": 2220, "rho": 0.75, "T_f": -40, "T_e": 150, "L_f": 95000, "L_v": 315000, "col": "#fef9c3"},
        "Gazole / Diesel": {"c": 2000, "rho": 0.85, "T_f": -5, "T_e": 280, "L_f": 85000, "L_v": 290000, "col": "#fef08a"},
        "Acide sulfurique": {"c": 1390, "rho": 1.84, "T_f": 10, "T_e": 337, "L_f": 103000, "L_v": 510000, "col": "#e9d5ff"},
        "Éthylène glycol": {"c": 2400, "rho": 1.11, "T_f": -13, "T_e": 197, "L_f": 181000, "L_v": 800000, "col": "#f5d0fe"},
        "Eau de mer": {"c": 3990, "rho": 1.02, "T_f": -2, "T_e": 101, "L_f": 325000, "L_v": 2240000, "col": "#7dd3fc"},
        "Aniline": {"c": 2060, "rho": 1.02, "T_f": -6, "T_e": 184, "L_f": 112000, "L_v": 479000, "col": "#fae8ff"}
    }

    nb_melanges = st.slider(
        "Nombre de liquides à intégrer :", 
        min_value=2, 
        max_value=5, 
        value=2, 
        step=1, 
        key="t3_nb_liquides_melange_24"
    )

    volume_total = 0.0
    somme_m_c = 0.0
    somme_m_c_T = 0.0
    fluides_presents = []

    st.write("")
    st.markdown("**Configuration des compartiments fluides :**")
    colonnes_fluides = st.columns(nb_melanges)

    for i in range(nb_melanges):
        with colonnes_fluides[i]:
            st.markdown(f"**Fluide {i+1}**")
            liq_nom = st.selectbox(f"Nature :", list(bibliotheque_24_liquides.keys()), key=f"t3_m24_nat_{i}")
            liq_vol = st.slider(f"Volume (L) :", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"t3_m24_vol_{i}")
            
            p_therm = bibliotheque_24_liquides[liq_nom]
            
            t_min_curseur = int(max(-220, p_therm["T_f"]))
            t_max_curseur = int(min(400, p_therm["T_e"]))
            if t_min_curseur >= t_max_curseur: 
                t_min_curseur, t_max_curseur = t_max_curseur - 20, t_max_curseur + 20
                
            liq_temp = st.slider(f"Température (°C) :", min_value=t_min_curseur, max_value=t_max_curseur, value=int((t_min_curseur + t_max_curseur)/2), step=1, key=f"t3_m24_tmp_{i}")
            
            masse = liq_vol * p_therm["rho"]
            volume_total += liq_vol
            somme_m_c += (masse * p_therm["c"])
            somme_m_c_T += masse * p_therm["c"] * liq_temp
            
            fluides_presents.append({
                "nom": liq_nom, 
                "vol": liq_vol, 
                "temp": liq_temp, 
                "masse": masse, 
                "prop": p_therm
            })

    # Moteur mathématique calorimétrique prédictif (Calcul de la température de convergence)
    if somme_m_c > 0:
        T_equil_brute = somme_m_c_T / somme_m_c
    else:
        T_equil_brute = 20.0

    # Algorithme de vérification des transitions de phase et calcul de la composition finale
    T_finale_calculee = T_equil_brute
    phase_statut = "Monophasique (Mélange liquide limpide)"
    
    # On va stocker le volume de chaque liquide restant sous forme liquide à la fin
    composition_finale = []
    volume_liquide_total_final = 0.0

    # Détection des paliers d'ébullition ou de solidification
    for f in fluides_presents:
        vol_liquide_restant = f["vol"]
        etat_composant_final = "Liquide"
        
        # Cas où le mélange est trop chaud pour le fluide : Vaporisation
        if T_equil_brute >= f["prop"]["T_e"]:
            T_finale_calculee = f["prop"]["T_e"]
            phase_statut = "Biphasique (Ébullition et présence de gaz)"
            vol_liquide_restant = 0.0
            etat_composant_final = "Totalement évaporé (Gaz)"
        
        # Cas où le mélange est trop froid pour le fluide : Solidification
        elif T_equil_brute <= f["prop"]["T_f"]:
            T_finale_calculee = f["prop"]["T_f"]
            phase_statut = "Biphasique (Précipité solide / Solidification)"
            etat_composant_final = "Solidifié (Glace / Cristal)"
            
        volume_liquide_total_final += vol_liquide_restant
        composition_finale.append({
            "nom": f["nom"],
            "vol_initial": f["vol"],
            "vol_final": vol_liquide_restant,
            "etat": etat_composant_final
        })

    # =============================================================================
    # RENDU DE LA GRAPHIQUE DU LABORATOIRE INTERACTIF (MATPLOTLIB)
    # =============================================================================
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_mel20, ax_mel20 = plt.subplots(figsize=(9, 3.8))
    
    # Rendu individuel des éprouvettes graduées d'introduction
    for i, f in enumerate(fluides_presents):
        x_pos = 0.4 + (i * 1.3)
        ax_mel20.add_patch(patches.Rectangle((x_pos, 0.7), 0.7, 1.4 * (f["vol"] / 5.0), color=f["prop"]["col"], alpha=0.8, zorder=1))
        ax_mel20.add_patch(patches.Polygon([[x_pos, 2.3], [x_pos, 0.7], [x_pos + 0.7, 0.7], [x_pos + 0.7, 2.3]], closed=False, fill=False, color='#475569', lw=1.5, zorder=2))
        ax_mel20.text(x_pos + 0.35, 0.3, f"F{i+1}\n{f['temp']} °C", color='#1e293b', fontsize=8, ha='center', fontweight='bold')

    # Grande enceinte de confinement adiabatique à droite
    x_cadre = 7.2
    ax_mel20.add_patch(patches.Rectangle((x_cadre, 0.7), 2.2, 1.8 * (volume_liquide_total_final / 25.0) if volume_liquide_total_final > 0 else 0.1, color='#cbd5e1', alpha=0.8, zorder=1))
    ax_mel20.add_patch(patches.Polygon([[x_cadre, 3.0], [x_cadre, 0.7], [x_cadre + 2.2, 0.7], [x_cadre + 2.2, 3.0]], closed=False, fill=False, color='#0f172a', lw=2.5, zorder=2))
    ax_mel20.text(x_cadre + 1.1, 0.3, "CONFINEMENT\nFINAL", color='#0f172a', fontsize=8.5, ha='center', fontweight='bold')

    # Flèche directionnelle d'écoulement du flux de matière
    ax_mel20.arrow(0.4 + (nb_melanges * 1.3), 1.4, 1.0, 0, head_width=0.12, head_length=0.12, fc='#0f172a', ec='#0f172a', lw=2)

    ax_mel20.set_xlim(0, 9.8)
    ax_mel20.set_ylim(0, 3.3)
    ax_mel20.axis('off')
    st.pyplot(fig_mel20)

    # 4. Bloc d'affichage des résultats de laboratoire pur
    st.markdown("**Résultats métrologiques mesurés à l'équilibre :**")
    
    html_m20_box = f"""
    <div style='display: flex; gap: 15px; margin-bottom: 15px;'>
        <div style='flex: 1; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 4px solid #1e3a8a; font-size: 15px; font-weight: bold; color: #0f172a; text-align: center;'>
            Volume Liquide Résiduel : {volume_liquide_total_final:.2f} L
        </div>
        <div style='flex: 1; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 4px solid #ea580c; font-size: 15px; font-weight: bold; color: #0f172a; text-align: center;'>
            Température Finale Réelle : {T_finale_calculee:.2f} °C
        </div>
    </div>
    <div style='background-color: #f8fafc; padding: 10px; border-radius: 4px; border: 1px dashed #cbd5e1; font-size: 13px; color: #475569; text-align: center; font-weight: bold; margin-bottom: 15px;'>
        Régime thermodynamique observé : {phase_statut}
    </div>
    """
    st.markdown(html_m20_box, unsafe_allow_html=True)

    # --- TABLEAU DE COMPOSITION DÉTAILLÉ SANS ÉMOJI ---
    st.markdown("**Analyse qualitative de la solution finale :**")
    
    # Construction d'un tableau HTML propre
    tableau_html = """
    <table style='width: 100%; border-collapse: collapse; background-color: white; font-size: 13px; text-align: left;'>
        <thead>
            <tr style='background-color: #0f172a; color: white;'>
                <th style='padding: 8px;'>Nom du fluide</th>
                <th style='padding: 8px;'>Volume initial</th>
                <th style='padding: 8px;'>Volume sous forme liquide à la fin</th>
                <th style='padding: 8px;'>État physique final</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for c in composition_finale:
        style_ligne = "style='color: #ef4444; font-weight: bold;'" if "évaporé" in c["etat"] else ""
        tableau_html += f"""
            <tr style='border-bottom: 1px solid #e2e8f0;'>
                <td style='padding: 8px;'>{c['nom']}</td>
                <td style='padding: 8px;'>{c['vol_initial']:.1f} L</td>
                <td style='padding: 8px;'>{c['vol_final']:.1f} L</td>
                <td style='padding: 8px;' {style_ligne}>{c['etat']}</td>
            </tr>
        """
        
    tableau_html += "</tbody></table>"
    st.markdown(tableau_html, unsafe_allow_html=True)
    st.write("---")
    
    st.write("---")
    if "suite_verrouille_tab3_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab3_therm = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_therm

    # Affichage du module de questions spécifique à l'Atelier de la Chaleur
    afficher_atelier_chaleur_verrouille(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Chaleur.",
        key="check_certif_therm3_final_net",
        disabled=verrou_at3,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3",
        key="btn_export_suite3_therm_official",
        use_container_width=True,
        disabled=verrou_at3,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t3 = 0.0
            if "champs_therm3_clean" in st.session_state:
                for ligne in st.session_state.champs_therm3_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm3_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t3 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite3_therm_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_therm_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_therm = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab3_therm", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_therm_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_therm_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_therm", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER CHALEUR SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_therm3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Chaleur Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 3 : Principes fondamentaux, équivalence mécanique et calcul de la chaleur</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 3 (.HTML)",
            data=html_export_therm3,
            file_name=preparer_nom_fichier("Atelier_3_Chaleur").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )

































