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
    "Permis C",
    "Permis C et caravane",
    "Permis C",
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]


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
    st.info("Espace reserve pour la simulation de trajectoire d'un vehicule leger.")

with tab2:
    st.header("Simulation Permis B et caravane")
    st.info("Espace reserve pour la simulation d'un vehicule articule leger avec caravane.")


# =============================================================================
# CONTENU DE L'ONGLET 3 : PERMIS C (PREMIER ATELIER - DYNAMIQUE RIGIDE)
# =============================================================================
with tab3:
    st.header("Simulation de Trajectoire - Camion Rigide Categorie C")
    st.markdown("""
    Cette section montre l'influence de la vitesse, du poids et de la geometrie sur le phenomene de chasse 
    (le decalage des roues arriere vers l'interieur du virage).
    """)

    # Configuration des parametres de controle
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
        largeur_voie = 3.5

    # Calculs Mecaniques et Dynamiques
    acceleration_laterale_g = (vitesse_ms**2) / (rayon_courbure * 9.81)

    raideur_derive_av = 150000  # N/rad
    force_laterale_av = ((masse_totale * 1000) * 9.81 * 0.5) * acceleration_laterale_g
    angle_derive_rad = force_laterale_av / raideur_derive_av

    angle_braquage_theorique_rad = np.arctan(empattement / rayon_courbure)
    angle_braquage_reel_rad = angle_braquage_theorique_rad + angle_derive_rad

    # Integration Numerique des Trajectoires
    ds = 0.05  # Pas d'espace de 5 cm
    distance_totale = rayon_courbure * np.radians(angle_virage_deg) + 20.0
    pas = int(distance_totale / ds)

    # Configuration geometrique de la route de reference (Virage parfait)
    # Generation d'un arc de cercle propre pour le centre de la route
    angles_route = np.linspace(0, np.radians(angle_virage_deg), pas)
    
    y_centre_virage = 2 * rayon_courbure
    
    # Initialisation des vecteurs d'état du camion
    x_arr = np.zeros(pas)
    y_arr = np.zeros(pas)
    theta = np.zeros(pas)

    # Positionnement initial en ligne droite (10 mètres avant l'entrée du virage)
    x_arr[0] = -10.0
    y_arr[0] = rayon_courbure
    theta[0] = 0.0

    # Simulation cinématique progressive
    for i in range(1, pas):
        # Le virage commence à X = 0 et se termine quand le cap nominal est atteint
        if x_arr[i-1] >= 0 and theta[i-1] < np.radians(angle_virage_deg):
            alpha = angle_braquage_reel_rad
            
            x_arr[i] = x_arr[i-1] + ds * np.cos(theta[i-1])
            y_arr[i] = y_arr[i-1] + ds * np.sin(theta[i-1])
            theta[i] = theta[i-1] + (ds / empattement) * np.tan(alpha - angle_derive_rad)
        elif theta[i-1] >= np.radians(angle_virage_deg):
            # Sortie de virage : prolongation en ligne droite selon le nouveau cap
            alpha = 0.0
            x_arr[i] = x_arr[i-1] + ds * np.cos(np.radians(angle_virage_deg))
            y_arr[i] = y_arr[i-1] + ds * np.sin(np.radians(angle_virage_deg))
            theta[i] = np.radians(angle_virage_deg)
        else:
            # Approche initiale en ligne droite horizontale
            alpha = 0.0
            x_arr[i] = x_arr[i-1] + ds
            y_arr[i] = rayon_courbure
            theta[i] = 0.0

    # Coordonnées de l'essieu avant du camion
    x_av = x_arr + empattement * np.cos(theta)
    y_av = y_arr + empattement * np.sin(theta)

    # Calcul de la chasse maximale mesurée
    rayons_arriere = np.sqrt(x_arr**2 + (y_arr - y_centre_virage)**2)
    rayons_avant = np.sqrt(x_av**2 + (y_av - y_centre_virage)**2)
    decalage_reel = np.max(rayons_avant) - np.min(rayons_arriere)

    # --- Bloc d'affichage graphique Matplotlib ---
    col_graphe, col_analyse = st.columns(2)

    with col_graphe:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # 1. Tracé de la chaussée (Lignes d'approche + Arcs de cercle du virage)
        t = np.linspace(0, np.radians(angle_virage_deg), 100)
        
        # Rayons des bords intérieur et extérieur de la route
        r_int = rayon_courbure - (largeur_voie / 2)
        r_ext = rayon_courbure + (largeur_voie / 2)
        
        # Portion 1 : Ligne droite d'approche (de X = -10 à X = 0)
        x_droite = np.linspace(-10, 0, 10)
        ax.plot(x_droite, np.full_like(x_droite, rayon_courbure - largeur_voie/2), color='black', linewidth=1.5)
        ax.plot(x_droite, np.full_like(x_droite, rayon_courbure + largeur_voie/2), color='black', linewidth=1.5)
        
        # Portion 2 : L'arc de cercle du virage (centré en 0, y_centre_virage)
        x_arc_int = r_int * np.sin(t)
        y_arc_int = y_centre_virage - r_int * np.cos(t)
        
        x_arc_ext = r_ext * np.sin(t)
        y_arc_ext = y_centre_virage - r_ext * np.cos(t)
        
        # Portion 3 : Ligne droite de sortie (tangente après le virage)
        x_fin_int = x_arc_int[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
        y_fin_int = y_arc_int[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
        
        x_fin_ext = x_arc_ext[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_deg))
        y_fin_ext = y_arc_ext[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_deg))
        
        # Dessin des infrastructures routières continues
        ax.plot(np.concatenate([x_droite, x_arc_int, x_fin_int]), 
                np.concatenate([np.full_like(x_droite, rayon_courbure - largeur_voie/2), y_arc_int, y_fin_int]), 
                color='black', linestyle='-', linewidth=2, label="Bord interieur de la route")
        
        ax.plot(np.concatenate([x_droite, x_arc_ext, x_fin_ext]), 
                np.concatenate([np.full_like(x_droite, rayon_courbure + largeur_voie/2), y_arc_ext, y_fin_ext]), 
                color='black', linestyle='-', linewidth=2, label="Bord exterieur de la route")
        
        # 2. Tracé des trajectoires cinématiques réelles du camion
        ax.plot(x_av, y_av, color='#e74c3c', linewidth=3, label="Trajectoire Roues AVANT")
        ax.plot(x_arr, y_arr, color='#3498db', linewidth=3, linestyle='--', label="Trajectoire Roues ARRIERE")
        
        # Segment matérialisant la position instantanée du châssis au milieu de la courbe
        mid = int(pas / 2)
        ax.plot([x_arr[mid], x_av[mid]], [y_arr[mid], y_av[mid]], color='#2c3e50', 
                linewidth=3, label=f"Chassis rigide (L = {empattement}m)")
        
        ax.set_xlabel("X (Metres)")
        ax.set_ylabel("Y (Metres)")
        ax.axis("equal")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(loc="upper left")
        
        st.pyplot(fig)
        
    with col_analyse:
        st.subheader("Indicateurs Physiques du Vehicule")
        st.metric(label="Decalage mesure (Chasse)", value=f"{decalage_reel:.2f} m")
        st.metric(label="Acceleration laterale subie", value=f"{acceleration_laterale_g:.2f} G")
        
        if acceleration_laterale_g > 0.35:
            st.error("Force laterale critique. Risque eleve de derapage ou de renversement.")
        elif acceleration_laterale_g > 0.20:
            st.warning("Force laterale marquee. Glissement des pneumatiques quantifiable.")
        else:
            st.success("Force laterale faible. Comportement stable.")

        # Generation de la chaine de texte pour le livrable eleve
        texte_rapport = f"""RAPPORT D'ATELIER - SIMULATION PERMIS C
Eleve : {st.session_state.get('prenom_var', 'PRENOM')} {st.session_state.get('nom_var', 'ELEVE')}
Classe : {st.session_state.get('classe_var', 'GROUPE')}
--------------------------------------------------
PARAMETRES DU VEHICULE :
- Empattement : {empattement} m
- Masse a vide : {masse_vide} t
- Masse du chargement : {masse_charge} t
- Masse totale : {masse_totale:.1f} t

PARAMETRES DE LA ROUTE :
- Rayon de courbure : {rayon_courbure} m
- Angle du virage : {angle_virage_deg} degres
- Vitesse definie : {vitesse_kmh} km/h

RESULTATS MESURES :
- Decalage geometrique (Chasse) : {decalage_reel:.2f} m
- Acceleration transversale : {acceleration_laterale_g:.2f} G
"""
        
        # Generation de l'intitule de fichier via votre fonction personnalisee
        nom_fichier_export = preparer_nom_fichier(nom_onglet="Permis_C")
        
        # Bouton de telechargement
        st.download_button(
            label="Exporter le rapport d'atelier (Fichier texte)",
            data=texte_rapport,
            file_name=nom_fichier_export,
            mime="text/plain",
            key="btn_download_c"
        )


# =============================================================================
# CONTENU DES ONGLETS RESTANTS
# =============================================================================
with tab4:
    st.header("Simulation Permis C et caravane")
    st.info("Espace reserve pour la simulation d'un camion rigide tractant une remorque de type caravane.")

with tab5:
    st.header("Simulation Permis C (Deuxieme Atelier)")
    st.info("Espace reserve pour le second module applique au Permis C.")












