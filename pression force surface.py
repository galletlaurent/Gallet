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
        # Remplacement du lien générique par le portrait officiel de Blaise Pascal
        try:
            st.image("Pascal.jpg", caption="Blaise Pascal", use_container_width=True)
        except Exception:
            # Remplacement par un avertissement d'absence de média plus propre pour l'élève
            st.warning("Illustration en cours de chargement ou fichier 'Pascal.jpg' absent du serveur.")

        st.markdown("""
        * **Sa Trouvaille :** La formulation de la pression comme le rapport d'une force sur une surface (**P = F / S**). Il démontre qu'une même force répartie sur une surface plus petite engendre une pression bien plus élevée.
        * **L'Expérience Célèbre :** *Le crève-tonneau de Pascal (1646)*. En appliquant le poids d'un faible volume d'eau (Force) au sommet d'un long tube de très fine section (Surface minuscule), il génère une pression hydrostatique immense capable de faire éclater le bois.
        """)
        try:
            st.image("crevetonneau.jpg", caption="tonneau", use_container_width=True)
        except Exception:
            # Remplacement par un avertissement d'absence de média plus propre pour l'élève
            st.warning("Illustration en cours de chargement ou fichier 'crevetonneau.jpg' absent du serveur.")

        
    with col_torricelli:
        st.markdown("### Evangelista Torricelli (1608 - 1647)")
        # Remplacement du lien générique par le portrait officiel de Evangelista Torricelli
        try:
            st.image("Torricelli.jpg", caption="Evangelista Torricelli", use_container_width=True)
        except Exception:
            # Remplacement par un avertissement d'absence de média plus propre pour l'élève
            st.warning("Illustration en cours de chargement ou fichier 'Torricelli.jpg' absent du serveur.")
       
        st.markdown("""
        * **Sa Trouvaille :** La mesure de la force pressante de l'air. Il est le premier à quantifier la force colossale exercée par le poids de l'atmosphère sur chaque unité de surface terrestre.
        * **L'Expérience Célèbre :** *Le tube de Torricelli (1643)*. Il équilibre la force du poids de l'atmosphère s'exerçant sur la surface d'un bassin avec le poids d'une colonne de mercure de 76 centimètres de hauteur.
        """)
        try:
            st.image("pressionatmos.jpg", caption="Baromètre", use_container_width=True)
        except Exception:
            # Remplacement par un avertissement d'absence de média plus propre pour l'élève
            st.warning("Illustration en cours de chargement ou fichier 'pressionatmos.jpg' absent du serveur.")

    st.markdown("---")
    # -------------------------------------------------------------------------
    # PARTIE 2 : BANDE DESSINÉE EN DEUX COLONNES (TEXTES À GAUCHE, IMAGE À DROITE)
    # -------------------------------------------------------------------------
    st.subheader("Bande Dessinée : Le Choc des Fluides")
    st.write("Une histoire imaginaire pour comprendre leurs discussions scientifiques.")

    # Style visuel pour les bulles de dialogue de la bande dessinée
    st.markdown("""
    <style>
    .bulles { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px; }
    .narrateur { font-style: italic; color: #555555; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

    # Correction de la syntaxe : Ajout du chiffre 2 pour spécifier deux colonnes égales
    col_bd_texte, col_bd_image = st.columns(2)

    # Colonne de gauche : Empilement de toutes les cases de texte
    with col_bd_texte:
        st.markdown("**Case 1 : À la taverne de la Science (Paris, 1648)**")
        st.markdown('<div class="narrateur">Pascal et Torricelli s\'installent à une table. Torricelli pose un lourd tube de mercure sur le comptoir, l\'air fatigué.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Torricelli :</b> "Mon cher Blaise, j\'ai mal au dos... L\'air pèse des tonnes aujourd\'hui ! Les gens croient que la nature a horreur du vide, mais c\'est faux, c\'est juste l\'atmosphère qui applique sa force sur chaque unité de surface terrestre !"</div>', unsafe_allow_html=True)

        st.markdown("**Case 2 : L\'illumination de Pascal**")
        st.markdown('<div class="narrateur">Pascal regarde son verre, prend une paille, et tape du poing sur la table.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Pascal :</b> "Tu as raison Evangelista ! Et regarde ça : la pression dépend directement du rapport P = F / S. Si j\'appuie sur mon verre ici, la pression pushes le liquide partout en même temps ! C\'est comme cela que j\'ai brisé mon tonneau !"</div>', unsafe_allow_html=True)

        st.markdown("**Case 3 : La panique au laboratoire**")
        st.markdown('<div class="narrateur">Le serveur de la taverne recule, inquiet des théories des deux physiciens et des formules mathématiques.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Le Serveur :</b> "Messieurs, calmez-vous avec vos calculs de force et de surface. Vous voulez régler l\'addition ou vous allez aussi faire éclater ma cave avec votre relation P = F / S ?"<br><br><b>Pascal et Torricelli (en chœur) :</b> "C\'est pour la science !"</div>', unsafe_allow_html=True)

    # Colonne de droite : Affichage de la grande image hébergée en ligne
    with col_bd_image:
        st.image("https://unsplash.com", use_container_width=True, caption="Anomalie hydrostatique sur la Cuve 4")

    st.markdown("---")
    
    
    if "suite_verrouille_tab1_pression" not in st.session_state:
        st.session_state.suite_verrouille_tab1_pression = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_pression

    # Affichage du module de questions spécifique à l'histoire de la formule P=F/S
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
            # Correction automatisée du Quiz (10 questions)
            score_q1 = 0.0
            if "ordre_quiz_pression_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_pression_aleatoire:
                    saisie = st.session_state.get(f"pres_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q1 += 1.0

            # Correction automatisée du Texte à trous (10 trous)
            score_t1 = 0.0
            if "champs_pression_clean" in st.session_state:
                for ligne in st.session_state.champs_pression_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_pres_clean", "Choisir...") == attendu: 
                        score_t1 += 1.0

            # Sauvegarde des scores et verrouillage de la session
            st.session_state.score_suite1_pres_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_pres_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_pres = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_pression = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_pression", False):
        scr1_t1 = st.session_state.get("score_suite1_pres_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_pres_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_pres", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_pres1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Relation P=F/S - {n_eleve}</title>
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
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique</h1>
                <p>Atelier 1 : Contexte historique de la relation fondamentale de la pression P = F / S</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t1:.1f} / 10</strong><br>
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
                saisie = st.session_state.get(f"pres_at1_final_g_{q_item['id']}", "Choisir...")
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
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pres_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pres1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_pres1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pres1 = preparer_nom_fichier("Rapport_Histoire_Pression").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel",
            data=html_export_pres1,
            file_name=nom_fichier_html_pres1,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_pres_final"
        )

        
with tab2:
    st.header("Étude des Forces Physiques et Pressantes")
    st.write("Explorez les fondements mécaniques des actions réciproques, manipulez les vecteurs, puis complétez l'évaluation de l'Atelier 2.")

    # Styles CSS pour les légendes, bandeaux et textes spécifiques
    st.markdown("""
    <style>
    .legende-forces { color: #2563eb; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-forces { background-color: #e0f2fe; border-left: 5px solid #0284c7; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #1e3a8a; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # DÉFINITION INTERNE DE L'ATELIER INTERACTIF (QUIZ, FORCES ET TROUS)
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

        if "ordre_quiz_forces_aleatoire" not in st.session_state:
            random.shuffle(questions_forces_sources)
            st.session_state.ordre_quiz_forces_aleatoire = questions_forces_sources

        if "champs_forces_clean" not in st.session_state:
            st.session_state.champs_forces_clean = [
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

        # SÉPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES (Mise en page style 4 pages par feuille)
        col_gauche_globale, col_droite_globale = st.columns(2)

        # ---------------------------------------------------------------------
        # COLONNE GAUCHE (PAGES 1 ET 3 : CONTEXTE, SIMULATEUR ET QUIZ)
        # ---------------------------------------------------------------------
        with col_gauche_globale:
            # PAGE 1 : CONTEXTE HISTORIQUE DES FORCES
            st.subheader("La Galerie des Génies : La Notion de Force")
            st.markdown("""
            <div class="bandeau-forces">
                <b>Repères Historiques :</b> Si Galilée formalise le principe d'inertie, c'est Isaac Newton qui formalise en 1687 les lois de la dynamique. Il définit la force comme une action capable de modifier le mouvement d'un corps ou de le déformer.
            </div>
            """, unsafe_allow_html=True)

            sub_col_hist1, sub_col_hist2 = st.columns(2)
            with sub_col_hist1:
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-forces">Galilée (1564 - 1642)</div>', unsafe_allow_html=True)
            with sub_col_hist2:
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-forces">Isaac Newton (1643 - 1727)</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("**Simulateur Interactif de Vecteurs Force**")
            valeur_force = st.slider("Ajuster l'intensité de la Force Motrice (en Newtons) :", min_value=0, max_value=200, value=100, step=10, disabled=verrouille, key="slider_force_motrice")
            if valeur_force == 100:
                st.info("État du système : Les forces opposées se compensent (100 N). Le système est en équilibre mécanique.")
            elif valeur_force > 100:
                st.warning(f"État du système : Rupture d'équilibre. La force motrice ({valeur_force} N) surpasse la résistance.")
            else:
                st.error(f"État du système : Force motrice insuffisante ({valeur_force} N). La charge reste immobile.")

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 3 : QUIZ TECHNIQUE DES FORCES
            st.markdown("##### Quiz Technique (10 questions - 10 pts)")
            for idx, q_data in enumerate(st.session_state.ordre_quiz_forces_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"forc_at2_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")




    if "suite_verrouille_tab2_forces" not in st.session_state:
        st.session_state.suite_verrouille_tab2_forces = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_forces

    # Appel de la fonction d'affichage
    afficher_atelier_forces(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier d'Étude des Forces.",
        key="check_certif_forc2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_forc_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatique du Quiz
            score_q2 = 0.0
            if "ordre_quiz_forces_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_forces_aleatoire:
                    saisie = st.session_state.get(f"forc_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q2 += 1.0

            # Correction automatique du Texte à trous
            score_t2 = 0.0
            if "champs_forces_clean" in st.session_state:
                for ligne in st.session_state.champs_forces_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_forc_clean", "Choisir...") == attendu: 
                        score_t2 += 1.0

            st.session_state.score_suite2_forc_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_forc_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_forc = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_forces = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML DE L'ATELIER 2 ---
    if st.session_state.get("suite_verrouille_tab2_forces", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_forc_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_forc_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_forc", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER FORCES SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_forc2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport d'Étude des Forces - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0384c7; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 2 : Caractérisation des forces mécaniques et modélisation des forces pressantes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
        </body>
        </html>
        """
        if "ordre_quiz_forces_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_forces_aleatoire, 1):
                saisie = st.session_state.get(f"forc_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_forc2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_forc2 += """
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
            for num, ligne in enumerate(st.session_state.champs_forces_clean, 1):
                # Correction des index de tuple pour correspondre a la structure reelle
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_forc_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_forc2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_forc2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_forc2 = preparer_nom_fichier("Rapport_Etude_Forces").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2",
            data=html_export_forc2,
            file_name=nom_fichier_html_forc2,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_forc_final"
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

    # DÉFINITION INTERNE DE L'ATELIER INTERACTIF (QUIZ, PRESSION ET TROUS)
    def afficher_atelier_pression(verrouille=False):
        import random

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
                ("3. En hydraulique, le manomètre indique souvent une pression relative par rapport à l'..........", ["Choisir...", "atmosphère", "vide"], "atmosphere", "pres3_t3"),
                ("4. La pression hydrostatique au sein d'un liquide au repos croît avec la ..........", ["Choisir...", "profondeur", "surface"], "profondeur", "pres3_t4"),
                ("5. Un fluide transmettant fidèlement les pressions subies est qualifié d'..........", ["Choisir...", "incompressible", "gazeux"], "incompressible", "pres3_t5"),
                ("6. L'unité légale du système international pour quantifier la pression est le ..........", ["Choisir...", "Pascal", "Bar"], "Pascal", "pres3_t6"),
                ("7. Un bar correspond à une valeur de pression équivalente à cent mille ..........", ["Choisir...", "Pascals", "Newtons"], "Pascals", "pres3_t7"),
                ("8. À force constante, si la section d'appui est divisée par deux, la pression ..........", ["Choisir...", "double", "diminue"], "double", "pres3_t8"),
                ("9. La force pressante générée agit de façon normale, c'est-à-dire .......... aux parois.", ["Choisir...", "perpendiculaire", "tangentielle"], "perpendiculaire", "pres3_t9"),
                ("10. L'absence totale de molécules de gaz ou de matière définit l'état de ..........", ["Choisir...", "vide", "surpression"], "vide", "pres3_t10")
            ]

        # SEPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES (Mise en page style 4 pages par feuille)
        col_gauche_globale, col_droite_globale = st.columns(2)

        # ---------------------------------------------------------------------
        # COLONNE GAUCHE (PAGES 1 ET 3 : CONTEXTE, SIMULATEUR ET QUIZ)
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
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-pression">Blaise Pascal (1623 - 1662)</div>', unsafe_allow_html=True)
            with sub_col_hist2:
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-pression">Expérimentation barométrique</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # SIMULATEUR INTERACTIF DE PRESSION HYDROSTATIQUE
            st.markdown("**Simulateur de Pression Hydrostatique (P = rho * g * h)**")
            hauteur_fluide = st.slider("Ajuster la profondeur de mesure dans la cuve (en mètres) :", min_value=0.0, max_value=10.0, value=5.0, step=0.5, disabled=verrouille, key="slider_profondeur_cuve")
            
            # Calcul théorique simplifié de la pression hydrostatique (pression = rho * g * h avec rho=1000 et g=9.81)
            pression_calculee_bar = (1000 * 9.81 * hauteur_fluide) / 100000
            st.info(f"Mesure au manomètre : À une profondeur de {hauteur_fluide} m, la pression relative exercée par l'eau est de {pression_calculee_bar:.3f} bar.")

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 3 : QUIZ TECHNIQUE DE LA PRESSION
            st.markdown("##### Quiz Technique (10 questions - 10 pts)")
            for idx, q_data in enumerate(st.session_state.ordre_quiz_pres3_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"pres3_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

        # ---------------------------------------------------------------------
        # COLONNE DROITE (PAGES 2 ET 4 : CARICATURE, MODÉLISATION ET TROUS)
        # ---------------------------------------------------------------------
        with col_droite_globale:
            # PAGE 2 : BANDE CARICATURALE TECHNIQUE
            st.subheader("Bande Caricaturale : Le Principe des Vases Communiquants")
            
            sub_col_text, sub_col_img = st.columns([0.45, 0.55])
            with sub_col_text:
                st.markdown('<div class="legende-pression">Observations Hydrostatiques</div>', unsafe_allow_html=True)
                st.write("**Case 1 :** Plusieurs réservoirs de formes et de sections totalement différentes sont reliés à leur base.")
                st.write("**Case 2 :** Lorsque l'on verse le liquide, les molécules se répartissent librement d'un contenant à un autre.")
                st.write("**Case 3 :** À l'équilibre, la hauteur du fluide atteint strictement le même niveau horizontal dans chaque colonne.")
                st.write("**Case 4 :** Ce phénomène confirme que la pression en un point ne dépend pas du volume de fluide mais uniquement de la profondeur.")
            with sub_col_img:
                st.image("https://unsplash.com")

                st.markdown('<div class="legende-pression">Analyse de la répartition des niveaux hydrostatiques</div>', unsafe_allow_html=True)

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 4 : SYNTHÈSE DE L'ATELIER (TEXTE À TROUS - 10 CASES)
            st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
            for ligne in st.session_state.champs_pres3_clean:
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_pres3_clean", disabled=verrouille, label_visibility="collapsed")


    # --- EXECUTION DE LA LOGIQUE DE CORRECTION ET D'EXPORT DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_pression" not in st.session_state:
        st.session_state.suite_verrouille_tab3_pression = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_pression

    # Appel de la fonction d'affichage
    afficher_atelier_pression(verrouille=verrou_at3)
    
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
            # Correction automatique du Quiz
            score_q3 = 0.0
            if "ordre_quiz_pres3_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_pres3_aleatoire:
                    saisie = st.session_state.get(f"pres3_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # Correction automatique du Texte à trous
            score_t3 = 0.0
            if "champs_pres3_clean" in st.session_state:
                for ligne in st.session_state.champs_pres3_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_pres3_clean", "Choisir...") == attendu: 
                        score_t3 += 1.0

            st.session_state.score_suite3_pres_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_pres_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_pres = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_pression = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML DE L'ATELIER 3 ---
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
                .header-box {{ background-color: #10b981; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier 3 : Lois barométriques, phénomènes hydrostatiques et instruments manométriques</p>
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
                saisie = st.session_state.get(f"pres3_at3_final_g_{q_item['id']}", "Choisir...")
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
                
                saisie_texte = st.session_state.get(f"{cle_variable}_pres3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_pres3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_pres3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_pres3 = preparer_nom_fichier("Rapport_Etude_Pression").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3",
            data=html_export_pres3,
            file_name=nom_fichier_html_pres3,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_pres3_final"
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

    # DÉFINITION INTERNE DE L'ATELIER INTERACTIF (QUIZ, SURFACE ET TROUS)
    def afficher_atelier_surface(verrouille=False):
        import random
        import math

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

        # SÉPARATION PRINCIPALE EN DEUX GRANDES COLONNES GLOBALES (Mise en page style 4 pages par feuille)
        col_gauche_globale, col_droite_globale = st.columns(2)

        # ---------------------------------------------------------------------
        # COLONNE GAUCHE (PAGES 1 ET 3 : CONTEXTE, SIMULATEUR ET QUIZ)
        # ---------------------------------------------------------------------
        with col_gauche_globale:
            # PAGE 1 : CONTEXTE HISTORIQUE
            st.subheader("La Galerie des Génies : La Mesure des Aires")
            st.markdown("""
            <div class="bandeau-surface">
                <b>Repères Historiques :</b> Dès l'Antiquité, Archimède de Syracuse développe la méthode d'exhaustion pour encadrer précisément la valeur de Pi et calculer l'aire du disque. Cette maîtrise géométrique s'avérera indispensable des siècles plus tard pour concevoir les pistons des premières machines hydrauliques.
            </div>
            """, unsafe_allow_html=True)

            sub_col_hist1, sub_col_hist2 = st.columns(2)
            with sub_col_hist1:
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-surface">Géométrie d\'Archimède</div>', unsafe_allow_html=True)
            with sub_col_hist2:
                st.image("https://wikimedia.org", use_container_width=True)
                st.markdown('<div class="legende-surface">Blaise Pascal (1623 - 1662)</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # SIMULATEUR INTERACTIF DE SECTION DE VÉRIN
            st.markdown("**Simulateur de Dimensionnement de Surface Circulaire**")
            diametre_mm = st.slider("Ajuster le diamètre utile du piston (en millimètres) :", min_value=10, max_value=200, value=50, step=5, disabled=verrouille, key="slider_diametre_piston")
            
            # Calcul en mm² puis conversion en m²
            surface_mm2 = (math.pi * (diametre_mm ** 2)) / 4
            surface_m2 = surface_mm2 / 1_000_000
            st.info(f"Calcul Géométrique : Pour un diamètre de {diametre_mm} mm, la surface d'appui utile est de {surface_mm2:.1f} mm² (soit {surface_m2:.6f} m²).")

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 3 : QUIZ TECHNIQUE DE LA SURFACE
            st.markdown("##### Quiz Technique (10 questions - 10 pts)")
            for idx, q_data in enumerate(st.session_state.ordre_quiz_surf4_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"surf4_at4_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

        # ---------------------------------------------------------------------
        # COLONNE DROITE (PAGES 2 ET 4 : CARICATURE, MODÉLISATION ET TROUS)
        # ---------------------------------------------------------------------
        with col_droite_globale:
            # PAGE 2 : BANDE CARICATURALE TECHNIQUE
            st.subheader("Bande Caricaturale : Le Paradoxe des Raquettes à Neige")
            
            sub_col_text, sub_col_img = st.columns([0.45, 0.55])
            with sub_col_text:
                st.markdown('<div class="legende-surface">Répartition des Pressions</div>', unsafe_allow_html=True)
                st.write("**Case 1 :** Un randonneur équipé de bottes classiques s'enfonce profondément au premier pas dans la neige poudreuse.")
                st.write("**Case 2 :** Son poids (Force) se concentre sur la faible section de ses semelles, créant une forte pression locale.")
                st.write("**Case 3 :** Il chausse des raquettes de grande section. La force de son poids reste rigoureusement inchangée.")
                st.write("**Case 4 :** En multipliant la surface d'appui par dix, la pression s'effondre. Il marche à la surface sans s'enfoncer.")
            with sub_col_img:
                st.image("https://unsplash.com")
                st.markdown('<div class="legende-surface">Vérification de la surface géométrique d\'un support support mécanique</div>', unsafe_allow_html=True)

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 4 : SYNTHÈSE DE L'ATELIER (TEXTE À TROUS - 10 CASES)
            st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
            for ligne in st.session_state.champs_surf4_clean:
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_surf4_clean", disabled=verrouille, label_visibility="collapsed")


    # --- EXECUTION DE LA LOGIQUE DE CORRECTION ET D'EXPORT DE L'ATELIER 4 ---
    if "suite_verrouille_tab4_surface" not in st.session_state:
        st.session_state.suite_verrouille_tab4_surface = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_surface

    # Appel de la fonction d'affichage
    afficher_atelier_surface(verrouille=verrou_at4)
    
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
            # Correction automatique du Quiz
            score_q4 = 0.0
            if "ordre_quiz_surf4_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_surf4_aleatoire:
                    saisie = st.session_state.get(f"surf4_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q4 += 1.0

            # Correction automatique du Texte à trous
            score_t4 = 0.0
            if "champs_surf4_clean" in st.session_state:
                for ligne in st.session_state.champs_surf4_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_surf4_clean", "Choisir...") == attendu: 
                        score_t4 += 1.0

            st.session_state.score_suite4_surf_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_surf_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_surf = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_surface = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML DE L'ATELIER 4 ---
    if st.session_state.get("suite_verrouille_tab4_surface", False):
        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_surf_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_surf_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_surf", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER SURFACE SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

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
                <p>Atelier 4 : Dimensionnement géométrique des sections et transmission des forces pressantes</p>
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
                saisie = st.session_state.get(f"surf4_at4_final_g_{q_item['id']}", "Choisir...")
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
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_surf4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_surf4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_surf4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_surf4 = preparer_nom_fichier("Rapport_Etude_Surfaces").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4",
            data=html_export_surf4,
            file_name=nom_fichier_html_surf4,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_surf4_final"
        )


with tab5:
    st.header("Application professionnelle : Diagnostic et Maintenance")
    
    id_cas_maint = st.session_state.cas_aleatoire_tab5
    st.write(f"Dossier technique de maintenance attribué : **Anomalie mécanique n°{id_cas_maint}**")

    # Styles CSS pour les légendes, bandeaux et alertes de l'Atelier 5
    st.markdown("""
    <style>
    .legende-maint { color: #dc2626; font-weight: bold; text-align: center; margin-top: 5px; font-size: 13px; }
    .bandeau-maint { background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 12px; font-size: 14px; font-weight: 500; margin-bottom: 20px; color: #991b1b; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

    # DÉFINITION DYNAMIQUE DE L'ATELIER DE MAINTENANCE SELON LE CAS
    def afficher_atelier_maintenance(verrouille=False):
        import random

        # ---------------------------------------------------------------------
        # CONFIGURATION DES BANQUES DE DONNÉES SELON LE CAS DE MAINTENANCE
        # ---------------------------------------------------------------------
        if id_cas_maint == 1:
            titre_maint = "Défaut d'étanchéité du piston sur un vérin hydraulique de presse"
            desc_bd = [
                "**Case 1 :** La presse hydraulique n'atteint plus sa force nominale de compactage lors des cycles de production.",
                "**Case 2 :** Le technicien connecte un manomètre en dérivation et constate une chute de pression en fin de course.",
                "**Case 3 :** Le diagnostic confirme un passage d'huile interne entre la chambre de travail et la chambre de retour.",
                "**Case 4 :** Après remplacement du joint composite de section, le profil de pression redevient conforme aux spécifications."
            ]
            questions_sources = [
                {"id": "qm1", "q": "Quel appareil de mesure permet de valider la valeur de pression dans le circuit ?", "options": ["Un manomètre", "Un débitmètre", "Un thermomètre"], "rep": "Un manomètre"},
                {"id": "qm2", "q": "Si l'huile contourne le piston à cause d'un joint usé, comment qualifie-t-on cette défaillance ?", "options": ["Une fuite interne", "Une fuite externe", "Une cavitation"], "rep": "Une fuite interne"},
                {"id": "qm3", "q": "Dans la relation P = F / S, si l'huile fuit et la pression s'effondre, la force développée :", "options": ["Chute proportionnellement", "Reste maximale", "Augmente subitement"], "rep": "Chute proportionnellement"},
                {"id": "qm4", "q": "Quelle unité normalisée est généralement lue sur le cadran d'un manomètre industriel ?", "options": ["Le bar", "Le Newton", "Le mètre par seconde"], "rep": "Le bar"},
                {"id": "qm5", "q": "Pour augmenter la force d'une presse sans modifier sa pression de service, il faut :", "options": ["Augmenter la section du vérin", "Réduire le diamètre du piston", "Allonger la course"], "rep": "Augmenter la section du vérin"},
                {"id": "qm6", "q": "Un fluide hydraulique industriel est utilisé dans les circuits car il est pratiquement :", "options": ["Incompressible", "Compressible", "Volatile"], "rep": "Incompressible"},
                {"id": "qm7", "q": "La force pressante s'exerçant sur la face plane d'un piston de vérin agit toujours de façon :", "options": ["Perpendiculaire", "Parallèle", "Oblique"], "rep": "Perpendiculaire"},
                {"id": "qm8", "q": "Quel risque présente une huile contenant des impuretés ou des particules métalliques ?", "options": ["Abrasion des joints de section", "Augmentation de la viscosité", "Chute de la gravité"], "rep": "Abrasion des joints de section"},
                {"id": "qm9", "q": "Quelle opération préventive permet de limiter l'usure prématurée des composants hydrauliques ?", "options": ["La filtration périodique", "Le surtarage des valves", "L'augmentation du débit"], "rep": "La filtration périodique"},
                {"id": "qm10", "q": "L'unité de pression du système international équivalente à 1 N/m² est :", "options": ["Le Pascal", "Le Bar", "Le Joule"], "rep": "Le Pascal"}
            ]
            trous_sources = [
                ("1. Un manque de force sur un actionneur traduit une perte de .......... hydraulique.", ["Choisir...", "pression", "vitesse"], "pression", "m5_t1"),
                ("2. Le manomètre mesure l'effort réparti par le fluide sur l'unité de ..........", ["Choisir...", "surface", "longueur"], "surface", "m5_t2"),
                ("3. Le contournement du piston par le fluide constitue une fuite ..........", ["Choisir...", "interne", "externe"], "interne", "m5_t3"),
                ("4. La force pressante se déploie de manière orthogonale, donc .......... à la paroi.", ["Choisir...", "perpendiculaire", "tangente"], "perpendiculaire", "m5_t4"),
                ("5. L'unité courante lue sur les cadrans des techniciens est le ..........", ["Choisir...", "bar", "Pascal"], "bar", "m5_t5"),
                ("6. Pour restaurer l'étanchéité, il faut remplacer le .......... d'usure.", ["Choisir...", "joint", "piston"], "joint", "m5_t6"),
                ("7. Un fluide sous pression transmet son action dans toutes les ..........", ["Choisir...", "directions", "lignes"], "directions", "m5_t7"),
                ("8. L'huile de maintenance est choisie pour ses propriétés d'..........", ["Choisir...", "incompressibilité", "dilatation"], "incompressibilité", "m5_t8"),
                ("9. Modifier l'aire de poussée modifie l'intensité du vecteur .......... développé.", ["Choisir...", "force", "vitesse"], "force", "m5_t9"),
                ("10. Le maintien d'une pression stable garantit le bon fonctionnement mécanique de la ..........", ["Choisir...", "presse", "pompe"], "presse", "m5_t10")
            ]

        elif id_cas == 2:
            titre_maint = "Rupture par fatigue d'une canalisation rigide de distribution"
            desc_bd = [
                "**Case 1 :** Une canalisation en acier éclate brutalement lors d'une phase de surpression transitoire.",
                "**Case 2 :** L'équipe de maintenance balise la zone et isole le tronçon en fermant les vannes de sectionnement.",
                "**Case 3 :** L'expertise révèle une fragilisation du métal due à des vibrations répétées et des coups de bélier.",
                "**Case 4 :** Une nouvelle conduite avec lyre de dilatation et amortisseurs de pulsations est mise en service."
            ]
            questions_sources = [
                {"id": "qm1", "q": "Comment qualifie-t-on une onde de surpression brutale provoquée par la fermeture rapide d'une vanne ?", "options": ["Un coup de bélier", "Une cavitation", "Un effet Venturi"], "rep": "Un coup de bélier"},
                {"id": "qm2", "q": "Quelle unité SI définit la contrainte mécanique maximale admissible par l'acier du tube ?", "options": ["Le Pascal (ou MPa)", "Le Newton", "Le Bar"], "rep": "Le Pascal (ou MPa)"},
                {"id": "qm3", "q": "Pour dissiper les ondes de choc de pression dans un circuit, quel composant ajoute-t-on ?", "options": ["Un accumulateur hydropneumatique", "Une pompe de gavage", "Un limiteur de débit"], "rep": "Un accumulateur hydropneumatique"},
                {"id": "qm4", "q": "La force de rupture appliquée sur la paroi du tube dépend de la pression et de :", "options": ["La surface intérieure exposée", "La longueur totale de la ligne", "La température ambiante"], "rep": "La surface intérieure exposée"},
                {"id": "qm5", "q": "Une rupture par application répétée de contraintes inférieures à la limite élastique est appelée :", "options": ["Rupture par fatigue", "Rupture ductile", "Arrachement thermique"], "rep": "Rupture par fatigue"},
                {"id": "qm6", "q": "Quel appareil permet de détecter des micro-fissures invisibles à l'œil nu sur un tube ?", "options": ["Un système de contrôle par ressuage", "Un manomètre", "Un multimètre"], "rep": "Un système de contrôle par ressuage"},
                {"id": "qm7", "q": "Si l'épaisseur de la paroi du tube est doublée, sa résistance aux forces pressantes :", "options": ["Augmente", "Diminue", "Reste inchangée"], "rep": "Augmente"},
                {"id": "qm8", "q": "Les colliers de fixation d'une tuyauterie industrielle ont pour rôle principal de :", "options": ["Amortir les vibrations", "Augmenter la pression", "Guider le fluide"], "rep": "Amortir les vibrations"},
                {"id": "qm9", "q": "En cas de fuite externe de fluide, quel est le premier réflexe de sécurité ?", "options": ["Consigner l'énergie hydraulique", "Remplacer le tube sous pression", "Essuyer le fluide"], "rep": "Consigner l'énergie hydraulique"},
                {"id": "qm10", "q": "La direction de la force pressante qui a fissuré le tube était :", "options": ["Perpendiculaire à la surface interne", "Parallèle à l'écoulement", "Hélicoïdale"], "rep": "Perpendiculaire à la surface interne"}
            ]
            trous_sources = [
                ("1. L'élévation brutale et transitoire de la pression est un coup de ..........", ["Choisir...", "bélier", "frein"], "bélier", "m5_t1"),
                ("2. La sollicitation répétée du métal entraîne une rupture par ..........", ["Choisir...", "fatigue", "flexion"], "fatigue", "m5_t2"),
                ("3. La force destructive est le produit de la surpression par la .......... interne.", ["Choisir...", "surface", "longueur"], "surface", "m5_t3"),
                ("4. La contrainte mécanique dans le métal s'exprime légalement en ..........", ["Choisir...", "Pascals", "Newtons"], "Pascals", "m5_t4"),
                ("5. Avant toute intervention sur la conduite, il faut effectuer la ..........", ["Choisir...", "consignation", "lubrification"], "consignation", "m5_t5"),
                ("6. Pour absorber les variations de volume, on installe un ..........", ["Choisir...", "accumulateur", "filtre"], "accumulateur", "m5_t6"),
                ("7. Les colliers rigides limitent la propagation des .......... mécaniques.", ["Choisir...", "vibrations", "fluides"], "vibrations", "m5_t7"),
                ("8. Le vecteur force pressante s'exerce de l'intérieur vers l'.......... du tube.", ["Choisir...", "extérieur", "centre"], "extérieur", "m5_t8"),
                ("9. L'acier est choisi pour sa haute limite de résistance ..........", ["Choisir...", "élastique", "thermique"], "élastique", "m5_t9"),
                ("10. Le remplacement du tronçon rétablit la continuité de la ..........", ["Choisir...", "distribution", "aspiration"], "distribution", "m5_t10")
            ]

        elif id_cas_maint == 3:
            titre_maint = "Cavitation et érosion de la turbine d'une pompe centrifuge"
            desc_bd = [
                "**Case 1 :** Une pompe de transfert émet un bruit anormal de gravier et son débit chute en continu.",
                "**Case 2 :** Au démontage, le technicien découvre des micro-cavités de matière détruite sur les pales.",
                "**Case 3 :** La chute locale de pression sous la tension de vapeur a provoqué l'implosion de bulles de gaz.",
                "**Case 4 :** La hauteur d'aspiration est corrigée et une turbine neuve à traitement de surface est posée."
            ]
            questions_sources = [
                {"id": "qm1", "q": "Quel phénomène physique provoque la formation et l'implosion de bulles de vapeur dans une pompe ?", "options": ["La cavitation", "La lamination", "L'oxydation"], "rep": "La cavitation"},
                {"id": "qm2", "q": "La cavitation se produit lorsque la pression locale descend en dessous de :", "options": ["La pression de vapeur saturante", "La pression atmosphérique", "Le vide absolu"], "rep": "La pression de vapeur saturante"},
                {"id": "qm3", "q": "Quel type de bruit caractéristique signale la présence de cavitation dans une tuyauterie ?", "options": ["Un crépitement (bruit de gravier)", "Un sifflement aigu", "Un ronronnement sourd"], "rep": "Un crépitement (bruit de gravier)"},
                {"id": "qm4", "q": "L'implosion des bulles génère des micro-jets de fluide dont la force locale crée une pression :", "options": ["Extrêmement élevée", "Parfaitement nulle", "Négative"], "rep": "Extrêmement élevée"},
                {"id": "qm5", "q": "Pour éviter la cavitation, il faut s'assurer que le NPSH disponible du circuit est :", "options": ["Supérieur au NPSH requis de la pompe", "Inférieur au NPSH requis", "Égal à zéro"], "rep": "Supérieur au NPSH requis de la pompe"},
                {"id": "qm6", "q": "L'érosion des pales de la turbine modifie leur profil géométrique, ce qui réduit :", "options": ["Le rendement hydrostatique", "La vitesse de rotation", "La masse du fluide"], "rep": "Le rendement hydrostatique"},
                {"id": "qm7", "q": "Une solution de maintenance pour réduire la cavitation à l'aspiration consiste à :", "options": ["Diminuer la hauteur d'aspiration", "Augmenter la vitesse de la pompe", "Restreindre le diamètre d'entrée"], "rep": "Diminuer la hauteur d'aspiration"},
                {"id": "qm8", "q": "La force d'impact répétée des bulles arrache la matière par un phénomène de :", "options": ["Fatigue de surface mécanique", "Corrosion chimique pure", "Dilatation thermique"], "rep": "Fatigue de surface mécanique"},
                {"id": "qm9", "q": "Quel appareil permet de mesurer la dépression à l'entrée d'aspiration d'une pompe ?", "options": ["Un vacuomètre", "Un débitmètre à engrenages", "Un thermomètre"], "rep": "Un vacuomètre"},
                {"id": "qm10", "q": "Dans quelle zone de la pale la pression est-elle la plus basse, favorisant les bulles ?", "options": ["Le côté aspiration (extrados)", "Le côté pression (intrados)", "Le moyeu central"], "rep": "Le côté aspiration (extrados)"}
            ]
            trous_sources = [
                ("1. La formation de bulles de vapeur due à une baisse de pression est la ..........", ["Choisir...", "cavitation", "lamination"], "cavitation", "m5_t1"),
                ("2. Ce phénomène apparaît quand la pression descend sous le seuil de ..........", ["Choisir...", "vapeur saturante", "pression nominale"], "vapeur saturante", "m5_t2"),
                ("3. L'implosion des bulles libère une .......... d'impact locale destructrice.", ["Choisir...", "force", "chaleur"], "force", "m5_t3"),
                ("4. Les chocs répététés provoquent un arrachement de matière appelé ..........", ["Choisir...", "érosion", "grippage"], "érosion", "m5_t4"),
                ("5. Le contrôle de la pression d'entrée s'effectue avec un ..........", ["Choisir...", "vacuomètre", "débitmètre"], "vacuomètre", "m5_t5"),
                ("6. Pour stopper le défaut, on doit augmenter la pression à l'..........", ["Choisir...", "aspiration", "refoulement"], "aspiration", "m5_t6"),
                ("7. Le bruit de fonctionnement s'apparente à un passage de ..........", ["Choisir...", "gravier", "liquide fluide"], "gravier", "m5_t7"),
                ("8. Les pales de la roue constituent la .......... d'action géométrique.", ["Choisir...", "surface", "longueur"], "surface", "m5_t8"),
                ("9. L'altération géométrique de la turbine détruit son .......... hydraulique.", ["Choisir...", "rendement", "poids"], "rendement", "m5_t9"),
                ("10. La remise en état exige le remplacement de la .......... endommagée.", ["Choisir...", "turbine", "volute"], "turbine", "m5_t10")
            ]

        else:
            titre_maint = "Anomalie de tarage sur un limiteur de pression de centrale hydraulique"
            desc_bd = [
                "**Case 1 :** Les actionneurs de la machine se déplacent trop lentement et la centrale surchauffe.",
                "**Case 2 :** Le technicien constate que le fluide s'échappe en continu vers le réservoir via la ligne de décharge.",
                "**Case 3 :** La force du ressort de la valve de sécurité est trop faible par rapport à la consigne requise.",
                "**Case 4 :** Le technicien ajuste la vis de réglage pour comprimer le ressort et restaurer la pression nominale."
            ]
            questions_sources = [
                {"id": "qm1", "q": "Quel composant protège le circuit hydraulique contre les surpressions dangereuses ?", "options": ["Le limiteur de pression", "Le clapet anti-retour", "Le filtre"], "rep": "Le limiteur de pression"},
                {"id": "qm2", "q": "Si le limiteur est réglé trop bas, que devient l'énergie de la pompe non utilisée ?", "options": ["Elle se dissipe en chaleur (surchauffe)", "Elle est détruite", "Elle augmente le débit utile"], "rep": "Elle se dissipe en chaleur (surchauffe)"},
                {"id": "qm3", "q": "La force qui pousse le clapet du limiteur pour l'ouvrir provient de :", "options": ["La force pressante du fluide", "La tension du ressort", "Le débit de la pompe"], "rep": "La force pressante du fluide"},
                {"id": "qm4", "q": "Quel composant mécanique interne s'oppose à l'ouverture du clapet de décharge ?", "options": ["Un ressort de tarage", "Un piston amortisseur", "Une aiguille conique"], "rep": "Un ressort de tarage"},
                {"id": "qm5", "q": "Pour augmenter la valeur de déclenchement du limiteur, il faut :", "options": ["Comprimer le ressort (visser)", "Détendre le ressort (dévisser)", "Changer l'huile"], "rep": "Comprimer le ressort (visser)"},
                {"id": "qm6", "q": "À l'instant précis où la valve s'ouvre, la force du fluide et la force du ressort sont :", "options": ["Strictement égales (équilibre)", "Opposées et asymétriques", "Nulles"], "rep": "Strictement égales (équilibre)"},
                {"id": "qm7", "q": "L'ouverture du limiteur renvoie directement le fluide excédentaire vers :", "options": ["Le réservoir (bac)", "Le vérin", "L'accumulateur"], "rep": "Le réservoir (bac)"},
                {"id": "qm8", "q": "Quelle est l'unité légale d'intensité pour régler l'effort de fermeture du ressort ?", "options": ["Le Newton", "Le Pascal", "Le Bar"], "rep": "Le Newton"},
                {"id": "qm9", "q": "Si le limiteur reste bloqué en position ouverte, la pression du circuit sera :", "options": ["Proche de zéro", "Maximale", "Instable"], "rep": "Proche de zéro"},
                {"id": "qm10", "q": "Le contrôle final du bon tarage s'effectue en observant un :", "options": ["Manomètre en dérivation", "Débitmètre de ligne", "Thermomètre"], "rep": "Manomètre en dérivation"}
            ]
            trous_sources = [
                ("1. La protection de la centrale est assurée par le limiteur de ..........", ["Choisir...", "pression", "débit"], "pression", "m5_t1"),
                ("2. L'effort d'opposition interne est généré par un .......... métallique.", ["Choisir...", "ressort", "piston"], "ressort", "m5_t2"),
                ("3. Le fluide exerce sur le clapet une .......... pressante ascendante.", ["Choisir...", "force", "vitesse"], "force", "m5_t3"),
                ("4. L'aire du clapet soumise au fluide constitue la .......... de contact.", ["Choisir...", "surface", "section"], "surface", "m5_t4"),
                ("5. Un tarage trop bas provoque une décharge permanente vers le ..........", ["Choisir...", "réservoir", "vérin"], "réservoir", "m5_t5"),
                ("6. L'énergie perdue par laminage se transforme directement en ..........", ["Choisir...", "chaleur", "pression"], "chaleur", "m5_t6"),
                ("7. Pour corriger le réglage, le technicien doit .......... la vis de tarage.", ["Choisir...", "visser", "dévisser"], "visser", "m5_t7"),
                ("8. L'intensité des actions mécaniques antagonistes est mesurée en ..........", ["Choisir...", "Newtons", "Pascals"], "Newtons", "m5_t8"),
                ("9. Le contrôle visuel du seuil de basculement utilise un ..........", ["Choisir...", "manomètre", "thermomètre"], "manomètre", "m5_t9"),
                ("10. À l'équilibre limite, les vecteurs forces opposés possèdent la même ..........", ["Choisir...", "intensité", "direction"], "intensité", "m5_t10")
            ]

        # Sauvegarde des listes configurées dans l'état de la session élève
        st.session_state.ordre_quiz_maint_aleatoire = questions_sources
        st.session_state.champs_maint_clean = trous_sources

        # SÉPARATION EN DEUX COLONNES GLOBALES STYLE 4 PAGES PAR FEUILLE
        col_gauche_globale, col_droite_globale = st.columns(2)

        # ---------------------------------------------------------------------
        # COLONNE GAUCHE (PAGES 1 ET 3 : CAS TECHNIQUE ET QUIZ ADAPTATIF)
        # ---------------------------------------------------------------------
        with col_gauche_globale:
            st.subheader(f"Dossier Technique : {titre_maint}")
            st.markdown("""
            <div class="bandeau-maint">
                <b>Analyse du Cas :</b> Examinez la situation d'anomalie industrielle affectant votre poste. Identifiez le lien mécanique direct entre force, surface et pression pour remplir le questionnaire de diagnostic.
            </div>
            """, unsafe_allow_html=True)

            # AFFICHAGE CHRONOLOGIQUE DES SYMPTÔMES DU CAS ACTIF
            st.write("**Symptômes constatés en atelier :**")
            for case_texte in desc_bd:
                st.write(case_texte)

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 3 : QUIZ DE DIAGNOSTIC À 10 QUESTIONS
            st.markdown("##### Quiz de Diagnostic (10 questions - 10 pts)")
            for idx, q_data in enumerate(st.session_state.ordre_quiz_maint_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"maint_at5_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

        # ---------------------------------------------------------------------
        # COLONNE DROITE (PAGES 2 ET 4 : ILLUSTRATION ET SYNTHÈSE TEXTE À TROUS)
        # ---------------------------------------------------------------------
        with col_droite_globale:
            st.subheader("Bande Caricaturale de l'Incident")
            
            sub_col_text, sub_col_img = st.columns([0.50, 0.50])
            with sub_col_text:
                st.markdown('<div class="legende-maint">Rapport d\'Intervention</div>', unsafe_allow_html=True)
                for case_texte in desc_bd:
                    st.write(case_texte)
            with sub_col_img:
                st.image("https://unsplash.com")
                st.markdown('<div class="legende-maint">Résolution technique du dysfonctionnement</div>', unsafe_allow_html=True)

            st.markdown("<br><hr><br>", unsafe_allow_html=True)

            # PAGE 4 : SYNTHÈSE DE L'ATELIER (TEXTE À TROUS ADAPTATIF DE 10 CASES)
            st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
            for ligne in st.session_state.champs_maint_clean:
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_maint_clean", disabled=verrouille, label_visibility="collapsed")


    # --- EXECUTION DE LA LOGIQUE DE CORRECTION ET D'EXPORT DE L'ATELIER 5 ---
    if "suite_verrouille_tab5_maint" not in st.session_state:
        st.session_state.suite_verrouille_tab5_maint = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_maint

    # Appel de la fonction d'affichage de l'atelier 5
    afficher_atelier_maintenance(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de diagnostic de l'Atelier Maintenance.",
        key="check_certif_maint5_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_maint_official", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Correction automatique du Quiz
            score_q5 = 0.0
            if "ordre_quiz_maint_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_maint_aleatoire:
                    saisie = st.session_state.get(f"maint_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q5 += 1.0

            # Correction automatique du Texte à trous
            score_t5 = 0.0
            if "champs_maint_clean" in st.session_state:
                for ligne in st.session_state.champs_maint_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_maint_clean", "Choisir...") == attendu: 
                        score_t5 += 1.0

            st.session_state.score_suite5_maint_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_maint_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_maint = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_maint = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML DE L'ATELIER 5 ---
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

        if "ordre_quiz_maint_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_maint_aleatoire, 1):
                saisie = st.session_state.get(f"maint_at5_final_g_{q_item['id']}", "Choisir...")
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

        if "champs_maint_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_maint_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_maint_clean", "Choisir...")
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
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5",
            data=html_export_maint5,
            file_name=nom_fichier_html_maint5,
            mime="text/html",
            use_container_width=True,
            key="btn_download_html_maint_final"
        )














