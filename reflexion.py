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
    st.header("Atelier 2 : Lois de la Reflexion ")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel de la Premiere Loi de Snell-Descartes pour la Reflexion :</p>
        <ul>
            <li><strong>Loi fondamentale :</strong> $i = i'$ (L'angle de reflexion $i'$ est rigoureusement egal a l'angle d'incidence $i$).</li>
            <li><strong>Mesure des angles :</strong> Les deux angles sont mesures par rapport a la <strong>normale</strong> (la droite perpendiculaire a la surface du miroir au point d'impact).</li>
            <li><strong>Application du Spectre de Pepper :</strong> Permet de creer une image virtuelle superposee a un objet reel par une inclinaison precise a $45.0^\circ$.</li>
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





with tab6:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")




with tab7:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")





with tab8:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")



with tab9:
    st.header("**Manipulation  : Application Navale (Le Periscope du sous-marin)**")

