# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Réflexion ",
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

