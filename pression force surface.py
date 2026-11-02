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
            enonce, choix, cle = ligne, ligne, ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_pres_clean", disabled=verrouille, label_visibility="collapsed")


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
        st.image("https://wikimedia.org", width=180, caption="Blaise Pascal")
        st.markdown("""
        * **Sa Trouvaille :** La formulation de la pression comme le rapport d'une force sur une surface (**P = F / S**). Il démontre qu'une même force répartie sur une surface plus petite engendre une pression bien plus élevée.
        * **L'Expérience Célèbre :** *Le crève-tonneau de Pascal (1646)*. En appliquant le poids d'un faible volume d'eau (Force) au sommet d'un long tube de très fine section (Surface minuscule), il génère une pression hydrostatique immense capable de faire éclater le bois.
        """)
        
    with col_torricelli:
        st.markdown("### Evangelista Torricelli (1608 - 1647)")
        # Remplacement du lien générique par le portrait officiel de Evangelista Torricelli
        st.image("https://wikimedia.org", width=180, caption="Evangelista Torricelli")
        st.markdown("""
        * **Sa Trouvaille :** La mesure de la force pressante de l'air. Il est le premier à quantifier la force colossale exercée par le poids de l'atmosphère sur chaque unité de surface terrestre.
        * **L'Expérience Célèbre :** *Le tube de Torricelli (1643)*. Il équilibre la force du poids de l'atmosphère s'exerçant sur la surface d'un bassin avec le poids d'une colonne de mercure de 76 centimètres de hauteur.
        """)

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

    # Création des deux colonnes principales pour la BD
    col_bd_texte, col_bd_image = st.columns([1, 1])

    # Colonne de gauche : Empilement de toutes les cases de texte
    with col_bd_texte:
        st.markdown("**Case 1 : À la taverne de la Science (Paris, 1648)**")
        st.markdown('<div class="narrateur">Pascal et Torricelli s\'installent à une table. Torricelli pose un lourd tube de mercure sur le comptoir, l\'air fatigué.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Torricelli :</b> "Mon cher Blaise, j\'ai mal au dos... L\'air pèse des tonnes aujourd\'hui ! Les gens croient que la nature a horreur du vide, mais c\'est faux, c\'est juste l\'atmosphère qui applique sa force sur chaque unité de surface terrestre !"</div>', unsafe_allow_html=True)

        st.markdown("**Case 2 : L\'illumination de Pascal**")
        st.markdown('<div class="narrateur">Pascal regarde son verre, prend une paille, et tape du poing sur la table.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Pascal :</b> "Tu as raison Evangelista ! Et regarde ça : la pression dépend directement du rapport P = F / S. Si j\'appuie sur mon verre ici, la pression pousse le liquide partout en même temps ! C\'est comme cela que j\'ai brisé mon tonneau !"</div>', unsafe_allow_html=True)

        st.markdown("**Case 3 : La panique au laboratoire**")
        st.markdown('<div class="narrateur">Le serveur de la taverne recule, inquiet des théories des deux physiciens et des formules mathématiques.</div>', unsafe_allow_html=True)
        st.markdown('<div class="bulles"><b>Le Serveur :</b> "Messieurs, calmez-vous avec vos calculs de force et de surface. Vous voulez régler l\'addition ou vous allez aussi faire éclater ma cave avec votre relation P = F / S ?"<br><br><b>Pascal et Torricelli (en chœur) :</b> "C\'est pour la science !"</div>', unsafe_allow_html=True)

    # Colonne de droite : Affichage de la grande image de la BD qui s'aligne avec le texte
    with col_bd_image:
        st.image("bd_cuve4.png", use_container_width=True, caption="Anomalie hydrostatique sur la Cuve 4")

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




















