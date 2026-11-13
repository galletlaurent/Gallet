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
    "Loi de la Reflexion",
    "SPECTRE DE PEPPER",
    "Simulation Retroviseurs",
    "Le Periscope du sous-marin",
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
tab9 = onglets[9] 


def mettre_a_jour_illusion_matplotlib():
    """Moteur d'illusion HUD : simulation automobile reelle avec projecteur vertical.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du laboratoire d'origine
    w = 400
    h = 240
    x0, y0 = 200.0, 115.0  # Point d'impact fixe au centre du pare-brise

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12,8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du curseur d'angle depuis le session_state de Streamlit
    angle_deg = st.session_state.get("slider_angle_ill", 45.0)
    angle_rad = math.radians(angle_deg)

    # =========================================================================
    # 1. LE PROJECTEUR AUTOMOBILE (Placé verticalement sous le pare-brise)
    # =========================================================================
    x_ecran, y_ecran = x0, 205.0
    # Boîtier du projecteur HUD encastre
    proj_box = patches.Rectangle((x_ecran - 25, y_ecran), 50, 12, facecolor="#334155", edgecolor="#1e293b", zorder=3)
    proj_lens = patches.Rectangle((x_ecran - 18, y_ecran - 4), 36, 4, facecolor="#0284c7", edgecolor="none", zorder=3)
    ax.add_patch(proj_box)
    ax.add_patch(proj_lens)
    ax.text(x_ecran, y_ecran - 2, "50", color="white", fontsize=6, fontweight="bold", ha="center", va="bottom", zorder=4)
    ax.text(x_ecran, y_ecran + 22, "Projecteur HUD", color="#475569", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 2. LA ROUTE RÉELLE D'HORIZON (Centrée au milieu à droite)
    # =========================================================================
    x_route, y_route = 330.0, 90.0  
    route_rect = patches.Rectangle((x_route - 40, y_route), 80, 50, facecolor="#64748b", edgecolor="none", zorder=1)
    ax.add_patch(route_rect)
    ax.plot([x_route, x_route], [y_route, y_route + 50], color="white", lw=1.5, linestyle=(0, (4, 4)), zorder=2)
    ax.text(x_route, y_route + 56, "Axe de la route", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 3. LA PLANCHE DE BORD HORIZONTALE ET LE PARE-BRISE MOBILE
    # =========================================================================
    # Table de bord gauche qui cache la vue directe
    bord_rect = patches.Rectangle((20, y_ecran - 4), x_ecran - 45, 16, facecolor="#1e293b", edgecolor="none", zorder=2)
    ax.add_patch(bord_rect)
    
    # Pare-brise mobile turquoise incline
    dx_m = 70 * math.cos(angle_rad)
    dy_m = 70 * math.sin(angle_rad)
    ax.plot([x0 - dx_m, x0 + dx_m], [y0 - dy_m, y0 + dy_m], color="#0d9488", lw=3, zorder=3)
    ax.text(x0 + dx_m + 5, y0 + dy_m + 5, "miroir", color="#0d9488", fontsize=7, fontweight="bold", ha="left", va="center")

    # =========================================================================
    # 4. MOTEUR PHYSIQUE VECTORIEL (PROJECTEUR VERTICAL)
    # =========================================================================
    # Le rayon émis monte verticalement
    uix, uiy = 0.0, -1.0
    ax.annotate("", xy=(x0, y0), xytext=(x_ecran, y_ecran - 4), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_ecran + 10, (y_ecran + y0)/2, "Rayon incident", color="#ef4444", fontsize=7, style="italic", ha="left", va="center")

    # La Normale pivotante a 90° face au rayon vertical
    unx = -math.sin(angle_rad)
    uny = math.cos(angle_rad)
    ax.plot([x0 - 50 * unx, x0 + 50 * unx], [y0 - 50 * uny, y0 + 50 * uny], color="#94a3b8", lw=1.2, linestyle=(0, (3, 3)))
    ax.text(x0 + 55 * unx, y0 + 55 * uny, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="center", va="center")

    # Lois de réflexion de Descartes (Vecteur réfléchi)
    dot_product = uix * unx + uiy * uny
    urx = uix - 2.0 * dot_product * unx
    ury = uiy - 2.0 * dot_product * uny

    # Tracé du Rayon Réfléchi vers le conducteur a gauche
    x_conducteur = x0 + urx * 130.0
    y_conducteur = y0 + ury * 130.0
    ax.annotate("", xy=(x_conducteur, y_conducteur), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_conducteur - 5, y_conducteur, "Conducteur ", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right", va="center")
    ax.text(x0 - 40, y0 - 30, "Rayon reflechi", color="#b91c1c", fontsize=7, style="italic", ha="left", va="bottom")

    # Prolongement virtuel en ligne droite vers la route
    x_illusion = x0 - urx * 130.0
    y_illusion = y0 - ury * 130.0
    ax.plot([x0, x_illusion], [y0, y_illusion], color="#94a3b8", lw=1, linestyle=(0, (2, 2)))

    # =========================================================================
    # 5. PROJECTION DE L'HOLOGRAMME HUD (PILE SUR LA ROUTE À 45°)
    # =========================================================================
    hud_box = patches.Rectangle((x_illusion - 18, y_illusion - 12), 36, 16, fill=False, edgecolor="#22c55e", lw=1.5, linestyle=(0, (2, 2)), zorder=4)
    ax.add_patch(hud_box)
    ax.text(x_illusion, y_illusion - 4, "50", color="#22c55e", fontsize=10, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(x_illusion, y_illusion - 18, "HUD", color="#22c55e", fontsize=7, style="italic", ha="center", va="bottom")

    # Condition de validation mecanique de l'illusion d'optique
    if 44.0 <= angle_deg <= 46.0:
        msg_ill = "ALIGNEMENT HUD OK : La vitesse est projetee pile sur la route !"
        couleur_ill = "#16a34a"
    else:
        msg_ill = "DEREGLE : L'hologramme sort de la zone de vision."
        couleur_ill = "#ef4444"

    # Affichage des en-têtes de statut textuels de Matplotlib
    ax.text(20, h - 220, "AFFICHAGE TETE HAUTE (HUD)", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(20, h - 205, msg_ill, color=couleur_ill, fontsize=7, fontweight="bold", ha="left", va="top")

    # Sauvegarde des donnees numeriques de simulation dans le bloc de l'Atelier 3
    st.session_state.opt3_txt_box_ill = (
        f"Mesures du HUD :\n"
        f"• Miroir i = {angle_deg:.1f}°\n"
        f"• Reflexion i' = {angle_deg:.1f}°\n"
        f"• Loi optique : i = i'\n"
        f"• Point X={x_illusion:.1f} / Y={y_illusion:.1f}"
    )

    return fig


def mettre_a_jour_reflexion_pure_matplotlib():
    """Moteur physique de reflexion pure : entierement verrouille sur le curseur d'incidence.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions de securite fixes constantes
    w, h = 400, 240
    x0, y0 = 200.0, 180.0  

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du vrai curseur d'incidence synchronise
    theta_i_deg = st.session_state.get("slider_angle_ref_i", 45.0)
    theta_i_rad = math.radians(theta_i_deg)

    # Support hachure du miroir plan horizontal
    miroir_fond = patches.Rectangle((0, y0), w, h - y0, facecolor="#1e293b", edgecolor="none", alpha=0.5)
    ax.add_patch(miroir_fond)
    ax.plot([15, w - 15], [y0, y0], color="#cbd5e1", lw=3, zorder=3) 
    
    # Hachures mecaniques
    for x_hach in range(20, int(w - 15), 12):
        ax.plot([x_hach, x_hach - 6], [y0, y0 + 8], color="#64748b", lw=1)

    # Tracé de la ligne de repère : La Normale verticale
    ax.plot([x0, x0], [15, y0], color="#94a3b8", linestyle=(0, (4, 4)), lw=1.5)
    ax.text(x0 + 8, 25, "Normale", color="#64748b", fontsize=8, fontweight="bold", ha="left", va="top")

    # Tracé du Rayon Incident (i)
    x_inc = x0 - 130 * math.sin(theta_i_rad)
    y_inc = y0 - 130 * math.cos(theta_i_rad)
    couleur_laser = "#ef4444" 
    ax.annotate("", xy=(x0, y0), xytext=(x_inc, y_inc), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
    ax.text(x_inc - 8, y_inc, "Rayon incident", color=couleur_laser, fontsize=8, fontweight="bold", style="italic", ha="right", va="center")

    # Tracé du Rayon Réfléchi (i')
    x_ref = x0 + 130 * math.sin(theta_i_rad)
    y_ref = y0 - 130 * math.cos(theta_i_rad)
    ax.annotate("", xy=(x_ref, y_ref), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color=couleur_laser, lw=2.5), zorder=4)
    ax.text(x_ref + 8, y_ref, "Rayon reflechi", color="#cbd5e1", fontsize=8, fontweight="bold", ha="left", va="center")

    # Arcs geometriques des angles i et i' via des patches Arc de Matplotlib
    arc_i = patches.Arc((x0, y0), 70, 70, angle=270, theta1=0, theta2=theta_i_deg, edgecolor=couleur_laser, lw=1.5)
    arc_iprime = patches.Arc((x0, y0), 70, 70, angle=270, theta1=-theta_i_deg, theta2=0, edgecolor="#cbd5e1", lw=1.5)
    ax.add_patch(arc_i)
    ax.add_patch(arc_iprime)
    
    ax.text(x0 - 18, y0 - 42, "i", color=couleur_laser, fontsize=9, fontweight="bold", ha="center")
    ax.text(x0 + 18, y0 - 42, "i'", color="#cbd5e1", fontsize=9, fontweight="bold", ha="center")

    # Titres généraux de l'Atelier 3
    ax.text(20, 20, "LOI DE LA REFLEXION (i = i')", color="#38bdf8", fontsize=9, fontweight="bold", ha="left")
    
    # Generation de la boite de resultats synchrone
    st.session_state.opt3_txt_box_ref = (
        f"Mesures Miroir Plan :\n"
        f"• Angle d'incidence i = {theta_i_deg:.1f}°\n"
        f"• Angle de reflexion i' = {theta_i_deg:.1f}°\n"
        f"• Statut : i = i' verifie"
    )

    return fig

def ajouter_mesure_reflexion_pure_streamlit():
    """Capte la valeur de la reglette i et l'ajoute de maniere permanente dans les listes de session."""
    theta_i = st.session_state.get("slider_angle_ref_i", 45.0)
    
    # Memorisation etanche dans vos tableaux de stockage de reflexion
    if "mesures_reflexion_i" in st.session_state:
        st.session_state.mesures_reflexion_i.append(theta_i)
        st.session_state.mesures_reflexion_iprime.append(theta_i)



def mettre_a_jour_illusion_matplotlib():
    """Moteur d'illusion HUD : simulation automobile reelle avec projecteur vertical.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # VERROUILLÉ : Dimensions fixes constantes du laboratoire
    w = 400
    h = 240
    x0, y0 = 200.0, 115.0  # Point d'impact fixe au centre du pare-brise

    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # RECONNEXION DIRECTE SUR LE CURSEUR DU LABORATOIRE VISUEL DE GAUCHE
    angle_deg = st.session_state.get("slider_angle_ill_quiz", 45.0)
    angle_rad = math.radians(angle_deg)

    
    # =========================================================================
    # 1. LE PROJECTEUR AUTOMOBILE (Placé verticalement sous le pare-brise)
    # =========================================================================
    x_ecran, y_ecran = x0, 205.0
    # Boîtier du projecteur HUD encastre
    proj_box = patches.Rectangle((x_ecran - 25, y_ecran), 50, 12, facecolor="#334155", edgecolor="#1e293b", zorder=3)
    proj_lens = patches.Rectangle((x_ecran - 18, y_ecran - 4), 36, 4, facecolor="#0284c7", edgecolor="none", zorder=3)
    ax.add_patch(proj_box)
    ax.add_patch(proj_lens)
    ax.text(x_ecran, y_ecran - 2, "50", color="white", fontsize=6, fontweight="bold", ha="center", va="bottom", zorder=4)
    ax.text(x_ecran, y_ecran + 22, "Projecteur HUD", color="#475569", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 2. LA ROUTE RÉELLE D'HORIZON (Centrée au milieu à droite)
    # =========================================================================
    x_route, y_route = 330.0, 90.0  
    route_rect = patches.Rectangle((x_route - 40, y_route), 80, 50, facecolor="#64748b", edgecolor="none", zorder=1)
    ax.add_patch(route_rect)
    ax.plot([x_route, x_route], [y_route, y_route + 50], color="white", lw=1.5, linestyle=(0, (4, 4)), zorder=2)
    ax.text(x_route, y_route + 56, "Axe de la route", color="#cbd5e1", fontsize=7, fontweight="bold", ha="center", va="top")

    # =========================================================================
    # 3. LA PLANCHE DE BORD HORIZONTALE ET LE PARE-BRISE MOBILE
    # =========================================================================
    bord_rect = patches.Rectangle((20, y_ecran - 4), x_ecran - 45, 16, facecolor="#1e293b", edgecolor="none", zorder=2)
    ax.add_patch(bord_rect)
    
    # Pare-brise mobile turquoise incline
    dx_m = 70 * math.cos(angle_rad)
    dy_m = 70 * math.sin(angle_rad)
    ax.plot([x0 - dx_m, x0 + dx_m], [y0 - dy_m, y0 + dy_m], color="#0d9488", lw=3, zorder=3)
    ax.text(x0 + dx_m + 5, y0 + dy_m + 5, "Pare-brise", color="#0d9488", fontsize=7, fontweight="bold", ha="left", va="center")

    # =========================================================================
    # 4. MOTEUR PHYSIQUE VECTORIEL (PROJECTEUR VERTICAL)
    # =========================================================================
    uix, uiy = 0.0, -1.0
    ax.annotate("", xy=(x0, y0), xytext=(x_ecran, y_ecran - 4), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_ecran + 10, (y_ecran + y0)/2, "Rayon incident", color="#ef4444", fontsize=7, style="italic", ha="left", va="center")

    unx = -math.sin(angle_rad)
    uny = math.cos(angle_rad)
    ax.plot([x0 - 50 * unx, x0 + 50 * unx], [y0 - 50 * uny, y0 + 50 * uny], color="#94a3b8", lw=1.2, linestyle=(0, (3, 3)))
    ax.text(x0 + 55 * unx, y0 + 55 * uny, "Normale", color="#64748b", fontsize=7, fontweight="bold", ha="center", va="center")

    dot_product = uix * unx + uiy * uny
    urx = uix - 2.0 * dot_product * unx
    ury = uiy - 2.0 * dot_product * uny

    x_conducteur = x0 + urx * 130.0
    y_conducteur = y0 + ury * 130.0
    ax.annotate("", xy=(x_conducteur, y_conducteur), xytext=(x0, y0), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2), zorder=4)
    ax.text(x_conducteur - 5, y_conducteur, "Conducteur ", color="#cbd5e1", fontsize=8, fontweight="bold", ha="right", va="center")
    ax.text(x0 - 40, y0 - 30, "Rayon reflechi", color="#b91c1c", fontsize=7, style="italic", ha="left", va="bottom")

    x_illusion = x0 - urx * 130.0
    y_illusion = y0 - ury * 130.0
    ax.plot([x0, x_illusion], [y0, y_illusion], color="#94a3b8", lw=1, linestyle=(0, (2, 2)))

    # =========================================================================
    # 5. PROJECTION DE L'HOLOGRAMME HUD (PILE SUR LA ROUTE À 45°)
    # =========================================================================
    hud_box = patches.Rectangle((x_illusion - 18, y_illusion - 12), 36, 16, fill=False, edgecolor="#22c55e", lw=1.5, linestyle=(0, (2, 2)), zorder=4)
    ax.add_patch(hud_box)
    ax.text(x_illusion, y_illusion - 4, "50", color="#22c55e", fontsize=10, fontweight="bold", ha="center", va="center", zorder=4)
    ax.text(x_illusion, y_illusion - 18, "HUD", color="#22c55e", fontsize=7, style="italic", ha="center", va="bottom")

    if 44.0 <= angle_deg <= 46.0:
        msg_ill = "ALIGNEMENT HUD OK : La vitesse est projetee pile sur la route !"
        couleur_ill = "#16a34a"
    else:
        msg_ill = "DEREGLE : L'hologramme sort de la zone de vision."
        couleur_ill = "#ef4444"

    ax.text(20, h - 220, "AFFICHAGE TETE HAUTE (HUD)", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(20, h - 205, msg_ill, color=couleur_ill, fontsize=7, fontweight="bold", ha="left", va="top")

    st.session_state.opt3_txt_box_ill = (
        f"Mesures du HUD :\n"
        f"• Miroir i = {angle_deg:.1f}°\n"
        f"• Reflexion i' = {angle_deg:.1f}°\n"
        f"• Loi optique : i = i'\n"
        f"• Point X={x_illusion:.1f} / Y={y_illusion:.1f}"
    )

    return fig

def mettre_a_jour_periscope_matplotlib():
    """Moteur physique de reflexion : calcule et dessine le periscope du sous-marin.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions fixes constantes du laboratoire
    w = 600
    h = 280
    x0 = 300.0  # Axe central vertical exact du tube du periscope (600 / 2)

    # Creation de la figure Matplotlib sombre ajustee en taille
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien indispensable du repere inverse Tkinter
    ax.axis("off")

    # Lecture du curseur d'angle depuis le session_state de Streamlit
    angle_miroir_deg = st.session_state.get("slider_angle_periscope", 45.0)
    angle_miroir_rad = math.radians(angle_miroir_deg)

    # Hauteurs fixes des deux miroirs pour s'aligner sur la double reflexion
    y_miroir1 = 90.0
    y_miroir2 = 180.0
    epaisseur_tube_px = y_miroir2 - y_miroir1

    # =========================================================================
    # 1. DESSIN DU DECOR : LA MER ET LE TUBE DU PÉRISCOPE
    # =========================================================================
    # La mer bleue en fond bas (S'aligne sur la strate basse du dioptre)
    mer_rect = patches.Rectangle((15, y_miroir2), w - 30, h - 10 - y_miroir2, facecolor="#0284c7", edgecolor="none", zorder=1)
    ax.add_patch(mer_rect)
    
    # Tube vertical metallique du periscope (Centre sur x0)
    tube_vert = patches.Rectangle((x0 - 25, 10), 50, y_miroir2 + 13, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    # Coude amont d'entree (a gauche)
    coude_amont = patches.Rectangle((x0 - 120, y_miroir1 - 25), 95, 50, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    # Coude aval de sortie vers l'oeil (a droite)
    coude_aval = patches.Rectangle((x0 + 25, y_miroir2 - 25), 95, 50, facecolor="#cbd5e1", edgecolor="#475569", lw=1.5, zorder=2)
    
    ax.add_patch(tube_vert)
    ax.add_patch(coude_amont)
    ax.add_patch(coude_aval)

    # Masquage des jointures internes pour un rendu de canalisation propre et fluide
    ax.add_patch(patches.Rectangle((x0 - 23, 12), 46, y_miroir2 - 12, facecolor="#cbd5e1", edgecolor="none", zorder=2))
    ax.add_patch(patches.Rectangle((x0 - 118, y_miroir1 - 23), 95, 46, facecolor="#cbd5e1", edgecolor="none", zorder=2))
    ax.add_patch(patches.Rectangle((x0 + 23, y_miroir2 - 23), 95, 46, facecolor="#cbd5e1", edgecolor="none", zorder=2))

    # =========================================================================
    # 2. POSITIONNEMENT DES DEUX MIROIRS PLANS
    # =========================================================================
    # Miroir 1 superieur (Incline a l'impact vertical de l'entree)
    ax.plot([x0 - 25, x0 + 25], [y_miroir1 - 25, y_miroir1 + 25], color="#475569", lw=4, zorder=3)
    ax.text(x0 + 32, y_miroir1 - 15, "Miroir 1", color="#cbd5e1", fontsize=7, fontweight="bold", ha="left", va="center", zorder=4)
    
    # Miroir 2 inferieur (Incline a l'impact vertical de la sortie)
    ax.plot([x0 - 25, x0 + 25], [y_miroir2 - 25, y_miroir2 + 25], color="#475569", lw=4, zorder=3)
    ax.text(x0 - 32, y_miroir2 + 15, "Miroir 2", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right", va="center", zorder=4)

    # =========================================================================
    # 3. TRACE GEOMETRIQUE DES RAYONS LASER (i = r)
    # =========================================================================
    angle_deviation_deg = angle_miroir_deg * 2.0
    angle_deviation_rad = math.radians(angle_deviation_deg)

    # Rayon 1 : Faisceau incident horizontal exterieur arrivant de gauche
    ax.annotate("", xy=(x0, y_miroir1), xytext=(15, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
    ax.text(25, y_miroir1 - 10, "Rayon incident", color="#ef4444", fontsize=8, fontweight="bold", style="italic", ha="left", va="bottom")

    # Calcul de la trajectoire descendante dans le tube vertical
    dx_faisceau = epaisseur_tube_px * math.tan(math.radians(90.0 - angle_deviation_deg)) if angle_deviation_deg != 90.0 else 0
    x_impact2 = x0 + dx_faisceau
    y_impact2 = y_miroir2

    # Rayon 2 : Faisceau reflechi intermediaire circulant dans le tube vertical
    ax.annotate("", xy=(x_impact2, y_impact2), xytext=(x0, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)

    # Rayon 3 : Faisceau emergent final vers l'oeil de l'etudiant
    angle_deviation_deg = angle_miroir_deg * 2.0
    
    # Rayon 1 : Faisceau incident horizontal exterieur arrivant de gauche
    ax.annotate("", xy=(x0, y_miroir1), xytext=(15, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
    ax.text(25, y_miroir1 - 10, "Rayon incident", color="#ef4444", fontsize=8, fontweight="bold", style="italic", ha="left", va="bottom")

    # Calcul de la trajectoire descendante dans le tube vertical
    dx_faisceau = epaisseur_tube_px * math.tan(math.radians(90.0 - angle_deviation_deg)) if angle_deviation_deg != 90.0 else 0
    x_impact2 = x0 + dx_faisceau
    y_impact2 = y_miroir2

    # Rayon 2 : Faisceau genie intermediaire circulant dans le tube vertical
    ax.annotate("", xy=(x_impact2, y_impact2), xytext=(x0, y_miroir1), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)

    # Rayon 3 : Faisceau emergent final recalcule selon l'inclinaison reelle
    if 44.0 <= angle_miroir_deg <= 46.0:
        # Alignement geometrique parfait (90 degres de cassure vers l'oeil)
        ax.annotate("", xy=(w - 15, y_impact2), xytext=(x_impact2, y_impact2), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
        ax.text(w - 25, y_impact2 - 10, "Oeil du Marin (Vision OK)", color="#15803d", fontsize=8, fontweight="bold", ha="right", va="bottom")
        msg_status = "PERISCOPE ALIGNE : Les faisceaux de sortie sont paralleles."
        couleur_status = "#0d9488"
    else:
        # DEVIATION RECOUPÉE EN DIRECT : L'angle de sortie depend directement de la loi des miroirs
        # L'angle de sortie par rapport a l'horizontale vaut (90 - 2 * delta_angle)
        angle_sortie_rad = math.radians(90.0 - (angle_miroir_deg - 45.0) * 2.0)
        
        x_perdu = x_impact2 + 120.0 * math.sin(angle_sortie_rad)
        y_perdu = y_impact2 + 120.0 * math.cos(angle_sortie_rad)
        
        # Securite pour confiner le tracé dans la structure basse si le faisceau plonge
        if y_perdu > h - 15:
            y_perdu = h - 15
            
        ax.annotate("", xy=(x_perdu, y_perdu), xytext=(x_impact2, y_impact2), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5), zorder=5)
        ax.text(w - 25, y_miroir2 - 10, "Faisceau obstrue", color="#ef4444", fontsize=8, fontweight="bold", ha="right", va="bottom")
        msg_status = "ERREUR D'ALIGNEMENT : Le rayon percute la structure."
        couleur_status = "#ef4444"

    # CORRECTION : Titre singulier propre sans lettre parasite
    ax.text(25, 20, "LE PÉRISCOPE", color="#38bdf8", fontsize=9, fontweight="bold", ha="left", va="top")
    ax.text(25, 35, msg_status, color=couleur_status, fontsize=7, fontweight="bold", ha="left", va="top")

    # Legendes des milieux ancrees fixement a l'extreme droite (X=575)
    ax.text(w - 25, 20, "Milieu 1 : Air (n=1.00)", color="#94a3b8", fontsize=7, fontweight="bold", ha="right")
    ax.text(w - 25, y_miroir1 + 15, "Structure : Metal opaque", color="#475569", fontsize=7, fontweight="bold", ha="right")
    ax.text(w - 25, h - 20, "Milieu 3 : Eau de mer (n=1.33)", color="#cbd5e1", fontsize=7, fontweight="bold", ha="right")

    # Sauvegarde du bloc de texte technique pour la boite d'information
    st.session_state.opt3_txt_box_periscope = (
        f"Periscope :\n"
        f"• Miroir 1 = {angle_miroir_deg:.1f}°\n"
        f"• Miroir 2 = {angle_miroir_deg:.1f}°\n"
        f"• Reflexion i=r = {angle_miroir_deg:.1f}°\n"
        f"• Deviation = {angle_deviation_deg:.1f}°"
    )

    return fig

def mettre_a_jour_retroviseurs_matplotlib():
    """Moteur physique : Calcule les lois de reflexion de Descartes avec conversion en radians.
    Genere une figure Matplotlib haute definition synchrone pour Streamlit.
    """
    import math
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    # Dimensions stables calquees sur le Canvas Tkinter d'origine
    w = 740
    h = 260
    
    # Creation de la figure Matplotlib sombre
    fig, ax = plt.subplots(figsize=(12, 8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Maintien du repere inversé indispensable de Tkinter
    ax.axis("off")

    # Positionnement de la voiture (Recentré bas pour laisser de la place au champ arriere)
    cx, cy = w / 2.0, h / 2.0 + 35.0
    w_voiture, h_voiture = 110.0, 150.0
    
    # Tracé des lignes de delimitation de la route
    ax.plot([130, 130], [0, h], color="#475569", lw=1.5, linestyle=(0, (6, 6)))
    ax.plot([w - 130, w - 130], [0, h], color="#475569", lw=1.5, linestyle=(0, (6, 6)))

    # Carrosserie grise de la voiture
    voiture_rect = patches.Rectangle(
        (cx - w_voiture/2, cy - h_voiture/2), w_voiture, h_voiture,
        facecolor="#334155", edgecolor="#cbd5e1", lw=2, zorder=3
    )
    ax.add_patch(voiture_rect)
    
    # Vitrages (Pare-brise en bas / Lunette arriere en haut)
    ax.plot([cx - w_voiture/2 + 6, cx + w_voiture/2 - 6], [cy + h_voiture/4, cy + h_voiture/4], color="#94a3b8", lw=3, zorder=4)
    ax.plot([cx - w_voiture/2 + 6, cx + w_voiture/2 - 6], [cy - h_voiture/3, cy - h_voiture/3], color="#94a3b8", lw=3, zorder=4)

    # =========================================================================
    # RECOVERY DES COMPOSANTS DE SESSIONS DE L'ATELIER 3
    # =========================================================================
    obs = st.session_state.get("combo_obs_retro_final", "Conducteur")
    decalage_cond = st.session_state.get("slide_siege_cond_eval", 0.0)
    decalage_pass = st.session_state.get("slide_siege_pass_eval", 0.0)

    # Récupération dynamique des curseurs d'angles de rétroviseurs révisés
    dev_g = st.session_state.get("slide_retro_g_eval", 0.0)
    dev_i = st.session_state.get("slide_retro_i_eval", 0.0)
    dev_d = st.session_state.get("slide_retro_d_eval", 0.0)

    y_cond_dynamique = (cy + 25.0) - decalage_cond
    y_pass_dynamique = (cy + 25.0) - decalage_pass

    if obs == "Conducteur":
        x_oeil, y_oeil = cx - 22.0, y_cond_dynamique
        ax.plot(x_oeil, y_oeil, marker="o", color="#2563eb", markeredgecolor="white", markersize=7, zorder=5)
        ax.text(x_oeil, y_oeil + 14, "Conducteur", color="#38bdf8", fontsize=7, fontweight="bold", ha="center", zorder=5)
        ax.plot(cx + 22, y_pass_dynamique, marker="o", color="#64748b", markersize=4, zorder=5)
    else:
        x_oeil, y_oeil = cx + 22.0, y_pass_dynamique
        ax.plot(x_oeil, y_oeil, marker="o", color="#ec4899", markeredgecolor="white", markersize=7, zorder=5)
        ax.text(x_oeil, y_oeil + 14, "Passager", color="#f472b6", fontsize=7, fontweight="bold", ha="center", zorder=5)
        ax.plot(cx - 22, y_cond_dynamique, marker="o", color="#64748b", markersize=4, zorder=5)

    # Configuration geometrique des 3 miroirs
    positions_miroirs = {
        "gauche": {"x": cx - w_voiture/2 - 10, "y": cy - h_voiture/4, "long": 16.0, "ang_base": 90.0, "dev": dev_g},
        "interne": {"x": cx, "y": cy - h_voiture/3 - 10, "long": 22.0, "ang_base": 0.0, "dev": dev_i},
        "droit": {"x": cx + w_voiture/2 + 10, "y": cy - h_voiture/4, "long": 16.0, "ang_base": -90.0, "dev": dev_d}
    }

    for nom, m in positions_miroirs.items():
        angle_miroir_rad = math.radians(m["ang_base"] + m["dev"])
        
        xa = m["x"] - (m["long"] / 2.0) * math.cos(angle_miroir_rad)
        ya = m["y"] - (m["long"] / 2.0) * math.sin(angle_miroir_rad)
        xb = m["x"] + (m["long"] / 2.0) * math.cos(angle_miroir_rad)
        yb = m["y"] + (m["long"] / 2.0) * math.sin(angle_miroir_rad)
        
        # Bras de fixation physiques de la carrosserie
        if nom == "gauche":
            ax.plot([cx - w_voiture/2, xa], [m["y"], ya], color="#cbd5e1", lw=2, zorder=3)
        elif nom == "droit":
            ax.plot([cx + w_voiture/2, xb], [m["y"], yb], color="#cbd5e1", lw=2, zorder=3)

        # Dessin de la face réfléchissante cyan
        ax.plot([xa, xb], [ya, yb], color="#06b6d4", lw=3.5, zorder=4)

        # Tracé des rayons incidents de visée (Jaune)
        ax.plot([x_oeil, xa], [y_oeil, ya], color="#f59e0b", lw=1.0, alpha=0.8, zorder=2)
        ax.plot([x_oeil, xb], [y_oeil, yb], color="#f59e0b", lw=1.0, alpha=0.8, zorder=2)

        # CALCUL TRIGONOMÉTRIQUE DES DEUX RAYONS RÉFLÉCHIS (i = r)
        ang_inc_a = math.atan2(ya - y_oeil, xa - x_oeil)
        ang_norm_a = angle_miroir_rad + math.pi / 2.0
        ang_ref_a = 2.0 * ang_norm_a - ang_inc_a - math.pi
        x_fond_a = xa + 600.0 * math.cos(ang_ref_a)
        y_fond_a = ya + 600.0 * math.sin(ang_ref_a)

        ang_inc_b = math.atan2(yb - y_oeil, xb - x_oeil)
        ang_norm_b = angle_miroir_rad + math.pi / 2.0
        ang_ref_b = 2.0 * ang_norm_b - ang_inc_b - math.pi
        x_fond_b = xb + 600.0 * math.cos(ang_ref_b)
        y_fond_b = yb + 600.0 * math.sin(ang_ref_b)

        # Test d'obstacle de la vitre arriere pour le rétroviseur interne
        passe_par_vitre = True
        if nom == "interne":
            y_vitre_arriere = cy - h_voiture / 2.0
            largeur_vitre_arriere = w_voiture - 30.0
            x_vitre_gauche = cx - largeur_vitre_arriere / 2.0
            x_vitre_droite = cx + largeur_vitre_arriere / 2.0
            
            x_int_a = xa + ((y_vitre_arriere - ya) / math.sin(ang_ref_a)) * math.cos(ang_ref_a) if math.sin(ang_ref_a) != 0 else 9999
            x_int_b = xb + ((y_vitre_arriere - yb) / math.sin(ang_ref_b)) * math.cos(ang_ref_b) if math.sin(ang_ref_b) != 0 else -9999
            
            if not (x_vitre_gauche <= x_int_a <= x_vitre_droite) or not (x_vitre_gauche <= x_int_b <= x_vitre_droite):
                passe_par_vitre = False

        # Rendu du champ visuel refléchi ou de l'angle mort obstrué
        if nom == "interne" and not passe_par_vitre:
            ax.plot([xa, x_fond_a], [ya, y_fond_a], color="#475569", lw=1.0, linestyle=":", alpha=0.6)
            ax.plot([xb, x_fond_b], [yb, y_fond_b], color="#475569", lw=1.0, linestyle=":", alpha=0.6)
        else:
            # Remplacement de create_polygon par un polygone Matplotlib bleu translucide
            poly_points = np.array([[xa, ya], [xb, yb], [x_fond_b, y_fond_b], [x_fond_a, y_fond_a]])
            champ_poly = patches.Polygon(poly_points, facecolor="#1d4ed8", alpha=0.25, edgecolor="none", zorder=1)
            ax.add_patch(champ_poly)
            
            # Tracé net des deux bordures du cône de visibilité en rouge vif
            ax.plot([xa, x_fond_a], [ya, y_fond_a], color="#ef4444", lw=1.5, zorder=2)
            ax.plot([xb, x_fond_b], [yb, y_fond_b], color="#ef4444", lw=1.5, zorder=2)

    # Affichage de la legende technique informative au bas du repere
    ax.text(15, h - 15, "Jaune : Visee | Voile Bleu : Champ de vision | Zones sombres : Angles morts", color="#94a3b8", fontsize=8, style="italic", va="center", ha="left")

    return fig

def afficher_atelier_historique_complet(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 1 (Historique) sur deux colonnes."""
    questions_hist_sources = [
        {
            "id": "qh1",
            "q": "Quel matériau était utilisé pour fabriquer les premiers miroirs dans l'Antiquité ?",
            "options": ["Le bronze ou l'obsidienne polie", "Le verre argenté industriel", "Le plastique réfléchissant"],
            "rep": "Le bronze ou l'obsidienne polie"
        },
        {
            "id": "qh2",
            "q": "Quel mathématicien grec a écrit « La Catoptrique » vers 300 av. J.-C. ?",
            "options": ["Euclide", "Pythagore", "Thalès"],
            "rep": "Euclide"
        },
        {
            "id": "qh3",
            "q": "Quelle loi fondamentale de la réflexion Euclide a-t-il énoncée dès l'Antiquité ?",
            "options": ["L'égalité des angles d'incidence et de réflexion", "La déviation de la lumière dans l'eau", "La vitesse finie de la lumière"],
            "rep": "L'égalité des angles d'incidence et de réflexion"
        },
        {
            "id": "qh4",
            "q": "Quel savant du XIe siècle est l'auteur du célèbre « Traité d'optique » (Kitab al-Manazir) ?",
            "options": ["Ibn al-Haytham (Alhazen)", "Galilée", "Johannes Kepler"],
            "rep": "Ibn al-Haytham (Alhazen)"
        },
        {
            "id": "qh5",
            "q": "Quelle erreur antique Ibn al-Haytham a-t-il corrigée grâce à ses expériences ?",
            "options": ["La lumière va de l'objet vers l'œil, et non l'inverse", "La lumière se déplace en spirale", "Les miroirs plans inversent le haut et le bas"],
            "rep": "La lumière va de l'objet vers l'œil, et non l'inverse"
        },
        {
            "id": "qh6",
            "q": "En quelle année René Descartes a-t-il publié son ouvrage « La Dioptrique » ?",
            "options": ["1637", "1515", "1789"],
            "rep": "1637"
        },
        {
            "id": "qh7",
            "q": "Quelle est la relation mathématique moderne formalisée par Descartes pour la réflexion ?",
            "options": ["i = i'", "i + i' = 90°", "i = 2 * i'"],
            "rep": "i = i'"
        },
        {
            "id": "qh8",
            "q": "Quel procédé chimique inventé en 1835 par Justus von Liebig a modernisé les miroirs ?",
            "options": ["L'argenture du verre", "Le polissage de la pierre", "La gravure laser"],
            "rep": "L'argenture du verre"
        },
        {
            "id": "qh9",
            "q": "À quel angle précis John Henry Pepper inclinait-il sa vitre sans tain en 1862 ?",
            "options": ["45 degrés", "90 degrés", "15 degrés"],
            "rep": "45 degrés"
        },
        {
            "id": "qh10",
            "q": "Quelle technologie moderne utilise directement le principe du Spectre de Pepper ?",
            "options": ["L'affichage tête haute (HUD) sur pare-brise", "Le microscope électronique", "La fibre optique sous-marine"],
            "rep": "L'affichage tête haute (HUD) sur pare-brise"
        },
    ]

    if "ordre_quiz_hist_aleatoire" not in st.session_state:
        random.shuffle(questions_hist_sources)
        st.session_state.ordre_quiz_hist_aleatoire = questions_hist_sources

    # Conservation de la structure exacte à 4 éléments par tuple
    champs_hist = [
        ("1. Dans l'Antiquité, les miroirs étaient fabriqués en ......... poli.", ["Choisir...", "bronze", "aluminium"], "bronze", "hist_t1_final"),
        ("2. Le premier traité grec sur les miroirs s'intitule La .........", ["Choisir...", "Catoptrique", "Mécanique"], "Catoptrique", "hist_t2_final"),
        ("3. Selon Euclide, la lumière se propage en ligne .........", ["Choisir...", "droite", "courbe"], "droite", "hist_t3_final"),
        ("4. Alhazen prouve que les rayons lumineux entrent dans l'.........", ["Choisir...", "oeil", "objet"], "oeil", "hist_t4_final"),
        ("5. Le rayon incident et le rayon réfléchi sont dans un même .........", ["Choisir...", "plan", "volume"], "plan", "hist_t5_final"),
        ("6. René Descartes publie La ......... en 1637.", ["Choisir...", "Dioptrique", "Géométrie"], "Dioptrique", "hist_t6_final"),
        ("7. Les angles se mesurent toujours par rapport à la .........", ["Choisir...", "normale", "surface"], "normale", "hist_t7_final"),
        ("8. La loi de la réflexion impose l'égalité stricte : i = .........", ["Choisir...", "i'", "90°"], "i'", "hist_t8_final"),
        ("9. Le Spectre de Pepper utilise une vitre inclinée à ......... degrés.", ["Choisir...", "45", "60"], "45", "hist_t9_final"),
        ("10. Le HUD automobile projette une image ......... devant le conducteur.", ["Choisir...", "virtuelle", "opaque"], "virtuelle", "hist_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_hist_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hist_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Historique (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_hist:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
                
def afficher_atelier_reflexion_complet(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 2 (Réflexion) sur deux colonnes."""
    questions_ref_sources = [
        {"id": "qr1", "q": "Quelle est la relation mathématique de la loi de la réflexion ?", "options": ["i = i'", "i + i' = 90°", "i = 90° - i'"], "rep": "i = i'"},
        {"id": "qr2", "q": "Par rapport à quelle droite mesure-t-on toujours les angles i et i' ?", "options": ["La normale au miroir", "La surface du miroir", "L'horizontale du sol"], "rep": "La normale au miroir"},
        {"id": "qr3", "q": "Quel angle forme la normale avec la surface plane du miroir ?", "options": ["90° (perpendiculaire)", "45°", "180° (parallèle)"], "rep": "90° (perpendiculaire)"},
        {"id": "qr4", "q": "Si un rayon lumineux arrive avec un angle d'incidence i = 32°, quel est l'angle de réflexion i' ?", "options": ["32°", "58°", "64°"], "rep": "32°"},
        {"id": "qr5", "q": "Si un rayon laser frappe le miroir perpendiculairement (confondu avec la normale), que vaut i ?", "options": ["0°", "90°", "45°"], "rep": "0°"},
        {"id": "qr6", "q": "Dans quel plan se situent le rayon incident, la normale et le rayon réfléchi ?", "options": ["Dans le même plan (plan d'incidence)", "Dans deux plans perpendiculaires", "Dans un plan parallèle au miroir"], "rep": "Dans le même plan (plan d'incidence)"},
        {"id": "qr7", "q": "Si le rayon incident fait un angle de 20° avec la surface du miroir, combien vaut l'angle d'incidence i ?", "options": ["70° (car 90° - 20°)", "20°", "40°"], "rep": "70° (car 90° - 20°)"},
        {"id": "qr8", "q": "Quelle est la déviation totale du rayon lumineux lorsque i = 45° ?", "options": ["90° (i + i')", "45°", "0°"], "rep": "90° (i + i')"},
        {"id": "qr9", "q": "Comment appelle-t-on le rayon lumineux qui arrive sur le miroir ?", "options": ["Le rayon incident", "Le rayon réfléchi", "Le rayon normal"], "rep": "Le rayon incident"},
        {"id": "qr10", "q": "Comment appelle-t-on le point précis où le laser touche le miroir ?", "options": ["Le point d'incidence", "Le foyer image", "Le centre optique"], "rep": "Le point d'incidence"},
    ]

    if "ordre_quiz_ref_aleatoire" not in st.session_state:
        random.shuffle(questions_ref_sources)
        st.session_state.ordre_quiz_ref_aleatoire = questions_ref_sources

    champs_ref = [
        ("1. Le rayon qui arrive de la source laser s'appelle le rayon .........", ["Choisir...", "incident", "réfléchi"], "incident", "ref_t1_final"),
        ("2. Le rayon qui repart après avoir touché le miroir est le rayon .........", ["Choisir...", "réfléchi", "incident"], "réfléchi", "ref_t2_final"),
        ("3. La droite perpendiculaire au miroir au point d'impact est la .........", ["Choisir...", "normale", "tangente"], "normale", "ref_t3_final"),
        ("4. L'angle d'incidence i se mesure entre le rayon incident et la .........", ["Choisir...", "normale", "surface"], "normale", "ref_t4_final"),
        ("5. L'angle de réflexion i' est toujours ......... à l'angle d'incidence i.", ["Choisir...", "égal", "supérieur"], "égal", "ref_t5_final"),
        ("6. Le rayon incident et le rayon réfléchi sont situés dans un même .........", ["Choisir...", "plan", "cercle"], "plan", "ref_t6_final"),
        ("7. Si i = 0°, le rayon réfléchi repart sur lui-même en sens .........", ["Choisir...", "inverse", "perpendiculaire"], "inverse", "ref_t7_final"),
        ("8. Pour un angle i = 45°, l'angle entre les deux rayons vaut ......... degrés.", ["Choisir...", "90", "45"], "90", "ref_t8_final"),
        ("9. Un miroir plan donne d'un objet réel une image ......... symétrique.", ["Choisir...", "virtuelle", "inversée"], "virtuelle", "ref_t9_final"),
        ("10. Les lois de la réflexion portent le nom de Snell et .........", ["Choisir...", "Descartes", "Newton"], "Descartes", "ref_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Réflexion (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_ref_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ref_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Réflexion (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_ref:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
                
def afficher_atelier_pepper_complet(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 3 (Spectre de Pepper / HUD)."""
    questions_pep_sources = [
        {"id": "qp1", "q": "Quel angle précis doit avoir le pare-brise (ou la vitre sans tain) pour projeter l'image HUD horizontalement vers le conducteur ?", "options": ["45°", "90°", "15°"], "rep": "45°"},
        {"id": "qp2", "q": "De quelle nature est l'image (le chiffre 50) observée par le conducteur sur la route ?", "options": ["Une image virtuelle", "Une image réelle projetée sur le bitume", "Une ombre portée"], "rep": "Une image virtuelle"},
        {"id": "qp3", "q": "Quelle propriété optique doit posséder le pare-brise pour permettre l'effet Spectre de Pepper ?", "options": ["Être semi-réfléchissant (laisser passer la lumière et en réfléchir une partie)", "Être totalement opaque comme un miroir de salle de bain", "Être dépoli et rugueux"], "rep": "Être semi-réfléchissant (laisser passer la lumière et en réfléchir une partie)"},
        {"id": "qp4", "q": "Quel est le principal avantage sécuritaire d'un affichage tête haute (HUD) en conduite ?", "options": ["Le conducteur lit sa vitesse sans quitter la route des yeux", "Il remplace complètement les phares la nuit", "Il permet de rouler sans pare-brise"], "rep": "Le conducteur lit sa vitesse sans quitter la route des yeux"},
        {"id": "qp5", "q": "Où semble se situer l'hologramme HUD pour l'œil du conducteur lorsque le système est réglé à 45° ?", "options": ["Au loin devant le capot, superposé à la route", "Collé directement sur le tableau de bord", "Derrière la tête du conducteur"], "rep": "Au loin devant le capot, superposé à la route"},
        {"id": "qp6", "q": "Si le pare-brise est incliné à 45° et que le projecteur émet un rayon vertical vers le haut, quel est l'angle d'incidence i ?", "options": ["45°", "0°", "90°"], "rep": "45°"},
        {"id": "qp7", "q": "Dans le théâtre du XIXe siècle (Spectre de Pepper), où était caché l'acteur jouant le fantôme ?", "options": ["Dans une fosse éclairée sous la scène, hors de vue du public", "Suspendu au plafond au-dessus du public", "Derrière un rideau noir au fond de la scène"], "rep": "Dans une fosse éclairée sous la scène, hors de vue du public"},
        {"id": "qp8", "q": "Pourquoi l'image affichée par le projecteur HUD dans la planche de bord doit-elle être inversée à la source ?", "options": ["Parce que la réflexion sur le pare-brise inverse le sens de lecture", "Pour économiser la batterie du véhicule", "Parce que le verre grossit les chiffres"], "rep": "Parce que la réflexion sur le pare-brise inverse le sens de lecture"},
        {"id": "qp9", "q": "Dans la simulation HUD, que se passe-t-il si l'angle du pare-brise est déréglé à 30° au lieu de 45° ?", "options": ["Le rayon réfléchi part trop haut et rate l'œil du conducteur", "L'image devient deux fois plus nette", "La vitesse affichée change de valeur"], "rep": "Le rayon réfléchi part trop haut et rate l'œil du conducteur"},
        {"id": "qp10", "q": "Dans quel autre domaine professionnel l'affichage tête haute (HUD) est-il massivement utilisé ?", "options": ["L'aéronautique (pilotes d'avions de ligne et de chasse)", "La plomberie sanitaire", "La boulangerie industrielle"], "rep": "L'aéronautique (pilotes d'avions de ligne et de chasse)"},
    ]

    if "ordre_quiz_pep_aleatoire" not in st.session_state:
        random.shuffle(questions_pep_sources)
        st.session_state.ordre_quiz_pep_aleatoire = questions_pep_sources

    champs_pep = [
        ("1. L'illusion du Spectre de Pepper repose sur une vitre inclinée à ......... degrés.", ["Choisir...", "45", "90"], "45", "pep_t1_final"),
        ("2. L'image observée au travers de la vitre est une image .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "pep_t2_final"),
        ("3. Le sigle HUD signifie Affichage Tête ......... en français.", ["Choisir...", "Haute", "Basse"], "Haute", "pep_t3_final"),
        ("4. Le pare-brise agit à la fois comme une vitre transparente et un .........", ["Choisir...", "miroir", "prisme"], "miroir", "pep_t4_final"),
        ("5. Le rayon issu du projecteur se réfléchit en respectant la loi i = .........", ["Choisir...", "i'", "0°"], "i'", "pep_t5_final"),
        ("6. Le cerveau prolonge les rayons reçus en ligne ......... derrière le pare-brise.", ["Choisir...", "droite", "courbe"], "droite", "pep_t6_final"),
        ("7. Au théâtre, l'acteur fantôme était éclairé dans une ......... sous la scène.", ["Choisir...", "fosse", "loge"], "fosse", "pep_t7_final"),
        ("8. Le HUD évite au conducteur de baisser les ......... vers le compteur.", ["Choisir...", "yeux", "mains"], "yeux", "pep_t8_final"),
        ("9. Un rayon incident vertical dévié à 90° nécessite un angle d'incidence de .........°.", ["Choisir...", "45", "60"], "45", "pep_t9_final"),
        ("10. L'image projetée sur le pare-brise se superpose directement à la .........", ["Choisir...", "route", "toiture"], "route", "pep_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Spectre de Pepper & HUD (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_pep_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pep_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Spectre de Pepper (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_pep:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
                
def afficher_atelier_retroviseurs_complet(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 4 (Rétroviseurs)."""
    questions_retro_sources = [
        {"id": "qret1", "q": "Quelle loi physique permet de déterminer le champ de vision dans un rétroviseur ?", "options": ["La loi de la réflexion (i = i')", "La loi de la gravité", "La loi d'Ohm"], "rep": "La loi de la réflexion (i = i')"},
        {"id": "qret2", "q": "Comment appelle-t-on les zones situées autour du véhicule que le conducteur ne voit ni directement ni dans ses rétroviseurs ?", "options": ["Les angles morts", "Les points focaux", "Les zones de réfraction"], "rep": "Les angles morts"},
        {"id": "qret3", "q": "Que se passe-t-il pour le champ de vision si le conducteur avance ou recule son siège sans toucher aux miroirs ?", "options": ["Le champ de vision se déplace car l'angle d'incidence change", "Le champ de vision reste strictement identique", "Les miroirs deviennent opaques"], "rep": "Le champ de vision se déplace car l'angle d'incidence change"},
        {"id": "qret4", "q": "Pourquoi un passager avant ne voit-il pas la même zone que le conducteur dans le rétroviseur intérieur ?", "options": ["Parce que son œil n'est pas au même endroit : les rayons incidents ont un angle différent", "Parce que la vitre arrière bloque la lumière pour le passager", "Parce que le miroir central est uniquement orienté vers le plafond"], "rep": "Parce que son œil n'est pas au même endroit : les rayons incidents ont un angle différent"},
        {"id": "qret5", "q": "Comment doit-on régler les rétroviseurs extérieurs (gauche et droit) pour limiter les angles morts ?", "options": ["En apercevant à peine le flanc de sa propre carrosserie au bord intérieur du miroir", "En voyant la moitié de sa propre voiture dans chaque miroir", "En les orientant vers le ciel"], "rep": "En apercevant à peine le flanc de sa propre carrosserie au bord intérieur du miroir"},
        {"id": "qret6", "q": "Quel élément de la carrosserie peut bloquer le champ de vision du rétroviseur intérieur central ?", "options": ["Les montants latéraux et la largeur de la lunette arrière", "Le pare-brise avant", "Le capot moteur"], "rep": "Les montants latéraux et la largeur de la lunette arrière"},
        {"id": "qret7", "q": "Pourquoi certains rétroviseurs extérieurs sont-ils légèrement bombés (convexes) ?", "options": ["Pour élargir l'angle du champ de vision et réduire l'angle mort", "Pour grossir les voitures qui suivent", "Pour empêcher la pluie de mouiller le verre"], "rep": "Pour élargir l'angle du champ de vision et réduire l'angle mort"},
        {"id": "qret8", "q": "Que faut-il toujours faire en plus de regarder dans ses rétroviseurs avant de changer de file ?", "options": ["Tourner la tête pour contrôler directement l'angle mort", "Klaxonner systématiquement", "Allumer les feux de brouillard"], "rep": "Tourner la tête pour contrôler directement l'angle mort"},
        {"id": "qret9", "q": "Dans la simulation, de quelle couleur est représenté le cône de vision réfléchi par chaque rétroviseur ?", "options": ["En bleu translucide bordé de rouge", "En vert fluo", "En noir opaque"], "rep": "En bleu translucide bordé de rouge"},
        {"id": "qret10", "q": "Si l'on tourne un miroir de rétroviseur d'un angle de 10°, de combien tourne le rayon réfléchi ?", "options": ["20° (le double de la rotation du miroir)", "10°", "5°"], "rep": "20° (le double de la rotation du miroir)"},
    ]

    if "ordre_quiz_retro_aleatoire" not in st.session_state:
        random.shuffle(questions_retro_sources)
        st.session_state.ordre_quiz_retro_aleatoire = questions_retro_sources

    champs_retro = [
        ("1. Les rétroviseurs utilisent des miroirs pour renvoyer la ......... vers l'œil.", ["Choisir...", "lumière", "chaleur"], "lumière", "retro_t1_final"),
        ("2. Les zones invisibles autour d'un véhicule s'appellent les angles .........", ["Choisir...", "morts", "droits"], "morts", "retro_t2_final"),
        ("3. Chaque rayon lumineux rebondit sur le miroir selon la loi i = .........", ["Choisir...", "i'", "90°"], "i'", "retro_t3_final"),
        ("4. Un véhicule possède généralement ......... rétroviseurs (gauche, droit et central).", ["Choisir...", "trois", "deux"], "trois", "retro_t4_final"),
        ("5. Si le conducteur règle son ........., il doit aussi réajuster ses miroirs.", ["Choisir...", "siège", "volant"], "siège", "retro_t5_final"),
        ("6. Le rétroviseur central vise à travers la lunette ......... du véhicule.", ["Choisir...", "arrière", "avant"], "arrière", "retro_t6_final"),
        ("7. Un miroir légèrement convexe permet d'......... le champ de vision.", ["Choisir...", "élargir", "réduire"], "élargir", "retro_t7_final"),
        ("8. Avant de dépasser, un contrôle ......... en tournant la tête est obligatoire.", ["Choisir...", "direct", "indirect"], "direct", "retro_t8_final"),
        ("9. Si un miroir pivote d'un angle alpha, le rayon réfléchi pivote de ......... alpha.", ["Choisir...", "2", "0.5"], "2", "retro_t9_final"),
        ("10. Les poids lourds portent des autocollants signalant le danger des angles .........", ["Choisir...", "morts", "vifs"], "morts", "retro_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Rétroviseurs & Sécurité (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_retro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"retro_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Rétroviseurs (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_retro:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
                
def afficher_atelier_periscope_complet(verrouille=False):
    """Affiche le Quiz (10 questions) et le Texte à trous (10 cases) de l'Atelier 5 (Périscope)."""
    questions_peri_sources = [
        {"id": "qper1", "q": "Combien de miroirs plans (ou prismes) compose un périscope simple ?", "options": ["Deux miroirs parallèles", "Un seul miroir sphérique", "Quatre lentilles divergentes"], "rep": "Deux miroirs parallèles"},
        {"id": "qper2", "q": "À quel angle précis les deux miroirs d'un périscope doivent-ils être inclinés par rapport à l'horizontale ?", "options": ["45°", "90°", "30°"], "rep": "45°"},
        {"id": "qper3", "q": "De quel angle le premier miroir dévie-t-il le rayon lumineux horizontal pour l'envoyer verticalement vers le bas ?", "options": ["90°", "45°", "180°"], "rep": "90°"},
        {"id": "qper4", "q": "Quelle est la direction du rayon qui sort du second miroir par rapport au rayon qui entre en haut du périscope ?", "options": ["Il est parallèle et de même sens", "Il est perpendiculaire", "Il repart en sens opposé"], "rep": "Il est parallèle et de même sens"},
        {"id": "qper5", "q": "Pourquoi l'image observée dans un périscope à deux miroirs n'est-elle pas inversée (à l'endroit) ?", "options": ["La seconde réflexion annule l'inversion de la première réflexion", "Le tube métallique redresse l'image", "L'eau de mer corrige le sens de la lumière"], "rep": "La seconde réflexion annule l'inversion de la première réflexion"},
        {"id": "qper6", "q": "Que se passe-t-il dans la simulation si les miroirs sont inclinés à 35° au lieu de 45° ?", "options": ["Le rayon est mal dévié et frappe la paroi du tube", "Le périscope grossit deux fois plus l'image", "Le rayon sort parfaitement horizontalement"], "rep": "Le rayon est mal dévié et frappe la paroi du tube"},
        {"id": "qper7", "q": "Quelle loi optique est appliquée successivement sur le Miroir 1 puis sur le Miroir 2 ?", "options": ["La loi de la réflexion (i = i')", "La loi de la diffraction", "L'absorption totale"], "rep": "La loi de la réflexion (i = i')"},
        {"id": "qper8", "q": "Quel est l'intérêt principal d'un périscope pour un sous-marin ?", "options": ["Observer la surface tout en restant immergé et caché sous l'eau", "Éclairer les fonds marins à 1000 mètres", "Mesurer la température de l'eau"], "rep": "Observer la surface tout en restant immergé et caché sous l'eau"},
        {"id": "qper9", "q": "Par quoi remplace-t-on souvent les miroirs plans dans les périscopes de haute précision ?", "options": ["Des prismes à réflexion totale", "Des plaques de carton blanc", "Des filtres polarisants"], "rep": "Des prismes à réflexion totale"},
        {"id": "qper10", "q": "Si la distance verticale entre les deux miroirs augmente (tube plus long), comment doit-on modifier l'angle des miroirs ?", "options": ["On ne change rien : ils restent inclinés à 45°", "Il faut les incliner à 60°", "Il faut les placer à 90°"], "rep": "On ne change rien : ils restent inclinés à 45°"},
    ]

    if "ordre_quiz_peri_aleatoire" not in st.session_state:
        random.shuffle(questions_peri_sources)
        st.session_state.ordre_quiz_peri_aleatoire = questions_peri_sources

    champs_peri = [
        ("1. Un périscope simple utilise ......... miroirs plans parallèles.", ["Choisir...", "deux", "trois"], "deux", "peri_t1_final"),
        ("2. Les deux miroirs sont inclinés à ......... degrés par rapport à l'horizontale.", ["Choisir...", "45", "90"], "45", "peri_t2_final"),
        ("3. Le premier miroir dévie la lumière horizontalement vers le .........", ["Choisir...", "bas", "haut"], "bas", "peri_t3_final"),
        ("4. Chaque miroir provoque une déviation du faisceau de ......... degrés.", ["Choisir...", "90", "45"], "90", "peri_t4_final"),
        ("5. Le rayon sortant est ......... au rayon entrant dans le périscope.", ["Choisir...", "parallèle", "perpendiculaire"], "parallèle", "peri_t5_final"),
        ("6. Le dispositif repose sur une ......... réflexion successive.", ["Choisir...", "double", "triple"], "double", "peri_t6_final"),
        ("7. Sur chaque miroir, l'angle d'incidence i est égal à l'angle ......... i'.", ["Choisir...", "réfléchi", "incident"], "réfléchi", "peri_t7_final"),
        ("8. Grâce aux deux réflexions, l'image finale est vue à l'.........", ["Choisir...", "endroit", "envers"], "endroit", "peri_t8_final"),
        ("9. Si l'angle des miroirs est déréglé, le rayon heurte la ......... du tube.", ["Choisir...", "paroi", "lentille"], "paroi", "peri_t9_final"),
        ("10. Le périscope permet d'observer au-dessus d'un ......... sans être vu.", ["Choisir...", "obstacle", "nuage"], "obstacle", "peri_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Périscope & Double Réflexion (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_peri_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"peri_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Périscope (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_peri:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def mettre_a_jour_maintenance_matplotlib(sujet_idx):
    """Banc d'essai optique ultra-réaliste adapté au sujet de maintenance tiré au sort."""
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 260)
    ax.invert_yaxis()
    ax.axis("off")

    # =========================================================================
    # SUJET 0 : ALIGNEMENT LASER D'ARBRES TOURNANTS (MOTEUR / POMPE)
    # =========================================================================
    if sujet_idx == 0:
        defaut_deg = st.session_state.get("slider_maint_s0", 0.25)
        dist_mm = 250.0
        # Loi de la réflexion : une rotation miroir de alpha dévie le rayon de 2*alpha
        deviation_rad = math.radians(2.0 * defaut_deg)
        decalage_mm = dist_mm * math.tan(deviation_rad)
        echelle_px = 35.0
        y_impact = 130.0 + decalage_mm * echelle_px
        y_impact = max(35.0, min(225.0, y_impact))

        # Moteur (gauche) et Pompe (droite)
        ax.add_patch(patches.Rectangle((30, 85), 110, 90, facecolor="#334155", edgecolor="#94a3b8", lw=1.5))
        ax.text(85, 130, "MOTEUR\n(3000 tr/min)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")
        ax.add_patch(patches.Rectangle((140, 118), 45, 24, facecolor="#64748b", edgecolor="#cbd5e1"))
        # Tête laser S (émetteur + cible PSD)
        ax.add_patch(patches.Rectangle((165, 70), 22, 48, facecolor="#0284c7", edgecolor="white", lw=1))
        ax.text(176, 62, "Tête Laser S", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        # Pompe (droite) + Prisme/Miroir réflecteur M incliné du défaut angulaire
        ax.add_patch(patches.Rectangle((460, 85), 110, 90, facecolor="#334155", edgecolor="#94a3b8", lw=1.5))
        ax.text(515, 130, "POMPE\nHYDRAULIQUE", color="white", fontsize=8, fontweight="bold", ha="center", va="center")
        ax.add_patch(patches.Rectangle((415, 118), 45, 24, facecolor="#64748b", edgecolor="#cbd5e1"))

        xm, ym = 425.0, 90.0
        ang_visuel = math.radians(defaut_deg * 25.0)
        dx_m = 22.0 * math.sin(ang_visuel)
        dy_m = 22.0 * math.cos(ang_visuel)
        ax.plot([xm - dx_m, xm + dx_m], [ym - dy_m, ym + dy_m], color="#38bdf8", lw=4)
        ax.text(xm, 58, "Réflecteur M", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        # Faisceau aller (y=90) et faisceau retour dévié de 2*alpha
        ax.annotate("", xy=(xm, ym), xytext=(187, 90), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))
        y_retour = 90.0 + decalage_mm * 12.0
        y_retour = max(40.0, min(145.0, y_retour))
        ax.annotate("", xy=(187, y_retour), xytext=(xm, ym), arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2, ls="--"))

        tol_ok = abs(defaut_deg) <= 0.05
        statut = "ALIGNEMENT CONFORME (Tolérance <= 0,05°)" if tol_ok else "DÉFAUT ANGULAIRE CRITIQUE (Risque casse roulement)"
        c_stat = "#22c55e" if tol_ok else "#ef4444"

        ax.text(25, 20, "BANC LASER : ALIGNEMENT D'ARBRES TOURNANTS (L = 250 mm)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 235, f"Défaut angulaire arbre : {defaut_deg:+.2f}° | Déviation faisceau (2α) : {2*defaut_deg:+.2f}° | Décalage cible : {decalage_mm:+.2f} mm",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.maint_mesure_courante = (f"Défaut = {defaut_deg:+.2f}°", f"Déviation = {2*defaut_deg:+.2f}°", f"Décalage = {decalage_mm:+.2f} mm", "CONFORME" if tol_ok else "HORS TOLÉRANCE")

    # =========================================================================
    # SUJET 1 : MIROIR D'INSPECTION ARTICULÉ (CONTRÔLE SOUDURE / FUITE)
    # =========================================================================
    elif sujet_idx == 1:
        ang_mir = st.session_state.get("slider_maint_s1", 35.0)
        rad_mir = math.radians(ang_mir)

        # Carter machine bloquant la vue directe
        ax.add_patch(patches.Rectangle((180, 30), 140, 110, facecolor="#475569", edgecolor="#94a3b8", lw=2))
        ax.text(250, 85, "CARTER MOTEUR\n(Obstacle opaque)", color="white", fontsize=8, fontweight="bold", ha="center", va="center")

        # Zone cachée (joint / soudure à inspecter derrière le carter)
        ax.add_patch(patches.Rectangle((215, 140), 70, 14, facecolor="#ef4444", edgecolor="white"))
        ax.text(250, 166, "Zone de fuite / Soudure", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        # Technicien (œil à gauche) et miroir articulé en bas (x=250, y=220)
        ax.text(65, 215, "Œil du\nTechnicien", color="#38bdf8", fontsize=8.5, fontweight="bold", ha="center")
        xm, ym = 250.0, 220.0
        dx_m = 32.0 * math.cos(rad_mir)
        dy_m = 32.0 * math.sin(rad_mir)
        ax.plot([xm - dx_m, xm + dx_m], [ym + dy_m, ym - dy_m], color="#38bdf8", lw=4)
        ax.plot([xm, xm + 65], [ym, ym + 25], color="#94a3b8", lw=2.5)
        ax.text(xm + 70, ym + 25, "Tige télescopique", color="#94a3b8", fontsize=7)

        # Rayon issu de la soudure (250, 154) vertical vers le miroir (250, 220)
        # Rayon issu de la soudure (250, 154) vertical vers le miroir (250, 220)
        ax.annotate("", xy=(xm, ym), xytext=(250, 154), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))
        # Rayon réfléchi partant du miroir selon angle 2*ang_mir par rapport à la verticale (vers l'œil à x=65)
        ang_refl_rad = math.radians(2.0 * ang_mir)
        x_fin = xm - 185.0 * math.sin(ang_refl_rad)
        y_fin = ym - 185.0 * math.cos(ang_refl_rad)
        ax.annotate("", xy=(x_fin, y_fin), xytext=(xm, ym), arrowprops=dict(arrowstyle="->", color="#22c55e" if 43 <= ang_mir <= 47 else "#f59e0b", lw=2))

        visu_ok = 43.0 <= ang_mir <= 47.0
        statut = "INSPECTION VISUELLE OK : La soudure est centrée dans le miroir !" if visu_ok else "ANGLE INCORRECT : La soudure est hors du champ de vision."
        c_stat = "#22c55e" if visu_ok else "#ef4444"

        ax.text(25, 20, "CONTRÔLE NON DESTRUCTIF : MIROIR D'INSPECTION ARTICULÉ", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 245, f"Inclinaison miroir : {ang_mir:.1f}° | Incidence i = {ang_mir:.1f}° | Réflexion i' = {ang_mir:.1f}°",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.maint_mesure_courante = (f"Miroir = {ang_mir:.1f}°", f"i = i' = {ang_mir:.1f}°", f"Déviation = {2*ang_mir:.1f}°", "VISIBLE" if visu_ok else "MASQUÉ")

    # =========================================================================
    # SUJET 2 : BARRIÈRE PHOTOÉLECTRIQUE À RÉFLECTEUR (CATADIOPTRE SUR CONVOYEUR)
    # =========================================================================
    else:
        desaxage_deg = st.session_state.get("slider_maint_s2", 5.0)
        # Un catadioptre (coin de cube) tolère jusqu'à +/- 15° avant perte brutale du signal
        if abs(desaxage_deg) <= 15.0:
            signal_pct = max(80.0, 100.0 - (abs(desaxage_deg) * 1.2))
        else:
            signal_pct = max(0.0, 80.0 - (abs(desaxage_deg) - 15.0) * 7.5)

        # Émetteur/Récepteur photoélectrique (gauche)
        ax.add_patch(patches.Rectangle((40, 100), 75, 60, facecolor="#1e293b", edgecolor="#38bdf8", lw=2))
        ax.text(77, 130, "CAPTEUR\nOPTIQUE\n(Émetteur/Réc.)", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center")

        # Convoyeur au centre
        ax.add_patch(patches.Rectangle((220, 165), 160, 22, facecolor="#475569", edgecolor="#94a3b8"))
        ax.text(300, 176, "CONVOYEUR INDUSTRIEL", color="#e2e8f0", fontsize=7, fontweight="bold", ha="center", va="center")

        # Catadioptre (coin de cube) à droite
        xc, yc = 510.0, 130.0
        rad_c = math.radians(desaxage_deg)
        dx_c = 28.0 * math.sin(rad_c)
        dy_c = 28.0 * math.cos(rad_c)
        ax.plot([xc - dx_c, xc + dx_c], [yc - dy_c, yc + dy_c], color="#eab308", lw=5)
        ax.text(xc, 85, "Catadioptre\n(Coin de cube)", color="#eab308", fontsize=7.5, fontweight="bold", ha="center")

        # Faisceau aller
        ax.annotate("", xy=(xc, yc - 5), xytext=(115, 125), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))

        # Faisceau retour : parallèle si |desaxage| <= 15°, perdu sinon
        if signal_pct >= 80.0:
            ax.annotate("", xy=(115, 138), xytext=(xc, yc + 8), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            statut = f"SIGNAL OPTIQUE OPTIMAL ({signal_pct:.0f}%) : Rétroréflexion active."
            c_stat = "#22c55e"
        else:
            y_rate = 138.0 + (abs(desaxage_deg) - 15.0) * 8.0
            ax.annotate("", xy=(140, min(230.0, y_rate)), xytext=(xc, yc + 8), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2, ls="--"))
            statut = f"ALARME MAINTENANCE ({signal_pct:.0f}%) : Réflecteur trop désaxé (> 15°)."
            c_stat = "#ef4444"

        ax.text(25, 20, "DÉTECTION SUR LIGNE : BARRIÈRE PHOTOÉLECTRIQUE À CATADIOPTRE", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 235, f"Désalignement catadioptre : {desaxage_deg:+.1f}° | Signal reçu : {signal_pct:.0f}% (Seuil mini : 80%)",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.maint_mesure_courante = (f"Désaxage = {desaxage_deg:+.1f}°", f"Signal = {signal_pct:.0f}%", "Seuil >= 80%", "OPÉRATIONNEL" if signal_pct >= 80 else "DÉFAUT LIGNE")

    return fig


BANQUES_MAINTENANCE = {
    # =========================================================================
    # BANQUE SUJET 0 : ALIGNEMENT LASER D'ARBRES TOURNANTS (MOTEUR - POMPE)
    # =========================================================================
    0: {
        "questions": [
            {"id": "qm0_1", "q": "Lors d'un lignage laser moteur-pompe, si l'arbre récepteur tourne d'un angle α, de quel angle dévie le faisceau laser réfléchi ?", "options": ["2 × α (le double de l'angle)", "α (le même angle)", "α / 2 (la moitié de l'angle)"], "rep": "2 × α (le double de l'angle)"},
            {"id": "qm0_2", "q": "Quelle est la tolérance angulaire maximale admise pour un alignement laser sur une machine tournant à 3000 tr/min ?", "options": ["0,05°", "2,50°", "10,0°"], "rep": "0,05°"},
            {"id": "qm0_3", "q": "Si le défaut angulaire α = 0,25° à une distance de 250 mm, pourquoi le décalage sur le capteur est-il amplifié ?", "options": ["Parce que la déviation optique vaut 2α et augmente avec la distance L", "Parce que le laser ralentit dans l'air", "Parce que la pompe dilate le faisceau"], "rep": "Parce que la déviation optique vaut 2α et augmente avec la distance L"},
            {"id": "qm0_4", "q": "Quel composant mécanique casse prématurément en cas de défaut d'alignement angulaire entre le moteur et la pompe ?", "options": ["Les roulements et les garnitures d'étanchéité", "Le bobinage électrique du stator", "Le ventilateur de refroidissement"], "rep": "Les roulements et les garnitures d'étanchéité"},
            {"id": "qm0_5", "q": "Sur quel arbre fixe-t-on généralement le prisme ou miroir réflecteur lors d'un contrôle d'alignement ?", "options": ["Sur l'arbre de la machine mobile à régler (la pompe)", "Sur le sol de l'atelier", "Sur le capot de protection en plastique"], "rep": "Sur l'arbre de la machine mobile à régler (la pompe)"},
            {"id": "qm0_6", "q": "Comment corrige-t-on un défaut d'alignement angulaire détecté par le faisceau laser réfléchi ?", "options": ["En ajoutant des cales calibrées sous les pattes de fixation de la machine", "En tordant l'arbre moteur à la presse", "En changeant la couleur du laser"], "rep": "En ajoutant des cales calibrées sous les pattes de fixation de la machine"},
            {"id": "qm0_7", "q": "Lorsque l'alignement entre les deux arbres est parfait (α = 0°), comment revient le rayon réfléchi sur la tête laser ?", "options": ["Il revient exactement sur son trajet aller (i = i' = 0°)", "Il est dévié à 90° vers le plafond", "Il disparaît totalement"], "rep": "Il revient exactement sur son trajet aller (i = i' = 0°)"},
            {"id": "qm0_8", "q": "Quelle est l'unité de précision courante d'un capteur optique PSD utilisé en lignage laser ?", "options": ["Le micromètre (0,001 mm)", "Le centimètre (10 mm)", "Le décimètre (100 mm)"], "rep": "Le micromètre (0,001 mm)"},
            {"id": "qm0_9", "q": "Quel symptôme physique sur la machine alerte le technicien avant même le contrôle laser ?", "options": ["Des vibrations anormales et un échauffement des paliers", "Une baisse de pression atmosphérique", "Un changement de couleur de la peinture"], "rep": "Des vibrations anormales et un échauffement des paliers"},
            {"id": "qm0_10", "q": "Pourquoi préfère-t-on le lignage laser à la règle métallique ou au comparateur mécanique ?", "options": ["Il supprime la flexion mécanique et multiplie par 2 la sensibilité grâce à la réflexion", "Il coûte moins cher qu'un réglet", "Il fonctionne sans électricité ni batterie"], "rep": "Il supprime la flexion mécanique et multiplie par 2 la sensibilité grâce à la réflexion"},
        ],
        "trous": [
            ("1. Le lignage laser évite l'usure prématurée des ......... et des joints.", ["Choisir...", "roulements", "câbles"], "roulements", "maint_t1_final"),
            ("2. Un défaut angulaire alpha de l'arbre dévie le laser réfléchi de ......... alpha.", ["Choisir...", "2", "0.5"], "2", "maint_t2_final"),
            ("3. À 3000 tr/min, le défaut angulaire ne doit pas dépasser ......... degrés.", ["Choisir...", "0.05", "5.0"], "0.05", "maint_t3_final"),
            ("4. Lorsque les deux arbres sont parfaitement alignés, i = i' = .........°.", ["Choisir...", "0", "45"], "0", "maint_t4_final"),
            ("5. Le faisceau laser rebondit sur un prisme ou un miroir .........", ["Choisir...", "réflecteur", "absorbant"], "réflecteur", "maint_t5_final"),
            ("6. Plus la distance L entre les machines est grande, plus le décalage est .........", ["Choisir...", "important", "faible"], "important", "maint_t6_final"),
            ("7. Un mauvais alignement génère de fortes ......... sur le bâti.", ["Choisir...", "vibrations", "économies"], "vibrations", "maint_t7_final"),
            ("8. On corrige la hauteur des pattes moteur à l'aide de ......... calibrées.", ["Choisir...", "cales", "vis"], "cales", "maint_t8_final"),
            ("9. La réflexion optique permet une précision de mesure au ......... de millimètre.", ["Choisir...", "centième", "mètre"], "centième", "maint_t9_final"),
            ("10. Le faisceau réfléchi respecte la loi fondamentale i = .........", ["Choisir...", "i'", "90°"], "i'", "maint_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 1 : MIROIR D'INSPECTION ARTICULÉ (SOUDURES & FUITES)
    # =========================================================================
    1: {
        "questions": [
            {"id": "qm1_1", "q": "À quel angle précis faut-il incliner un miroir d'inspection pour observer une fuite située à 90° derrière un carter ?", "options": ["45°", "90°", "15°"], "rep": "45°"},
            {"id": "qm1_2", "q": "Quelle loi optique permet de prévoir la direction dans laquelle l'image de la soudure sera renvoyée ?", "options": ["La loi de la réflexion (i = i')", "La loi de gravitation universelle", "La loi de Joule"], "rep": "La loi de la réflexion (i = i')"},
            {"id": "qm1_3", "q": "Pourquoi le contrôle au miroir d'inspection est-il classé parmi les contrôles non destructifs (CND) ?", "options": ["Il permet d'inspecter la pièce sans démonter ni détériorer la machine", "Il détruit uniquement les soudures défectueuses", "Il soude automatiquement les fissures"], "rep": "Il permet d'inspecter la pièce sans démonter ni détériorer la machine"},
            {"id": "qm1_4", "q": "Si le technicien incline son miroir à 35° au lieu de 45°, pourquoi ne voit-il plus la soudure ?", "options": ["Le rayon réfléchi est dévié de 70° au lieu de 90° et rate son œil", "Le miroir devient opaque en dessous de 40°", "La lumière s'arrête sur le carter"], "rep": "Le rayon réfléchi est dévié de 70° au lieu de 90° et rate son œil"},
            {"id": "qm1_5", "q": "De quelle nature est l'image de la fuite observée par le technicien dans le miroir plan articulé ?", "options": ["Une image virtuelle symétrique par rapport au plan du miroir", "Une image réelle projetée sur le carter", "Une ombre inversée"], "rep": "Une image virtuelle symétrique par rapport au plan du miroir"},
            {"id": "qm1_6", "q": "Quel accessoire est souvent intégré autour du miroir d'inspection industriel pour travailler dans les carters sombres ?", "options": ["Un éclairage LED orienté vers la zone inspectée", "Un aimant permanent haute puissance", "Un capteur de pression hydraulique"], "rep": "Un éclairage LED orienté vers la zone inspectée"},
            {"id": "qm1_7", "q": "Pourquoi utilise-t-on une tige télescopique et une rotule sur un miroir de maintenance ?", "options": ["Pour atteindre des zones profondes et ajuster finement l'angle d'incidence i", "Pour mesurer la température de l'huile", "Pour serrer des écrous inaccessibles"], "rep": "Pour atteindre des zones profondes et ajuster finement l'angle d'incidence i"},
            {"id": "qm1_8", "q": "Dans un environnement avec projections d'étincelles de soudage, quel matériau privilégie-t-on pour le miroir ?", "options": ["L'acier inoxydable poli incassable", "Le verre fin non trempé", "Le carton aluminium"], "rep": "L'acier inoxydable poli incassable"},
            {"id": "qm1_9", "q": "Lorsque le miroir pivote de 5° sur sa rotule, de combien pivote le champ de vision observé ?", "options": ["10° (le double de la rotation du miroir)", "5°", "2,5°"], "rep": "10° (le double de la rotation du miroir)"},
            {"id": "qm1_10", "q": "Quelle précaution de maintenance faut-il prendre avant d'utiliser le miroir près d'un circuit hydraulique ?", "options": ["Essuyer toute trace d'huile sur le miroir pour éviter une réflexion diffuse floue", "Tremper le miroir dans l'huile", "Chauffer le miroir au chalumeau"], "rep": "Essuyer toute trace d'huile sur le miroir pour éviter une réflexion diffuse floue"},
        ],
        "trous": [
            ("1. Pour voir derrière un carter à 90°, on incline le miroir à .........°.", ["Choisir...", "45", "90"], "45", "maint_t1_final"),
            ("2. Le miroir d'inspection applique la loi de réflexion i = .........", ["Choisir...", "i'", "0°"], "i'", "maint_t2_final"),
            ("3. Inspecter sans démonter la machine est un contrôle non .........", ["Choisir...", "destructif", "visuel"], "destructif", "maint_t3_final"),
            ("4. L'image observée dans le miroir plan est une image .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "maint_t4_final"),
            ("5. Une ......... orientable permet de régler l'angle du miroir.", ["Choisir...", "rotule", "poulie"], "rotule", "maint_t5_final"),
            ("6. La tige ......... permet d'atteindre les zones profondes du moteur.", ["Choisir...", "télescopique", "rigide"], "télescopique", "maint_t6_final"),
            ("7. Si le miroir tourne de 10°, le rayon réfléchi tourne de .........°.", ["Choisir...", "20", "10"], "20", "maint_t7_final"),
            ("8. Une trace d'huile sur le verre provoque une réflexion ......... floue.", ["Choisir...", "diffuse", "totale"], "diffuse", "maint_t8_final"),
            ("9. Les angles i et i' sont mesurés par rapport à la ......... au miroir.", ["Choisir...", "normale", "tige"], "normale", "maint_t9_final"),
            ("10. Des LED éclairent la zone cachée pour fournir des rayons .........", ["Choisir...", "incidents", "réfléchis"], "incidents", "maint_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 2 : BARRIÈRE PHOTOÉLECTRIQUE À CATADIOPTRE SUR CONVOYEUR
    # =========================================================================
    2: {
        "questions": [
            {"id": "qm2_1", "q": "Quelle est la propriété optique principale d'un catadioptre monté face à une cellule photoélectrique ?", "options": ["Il renvoie le faisceau lumineux parallèlement à sa direction d'arrivée", "Il disperse la lumière à 180° dans tout l'atelier", "Il transforme la lumière rouge en lumière bleue"], "rep": "Il renvoie le faisceau lumineux parallèlement à sa direction d'arrivée"},
            {"id": "qm2_2", "q": "Comment sont disposées les facettes réfléchissantes à l'intérieur d'un catadioptre (coin de cube) ?", "options": ["Trois miroirs plans perpendiculaires entre eux à 90°", "Un seul miroir sphérique concave", "Deux lentilles divergentes"], "rep": "Trois miroirs plans perpendiculaires entre eux à 90°"},
            {"id": "qm2_3", "q": "Pourquoi utilise-t-on un catadioptre sur un convoyeur soumis aux vibrations plutôt qu'un simple miroir plan ?", "options": ["Le catadioptre tolère un désalignement jusqu'à ± 15° sans perdre le signal", "Un miroir plan ne réfléchit pas les rayons infrarouges", "Le catadioptre fonctionne sans émetteur"], "rep": "Le catadioptre tolère un désalignement jusqu'à ± 15° sans perdre le signal"},
            {"id": "qm2_4", "q": "Que détecte la cellule photoélectrique lorsqu'un colis passe sur le convoyeur entre le capteur et le réflecteur ?", "options": ["La coupure brutale du faisceau réfléchi", "L'augmentation du poids du colis", "La température du carton"], "rep": "La coupure brutale du faisceau réfléchi"},
            {"id": "qm2_5", "q": "Dans la simulation, en dessous de quel pourcentage de signal réfléchi l'alarme de maintenance préventive se déclenche-t-elle ?", "options": ["80 %", "10 %", "100 %"], "rep": "80 %"},
            {"id": "qm2_6", "q": "Quelle est la cause la plus fréquente d'une baisse progressive du signal optique (ex : 65 %) sans passage de colis ?", "options": ["L'encrassement du réflecteur par la poussière ou un choc qui l'a désaxé de plus de 15°", "L'usure du faisceau lumineux", "La couleur des murs de l'usine"], "rep": "L'encrassement du réflecteur par la poussière ou un choc qui l'a désaxé de plus de 15°"},
            {"id": "qm2_7", "q": "Combien de réflexions successives subit le faisceau à l'intérieur d'un coin de cube avant de repartir vers le capteur ?", "options": ["Trois réflexions", "Une seule réflexion", "Cinq réflexions"], "rep": "Trois réflexions"},
            {"id": "qm2_8", "q": "Quel avantage économique présente un capteur reflex (émetteur + récepteur réunis + catadioptre) sur une ligne de production ?", "options": ["Il n'y a besoin de câbler électriquement qu'un seul côté du convoyeur", "Il ne nécessite aucun réglage mécanique", "Il remplace le moteur du convoyeur"], "rep": "Il n'y a besoin de câbler électriquement qu'un seul côté du convoyeur"},
            {"id": "qm2_9", "q": "Que doit faire le technicien de maintenance si un chariot élévateur a heurté et tordu le support du catadioptre de 22° ?", "options": ["Redresser le support pour revenir dans la plage de tolérance (± 15°) et vérifier le voyant de gain", "Remplacer toute l'armoire électrique", "Peindre le catadioptre en noir mat"], "rep": "Redresser le support pour revenir dans la plage de tolérance (± 15°) et vérifier le voyant de gain"},
            {"id": "qm2_10", "q": "Quelle technologie de filtre utilise-t-on sur ces capteurs pour éviter qu'un objet brillant (film plastique, métal) ne trompe la cellule ?", "options": ["Un filtre polarisant (seule la lumière dépolarisée par le catadioptre est acceptée)", "Un filtre à huile", "Un verre fumé opaque"], "rep": "Un filtre polarisant (seule la lumière dépolarisée par le catadioptre est acceptée)"},
        ],
        "trous": [
            ("1. Un réflecteur en coin de cube s'appelle un .........", ["Choisir...", "catadioptre", "prisme"], "catadioptre", "maint_t1_final"),
            ("2. Le catadioptre renvoie la lumière parallèlement à son rayon .........", ["Choisir...", "incident", "perpendiculaire"], "incident", "maint_t2_final"),
            ("3. Il est composé de trois micro-miroirs inclinés à ......... degrés.", ["Choisir...", "90", "45"], "90", "maint_t3_final"),
            ("4. Le catadioptre tolère les vibrations jusqu'à ± ......... degrés.", ["Choisir...", "15", "60"], "15", "maint_t4_final"),
            ("5. Le passage d'un colis sur le convoyeur ......... le faisceau réfléchi.", ["Choisir...", "coupe", "amplifie"], "coupe", "maint_t5_final"),
            ("6. L'émetteur et le récepteur sont regroupés dans le même .........", ["Choisir...", "boîtier", "convoyeur"], "boîtier", "maint_t6_final"),
            ("7. Si le signal passe sous ......... %, une alarme maintenance s'active.", ["Choisir...", "80", "20"], "80", "maint_t7_final"),
            ("8. La poussière sur le réflecteur diminue l'intensité .........", ["Choisir...", "réfléchie", "électrique"], "réfléchie", "maint_t8_final"),
            ("9. Chaque face interne du coin de cube applique la loi i = .........", ["Choisir...", "i'", "0°"], "i'", "maint_t9_final"),
            ("10. Le système reflex évite de tirer des ......... des deux côtés du tapis.", ["Choisir...", "câbles", "rails"], "câbles", "maint_t10_final"),
        ]
    }
}


def afficher_atelier_maintenance_complet(sujet_idx, verrouille=False):
    """Affiche les 10 QCM et les 10 trous spécifiques au sujet de maintenance tiré au sort."""
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet de maintenance ci-dessus pour débloquer les 10 questions et les 10 phrases à trous correspondantes.")
        return

    banque = BANQUES_MAINTENANCE[sujet_idx]
    cle_session_ordre = f"ordre_quiz_maint_sujet_{sujet_idx}"

    if cle_session_ordre not in st.session_state:
        liste_q = list(banque["questions"])
        random.shuffle(liste_q)
        st.session_state[cle_session_ordre] = liste_q

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique sur votre sujet (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_session_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"maint_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse sur votre sujet (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
BANQUES_TP = {
    # =========================================================================
    # BANQUE SUJET 0 : LASER ROTATIF DE NIVELLEMENT (TERRASSEMENT & PELLE)
    # =========================================================================
    0: {
        "questions": [
            {"id": "qtp0_1", "q": "Quel composant optique situé dans la tête tournante du laser rotatif dévie le faisceau vertical de 90° pour créer un plan horizontal ?", "options": ["Un pentaprisme (prisme à double réflexion)", "Une lentille divergente en plastique", "Un filtre polarisant circulaire"], "rep": "Un pentaprisme (prisme à double réflexion)"},
            {"id": "qtp0_2", "q": "De quel angle précis le pentaprisme dévie-t-il le faisceau laser entre son entrée verticale et sa sortie horizontale ?", "options": ["90°", "45°", "180°"], "rep": "90°"},
            {"id": "qtp0_3", "q": "À quelle hauteur (cote de référence) le faisceau laser horizontal est-il réglé dans la simulation de terrassement ?", "options": ["1,50 m au-dessus du fond de fouille cible", "0,10 m sous la terre", "12,0 m au-dessus de la grue"], "rep": "1,50 m au-dessus du fond de fouille cible"},
            {"id": "qtp0_4", "q": "Que signifie l'indication « TROP HAUT (Creuser) » affichée sur la cellule de réception fixée sur le bras de la pelle ?", "options": ["Le godet est au-dessus de la cote projet : le faisceau frappe le bas de la cellule", "La batterie du trépied est déchargée", "Le trépied est penché de 45°"], "rep": "Le godet est au-dessus de la cote projet : le faisceau frappe le bas de la cellule"},
            {"id": "qtp0_5", "q": "Pourquoi le laser rotatif tourne-t-il à haute vitesse (jusqu'à 600 tr/min) sur un chantier ?", "options": ["Pour balayer 360° et matérialiser un plan de référence horizontal sur tout le chantier", "Pour refroidir la diode laser par ventilation", "Pour creuser le sol par friction"], "rep": "Pour balayer 360° et matérialiser un plan de référence horizontal sur tout le chantier"},
            {"id": "qtp0_6", "q": "Quel est l'avantage majeur d'un pentaprisme par rapport à un simple miroir plan dans un laser de chantier ?", "options": ["Il maintient une déviation exacte de 90° même en cas de légères vibrations du rotor", "Il multiplie par dix la puissance du laser", "Il fonctionne sans batterie"], "rep": "Il maintient une déviation exacte de 90° même en cas de légères vibrations du rotor"},
            {"id": "qtp0_7", "q": "Sur quel équipement fixe-t-on la cellule de détection optique pour guider un engin de terrassement en temps réel ?", "options": ["Sur le balancier (bras) de la pelle hydraulique ou sur une mire graduée", "Sur le pneu arrière du camion benne", "Sur le casque du chef de chantier"], "rep": "Sur le balancier (bras) de la pelle hydraulique ou sur une mire graduée"},
            {"id": "qtp0_8", "q": "Quelle est la précision altimétrique typique d'un laser rotatif de chantier à 100 mètres de distance ?", "options": ["Environ ± 1,5 mm à ± 3 mm", "Environ ± 50 cm", "Environ ± 2 mètres"], "rep": "Environ ± 1,5 mm à ± 3 mm"},
            {"id": "qtp0_9", "q": "Que fait le système d'auto-nivellement du laser rotatif si un engin fait vibrer le trépied au-delà de ± 5° ?", "options": ["Il coupe le faisceau et clignote pour éviter toute erreur de cote sur le chantier", "Il continue de tourner en biais sans prévenir", "Il augmente la vitesse de rotation"], "rep": "Il coupe le faisceau et clignote pour éviter toute erreur de cote sur le chantier"},
            {"id": "qtp0_10", "q": "Quelle loi optique régit chaque réflexion interne du faisceau laser dans le pentaprisme ?", "options": ["La loi de la réflexion (i = i')", "La loi de la pesanteur", "L'effet Doppler"], "rep": "La loi de la réflexion (i = i')"},
        ],
        "trous": [
            ("1. La tête du laser rotatif contient un ......... qui dévie la lumière à 90°.", ["Choisir...", "pentaprisme", "entonnoir"], "pentaprisme", "tp_t1_final"),
            ("2. En tournant à 360°, le faisceau crée un ......... de référence horizontal.", ["Choisir...", "plan", "cercle"], "plan", "tp_t2_final"),
            ("3. Le faisceau vertical est dévié d'un angle droit de ......... degrés.", ["Choisir...", "90", "45"], "90", "tp_t3_final"),
            ("4. Sur la pelle, une ......... optique détecte le passage du rayon laser.", ["Choisir...", "cellule", "boussole"], "cellule", "tp_t4_final"),
            ("5. Le nivellement laser permet d'éviter de ......... trop profondément.", ["Choisir...", "creuser", "éclairer"], "creuser", "tp_t5_final"),
            ("6. Les réflexions internes dans le prisme suivent la loi i = .........", ["Choisir...", "i'", "0°"], "i'", "tp_t6_final"),
            ("7. Si le trépied est heurté, une sécurité ......... le faisceau laser.", ["Choisir...", "coupe", "amplifie"], "coupe", "tp_t7_final"),
            ("8. La précision d'un laser de chantier est de l'ordre du .........", ["Choisir...", "millimètre", "kilomètre"], "millimètre", "tp_t8_final"),
            ("9. On utilise une ......... graduée pour contrôler manuellement les hauteurs.", ["Choisir...", "mire", "pelle"], "mire", "tp_t9_final"),
            ("10. Le laser rotatif est indispensable pour régler la pente d'une .........", ["Choisir...", "tranchée", "grue"], "tranchée", "tp_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 1 : TÉLÉMÈTRE LASER DE CHANTIER & PLAQUE CIBLE
    # =========================================================================
    1: {
        "questions": [
            {"id": "qtp1_1", "q": "Sur quel principe physique repose la mesure de distance d'un télémètre laser de chantier ?", "options": ["Le temps de vol (aller-retour) ou le déphasage d'un faisceau laser réfléchi sur une cible", "La mesure de la température de l'air entre deux murs", "Le calcul du poids de l'appareil"], "rep": "Le temps de vol (aller-retour) ou le déphasage d'un faisceau laser réfléchi sur une cible"},
            {"id": "qtp1_2", "q": "Pourquoi utilise-t-on une plaque cible réfléchissante en plein soleil à plus de 50 mètres ?", "options": ["Pour concentrer la réflexion vers le capteur et compenser la forte luminosité ambiante", "Pour refroidir le faisceau laser", "Pour dévier le laser vers le sol"], "rep": "Pour concentrer la réflexion vers le capteur et compenser la forte luminosité ambiante"},
            {"id": "qtp1_3", "q": "Que se passe-t-il si le faisceau d'un télémètre frappe une surface noire mate ou vitrée très inclinée ?", "options": ["Trop peu de lumière est réfléchie vers le capteur : une erreur de mesure s'affiche", "La distance mesurée est divisée par dix", "Le faisceau traverse le béton"], "rep": "Trop peu de lumière est réfléchie vers le capteur : une erreur de mesure s'affiche"},
            {"id": "qtp1_4", "q": "Si l'impulsion laser met 200 nanosecondes (200 × 10⁻⁹ s) pour faire l'aller-retour (c = 3 × 10⁸ m/s), quelle est la distance D ?", "options": ["30 mètres (car D = c × t / 2)", "60 mètres", "3 mètres"], "rep": "30 mètres (car D = c × t / 2)"},
            {"id": "qtp1_5", "q": "Pourquoi divise-t-on par 2 le temps de trajet mesuré par le télémètre ?", "options": ["Parce que la lumière effectue un aller vers la cible puis un retour par réflexion", "Parce que le laser va deux fois moins vite au retour", "Parce que l'écran affiche en demi-mètres"], "rep": "Parce que la lumière effectue un aller vers la cible puis un retour par réflexion"},
            {"id": "qtp1_6", "q": "Quel type de réflexion se produit sur un mur en béton brut (non lisse) visé par un télémètre ?", "options": ["Une réflexion diffuse (une partie des rayons repart vers le télémètre)", "Une réflexion spéculaire totale à 90° uniquement", "Une réfraction magnétique"], "rep": "Une réflexion diffuse (une partie des rayons repart vers le télémètre)"},
            {"id": "qtp1_7", "q": "Quelle fonction mathématique intégrée au télémètre permet de mesurer la hauteur d'une façade inaccessible en deux visées ?", "options": ["Le théorème de Pythagore indirect", "La règle de trois", "Le calcul intégral"], "rep": "Le théorème de Pythagore indirect"},
            {"id": "qtp1_8", "q": "Quelle est la précision courante d'un télémètre laser professionnel sur un chantier de BTP ?", "options": ["± 1,0 mm à ± 1,5 mm", "± 15 cm", "± 1 mètre"], "rep": "± 1,0 mm à ± 1,5 mm"},
            {"id": "qtp1_9", "q": "Dans la simulation, sous quel pourcentage de retour optique le télémètre affiche-t-il « SIGNAL TROP FAIBLE (Utiliser plaque cible) » ?", "options": ["Sous 35 %", "Sous 99 %", "Sous 5 %"], "rep": "Sous 35 %"},
            {"id": "qtp1_10", "q": "Quelle règle de sécurité s'applique lors de l'utilisation d'un télémètre laser de classe 2 sur un chantier ?", "options": ["Ne jamais diriger le faisceau vers les yeux des ouvriers ou des conducteurs d'engins", "Porter des gants isolants haute tension", "Utiliser l'appareil uniquement sous la pluie"], "rep": "Ne jamais diriger le faisceau vers les yeux des ouvriers ou des conducteurs d'engins"},
        ],
        "trous": [
            ("1. Le télémètre mesure le temps d'.........-retour de la lumière.", ["Choisir...", "aller", "demi"], "aller", "tp_t1_final"),
            ("2. La formule de distance est D = (c × t) divisé par .........", ["Choisir...", "2", "4"], "2", "tp_t2_final"),
            ("3. Sur du béton rugueux, la lumière subit une réflexion .........", ["Choisir...", "diffuse", "spéculaire"], "diffuse", "tp_t3_final"),
            ("4. En plein soleil, on place une ......... cible pour renforcer le retour.", ["Choisir...", "plaque", "brique"], "plaque", "tp_t4_final"),
            ("5. Une surface noire ......... une grande partie du faisceau laser.", ["Choisir...", "absorbe", "réfléchit"], "absorbe", "tp_t5_final"),
            ("4. En plein soleil, on place une ......... cible pour renforcer le retour.", ["Choisir...", "plaque", "brique"], "plaque", "tp_t4_final"),
            ("5. Une surface noire ......... une grande partie du faisceau laser.", ["Choisir...", "absorbe", "réfléchit"], "absorbe", "tp_t5_final"),
            ("6. Le télémètre remplace avantageusement le ......... à ruban sur longues distances.", ["Choisir...", "mètre", "niveau"], "mètre", "tp_t6_final"),
            ("7. La vitesse de la lumière c vaut environ 300 000 ......... par seconde.", ["Choisir...", "kilomètres", "mètres"], "kilomètres", "tp_t7_final"),
            ("8. Une vitre propre laisse ......... le laser au lieu de le renvoyer.", ["Choisir...", "traverser", "bloquer"], "traverser", "tp_t8_final"),
            ("9. La fonction ......... permet de calculer une hauteur à distance.", ["Choisir...", "Pythagore", "Thalès"], "Pythagore", "tp_t9_final"),
            ("10. Le point laser rouge permet de ......... précisément la zone à mesurer.", ["Choisir...", "viser", "chauffer"], "viser", "tp_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 2 : BALISAGE RÉTRORÉFLÉCHISSANT DE CHANTIER (MICROBILLES)
    # =========================================================================
    2: {
        "questions": [
            {"id": "qtp2_1", "q": "Quel phénomène optique permet à un panneau de chantier temporaire de briller intensément la nuit dans les phares d'une voiture ?", "options": ["La rétroréflexion (renvoi de la lumière vers sa source)", "La phosphorescence nucléaire", "L'éclairage électrique intégré dans chaque panneau"], "rep": "La rétroréflexion (renvoi de la lumière vers sa source)"},
            {"id": "qtp2_2", "q": "De quels éléments microscopiques sont recouverts les films rétroréfléchissants des panneaux TP et des gilets haute visibilité ?", "options": ["Des microbilles de verre ou des microprismes", "Des paillettes de bois verni", "De la poudre de craie blanche"], "rep": "Des microbilles de verre ou des microprismes"},
            {"id": "qtp2_3", "q": "Pourquoi un panneau peint simplement en blanc mat est-il beaucoup moins visible la nuit qu'un panneau rétroréfléchissant ?", "options": ["La peinture blanche diffuse la lumière dans toutes les directions au lieu de la renvoyer vers le conducteur", "La peinture blanche absorbe 100 % des phares", "Le blanc devient noir la nuit"], "rep": "La peinture blanche diffuse la lumière dans toutes les directions au lieu de la renvoyer vers le conducteur"},
            {"id": "qtp2_4", "q": "Dans un film de Classe 2 ou Classe 3 (microprismes), quel principe optique renvoie la lumière des phares vers l'automobiliste ?", "options": ["La réflexion totale sur les faces inclinées de micro-coins de cube", "La diffraction par fentes fines", "L'absorption infrarouge"], "rep": "La réflexion totale sur les faces inclinées de micro-coins de cube"},
            {"id": "qtp2_5", "q": "Quelle classe de film rétroréfléchissant est obligatoire sur les autoroutes et routes à grande circulation pour les chantiers temporaires ?", "options": ["La Classe 2 (haute intensité, visible à plus de 250 m)", "La Classe 0 (non réfléchissante)", "Du papier peint standard"], "rep": "La Classe 2 (haute intensité, visible à plus de 250 m)"},
            {"id": "qtp2_6", "q": "Que se passe-t-il si un panneau de chantier est posé trop incliné (ex : 40° par rapport à la route) au bord de la chaussée ?", "options": ["L'angle d'incidence dépasse la plage de rétroréflexion et le panneau paraît sombre", "Le panneau devient deux fois plus lumineux", "Les phares sont déviés vers le ciel"], "rep": "L'angle d'incidence dépasse la plage de rétroréflexion et le panneau paraît sombre"},
            {"id": "qtp2_7", "q": "Pourquoi les agents de chantier portent-ils des bandes grises argentées sur leurs vestes et pantalons ?", "options": ["Ces bandes contiennent des microbilles de verre qui rétroréfléchissent les phares des engins et voitures", "Pour renforcer les coutures contre les déchirures", "Pour isoler du froid en hiver"], "rep": "Ces bandes contiennent des microbilles de verre qui rétroréfléchissent les phares des engins et voitures"},
            {"id": "qtp2_8", "q": "Quel geste d'entretien simple sur un chantier boueux permet de maintenir l'efficacité du balisage nocturne ?", "options": ["Laver régulièrement les panneaux et cônes K5a pour que la boue ne bloque pas les microbilles", "Repeindre les panneaux au pinceau tous les soirs", "Coucher les panneaux au sol la nuit"], "rep": "Laver régulièrement les panneaux et cônes K5a pour que la boue ne bloque pas les microbilles"},
            {"id": "qtp2_9", "q": "Quelle est la distance de visibilité nocturne minimale assurée par un balisage rétroréfléchissant de Classe 2 en feux de croisement ?", "options": ["Environ 250 mètres", "10 mètres", "2 kilomètres"], "rep": "Environ 250 mètres"},
            {"id": "qtp2_10", "q": "Dans la simulation de balisage nocturne, jusqu'à quel angle d'observation (angle d'entrée) le panneau reste-t-il parfaitement visible ?", "options": ["Jusqu'à ± 30°", "Uniquement à 0,0° pile", "Jusqu'à 90°"], "rep": "Jusqu'à ± 30°"},
        ],
        "trous": [
            ("1. Les panneaux de chantier renvoient la lumière des phares par .........", ["Choisir...", "rétroréflexion", "diffusion"], "rétroréflexion", "tp_t1_final"),
            ("2. Les films réfléchissants contiennent des ......... de verre.", ["Choisir...", "microbilles", "plaques"], "microbilles", "tp_t2_final"),
            ("3. La lumière est renvoyée directement vers sa ......... d'émission.", ["Choisir...", "source", "cible"], "source", "tp_t3_final"),
            ("4. Sur autoroute, les panneaux temporaires doivent être de Classe .........", ["Choisir...", "2", "1"], "2", "tp_t4_final"),
            ("5. Une peinture blanche classique produit une réflexion ......... peu visible.", ["Choisir...", "diffuse", "totale"], "diffuse", "tp_t5_final"),
            ("6. Les bandes des gilets de sécurité assurent la visibilité .........", ["Choisir...", "nocturne", "thermique"], "nocturne", "tp_t6_final"),
            ("7. Un panneau de Classe 2 est visible à plus de ......... mètres la nuit.", ["Choisir...", "250", "20"], "250", "tp_t7_final"),
            ("8. La boue sur un cône de chantier ......... les rayons lumineux incidents.", ["Choisir...", "bloque", "amplifie"], "bloque", "tp_t8_final"),
            ("9. Les microprismes utilisent la réflexion interne sur des coins de .........", ["Choisir...", "cube", "sphère"], "cube", "tp_t9_final"),
            ("10. Le panneau doit être orienté ......... à l'axe de la chaussée.", ["Choisir...", "perpendiculairement", "parallèlement"], "perpendiculairement", "tp_t10_final"),
        ]
    }
}


def mettre_a_jour_tp_matplotlib(sujet_idx):
    """Banc d'essai expérimental réaliste adapté au chantier TP tiré au sort."""
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 260)
    ax.invert_yaxis()
    ax.axis("off")

    # =========================================================================
    # SUJET 0 : LASER ROTATIF DE NIVELLEMENT & PELLE HYDRAULIQUE
    # =========================================================================
    if sujet_idx == 0:
        hauteur_godet = st.session_state.get("slider_tp_s0", 1.65)
        cote_projet = 1.50
        ecart_cm = (hauteur_godet - cote_projet) * 100.0

        # Sol naturel et fond de fouille projet
        ax.add_patch(patches.Rectangle((20, 190), 560, 55, facecolor="#78350f", edgecolor="#92400e"))
        ax.plot([20, 580], [190, 190], color="#f59e0b", lw=2, ls="--")
        ax.text(570, 184, "Fond de fouille projet (Cote 0,00 m)", color="#fbbf24", fontsize=7.5, fontweight="bold", ha="right")

        # Trépied et laser rotatif à gauche (plan laser horizontal à y=110)
        ax.plot([75, 50], [130, 190], color="#cbd5e1", lw=2.5)
        ax.plot([75, 100], [130, 190], color="#cbd5e1", lw=2.5)
        ax.add_patch(patches.Rectangle((63, 100), 24, 30, facecolor="#eab308", edgecolor="white"))
        ax.text(75, 92, "Laser Rotatif\n(Pentaprisme 90°)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        # Plan laser horizontal à y = 110
        ax.plot([87, 560], [110, 110], color="#ef4444", lw=2)
        ax.text(240, 103, "Plan laser horizontal de référence (+1,50 m)", color="#f87171", fontsize=7.5, fontweight="bold", ha="center")

        # Bras de pelle et cellule de réception mobile selon hauteur_godet
        y_godet = 190.0 - (hauteur_godet - cote_projet) * 120.0
        y_godet = max(145.0, min(225.0, y_godet))
        y_cellule = y_godet - 80.0

        ax.add_patch(patches.Rectangle((410, y_godet - 18), 45, 18, facecolor="#475569", edgecolor="#94a3b8", lw=1.5))
        ax.text(465, y_godet - 9, f"Godet ({hauteur_godet:.2f} m)", color="#cbd5e1", fontsize=7.5, fontweight="bold", va="center")

        # Mât et cellule de détection
        ax.plot([432, 432], [y_cellule - 15, y_godet - 18], color="#94a3b8", lw=3)
        ax.add_patch(patches.Rectangle((422, y_cellule - 15), 20, 30, facecolor="#0284c7", edgecolor="white", lw=1.5))
        ax.text(450, y_cellule, "Cellule TP", color="#38bdf8", fontsize=7.5, fontweight="bold", va="center")

        if abs(ecart_cm) <= 2.0:
            statut = "COTE ATTEINTE (± 2 cm) : Arrêter de creuser, fond de fouille conforme !"
            c_stat = "#22c55e"
            diag = "CONFORME"
        elif ecart_cm > 2.0:
            statut = f"TROP HAUT (+{ecart_cm:.0f} cm) : Continuer à creuser la tranchée."
            c_stat = "#f59e0b"
            diag = "À CREUSER"
        else:
            statut = f"TROP BAS ({ecart_cm:.0f} cm) : Remblayer et compacter le fond !"
            c_stat = "#ef4444"
            diag = "TROP PROFOND"

        ax.text(25, 20, "TERRASSEMENT TP : GUIDAGE PAR LASER ROTATIF (DÉVIATION 90°)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 248, f"Cote projet : 1,50 m | Hauteur godet : {hauteur_godet:.2f} m | Écart : {ecart_cm:+.1f} cm",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tp_mesure_courante = (f"Hauteur = {hauteur_godet:.2f} m", f"Écart = {ecart_cm:+.1f} cm", "Déviation = 90°", diag)

    # =========================================================================
    # SUJET 1 : TÉLÉMÈTRE LASER DE CHANTIER & PLAQUE CIBLE
    # =========================================================================
    elif sujet_idx == 1:
        dist_m = st.session_state.get("slider_tp_s1", 45.0)
        avec_cible = st.session_state.get("check_tp_cible_s1", True)

        c_ms = 299792458.0
        temps_ns = (2.0 * dist_m / c_ms) * 1e9
        base_signal = 95.0 if avec_cible else 58.0
        signal_retour = max(5.0, base_signal - (dist_m * 0.45))

        ax.add_patch(patches.Rectangle((40, 105), 55, 36, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(67, 123, "Télémètre\nLaser", color="#0f172a", fontsize=7.5, fontweight="bold", ha="center", va="center")

        x_mur = 160.0 + (dist_m / 100.0) * 380.0
        ax.add_patch(patches.Rectangle((x_mur, 65), 22, 120, facecolor="#64748b", edgecolor="#cbd5e1", lw=1.5))
        ax.text(x_mur + 11, 55, f"Ouvrage ({dist_m:.0f} m)", color="#cbd5e1", fontsize=7.5, fontweight="bold", ha="center")

        if avec_cible:
            ax.add_patch(patches.Rectangle((x_mur - 5, 108), 5, 30, facecolor="#ef4444", edgecolor="white"))
            ax.text(x_mur - 8, 98, "Plaque cible", color="#fca5a5", fontsize=7, fontweight="bold", ha="right")

        ax.annotate("", xy=(x_mur - 5, 118), xytext=(95, 118), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))
        if signal_retour >= 35.0:
            ax.annotate("", xy=(95, 130), xytext=(x_mur - 5, 130), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            statut = f"MESURE VALIDÉE : D = {dist_m:.2f} m | Signal réfléchi : {signal_retour:.0f}%"
            c_stat = "#22c55e"
            diag = "MESURE OK"
        else:
            ax.annotate("", xy=((95 + x_mur) / 2, 145), xytext=(x_mur - 5, 130), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.5, ls="--"))
            statut = f"ERREUR SIGNAL ({signal_retour:.0f}% < 35%) : Activez la plaque cible réfléchissante !"
            c_stat = "#ef4444"
            diag = "SIGNAL FAIBLE"

        ax.text(25, 20, "MÉTRÉ DE CHANTIER : TÉLÉMÈTRE LASER (TEMPS DE VOL ALLER-RETOUR)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 235, f"Distance : {dist_m:.1f} m | Temps aller-retour : {temps_ns:.1f} ns | Retour optique : {signal_retour:.0f}%",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tp_mesure_courante = (f"D = {dist_m:.1f} m", f"t = {temps_ns:.1f} ns", f"Signal = {signal_retour:.0f}%", diag)

    # =========================================================================
    # SUJET 2 : BALISAGE RÉTRORÉFLÉCHISSANT DE CHANTIER (MICROBILLES)
    # =========================================================================
    else:
        angle_panneau = st.session_state.get("slider_tp_s2", 10.0)
        classe_film = st.session_state.get("radio_tp_classe_s2", "Classe 2 (Microprismes TP)")

        facteur_classe = 1.0 if "Classe 2" in classe_film else 0.55
        if abs(angle_panneau) <= 30.0:
            visibilite_pct = max(0.0, (100.0 - abs(angle_panneau) * 1.4) * facteur_classe)
        else:
            visibilite_pct = max(0.0, (58.0 - (abs(angle_panneau) - 30.0) * 3.5) * facteur_classe)

        ax.add_patch(patches.Rectangle((35, 115), 85, 42, facecolor="#1e293b", edgecolor="#38bdf8", lw=1.5))
        ax.text(77, 136, "VÉHICULE\n(Phares nuit)", color="white", fontsize=7.5, fontweight="bold", ha="center", va="center")

        xp, yp = 500.0, 136.0
        rad_p = math.radians(angle_panneau)
        dx_p = 30.0 * math.sin(rad_p)
        dy_p = 30.0 * math.cos(rad_p)
        ax.plot([xp - dx_p, xp + dx_p], [yp - dy_p, yp + dy_p], color="#f59e0b", lw=6)
        nom_classe_court = classe_film[:8]
        ax.text(xp, 88, f"Panneau AK5\n({nom_classe_court})", color="#fbbf24", fontsize=7.5, fontweight="bold", ha="center")

        ax.annotate("", xy=(xp, yp - 6), xytext=(120, 128), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2.5))

        if visibilite_pct >= 50.0:
            ax.annotate("", xy=(120, 144), xytext=(xp, yp + 6), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2.5))
            statut = f"BALISAGE CONFORME ({visibilite_pct:.0f}%) : Rétroréflexion nette à 250 m."
            c_stat = "#22c55e"
            diag = "VISIBLE (OK)"
        else:
            ax.annotate("", xy=(250, 210), xytext=(xp, yp + 6), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2, ls="--"))
            statut = f"DANGER CHANTIER ({visibilite_pct:.0f}%) : Panneau mal orienté ou classe insuffisante !"
            c_stat = "#ef4444"
            diag = "DANGER NUIT"

        ax.text(25, 20, "SÉCURITÉ CHANTIER : RÉTRORÉFLEXION SUR FILM À MICROBILLES", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 235, f"Orientation panneau : {angle_panneau:+.0f}° | Film : {classe_film} | Intensité renvoyée : {visibilite_pct:.0f}%",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tp_mesure_courante = (f"Angle = {angle_panneau:+.0f}°", nom_classe_court, f"Retour = {visibilite_pct:.0f}%", diag)

    return fig


def afficher_atelier_tp_complet(sujet_idx, verrouille=False):
    """Affiche les 10 QCM et les 10 trous spécifiques au chantier TP tiré au sort."""
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un chantier TP ci-dessus pour débloquer les 10 questions et les 10 phrases à trous correspondantes.")
        return

    banque = BANQUES_TP[sujet_idx]
    cle_session_ordre = f"ordre_quiz_tp_sujet_{sujet_idx}"

    if cle_session_ordre not in st.session_state:
        liste_q = list(banque["questions"])
        random.shuffle(liste_q)
        st.session_state[cle_session_ordre] = liste_q

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique Travaux Publics (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_session_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tp_at7_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Travaux Publics (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")

BANQUES_TRANSPORT = {
    # =========================================================================
    # BANQUE SUJET 0 : ANTÉVISEUR POIDS LOURD & ANGLES MORTS (MIROIR CONVEXE)
    # =========================================================================
    0: {
        "questions": [
            {"id": "qtr0_1", "q": "Où est installé le rétroviseur antéviseur (Classe VI) sur un camion poids lourd ?", "options": ["Au-dessus du pare-brise avant, orienté vers le pare-chocs", "Sur le pare-chocs arrière", "À l'intérieur de la remorque"], "rep": "Au-dessus du pare-brise avant, orienté vers le pare-chocs"},
            {"id": "qtr0_2", "q": "Quelle forme géométrique possède la glace d'un antéviseur ou d'un rétroviseur grand angle poids lourd ?", "options": ["Une surface convexe (bombée vers l'extérieur)", "Une surface concave (creuse)", "Une surface plane opaque"], "rep": "Une surface convexe (bombée vers l'extérieur)"},
            {"id": "qtr0_3", "q": "Quel est l'effet optique principal d'un miroir convexe sur le champ de vision du conducteur ?", "options": ["Il élargit considérablement l'angle de vue en réduisant la taille apparente des objets", "Il grossit les objets comme une loupe", "Il inverse le haut et le bas de la route"], "rep": "Il élargit considérablement l'angle de vue en réduisant la taille apparente des objets"},
            {"id": "qtr0_4", "q": "Pourquoi un cycliste ou un piéton arrêté juste devant la calandre d'un camion est-il invisible sans antéviseur ?", "options": ["La hauteur de la cabine et du capot crée un angle mort direct de plus de 2 mètres devant le véhicule", "Le pare-brise bloque la lumière du jour", "Les pneus avant masquent toute la route"], "rep": "La hauteur de la cabine et du capot crée un angle mort direct de plus de 2 mètres devant le véhicule"},
            {"id": "qtr0_5", "q": "Comment la loi de la réflexion (i = i') s'applique-t-elle sur un miroir convexe ?", "options": ["Elle s'applique en chaque point par rapport à la normale locale à la surface courbe", "Elle ne s'applique pas aux miroirs bombés", "L'angle réfléchi vaut toujours 0°"], "rep": "Elle s'applique en chaque point par rapport à la normale locale à la surface courbe"},
            {"id": "qtr0_6", "q": "Dans la simulation de manœuvre urbaine, que risque le conducteur si l'antéviseur est mal orienté (ex : 15° au lieu de 42°) ?", "options": ["Le piéton situé à 1,20 m devant le pare-chocs reste dans l'angle mort", "Le camion accélère tout seul", "Le rétroviseur reflète uniquement le ciel"], "rep": "Le piéton situé à 1,20 m devant le pare-chocs reste dans l'angle mort"},
            {"id": "qtr0_7", "q": "Quelle précaution le conducteur doit-il garder à l'esprit lorsqu'il observe un véhicule dans un miroir convexe ?", "options": ["Les objets paraissent plus petits et plus éloignés qu'ils ne le sont en réalité", "Les objets paraissent deux fois plus proches", "Les couleurs sont inversées"], "rep": "Les objets paraissent plus petits et plus éloignés qu'ils ne le sont en réalité"},
            {"id": "qtr0_8", "q": "Combien de rétroviseurs obligatoires équipent un tracteur routier moderne pour couvrir tous les angles morts ?", "options": ["6 rétroviseurs (2 principaux, 2 grand angle, 1 accostage droit, 1 antéviseur)", "1 seul rétroviseur central intérieur", "2 rétroviseurs identiques à une citadine"], "rep": "6 rétroviseurs (2 principaux, 2 grand angle, 1 accostage droit, 1 antéviseur)"},
            {"id": "qtr0_9", "q": "Quel dispositif complémentaire assiste désormais les miroirs optiques pour détecter les usagers vulnérables en ville ?", "options": ["Les radars latéraux et caméras d'angle mort (norme GSR2)", "Les phares longue portée au xénon", "Le régulateur de vitesse adaptatif"], "rep": "Les radars latéraux et caméras d'angle mort (norme GSR2)"},
            {"id": "qtr0_10", "q": "De quelle nature est l'image d'un piéton formée par le miroir convexe de l'antéviseur ?", "options": ["Une image virtuelle, droite et rétrécie", "Une image réelle et renversée", "Une ombre portée sur le tableau de bord"], "rep": "Une image virtuelle, droite et rétrécie"},
        ],
        "trous": [
            ("1. Le rétroviseur situé au-dessus du pare-brise d'un camion est l'.........", ["Choisir...", "antéviseur", "accosteur"], "antéviseur", "tr_t1_final"),
            ("2. Pour élargir le champ de vision, le miroir possède une forme .........", ["Choisir...", "convexe", "concave"], "convexe", "tr_t2_final"),
            ("3. L'antéviseur supprime l'angle ......... situé juste devant le pare-chocs.", ["Choisir...", "mort", "droit"], "mort", "tr_t3_final"),
            ("4. Dans un miroir convexe, les objets observés paraissent plus .........", ["Choisir...", "petits", "grands"], "petits", "tr_t4_final"),
            ("5. En chaque point du miroir courbe, la réflexion respecte i = .........", ["Choisir...", "i'", "90°"], "i'", "tr_t5_final"),
            ("6. Le rétroviseur d'......... surveille le côté droit de la cabine en ville.", ["Choisir...", "accostage", "intérieur"], "accostage", "tr_t6_final"),
            ("7. Les ......... et les piétons sont les usagers les plus exposés aux angles morts.", ["Choisir...", "cyclistes", "trains"], "cyclistes", "tr_t7_final"),
            ("8. La hauteur de la ......... d'un poids lourd masque la zone proche du sol.", ["Choisir...", "cabine", "remorque"], "cabine", "tr_t8_final"),
            ("9. L'image formée par un miroir convexe est toujours droite et .........", ["Choisir...", "virtuelle", "réelle"], "virtuelle", "tr_t9_final"),
            ("10. Le conducteur doit régler ses miroirs avant tout ......... du véhicule.", ["Choisir...", "départ", "lavage"], "départ", "tr_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 1 : PHARE À RÉFLECTEUR PARABOLIQUE (FEUX DE ROUTE)
    # =========================================================================
    1: {
        "questions": [
            {"id": "qtr1_1", "q": "Quelle est la forme géométrique du miroir métallisé situé derrière l'ampoule d'un phare automobile longue portée ?", "options": ["Un réflecteur parabolique (concave)", "Un miroir convexe bombé", "Un prisme triangulaire"], "rep": "Un réflecteur parabolique (concave)"},
            {"id": "qtr1_2", "q": "Où doit être placé le filament de l'ampoule (ou la source LED) pour que le phare projette un faisceau parallèle ?", "options": ["Au foyer F du miroir parabolique", "Contre la vitre avant du phare", "À l'infini derrière le moteur"], "rep": "Au foyer F du miroir parabolique"},
            {"id": "qtr1_3", "q": "Pourquoi un réflecteur parabolique permet-il d'éclairer la route à plus de 150 mètres sans disperser la lumière ?", "options": ["Tous les rayons issus du foyer F sont réfléchis parallèlement à l'axe optique", "Il multiplie la tension de la batterie par dix", "Il colore la lumière en ultraviolet"], "rep": "Tous les rayons issus du foyer F sont réfléchis parallèlement à l'axe optique"},
            {"id": "qtr1_4", "q": "Que se passe-t-il si une ampoule est mal clipsée et s'éloigne du foyer F du réflecteur ?", "options": ["Le faisceau devient convergent ou divergent : la portée d'éclairage chute et éblouit", "Le phare éclaire deux fois plus loin", "La couleur devient rouge"], "rep": "Le faisceau devient convergent ou divergent : la portée d'éclairage chute et éblouit"},
            {"id": "qtr1_5", "q": "Comment réalise-t-on le faisceau « feux de croisement » (code) pour ne pas éblouir les conducteurs arrivant en face ?", "options": ["Un cache métallique (coupelle) bloque les rayons vers le bas du réflecteur pour rabattre le faisceau vers la chaussée", "On éteint totalement le phare gauche", "On retourne le miroir parabolique"], "rep": "Un cache métallique (coupelle) bloque les rayons vers le bas du réflecteur pour rabattre le faisceau vers la chaussée"},
            {"id": "qtr1_6", "q": "Quel appareil utilise-t-on en atelier de contrôle technique ou de maintenance transport pour vérifier l'inclinaison du faisceau ?", "options": ["Un régloscope (contrôleur de phares)", "Un oscilloscope numérique", "Un manomètre de pression"], "rep": "Un régloscope (contrôleur de phares)"},
            {"id": "qtr1_7", "q": "Quelle est la pente réglementaire typique d'abaissement du faisceau des feux de croisement sur un véhicule ?", "options": ["Environ -1,0 % à -1,5 % (soit 10 à 15 cm de baisse tous les 10 mètres)", "+10 % vers le ciel", "0 % (strictement horizontal comme les feux de route)"], "rep": "Environ -1,0 % à -1,5 % (soit 10 à 15 cm de baisse tous les 10 mètres)"},
            {"id": "qtr1_8", "q": "Pourquoi l'intérieur d'un optique de phare est-il recouvert d'une fine couche d'aluminium sous vide ?", "options": ["Pour obtenir une réflexion spéculaire maximale (supérieure à 90 %)", "Pour isoler thermiquement le pare-chocs", "Pour alourdir l'avant du véhicule"], "rep": "Pour obtenir une réflexion spéculaire maximale (supérieure à 90 %)"},
            {"id": "qtr1_9", "q": "Quel défaut optique apparaît lorsque l'optique en polycarbonate d'un phare devient opaque et jauni par les UV ?", "options": ["Une diffusion parasite qui réduit la portée et éblouit les autres usagers", "Une augmentation de la focale du miroir", "Une réflexion totale interne"], "rep": "Une diffusion parasite qui réduit la portée et éblouit les autres usagers"},
            {"id": "qtr1_10", "q": "Quelle loi physique est vérifiée en chaque point de la parabole métallisée du phare ?", "options": ["L'angle d'incidence i est égal à l'angle de réflexion i' par rapport à la normale", "La lumière se propage en cercle autour de l'ampoule", "La vitesse de la lumière double après réflexion"], "rep": "L'angle d'incidence i est égal à l'angle de réflexion i' par rapport à la normale"},
        ],
        "trous": [
            ("1. Le miroir d'un phare longue portée a la forme d'une .........", ["Choisir...", "parabole", "sphère"], "parabole", "tr_t1_final"),
            ("2. L'ampoule doit être placée exactement au ......... F du réflecteur.", ["Choisir...", "foyer", "sommet"], "foyer", "tr_t2_final"),
            ("3. Les rayons issus du foyer repartent ......... à l'axe optique.", ["Choisir...", "parallèles", "perpendiculaires"], "parallèles", "tr_t3_final"),
            ("4. Le revêtement brillant assure une réflexion ......... de la lumière.", ["Choisir...", "spéculaire", "diffuse"], "spéculaire", "tr_t4_final"),
            ("5. Le contrôle de l'orientation des phares s'effectue avec un .........", ["Choisir...", "régloscope", "périscope"], "régloscope", "tr_t5_final"),
            ("6. Les feux de ......... possèdent une coupure nette pour ne pas éblouir.", ["Choisir...", "croisement", "route"], "croisement", "tr_t6_final"),
            ("7. Si l'ampoule est décalée du foyer, le faisceau ......... ou converge.", ["Choisir...", "diverge", "s'éteint"], "diverge", "tr_t7_final"),
            ("8. Une vitre de phare rayée ou jaunie provoque une ......... de la lumière.", ["Choisir...", "diffusion", "absorption"], "diffusion", "tr_t8_final"),
            ("9. En chaque point du réflecteur, on a l'égalité i = .........", ["Choisir...", "i'", "0°"], "i'", "tr_t9_final"),
            ("10. Le réglage de hauteur des phares compense la ......... du véhicule.", ["Choisir...", "charge", "vitesse"], "charge", "tr_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 2 : RÉTROVISEUR INTÉRIEUR JOUR / NUIT À PRISME
    # =========================================================================
    2: {
        "questions": [
            {"id": "qtr2_1", "q": "Quel composant optique constitue un rétroviseur intérieur manuel « jour/nuit » ?", "options": ["Un prisme en verre dont les deux faces (avant et arrière) ne sont pas parallèles", "Deux miroirs collés dos à dos", "Un écran LCD alimenté en 24 V"], "rep": "Un prisme en verre dont les deux faces (avant et arrière) ne sont pas parallèles"},
            {"id": "qtr2_2", "q": "En position « JOUR », quelle surface du rétroviseur renvoie la majeure partie de la lumière vers les yeux du conducteur ?", "options": ["La face arrière argentée très réfléchissante (environ 90 % de réflexion)", "La face avant en verre nu (4 %)", "Le boîtier en plastique noir"], "rep": "La face arrière argentée très réfléchissante (environ 90 % de réflexion)"},
            {"id": "qtr2_3", "q": "Que fait-on mécaniquement en basculant la languette sous le rétroviseur en position « NUIT » ?", "options": ["On fait pivoter le prisme d'environ 4° à 5° pour dévier le faisceau principal vers le plafond", "On éteint les phares de la voiture qui suit", "On baisse la luminosité du tableau de bord"], "rep": "On fait pivoter le prisme d'environ 4° à 5° pour dévier le faisceau principal vers le plafond"},
            {"id": "qtr2_4", "q": "En position « NUIT », quel pourcentage de lumière des phares suiveurs est renvoyé vers l'œil du conducteur par la face avant en verre ?", "options": ["Environ 4 % seulement (image atténuée anti-éblouissement)", "100 %", "50 %"], "rep": "Environ 4 % seulement (image atténuée anti-éblouissement)"},
            {"id": "qtr2_5", "q": "Pourquoi conserve-t-on un faible reflet de 4 % en position nuit au lieu de bloquer 100 % de la lumière ?", "options": ["Pour continuer à distinguer les phares du véhicule suiveur sans être ébloui", "Pour pouvoir se coiffer dans le noir", "Parce que le verre ne peut pas être rendu opaque"], "rep": "Pour continuer à distinguer les phares du véhicule suiveur sans être ébloui"},
            {"id": "qtr2_6", "q": "Comment fonctionne un rétroviseur intérieur moderne « électrochrome » (jour/nuit automatique) ?", "options": ["Deux capteurs optiques mesurent l'éblouissement et un gel électrique s'assombrit progressivement", "Un petit moteur fait tourner le miroir à 1000 tr/min", "Un rideau mécanique descend devant le miroir"], "rep": "Deux capteurs optiques mesurent l'éblouissement et un gel électrique s'assombrit progressivement"},
            {"id": "qtr2_7", "q": "Quel angle forme typiquement la face avant vitrée avec la face arrière argentée dans un prisme jour/nuit ?", "options": ["Environ 4° à 5° (prisme en coin)", "90°", "45°"], "rep": "Environ 4° à 5° (prisme en coin)"},
            {"id": "qtr2_8", "q": "Dans la simulation jour/nuit, où part le faisceau intense (90 %) réfléchi par la face arrière lorsque la languette nuit est activée ?", "options": ["Vers le plafond (pavillon) de l'habitacle, au-dessus de la tête du conducteur", "Directement dans les yeux du passager", "Vers le levier de vitesse"], "rep": "Vers le plafond (pavillon) de l'habitacle, au-dessus de la tête du conducteur"},
            {"id": "qtr2_9", "q": "Pourquoi le verre nu de la face avant réfléchit-il environ 4 % de la lumière incidente ?", "options": ["C'est la réflexion vitreuse partielle due au changement d'indice entre l'air (n=1) et le verre (n=1,5)", "C'est dû à la poussière sur la vitre", "Parce que la vitre est peinte en gris"], "rep": "C'est la réflexion vitreuse partielle due au changement d'indice entre l'air (n=1) et le verre (n=1,5)"},
            {"id": "qtr2_10", "q": "Quel danger entraîne l'éblouissement nocturne dans le rétroviseur intérieur pour un conducteur ?", "options": ["Une perte temporaire d'acuité visuelle et un allongement du temps de réaction", "Une crevaison immédiate", "Une hausse de la consommation de carburant"], "rep": "Une perte temporaire d'acuité visuelle et un allongement du temps de réaction"},
        ],
        "trous": [
            ("1. Le rétroviseur jour/nuit utilise un ......... en verre à faces non parallèles.", ["Choisir...", "prisme", "cylindre"], "prisme", "tr_t1_final"),
            ("2. En mode JOUR, la face arrière ......... renvoie 90 % de la lumière.", ["Choisir...", "argentée", "transparente"], "argentée", "tr_t2_final"),
            ("3. En mode NUIT, on bascule la ......... située sous le rétroviseur.", ["Choisir...", "languette", "pédale"], "languette", "tr_t3_final"),
            ("4. Le basculement fait pivoter le miroir d'environ ......... degrés.", ["Choisir...", "4", "45"], "4", "tr_t4_final"),
            ("5. Le faisceau intense de 90 % est alors dévié vers le ......... de la voiture.", ["Choisir...", "plafond", "volant"], "plafond", "tr_t5_final"),
            ("6. La face avant en verre ne renvoie que ......... % de lumière vers l'œil.", ["Choisir...", "4", "85"], "4", "tr_t6_final"),
            ("7. Ce système évite l'......... du conducteur par les phares suiveurs.", ["Choisir...", "éblouissement", "endormissement"], "éblouissement", "tr_t7_final"),
            ("8. Chaque réflexion sur les deux faces obéit à la loi i = .........", ["Choisir...", "i'", "90°"], "i'", "tr_t8_final"),
            ("9. Les versions automatiques modernes sont dites .........", ["Choisir...", "électrochromes", "paraboliques"], "électrochromes", "tr_t9_final"),
            ("10. L'indice de réfraction du verre du prisme vaut environ .........", ["Choisir...", "1.5", "0.5"], "1.5", "tr_t10_final"),
        ]
    }
}


def mettre_a_jour_transport_matplotlib(sujet_idx):
    """Banc d'essai expérimental réaliste adapté au transport routier."""
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 260)
    ax.invert_yaxis()
    ax.axis("off")

    # =========================================================================
    # SUJET 0 : ANTÉVISEUR POIDS LOURD & ANGLE MORT AVANT (SYNCHRONISÉ)
    # =========================================================================
    if sujet_idx == 0:
        ang_ante = st.session_state.get("slider_tr_s0", 25.0)
        dist_pieton = st.session_state.get("slider_tr_pieton_s0", 1.20)

        # Chaussée
        ax.add_patch(patches.Rectangle((20, 210), 560, 35, facecolor="#334155", edgecolor="#64748b"))

        # Cabine Poids Lourd (pare-chocs avant à x = 185)
        ax.add_patch(patches.Rectangle((40, 75), 145, 135, facecolor="#1e3a8a", edgecolor="#93c5fd", lw=1.5))
        ax.add_patch(patches.Rectangle((145, 85), 35, 55, facecolor="#38bdf8", alpha=0.4, edgecolor="white"))
        ax.text(105, 145, "CABINE\nPOIDS LOURD", color="white", fontsize=8.5, fontweight="bold", ha="center", va="center")

        # Bras et miroir antéviseur convexe au-dessus du pare-brise (x=195, y=68)
        ax.plot(list((180, 195)), list((75, 68)), color="#cbd5e1", lw=2.5)
        xm, ym = 195.0, 68.0
        rad_a = math.radians(ang_ante)
        dx_m = 22.0 * math.cos(rad_a)
        dy_m = 22.0 * math.sin(rad_a)
        ax.plot(list((xm - dx_m, xm + dx_m)), list((ym - dy_m, ym + dy_m)), color="#eab308", lw=4.5)
        ax.text(xm + 12, ym - 12, f"Antéviseur ({ang_ante:.0f}°)", color="#fde047", fontsize=7.5, fontweight="bold")

        # Piéton devant le pare-chocs (x = 185 + dist_pieton * 130)
        xp = 185.0 + dist_pieton * 130.0
        ax.add_patch(patches.Rectangle((xp - 7, 165), 14, 45, facecolor="#f97316", edgecolor="white", zorder=4))
        ax.add_patch(patches.Circle((xp, 156), 7, facecolor="#fed7aa", edgecolor="white", zorder=4))
        ax.text(xp, 142, f"Piéton ({dist_pieton:.2f} m)", color="#fdba74", fontsize=7.5, fontweight="bold", ha="center", zorder=5)

        # Cône de vision réfléchi au sol (plus ang_ante augmente, plus le cône se rapproche du pare-chocs x=185)
        # À 42° et plus, le cône couvre dès x = 185 (pied du pare-chocs) jusqu'à x = 395 (soit 0 m à 1,60 m)
        x_champ_min = max(185.0, 185.0 + (42.0 - ang_ante) * 11.0)
        x_champ_max = x_champ_min + 210.0

        # Détection exacte sur la largeur du piéton
        pieton_vu = (x_champ_min <= xp + 7) and (xp - 7 <= x_champ_max)

        couleur_cone = "#22c55e" if pieton_vu else "#ef4444"
        ax.fill(list((xm, x_champ_min, x_champ_max)), list((ym, 210, 210)), color=couleur_cone, alpha=0.22, zorder=2)
        ax.plot(list((xm, x_champ_min)), list((ym, 210)), color=couleur_cone, lw=1.2, ls="--")
        ax.plot(list((xm, x_champ_max)), list((ym, 210)), color=couleur_cone, lw=1.2, ls="--")

        # Rayon réfléchi de l'antéviseur vers les yeux du conducteur dans la cabine (x=155, y=108)
        ax.annotate("", xy=(155, 108), xytext=(xm, ym), arrowprops=dict(arrowstyle="->", color=couleur_cone, lw=2.2), zorder=5)

        if pieton_vu:
            ax.annotate("", xy=(xm, ym), xytext=(xp, 165), arrowprops=dict(arrowstyle="->", color="#fde047", lw=1.8, ls=":"), zorder=4)
            ax.annotate("", xy=(155, 108), xytext=(xm, ym), arrowprops=dict(arrowstyle="->", color=couleur_cone, lw=2.2), zorder=5)
            statut = f"USAGER DÉTECTÉ : Le piéton à {dist_pieton:.2f} m est visible dans l'antéviseur !"
            c_stat = "#22c55e"
            diag = "VISIBLE (OK)"
        else:
            ax.annotate("", xy=(155, 108), xytext=(xm, ym), arrowprops=dict(arrowstyle="->", color=couleur_cone, lw=2.2, ls="--"), zorder=5)
            statut = f"DANGER ANGLE MORT : Piéton à {dist_pieton:.2f} m hors du champ ! Inclinez l'antéviseur à 42°."
            c_stat = "#ef4444"
            diag = "ANGLE MORT"

        ax.text(25, 20, "SÉCURITÉ TRANSPORT : RÉGLAGE DE L'ANTÉVISEUR POIDS LOURD (CLASSE VI)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 248, f"Inclinaison antéviseur : {ang_ante:.0f}° | Distance piéton : {dist_pieton:.2f} m | Statut : {diag}",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tr_mesure_courante = (f"Miroir = {ang_ante:.0f}°", f"Piéton = {dist_pieton:.2f} m", "Miroir convexe", diag)

    # =========================================================================
    # SUJET 1 : PHARE À RÉFLECTEUR PARABOLIQUE (POSITION DE L'AMPOULE AU FOYER)
    # =========================================================================
    elif sujet_idx == 1:
        decalage_foyer_mm = st.session_state.get("slider_tr_s1", 0.0)

        ys_para = [130 + dy for dy in range(-65, 66, 5)]
        xs_para = [60 + (dy ** 2) / 220.0 for dy in range(-65, 66, 5)]
        ax.plot(xs_para, ys_para, color="#cbd5e1", lw=4)
        ax.text(55, 55, "Réflecteur\nParabolique", color="#cbd5e1", fontsize=7.5, fontweight="bold", ha="center")

        xf = 115.0
        x_amp = xf + decalage_foyer_mm * 3.0
        ax.scatter(xf, 130, color="#38bdf8", s=40, zorder=4)
        ax.text(xf, 115, "Foyer F", color="#38bdf8", fontsize=7, fontweight="bold", ha="center")

        ax.add_patch(patches.Circle((x_amp, 130), 7, facecolor="#fde047", edgecolor="#f59e0b", lw=1.5, zorder=5))
        ax.text(x_amp, 148, f"Ampoule ({decalage_foyer_mm:+.1f} mm)", color="#fde047", fontsize=7, fontweight="bold", ha="center")

        # Physique réelle : decalage > 0 (ampoule plus loin du miroir que F) => faisceau CONVERGENT (pente négative pour dy > 0)
        pente = -decalage_foyer_mm * 0.035
        for dy_r in [-48, -24, 24, 48]:
            xr_hit = 60 + (dy_r ** 2) / 220.0
            yr_hit = 130 + dy_r
            ax.plot([x_amp, xr_hit], [130, yr_hit], color="#fde047", lw=1.2, ls=":")
            y_fin = yr_hit + (550 - xr_hit) * (pente * (dy_r / 48.0))
            c_ray = "#22c55e" if abs(decalage_foyer_mm) <= 1.0 else "#f59e0b"
            ax.annotate("", xy=(550, y_fin), xytext=(xr_hit, yr_hit), arrowprops=dict(arrowstyle="->", color=c_ray, lw=2))

        if abs(decalage_foyer_mm) <= 1.0:
            statut = "FAISCEAU PARALLÈLE OPTIMAL : Portée maximale (> 150 m) sans éblouissement."
            c_stat = "#22c55e"
            diag = "PARALLÈLE (OK)"
        elif decalage_foyer_mm > 1.0:
            statut = "AMPOULE TROP AVANCÉE (au-delà de F) : Faisceau convergent qui croise et éblouit en face."
            c_stat = "#ef4444"
            diag = "CONVERGENT"
        else:
            statut = "AMPOULE TROP RECULÉE (entre miroir et F) : Faisceau divergent, perte de portée sur la route."
            c_stat = "#f59e0b"
            diag = "DIVERGENT"


        ax.text(25, 20, "ÉCLAIRAGE VÉHICULE : RÉFLECTEUR PARABOLIQUE & POSITION FOYER F", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 235, f"Écart au foyer F : {decalage_foyer_mm:+.1f} mm | Divergence faisceau : {abs(decalage_foyer_mm)*2.0:.1f}°",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tr_mesure_courante = (f"Écart F = {decalage_foyer_mm:+.1f} mm", f"Angle = {abs(decalage_foyer_mm)*2.0:.1f}°", "Tolérance ±1 mm", diag)


    # =========================================================================
    # SUJET 2 : RÉTROVISEUR INTÉRIEUR JOUR / NUIT À PRISME (PHYSIQUE EXACTE)
    # =========================================================================
    else:
        mode_retro = st.session_state.get("radio_tr_mode_s2", "Position JOUR (Réflexion 90%)")
        est_nuit = "NUIT" in mode_retro

        # 1. Œil du conducteur à gauche (x=110, y=110)
        ax.add_patch(patches.Circle((110, 110), 14, facecolor="#1e293b", edgecolor="#38bdf8", lw=2))
        ax.text(110, 138, "Œil du Conducteur", color="#38bdf8", fontsize=8, fontweight="bold", ha="center")

        # 2. Prisme en coin à droite (x=475, y=125)
        # L'angle du prisme est élargi visuellement pour bien distinguer les deux faces
        if not est_nuit:
            # MODE JOUR : Face arrière argentée verticale (renvoie 90% horizontalement vers l'œil)
            # Face avant vitrée inclinée vers le bas (renvoie 4% vers le tableau de bord)
            poly_prisme = patches.Polygon([(470, 90), (486, 90), (486, 160), (464, 160)], facecolor="#38bdf8", alpha=0.45, edgecolor="white", lw=1.5)
            ax.plot(list((486, 486)), list((90, 160)), color="#eab308", lw=4.5)
        else:
            # MODE NUIT (basculement vers le haut) :
            # Face avant vitrée devient verticale (renvoie 4% horizontalement vers l'œil)
            # Face arrière argentée bascule vers le haut (renvoie 90% vers le plafond)
            poly_prisme = patches.Polygon([(468, 90), (484, 88), (490, 158), (468, 160)], facecolor="#38bdf8", alpha=0.45, edgecolor="white", lw=1.5)
            ax.plot(list((484, 490)), list((88, 158)), color="#eab308", lw=4.5)

        ax.add_patch(poly_prisme)
        ax.text(478, 62, "Prisme Verre\n+ Face Argentée (jaune)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        # 3. Rayon incident venant des phares arrière (légèrement plongeant vers y=125)
        ax.annotate("", xy=(468, 125), xytext=(110, 175), arrowprops=dict(arrowstyle="->", color="#fde047", lw=2.5))
        ax.text(275, 172, "Rayon incident : Phares du véhicule suiveur (100 %)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center", rotation=-8)

        if not est_nuit:
            # MODE JOUR :
            # - 90% réfléchi par la face arrière verticale -> part vers le haut gauche (vers l'œil à y=110)
            ax.annotate("", xy=(126, 110), xytext=(484, 125), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=3))
            ax.text(295, 102, "Faisceau principal réfléchi (face arrière) : 90 % -> Vision claire", color="#f87171", fontsize=7.5, fontweight="bold", ha="center")

            # - 4% réfléchi par la face avant inclinée -> part vers le bas (vers le levier de vitesse)
            ax.annotate("", xy=(310, 215), xytext=(467, 130), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.5, ls=":"))
            ax.text(395, 212, "Reflet vitreux (4 %) vers le bas", color="#94a3b8", fontsize=7, style="italic", ha="center")

            statut = "MODE JOUR : Réflexion maximale (90 %) par la face arrière argentée."
            c_stat = "#f59e0b"
            diag = "90% (JOUR)"
        else:
            # MODE NUIT :
            # - 90% réfléchi par la face arrière basculée -> part très haut vers le plafond
            ax.annotate("", xy=(260, 28), xytext=(486, 122), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2.5, ls="--"))
            ax.text(320, 46, "Faisceau éblouissant (90 %) dévié vers le plafond", color="#f87171", fontsize=7.5, fontweight="bold", ha="center")

            # - 4% réfléchi par la face avant verticale -> part vers l'œil à y=110
            ax.annotate("", xy=(126, 110), xytext=(468, 125), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            ax.text(295, 102, "Reflet vitreux atténué (face avant) : 4 % -> Anti-éblouissement", color="#22c55e", fontsize=7.5, fontweight="bold", ha="center")

            statut = "MODE NUIT ACTIF : Éblouissement supprimé (4 % vers l'œil, 90 % au plafond)."
            c_stat = "#22c55e"
            diag = "4% (NUIT OK)"

        ax.text(25, 20, "CONFORT & SÉCURITÉ : RÉTROVISEUR INTÉRIEUR PRISMATIQUE JOUR / NUIT", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        retour_txt = "4 %" if est_nuit else "90 %"
        ax.text(300, 242, f"Configuration : {mode_retro} | Angle prisme : 4,5° | Intensité reçue : {retour_txt}",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.tr_mesure_courante = (mode_retro[:13], "Prisme = 4,5°", f"Retour = {retour_txt}", diag)
    return fig


def afficher_atelier_transport_complet(sujet_idx, verrouille=False):
    """Affiche les 10 QCM et les 10 trous spécifiques au sujet Transport Routier tiré au sort."""
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort un sujet Transport Routier ci-dessus pour débloquer les 10 questions et les 10 phrases à trous correspondantes.")
        return

    banque = BANQUES_TRANSPORT[sujet_idx]
    cle_session_ordre = f"ordre_quiz_tr_sujet_{sujet_idx}"

    if cle_session_ordre not in st.session_state:
        liste_q = list(banque["questions"])
        random.shuffle(liste_q)
        st.session_state[cle_session_ordre] = liste_q

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique Transport Routier (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_session_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tr_at8_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Transport Routier (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")

BANQUES_GEOMETRE = {
    # =========================================================================
    # BANQUE SUJET 0 : STATION TOTALE & PRISME RÉFLECTEUR (COIN DE CUBE)
    # =========================================================================
    0: {
        "questions": [
            {"id": "qgeo0_1", "q": "Quel type de réflecteur est monté sur la canne tenue par l'opérateur face à une station totale ?", "options": ["Un prisme en coin de cube (rétroréflecteur trièdre)", "Un miroir plan de salle de bain", "Une lentille convergente en plastique"], "rep": "Un prisme en coin de cube (rétroréflecteur trièdre)"},
            {"id": "qgeo0_2", "q": "Pourquoi le prisme de topographie renvoie-t-il le faisceau infrarouge exactement vers la station totale même s'il n'est pas parfaitement perpendiculaire ?", "options": ["Ses trois faces internes à 90° réfléchissent le rayon parallèlement à sa direction d'entrée", "Le prisme contient un moteur GPS qui suit la station", "La lumière se courbe sous l'effet de la gravité"], "rep": "Ses trois faces internes à 90° réfléchissent le rayon parallèlement à sa direction d'entrée"},
            {"id": "qgeo0_3", "q": "Quelle est la précision millimétrique courante d'une station totale mesurant sur un prisme à 200 mètres ?", "options": ["± 1 mm + 1,5 ppm (environ ± 1,3 mm)", "± 25 cm", "± 1,5 mètre"], "rep": "± 1 mm + 1,5 ppm (environ ± 1,3 mm)"},
            {"id": "qgeo0_4", "q": "Qu'appelle-t-on la « constante de prisme » (souvent -34,4 mm ou 0 mm) à paramétrer dans la station totale ?", "options": ["Le décalage optique dû au trajet et à l'indice du verre à l'intérieur du prisme", "Le poids de la canne télescopique en grammes", "La hauteur du trépied au-dessus du sol"], "rep": "Le décalage optique dû au trajet et à l'indice du verre à l'intérieur du prisme"},
            {"id": "qgeo0_5", "q": "Dans la simulation de levé topographique, jusqu'à quel angle de désorientation de la canne le prisme renvoie-t-il un signal exploitable ?", "options": ["Jusqu'à ± 25°", "Uniquement à 0,0° exact", "Jusqu'à 85°"], "rep": "Jusqu'à ± 25°"},
            {"id": "qgeo0_6", "q": "Quelle grandeur physique mesure le distancemètre (IMEL) intégré à la station totale ?", "options": ["Le déphasage ou le temps d'aller-retour de l'onde lumineuse réfléchie", "La pression atmosphérique sur le prisme", "La résistance électrique du sol"], "rep": "Le déphasage ou le temps d'aller-retour de l'onde lumineuse réfléchie"},
            {"id": "qgeo0_7", "q": "Quelle erreur de mesure commet le géomètre si la bulle sphérique de la canne à prisme n'est pas centrée (canne penchée) ?", "options": ["Les coordonnées (X, Y) du point levé au sol sont faussées", "La couleur du laser change", "La batterie de la station se vide"], "rep": "Les coordonnées (X, Y) du point levé au sol sont faussées"},
            {"id": "qgeo0_8", "q": "Combien de réflexions totales internes subit le faisceau lumineux dans un prisme topographique avant de ressortir ?", "options": ["Trois réflexions successives", "Une seule réflexion", "Six réflexions"], "rep": "Trois réflexions successives"},
            {"id": "qgeo0_9", "q": "Pourquoi préfère-t-on le mode « avec prisme » au mode « sans prisme » pour borner une limite de propriété officielle ?", "options": ["Le prisme offre une portée de plusieurs kilomètres et une précision millimétrique garantie", "Le mode sans prisme est interdit par la loi", "Le prisme fonctionne sans trépied"], "rep": "Le prisme offre une portée de plusieurs kilomètres et une précision millimétrique garantie"},
            {"id": "qgeo0_10", "q": "Quelle loi optique fondamentale s'applique sur chacune des trois faces internes du prisme ?", "options": ["La loi de la réflexion (i = i')", "La loi de Coulomb", "L'effet Venturi"], "rep": "La loi de la réflexion (i = i')"},
        ],
        "trous": [
            ("1. La station totale vise un ......... monté sur une canne verticale.", ["Choisir...", "prisme", "aimant"], "prisme", "geo_t1_final"),
            ("2. Le réflecteur topographique a la géométrie d'un coin de .........", ["Choisir...", "cube", "cylindre"], "cube", "geo_t2_final"),
            ("3. Le faisceau réfléchi repart ......... au faisceau émis par la station.", ["Choisir...", "parallèlement", "perpendiculairement"], "parallèlement", "geo_t3_final"),
            ("4. Le faisceau subit ......... réflexions successives dans le verre.", ["Choisir...", "trois", "deux"], "trois", "geo_t4_final"),
            ("5. Le paramètre de correction propre à chaque modèle est la ......... de prisme.", ["Choisir...", "constante", "vitesse"], "constante", "geo_t5_final"),
            ("6. L'opérateur maintient la canne verticale grâce à une nivelle .........", ["Choisir...", "sphérique", "thermique"], "sphérique", "geo_t6_final"),
            ("7. La précision d'un levé au prisme est de l'ordre du .........", ["Choisir...", "millimètre", "décimètre"], "millimètre", "geo_t7_final"),
            ("8. Le prisme tolère un désaxage angulaire jusqu'à ± ......... degrés.", ["Choisir...", "25", "2"], "25", "geo_t8_final"),
            ("9. Chaque face réfléchissante respecte l'égalité i = .........", ["Choisir...", "i'", "90°"], "i'", "geo_t9_final"),
            ("10. Le distancemètre calcule la distance à partir du trajet .........-retour.", ["Choisir...", "aller", "simple"], "aller", "geo_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 1 : ÉQUERRE OPTIQUE À DOUBLE PRISME PENTAGONAL (90°)
    # =========================================================================
    1: {
        "questions": [
            {"id": "qgeo1_1", "q": "À quoi sert une équerre optique sur le terrain pour un géomètre topographe ?", "options": ["À implanter rapidement des angles droits (90°) et à s'aligner entre deux jalons", "À mesurer la température de l'asphalte", "À niveler une dalle en béton à 500 mètres"], "rep": "À implanter rapidement des angles droits (90°) et à s'aligner entre deux jalons"},
            {"id": "qgeo1_2", "q": "De quel angle précis un prisme pentagonal (pentaprisme) dévie-t-il les rayons lumineux ?", "options": ["90° (un angle droit exact)", "45°", "180°"], "rep": "90° (un angle droit exact)"},
            {"id": "qgeo1_3", "q": "Combien de prismes pentagonaux superposés contient une équerre optique double ?", "options": ["Deux prismes (un déviant à 90° vers la gauche, l'autre à 90° vers la droite)", "Un seul prisme triangulaire", "Quatre lentilles divergentes"], "rep": "Deux prismes (un déviant à 90° vers la gauche, l'autre à 90° vers la droite)"},
            {"id": "qgeo1_4", "q": "Comment le géomètre sait-il qu'il se trouve exactement au pied de la perpendiculaire (angle à 90°) dans l'équerre optique ?", "options": ["Les images des deux jalons observés dans les prismes et le jalon vu directement sont parfaitement alignés verticalement", "Un bip sonore retentit dans le manche", "Les jalons deviennent verts"], "rep": "Les images des deux jalons observés dans les prismes et le jalon vu directement sont parfaitement alignés verticalement"},
            {"id": "qgeo1_5", "q": "Pourquoi l'équerre optique reste-t-elle précise même si le géomètre la tient à la main avec de légers mouvements de rotation ?", "options": ["Le pentaprisme dévie toujours le faisceau de 90° quelle que soit sa légère rotation autour de l'axe vertical", "L'équerre est aimantée au champ terrestre", "Le verre corrige automatiquement les tremblements"], "rep": "Le pentaprisme dévie toujours le faisceau de 90° quelle que soit sa légère rotation autour de l'axe vertical"},
            {"id": "qgeo1_6", "q": "Combien de réflexions internes subit un rayon lumineux à l'intérieur d'un pentaprisme pour sortir dévié de 90° ?", "options": ["Deux réflexions sur deux faces inclinées à 45° l'une par rapport à l'autre", "Une seule réflexion", "Quatre réflexions"], "rep": "Deux réflexions sur deux faces inclinées à 45° l'une par rapport à l'autre"},
            {"id": "qgeo1_7", "q": "Quel accessoire suspendu sous le manche de l'équerre optique permet de reporter précisément le point trouvé au sol ?", "options": ["Un fil à plomb (ou une canne à plomber)", "Un thermomètre à mercure", "Une boussole magnétique"], "rep": "Un fil à plomb (ou une canne à plomber)"},
            {"id": "qgeo1_8", "q": "Dans la simulation de l'équerre optique, si le géomètre est décalé de +1,50 m par rapport à l'alignement, que voit-il dans l'oculaire ?", "options": ["Les traits verticaux des trois jalons sont décalés les uns par rapport aux autres", "Il ne voit plus rien du tout", "L'angle passe à 180°"], "rep": "Les traits verticaux des trois jalons sont décalés les uns par rapport aux autres"},
            {"id": "qgeo1_9", "q": "Quel angle forment entre elles les deux faces réfléchissantes argentées d'un pentaprisme ?", "options": ["45° (ce qui produit une déviation totale de 2 × 45° = 90°)", "90°", "120°"], "rep": "45° (ce qui produit une déviation totale de 2 × 45° = 90°)"},
            {"id": "qgeo1_10", "q": "Pourquoi l'équerre optique est-elle toujours utilisée en topographie malgré l'arrivée des stations totales ?", "options": ["Elle ne nécessite aucune pile, est instantanée pour lever des détails proches et tient dans la poche", "Elle a une portée de 50 kilomètres", "Elle imprime directement les plans cadastraux"], "rep": "Elle ne nécessite aucune pile, est instantanée pour lever des détails proches et tient dans la poche"},
        ],
        "trous": [
            ("1. L'équerre optique permet d'implanter des angles droits de ......... degrés.", ["Choisir...", "90", "45"], "90", "geo_t1_final"),
            ("2. Elle utilise deux ......... pentagonaux superposés.", ["Choisir...", "prismes", "miroirs"], "prismes", "geo_t2_final"),
            ("3. Dans un pentaprisme, le rayon lumineux subit ......... réflexions internes.", ["Choisir...", "deux", "trois"], "deux", "geo_t3_final"),
            ("4. Les deux faces réfléchissantes du prisme forment un angle de .........°.", ["Choisir...", "45", "90"], "45", "geo_t4_final"),
            ("5. Le géomètre vise des ......... plantés verticalement sur le terrain.", ["Choisir...", "jalons", "piquets"], "jalons", "geo_t5_final"),
            ("6. Lorsque l'angle droit est atteint, les images des jalons sont .........", ["Choisir...", "alignées", "inversées"], "alignées", "geo_t6_final"),
            ("7. Un fil à ......... permet de marquer le point exact sur le sol.", ["Choisir...", "plomb", "fer"], "plomb", "geo_t7_final"),
            ("8. Une légère rotation de l'équerre en main ne modifie pas la ......... de 90°.", ["Choisir...", "déviation", "couleur"], "déviation", "geo_t8_final"),
            ("9. Chaque réflexion interne obéit à la loi i = .........", ["Choisir...", "i'", "0°"], "i'", "geo_t9_final"),
            ("10. Cet instrument optique fonctionne sans aucune ......... électrique.", ["Choisir...", "batterie", "lentille"], "batterie", "geo_t10_final"),
        ]
    },
    # =========================================================================
    # BANQUE SUJET 2 : SCANNER LASER TERRESTRE 3D (LIDAR À MIROIR TOURNANT)
    # =========================================================================
    2: {
        "questions": [
            {"id": "qgeo2_1", "q": "Quel composant optique tourne à très haute vitesse au centre d'un scanner laser terrestre 3D (LiDAR) ?", "options": ["Un miroir plan incliné (ou polygonal) qui dévie le faisceau laser verticalement", "Une loupe en verre dépoli", "Un disque vinyle noir"], "rep": "Un miroir plan incliné (ou polygonal) qui dévie le faisceau laser verticalement"},
            {"id": "qgeo2_2", "q": "Comment le scanner laser 3D parvient-il à numériser toute une pièce ou une façade entière à 360° ?", "options": ["En combinant la rotation rapide du miroir vertical et la rotation horizontale de la tête du scanner", "En déplaçant le trépied tous les centimètres", "En utilisant mille lasers fixes différents"], "rep": "En combinant la rotation rapide du miroir vertical et la rotation horizontale de la tête du scanner"},
            {"id": "qgeo2_3", "q": "Combien de points 3D par seconde un scanner laser topographique moderne peut-il mesurer par réflexion ?", "options": ["Jusqu'à 1 000 000 à 2 000 000 de points par seconde", "10 points par minute", "50 points par heure"], "rep": "Jusqu'à 1 000 000 à 2 000 000 de points par seconde"},
            {"id": "qgeo2_4", "q": "Si le miroir interne du scanner tourne d'un angle α, de combien tourne le faisceau laser projeté sur la façade ?", "options": ["2 × α (le double de l'angle de rotation du miroir)", "α (le même angle)", "α / 2"], "rep": "2 × α (le double de l'angle de rotation du miroir)"},
            {"id": "qgeo2_5", "q": "Comment s'appelle le fichier numérique 3D obtenu après le balayage laser complet d'un bâtiment ?", "options": ["Un nuage de points (Point Cloud)", "Un tableau Excel", "Une photographie argentique"], "rep": "Un nuage de points (Point Cloud)"},
            {"id": "qgeo2_6", "q": "Pourquoi les façades vitrées (miroirs, baies vitrées) posent-elles un problème lors d'un relevé au scanner laser 3D ?", "options": ["Le laser se réfléchit spéculairement sur la vitre et crée des points « fantômes » derrière le mur", "La vitre fait exploser le miroir du scanner", "Le laser devient invisible pour l'ordinateur"], "rep": "Le laser se réfléchit spéculairement sur la vitre et crée des points « fantômes » derrière le mur"},
            {"id": "qgeo2_7", "q": "Que placent les géomètres sur le chantier pour assembler précisément plusieurs stations de scan 3D entre elles ?", "options": ["Des sphères blanches mates ou des cibles damiers à haute réflectivité", "Des drapeaux rouges en tissu", "Des cônes de chantier orange"], "rep": "Des sphères blanches mates ou des cibles damiers à haute réflectivité"},
            {"id": "qgeo2_8", "q": "Quel type de réflexion sur un mur en pierre permet au scanner 3D de recevoir une partie du faisceau retour ?", "options": ["La réflexion diffuse sur la rugosité de la pierre", "La réflexion totale dans le verre", "La réfraction atmosphérique"], "rep": "La réflexion diffuse sur la rugosité de la pierre"},
            {"id": "qgeo2_9", "q": "Dans la simulation du scanner 3D, comment évolue la densité des points sur la façade lorsque la distance d'éloignement augmente ?", "options": ["L'espacement entre les points augmente (la densité diminue avec la distance)", "Les points deviennent plus serrés", "La densité reste strictement identique à 1 m et à 200 m"], "rep": "L'espacement entre les points augmente (la densité diminue avec la distance)"},
            {"id": "qgeo2_10", "q": "Quelle loi physique gouverne à la fois la déviation sur le miroir tournant interne et le rebond sur les sphères de calage ?", "options": ["La loi de la réflexion (i = i')", "La loi d'Archimède", "La loi de Boyle-Mariotte"], "rep": "La loi de la réflexion (i = i')"},
        ],
        "trous": [
            ("1. Au cœur du scanner 3D, un ......... tournant dévie le faisceau laser.", ["Choisir...", "miroir", "prisme"], "miroir", "geo_t1_final"),
            ("2. Lorsque le miroir tourne d'un angle alpha, le laser balaie un angle de ......... alpha.", ["Choisir...", "2", "0.5"], "2", "geo_t2_final"),
            ("3. L'ensemble des mesures forme un ......... de points en trois dimensions.", ["Choisir...", "nuage", "cercle"], "nuage", "geo_t3_final"),
            ("4. Le scanner mesure la distance grâce au temps d'.........-retour du laser.", ["Choisir...", "aller", "arrêt"], "aller", "geo_t4_final"),
            ("5. Sur un mur rugueux, la lumière revient par réflexion .........", ["Choisir...", "diffuse", "totale"], "diffuse", "geo_t5_final"),
            ("6. Les baies vitrées créent des points ......... par réflexion spéculaire.", ["Choisir...", "fantômes", "fixes"], "fantômes", "geo_t6_final"),
            ("7. On utilise des ......... blanches pour assembler plusieurs scans 3D.", ["Choisir...", "sphères", "briques"], "sphères", "geo_t7_final"),
            ("8. La tête du scanner pivote à ......... degrés autour de l'axe vertical.", ["Choisir...", "360", "90"], "360", "geo_t8_final"),
            ("9. Plus la façade est éloignée, plus l'......... entre deux points augmente.", ["Choisir...", "espacement", "intensité"], "espacement", "geo_t9_final"),
            ("10. Le miroir interne applique la loi fondamentale i = .........", ["Choisir...", "i'", "45°"], "i'", "geo_t10_final"),
        ]
    }
}


def mettre_a_jour_geometre_matplotlib(sujet_idx):
    """Banc d'essai topographique réaliste adapté à la mission tirée au sort."""
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, 600)
    ax.set_ylim(0, 260)
    ax.invert_yaxis()
    ax.axis("off")

    # =========================================================================
    # SUJET 0 : STATION TOTALE & PRISME RÉFLECTEUR EN COIN DE CUBE
    # =========================================================================
    if sujet_idx == 0:
        dist_m = st.session_state.get("slider_geo_dist_s0", 120.0)
        ang_prisme = st.session_state.get("slider_geo_ang_s0", 10.0)

        ax.add_patch(patches.Rectangle((20, 205), 560, 40, facecolor="#365314", edgecolor="#4d7c0f"))

        ax.plot(list((65, 80)), list((205, 145)), color="#cbd5e1", lw=2.5)
        ax.plot(list((95, 80)), list((205, 145)), color="#cbd5e1", lw=2.5)
        ax.add_patch(patches.Rectangle((66, 112), 28, 33, facecolor="#eab308", edgecolor="white", lw=1.5))
        ax.text(80, 102, "Station Totale\n(IMEL Infrarouge)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        xp = 180.0 + (dist_m / 300.0) * 360.0
        ax.plot(list((xp, xp)), list((205, 125)), color="#ef4444", lw=3)
        rad_p = math.radians(ang_prisme)
        dx_p = 14.0 * math.sin(rad_p)
        dy_p = 18.0 * math.cos(rad_p)
        ax.plot(list((xp - dx_p, xp + dx_p)), list((125 - dy_p, 125 + dy_p)), color="#38bdf8", lw=5)
        ax.text(xp, 96, f"Prisme ({ang_prisme:+.0f}°)\nà {dist_m:.0f} m", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        precision_mm = 1.0 + (dist_m * 0.0015)
        ax.annotate("", xy=(xp, 122), xytext=(94, 122), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))

        if abs(ang_prisme) <= 25.0:
            ax.annotate("", xy=(94, 132), xytext=(xp, 132), arrowprops=dict(arrowstyle="->", color="#22c55e", lw=2))
            statut = f"VISÉE VALIDÉE : D = {dist_m:.2f} m | Précision : ± {precision_mm:.2f} mm (Rétroréflexion OK)"
            c_stat = "#22c55e"
            diag = "LEVÉ OK"
        else:
            ax.annotate("", xy=(xp - 90, 190), xytext=(xp, 132), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.5, ls="--"))
            statut = f"PERTE DE SIGNAL : Prisme trop tourné ({ang_prisme:+.0f}° > ±25°), le rayon sort du coin de cube !"
            c_stat = "#ef4444"
            diag = "HORS CHAMP"

        ax.text(25, 20, "TOPOGRAPHIE : STATION TOTALE & PRISME RÉFLECTEUR (COIN DE CUBE)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 242, f"Distance : {dist_m:.1f} m | Orientation prisme : {ang_prisme:+.0f}° | Précision : ± {precision_mm:.2f} mm",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.geo_mesure_courante = (f"D = {dist_m:.1f} m", f"Prisme = {ang_prisme:+.0f}°", f"± {precision_mm:.2f} mm", diag)

    # =========================================================================
    # SUJET 1 : ÉQUERRE OPTIQUE À DOUBLE PRISME PENTAGONAL (90°)
    # =========================================================================
    elif sujet_idx == 1:
        ecart_align_m = st.session_state.get("slider_geo_s1", 0.40)

        ax.scatter(70, 175, color="#ef4444", s=80, zorder=4)
        ax.text(70, 194, "Jalon A (Gauche)", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        ax.scatter(530, 175, color="#ef4444", s=80, zorder=4)
        ax.text(530, 194, "Jalon B (Droite)", color="#fca5a5", fontsize=7.5, fontweight="bold", ha="center")

        ax.scatter(300, 55, color="#38bdf8", s=80, zorder=4)
        ax.text(300, 44, "Jalon C (Perpendiculaire 90°)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        ax.plot(list((70, 530)), list((175, 175)), color="#64748b", lw=1.5, ls="--")

        x_geo = 300.0 + ecart_align_m * 70.0
        y_geo = 175.0
        ax.add_patch(patches.Rectangle((x_geo - 12, y_geo - 12), 24, 24, facecolor="#eab308", edgecolor="white", lw=1.5, zorder=5))
        ax.text(x_geo, y_geo + 24, f"Géomètre (Écart : {ecart_align_m:+.2f} m)", color="#fde047", fontsize=7.5, fontweight="bold", ha="center")

        ax.annotate("", xy=(x_geo - 4, y_geo), xytext=(70, 175), arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2))
        ax.annotate("", xy=(x_geo + 4, y_geo), xytext=(530, 175), arrowprops=dict(arrowstyle="->", color="#f59e0b", lw=2))
        ax.plot(list((300, x_geo)), list((55, y_geo)), color="#38bdf8", lw=1.5, ls=":")

        if abs(ecart_align_m) <= 0.05:
            statut = "ANGLE DROIT (90,0°) IMPLANTÉ : Les 3 jalons A, B et C sont superposés dans l'oculaire !"
            c_stat = "#22c55e"
            diag = "90° EXACT (OK)"
        else:
            statut = f"DÉCALAGE DE {ecart_align_m:+.2f} m : Les images des jalons sont décalées, déplacez-vous sur la base AB."
            c_stat = "#ef4444"
            diag = "NON ALIGNÉ"

        ax.text(25, 20, "IMPLANTATION TERRAIN : ÉQUERRE OPTIQUE À DOUBLE PENTAPRISME (90°)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 242, f"Écart latéral sur base AB : {ecart_align_m:+.2f} m | Déviation interne pentaprisme : 90,0°",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.geo_mesure_courante = (f"Écart = {ecart_align_m:+.2f} m", "Déviation = 90°", "Pentaprisme", diag)

    # =========================================================================
    # SUJET 2 : SCANNER LASER TERRESTRE 3D (LIDAR À MIROIR TOURNANT)
    # =========================================================================
    else:
        dist_facade = st.session_state.get("slider_geo_s2", 25.0)
        freq_miroir = st.session_state.get("slider_geo_freq_s2", 50.0)

        ax.plot(list((65, 80)), list((205, 145)), color="#cbd5e1", lw=2.5)
        ax.plot(list((95, 80)), list((205, 145)), color="#cbd5e1", lw=2.5)
        ax.add_patch(patches.Rectangle((65, 110), 30, 35, facecolor="#0284c7", edgecolor="white", lw=1.5))
        ax.text(80, 98, f"Scanner 3D\n({freq_miroir:.0f} Hz)", color="#38bdf8", fontsize=7.5, fontweight="bold", ha="center")

        xf = 180.0 + (dist_facade / 80.0) * 350.0
        ax.add_patch(patches.Rectangle((xf, 55), 24, 150, facecolor="#475569", edgecolor="#94a3b8", lw=2))
        ax.text(xf + 12, 46, f"Façade ({dist_facade:.0f} m)", color="#cbd5e1", fontsize=7.5, fontweight="bold", ha="center")

        nb_rayons = int(min(18, max(5, freq_miroir / 5)))
        espacement_mm = (dist_facade * 1000.0) / (freq_miroir * 20.0)
        for k in range(nb_rayons):
            y_cible = 62.0 + k * (136.0 / max(1, nb_rayons - 1))
            ax.plot(list((95, xf)), list((127, y_cible)), color="#22c55e", lw=0.9, alpha=0.6)
            ax.scatter(xf, y_cible, color="#ef4444", s=18, zorder=5)

        if espacement_mm <= 15.0:
            statut = f"NUAGE DE POINTS HAUTE DENSITÉ : Espacement = {espacement_mm:.1f} mm (Relevé architectural conforme)."
            c_stat = "#22c55e"
            diag = "HAUTE DENSITÉ"
        else:
            statut = f"DENSITÉ FAIBLE ({espacement_mm:.1f} mm) : Rapprochez le scanner ou augmentez la vitesse du miroir."
            c_stat = "#f59e0b"
            diag = "DENSITÉ FAIBLE"

        ax.text(25, 20, "NUMÉRISATION 3D : SCANNER LASER TERRESTRE (MIROIR TOURNANT)", color="#38bdf8", fontsize=9, fontweight="bold")
        ax.text(25, 36, statut, color=c_stat, fontsize=8, fontweight="bold")
        ax.text(300, 242, f"Distance façade : {dist_facade:.0f} m | Vitesse miroir : {freq_miroir:.0f} tr/s | Pas des points : {espacement_mm:.1f} mm",
                color="#f8fafc", fontsize=8, fontweight="bold", ha="center", bbox=dict(boxstyle="round", facecolor="#1e293b", edgecolor=c_stat))

        st.session_state.geo_mesure_courante = (f"D = {dist_facade:.0f} m", f"Miroir = {freq_miroir:.0f} Hz", f"Pas = {espacement_mm:.1f} mm", diag)

    return fig


def afficher_atelier_geometre_complet(sujet_idx, verrouille=False):
    """Affiche les 10 QCM et les 10 trous spécifiques à la mission Géomètre tirée au sort."""
    if sujet_idx is None:
        st.warning("Tirez d'abord au sort une mission de Géomètre Topographe ci-dessus pour débloquer les 10 questions et les 10 phrases à trous correspondantes.")
        return

    banque = BANQUES_GEOMETRE[sujet_idx]
    cle_session_ordre = f"ordre_quiz_geo_sujet_{sujet_idx}"

    if cle_session_ordre not in st.session_state:
        liste_q = list(banque["questions"])
        random.shuffle(liste_q)
        st.session_state[cle_session_ordre] = liste_q

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique Géomètre Topographe (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state[cle_session_ordre], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"geo_at9_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Géomètre Topographe (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in banque["trous"]:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox("", choix, key=f"{cle}_s{sujet_idx}", disabled=verrouille, label_visibility="collapsed")



                
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
    st.header("Atelier 1 : Histoire des lois de la réflexion et des miroirs")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Objectif de l'atelier :</p>
        <p style="color: #334155; margin-bottom: 0;">Découvrir les savants qui ont établi les lois de la réflexion, leurs découvertes majeures, ainsi qu'une approche illustrée en bande dessinée.</p>
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # 1. LES SAVANTS ET LEURS DÉCOUVERTES (4 COLONNES : IMAGE + DESCRIPTIF)
    # =========================================================================
    st.subheader("1. Les grands savants et leurs découvertes sur la réflexion")

    col1, col2, col3, col4 = st.columns(4)

    # --- SAVANT 1 : EUCLIDE ---
    with col1:
        try:
            st.image("euclide.jpg", caption="Euclide (IIIe siècle av. J.-C.)", use_container_width=True)
        except Exception:
            st.warning("L'image 'euclide.jpg' est introuvable.")
        st.info("""
        **Euclide et *La Catoptrique* (vers 300 av. J.-C.)**
        * **Le savant :** Mathématicien de la Grèce antique vivant à Alexandrie.
        * **Sa découverte :** Il publie *La Catoptrique*, le premier traité consacré aux miroirs. Il y démontre géométriquement que la lumière se propage en ligne droite et que **l'angle de réflexion est toujours égal à l'angle d'incidence**.
        """)

    # --- SAVANT 2 : IBN AL-HAYTHAM (ALHAZEN) ---
    with col2:
        try:
            st.image("alhazen.jpg", caption="Ibn al-Haytham / Alhazen (965 - 1040)", use_container_width=True)
        except Exception:
            st.warning("L'image 'alhazen.jpg' est introuvable.")
        st.info("""
        **Ibn al-Haytham, dit Alhazen (*Traité d'optique*, 1021)**
        * **Le savant :** Physicien, mathématicien et astronome majeur de l'âge d'or islamique.
        * **Sa découverte :** Il prouve par l'expérience que la lumière provient des sources lumineuses, rebondit sur les objets et entre dans l'œil (et non l'inverse). Il établit aussi que le rayon incident, la normale et le rayon réfléchi sont dans **un même plan**.
        """)

    # --- SAVANT 3 : RENÉ DESCARTES ---
    with col3:
        try:
            st.image("descartes.jpg", caption="René Descartes (1596 - 1650)", use_container_width=True)
        except Exception:
            st.warning("L'image 'descartes.jpg' est introuvable.")
        st.info("""
        **René Descartes (*La Dioptrique*, 1637)**
        * **Le savant :** Mathématicien, physicien et philosophe français.
        * **Sa découverte :** Il formalise les lois universelles de la réflexion et de la réfraction (lois de Snell-Descartes). Il fixe le vocabulaire technique moderne (**normale, rayon incident, rayon réfléchi**) et la formule **$i = i'$**.
        """)

    # --- SAVANT 4 : JOHN HENRY PEPPER ---
    with col4:
        try:
            st.image("pepper.jpg", caption="John Henry Pepper (1821 - 1900)", use_container_width=True)
        except Exception:
            st.warning("L'image 'pepper.jpg' est introuvable.")
        st.info("""
        **John Henry Pepper et l'illusion du Spectre (1862)**
        * **Le savant :** Chimiste et inventeur britannique au Royal Polytechnic Institution de Londres.
        * **Sa découverte :** Il utilise une grande vitre sans tain inclinée à **45°** pour réfléchir l'image d'un acteur caché sous la scène. Cette découverte est l'ancêtre direct des **affichages tête haute (HUD)** des avions et des voitures.
        """)

    # =========================================================================
    # 2. LA RÉFLEXION EN BANDE DESSINÉE ET EN HUMOUR (.JPG)
    # =========================================================================
    st.markdown("---")
    st.subheader("2. La loi de la réflexion illustrée : Bande dessinée & Humour")
    st.write("Retrouvez ci-dessous la bande dessinée pédagogique ainsi que la vignette humoristique sur la réflexion :")

    try:
        st.image("humour_reflexion.jpg", caption="La pause humoristique : Réflexion physique vs philosophique", use_container_width=True)
    except Exception:
        st.warning("L'image 'humour_reflexion.jpg' est introuvable.")


    if "hist_verrouille_tab1" not in st.session_state:
        st.session_state.hist_verrouille_tab1 = False
    verrou_at1 = st.session_state.hist_verrouille_tab1

    afficher_atelier_historique_complet(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1 (Historique)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_hist1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique de l'Optique.",
        key="check_certif_historique_final_net",
        disabled=verrou_at1,
    )

    # --- 4. BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_hist1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_hist1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_hist_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_hist_aleatoire:
                    reponse_eleve = st.session_state.get(f"hist_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = sum(
                [
                    st.session_state.get("hist_t1_final") == "bronze",
                    st.session_state.get("hist_t2_final") == "Catoptrique",
                    st.session_state.get("hist_t3_final") == "droite",
                    st.session_state.get("hist_t4_final") == "oeil",
                    st.session_state.get("hist_t5_final") == "plan",
                    st.session_state.get("hist_t6_final") == "Dioptrique",
                    st.session_state.get("hist_t7_final") == "normale",
                    st.session_state.get("hist_t8_final") == "i'",
                    st.session_state.get("hist_t9_final") == "45",
                    st.session_state.get("hist_t10_final") == "virtuelle",
                ]
            )

            st.session_state.score_hist1_p1 = round(float(score_q1), 1)
            st.session_state.score_hist1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_hist1 = round(float(score_q1 + score_t1), 1)
            st.session_state.hist_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 1 (COMPLET : QUIZ + TEXTE À TROUS) ---
    if st.session_state.get("hist_verrouille_tab1", False):
        scr1 = st.session_state.get("score_hist1_p1", 0.0)
        scr2 = st.session_state.get("score_hist1_p2", 0.0)
        tot_s = st.session_state.get("score_final_hist1", 0.0)

        timestamp_hist1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_hist = f"""<!DOCTYPE html>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 1 : Histoire des lois de la réflexion et des miroirs</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_hist1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Historique : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_hist_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_hist_aleatoire, 1):
                saisie = st.session_state.get(f"hist_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hist += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_hist += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        liste_verification_trous = [
            ("1. Dans l'Antiquité, les miroirs étaient fabriqués en ......... poli.", "bronze", "hist_t1_final"),
            ("2. Le premier traité grec sur les miroirs s'intitule La .........", "Catoptrique", "hist_t2_final"),
            ("3. Selon Euclide, la lumière se propage en ligne .........", "droite", "hist_t3_final"),
            ("4. Alhazen prouve que les rayons lumineux entrent dans l'.........", "oeil", "hist_t4_final"),
            ("5. Le rayon incident et le rayon réfléchi sont dans un même .........", "plan", "hist_t5_final"),
            ("6. René Descartes publie La ......... en 1637.", "Dioptrique", "hist_t6_final"),
            ("7. Les angles se mesurent toujours par rapport à la .........", "normale", "hist_t7_final"),
            ("8. La loi de la réflexion impose l'égalité stricte : i = .........", "i'", "hist_t8_final"),
            ("9. Le Spectre de Pepper utilise une vitre inclinée à ......... degrés.", "45", "hist_t9_final"),
            ("10. Le HUD automobile projette une image ......... devant le conducteur.", "virtuelle", "hist_t10_final"),
        ]

        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(liste_verification_trous, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_hist += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_hist += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html = preparer_nom_fichier("Rapport_Atelier_1_Historique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_hist,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )



with tab2:
    st.header("Atelier 2 : Lois de la Reflexion ")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Rappel de la Première Loi de Snell-Descartes pour la Réflexion :</p>
        <ul style="margin-bottom: 0; line-height: 1.6;">
            <li><strong>Loi fondamentale :</strong> <b><i>i</i> = <i>i'</i></b> (L'angle de réflexion <i>i'</i> est rigoureusement égal à l'angle d'incidence <i>i</i>).</li>
            <li><strong>Mesure des angles :</strong> Les deux angles sont mesurés par rapport à la <strong>normale</strong> (la droite perpendiculaire à la surface du miroir au point d'impact).</li>
            <li><strong>Application du Spectre de Pepper :</strong> Permet de créer une image virtuelle superposée à un objet réel par une inclinaison précise à <strong>45,0°</strong>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if "opt3_verrouille" not in st.session_state: st.session_state.opt3_verrouille = False

    # Initialisation permanente du tableau de mesures pour l'exercice de l'eleve
    if "mesures_reflexion_i" not in st.session_state: st.session_state.mesures_reflexion_i = []
    if "mesures_reflexion_iprime" not in st.session_state: st.session_state.mesures_reflexion_iprime = []

    st.subheader("Laboratoire Virtuel de Reflexion")
        
    # Le curseur d'angle d'incidence exclusif
    st.slider("Angle d'incidence i (degrés) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ref_i")
    
    # Bouton d'action connecte au systeme de memorisation
    if st.button("PRENDRE UNE MESURE (MIROIR)", key="btn_ajouter_mesure_ref", use_container_width=True):
        ajouter_mesure_reflexion_pure_streamlit()
        st.rerun()
    
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    # Affichage synchrone du rayon laser et du miroir horizontal
    fig_miroir_laser = mettre_a_jour_reflexion_pure_matplotlib()
    st.pyplot(fig_miroir_laser, use_container_width=True)

    # Boîte de resultats technique locale sous le graphique
    st.info(st.session_state.get("opt3_txt_box_ref", "Ajustez le curseur pour initialiser."))

    # Affichage de l'historique des mesures (Treeview) sous forme de tableau Pandas propre
    import pandas as pd
    st.markdown("##### Historique des points de mesures enregistres")
    if st.session_state.get("mesures_reflexion_i"):
        df_mesures = pd.DataFrame({
            "N° Essai": [f"Essai {idx}" for idx in range(1, len(st.session_state.mesures_reflexion_i) + 1)],
            "Incidence i (°)": [f"{val:.1f}°" for val in st.session_state.mesures_reflexion_i],
            "Réflexion i' (°)": [f"{val:.1f}°" for val in st.session_state.mesures_reflexion_iprime],
            "Loi : i = i' ?": ["Oui (100%)" for _ in st.session_state.mesures_reflexion_i]
        })
        st.dataframe(df_mesures, use_container_width=True, hide_index=True)
    else:
        st.caption("Tableau vide. Cliquez sur le bouton bleu ci-dessus pour memoriser l'angle courant.")
    # =========================================================================
    # 2. ÉVALUATION (10 QUESTIONS + 10 TROUS) ET EXPORT HTML COMPLET
    # =========================================================================
    st.write("---")
    st.subheader("2. Évaluation des connaissances (20 points)")

    if "ref_verrouille_tab2" not in st.session_state:
        st.session_state.ref_verrouille_tab2 = False
    verrou_at2 = st.session_state.ref_verrouille_tab2

    afficher_atelier_reflexion_complet(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2 (Réflexion)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ref2 = st.checkbox(
        "Je certifie avoir réalisé les mesures et complété les questions de l'Atelier Réflexion.",
        key="check_certif_reflexion_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_ref2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_ref2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_ref_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_ref_aleatoire:
                    reponse_eleve = st.session_state.get(f"ref_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = sum([
                st.session_state.get("ref_t1_final") == "incident",
                st.session_state.get("ref_t2_final") == "réfléchi",
                st.session_state.get("ref_t3_final") == "normale",
                st.session_state.get("ref_t4_final") == "normale",
                st.session_state.get("ref_t5_final") == "égal",
                st.session_state.get("ref_t6_final") == "plan",
                st.session_state.get("ref_t7_final") == "inverse",
                st.session_state.get("ref_t8_final") == "90",
                st.session_state.get("ref_t9_final") == "virtuelle",
                st.session_state.get("ref_t10_final") == "Descartes",
            ])

            st.session_state.score_ref2_p1 = round(float(score_q2), 1)
            st.session_state.score_ref2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_ref2 = round(float(score_q2 + score_t2), 1)
            st.session_state.ref_verrouille_tab2 = True
            st.rerun()

    if st.session_state.get("ref_verrouille_tab2", False):
        scr1 = st.session_state.get("score_ref2_p1", 0.0)
        scr2 = st.session_state.get("score_ref2_p2", 0.0)
        tot_s = st.session_state.get("score_final_ref2", 0.0)

        timestamp_ref2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER RÉFLEXION SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_ref = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Loi de la Réflexion - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 2 : Lois de la Réflexion (i = i')</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_ref2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Réflexion : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Nombre de mesures expérimentales relevées : <strong>{len(st.session_state.get("mesures_reflexion_i", []))}</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_ref_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_ref_aleatoire, 1):
                saisie = st.session_state.get(f"ref_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ref += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ref += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        liste_verif_trous_ref = [
            ("1. Le rayon qui arrive de la source laser s'appelle le rayon .........", "incident", "ref_t1_final"),
            ("2. Le rayon qui repart après avoir touché le miroir est le rayon .........", "réfléchi", "ref_t2_final"),
            ("3. La droite perpendiculaire au miroir au point d'impact est la .........", "normale", "ref_t3_final"),
            ("4. L'angle d'incidence i se mesure entre le rayon incident et la .........", "normale", "ref_t4_final"),
            ("5. L'angle de réflexion i' est toujours ......... à l'angle d'incidence i.", "égal", "ref_t5_final"),
            ("6. Le rayon incident et le rayon réfléchi sont situés dans un même .........", "plan", "ref_t6_final"),
            ("7. Si i = 0°, le rayon réfléchi repart sur lui-même en sens .........", "inverse", "ref_t7_final"),
            ("8. Pour un angle i = 45°, l'angle entre les deux rayons vaut ......... degrés.", "90", "ref_t8_final"),
            ("9. Un miroir plan donne d'un objet réel une image ......... symétrique.", "virtuelle", "ref_t9_final"),
            ("10. Les lois de la réflexion portent le nom de Snell et .........", "Descartes", "ref_t10_final"),
        ]

        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(liste_verif_trous_ref, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_ref += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_ref += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_ref = preparer_nom_fichier("Rapport_Atelier_2_Reflexion").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_ref,
            file_name=nom_fichier_html_ref,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("**Manipulation  : Illusion d'optique (Affichage Tete Haute - HUD)**")
            
    # Curseur interactif d'angle connecté au moteur physique
    st.slider("Angle d'inclinaison du pare-brise i (degrés) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ill")
    
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    # APPEL ET RENDU DE LA GRAPHISQUE VECTORIELLE DU PAR-BRISE HUD
    fig_hud_illusion = mettre_a_jour_illusion_matplotlib()
    st.pyplot(fig_hud_illusion, use_container_width=True)

    # Affichage de la boîte de résultats technique en couleur
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    st.info(st.session_state.get("opt3_txt_box_ill", "Ajustez le curseur pour initialiser la matrice."))
    
    angle_illusion = st.slider("Angle du miroir plan i (°) :", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="slider_angle_ill_quiz")
    st.write("---")
    st.subheader("2. Évaluation des connaissances (20 points)")

    if "pep_verrouille_tab3" not in st.session_state:
        st.session_state.pep_verrouille_tab3 = False
    verrou_at3 = st.session_state.pep_verrouille_tab3

    afficher_atelier_pepper_complet(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3 (Spectre de Pepper)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_pep3 = st.checkbox(
        "Je certifie avoir testé le simulateur HUD et complété les questions de l'Atelier 3.",
        key="check_certif_pepper_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_pep3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_pep3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_pep_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_pep_aleatoire:
                    reponse_eleve = st.session_state.get(f"pep_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            score_t3 = sum([
                st.session_state.get("pep_t1_final") == "45",
                st.session_state.get("pep_t2_final") == "virtuelle",
                st.session_state.get("pep_t3_final") == "Haute",
                st.session_state.get("pep_t4_final") == "miroir",
                st.session_state.get("pep_t5_final") == "i'",
                st.session_state.get("pep_t6_final") == "droite",
                st.session_state.get("pep_t7_final") == "fosse",
                st.session_state.get("pep_t8_final") == "yeux",
                st.session_state.get("pep_t9_final") == "45",
                st.session_state.get("pep_t10_final") == "route",
            ])

            st.session_state.score_pep3_p1 = round(float(score_q3), 1)
            st.session_state.score_pep3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_pep3 = round(float(score_q3 + score_t3), 1)
            st.session_state.pep_verrouille_tab3 = True
            st.rerun()

    if st.session_state.get("pep_verrouille_tab3", False):
        scr1 = st.session_state.get("score_pep3_p1", 0.0)
        scr2 = st.session_state.get("score_pep3_p2", 0.0)
        tot_s = st.session_state.get("score_final_pep3", 0.0)

        timestamp_pep3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER SPECTRE DE PEPPER SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_pep = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Spectre de Pepper - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 3 : Spectre de Pepper & Affichage Tête Haute (HUD)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_pep3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Spectre de Pepper : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_pep_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_pep_aleatoire, 1):
                saisie = st.session_state.get(f"pep_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_pep += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_pep += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """
        liste_verif_trous_pep = [
            ("1. L'illusion du Spectre de Pepper repose sur une vitre inclinée à ......... degrés.", "45", "pep_t1_final"),
            ("2. L'image observée au travers de la vitre est une image .........", "virtuelle", "pep_t2_final"),
            ("3. Le sigle HUD signifie Affichage Tête ......... en français.", "Haute", "pep_t3_final"),
            ("4. Le pare-brise agit à la fois comme une vitre transparente et un .........", "miroir", "pep_t4_final"),
            ("5. Le rayon issu du projecteur se réfléchit en respectant la loi i = .........", "i'", "pep_t5_final"),
            ("6. Le cerveau prolonge les rayons reçus en ligne ......... derrière le pare-brise.", "droite", "pep_t6_final"),
            ("7. Au théâtre, l'acteur fantôme était éclairé dans une ......... sous la scène.", "fosse", "pep_t7_final"),
            ("8. Le HUD évite au conducteur de baisser les ......... vers le compteur.", "yeux", "pep_t8_final"),
            ("9. Un rayon incident vertical dévié à 90° nécessite un angle d'incidence de .........°.", "45", "pep_t9_final"),
            ("10. L'image projetée sur le pare-brise se superpose directement à la .........", "route", "pep_t10_final"),
        ]

        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(liste_verif_trous_pep, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_pep += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_pep += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_pep = preparer_nom_fichier("Rapport_Atelier_3_Spectre_Pepper").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_pep,
            file_name=nom_fichier_html_pep,
            mime="text/html",
            use_container_width=True
        )

with tab4:
    st.header("**Manipulation : Conduite & Topographie (Simulation Retroviseurs)**")
            
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    st.markdown("##### Carte interactive du champ de vision arriere")
    
    # APPEL ET AFFICHAGE SYNCHRONE DE LA MAP DE LA ROUTE MATPLOTLIB
    fig_retro_route = mettre_a_jour_retroviseurs_matplotlib()
    st.pyplot(fig_retro_route, use_container_width=True)
    observateur = st.selectbox("Qui regarde dans les miroirs ?", ["Conducteur", "Passager Avant"], key="combo_obs_retro_final")
    retro_gauche = st.slider("Orientation Retroviseur Gauche (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_g_eval")
    retro_interne = st.slider("Orientation Retroviseur Interne Central (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_i_eval")
    retro_droit = st.slider("Orientation Retroviseur Droit (°)", min_value=-180.0, max_value=180.0, value=0.0, step=1.0, key="slide_retro_d_eval")
    
    st.slider("Position Avancement Siege Conducteur (cm)", min_value=-15.0, max_value=15.0, value=0.0, step=1.0, key="slide_siege_cond_eval")
    st.slider("Position Avancement Siege Passager (cm)", min_value=-15.0, max_value=15.0, value=0.0, step=1.0, key="slide_siege_pass_eval")
    st.caption(f"Position active calculee pour le profil : {observateur}")
    st.write("---")
    st.subheader("2. Évaluation des connaissances (20 points)")

    if "retro_verrouille_tab4" not in st.session_state:
        st.session_state.retro_verrouille_tab4 = False
    verrou_at4 = st.session_state.retro_verrouille_tab4

    afficher_atelier_retroviseurs_complet(verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4 (Rétroviseurs)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_retro4 = st.checkbox(
        "Je certifie avoir réglé les rétroviseurs sur le simulateur et complété les questions de l'Atelier 4.",
        key="check_certif_retro_final_net",
        disabled=verrou_at4,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_retro4_official_net", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_retro4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_retro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_retro_aleatoire:
                    reponse_eleve = st.session_state.get(f"retro_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            score_t4 = sum([
                st.session_state.get("retro_t1_final") == "lumière",
                st.session_state.get("retro_t2_final") == "morts",
                st.session_state.get("retro_t3_final") == "i'",
                st.session_state.get("retro_t4_final") == "trois",
                st.session_state.get("retro_t5_final") == "siège",
                st.session_state.get("retro_t6_final") == "arrière",
                st.session_state.get("retro_t7_final") == "élargir",
                st.session_state.get("retro_t8_final") == "direct",
                st.session_state.get("retro_t9_final") == "2",
                st.session_state.get("retro_t10_final") == "morts",
            ])

            st.session_state.score_retro4_p1 = round(float(score_q4), 1)
            st.session_state.score_retro4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_retro4 = round(float(score_q4 + score_t4), 1)
            st.session_state.retro_verrouille_tab4 = True
            st.rerun()

    if st.session_state.get("retro_verrouille_tab4", False):
        scr1 = st.session_state.get("score_retro4_p1", 0.0)
        scr2 = st.session_state.get("score_retro4_p2", 0.0)
        tot_s = st.session_state.get("score_final_retro4", 0.0)

        timestamp_retro4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER RÉTROVISEURS SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_retro = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Rétroviseurs - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 4 : Simulation des Rétroviseurs & Angles Morts</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_retro4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Rétroviseurs : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_retro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_retro_aleatoire, 1):
                saisie = st.session_state.get(f"retro_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_retro += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_retro += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        liste_verif_trous_retro = [
            ("1. Les rétroviseurs utilisent des miroirs pour renvoyer la ......... vers l'œil.", "lumière", "retro_t1_final"),
            ("2. Les zones invisibles autour d'un véhicule s'appellent les angles .........", "morts", "retro_t2_final"),
            ("3. Chaque rayon lumineux rebondit sur le miroir selon la loi i = .........", "i'", "retro_t3_final"),
            ("4. Un véhicule possède généralement ......... rétroviseurs (gauche, droit et central).", "trois", "retro_t4_final"),
            ("5. Si le conducteur règle son ........., il doit aussi réajuster ses miroirs.", "siège", "retro_t5_final"),
            ("6. Le rétroviseur central vise à travers la lunette ......... du véhicule.", "arrière", "retro_t6_final"),
            ("7. Un miroir légèrement convexe permet d'......... le champ de vision.", "élargir", "retro_t7_final"),
            ("8. Avant de dépasser, un contrôle ......... en tournant la tête est obligatoire.", "direct", "retro_t8_final"),
            ("9. Si un miroir pivote d'un angle alpha, le rayon réfléchi pivote de ......... alpha.", "2", "retro_t9_final"),
            ("10. Les poids lourds portent des autocollants signalant le danger des angles .........", "morts", "retro_t10_final"),
        ]

        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(liste_verif_trous_retro, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_retro += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_retro += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_retro = preparer_nom_fichier("Rapport_Atelier_4_Retroviseurs").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_retro,
            file_name=nom_fichier_html_retro,
            mime="text/html",
            use_container_width=True
        )


with tab5:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")
            
    # Curseur d'angle unique connecté au moteur du périscope Matplotlib
    st.slider(
        "Angle d'inclinaison des miroirs internes (degrés) :", 
        min_value=0.0, 
        max_value=90.0, 
        value=45.0, 
        step=1.0, 
        key="slider_angle_periscope"
    )
    
    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    # Rendu graphique dynamique de la canalisation du laser périscopique
    fig_periscope = mettre_a_jour_periscope_matplotlib()
    st.pyplot(fig_periscope, use_container_width=True)

    # Boîte de résultats technique locale
    st.info(st.session_state.get("opt3_txt_box_periscope", "Ajustez la reglette pour deplacer le laser."))

    st.write("---")
    st.subheader("2. Évaluation des connaissances (20 points)")

    if "peri_verrouille_tab5" not in st.session_state:
        st.session_state.peri_verrouille_tab5 = False
    verrou_at5 = st.session_state.peri_verrouille_tab5

    afficher_atelier_periscope_complet(verrouille=verrou_at5)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5 (Périscope)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_peri5 = st.checkbox(
        "Je certifie avoir testé le périscope sur le simulateur et complété les questions de l'Atelier 5.",
        key="check_certif_periscope_final_net",
        disabled=verrou_at5,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_peri5_official_net", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_peri5:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_peri_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_peri_aleatoire:
                    reponse_eleve = st.session_state.get(f"peri_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            score_t5 = sum([
                st.session_state.get("peri_t1_final") == "deux",
                st.session_state.get("peri_t2_final") == "45",
                st.session_state.get("peri_t3_final") == "bas",
                st.session_state.get("peri_t4_final") == "90",
                st.session_state.get("peri_t5_final") == "parallèle",
                st.session_state.get("peri_t6_final") == "double",
                st.session_state.get("peri_t7_final") == "réfléchi",
                st.session_state.get("peri_t8_final") == "endroit",
                st.session_state.get("peri_t9_final") == "paroi",
                st.session_state.get("peri_t10_final") == "obstacle",
            ])

            st.session_state.score_peri5_p1 = round(float(score_q5), 1)
            st.session_state.score_peri5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_peri5 = round(float(score_q5 + score_t5), 1)
            st.session_state.peri_verrouille_tab5 = True
            st.rerun()

    if st.session_state.get("peri_verrouille_tab5", False):
        scr1 = st.session_state.get("score_peri5_p1", 0.0)
        scr2 = st.session_state.get("score_peri5_p2", 0.0)
        tot_s = st.session_state.get("score_final_peri5", 0.0)

        timestamp_peri5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER PÉRISCOPE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_peri = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Périscope - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 5 : Le Périscope du sous-marin (Double réflexion)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_peri5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Périscope : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_peri_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_peri_aleatoire, 1):
                saisie = st.session_state.get(f"peri_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_peri += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_peri += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        liste_verif_trous_peri = [
            ("1. Un périscope simple utilise ......... miroirs plans parallèles.", "deux", "peri_t1_final"),
            ("2. Les deux miroirs sont inclinés à ......... degrés par rapport à l'horizontale.", "45", "peri_t2_final"),
            ("3. Le premier miroir dévie la lumière horizontalement vers le .........", "bas", "peri_t3_final"),
            ("4. Chaque miroir provoque une déviation du faisceau de ......... degrés.", "90", "peri_t4_final"),
            ("5. Le rayon sortant est ......... au rayon entrant dans le périscope.", "parallèle", "peri_t5_final"),
            ("6. Le dispositif repose sur une ......... réflexion successive.", "double", "peri_t6_final"),
            ("7. Sur chaque miroir, l'angle d'incidence i est égal à l'angle ......... i'.", "réfléchi", "peri_t7_final"),
            ("8. Grâce aux deux réflexions, l'image finale est vue à l'.........", "endroit", "peri_t8_final"),
            ("9. Si l'angle des miroirs est déréglé, le rayon heurte la ......... du tube.", "paroi", "peri_t9_final"),
            ("10. Le périscope permet d'observer au-dessus d'un ......... sans être vu.", "obstacle", "peri_t10_final"),
        ]

        for idx_t, (enonce_t, attendu_t, cle_t) in enumerate(liste_verif_trous_peri, 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_peri += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_peri += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_peri = preparer_nom_fichier("Rapport_Atelier_5_Periscope").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_peri,
            file_name=nom_fichier_html_peri,
            mime="text/html",
            use_container_width=True
        )

with tab6:
    st.header("Atelier 6 : Applications dans le domaine de la Maintenance Industrielle")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Rôle de la réflexion optique en maintenance préventive et corrective :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">En milieu industriel, les techniciens de maintenance utilisent quotidiennement la loi <b><i>i</i> = <i>i'</i></b> pour aligner des machines tournantes au centième de millimètre, inspecter des zones inaccessibles sans démontage ou sécuriser des lignes automatisées.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_maintenance = [
        {
            "titre": "Cas N°1 : Alignement laser d'arbres tournants (Moteur - Pompe)",
            "img_metier": "maint_laser_arbre.jpg",
            "legende_metier": "Système d'alignement laser monté sur accouplement moteur-pompe",
            "explication": (
                "**Principe technique :** Un émetteur laser fixé sur l'arbre moteur projette un faisceau sur un prisme/miroir réflecteur monté sur l'arbre de la pompe. "
                "D'après les lois de la réflexion, un défaut d'alignement angulaire **α** de l'arbre dévie le faisceau réfléchi d'un angle **2α**. "
                "À 3 000 tr/min, la tolérance maximale admise est de **0,05°** (soit un décalage inférieur à **0,44 mm** à 250 mm de distance)."
            )
        },
        {
            "titre": "Cas N°2 : Miroir d'inspection articulé (Contrôle de soudures et fuites)",
            "img_metier": "maint_miroir_inspection.jpg",
            "legende_metier": "Miroir télescopique orientable pour contrôle visuel derrière un carter",
            "explication": (
                "**Principe technique :** Lorsqu'une fuite hydraulique ou une fissure de soudure se situe derrière un carter opaque impossible à démonter rapidement, "
                "le technicien glisse un miroir plan articulé. En l'inclinant à **45,0°** (<b><i>i</i> = <i>i'</i> = 45°</b>), les rayons lumineux issus de la zone cachée "
                "sont déviés de **90°** directement vers l'œil de l'opérateur."
            )
        },
        {
            "titre": "Cas N°3 : Barrière photoélectrique à catadioptre sur convoyeur",
            "img_metier": "maint_capteur_catadioptre.jpg",
            "legende_metier": "Cellule photoélectrique et son réflecteur en coin de cube sur ligne de production",
            "explication": (
                "**Principe technique :** Pour détecter le passage de pièces sur un tapis roulant, un capteur envoie un faisceau infrarouge vers un réflecteur (catadioptre). "
                "Constitué de micro-miroirs à **90°** (coins de cube), il renvoie la lumière parallèlement à son axe d'arrivée même si le support vibre ou se désaxe jusqu'à **± 15°**. "
                "Si l'intensité réfléchie passe sous **80 %**, une alarme de maintenance préventive se déclenche."
            )
        }
    ]

    if "sujet_maint_tire" not in st.session_state:
        st.session_state.sujet_maint_tire = None

    st.subheader("1. Attribution de votre ordre d'intervention")
    
    # Le bouton reste toujours visible et toujours actif (jamais bloqué)
    if st.button("TIRER AU SORT UN SUJET DE MAINTENANCE", key="btn_tirage_maint", use_container_width=True):
        choix_possibles = [i for i in [0, 1, 2] if i != st.session_state.sujet_maint_tire]
        st.session_state.sujet_maint_tire = random.choice(choix_possibles)
        st.session_state.mesures_maint_log = []
        st.rerun()

    if st.session_state.sujet_maint_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique de maintenance parmi les 3 équipements industriels.")
    else:
        idx_sujet = st.session_state.sujet_maint_tire
        data_sujet = sujets_maintenance[idx_sujet]

        st.success(f"Ordre d'intervention attribué : **{data_sujet['titre']}**")
        st.markdown(data_sujet["explication"], unsafe_allow_html=True)
        # ... (le reste du bloc avec les images .jpg et le banc d'essai reste inchangé)
        # ... (le reste du bloc avec les images .jpg et le banc d'essai reste inchangé)


        col_img_m, col_bd_m = st.columns(2)
        with col_img_m:
            img_m = charger_image(data_sujet["img_metier"])
            if img_m is not None:
                st.image(img_m, caption=data_sujet["legende_metier"], use_container_width=True)
            else:
                st.warning(f"Image métier attendue dans le dossier image/ : **{data_sujet['img_metier']}**")

        with col_bd_m:
            img_bd = charger_image("bd_humour_maintenance.jpg")
            if img_bd is not None:
                st.image(img_bd, caption="La pause BD : Quand le laser de maintenance fait des siennes !", use_container_width=True)
            else:
                st.warning("BD humoristique attendue dans le dossier image/ : **bd_humour_maintenance.jpg**")

        st.markdown("---")
        st.subheader("2. Banc de mesure expérimental sur site")

        if "mesures_maint_log" not in st.session_state:
            st.session_state.mesures_maint_log = []

        if idx_sujet == 0:
            st.slider("Défaut angulaire de l'arbre pompe α (degrés) :", min_value=-0.50, max_value=0.50, value=0.25, step=0.01, key="slider_maint_s0")
        elif idx_sujet == 1:
            st.slider("Angle d'inclinaison de la tête du miroir articulé (degrés) :", min_value=15.0, max_value=75.0, value=35.0, step=1.0, key="slider_maint_s1")
        else:
            st.slider("Désalignement angulaire du catadioptre dû aux vibrations (degrés) :", min_value=-25.0, max_value=25.0, value=5.0, step=1.0, key="slider_maint_s2")

        if st.button("ENREGISTRER CE RELEVÉ DANS LE RAPPORT D'INTERVENTION", key="btn_releve_maint", use_container_width=True):
            if "maint_mesure_courante" in st.session_state:
                st.session_state.mesures_maint_log.append(st.session_state.maint_mesure_courante)
                st.rerun()

        fig_maint = mettre_a_jour_maintenance_matplotlib(idx_sujet)
        st.pyplot(fig_maint, use_container_width=True)

        if st.session_state.mesures_maint_log:
            df_maint = pd.DataFrame(
                st.session_state.mesures_maint_log,
                columns=["Paramètre mesuré", "Grandeur optique", "Seuil / Valeur", "Diagnostic"]
            )
            df_maint.insert(0, "Relevé N°", [f"Mesure {i}" for i in range(1, len(df_maint) + 1)])
            st.dataframe(df_maint, use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("3. Évaluation des connaissances sur votre sujet (20 points)")

    if "maint_verrouille_tab6" not in st.session_state:
        st.session_state.maint_verrouille_tab6 = False
    verrou_at6 = st.session_state.maint_verrouille_tab6
    sujet_actif_m = st.session_state.get("sujet_maint_tire", None)

    afficher_atelier_maintenance_complet(sujet_actif_m, verrouille=verrou_at6)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6 (Maintenance)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_maint6 = st.checkbox(
        "Je certifie avoir réalisé mon intervention de maintenance et complété les questions de l'Atelier 6.",
        key="check_certif_maint_final_net",
        disabled=verrou_at6,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_maint6_official_net", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_m is None:
            st.error("Action refusée : Tirez d'abord au sort votre sujet de maintenance en haut de l'onglet.")
        elif not case_certif_maint6:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            banque_active = BANQUES_MAINTENANCE[sujet_actif_m]
            cle_ordre = f"ordre_quiz_maint_sujet_{sujet_actif_m}"

            score_q6 = 0.0
            for q_item in st.session_state.get(cle_ordre, []):
                reponse_eleve = st.session_state.get(f"maint_at6_final_g_{q_item['id']}", "Choisir...")
                if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                    score_q6 += 1.0

            score_t6 = 0.0
            for _, _, bonne_rep_t, cle_t in banque_active["trous"]:
                if str(st.session_state.get(cle_t, "Choisir...")).strip() == str(bonne_rep_t).strip():
                    score_t6 += 1.0

            st.session_state.score_maint6_p1 = round(float(score_q6), 1)
            st.session_state.score_maint6_p2 = round(float(score_t6), 1)
            st.session_state.score_final_maint6 = round(float(score_q6 + score_t6), 1)
            st.session_state.maint_verrouille_tab6 = True
            st.rerun()

    if st.session_state.get("maint_verrouille_tab6", False) and sujet_actif_m is not None:
        scr1 = st.session_state.get("score_maint6_p1", 0.0)
        scr2 = st.session_state.get("score_maint6_p2", 0.0)
        tot_s = st.session_state.get("score_final_maint6", 0.0)
        titre_sujet_export = sujets_maintenance[sujet_actif_m]["titre"]
        banque_active = BANQUES_MAINTENANCE[sujet_actif_m]
        cle_ordre = f"ordre_quiz_maint_sujet_{sujet_actif_m}"

        timestamp_maint6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_maint = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Maintenance Optique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 6 : Applications dans le domaine de la Maintenance Industrielle</p>
                <p>Sujet attribué par tirage au sort : <strong>{titre_sujet_export}</strong></p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_maint6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Relevés expérimentaux enregistrés : <strong>{len(st.session_state.get("mesures_maint_log", []))}</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS SPÉCIFIQUES AU SUJET)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(st.session_state.get(cle_ordre, []), 1):
            saisie = st.session_state.get(f"maint_at6_final_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_maint += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_maint += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for idx_t, (enonce_t, _, attendu_t, cle_t) in enumerate(banque_active["trous"], 1):
            saisie_t = st.session_state.get(cle_t, "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_maint += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_maint += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_maint = preparer_nom_fichier("Rapport_Atelier_6_Maintenance").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_maint,
            file_name=nom_fichier_html_maint,
            mime="text/html",
            use_container_width=True
        )


with tab7:
    st.header("Atelier 7 : Applications dans le domaine des Travaux Publics")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">Maîtrise de la lumière réfléchie sur les chantiers de Travaux Publics :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Sur un chantier de terrassement, de voirie ou de génie civil, la loi de la réflexion <b><i>i</i> = <i>i'</i></b> permet de niveler les sols au millimètre près, de mesurer des ouvrages d'art à distance et d'assurer la visibilité nocturne des zones de travaux.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_tp = [
        {
            "titre": "Chantier N°1 : Nivellement laser rotatif & Guidage de pelle hydraulique",
            "img_metier": "tp_laser_rotatif.jpg",
            "legende_metier": "Laser rotatif sur trépied et cellule de réception montée sur pelle de terrassement",
            "explication": (
                "**Principe technique :** À l'intérieur de la tête tournante du laser, un **pentaprisme** dévie le faisceau vertical d'un angle exact de **90°** par double réflexion interne. "
                "En tournant à 600 tr/min, il génère un **plan horizontal de référence** sur tout le chantier. La cellule fixée sur le bras de la pelle indique au conducteur s'il est au-dessus ou au-dessous de la cote projet (**1,50 m**)."
            )
        },
        {
            "titre": "Chantier N°2 : Métré à distance au télémètre laser & Plaque cible",
            "img_metier": "tp_telemetre_chantier.jpg",
            "legende_metier": "Télémètre laser de chantier visant une plaque cible réfléchissante",
            "explication": (
                "**Principe technique :** Le télémètre émet une impulsion laser vers un ouvrage (mur de soutènement, tablier de pont) et capte la lumière réfléchie. "
                "Il calcule la distance via la formule **D = (c × t) / 2** (aller-retour de la lumière). Sur longue distance ou en plein soleil, une **plaque cible réfléchissante** est indispensable pour maintenir un signal de retour supérieur à **35 %**."
            )
        },
        {
            "titre": "Chantier N°3 : Balisage nocturne rétroréfléchissant (Microbilles & Classe 2)",
            "img_metier": "tp_balisage_microbilles.jpg",
            "legende_metier": "Panneaux temporaires de chantier et équipements haute visibilité éclairés la nuit",
            "explication": (
                "**Principe technique :** Contrairement à une peinture blanche qui diffuse la lumière dans tous les sens, les films de chantier de **Classe 2** contiennent des milliers de **microbilles de verre** ou de **microprismes**. "
                "Grâce à la réflexion interne, ils renvoient le faisceau des phares directement vers les yeux du conducteur jusqu'à **250 mètres** de distance."
            )
        }
    ]

    if "sujet_tp_tire" not in st.session_state:
        st.session_state.sujet_tp_tire = None

    st.subheader("1. Attribution de votre chantier de Travaux Publics")
    if st.button("TIRER AU SORT UN CHANTIER TP", key="btn_tirage_tp", use_container_width=True):
        choix_possibles_tp = [i for i in range(3) if i != st.session_state.sujet_tp_tire]
        st.session_state.sujet_tp_tire = random.choice(choix_possibles_tp)
        st.session_state.mesures_tp_log = []
        for k in list(st.session_state.keys()):
            if k.startswith("tp_t") or k.startswith("tp_at7_final_g_"):
                del st.session_state[k]
        st.rerun()

    if st.session_state.sujet_tp_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un chantier de Travaux Publics parmi les 3 applications.")
    else:
        idx_sujet_tp = st.session_state.sujet_tp_tire
        data_sujet_tp = sujets_tp[idx_sujet_tp]

        st.success(f"Chantier attribué : **{data_sujet_tp['titre']}**")
        st.markdown(data_sujet_tp["explication"], unsafe_allow_html=True)

        col_img_tp, col_bd_tp = st.columns(2)
        with col_img_tp:
            img_tp = charger_image(data_sujet_tp["img_metier"])
            if img_tp is not None:
                st.image(img_tp, caption=data_sujet_tp["legende_metier"], use_container_width=True)
            else:
                st.warning(f"Image métier attendue dans le dossier image/ : **{data_sujet_tp['img_metier']}**")

        with col_bd_tp:
            img_bd_tp = charger_image("bd_humour_tp.jpg")
            if img_bd_tp is not None:
                st.image(img_bd_tp, caption="La pause BD : Quand le niveau laser se dérègle sur le chantier !", use_container_width=True)
            else:
                st.warning("BD humoristique attendue dans le dossier image/ : **bd_humour_tp.jpg**")

        st.markdown("---")
        st.subheader("2. Banc de mesure expérimental sur chantier")

        if "mesures_tp_log" not in st.session_state:
            st.session_state.mesures_tp_log = []

        if idx_sujet_tp == 0:
            st.slider("Hauteur actuelle du godet sous le plan laser (mètres) :", min_value=1.20, max_value=1.80, value=1.65, step=0.01, key="slider_tp_s0")
        elif idx_sujet_tp == 1:
            col_s1_a, col_s1_b = st.columns([0.70, 0.30])
            with col_s1_a:
                st.slider("Distance de l'ouvrage à mesurer (mètres) :", min_value=5.0, max_value=100.0, value=45.0, step=1.0, key="slider_tp_s1")
            with col_s1_b:
                st.checkbox("Plaque cible installée sur le mur", value=True, key="check_tp_cible_s1")
        else:
            col_s2_a, col_s2_b = st.columns([0.65, 0.35])
            with col_s2_a:
                st.slider("Angle d'orientation du panneau par rapport à la route (°) :", min_value=-45.0, max_value=45.0, value=10.0, step=1.0, key="slider_tp_s2")
            with col_s2_b:
                st.radio("Classe du film rétroréfléchissant :", ["Classe 2 (Microprismes TP)", "Classe 1 (Standard)"], key="radio_tp_classe_s2")

        if st.button("ENREGISTRER CE RELEVÉ DANS LE CARNET DE CHANTIER", key="btn_releve_tp", use_container_width=True):
            if "tp_mesure_courante" in st.session_state:
                st.session_state.mesures_tp_log.append(st.session_state.tp_mesure_courante)
                st.rerun()

        fig_tp = mettre_a_jour_tp_matplotlib(idx_sujet_tp)
        st.pyplot(fig_tp, use_container_width=True)

        if st.session_state.mesures_tp_log:
            df_tp = pd.DataFrame(
                st.session_state.mesures_tp_log,
                columns=["Paramètre mesuré", "Grandeur optique", "Référence", "Diagnostic"]
            )
            df_tp.insert(0, "Relevé N°", [f"Mesure {i}" for i in range(1, len(df_tp) + 1)])
            st.dataframe(df_tp, use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("3. Évaluation des connaissances sur votre chantier (20 points)")

    if "tp_verrouille_tab7" not in st.session_state:
        st.session_state.tp_verrouille_tab7 = False
    verrou_at7 = st.session_state.tp_verrouille_tab7
    sujet_actif_tp = st.session_state.get("sujet_tp_tire", None)

    afficher_atelier_tp_complet(sujet_actif_tp, verrouille=verrou_at7)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7 (Travaux Publics)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_tp7 = st.checkbox(
        "Je certifie avoir réalisé mes relevés sur le chantier TP et complété les questions de l'Atelier 7.",
        key="check_certif_tp_final_net",
        disabled=verrou_at7,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_tp7_official_net", use_container_width=True, disabled=verrou_at7):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_tp is None:
            st.error("Action refusée : Tirez d'abord au sort votre chantier TP en haut de l'onglet.")
        elif not case_certif_tp7:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            banque_active_tp = BANQUES_TP[sujet_actif_tp]
            cle_ordre_tp = f"ordre_quiz_tp_sujet_{sujet_actif_tp}"

            score_q7 = 0.0
            for q_item in st.session_state.get(cle_ordre_tp, []):
                reponse_eleve = st.session_state.get(f"tp_at7_final_g_{q_item['id']}", "Choisir...")
                if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                    score_q7 += 1.0

            score_t7 = 0.0
            for _, _, bonne_rep_t, cle_t in banque_active_tp["trous"]:
                if str(st.session_state.get(f"{cle_t}_s{sujet_actif_tp}", "Choisir...")).strip() == str(bonne_rep_t).strip():
                    score_t7 += 1.0

            st.session_state.score_tp7_p1 = round(float(score_q7), 1)
            st.session_state.score_tp7_p2 = round(float(score_t7), 1)
            st.session_state.score_final_tp7 = round(float(score_q7 + score_t7), 1)
            st.session_state.tp_verrouille_tab7 = True
            st.rerun()


    if st.session_state.get("tp_verrouille_tab7", False) and sujet_actif_tp is not None:
        scr1 = st.session_state.get("score_tp7_p1", 0.0)
        scr2 = st.session_state.get("score_tp7_p2", 0.0)
        tot_s = st.session_state.get("score_final_tp7", 0.0)
        titre_sujet_export_tp = sujets_tp[sujet_actif_tp]["titre"]
        banque_active_tp = BANQUES_TP[sujet_actif_tp]
        cle_ordre_tp = f"ordre_quiz_tp_sujet_{sujet_actif_tp}"
        banque_active_tp = BANQUES_TP[sujet_actif_tp]
        cle_ordre_tp = f"ordre_quiz_tp_sujet_{sujet_actif_tp}"

        timestamp_tp7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER TRAVAUX PUBLICS SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_tp = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Travaux Publics Optique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 7 : Applications dans le domaine des Travaux Publics</p>
                <p>Chantier attribué par tirage au sort : <strong>{titre_sujet_export_tp}</strong></p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tp7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique TP : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Relevés de chantier enregistrés : <strong>{len(st.session_state.get("mesures_tp_log", []))}</strong><br>
                Note Totale de l'Atelier 7 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS SPÉCIFIQUES AU CHANTIER)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(st.session_state.get(cle_ordre_tp, []), 1):
            saisie = st.session_state.get(f"tp_at7_final_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_tp += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tp += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for idx_t, (enonce_t, _, attendu_t, cle_t) in enumerate(banque_active_tp["trous"], 1):
            saisie_t = st.session_state.get(f"{cle_t}_s{sujet_actif_tp}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_tp += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tp += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_tp = preparer_nom_fichier("Rapport_Atelier_7_Travaux_Publics").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 7 (.html)",
            data=html_export_tp,
            file_name=nom_fichier_html_tp,
            mime="text/html",
            use_container_width=True
        )



with tab8:
    st.header("Atelier 8 : Applications dans le domaine du Transport Routier")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">L'optique réfléchissante au service de la sécurité des conducteurs :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Dans le transport de marchandises et de voyageurs, les miroirs convexes, les réflecteurs paraboliques de phares et les prismes jour/nuit exploitent la loi <b><i>i</i> = <i>i'</i></b> pour supprimer les angles morts et optimiser la vision de nuit.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_transport = [
        {
            "titre": "Cas Transport N°1 : Antéviseur poids lourd & Suppression de l'angle mort avant",
            "img_metier": "trans_anteviseur_pl.jpg",
            "legende_metier": "Miroir antéviseur convexe (Classe VI) monté au-dessus du pare-brise d'un poids lourd",
            "explication": (
                "**Principe technique :** En raison de la hauteur d'une cabine de camion, un piéton ou un cycliste situé à moins de **2 mètres** devant le pare-chocs est totalement invisible en vision directe. "
                "L'**antéviseur** utilise un **miroir convexe** (bombé) incliné à **42°** qui élargit le cône de réflexion et permet au conducteur de voir jusqu'au pied de sa calandre."
            )
        },
        {
            "titre": "Cas Transport N°2 : Projecteur avant à réflecteur parabolique",
            "img_metier": "trans_phare_parabolique.jpg",
            "legende_metier": "Optique de phare automobile avec miroir parabolique métallisé",
            "explication": (
                "**Principe technique :** Pour éclairer la chaussée à plus de **150 mètres** la nuit, la source lumineuse est placée exactement au **foyer F** d'un miroir concave en forme de **parabole**. "
                "Par propriété géométrique de la réflexion (<b><i>i</i> = <i>i'</i></b>), tous les rayons réfléchis repartent **parallèlement** à l'axe de la route."
            )
        },
        {
            "titre": "Cas Transport N°3 : Rétroviseur intérieur prismatique Jour / Nuit",
            "img_metier": "trans_retro_jour_nuit.jpg",
            "legende_metier": "Prisme en coin du rétroviseur intérieur anti-éblouissement",
            "explication": (
                "**Principe technique :** Le miroir est constitué d'un **prisme en verre** dont la face avant vitrée et la face arrière argentée forment un angle de **4,5°**. "
                "De jour, la face arrière renvoie **90 %** de la lumière vers l'œil. De nuit, basculer la languette dévie le faisceau de 90 % vers le plafond et ne laisse vers l'œil qu'un reflet doux de **4 %**."
            )
        }
    ]

    if "sujet_tr_tire" not in st.session_state:
        st.session_state.sujet_tr_tire = None

    st.subheader("1. Attribution de votre étude technique Transport Routier")
    if st.button("TIRER AU SORT UN SUJET TRANSPORT", key="btn_tirage_tr", use_container_width=True):
        choix_possibles_tr = [i for i in range(3) if i != st.session_state.sujet_tr_tire]
        st.session_state.sujet_tr_tire = random.choice(choix_possibles_tr)
        st.session_state.mesures_tr_log = []
        st.rerun()

    if st.session_state.sujet_tr_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort un cas pratique du Transport Routier parmi les 3 dispositifs.")
    else:
        idx_sujet_tr = st.session_state.sujet_tr_tire
        data_sujet_tr = sujets_transport[idx_sujet_tr]

        st.success(f"Étude attribuée : **{data_sujet_tr['titre']}**")
        st.markdown(data_sujet_tr["explication"], unsafe_allow_html=True)

        col_img_tr, col_bd_tr = st.columns(2)
        with col_img_tr:
            img_tr = charger_image(data_sujet_tr["img_metier"])
            if img_tr is not None:
                st.image(img_tr, caption=data_sujet_tr["legende_metier"], use_container_width=True)
            else:
                st.warning(f"Image métier attendue dans le dossier image/ : **{data_sujet_tr['img_metier']}**")

        with col_bd_tr:
            img_bd_tr = charger_image("bd_humour_transport.jpg")
            if img_bd_tr is not None:
                st.image(img_bd_tr, caption="La pause BD : Attention aux angles morts et aux plein phares !", use_container_width=True)
            else:
                st.warning("BD humoristique attendue dans le dossier image/ : **bd_humour_transport.jpg**")

        st.markdown("---")
        st.subheader("2. Banc d'essai optique sur véhicule")

        if "mesures_tr_log" not in st.session_state:
            st.session_state.mesures_tr_log = []

        if idx_sujet_tr == 0:
            col_tr0_a, col_tr0_b = st.columns(2)
            with col_tr0_a:
                st.slider("Angle d'inclinaison de l'antéviseur (degrés) :", min_value=15.0, max_value=55.0, value=25.0, step=1.0, key="slider_tr_s0")
            with col_tr0_b:
                st.slider("Distance du piéton devant le pare-chocs (mètres) :", min_value=0.30, max_value=2.50, value=1.20, step=0.10, key="slider_tr_pieton_s0")
        elif idx_sujet_tr == 1:
            st.slider("Décalage de l'ampoule par rapport au foyer F de la parabole (mm) :", min_value=-10.0, max_value=10.0, value=0.0, step=0.5, key="slider_tr_s1")
        else:
            st.radio("Position de la languette du rétroviseur intérieur :", ["Position JOUR (Réflexion 90%)", "Position NUIT (Anti-éblouissement 4%)"], key="radio_tr_mode_s2")

        if st.button("ENREGISTRER CE CONTRÔLE DANS LA FICHE VÉHICULE", key="btn_releve_tr", use_container_width=True):
            if "tr_mesure_courante" in st.session_state:
                st.session_state.mesures_tr_log.append(st.session_state.tr_mesure_courante)
                st.rerun()

        fig_tr = mettre_a_jour_transport_matplotlib(idx_sujet_tr)
        st.pyplot(fig_tr, use_container_width=True)

        if st.session_state.mesures_tr_log:
            df_tr = pd.DataFrame(
                st.session_state.mesures_tr_log,
                columns=["Paramètre réglé", "Grandeur optique", "Spécification", "Diagnostic"]
            )
            df_tr.insert(0, "Contrôle N°", [f"Essai {i}" for i in range(1, len(df_tr) + 1)])
            st.dataframe(df_tr, use_container_width=True, hide_index=True)

    st.write("---")
    st.subheader("3. Évaluation des connaissances sur votre étude (20 points)")

    if "tr_verrouille_tab8" not in st.session_state:
        st.session_state.tr_verrouille_tab8 = False
    verrou_at8 = st.session_state.tr_verrouille_tab8
    sujet_actif_tr = st.session_state.get("sujet_tr_tire", None)

    afficher_atelier_transport_complet(sujet_actif_tr, verrouille=verrou_at8)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 8 (Transport Routier)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_tr8 = st.checkbox(
        "Je certifie avoir réalisé mes contrôles sur véhicule et complété les questions de l'Atelier 8.",
        key="check_certif_tr_final_net",
        disabled=verrou_at8,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 8", key="btn_export_tr8_official_net", use_container_width=True, disabled=verrou_at8):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_tr is None:
            st.error("Action refusée : Tirez d'abord au sort votre sujet Transport en haut de l'onglet.")
        elif not case_certif_tr8:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            banque_active_tr = BANQUES_TRANSPORT[sujet_actif_tr]
            cle_ordre_tr = f"ordre_quiz_tr_sujet_{sujet_actif_tr}"

            score_q8 = 0.0
            for q_item in st.session_state.get(cle_ordre_tr, []):
                reponse_eleve = st.session_state.get(f"tr_at8_final_g_{q_item['id']}", "Choisir...")
                if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                    score_q8 += 1.0

            score_t8 = 0.0
            for _, _, bonne_rep_t, cle_t in banque_active_tr["trous"]:
                if str(st.session_state.get(f"{cle_t}_s{sujet_actif_tr}", "Choisir...")).strip() == str(bonne_rep_t).strip():
                    score_t8 += 1.0

            st.session_state.score_tr8_p1 = round(float(score_q8), 1)
            st.session_state.score_tr8_p2 = round(float(score_t8), 1)
            st.session_state.score_final_tr8 = round(float(score_q8 + score_t8), 1)
            st.session_state.tr_verrouille_tab8 = True
            st.rerun()

    if st.session_state.get("tr_verrouille_tab8", False) and sujet_actif_tr is not None:
        scr1 = st.session_state.get("score_tr8_p1", 0.0)
        scr2 = st.session_state.get("score_tr8_p2", 0.0)
        tot_s = st.session_state.get("score_final_tr8", 0.0)
        titre_sujet_export_tr = sujets_transport[sujet_actif_tr]["titre"]
        banque_active_tr = BANQUES_TRANSPORT[sujet_actif_tr]
        cle_ordre_tr = f"ordre_quiz_tr_sujet_{sujet_actif_tr}"

        timestamp_tr8 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER TRANSPORT ROUTIER SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_tr = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Transport Routier Optique - {n_eleve}</title>
            <style>
            <meta charset="utf-8">
            <title>Rapport Transport Routier Optique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 8 : Applications dans le domaine du Transport Routier</p>
                <p>Étude attribuée par tirage au sort : <strong>{titre_sujet_export_tr}</strong></p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_tr8}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique Transport : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Contrôles expérimentaux enregistrés : <strong>{len(st.session_state.get("mesures_tr_log", []))}</strong><br>
                Note Totale de l'Atelier 8 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS SPÉCIFIQUES AU SUJET)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(st.session_state.get(cle_ordre_tr, []), 1):
            saisie = st.session_state.get(f"tr_at8_final_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_tr += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tr += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for idx_t, (enonce_t, _, attendu_t, cle_t) in enumerate(banque_active_tr["trous"], 1):
            saisie_t = st.session_state.get(f"{cle_t}_s{sujet_actif_tr}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_tr += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_tr += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_tr = preparer_nom_fichier("Rapport_Atelier_8_Transport_Routier").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 8 (.html)",
            data=html_export_tr,
            file_name=nom_fichier_html_tr,
            mime="text/html",
            use_container_width=True
        )



with tab9:
    st.header("Atelier 9 : Applications dans le domaine du Géomètre Topographe")

    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px; color: #1e293b;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0; font-size: 16px;">L'optique de précision au cœur des levés topographiques et du cadastre :</p>
        <p style="margin-bottom: 0; line-height: 1.6;">Pour dresser des plans au millimètre près, borner des terrains ou numériser des monuments en 3D, le géomètre topographe s'appuie sur des prismes en coin de cube, des pentaprismes à 90° et des miroirs tournants haute vitesse régis par la loi <b><i>i</i> = <i>i'</i></b>.</p>
    </div>
    """, unsafe_allow_html=True)

    sujets_geometre = [
        {
            "titre": "Mission N°1 : Levé planimétrique à la station totale & Prisme coin de cube",
            "img_metier": "geo_station_totale.jpg",
            "legende_metier": "Station totale robotisée visant un prisme réflecteur monté sur canne",
            "explication": (
                "**Principe technique :** La station totale émet un faisceau infrarouge vers un **prisme en coin de cube** tenu par l'opérateur. "
                "Grâce à **trois réflexions totales** sur ses faces internes à **90°**, le prisme renvoie la lumière parallèlement à son rayon d'entrée jusqu'à **± 25°** de désaxage, garantissant une précision millimétrique."
            )
        },
        {
            "titre": "Mission N°2 : Implantation d'angles droits à l'équerre optique (Pentaprisme)",
            "img_metier": "geo_equerre_optique.jpg",
            "legende_metier": "Équerre optique à double prisme pentagonal utilisée pour lever des perpendiculaires",
            "explication": (
                "**Principe technique :** L'équerre optique superpose deux **pentaprismes** dont les faces réfléchissantes forment un angle de **45°**. "
                "Chaque rayon subit une **double réflexion** et ressort dévié d'un angle droit exact de **90°** (<b>2 × 45°</b>). Lorsque les images des jalons gauche, droit et avant sont alignées, le point est implanté."
            )
        },
        {
            "titre": "Mission N°3 : Numérisation de façade au scanner laser 3D (LiDAR)",
            "img_metier": "geo_scanner_lidar.jpg",
            "legende_metier": "Scanner laser terrestre 3D relevant un nuage de points haute densité",
            "explication": (
                "**Principe technique :** Au centre du scanner, un **miroir plan tournant** dévie le faisceau laser dans un plan vertical (rotation du faisceau **2α** pour une rotation miroir **α**), tandis que la tête pivote à **360°**. "
                "La réflexion diffuse sur la façade permet de calculer la position 3D (X, Y, Z) de plus d'un million de points par seconde."
            )
        }
    ]

    if "sujet_geo_tire" not in st.session_state:
        st.session_state.sujet_geo_tire = None

    st.subheader("1. Attribution de votre mission topographique")
    if st.button("TIRER AU SORT UNE MISSION GÉOMÈTRE", key="btn_tirage_geo", use_container_width=True):
        choix_possibles_geo = [i for i in range(3) if i != st.session_state.sujet_geo_tire]
        st.session_state.sujet_geo_tire = random.choice(choix_possibles_geo)
        st.session_state.mesures_geo_log = []
        st.rerun()

    if st.session_state.sujet_geo_tire is None:
        st.info("Cliquez sur le bouton ci-dessus pour tirer au sort une mission de Géomètre Topographe parmi les 3 instruments.")
    else:
        idx_sujet_geo = st.session_state.sujet_geo_tire
        data_sujet_geo = sujets_geometre[idx_sujet_geo]

        st.success(f"Mission attribuée : **{data_sujet_geo['titre']}**")
        st.markdown(data_sujet_geo["explication"], unsafe_allow_html=True)

        col_img_geo, col_bd_geo = st.columns(2)
        with col_img_geo:
            img_geo = charger_image(data_sujet_geo["img_metier"])
            if img_geo is not None:
                st.image(img_geo, caption=data_sujet_geo["legende_metier"], use_container_width=True)
            else:
                st.warning(f"Image métier attendue dans le dossier image/ : **{data_sujet_geo['img_metier']}**")

        with col_bd_geo:
            img_bd_geo = charger_image("bd_humour_geometre.jpg")
            if img_bd_geo is not None:
                st.image(img_bd_geo, caption="La pause BD : Quand un camion passe devant le prisme en plein levé !", use_container_width=True)
            else:
                st.warning("BD humoristique attendue dans le dossier image/ : **bd_humour_geometre.jpg**")

        st.markdown("---")
        st.subheader("2. Banc de mesure topographique sur le terrain")

        if "mesures_geo_log" not in st.session_state:
            st.session_state.mesures_geo_log = []

        if idx_sujet_geo == 0:
            col_geo0_a, col_geo0_b = st.columns(2)
            with col_geo0_a:
                st.slider("Distance Station Totale - Prisme (mètres) :", min_value=10.0, max_value=300.0, value=120.0, step=5.0, key="slider_geo_dist_s0")
            with col_geo0_b:
                st.slider("Désorientation angulaire du prisme (degrés) :", min_value=-35.0, max_value=35.0, value=10.0, step=1.0, key="slider_geo_ang_s0")
        elif idx_sujet_geo == 1:
            st.slider("Décalage latéral du géomètre sur l'alignement AB (mètres) :", min_value=-2.00, max_value=2.00, value=0.40, step=0.05, key="slider_geo_s1")
        else:
            col_geo2_a, col_geo2_b = st.columns(2)
            with col_geo2_a:
                st.slider("Distance Scanner 3D - Façade (mètres) :", min_value=5.0, max_value=80.0, value=25.0, step=1.0, key="slider_geo_s2")
            with col_geo2_b:
                st.slider("Vitesse de rotation du miroir interne (tr/s) :", min_value=10.0, max_value=100.0, value=50.0, step=5.0, key="slider_geo_freq_s2")

        if st.button("ENREGISTRER CE POINT DANS LE CARNET DE LEVÉ", key="btn_releve_geo", use_container_width=True):
            if "geo_mesure_courante" in st.session_state:
                st.session_state.mesures_geo_log.append(st.session_state.geo_mesure_courante)
                st.rerun()

        fig_geo = mettre_a_jour_geometre_matplotlib(idx_sujet_geo)
        st.pyplot(fig_geo, use_container_width=True)

        if st.session_state.mesures_geo_log:
            df_geo = pd.DataFrame(
                st.session_state.mesures_geo_log,
                columns=["Paramètre terrain", "Grandeur optique", "Précision / Pas", "Validation"]
            )
            df_geo.insert(0, "Station N°", [f"Point {i}" for i in range(1, len(df_geo) + 1)])
            st.dataframe(df_geo, use_container_width=True, hide_index=True)

    # =========================================================================
    # 3. ÉVALUATION (10 QUESTIONS + 10 TROUS) ET EXPORT HTML COMPLET
    # =========================================================================
    st.write("---")
    st.subheader("3. Évaluation des connaissances sur votre mission (20 points)")

    if "geo_verrouille_tab9" not in st.session_state:
        st.session_state.geo_verrouille_tab9 = False
    verrou_at9 = st.session_state.geo_verrouille_tab9
    sujet_actif_geo = st.session_state.get("sujet_geo_tire", None)

    afficher_atelier_geometre_complet(sujet_actif_geo, verrouille=verrou_at9)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9 (Géomètre Topographe)")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_geo9 = st.checkbox(
        "Je certifie avoir réalisé mon levé topographique et complété les questions de l'Atelier 9.",
        key="check_certif_geo_final_net",
        disabled=verrou_at9,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9", key="btn_export_geo9_official_net", use_container_width=True, disabled=verrou_at9):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif sujet_actif_geo is None:
            st.error("Action refusée : Tirez d'abord au sort votre mission Géomètre en haut de l'onglet.")
        elif not case_certif_geo9:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            banque_active_geo = BANQUES_GEOMETRE[sujet_actif_geo]
            cle_ordre_geo = f"ordre_quiz_geo_sujet_{sujet_actif_geo}"

            score_q9 = 0.0
            for q_item in st.session_state.get(cle_ordre_geo, []):
                reponse_eleve = st.session_state.get(f"geo_at9_final_g_{q_item['id']}", "Choisir...")
                if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                    score_q9 += 1.0

            score_t9 = 0.0
            for _, _, bonne_rep_t, cle_t in banque_active_geo["trous"]:
                if str(st.session_state.get(f"{cle_t}_s{sujet_actif_geo}", "Choisir...")).strip() == str(bonne_rep_t).strip():
                    score_t9 += 1.0

            st.session_state.score_geo9_p1 = round(float(score_q9), 1)
            st.session_state.score_geo9_p2 = round(float(score_t9), 1)
            st.session_state.score_final_geo9 = round(float(score_q9 + score_t9), 1)
            st.session_state.geo_verrouille_tab9 = True
            st.rerun()

    if st.session_state.get("geo_verrouille_tab9", False) and sujet_actif_geo is not None:
        scr1 = st.session_state.get("score_geo9_p1", 0.0)
        scr2 = st.session_state.get("score_geo9_p2", 0.0)
        tot_s = st.session_state.get("score_final_geo9", 0.0)
        titre_sujet_export_geo = sujets_geometre[sujet_actif_geo]["titre"]
        banque_active_geo = BANQUES_GEOMETRE[sujet_actif_geo]
        cle_ordre_geo = f"ordre_quiz_geo_sujet_{sujet_actif_geo}"

        timestamp_geo9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER GÉOMÈTRE TOPOGRAPHE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_geo = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Géomètre Topographe Optique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation d'Optique Géométrique</h1>
                <p>Atelier 9 : Applications dans le domaine du Géomètre Topographe</p>
                <p>Mission attribuée par tirage au sort : <strong>{titre_sujet_export_geo}</strong></p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_geo9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique Topographie : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours (Texte à trous) : <strong>{scr2:.1f} / 10</strong><br>
                Points de levé enregistrés au carnet : <strong>{len(st.session_state.get("mesures_geo_log", []))}</strong><br>
                Note Totale de l'Atelier 9 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">1. CORRECTION DÉTAILLÉE DU QUIZ (10 QUESTIONS SPÉCIFIQUES À LA MISSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(st.session_state.get(cle_ordre_geo, []), 1):
            saisie = st.session_state.get(f"geo_at9_final_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_geo += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_geo += """
                </tbody>
            </table>

            <div class="sub-title">2. CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS - 10 CASES)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase à compléter</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for idx_t, (enonce_t, _, attendu_t, cle_t) in enumerate(banque_active_geo["trous"], 1):
            saisie_t = st.session_state.get(f"{cle_t}_s{sujet_actif_geo}", "Choisir...")
            v_lbl_t = "CORRECT" if str(saisie_t).strip() == str(attendu_t).strip() else "INCORRECT"
            v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
            html_export_geo += f"<tr><td>{idx_t}</td><td>{enonce_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_geo += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_geo = preparer_nom_fichier("Rapport_Atelier_9_Geometre_Topographe").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 9 (.html)",
            data=html_export_geo,
            file_name=nom_fichier_html_geo,
            mime="text/html",
            use_container_width=True
        )
