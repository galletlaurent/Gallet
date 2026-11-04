# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application réflexion et réfraction",
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
st.title("Application réflexion et réfraction")
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
    "Loi de la reflexion pour un miroir plan",
    "Loi de la refraction",
    "La réflexion totale",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine topographe géomètre",
    "Réflexion pour un miroir concave",
    "Réflexion pour un miroir concave"
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

def afficher_atelier_reflexion_totale(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 4 de la Réflexion Totale."""
    import random

    st.subheader("Atelier Interactif : Phénomène de Réflexion Totale et Applications")

    questions_totale_sources = [
        {"id": "qrt1", "q": "Quelle condition sur les indices de réfraction est obligatoire pour obtenir une réflexion totale ?", "options": ["n1 doit être supérieur à n2", "n1 doit être inférieur à n2", "n1 doit être égal à n2"], "rep": "n1 doit être supérieur à n2"},
        {"id": "qrt2", "q": "Quelle technologie de communication moderne utilise la réflexion totale pour guider la lumière ?", "options": ["La fibre optique", "Le câble coaxial", "La ligne de cuivre"], "rep": "La fibre optique"},
        {"id": "qrt3", "q": "À quel angle de réfraction (i2) correspond exactement l'angle d'incidence limite ?", "options": ["90 degrés", "0 degré", "45 degrés"], "rep": "90 degrés"},
        {"id": "qrt4", "q": "Si l'angle d'incidence est strictement supérieur à l'angle critique, que devient l'intensité du rayon réfracté ?", "options": ["Elle devient nulle", "Elle double", "Elle reste identique"], "rep": "Elle devient nulle"},
        {"id": "qrt5", "q": "Quel instrument médical utilise des faisceaux de fibres optiques pour explorer l'intérieur du corps ?", "options": ["L'endoscope", "Le stéthoscope", "Le tensiomètre"], "rep": "L'endoscope"},
        {"id": "qrt6", "q": "Comment appelle-t-on la partie centrale d'une fibre optique où circule la lumière ?", "options": ["Le cœur", "La gaine", "Le revêtement"], "rep": "Le cœur"},
        {"id": "qrt7", "q": "Pour que la lumière reste piégée dans le cœur de la fibre, la gaine doit avoir :", "options": ["Un indice n2 inférieur à n1", "Un indice n2 supérieur à n1", "Le même indice n1"], "rep": "Un indice n2 inférieur à n1"},
        {"id": "qrt8", "q": "Quel composant optique à réflexion totale trouve-t-on dans les appareils photo reflex et les jumelles ?", "options": ["Le prisme à angle droit", "La lentille divergente", "Le miroir concave"], "rep": "Le prisme à angle droit"},
        {"id": "qrt9", "q": "Quel phénomène optique naturel et chaud crée des illusions visuelles de flaques d'eau sur la route ?", "options": ["Un mirage", "Un arc-en-ciel", "Une ombre portée"], "rep": "Un mirage"},
        {"id": "qrt10", "q": "Si la lumière voyage du verre (n=1.5) vers l'air (n=1), la réflexion totale est-elle possible ?", "options": ["Oui, si l'angle d'incidence est suffisant", "Non, c'est physiquement impossible", "Uniquement si le laser est violet"], "rep": "Oui, si l'angle d'incidence est suffisant"}
    ]

    if "ordre_quiz_totale_aleatoire" not in st.session_state:
        random.shuffle(questions_totale_sources)
        st.session_state.ordre_quiz_totale_aleatoire = questions_totale_sources

    if "champs_totale_clean" not in st.session_state:
        st.session_state.champs_totale_clean = [
            ("1. La réflexion totale se produit uniquement si le milieu 1 est plus .......... que le milieu 2.", ["Choisir...", "réfringent", "transparent"], "réfringent", "tot_t1"),
            ("2. L'angle d'incidence à partir duquel la réfraction s'annule est l'angle ..........", ["Choisir...", "limite", "normal"], "limite", "tot_t2"),
            ("3. Au-delà de l'angle critique, la totalité de l'énergie lumineuse est ..........", ["Choisir...", "réfléchie", "absorbée"], "réfléchie", "tot_t3"),
            ("4. Le guide de lumière souple constitué d'un cœur et d'une gaine est la fibre ..........", ["Choisir...", "optique", "de carbone"], "optique", "tot_t4"),
            ("5. Dans une fibre, l'indice du cœur doit être strictement .......... à celui de la gaine.", ["Choisir...", "supérieur", "inférieur"], "supérieur", "tot_t5"),
            ("6. Un prisme à réflexion totale permet de dévier un faisceau de quatre-vingt-dix ..........", ["Choisir...", "degrés", "pascals"], "degrés", "tot_t6"),
            ("7. Lors d'une réflexion totale, le dioptre se comporte comme un .......... parfait.", ["Choisir...", "miroir", "filtre"], "miroir", "tot_t7"),
            ("8. Les mirages routiers proviennent de la courbure des rayons dans l'air ..........", ["Choisir...", "surchauffé", "glacial"], "surchauffé", "tot_t8"),
            ("9. L'examen médical interne exploitant la réflexion totale est l'..........", ["Choisir...", "endoscopie", "échographie"], "endoscopie", "tot_t9"),
            ("10. Si l'angle d'incidence est inférieur à l'angle critique, il y a toujours ..........", ["Choisir...", "réfraction", "absorption"], "réfraction", "tot_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_totale_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"tot_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_totale_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_tot_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_refraction(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 3 de la Réfraction."""
    import random

    st.subheader("Atelier Interactif : Lois de la Réfraction et Indices Optiques")

    questions_refraction_sources = [
        {"id": "qr1", "q": "Quelle formule traduit mathématiquement la loi de Snell-Descartes pour la réfraction ?", "options": ["n1 * sin(i1) = n2 * sin(i2)", "i1 = i2", "n1 * cos(i1) = n2 * cos(i2)"], "rep": "n1 * sin(i1) = n2 * sin(i2)"},
        {"id": "qr2", "q": "Que représente la grandeur 'n' pour un milieu transparent ?", "options": ["L'indice de réfraction", "L'intensité lumineuse", "Le niveau de réflexion"], "rep": "L'indice de réfraction"},
        {"id": "qr3", "q": "Quelle est la valeur approximative de l'indice de réfraction de l'air ?", "options": ["1.00", "1.33", "1.52"], "rep": "1.00"},
        {"id": "qr4", "q": "Quand la lumière passe de l'air (n=1) à l'eau (n=1.33), le rayon réfracté :", "options": ["Se rapproche de la normale", "S'éloigne de la normale", "Ne subit aucune déviation"], "rep": "Se rapproche de la normale"},
        {"id": "qr5", "q": "Comment s'appelle la surface plane qui sépare deux milieux transparents différents ?", "options": ["Un dioptre plan", "Une normale", "Un miroir plan"], "rep": "Un dioptre plan"},
        {"id": "qr6", "q": "Quelle est l'unité légale de l'indice de réfraction 'n' ?", "options": ["Il n'a pas d'unité", "Le degré (°)", "Le Pascal (Pa)"], "rep": "Il n'a pas d'unité"},
        {"id": "qr7", "q": "Que se passe-t-il si l'argument du sinus calculé pour l'angle i2 dépasse la valeur 1 ?", "options": ["Une réflexion totale", "Le rayon s'annule", "Une réfraction infinie"], "rep": "Une réflexion totale"},
        {"id": "qr8", "q": "Pour observer une réflexion totale, quelle condition doit remplir l'indice n1 par rapport à n2 ?", "options": ["n1 doit être supérieur à n2", "n1 doit être inférieur à n2", "n1 doit être égal à n2"], "rep": "n1 doit être supérieur à n2"},
        {"id": "qr9", "q": "Parmi ces milieux, lequel possède l'indice de réfraction le plus élevé (n = 2.417) ?", "options": ["Le diamant", "Le verre Crown", "L'eau"], "rep": "Le diamant"},
        {"id": "qr10", "q": "Si un rayon incident arrive perpendiculairement à la surface (i1 = 0°), que vaut l'angle i2 ?", "options": ["0 degré", "90 degrés", "45 degrés"], "rep": "0 degré"}
    ]

    if "ordre_quiz_refraction_aleatoire" not in st.session_state:
        random.shuffle(questions_refraction_sources)
        st.session_state.ordre_quiz_refraction_aleatoire = questions_refraction_sources

    if "champs_refraction_clean" not in st.session_state:
        st.session_state.champs_refraction_clean = [
            ("1. Le changement de direction de la lumière s'appelle la ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "ref_t1"),
            ("2. L'indice optique traduit le rapport entre la vitesse de la lumière dans le vide et dans le ..........", ["Choisir...", "matériau", "miroir"], "matériau", "ref_t2"),
            ("3. Plus l'indice de réfraction d'un milieu est grand, plus la vitesse de la lumière ..........", ["Choisir...", "diminue", "augmente"], "diminue", "ref_t3"),
            ("4. La ligne de référence tracée à 90 degrés de l'interface est la ..........", ["Choisir...", "normale", "tangente"], "normale", "ref_t4"),
            ("5. La loi de Snell-Descartes relie les indices aux .......... des angles.", ["Choisir...", "sinus", "cosinus"], "sinus", "ref_t5"),
            ("6. Le milieu de référence dont l'indice de réfraction vaut exactement 1 est le ..........", ["Choisir...", "vide", "verre"], "vide", "ref_t6"),
            ("7. Quand le rayon s'éloigne de la normale, cela signifie que n2 est .......... à n1.", ["Choisir...", "inférieur", "supérieur"], "inférieur", "ref_t7"),
            ("8. L'angle limite d'incidence est le point de départ de la réflexion ..........", ["Choisir...", "totale", "spéculaire"], "totale", "ref_t8"),
            ("9. L'illusion du bâton brisé dans un verre est provoquée par la ..........", ["Choisir...", "réfraction", "dispersion"], "réfraction", "ref_t9"),
            ("10. L'indice optique de l'eau pure est égal à ..........", ["Choisir...", "1.333", "1.520"], "1.333", "ref_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_refraction_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"ref_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_refraction_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ref_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_miroir_plan(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte pour l'Atelier 2 du Miroir Plan."""
    import random

    st.subheader("Atelier Interactif : Lois de la Réflexion Spéculaire")

    questions_miroir_sources = [
        {"id": "qm1", "q": "Comment appelle-t-on la ligne imaginaire perpendiculaire à la surface du miroir ?", "options": ["La Normale", "La Tangente", "Le Dioptre"], "rep": "La Normale"},
        {"id": "qm2", "q": "Quel angle est défini entre le rayon incident et la normale ?", "options": ["L'angle d'incidence", "L'angle de réflexion", "L'angle de réfraction"], "rep": "L'angle d'incidence"},
        {"id": "qm3", "q": "Si un rayon frappe un miroir plan avec un angle d'incidence de 40 degrés, quel est l'angle du rayon réfléchi ?", "options": ["40 degrés", "20 degrés", "50 degrés"], "rep": "40 degrés"},
        {"id": "qm4", "q": "Par rapport à quel élément de référence mesure-t-on toujours les angles en optique géométrique ?", "options": ["La normale", "La surface du miroir", "La source laser"], "rep": "La normale"},
        {"id": "qm5", "q": "Comment appelle-t-on le rayon lumineux qui provient directement de la source ?", "options": ["Le rayon incident", "Le rayon réfléchi", "Le rayon réfracté"], "rep": "Le rayon incident"},
        {"id": "qm6", "q": "Quelle est la relation mathématique exacte de la deuxième loi de Snell-Descartes pour la réflexion ?", "options": ["i = r", "i = 2r", "n1 * i = n2 * r"], "rep": "i = r"},
        {"id": "qm7", "q": "Comment qualifie-t-on le point d'intersection précis où le faisceau touche le miroir ?", "options": ["Le point d'incidence", "Le point focal", "Le point de déviation"], "rep": "Le point d'incidence"},
        {"id": "qm8", "q": "Dans quel plan particulier les rayons incident, réfléchi et la normale sont-ils tous situés ?", "options": ["Le plan d'incidence", "Le plan de réfraction", "Le plan horizontal"], "rep": "Le plan d'incidence"},
        {"id": "qm9", "q": "Quel type de surface caractérise un miroir plan parfait ?", "options": ["Une surface parfaitement lisse et réfléchissante", "Une surface rugueuse et mate", "Une surface transparente et courbe"], "rep": "Une surface parfaitement lisse et réfléchissante"},
        {"id": "qm10", "q": "Si un rayon laser arrive de manière parfaitement perpendiculaire au miroir (i = 0°), que fait le rayon réfléchi ?", "options": ["Il rebrousse chemin sur lui-même", "Il est dévié à 90 degrés", "Il est totalement absorbé"], "rep": "Il rebrousse chemin sur lui-même"}
    ]

    if "ordre_quiz_miroir_aleatoire" not in st.session_state:
        random.shuffle(questions_miroir_sources)
        st.session_state.ordre_quiz_miroir_aleatoire = questions_miroir_sources

    if "champs_miroir_clean" not in st.session_state:
        st.session_state.champs_miroir_clean = [
            ("1. Le rayon provenant du laser qui se dirige vers la surface est le rayon ..........", ["Choisir...", "incident", "réfléchi"], "incident", "mir_t1"),
            ("2. Après avoir frappé le miroir, le rayon lumineux qui repart est le rayon ..........", ["Choisir...", "réfléchi", "incident"], "réfléchi", "mir_t2"),
            ("3. La droite fictive tracée à 90 degrés de la surface s'appelle la ..........", ["Choisir...", "normale", "diagonale"], "normale", "mir_t3"),
            ("4. L'intersection géométrique entre le rayon initial et le miroir est le point d'..........", ["Choisir...", "incidence", "réflexion"], "incidence", "mir_t4"),
            ("5. La surface plane séparant deux milieux transparents distincts s'appelle un ..........", ["Choisir...", "dioptre", "prisme"], "dioptre", "mir_t5"),
            ("6. Sur un miroir plan, l'angle de réflexion r est toujours .......... à l'angle d'incidence i.", ["Choisir...", "égal", "supérieur"], "égal", "mir_t6"),
            ("7. Une réflexion nette sans dispersion de la lumière est dite ..........", ["Choisir...", "spéculaire", "diffuse"], "spéculaire", "mir_t7"),
            ("8. L'angle d'incidence s'évalue strictement entre le rayon incident et la ..........", ["Choisir...", "normale", "surface"], "normale", "mir_t8"),
            ("9. Les lois physiques qui régissent le comportement de la réflexion sont les lois de ..........", ["Choisir...", "Snell-Descartes", "Newton"], "Snell-Descartes", "mir_t9"),
            ("10. Si l'angle d'incidence i augmente, l'angle de réflexion r va lui aussi ..........", ["Choisir...", "augmenter", "diminue"], "augmenter", "mir_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_miroir_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"mir_at2_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_miroir_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_mir_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_histoire_optique(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page de l'historique."""
    import random

    st.subheader("Atelier Interactif : Histoire et Fondations de l'Optique")

    questions_optique_sources = [
        {"id": "qo1", "q": "Quel scientifique du XIe siècle démontre que la lumière entre dans l'oeil ?", "options": ["Ibn al-Haytham", "René Descartes", "Willebrord Snell"], "rep": "Ibn al-Haytham"},
        {"id": "qo2", "q": "Quelle est la nationalité du mathématicien Willebrord Snell ?", "options": ["Hollandaise", "Française", "Italienne"], "rep": "Hollandaise"},
        {"id": "qo3", "q": "Dans la formule moderne n1 * sin(i1) = n2 * sin(i2), que représente la lettre 'n' ?", "options": ["L'indice de réfraction du milieu", "Le nombre de rayons lumineux", "Le niveau d'intensité de la source"], "rep": "L'indice de réfraction du milieu"},
        {"id": "qo4", "q": "Quel appareil historique Ibn al-Haytham a-t-il utilisé pour ses expériences ?", "options": ["La chambre noire", "Le microscope optique", "Le télescope réfracteur"], "rep": "La chambre noire"},
        {"id": "qo5", "q": "Sous quel nom latin le scientifique Ibn al-Haytham est-il aussi connu ?", "options": ["Alhazen", "Avicenne", "Averroès"], "rep": "Alhazen"},
        {"id": "qo6", "q": "Quelle fonction mathématique associe-t-on à la loi de Snell-Descartes pour la réfraction ?", "options": ["Le sinus (sin)", "Le cosinus (cos)", "La tangente (tan)"], "rep": "Le sinus (sin)"},
        {"id": "qo7", "q": "Dans quel ouvrage célèbre René Descartes publie-t-il sa formulation de la réfraction ?", "options": ["La Dioptrique", "Le Discours de la méthode", "Le Traité du monde"], "rep": "La Dioptrique"},
        {"id": "qo8", "q": "Comment appelle-t-on l'ancienne théorie grecque erronée qui disait que les yeux projetaient des rayons ?", "options": ["L'émission ou extramission", "L'intromission", "La réfraction passive"], "rep": "L'émission ou extramission"},
        {"id": "qo9", "q": "Lorsque la lumière passe d'un milieu moins dense à un milieu plus dense (l'air vers l'eau), le rayon dévié :", "options": ["Se rapproche de la normale", "S'éloigne de la normale", "Reste parfaitement droit"], "rep": "Se rapproche de la normale"},
        {"id": "qo10", "q": "Au cours de quel siècle les lois mathématiques de la réfraction ont-elles été fixées en Europe ?", "options": ["Le XVIIe siècle", "Le XIe siècle", "Le XIXe siècle"], "rep": "Le XVIIe siècle"}
    ]

    if "ordre_quiz_optique_aleatoire" not in st.session_state:
        random.shuffle(questions_optique_sources)
        st.session_state.ordre_quiz_optique_aleatoire = questions_optique_sources

    if "champs_optique_clean" not in st.session_state:
        st.session_state.champs_optique_clean = [
            ("1. Le père de l'optique moderne se nomme Ibn al-..........", ["Choisir...", "Haytham", "Siha"], "Haytham", "opt_t1"),
            ("2. L'appareil de la chambre noire s'appelle aussi la camera ..........", ["Choisir...", "obscura", "lucida"], "obscura", "opt_t2"),
            ("3. Snell a découvert la loi de la réfraction en utilisant la trigonométrie des ..........", ["Choisir...", "sinus", "cosinus"], "sinus", "opt_t3"),
            ("4. Le physicien français qui a donné son nom à la loi finale est René ..........", ["Choisir...", "Descartes", "Pascal"], "Descartes", "opt_t4"),
            ("5. La déviation de la lumière changeant de milieu s'appelle la ..........", ["Choisir...", "réfraction", "réflexion"], "réfraction", "opt_t5"),
            ("6. Le comportement rectiligne de la lumière signifie qu'elle se déplace en ligne ..........", ["Choisir...", "droite", "courbe"], "droite", "opt_t6"),
            ("7. Dans la loi n1*sin(i1) = n2*sin(i2), la lettre i désigne l'angle d'..........", ["Choisir...", "incidence", "intensité"], "incidence", "opt_t7"),
            ("8. L'indice optique de l'air possède une valeur de référence égale à ..........", ["Choisir...", "1", "1.33"], "1", "opt_t8"),
            ("9. Un bâton plongé dans un verre d'eau subit une illusion et semble ..........", ["Choisir...", "cassé", "plus grand"], "cassé", "opt_t9"),
            ("10. Alhazen a prouvé sa théorie en observant que la lumière de l'objet .......... dans l'oeil.", ["Choisir...", "entrait", "sortait"], "entrait", "opt_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_optique_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"opt_at1_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_optique_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_opt_clean", disabled=verrouille, label_visibility="collapsed")with tab0:
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
    st.header("Histoire et Découverte de l'Optique")
    st.write(
        "Découvrez comment l'humanité a compris la nature de la lumière, passant d'un fluide imaginaire à un comportement géométrique précis :"
    )

    # =============================================================================
    # SECTION HISTORIQUE ET SCIENTIFIQUES CLÉS
    # =============================================================================
    col_hist_1, col_hist_img1 = st.columns(2)
    
    with col_hist_1:
        st.markdown("##### La théorie de l'intromission")
        st.write(
            "Pendant longtemps, les anciens savants grecs pensaient que nos yeux émettaient des rayons visuels "
            "pour palper les objets. Au XIe siècle, le scientifique **Ibn al-Haytham** (Alhazen) démontre le contraire : "
            "la lumière entre dans notre oeil après avoir été réfléchie par les objets. Il invente la chambre noire et devance la méthode scientifique."
        )

    with col_hist_img1:
        if os.path.exists("al_haytham_portrait.jpg"):
            st.image(
                "al_haytham_portrait.jpg",
                caption="Ibn al-Haytham (Alhazen)"
            )
        else:
            st.warning(
                "L'image 'al_haytham_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    col_hist_2, col_hist_img2 = st.columns(2)
    
    with col_hist_2:
        st.markdown("##### La loi de la réfraction")
        st.write(
            "Au XVIIe siècle, la quête de la compréhension de la déviation de la lumière dans l'eau s'accélère. "
            "Le mathématicien hollandais **Willebrord Snell** découvre le rapport constant lié aux sinus des angles. "
            "Quelques années plus tard, le philosophe français **René Descartes** formalise mathématiquement la loi stricte "
            "que nous utilisons aujourd'hui en classe : n1 * sin(i1) = n2 * sin(i2)."
        )
        
    with col_hist_img2:
        col_hist_img21, col_hist_img22 = st.columns(2)
        with col_hist_img21:
            if os.path.exists("snell_portrait.jpg"):
                st.image(
                    "snell_portrait.jpg",
                    caption="Willebrord Snell",
                )
            else:
                st.warning(
                    "L'image 'snell_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )

        with col_hist_img22:
            if os.path.exists("descartes_portrait.jpg"):
                st.image(
                    "descartes_portrait.jpg",
                    caption="René Descartes",
                )
            else:
                st.warning(
                    "L'image 'descartes_portrait.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )
                  
    st.write("---")

    # =============================================================================
    # BANDE DESSINÉE HUMORISTIQUE EN 4 CASES
    # =============================================================================
    col_gauche_texte, col_droite_img = st.columns(2)

    with col_gauche_texte:
        st.write(
            "**La BD humoristique textuelle : Le mystère des rayons déviés**")
        
        st.info(
            "**Case 1 :** Un rayon lumineux voyage tranquillement en ligne droite dans l'air à une vitesse vertigineuse. "
            "Il discute avec ses photons voisins : "
            "« Tout va bien la trajectoire est parfaite, aucun obstacle en vue, on fonce à la vitesse de la lumière ! ».\n\n"
            
            "**Case 2 :** Une surface d'eau plane apparaît brusquement. Le milieu change et l'indice de réfraction augmente. "
            "L'eau ralentit brutalement le premier photon du rayon et lui crie : "
            "« Hé toi ! Ralentis immédiatement ! Ton angle d'attaque ne convient plus à mon milieu dense ! ».\n\n"
            
            "**Case 3 :** Le rayon lumineux se retrouve brisé et dévié à l'interface des deux milieux. "
            "Il panique en voyant sa direction changer selon la loi des sinus : "
            "« Oh non ! Je viens de subir une réfraction ! Mon angle d'incidence i1 s'est transformé en un angle i2 plus petit ! "
            "Je me rapproche de la normale ! ».\n\n"
            
            "**Case 4 :** Le rayon dévié continue sa course sous l'eau vers le fond du récipient. "
            "Au loin, un observateur au laboratoire regarde l'illusion d'optique et s'exclame : "
            "« C'est magique ! Le bâton plongé dans l'eau semble cassé alors qu'il est parfaitement droit ! »."
        )

    with col_droite_img:
        if os.path.exists("optique_caricature.jpg"):
            st.image(
                "optique_caricature.jpg",
                caption="Illustration humoristique du mystère des rayons déviés",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'optique_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
    
    if "suite_verrouille_tab1_optique" not in st.session_state:
        st.session_state.suite_verrouille_tab1_optique = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_optique

    # Rendu des questionnaires d'évaluation de l'Atelier 1
    afficher_atelier_histoire_optique(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique sur l'histoire de l'optique et les lois de propagation.",
        key="check_certif_opt1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_opt_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q1 = 0.0
            if "ordre_quiz_optique_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_optique_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"opt_at1_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t1 = 0.0
            if "champs_optique_clean" in st.session_state:
                for ligne in st.session_state.champs_optique_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_opt_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t1 += 1.0

            st.session_state.score_suite1_opt_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_opt_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_opt = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_optique = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab1_optique", False):
        from datetime import datetime
        scr1_t1 = st.session_state.get("score_suite1_opt_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_opt_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_opt", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_opt1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Optique - {n_eleve}</title>
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
                <p>Atelier 1 : Fondements Historiques de l'Optique (Réflexion et Réfraction)</p>
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

        if "ordre_quiz_optique_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_optique_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"opt_at1_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_opt1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_optique_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_optique_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_opt_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_opt1 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_opt1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement du fichier HTML généré
        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Historique_Optique") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION OFFICIEL (HTML)",
            data=html_export_opt1,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_opt"
        )

with tab2:
    st.header("Loi de la réflexion pour un miroir plan")
    st.write(
        "Explorez la façon dont un rayon lumineux interagit avec une surface lisse et réfléchissante à travers les définitions de cours et notre simulateur de laboratoire :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_def_texte, col_def_alerte_img = st.columns(2)
    
    with col_def_texte:
        st.markdown("##### Vocabulaire fondamental de l'optique géométrique")
        st.write(
            "**Surface réfléchissante (ou miroir plan) :** Interface lisse qui renvoie la totalité de la "
            "lumière reçue dans une direction privilégiée sans la disperser.\n\n"
            
            "**Dioptre plan :** Surface géométrique plane séparant deux milieux transparents d'indices de "
            "réfraction différents (dans le cas du miroir, la lumière ne traverse pas ce dioptre, elle rebondit).\n\n"
            
            "**Rayon incident :** Rayon lumineux provenant de la source (laser) qui se dirige vers la surface du miroir.\n\n"
            
            "**Point d'incidence (I) :** Point d'intersection exact où le rayon incident frappe le miroir.\n\n"
            
            "**La Normale :** Ligne imaginaire tracée perpendiculairement (à 90 degrés) à la surface du miroir au point d'incidence. Toutes les mesures d'angles s'effectuent par rapport à cette droite de référence.\n\n"
            
            "**Rayon réfléchi :** Rayon lumineux qui repart du point d'incidence après avoir rebondi sur la surface."
        )

    with col_def_alerte_img:
        # Bloc de texte avec fond bleu stylisé
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Notice d'utilisation du Laboratoire</h4>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Première loi de Snell-Descartes :</b> Le rayon incident, le rayon réfléchi et la normale au dioptre réfléchi sont tous situés dans un même plan appelé le plan d'incidence.</p>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Deuxième loi de Snell-Descartes :</b> L'angle de réflexion r est rigoureusement égal à l'angle d'incidence i. Mathématiquement, on écrit : <b>i = r</b>.</p>
            <p style="font-size: 14px; margin-bottom: 0;">Utilisez les commandes du module ci-dessous pour modifier dynamiquement les paramètres du banc d'essai optique virtuel.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("miroir_plan_schema.jpg"):
            st.image(
                "miroir_plan_schema.jpg",
                caption="Schéma annoté structurel du miroir plan"
            )
        else:
            st.warning(
                "L'image 'miroir_plan_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION DU LASER INTERACTIF
    # =============================================================================
    st.subheader("Simulateur de Banc Optique Virtuel")
    
    # Zone de contrôle des paramètres de la simulation
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        angle_inc = st.slider(
            "Ajuster l'angle d'incidence (i) en degrés par rapport à la normale :",
            min_value=0,
            max_value=85,
            value=30,
            step=1
        )
    with col_ctrl2:
        couleur_nom = st.selectbox(
            "Sélectionner la couleur du faisceau laser :",
            options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"]
        )
    
    # Dictionnaire de correspondance pour le rendu graphique Matplotlib
    carte_couleurs = {
        "Rouge": "#ff0000",
        "Bleu": "#0000ff",
        "Vert": "#00ff00",
        "Jaune": "#eeee00",
        "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # Génération du graphique de simulation dynamique
    import matplotlib.pyplot as plt
    import numpy as np

    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Tracé de la surface du miroir plan (Axe horizontal y=0)
    ax.plot([-10, 10], [0, 0], color="#64748b", linewidth=6, label="Miroir Plan")
    # Ajout d'une hachure sous le miroir pour symboliser la face opaque cachée
    ax.fill_between([-10, 10], 0, -1, color="#cbd5e1", hatch="//", alpha=0.3)
    
    # Tracé de la Normale perpendiculaire au point d'incidence (0,0)
    ax.plot([0, 0], [0, 10], color="#475569", linestyle="--", linewidth=2, label="La Normale")
    
    # Calcul des vecteurs unitaires pour le rayon incident et réfléchi
    # En optique géométrique, l'angle est donné par rapport à la verticale (normale)
    rad_inc = np.radians(angle_inc)
    
    # Rayon incident arrivant de la gauche vers l'origine (0,0)
    x_inc = -8 * np.sin(rad_inc)
    y_inc = 8 * np.cos(rad_inc)
    ax.annotate(
        "", xy=(0, 0), xytext=(x_inc, y_inc),
        arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15)
    )
    
    # Rayon réfléchi repartant de l'origine (0,0) vers la droite
    x_ref = 8 * np.sin(rad_inc)
    y_ref = 8 * np.cos(rad_inc)
    ax.annotate(
        "", xy=(x_ref, y_ref), xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15)
    )
    
    # Textes indicatifs et étiquettes d'angles dynamiques sur le graphique
    ax.text(x_inc - 0.5, y_inc + 0.3, "Rayon Incident", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(x_ref - 0.5, y_ref + 0.3, "Rayon Réfléchi", fontsize=10, fontweight="bold", color="#1e293b")
    ax.text(-0.5, 10.3, "Normale", fontsize=10, color="#475569")
    
    # Affichage des valeurs numériques d'angles lues en temps réel
    ax.text(-3, 2, f"i = {angle_inc}°", fontsize=12, color="#0f172a", fontweight="bold")
    ax.text(1.5, 2, f"r = {angle_inc}°", fontsize=12, color="#0f172a", fontweight="bold")
    
    # Décoration et limites de la zone graphique
    ax.set_xlim(-10, 10)
    ax.set_ylim(-2, 11)
    ax.axis("off") # Suppression des axes gradués pour un rendu épuré de type schéma
    
    # Rendu final de la simulation dans Streamlit
    st.pyplot(fig)

    # Affichage de la boîte de contrôle et de validation des données numériques
    st.info(
        f"**Données du tableau d'expérimentation lues en temps réel :**\n\n"
        f"Angle mesuré du rayon incident par rapport à la normale : **{angle_inc}°**\n\n"
        f"Angle mesuré du rayon réfléchi obtenu sur le cadran gradué : **{angle_inc}°**\n\n"
        f"Constat vérifié : L'égalité mathématique fondamentale **i = r** est validée."
    )

    # Préparation et sauvegarde dynamique du fichier texte brut associé à cet onglet
    nom_fic = preparer_nom_fichier("Miroir_Plan")
    donnees_sauvegarde = (
        f"RAPPORT EXPERIMENTAL - LOI DE LA REFLEXION\n"
        f"Angle d'incidence teste : {angle_inc} degres\n"
        f"Angle de reflexion observe : {angle_inc} degres\n"
        f"Resultat : Conformite aux lois de Snell-Descartes etablie."
    )
    
    st.download_button(
        label="Télécharger les données de mesures de cet onglet",
        data=donnees_sauvegarde,
        file_name=nom_fic,
        mime="text/plain",
        use_container_width=True,
        key="btn_download_mesures_miroir_plan"
    )

    if "suite_verrouille_tab2_miroir" not in st.session_state:
        st.session_state.suite_verrouille_tab2_miroir = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_miroir

    # Rendu des questionnaires d'évaluation de l'Atelier 2
    afficher_atelier_miroir_plan(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Loi de la Réflexion pour un miroir plan.",
        key="check_certif_mir2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_mir_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q2 = 0.0
            if "ordre_quiz_miroir_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_miroir_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"mir_at2_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q2 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t2 = 0.0
            if "champs_miroir_clean" in st.session_state:
                for ligne in st.session_state.champs_miroir_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_mir_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t2 += 1.0

            st.session_state.score_suite2_mir_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_mir_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_mir = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_miroir = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab2_miroir", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_mir_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_mir_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_mir", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MIROIR PLAN SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_mir2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Miroir Plan - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 2 : Loi de la Réflexion pour un Miroir Plan (i = r)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
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

        if "ordre_quiz_miroir_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_miroir_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"mir_at2_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mir2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mir2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_miroir_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_miroir_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_mir_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_mir2 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_mir2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement du fichier HTML généré
        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Miroir_Plan") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DU MIROIR PLAN (HTML)",
            data=html_export_mir2,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_mir"
        )

with tab3:
    st.header("Loi de la réfraction (Loi de Snell-Descartes)")
    st.write(
        "Explorez la façon dont la lumière change de direction lorsqu'elle passe d'un matériau transparent à un autre :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_ref_texte, col_ref_alerte_img = st.columns(2)
    
    with col_ref_texte:
        st.markdown("##### Vocabulaire fondamental de la réfraction")
        st.write(
            "**Dioptre plan :** Surface géométrique plane séparant deux milieux transparents distincts dotés d'un indice optique différent (comme la surface séparant l'air et l'eau).\n\n"
            
            "**Rayon incident :** Rayon lumineux provenant de la source (laser) voyageant dans le premier milieu (Milieu 1) et se dirigeant vers l'interface.\n\n"
            
            "**La Normale :** Ligne imaginaire tracée perpendiculairement (à 90 degrés) à la surface de séparation au point d'incidence. Tous les angles s'évaluent par rapport à elle.\n\n"
            
            "**Rayon réfracté :** Faisceau lumineux transmis dans le second milieu (Milieu 2). Sa trajectoire subit une déviation géométrique brusque à l'interface.\n\n"
            
            "**Indice de réfraction (n) :** Grandeur sans unité caractérisant la vitesse de propagation de la lumière dans un matériau (n = c / v). Plus l'indice est élevé, plus le milieu ralentit le faisceau."
        )

    with col_ref_alerte_img:
        # Bloc de texte avec fond bleu stylisé
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Notice d'utilisation de la Réfraction</h4>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Relation de Snell-Descartes :</b> Le comportement mathématique s'écrit de la façon suivante : <b>n1 * sin(i1) = n2 * sin(i2)</b>.</p>
            <p style="font-size: 14px; margin-bottom: 8px;"><b>Milieu moins réfringent vers plus réfringent (n1 < n2) :</b> Le rayon dévié se rapproche de la normale.</p>
            <p style="font-size: 14px; margin-bottom: 0;"><b>Milieu plus réfringent vers moins réfringent (n1 > n2) :</b> Le rayon dévié s'éloigne de la normale. Si l'angle d'incidence est trop important, la réfraction disparaît au profit d'une réflexion totale.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("loi_refraction_schema.jpg"):
            st.image(
                "loi_refraction_schema.jpg",
                caption="Schéma annoté structurel de la réfraction"
            )
        else:
            st.warning(
                "L'image 'loi_refraction_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION DU LABORATOIRE DE RÉFRACTION INTERACTIF
    # =============================================================================
    st.subheader("Simulateur de Réfraction et Recherche d'Indices")
    
    # Base de données exhaustive de 30 milieux avec leurs indices de réfraction réels
    base_milieux = {
        "Vide (n = 1.0000)": 1.0,
        "Hydrogène gaz (n = 1.0001)": 1.0001,
        "Air (n = 1.0003)": 1.0003,
        "Dioxyde de carbone gaz (n = 1.0005)": 1.0005,
        "Glace (n = 1.3100)": 1.31,
        "Eau (n = 1.3330)": 1.333,
        "Acétone (n = 1.3590)": 1.359,
        "Éthanol / Alcool (n = 1.3610)": 1.361,
        "Solution sucrée 30% (n = 1.3800)": 1.38,
        "Kérosène (n = 1.4400)": 1.440,
        "Quartz fondu (n = 1.4580)": 1.458,
        "Glycerine (n = 1.4730)": 1.473,
        "Huile minérale (n = 1.4800)": 1.480,
        "Huile d'olive (n = 1.4900)": 1.490,
        "Benzène (n = 1.5010)": 1.501,
        "Plexiglas / PMMA (n = 1.5100)": 1.510,
        "Verre Crown standard (n = 1.5200)": 1.520,
        "Sel de table / Halite (n = 1.5440)": 1.544,
        "Verre Flint léger (n = 1.5800)": 1.580,
        "Polystyrène plastique (n = 1.5900)": 1.590,
        "Ambre (n = 1.6000)": 1.600,
        "Sulfure de carbone (n = 1.6280)": 1.628,
        "Verre Flint lourd (n = 1.6600)": 1.660,
        "Topaze (n = 1.6200)": 1.620,
        "Saphir / Corindon (n = 1.7700)": 1.770,
        "Rubis (n = 1.7650)": 1.765,
        "Zircon (n = 1.9200)": 1.920,
        "Soufre solide (n = 1.9600)": 1.960,
        "Oxyde de zinc (n = 2.0000)": 2.0,
        "Diamant (n = 2.4170)": 2.417
    }

    # Configuration des entrées utilisateur du simulateur
    col_sel1, col_sel2, col_sel3 = st.columns(3)
    with col_sel1:
        nom_milieu1 = st.selectbox("Choisir le Milieu 1 (milieu supérieur) :", options=list(base_milieux.keys()), index=2) # Par défaut l'Air
        n1 = base_milieux[nom_milieu1]
    with col_sel2:
        nom_milieu2 = st.selectbox("Choisir le Milieu 2 (milieu inférieur) :", options=list(base_milieux.keys()), index=5) # Par défaut l'Eau
        n2 = base_milieux[nom_milieu2]
    with col_sel3:
        couleur_nom = st.selectbox("Choisir la couleur du laser :", options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"], key="laser_refraction")

    angle_i1 = st.slider(
        "Ajuster l'angle d'incidence (i1) en degrés :",
        min_value=0,
        max_value=89,
        value=45,
        step=1
    )

    carte_couleurs = {
        "Rouge": "#ff0000", "Bleu": "#0000ff", "Vert": "#00ff00", "Jaune": "#eeee00", "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # =============================================================================
    # CALCUL MATHÉMATIQUE DE LA RÉFRACTION (SNELL-DESCARTES)
    # =============================================================================
    import matplotlib.pyplot as plt
    import numpy as np

    rad_i1 = np.radians(angle_i1)
    argument_sin = (n1 * np.sin(rad_i1)) / n2
    
    reflexion_totale = False
    angle_i2_deg = 0.0

    if argument_sin > 1.0:
        reflexion_totale = True
    else:
        rad_i2 = np.arcsin(argument_sin)
        angle_i2_deg = np.degrees(rad_i2)

    # Création de l'affichage graphique vectoriel
    fig, ax = plt.subplots(figsize=(8, 7))
    
    # Remplissage coloré des deux milieux transparents
    ax.fill_between([-10, 10], 0, 10, color="#f8fafc", alpha=0.5) # Milieu 1 en haut
    ax.fill_between([-10, 10], -10, 0, color="#f0fdf4" if n2 > n1 else "#fff7ed", alpha=0.5) # Milieu 2 en bas
    
    # Tracé du Dioptre Plan (Ligne horizontale y=0) et de la Normale (Axe vertical x=0)
    ax.plot([-10, 10], [0, 0], color="#334155", linewidth=3, label="Dioptre Plan")
    ax.plot([0, 0], [-10, 10], color="#94a3b8", linestyle="--", linewidth=2)
    
    # Tracé du rayon incident (Milieu 1, quadrant supérieur gauche)
    x_inc = -8 * np.sin(rad_i1)
    y_inc = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(0, 0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
    ax.text(x_inc - 0.5, y_inc + 0.4, "Rayon Incident", fontsize=10, fontweight="bold")

    # Tracé automatique du reflet (Rayon réfléchi résiduel permanent sur le dioptre)
    x_ref = 8 * np.sin(rad_i1)
    y_ref = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(x_ref, y_ref), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=1.5, linestyle=":", alpha=0.6))

    if reflexion_totale:
        # En cas de réflexion totale, le rayon rebondit entièrement dans le milieu 1
        ax.annotate("", xy=(8 * np.sin(rad_i1), 8 * np.cos(rad_i1)), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(4, 4, "Réflexion Totale", color="#ef4444", fontsize=12, fontweight="bold")
    else:
        # Tracé du rayon réfracté (Milieu 2, quadrant inférieur droit)
        x_fra = 8 * np.sin(rad_i2)
        y_fra = -8 * np.cos(rad_i2)
        ax.annotate("", xy=(x_fra, y_fra), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(x_fra - 0.5, y_fra - 0.8, "Rayon Réfracté", fontsize=10, fontweight="bold")
        ax.text(1, -2, f"i2 = {angle_i2_deg:.1f}°", fontsize=12, fontweight="bold", color="#15803d")

    # Inscriptions et mise en page du graphique
    ax.text(-9, 8, f"Milieu 1 : n1 = {n1:.4f}", fontsize=11, color="#1e3a8a", fontweight="bold")
    ax.text(-9, -8, f"Milieu 2 : n2 = {n2:.4f}", fontsize=11, color="#166534", fontweight="bold")
    ax.text(-1.5, 2, f"i1 = {angle_i1}°", fontsize=12, fontweight="bold", color="#1e3a8a")
    ax.text(0.3, 9, "Normale", fontsize=9, color="#94a3b8")
    
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.axis("off")
    st.pyplot(fig)

    # Message de synthèse des résultats numériques lus en temps réel
    if reflexion_totale:
        st.error(
            f"**Constat Expérimental - Phénomène de Réflexion Totale :**\n\n"
            f"L'indice du premier milieu (**n1 = {n1}**) est plus grand que celui du deuxième milieu (**n2 = {n2}**).\n\n"
            f"Pour l'angle d'incidence choisi (**{angle_i1}°**), la valeur mathématique dépasse la limite critique. "
            f"La lumière ne peut plus traverser la surface et se retrouve piégée, se réfléchissant à 100% dans le premier milieu."
        )
    else:
        st.info(
            f"**Données du tableau de réfraction enregistrées :**\n\n"
            f"Angle d'incidence mesuré dans le milieu 1 ($i_1$) : **{angle_i1}°**\n\n"
            f"Angle de réfraction calculé dans le milieu 2 ($i_2$) : **{angle_i2_deg:.2f}°**"
        ) # Fermeture correcte de la f-string et de st.info()

    # Le code suivant reprend avec l'alignement général de l'onglet
    nom_fic = preparer_nom_fichier("Loi_Refraction")
    donnees_sauvegarde = (
        f"RAPPORT EXPERIMENTAL - LOI DE LA REFRACTION\n"
        f"Milieu 1 : {nom_milieu1} (n1 = {n1})\n"
        f"Milieu 2 : {nom_milieu2} (n2 = {n2})\n"
        f"Angle d'incidence i1 : {angle_i1} degres\n"
        f"Resultat mesure i2 : {angle_i2_deg:.2f} degres\n"
    )
    
    st.download_button(
        label="Télécharger les données de mesures de la réfraction",
        data=donnees_sauvegarde,
        file_name=nom_fic,
        mime="text/plain",
        use_container_width=True,
        key="btn_download_mesures_refraction"
    )


    if "suite_verrouille_tab3_refraction" not in st.session_state:
        st.session_state.suite_verrouille_tab3_refraction = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_refraction

    # Rendu des questionnaires d'évaluation de l'Atelier 3
    afficher_atelier_refraction(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Loi de la Réfraction.",
        key="check_certif_ref3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_ref_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q3 = 0.0
            if "ordre_quiz_refraction_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_refraction_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"ref_at3_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t3 = 0.0
            if "champs_refraction_clean" in st.session_state:
                for ligne in st.session_state.champs_refraction_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_ref_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_ref_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_ref_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_ref = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_refraction = True
            st.st.unhandled_status_code_exception_handler = None  # Reset temporaire si nécessaire
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab3_refraction", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_ref_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_ref_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_ref", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RÉFRACTION SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_ref3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réfraction - {n_eleve}</title>
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
                <p>Atelier 3 : Lois de la Réfraction (Snell-Descartes)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
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

        if "ordre_quiz_refraction_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_refraction_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"ref_at3_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ref3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ref3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_refraction_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_refraction_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_ref_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ref3 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ref3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Refraction") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE LA RÉFRACTION (HTML)",
            data=html_export_ref3,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_ref"
        )


with tab4:
    st.header("La réflexion totale")
    st.write(
        "Découvrez le phénomène de réflexion totale, une condition limite de la réfraction essentielle au fonctionnement des technologies modernes :"
    )

    # =============================================================================
    # SECTION DÉFINITIONS THÉORIQUES ET SCHÉMA D'ORIENTATION
    # =============================================================================
    col_tot_texte, col_tot_alerte_img = st.columns(2)
    
    with col_tot_texte:
        st.markdown("##### Principes physiques et Angle Critique")
        st.write(
            "**Condition de départ :** La réflexion totale ne peut avoir lieu que si la lumière tente de passer d'un "
            "milieu plus réfringent (indice $n_1$ élevé) vers un milieu moins réfringent (indice $n_2$ plus bas). Exemple : du verre vers l'air.\n\n"
            
            "**Angle limite de réfraction :** À mesure que l'angle d'incidence $i_1$ augmente, le rayon réfracté s'éloigne "
            "de la normale jusqu'à s'aligner parallèlement au dioptre ($\hat{\imath}_2 = 90^\circ$).\n\n"
            
            "**L'Angle Critique ($\lambda$) :** C'est l'angle d'incidence exact pour lequel $\hat{\imath}_2 = 90^\circ$. "
            "Sa valeur mathématique se calcule par la relation : **$\sin(\lambda) = n_2 / n_1$**.\n\n"
            
            "**Réflexion totale interne :** Si l'angle d'incidence dépasse cet angle critique ($\hat{\imath}_1 > \lambda$), "
            "la réfraction devient mathématiquement et physiquement impossible. Le dioptre se comporte alors comme un miroir parfait "
            "et renvoie 100% de la lumière.\n\n"
            
            "**Applications réelles :** Ce phénomène permet de guider la lumière dans le cœur des fibres optiques (télécommunications, "
            "endoscopie médicale), dans les prismes des paires de jumelles et explique la formation des mirages."
        )

    with col_tot_alerte_img:
        st.markdown("""
        <div style="background-color: #e6f3ff; padding: 20px; border-radius: 8px; border-left: 6px solid #0066cc; font-family: sans-serif; color: #333333;">
            <h4 style="color: #004488; margin-top: 0; font-size: 16px;">Consigne du Laboratoire</h4>
            <p style="font-size: 14px; margin-bottom: 8px;">Pour pouvoir observer une réflexion totale dans le module ci-dessous, assurez-vous de choisir un <b>Milieu 1 supérieur à votre Milieu 2</b> (par exemple : le Diamant vers l'Air).</p>
            <p style="font-size: 14px; margin-bottom: 0;">Augmentez ensuite l'angle d'incidence à l'aide du curseur pour franchir le seuil de l'angle critique calculated en temps réel.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if os.path.exists("reflexion_totale_schema.jpg"):
            st.image(
                "reflexion_totale_schema.jpg",
                caption="Schéma structurel de la réflexion totale"
            )
        else:
            st.warning(
                "L'image 'reflexion_totale_schema.jpg' est introuvable. Placez l'illustration annotée fixe dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # INTERFACE DE SIMULATION INTERACTIVE DE L'ANGLE CRITIQUE
    # =============================================================================
    st.subheader("Simulateur d'Angle Limite Critique")
    
    # Base de données identique de 30 milieux
    base_milieux = {
        "Vide (n = 1.0000)": 1.0, "Hydrogène gaz (n = 1.0001)": 1.0001, "Air (n = 1.0003)": 1.0003,
        "Dioxyde de carbone gaz (n = 1.0005)": 1.0005, "Glace (n = 1.3100)": 1.31, "Eau (n = 1.3330)": 1.333,
        "Acétone (n = 1.3590)": 1.359, "Éthanol / Alcool (n = 1.3610)": 1.361, "Solution sucrée 30% (n = 1.3800)": 1.38,
        "Kérosène (n = 1.4400)": 1.44, "Quartz fondu (n = 1.4580)": 1.458, "Glycerine (n = 1.4730)": 1.473,
        "Huile minérale (n = 1.4800)": 1.48, "Huile d'olive (n = 1.4900)": 1.49, "Benzène (n = 1.5010)": 1.501,
        "Plexiglas / PMMA (n = 1.5100)": 1.51, "Verre Crown standard (n = 1.5200)": 1.52, "Sel de table / Halite (n = 1.5440)": 1.544,
        "Verre Flint léger (n = 1.5800)": 1.58, "Polystyrène plastique (n = 1.5900)": 1.59, "Ambre (n = 1.6000)": 1.6,
        "Sulfure de carbone (n = 1.6280)": 1.628, "Verre Flint lourd (n = 1.6600)": 1.66, "Topaze (n = 1.6200)": 1.62,
        "Saphir / Corindon (n = 1.7700)": 1.77, "Rubis (n = 1.7650)": 1.765, "Zircon (n = 1.9200)": 1.92,
        "Soufre solide (n = 1.9600)": 1.96, "Oxyde de zinc (n = 2.0000)": 2.0, "Diamant (n = 2.4170)": 2.417
    }

    col_tot1, col_tot2, col_tot3 = st.columns(3)
    with col_tot1:
        nom_milieu1 = st.selectbox("Choisir le Milieu 1 (milieu émetteur) :", options=list(base_milieux.keys()), index=29) # Diamant par défaut
        n1 = base_milieux[nom_milieu1]
    with col_tot2:
        nom_milieu2 = st.selectbox("Choisir le Milieu 2 (milieu récepteur) :", options=list(list(base_milieux.keys())), index=2) # Air par défaut
        n2 = base_milieux[nom_milieu2]
    with col_tot3:
        couleur_nom = st.selectbox("Choisir la couleur du laser :", options=["Rouge", "Bleu", "Vert", "Jaune", "Violet"], key="laser_totale")

    angle_i1 = st.slider("Ajuster l'angle d'incidence (i1) :", min_value=0, max_value=89, value=35, step=1)
    
    carte_couleurs = {
        "Rouge": "#ff0000", "Bleu": "#0000ff", "Vert": "#00ff00", "Jaune": "#eeee00", "Violet": "#8b008b"
    }
    couleur_laser = carte_couleurs[couleur_nom]

    # Calcul de l'angle limite physique
    angle_limite_possible = n1 > n2
    angle_critique_deg = 0.0
    if angle_limite_possible:
        angle_critique_deg = np.degrees(np.arcsin(n2 / n1))

    # Logique de trajectoire
    import matplotlib.pyplot as plt
    import numpy as np

    rad_i1 = np.radians(angle_i1)
    argument_sin = (n1 * np.sin(rad_i1)) / n2
    reflexion_totale = argument_sin > 1.0 or angle_i1 > angle_critique_deg

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.fill_between([-10, 10], 0, 10, color="#f8fafc", alpha=0.5)
    ax.fill_between([-10, 10], -10, 0, color="#fff1f2" if reflexion_totale else "#f0fdf4", alpha=0.5)
    ax.plot([-10, 10],, color="#334155", linewidth=3)
    ax.plot(, [-10, 10], color="#94a3b8", linestyle="--", linewidth=2)

    # Tracé incident
    x_inc = -8 * np.sin(rad_i1)
    y_inc = 8 * np.cos(rad_i1)
    ax.annotate("", xy=(0, 0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))

    if angle_limite_possible:
        ax.text(-9, 6, f"Angle critique limite lambda = {angle_critique_deg:.2f}°", color="#b91c1c", fontweight="bold")

    if reflexion_totale:
        # Faisceau réfléchi complet à 100%
        x_ref = 8 * np.sin(rad_i1)
        y_ref = 8 * np.cos(rad_i1)
        ax.annotate("", xy=(x_ref, y_ref), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(3, 4, "RÉFLEXION TOTALE INTERNE", color="#b91c1c", fontsize=11, fontweight="bold")
    else:
        # Faisceau réfracté classique
        rad_i2 = np.arcsin(argument_sin)
        x_fra = 8 * np.sin(rad_i2)
        y_fra = -8 * np.cos(rad_i2)
        ax.annotate("", xy=(x_fra, y_fra), xytext=(0, 0), arrowprops=dict(arrowstyle="->", color=couleur_laser, linewidth=3, mutation_scale=15))
        ax.text(x_fra, y_fra - 0.5, f"i2 = {np.degrees(rad_i2):.1f}°", fontsize=11, color="#166534", fontweight="bold")

    ax.text(-9, 8, f"Milieu 1 : n1 = {n1:.4f}", fontsize=10, fontweight="bold")
    ax.text(-9, -8, f"Milieu 2 : n2 = {n2:.4f}", fontsize=10, fontweight="bold")
    ax.axis("off")
    st.pyplot(fig)

    # Message informatif
    if not angle_limite_possible:
        st.warning("Calcul impossible : n1 est inférieur ou égal à n2. La lumière s'écarte du dioptre, il n'existe aucun angle critique pour cette configuration.")
    elif reflexion_totale:
        st.error(f"Données enregistrées : Angle d'incidence choisi ({angle_i1}°) supérieur à la limite ({angle_critique_deg:.2f}°). Le rayon est piégé.")
    else:
        st.info(f"Données enregistrées : Angle d'incidence ({angle_i1}°) inférieur à l'angle critique ({angle_critique_deg:.2f}°). Le faisceau traverse et se réfracte.")

    # Enregistrement brut
    nom_fic = preparer_nom_fichier("Reflexion_Totale")
    verdict_sauve = "Reflexion Totale Active" if reflexion_totale else "Refraction simple"
    donnees_sauvegarde = f"RAPPORT EXPERIMENTAL - REFLEXION TOTALE\nMilieu 1 : {nom_milieu1}\nMilieu 2 : {nom_milieu2}\nAngle i1 : {angle_i1} degres\nVerdict : {verdict_sauve}\n"
    
    st.download_button(
        label="Télécharger les données de mesures de la réflexion totale",
        data=donnees_sauvegarde, file_name=nom_fic, mime="text/plain", use_container_width=True, key="btn_download_mesures_totale"
    )

    # -------------------------------------------------------------------------
    # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
    # -------------------------------------------------------------------------
    if "suite_verrouille_tab4_totale" not in st.session_state:
        st.session_state.suite_verrouille_tab4_totale = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_totale

    afficher_atelier_reflexion_totale(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Réflexion Totale.",
        key="check_certif_tot4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_tot_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q4 = 0.0
            if "ordre_quiz_totale_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_totale_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"tot_at4_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t4 = 0.0
            if "champs_totale_clean" in st.session_state:
                for ligne in st.session_state.champs_totale_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_tot_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t4 += 1.0

            st.session_state.score_suite4_tot_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_tot_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_tot = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_totale = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab4_totale", False):
        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_tot_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_tot_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_tot", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RÉFLEXION TOTALE SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_tot4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Réflexion Totale - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b91c1c; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 4 : Phénomène de Réflexion Totale Interne</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #b91c1c;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_totale_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_totale_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"tot_at4_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tot4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tot4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_totale_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_totale_clean, 1):
                cle_variable = ligne[-1]
                enonce_phrase = ligne[0]
                attendu = ligne[2]
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_tot_clean"):
                        saisie = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tot4 += f"<tr><td>{num}</td><td>{enonce_phrase}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tot4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_telechargement = preparer_nom_fichier("Rapport_Reflexion_Totale") + ".html"
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT D'ÉVALUATION DE LA RÉFLEXION TOTALE (HTML)",
            data=html_export_tot4,
            file_name=nom_fichier_telechargement,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_scelle_tot"
        )













