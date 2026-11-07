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
        
        # CORRECTION SYNCHRONISATION : On utilise la cle unique "debord_init_c_final"
        angle_debord_initial_deg = st.slider("Angle de debord initial du train (degres)", 0, 20, 5, key="debord_init_c_final")
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
    
    # Configuration geometrique et devers de la route
    y_centre_virage = 2 * rayon_courbure
    
    # Prise en compte du curseur synchronise
    beta = np.radians(angle_route_deg)
    beta_debord_init = np.radians(angle_debord_initial_deg)
    
    g = 9.81
    seuil_glissement_mu = 0.35
    hauteur_cg = 1.1 + (masse_charge / masse_totale) * 0.9
    largeur_camion = 2.5

    r_int = rayon_courbure - (largeur_voie / 2)
    r_ext = rayon_courbure + (largeur_voie / 2)

    x_arr = np.zeros(pas)
    y_arr = np.zeros(pas)
    theta = np.zeros(pas)
    angle_debord = np.zeros(pas)

    x_arr[0] = -10.0
    y_arr[0] = rayon_courbure
    theta[0] = 0.0
    angle_debord[0] = float(angle_debord_initial_deg)

    evenement_detecte = "Aucun"
    index_interruption = pas - 1

    for i in range(1, pas):
        if x_arr[i-1] >= 0 and theta[i-1] < np.radians(angle_virage_deg):
            acc_lat_inst_g = (vitesse_ms**2) / (rayon_courbure * g)
            
            # INTEGRATION REELLE : L'angle de debord initial modifie l'angle effectif des roues arrière
            alpha = angle_braquage_reel_rad + beta_debord_init
            
            # Équations mecaniques sur plan incliné
            P_normale = masse_totale * 1000 * g * np.cos(beta)
            Fc_normale = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.sin(beta)
            N = P_normale + Fc_normale
            
            P_tangente = masse_totale * 1000 * g * np.sin(beta)
            Fc_tangente = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.cos(beta)
            
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            # Verifications de securite
            Moment_renversement = Fc_tangente * hauteur_cg
            Moment_stabilisateur = N * (largeur_camion / 2) + P_tangente * hauteur_cg
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte = "Basculement"
                index_interruption = i - 1
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte == "Aucun":
                evenement_detecte = "Glissement"
        else:
            acc_lat_inst_g = 0.0
            alpha = 0.0

        if x_arr[i-1] >= 0 and theta[i-1] < np.radians(angle_virage_deg):
            x_arr[i] = x_arr[i-1] + ds * np.cos(theta[i-1])
            y_arr[i] = y_arr[i-1] + ds * np.sin(theta[i-1])
            theta[i] = theta[i-1] + (ds / empattement) * np.tan(alpha - angle_derive_rad)
            
            changement_cap_deg = np.degrees(theta[i] - theta[i-1])
            angle_debord[i] = angle_debord[i-1] + (changement_cap_deg * (empattement / rayon_courbure))
        elif theta[i-1] >= np.radians(angle_virage_deg):
            x_arr[i] = x_arr[i-1] + ds * np.cos(np.radians(angle_virage_deg))
            y_arr[i] = y_arr[i-1] + ds * np.sin(np.radians(angle_virage_deg))
            theta[i] = np.radians(angle_virage_deg)
            angle_debord[i] = max(0.0, angle_debord[i-1] - 0.5)
        else:
            x_arr[i] = x_arr[i-1] + ds
            y_arr[i] = rayon_courbure
            theta[i] = 0.0
            angle_debord[i] = float(angle_debord_initial_deg)
            
        # 3. Verification geometrique du franchissement de voie
        x_av_inst = x_arr[i] + empattement * np.cos(theta[i])
        y_av_inst = y_arr[i] + empattement * np.sin(theta[i])
        if x_arr[i] >= 0:
            r_av = np.sqrt(x_av_inst**2 + (y_av_inst - y_centre_virage)**2)
            r_ar = np.sqrt(x_arr[i]**2 + (y_arr[i] - y_centre_virage)**2)
            if (r_av > r_ext or r_av < r_int or r_ar > r_ext or r_ar < r_int) and evenement_detecte == "Aucun":
                evenement_detecte = "Sortie de route"

    # Tronquage des structures selon la duree reelle avant accident
    x_arr = x_arr[:index_interruption+1]
    y_arr = y_arr[:index_interruption+1]
    theta = theta[:index_interruption+1]
    angle_debord = angle_debord[:index_interruption+1]

    x_av = x_arr + empattement * np.cos(theta)
    y_av = y_arr + empattement * np.sin(theta)

    if len(x_arr) > 1 and evenement_detecte != "Basculement":
        rayons_arriere = np.sqrt(x_arr**2 + (y_arr - y_centre_virage)**2)
        rayons_avant = np.sqrt(x_av**2 + (y_av - y_centre_virage)**2)
        decalage_reel = np.max(rayons_avant) - np.min(rayons_arriere)
    else:
        decalage_reel = 0.0

    # Definition explicite de t_route utilisee pour tracer la route fixe
    t_route = np.linspace(0, np.radians(angle_virage_deg), 100)

    # CORRECTION : Re-introduction des lignes de calcul de sortie de courbe manquantes
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

    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Dynamiques")
        zone_metrique_chasse = st.empty()
        zone_metrique_debord = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        declencher_animation = st.button("Lancer la simulation pas-a-pas")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_arr), max(1, len(x_arr) // 40)) if declencher_animation else [len(x_arr) - 1]

    for k in points_animation:
        # Trace standard Matplotlib de la trajectoire au sol
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int, y_route_int, color='black', linewidth=2)
        ax_anim.plot(x_route_ext, y_route_ext, color='black', linewidth=2)
        if k > 0:
            ax_anim.plot(x_av[:k], y_av[:k], color='#e74c3c', linewidth=2)
            ax_anim.plot(x_arr[:k], y_arr[:k], color='#3498db', linewidth=2, linestyle='--')
        
        cos_tk, sin_tk = np.cos(theta[k]), np.sin(theta[k])
        arriere_gauche = [x_arr[k] - 1.0 * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk - (largeur_camion/2) * cos_tk]
        arriere_droit  = [x_arr[k] - 1.0 * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk + (largeur_camion/2) * cos_tk]
        avant_droit    = [x_arr[k] + (empattement + 1.0) * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk + (largeur_camion/2) * cos_tk]
        avant_gauche   = [x_arr[k] + (empattement + 1.0) * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk - (largeur_camion/2) * cos_tk]
        ax_anim.add_patch(Polygon(np.array([arriere_gauche, arriere_droit, avant_droit, avant_gauche]), closed=True, facecolor='#2c3e50', alpha=0.8))
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext) + 5)
        conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # =============================================================================
        # TRACÉ DU SCHÉMA DES FORCES CORRIGÉ ET COMPATIBLE (VUE ARRIÈRE)
        # =============================================================================
        fig_forces, ax_f = plt.subplots(figsize=(5, 4))
        
        # Ligne d'assiette du sol deversé
        ax_f.plot([-2, 2], [-2 * np.sin(beta), 2 * np.sin(beta)], color='black', linewidth=3)
        
        # Chassis du camion orienté selon l'angle beta
        cam_box = np.array([[-largeur_camion/2, 0], [largeur_camion/2, 0], [largeur_camion/2, hauteur_cg * 1.4], [-largeur_camion/2, hauteur_cg * 1.4]])
        R_mat = np.array([[np.cos(beta), -np.sin(beta)], [np.sin(beta), np.cos(beta)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        # Positionnement exact du Centre de Gravite G
        G_coord = np.dot(np.array([0, hauteur_cg]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        # Calcul des coordonnees réelles au sol des pneumatiques gauche et droit tournes
        roue_gauche = np.dot(np.array([-largeur_camion/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_camion/2, 0]), R_mat.T)
        
        # Dessin des roues sous la carrosserie pour la logique visuelle
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=150, marker='s', zorder=4)
        
        # Normalisation d'echelle des vecteurs forces
        f_scale = 1.0 / (masse_totale * 1000 * g)
        val_P = masse_totale * 1000 * g
        val_Fc = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) if x_arr[k] >= 0 else 0.0
        
        # CORRECTION EFFECTUÉE : Extraction explicite de [0] et [1] pour chaque coordonnée
        # Application des forces au CG : Poids (Vertical bas) et Centrifuge (Horizontal droit)
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        # Calcul de la repartition du poids et effet centrifuge sous les pneus
        val_N_totale = val_P * np.cos(beta) + val_Fc * np.sin(beta)
        val_Ff_totale = val_Fc * np.cos(beta) - val_P * np.sin(beta) if x_arr[k] >= 0 else 0.0
        
        # Tracé des forces de contact appliquées sous chaque pneumatique (indexés explicitement)
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

        # Affichage dynamique des indicateurs textuels
        decalage_inst = np.abs(np.sqrt(x_av[k]**2 + (y_av[k] - y_centre_virage)**2) - np.sqrt(x_arr[k]**2 + (y_arr[k] - y_centre_virage)**2)) if x_arr[k] >= 0 else 0.0
        zone_metrique_chasse.metric(label="Decalage de chasse instantane", value=f"{decalage_inst:.2f} m")
        
        # CORRECTION : Affichage de la valeur reelle stockee a l'index k
        zone_metrique_debord.metric(label="Angle de debord du train AR", value=f"{angle_debord[k]:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms**2)/(rayon_courbure*g) if x_arr[k]>=0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)
    animation_terminee = True

    # COPIER-COLLER LE BLOC ICI, JUSTE APRES L'ANIMATION :
    if not declencher_animation or animation_terminee:
        zone_metrique_chasse.metric(label="Decalage de chasse maximal", value=f"{decalage_reel:.2f} m")
        angle_max_atteint = np.max(angle_debord)
        zone_metrique_debord.metric(label="Angle de debord maximal du train AR", value=f"{angle_max_atteint:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_g:.2f} G")
            
    # Gestion de l'affichage de fin de parcours (Arret sur accident ou Graphique zoomable)
    if evenement_detecte == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementCE.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).")
            except Exception:
                st.error("Fichier basculementCE.jpg introuvable.")
        with col_analyse:
            zone_alerte.error("ACCIDENT : Le camion a bascule. Le devers de la route n'a pas suffi a compenser l'effet centrifuge.")
    else:
        import plotly.graph_objects as go
        fig_plotly = go.Figure()
        fig_plotly.add_trace(go.Scatter(x=x_route_int, y=y_route_int, name="Bord interieur", line=dict(color='black', width=2)))
        fig_plotly.add_trace(go.Scatter(x=x_route_ext, y=y_route_ext, name="Bord exterieur", line=dict(color='black', width=2)))
        fig_plotly.add_trace(go.Scatter(x=x_av, y=y_av, name="Roues AVANT", line=dict(color='#e74c3c', width=3)))
        fig_plotly.add_trace(go.Scatter(x=x_arr, y=y_arr, name="Roues ARRIERE", line=dict(color='#3498db', width=3, dash='dash')))
        fig_plotly.update_layout(xaxis=dict(scaleanchor="y", scaleratio=1), hovermode="closest", height=500)
        conteneur_graphique.plotly_chart(fig_plotly, use_container_width=True)

        with col_analyse:
            if evenement_detecte == "Glissement":
                zone_alerte.warning("GLISSEMENT : L'effort lateral demande a surpasse l'adherence disponible (Derapage).")
            elif evenement_detecte == "Sortie de route":
                zone_alerte.warning("SORTIE DE VOIE : Le gabarit a franchi les marquages au sol.")
            else:
                zone_alerte.success("TRAJECTOIRE REUSSITE : Le camion est reste stable dans sa voie.")

    # Bloc final d'exportation du livrable eleve
    with col_analyse:
        texte_rapport = f"RAPPORT D'ATELIER\nStatut final : {evenement_detecte}\nDecalage de chasse maximal : {decalage_reel:.2f} m\nAngle de debord maximal : {np.max(angle_debord):.1f} degres\n"
        st.download_button(
            label="Exporter le rapport d'atelier (Fichier texte)",
            data=texte_rapport,
            file_name=preparer_nom_fichier(nom_onglet="Permis_C"),
            mime="text/plain",
            key="btn_download_c_final"
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












