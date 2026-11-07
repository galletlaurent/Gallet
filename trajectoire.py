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
    "Permis CE",
    "Permis CE et caravane",
    "Permis C",
])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]





def afficher_atelier_trajectoire_gabarit(verrouille=False):
    """Affiche le Quiz et le Texte à trous côte à côte en bas de la page pour l'atelier trajectoire."""
    import random

    st.subheader("Atelier Interactif : Cinématique et Dynamique du Véhicule Porteur")

    questions_trajectoire_sources = [
        {"id": "qt1", "q": "Lors d'un virage, quelle ligne décrit une trajectoire circulaire parfaite ?", "options": ["Les roues avant (ligne rouge)", "Les roues arrière (ligne bleue)", "Le centre de gravité uniquement"], "rep": "Les roues avant (ligne rouge)"},
        {"id": "qt2", "q": "Quel phénomène physique force les roues arrière à couper le virage vers l'intérieur ?", "options": ["Le décalage de chasse géométrique", "La force centrifuge", "Le devers de la route"], "rep": "Le décalage de chasse géométrique"},
        {"id": "qt3", "q": "Où se situe le point de décrochage (amorce de la courbe) pour les roues arrière ?", "options": ["Décalé en X après la ligne de rupture", "Pile sur la ligne verticale 0", "Avant la ligne de rupture"], "rep": "Décalé en X après la ligne de rupture"},
        {"id": "qt4", "q": "Quelle force pousse le porteur vers l'extérieur du virage perpendiculairement à sa trajectoire ?", "options": ["La force centrifuge", "La réaction normale", "Le poids du chargement"], "rep": "La force centrifuge"},
        {"id": "qt5", "q": "Comment appelle-t-on l'inclinaison de la chaussée vers l'intérieur d'un virage ?", "options": ["Le dévers de la route", "L'angle d'Ackermann", "La raideur de dérive"], "rep": "Le dévers de la route"},
        {"id": "qt6", "q": "Quel est l'effet d'un dévers positif sur le risque de basculement du porteur ?", "options": ["Il augmente la stabilité", "Il provoque un glissement immédiat", "Il amplifie la force centrifuge"], "rep": "Il augmente la stabilité"},
        {"id": "qt7", "q": "Si la vitesse du véhicule double dans un même virage, par combien est multipliée la force centrifuge ?", "options": ["Par quatre", "Par deux", "Elle reste identique"], "rep": "Par quatre"},
        {"id": "qt8", "q": "Quelle force de contact parallèle au sol empêche les pneumatiques de déraper ?", "options": ["La force de frottement", "La réaction normale", "Le poids total"], "rep": "La force de frottement"},
        {"id": "qt9", "q": "Quelle est l'unité de mesure de l'accélération transversale subie par le véhicule ?", "options": ["Le G (fraction de la gravité)", "Le Newton (N)", "Le Pascal (Pa)"], "rep": "Le G (fraction de la gravité)"},
        {"id": "qt10", "q": "Si le moment de renversement dépasse le moment stabilisateur, que subit le véhicule ?", "options": ["Un basculement", "Un glissement", "Une trajectoire rectiligne"], "rep": "Un basculement"}
    ]

    if "ordre_quiz_trajectoire_aleatoire" not in st.session_state:
        random.shuffle(questions_trajectoire_sources)
        st.session_state.ordre_quiz_trajectoire_aleatoire = questions_trajectoire_sources

    if "champs_trajectoire_clean" not in st.session_state:
        st.session_state.champs_trajectoire_clean = [
            ("1. Les roues avant décrivent une courbe guidée tandis que les roues arrière subissent une ..........", ["Choisir...", "chasse", "dérive"], "chasse", "traj_t1"),
            ("2. L'essieu arrière reste droit au départ et ne commence à tourner qu'avec un décalage en ..........", ["Choisir...", "X", "Y"], "X", "traj_t2"),
            ("3. En fin de virage, la stabilisation rectiligne de l'essieu arrière s'effectue avec un décalage en ..........", ["Choisir...", "Y", "X"], "Y", "traj_t3"),
            ("4. La force centrifuge est directement proportionnelle au carré de la .......... du véhicule.", ["Choisir...", "vitesse", "masse"], "vitesse", "traj_t4"),
            ("5. La force perpendiculaire à la chaussée inclinée s'appelle la réaction ..........", ["Choisir...", "normale", "tangentielle"], "normale", "traj_t5"),
            ("6. Plus le centre de gravité du chargement est haut, plus le risque de .......... est élevé.", ["Choisir...", "basculement", "glissement"], "basculement", "traj_t6"),
            ("7. L'angle de .......... de la route aide à compenser les effets de la force centrifuge.", ["Choisir...", "dévers", "braquage"], "dévers", "traj_t7"),
            ("8. Si les pneus perdent leur adhérence latérale, le porteur subit un ..........", ["Choisir...", "glissement", "renversement"], "glissement", "traj_t8"),
            ("9. La ligne courbe dessinée en rouge représente la trajectoire des roues ..........", ["Choisir...", "avant", "arrière"], "avant", "traj_t9"),
            ("10. Le franchissement des lignes noires de la chaussée constitue une .......... de route.", ["Choisir...", "sortie", "stabilité"], "sortie", "traj_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_trajectoire_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"traj_at3_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_trajectoire_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_traj_clean", disabled=verrouille, label_visibility="collapsed")


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
    st.header("Simulation de Trajectoire - Camion Rigide Categorie CE")
    st.markdown("""
    Cette section montre l'influence de la vitesse, du poids et de la geometrie sur le phenomene de chasse 
    (le decalage des roues arriere vers l'interieur du virage).
    """)

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
        angle_route_deg = st.slider("Angle de devers de la route (degres)", 0, 15, 4, key="devers_c_central")
        largeur_voie = 3.5

    # Configuration de l'infrastructure
    y_centre_virage = 2 * rayon_courbure
    beta = np.radians(angle_route_deg)
    
    g = 9.81
    seuil_glissement_mu = 0.35
    hauteur_cg = 1.1 + (masse_charge / masse_totale) * 0.9
    largeur_camion = 2.5

    r_int = rayon_courbure - (largeur_voie / 2)
    r_ext = rayon_courbure + (largeur_voie / 2)

    ds = 0.05  
    distance_totale = rayon_courbure * np.radians(angle_virage_deg) + 20.0
    pas = int(distance_totale / ds)

    # Creation de tableaux de zeros pour eviter les erreurs d'indexation
    x_arr = np.zeros(pas)
    y_arr = np.zeros(pas)
    x_av = np.zeros(pas)
    y_av = np.zeros(pas)
    theta = np.zeros(pas)

    # CORRECTION DEFINITIVE : Remplissage de l'index 0 pour conserver la structure NumPy
    x_av[0] = -10.0
    y_av[0] = rayon_courbure
    x_arr[0] = -10.0 - empattement
    y_arr[0] = rayon_courbure
    theta[0] = 0.0

    evenement_detecte = "Aucun"
    index_interruption = pas - 1

    # Calcul des variables physiques
    vitesse_ms = vitesse_kmh / 3.6
    acceleration_laterale_g = (vitesse_ms**2) / (rayon_courbure * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE : ROUGE = AVANT SUR LE TRAIT / BLEU = ARRIERE AVANT
    # =============================================================================
    cap_cible_rad = np.radians(angle_virage_deg)

    for i in range(1, pas):
        # 1. Trajectoire de reference de l'essieu avant (Ligne rouge)
        if x_av[i-1] < 0.0:
            # L'avant (rouge) reste strictement horizontal et droit jusqu'au trait vertical (0)
            x_av[i] = x_av[i-1] + ds
            y_av[i] = rayon_courbure
            theta[i] = 0.0
        elif x_av[i-1] >= 0.0 and theta[i-1] < cap_cible_rad:
            # L'avant (rouge) commence a tourner pile au trait vertical (0)
            cap_av_rad = ds / rayon_courbure
            theta[i] = theta[i-1] + cap_av_rad
            x_av[i] = rayon_courbure * np.sin(theta[i])
            y_av[i] = y_centre_virage - rayon_courbure * np.cos(theta[i])
        else:
            # Sortie en ligne droite verticale stable
            x_av[i] = x_av[i-1] + ds * np.cos(cap_cible_rad)
            y_av[i] = y_av[i-1] + ds * np.sin(cap_cible_rad)
            theta[i] = cap_cible_rad

        # 2. Trajectoire de l'essieu arriere tracte (Ligne bleue)
        # L'arriere (bleu) commence a s'ecarter vers le haut avant le trait vertical (0) 
        # a cause de la traction cinematique de la barre de carrosserie
        dx = x_av[i] - x_arr[i-1]
        dy = y_av[i] - y_arr[i-1]
        distance_inter_essieux = np.hypot(dx, dy)
        
        x_arr[i] = x_av[i] - empattement * (dx / distance_inter_essieux)
        y_arr[i] = y_av[i] - empattement * (dy / distance_inter_essieux)

        # 3. Calcul de la dynamique des forces liees au devers pour les alertes
        if x_av[i] >= 0.0 and theta[i] < cap_cible_rad:
            acc_lat_inst_g = (vitesse_ms**2) / (rayon_courbure * g)
            
            P_normale = masse_totale * 1000 * g * np.cos(beta)
            Fc_normale = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.sin(beta)
            N = P_normale + Fc_normale
            
            P_tangente = masse_totale * 1000 * g * np.sin(beta)
            Fc_tangente = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) * np.cos(beta)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg
            Moment_stabilisateur = N * (largeur_camion / 2) + P_tangente * hauteur_cg
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte = "Basculement"
                index_interruption = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte == "Aucun":
                evenement_detecte = "Glissement"
                
        # 4. Verification du franchissement des voies
        if x_av[i] >= 0.0:
            r_av = np.sqrt(x_av[i]**2 + (y_av[i] - y_centre_virage)**2)
            r_ar = np.sqrt(x_arr[i]**2 + (y_arr[i] - y_centre_virage)**2)
            if (r_av > r_ext or r_av < r_int or r_ar > r_ext or r_ar < r_int) and evenement_detecte == "Aucun":
                evenement_detecte = "Sortie de route"
    # Tronquage des vecteurs au point d'arret reel
    x_arr = x_arr[:index_interruption+1]
    y_arr = y_arr[:index_interruption+1]
    theta = theta[:index_interruption+1]
    x_av = x_av[:index_interruption+1]
    y_av = y_av[:index_interruption+1]

    if len(x_av) > 1 and evenement_detecte != "Basculement":
        rayons_arriere = np.sqrt(x_arr**2 + (y_arr - y_centre_virage)**2)
        rayons_avant = np.sqrt(x_av**2 + (y_av - y_centre_virage)**2)
        decalage_reel = np.max(rayons_avant) - np.min(rayons_arriere)
    else:
        decalage_reel = 0.0

    t_route = np.linspace(0, np.radians(angle_virage_deg), 100)

    # Reconstruction de la chaussee fixe concentrique
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

    # =============================================================================
    # RENDU ET COLONNES D'AFFICHAGE AVEC INTEGRATION DU BOUTON D'ANIMATION
    # =============================================================================
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_arr), max(1, len(x_arr) // 40)) if declencher_animation else [len(x_arr) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int, y_route_int, color='black', linewidth=2)
        ax_anim.plot(x_route_ext, y_route_ext, color='black', linewidth=2)
        
        if k > 0:
            # ROUGE pour l'AVANT (x_av), BLEU pour l'ARRIERE (x_arr)
            ax_anim.plot(x_av[:k], y_av[:k], color='#e74c3c', linewidth=2, label="Trajectoire Roues AV")
            ax_anim.plot(x_arr[:k], y_arr[:k], color='#3498db', linewidth=2, linestyle='--', label="Trajectoire Roues AR")
        
        cos_tk, sin_tk = np.cos(theta[k]), np.sin(theta[k])
        arriere_gauche = [x_arr[k] - 1.0 * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk - (largeur_camion/2) * cos_tk]
        arriere_droit  = [x_arr[k] - 1.0 * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] - 1.0 * sin_tk + (largeur_camion/2) * cos_tk]
        avant_droit    = [x_arr[k] + (empattement + 1.0) * cos_tk + (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk + (largeur_camion/2) * cos_tk]
        avant_gauche   = [x_arr[k] + (empattement + 1.0) * cos_tk - (largeur_camion/2) * (-sin_tk), y_arr[k] + (empattement + 1.0) * sin_tk - (largeur_camion/2) * cos_tk]
        ax_anim.add_patch(Polygon(np.array([arriere_gauche, arriere_droit, avant_droit, avant_gauche]), closed=True, facecolor='#2c3e50', alpha=0.8))
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Tracé du schema vectoriel des forces (Vue arriere synchrone)
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        
        # Inclinaison de la ligne d'assiette du sol
        ax_f.plot([-2, 2], [-2 * np.sin(beta), 2 * np.sin(beta)], color='black', linewidth=3)
        
        # Section rectangulaire du camion inclinee de l'angle beta
        cam_box = np.array([[-largeur_camion/2, 0], [largeur_camion/2, 0], [largeur_camion/2, hauteur_cg * 1.4], [-largeur_camion/2, hauteur_cg * 1.4]])
        R_mat = np.array([[np.cos(beta), -np.sin(beta)], [np.sin(beta), np.cos(beta)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        from matplotlib.patches import Polygon
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        # Positionnement de la masse au CG
        G_coord = np.dot(np.array([0, hauteur_cg]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        # Calcul des points d'appui des pneumatiques au sol
        roue_gauche = np.dot(np.array([-largeur_camion/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_camion/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=150, marker='s', zorder=4)
        
        # Echelle de proportion des forces
        f_scale = 1.0 / (masse_totale * 1000 * g)
        val_P = masse_totale * 1000 * g
        val_Fc = masse_totale * 1000 * (vitesse_ms**2 / rayon_courbure) if evenement_detecte != "Basculement" else 0.0
        
        # CORRECTION EFFECTUÉE : Extraction avec [0] et [1] des composantes des flèches au CG
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        # Repartition des forces Normales et Tangentielles
        val_N_totale = val_P * np.cos(beta) + val_Fc * np.sin(beta)
        val_Ff_totale = val_Fc * np.cos(beta) - val_P * np.sin(beta) if evenement_detecte != "Basculement" else 0.0
        
        # CORRECTION EFFECTUÉE : Extraction avec [0] et [1] pour le tracé sous les roues
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

        decalage_inst = np.abs(np.sqrt(x_av[k]**2 + (y_av[k] - y_centre_virage)**2) - np.sqrt(x_arr[k]**2 + (y_arr[k] - y_centre_virage)**2)) if x_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Decalage de chasse instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_deg:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms**2)/(rayon_courbure*g) if x_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- AFFICHAGE DE FIN DE PARCOURS (INTERACTIF PLOTLY) ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Decalage de chasse maximal", value=f"{decalage_reel:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_deg:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_g:.2f} G")

    if evenement_detecte == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementCE.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).")
            except Exception:
                st.error("Fichier basculementCE.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : Le camion a bascule sous l'effet de la force centrifuge.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int, y=y_route_int, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext, y=y_route_ext, name="Bord exterieur", line=dict(color='black', width=2)))
            
            # ATTRIBUTION CONFORME VISUELLE : x_av = ROUGE (Avant) / x_arr = BLEU (Arriere)
            fig_plotly.add_trace(go.Scatter(x=x_av, y=y_av, name="Trajectoire Roues AVANT", line=dict(color='#e74c3c', width=3)))
            fig_plotly.add_trace(go.Scatter(x=x_arr, y=y_arr, name="Trajectoire Roues ARRIERE", line=dict(color='#3498db', width=3, dash='dash')))
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        # INDENTATION CORRIGÉE : Alignement par rapport aux blocs précédents
        if evenement_detecte == "Glissement":
            zone_alerte.warning("GLISSEMENT : L'effort lateral demande a surpasse l'adherence disponible (Derapage).")
        elif evenement_detecte == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : Le gabarit a franchi les marquages au sol.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : Le camion est reste stable dans sa voie.")

    if "suite_verrouille_tab3_trajectoire" not in st.session_state:
        st.session_state.suite_verrouille_tab3_trajectoire = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_trajectoire

    # Rendu des questionnaires d'évaluation de l'Atelier 3
    afficher_atelier_trajectoire_gabarit(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Cinématique et Dynamique sur la trajectoire des essieux.",
        key="check_certif_traj3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_traj_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz par parcours sécurisé de clés
            score_q3 = 0.0
            if "ordre_quiz_trajectoire_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_trajectoire_aleatoire:
                    saisie = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"traj_at3_final_g_{q_item['id']}"):
                            saisie = st.session_state[k]
                            break
                    if str(saisie).strip() == str(q_item["rep"]).strip(): 
                        score_q3 += 1.0

            # 2. Correction automatisée du Texte à trous par parcours sécurisé de clés
            score_t3 = 0.0
            if "champs_trajectoire_clean" in st.session_state:
                for ligne in st.session_state.champs_trajectoire_clean:
                    cle_variable = ligne[-1]
                    attendu_texte = ligne[2]
                    saisie_texte = "Choisir..."
                    for k in st.session_state.keys():
                        if k.startswith(f"{cle_variable}_traj_clean"):
                            saisie_texte = st.session_state[k]
                            break
                    if str(saisie_texte).strip() == str(attendu_texte).strip(): 
                        score_t3 += 1.0

            st.session_state.score_suite3_traj_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_traj_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_traj = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_trajectoire = True
            st.rerun()

    # -------------------------------------------------------------------------
    # PARTIE 4 : EXPORTATION DU RAPPORT INDIVIDUEL HTML SCELLÉ
    # -------------------------------------------------------------------------
    if st.session_state.get("suite_verrouille_tab3_trajectoire", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_traj_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_traj_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_traj", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER CINÉMATIQUE SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_traj3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Trajectoire Porteur - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Physique-Cinématique</h1>
                <p>Atelier 3 : Modélisation et Étude des Trajectoires et Gabarits d'Inscription en Courbe du Véhicule Porteur</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_trajectoire_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_trajectoire_aleatoire, 1):
                saisie = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"traj_at3_final_g_{q_item['id']}"):
                        saisie = st.session_state[k]
                        break
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_traj3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_traj3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_trajectoire_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_trajectoire_clean, 1):
                cle_variable = ligne[-1]
                attendu_texte = ligne[2]
                phrase_enonce = ligne[0]
                saisie_texte = "Choisir..."
                for k in st.session_state.keys():
                    if k.startswith(f"{cle_variable}_traj_clean"):
                        saisie_texte = st.session_state[k]
                        break
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_traj3 += f"<tr><td>{num}</td><td>{phrase_enonce}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_traj3 += f"""
                </tbody>
            </table>
            
            <div class="sub-title">DONNÉES COMPLÉMENTAIRES D'ATELIER TECHNIQUE</div>
            <p style="font-size: 13px; color: #64748b;">
                Valeur maximale enregistrée pour le décalage de chasse : <strong>{st.session_state.get('decalage_reel', 0.0):.2f} m</strong><br>
                Angle de dévers configuré pour la chaussée : <strong>{st.session_state.get('angle_route_deg', 0.0):.1f} degrés</strong>
            </p>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL SCELLÉ (FORMAT HTML)",
            data=html_export_traj3,
            file_name=f"Rapport_Trajectoire_{n_eleve}_{p_eleve}.html",
            background="red",
            mime="text/html",
            key="btn_download_html_official_traj3",
            use_container_width=True
        )





                

with tab4:
    st.header("Simulation Permis CE et caravane")
    st.info("Espace reserve pour la simulation d'un camion rigide tractant une remorque de type caravane.")

with tab5:
    st.header("Simulation Permis C )")
    st.info("Espace reserve pour le second module applique au Permis C.")

    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        vitesse_kmh_semi = st.slider("Vitesse de l'ensemble (km/h)", 5, 50, 20, step=5, key="vitesse_semi")
        vitesse_ms_semi = vitesse_kmh_semi / 3.6
        empattement_tracteur = st.slider("Empattement du tracteur - L1 (m)", 3.0, 5.0, 3.8, step=0.1, key="emp_trac_semi")

    with col_p2:
        # Configuration detailee de la repartition des masses lourdes
        masse_tracteur = st.slider("Masse a vide du tracteur (t)", 5.0, 10.0, 7.5, step=0.5, key="m_trac_semi")
        masse_semi_vide = st.slider("Masse a vide de la semi-remorque (t)", 4.0, 12.0, 6.0, step=0.5, key="m_semi_vide")
        masse_charge_semi = st.slider("Masse du chargement (t)", 0.0, 30.0, 20.0, step=0.5, key="m_charge_semi")
        
        # Calcul de la masse totale de l'ensemble routier articule
        masse_totale_semi = masse_tracteur + masse_semi_vide + masse_charge_semi
        st.write(f"Masse totale de l'ensemble : {masse_totale_semi:.1f} tonnes")
        
        distance_sellette = st.slider("Avance de la sellette / essieu AR (m)", 0.0, 1.0, 0.3, step=0.05, key="sellette_semi")
        longueur_semi = st.slider("Distance sellette - Essieux semi - L2 (m)", 6.0, 10.0, 7.5, step=0.1, key="long_semi")

    with col_p3:
        rayon_courbure_semi = st.slider("Rayon de la route (m)", 15, 60, 25, key="rc_semi")
        angle_virage_semi = st.slider("Angle du virage (degres)", 45, 135, 90, key="av_semi")
        angle_route_semi = st.slider("Angle de devers de la route (degres)", 0, 15, 4, key="devers_semi_central")
        largeur_voie = 3.5

    # Configuration de l'infrastructure
    y_centre_virage_semi = 2 * rayon_courbure_semi
    beta_semi = np.radians(angle_route_semi)
    
    g = 9.81
    seuil_glissement_mu = 0.35
    largeur_camion = 2.5
    
    # Centre de gravite adaptatif dependant du poids du chargement integre
    hauteur_cg_semi = 1.1 + (masse_charge_semi / (masse_tracteur + masse_semi_vide)) * 1.2

    r_int_semi = rayon_courbure_semi - (largeur_voie / 2)
    r_ext_semi = rayon_courbure_semi + (largeur_voie / 2)

    # Calcul preliminaire du pas d'espace
    ds_semi = 0.05  
    distance_totale_semi = rayon_courbure_semi * np.radians(angle_virage_semi) + 25.0
    pas_semi = int(distance_totale_semi / ds_semi)

    # Creation des structures de tableaux fixes (3 essieux distincts)
    x_trac_av = np.zeros(pas_semi)
    y_trac_av = np.zeros(pas_semi)
    x_trac_ar = np.zeros(pas_semi)
    y_trac_ar = np.zeros(pas_semi)
    x_semi_ar = np.zeros(pas_semi)
    y_semi_ar = np.zeros(pas_semi)
    
    theta_trac = np.zeros(pas_semi)
    theta_semi = np.zeros(pas_semi)

    # CORRECTION STRICTE : Affectation par index [0] pour préserver le format matriciel NumPy
    x_trac_av[0] = -10.0
    y_trac_av[0] = rayon_courbure_semi
    
    x_trac_ar[0] = x_trac_av[0] - empattement_tracteur
    y_trac_ar[0] = rayon_courbure_semi
    theta_trac[0] = 0.0

    # Position initiale de la sellette d'attelage
    x_sellette_init = x_trac_ar[0] + distance_sellette
    x_semi_ar[0] = x_sellette_init - longueur_semi
    y_semi_ar[0] = rayon_courbure_semi
    theta_semi[0] = 0.0

    evenement_detecte_semi = "Aucun"
    index_interruption_semi = pas_semi - 1

    # Calcul de l'acceleration transversale nominale
    acceleration_laterale_semi_g = (vitesse_ms_semi**2) / (rayon_courbure_semi * g)

    # =============================================================================
    # BOUCLE DE CALCUL GEOMETRIQUE RESOLUTION SEMI-REMORQUE COMPLÈTE
    # =============================================================================
    cap_cible_semi_rad = np.radians(angle_virage_semi)

    for i in range(1, pas_semi):
        # 1. Trajectoire de reference de l'essieu avant du tracteur (Roues AV - Rouge)
        if x_trac_av[i-1] < 0.0:
            x_trac_av[i] = x_trac_av[i-1] + ds_semi
            y_trac_av[i] = rayon_courbure_semi
            theta_trac[i] = 0.0
        elif x_trac_av[i-1] >= 0.0 and theta_trac[i-1] < cap_cible_semi_rad:
            cap_av_rad = ds_semi / rayon_courbure_semi
            theta_trac[i] = theta_trac[i-1] + cap_av_rad
            x_trac_av[i] = rayon_courbure_semi * np.sin(theta_trac[i])
            y_trac_av[i] = y_centre_virage_semi - rayon_courbure_semi * np.cos(theta_trac[i])
        else:
            x_trac_av[i] = x_trac_av[i-1] + ds_semi * np.cos(cap_cible_semi_rad)
            y_trac_av[i] = y_trac_av[i-1] + ds_semi * np.sin(cap_cible_semi_rad)
            theta_trac[i] = cap_cible_semi_rad

        # 2. Cinematique de l'essieu arriere du tracteur (Roues AR Tracteur - Bleu)
        dx_trac = x_trac_av[i] - x_trac_ar[i-1]
        dy_trac = y_trac_av[i] - y_trac_ar[i-1]
        dist_trac = np.hypot(dx_trac, dy_trac)
        x_trac_ar[i] = x_trac_av[i] - empattement_tracteur * (dx_trac / dist_trac)
        y_trac_ar[i] = y_trac_av[i] - empattement_tracteur * (dy_trac / dist_trac)

        # Coordonnees instantanees de la sellette d'attelage pivotante
        x_sel = x_trac_ar[i] + distance_sellette * np.cos(theta_trac[i])
        y_sel = y_trac_ar[i] + distance_sellette * np.sin(theta_trac[i])

        # 3. Cinematique du groupe d'essieux de la semi-remorque (Roues AR Semi - Vert)
        dx_semi = x_sel - x_semi_ar[i-1]
        dy_semi = y_sel - y_semi_ar[i-1]
        dist_semi = np.hypot(dx_semi, dy_semi)
        theta_semi[i] = np.arctan2(dy_semi, dx_semi)
        x_semi_ar[i] = x_sel - longueur_semi * (dx_semi / dist_semi)
        y_semi_ar[i] = y_sel - longueur_semi * (dy_semi / dist_semi)

        # 4. Calcul de la dynamique des forces et verifications de securite
        if x_trac_av[i] >= 0.0 and theta_trac[i] < cap_cible_semi_rad:
            val_P_semi = masse_totale_semi * 1000 * g
            val_Fc_semi = masse_totale_semi * 1000 * (vitesse_ms_semi**2 / rayon_courbure_semi)
            
            P_normale = val_P_semi * np.cos(beta_semi)
            Fc_normale = val_Fc_semi * np.sin(beta_semi)
            N = P_normale + Fc_normale
            
            P_tangente = val_P_semi * np.sin(beta_semi)
            Fc_tangente = val_Fc_semi * np.cos(beta_semi)
            F_frottement_requise = Fc_tangente - P_tangente
            F_frottement_max = seuil_glissement_mu * N
            
            Moment_renversement = Fc_tangente * hauteur_cg_semi
            Moment_stabilisateur = N * (largeur_camion / 2) + P_tangente * hauteur_cg_semi
            
            if Moment_renversement >= Moment_stabilisateur:
                evenement_detecte_semi = "Basculement"
                index_interruption_semi = i
                break
            if np.abs(F_frottement_requise) >= F_frottement_max and evenement_detecte_semi == "Aucun":
                evenement_detecte_semi = "Glissement"
                
        # 5. Verification du gabarit routier pour les 3 trains d'essieux
        if x_trac_av[i] >= 0.0:
            r_av = np.sqrt(x_trac_av[i]**2 + (y_trac_av[i] - y_centre_virage_semi)**2)
            r_ar = np.sqrt(x_trac_ar[i]**2 + (y_trac_ar[i] - y_centre_virage_semi)**2)
            r_sm = np.sqrt(x_semi_ar[i]**2 + (y_semi_ar[i] - y_centre_virage_semi)**2)
            if (r_av > r_ext_semi or r_av < r_int_semi or r_ar > r_ext_semi or r_ar < r_int_semi or r_sm > r_ext_semi or r_sm < r_int_semi) and evenement_detecte_semi == "Aucun":
                evenement_detecte_semi = "Sortie de route"

    # Tronquage des vecteurs au point d'arret reel
    x_trac_av = x_trac_av[:index_interruption_semi+1]
    y_trac_av = y_trac_av[:index_interruption_semi+1]
    x_trac_ar = x_trac_ar[:index_interruption_semi+1]
    y_trac_ar = y_trac_ar[:index_interruption_semi+1]
    x_semi_ar = x_semi_ar[:index_interruption_semi+1]
    y_semi_ar = y_semi_ar[:index_interruption_semi+1]
    theta_trac = theta_trac[:index_interruption_semi+1]

    # Calcul du balayage de chasse maximal cumule (Tracteur + Remorque)
    if len(x_trac_av) > 1 and evenement_detecte_semi != "Basculement":
        rayons_semi = np.sqrt(x_semi_ar**2 + (y_semi_ar - y_centre_virage_semi)**2)
        rayons_avant = np.sqrt(x_trac_av**2 + (y_trac_av - y_centre_virage_semi)**2)
        decalage_reel_semi = np.max(rayons_avant) - np.min(rayons_semi)
    else:
        decalage_reel_semi = 0.0
    t_route_semi = np.linspace(0, np.radians(angle_virage_semi), 100)

    # Generation des traces de routes fixes concentriques
    x_dr_semi = np.linspace(-10, 0, 10)
    x_arc_int_semi = r_int_semi * np.sin(t_route_semi)
    y_arc_int_semi = y_centre_virage_semi - r_int_semi * np.cos(t_route_semi)
    x_arc_ext_semi = r_ext_semi * np.sin(t_route_semi)
    y_arc_ext_semi = y_centre_virage_semi - r_ext_semi * np.cos(t_route_semi)
    
    x_fin_int_semi = x_arc_int_semi[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_semi))
    y_fin_int_semi = y_arc_int_semi[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_semi))
    x_fin_ext_semi = x_arc_ext_semi[-1] + np.linspace(0, 15, 10) * np.cos(np.radians(angle_virage_semi))
    y_fin_ext_semi = y_arc_ext_semi[-1] + np.linspace(0, 15, 10) * np.sin(np.radians(angle_virage_semi))
    
    x_route_int_semi = np.concatenate([x_dr_semi, x_arc_int_semi, x_fin_int_semi])
    y_route_int_semi = np.concatenate([np.full_like(x_dr_semi, rayon_courbure_semi - largeur_voie/2), y_arc_int_semi, y_fin_int_semi])
    x_route_ext_semi = np.concatenate([x_dr_semi, x_arc_ext_semi, x_fin_ext_semi])
    y_route_ext_semi = np.concatenate([np.full_like(x_dr_semi, rayon_courbure_semi + largeur_voie/2), y_arc_ext_semi, y_fin_ext_semi])

    # Configuration des colonnes d'affichage
    col_graphe, col_analyse = st.columns(2)

    with col_analyse:
        st.subheader("Indicateurs Physiques Synchrones")
        zone_metrique_chasse = st.empty()
        zone_metrique_devers = st.empty()
        zone_metrique_g = st.empty()
        zone_alerte = st.empty()
        
        declencher_animation = st.button("Lancer la simulation pas-a-pas", key="btn_anim_semi_final")
        
        st.subheader("Schema Vectoriel du Bilan des Forces (Vue arriere)")
        zone_schema_forces = st.empty()

    with col_graphe:
        conteneur_graphique = st.empty()

    points_animation = range(0, len(x_trac_av), max(1, len(x_trac_av) // 40)) if declencher_animation else [len(x_trac_av) - 1]
    
    import time
    from matplotlib.patches import Polygon

    for k in points_animation:
        # Trace Matplotlib de l'ensemble articule mobile
        fig_anim, ax_anim = plt.subplots(figsize=(7, 5))
        ax_anim.plot(x_route_int_semi, y_route_int_semi, color='black', linewidth=2)
        ax_anim.plot(x_route_ext_semi, y_route_ext_semi, color='black', linewidth=2)
        
        if k > 0:
            # Ligne bleue pour l'AVANT (tracteur), Ligne rouge pour l'ARRIÈRE (semi)
            ax_anim.plot(x_trac_av[:k], y_trac_av[:k], color='#3498db', linewidth=2, label="Trajectoire Roues AV")
            ax_anim.plot(x_semi_ar[:k], y_semi_ar[:k], color='#e74c3c', linewidth=2, linestyle='--', label="Trajectoire Roues AR")
        
        # Dessinement simplifie des deux boites (Tracteur + Remorque)
        cos_tk, sin_tk = np.cos(theta_trac[k]), np.sin(theta_trac[k])
        ax_anim.scatter(x_trac_av[k], y_trac_av[k], color='#3498db', s=60)
        ax_anim.scatter(x_trac_ar[k], y_trac_ar[k], color='black', s=60)
        ax_anim.scatter(x_semi_ar[k], y_semi_ar[k], color='#e74c3c', s=60)
        
        ax_anim.axis("equal")
        ax_anim.set_xlim(-12, max(x_route_ext_semi) + 5)
        ax_anim.set_ylim(-5, max(y_route_ext_semi) + 5)
        
        if declencher_animation:
            conteneur_graphique.pyplot(fig_anim)
        plt.close(fig_anim)

        # Tracé du schema des forces synchrone
        fig_forces, ax_f = plt.subplots(figsize=(5, 3.5))
        ax_f.plot([-2, 2], [-2 * np.sin(beta_semi), 2 * np.sin(beta_semi)], color='black', linewidth=3)
        cam_box = np.array([[-largeur_camion/2, 0], [largeur_camion/2, 0], [largeur_camion/2, hauteur_cg_semi * 1.4], [-largeur_camion/2, hauteur_cg_semi * 1.4]])
        R_mat = np.array([[np.cos(beta_semi), -np.sin(beta_semi)], [np.sin(beta_semi), np.cos(beta_semi)]])
        cam_box_rot = np.dot(cam_box, R_mat.T)
        ax_f.add_patch(Polygon(cam_box_rot, closed=True, facecolor='#7f8c8d', alpha=0.3))
        
        G_coord = np.dot(np.array([0, hauteur_cg_semi]), R_mat.T)
        ax_f.scatter(G_coord[0], G_coord[1], color='black', s=90, zorder=5)
        
        roue_gauche = np.dot(np.array([-largeur_camion/2, 0]), R_mat.T)
        roue_droite = np.dot(np.array([largeur_camion/2, 0]), R_mat.T)
        ax_f.scatter([roue_gauche[0], roue_droite[0]], [roue_gauche[1], roue_droite[1]], color='black', s=150, marker='s', zorder=4)
        
        f_scale = 1.0 / (masse_totale_semi * 1000 * g)
        val_P = masse_totale_semi * 1000 * g
        val_Fc = masse_totale_semi * 1000 * (vitesse_ms_semi**2 / rayon_courbure_semi) if evenement_detecte_semi != "Basculement" else 0.0
        
        ax_f.arrow(G_coord[0], G_coord[1], 0, -val_P * f_scale * 1.3, head_width=0.08, head_length=0.12, color='#2ecc71', label='Poids (P)')
        ax_f.arrow(G_coord[0], G_coord[1], val_Fc * f_scale * 1.3, 0, head_width=0.08, head_length=0.12, color='#e74c3c', label='Force Centrifuge (Fc)')
        
        val_N_totale = val_P * np.cos(beta_semi) + val_Fc * np.sin(beta_semi)
        val_Ff_totale = val_Fc * np.cos(beta_semi) - val_P * np.sin(beta_semi) if evenement_detecte_semi != "Basculement" else 0.0
        
        ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_semi), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_semi), head_width=0.08, head_length=0.12, color='#9b59b6', label='Reaction Normale (N)')
        ax_f.arrow(roue_droite[0], roue_droite[1], -(val_N_totale/2) * f_scale * 1.3 * np.sin(beta_semi), (val_N_totale/2) * f_scale * 1.3 * np.cos(beta_semi), head_width=0.08, head_length=0.12, color='#9b59b6')
        
        if np.abs(val_Ff_totale) > 0:
            ax_f.arrow(roue_gauche[0], roue_gauche[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_semi), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_semi), head_width=0.08, head_length=0.12, color='#3498db', label='Frottement Pneus (Ff)')
            ax_f.arrow(roue_droite[0], roue_droite[1], -(val_Ff_totale/2) * f_scale * 1.3 * np.cos(beta_semi), -(val_Ff_totale/2) * f_scale * 1.3 * np.sin(beta_semi), head_width=0.08, head_length=0.12, color='#3498db')

        ax_f.set_xlim(-2.2, 2.2)
        ax_f.set_ylim(-1.0, 3.2)
        ax_f.axis('off')
        
        handles, labels = ax_f.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax_f.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
        zone_schema_forces.pyplot(fig_forces)
        plt.close(fig_forces)

        # Compteurs textuels intermédiaires
        decalage_inst = np.abs(np.sqrt(x_trac_av[k]**2 + (y_trac_av[k] - y_centre_virage_semi)**2) - np.sqrt(x_semi_ar[k]**2 + (y_semi_ar[k] - y_centre_virage_semi)**2)) if x_trac_av[k] >= 0.0 else 0.0
        zone_metrique_chasse.metric(label="Balayage global instantane", value=f"{decalage_inst:.2f} m")
        zone_metrique_devers.metric(label="Angle de devers de la route", value=f"{angle_route_semi:.1f} degres")
        zone_metrique_g.metric(label="Acceleration transversale", value=f"{(vitesse_ms_semi**2)/(rayon_courbure_semi*g) if x_trac_av[k]>=0.0 else 0.0:.2f} G")
        
        if declencher_animation:
            time.sleep(0.04)

    # --- RENDU PLOTLY INTERACTIF ZOOMABLE EN FIN DE SIMULATION ---
    animation_terminee = True
    zone_metrique_chasse.metric(label="Balayage global maximal (Chasse)", value=f"{decalage_reel_semi:.2f} m")
    zone_metrique_devers.metric(label="Devers configure de la chaussee", value=f"{angle_route_semi:.1f} degres")
    zone_metrique_g.metric(label="Acceleration transversale maximale", value=f"{acceleration_laterale_semi_g:.2f} G")

    if evenement_detecte_semi == "Basculement":
        with col_graphe:
            conteneur_graphique.empty()
            try:
                st.image("basculementCE.jpg", caption="Accident : Rupture d'equilibre statique (Renversement).")
            except Exception:
                st.error("Fichier basculementCE.jpg introuvable.")
        zone_alerte.error("ACCIDENT DETECTE : Le vehicule articule a bascule sous l'effet de la force centrifuge.")
    else:
        with col_graphe:
            conteneur_graphique.empty()
            
            import plotly.graph_objects as go
            fig_plotly = go.Figure()
            fig_plotly.add_trace(go.Scatter(x=x_route_int_semi, y=y_route_int_semi, name="Bord interieur", line=dict(color='black', width=2)))
            fig_plotly.add_trace(go.Scatter(x=x_route_ext_semi, y=y_route_ext_semi, name="Bord exterieur", line=dict(color='black', width=2)))
            
            # 1. Roues AVANT Tracteur (Bleu lisse)
            fig_plotly.add_trace(go.Scatter(x=x_trac_av, y=y_trac_av, name="Trajectoire Roues AVANT Tracteur", line=dict(color='#3498db', width=3)))
            
            # 2. L'ESSIEU MANQUANT : Roues ARRIÈRE Tracteur / Sellette (Vert pointillé)
            fig_plotly.add_trace(go.Scatter(x=x_trac_ar, y=y_trac_ar, name="Trajectoire Essieu AR TRACTEUR", line=dict(color='#2ecc71', width=2.5, dash='dash')))
            
            # 3. Roues ARRIÈRE Semi-remorque (Rouge pointillé extrême)
            fig_plotly.add_trace(go.Scatter(x=x_semi_ar, y=y_semi_ar, name="Trajectoire Roues ARRIERE SEMI", line=dict(color='#e74c3c', width=3, dash='dash')))
            
            fig_plotly.update_layout(
                xaxis=dict(scaleanchor="y", scaleratio=1),
                hovermode="closest",
                height=450,
                title="Visualisation interactive (Zoomable pour mesures fines)"
            )
            st.plotly_chart(fig_plotly, use_container_width=True)

        if evenement_detecte_semi == "Glissement":
            zone_alerte.warning("GLISSEMENT : L'ensemble routier a surpasse l'adherence disponible (Mise en portefeuille).")
        elif evenement_detecte_semi == "Sortie de route":
            zone_alerte.warning("SORTIE DE VOIE : La semi-remorque a chevauche le marquage au sol interieur.")
        else:
            zone_alerte.success("TRAJECTOIRE REUSSITE : L'ensemble articule est reste stable dans sa voie.")







