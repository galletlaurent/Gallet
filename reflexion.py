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
        ax.annotate("", xy=(xm, ym), xytext=(250, 154), arrowprops=dict(arrowstyle="->", color="#ef4444", lw=2))
        # Rayon réfléchi partant du miroir selon angle 2*ang_mir par rapport à la verticale
        ang_refl_rad = math.radians(2.0 * ang_mir)
        x_fin = xm - 170.0 * math.sin(ang_refl_rad)
        y_fin = ym - 170.0 * math.cos(ang_refl_rad)
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

    # Petite fonction d'affichage sécurisé utilisant votre système charger_image()
    def afficher_vignette_jpg(nom_jpg, legende):
        img = charger_image(nom_jpg)
        if img is not None:
            st.image(img, caption=legende, use_container_width=True)
        else:
            st.warning(f"Image attendue dans le dossier image/ : **{nom_jpg}**")

    # =========================================================================
    # 1. LES SAVANTS ET LEURS DÉCOUVERTES (PORTRAITS + EXPÉRIENCES EN .JPG)
    # =========================================================================
    st.subheader("1. Les grands savants et leurs découvertes sur la réflexion")

    # --- SAVANT 1 : EUCLIDE ---
    col_euc_img, col_euc_txt = st.columns([1, 2])
    with col_euc_img:
        afficher_vignette_jpg("euclide.jpg", "Euclide (IIIe siècle av. J.-C.)")
    with col_euc_txt:
        st.info("""
        **Euclide et *La Catoptrique* (vers 300 av. J.-C.)**
        * **Le savant :** Mathématicien de la Grèce antique vivant à Alexandrie.
        * **Sa découverte :** Il publie *La Catoptrique*, le premier traité consacré aux miroirs. Il y démontre géométriquement que la lumière se propage en ligne droite et que **l'angle de réflexion est toujours égal à l'angle d'incidence**.
        """)

    st.markdown("---")

    # --- SAVANT 2 : IBN AL-HAYTHAM (ALHAZEN) ---
    col_alh_img, col_alh_txt = st.columns([1, 2])
    with col_alh_img:
        afficher_vignette_jpg("alhazen.jpg", "Ibn al-Haytham / Alhazen (965 - 1040)")
    with col_alh_txt:
        st.info("""
        **Ibn al-Haytham, dit Alhazen (*Traité d'optique*, 1021)**
        * **Le savant :** Physicien, mathématicien et astronome majeur de l'âge d'or islamique.
        * **Sa découverte :** Il prouve par l'expérience que la lumière provient des sources lumineuses, rebondit sur les objets et entre dans l'œil (et non l'inverse). Il établit aussi que le rayon incident, la normale et le rayon réfléchi sont dans **un même plan**.
        """)

    st.markdown("---")

    # --- SAVANT 3 : RENÉ DESCARTES ---
    col_des_img, col_des_txt = st.columns([1, 2])
    with col_des_img:
        afficher_vignette_jpg("descartes.jpg", "René Descartes (1596 - 1650)")
    with col_des_txt:
        st.info("""
        **René Descartes (*La Dioptrique*, 1637)**
        * **Le savant :** Mathématicien, physicien et philosophe français.
        * **Sa découverte :** Il formalise les lois universelles de la réflexion et de la réfraction (lois de Snell-Descartes). Il fixe le vocabulaire technique moderne (**normale, rayon incident, rayon réfléchi**) et la formule **$i = i'$**.
        """)

    st.markdown("---")

    # --- SAVANT 4 : JOHN HENRY PEPPER ---
    col_pep_img, col_pep_txt = st.columns([1, 2])
    
    with col_pep_img:
        afficher_vignette_jpg("pepper.jpg", "John Henry Pepper (1821 - 1900)")
        
    with col_pep_txt:
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

    col_bd1, col_bd2, col_hum = st.columns(3)
    with col_bd1:
        afficher_vignette_jpg("bd_reflexion_1.jpg", "BD Planche 1 : Le trajet du rayon lumineux")
    with col_bd2:
        afficher_vignette_jpg("bd_reflexion_2.jpg", "BD Planche 2 : L'égalité des angles i = i'")
    with col_hum:
        afficher_vignette_jpg("humour_reflexion.jpg", "La pause humoristique : Réflexion physique vs philosophique")


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
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")





with tab8:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")



with tab9:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")

