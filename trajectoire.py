# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application trajectoire",
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
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import streamlit.components.v1 as components
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application trajectoire")
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
    "Permis B",
    "Permis B et caravane",
    "Permis CE",
    "Permis CE et caravane",
    "Permis C",
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]

def afficher_atelier_permis_b(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour le permis B."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique du Véhicule Léger")

    questions_sources = [
        {"id": "qb1", "q": "Pourquoi le décalage de chasse d'une voiture est-il beaucoup plus faible que celui d'un porteur ?", "options": ["Parce que son empattement est plus court", "Parce qu'elle roule plus vite", "En raison de son aérodynamisme"], "rep": "Parce que son empattement est plus court"},
        {"id": "qb2", "q": "Quelle force retient la voiture vers l'intérieur du virage pour contrecarrer la force centrifuge ?", "options": ["La force de frottement latéral des pneus", "Le poids du moteur", "La réaction normale du châssis"], "rep": "La force de frottement latéral des pneus"},
        {"id": "qb3", "q": "Quel paramètre géométrique du véhicule influe directement sur la valeur du décalage de chasse ?", "options": ["L'empattement (distance entre essieux)", "La largeur des pneumatiques", "La masse totale"], "rep": "L'empattement (distance entre essieux)"},
        {"id": "qb4", "q": "Quelle est l'unité de mesure de l'accélération transversale subie par les passagers ?", "options": ["Le G (fraction de g)", "Le Newton (N)", "Le Pascal (Pa)"], "rep": "Le G (fraction de g)"},
        {"id": "qb5", "q": "Si le véhicule glisse vers l'extérieur du virage sans tourner assez, on parle de :", "options": ["Sous-virage (perte d'adhérence AV)", "Survirage (perte d'adhérence AR)", "Mise en portefeuille"], "rep": "Sous-virage (perte d'adhérence AV)"},
        {"id": "qb6", "q": "Pourquoi une voiture a-t-elle moins de risques de basculer qu'un camion porteur ?", "options": ["Son centre de gravité est beaucoup plus bas", "Ses pneus sont plus larges", "Elle possède un devers naturel"], "rep": "Son centre de gravité beaucoup plus bas"},
        {"id": "qb7", "q": "Quelle action du conducteur augmente instantanément la force centrifuge au milieu de la courbe ?", "options": ["Une augmentation de la vitesse", "Un coup de frein sec", "Un débrayage"], "rep": "Une augmentation de la vitesse"},
        {"id": "qb8", "q": "Quel élément de l'infrastructure routière permet de réduire l'effort de friction demandé aux pneus ?", "options": ["Le dévers positif de la chaussée", "Les bandes rugueuses", "Les lignes blanches"], "rep": "Le dévers positif de la chaussée"},
        {"id": "qb9", "q": "Sur le graphique, quelle ligne de couleur correspond à l'essieu avant directeur ?", "options": ["La ligne rouge", "La ligne bleue", "La ligne noire concentrique"], "rep": "La ligne rouge"},
        {"id": "qb10", "q": "L'adhérence maximale disponible entre le pneu et le sol dépend du coefficient de :", "options": ["Frottement (mu)", "Raideur de dérive", "Renversement statique"], "rep": "Frottement (mu)"}
    ]

    if "ordre_quiz_b_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_b_aleatoire = questions_sources

    if "champs_b_clean" not in st.session_state:
        st.session_state.champs_b_clean = [
            ("1. Le décalage de chasse d'une voiture est réduit car son .......... est court.", ["Choisir...", "empattement", "porte-à-faux"], "empattement", "b_t1"),
            ("2. Les roues avant guident la trajectoire et sont tracées en ..........", ["Choisir...", "rouge", "bleu"], "rouge", "b_t2"),
            ("3. La force centrifuge pousse la voiture vers l'.......... de la courbe.", ["Choisir...", "extérieur", "intérieur"], "extérieur", "b_t3"),
            ("4. À vitesse élevée, si l'effort requis dépasse l'adhérence, il y a ..........", ["Choisir...", "glissement", "basculement"], "glissement", "b_t4"),
            ("5. La force verticale exercée par la route sur les roues est la réaction ..........", ["Choisir...", "normale", "tangentielle"], "normale", "b_t5"),
            ("6. Le risque de renversement est minime car le centre de gravité est ..........", ["Choisir...", "bas", "haut"], "bas", "b_t6"),
            ("7. L'inclinaison de la route appelée .......... améliore la tenue de route.", ["Choisir...", "dévers", "pente"], "dévers", "b_t7"),
            ("8. L'accélération transversale maximale s'exprime en unités ..........", ["Choisir...", "G", "Newton"], "G", "b_t8"),
            ("9. Les roues arrière coupent légèrement le virage et sont tracées en ..........", ["Choisir...", "bleu", "rouge"], "bleu", "b_t9"),
            ("10. Si le véhicule franchit les marquages au sol, il y a .......... de route.", ["Choisir...", "sortie", "stabilité"], "sortie", "b_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_b_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"b_at1_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_b_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_b_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_permis_b_caravane(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour le permis B + caravane."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique de l'Attelage Légat")

    questions_sources = [
        {"id": "qca1", "q": "Pourquoi une caravane coupe-t-elle le virage vers l'intérieur de la courbe ?", "options": ["En raison de la chasse cinématique liée à l'attelage", "À cause d'un manque de puissance de la voiture", "Parce que ses pneus glissent d'office"], "rep": "En raison de la chasse cinématique liée à l'attelage"},
        {"id": "qca2", "q": "Quel point d'articulation relie la caravane au porte-à-faux arrière de la voiture ?", "options": ["La rotule d'attelage", "La sellette de pivotement", "L'essieu équivalent"], "rep": "La rotule d'attelage"},
        {"id": "qca3", "q": "Quel paramètre amplifie le déport de la caravane vers la corde au début de la manœuvre ?", "options": ["La longueur de la flèche (timon)", "La masse des bagages", "L'aérodynamisme de la remorque"], "rep": "La longueur de la flèche (timon)"},
        {"id": "qca4", "q": "Comment se comportent les trajectoires des roues avant et de la caravane en ligne droite initiale ?", "options": ["Les trois trajectoires fusionnent horizontalement", "Elles sont déjà écartées de un mètre", "Elles forment un angle droit"], "rep": "Les trois trajectoires fusionnent horizontalement"},
        {"id": "qca5", "q": "Le phénomène d'oscillation dangereux d'une caravane à haute vitesse s'appelle :", "options": ["Le louvoiement ou mise en lacet", "Le sous-virage cinématique", "Le basculement statique"], "rep": "Le louvoiement ou mise en lacet"},
        {"id": "qca6", "q": "Quel est le comportement de la ligne rouge (roues avant) lors de l'amorce du virage ?", "options": ["Elle commence à tourner pile sur la ligne verticale 0", "Elle commence à s'écarter deux mètres avant", "Elle reste rectiligne tout au long de la course"], "rep": "Elle commence à tourner pile sur la ligne verticale 0"},
        {"id": "qca7", "q": "Quel élément graphique représente le train suiveur de l'ensemble articulé ?", "options": ["La ligne bleue pointillée", "La ligne rouge lisse", "Les lignes noires concentriques"], "rep": "La ligne bleue pointillée"},
        {"id": "qca8", "q": "Si la vitesse de l'attelage est excessive dans une courbe serrée, quel accident est redouté ?", "options": ["Un basculement ou un glissement latéral", "Un allongement de l'empattement", "Un alignement parfait sur la ligne centrale"], "rep": "Un basculement ou un glissement latéral"},
        {"id": "qca9", "q": "Quel facteur lié à l'infrastructure routière aide à maintenir la caravane stable ?", "options": ["Le dévers positif de la chaussée", "L'épaisseur du marquage blanc", "La présence d'une ligne droite de sortie"], "rep": "Le dévers positif de la chaussée"},
        {"id": "qca10", "q": "Pour éviter que la caravane ne percute le trottoir intérieur, le conducteur doit :", "options": ["Ouvrir sa trajectoire vers l'extérieur au point 0", "Serrer immédiatement le bord droit", "Freiner au milieu de la courbe"], "rep": "Ouvrir sa trajectoire vers l'extérieur au point 0"}
    ]

    if "ordre_quiz_cara_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_cara_aleatoire = questions_sources

    if "champs_cara_clean" not in st.session_state:
        st.session_state.champs_cara_clean = [
            ("1. La caravane est reliée à la voiture par un point articulé appelé de ..........", ["Choisir...", "rotule", "sellette"], "rotule", "cara_t1"),
            ("2. Les roues avant de la voiture guident l'ensemble et sont tracées en ..........", ["Choisir...", "rouge", "bleu"], "rouge", "b_t2"),
            ("3. L'essieu arrière de la caravane coupe le virage et est tracé en ..........", ["Choisir...", "bleu", "rouge"], "bleu", "cara_t3"),
            ("4. Plus le timon de la caravane est long, plus la .......... géométrique augmente.", ["Choisir...", "chasse", "dérive"], "chasse", "cara_t4"),
            ("5. Avant le virage, en ligne droite, les trajectoires sont parfaitement ..........", ["Choisir...", "confondues", "décalées"], "confondues", "cara_t5"),
            ("6. À vitesse élevée, des oscillations latérales peuvent provoquer une mise en ..........", ["Choisir...", "lacet", "portefeuille"], "lacet", "cara_t6"),
            ("7. L'angle de .......... incliné de la route réduit les effets de la force centrifuge.", ["Choisir...", "dévers", "braquage"], "dévers", "cara_t7"),
            ("8. L'accélération latérale subie par l'attelage s'évalue en unités ..........", ["Choisir...", "G", "Newton"], "G", "cara_t8"),
            ("9. Les roues avant commencent à virer précisément sur la ligne ..........", ["Choisir...", "verticale", "horizontale"], "verticale", "cara_t9"),
            ("10. Si le gabarit de la caravane morde sur le trottoir, il y a .......... de route.", ["Choisir...", "sortie", "stabilité"], "sortie", "cara_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_cara_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"cara_at2_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_cara_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_cara_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_semi_remorque(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour l'atelier semi-remorque."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique de l'Ensemble Semi-Remorque")

    questions_semi_sources = [
        {"id": "qs1", "q": "Pourquoi le décalage de chasse d'une semi-remorque est-il plus impressionnant que celui d'un porteur ?", "options": ["À cause de la double articulation (tracteur puis sellette)", "Parce que la vitesse est toujours plus élevée", "En raison du nombre de pneumatiques"], "rep": "À cause de la double articulation (tracteur puis sellette)"},
        {"id": "qs2", "q": "Quel composant mécanique sert de point de pivot rotatif entre le tracteur et la semi-remorque ?", "options": ["La sellette d'attelage", "L'axe de fusée", "Le timon rigide"], "rep": "La sellette d'attelage"},
        {"id": "qs3", "q": "En ligne droite avant le virage, comment se comportent les trois trajectoires des essieux ?", "options": ["Elles sont strictement confondues et superposées", "Elles sont déjà écartées parallèlement", "Elles oscillent de gauche à droite"], "rep": "Elles sont strictement confondues et superposées"},
        {"id": "qs4", "q": "Quel essieu subit la trajectoire directrice imposée par la géométrie de la route ?", "options": ["L'essieu avant du tracteur", "L'essieu arrière du tracteur", "L'essieu arrière de la semi"], "rep": "L'essieu avant du tracteur"},
        {"id": "qs5", "q": "Quelle ligne de couleur matérialise le balayage de chasse extrême à l'intérieur du virage ?", "options": ["La ligne rouge (arrière de la semi)", "La ligne bleue (avant du tracteur)", "La ligne verte (arrière du tracteur)"], "rep": "La ligne rouge (arrière de la semi)"},
        {"id": "qs6", "q": "Comment réagit le train arrière de la semi-remorque lors de l'amorce du virage ?", "options": ["Il continue tout droit avec un retard spatial en X", "Il pivote instantanément au même repère que l'avant", "Il s'écarte vers l'extérieur du virage"], "rep": "Il continue tout droit avec un retard spatial en X"},
        {"id": "qs7", "q": "Quel est l'impact d'une grande longueur de semi (L2) sur le couloir de balayage ?", "options": ["Elle augmente massivement le décalage de chasse", "Elle réduit la force centrifuge", "Elle stabilise le véhicule sur la ligne bleue"], "rep": "Elle augmente massivement le décalage de chasse"},
        {"id": "qs8", "q": "Quelle configuration présente le centre de gravité (CG) le plus haut et le plus instable ?", "options": ["La semi-remorque chargée", "Le porteur à vide", "Le tracteur solo"], "rep": "La semi-remorque chargée"},
        {"id": "qs9", "q": "Quel accident dynamique risque de se produire si les pneus du tracteur perdent leur adhérence latérale ?", "options": ["Une mise en portefeuille", "Un cabrage de la cabine", "Une augmentation du rayon de courbure"], "rep": "Une mise en portefeuille"},
        {"id": "qs10", "q": "Pour éviter que les roues de la semi ne montent sur le trottoir intérieur, que doit faire le conducteur ?", "options": ["Ouvrir au maximum son virage vers l'extérieur", "Serrer la corde immédiatement", "Freiner brutalement au point 0"], "rep": "Ouvrir au maximum son virage vers l'extérieur"}
    ]

    if "ordre_quiz_semi_aleatoire" not in st.session_state:
        random.shuffle(questions_semi_sources)
        st.session_state.ordre_quiz_semi_aleatoire = questions_semi_sources

    if "champs_semi_clean" not in st.session_state:
        st.session_state.champs_trajectoire_clean = [
            ("1. La trajectoire d'une semi-remorque est une cascade cinématique à .......... articulations.", ["Choisir...", "deux", "trois"], "deux", "semi_t1"),
            ("2. Avant le point de rupture, l'alignement initial des trois essieux est parfaitement ..........", ["Choisir...", "horizontal", "décalé"], "horizontal", "semi_t2"),
            ("3. L'essieu arrière de la semi-remorque subit une équation différentielle de .......... pure.", ["Choisir...", "poursuite", "braquage"], "poursuite", "semi_t3"),
            ("4. Plus la distance L2 entre la sellette et l'essieu est grande, plus l'arrière plonge à la ..........", ["Choisir...", "corde", "tangente"], "corde", "semi_t4"),
            ("5. La ligne verte représente la trajectoire de l'essieu arrière du ..........", ["Choisir...", "tracteur", "porteur"], "tracteur", "semi_t5"),
            ("6. Le phénomène de glissement latéral d'un ensemble articulé lourd s'appelle la mise en ..........", ["Choisir...", "portefeuille", "renversement"], "portefeuille", "semi_t6"),
            ("7. La hauteur du centre de gravité augmente de façon importante avec le poids du ..........", ["Choisir...", "chargement", "châssis"], "chargement", "semi_t7"),
            ("8. L'accélération transversale subie par l'ensemble s'exprime en unités ..........", ["Choisir...", "G", "Newton"], "G", "semi_t8"),
            ("9. Sur le graphique, la trajectoire des roues avant du tracteur est représentée en ..........", ["Choisir...", "bleu", "rouge"], "bleu", "semi_t9"),
            ("10. Le décalage géométrique cumulé de l'ensemble constitue le balayage de .......... global.", ["Choisir...", "chasse", "dérive"], "chasse", "semi_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_semi_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"semi_at5_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_trajectoire_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_semi_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_trajectoire_gabarit(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour l'atelier trajectoire."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique du Véhicule Porteur")

    questions_trajectoire_sources = [
        {"id": "qt1", "q": "Lors d'un virage, quelle ligne décrit une trajectoire circulaire parfaite ?", "options": ["Les roues avant (ligne rouge)", "Les roues arrière (ligne bleue)", "Le centre de gravité uniquement"], "rep": "Les roues avant (ligne rouge)"},
        {"id": "qt2", "q": "Quel phénomène physique force les roues arrière à couper le virage vers l'intérieur ?", "options": ["Le décalage de chasse géométrique", "La force centrifuge", "Le devers de la route"], "rep": "Le décalage de chasse géométrique"},
        {"id": "qt3", "q": "Où se situe le point de décrochage (amorce de la courbe) pour les roues arrière ?", "options": ["Décalé en X après la ligne de rupture", "Pile sur la ligne verticale 0", "Avant la ligne de rupture"], "rep": "Décalé en X après la ligne de rupture"},
        {"id": "qt4", "q": "Quelle force pousse le porteur vers l'extérieur du virage perpendiculairement à sa trajectoire ?", "options": ["La force centrifuge", "La réaction normale", "Le poids du chargement"], "rep": "La force centrifuge"},
        {"id": "qt5", "q": "Comment appelle-t-on l'inclinaison de la chaussée vers l'intérieur d'un virage ?", "options": ["Le dévers de la route", "L'angle d'Ackermann", "La raideur de dérive"], "rep": "Le dévers de la route"},
        {"id": "qt6", "q": "Quel est l'effet d'un dévers positif sur le risque de basculement du porteur ?", "options": ["Il augmente la stabilité", "Il provoque un glissement immédiat", "Il amplifie la force centrifuge"], "rep": "Il augmente la stabilité"},
        {"id": "qt7", "q": "Si la vitesse du véhicule double dans un même virage, par combien est multipliée la force centrifuge ?", "options": ["Par quatre", "Par deux", "Elle reste identique"], "rep": "Par quatre"},
        {"id": "qt8", "q": "Quelle force de contact parallèle au sol empêche les pneumatiques de déraper ?", "options": ["La force de frottement", "La réaction normale", "Le poids total"], "rep": "La force de frottement"},
        {"id": "qt9", "q": "Quelle est l'unité de mesure de l'accélération transversale subie par le véhicule ?", "options": ["Le G (fraction de la gravité)", "Le Newton (N)", "Le Pascal (Pa)"], "rep": "Le G (fraction de la gravité)"},
        {"id": "qt10", "q": "Si le moment de renversement dépasse le moment stabilisateur, que subit le véhicule ?", "options": ["Un basculement", "Un glissement", "Une trajectoire rectiligne"], "rep": "Un basculement"}
    ]

    if "ordre_quiz_trajectoire_aleatoire" not in st.session_state:
        random.shuffle(questions_trajectoire_sources)
        st.session_state.ordre_quiz_trajectoire_aleatoire = questions_trajectoire_sources

    if "champs_trajectoire_clean" not in st.session_state:
        st.session_state.champs_trajectoire_clean = [
            ("1. Les roues avant décrivent une courbe guidée tandis que les roues arrière subissent une ..........", ["Choisir...", "chasse", "dérive"], "chasse", "traj_t1"),
            ("2. L'essieu arrière reste droit au départ et ne commence à tourner qu'avec un décalage en ..........", ["Choisir...", "X", "Y"], "X", "traj_t2"),
            ("3. En fin de virage, la stabilisation rectiligne de l'essieu arrière s'effectue avec un décalage en ..........", ["Choisir...", "Y", "X"], "Y", "traj_t3"),
            ("4. La force centrifuge est directement proportionnelle au carré de la .......... du véhicule.", ["Choisir...", "vitesse", "masse"], "vitesse", "traj_t4"),
            ("5. La force perpendiculaire à la chaussée inclinée s'appelle la réaction ..........", ["Choisir...", "normale", "tangentielle"], "normale", "traj_t5"),
            ("6. Plus le centre de gravité du chargement est haut, plus le risque de .......... est élevé.", ["Choisir...", "basculement", "glissement"], "basculement", "traj_t6"),
            ("7. L'angle de .......... de la route aide à compenser les effets de la force centrifuge.", ["Choisir...", "dévers", "braquage"], "dévers", "traj_t7"),
            ("8. Si les pneus perdent leur adhérence latérale, le porteur subit un ..........", ["Choisir...", "glissement", "renversement"], "glissement", "traj_t8"),
            ("9. La ligne courbe dessinée en rouge représente la trajectoire des roues ..........", ["Choisir...", "avant", "arrière"], "avant", "traj_t9"),
            ("10. Le franchissement des lignes noires de la chaussée constitue une .......... de route.", ["Choisir...", "sortie", "stabilité"], "sortie", "traj_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_trajectoire_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"traj_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_trajectoire_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_traj_clean", disabled=verrouille, label_visibility="collapsed")


def afficher_atelier_permis_ce_caravane(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour le permis CE + caravane/remorque lourde."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique de l'Attelage Lourd (CE)")

    questions_sources_ce = [
        {"id": "qce1", "q": "Pourquoi un ensemble articulé CE coupe-t-il fortement le virage vers l'intérieur de la courbe ?", "options": ["En raison de la chasse cinématique accrue due aux dimensions de la remorque", "À cause d'un manque de puissance du tracteur", "Parce que le pont arrière est bloqué"], "rep": "En raison de la chasse cinématique accrue due aux dimensions de la remorque"},
        {"id": "qce2", "q": "Quel organe d'accouplement remplace la rotule légère sur un ensemble articulé lourd de type CE ?", "options": ["La sellette d'attelage (ou crochet de remorque lourd)", "La rotule standard", "L'essieu rétractable"], "rep": "La sellette d'attelage (ou crochet de remorque lourd)"},
        {"id": "qce3", "q": "Quel paramètre géométrique amplifie considérablement la surface de balayage de la remorque lourde ?", "options": ["La distance axe pivot - essieu de la remorque", "Le PTRA imprimé sur la carte grise", "Le carénage aérodynamique latéral"], "rep": "La distance axe pivot - essieu de la remorque"},
        {"id": "qce4", "q": "Comment se comportent les trajectoires du camion et de sa remorque en phase d'approche rectiligne ?", "options": ["Les trajectoires des essieux sont parfaitement confondues", "Elles sont décalées d'un mètre sur la droite", "Elles oscillent en permanence"], "rep": "Les trajectoires des essieux sont parfaitement confondues"},
        {"id": "qce5", "q": "Quel risque dynamique majeur guette un ensemble CE à centre de gravité élevé en courbe serrée ?", "options": ["Le basculement ou renversement latéral", "L'allongement de l'empattement du camion", "Le rétrécissement instantané des voies"], "rep": "Le basculement ou renversement latéral"},
        {"id": "qce6", "q": "Sur quel repère précis l'essieu avant du camion commence-t-il sa rotation géométrique ?", "options": ["Pile à l'intersection de la ligne verticale 0", "Trois mètres après la sortie de courbe", "Au milieu de la ligne droite de départ"], "rep": "Pile à l'intersection de la ligne verticale 0"},
        {"id": "qce7", "q": "Dans l'interface graphique du simulateur CE, comment est représentée la trajectoire du train suiveur ?", "options": ["Par une ligne bleue pointillée", "Par une ligne rouge continue", "Par une double bande noire rigide"], "rep": "Par une ligne bleue pointillée"},
        {"id": "qce8", "q": "Quel phénomène de perte d'adhérence pneu/sol peut provoquer une mise en portefeuille de l'ensemble CE ?", "options": ["Le glissement latéral (perte d'adhérence)", "Le devers positif de l'infrastructure", "La stabilisation cinématique"], "rep": "Le glissement latéral (perte d'adhérence)"},
        {"id": "qce9", "q": "Quelle caractéristique géométrique de la route permet de contrer en partie l'effet centrifuge subi par le poids lourd ?", "options": ["L'angle de dévers de la chaussée", "La largeur de la ligne blanche axiale", "L'état de rugosité de la berme"], "rep": "L'angle de dévers de la chaussée"},
        {"id": "qce10", "q": "Pour éviter que l'essieu de la remorque ne monte sur le trottoir intérieur, le conducteur CE doit :", "options": ["Ouvrir largement sa trajectoire vers l'extérieur (gabarit lourd)", "Serrer immédiatement le point de corde", "Donner un coup de frein brusque au point 0"], "rep": "Ouvrir largement sa trajectoire vers l'extérieur (gabarit lourd)"}
    ]

    if "ordre_quiz_ce_cara_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_ce)
        st.session_state.ordre_quiz_ce_cara_aleatoire = questions_sources_ce

    if "champs_ce_cara_clean" not in st.session_state:
        st.session_state.champs_ce_cara_clean = [
            ("1. La remorque lourde CE est connectée au tracteur par un système de ..........", ["Choisir...", "sellette", "rotule"], "sellette", "ce_t1"),
            ("2. Les roues directrices du camion guident l'ensemble et apparaissent en ..........", ["Choisir...", "rouge", "bleu"], "rouge", "ce_t2"),
            ("3. L'essieu arrière de la remorque lourde coupe la trajectoire en ..........", ["Choisir...", "bleu", "rouge"], "bleu", "ce_t3"),
            ("4. Le grand gabarit d'un ensemble articulé augmente l'effet de .......... géométrique.", ["Choisir...", "chasse", "braquage"], "chasse", "ce_t4"),
            ("5. En approche sur la section rectiligne, les lignes de trajectoire sont ..........", ["Choisir...", "confondues", "séparées"], "confondues", "ce_t5"),
            ("6. Une perte d'adhérence du train arrière du tracteur peut mener à une mise en ..........", ["Choisir...", "portefeuille", "ligne"], "portefeuille", "ce_t6"),
            ("7. Le profil incliné de la route, ou .........., aide à stabiliser les masses lourdes.", ["Choisir...", "dévers", "pente"], "dévers", "ce_t7"),
            ("8. L'accélération transversale subie par le véhicule se mesure en unités ..........", ["Choisir...", "G", "Pascal"], "G", "ce_t8"),
            ("9. L'inscription dans la courbe se déclenche précisément au repère ..........", ["Choisir...", "vertical 0", "horizontal 5"], "vertical 0", "ce_t9"),
            ("10. Un empiétement hors des limites de la voie matérialise une .......... de route.", ["Choisir...", "sortie", "conformité"], "sortie", "ce_t10")
        ]

    col_quiz_ce, col_trous_ce = st.columns(2)
    
    with col_quiz_ce:
        st.markdown("##### Quiz Technique CE (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_ce_cara_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"ce_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous_ce:
        st.markdown("##### Synthèse de l'Atelier CE (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ce_cara_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ce_cara_clean", disabled=verrouille, label_visibility="collapsed")



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
    st.header("Simulation Permis B")
    col_imB1, col_imB2, col_imB3 = st.columns(3)

    with col_imB1:    
        try:
            st.image("imBcar1.jpg", caption="véhicule catégorie B.",width=600)
        except Exception:
            st.error("Fichier imBcar1.jpg introuvable.")
    with col_imB2:    
        try:
            st.image("imBcar2.jpg", caption="véhicule catégorie B.",width=600)
        except Exception:
            st.error("Fichier imBcar2.jpg introuvable.")
    with col_imB3:    
        try:
            st.image("imBcar3.jpg", caption="véhicule catégorie B.",width=600)
        except Exception:
            st.error("Fichier imBcar3.jpg introuvable.")

    st.title("Tout savoir sur le Permis B")
    st.write(
        "Le permis B permet de conduire des voitures automobiles, des camionnettes "
        "et des camping-cars dont le poids n'excède pas 3,5 tonnes."
    )

    # --- SECTION 1 : DEFINITION ET REGLES ---
    st.header("1. Qu'est-ce que le permis B ?")

    st.markdown("""
    Le permis de catégorie B autorise la conduite des véhicules qui remplissent ces conditions :
    * **Nombre de places** : Conçu pour le transport de 8 passagers maximum (en plus du conducteur).
    * **PTAC maximal** : Le Poids Total Autorisé en Charge (case F2 de la carte grise) ne doit pas dépasser **3 500 kg**.

    Pour tracter une remorque avec le permis B seul :
    * La remorque est toujours autorisée si son PTAC est inférieur ou égal à **750 kg**.
    * Si la remorque dépasse 750 kg, la somme des PTAC (Voiture + Remorque) ne doit pas dépasser **3 500 kg**.
    """)

    # Tableau récapitulatif de la réglementation pour le permis B
    st.subheader("Tableau des droits de traction avec le Permis B")
    st.markdown("""

    | Type de remorque | Conditions de poids | Statut du Permis B |
    | :--- | :--- | :--- |
    | **Remorque légère** | PTAC inférieur ou égal à 750 kg | Permis B suffisant (quel que soit le poids de l'auto) |
    | **Remorque lourde** | PTAC supérieur à 750 kg et cumul des PTAC jusqu'à 3 500 kg | Permis B suffisant |
    | **Remorque lourde** | PTAC supérieur à 750 kg et cumul des PTAC supérieur à 3 500 kg | Permis B insuffisant (Formation B96 ou Permis BE requis) |
    """)

    # --- SECTION 2 : SIMULATEUR INTERACTIF ---
    st.header("2. Votre attelage est-il compatible avec le Permis B seul ?")
    st.write("Saisissez les poids (F2) de vos cartes grises pour vérifier vos droits :")

    # Formulaire de saisie des données avec valeurs par défaut adaptées au permis B
    col1, col2 = st.columns(2)

    with col1:
        ptac_voiture = st.number_input(
            "PTAC de la Voiture (en kg)", 
            min_value=0, 
            max_value=3500, 
            value=1800, 
            step=50
        )

    with col2:
        ptac_remorque = st.number_input(
            "PTAC de la Remorque (en kg)", 
            min_value=0, 
            max_value=3500, 
            value=700, 
            step=50
        )

    # Calculs logiques
    somme_ptac = ptac_voiture + ptac_remorque

    st.subheader("Résultat de l'analyse")
    st.info(f"Poids total de l'ensemble roulant : {somme_ptac} kg")

    # Logique de décision pour le Permis B strict
    if ptac_voiture > 3500:
        st.error("Le véhicule tracteur dépasse 3 500 kg. Le permis B ne suffit pas (Permis C1 ou C nécessaire).")
    elif ptac_remorque <= 750:
        st.success("Permis B suffisant : La remorque ne dépasse pas 750 kg.")
    else:
        if somme_ptac <= 3500:
            st.success("Permis B suffisant : La remorque dépasse 750 kg mais la somme des PTAC reste inférieure ou égale à 3 500 kg.")
        else:
            st.error(
                f"Permis B insuffisant : La remorque dépasse 750 kg et le total fait {somme_ptac} kg (supérieur à 3 500 kg). "
                "Vous devez passer la formation B96 (jusqu'à 4 250 kg) ou le permis BE (au-delà)."
            )

    # --- SECTION 3 : INFOS OBTENTION ---
    with st.expander("En savoir plus sur les conditions du permis B"):
        st.markdown("""
        * **Âge minimal** : 18 ans pour l'examen pratique (dès 17 ans dans le cadre de l'apprentissage anticipé de la conduite / conduite accompagnée).
        * **Épreuves** :
            * Épreuve théorique générale (le Code de la route).
            * Épreuve pratique de conduite de 32 minutes minimum (comprenant la conduite en circulation, deux manœuvres et des questions de vérification).
        """)


    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        vitesse_kmh = st.slider("Vitesse de la voiture (km/h)", 10, 130, 50, step=5, key="vitesse_b")
        vitesse_ms = vitesse_kmh / 3.6
        empattement = st.slider("Empattement - Distance entre essieux (m)", 2.2, 3.5, 2.7, step=0.1, key="emp_b")

    with col_param2:
        masse_vide = st.slider("Masse a vide du vehicule (kg)", 800, 2500, 1300, step=50, key="mv_b")
        masse_passagers = st.slider("Masse des occupants et bagages (kg)", 0, 500, 150, step=10, key="mc_b")
        masse_totale = (masse_vide + masse_passagers) / 1000.0  # Conversion en tonnes pour les formules
        st.write(f"Masse totale actuelle : {masse_vide + masse_passagers} kg")

    with col_param3:
        rayon_courbure = st.slider("Rayon de la courbe (m)", 30, 150, 60, key="rc_b")
        angle_virage_deg = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_b")
        angle_route_deg = st.slider("Angle de devers de la route (degres)", 0, 15, 2, key="devers_b_central")
        largeur_voie = 3.0

    # Configuration de l'infrastructure
    y_centre_virage = 2 * rayon_courbure
    beta = np.radians(angle_route_deg)
    
    g = 9.81
    seuil_glissement_mu = 0.65  # Adhérence plus élevée pour des pneus tourisme récents
    hauteur_cg = 0.55 + (masse_passagers / (masse_vide + masse_passagers)) * 0.10  # CG bas
    largeur_voiture = 1.8

    r_int = rayon_courbure - (largeur_voie / 2)
    r_ext = rayon_courbure + (largeur_voie / 2)

    # Creation des structures matricielles fixes
    # Creation des structures matricielles fixes pour l'onglet 1
    ds = 0.05  
    distance_totale = rayon_courbure * np.radians(angle_virage_deg) + 30.0
    pas = int(distance_totale / ds)

    x_arr = np.zeros(pas)
    y_arr = np.zeros(pas)
    x_av = np.zeros(pas)
    y_av = np.zeros(pas)
    theta = np.zeros(pas)

    # CORRECTION : Affectation explicite sur l'index 0 pour ne pas casser la matrice NumPy
    x_av[0] = -10.0
    y_av[0] = rayon_courbure
    x_arr[0] = -10.0 - empattement
    y_arr[0] = rayon_courbure
    theta[0] = 0.0

    evenement_detecte = "Aucun"
    index_interruption = pas - 1

    # Calcul dynamique preliminaire de l'acceleration nominale
    vitesse_ms = vitesse_kmh / 3.6
    acceleration_laterale_g = (vitesse_ms**2) / (rayon_courbure * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE RESOLUTION DE TRAJECTOIRE
    # =============================================================================
    cap_cible_rad = np.radians(angle_virage_deg)

    for i in range(1, pas):
        # 1. Trajectoire de reference de l'essieu avant (Ligne rouge lisse)
        if x_av[i-1] < 0.0:
            x_av[i] = x_av[i-1] + ds
            y_av[i] = rayon_courbure
            theta[i] = 0.0
        elif x_av[i-1] >= 0.0 and theta[i-1] < cap_cible_rad:
            cap_av_rad = ds / rayon_courbure
            theta[i] = theta[i-1] + cap_av_rad
            x_av[i] = rayon_courbure * np.sin(theta[i])
            y_av[i] = y_centre_virage - rayon_courbure * np.cos(theta[i])
        else:
            x_av[i] = x_av[i-1] + ds * np.cos(cap_cible_rad)
            y_av[i] = y_av[i-1] + ds * np.sin(cap_cible_rad)
            theta[i] = cap_cible_rad

        # 2. Cinematique de l'essieu arriere tracte (Ligne bleue decalee)
        dx = x_av[i] - x_arr[i-1]
        dy = y_av[i] - y_arr[i-1]
        distance_inter_essieux = np.hypot(dx, dy)
        
        x_arr[i] = x_av[i] - empattement * (dx / distance_inter_essieux)
        y_arr[i] = y_av[i] - empattement * (dy / distance_inter_essieux)

        # 3. Calcul de la dynamique des forces liees au devers pour les alertes
        if x_av[i] >= 0.0 and theta[i] < cap_cible_rad:
            acc_lat_inst_g = (vitesse_ms**2) / (rayon_courbure * g)
            
            P_normale = (masse_totale * 1000) * g * np.cos(beta)
            Fc_normale = (masse_totale * 1000) * (vitesse_ms**2 / rayon_courbure) * np.sin(beta)
            N = P_normale + Fc_normale
            
            P_tangente = (masse_totale * 1000) * g * np.sin(beta)
            Fc_tangente = (masse_totale * 1000) * (vitesse_ms**2 / rayon_courbure) * np.cos(beta)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg
            Moment_stabilisateur = N * (largeur_voiture / 2) + P_tangente * hauteur_cg
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte = "Basculement"
                index_interruption = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte == "Aucun":
                evenement_detecte = "Glissement"
                
        # 4. Verification geometrique du franchissement de voie
        if x_av[i] >= 0.0:
            r_av = np.sqrt(x_av[i]**2 + (y_av[i] - y_centre_virage)**2)
            r_ar = np.sqrt(x_arr[i]**2 + (y_arr[i] - y_centre_virage)**2)
            if (r_av > r_ext or r_av < r_int or r_ar > r_ext or r_ar < r_int) and evenement_detecte == "Aucun":
                evenement_detecte = "Sortie de route"

    # Tronquage des vecteurs au point d'arret reel
    x_arr = x_arr[:index_interruption+1]
    y_arr = y_arr[:index_interruption+1]
    theta = theta[:index_interruption+1]
    x_av = x_av[:index_interruption+1]
    y_av = y_av[:index_interruption+1]

    if len(x_av) > 1 and evenement_detecte != "Basculement":
        rayons_arriere = np.sqrt(x_arr**2 + (y_arr - y_centre_virage)**2)
        rayons_avant = np.sqrt(x_av**2 + (y_av - y_centre_virage)**2)
        decalage_reel = np.max(rayons_avant) - np.min(rayons_arriere)
    else:
        decalage_reel = 0.0

    t_route = np.linspace(0, np.radians(angle_virage_deg), 100)

    # Reconstruction de la chaussee fixe concentrique
    x_droite = np.linspace(-10, 0, 10)
    x_arc_int = r_int * np.sin(t_route)
    y_arc_int = y_centre_virage - r_int * np.cos(t_route)
    x_arc_ext = r_ext * np.sin(t_route)
    y_arc_ext = y_centre_virage - r_ext * np.cos(t_route)
    
    x_fin_int = x_arc_int[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
    y_fin_int = y_arc_int[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
    x_fin_ext = x_arc_ext[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
    y_fin_ext = y_arc_ext[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
    
    x_route_int = np.concatenate([x_droite, x_arc_int, x_fin_int])
    y_route_int = np.concatenate([np.full_like(x_droite, rayon_courbure - largeur_voie/2), y_arc_int, y_fin_int])
    x_route_ext = np.concatenate([x_droite, x_arc_ext, x_fin_ext])
    y_route_ext = np.concatenate([np.full_like(x_droite, rayon_courbure + largeur_voie/2), y_arc_ext, y_fin_ext])

    # =============================================================================
    # RENDU DE L'ECRAN EN DEUX COLONNES STREAMLIT
    # =============================================================================
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas", key="btn_anim_b")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_arr), max(1, len(x_arr) // 40)) if declencher_animation else [len(x_arr) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int, y_route_int, color='black', linewidth=2)
        ax_anim.plot(x_route_ext, y_route_ext, color='black', linewidth=2)
        
        if k > 0:
            ax_anim.plot(x_av[:k], y_av[:k], color='#e74c3c', linewidth=2, label="Trajectoire Roues AV")
            ax_anim.plot(x_arr[:k], y_arr[:k], color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Roues AR")
        
        cos_tk, sin_tk = np.cos(theta[k]), np.sin(theta[k])
        arriere_gauche = [x_arr[k] - 0.7 * cos_tk - (largeur_voiture/2) * (-sin_tk), y_arr[k] - 0.7 * sin_tk - (largeur_voiture/2) * cos_tk]
        arriere_droit  = [x_arr[k] - 0.7 * cos_tk + (largeur_voiture/2) * (-sin_tk), y_arr[k] - 0.7 * sin_tk + (largeur_voiture/2) * cos_tk]
        avant_droit    = [x_arr[k] + (empattement + 0.7) * cos_tk + (largeur_voiture/2) * (-sin_tk), y_arr[k] + (empattement + 0.7) * sin_tk + (largeur_voiture/2) * cos_tk]
        avant_gauche   = [x_arr[k] + (empattement + 0.7) * cos_tk - (largeur_voiture/2) * (-sin_tk), y_arr[k] + (empattement + 0.7) * sin_tk - (largeur_voiture/2) * cos_tk]
        ax_anim.add_patch(Polygon(np.array([arriere_gauche, arriere_droit, avant_droit, avant_gauche]), closed=True, facecolor='#34495e', alpha=0.8))
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Tracé des forces vectorielles adaptées à la voiture
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        ax_f.plot([-2, 2], [-2 * np.sin(beta), 2 * np.sin(beta)], color='black', linewidth=3)
        cam_box = np.array([[-largeur_voiture/2, 0], [largeur_voiture/2, 0], [largeur_voiture/2, hauteur_cg * 1.4], [-largeur_voiture/2, hauteur_cg * 1.4]])
        R_mat = np.array([[np.cos(beta), -np.sin(beta)], [np.sin(beta), np.cos(beta)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#bdc3c7', alpha=0.5))
        
        G_coord = np.dot(np.array([0, hauteur_cg]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        roue_gauche = np.dot(np.array([-largeur_voiture/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_voiture/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=120, marker='s', zorder=4)
        
        f_scale = 1.0 / (masse_totale * 1000 * g)
        val_P = masse_totale * 1000 * g
        val_Fc = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) if evenement_detecte != "Basculement" else 0.0
        
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        val_N_totale = val_P * np.cos(beta) + val_Fc * np.sin(beta)
        val_Ff_totale = val_Fc * np.cos(beta) - val_P * np.sin(beta) if evenement_detecte != "Basculement" else 0.0
        
        ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta), head_width=0.08, head_length=0.12, color='#9b59b6', label='Reaction Normale (N)')
        ax_f.arrow(roue_droite[0], roue_droite[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale) > 0:
            ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f.arrow(roue_droite[0], roue_droite[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta), head_width=0.08, head_length=0.12, color='#3498db')

        ax_f.set_xlim(-1.8, 1.8)
        ax_f.set_ylim(-0.8, 2.5)
        ax_f.axis('off')
        
        handles, labels = ax_f.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_f.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
        zone_schema_forces.pyplot(fig_forces)
        plt.close(fig_forces)

        decalage_inst = np.abs(np.sqrt(x_av[k]**2 + (y_av[k] - y_centre_virage)**2) - np.sqrt(x_arr[k]**2 + (y_arr[k] - y_centre_virage)**2)) if x_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Decalage de chasse instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_deg:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms**2)/(rayon_courbure*g) if x_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- VERDICT ET TRACÉ PLOTLY ZOOMABLE FINAL ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Decalage de chasse maximal", value=f"{decalage_reel:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_deg:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_g:.2f} G")
    if evenement_detecte == "Glissement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                # Affichage de la photo du dérapage de la voiture en grand format
                st.image("derapageVoitureB.jpg", caption="Accident : Perte d'adherence des pneumatiques (Derapage / Sous-virage).",width=800)
            except Exception:
                st.error("Fichier derapageVoitureB.jpg introuvable.")
        zone_alerte.warning("GLISSEMENT : La voiture a glisse vers l'exterieur sous l'effet du sous-virage (Derapage).")
        
    elif evenement_detecte == "Sortie de route":
        zone_alerte.warning("SORTIE DE VOIE : Le vehicule a franchi la ligne continue.")
        
    else:
        zone_alerte.success("TRAJECTOIRE REUSSITE : Le vehicule est reste stable dans sa voie.")
    if evenement_detecte == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementB.jpg", caption="Accident : Perte d'equilibre transversal (Renversement).",width=800)
            except Exception:
                st.error("Fichier basculementB.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : La voiture a bascule sous l'effet de la force centrifuge excessive.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int, y=y_route_int, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext, y=y_route_ext, name="Bord exterieur", line=dict(color='black', width=2)))
            
            fig_plotly.add_trace(go.Scatter(x=x_av, y=y_av, name="Trajectoire Roues AVANT", line=dict(color='#e74c3c', width=3)))
            fig_plotly.add_trace(go.Scatter(x=x_arr, y=y_arr, name="Trajectoire Roues ARRIERE", line=dict(color='#3498db', width=3, dash='dash')))
            
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        if evenement_detecte == "Glissement":
            zone_alerte.warning("GLISSEMENT : La voiture a glisse vers l'exterieur sous l'effet du sous-virage (Derapage).")
        elif evenement_detecte == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : Le vehicule a franchi la ligne continue.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : Le vehicule est reste stable dans sa voie.")
    # -------------------------------------------------------------------------
    # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
    # -------------------------------------------------------------------------
    if "suite_verrouille_tab1_b" not in st.session_state:
        st.session_state.suite_verrouille_tab1_b = False
    verrou_at1_b = st.session_state.suite_verrouille_tab1_b

    # APPEL CRITIQUE : C'est cette ligne qui fait apparaitre le Quiz et le Texte à trous
    afficher_atelier_permis_b(verrouille=verrou_at1_b)

    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_b = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier Vehicule Leger sur la dynamique de glissement.",
        key="check_certif_b_final_net",
        disabled=verrou_at1_b,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_b_official", use_container_width=True, disabled=verrou_at1_b):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_b: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (1 point par bonne reponse)
            score_qb = 0.0
            if "ordre_quiz_b_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_b_aleatoire:
                    saisie = st.session_state.get(f"b_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_qb += 1.0

            # 2. Correction du Texte a trous (1 point par bonne reponse)
            score_tb = 0.0
            if "champs_b_clean" in st.session_state:
                for ligne in st.session_state.champs_b_clean:
                    cle_variable = ligne[3]
                    attendu_texte = ligne[2]
                    saisie_texte = st.session_state.get(f"{cle_variable}_b_clean", "Choisir...")
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_tb += 1.0

            st.session_state.score_suite1_b_p1 = round(float(score_qb), 1)
            st.session_state.score_suite1_b_p2 = round(float(score_tb), 1)
            st.session_state.score_final_suite1_b = round(float(score_qb + score_tb), 1)
            st.session_state.suite_verrouille_tab1_b = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab1_b", False):
        from datetime import datetime
        scr1_b = st.session_state.get("score_suite1_b_p1", 0.0)
        scr2_b = st.session_state.get("score_suite1_b_p2", 0.0)
        tot_s_b = st.session_state.get("score_final_suite1_b", 0.0)
        timestamp_b = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VEHICULE LEGER SCELLE | Note de session : {tot_s_b:.1f} / 20")

        html_export_b = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Permis B - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Physique-Cinematique</h1>
                <p>Atelier 1 : Dynamique et Inscription en Courbe du Vehicule Leger (Permis B)</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_b}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_b:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_b:.1f} / 10</strong><br>
                Note obtenue a la Synthèse de Cours : <strong>{scr2_b:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_b:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_b_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_b_aleatoire, 1):
                saisie = st.session_state.get(f"b_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_b += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_b += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_b_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_b_clean, 1):
                cle_variable = ligne[3]
                phrase_enonce = ligne[0]
                attendu_texte = ligne[2]
                saisie_texte = st.session_state.get(f"{cle_variable}_b_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_b += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_b += f"""
                </tbody>
            </table>
            
            <div class="sub-title">DONNEES COMPLEMENTAIRES D'ATELIER TECHNIQUE</div>
            <p style="font-size: 13px; color: #64748b;">
                Valeur maximale enregistree pour le decalage de chasse : <strong>{decalage_reel:.2f} m</strong><br>
                Acceleration transversale maximale atteinte : <strong>{acceleration_laterale_g:.2f} G</strong>
            </p>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT INDIVIDUEL SCELLE (FORMAT HTML)",
            data=html_export_b,
            file_name=f"Rapport_Permis_B_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            key="btn_download_html_official_b",
            use_container_width=True
        )







with tab2:
    
    st.header("Simulation Permis B et remorque( BE)")
    col_imBE1, col_imBE2, col_imBE3 = st.columns(3)
    with col_imBE1:    
        try:
            st.image("imBE1.jpg", caption="véhicule catégorie BE.",width=600)
        except Exception:
            st.error("Fichier imBE1.jpg introuvable.")
    with col_imBE2:    
        try:
            st.image("imBE2.jpg", caption="véhicule catégorie BE.",width=600)
        except Exception:
            st.error("Fichier imBE2.jpg introuvable.")
    with col_imBE3:    
        try:
            st.image("imBE3.jpg", caption="véhicule catégorie BE.",width=600)
        except Exception:
            st.error("Fichier imBE3.jpg introuvable.")
            
    st.title("Tout savoir sur le Permis BE")
    st.write(
        "Le permis BE (ou permis remorque) est obligatoire pour tracter une remorque lourde "
        "avec un véhicule de catégorie B."
    )

    # --- SECTION 1 : DEFINITION ET REGLES ---
    st.header("1. Qu'est-ce que le permis BE ?")

    st.markdown("""
    Le permis BE est requis dès que vous remplissez simultanément ces deux conditions :
    * **PTAC de la remorque** : Supérieur à 750 kg (et inférieur ou égal à 3 500 kg).
    * **Somme des PTAC** (Voiture + Remorque) : Supérieure à 4 250 kg.

    Note : Le PTAC (Poids Total Autorisé en Charge) se trouve à la case F2 de votre carte grise.
    """)

    # Tableau récapitulatif de la réglementation
    st.subheader("Tableau de synthèse des obligations")
    st.markdown("""

    | Cumul des PTAC (Voiture + Remorque) | Remorque inférieure ou égale à 750 kg | Remorque supérieure à 750 kg |
    | :--- | :--- | :--- |
    | **Jusqu'à 3 500 kg** | Permis B | Permis B |
    | **Entre 3 501 kg et 4 250 kg** | Permis B | Formation B96 (7h sans examen) |
    | **Plus de 4 250 kg** | Permis B | Permis BE obligatoire |
    """)

    # --- SECTION 2 : SIMULATEUR INTERACTIF ---
    st.header("2. Quel permis pour votre attelage ?")
    st.write("Saisissez les poids (F2) de votre carte grise pour vérifier vos obligations :")

    # Formulaire de saisie des données avec nouvelles valeurs par défaut
    col1, col2 = st.columns(2)

    with col1:
        ptac_voiture = st.number_input(
            "PTAC de la Voiture (en kg)", 
            min_value=0, 
            max_value=3500, 
            value=2500, 
            step=50
        )

    with col2:
        ptac_remorque = st.number_input(
            "PTAC de la Remorque (en kg)", 
            min_value=0, 
            max_value=3500, 
            value=2000, 
            step=50
        )

    # Calculs logiques
    somme_ptac = ptac_voiture + ptac_remorque

    st.subheader("Résultat de l'analyse")
    st.info(f"Poids total de l'ensemble roulant : {somme_ptac} kg")

    # Logique de décision selon la réglementation française
    if ptac_remorque <= 750:
        st.success("Permis B suffisant : La remorque fait moins de 750 kg.")
    else:
        if somme_ptac <= 3500:
            st.success("Permis B suffisant : La somme des PTAC ne dépasse pas 3 500 kg.")
        elif 3500 < somme_ptac <= 4250:
            st.warning(
                "Formation B96 requise : La somme des PTAC est entre 3 501 kg et 4 250 kg. "
                "Il s'agit d'une formation de 7 heures en auto-école (sans examen)."
            )
        else:
            st.error(
                "Permis BE Obligatoire : La remorque dépasse 750 kg et la somme des PTAC "
                "est supérieure à 4 250 kg. Vous devez passer l'examen du permis BE."
            )

    # --- SECTION 3 : INFOS EXAMEN ---
    with st.expander("En savoir plus sur l'examen du permis BE"):
        st.markdown("""
        * **Conditions** : Avoir au moins 18 ans et posséder le permis B.
        * **Code de la route** : Nécessaire si votre dernier permis ou code a plus de 5 ans.
        * **Épreuves** :
            * Une épreuve hors circulation (plateau) de 30 min (attelage, vérifications, marche arrière).
            * Une épreuve en circulation de 30 min sur route.
        """)

        
    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        vitesse_kmh_cara = st.slider("Vitesse de l'ensemble (km/h)", 10, 110, 50, step=5, key="vitesse_cara")
        vitesse_ms_cara = vitesse_kmh_cara / 3.6
        empattement_voiture = st.slider("Empattement de la voiture (m)", 2.2, 3.5, 2.7, step=0.1, key="emp_voiture_cara")

    with col_param2:
        longueur_fleche = st.slider("Distance rotule - Essieu caravane (m)", 3.0, 7.0, 4.5, step=0.1, key="long_cara")
        porte_a_faux_ar = st.slider("Porte-a-faux arriere de la voiture (m)", 0.5, 1.5, 0.9, step=0.05, key="paf_voiture_cara")
        
        masse_voiture = st.slider("Masse de la voiture (kg)", 1000, 2500, 1400, step=50, key="m_voit_cara")
        masse_caravane = st.slider("Masse de la caravane (kg)", 400, 1800, 900, step=50, key="m_cara")
        masse_totale_cara = (masse_voiture + masse_caravane) / 1000.0
        st.write(f"Masse totale de l'ensemble : {masse_voiture + masse_caravane} kg")

    with col_param3:
        rayon_courbure_cara = st.slider("Rayon de la courbe (m)", 20, 120, 45, key="rc_cara")
        angle_virage_cara = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_cara")
        angle_route_cara = st.slider("Angle de devers de la route (degres)", 0, 15, 2, key="devers_cara_central")
        largeur_voie = 3.0

    # Configuration de l'infrastructure
    y_centre_virage_cara = 2 * rayon_courbure_cara
    beta_cara = np.radians(angle_route_cara)
    
    g = 9.81
    seuil_glissement_mu = 0.55
    largeur_ensemble = 2.0
    hauteur_cg_cara = 0.85

    r_int_cara = rayon_courbure_cara - (largeur_voie / 2)
    r_ext_cara = rayon_courbure_cara + (largeur_voie / 2)

    # Calcul preliminaire du pas d'espace
    ds_cara = 0.05  
    distance_totale_cara = rayon_courbure_cara * np.radians(angle_virage_cara) + 25.0
    pas_cara = int(distance_totale_cara / ds_cara)

    # Creation des structures de tableaux pour les essieux
    x_v_av = np.zeros(pas_cara)
    y_v_av = np.zeros(pas_cara)
    x_v_ar = np.zeros(pas_cara)
    y_v_ar = np.zeros(pas_cara)
    x_c_ar = np.zeros(pas_cara)
    y_c_ar = np.zeros(pas_cara)
    
    theta_v = np.zeros(pas_cara)
    theta_c = np.zeros(pas_cara)

    # Initialisation stricte a l'index 0 en ligne droite horizontale
    x_v_av[0] = -10.0
    y_v_av[0] = rayon_courbure_cara
    
    x_v_ar[0] = x_v_av[0] - empattement_voiture
    y_v_ar[0] = rayon_courbure_cara
    theta_v[0] = 0.0

    x_rotule_init = x_v_ar[0] - porte_a_faux_ar
    x_c_ar[0] = x_rotule_init - longueur_fleche
    y_c_ar[0] = rayon_courbure_cara
    theta_c[0] = 0.0

    evenement_detecte_cara = "Aucun"
    index_interruption_cara = pas_cara - 1
    acceleration_laterale_cara_g = (vitesse_ms_cara**2) / (rayon_courbure_cara * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE RESOLUTION ATTELLAGE LEGER (TAB 2)
    # =============================================================================
    cap_cible_cara_rad = np.radians(angle_virage_cara)

    for i in range(1, pas_cara):
        # 1. Cinematique de l'essieu avant de la voiture (Roues AV - Rouge lisse)
        if x_v_av[i-1] < 0.0:
            x_v_av[i] = x_v_av[i-1] + ds_cara
            y_v_av[i] = rayon_courbure_cara
            theta_v[i] = 0.0
        elif x_v_av[i-1] >= 0.0 and theta_v[i-1] < cap_cible_cara_rad:
            cap_av_rad = ds_cara / rayon_courbure_cara
            theta_v[i] = theta_v[i-1] + cap_av_rad
            x_v_av[i] = rayon_courbure_cara * np.sin(theta_v[i])
            y_v_av[i] = y_centre_virage_cara - rayon_courbure_cara * np.cos(theta_v[i])
        else:
            x_v_av[i] = x_v_av[i-1] + ds_cara * np.cos(cap_cible_cara_rad)
            y_v_av[i] = y_v_av[i-1] + ds_cara * np.sin(cap_cible_cara_rad)
            theta_v[i] = cap_cible_cara_rad

        # 2. Cinematique de l'essieu arriere de la voiture
        dx_v = x_v_av[i] - x_v_ar[i-1]
        dy_v = y_v_av[i] - y_v_ar[i-1]
        dist_v = np.hypot(dx_v, dy_v)
        x_v_ar[i] = x_v_av[i] - empattement_voiture * (dx_v / dist_v)
        y_v_ar[i] = y_v_av[i] - empattement_voiture * (dy_v / dist_v)

        # Repere spatial de la rotule d'attelage arriere
        x_rot = x_v_ar[i] - porte_a_faux_ar * np.cos(theta_v[i])
        y_rot = y_v_ar[i] - porte_a_faux_ar * np.sin(theta_v[i])

        # 3. Cinematique de l'essieu de la caravane (Ligne bleue decalee)
        dx_c = x_rot - x_c_ar[i-1]
        dy_c = y_rot - y_c_ar[i-1]
        dist_c = np.hypot(dx_c, dy_c)
        theta_c[i] = np.arctan2(dy_c, dx_c)
        x_c_ar[i] = x_rot - longueur_fleche * (dx_c / dist_c)
        y_c_ar[i] = y_rot - longueur_fleche * (dy_c / dist_c)

        # 4. Calcul de la dynamique des forces liees au devers
        if x_v_av[i] >= 0.0 and theta_v[i] < cap_cible_cara_rad:
            val_P_cara = masse_totale_cara * 1000 * g
            val_Fc_cara = masse_totale_cara * 1000 * (vitesse_ms_cara**2 / rayon_courbure_cara)
            
            P_normale = val_P_cara * np.cos(beta_cara)
            Fc_normale = val_Fc_cara * np.sin(beta_cara)
            N = P_normale + Fc_normale
            
            P_tangente = val_P_cara * np.sin(beta_cara)
            Fc_tangente = val_Fc_cara * np.cos(beta_cara)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg_cara
            Moment_stabilisateur = N * (largeur_ensemble / 2) + P_tangente * hauteur_cg_cara
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte_cara = "Basculement"
                index_interruption_cara = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte_cara == "Aucun":
                evenement_detecte_cara = "Glissement"
                
        # 5. Verification geometrique du franchissement de voie
        if x_v_av[i] >= 0.0:
            r_av = np.sqrt(x_v_av[i]**2 + (y_v_av[i] - y_centre_virage_cara)**2)
            r_car = np.sqrt(x_c_ar[i]**2 + (y_c_ar[i] - y_centre_virage_cara)**2)
            if (r_av > r_ext_cara or r_av < r_int_cara or r_car > r_ext_cara or r_car < r_int_cara) and evenement_detecte_cara == "Aucun":
                evenement_detecte_cara = "Sortie de route"

    # Tronquage des vecteurs au point d'arret reel
    x_v_av = x_v_av[:index_interruption_cara+1]
    y_v_av = y_v_av[:index_interruption_cara+1]
    x_v_ar = x_v_ar[:index_interruption_cara+1]
    y_v_ar = y_v_ar[:index_interruption_cara+1]
    x_c_ar = x_c_ar[:index_interruption_cara+1]
    y_c_ar = y_c_ar[:index_interruption_cara+1]
    theta_v = theta_v[:index_interruption_cara+1]

    if len(x_v_av) > 1 and evenement_detecte_cara != "Basculement":
        rayons_cara_ar = np.sqrt(x_c_ar**2 + (y_c_ar - y_centre_virage_cara)**2)
        rayons_avant = np.sqrt(x_v_av**2 + (y_v_av - y_centre_virage_cara)**2)
        decalage_reel_cara = np.max(rayons_avant) - np.min(rayons_cara_ar)
    else:
        decalage_reel_cara = 0.0

    t_route_cara = np.linspace(0, np.radians(angle_virage_cara), 100)

    # Reconstruction de la chaussee fixe concentrique
    x_dr_cara = np.linspace(-10, 0, 10)
    x_arc_int_cara = r_int_cara * np.sin(t_route_cara)
    y_arc_int_cara = y_centre_virage_cara - r_int_cara * np.cos(t_route_cara)
    x_arc_ext_cara = r_ext_cara * np.sin(t_route_cara)
    y_arc_ext_cara = y_centre_virage_cara - r_ext_cara * np.cos(t_route_cara)
    
    x_fin_int_cara = x_arc_int_cara[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_cara))
    y_fin_int_cara = y_arc_int_cara[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_cara))
    x_fin_ext_cara = x_arc_ext_cara[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_cara))
    y_fin_ext_cara = y_arc_ext_cara[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_cara))
    
    x_route_int_cara = np.concatenate([x_dr_cara, x_arc_int_cara, x_fin_int_cara])
    y_route_int_cara = np.concatenate([np.full_like(x_dr_cara, rayon_courbure_cara - largeur_voie/2), y_arc_int_cara, y_fin_int_cara])
    x_route_ext_cara = np.concatenate([x_dr_cara, x_arc_ext_cara, x_fin_ext_cara])
    y_route_ext_cara = np.concatenate([np.full_like(x_dr_cara, rayon_courbure_cara + largeur_voie/2), y_arc_ext_cara, y_fin_ext_cara])

    # =============================================================================
    # RENDU ET COLONNES D'AFFICHAGE (ONGLET 2)
    # =============================================================================
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas", key="btn_anim_cara")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_v_av), max(1, len(x_v_av) // 40)) if declencher_animation else [len(x_v_av) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int_cara, y_route_int_cara, color='black', linewidth=2)
        ax_anim.plot(x_route_ext_cara, y_route_ext_cara, color='black', linewidth=2)
        
        if k > 0:
            # ROUGE pour l'AVANT de la voiture (x_v_av), BLEU pour l'ARRIERE de la caravane (x_c_ar)
            ax_anim.plot(x_v_av[:k], y_v_av[:k], color='#e74c3c', linewidth=2, label="Trajectoire Roues AV Voiture")
            ax_anim.plot(x_c_ar[:k], y_c_ar[:k], color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Essieu Caravane")
        
        ax_anim.scatter(x_v_av[k], y_v_av[k], color='#e74c3c', s=50)
        ax_anim.scatter(x_c_ar[k], y_c_ar[k], color='#3498db', s=50)
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext_cara) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext_cara) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Schema des forces vectorielles de la caravane
        # Schema des forces vectorielles de la caravane corrige
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        ax_f.plot([-2, 2], [-2 * np.sin(beta_cara), 2 * np.sin(beta_cara)], color='black', linewidth=3)
        cam_box = np.array([[-largeur_ensemble/2, 0], [largeur_ensemble/2, 0], [largeur_ensemble/2, hauteur_cg_cara * 1.4], [-largeur_ensemble/2, hauteur_cg_cara * 1.4]])
        R_mat = np.array([[np.cos(beta_cara), -np.sin(beta_cara)], [np.sin(beta_cara), np.cos(beta_cara)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        G_coord = np.dot(np.array([0, hauteur_cg_cara]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        roue_gauche = np.dot(np.array([-largeur_ensemble/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_ensemble/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=120, marker='s', zorder=4)
        
        f_scale = 1.0 / (masse_totale_cara * 1000 * g)
        val_P = masse_totale_cara * 1000 * g
        val_Fc = masse_totale_cara * 1000 * (vitesse_ms_cara**2 / rayon_courbure_cara) if evenement_detecte_cara != "Basculement" else 0.0
        
        # CORRECTION : Extraction des index [0] et [1] pour Matplotlib
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        val_N_totale = val_P * np.cos(beta_cara) + val_Fc * np.sin(beta_cara)
        val_Ff_totale = val_Fc * np.cos(beta_cara) - val_P * np.sin(beta_cara) if evenement_detecte_cara != "Basculement" else 0.0
        
        # CORRECTION : Extraction des index [0] et [1] pour les fleches des roues
        ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_cara), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_cara), head_width=0.08, head_length=0.12, color='#9b59b6', label='Reaction Normale (N)')
        ax_f.arrow(roue_droite[0], roue_droite[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_cara), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_cara), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale) > 0:
            ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_cara), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_cara), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f.arrow(roue_droite[0], roue_droite[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_cara), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_cara), head_width=0.08, head_length=0.12, color='#3498db')
        ax_f.set_xlim(-1.8, 1.8)
        ax_f.set_ylim(-0.8, 2.5)
        ax_f.axis('off')
        
        handles, labels = ax_f.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_f.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
        zone_schema_forces.pyplot(fig_forces)
        plt.close(fig_forces)

        decalage_inst = np.abs(np.sqrt(x_v_av[k]**2 + (y_v_av[k] - y_centre_virage_cara)**2) - np.sqrt(x_c_ar[k]**2 + (y_c_ar[k] - y_centre_virage_cara)**2)) if x_v_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Balayage instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_cara:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms_cara**2)/(rayon_courbure_cara*g) if x_v_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- VERDICT ET TRACÉ PLOTLY ZOOMABLE FINAL ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Balayage global maximal (Chasse)", value=f"{decalage_reel_cara:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_cara:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_cara_g:.2f} G")
    if evenement_detecte_cara == "Glissement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                # Rendu de la photo de mise en lacet / derapage agrandie
                st.image("derapageBcar.jpg", caption="Accident : Perte d'adhérence latérale (Mise en lacet / Louvoiement).", width=800)
            except Exception:
                st.error("Fichier derapageB.jpg introuvable.")
        zone_alerte.warning("GLISSEMENT : L'ensemble a surpasse l'adherence disponible (Mise en lacet / Derapage).")
        
    elif evenement_detecte_cara == "Sortie de route":
        zone_alerte.warning("SORTIE DE VOIE : La caravane a chevauche le marquage au sol.")
        
    else:
        zone_alerte.success("TRAJECTOIRE REUSSITE : L'attelage est reste stable dans sa voie.")
    if evenement_detecte_cara == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementBcar.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).",width=800)
            except Exception:
                st.error("Fichier basculementBcar.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : L'attelage a bascule sous l'effet de la force centrifuge excessive.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int_cara, y=y_route_int_cara, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext_cara, y=y_route_ext_cara, name="Bord exterieur", line=dict(color='black', width=2)))
            
            fig_plotly.add_trace(go.Scatter(x=x_v_av, y=y_v_av, name="Trajectoire Roues AVANT", line=dict(color='#e74c3c', width=3)))
            fig_plotly.add_trace(go.Scatter(x=x_c_ar, y=y_c_ar, name="Trajectoire Roues ARRIERE", line=dict(color='#3498db', width=3, dash='dash')))
            
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        if evenement_detecte_cara == "Glissement":
            zone_alerte.warning("GLISSEMENT : L'ensemble a surpasse l'adherence disponible (Mise en lacet / Derapage).")
        elif evenement_detecte_cara == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : La caravane a chevauché le marquage au sol.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : L'attelage est resté stable dans sa voie.")



            
    if "suite_verrouille_tab2_cara" not in st.session_state:
        st.session_state.suite_verrouille_tab2_cara = False
    verrou_at2_cara = st.session_state.suite_verrouille_tab2_cara

    # CORRECTION : Insertion de l'appel manquant pour afficher le Quiz et le Texte à trous
    afficher_atelier_permis_b_caravane(verrouille=verrou_at2_cara)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_cara = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Ensemble Articulé Léger sur la dynamique de louvoiement.",
        key="check_certif_cara_final_net",
        disabled=verrou_at2_cara,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_cara_official", use_container_width=True, disabled=verrou_at2_cara):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_cara: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (1 point par bonne réponse)
            score_qca = 0.0
            if "ordre_quiz_cara_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_cara_aleatoire:
                    saisie = st.session_state.get(f"cara_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_qca += 1.0

            # 2. Correction du Texte à trous (1 point par bonne réponse)
            score_tca = 0.0
            if "champs_cara_clean" in st.session_state:
                for ligne in st.session_state.champs_cara_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = st.session_state.get(f"{cle_variable}_cara_clean", "Choisir...")
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_tca += 1.0

            st.session_state.score_suite2_cara_p1 = round(float(score_qca), 1)
            st.session_state.score_suite2_cara_p2 = round(float(score_tca), 1)
            st.session_state.score_final_suite2_cara = round(float(score_qca + score_tca), 1)
            st.session_state.suite_verrouille_tab2_cara = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab2_cara", False):
        from datetime import datetime
        scr1_c = st.session_state.get("score_suite2_cara_p1", 0.0)
        scr2_c = st.session_state.get("score_suite2_cara_p2", 0.0)
        tot_s_c = st.session_state.get("score_final_suite2_cara", 0.0)
        timestamp_c = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER ENSEMBLE LÉGER SCELLÉ | Note de session : {tot_s_c:.1f} / 20")

        html_export_cara = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Permis B + Caravane - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique-Cinématique</h1>
                <p>Atelier 2 : Dynamique et Balayage de Couloir de l'Attelage Léger (Permis B + Caravane)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_c}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_c:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_c:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_c:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_c:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_cara_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_cara_aleatoire, 1):
                saisie = st.session_state.get(f"cara_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_cara += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_cara += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_cara_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_cara_clean, 1):
                cle_variable = ligne[-1]
                phrase_enonce = ligne[0]
                attendu_texte = ligne[2]
                saisie_texte = st.session_state.get(f"{cle_variable}_cara_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_cara += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_cara += f"""
                </tbody>
            </table>
            
            <div class="sub-title">DONNÉES COMPLÉMENTAIRES D'ATELIER TECHNIQUE</div>
            <p style="font-size: 13px; color: #64748b;">
                Valeur maximale enregistrée pour le décalage de chasse de la caravane : <strong>{decalage_reel_cara:.2f} m</strong><br>
                Accélération transversale maximale atteinte : <strong>{acceleration_laterale_cara_g:.2f} G</strong>
            </p>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL SCELLÉ (FORMAT HTML)",
            data=html_export_cara,
            file_name=f"Rapport_Caravane_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            key="btn_download_html_official_cara",
            use_container_width=True
        )
        


# =============================================================================
# CONTENU DE L'ONGLET 3 : PERMIS C (PREMIER ATELIER - DYNAMIQUE RIGIDE)
# =============================================================================
with tab3:
    st.header("Simulation de Trajectoire - Camion Rigide Categorie CE")
    st.markdown("""
    Cette section montre l'influence de la vitesse, du poids et de la geometrie sur le phenomene de chasse 
    (le decalage des roues arriere vers l'interieur du virage).
    """)

    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        vitesse_kmh = st.slider("Vitesse du camion (km/h)", 5, 60, 25, step=5, key="vitesse_c")
        vitesse_ms = vitesse_kmh / 3.6
        empattement = st.slider("Empattement - Distance entre essieux (m)", 3.5, 6.5, 4.5, step=0.1, key="emp_c")

    with col_param2:
        masse_vide = st.slider("Masse a vide (t)", 6.0, 15.0, 10.0, step=0.5, key="mv_c")
        masse_charge = st.slider("Masse du chargement (t)", 0.0, 26.0, 14.0, step=0.5, key="mc_c")
        masse_totale = masse_vide + masse_charge
        st.write(f"Masse totale actuelle : {masse_totale:.1f} tonnes")

    with col_param3:
        rayon_courbure = st.slider("Rayon de la route (m)", 15, 60, 25, key="rc_c")
        angle_virage_deg = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_c")
        angle_route_deg = st.slider("Angle de devers de la route (degres)", 0, 15, 4, key="devers_c_central")
        largeur_voie = 3.5

    # Configuration de l'infrastructure
    y_centre_virage = 2 * rayon_courbure
    beta = np.radians(angle_route_deg)
    
    g = 9.81
    seuil_glissement_mu = 0.35
    hauteur_cg = 1.1 + (masse_charge / masse_totale) * 0.9
    largeur_camion = 2.5

    r_int = rayon_courbure - (largeur_voie / 2)
    r_ext = rayon_courbure + (largeur_voie / 2)

    ds = 0.05  
    distance_totale = rayon_courbure * np.radians(angle_virage_deg) + 20.0
    pas = int(distance_totale / ds)

    # Creation de tableaux de zeros pour eviter les erreurs d'indexation
    x_arr = np.zeros(pas)
    y_arr = np.zeros(pas)
    x_av = np.zeros(pas)
    y_av = np.zeros(pas)
    theta = np.zeros(pas)

    # CORRECTION DEFINITIVE : Remplissage de l'index 0 pour conserver la structure NumPy
    x_av[0] = -10.0
    y_av[0] = rayon_courbure
    x_arr[0] = -10.0 - empattement
    y_arr[0] = rayon_courbure
    theta[0] = 0.0

    evenement_detecte = "Aucun"
    index_interruption = pas - 1

    # Calcul des variables physiques
    vitesse_ms = vitesse_kmh / 3.6
    acceleration_laterale_g = (vitesse_ms**2) / (rayon_courbure * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE : ROUGE = AVANT SUR LE TRAIT / BLEU = ARRIERE AVANT
    # =============================================================================
    cap_cible_rad = np.radians(angle_virage_deg)

    for i in range(1, pas):
        # 1. Trajectoire de reference de l'essieu avant (Ligne rouge)
        if x_av[i-1] < 0.0:
            # L'avant (rouge) reste strictement horizontal et droit jusqu'au trait vertical (0)
            x_av[i] = x_av[i-1] + ds
            y_av[i] = rayon_courbure
            theta[i] = 0.0
        elif x_av[i-1] >= 0.0 and theta[i-1] < cap_cible_rad:
            # L'avant (rouge) commence a tourner pile au trait vertical (0)
            cap_av_rad = ds / rayon_courbure
            theta[i] = theta[i-1] + cap_av_rad
            x_av[i] = rayon_courbure * np.sin(theta[i])
            y_av[i] = y_centre_virage - rayon_courbure * np.cos(theta[i])
        else:
            # Sortie en ligne droite verticale stable
            x_av[i] = x_av[i-1] + ds * np.cos(cap_cible_rad)
            y_av[i] = y_av[i-1] + ds * np.sin(cap_cible_rad)
            theta[i] = cap_cible_rad

        # 2. Trajectoire de l'essieu arriere tracte (Ligne bleue)
        # L'arriere (bleu) commence a s'ecarter vers le haut avant le trait vertical (0) 
        # a cause de la traction cinematique de la barre de carrosserie
        dx = x_av[i] - x_arr[i-1]
        dy = y_av[i] - y_arr[i-1]
        distance_inter_essieux = np.hypot(dx, dy)
        
        x_arr[i] = x_av[i] - empattement * (dx / distance_inter_essieux)
        y_arr[i] = y_av[i] - empattement * (dy / distance_inter_essieux)

        # 3. Calcul de la dynamique des forces liees au devers pour les alertes
        if x_av[i] >= 0.0 and theta[i] < cap_cible_rad:
            acc_lat_inst_g = (vitesse_ms**2) / (rayon_courbure * g)
            
            P_normale = masse_totale * 1000 * g * np.cos(beta)
            Fc_normale = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.sin(beta)
            N = P_normale + Fc_normale
            
            P_tangente = masse_totale * 1000 * g * np.sin(beta)
            Fc_tangente = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.cos(beta)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg
            Moment_stabilisateur = N * (largeur_camion / 2) + P_tangente * hauteur_cg
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte = "Basculement"
                index_interruption = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte == "Aucun":
                evenement_detecte = "Glissement"
                
        # 4. Verification du franchissement des voies
        if x_av[i] >= 0.0:
            r_av = np.sqrt(x_av[i]**2 + (y_av[i] - y_centre_virage)**2)
            r_ar = np.sqrt(x_arr[i]**2 + (y_arr[i] - y_centre_virage)**2)
            if (r_av > r_ext or r_av < r_int or r_ar > r_ext or r_ar < r_int) and evenement_detecte == "Aucun":
                evenement_detecte = "Sortie de route"
    # Tronquage des vecteurs au point d'arret reel
    x_arr = x_arr[:index_interruption+1]
    y_arr = y_arr[:index_interruption+1]
    theta = theta[:index_interruption+1]
    x_av = x_av[:index_interruption+1]
    y_av = y_av[:index_interruption+1]

    if len(x_av) > 1 and evenement_detecte != "Basculement":
        rayons_arriere = np.sqrt(x_arr**2 + (y_arr - y_centre_virage)**2)
        rayons_avant = np.sqrt(x_av**2 + (y_av - y_centre_virage)**2)
        decalage_reel = np.max(rayons_avant) - np.min(rayons_arriere)
    else:
        decalage_reel = 0.0

    t_route = np.linspace(0, np.radians(angle_virage_deg), 100)

    # Reconstruction de la chaussee fixe concentrique
    x_droite = np.linspace(-10, 0, 10)
    x_arc_int = r_int * np.sin(t_route)
    y_arc_int = y_centre_virage - r_int * np.cos(t_route)
    x_arc_ext = r_ext * np.sin(t_route)
    y_arc_ext = y_centre_virage - r_ext * np.cos(t_route)
    
    x_fin_int = x_arc_int[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
    y_fin_int = y_arc_int[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
    x_fin_ext = x_arc_ext[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
    y_fin_ext = y_arc_ext[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
    
    x_route_int = np.concatenate([x_droite, x_arc_int, x_fin_int])
    y_route_int = np.concatenate([np.full_like(x_droite, rayon_courbure - largeur_voie/2), y_arc_int, y_fin_int])
    x_route_ext = np.concatenate([x_droite, x_arc_ext, x_fin_ext])
    y_route_ext = np.concatenate([np.full_like(x_droite, rayon_courbure + largeur_voie/2), y_arc_ext, y_fin_ext])

    # =============================================================================
    # RENDU ET COLONNES D'AFFICHAGE AVEC INTEGRATION DU BOUTON D'ANIMATION
    # =============================================================================
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_arr), max(1, len(x_arr) // 40)) if declencher_animation else [len(x_arr) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int, y_route_int, color='black', linewidth=2)
        ax_anim.plot(x_route_ext, y_route_ext, color='black', linewidth=2)
        
        if k > 0:
            # ROUGE pour l'AVANT (x_av), BLEU pour l'ARRIERE (x_arr)
            ax_anim.plot(x_av[:k], y_av[:k], color='#e74c3c', linewidth=2, label="Trajectoire Roues AV")
            ax_anim.plot(x_arr[:k], y_arr[:k], color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Roues AR")
        
        cos_tk, sin_tk = np.cos(theta[k]), np.sin(theta[k])
        arriere_gauche = [x_arr[k] - 1.0 * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk - (largeur_camion/2) * cos_tk]
        arriere_droit  = [x_arr[k] - 1.0 * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk + (largeur_camion/2) * cos_tk]
        avant_droit    = [x_arr[k] + (empattement + 1.0) * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk + (largeur_camion/2) * cos_tk]
        avant_gauche   = [x_arr[k] + (empattement + 1.0) * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk - (largeur_camion/2) * cos_tk]
        ax_anim.add_patch(Polygon(np.array([arriere_gauche, arriere_droit, avant_droit, avant_gauche]), closed=True, facecolor='#2c3e50', alpha=0.8))
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Tracé du schema vectoriel des forces (Vue arriere synchrone)
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        
        # Inclinaison de la ligne d'assiette du sol
        ax_f.plot([-2, 2], [-2 * np.sin(beta), 2 * np.sin(beta)], color='black', linewidth=3)
        
        # Section rectangulaire du camion inclinee de l'angle beta
        cam_box = np.array([[-largeur_camion/2, 0], [largeur_camion/2, 0], [largeur_camion/2, hauteur_cg * 1.4], [-largeur_camion/2, hauteur_cg * 1.4]])
        R_mat = np.array([[np.cos(beta), -np.sin(beta)], [np.sin(beta), np.cos(beta)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        from matplotlib.patches import Polygon
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        # Positionnement de la masse au CG
        G_coord = np.dot(np.array([0, hauteur_cg]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        # Calcul des points d'appui des pneumatiques au sol
        roue_gauche = np.dot(np.array([-largeur_camion/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_camion/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=150, marker='s', zorder=4)
        
        # Echelle de proportion des forces
        f_scale = 1.0 / (masse_totale * 1000 * g)
        val_P = masse_totale * 1000 * g
        val_Fc = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) if evenement_detecte != "Basculement" else 0.0
        
        # CORRECTION EFFECTUÉE : Extraction avec [0] et [1] des composantes des flèches au CG
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        # Repartition des forces Normales et Tangentielles
        val_N_totale = val_P * np.cos(beta) + val_Fc * np.sin(beta)
        val_Ff_totale = val_Fc * np.cos(beta) - val_P * np.sin(beta) if evenement_detecte != "Basculement" else 0.0
        
        # CORRECTION EFFECTUÉE : Extraction avec [0] et [1] pour le tracé sous les roues
        ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta), head_width=0.08, head_length=0.12, color='#9b59b6', label='Reaction Normale (N)')
        ax_f.arrow(roue_droite[0], roue_droite[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale) > 0:
            ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f.arrow(roue_droite[0], roue_droite[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta), head_width=0.08, head_length=0.12, color='#3498db')

        ax_f.set_xlim(-2.2, 2.2)
        ax_f.set_ylim(-1.0, 3.2)
        ax_f.axis('off')
        
        handles, labels = ax_f.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_f.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
        zone_schema_forces.pyplot(fig_forces)
        plt.close(fig_forces)

        decalage_inst = np.abs(np.sqrt(x_av[k]**2 + (y_av[k] - y_centre_virage)**2) - np.sqrt(x_arr[k]**2 + (y_arr[k] - y_centre_virage)**2)) if x_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Decalage de chasse instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_deg:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms**2)/(rayon_courbure*g) if x_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- AFFICHAGE DE FIN DE PARCOURS (INTERACTIF PLOTLY) ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Decalage de chasse maximal", value=f"{decalage_reel:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_deg:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_g:.2f} G")

    if evenement_detecte == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementCE.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).",width=800)
            except Exception:
                st.error("Fichier basculementCE.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : Le camion a bascule sous l'effet de la force centrifuge.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int, y=y_route_int, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext, y=y_route_ext, name="Bord exterieur", line=dict(color='black', width=2)))
            
            # ATTRIBUTION CONFORME VISUELLE : x_av = ROUGE (Avant) / x_arr = BLEU (Arriere)
            fig_plotly.add_trace(go.Scatter(x=x_av, y=y_av, name="Trajectoire Roues AVANT", line=dict(color='#e74c3c', width=3)))
            fig_plotly.add_trace(go.Scatter(x=x_arr, y=y_arr, name="Trajectoire Roues ARRIERE", line=dict(color='#3498db', width=3, dash='dash')))
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        # INDENTATION CORRIGÉE : Alignement par rapport aux blocs précédents
        if evenement_detecte == "Glissement":
            zone_alerte.warning("GLISSEMENT : L'effort lateral demande a surpasse l'adherence disponible (Derapage).")
        elif evenement_detecte == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : Le gabarit a franchi les marquages au sol.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : Le camion est reste stable dans sa voie.")

    if "suite_verrouille_tab3_trajectoire" not in st.session_state:
        st.session_state.suite_verrouille_tab3_trajectoire = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_trajectoire

    # Rendu des questionnaires d'évaluation de l'Atelier 3
    afficher_atelier_trajectoire_gabarit(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Cinématique et Dynamique sur la trajectoire des essieux.",
        key="check_certif_traj3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_traj_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q3 = 0.0
            if "ordre_quiz_trajectoire_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_trajectoire_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"traj_at3_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t3 = 0.0
            if "champs_trajectoire_clean" in st.session_state:
                for ligne in st.session_state.champs_trajectoire_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_traj_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_traj_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_traj_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_traj = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_trajectoire = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab3_trajectoire", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_traj_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_traj_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_traj", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER CINÉMATIQUE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_traj3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Trajectoire Porteur - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique-Cinématique</h1>
                <p>Atelier 3 : Modélisation et Étude des Trajectoires et Gabarits d'Inscription en Courbe du Véhicule Porteur</p>
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

        if "ordre_quiz_trajectoire_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_trajectoire_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"traj_at3_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_traj3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_traj3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_trajectoire_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_trajectoire_clean, 1):
                cle_variable = ligne[-1]
                attendu_texte = ligne[2]
                phrase_enonce = ligne[0]
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_traj_clean"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_traj3 += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_traj3 += f"""
                </tbody>
            </table>
            
            <div class="sub-title">DONNÉES COMPLÉMENTAIRES D'ATELIER TECHNIQUE</div>
            <p style="font-size: 13px; color: #64748b;">
                Valeur maximale enregistrée pour le décalage de chasse : <strong>{st.session_state.get('decalage_reel', 0.0):.2f} m</strong><br>
                Angle de dévers configuré pour la chaussée : <strong>{st.session_state.get('angle_route_deg', 0.0):.1f} degrés</strong>
            </p>
        </body>
        </html>
        """
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL SCELLÉ (FORMAT HTML)",
            data=html_export_traj3,
            file_name=f"Rapport_Trajectoire_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            key="btn_download_html_official_traj3",
            use_container_width=True
        )




                

with tab4:
    st.header("Simulation Permis CE et caravane")
    col_param1, col_param2, col_param3 = st.columns(3)
    
    with col_param1:
        vitesse_kmh_ce_cara = st.slider("Vitesse de l'ensemble (km/h)", 10, 110, 50, step=5, key="vitesse_ce_cara")
        vitesse_ms_ce_cara = vitesse_kmh_ce_cara / 3.6
        empattement_camion = st.slider("Empattement du camion (m)", 2.2, 5.5, 3.8, step=0.1, key="emp_camion_ce_cara")

    with col_param2:
        longueur_fleche_ce = st.slider("Distance rotule - Essieu remorque (m)", 3.0, 9.0, 5.5, step=0.1, key="long_ce_cara")
        porte_a_faux_ar_camion = st.slider("Porte-a-faux arriere du camion (m)", 0.5, 2.0, 1.2, step=0.05, key="paf_camion_ce_cara")
        
        masse_camion = st.slider("Masse du camion (kg)", 3500, 19000, 8000, step=100, key="m_camion_ce_cara")
        masse_remorque_ce = st.slider("Masse de la remorque/caravane (kg)", 750, 10000, 3500, step=100, key="m_remorque_ce_cara")
        masse_totale_ce_cara = (masse_camion + masse_remorque_ce) / 1000.0
        st.write(f"Masse totale de l'ensemble : {masse_camion + masse_remorque_ce} kg")

    with col_param3:
        rayon_courbure_ce_cara = st.slider("Rayon de la courbe (m)", 20, 120, 45, key="rc_ce_cara")
        angle_virage_ce_cara = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_ce_cara")
        angle_route_ce_cara = st.slider("Angle de devers de la route (degres)", 0, 15, 2, key="devers_ce_cara_central")
        largeur_voie_ce = 3.5  # Légèrement élargie pour le gabarit lourd

    # Configuration de l'infrastructure
    y_centre_virage_ce_cara = 2 * rayon_courbure_ce_cara
    beta_ce_cara = np.radians(angle_route_ce_cara)
    
    g = 9.81
    seuil_glissement_mu = 0.55
    largeur_ensemble_ce = 2.5  # Gabarit routier poids lourd standard
    hauteur_cg_ce_cara = 1.40  # Centre de gravité plus élevé pour du matériel CE

    r_int_ce_cara = rayon_courbure_ce_cara - (largeur_voie_ce / 2)
    r_ext_ce_cara = rayon_courbure_ce_cara + (largeur_voie_ce / 2)

    # Calcul préliminaire du pas d'espace
    ds_ce_cara = 0.05  
    distance_totale_ce_cara = rayon_courbure_ce_cara * np.radians(angle_virage_ce_cara) + 25.0
    pas_ce_cara = int(distance_totale_ce_cara / ds_ce_cara)

    # Création des structures de tableaux pour les essieux
    x_v_av = np.zeros(pas_ce_cara)
    y_v_av = np.zeros(pas_ce_cara)
    x_v_ar = np.zeros(pas_ce_cara)
    y_v_ar = np.zeros(pas_ce_cara)
    x_c_ar = np.zeros(pas_ce_cara)
    y_c_ar = np.zeros(pas_ce_cara)
    
    theta_v = np.zeros(pas_ce_cara)
    theta_c = np.zeros(pas_ce_cara)

    # Initialisation stricte a l'index 0 en ligne droite horizontale
    x_v_av[0] = -10.0
    y_v_av[0] = rayon_courbure_ce_cara
    
    x_v_ar[0] = x_v_av[0] - empattement_camion
    y_v_ar[0] = rayon_courbure_ce_cara
    theta_v[0] = 0.0

    x_rotule_init = x_v_ar[0] - porte_a_faux_ar_camion
    x_c_ar[0] = x_rotule_init - longueur_fleche_ce
    y_c_ar[0] = rayon_courbure_ce_cara
    theta_c[0] = 0.0

    evenement_detecte_ce_cara = "Aucun"
    index_interruption_ce_cara = pas_ce_cara - 1
    acceleration_laterale_ce_cara_g = (vitesse_ms_ce_cara**2) / (rayon_courbure_ce_cara * g)

    # =============================================================================
    # BOUCLE DE CALCUL GÉOMÉTRIQUE RÉSOLUTION ATTELAGE LOURD (TAB 4)
    # =============================================================================
    cap_cible_ce_cara_rad = np.radians(angle_virage_ce_cara)

    for i in range(1, pas_ce_cara):
        # 1. Cinématique de l'essieu avant du camion
        if x_v_av[i-1] < 0.0:
            x_v_av[i] = x_v_av[i-1] + ds_ce_cara
            y_v_av[i] = rayon_courbure_ce_cara
            theta_v[i] = 0.0
        elif x_v_av[i-1] >= 0.0 and theta_v[i-1] < cap_cible_ce_cara_rad:
            cap_av_rad = ds_ce_cara / rayon_courbure_ce_cara
            theta_v[i] = theta_v[i-1] + cap_av_rad
            x_v_av[i] = rayon_courbure_ce_cara * np.sin(theta_v[i])
            y_v_av[i] = y_centre_virage_ce_cara - rayon_courbure_ce_cara * np.cos(theta_v[i])
        else:
            x_v_av[i] = x_v_av[i-1] + ds_ce_cara * np.cos(cap_cible_ce_cara_rad)
            y_v_av[i] = y_v_av[i-1] + ds_ce_cara * np.sin(cap_cible_ce_cara_rad)
            theta_v[i] = cap_cible_ce_cara_rad

        # 2. Cinématique de l'essieu arrière du camion
        dx_v = x_v_av[i] - x_v_ar[i-1]
        dy_v = y_v_av[i] - y_v_ar[i-1]
        dist_v = np.hypot(dx_v, dy_v)
        x_v_ar[i] = x_v_av[i] - empattement_camion * (dx_v / dist_v)
        y_v_ar[i] = y_v_av[i] - empattement_camion * (dy_v / dist_v)

        # Repère spatial de la rotule d'attelage arrière
        x_rot = x_v_ar[i] - porte_a_faux_ar_camion * np.cos(theta_v[i])
        y_rot = y_v_ar[i] - porte_a_faux_ar_camion * np.sin(theta_v[i])

        # 3. Cinématique de l'essieu de la remorque/caravane lourde
        dx_c = x_rot - x_c_ar[i-1]
        dy_c = y_rot - y_c_ar[i-1]
        dist_c = np.hypot(dx_c, dy_c)
        theta_c[i] = np.arctan2(dy_c, dx_c)
        x_c_ar[i] = x_rot - longueur_fleche_ce * (dx_c / dist_c)
        y_c_ar[i] = y_rot - longueur_fleche_ce * (dy_c / dist_c)

        # 4. Calcul de la dynamique des forces liées au dévers
        if x_v_av[i] >= 0.0 and theta_v[i] < cap_cible_ce_cara_rad:
            val_P_ce_cara = masse_totale_ce_cara * 1000 * g
            val_Fc_ce_cara = masse_totale_ce_cara * 1000 * (vitesse_ms_ce_cara**2 / rayon_courbure_ce_cara)
            
            P_normale = val_P_ce_cara * np.cos(beta_ce_cara)
            Fc_normale = val_Fc_ce_cara * np.sin(beta_ce_cara)
            N = P_normale + Fc_normale
            
            P_tangente = val_P_ce_cara * np.sin(beta_ce_cara)
            Fc_tangente = val_Fc_ce_cara * np.cos(beta_ce_cara)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg_ce_cara
            Moment_stabilisateur = N * (largeur_ensemble_ce / 2) + P_tangente * hauteur_cg_ce_cara
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte_ce_cara = "Basculement"
                index_interruption_ce_cara = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte_ce_cara == "Aucun":
                evenement_detecte_ce_cara = "Glissement"
                
        # 5. Vérification géométrique du franchissement de voie
        if x_v_av[i] >= 0.0:
            r_av = np.sqrt(x_v_av[i]**2 + (y_v_av[i] - y_centre_virage_ce_cara)**2)
            r_car = np.sqrt(x_c_ar[i]**2 + (y_c_ar[i] - y_centre_virage_ce_cara)**2)
            if (r_av > r_ext_ce_cara or r_av < r_int_ce_cara or r_car > r_ext_ce_cara or r_car < r_int_ce_cara) and evenement_detecte_ce_cara == "Aucun":
                evenement_detecte_ce_cara = "Sortie de route"

    # Affichage du statut après la boucle
    st.info(f"Résultat de la simulation : {evenement_detecte_ce_cara}")

    # Préparation et affichage du bouton d'exportation de données
    nom_fic_ce = preparer_nom_fichier("Permis_CE_Caravane")
    st.download_button(
        label="Exporter les données CE et Caravane",
        data=f"Statut: {evenement_detecte_ce_cara}\nAccélération latérale: {acceleration_laterale_ce_cara_g:.2f} g",
        file_name=nom_fic_ce,
        mime="text/plain",
        key="btn_dl_ce_cara"
    )

    # Tronquage des vecteurs au point d'arret reel (TAB 4 - CE et caravane)
    x_v_av = x_v_av[:index_interruption_ce_cara+1]
    y_v_av = y_v_av[:index_interruption_ce_cara+1]
    x_v_ar = x_v_ar[:index_interruption_ce_cara+1]
    y_v_ar = y_v_ar[:index_interruption_ce_cara+1]
    x_c_ar = x_c_ar[:index_interruption_ce_cara+1]
    y_c_ar = y_c_ar[:index_interruption_ce_cara+1]
    theta_v = theta_v[:index_interruption_ce_cara+1]

    if len(x_v_av) > 1 and evenement_detecte_ce_cara != "Basculement":
        rayons_ce_cara_ar = np.sqrt(x_c_ar**2 + (y_c_ar - y_centre_virage_ce_cara)**2)
        rayons_avant_ce = np.sqrt(x_v_av**2 + (y_v_av - y_centre_virage_ce_cara)**2)
        decalage_reel_ce_cara = np.max(rayons_avant_ce) - np.min(rayons_ce_cara_ar)
    else:
        decalage_reel_ce_cara = 0.0

    t_route_ce_cara = np.linspace(0, np.radians(angle_virage_ce_cara), 100)

    # Reconstruction de la chaussee fixe concentrique (Adaptée au gabarit CE)
    x_dr_ce_cara = np.linspace(-10, 0, 10)
    x_arc_int_ce_cara = r_int_ce_cara * np.sin(t_route_ce_cara)
    y_arc_int_ce_cara = y_centre_virage_ce_cara - r_int_ce_cara * np.cos(t_route_ce_cara)
    x_arc_ext_ce_cara = r_ext_ce_cara * np.sin(t_route_ce_cara)
    y_arc_ext_ce_cara = y_centre_virage_ce_cara - r_ext_ce_cara * np.cos(t_route_ce_cara)
    
    x_fin_int_ce_cara = x_arc_int_ce_cara[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_ce_cara))
    y_fin_int_ce_cara = y_arc_int_ce_cara[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_ce_cara))
    x_fin_ext_ce_cara = x_arc_ext_ce_cara[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_ce_cara))
    y_fin_ext_ce_cara = y_arc_ext_ce_cara[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_ce_cara))
    
    x_route_int_ce_cara = np.concatenate([x_dr_ce_cara, x_arc_int_ce_cara, x_fin_int_ce_cara])
    y_route_int_ce_cara = np.concatenate([np.full_like(x_dr_ce_cara, rayon_courbure_ce_cara - largeur_voie_ce/2), y_arc_int_ce_cara, y_fin_int_ce_cara])
    x_route_ext_ce_cara = np.concatenate([x_dr_ce_cara, x_arc_ext_ce_cara, x_fin_ext_ce_cara])
    y_route_ext_ce_cara = np.concatenate([np.full_like(x_dr_ce_cara, rayon_courbure_ce_cara + largeur_voie_ce/2), y_arc_ext_ce_cara, y_fin_ext_ce_cara])

    # =============================================================================
    # RENDU ET COLONNES D'AFFICHAGE (ONGLET 4 - CE et caravane)
    # =============================================================================
    col_graphe_ce, col_analyse_ce = st.columns(2)

    with col_analyse_ce:
        st.subheader("Indicateurs Physiques Synchrones (CE)")
        zone_metrique_chasse_ce = st.empty()
        zone_metrique_devers_ce = st.empty()
        zone_metrique_g_ce = st.empty()
        zone_alerte_ce = st.empty()
        
        declencher_animation_ce = st.button("Lancer la simulation pas-a-pas", key="btn_anim_ce_cara")
        
        st.subheader("Schéma Vectoriel du Bilan des Forces (Vue arrière CE)")
        zone_schema_forces_ce = st.empty()

    with col_graphe_ce:
        conteneur_graphique_ce = st.empty()

    points_animation_ce = range(0, len(x_v_av), max(1, len(x_v_av) // 40)) if declencher_animation_ce else [len(x_v_av) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation_ce:
        fig_anim_ce, ax_anim_ce = plt.subplots(figsize=(7, 5))
        ax_anim_ce.plot(x_route_int_ce_cara, y_route_int_ce_cara, color='black', linewidth=2)
        ax_anim_ce.plot(x_route_ext_ce_cara, y_route_ext_ce_cara, color='black', linewidth=2)
        
        if k > 0:
            # ROUGE pour l'AVANT du camion (x_v_av), BLEU pour l'ARRIERE de la remorque/caravane (x_c_ar)
            ax_anim_ce.plot(x_v_av[:k], y_v_av[:k], color='#e74c3c', linewidth=2, label="Trajectoire Roues AV Camion")
            ax_anim_ce.plot(x_c_ar[:k], y_c_ar[:k], color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Essieu Remorque")
        
        ax_anim_ce.scatter(x_v_av[k], y_v_av[k], color='#e74c3c', s=50)
        ax_anim_ce.scatter(x_c_ar[k], y_c_ar[k], color='#3498db', s=50)
        ax_anim_ce.axis("equal")
        ax_anim_ce.set_xlim(-12, max(x_route_ext_ce_cara) + 5)
        ax_anim_ce.set_ylim(-5, max(y_route_ext_ce_cara) + 5)
        
        if declencher_animation_ce:
            conteneur_graphique_ce.pyplot(fig_anim_ce)
        plt.close(fig_anim_ce)

        # Schéma des forces vectorielles de la caravane lourde
        fig_forces_ce, ax_f_ce = plt.subplots(figsize=(5, 3.5))
        ax_f_ce.plot([-2, 2], [-2 * np.sin(beta_ce_cara), 2 * np.sin(beta_ce_cara)], color='black', linewidth=3)
        cam_box_ce = np.array([[-largeur_ensemble_ce/2, 0], [largeur_ensemble_ce/2, 0], [largeur_ensemble_ce/2, hauteur_cg_ce_cara * 1.4], [-largeur_ensemble_ce/2, hauteur_cg_ce_cara * 1.4]])
        R_mat_ce = np.array([[np.cos(beta_ce_cara), -np.sin(beta_ce_cara)], [np.sin(beta_ce_cara), np.cos(beta_ce_cara)]])
        cam_box_rot_ce = np.dot(cam_box_ce, R_mat_ce.T)
        ax_f_ce.add_patch(Polygon(cam_box_rot_ce, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        G_coord_ce = np.dot(np.array([0, hauteur_cg_ce_cara]), R_mat_ce.T)
        ax_f_ce.scatter(G_coord_ce[0], G_coord_ce[1], color='black', s=90, zorder=5)
        
        roue_gauche_ce = np.dot(np.array([-largeur_ensemble_ce/2, 0]), R_mat_ce.T)
        roue_droite_ce = np.dot(np.array([largeur_ensemble_ce/2, 0]), R_mat_ce.T)
        ax_f_ce.scatter([roue_gauche_ce[0], roue_droite_ce[0]], [roue_gauche_ce[1], roue_droite_ce[1]], color='black', s=120, marker='s', zorder=4)
        
        f_scale_ce = 1.0 / (masse_totale_ce_cara * 1000 * g)
        val_P_ce = masse_totale_ce_cara * 1000 * g
        val_Fc_ce = masse_totale_ce_cara * 1000 * (vitesse_ms_ce_cara**2 / rayon_courbure_ce_cara) if evenement_detecte_ce_cara != "Basculement" else 0.0
        
        # Flèches vectorielles Poids et Force Centrifuge
        ax_f_ce.arrow(G_coord_ce[0], G_coord_ce[1], 0, -val_P_ce * f_scale_ce * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f_ce.arrow(G_coord_ce[0], G_coord_ce[1], val_Fc_ce * f_scale_ce * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        val_N_totale_ce = val_P_ce * np.cos(beta_ce_cara) + val_Fc_ce * np.sin(beta_ce_cara)
        val_Ff_totale_ce = val_Fc_ce * np.cos(beta_ce_cara) - val_P_ce * np.sin(beta_ce_cara) if evenement_detecte_ce_cara != "Basculement" else 0.0
        
        # Flèches de réaction normale pour les roues
        ax_f_ce.arrow(roue_gauche_ce[0], roue_gauche_ce[1], -(val_N_totale_ce/2) * f_scale_ce * 1.3 * np.sin(beta_ce_cara), (val_N_totale_ce/2) * f_scale_ce * 1.3 * np.cos(beta_ce_cara), head_width=0.08, head_length=0.12, color='#9b59b6', label='Réaction Normale (N)')
        ax_f_ce.arrow(roue_droite_ce[0], roue_droite_ce[1], -(val_N_totale_ce/2) * f_scale_ce * 1.3 * np.sin(beta_ce_cara), (val_N_totale_ce/2) * f_scale_ce * 1.3 * np.cos(beta_ce_cara), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale_ce) > 0:
            ax_f_ce.arrow(roue_gauche_ce[0], roue_gauche_ce[1], -(val_Ff_totale_ce/2) * f_scale_ce * 1.3 * np.cos(beta_ce_cara), -(val_Ff_totale_ce/2) * f_scale_ce * 1.3 * np.sin(beta_ce_cara), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f_ce.arrow(roue_droite_ce[0], roue_droite_ce[1], -(val_Ff_totale_ce/2) * f_scale_ce * 1.3 * np.cos(beta_ce_cara), -(val_Ff_totale_ce/2) * f_scale_ce * 1.3 * np.sin(beta_ce_cara), head_width=0.08, head_length=0.12, color='#3498db')
        ax_f_ce.set_xlim(-1.8, 1.8)
        ax_f_ce.set_ylim(-0.8, 2.5)
        ax_f_ce.axis('off')
        
        handles_ce, labels_ce = ax_f_ce.get_legend_handles_labels()
        by_label_ce = dict(zip(labels_ce, handles_ce))
        ax_f_ce.legend(by_label_ce.values(), by_label_ce.keys(), loc="upper right", fontsize='small')
        zone_schema_forces_ce.pyplot(fig_forces_ce)
        plt.close(fig_forces_ce)

        decalage_inst_ce = np.abs(np.sqrt(x_v_av[k]**2 + (y_v_av[k] - y_centre_virage_ce_cara)**2) - np.sqrt(x_c_ar[k]**2 + (y_c_ar[k] - y_centre_virage_ce_cara)**2)) if x_v_av[k] >= 0.0 else 0.0
        zone_metrique_chasse_ce.metric(label="Balayage instantané", value=f"{decalage_inst_ce:.2f} m")
        zone_metrique_devers_ce.metric(label="Angle de dévers de la route", value=f"{angle_route_ce_cara:.1f} degrés")
        zone_metrique_g_ce.metric(label="Accélération transversale", value=f"{(vitesse_ms_ce_cara**2)/(rayon_courbure_ce_cara*g) if x_v_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation_ce:
            time.sleep(0.04)

    # Si l'animation n'est pas lancée, on affiche quand même le graphique final dans son conteneur fixe
    if not declencher_animation_ce:
        fig_final_ce, ax_final_ce = plt.subplots(figsize=(7, 5))
        ax_final_ce.plot(x_route_int_ce_cara, y_route_int_ce_cara, color='black', linewidth=2)
        ax_final_ce.plot(x_route_ext_ce_cara, y_route_ext_ce_cara, color='black', linewidth=2)
        ax_final_ce.plot(x_v_av, y_v_av, color='#e74c3c', linewidth=2, label="Trajectoire Roues AV Camion")
        ax_final_ce.plot(x_c_ar, y_c_ar, color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Essieu Remorque")
        ax_final_ce.scatter(x_v_av[-1], y_v_av[-1], color='#e74c3c', s=50)
        ax_final_ce.scatter(x_c_ar[-1], y_c_ar[-1], color='#3498db', s=50)
        ax_final_ce.axis("equal")
        ax_final_ce.legend(loc="lower left")
        conteneur_graphique_ce.pyplot(fig_final_ce)
        plt.close(fig_final_ce)



    # --- VERDICT ET TRACÉ PLOTLY ZOOMABLE FINAL (TAB 4 - CE et caravane) ---
    animation_terminee_ce = True
    zone_metrique_chasse_ce.metric(label="Balayage global maximal (Chasse)", value=f"{decalage_reel_ce_cara:.2f} m")
    zone_metrique_devers_ce.metric(label="Dévers configuré de la chaussée", value=f"{angle_route_ce_cara:.1f} degrés")
    zone_metrique_g_ce.metric(label="Accélération transversale maximale", value=f"{acceleration_laterale_ce_cara_g:.2f} G")
    
    if evenement_detecte_ce_cara == "Glissement":
        with col_graphe_ce:
            conteneur_graphique_ce.empty()
            try:
                # Rendu de la photo de mise en lacet / dérapage poids lourd agrandie
                st.image("derapageCEcar.jpg", caption="Accident : Perte d'adhérence latérale PL (Mise en lacet / Louvoiement).", width=800)
            except Exception:
                st.error("Fichier derapageCEcar.jpg introuvable.")
        zone_alerte_ce.warning("GLISSEMENT : L'ensemble lourd a surpassé l'adhérence disponible (Mise en lacet / Dérapage).")
        
    elif evenement_detecte_ce_cara == "Sortie de route":
        zone_alerte_ce.warning("SORTIE DE VOIE : La remorque/caravane a chevauché le marquage au sol.")
        
    else:
        zone_alerte_ce.success("TRAJECTOIRE RÉUSSITE : L'attelage lourd est resté stable dans sa voie.")
        
    if evenement_detecte_ce_cara == "Basculement":
        with col_graphe_ce:
            conteneur_graphique_ce.empty()
            try:
                st.image("basculementCEcar.jpg", caption="Accident : Rupture d'équilibre statique PL (Renversement).", width=800)
            except Exception:
                st.error("Fichier basculementCEcar.jpg introuvable.")
        zone_alerte_ce.error("ACCIDENT DÉTECTÉ : L'ensemble CE a basculé sous l'effet de la force centrifuge excessive.")
    else:
        with col_graphe_ce:
            conteneur_graphique_ce.empty()
            
            import plotly.graph_objects as go
            fig_plotly_ce = go.Figure()
            fig_plotly_ce.add_trace(go.Scatter(x=x_route_int_ce_cara, y=y_route_int_ce_cara, name="Bord intérieur", line=dict(color='black', width=2)))
            fig_plotly_ce.add_trace(go.Scatter(x=x_route_ext_ce_cara, y=y_route_ext_ce_cara, name="Bord extérieur", line=dict(color='black', width=2)))
            
            fig_plotly_ce.add_trace(go.Scatter(x=x_v_av, y=y_v_av, name="Trajectoire Roues AVANT", line=dict(color='#e74c3c', width=3)))
            fig_plotly_ce.add_trace(go.Scatter(x=x_c_ar, y=y_c_ar, name="Trajectoire Roues ARRIÈRE", line=dict(color='#3498db', width=3, dash='dash')))
            
            fig_plotly_ce.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive CE (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly_ce, use_container_width=True)

        if evenement_detecte_ce_cara == "Glissement":
            zone_alerte_ce.warning("GLISSEMENT : L'ensemble lourd a surpassé l'adhérence disponible (Mise en lacet / Dérapage).")
        elif evenement_detecte_ce_cara == "Sortie de route":
            zone_alerte_ce.warning("SORTIE DE VOIE : La remorque/caravane a chevauché le marquage au sol.")
        else:
            zone_alerte_ce.success("TRAJECTOIRE RÉUSSITE : L'attelage lourd est resté stable dans sa voie.")

    if "suite_verrouille_tab4_ce_cara" not in st.session_state:
        st.session_state.suite_verrouille_tab4_ce_cara = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_ce_cara

    # Rendu des questionnaires d'évaluation de l'Atelier 4
    afficher_atelier_permis_ce_caravane(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 4")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier sur la trajectoire de l'ensemble CE et caravane.",
        key="check_certif_ce_cara4_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_ce_cara_official", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatisee du Quiz CE
            score_q4 = 0.0
            if "ordre_quiz_ce_cara_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_ce_cara_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"ce_at4_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # 2. Correction automatisee du Texte a trous CE
            score_t4 = 0.0
            if "champs_ce_cara_clean" in st.session_state:
                for ligne in st.session_state.champs_ce_cara_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_ce_cara_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t4 += 1.0

            st.session_state.score_suite4_ce_cara_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_ce_cara_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_ce_cara = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_ce_cara = True
            st.rerun()

    # -------------------------------------------------------------------------
    # EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLE CE
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab4_ce_cara", False):
        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_ce_cara_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_ce_cara_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_ce_cara", 0.0)
        timestamp_ce4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ENSEMBLE CE ET CARAVANE SCELLE | Note de session : {tot_s_t4:.1f} / 20")

        html_export_semi5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Ensemble CE et Caravane - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Physique-Cinematique</h1>
                <p>Atelier 4 : Inscription en Courbe et Stabilite des Ensembles Routiers CE</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ce4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue a la Synthese de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_ce_cara_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_ce_cara_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"ce_at4_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_semi5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_semi5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_ce_cara_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ce_cara_clean, 1):
                cle_variable = ligne[-1]
                attendu_texte = ligne
                phrase_enonce = ligne
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_ce_cara_clean"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_semi5 += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_semi5 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html_ce = preparer_nom_fichier("Rapport_Atelier4_CE_Caravane").replace(".txt", ".html")

        st.download_button(
            label="TELECHARGER LE RAPPORT SCELLE (HTML)",
            data=html_export_semi5,
            file_name=nom_fichier_html_ce,
            mime="text/html",
            key="btn_download_html_official_ce_cara",
            use_container_width=True
        )




with tab5:
    st.header("Simulation Permis C )")
    st.info("Espace reserve pour le second module applique au Permis C.")

    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        vitesse_kmh_semi = st.slider("Vitesse de l'ensemble (km/h)", 5, 50, 20, step=5, key="vitesse_semi")
        vitesse_ms_semi = vitesse_kmh_semi / 3.6
        empattement_tracteur = st.slider("Empattement du tracteur - L1 (m)", 3.0, 5.0, 3.8, step=0.1, key="emp_trac_semi")

    with col_p2:
        # Configuration detailee de la repartition des masses lourdes
        masse_tracteur = st.slider("Masse a vide du tracteur (t)", 5.0, 10.0, 7.5, step=0.5, key="m_trac_semi")
        masse_semi_vide = st.slider("Masse a vide de la semi-remorque (t)", 4.0, 12.0, 6.0, step=0.5, key="m_semi_vide")
        masse_charge_semi = st.slider("Masse du chargement (t)", 0.0, 30.0, 20.0, step=0.5, key="m_charge_semi")
        
        # Calcul de la masse totale de l'ensemble routier articule
        masse_totale_semi = masse_tracteur + masse_semi_vide + masse_charge_semi
        st.write(f"Masse totale de l'ensemble : {masse_totale_semi:.1f} tonnes")
        
        distance_sellette = st.slider("Avance de la sellette / essieu AR (m)", 0.0, 1.0, 0.3, step=0.05, key="sellette_semi")
        longueur_semi = st.slider("Distance sellette - Essieux semi - L2 (m)", 6.0, 10.0, 7.5, step=0.1, key="long_semi")

    with col_p3:
        rayon_courbure_semi = st.slider("Rayon de la route (m)", 15, 60, 25, key="rc_semi")
        angle_virage_semi = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_semi")
        angle_route_semi = st.slider("Angle de devers de la route (degres)", 0, 15, 4, key="devers_semi_central")
        largeur_voie = 3.5

    # Configuration de l'infrastructure
    y_centre_virage_semi = 2 * rayon_courbure_semi
    beta_semi = np.radians(angle_route_semi)
    
    g = 9.81
    seuil_glissement_mu = 0.35
    largeur_camion = 2.5
    
    # Centre de gravite adaptatif dependant du poids du chargement integre
    hauteur_cg_semi = 1.1 + (masse_charge_semi / (masse_tracteur + masse_semi_vide)) * 1.2

    r_int_semi = rayon_courbure_semi - (largeur_voie / 2)
    r_ext_semi = rayon_courbure_semi + (largeur_voie / 2)

    # Calcul preliminaire du pas d'espace
    ds_semi = 0.05  
    distance_totale_semi = rayon_courbure_semi * np.radians(angle_virage_semi) + 25.0
    pas_semi = int(distance_totale_semi / ds_semi)

    # Creation des structures de tableaux fixes (3 essieux distincts)
    x_trac_av = np.zeros(pas_semi)
    y_trac_av = np.zeros(pas_semi)
    x_trac_ar = np.zeros(pas_semi)
    y_trac_ar = np.zeros(pas_semi)
    x_semi_ar = np.zeros(pas_semi)
    y_semi_ar = np.zeros(pas_semi)
    
    theta_trac = np.zeros(pas_semi)
    theta_semi = np.zeros(pas_semi)

    # CORRECTION STRICTE : Affectation par index [0] pour préserver le format matriciel NumPy
    x_trac_av[0] = -10.0
    y_trac_av[0] = rayon_courbure_semi
    
    x_trac_ar[0] = x_trac_av[0] - empattement_tracteur
    y_trac_ar[0] = rayon_courbure_semi
    theta_trac[0] = 0.0

    # Position initiale de la sellette d'attelage
    x_sellette_init = x_trac_ar[0] + distance_sellette
    x_semi_ar[0] = x_sellette_init - longueur_semi
    y_semi_ar[0] = rayon_courbure_semi
    theta_semi[0] = 0.0

    evenement_detecte_semi = "Aucun"
    index_interruption_semi = pas_semi - 1

    # Calcul de l'acceleration transversale nominale
    acceleration_laterale_semi_g = (vitesse_ms_semi**2) / (rayon_courbure_semi * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE RESOLUTION SEMI-REMORQUE COMPLÈTE
    # =============================================================================
    cap_cible_semi_rad = np.radians(angle_virage_semi)

    for i in range(1, pas_semi):
        # 1. Trajectoire de reference de l'essieu avant du tracteur (Roues AV - Rouge)
        if x_trac_av[i-1] < 0.0:
            x_trac_av[i] = x_trac_av[i-1] + ds_semi
            y_trac_av[i] = rayon_courbure_semi
            theta_trac[i] = 0.0
        elif x_trac_av[i-1] >= 0.0 and theta_trac[i-1] < cap_cible_semi_rad:
            cap_av_rad = ds_semi / rayon_courbure_semi
            theta_trac[i] = theta_trac[i-1] + cap_av_rad
            x_trac_av[i] = rayon_courbure_semi * np.sin(theta_trac[i])
            y_trac_av[i] = y_centre_virage_semi - rayon_courbure_semi * np.cos(theta_trac[i])
        else:
            x_trac_av[i] = x_trac_av[i-1] + ds_semi * np.cos(cap_cible_semi_rad)
            y_trac_av[i] = y_trac_av[i-1] + ds_semi * np.sin(cap_cible_semi_rad)
            theta_trac[i] = cap_cible_semi_rad

        # 2. Cinematique de l'essieu arriere du tracteur (Roues AR Tracteur - Bleu)
        dx_trac = x_trac_av[i] - x_trac_ar[i-1]
        dy_trac = y_trac_av[i] - y_trac_ar[i-1]
        dist_trac = np.hypot(dx_trac, dy_trac)
        x_trac_ar[i] = x_trac_av[i] - empattement_tracteur * (dx_trac / dist_trac)
        y_trac_ar[i] = y_trac_av[i] - empattement_tracteur * (dy_trac / dist_trac)

        # Coordonnees instantanees de la sellette d'attelage pivotante
        x_sel = x_trac_ar[i] + distance_sellette * np.cos(theta_trac[i])
        y_sel = y_trac_ar[i] + distance_sellette * np.sin(theta_trac[i])

        # 3. Cinematique du groupe d'essieux de la semi-remorque (Roues AR Semi - Vert)
        dx_semi = x_sel - x_semi_ar[i-1]
        dy_semi = y_sel - y_semi_ar[i-1]
        dist_semi = np.hypot(dx_semi, dy_semi)
        theta_semi[i] = np.arctan2(dy_semi, dx_semi)
        x_semi_ar[i] = x_sel - longueur_semi * (dx_semi / dist_semi)
        y_semi_ar[i] = y_sel - longueur_semi * (dy_semi / dist_semi)

        # 4. Calcul de la dynamique des forces et verifications de securite
        if x_trac_av[i] >= 0.0 and theta_trac[i] < cap_cible_semi_rad:
            val_P_semi = masse_totale_semi * 1000 * g
            val_Fc_semi = masse_totale_semi * 1000 * (vitesse_ms_semi**2 / rayon_courbure_semi)
            
            P_normale = val_P_semi * np.cos(beta_semi)
            Fc_normale = val_Fc_semi * np.sin(beta_semi)
            N = P_normale + Fc_normale
            
            P_tangente = val_P_semi * np.sin(beta_semi)
            Fc_tangente = val_Fc_semi * np.cos(beta_semi)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg_semi
            Moment_stabilisateur = N * (largeur_camion / 2) + P_tangente * hauteur_cg_semi
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte_semi = "Basculement"
                index_interruption_semi = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte_semi == "Aucun":
                evenement_detecte_semi = "Glissement"
                
        # 5. Verification du gabarit routier pour les 3 trains d'essieux
        if x_trac_av[i] >= 0.0:
            r_av = np.sqrt(x_trac_av[i]**2 + (y_trac_av[i] - y_centre_virage_semi)**2)
            r_ar = np.sqrt(x_trac_ar[i]**2 + (y_trac_ar[i] - y_centre_virage_semi)**2)
            r_sm = np.sqrt(x_semi_ar[i]**2 + (y_semi_ar[i] - y_centre_virage_semi)**2)
            if (r_av > r_ext_semi or r_av < r_int_semi or r_ar > r_ext_semi or r_ar < r_int_semi or r_sm > r_ext_semi or r_sm < r_int_semi) and evenement_detecte_semi == "Aucun":
                evenement_detecte_semi = "Sortie de route"

    # Tronquage des vecteurs au point d'arret reel
    x_trac_av = x_trac_av[:index_interruption_semi+1]
    y_trac_av = y_trac_av[:index_interruption_semi+1]
    x_trac_ar = x_trac_ar[:index_interruption_semi+1]
    y_trac_ar = y_trac_ar[:index_interruption_semi+1]
    x_semi_ar = x_semi_ar[:index_interruption_semi+1]
    y_semi_ar = y_semi_ar[:index_interruption_semi+1]
    theta_trac = theta_trac[:index_interruption_semi+1]

    # Calcul du balayage de chasse maximal cumule (Tracteur + Remorque)
    if len(x_trac_av) > 1 and evenement_detecte_semi != "Basculement":
        rayons_semi = np.sqrt(x_semi_ar**2 + (y_semi_ar - y_centre_virage_semi)**2)
        rayons_avant = np.sqrt(x_trac_av**2 + (y_trac_av - y_centre_virage_semi)**2)
        decalage_reel_semi = np.max(rayons_avant) - np.min(rayons_semi)
    else:
        decalage_reel_semi = 0.0
    t_route_semi = np.linspace(0, np.radians(angle_virage_semi), 100)

    # Generation des traces de routes fixes concentriques
    x_dr_semi = np.linspace(-10, 0, 10)
    x_arc_int_semi = r_int_semi * np.sin(t_route_semi)
    y_arc_int_semi = y_centre_virage_semi - r_int_semi * np.cos(t_route_semi)
    x_arc_ext_semi = r_ext_semi * np.sin(t_route_semi)
    y_arc_ext_semi = y_centre_virage_semi - r_ext_semi * np.cos(t_route_semi)
    
    x_fin_int_semi = x_arc_int_semi[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_semi))
    y_fin_int_semi = y_arc_int_semi[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_semi))
    x_fin_ext_semi = x_arc_ext_semi[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_semi))
    y_fin_ext_semi = y_arc_ext_semi[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_semi))
    
    x_route_int_semi = np.concatenate([x_dr_semi, x_arc_int_semi, x_fin_int_semi])
    y_route_int_semi = np.concatenate([np.full_like(x_dr_semi, rayon_courbure_semi - largeur_voie/2), y_arc_int_semi, y_fin_int_semi])
    x_route_ext_semi = np.concatenate([x_dr_semi, x_arc_ext_semi, x_fin_ext_semi])
    y_route_ext_semi = np.concatenate([np.full_like(x_dr_semi, rayon_courbure_semi + largeur_voie/2), y_arc_ext_semi, y_fin_ext_semi])

    # Configuration des colonnes d'affichage
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas", key="btn_anim_semi_final")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_trac_av), max(1, len(x_trac_av) // 40)) if declencher_animation else [len(x_trac_av) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        # Trace Matplotlib de l'ensemble articule mobile
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int_semi, y_route_int_semi, color='black', linewidth=2)
        ax_anim.plot(x_route_ext_semi, y_route_ext_semi, color='black', linewidth=2)
        
        if k > 0:
            # Ligne bleue pour l'AVANT (tracteur), Ligne rouge pour l'ARRIÈRE (semi)
            ax_anim.plot(x_trac_av[:k], y_trac_av[:k], color='#3498db', linewidth=2, label="Trajectoire Roues AV")
            ax_anim.plot(x_semi_ar[:k], y_semi_ar[:k], color='#e74c3c', linewidth=2, linestyle='--', label="Trajectoire Roues AR")
        
        # Dessinement simplifie des deux boites (Tracteur + Remorque)
        cos_tk, sin_tk = np.cos(theta_trac[k]), np.sin(theta_trac[k])
        ax_anim.scatter(x_trac_av[k], y_trac_av[k], color='#3498db', s=60)
        ax_anim.scatter(x_trac_ar[k], y_trac_ar[k], color='black', s=60)
        ax_anim.scatter(x_semi_ar[k], y_semi_ar[k], color='#e74c3c', s=60)
        
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext_semi) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext_semi) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Tracé du schema des forces synchrone
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        ax_f.plot([-2, 2], [-2 * np.sin(beta_semi), 2 * np.sin(beta_semi)], color='black', linewidth=3)
        cam_box = np.array([[-largeur_camion/2, 0], [largeur_camion/2, 0], [largeur_camion/2, hauteur_cg_semi * 1.4], [-largeur_camion/2, hauteur_cg_semi * 1.4]])
        R_mat = np.array([[np.cos(beta_semi), -np.sin(beta_semi)], [np.sin(beta_semi), np.cos(beta_semi)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        G_coord = np.dot(np.array([0, hauteur_cg_semi]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        roue_gauche = np.dot(np.array([-largeur_camion/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_camion/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=150, marker='s', zorder=4)
        
        f_scale = 1.0 / (masse_totale_semi * 1000 * g)
        val_P = masse_totale_semi * 1000 * g
        val_Fc = masse_totale_semi * 1000 * (vitesse_ms_semi**2 / rayon_courbure_semi) if evenement_detecte_semi != "Basculement" else 0.0
        
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        val_N_totale = val_P * np.cos(beta_semi) + val_Fc * np.sin(beta_semi)
        val_Ff_totale = val_Fc * np.cos(beta_semi) - val_P * np.sin(beta_semi) if evenement_detecte_semi != "Basculement" else 0.0
        
        ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_semi), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_semi), head_width=0.08, head_length=0.12, color='#9b59b6', label='Reaction Normale (N)')
        ax_f.arrow(roue_droite[0], roue_droite[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_semi), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_semi), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale) > 0:
            ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_semi), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_semi), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f.arrow(roue_droite[0], roue_droite[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_semi), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_semi), head_width=0.08, head_length=0.12, color='#3498db')

        ax_f.set_xlim(-2.2, 2.2)
        ax_f.set_ylim(-1.0, 3.2)
        ax_f.axis('off')
        
        handles, labels = ax_f.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_f.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
        zone_schema_forces.pyplot(fig_forces)
        plt.close(fig_forces)

        # Compteurs textuels intermédiaires
        decalage_inst = np.abs(np.sqrt(x_trac_av[k]**2 + (y_trac_av[k] - y_centre_virage_semi)**2) - np.sqrt(x_semi_ar[k]**2 + (y_semi_ar[k] - y_centre_virage_semi)**2)) if x_trac_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Balayage global instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_semi:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms_semi**2)/(rayon_courbure_semi*g) if x_trac_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- RENDU PLOTLY INTERACTIF ZOOMABLE EN FIN DE SIMULATION ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Balayage global maximal (Chasse)", value=f"{decalage_reel_semi:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_semi:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_semi_g:.2f} G")
    if evenement_detecte_semi == "Glissement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                # Affichage de la photo de l'accident en grand format
                st.image("portefeuilleSPL.jpg", caption="Accident : Glissement lateral des essieux (Mise en portefeuille).",width=800)
            except Exception:
                st.error("Fichier portefeuilleSPL.jpg introuvable.")
        zone_alerte.warning("GLISSEMENT : L'ensemble routier a surpasse l'adherence disponible (Mise en portefeuille).")
        
    elif evenement_detecte_semi == "Sortie de route":
        zone_alerte.warning("SORTIE DE VOIE : La semi-remorque a chevauche le marquage au sol interieur.")
        
    else:
        zone_alerte.success("TRAJECTOIRE REUSSITE : L'ensemble articule est reste stable dans sa voie.")
    if evenement_detecte_semi == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementC.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).",width=800)
            except Exception:
                st.error("basculementC.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : Le vehicule articule a basculé sous l'effet de la force centrifuge.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int_semi, y=y_route_int_semi, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext_semi, y=y_route_ext_semi, name="Bord exterieur", line=dict(color='black', width=2)))
            
            # 1. Roues AVANT Tracteur (Bleu lisse)
            fig_plotly.add_trace(go.Scatter(x=x_trac_av, y=y_trac_av, name="Trajectoire Roues AVANT Tracteur", line=dict(color='#3498db', width=3)))
            
            # 2. L'ESSIEU MANQUANT : Roues ARRIÈRE Tracteur / Sellette (Vert pointillé)
            fig_plotly.add_trace(go.Scatter(x=x_trac_ar, y=y_trac_ar, name="Trajectoire Essieu AR TRACTEUR", line=dict(color='#2ecc71', width=2.5, dash='dash')))
            
            # 3. Roues ARRIÈRE Semi-remorque (Rouge pointillé extrême)
            fig_plotly.add_trace(go.Scatter(x=x_semi_ar, y=y_semi_ar, name="Trajectoire Roues ARRIERE SEMI", line=dict(color='#e74c3c', width=3, dash='dash')))
            
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        if evenement_detecte_semi == "Glissement":
            zone_alerte.warning("GLISSEMENT : L'ensemble routier a surpasse l'adherence disponible (Mise en portefeuille).")
        elif evenement_detecte_semi == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : La semi-remorque a chevauche le marquage au sol interieur.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : L'ensemble articule est reste stable dans sa voie.")

    # -------------------------------------------------------------------------
    # PARTIE 3 : LOGIQUE DE VALIDATION ET MOTEUR DE CORRECTION SCELLÉ
    # -------------------------------------------------------------------------
    if "suite_verrouille_tab5_semi" not in st.session_state:
        st.session_state.suite_verrouille_tab5_semi = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_semi

    # Rendu des questionnaires d'évaluation de l'Atelier 5
    afficher_atelier_semi_remorque(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la trajectoire de l'ensemble semi-remorque.",
        key="check_certif_semi5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_semi_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q5 = 0.0
            if "ordre_quiz_semi_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_semi_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"semi_at5_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q5 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t5 = 0.0
            if "champs_trajectoire_clean" in st.session_state:
                for ligne in st.session_state.champs_trajectoire_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_semi_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t5 += 1.0

            st.session_state.score_suite5_semi_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_semi_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_semi = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_semi = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab5_semi", False):
        from datetime import datetime
        scr1_t5 = st.session_state.get("score_suite5_semi_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_semi_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_semi", 0.0)
        timestamp_semi5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER ENSEMBLE ARTICULÉ SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_semi5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Ensemble Articulé - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique-Cinématique</h1>
                <p>Atelier 5 : Inscription en Courbe et Stabilité des Ensembles Articulés Lourds</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_semi5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_semi_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_semi_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"semi_at5_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_semi5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_semi5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_trajectoire_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_trajectoire_clean, 1):
                cle_variable = ligne[-1]
                attendu_texte = ligne[2]
                phrase_enonce = ligne[0]
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_semi_clean"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_semi5 += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_semi5 += f"""
                </tbody>
            </table>
            
            <div class="sub-title">DONNÉES COMPLÉMENTAIRES D'ATELIER TECHNIQUE</div>
            <p style="font-size: 13px; color: #64748b;">
                Valeur maximale enregistrée pour le balayage de chasse cumulé : <strong>{decalage_reel_semi:.2f} m</strong><br>
                Angle de dévers configuré pour la chaussée : <strong>{angle_route_semi:.1f} degrés</strong>
            </p>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL SCELLÉ (FORMAT HTML)",
            data=html_export_semi5,
            file_name=f"Rapport_Semi_Remorque_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            key="btn_download_html_official_semi5",
            use_container_width=True
        )





