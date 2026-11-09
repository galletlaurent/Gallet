# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Réflexion ",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# Vos importations d'origine propres et saines se placent juste en dessous
from datetime import datetime
from itertools import combinations, product
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
st.title("Application Réflexion")
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
    "Loi de la Réfraction",
    "Double réfraction",
    "Fibre optique et réflexion totale",
    "Application le domaine de la maintenance",
    "Application dans le domaine les travaux publics",
    "Application dans le domaine du transport routier",
    "Application dans le domaine dgéomètre topographe"
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



def afficher_questions_optique7(verrouille=False):
    col_double_quiz_opt7, col_double_trous_opt7 = st.columns(2)

    # Récupération du cas routier actif généré dans l'onglet tab7
    cas_actif = st.session_state.get("app_routiere_choisie", "catadioptre")

    # =========================================================================
    # COLONNE GAUCHE : QUIZ SÉLECTIONNÉ SELON LE CAS (10 QUESTIONS)
    # =========================================================================
    with col_double_quiz_opt7:
        st.markdown("##### Quiz d'application routiere (10 questions) - Optique 7 (10 pts)")
        
        # Initialisation unique de l'ordre des questions pour le cas actif
        cle_session_ordre = f"ordre_questions_opt7_{cas_actif}"
        if cle_session_ordre not in st.session_state:
            if cas_actif == "catadioptre":
                base_questions = [
                    ("c1", "Un catadioptre sert a renvoyer les rayons lumineux de facon :"),
                    ("c2", "La forme geometrique interne utilisee dans un catadioptre est un :"),
                    ("c3", "Les facettes arriere du catadioptre forment entre elles un angle de :"),
                    ("c4", "Le retour de la lumiere s'effectue sans miroir grace au phenomene de :"),
                    ("c5", "Apres deux reflexions successives a 90 degres, la deviation totale vaut :"),
                    ("c6", "Pour que le dispositif fonctionne, l'angle d'impact sur la facette doit etre :"),
                    ("c7", "Le grand avantage du catadioptre par rapport a une lampe classique est qu'il est :"),
                    ("c8", "Dans le repere d'un prisme droit, les rayons incidents et emergents sont :"),
                    ("c9", "Si le materiau du catadioptre possede un indice trop faible, la lumiere va :"),
                    ("c10", "Sur la route, les catadioptres équipent obligatoirement l'arriere des véhicules en :")
                ]
            elif cas_actif == "mirage":
                base_questions = [
                    ("m1", "Le mirage routier donne l'illusion visuelle de la présence d'une :"),
                    ("m2", "En ete, la forte chaleur emise par le bitume rend l'air en surface tres :"),
                    ("m3", "Cet air fortement chauffe possede une densite plus :"),
                    ("m4", "L'indice de refraction de la couche d'air au ras du sol devient donc plus :"),
                    ("m5", "Le gradient d'indice genere des couches d'air qui font courber la trajectoire en :"),
                    ("m6", "La reflexion totale progressive se produit car l'angle d'incidence finit par dépasser l' :"),
                    ("m7", "Les rayons lumineux qui subissent cette courbe proviennent initialement du :"),
                    ("m8", "Puisque l'indice varie continuellement avec l'altitude, la trajectoire finale est :"),
                    ("m9", "L'oeil du conducteur prolonge la trajectoire rectilignement et voit une image :"),
                    ("m10", "Ce phenomene montre que la lumiere ne se propage en ligne droite que si le milieu est :")
                ]
            elif cas_actif == "capteur_pluie":
                base_questions = [
                    ("p1", "Le capteur de pluie automatique d'une automobile est generalement place derriere le :"),
                    ("p2", "La source lumineuse utilisee par l'emetteur est une LED fonctionnant en :"),
                    ("p3", "Lorsque le pare-brise est sec, le faisceau lumineux subit sur la face externe une :"),
                    ("p4", "L'angle d'injection initial de la LED dans le verre est calcule pour etre :"),
                    ("p5", "Dans des conditions seches, la quantite de lumiere renvoyee au recepteur vaut environ :"),
                    ("p6", "L'indice de refraction de l'eau (n = 1.33) est superieur a celui de l' :"),
                    ("p7", "L'arrivee d'eau sur le pare-brise modifie la valeur de l'angle :"),
                    ("p8", "Lorsque la condition aux limites change a cause de la pluie, la reflexion totale est :"),
                    ("p9", "Une fraction importante de l'intensite lumineuse infrarouge va alors :"),
                    ("p10", "La baisse de signal electrique mesuree par la photodiode declenche l'action des :")
                ]
            else: # panneau_signalisation
                base_questions = [
                    ("s1", "Le revetement brillant des panneaux de signalisation routiere modernes est un :"),
                    ("s2", "Ce film plastique technique renferme une multitude de structures nommees :"),
                    ("s3", "Contrairement a un miroir classique, le panneau de signalisation renvoie le flux vers :"),
                    ("s4", "Cette capacite particuliere a renvoyer la lumiere vers sa source s'appelle la :"),
                    ("s5", "A l'interieur d'un microprisme, les rayons subissent une serie de reflexions :"),
                    ("s6", "La surface du panneau semble s'illuminer fortement des que la voiture allume ses :"),
                    ("s7", "La directivite du faisceau evite de disperser inutilement l'energie vers le :"),
                    ("s8", "La condition de guidage impose que l'indice du plastique soit superieur a celui de l' :"),
                    ("s9", "Les facettes microscopiques arriere agissent comme des miroirs parfaits grace a l' :"),
                    ("s10", "Pour l'automobiliste de nuit, ce systeme passif apporte un gain majeur en termes de :")
                ]
            import random
            random.shuffle(base_questions)
            st.session_state[cle_session_ordre] = base_questions

        dict_quiz_opt7 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state[cle_session_ordre], 1):
            cle_qo7 = f"col_g_quiz_opt7_{cas_actif}_{q_id}"
            cle_opts_unique = f"opts_opt7_shuffled_{cas_actif}_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if cas_actif == "catadioptre":
                    if q_id == "c1": copie_opts = ["Parallèle à l'axe incident", "Perpendiculaire à la route", "Diffuse dans toutes les directions", "Divergente vers le fossé"]
                    elif q_id == "c2": copie_opts = ["Coin de cube (angle droit)", "Cylindre concave", "Disque convexe plan", "Prisme dispersif triangulaire"]
                    elif q_id == "c3": copie_opts = ["90°", "45°", "60°", "180°"]
                    elif q_id == "c4": copie_opts = ["Réflexion totale interne", "Réfraction limite", "Dispersion chromatique", "Interférence destructive"]
                    elif q_id == "c5": copie_opts = ["180° (demi-tour complet)", "90° (quart de tour)", "0° (aucune déviation)", "360° (tour complet)"]
                    elif q_id == "c6": copie_opts = ["Supérieur à l'angle critique", "Inférieur à l'angle critique", "Parfaitement nul", "Égal à 30°"]
                    elif q_id == "c7": copie_opts = ["Passif (sans consommation électrique)", "Actif à batterie", "Fluorescent à rayons UV", "Alimenté par l'alternateur"]
                    elif q_id == "c8": copie_opts = ["Parallèles", "Perpendiculaires", "Sécants à 45°", "Inclinés à 60°"]
                    elif q_id == "c9": copie_opts = ["S'échapper par réfraction", "Être absorbée à 100%", "Accélérer sa course", "Changer de longueur d'onde"]
                    elif q_id == "c10": copie_opts = ["Rouge", "Blanc", "Jaune", "Bleu"]
                elif cas_actif == "mirage":
                    if q_id == "m1": copie_opts = ["Flaque d'eau", "Plaque de verglas", "Ombre géante", "Brumisation dense"]
                    elif q_id == "m2": copie_opts = ["Chaud", "Froid", "Humide", "Saturé en ozone"]
                    elif q_id == "m3": copie_opts = ["Faible", "Élevée", "Infinie", "Stable"]
                    elif q_id == "m4": copie_opts = ["Faible", "Élevé", "Nul", "Égal à celui du verre"]
                    elif q_id == "m5": copie_opts = ["U inversé (courbe montante)", "Ligne droite oblique", "Z (zig-zag brisé)", "Spirale descendante"]
                    elif q_id == "m6": copie_opts = ["Angle critique (limite)", "Angle droit", "Angle nul", "Angle d'incidence normal"]
                    elif q_id == "m7": copie_opts = ["Ciel", "Sol", "Tableau de bord", "Phares de la voiture"]
                    elif q_id == "m8": copie_opts = ["Curviligne (courbe)", "Rectiligne (droite)", "Brisée en facettes", "Ondulatoire sinusoïdale"]
                    elif q_id == "m9": copie_opts = ["Inversée (reflétée)", "Droite et rétrécie", "Floue et décolorée", "Totalement invisible"]
                    elif q_id == "m10": copie_opts = ["Homogène", "Hétérogène", "Opaque", "Conducteur"]
                elif cas_actif == "capteur_pluie":
                    if q_id == "p1": copie_opts = ["Rétroviseur central", "Pare-chocs avant", "Compteur de vitesse", "Gicleur de lave-glace"]
                    elif q_id == "p2": copie_opts = ["Infrarouge (invisible)", "Ultraviolet", "Laser vert puissant", "Lumière blanche pulsée"]
                    elif q_id == "p3": copie_opts = ["Réflexion totale interne", "Réfraction vers l'extérieur", "Absorption calorifique", "Dispersion spectrale"]
                    elif q_id == "p4": copie_opts = ["Supérieur à l'angle critique", "Inférieur à l'angle critique", "Nul (incidence normale)", "Égal à 90°"]
                    elif q_id == "p5": copie_opts = ["100% (intensité maximale)", "50% (intensité moitié)", "0% (signal nul)", "25% seulement"]
                    elif q_id == "p6": copie_opts = ["Air (n = 1.00)", "Verre (n = 1.50)", "Plexiglas (n = 1.49)", "Diamant (n = 2.42)"]
                    elif q_id == "p7": copie_opts = ["Critique (limite)", "De Brewster", "D'injection", "De émergence"]
                    elif q_id == "p8": copie_opts = ["Brisée (rompue)", "Amplifiée", "Stabilisée", "Inversée"]
                    elif q_id == "p9": copie_opts = ["S'échapper dans la goutte", "Retourner vers la LED", "Se transformer en chaleur", "Accélérer dans le verre"]
                    elif q_id == "p10": copie_opts = ["Essuie-glaces", "Phares directionnels", "Freins d'urgence", "Feux de détresse"]
                else: # panneau_signalisation
                    if q_id == "s1": copie_opts = ["Film plastique technique", "Miroir d'argent classique", "Vernis fluorescent", "Plaque métallique polie"]
                    elif q_id == "s2": copie_opts = ["Microprismes transparents", "Lentilles concaves", "Fibres optiques parallèles", "Fils de carbone"]
                    elif q_id == "s3": copie_opts = ["La voiture d'origine (la source)", "Le ciel uniquement", "Le bas-côté de la chaussée", "Les nuages en hauteur"]
                    elif q_id == "s4": copie_opts = ["Rétroréflexion", "Réfraction totale", "Dispersion diffuse", "Focalisation optique"]
                    elif q_id == "s5": copie_opts = ["Totales internes", "Partielles externes", "Réfractées rasantes", "Absorbantes sélectives"]
                    elif q_id == "s6": copie_opts = ["Phares", "Clignotants", "Feux de stop", "Plafonniers"]
                    elif q_id == "s7": copie_opts = ["Ciel ou environnement", "Sol immédiat", "Moteur", "Rétroviseur"]
                    elif q_id == "s8": copie_opts = ["Air", "Verre", "Métal", "Silicone lourd"]
                    elif q_id == "s9": copie_opts = ["Angle limite dépassé", "Dépôt d'argenture", "Peinture blanche", "Effet laser de champ"]
                    elif q_id == "s10": copie_opts = ["Sécurité routière", "Vitesse de conduite", "Consommation de carburant", "Confort des sièges"]
                
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts

            val_p = st.session_state.get(cle_qo7, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0

            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_opt7[f"{q_id}_opt7"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qo7, disabled=verrouille, label_visibility="collapsed")

    # =========================================================================
    # COLONNE DROITE : SYNTHÈSE DE COURS À TROUS VARIANT SELON LE CAS (4 OPTIONS)
    # =========================================================================
    with col_double_trous_opt7:
        st.markdown("##### Synthese de cours (Texte a trous) - Optique 7 (10 pts)")

        if cas_actif == "catadioptre":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le catadioptre routier utilise un bloc plastique constitue de petits")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Prismes", "Miroirs", "Fils", "Lentilles"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. tailles en angle droit. Le faisceau lumineux des phares y subit une")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Réflexion", "Réfraction", "Dispersion", "Absorption"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. qui est qualifiée de totale car toute l'intensité est renvoyée dans le milieu")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Initial", "Extérieur", "Métallique", "Opaque"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. sans aucune perte. Les rebonds successifs dévient le rayon d'un angle de")
            with ct8: t4 = st.selectbox("", ["Choisir...", "90°", "45°", "180°", "0°"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. sur chaque face interne. Le faisceau émergeant repart de facon")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Parallèle", "Inclinée", "Perpendiculaire", "Diffuse"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. par rapport à l'axe d'entrée. Ce retour rectiligne cible directement le")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Conducteur", "Piéton", "Nuage", "Soleil"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. de l'automobile. Ce système fonctionne la nuit de manière entièrement")
            with ct14: t7 = st.selectbox("", ["Choisir...", "Passive", "Active", "Électrique", "Thermique"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. sans consommer de batterie. Pour être visible, l'indice du plastique doit être")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Supérieur", "Inférieur", "Égal", "Nul"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. à l'indice extérieur de l'")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Air", "Verre", "Eau", "Goudron"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. afin que la condition limite de Snell-Descartes soit toujours vérifiée pour la sécurité")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Routière", "Aérienne", "Maritime", "Ferroviaire"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        elif cas_actif == "mirage":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le mirage routier apparaît en été lorsque la forte chaleur surchauffe le")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Bitume", "Ciel", "Pneu", "Pare-brise"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. de la chaussée. Cela diminue localement la densité et l'indice de l'")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Air", "Sol", "Goudron", "Verre"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. au ras du sol. L'indice de réfraction de cette zone devient très")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Faible", "Élevé", "Infini", "Stable"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. par rapport à l'air frais plus haut. Les rayons lumineux descendants du")
            with ct8: t4 = st.selectbox("", ["Choisir...", "Ciel", "Moteur", "Phares", "Tableau"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. traversent un milieu d'indice continuellement décroissant. La trajectoire est")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Curviligne", "Rectiligne", "Brisée", "Ondulée"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. car l'angle d'incidence augmente à chaque couche d'air jusqu'à dépasser l'angle")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Critique", "Droit", "Nul", "Plat"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. On observe alors une réflexion totale progressive qui fait remonter le rayon vers l'")
            with ct14: t7 = st.selectbox("", ["Choisir...", "Oeil", "Bitume", "Feu", "Brouillard"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. de l'automobiliste. Le cerveau prolonge la direction finale et interprète une image")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Inversée", "Droite", "Rétrécie", "Invisible"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. de l'azur lointain sur l'asphalte, provoquant la spectaculaire")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Illusion", "Ombre", "Teinte", "Vapeur"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. d'une fausse flaque d'eau miroitante sur une route totalement")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Sèche", "Mouillée", "Inondée", "Glacée"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        elif cas_actif == "capteur_pluie":
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. Le capteur automatique d'essuyage est fixé directement contre le")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Pare-brise", "Moteur", "Pneu", "Phare"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. Une source émettrice produit un rayon invisible de nature")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Infrarouge", "Ultraviolete", "Laser", "Visible"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. Ce faisceau est injecté à l'intérieur de l'épaisseur du")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Verre", "Plastique", "Silicone", "Quartz"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. Tant que la surface extérieure reste parfaitement sèche, le contact avec l'")
            with ct8: t4 = st.selectbox("", ["Choisir...", "Air", "Eau", "Métal", "Givre"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. d'indice n = 1.00 provoque au niveau du dioptre une réflexion")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Totale", "Partielle", "Diffuse", "Nulle"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. interne. L'intégralité de l'énergie lumineuse est guidée vers le")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Récepteur", "Générateur", "Prisme", "Miroir"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. Mais lorsque des gouttes d'eau se déposent, l'indice externe passe à")
            with ct14: t7 = st.selectbox("", ["Choisir...", "1.33", "1.00", "1.50", "2.42"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. Cette élévation d'indice à l'interface modifie l'angle limite : la condition est")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Brisée", "Rendue stable", "Inversée", "Amplifiée"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. Une partie de la lumière s'échappe à l'extérieur. La photodiode mesure une forte")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Baisse", "Hausse", "Stabilité", "Dispersion"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. d'intensité, ce qui commande l'enclenchement instantané des")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Essuie-glaces", "Freins", "Phares", "Clignotants"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        else: # panneau_signalisation
            ct1, ct2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct1: st.write("1. La rétroréflexion nocturne des panneaux utilise un film plastique à")
            with ct2: t1 = st.selectbox("", ["Choisir...", "Microprismes", "Miroirs", "Lentilles", "Fils"], key="opt7_t1", disabled=verrouille, label_visibility="collapsed")

            ct3, ct4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct3: st.write("2. Le faisceau lumineux provient directement des projecteurs de")
            with ct4: t2 = st.selectbox("", ["Choisir...", "Phares", "Clignotants", "Feux de stop", "Plafonniers"], key="opt7_t2", disabled=verrouille, label_visibility="collapsed")

            ct5, ct6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct5: st.write("3. de la voiture. La lumière pénètre dans le polymère rigide de nature")
            with ct6: t3 = st.selectbox("", ["Choisir...", "Transparente", "Opaque", "Réfléchissante", "Métallique"], key="opt7_t3", disabled=verrouille, label_visibility="collapsed")

            ct7, ct8 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct7: st.write("4. Elle rencontre les facettes microscopiques arrières de chaque prisme droit")
            with ct8: t4 = st.selectbox("", ["Choisir...", "D'angle droit", "Arrondies", "Concaves", "Polies"], key="opt7_t4", disabled=verrouille, label_visibility="collapsed")

            ct9, ct10 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct9: st.write("5. Le guidage interne parfait de l'intensité s'effectue par réflexion")
            with ct10: t5 = st.selectbox("", ["Choisir...", "Totale", "Partielle", "Diffuse", "Réfractée"], key="opt7_t5", disabled=verrouille, label_visibility="collapsed")

            ct11, ct12 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct11: st.write("6. car la valeur d'incidence dépasse l'angle critique de l'interface avec l'")
            with ct12: t6 = st.selectbox("", ["Choisir...", "Air", "Verre", "Métal", "Eau"], key="opt7_t6", disabled=verrouille, label_visibility="collapsed")

            ct13, ct14 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct13: st.write("7. Mais lorsque des gouttes d'eau se déposent, l'indice externe passe à")
            with ct14: t7 = st.selectbox("", ["Choisir...", "1.33", "1.00", "1.50", "2.42"], key="opt7_t7", disabled=verrouille, label_visibility="collapsed")

            ct15, ct16 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct15: st.write("8. Les rayons concentrés retournent vers le conducteur au lieu d'être")
            with ct16: t8 = st.selectbox("", ["Choisir...", "Dispersés", "Absorbés", "Accélérés", "Filtrés"], key="opt7_t8", disabled=verrouille, label_visibility="collapsed")

            ct17, ct18 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct17: st.write("9. dans l'espace ou vers le ciel. La surface du panneau semble posséder une forte")
            with ct18: t9 = st.selectbox("", ["Choisir...", "Luminosité", "Chaleur", "Transparence", "Opacité"], key="opt7_t9", disabled=verrouille, label_visibility="collapsed")

            ct19, ct20 = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with ct19: st.write("10. apportant une aide à la visibilité indispensable pour assurer la sécurité")
            with ct20: t10 = st.selectbox("", ["Choisir...", "Routière", "Aérienne", "Maritime", "Industrielle"], key="opt7_t10", disabled=verrouille, label_visibility="collapsed")

        # Ligne de conclusion invariable commune aux 4 structures conditionnelles
        ct_fin1, ct_fin2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with ct_fin1: st.write("Ces diverses applications routieres mettent en evidence la maitrise des phenomenes optiques pour la securite.")

        dict_trous_opt7 = {
            "t1_opt7": t1, "t2_opt7": t2, "t3_opt7": t3, "t4_opt7": t4, "t5_opt7": t5,
            "t6_opt7": t6, "t7_opt7": t7, "t8_opt7": t8, "t9_opt7": t9, "t10_opt7": t10
        }

    return dict_quiz_opt7, dict_trous_opt7



if "lampes_data" not in st.session_state:
    st.session_state.lampes_data = {
        "Lumière du Soleil": {
            "type": "continu",
            "couleur_source": "#FFFDE7",
            "descr": "SPECTRE CONTINU (Étoile de type G2V avec raies de Fraunhofer)",
            "raies": [
                (400.0, "#7C3AED", 0.30),
                (445.0, "#2563EB", 0.50),
                (490.0, "#06B6D4", 0.70),
                (550.0, "#22C55E", 0.95),
                (590.0, "#EAB308", 0.90),
                (640.0, "#F97316", 0.75),
                (700.0, "#EF4444", 0.50),
                (760.0, "#450a0a", 0.30),
                (850.0, "#450a0a", 0.15),
            ],
        },
        "Lampe Halogène": {
            "type": "continu_chaude",
            "couleur_source": "#FFE082",
            "descr": "SPECTRE CONTINU (Filament de tungstène sous enveloppe quartz)",
            "raies": [
                (420.0, "#4F46E5", 0.15),
                (460.0, "#3B82F6", 0.30),
                (510.0, "#10B981", 0.45),
                (560.0, "#84CC16", 0.65),
                (600.0, "#F97316", 0.85),
                (650.0, "#EF4444", 0.95),
                (750.0, "#450a0a", 0.95),
                (850.0, "#450a0a", 0.99),
            ],
        },
        "Lampe à Incandescence Standard": {
            "type": "continu_chaude",
            "couleur_source": "#FFD54F",
            "descr": "SPECTRE CONTINU THERMIQUE FILAMENT STANDARD",
            "raies": [
                (430.0, "#4338CA", 0.10),
                (470.0, "#1D4ED8", 0.22),
                (520.0, "#047857", 0.40),
                (570.0, "#A3E635", 0.60),
                (610.0, "#EA580C", 0.80),
                (660.0, "#DC2626", 0.90),
                (740.0, "#450a0a", 0.95),
                (840.0, "#450a0a", 0.96),
            ],
        },
        "Corps Noir Élevé (5000K)": {
            "type": "continu",
            "couleur_source": "#F8FAFC",
            "descr": "SPECTRE CONTINU THÉORIQUE ÉQUILIBRE PLANCKIEN",
            "raies": [
                (410.0, "#6366F1", 0.60),
                (450.0, "#2563EB", 0.85),
                (500.0, "#06B6D4", 0.95),
                (550.0, "#22C55E", 0.90),
                (600.0, "#EAB308", 0.75),
                (650.0, "#EF4444", 0.60),
                (720.0, "#450a0a", 0.40),
                (820.0, "#450a0a", 0.20),
            ],
        },
        "Tube Fluorescent (Bureau)": {
            "type": "mixte",
            "couleur_source": "#F5F5F5",
            "descr": "SPECTRE MIXTE (Fonds thermique et raies de décharge)",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.29),
                (546.0, "#2E7D32", 0.49),
                (611.0, "#E65100", 0.70),
            ],
        },
        "Ampoule Fluocompacte": {
            "type": "raies",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE DE RAIES / BANDES FLUORESCENTES",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.31),
                (544.0, "#2E7D32", 0.48),
                (587.0, "#FF8F00", 0.62),
                (611.0, "#C62828", 0.70),
            ],
        },
        "LED Blanche (Froide)": {
            "type": "led_froide",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE MIXTE (Pic Bleu intense + cloche d'émission Jaune)",
            "raies": [
                (450.0, "#0000FF", 0.98),
                (520.0, "#00FF00", 0.35),
                (560.0, "#FFFF00", 0.55),
                (600.0, "#FF8000", 0.48),
                (645.0, "#FF0000", 0.30),
            ],
        },
        "Lampe au Deutérium (D2)": {
            "type": "raies",
            "couleur_source": "#EDE7F6",
            "descr": "SPECTRE DE LABO ATOMIQUE LOURD",
            "raies": [(486.0, "#00ffcc", 0.25), (656.1, "#ff0000", 0.80)],
        },
        "Lampe au Mercure (Hg)": {
            "type": "raies",
            "couleur_source": "#E0F7FA",
            "descr": "SPECTRE DE RAIES INTENSE UV-VISIBLE",
            "raies": [
                (404.7, "#4c0519", 0.02),
                (435.8, "#2563eb", 0.12),
                (546.1, "#22c55e", 0.49),
                (578.0, "#eab308", 0.59),
            ],
        },
        "Lampe au Sodium (Na)": {
            "type": "raies",
            "couleur_source": "#FFF3E0",
            "descr": "SPECTRE DE RAIES (DOUBLET D DE FRAUNHOFER)",
            "raies": [(589.0, "#ffcc00", 0.95), (589.6, "#ff9900", 0.90)],
        },
        "Lampe à l'Hélium (He)": {
            "type": "raies",
            "couleur_source": "#FFE0B2",
            "descr": "SPECTRE DE RAIES ATOMIQUE SIMPLE",
            "raies": [
                (447.1, "#1d4ed8", 0.16),
                (501.6, "#06b6d4", 0.34),
                (587.6, "#f59e0b", 0.63),
                (667.8, "#dc2626", 0.89),
            ],
        },
        "Lampe au Néon (Ne)": {
            "type": "raies",
            "couleur_source": "#FFCCBC",
            "descr": "SPECTRE DE RAIES TRÈS RICHE DANS LE ROUGE",
            "raies": [
                (585.2, "#f59e0b", 0.62),
                (614.3, "#ea580c", 0.71),
                (640.2, "#dc2626", 0.80),
                (692.9, "#991b1b", 0.97),
            ],
        },
        "Lampe à l'Argon (Ar)": {
            "type": "raies",
            "couleur_source": "#E8EAF6",
            "descr": "SPECTRE DE GAZ DE DÉCHARGE BLEUTÉ",
            "raies": [
                (420.0, "#581c87", 0.45),
                (430.0, "#4338ca", 0.30),
                (450.0, "#2563eb", 0.25),
                (488.0, "#06b6d4", 0.40),
                (696.5, "#991b1b", 0.50),
            ],
        },
        "Lampe au Krypton (Kr)": {
            "type": "raies",
            "couleur_source": "#F1F5F9",
            "descr": "SPECTRE ATOMIQUE KRYPTON COHÉRENT",
            "raies": [
                (431.9, "#4338ca", 0.15),
                (557.0, "#22c55e", 0.60),
                (587.1, "#f59e0b", 0.45),
                (642.1, "#dc2626", 0.35),
            ],
        },
        "Lampe au Xénon (Xe)": {
            "type": "raies",
            "couleur_source": "#E2E8F0",
            "descr": "SPECTRE DE DÉCHARGE FLASH CONTINU/RAIES",
            "raies": [
                (462.7, "#2563eb", 0.40),
                (467.1, "#3b82f6", 0.50),
                (473.4, "#06b6d4", 0.35),
                (529.2, "#22c55e", 0.20),
                (680.6, "#dc2626", 0.45),
            ],
        },
        "Lampe au Cadmium (Cd)": {
            "type": "raies",
            "couleur_source": "#D1C4E9",
            "descr": "SPECTRE DE RAIES MÉTALLIQUES STABLES",
            "raies": [
                (467.8, "#2563eb", 0.22),
                (479.9, "#06b6d4", 0.29),
                (508.6, "#22c55e", 0.36),
            ],
        },
        "Lampe au Zinc (Zn)": {
            "type": "raies",
            "couleur_source": "#ECEFF1",
            "descr": "SPECTRE DE RAIES VAPEUR MÉTAL HAUTE PRESSION",
            "raies": [
                (468.0, "#2563eb", 0.15),
                (472.2, "#1d4ed8", 0.20),
                (481.1, "#06b6d4", 0.35),
                (636.2, "#dc2626", 0.50),
            ],
        },
        "Lampe au Lithium (Li)": {
            "type": "raies",
            "couleur_source": "#FEE2E2",
            "descr": "SPECTRE D'ALCALIN LABO VIF (3 RAIES PHYSIQUES)",
            "raies": [
                (460.3, "#1d4ed8", 0.10),
                (610.3, "#ff6b00", 0.30),
                (670.8, "#ff0000", 0.90),
            ],
        },
        "Lampe au Potassium (K)": {
            "type": "raies",
            "couleur_source": "#F3E8FF",
            "descr": "SPECTRE ALCALIN DE LABO STABLE (SANS ERREUR 693 NM)",
            "raies": [
                (404.4, "#4c0519", 0.40),
                (766.5, "#450a0a", 0.95),
                (769.9, "#450a0a", 0.85),
            ],
        },
        "Lampe au Thallium (Tl)": {
            "type": "raies",
            "couleur_source": "#DCFCE7",
            "descr": "SPECTRE A RAIE VERTE UNIQUE PRÉPONDÉRANTE",
            "raies": [(535.0, "#22c55e", 0.95)],
        },
        "Vapeur d'Iode (I2 - Moléculaire)": {
            "type": "raies",
            "couleur_source": "#FAE8FF",
            "descr": "SPECTRE DE BANDES MOLÉCULAIRES DISCRETES",
            "raies": [
                (520.0, "#16a34a", 0.30),
                (535.0, "#15803d", 0.45),
                (550.0, "#84cc16", 0.50),
                (565.0, "#eab308", 0.40),
            ],
        },
    }



 
if "produits_indices" not in st.session_state:
    st.session_state.produits_indices = {
        "Air (n = 1.00)": 1.00,
        "Eau (n = 1.33)": 1.33,
        "Plexiglas / PMMA (n = 1.49)": 1.49,
        "Kérosène / Fioul (n = 1.44)": 1.44,
        "Cyclohexane (n = 1.43)": 1.43,
        "Huile Moteur 10W40 (n = 1.47)": 1.47,
        "Huile Hydraulique HV46 (n = 1.46)": 1.46,
        "Liquide de Frein DOT4 (n = 1.44)": 1.44,
        "Liquide de Refroidissement / Glycol (n = 1.38)": 1.38,
        "Huile de Coupe / Soluble Usinage (n = 1.41)": 1.41,
        "Gazole / Diesel (n = 1.45)": 1.45,
    }

def dessiner_fibre_optique_avancee_matplotlib():
    """Genere le schema complet d'une fibre optique à sauts d'indice.
    Incorpore l'ouverture numerique (ON), l'angle maximal d'injection dans l'air,
    la normale d'entree horizontale avec son angle i1, et les rebonds internes.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions du canevas
    w = 600
    h = 280
    
    # Structure de la fibre (interfaces horizontales)
    y_gaine_haut = 60.0
    y_gaine_bas = 220.0
    hauteur_coeur = y_gaine_bas - y_gaine_haut
    y_centre = h / 2.0

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Alignement repere informatique inversé
    ax.axis("off")

    # 1. Récupération des variables de session Streamlit
    n_coeur = st.session_state.get("var_n_coeur", 1.50)
    n_gaine = st.session_state.get("var_n_gaine", 1.40)
    n_air = 1.00  # Milieu extérieur d'injection
    
    nb_rebonds_max = st.session_state.get("var_nb_rebonds", 3)
    
    nom_lampe = st.session_state.get("var_choix_lampe_fibre", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    # Fond visuel : Gaines et Coeur
    ax.add_patch(patches.Rectangle((0, 10), w, y_gaine_haut - 10, facecolor="#38bdf8", alpha=0.05, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, y_gaine_haut), w, hauteur_coeur, facecolor="#e0f2fe", alpha=0.12, edgecolor="none"))
    ax.add_patch(patches.Rectangle((0, y_gaine_bas), w, h - 10 - y_gaine_bas, facecolor="#38bdf8", alpha=0.05, edgecolor="none"))
    
    # Lignes d'interfaces horizontales
    ax.plot([0, w], [y_gaine_haut, y_gaine_haut], color="#475569", lw=1.5, zorder=3)
    ax.plot([0, w], [y_gaine_bas, y_gaine_bas], color="#475569", lw=1.5, zorder=3)

    # Face d'entrée de la fibre (Dioptre d'entrée vertical à x = 60)
    x_entree = 60.0
    ax.plot([x_entree, x_entree], [y_gaine_haut, y_gaine_bas], color="#94a3b8", lw=2, zorder=3)

    if n_coeur <= n_gaine:
        msg, color = "ERREUR : L'indice du cœur doit être strictement supérieur à celui de la gaine.", "#ef4444"
        txt_math = "Guidage impossible (n_coeur <= n_gaine)"
        ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
        st.session_state.opt4_txt_box_fibre = txt_math
        return fig

    # 2. CALCULS THÉORIQUES
    on = math.sqrt(n_coeur**2 - n_gaine**2)
    
    if on <= 1.0:
        i_max_rad = math.asin(on / n_air)
        i_max_deg = math.degrees(i_max_rad)
        txt_i_max = f"{i_max_deg:.1f}°"
    else:
        i_max_rad = math.radians(90.0)
        i_max_deg = 90.0
        txt_i_max = "90° (Total)"

    theta_c_rad = math.asin(n_gaine / n_coeur)
    theta_c_deg = math.degrees(theta_c_rad)

    # Angle d'injection choisi à l'entrée de la fibre (par rapport à l'HORIZONTALE)
    i1_deg = st.session_state.get("var_angle_injection_externe", 25.0)
    i1_rad = math.radians(i1_deg)

    # Réfraction au dioptre d'entrée (Air -> Cœur)
    sin_r1 = (n_air * math.sin(i1_rad)) / n_coeur
    r1_rad = math.asin(sin_r1)
    
    alpha_interne_rad = r1_rad
    theta_interne_rad = (math.pi / 2.0) - alpha_interne_rad
    theta_interne_deg = math.degrees(theta_interne_rad)

    # --- AJOUT : NORMALE HORIZONTALE D'ENTRÉE ET SON ANGLE ---
    # Ligne pointillée horizontale représentant l'axe central (normale de la face d'entrée)
    ax.plot([15, x_entree + 40], [y_centre, y_centre], color="#64748b", linestyle=":", lw=1.2, zorder=2)
    
    # Rayon incident extérieur (de l'air jusqu'à la face d'entrée)
    x_source = x_entree - 55.0
    y_source = y_centre - 55.0 * math.tan(i1_rad)
    ax.annotate("", xy=(x_entree, y_centre), xytext=(x_source, y_source),
                arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    # Arc pour l'angle d'incidence i1 à l'entrée (mesuré entre l'horizontale et le rayon incident)
    # Compte tenu du repère inversé, l'arc s'oriente de 180° à 180° + i1_deg
    arc_i1 = patches.Arc((x_entree, y_centre), 35, 35, angle=0, 
                        theta1=180, theta2=180 + i1_deg, 
                        edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i1)
    
    # Positionnement du texte i1 au-dessus de l'axe pointillé
    x_text_i1 = x_entree - 25 * math.cos(math.radians(i1_deg / 2))
    y_text_i1 = y_centre - 25 * math.sin(math.radians(i1_deg / 2))
    ax.text(x_text_i1, y_text_i1, "i1", color="#cbd5e1", fontsize=8, fontweight="bold", ha="center", va="bottom")
    # Initialisation du parcours
    x_actuel = x_entree
    y_actuel = y_centre
    signe_y = 1  # Commence en montant vers la gaine du haut

    # 3. PROPAGATION ET REBONDS MULTIPLES
    if theta_interne_deg >= theta_c_deg:
        msg, color = "GUIDAGE VALIDÉ : Réflexions totales internes parfaites.", "#10b981"
        
        for rebond in range(nb_rebonds_max):
            if signe_y == -1:
                y_suivant = y_gaine_haut
                dy = y_actuel - y_gaine_haut
            else:
                y_suivant = y_gaine_bas
                dy = y_gaine_bas - y_actuel

            dx = dy / math.tan(alpha_interne_rad)
            x_suivant = x_actuel + dx

            if x_suivant > w - 10:
                x_suivant = w - 10
                y_suivant = y_actuel + (signe_y * (x_suivant - x_actuel) * math.tan(alpha_interne_rad))
                ax.annotate("", xy=(x_suivant, y_suivant), xytext=(x_actuel, y_actuel),
                            arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
                break

            # Tracé du segment de rebond
            ax.annotate("", xy=(x_suivant, y_suivant), xytext=(x_actuel, y_actuel),
                        arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

            # --- CORRECTION DE L'ARC INTERNE (i > ic) ---
            if rebond == 0:
                # --- CORRECTION DE LA NORMALE (MONTE VERS LE CŒUR) ---
                # Dans le repère inversé, soustraire 40 fait monter la ligne vers le haut de l'écran
                ax.plot([x_suivant, x_suivant], [y_suivant - 40, y_suivant], color="#64748b", linestyle=":", lw=1.2)
                
                # --- CORRECTION DE L'ARC (QUADRANT HAUT-GAUCHE INTERNE) ---
                # L'angle 270° pointe vers le haut. On dessine l'arc entre (270 - theta) et 270°
                arc_r = patches.Arc((x_suivant, y_suivant), 35, 35, angle=0, 
                                    theta1=270 - theta_interne_deg, theta2=270, 
                                    edgecolor="#cbd5e1", lw=1, zorder=5)
                ax.add_patch(arc_r)
                
                # --- CORRECTION DU TEXTE (AU-DESSUS DE LA PAROI INFÉRIEURE) ---
                x_text_refl = x_suivant - 22 * math.sin(theta_interne_rad / 2)
                y_text_refl = y_suivant - 22 * math.cos(theta_interne_rad / 2)  # Moins pour monter le texte dans le cœur
                ax.text(x_text_refl, y_text_refl, "i > ic", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right", va="bottom")

            x_actuel = x_suivant
            y_actuel = y_suivant
            signe_y *= -1
            
        if x_actuel < w - 10:
            x_fin = w - 10
            y_fin = y_actuel + (signe_y * (x_fin - x_actuel) * math.tan(alpha_interne_rad))
            ax.plot([x_actuel, x_fin], [y_actuel, y_fin], color=couleur_laser, lw=2.5, zorder=4)
            
    else:
        msg, color = "RÉFRACTION DANS LA GAINE : Rayon perdu (Angle trop grand).", "#ef4444"
        dy = y_actuel - y_gaine_haut
        dx = dy / math.tan(alpha_interne_rad)
        x_perte = x_actuel + dx
        ax.annotate("", xy=(x_perte, y_gaine_haut), xytext=(x_actuel, y_actuel), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        sin_gaine = (n_coeur * math.sin(theta_interne_rad)) / n_gaine
        angle_gaine_rad = math.asin(sin_gaine)
        dx_fuite = 40 * math.sin(angle_gaine_rad)
        dy_fuite = 40 * math.cos(angle_gaine_rad)
        ax.annotate("", xy=(x_perte + dx_fuite, y_gaine_haut - dy_fuite), xytext=(x_perte, y_gaine_haut), 
                    arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=1.5, linestyle="--"), zorder=4)

    # 4. Textes d'affichage et habillage
    txt_math = (
        f"Données de la Fibre :\n"
        f"• Ouverture Numérique (ON) = {on:.3f}\n"
        f"• Cône d'Acceptance (i_max) = {txt_i_max}\n"
        f"• Incidence choisie i1 = {i1_deg:.1f}°\n"
        f"• Angle critique interne (ic) = {theta_c_deg:.1f}°\n"
        f"• Angle d'impact interne = {theta_interne_deg:.1f}°\n"
        f"• Nombre de rebonds tracés = {nb_rebonds_max}"
    )

    ax.text(25, 20, "ATELIER 3 - OPTIQUE GÉOMÉTRIQUE : LA FIBRE OPTIQUE PRO", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    
    ax.text(w - 60, y_gaine_haut - 12, "Gaine (n2)", color="#64748b", fontsize=7, fontweight="bold")
    ax.text(w - 60, y_centre, "Cœur (n1)", color="#94a3b8", fontsize=8, fontweight="bold")
    ax.text(w - 60, y_gaine_bas + 15, "Gaine (n2)", color="#64748b", fontsize=7, fontweight="bold")
    ax.text(x_entree - 10, y_gaine_bas - 15, "Face\nd'entrée", color="#94a3b8", fontsize=6, ha="right", style="italic")

    st.session_state.opt4_txt_box_fibre = txt_math
    return fig

def dessiner_reflexion_totale_directe_matplotlib():
    """Genere le schema d'une reflexion totale interne pure (Source en bas, Dioptre horizontal).
    Version vectorielle haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w = 600
    h = 280
    x0 = 300.0  
    y_dioptre = 110.0  # Position horizontale de la surface

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Alignement sur le repere informatique inversé
    ax.axis("off")

    # Lecture des paramètres de la session active
    m1_nom = st.session_state.get("var_choix_milieu_bas", "Verre Couronne (n = 1.52)")
    m2_nom = st.session_state.get("var_choix_milieu_haut", "Air (n = 1.00)")
    
    n1 = st.session_state.produits_indices[m1_nom] if "produits_indices" in st.session_state else 1.52
    n2 = st.session_state.produits_indices[m2_nom] if "produits_indices" in st.session_state else 1.00

    nom_lampe = st.session_state.get("var_choix_lampe_refl", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    theta1_deg = st.session_state.get("var_angle_incidence_bas", 50.0)
    theta1_rad = math.radians(theta1_deg)

    # Tracé des milieux (Milieu léger en haut, Milieu dense transparent en bas)
    ax.add_patch(patches.Rectangle((15, 10), w - 30, y_dioptre - 10, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre), w - 30, h - 10 - y_dioptre, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.plot([15, w - 15], [y_dioptre, y_dioptre], color="#475569", lw=2, zorder=3)

    # Axe de la Normale verticale (S'arrête là où il faut selon le cas pour la clarté)
    ax.plot([x0, x0], [20, h - 20], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
    ax.text(x0 + 6, 25, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="left")

    # Rayon incident provenant DU BAS et allant vers le centre (x0, y_dioptre)
    longueur_rayon = 100
    x_inc = x0 - longueur_rayon * math.sin(theta1_rad)
    y_inc = y_dioptre + longueur_rayon * math.cos(theta1_rad) # Plus grand car l'axe Y descend
    ax.annotate("", xy=(x0, y_dioptre), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    # Arc et étiquette pour l'angle d'incidence i (en bas à gauche du point d'impact)
    # L'angle 90° pointe vers le bas. L'arc va de 90° à 90° + theta1
    arc_i = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=90, theta2=90 + theta1_deg, edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i)
    ax.text(x0 - 15 * math.sin(theta1_rad/2) - 8, y_dioptre + 25 * math.cos(theta1_rad/2), "i", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right")

    # Calcul de la condition limite
    if n1 > n2:
        sin_lim = n2 / n1
        angle_critique_deg = math.degrees(math.asin(sin_lim))
    else:
        sin_lim = 2.0  # Impossible d'avoir de réflexion totale si n1 <= n2
        angle_critique_deg = 0.0

    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if sin_theta2 > 1.0:
        # --- CAS DE LA RÉFLEXION TOTALE INTERNE PURE ---
        # Le rayon rebondit vers le bas à droite
        x_refl = x0 + longueur_rayon * math.sin(theta1_rad)
        y_refl = y_dioptre + longueur_rayon * math.cos(theta1_rad)
        ax.annotate("", xy=(x_refl, y_refl), xytext=(x0, y_dioptre), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Arc pour l'angle réfléchi r (en bas à droite du point d'impact)
        # Il va de 90 - theta1 jusqu'à 90° pour épouser la normale du bas
        arc_r_refl = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=90 - theta1_deg, theta2=90, edgecolor=couleur_laser, lw=1.2, zorder=5)
        ax.add_patch(arc_r_refl)
        ax.text(x0 + 15 * math.sin(theta1_rad/2) + 8, y_dioptre + 25 * math.cos(theta1_rad/2), "r", color=couleur_laser, fontsize=8, fontweight="bold", ha="left")

        msg, color = "RÉFLEXION TOTALE INTERNE : Le rayon reste piégé.", "#ef4444"
        txt_math = f"Indices : n1={n1:.2f} > n2={n2:.2f}\nAngle critique = {angle_critique_deg:.1f}°\ni = {theta1_deg:.1f}° > Angle critique\n-> 100% Réfléchi !"
    else:
        # --- CAS DE LA RÉFRACTION CLASSIQUE ---
        # Le rayon s'échappe vers le haut à droite
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)
        
        x_ref = x0 + longueur_rayon * math.sin(theta2_rad)
        y_ref = y_dioptre - longueur_rayon * math.cos(theta2_rad) # Moins car il monte dans le repère inversé
        ax.annotate("", xy=(x_ref, y_ref), xytext=(x0, y_dioptre), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Arc pour l'angle réfracté r (en haut à droite de la normale)
        # L'angle 270° pointe vers le haut. On tourne de 270° à 270° + theta2
        arc_r = patches.Arc((x0, y_dioptre), 40, 40, angle=0, theta1=270, theta2=270 + theta2_deg, edgecolor="#cbd5e1", lw=1.2, zorder=5)
        ax.add_patch(arc_r)
        ax.text(x0 + 15 * math.sin(theta2_rad/2) + 8, y_dioptre - 25 * math.cos(theta2_rad/2), "r", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left")

        msg, color = "RÉFRACTION CLASSIQUE : Le rayon traverse l'interface.", "#10b981"
        txt_math = f"Indices : n1={n1:.2f}, n2={n2:.2f}\nAngle critique = {angle_critique_deg:.1f}°\ni = {theta1_deg:.1f}°\nr = {theta2_deg:.1f}°"

    # Habillage textuel
    ax.text(25, 20, "ATELIER DE SPÉCIALITÉ - RÉFLEXION TOTALE INTERNE", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    ax.text(25, y_dioptre - 15, f"Milieu supérieur : {m2_nom}", color="#64748b", fontsize=7, ha="left")
    ax.text(25, y_dioptre + 20, f"Milieu inférieur : {m1_nom}", color="#94a3b8", fontsize=7, ha="left")

    st.session_state.opt4_txt_box_refl_totale = txt_math
    return fig

def dessiner_double_refraction_lame_matplotlib():
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    w = 600
    h = 280
    x0 = 300.0  
    y_dioptre1, y_dioptre2 = 90.0, 180.0
    epaisseur_lame_px = y_dioptre2 - y_dioptre1

    fig, ax = plt.subplots(figsize=(7.5, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(15, w - 15)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  
    ax.axis("off")

    m1_nom = st.session_state.get("var_choix_milieu1_double", "Air (n = 1.00)")
    m2_nom = st.session_state.get("var_choix_milieu2_double", "Verre Couronne (n = 1.52)")
    m3_nom = st.session_state.get("var_choix_milieu3_double", "Air (n = 1.00)")
    
    n1 = st.session_state.produits_indices[m1_nom] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[m2_nom] if "produits_indices" in st.session_state else 1.52
    n3 = st.session_state.produits_indices[m3_nom] if "produits_indices" in st.session_state else 1.00

    nom_lampe2 = st.session_state.get("var_choix_lampe_double2", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[nom_lampe2]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    theta1_deg = st.session_state.get("var_angle_double", 45.0)
    theta1_rad = math.radians(theta1_deg)

    ax.add_patch(patches.Rectangle((15, 10), w - 30, y_dioptre1 - 10, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre1), w - 30, epaisseur_lame_px, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.add_patch(patches.Rectangle((15, y_dioptre2), w - 30, h - 10 - y_dioptre2, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    
    ax.plot([15, w - 15], [y_dioptre1, y_dioptre1], color="#475569", lw=2, zorder=3)
    ax.plot([15, w - 15], [y_dioptre2, y_dioptre2], color="#475569", lw=2, zorder=3)

    # Axe de la Normale 1 (S'arrête au premier dioptre pour la clarté)
    ax.plot([x0, x0], [20, y_dioptre1 + 40], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
    ax.text(x0 + 6, 25, "Normale 1", color="#64748b", fontsize=7, fontweight="bold", ha="left")

    x_inc = x0 - 70 * math.sin(theta1_rad)
    y_inc = y_dioptre1 - 70 * math.cos(theta1_rad)
    ax.annotate("", xy=(x0, y_dioptre1), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)

    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if sin_theta2 > 1.0:
        x_total = x0 + 80 * math.sin(theta1_rad)
        y_total = y_dioptre1 - 80 * math.cos(theta1_rad)
        ax.annotate("", xy=(x_total, y_total), xytext=(x0, y_dioptre1), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        msg, color = "REFLEXION TOTALE INTERNE amont.", "#ef4444"
        txt_math = "Reflexion totale amont !\nSin(r1) impossible > 1"
        ax.text(x0 + 40, y_dioptre1 - 30, "Rayon reflechi", color="#ef4444", fontsize=7, style="italic", ha="left")
    else:
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)

        dx_px = epaisseur_lame_px * math.tan(theta2_rad)
        x_sortie = x0 + dx_px
        ax.annotate("", xy=(x_sortie, y_dioptre2), xytext=(x0, y_dioptre1), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
        
        # Positionnement optimisé du texte de r1 près de son arc
        ax.text(x0 + 15 * math.sin(theta2_rad/2) + 5, y_dioptre1 + 25 * math.cos(theta2_rad/2), "r1", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

        # Axe de la Normale 2 (Dépasse un peu à l'intérieur de la lame)
        ax.plot([x_sortie, x_sortie], [y_dioptre2 - 40, h - 15], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.2, zorder=2)
        ax.text(x_sortie + 6, y_dioptre2 + 15, "Normale 2", color="#64748b", fontsize=7, fontweight="bold", ha="left")

        sin_theta3 = (n2 * math.sin(theta2_rad)) / n3

        if sin_theta3 > 1.0:
            x_total2 = x_sortie - 70 * math.sin(theta2_rad)
            y_total2 = y_dioptre2 - 70 * math.cos(theta2_rad)
            ax.annotate("", xy=(x_total2, y_total2), xytext=(x_sortie, y_dioptre2), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
            msg, color = "REFLEXION TOTALE INTERNE basse.", "#ef4444"
            txt_math = f"Incidence i1 = {theta1_deg:.1f}°\nRefraction r1 = {theta2_deg:.1f}°\nSortie : Miroir bas !"
        else:
            theta3_rad = math.asin(sin_theta3)
            theta3_deg = math.degrees(theta3_rad)
            
            x_emerg = x_sortie + 70 * math.sin(theta3_rad)
            y_emerg = y_dioptre2 + 70 * math.cos(theta3_rad)
            ax.annotate("", xy=(x_emerg, y_emerg), xytext=(x_sortie, y_dioptre2), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
            
            # Positionnement de l'étiquette s (angle d'émergence) près de son arc
            ax.text(x_sortie + 20 * math.sin(theta3_rad/2) + 6, y_dioptre2 + 25 * math.cos(theta3_rad/2), "s", color="#ef4444", fontsize=8, fontweight="bold", ha="left", va="center")

            dx_mm = (epaisseur_lame_px * 0.20) * math.sin(theta1_rad - theta2_rad) / math.cos(theta2_rad)
            msg, color = "DOUBLE DIOPTRE : Trajectoires de sorties calculees librement.", "#10b981"
            txt_math = f"Lame :\n• i1 = {theta1_deg:.1f}°\n• r1 = {theta2_deg:.1f}°\n• s = {theta3_deg:.1f}°\n• dx = {abs(dx_mm):.2f} mm"

            # Arc pour l'angle d'émergence s (en bas à droite du point de sortie)
            arc_s = patches.Arc((x_sortie, y_dioptre2), 40, 40, angle=0, theta1=90 - theta3_deg, theta2=90, edgecolor="#ef4444", lw=1.2, zorder=5)
            ax.add_patch(arc_s)

        # Arc pour l'angle de réfraction r1 (en bas à droite du point d'incidence dans la lame)
        arc_r1 = patches.Arc((x0, y_dioptre1), 40, 40, angle=0, theta1=90 - theta2_deg, theta2=90, edgecolor="#cbd5e1", lw=1.2, zorder=5)
        ax.add_patch(arc_r1)

    ax.text(25, 20, "ATELIER 2 - DOUBLE DIOPTRE ET TRAJECTOIRES", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    ax.text(25, 35, msg, color=color, fontsize=7, fontweight="bold", ha="left")
    ax.text(x_inc - 8, y_inc + 12, "Rayon incident (i1)", color="#cbd5e1", fontsize=7, style="italic", ha="right")

    # Arc corrigé pour l'angle incident i1 (en haut à gauche, du rayon jusqu'à la normale à 270°)
    arc_i1 = patches.Arc((x0, y_dioptre1), 40, 40, angle=0, theta1=270 - theta1_deg, theta2=270, edgecolor="#cbd5e1", lw=1.2, zorder=5)
    ax.add_patch(arc_i1)

    st.session_state.opt4_txt_box_double = txt_math
    return fig

def ajouter_point_mesure_optique_streamlit():
    import math
    theta1_deg = st.session_state.get("var_angle_inc", 30.0)
    theta1_rad = math.radians(theta1_deg)
    
    milieu1 = st.session_state.get("var_choix_milieu1", "Air (n = 1.00)")
    milieu2 = st.session_state.get("var_choix_milieu2", "Eau (n = 1.33)")
    n1 = st.session_state.produits_indices[milieu1] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[milieu2] if "produits_indices" in st.session_state else 1.33
    
    sin_i = math.sin(theta1_rad)
    sin_r = (n1 * sin_i) / n2
    
    if sin_r <= 1.0:
        if "mesures_sin_i" not in st.session_state: st.session_state.mesures_sin_i = []
        if "mesures_sin_r" not in st.session_state: st.session_state.mesures_sin_r = []
        if "mesures_i_deg" not in st.session_state: st.session_state.mesures_i_deg = []
        if "mesures_r_deg" not in st.session_state: st.session_state.mesures_r_deg = []
        
        st.session_state.mesures_sin_i.append(round(sin_i, 3))
        st.session_state.mesures_sin_r.append(round(sin_r, 3))
        st.session_state.mesures_i_deg.append(theta1_deg)
        st.session_state.mesures_r_deg.append(round(math.degrees(math.asin(sin_r)), 1))

def reinitialiser_graphique_optique_streamlit():
    st.session_state.mesures_sin_i = []
    st.session_state.mesures_sin_r = []
    st.session_state.mesures_i_deg = []
    st.session_state.mesures_r_deg = []


def dessiner_schema_refraction_simple():
    """Genere le schema de la cuve optique avec le rayon laser incident et refracte/reflechi.
    Version vectorielle haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du repere d'origine
    wg = 400
    hg = 260
    x0_s = (wg / 2.0) + 100.0  
    y0_s = 170.0        

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(x0_s - 250, x0_s + 150)
    ax.set_ylim(y0_s - 150, y0_s + 110)
    ax.invert_yaxis()  # Alignement sur le repere informatique inversé
    ax.axis("off")

    # Lecture des curseurs de l'Atelier 4 de la session active
    theta1_deg = st.session_state.get("var_angle_inc", 30.0)
    theta1_rad = math.radians(theta1_deg)
    
    milieu1 = st.session_state.get("var_choix_milieu1", "Air (n = 1.00)")
    milieu2 = st.session_state.get("var_choix_milieu2", "Eau (n = 1.33)")
    n1 = st.session_state.produits_indices[milieu1] if "produits_indices" in st.session_state else 1.00
    n2 = st.session_state.produits_indices[milieu2] if "produits_indices" in st.session_state else 1.33
    
    choix_lampe = st.session_state.get("slider_lampe_simple", "Lumiere du Soleil")
    couleur_laser = st.session_state.lampes_data[choix_lampe]["couleur_source"] if "lampes_data" in st.session_state else "#ef4444"

    # Tracé des milieux (Rectangle superieur Air / Inferieur Liquide)
    y_fond_liquide = y0_s + 160.0
    ax.add_patch(patches.Rectangle((x0_s - 300, y0_s - 160), 600, 160, facecolor="#f8fafc", alpha=0.1, edgecolor="none"))
    ax.add_patch(patches.Rectangle((x0_s - 300, y0_s), 600, 160, facecolor="#e0f2fe", alpha=0.2, edgecolor="none"))
    ax.plot([x0_s - 300, x0_s + 300], [y0_s, y0_s], color="#475569", lw=2, zorder=3)
    
    # Axe vertical : La Normale pointillee
    ax.plot([x0_s, x0_s], [y0_s - 150, y_fond_liquide - 10], color="#94a3b8", linestyle="--", lw=1.5, zorder=2)
    
    # Textes pour la normale
    ax.text(x0_s + 8, y0_s - 120, "Normale", color="#94a3b8", fontsize=9, va="center")

    # Longueur totale des rayons
    longueur_rayon = 130

    # --- 1. RAYON INCIDENT ET SON ANGLE ---
    x_inc = x0_s - longueur_rayon * math.sin(theta1_rad)
    y_inc = y0_s - longueur_rayon * math.cos(theta1_rad)
    
    # Tracé du rayon de base
    ax.plot([x_inc, x0_s], [y_inc, y0_s], color=couleur_laser, lw=3, zorder=4)
    
    # Flèche au milieu du rayon incident
    ax.annotate("", xy=(x0_s - (longueur_rayon/2) * math.sin(theta1_rad), y0_s - (longueur_rayon/2) * math.cos(theta1_rad)), 
                xytext=(x_inc, y_inc),
                arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=3, mutation_scale=15), zorder=5)

    # Arc de cercle pour l'angle incident 'i'
    # Compte tenu de l'inversion Y, l'angle vers le haut-gauche est défini géométriquement
    arc_i = patches.Arc((x0_s, y0_s), width=50, height=50, angle=0, theta1=270 - theta1_deg, theta2=270, 
                        color="#f1f5f9", lw=1.5, zorder=5)
    ax.add_patch(arc_i)
    
    # Positionnement du texte 'i'
    x_text_i = x0_s - 35 * math.sin(theta1_rad / 2)
    y_text_i = y0_s - 35 * math.cos(theta1_rad / 2)
    ax.text(x_text_i, y_text_i, "i", color="#f1f5f9", fontsize=11, fontweight="bold", ha="center", va="center")


    # --- 2. RAYON RÉFRACTÉ ET SON ANGLE ---
    sin_theta2 = (n1 * math.sin(theta1_rad)) / n2

    if abs(sin_theta2) <= 1.0:
        theta2_rad = math.asin(sin_theta2)
        theta2_deg = math.degrees(theta2_rad)
        
        x_ref = x0_s + longueur_rayon * math.sin(theta2_rad)
        y_ref = y0_s + longueur_rayon * math.cos(theta2_rad)
        
        # Tracé du rayon de base
        ax.plot([x0_s, x_ref], [y0_s, y_ref], color=couleur_laser, lw=3, zorder=4)
        
        # Flèche au milieu du rayon réfracté
        ax.annotate("", xy=(x0_s + (longueur_rayon/2) * math.sin(theta2_rad), y0_s + (longueur_rayon/2) * math.cos(theta2_rad)), 
                    xytext=(x0_s, y0_s),
                    arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=3, mutation_scale=15), zorder=5)

        # Arc de cercle pour l'angle réfracté 'r' (en bas à droite dans le repère inversé)
        arc_r = patches.Arc((x0_s, y0_s), width=50, height=50, angle=0, theta1=90 - theta2_deg, theta2=90, 
                            color="#f1f5f9", lw=1.5, zorder=5)
        ax.add_patch(arc_r)
        
        # Positionnement du texte 'r' (déjà correct, conservé tel quel)
        x_text_r = x0_s + 35 * math.sin(theta2_rad / 2)
        y_text_r = y0_s + 35 * math.cos(theta2_rad / 2)
        ax.text(x_text_r, y_text_r, "r", color="#f1f5f9", fontsize=11, fontweight="bold", ha="center", va="center")
    else:
        # En cas de Réflexion totale interne
        x_refl = x0_s + longueur_rayon * math.sin(theta1_rad)
        y_refl = y0_s - longueur_rayon * math.cos(theta1_rad)
        ax.plot([x0_s, x_refl], [y0_s, y_refl], color=couleur_laser, lw=2, linestyle=":", zorder=4)

    return fig

def dessiner_graphique_sinus_matplotlib():
    """Genere le graphique cartesien sin(r) = f(sin(i)) avec mise a jour de l'historique.
    """
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.1)

    # Affichage de la grille de cours millimetree stable
    ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)

    # Titres et axes
    ax.set_xlabel("sin(i)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_ylabel("sin(r)", color="#cbd5e1", fontsize=9, fontweight="bold", labelpad=5)
    ax.set_title("Atelier 4 : Releves sin(r) = f(sin(i))", color="#38bdf8", fontsize=8, style="italic")

    # Superposition permanente des points memorises (Croix vertes d'origine)
    m_sin_i = st.session_state.get("mesures_sin_i", [])
    m_sin_r = st.session_state.get("mesures_sin_r", [])
    
    if m_sin_i:
        ax.scatter(m_sin_i, m_sin_r, color="#10b981", marker="x", s=50, lw=2, label="Points mesures", zorder=5)
        ax.legend(facecolor="#1e293b", edgecolor="#334155", labelcolor="white", fontsize=7, loc="upper left")

    return fig

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


with tab2:
    
    st.header("Atelier  : Lois de Snell-Descartes ")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules Fondamentales de la Refraction :</p>
        <ul>
            <li><strong>Deuxieme loi de Snell-Descartes :</strong> $n_1 \\cdot \\sin(i_1) = n_2 \\cdot \\sin(i_2)$</li>
            <li><strong>Loi du double dioptre (Lame a faces paralleles) :</strong> Le rayon emergent sort de la lame avec un angle de deviation nul ($i_3 = i_1$) mais subit un <strong>decalage lateral $dx$</strong>.</li>
            <li><strong>Calcul de la pente :</strong> En tracant $\\sin(i_1)$ en fonction de $\\sin(i_2)$, la droite lineaire possede un coefficient directeur egal au rapport des indices $\\frac{n_2}{n_1}$.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt4_verrouille" not in st.session_state: 
        st.session_state.opt4_verrouille = False

    # Initialisation permanente des listes de mesures d'origine (Reconversion Tkinter)
    if "mesures_sin_i" not in st.session_state: st.session_state.mesures_sin_i = []
    if "mesures_sin_r" not in st.session_state: st.session_state.mesures_sin_r = []
    if "mesures_i_deg" not in st.session_state: st.session_state.mesures_i_deg = []
    if "mesures_r_deg" not in st.session_state: st.session_state.mesures_r_deg = []

    # Récupération des catalogues présents en mémoire de session
    liste_lampes = list(st.session_state.lampes_data.keys()) if "lampes_data" in st.session_state else ["Lumiere du Soleil"]
    liste_milieux = list(st.session_state.produits_indices.keys()) if "produits_indices" in st.session_state else ["Air (n = 1.00)", "Eau (n = 1.33)", "Verre Couronne (n = 1.52)"]

    # =========================================================================
    # INTERFACE EN COLONNES PROPRE ET AERÉE
    # =========================================================================

    st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:2px;'>1. REFRACTION SIMPLE</p>", unsafe_allow_html=True)
    
    choix_lampe1 = st.selectbox("Source lumineuse :", liste_lampes, key="slider_lampe_simple", disabled=st.session_state.opt4_verrouille)
    angle_i1 = st.slider("Angle d'incidence i1 (°) :", min_value=0.0, max_value=90.0, value=30.0, step=1.0, key="var_angle_inc", disabled=st.session_state.opt4_verrouille)
    
    milieu1 = st.selectbox("Milieu superieur (n1) :", liste_milieux, index=0, key="var_choix_milieu1", disabled=st.session_state.opt4_verrouille)
    milieu2 = st.selectbox("Milieu inferieur (n2) :", liste_milieux, index=1, key="var_choix_milieu2", disabled=st.session_state.opt4_verrouille)

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("PRENDRE UNE MESURE", key="btn_mesure_simple_officiel", use_container_width=True, disabled=st.session_state.opt4_verrouille):
            ajouter_point_mesure_optique_streamlit()
            st.rerun()

    with col_btn2:
        if st.button("Effacer le graphique", key="btn_raz_simple_officiel", use_container_width=True, disabled=st.session_state.opt4_verrouille):
            reinitialiser_graphique_optique_streamlit()
            st.rerun()


    # APPEL DE VOTRE DESSIN DU DIOPTRE SIMPLE DE REFRACTION
    fig_cuve_simple = dessiner_schema_refraction_simple()
    st.pyplot(fig_cuve_simple, use_container_width=True)
    
    # Boite blanche de resultats sous le graphique de la cuve
    st.info(st.session_state.get("opt4_txt_box_simple", "Ajustez le curseur pour initialiser."))
        
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Tableau des points de mesures memorises (Loi de Snell-Descartes)")
        
    import pandas as pd
    if st.session_state.mesures_i_deg:
        df_treeview = pd.DataFrame({
            "N° Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_i_deg) + 1)],
            "Angle i1 (°)": [f"{val:.1f}°" for val in st.session_state.mesures_i_deg],
            "Angle r2 (°)": [f"{val:.1f}°" for val in st.session_state.mesures_r_deg],
            "sin(i1)": st.session_state.mesures_sin_i,
            "sin(r2)": st.session_state.mesures_sin_r
        })
        st.dataframe(df_treeview, use_container_width=True, hide_index=True)
    else:
        st.caption("Tableau de mesures vide. Modifiez l'angle d'incidence et cliquez sur Prendre une mesure pour enregistrer des donnees.")            

                # APPEL DE VOTRE GRAPHIQUE LINÉAIRE EXPERIMENTAL SIN(R) = F(SIN(I))
        fig_loi_sinus = dessiner_graphique_sinus_matplotlib()
        st.pyplot(fig_loi_sinus, use_container_width=True)



with tab3:
    st.header("**Manipulation  : Illusion d'optique (Affichage Tete Haute - HUD)**")
            

    st.markdown("<p style='color:#991b1b; font-weight:bold; margin-bottom:2px;'> DOUBLE REFRACTION</p>", unsafe_allow_html=True)
    
    choix_lampe2 = st.selectbox("Source lumineuse  :", liste_lampes, key="var_choix_lampe_double2", disabled=st.session_state.opt4_verrouille)
    angle_double = st.slider("Angle d'incidence double (°) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="var_angle_double", disabled=st.session_state.opt4_verrouille)
    
    milieu1_d = st.selectbox("Milieu 1 (n1) :", liste_milieux, index=0, key="var_choix_milieu1_double", disabled=st.session_state.opt4_verrouille)
    milieu2_d = st.selectbox("Milieu 2 - Lame (n2) :", liste_milieux, index=2, key="var_choix_milieu2_double", disabled=st.session_state.opt4_verrouille)
    milieu3_d = st.selectbox("Milieu 3 (n3) :", liste_milieux, index=0, key="var_choix_milieu3_double", disabled=st.session_state.opt4_verrouille)    
  

    # Rendu du second schema de la double refraction en dessous
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    fig_double_dioptre = dessiner_double_refraction_lame_matplotlib()
    st.pyplot(fig_double_dioptre, use_container_width=True)
    
    # Boîte blanche flottante mémorisée dans la session
    st.info(st.session_state.get("opt4_txt_box_double", "Ajustez les curseurs pour initialiser la lame."))

with tab4:
    st.header("**Réflexion totale : application à la fibre optique**")

    st.markdown("<p style='color:#38bdf8; font-weight:bold; margin-bottom:2px;'>- PHÉNOMÈNE DE RÉFLEXION TOTALE INTERNE</p>", unsafe_allow_html=True)
    
    # Sélecteurs pour la réflexion totale directe (Source en bas)
    choix_lampe_refl = st.selectbox("Source lumineuse (Réflexion totale) :", liste_lampes, key="var_choix_lampe_refl", index=0)
    
    col_refl1, col_refl2 = st.columns(2)
    with col_refl1:
        milieu_bas = st.selectbox("Milieu inférieur (dense, n1) :", liste_milieux, index=2, key="var_choix_milieu_bas") # Ex: Verre Couronne
    with col_refl2:
        milieu_haut = st.selectbox("Milieu supérieur (léger, n2) :", liste_milieux, index=0, key="var_choix_milieu_haut") # Ex: Air
        
    angle_incidence_bas = st.slider("Angle d'incidence depuis le bas (i) (°) :", min_value=0.0, max_value=90.0, value=50.0, step=0.5, key="var_angle_incidence_bas")

    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # Rendu du schéma de la Réflexion Totale
    fig_refl_totale = dessiner_reflexion_totale_directe_matplotlib()
    st.pyplot(fig_refl_totale, use_container_width=True)

    # Boîte blanche d'information pour la réflexion totale
    st.info(st.session_state.get("opt4_txt_box_refl_totale", "Ajustez les curseurs pour initialiser la simulation de réflexion totale."))

    st.markdown("---") # Ligne de séparation visuelle entre les deux ateliers


    st.markdown("<p style='color:#38bdf8; font-weight:bold; margin-bottom:2px;'> LA FIBRE OPTIQUE PRO</p>", unsafe_allow_html=True)
    
    # 1. Sélection des composants et de la lampe
    choix_lampe_fibre = st.selectbox("Source lumineuse (Fibre) :", liste_lampes, key="var_choix_lampe_fibre", index=0)
    
    col_fibre1, col_fibre2 = st.columns(2)
    with col_fibre1:
        # Configuration des indices du cœur et de la gaine
        n_coeur = st.slider("Indice de réfraction du Cœur (n1) :", min_value=1.40, max_value=1.80, value=1.52, step=0.01, key="var_n_coeur")
    with col_fibre2:
        n_gaine = st.slider("Indice de réfraction de la Gaine (n2) :", min_value=1.30, max_value=1.45, value=1.40, step=0.01, key="var_n_gaine")

    # 2. Réglages des propriétés du rayon lumineux
    angle_injection = st.slider("Angle d'incidence externe (i1) (°) :", min_value=0.0, max_value=85.0, value=25.0, step=0.5, key="var_angle_injection_externe")
    nb_rebonds = st.slider("Nombre maximum de rebonds :", min_value=1, max_value=8, value=4, step=1, key="var_nb_rebonds")

    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)

    # 3. Rendu du schéma Matplotlib de la fibre optique avancée
    fig_fibre = dessiner_fibre_optique_avancee_matplotlib()
    st.pyplot(fig_fibre, use_container_width=True)

    # 4. Boîte d'information mémorisée dans la session
    st.info(st.session_state.get("opt4_txt_box_fibre", "Ajustez les curseurs pour initialiser la simulation de la fibre optique."))     



with tab5:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")
            




with tab6:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")




with tab7:
    st.header("Applications de la réflexion totale dans le domaine routier")
    
    import random
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    def dessiner_schema_explicatif_routier(type_application, couleur_faisceau="#ef4444"):
        fig, ax = plt.subplots(figsize=(5, 3.5), facecolor="#0f172a")
        ax.set_facecolor("#0f172a")
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.invert_yaxis()
        ax.axis("off")
        
        if type_application == "catadioptre":
            # Structure du prisme
            x_prisme = [45, 85, 45]
            y_prisme = [15, 45, 75]
            ax.fill(x_prisme, y_prisme, facecolor="#38bdf8", alpha=0.15, edgecolor="#475569", lw=1.5)
            
            x_entree = [45, 45]
            y_entree = [15, 75]
            ax.plot(x_entree, y_entree, color="#94a3b8", lw=2)
            
            # Trajectoire du rayon lumineux
            ax.annotate("", xy=(65, 35), xytext=(5, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(65, 55), xytext=(65, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(5, 55), xytext=(65, 55), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            
            ax.text(35, 28, "Entrée", color="#94a3b8", fontsize=8)
            ax.text(70, 45, "Réflexions\ntotales (2x)", color="#cbd5e1", fontsize=8, ha="left", va="center")
            
        elif type_application == "mirage":
            ax.add_patch(patches.Rectangle((0, 85), 100, 15, facecolor="#f59e0b", alpha=0.25, edgecolor="none"))
            
            x_sol = [0, 100]
            y_sol = [85, 85]
            ax.plot(x_sol, y_sol, color="#f59e0b", lw=1.5)
            ax.text(50, 95, "Bitume chaud (n plus faible)", color="#f59e0b", fontsize=8, ha="center")
            
            x_vals = [float(x) for x in range(5, 95)]
            y_vals = [25 + 0.0075 * (x - 50)**2 for x in x_vals]
            ax.plot(x_vals, y_vals, color=couleur_faisceau, lw=2.5)
            
            ax.annotate("", xy=(30, 28), xytext=(10, 37), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=0, mutation_scale=12))
            ax.annotate("", xy=(90, 37), xytext=(70, 28), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=0, mutation_scale=12))
            
            x_norm = [50, 50]
            y_norm = [60, 85]
            ax.plot(x_norm, y_norm, color="#64748b", linestyle=":", lw=1)
            ax.text(50, 55, "Réflexion totale\nprogressive", color="#cbd5e1", fontsize=8, ha="center")
            
        elif type_application == "capteur_pluie":
            ax.add_patch(patches.Rectangle((5, 35), 90, 25, facecolor="#e0f2fe", alpha=0.15, edgecolor="#475569", lw=1.5))
            ax.text(10, 48, "Verre du pare-brise", color="#94a3b8", fontsize=8)
            
            goutte = patches.Wedge((50, 35), 14, 180, 360, facecolor="#38bdf8", alpha=0.5, edgecolor="#0284c7")
            ax.add_patch(goutte)
            ax.text(50, 25, "Goutte de pluie", color="#38bdf8", fontsize=8, ha="center")
            
            ax.annotate("", xy=(50, 35), xytext=(20, 75), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(60, 10), xytext=(50, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=1.5, linestyle="--"))
            ax.annotate("", xy=(80, 75), xytext=(50, 35), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=1.5, alpha=0.4))
            
            ax.text(32, 60, "Faisceau LED", color=couleur_faisceau, fontsize=7, rotation=35)
            ax.text(54, 52, "Réflexion brisée", color="#cbd5e1", fontsize=8)
            
        elif type_application == "panneau_signalisation":
            # Reconstruction géométrique propre à base de listes indépendantes
            y_h = [45, 25, 45]
            for i in range(4):
                offset = 15 + i * 20
                x_h = [offset, offset + 10, offset + 20]
                ax.fill(x_h, y_h, facecolor="#10b981", alpha=0.1, edgecolor="#10b981", lw=1)
            
            ax.annotate("", xy=(40, 30), xytext=(15, 85), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            ax.annotate("", xy=(25, 85), xytext=(45, 30), arrowprops=dict(arrowstyle="->", color=couleur_faisceau, lw=2.5))
            
            ax.text(50, 70, "Retour du faisceau\nvers le conducteur", color="#cbd5e1", fontsize=8, ha="center")
            ax.text(50, 15, "Revêtement microprismatique", color="#10b981", fontsize=8, ha="center")
            
        return fig

    # --- BASE DE DONNÉES DES APPLICATIONS ROUTIÈRES ---
    APPLICATIONS_ROUTIERES = {
        "catadioptre": {
            "titre": "Le Catadioptre (Rétroréflecteur)",
            "description": """
            **Principe :** Les catadioptres situés à l'arrière des véhicules ou sur les balises de virage utilisent des prismes d'angle droit (coins de cube). 
            La lumière des phares d'une voiture entre par la face avant, subit **deux réflexions totales internes successives à 90°** sur les parois intérieures, et repart *exactement* dans la même direction vers les yeux du conducteur. 
            Cela permet de rendre les obstacles extrêmement visibles la nuit sans consommer d'électricité.
            """,
            "image_filename": "catadioptre_routier.jpg"
        },
        "mirage": {
            "titre": "Le Mirage Routier (Effet de flaque d'eau)",
            "description": """
            **Principe :** En été, le soleil chauffe intensément le bitume, ce qui crée une couche d'air très chaud (et donc moins dense, avec un indice de réfraction plus faible) juste au-dessus de la route. L'air plus haut reste plus frais (indice plus élevé).
            Les rayons lumineux du ciel descendent vers le sol et passent d'un milieu plus réfringent à un milieu moins réfringent. L'angle critique est dépassé : le rayon subit une **réflexion totale interne curviligne** juste avant de toucher le sol et remonte vers l'œil du conducteur. Celui-ci croit voir le ciel se refléter sur la route, donnant l'illusion d'une flaque d'eau.
            """,
            "image_filename": "mirage_routier.jpg"
        },
        "capteur_pluie": {
            "titre": "Le Capteur de Pluie automatique",
            "description": """
            **Principe :** Placé derrière le rétroviseur central, un émetteur LED envoie de la lumière dans le pare-brise avec un angle calculé pour qu'il y ait **réflexion totale interne** sur la face externe du verre sec. La lumière est normalement réfléchie à 100 % vers un récepteur.
            Dès que des gouttes de pluie tombent sur le pare-brise, l'eau (indice n = 1,33) modifie les conditions optiques par rapport à l'air (n = 1,00). L'angle critique change, la réflexion totale est brisée : une partie de la lumière s'échappe dans la goutte d'eau. Le récepteur reçoit moins de lumière et déclenche automatiquement les essuie-glaces !
            """,
            "image_filename": "capteur_pluie_routier.jpg"
        },
        "panneau_signalisation": {
            "titre": "Les Panneaux de Signalisation Rétroréflecteurs",
            "description": """
            **Principe :** Le revêtement des panneaux de signalisation routière modernes n'est pas un simple miroir, mais un film plastique composé de millions de **microprismes transparents**.
            La lumière des phares pénètre dans chaque microprisme et subit une série de **réflexions totales internes** sur les facettes arrières. Grâce à la géométrie rigoureuse des prismes, les rayons lumineux sont renvoyés de manière concentrée vers leur source (la voiture) plutôt que d'être dispersés dans la nature. Le panneau semble alors s'illuminer sous l'effet des phares.
            """,
            "image_filename": "panneau_signalisation_routier.jpg"
        }
    }

    if "app_routiere_choisie" not in st.session_state:
        st.session_state.app_routiere_choisie = "catadioptre"

    # Bouton pour générer une application au hasard
    if st.button("Générer une application routière au hasard"):
        choix_possibles = list(APPLICATIONS_ROUTIERES.keys())
        choix_filtrés = [c for c in choix_possibles if c != st.session_state.app_routiere_choisie]
        st.session_state.app_routiere_choisie = random.choice(choix_filtrés)
        st.rerun()

    app_active = APPLICATIONS_ROUTIERES[st.session_state.app_routiere_choisie]

    st.subheader(app_active["titre"])
    
    # Utilisation stricte de st.columns(2) pour éviter le bug safe_columns
    col_texte, col_visualisation = st.columns(2)
    
    with col_texte:
        st.markdown(app_active["description"])
        st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
        
        # Récupération dynamique de la couleur globale de la source lumineuse
        couleur_faisceau_bouton = "#ef4444"
        if "var_choix_lampe_simple" in st.session_state and "lampes_data" in st.session_state:
            lampe_sel = st.session_state.var_choix_lampe_simple
            if lampe_sel in st.session_state.lampes_data:
                couleur_faisceau_bouton = st.session_state.lampes_data[lampe_sel]["couleur_source"]

        # Affichage du schéma vectoriel Matplotlib
        st.markdown("**Schéma optique de principe :**")
        fig_routier = dessiner_schema_explicatif_routier(st.session_state.app_routiere_choisie, couleur_faisceau=couleur_faisceau_bouton)
        st.pyplot(fig_routier, use_container_width=True)

    with col_visualisation:
        try:
            st.image(app_active["image_filename"], caption="Illustration en situation réelle", use_container_width=True)
        except Exception:
            st.warning(f"Fichier image {app_active['image_filename']} introuvable dans le dossier.")  

    st.markdown("---")
    
    # Appel de la fonction pour générer et afficher les questions à l'écran
    dict_quiz_opt7, dict_trous_opt7 = afficher_questions_optique7(
        verrouille=st.session_state.get("opt7_verrouille", False)
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Optique 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    cas_actif = st.session_state.get("app_routiere_choisie", "catadioptre")

    case_certif_opt7 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 7.", 
        key="check_certif_opt7_officiel_20pts", 
        disabled=st.session_state.get("opt7_verrouille", False)
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_opt7_official_20pts", use_container_width=True, disabled=st.session_state.get("opt7_verrouille", False)):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_opt7: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. BASE DE CORRECTION DYNAMIQUE DU QUIZ (PARTIE 1 : 10 POINTS)
            reponses_attendues_quiz = {
                "catadioptre": {
                    "c1": "Parallèle à l'axe incident", "c2": "Coin de cube (angle droit)", "c3": "90°", 
                    "c4": "Réflexion totale interne", "c5": "180° (demi-tour complet)", "c6": "Supérieur à l'angle critique", 
                    "c7": "Passif (sans consommation électrique)", "c8": "Parallèles", "c9": "S'échapper par réfraction", "c10": "Rouge"
                },
                "mirage": {
                    "m1": "Flaque d'eau", "m2": "Chaud", "m3": "Faible", "m4": "Faible", 
                    "m5": "U inversé (courbe montante)", "m6": "Angle critique (limite)", "m7": "Ciel", 
                    "m8": "Curviligne (courbe)", "m9": "Inversée (reflétée)", "m10": "Homogène"
                },
                "capteur_pluie": {
                    "p1": "Rétroviseur central", "p2": "Infrarouge (invisible)", "p3": "Réflexion totale interne", 
                    "p4": "Supérieur à l'angle critique", "p5": "100% (intensité maximale)", "p6": "Air (n = 1.00)", 
                    "p7": "Critique (limite)", "p8": "Brisée (rompue)", "p9": "S'échapper dans la goutte", "p10": "Essuie-glaces"
                },
                "panneau_signalisation": {
                    "s1": "Film plastique technique", "s2": "Microprismes transparents", "s3": "La voiture d'origine (la source)", 
                    "s4": "Rétroréflexion", "s5": "Totales internes", "s6": "Phares", "s7": "Ciel ou environnement", 
                    "s8": "Air", "s9": "Angle limite dépassé", "s10": "Sécurité routière"
                }
            }

            dictionnaire_quiz_actif = reponses_attendues_quiz[cas_actif]
            score_quiz_opt7 = 0.0
            for qk, qv in dictionnaire_quiz_actif.items():
                cle_saisie = f"col_g_quiz_opt7_{cas_actif}_{qk}"
                if st.session_state.get(cle_saisie) == qv:
                    score_quiz_opt7 += 1.0
            
            score_quiz_opt7 = min(10.0, round(score_quiz_opt7, 1))

            # 2. BASE DE CORRECTION DYNAMIQUE DES TROUS (PARTIE 2 : 10 POINTS)
            reponses_attendues_trous = {
                "catadioptre": {
                    "t1_opt7": "Phares", "t2_opt7": "Avant", "t3_opt7": "Prismes", "t4_opt7": "Droit", "t5_opt7": "Incident",
                    "t6_opt7": "Réflexions", "t7_opt7": "Totales", "t8_opt7": "Internes", "t9_opt7": "Parallèle", "t10_opt7": "Conducteur"
                },
                "mirage": {
                    "t1_opt7": "Soleil", "t2_opt7": "Bitume", "t3_opt7": "Chaud", "t4_opt7": "Faible", "t5_opt7": "Supérieures",
                    "t6_opt7": "Réfringent", "t7_opt7": "Critique", "t8_opt7": "Totale", "t9_opt7": "Ciel", "t10_opt7": "Illusion"
                },
                "capteur_pluie": {
                    "t1_opt7": "Diode", "t2_opt7": "Verre", "t3_opt7": "Supérieur", "t4_opt7": "Air", "t5_opt7": "Totale",
                    "t6_opt7": "Récepteur", "t7_opt7": "Gouttes", "t8_opt7": "Eau", "t9_opt7": "Brisée", "t10_opt7": "Essuie-glaces"
                },
                "panneau_signalisation": {
                    "t1_opt7": "Film", "t2_opt7": "Microprismes", "t3_opt7": "Phares", "t4_opt7": "Transparents", "t5_opt7": "Facettes",
                    "t6_opt7": "Interne", "t7_opt7": "Supérieur", "t8_opt7": "Source", "t9_opt7": "Luminosité", "t10_opt7": "Sécurité routière"
                }
            }

            dict_t_actif = reponses_attendues_trous[cas_actif]
            score_trous_opt7 = 0.0
            for tk, tv in dict_t_actif.items():
                if st.session_state.get(f"opt7_{tk}") == tv:
                    score_trous_opt7 += 1.0

            st.session_state.score_opt7_p1 = round(score_quiz_opt7, 1)
            st.session_state.score_opt7_p2 = round(score_trous_opt7, 1)
            st.session_state.score_final_opt7 = round(score_quiz_opt7 + score_trous_opt7, 1)
            st.session_state.opt7_verrouille = True
            st.rerun()

    # BLOC PERMANENT D'AFFICHAGE DU RAPPORT HTML APRÈS VERROUILLAGE
    if st.session_state.get("opt7_verrouille", False):
        scr1 = st.session_state.get("score_opt7_p1", 0.0)
        scr2 = st.session_state.get("score_opt7_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt7", 0.0)

        # Heure locale fixe stable (UTC+1 ou UTC+2)
        from datetime import datetime, timedelta
        timestamp_opt7 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER OPTIQUE 7 SCELLE ET VALIDE | Note : {tot_s} / 20")

        # Re-déclaration locale des dictionnaires pour boucler dans la génération HTML
        reponses_attendues_quiz = {
            "catadioptre": {
                "c1": "Parallèle à l'axe incident", "c2": "Coin de cube (angle droit)", "c3": "90°", 
                "c4": "Réflexion totale interne", "c5": "180° (demi-tour complet)", "c6": "Supérieur à l'angle critique", 
                "c7": "Passif (sans consommation électrique)", "c8": "Parallèles", "c9": "S'échapper par réfraction", "c10": "Rouge"
            },
            "mirage": {
                "m1": "Flaque d'eau", "m2": "Chaud", "m3": "Faible", "m4": "Faible", 
                "m5": "U inversé (courbe montante)", "m6": "Angle critique (limite)", "m7": "Ciel", 
                "m8": "Curviligne (courbe)", "m9": "Inversée (reflétée)", "m10": "Homogène"
            },
            "capteur_pluie": {
                "p1": "Rétroviseur central", "p2": "Infrarouge (invisible)", "p3": "Réflexion totale interne", 
                "p4": "Supérieur à l'angle critique", "p5": "100% (intensité maximale)", "p6": "Air (n = 1.00)", 
                "p7": "Critique (limite)", "p8": "Brisée (rompue)", "p9": "S'échapper dans la goutte", "p10": "Essuie-glaces"
            },
            "panneau_signalisation": {
                "s1": "Film plastique technique", "s2": "Microprismes transparents", "s3": "La voiture d'origine (la source)", 
                "s4": "Rétroréflexion", "s5": "Totales internes", "s6": "Phares", "s7": "Ciel ou environnement", 
                "s8": "Air", "s9": "Angle limite dépassé", "s10": "Sécurité routière"
            }
        }
        reponses_attendues_trous = {
            "catadioptre": {"t1_opt7": "Prismes", "t2_opt7": "Réflexion totale", "t3_opt7": "Conducteur"},
            "mirage": {"t1_opt7": "Air", "t2_opt7": "Curviligne", "t3_opt7": "Ciel"},
            "capteur_pluie": {"t1_opt7": "Pare-brise", "t2_opt7": "Totale", "t3_opt7": "Essuie-glaces"},
            "panneau_signalisation": {"t1_opt7": "Microprismes", "t2_opt7": "Limite", "t3_opt7": "Source"}
        }

        dict_textes_questions_quiz = {
            "catadioptre": {
                "c1": "Un catadioptre sert a renvoyer les rayons lumineux de facon :",
                "c2": "La forme geometrique interne utilisee dans un catadioptre est un :",
                "c3": "Les facettes arriere du catadioptre forment entre elles un angle de :",
                "c4": "Le retour de la lumiere s'effectue sans miroir grace au phenomene de :",
                "c5": "Apres deux reflexions successives a 90 degres, la deviation totale vaut :",
                "c6": "Pour que le dispositif fonctionne, l'angle d'impact sur la facette doit etre :",
                "c7": "Le grand avantage du catadioptre par rapport a une lampe classique est qu'il est :",
                "c8": "Dans le repere d'un prisme droit, les rayons incidents et emergents sont :",
                "c9": "Si le materiau du catadioptre possede un indice trop faible, la lumiere va :",
                "c10": "Sur la route, les catadioptres équipent obligatoirement l'arriere des véhicules en :"
            },
            "mirage": {
                "m1": "Le mirage routier donne l'illusion visuelle de la présence d'une :",
                "m2": "En ete, la forte chaleur emise par le bitume rend l'air en surface tres :",
                "m3", "Cet air fortement chauffe possede une densite plus :",
                "m4": "L'indice de refraction de la couche d'air au ras du sol devient donc plus :",
                "m5": "Le gradient d'indice genere des couches d'air qui font courber la trajectoire en :",
                "m6": "La reflexion totale progressive se produit car l'angle d'incidence finit par dépasser l' :",
                "m7": "Les rayons lumineux qui subissent cette courbe proviennent initialement du :",
                "m8": "Puisque l'indice varie continuellement avec l'altitude, la trajectoire finale est :",
                "m9": "L'oeil du conducteur prolonge la trajectoire rectilignement et voit une image :",
                "m10": "Ce phenomene montre que la lumiere ne se propage en ligne droite que si le milieu est :"
            },
            "capteur_pluie": {
                "p1": "Le capteur de pluie automatique d'une automobile est generalement place derriere le :",
                "p2": "La source lumineuse utilisee par l'emetteur is une LED fonctionnant en :",
                "p3": "Lorsque le pare-brise est sec, le faisceau lumineux subit sur la face externe une :",
                "p4": "L'angle d'injection initial de la LED dans le verre est calcule pour etre :",
                "p5": "Dans des conditions seches, la quantite de lumiere renvoyee au recepteur vaut environ :",
                "p6": "L'indice de refraction de l'eau (n = 1.33) est superieur a celui de l' :",
                "p7": "L'arrivee d'eau sur le pare-brise modifie la valeur de l'angle :",
                "p8": "Lorsque la condition aux limites change a cause de la pluie, la reflexion totale est :",
                "p9": "Une fraction importante de l'intensite lumineuse infrarouge va alors :",
                "p10": "La baisse de signal electrique mesuree par la photodiode declenche l'action des :"
            },
            "panneau_signalisation": {
                "s1": "Le revetement brillant des panneaux de signalisation routiere modernes est un :",
                "s2": "Ce film plastique technique renferme une multitude de structures nommees :",
                "s3": "Contrairement a un miroir classique, le panneau de signalisation renvoie le flux vers :",
                "s4": "Cette capacite particuliere a renvoyer la lumiere vers sa source s'appelle la :",
                "s5", "A l'interieur d'un microprisme, les rayons subissent une serie de reflexions :",
                "s6": "La surface du panneau semble s'illuminer fortement des que la voiture allume ses :",
                "s7": "La directivite du faisceau evite de disperser inutilement l'energie vers le :",
                "s8": "La condition de guidage impose que l'indice du plastique soit superieur a celui de l' :",
                "s9": "Les facettes microscopiques arriere agissent comme des miroirs parfaits grace a l' :",
                "s10": "Pour l'automobiliste de nuit, ce systeme passif apporte un gain majeur en termes de :"
            }
        }

        dict_enonces_actif = dict_textes_questions_quiz[cas_actif]

        html_export_opt7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Optique 7 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #38bdf8; color: #0f172a; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #1e293b; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Cas routier etudie : {cas_actif.upper()} | Scelle le : {timestamp_opt7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores - Optique 7</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #38bdf8; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Questionnaire d'application routiere : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous thématique) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ SUR LES CONNAISSANCES ROUTIÈRES (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question posée</th>
                        <th style="width: 20%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 15%; text-align: center;">Attendu</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Remplissage du tableau de la Partie 1 avec l'énoncé de la question
        for idx_t, (q_id, attendu) in enumerate(dict_q_actif.items(), 1):
            cle_saisie = f"col_g_quiz_opt7_{cas_actif}_{q_id}"
            saisie = st.session_state.get(cle_saisie, "Choisir...")
            enonce_q = dict_enonces_actif.get(q_id, "Question d'optique routière")
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_opt7 += f"<tr><td>{idx_t}</td><td>{enonce_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"
            
        html_export_opt7 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS ASSOCIEE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Emplacement</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Remplissage du tableau de la Partie 2 pour les 10 trous
        reponses_trous_officiel = reponses_attendues_trous[cas_actif]
        for idx_t in range(1, 11):
            t_key = f"t{idx_t}_opt7"
            saisie = st.session_state.get(f"opt7_{t_key}", "Choisir...")
            attendu = reponses_trous_officiel.get(t_key, "Inconnu")
            
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            
            html_export_opt7 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_opt7 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #64748b;">
                Laboratoire d'Optique Physique Appliquee &copy; 2026
            </div>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement pour l'élève
        st.download_button(
            label="Télécharger le relevé de notes au format HTML",
            data=html_export_opt7,
            file_name=f"Bilan_Optique7_{n_eleve}_{cas_actif}.html",
            mime="text/html",
            use_container_width=True
        )


with tab8:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")


