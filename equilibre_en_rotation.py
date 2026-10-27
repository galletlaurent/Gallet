# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application équilibre en rotation",
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
st.title("Application équilibre en rotation")
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

def afficher_questions_exemple2_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    # Récupération des valeurs de l'élève
    f1_user = st.session_state.get("ex2_f1_aleatoire", 12000)
    d1_user = st.session_state.get("ex2_d1_aleatoire", 15)
    f2_user = st.session_state.get("ex2_f2_aleatoire", 36000)
    d2_user_attendu = round((f1_user * d1_user) / f2_user, 2)
    m1_user = f1_user * d1_user
    
    # Faux calculs pour les options
    faux_d1 = round((f1_user * f2_user) / d1_user, 2)
    faux_d2 = round(m1_user + f2_user, 2)

    if "ordre_quiz_ex2" not in st.session_state:
        base_quiz_ex2 = [
            {"id": "qe2_1", "q": f"À l'équilibre de la grue, le moment de F1 à gauche doit compenser le moment de :", "type": "menu", "options": ["F2 à droite", "L'axe central uniquement", "La flèche seule"], "rep": "F2 à droite"},
            {"id": "qe2_2", "q": f"Calculez le moment généré à gauche par la charge F1 (M1 = {f1_user} N x {d1_user} m) :", "type": "menu", "options": [f"{m1_user} N.m", f"{f1_user} N.m", "180 000 N.m"], "rep": f"{m1_user} N.m"},
            {"id": "qe2_3", "q": f"Quelle est la valeur de la force F2 du contrepoids lue dans votre énoncé ?", "type": "menu", "options": [f"{f2_user} N", f"{f1_user} N", "36 000 N"], "rep": f"{f2_user} N"},
            {"id": "qe2_4", "q": "Pour isoler la distance d2 dans la relation d'équilibre, la formule exacte est :", "type": "menu", "options": ["d2 = (F1 x d1) / F2", "d2 = F2 / (F1 x d1)", "d2 = F1 x d1 x F2"], "rep": "d2 = (F1 x d1) / F2"},
            {"id": "qe2_5", "q": f"Quelle distance d2 trouvez-vous pour obtenir l'équilibre parfait de votre grue ?", "type": "menu", "options": [f"{d2_user_attendu} m", f"{faux_d1} m", f"{faux_d2} m"], "rep": f"{d2_user_attendu} m"},
            {"id": "qe2_6", "q": "Le poids du conteneur maritime suspendu constitue une force s'exerçant à :", "type": "menu", "options": ["Distance", "Contact", "Frottement"], "rep": "Distance"},
            {"id": "qe2_7", "q": "La droite d'action du vecteur poids d'un corps suspendu est toujours :", "type": "menu", "options": ["Verticale", "Horizontale", "Oblique"], "rep": "Verticale"},
            {"id": "qe2_8", "q": "Le point d'application de la force du poids du conteneur se situe au :", "type": "menu", "options": ["Centre de gravité G", "Point d'ancrage du câble", "Moyeu du mât central"], "rep": "Centre de gravité G"},
            {"id": "qe2_9", "q": "Si la charge F1 s'éloigne du mât central, son bras de levier d1 va :", "type": "menu", "options": ["Augmente", "Diminue", "Rester constant"], "rep": "Augmente"},
            {"id": "qe2_10", "q": "Si le moment à gauche devient supérieur au moment à droite, la grue va :", "type": "menu", "options": ["Basculer vers l'avant", "Basculer vers l'arrière", "Rester immobile"], "rep": "Basculer vers l'avant"}
        ]
        copie_base = list(base_quiz_ex2)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_ex2 = copie_base

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz technique de l'Exemple 2 (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_ex2, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ex2_cl_g_{q_data['id']}"
            cle_shuff_opts = f"opts_shuff_ex2_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = ["Choisir..."] + opts_copie
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_shuff_opts].index(val_p) if val_p in st.session_state[cle_shuff_opts] else 0
            dict_reponses_quiz[q_data["id"]] = st.selectbox("", st.session_state[cle_shuff_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de mécanique de l'Exemple 2 (10 trous - 10 pts)")
        dict_trous = {}
        trous_data_ex2 = [
            (f"1. Le moment calculé à gauche pour votre charge F1 s'élève à :", ["Choisir...", f"{m1_user} N.m", "180 000 N.m"], "ex2_t1_s6", f"{m1_user} N.m"),
            (f"2. À l'équilibre, le moment à droite créé par F2 doit valoir :", ["Choisir...", f"{m1_user} N.m", f"{f2_user} N.m"], "ex2_t2_s6", f"{m1_user} N.m"),
            (f"3. La distance théorique d2 calculée pour votre contrepoids vaut :", ["Choisir...", f"{d2_user_attendu} m", f"{d1_user} m"], "ex2_t3_s6", f"{d2_user_attendu} m"),
            (f"4. L'équilibre de la flèche est régi par le théorème des :", ["Choisir...", "Moments", "Trajectoires"], "ex2_t4_s6", "Moments"),
            (f"5. Le mât central de la structure matérialise l'axe noté :", ["Choisir...", "Delta", "Sigma"], "ex2_t5_s6", "Delta"),
            (f"6. L'intensité de l'action mécanique du contrepoids F2 est de :", ["Choisir...", f"{f2_user} N", "36 000 N"], "ex2_t6_s6", f"{f2_user} N"),
            (f"7. La distance d1 reliant l'axe à votre charge mesure :", ["Choisir...", f"{d1_user} m", "15 m"], "ex2_t7_s6", f"{d1_user} m"),
            (f"8. Les deux actions mécaniques s'exercent dans des sens :", ["Choisir...", "Opposés", "Identiques"], "ex2_t8_s6", "Opposés"),
            (f"9. Si le contrepoids se rapproche du centre, son moment va :", ["Choisir...", "Diminuer", "Augmenter"], "ex2_t9_s6", "Diminuer"),
            (f"10. Cette loi garantit la sécurité lors des opérations de :", ["Choisir...", "Levage", "Soudage"], "ex2_t10_s6", "Levage")
        ]
        for phrase, opts, key, rep in trous_data_ex2:
            c_p, c_s = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_p: st.write(phrase)
            with c_s: dict_trous[key] = st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous





def afficher_questions_exemple1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    # Récupération des valeurs de l'élève
    f_user = st.session_state.get("ex1_force_aleatoire", 150)
    d_cm_user = st.session_state.get("ex1_dist_aleatoire", 30)
    d_m_user = round(d_cm_user / 100, 2)
    m_user = round(f_user * d_m_user, 1)
    
    # Calculs pour de fausses options cohérentes
    faux_m1 = round(f_user / d_m_user, 1) if d_m_user != 0 else 0.0
    faux_m2 = round(f_user * d_cm_user, 1)

    if "ordre_quiz_ex1" not in st.session_state:
        base_quiz_ex1 = [
            {"id": "qe1_1", "q": f"Quelle est la formule littérale pour calculer le moment de votre force F = {f_user} N ?", "type": "menu", "options": ["M = F x d", "M = F / d", "M = F + d"], "rep": "M = F x d"},
            {"id": "qe1_2", "q": f"Quelle valeur lisez-vous pour l'intensité de votre force F dans l'énoncé personnalisé ?", "type": "menu", "options": [f"{f_user} N", f"{d_cm_user} N", "150 N"], "rep": f"{f_user} N"},
            {"id": "qe1_3", "q": f"Dans le calcul du moment, la distance initiale d = {d_cm_user} cm doit être exprimée en :", "type": "menu", "options": ["Mètres (m)", "Millimètres (mm)", "Kilomètres (km)"], "rep": "Mètres (m)"},
            {"id": "qe1_4", "q": f"Le moment de votre force (M = {f_user} N x {d_m_user} m) est égal à :", "type": "menu", "options": [f"{m_user} N.m", f"{faux_m1} N.m", f"{faux_m2} N.m"], "rep": f"{m_user} N.m"},
            {"id": "qe1_5", "q": "L'unité légale du moment d'une force calculé dans le système international est :", "type": "menu", "options": ["Newton-mètre (N.m)", "Newton (N)", "Mètre (m)"], "rep": "Newton-mètre (N.m)"},
            {"id": "qe1_6", "q": f"Si vous doublez la valeur de votre force (F = {f_user * 2} N) sans changer la clé, le moment :", "type": "menu", "options": ["Double", "Est divisé par deux", "Reste identique"], "rep": "Double"},
            {"id": "qe1_7", "q": "Si la droite d'action de la force passait par le centre de l'écrou, le moment serait :", "type": "menu", "options": ["Nul", "Plus grand", "Inversé"], "rep": "Nul"},
            {"id": "qe1_8", "q": "Le bras de levier est la distance mesurée de façon perpendiculaire par rapport à :", "type": "menu", "options": ["La droite d'action de la force", "L'extrémité de la clé", "Le sol de l'atelier"], "rep": "La droite d'action de la force"},
            {"id": "qe1_9", "q": "Une clé dotée d'un manche plus long permet d'obtenir, pour un même effort musculaire, un moment :", "type": "menu", "options": ["Plus élevé", "Plus faible", "Identique"], "rep": "Plus élevé"},
            {"id": "qe1_10", "q": "L'appareil professionnel d'atelier utilisé pour appliquer ce couple précis est la :", "type": "menu", "options": ["Clé dynamométrique", "Clé plate standard", "Pince multiprise"], "rep": "Clé dynamométrique"}
        ]
        copie_base = list(base_quiz_ex1)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz_ex1 = copie_base

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz technique de l'Exemple 1 (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        for idx, q_data in enumerate(st.session_state.ordre_quiz_ex1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ex1_cl_g_{q_data['id']}"
            cle_shuff_opts = f"opts_shuff_ex1_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = ["Choisir..."] + opts_copie
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_shuff_opts].index(val_p) if val_p in st.session_state[cle_shuff_opts] else 0
            dict_reponses_quiz[q_data["id"]] = st.selectbox("", st.session_state[cle_shuff_opts], index=sel_idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse d'atelier de l'Exemple 1 (10 trous - 10 pts)")
        dict_trous = {}
        trous_data = [
            (f"1. La distance d de votre énoncé convertie en mètres vaut :", ["Choisir...", f"{d_m_user} m", f"{d_cm_user} m"], "ex1_t1_s5", f"{d_m_user} m"),
            (f"2. Pour effectuer cette conversion, on divise les centimètres par :", ["Choisir...", "100", "1000"], "ex1_t2_s5", "100"),
            (f"3. La valeur de la force F affectée à votre profil s'élève à :", ["Choisir...", f"{f_user} N", "150 N"], "ex1_t3_s5", f"{f_user} N"),
            (f"4. Le moment résultant de votre serrage est de :", ["Choisir...", f"{m_user} N.m", "45 N.m"], "ex1_t4_s5", f"{m_user} N.m"),
            (f"5. L'action mécanique exercée par l'opérateur est une force de :", ["Choisir...", "Contact", "Distance"], "ex1_t5_s5", "Contact"),
            (f"6. Le bras de levier forme un angle obligatoirement :", ["Choisir...", "Droit", "Aigu"], "ex1_t6_s5", "Droit"),
            (f"7. avec la droite d'action de la force appliquée sur le :", ["Choisir...", "Manche", "Pivot"], "ex1_t7_s5", "Manche"),
            (f"8. Le terme 'couple de serrage' désigne un effet de :", ["Choisir...", "Rotation", "Translation"], "ex1_t8_s5", "Rotation"),
            (f"9. En cas de dépassement des tolérances, il y a risque de :", ["Choisir...", "Rupture", "Glissement"], "ex1_t9_s5", "Rupture"),
            (f"10. du filetage mécanique, rendant l'assemblage non :", ["Choisir...", "Conforme", "Mobile"], "ex1_t10_s5", "Conforme")
        ]
        for phrase, opts, key, rep in trous_data:
            c_p, c_s = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_p: st.write(phrase)
            with c_s: dict_trous[key] = st.selectbox("", opts, key=key, disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous



def afficher_questions_applications_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "ordre_quiz4_applications" not in st.session_state:
        base_quiz4_applications = [
            {"id": "q4_1", "q": "Sur une grue de chantier, le contrepoids en béton sert principalement à :", "type": "menu", "options": ["Compenser le moment de la charge", "Augmenter la hauteur de la flèche", "Freiner la rotation de la cabine"], "rep": "Compenser le moment de la charge"},
            {"id": "q4_2", "q": "Si une grue soulève une charge trop lourde en bout de flèche, le risque majeur est :", "type": "menu", "options": ["Le basculement de la structure", "La rupture du câble uniquement", "L'arrêt du moteur électrique"], "rep": "Le basculement de la structure"},
            {"id": "q4_3", "q": "Pour serrer un écrou à une valeur de couple précise en atelier, on utilise :", "type": "menu", "options": ["Une clé dynamométrique", "Une clé plate standard", "Un dynamomètre à aiguille"], "rep": "Une clé dynamométrique"},
            {"id": "q4_4", "q": "Le terme 'couple de serrage' employé en mécanique industrielle est équivalent à :", "type": "menu", "options": ["Un moment de force", "Une intensité de force", "Une puissance thermique"], "rep": "Un moment de force"},
            {"id": "q4_5", "q": "Lorsqu'on éloigne une charge de la cabine d'une grue, son bras de levier :", "type": "menu", "options": ["Augmente", "Diminue", "Reste constant"], "rep": "Augmente"},
            {"id": "q4_6", "q": "Pour maintenir une grue en équilibre lorsque la charge s'éloigne, il faut :", "type": "menu", "options": ["Diminuer la masse de la charge", "Augmenter la masse de la charge", "Rapprocher le contrepoids"], "rep": "Diminuer la masse de la charge"},
            {"id": "q4_7", "q": "L'unité du couple de serrage indiquée sur les outils professionnels est le :", "type": "menu", "options": ["Newton-mètre", "Newton par mètre", "Kilogramme"], "rep": "Newton-mètre"},
            {"id": "q4_8", "q": "Un pont basculant pour camions repose sur le principe mécanique :", "type": "menu", "options": ["Du levier et des moments", "De la déformation élastique", "De la poussée d'Archimède"], "rep": "Du levier et des moments"},
            {"id": "q4_9", "q": "Si le manche d'une clé est trop court pour desserrer un écrou, un technicien peut :", "type": "menu", "options": ["Utiliser une rallonge de manche", "Appuyer plus près de l'écrou", "Réduire sa force musculaire"], "rep": "Utiliser une rallonge de manche"},
            {"id": "q4_10", "q": "Dans l'industrie, le non-respect du couple de serrage d'un boulon peut entraîner :", "type": "menu", "options": ["La rupture ou le desserrage de la pièce", "Une augmentation de la masse", "Une usure de l'axe de rotation"], "rep": "La rupture ou le desserrage de la pièce"}
        ]
        copie_base = list(base_quiz4_applications)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz4_applications = copie_base

    col_double_quiz_a4, col_double_trous_a4 = st.columns(2)

    with col_double_quiz_a4:
        st.markdown("##### Quiz sur les applications industrielles (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz4_applications, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"apps_cl_g_{q_data['id']}"
            
            cle_shuff_opts = f"opts_shuff_apps_{q_data['id']}"
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

    with col_double_trous_a4:
        st.markdown("##### Synthèse sur l'exploitation technique (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Une grue à tour maintient sa flèche horizontale en ajustant la position du")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Contrepoids", "Moteur", "Châssis"], key="apps_t1_s4", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. afin que le moment généré par les blocs de béton compense celui de la")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Charge", "Cabine", "Structure"], key="apps_t2_s4", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. suspendue à l'autre extrémité. En maintenance automobile, le contrôle du")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Serrage", "Niveau", "Mouvement"], key="apps_t3_s4", disabled=verrouille, label_visibility="collapsed")
        
        c47, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c47: st.write("4. des culasses ou des roues nécessite un outil de précision gradué en")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Newton-mètres", "Newtons", "Millimètres"], key="apps_t4_s4", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Cette clé spéciale intègre un système de déclenchement mécanique ou")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "Électronique", "Hydraulique", "Pneumatique"], key="apps_t5_s4", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. qui signale par un clic visuel ou sonore que la valeur requise du")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Moment", "Vecteur", "Poids"], key="apps_t6_s4", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. est atteinte. L'application d'un effort trop intense risque de déformer le")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Boulon", "Manche", "Pivot"], key="apps_t7_s4", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. et d'endommager définitivement le filetage. Les bras télescopiques utilisent la")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "Variation", "Stabilité", "Constante"], key="apps_t8_s4", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. de la distance pour modifier l'efficacité de la rotation sans changer la")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Force", "Masse", "Vitesse"], key="apps_t9_s4", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Ce principe de levier reste indispensable à la conception des machines de")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "Levage", "Usinage", "Soudage"], key="apps_t10_s4", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous

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
    st.divider()
    st.subheader("Validation de la section sur les forces")
    
    verrou_forces_1 = st.session_state.get("forces_verrouille_tab1", False)
    res_q1, res_t1 = afficher_questions_forces_dynamiques(verrouille=verrou_forces_1)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_forces1 = st.checkbox(
        "Je certifie avoir complété les questions de l'évaluation sur les forces.", 
        key="check_certif_forces1_official", 
        disabled=verrou_forces_1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ÉVALUATION DES FORCES", key="btn_export_forces1_official_net", use_container_width=True, disabled=verrou_forces_1):
        # Utilisation de la clé globale définie dans valider_saisie()
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_forces1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz1_forces" in st.session_state:
                for q_item in st.session_state.ordre_quiz1_forces:
                    reponse_eleve = st.session_state.get(f"forces_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

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
    
    col_sens_a, col_sens_b = st.columns(2)
    
    with col_sens_a:
        st.markdown("*   **Le sens positif (ou trigonométrique)** : Sens inverse des aiguilles d'une montre.")
        if os.path.exists("sens_positif.jpg"):
            st.image("sens_positif.jpg", caption="Représentation graphique du sens positif (anti-horaire)", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : sens_positif.jpg")

    with col_sens_b:
        st.markdown("*   **Le sens négatif (ou horaire)** : Sens des aiguilles d'une montre.")
        if os.path.exists("sens_negatif.jpg"):
            st.image("sens_negatif.jpg", caption="Représentation graphique du sens négatif (horaire)", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : sens_negatif.jpg")

    st.write("")
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

    # --- NOUVELLE SECTION : EXEMPLES DE LA VIE COURANTE ---
    st.subheader("4. Exemples d'objets en rotation dans la vie courante")
    st.write(
        "Voici des applications concrètes de solides en rotation ou recherchant l'équilibre des moments "
        "que vous rencontrez quotidiennement à la maison ou dans les ateliers :"
    )

    col_vie_1, col_vie_2 = st.columns(2)
    
    with col_vie_1:
        st.markdown("**Exemple A : La roue de vélo ou le manège**")
        st.write("L'axe métallique central reste fixe pendant que la structure externe tourne sous l'effet d'une force.")
        if os.path.exists("vie_courante_roue.jpg"):
            st.image("vie_courante_roue.jpg", caption="Roue en rotation autour de son moyeu central fixe", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : vie_courante_roue.jpg")

        st.write("")
        st.markdown("**Exemple B : La clé de serrage en atelier**")
        st.write("Plus le manche est long, plus l'effet de la force mécanique augmente pour faire pivoter le boulon.")
        if os.path.exists("vie_courante_cle.jpg"):
            st.image("vie_courante_cle.jpg", caption="Utilisation du bras de levier pour engendrer une rotation", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : vie_courante_cle.jpg")

    with col_vie_2:
        st.markdown("**Exemple C : La poignée de porte**")
        st.write("L'action de votre main à l'extrémité de la béquille crée le moment nécessaire pour actionner le pêne.")
        if os.path.exists("vie_courante_poignee.jpg"):
            st.image("vie_courante_poignee.jpg", caption="Pivotement de la poignée autour de son carré d'axe", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : vie_courante_poignee.jpg")

        st.write("")
        st.markdown("**Exemple D : La pédale de commande ou le pédalier**")
        st.write("L'effort musculaire vertical est transformé en un couple mécanique de rotation autour de l'axe de pédalier.")
        if os.path.exists("vie_courante_pedale.jpg"):
            st.image("vie_courante_pedale.jpg", caption="Transformation de l'effort linéaire en mouvement circulaire", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : vie_courante_pedale.jpg")
            
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

        # =============================================================================
        # LABORATOIRE AVANCÉ DYNAMIQUE MULTI-FORCES (À insérer sous la première simulation)
        # =============================================================================
    st.write("---")
    st.subheader("3. Laboratoire virtuel avancé : Systèmes multi-forces")
    st.write(
        "Dans la réalité industrielle, un objet en rotation peut être soumis à plusieurs forces simultanées "
        "de chaque côté de l'axe. Configurez votre système sur-mesure ci-dessous :"
    )

    col_cfg_g, col_cfg_d = st.columns(2)
    
    with col_cfg_g:
        nb_forces_g = st.number_input("Nombre de forces à GAUCHE", min_value=1, max_value=4, value=2, step=1, key="nb_f_g")
    with col_cfg_d:
        nb_forces_d = st.number_input("Nombre de forces à DROITE", min_value=1, max_value=4, value=2, step=1, key="nb_f_d")

    st.write("##### Saisie des caractéristiques des forces")
    col_tab_g, col_tab_d = st.columns(2)
    
    forces_g_list = []
    distances_g_list = []
    moments_g_list = []
    
    with col_tab_g:
        st.markdown("**Tableau des actions à GAUCHE**")
        for i in range(int(nb_forces_g)):
            c_f, c_d = st.columns(2)
            with c_f:
                f_val = st.number_input(f"Force G{i+1} (en N)", min_value=0.0, max_value=500.0, value=100.0 if i==0 else 50.0, step=10.0, key=f"f_g_{i}")
            with c_d:
                d_val = st.number_input(f"Distance G{i+1} (en m)", min_value=0.1, max_value=5.0, value=1.0 + i*0.5, step=0.1, key=f"d_g_{i}")
            m_val = round(f_val * d_val, 2)
            forces_g_list.append(f_val)
            distances_g_list.append(d_val)
            moments_g_list.append(m_val)

    forces_d_list = []
    distances_d_list = []
    moments_d_list = []

    with col_tab_d:
        st.markdown("**Tableau des actions à DROITE**")
        for j in range(int(nb_forces_d)):
            c_f, c_d = st.columns(2)
            with c_f:
                f_val = st.number_input(f"Force D{j+1} (en N)", min_value=0.0, max_value=500.0, value=150.0 if j==0 else 50.0, step=10.0, key=f"f_d_{j}")
            with c_d:
                d_val = st.number_input(f"Distance D{j+1} (en m)", min_value=0.1, max_value=5.0, value=0.8 + j*0.6, step=0.1, key=f"d_d_{j}")
            m_val = round(f_val * d_val, 2)
            forces_d_list.append(f_val)
            distances_d_list.append(d_val)
            moments_d_list.append(m_val)

    # Calculs des sommes des moments
    somme_moments_gauche = round(sum(moments_g_list), 2)
    somme_moments_droite = round(sum(moments_d_list), 2)

    st.write("##### Tableau récapitulatif et bilan des moments algébriques")
    
    # Affichage du tableau de synthèse dynamique pour la conclusion de l'élève
    col_res_g, col_res_d = st.columns(2)
    with col_res_g:
        st.info(f"Somme des moments faisant tourner à GAUCHE (+) : {somme_moments_gauche} N.m")
    with col_res_d:
        st.info(f"Somme des moments faisant tourner à DROITE (-) : {somme_moments_droite} N.m")

    col_visu_lbl, col_visu_graph = st.columns([0.4, 0.6])
    
    with col_visu_lbl:
        st.write("**Verdict de l'équilibre multi-forces :**")
        ecart_moments = abs(somme_moments_gauche - somme_moments_droite)
        
        if ecart_moments < 1.5:
            st.success("SYSTÈME EN PARFAIT ÉQUILIBRE ! La somme des moments est nulle (Somme M = 0). Le levier ne tourne pas.")
            verdict_texte = "PARFAIT ÉQUILIBRE"
            verdict_coulor = "green"
        elif somme_moments_gauche > somme_moments_droite:
            st.error(f"BASCULE À GAUCHE ! Le moment total à gauche est supérieur de {round(ecart_moments, 2)} N.m.")
            verdict_texte = "BASCULE A GAUCHE"
            verdict_coulor = "red"
        else:
            st.error(f"BASCULE À DROITE ! Le moment total à droite est supérieur de {round(ecart_moments, 2)} N.m.")
            verdict_texte = "BASCULE A DROITE"
            verdict_coulor = "red"

    with col_visu_graph:
        # Génération du graphique dynamique matplotlib pour le système multi-forces
        fig_multi, ax_multi = plt.subplots(figsize=(7, 4))
        
        # Dessin de la planche principale et du pivot central
        ax_multi.plot([-5.5, 5.5], [0, 0], color="brown", lw=6)
        ax_multi.plot([0, -0.3, 0.3, 0], [0, -0.5, -0.5, 0], color="black", lw=3)
        ax_multi.text(-0.3, -0.9, "Axe D", fontsize=10, weight='bold')

        # Tracé dynamique de toutes les forces de GAUCHE (Rouge)
        for idx, (f, d) in enumerate(zip(forces_g_list, distances_g_list)):
            ax_multi.annotate('', xy=(-d, -1.2), xytext=(-d, 0), arrowprops=dict(facecolor='red', width=2, headwidth=8))
            ax_multi.text(-d - 0.2, -1.5, f"G{idx+1}:{int(f)}N", color='red', fontsize=8, weight='bold')
            ax_multi.text(-d, 0.2, f"{d}m", color='red', fontsize=8)

        # Tracé dynamique de toutes les forces de DROITE (Vert)
        for idx, (f, d) in enumerate(zip(forces_d_list, distances_d_list)):
            ax_multi.annotate('', xy=(d, -1.2), xytext=(d, 0), arrowprops=dict(facecolor='green', width=2, headwidth=8))
            ax_multi.text(d - 0.2, -1.5, f"D{idx+1}:{int(f)}N", color='green', fontsize=8, weight='bold')
            ax_multi.text(d, 0.2, f"{d}m", color='green', fontsize=8)

        ax_multi.set_xlim(-6, 6)
        ax_multi.set_ylim(-2.2, 1)
        ax_multi.axis('off')
        ax_multi.title.set_text(verdict_texte)
        ax_multi.title.set_color(verdict_coulor)
        
        st.pyplot(fig_multi)
        
        # Exportation du schéma multi-forces personnalisé au format JPG
        nom_img_multi = preparer_nom_fichier("laboratoire_multiforces") + ".jpg"
        plt.savefig("temp_multi.jpg", format="jpg", dpi=150, bbox_inches='tight')
        with open("temp_multi.jpg", "rb") as file_multi:
            st.download_button(
                label="Télécharger le schéma du laboratoire avancé (JPG)",
                data=file_multi,
                file_name=nom_img_multi,
                mime="image/jpeg",
                key="btn_dl_multi")



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

        # Initialisation obligatoire de la variable avant la boucle
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

        # Remplissage des lignes du Quiz
        if "ordre_quiz3_moments" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz3_moments, 1):
                saisie = st.session_state.get(f"moments_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_moments3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # Suite du HTML et ouverture du second tableau
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

        # Remplissage des lignes du texte à trous
        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous3, attendus_trous3, cles_trous3), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_moments3 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # Fermeture finale du fichier HTML
        html_export_moments3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Affichage du bouton de téléchargement Streamlit
        nom_fichier_html3 = preparer_nom_fichier("rapport_moments") + ".html"
        st.download_button(
            label="Télécharger le fichier de rapport officiel de l'Atelier 3 (HTML)",
            data=html_export_moments3,
            file_name=nom_fichier_html3,
            mime="text/html",
            use_container_width=True
        )


with tab4:
    st.header("Applications en mécanique")
    
    st.subheader("1. Étude de cas A : L'équilibre des grues à tour")
    st.write(
        "Dans le secteur du bâtiment, les grues doivent manutentionner des charges lourdes à des distances "
        "variables. Pour éviter le basculement, la structure utilise un contrepoids en béton fixe ou mobile. "
        "L'équilibre de la flèche est régi par l'égalité des moments de part et d'autre du mât central."
    )
    
    col_app_1, col_app_2 = st.columns(2)
    with col_app_1:
        st.markdown("**Fonctionnement de la flèche et de la contre-flèche :**")
        st.write(
            "La charge suspendue crée une tendance à faire basculer la grue vers l'avant (moment positif). "
            "Le contrepoids situé sur la contre-flèche crée un moment opposé (moment négatif). "
            "Si la charge doit s'éloigner du mât, sa distance augmente : il faut impérativement réduire "
            "la masse maximale autorisée pour que la structure reste stable."
        )
    with col_app_2:
        if os.path.exists("application_grue.jpg"):
            st.image("application_grue.jpg", caption="Application du théorème des moments sur une grue de chantier", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : application_grue.jpg")

    st.divider()
    col_app_12, col_app_22 = st.columns(2)

    with col_app_12:
        st.markdown("**Fonctionnement de la flèche et de la contre-flèche :**")
        st.write("**La caricature humoristique : L'équilibre de la grue à tour**")
        
        # Bloc d'information bleu contenant l'intégralité du texte des 4 cases
        st.info(
            "**Case 1 : Le piège de la distance (Passé) :** Un jeune grutier veut déplacer une petite palette de briques, "
            "mais il l'envoie tout au bout de la flèche, très loin du mât central. À cause du bras de levier immense, "
            "la grue bascule complètement vers l'avant et ses fondations décollent du sol.\n\n"
            "**Case 2 : La réaction disproportionnée (Passé) :** Pour compenser, l'apprenti court à l'arrière sur la contre-flèche "
            "et y empile une montagne absurde de blocs de béton. Dès qu'il lâche les briques à l'avant, la grue bascule "
            "violemment dans l'autre sens et s'écrase vers l'arrière.\n\n"
            "**Case 3 : Le système D (La fausse bonne idée) :** Totalement dépassé, il décide d'attacher d'immenses cordes élastiques "
            "depuis le sommet du mât jusqu'aux camions et aux structures du chantier aux alentours. La grue ressemble à "
            "une toile d'araignée géante et tout le chantier se retrouve tordu.\n\n"
            "**Case 4 : La leçon de physique (Aujourd'hui) :** Un vieil ingénieur blasé arrive avec une règle et une calculatrice. "
            "Il ramène calmement la charge près du mât et ajuste la quantité exacte de contrepoids. La grue redevient "
            "parfaitement droite sous les yeux ébahis de l'apprenti."
        )

    with col_app_22:
        # Nom du fichier image généré juste au-dessus
        nom_image = "image_B2Vson.png"
        
        # Vérification de la présence du fichier (gère le fichier d'origine ou votre renommage)
        if os.path.exists(nom_image):
            st.image(nom_image, caption="L'équilibre de la grue à tour", use_container_width=True)
        elif os.path.exists("caricature_grue.jpg"):
            st.image("caricature_grue.jpg", caption="L'équilibre de la grue à tour", use_container_width=True)
        else:
            st.info(f"Emplacement pour l'image :caricature_grue.jpg")

    st.divider()
    st.subheader("2. Étude de cas B : Le contrôle du serrage industriel (Clé dynamométrique)")
    st.write(
        "En maintenance mécanique, l'assemblage de pièces maîtresses exige un effort de serrage parfaitement calibré. "
        "Un serrage insuffisant provoque des vibrations et un desserrage, tandis qu'un serrage excessif risque "
        "de casser le goujon ou de déformer les filetages."
    )
    
    col_app_3, col_app_4 = st.columns(2)
    with col_app_3:
        st.markdown("**Principe de la clé dynamométrique :**")
        st.write(
            "Cet outil permet d'appliquer un moment de force précis appelé couple de serrage. "
            "Grâce à un manche de longueur fixe connue (le bras de levier), le mécanisme interne "
            "mesure l'effort appliqué par l'opérateur et déclenche un signal mécanique ou électronique "
            "lorsque la valeur cible en Newton-mètres (N.m) est rigoureusement atteinte."
        )
    with col_app_4:
        if os.path.exists("application_cle.jpg"):
            st.image("application_cle.jpg", caption="Contrôle du couple de serrage à l'aide d'une clé graduée", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : application_cle.jpg")
            
    col_app_32, col_app_42 = st.columns(2)

    with col_app_32:
        st.markdown("**Le fonctionnement de la clé dynamométrique :**")
        st.write("**La caricature humoristique : Le serrage précis (ou pas !)**")
        
        st.info(
            "**Case 1 : L'ambition et la théorie (Passé) :** Notre ingénieur, plein d'entrain, rêve d'un serrage parfait à 150 N.m pour ce boulon colossal. Malheureusement, son outil standard s'avère bien trop court pour surmonter la résistance mécanique.\n\n"
            "**Case 2 : L'effort désespéré (Passé) :** Sans bras de levier suffisant, c'est l'impasse. Il s'épuise et donne tout ce qu'il a en grimpant sur un escabeau pour sauter sur une rallonge de fortune en tuyau, qui finit par plier sous son poids.\n\n"
            "**Case 3 : La solution de génie (Années 1950) :** Illumination ! Plus le bras est long, plus le moment est grand. Il décide d'improviser une clé gigantesque dotée d'un manche de 5 mètres de long pour minimiser son effort physique.\n\n"
            "**Case 4 : Le résultat précis (Aujourd'hui) :** Le couple cible est atteint de manière dévastatrice. Le bras de levier démesuré multiplie tellement sa force qu'il casse net le boulon en morceaux, sous le signal sonore ironique de l'outil."
        )
    with col_app_42:
        # Nom du fichier image généré précédemment pour ce cas précis
        nom_image_cle = "image_a3xqiX.png"
        
        # Vérification et affichage de la caricature graphique correspondante
        if os.path.exists(nom_image_cle):
            st.image(nom_image_cle, caption="Contrôle du couple de serrage à l'aide d'une clé graduée", use_container_width=True)
        elif os.path.exists("caricature_cle.jpg"):
            st.image("caricature_cle.jpg", caption="Contrôle du couple de serrage à l'aide d'une clé graduée", use_container_width=True)
        elif os.path.exists("application_cle.jpg"):
            st.image("application_cle.jpg", caption="Contrôle du couple de serrage à l'aide d'une clé graduée", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : application_cle.jpg")

    # --- LOGIQUE DE COUPLAGE ET VALIDATION DE L'ONGLET 4 ---
    st.divider()
    st.subheader("3. Évaluation sur les applications mécaniques")
    
    verrou_apps_4 = st.session_state.get("apps_verrouille_tab4", False)
    res_q4, res_t4 = afficher_questions_applications_dynamiques(verrouille=verrou_apps_4)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_apps4 = st.checkbox(
        "Je certifie avoir complété les questions de l'évaluation sur les applications.", 
        key="check_certif_apps4_official", 
        disabled=verrou_apps_4
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DES APPLICATIONS EN MÉCANIQUE", key="btn_export_apps4_official_net", use_container_width=True, disabled=verrou_apps_4):
        if not st.session_state.get("identifie", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_apps4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz4_applications" in st.session_state:
                for q_item in st.session_state.ordre_quiz4_applications:
                    reponse_eleve = st.session_state.get(f"apps_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            score_t4 = sum([
                st.session_state.get("apps_t1_s4") == "Contrepoids",
                st.session_state.get("apps_t2_s4") == "Charge",
                st.session_state.get("apps_t3_s4") == "Serrage",
                st.session_state.get("apps_t4_s4") == "Newton-mètres",
                st.session_state.get("apps_t5_s4") == "Électronique",
                st.session_state.get("apps_t6_s4") == "Moment",
                st.session_state.get("apps_t7_s4") == "Boulon",
                st.session_state.get("apps_t8_s4") == "Variation",
                st.session_state.get("apps_t9_s4") == "Force",
                st.session_state.get("apps_t10_s4") == "Levage"
            ])

            st.session_state.score_apps4_p1 = round(float(score_q4), 1)
            st.session_state.score_apps4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_apps4 = round(float(score_q4 + score_t4), 1)
            st.session_state.apps_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("apps_verrouille_tab4", False):
        scr1 = st.session_state.get("score_apps4_p1", 0.0)
        scr2 = st.session_state.get("score_apps4_p2", 0.0)
        tot_s = st.session_state.get("score_final_apps4", 0.0)

        timestamp_apps4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"SECTION APPLICATIONS SCELLÉE | Note de session : {tot_s:.1f} / 20")

        html_export_apps4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Applications mécaniques - {n_eleve}</title>
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
                <p>Évaluation : Applications industrielles et concrètes du théorème des moments</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_apps4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des notes générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Applications : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse technique : <strong>{scr2:.1f} / 10</strong><br>
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

        if "ordre_quiz4_applications" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz4_applications, 1):
                saisie = st.session_state.get(f"apps_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_apps4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_apps4 += """
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

        phrases_trous4 = [
            "1. Une grue à tour maintient sa flèche horizontale en ajustant la position du",
            "2. afin que le moment généré par les blocs de béton compense celui de la",
            "3. suspendue à l'autre extrémité. En maintenance automobile, le contrôle du",
            "4. des culasses ou des roues nécessite un outil de précision gradué en",
            "5. Cette clé spéciale intègre un système de déclenchement mécanique ou",
            "6. qui signale par un clic visuel ou sonore que la valeur requise du",
            "7. est atteinte. L'application d'un effort trop intense risque de déformer le",
            "8. et d'endommager définitivement le filetage. Les bras télescopiques utilisent la",
            "9. de la distance pour modifier l'efficacité de la rotation sans changer la",
            "10. Ce principe de levier reste indispensable à la conception des machines de"
        ]
        attendus_trous4 = ["Contrepoids", "Charge", "Serrage", "Newton-mètres", "Électronique", "Moment", "Boulon", "Variation", "Force", "Levage"]
        cles_trous4 = ["apps_t1_s4", "apps_t2_s4", "apps_t3_s4", "apps_t4_s4", "apps_t5_s4", "apps_t6_s4", "apps_t7_s4", "apps_t8_s4", "apps_t9_s4", "apps_t10_s4"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous4, attendus_trous4, cles_trous4), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_apps4 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_apps4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_html4 = preparer_nom_fichier("rapport_applications") + ".html"
        st.download_button(
            label="Télécharger le fichier de rapport officiel de l'Atelier 4 (HTML)",
            data=html_export_apps4,
            file_name=nom_fichier_html4,
            mime="text/html",
            use_container_width=True
        )


# =========================================================================
# CODE POUR L'ONGLET 5 : EXERCICES DE CALCUL NUMÉRIQUES ALÉATOIRES
# =========================================================================
with tab5:
    st.header("Exemple 1 : Étude d'un cas concret de serrage")
    
    col_ex1_txt, col_ex1_img = st.columns(2)
    
    with col_ex1_txt:
        if "ex1_force_aleatoire" not in st.session_state:
            import random
            st.session_state.ex1_force_aleatoire = random.randint(11, 25) * 10 # Entre 110 N et 250 N
            st.session_state.ex1_dist_aleatoire = random.randint(20, 50)     # Entre 20 cm et 50 cm

        f_ex1 = st.session_state.ex1_force_aleatoire
        d_cm_ex1 = st.session_state.ex1_dist_aleatoire
        d_m_attendu = round(d_cm_ex1 / 100, 2)
        moment_attendu = round(f_ex1 * d_m_attendu, 1)

        st.subheader("Énoncé de l'exercice")
        st.write(
            "Un opérateur utilise une clé de serrage pour fixer un boulon sur une structure industrielle. "
            "L'effort exercé à l'extrémité du manche de la clé est perpendiculaire à l'outil."
        )
        st.markdown(
            f"""
            **Données de l'étude personnalisées :**
            *   Intensité de la force appliquée : F = **{f_ex1} N**
            *   Longueur utile de la clé (bras de levier) : d = **{d_cm_ex1} cm**
            """
        )

    with col_ex1_img:
        st.subheader("Illustration de la situation")
        if os.path.exists("exemple_mecanique_1.jpg"):
            st.image("exemple_mecanique_1.jpg", caption="Schéma technique de l'application de la force sur la clé de serrage", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : exemple_mecanique_1.jpg")

    st.divider()
    st.subheader("Évaluation et exercices de l'Exemple 1")
    
    verrou_ex1 = st.session_state.get("ex1_verrouille_tab5", False)
    res_q_ex1, res_t_ex1 = afficher_questions_exemple1_dynamiques(verrouille=verrou_ex1)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ex1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Exemple 1.", 
        key="check_certif_ex1_official", 
        disabled=verrou_ex1
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'EXEMPLE 1", key="btn_export_ex1_official_net", use_container_width=True, disabled=verrou_ex1):
        if not st.session_state.get("identifie", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_ex1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 points)
            score_q1 = 0.0
            if "ordre_quiz_ex1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_ex1:
                    reponse_eleve = st.session_state.get(f"ex1_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction de la Synthèse d'atelier (10 points)
            score_t1 = sum([
                st.session_state.get("ex1_t1_s5") == f"{d_m_attendu} m",
                st.session_state.get("ex1_t2_s5") == "100",
                st.session_state.get("ex1_t3_s5") == f"{f_ex1} N",
                st.session_state.get("ex1_t4_s5") == f"{moment_attendu} N.m",
                st.session_state.get("ex1_t5_s5") == "Contact",
                st.session_state.get("ex1_t6_s5") == "Droit",
                st.session_state.get("ex1_t7_s5") == "Manche",
                st.session_state.get("ex1_t8_s5") == "Rotation",
                st.session_state.get("ex1_t9_s5") == "Rupture",
                st.session_state.get("ex1_t10_s5") == "Conforme"
            ])

            st.session_state.score_ex1_p1 = round(float(score_q1), 1)
            st.session_state.score_ex1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_ex1 = round(float(score_q1 + score_t1), 1)
            st.session_state.ex1_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("ex1_verrouille_tab5", False):
        scr1 = st.session_state.get("score_ex1_p1", 0.0)
        scr2 = st.session_state.get("score_ex1_p2", 0.0)
        tot_s = st.session_state.get("score_final_ex1", 0.0)

        timestamp_ex1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER EXEMPLE 1 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_ex1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Exemple 1 - {n_eleve}</title>
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
                <p>Exemple 1 : Étude d'un cas concret de serrage mécanique</p>
                <p>Énoncé de session : Force = {f_ex1} N | Distance initiale = {d_cm_ex1} cm</p>
                <p>Valeurs attendues calculées : Bras de levier = {d_m_attendu} m | Moment cible = {moment_attendu} N.m</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_ex1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Technique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse d'atelier : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Exemple 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction détaillée du Quiz</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_ex1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_ex1, 1):
                saisie = st.session_state.get(f"ex1_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ex1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ex1 += f"""
                </tbody>
            </table>

            <div class="sub-title">Correction détaillée des trous de synthèse</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_ex1 = [
            "1. La distance d de votre énoncé convertie en mètres vaut :",
            "2. Pour effectuer cette conversion, on divise les centimètres par :",
            "3. La valeur de la force F affectée à votre profil s'élève à :",
            "4. Le moment résultant de votre calcul de serrage personnalisé vaut :",
            "5. L'action mécanique exercée par l'opérateur est une force de :",
            "6. Le bras de levier forme un angle obligatoirement :",
            "7. avec la droite d'action de la force appliquée sur le :",
            "8. Le terme 'couple de serrage' désigne un effet de :",
            "9. En cas de dépassement des tolérances, il y a risque de :",
            "10. du filetage mécanique, rendant l'assemblage final non :"
        ]
        attendus_trous_ex1 = [f"{d_m_attendu} m", "100", f"{f_ex1} N", f"{moment_attendu} N.m", "Contact", "Droit", "Manche", "Rotation", "Rupture", "Conforme"]
        cles_trous_ex1 = ["ex1_t1_s5", "ex1_t2_s5", "ex1_t3_s5", "ex1_t4_s5", "ex1_t5_s5", "ex1_t6_s5", "ex1_t7_s5", "ex1_t8_s5", "ex1_t9_s5", "ex1_t10_s5"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous_ex1, attendus_trous_ex1, cles_trous_ex1), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_ex1 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ex1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_ex1 = preparer_nom_fichier("rapport_exemple1") + ".html"
        st.download_button(label="Télécharger le fichier de rapport officiel Exemple 1 (HTML)", data=html_export_ex1, file_name=nom_fichier_ex1, mime="text/html", use_container_width=True)

with tab6:
    st.header("Exemple 2 : Équilibre d'un système de levage (Grue)")
    
    col_ex2_txt, col_ex2_img = st.columns(2)
    
    with col_ex2_txt:
        if "ex2_force_aleatoire" not in st.session_state:
            import random
            st.session_state.ex2_f1_aleatoire = random.randint(10, 18) * 1000  # Entre 10 000 N et 18 000 N
            st.session_state.ex2_d1_aleatoire = random.randint(10, 20)         # Entre 10 m et 20 m
            st.session_state.ex2_f2_aleatoire = random.randint(30, 45) * 1000  # Entre 30 000 N et 45 000 N

        f1_ex2 = st.session_state.ex2_f1_aleatoire
        d1_ex2 = st.session_state.ex2_d1_aleatoire
        f2_ex2 = st.session_state.ex2_f2_aleatoire
        
        # Calcul automatique de la distance cible pour l'équilibre (F1 x d1) / F2
        d2_attendu_ex2 = round((f1_ex2 * d1_ex2) / f2_ex2, 2)

        st.subheader("Énoncé de l'exercice")
        st.write(
            "On étudie la flèche d'une grue de chantier en équilibre de rotation autour de son pylône central. "
            "La charge suspendue à gauche crée une tendance à la rotation qui doit être compensée par le contrepoids situé à droite."
        )
        st.markdown(
            f"""
            **Données du problème personnalisées :**
            *   Action de la charge à gauche : F1 = **{f1_ex2:,} N** située à d1 = **{d1_ex2} m** de l'axe.
            *   Action du contrepoids à droite : F2 = **{f2_ex2:,} N**.
            """
        )

    with col_ex2_img:
        st.subheader("Illustration de la situation")
        if os.path.exists("exemple_mecanique_2.jpg"):
            st.image("exemple_mecanique_2.jpg", caption="Modélisation des forces appliquées sur la flèche de la grue", use_container_width=True)
        else:
            st.info("Emplacement pour l'image : exemple_mecanique_2.jpg")

    st.divider()
    st.subheader("Évaluation et exercices de l'Exemple 2")
    
    verrou_ex2 = st.session_state.get("ex2_verrouille_tab6", False)
    res_q_ex2, res_t_ex2 = afficher_questions_exemple2_dynamiques(verrouille=verrou_ex2)

    st.write("---")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ex2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Exemple 2.", 
        key="check_certif_ex2_official", 
        disabled=verrou_ex2
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'EXEMPLE 2", key="btn_export_ex2_official_net", use_container_width=True, disabled=verrou_ex2):
        if not st.session_state.get("identifie", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_ex2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 points)
            score_q2 = 0.0
            if "ordre_quiz_ex2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_ex2:
                    reponse_eleve = st.session_state.get(f"ex2_cl_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction de la Synthèse mécanique (10 points)
            score_t2 = sum([
                st.session_state.get("ex2_t1_s6") == f"{m1_user} N.m",
                st.session_state.get("ex2_t2_s6") == f"{m1_user} N.m",
                st.session_state.get("ex2_t3_s6") == f"{d2_user_attendu} m",
                st.session_state.get("ex2_t4_s6") == "Moments",
                st.session_state.get("ex2_t5_s6") == "Delta",
                st.session_state.get("ex2_t6_s6") == f"{f2_user} N",
                st.session_state.get("ex2_t7_s6") == f"{d1_user} m",
                st.session_state.get("ex2_t8_s6") == "Opposés",
                st.session_state.get("ex2_t9_s6") == "Diminuer",
                st.session_state.get("ex2_t10_s6") == "Levage"
            ])

            st.session_state.score_ex2_p1 = round(float(score_q2), 1)
            st.session_state.score_ex2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_ex2 = round(float(score_q2 + score_t2), 1)
            st.session_state.ex2_verrouille_tab6 = True
            st.rerun()

    if st.session_state.get("ex2_verrouille_tab6", False):
        scr1 = st.session_state.get("score_ex2_p1", 0.0)
        scr2 = st.session_state.get("score_ex2_p2", 0.0)
        tot_s = st.session_state.get("score_final_ex2", 0.0)

        timestamp_ex2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER EXEMPLE 2 SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_ex2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Exemple 2 - {n_eleve}</title>
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
                <p>Exemple 2 : Étude de l'équilibre d'une grue de levage</p>
                <p>Énoncé de session : F1 = {f1_user} N | d1 = {d1_user} m | F2 = {f2_user} N</p>
                <p>Valeurs attendues calculées : Moment gauche = {m1_user} N.m | Position d'équilibre d2 = {d2_user_attendu} m</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_ex2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                &bull; Note obtenue au Quiz Technique : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse d'atelier : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Exemple 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">Correction détaillée du Quiz</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_ex2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_ex2, 1):
                saisie = st.session_state.get(f"ex2_cl_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ex2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ex2 += f"""
                </tbody>
            </table>

            <div class="sub-title">Correction détaillée des trous de synthèse</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_ex2 = [
            "1. Le moment calculé à gauche pour votre charge F1 s'élève à :",
            "2. À l'équilibre, le moment à droite créé par F2 doit valoir :",
            "3. La distance théorique d2 calculée pour votre contrepoids vaut :",
            "4. L'équilibre de la flèche est régi par le théorème des :",
            "5. Le mât central de la structure matérialise l'axe noté :",
            "6. L'intensité de l'action mécanique du contrepoids F2 est de :",
            "7. La distance d1 reliant l'axe à votre charge mesure :",
            "8. Les deux actions mécaniques s'exerzent dans des sens :",
            "9. Si le contrepoids se rapproche du centre, son moment va :",
            "10. Cette loi garantit la sécurité lors des opérations de :"
        ]
        attendus_trous_ex2 = [f"{m1_user} N.m", f"{m1_user} N.m", f"{d2_user_attendu} m", "Moments", "Delta", f"{f2_user} N", f"{d1_user} m", "Opposés", "Diminuer", "Levage"]
        cles_trous_ex2 = ["ex2_t1_s6", "ex2_t2_s6", "ex2_t3_s6", "ex2_t4_s6", "ex2_t5_s6", "ex2_t6_s6", "ex2_t7_s6", "ex2_t8_s6", "ex2_t9_s6", "ex2_t10_s6"]

        for idx, (phrase, attendu, cle) in enumerate(zip(phrases_trous_ex2, attendus_trous_ex2, cles_trous_ex2), 1):
            saisie_t = st.session_state.get(cle, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_ex2 += f"<tr><td>{idx}</td><td>{phrase} ...</td><td>{saisie_t}</td><td>{attendu}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ex2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        nom_fichier_ex2 = preparer_nom_fichier("rapport_exemple2") + ".html"
        st.download_button(label="Télécharger le fichier de rapport officiel Exemple 2 (HTML)", data=html_export_ex2, file_name=nom_fichier_ex2, mime="text/html", use_container_width=True)

