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

def afficher_questions_forces_dynamiques(verrouille=False):
    import streamlit as st
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
        with c9: st.write("5. Le poids d'un objet est une action mécanique s'exerçant à")
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
    with col_forces_b:
        st.markdown("**Forces à distance**")
        st.write("L'action s'exerce sans qu'il n'y ait de contact physique entre les objets.")
        st.markdown("- Force gravitationnelle (Poids d'un corps)\n- Force magnétique (Aimant)\n- Force électrostatique")

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




