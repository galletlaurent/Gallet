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

