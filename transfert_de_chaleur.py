# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application transfert de chaleur",
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
import sys
from PIL import Image
# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application thermo")
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
    "La température",
    "La chaleur",
    "Les modes de transfert thermique",
    "Les conducteurs et les isolants thermiques",
    "La quantité de chaleur",
    "Coefficient de transmission thermique",
    "La résistance thermique",
    "Application dans le domaine de la maintenance",
    "Application dans le domaine des TP",
    "Application dans le domaine de la conduite routière",
    "Application dans le domaine des géomètres",    
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
tab10 = onglets[10]
tab11 = onglets[11] 
tab12 = onglets[12]


def afficher_atelier_tp_dynamique(scenario_actif_tp, verrouille=False):
    import random

    # =============================================================================
    # ADAPTATION DYNAMIQUE DES QUESTIONS SELON LE SCÉNARIO TP ACTIF
    # =============================================================================
    if scenario_actif_tp == "Béton massif : Exothermie d'une pile de pont":
        questions_sources_tp = [
            {"id": "tp9_e1", "q": "Comment qualifie-t-on la libération d'énergie provoquée par l'hydratation chimique du ciment ?", "options": ["Exothermique", "Endothermique", "Isotherme"], "rep": "Exothermique"},
            {"id": "tp9_e2", "q": "Quelle est l'unité de mesure de la quantité d'énergie dégagée par kg de liant ?", "options": ["kJ/kg", "W/(m.K)", "J/K"], "rep": "kJ/kg"},
            {"id": "tp9_e3", "q": "Pourquoi la chaleur s'accumule-t-elle au cœur des éléments de béton massifs ?", "options": ["Car la conductivité thermique lambda du béton est faible", "Car le béton est un métal pur", "Car le coffrage insère de l'électricité"], "rep": "Car la conductivité thermique lambda du béton est faible"},
            {"id": "tp9_e4", "q": "Quel constituant du béton frais réagit avec l'eau pour engendrer ce flux de chaleur ?", "options": ["Le ciment", "Le sable", "Les adjuvants plastifiants"], "rep": "Le ciment"},
            {"id": "tp9_e5", "q": "Quel dispositif tubulaire interne permet d'extraire activement les calories du massif ?", "options": ["Un réseau de tubes de refroidissement à eau glacée", "Un manomètre", "Un extracteur d'air"], "rep": "Un réseau de tubes de refroidissement à eau glacée"},
            {"id": "tp9_e6", "q": "Dans quel type de structure le risque lié au pic exothermique est-il le plus critique ?", "options": ["Un barrage ou une pile de pont massive", "Un linteau de porte unitaire", "Une bordure de chaussée"], "rep": "Un barrage ou une pile de pont massive"},
            {"id": "tp9_e7", "q": "Si l'on augmente la quantité de ciment par m³ de béton, la quantité d'énergie dégagée sera :", "options": ["Plus élevée", "Plus faible", "Strictement identique"], "rep": "Plus élevée"},
            {"id": "tp9_e8", "q": "La chaleur emmagasinée temporairement au centre du bloc augmente sa chaleur :", "options": ["Sensible", "Latente de fusion", "Latente de vaporisation"], "rep": "Sensible"},
            {"id": "tp9_e9", "q": "L'évacuation de la chaleur vers l'extérieur du coffrage métallique se fait par :", "options": ["Conduction solide", "Changement d'état", "Sublimation"], "rep": "Conduction solide"},
            {"id": "tp9_e10", "q": "Pour réduire le dégagement thermique initial, la maintenance utilise des ciments dits :", "options": ["À basse chaleur d'hydratation (de type CEM III ou IV)", "Accélérés à haute résistance", "Alumineux"], "rep": "À basse chaleur d'hydratation (de type CEM III ou IV)"}
        ]
        trous_sources_tp = [
            ("1. La réaction chimique liant l'eau au ciment est de nature ..........", ["Choisir...", "exothermique", "endothermique"], "exothermique", "therm10_tp1"),
            ("2. Le béton frais présente une .......... conductivité lambda qui emprisonne le flux.", ["Choisir...", "faible", "forte"], "faible", "therm10_tp2"),
            ("3. L'énergie sensible accumulée engendre une hausse de .......... au centre.", ["Choisir...", "température", "résistance"], "température", "therm10_tp3"),
            ("4. La chaleur dégagée par le ciment est quantifiée en kJ par ..........", ["Choisir...", "kilogramme", "Kelvin"], "kilogramme", "therm10_tp4"),
            ("5. Ce phénomène critique concerne les pièces de béton de volume ..........", ["Choisir...", "massif", "mince"], "massif", "therm10_tp5"),
            ("6. L'extraction des calories s'effectue via un circuit de tubes d'..........", ["Choisir...", "eau", "air"], "eau", "therm10_tp6"),
            ("7. Ajuster le dosage en liant permet de modérer le .......... thermique global.", ["Choisir...", "flux", "volume"], "flux", "therm10_tp7"),
            ("8. Les liants d'élite à prise lente limitent la cinétique de l'..........", ["Choisir...", "exothermie", "conduction"], "exothermie", "therm10_tp8"),
            ("9. La quantité de chaleur s'évacue lentement à travers les parois par ..........", ["Choisir...", "conduction", "fusion"], "conduction", "therm10_tp9"),
            ("10. Ce contrôle thermique prévient les défauts de cohésion de la ..........", ["Choisir...", "structure", "peinture"], "structure", "therm10_tp10")
        ]
    elif scenario_actif_tp == "Ouvrage d'art : Fissuration thermique de tablier":
        questions_sources_tp = [
            {"id": "tp9_f1", "q": "Quel écart thermique maximal cœur/surface tolère-t-on pour éviter la fissuration du béton ?", "options": ["20 °C", "5 °C", "50 °C"], "rep": "20 °C"},
            {"id": "tp9_f2", "q": "Les contraintes mécaniques induites par un fort gradient de température sont des contraintes de :", "options": ["Traction", "Compression", "Torsion"], "rep": "Traction"},
            {"id": "tp9_f3", "q": "Si le gradient thermique mesuré sur le tablier atteint 25 °C, que se passe-t-il sur la peau du béton ?", "options": ["Des micro-fissures de traction apparaissent", "Le béton se liquéfie", "La résistance mécanique double"], "rep": "Des micro-fissures de traction apparaissent"},
            {"id": "tp9_f4", "q": "Quelle action permet de réduire l'écart de température en réchauffant la surface du béton ?", "options": ["Le déploiement de matelas ou bâches isolantes", "L'arrosage intensif à l'eau glacée", "La dépose immédiate des coffrages"], "rep": "Le déploiement de matelas ou bâches isolantes"},
            {"id": "tp9_f5", "q": "Le calcul de l'allongement ou du raccourcissement du tablier sous l'effet du climat dépend du :", "options": ["Coefficient de dilatation linéaire de l'acier et du béton", "Coefficient de conductivité de l'air", "Changement d'état latent"], "rep": "Coefficient de dilatation linéaire de l'acier et du béton"},
            {"id": "tp9_f6", "q": "Quelle saison présente le risque le plus aigu de fort gradient thermique pour un jeune tablier ?", "options": ["L'hiver (nuit glaciale)", "L'été (canicule)", "Le printemps doux"], "rep": "L'hiver (nuit glaciale)"},
            {"id": "tp9_f7", "q": "L'isoler en surface à l'aide de matelas de cure revient mathématiquement à :", "options": ["Augmenter la résistance thermique R en surface", "Réduire l'épaisseur totale", "Augmenter le lambda du matériau"], "rep": "Augmenter la résistance thermique R en surface"},
            {"id": "tp9_f8", "q": "Un profil thermique lissé et aplati supprime les contraintes de :", "options": ["Traction thermique", "Compression hydraulique", "Torsion mécanique"], "rep": "Traction thermique"},
            {"id": "tp9_f9", "q": "La mesure des gradients thermiques par thermocouples noyés dans l'ouvrage constitue un contrôle :", "options": ["Non destructif", "Curatif structurel", "Correctif après rupture"], "rep": "Non destructif"},
            {"id": "tp9_f10", "q": "Quelle enveloppe protectrice permet de lisser la température superficielle du béton ?", "options": ["La bâche de cure isolante", "Le coffrage en tôle nue ventilée", "Une couche de peinture hydrofuge"], "rep": "La bâche de cure isolante"}
        ]
        trous_sources_tp = [
            ("1. Un écart thermique excessif crée des contraintes de .......... mécanique.", ["Choisir...", "traction", "compression"], "traction", "therm10_tp1"),
            ("2. Le seuil de vigilance à ne pas dépasser pour le gradient est fixé à .......... °C.", ["Choisir...", "20", "50"], "20", "therm10_tp2"),
            ("3. Les fissures superficielles altèrent l'.......... et la durabilité du tablier.", ["Choisir...", "étanchéité", "couleur"], "étanchéité", "therm10_tp3"),
            ("4. Déployer des matelas de cure permet d'apporter une .......... thermique de surface.", ["Choisir...", "résistance", "conductivité"], "résistance", "therm10_tp4"),
            ("5. Cette barrière isolante R freine le .......... calorifique perdu vers l'air gelé.", ["Choisir...", "flux", "volume"], "flux", "therm10_tp5"),
            ("6. Le lissage des températures supprime la cassure de la courbe du .......... thermique.", ["Choisir...", "profil", "fluide"], "profil", "therm10_tp6"),
            ("7. La surveillance des ponts thermiques d'ouvrages est un diagnostic non ..........", ["Choisir...", "destructif", "conforme"], "destructif", "therm10_tp7"),
            ("8. Les variations géométriques de la structure découlent de la .......... linéaire.", ["Choisir...", "dilatation", "fusion"], "dilatation", "therm10_tp8"),
            ("9. Les Watts perdus à travers la peau du béton s'expriment en ..........", ["Choisir...", "Watts", "Joules"], "Watts", "therm10_tp9"),
            ("10. Maîtriser ces gradients garantit la parfaite tenue mécanique du ..........", ["Choisir...", "béton", "sol"], "béton", "therm10_tp10")
        ]
    elif scenario_actif_tp == "Viabilité hivernale : Coulage par temps de gel":
        questions_sources_tp = [
            {"id": "tp9_g1", "q": "Quel risque majeur pèse sur l'eau du béton frais lors d'un coulage par température négative ?", "options": ["Le gel (changement d'état en glace)", "Une évaporation instantanée", "Une ébullition précoce"], "rep": "Le gel (changement d'état en glace)"},
            {"id": "tp9_g2", "q": "À quelle température précise s'effectue la transition latente de solidification de l'eau ?", "options": ["0 °C", "100 °C", "20 °C"], "rep": "0 °C"},
            {"id": "tp9_g3", "q": "Si l'eau du béton gèle avant la fin de la prise, la matrice du ciment se retrouve :", "options": ["Détruite par éclatement cristallin", "Renforcée de moitié", "Strictement inchangée"], "rep": "Détruite par éclatement cristallin"},
            {"id": "tp9_g4", "q": "Quelle forme d'énergie doit-on apporter sur le chantier pour maintenir la masse au-dessus de 5 °C ?", "options": ["De la chaleur sensible via des brûleurs", "De la chaleur latente de fusion", "Un flux conducteur inversé"], "rep": "De la chaleur sensible via des brûleurs"},
            {"id": "tp9_g5", "q": "Pour isoler des fondations coulées par temps de gel, on déploie des bâches à forte :", "options": ["Résistance thermique R", "Conductivité lambda", "Transmission superficielle"], "rep": "Résistance thermique R"},
            {"id": "tp9_g6", "q": "La transformation de l'eau liquide en cristaux de glace rigides est une :", "options": ["Solidification (libération de chaleur latente)", "Fusion thermique", "Vaporisation"], "rep": "Solidification (libération de chaleur latente)"},
            {"id": "tp9_g7", "q": "Pour accélérer la cinétique chimique et contrer le gel, la maintenance du chantier ajoute :", "options": ["Un adjuvant accélérateur de prise", "Un retardateur", "De l'eau glacée"], "rep": "Un adjuvant accélérateur de prise"},
            {"id": "tp9_g8", "q": "L'unité de mesure du flux thermique perdu en surface à travers les bâches est :", "options": ["Le Watt par mètre carré (W/m²)", "Le Joule par kg", "Le Pascal"], "rep": "Le Watt par mètre carré (W/m²)"},
            {"id": "tp9_g9", "q": "Une bâche isolante performante se caractérise par une conductivité lambda :", "options": ["La plus faible possible proche de zéro", "Supérieure à celle de l'acier", "Identique à celle du cuivre"], "rep": "La plus faible possible proche de zéro"},
            {"id": "tp9_g10", "q": "Quelle température minimale doit conserver le béton pendant sa cure hivernale ?", "options": ["5 °C", "-5 °C", "50 °C"], "rep": "5 °C"}
        ]
        trous_sources_tp = [
            ("1. Le gel de l'eau correspond à une transition de phase appelée ..........", ["Choisir...", "solidification", "fusion"], "solidification", "therm10_tp1"),
            ("2. Cette transition latente destructrice s'opère à la température fixe de .......... °C.", ["Choisir...", "0", "20"], "0", "therm10_tp2"),
            ("3. L'expansion volumique de la glace brise le réseau .......... du ciment.", ["Choisir...", "cristallin", "liquide"], "cristallin", "therm10_tp3"),
            ("4. Les matelas de cure opposent une forte .......... thermique R au froid.", ["Choisir...", "résistance", "conductivité"], "résistance", "therm10_tp4"),
            ("5. La bâche isolante performante possède un coefficient .......... très bas.", ["Choisir...", "lambda", "U"], "lambda", "therm10_tp5"),
            ("6. Le flux thermique perdu en surface se comptabilise en Watts par ..........", ["Choisir...", "mètre carré", "Kelvin"], "mètre carré", "therm10_tp6"),
            ("7. Apporter de l'énergie à l'aide de radiants augmente la chaleur .......... du bloc.", ["Choisir...", "sensible", "latente"], "sensible", "therm10_tp7"),
            ("8. Pour maintenir la cinétique chimique, le béton doit rester au-dessus de .......... °C.", ["Choisir...", "5", "0"], "5", "therm10_tp8"),
            ("9. Un adjuvant .......... de durcissement aide à contrer l'effet de l'hiver.", ["Choisir...", "accélérateur", "retardateur"], "accélérateur", "therm10_tp9"),
            ("10. Protéger la cure hivernale garantit la bonne prise finale du ..........", ["Choisir...", "béton", "sol"], "béton", "therm10_tp10")
        ]
    else: # Prise sous-marine et flux conducteur
        questions_sources_tp = [
            {"id": "m9_s1", "q": "Pourquoi l'eau de mer refroidit-elle si rapidement les parois extérieures du bloc ?", "options": ["Car elle possède une gigantesque capacité thermique massique", "Car elle est un isolant parfait", "Car elle subit une solidification instantanée"], "rep": "Car elle possède une gigantesque capacité thermique massique"},
            {"id": "m9_s2", "q": "L'océan absorbant le flux thermique sans monter en température se comporte comme :", "options": ["Un puits thermique infini", "Une source exothermique", "Un calorimètre isolé"], "rep": "Un puits thermique infini"},
            {"id": "m9_s3", "q": "Comment qualifie-t-on le flux de chaleur cédé par la paroi du béton à l'eau en mouvement ?", "options": ["Un flux convectif et conducteur", "Un rayonnement ultraviolet", "Une transition de phase latente"], "rep": "Un flux convectif et conducteur"},
            {"id": "m9_s4", "q": "Quel impact majeur un refroidissement sous-marin trop rapide a-t-il sur le jeune béton ?", "options": ["Il ralentit ou bloque la cinétique chimique de prise", "Il augmente sa résistance au cœur", "Il annule l'exothermie"], "rep": "Il ralentit ou bloque la cinétique chimique de prise"},
            {"id": "m9_s5", "q": "Quel adjuvant permet de contrer ce pillage calorifique en accélérant le durcissement ?", "options": ["Un accélérateur de prise", "Un retardateur de prise", "Un entraîneur d'air"], "rep": "Un accélérateur de prise"},
            {"id": "m9_s6", "q": "L'unité réglementaire du flux thermique total dissipé dans la mer est :", "options": ["Le Watt (W)", "Le Joule (J)", "Le Kelvin (K)"], "rep": "Le Watt (W)"},
            {"id": "m9_s7", "q": "La chaleur libérée par le ciment au cœur du massif immergé augmente sa chaleur :", "options": ["Sensible", "Latente de fusion", "Latente de vaporisation"], "rep": "Sensible"},
            {"id": "m9_s8", "q": "La vitesse à laquelle les calories migrent du cœur chaud vers la face immergée dépend de la :", "options": ["Conductivité thermique lambda du béton", "Salinité de l'eau de mer", "Viscosité du fluide"], "rep": "Conductivité thermique lambda du béton"},
            {"id": "m9_s9", "q": "Quelle formule permet d'évaluer la puissance thermique instantanée perdue dans l'eau ?", "options": ["Phi = U.A.dT", "Phi = m.c.dT", "Phi = e / lambda"], "rep": "Phi = U.A.dT"},
            {"id": "m9_s10", "q": "Le contrôle de l'homogénéité du durcissement des fondations maritimes est un diagnostic :", "options": ["Non destructif", "Curatif d'urgence", "Correctif"], "rep": "Non destructif"}
        ]
        trous_sources_tp = [
            ("1. L'eau de mer se comporte comme un .......... thermique infini face au bloc chaud.", ["Choisir...", "puits", "source"], "puits", "therm10_tp1"),
            ("2. Cela découle de sa gigantesque .......... thermique massique.", ["Choisir...", "capacité", "conductivité"], "capacité", "therm10_tp2"),
            ("3. Le fluide en mouvement absorbe l'énergie de surface par ..........", ["Choisir...", "convection", "sublimation"], "convection", "therm10_tp3"),
            ("4. Ce pillage de calories perturbe la cinétique de la .......... chimique du ciment.", ["Choisir...", "réaction", "fusion"], "réaction", "therm10_tp4"),
            ("5. Les calories se déplacent au sein du massif par .......... unitaire.", ["Choisir...", "conduction", "changement d'état"], "conduction", "therm10_tp5"),
            ("6. Pour contrer ce flux perdu, on intègre un adjuvant .......... de prise au malaxage.", ["Choisir...", "accélérateur", "retardateur"], "accélérateur", "therm10_tp6"),
            ("7. La chaleur issue de l'exothermie fait monter la chaleur .......... interne.", ["Choisir...", "sensible", "latente"], "sensible", "therm10_tp7"),
            ("8. La puissance thermique instantanée transmise à l'océan se comptabilise en ..........", ["Choisir...", "Watts", "Joules"], "Watts", "therm10_tp8"),
            ("9. La vitesse de transfert interne est dictée par la conductivité .......... du béton.", ["Choisir...", "lambda", "R"], "lambda", "therm10_tp9"),
            ("10. Ce suivi garantit la parfaite cristallisation des fondations du .......... d'art.", ["Choisir...", "ouvrage", "sol"], "ouvrage", "therm10_tp10")
        ]

    # Sécurisation du stockage technique dans la session pour l'évaluation active
    if "ordre_quiz_tab10_tp_aleatoire" not in st.session_state:
        st.session_state.ordre_quiz_tab10_tp_aleatoire = questions_sources_tp
    if "champs_therm10_tp_clean" not in st.session_state:
        st.session_state.champs_therm10_tp_clean = trous_sources_tp

    # Rendu des deux colonnes d'évaluation Streamlit
    col_q_tp, col_t_tp = st.columns(2)
    with col_q_tp:
        st.markdown("##### Quiz Spécifique au Scénario TP (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab10_tp_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"therm_at10_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_t_tp:
        st.markdown("##### Synthèse de l'Atelier 10 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm10_tp_clean:
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_therm10_tp_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_maintenance_dynamique(scenario_actif, verrouille=False):
    import random

    # =============================================================================
    # ADAPTATION DYNAMIQUE DES QUESTIONS SELON LE SCÉNARIO DE MAINTENANCE ACTIVE
    # =============================================================================
    if scenario_actif == "Électricité : Surchauffe de discontacteur":
        questions_sources = [
            {"id": "m9_e1", "q": "Quel effet physique produit un dégagement de chaleur lors du passage d'un courant dans une résistance ?", "options": ["L'effet Joule", "L'effet Fourier", "L'effet Seebeck"], "rep": "L'effet Joule"},
            {"id": "m9_e2", "q": "Quelle formule régit la puissance dissipée dans une borne défectueuse de résistance R ?", "options": ["P = R.I²", "P = U / I", "P = R.I"], "rep": "P = R.I²"},
            {"id": "m9_e3", "q": "Quelle anomalie mécanique sur une borne électrique provoque l'augmentation de la résistance de contact ?", "options": ["Le desserrage des vis de fixation", "Un serrage trop puissant", "La présence de graisse conductrice"], "rep": "Le desserrage des vis de fixation"},
            {"id": "m9_e4", "q": "Quelle valeur limite de température ne doit pas être franchie sur un raccordement en cuivre ?", "options": ["80 °C", "35 °C", "150 °C"], "rep": "80 °C"},
            {"id": "m9_e5", "q": "Quelle action de maintenance permet d'éliminer définitivement ce type de point chaud ?", "options": ["Le resserrage au couple des connexions", "L'augmentation de la ventilation", "Le remplacement du disjoncteur"], "rep": "Le resserrage au couple des connexions"},
            {"id": "m9_e6", "q": "Si l'intensité du courant électrique est multipliée par deux, la puissance dissipée est :", "options": ["Multipliée par quatre", "Doublée", "Divisée par deux"], "rep": "Multipliée par quatre"},
            {"id": "m9_e7", "q": "La thermographie infrarouge capte des ondes lumineuses qui sont :", "options": ["Invisibles à l'œil nu", "Visibles au microscope", "Des rayons ultraviolets"], "rep": "Invisibles à l'œil nu"},
            {"id": "m9_e8", "q": "Un point chaud permanent non traité dans une armoire présente un risque majeur de :", "options": ["Départ d'incendie", "Surtension atmosphérique", "Baisse de tension immédiate"], "rep": "Départ d'incendie"},
            {"id": "m9_e9", "q": "Le diagnostic thermique réalisé avant toute panne s'inscrit dans la maintenance :", "options": ["Préventive conditionnelle", "Curative urgente", "Corrective différée"], "rep": "Préventive conditionnelle"},
            {"id": "m9_e10", "q": "Quel paramètre de l'image thermographique indique la sévérité du défaut de serrage ?", "options": ["L'écart de température avec les phases saines", "La taille physique du bouton", "La marque de la caméra"], "rep": "L'écart de température avec les phases saines"}
        ]
        trous_sources = [
            ("1. Le desserrage d'une borne crée une .......... de contact anormale.", ["Choisir...", "résistance", "conductivité"], "résistance", "therm9_m1"),
            ("2. Le dégagement de chaleur induit par le courant répond à l'effet ..........", ["Choisir...", "Joule", "Fourier"], "Joule", "therm9_m2"),
            ("3. La puissance thermique évolue proportionnellement au .......... de l'intensité.", ["Choisir...", "carré", "double"], "carré", "therm9_m3"),
            ("4. La caméra thermique intercepte le rayonnement .......... émis par la borne.", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "therm9_m4"),
            ("5. Un raccordement défectueux se traduit à l'écran par un .......... chaud.", ["Choisir...", "point", "palier"], "point", "therm9_m5"),
            ("6. Traiter ce problème avant la rupture s'appelle la maintenance ..........", ["Choisir...", "préventive", "curative"], "préventive", "therm9_m6"),
            ("7. Le resserrage des bornes permet de faire .......... la température du contact.", ["Choisir...", "chuter", "monter"], "chuter", "therm9_m7"),
            ("8. Le seuil critique pour une connexion électrique courante est fixé à .......... °C.", ["Choisir...", "80", "40"], "80", "therm9_m8"),
            ("9. L'échauffement non maîtrisé engendre un risque d'.......... de l'armoire.", ["Choisir...", "incendie", "surtension"], "incendie", "therm9_m9"),
            ("10. La thermographie est un outil d'inspection non .......... très performant.", ["Choisir...", "destructif", "conforme"], "destructif", "therm9_m10")
        ]
    elif scenario_actif == "Mécanique : Échauffement de roulement":
        questions_sources = [
            {"id": "m9_m1", "q": "Quelle est la cause primaire de l'échauffement de ce composant ?", "options": ["Le frottement par manque de lubrification", "Une vitesse excessive du vent", "Une conductivité trop élevée"], "rep": "Le frottement par manque de lubrification"},
            {"id": "m9_m2", "q": "La transformation de l'énergie mécanique en chaleur au niveau des billes est un transfert par :", "options": ["Friction cinétique", "Rayonnement pur", "Chaleur latente"], "rep": "Friction cinétique"},
            {"id": "m9_m3", "q": "Quel composant d'étanchéité défaillant provoque généralement la fuite de la graisse ?", "options": ["Le joint à lèvre", "La bague interne", "La cage de maintien"], "rep": "Le joint à lèvre"},
            {"id": "m9_m4", "q": "Quelle opération de maintenance mécanique permet de recréer le film protecteur ?", "options": ["Le graissage périodique", "Le lavage à haute pression", "La mise en peinture"], "rep": "Le graissage périodique"},
            {"id": "m9_m5", "q": "Si le corps métallique atteint 95 °C en fonctionnement stabilisé, la situation est :", "options": ["Une anomalie critique", "Un fonctionnement normal", "Un sous-régime thermique"], "rep": "Une anomalie critique"},
            {"id": "m9_m6", "q": "L'élévation thermique d'un palier mécanique est mesurable sans contact par :", "options": ["Une caméra infrarouge", "Un manomètre de pression", "Un anémomètre"], "rep": "Une caméra infrarouge"},
            {"id": "m9_m7", "q": "Le phénomène destructeur provoqué par le blocage des billes surchauffées s'appelle :", "options": ["Le grippage mécanique", "L'embouage sédimentaire", "La condensation"], "rep": "Le grippage mécanique"},
            {"id": "m9_m8", "q": "Suivre l'évolution thermique du boîtier pour planifier l'arrêt d'usine relève de la maintenance :", "options": ["Prédictive", "Curative d'urgence", "Corrective fortuite"], "rep": "Prédictive"},
            {"id": "m9_m9", "q": "La conductivité thermique de l'acier favorise la migration de la chaleur vers :", "options": ["Le corps externe du palier", "L'axe central creux", "Les pales du ventilateur"], "rep": "Le corps externe du palier"},
            {"id": "m9_m10", "q": "Quel est le risque ultime si l'échauffement du roulement mécanique est ignoré ?", "options": ["La casse de l'arbre par blocage net", "Une augmentation du rendement", "Une baisse des frottements"], "rep": "La casse de l'arbre par blocage net"}
        ]
        trous_sources = [
            ("1. La perte de graisse engendre un .......... intense entre les billes d'acier.", ["Choisir...", "frottement", "glissement"], "frottement", "therm9_m1"),
            ("2. L'énergie mécanique se convertit en un flux de .......... parasite.", ["Choisir...", "chaleur", "tension"], "chaleur", "therm9_m2"),
            ("3. La défaillance structurelle du .......... provoque la fuite de lubrifiant.", ["Choisir...", "joint", "carter"], "joint", "therm9_m3"),
            ("4. Cette surchauffe localisée est visible via la thermographie ..........", ["Choisir...", "infrarouge", "visuelle"], "infrarouge", "therm9_m4"),
            ("5. Le manque de graisse présente un risque immédiat de .......... de l'arbre.", ["Choisir...", "grippage", "lavage"], "grippage", "therm9_m5"),
            ("6. Surveiller la dérive de température qualifie la maintenance ..........", ["Choisir...", "prédictive", "curative"], "prédictive", "therm9_m6"),
            ("7. Ajouter un fluide .......... permet de restaurer le film de protection.", ["Choisir...", "lubrifiant", "isolant"], "lubrifiant", "therm9_m7"),
            ("8. Une valeur stabilisée à 95 °C constitue un signal .......... pour l'organe.", ["Choisir...", "critique", "conforme"], "critique", "therm9_m8"),
            ("9. Les calories se déplacent au sein des bagues par .......... thermique.", ["Choisir...", "conduction", "convection"], "conduction", "therm9_m9"),
            ("10. Ce contrôle évite la rupture .......... de l'ensemble de la transmission.", ["Choisir...", "brutale", "programmée"], "brutale", "therm9_m10")
        ]
    elif scenario_actif == "Réseaux : Dysfonctionnement de purgeur vapeur":
        questions_sources = [
            {"id": "m9_v1", "q": "Quelle anomalie thermographique caractérise un purgeur vapeur bloqué ouvert ?", "options": ["L'absence de saut thermique amont/aval", "Un refroidissement complet de l'organe", "Un givrage de surface"], "rep": "L'absence de saut thermique amont/aval"},
            {"id": "m9_v2", "q": "Quelle forme d'énergie s'échappe en masse lors de la fuite directe de vapeur ?", "options": ["La chaleur latente de vaporisation", "La chaleur sensible de fusion", "L'énergie potentielle"], "rep": "La chaleur latente de vaporisation"},
            {"id": "m9_v3", "q": "La valeur nominale de la chaleur latente de vaporisation de l'eau pure est de :", "options": ["2 260 kJ/kg", "334 kJ/kg", "4180 J/kg"], "rep": "2 260 kJ/kg"},
            {"id": "m9_v4", "q": "Quel est le rôle principal d'un purgeur fonctionnel sur un réseau de vapeur ?", "options": ["Évacuer les condensats et piéger la vapeur", "Augmenter la pression du gaz", "Chauffer les canalisations"], "rep": "Évacuer les condensats et piéger la vapeur"},
            {"id": "m9_v5", "q": "Une fuite de vapeur prolongée engendre directement à la chaudière :", "options": ["Une surconsommation massive de combustible", "Une augmentation du rendement global", "Une baisse du débit d'eau"], "rep": "Une surconsommation massive de combustible"},
            {"id": "m9_v6", "q": "Le transfert thermique perdu à travers le panache de vapeur s'effectue par :", "options": ["Convection et changement d'état", "Conduction métallique pure", "Rayonnement laser"], "rep": "Convection et changement d'état"},
            {"id": "m9_v7", "q": "Comment l'opérateur valide-t-on l'efficacité du remplacement du purgeur ?", "options": ["En mesurant le rétablissement de l'écart thermique", "En comptant le nombre de vis", "En coupant définitivement l'eau"], "rep": "En mesurant le rétablissement de l'écart thermique"},
            {"id": "m9_v8", "q": "La comptabilisation des pertes énergétiques sur 24 heures s'exprime en :", "options": ["kWatts-heures (kWh)", "Watts par seconde", "Joules par Kelvin"], "rep": "kWatts-heures (kWh)"},
            {"id": "m9_v9", "q": "Le contrôle non destructif des purgeurs par ultrasons ou infrarouge relève de la :", "options": ["Maintenance préventive", "Maintenance curative tardive", "Maintenance corrective différée"], "rep": "Maintenance préventive"},
            {"id": "m9_v10", "q": "Un purgeur bloqué fermé (bloquant les condensats) provoquerait en amont :", "options": ["Un refroidissement de la ligne et des coups de bélier", "Une hausse de température", "Une vaporisation instantanée"], "rep": "Un refroidissement de la ligne et des coups de bélier"}
        ]
        trous_sources = [
            ("1. Un purgeur défaillant laisse échapper la .......... calorifique en continu.", ["Choisir...", "vapeur", "eau"], "vapeur", "therm9_m1"),
            ("2. Le gaz emporte avec lui sa chaleur .......... de vaporisation colossale.", ["Choisir...", "latente", "sensible"], "latente", "therm9_m2"),
            ("3. La constante Lv pour l'eau pure s'élève à .......... kJ/kg.", ["Choisir...", "2260", "334"], "2260", "therm9_m3"),
            ("4. L'absence d'écart de température indique que le clapet reste ..........", ["Choisir...", "ouvert", "fermé"], "ouvert", "therm9_m4"),
            ("5. La détection du dysfonctionnement se fait par caméra .......... sans contact.", ["Choisir...", "thermique", "optique"], "thermique", "therm9_m5"),
            ("6. Le gaspillage de fluide engendre une surconsommation de ..........", ["Choisir...", "combustible", "matière"], "combustible", "therm9_m6"),
            ("7. Remplacer la cartouche permet de bloquer et .......... l'énergie en amont.", ["Choisir...", "conserver", "dissiper"], "conserver", "therm9_m7"),
            ("8. L'évaluation des pertes journalières se calcule sur une durée de .......... heures.", ["Choisir...", "24", "12"], "24", "therm9_m8"),
            ("9. Inspecter les réseaux thermiques sans démontage est un diagnostic non ..........", ["Choisir...", "destructif", "isolant"], "destructif", "therm9_m9"),
            ("10. Un purgeur sain doit obligatoirement piéger la vapeur et évacuer l'.......... liquide.", ["Choisir...", "eau", "air"], "eau", "therm9_m10")
        ]
    else:  # Embouage de radiateur central
        questions_sources = [
            {"id": "m9_r1", "q": "Quel sédiment obstrue la circulation interne des réseaux de chauffage ?", "options": ["Les boues d'oxydes métalliques", "Le calcaire de tartre pur", "Des résidus de graisse liquide"], "rep": "Les boues d'oxydes métalliques"},
            {"id": "m9_r2", "q": "Quel impact physique direct l'accumulation de boues a-t-elle sur la paroi ?", "options": ["Elle crée une résistance thermique parasite", "Elle augmente le coefficient U", "Elle annule l'épaisseur"], "rep": "Elle crée une résistance thermique parasite"},
            {"id": "m9_r3", "q": "Quelle signature visuelle révèle un radiateur emboué à la caméra thermique ?", "options": ["Un haut chaud et un bas totalement froid", "Une surface uniformément brûlante", "Un gradient horizontal parfait"], "rep": "Un haut chaud et un bas totalement froid"},
            {"id": "m9_r4", "q": "L'encrassement interne provoque l'effondrement de quel coefficient global ?", "options": ["Le coefficient de transmission U", "La conductivité lambda du fluide", "L'émissivité radiative"], "rep": "Le coefficient de transmission U"},
            {"id": "m9_r5", "q": "L'opération technique consistant à nettoyer et rincer le circuit s'appelle :", "options": ["Le désembouage hydrodynamique", "Le calorifugeage des tubes", "La purge d'air"], "rep": "Le désembouage hydrodynamique"},
            {"id": "m9_r6", "q": "La réduction de la zone d'échange active du radiateur dégrade le transfert par :", "options": ["Convection et rayonnement", "Conduction solide pure", "Changement d'état latent"], "rep": "Convection et rayonnement"},
            {"id": "m9_r7", "q": "Les dépôts de boues métalliques s'accumulent prioritairement dans quelle zone ?", "options": ["La partie inférieure (le fond)", "La vanne d'entrée haute", "Le purgeur d'air"], "rep": "La partie inférieure (le fond)"},
            {"id": "m9_r8", "q": "Un radiateur emboué induit directement pour les occupants de la pièce :", "options": ["Une perte de confort par baisse de puissance émise", "Une surchauffe spontanée", "Une émanation de gaz"], "rep": "Une perte de confort par baisse de puissance émise"},
            {"id": "m9_r9", "q": "Quelle est l'unité légale du coefficient de transmission U impacté par la boue ?", "options": ["W/(m².K)", "W/(m.K)", "Joule/kg"], "rep": "W/(m².K)"},
            {"id": "m9_r10", "q": "Vérifier la bonne répartition de la chaleur sur les parois s'inscrit dans la maintenance :", "options": ["Préventive", "Curative urgente", "Corrective fortuite"], "rep": "Préventive"}
        ]
        trous_sources = [
            ("1. L'accumulation d'oxydes crée des .......... au fond du corps de chauffe.", ["Choisir...", "boues", "bulles"], "boues", "therm9_m1"),
            ("2. Ce dépôt sédimentaire agit comme un .......... thermique parasite.", ["Choisir...", "isolant", "conducteur"], "isolant", "therm9_m2"),
            ("3. La présence de boue fait augmenter la .......... globale du composant.", ["Choisir...", "résistance", "conductivité"], "résistance", "therm9_m3"),
            ("4. En conséquence, le coefficient de transmission .......... U s'effondre.", ["Choisir...", "global", "unitaire"], "global", "therm9_m4"),
            ("5. La caméra thermique met en relief un défaut d'.......... de surface.", ["Choisir...", "homogénéité", "conduction"], "homogénéité", "therm9_m5"),
            ("6. Le bas du radiateur reste .......... en raison du manque de débit d'eau.", ["Choisir...", "froid", "chaud"], "froid", "therm9_m6"),
            ("7. La pompe de nettoyage effectue un .......... complet du réseau de tubes.", ["Choisir...", "désembouage", "calorifugeage"], "désembouage", "therm9_m7"),
            ("8. L'évacuation des sédiments permet de libérer la surface d'.......... active.", ["Choisir...", "échange", "conduction"], "échange", "therm9_m8"),
            ("9. Le radiateur retrouve ainsi son émission nominale exprimée en ..........", ["Choisir...", "Watts", "Joules"], "Watts", "therm9_m9"),
            ("10. Ce type de diagnostic infrarouge planifié relève de la maintenance ..........", ["Choisir...", "préventive", "curative"], "préventive", "therm9_m10")
        ]

    # Sécurisation du stockage dans la session pour l'évaluation active
    if "ordre_quiz_tab9_maint_aleatoire" not in st.session_state:
        st.session_state.ordre_quiz_tab9_maint_aleatoire = questions_sources
    if "champs_therm9_maint_clean" not in st.session_state:
        st.session_state.champs_therm9_maint_clean = trous_sources

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab9_maint_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"therm_at9_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 9 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm9_maint_clean:
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_therm9_maint_clean", disabled=verrouille, label_visibility="collapsed")






def afficher_atelier_monocouche_verrouille(verrouille=False):
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE DE L'ATELIER 9
    questions_therm9_sources = [
        {"id": "qt9_1", "q": "Quelle loi physique fondamentale régit le transfert de chaleur par conduction à travers une paroi ?", "options": ["La loi de Fourier", "La loi de Newton", "La loi de Stefan"], "rep": "La loi de Fourier"},
        {"id": "qt9_2", "q": "Comment évolue le flux thermique traversant si l'on double la surface de la paroi simple ?", "options": ["Il est doublé", "Il est divisé par deux", "Il reste identique"], "rep": "Il est doublé"},
        {"id": "qt9_3", "q": "Quelle est l'unité de mesure du flux thermique total dans le Système International ?", "options": ["Le Watt", "Le Joule", "Le Pascal"], "rep": "Le Watt"},
        {"id": "qt9_4", "q": "Comment varie l'évolution de la température à l'intérieur d'un matériau unique et homogène ?", "options": ["De façon linéaire et rectiligne", "De façon parabolique", "Par paliers horizontaux successifs"], "rep": "De façon linéaire et rectiligne"},
        {"id": "qt9_5", "q": "Si l'on multiplie l'épaisseur d'une paroi homogène par deux, qu'advient-il du flux perdu ?", "options": ["Il est divisé par deux", "Il est multiplié par deux", "Il augmente au carré"], "rep": "Il est divisé par deux"},
        {"id": "qt9_6", "q": "Dans l'équation de la conduction unitaire, que représente le terme désigné par la lettre 'A' ?", "options": ["La surface d'échange en m²", "L'épaisseur de la paroi", "L'écart thermique"], "rep": "La surface d'échange en m²"},
        {"id": "qt9_7", "q": "Quel paramètre se trouve au dénominateur dans l'expression littérale du flux conducteur unitaire ?", "options": ["L'épaisseur de la couche (e)", "La conductivité (lambda)", "La surface (A)"], "rep": "L'épaisseur de la couche (e)"},
        {"id": "qt9_8", "q": "Si la pente du profil de température dans le mur est forte, cela signifie que le matériau est :", "options": ["Peu conducteur (Plutôt isolant)", "Extrêmement conducteur", "Un métal pur"], "rep": "Peu conducteur (Plutôt isolant)"},
        {"id": "qt9_9", "q": "Le flux thermique se déplace spontanément depuis :", "options": ["La face la plus chaude vers la face la plus froide", "La face froide vers la face chaude", "Le milieu extérieur vers l'intérieur"], "rep": "La face la plus chaude vers la face la plus froide"},
        {"id": "qt10_10", "q": "Pour calculer le flux à travers une paroi simple, la formule correcte à appliquer est :", "options": ["Phi = (lambda * A * dT) / e", "Phi = (e * A * dT) / lambda", "Phi = lambda * e * A * dT"], "rep": "Phi = (lambda * A * dT) / e"}
    ]

    if "ordre_quiz_tab9_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm9_sources)
        st.session_state.ordre_quiz_tab9_therm_aleatoire = questions_therm9_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DE L'ATELIER 9
    if "champs_therm9_clean" not in st.session_state:
        st.session_state.champs_therm9_clean = [
            ("1. Le transfert conducteur à travers un matériau unitaire suit la loi de ..........", ["Choisir...", "Fourier", "Newton"], "Fourier", "therm9_t1"),
            ("2. Le flux thermique total traversant une paroi plane s'exprime en ..........", ["Choisir...", "Watts", "Joules"], "Watts", "therm9_t2"),
            ("3. À l'intérieur d'un seul matériau homogène, le profil thermique est ..........", ["Choisir...", "linéaire", "courbe"], "linéaire", "therm9_t3"),
            ("4. Doubler la surface de la paroi monocouche conduit à un flux thermique ..........", ["Choisir...", "doublé", "diminué"], "doublé", "therm9_t4"),
            ("5. Le flux est inversement proportionnel à l'.......... de la paroi étudiée.", ["Choisir...", "épaisseur", "surface"], "épaisseur", "therm9_t5"),
            ("6. La chaleur se propage toujours de la face la plus .......... vers la plus froide.", ["Choisir...", "chaude", "froide"], "chaude", "therm9_t6"),
            ("7. Dans la formule littérale, la constante lambda désigne la .......... thermique.", ["Choisir...", "conductivité", "résistance"], "conductivité", "therm9_t7"),
            ("8. Augmenter l'épaisseur du matériau permet d'accroître la résistance ..........", ["Choisir...", "R", "U"], "R", "therm9_t8"),
            ("9. Une forte pente de température traduit un matériau plutôt ..........", ["Choisir...", "isolant", "conducteur"], "isolant", "therm9_t9"),
            ("10. Si l'écart thermique dT augmente, les déperditions totales de Watts ..........", ["Choisir...", "augmentent", "diminuent"], "augmentent", "therm9_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 9 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab9_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"therm_at9_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 9 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm9_clean:
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_therm9_clean", disabled=verrouille, label_visibility="collapsed")



def afficher_atelier_transmission_verrouille(verrouille=False):
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE DU COEFFICIENT U
    questions_therm7_sources = [
        {"id": "qt7_1", "q": "Quelle lettre majuscule désigne le coefficient de transmission thermique global ?", "options": ["U", "R", "K"], "rep": "U"},
        {"id": "qt7_2", "q": "Quelle est l'unité légale du coefficient de transmission thermique globale dans le SI ?", "options": ["W/(m².K)", "W/(m.K)", "J/kg"], "rep": "W/(m².K)"},
        {"id": "qt7_3", "q": "Comment évolue la valeur du coefficient U d'une paroi si l'on augmente son isolation ?", "options": ["Elle diminue", "Elle augmente", "Elle reste inchangée"], "rep": "Elle diminue"},
        {"id": "qt7_4", "q": "Quelle relation lie mathématiquement le coefficient U à la résistance thermique totale R ?", "options": ["U = 1 / R", "U = R * e", "U = lambda / R"], "rep": "U = 1 / R"},
        {"id": "qt7_5", "q": "Pour concevoir un bâtiment performant de type passif, que doit viser la valeur du coefficient U ?", "options": ["Une valeur la plus faible possible proche de zéro", "Une valeur supérieure à 5", "Une valeur identique à celle du cuivre"], "rep": "Une valeur la plus faible possible proche de zéro"},
        {"id": "qt7_6", "q": "Quel vitrage possède le coefficient de transmission thermique U le plus catastrophique (le plus élevé) ?", "options": ["Le simple vitrage de 4 mm", "Le double vitrage Argon", "Le triple vitrage isolant"], "rep": "Le simple vitrage de 4 mm"},
        {"id": "qt7_7", "q": "Si le coefficient U d'une paroi vaut 2 W/(m².K) et que dT = 10°C, quel est le flux perdu par m² ?", "options": ["20 W/m²", "5 W/m²", "0,2 W/m²"], "rep": "20 W/m²"},
        {"id": "qt7_8", "q": "La formule du coefficient de transmission thermique U pour une paroi simple s'exprime par :", "options": ["U = lambda / e", "U = e / lambda", "U = 1 / lambda"], "rep": "U = lambda / e"},
        {"id": "qt7_9", "q": "Quel appareil de mesure permet de visualiser à distance les déperditions liées à un fort coefficient U ?", "options": ["Une caméra thermique infrarouge", "Un manomètre différentiel", "Un pyromètre optique"], "rep": "Une caméra thermique infrarouge"},
        {"id": "qt7_10", "q": "Quel phénomène inconfortable de surface apparaît en hiver sur un mur ayant un fort coefficient U ?", "options": ["Le phénomène de paroi froide et de condensation", "Une surchauffe spontanée", "Une émission d'ondes de rayonnement ultraviolet"], "rep": "Le phénomène de paroi froide et de condensation"}
    ]

    if "ordre_quiz_tab7_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm7_sources)
        st.session_state.ordre_quiz_tab7_therm_aleatoire = questions_therm7_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DU COEFFICIENT U
    if "champs_therm7_clean" not in st.session_state:
        st.session_state.champs_therm7_clean = [
            ("1. Le coefficient de transmission thermique global se note avec la lettre ..........", ["Choisir...", "U", "R"], "U", "therm7_t1"),
            ("2. L'unité légale du coefficient de transmission s'exprime en W/(m²...........).", ["Choisir...", "K", "J"], "K", "therm7_t2"),
            ("3. Le coefficient U est inversement proportionnel à la .......... thermique totale.", ["Choisir...", "résistance", "surface"], "résistance", "therm7_t3"),
            ("4. Un bâtiment hautement isolé possède des parois avec un U très ..........", ["Choisir...", "faible", "élevé"], "faible", "therm7_t4"),
            ("5. La formule analytique pour calculer une paroi monocouche est U = .......... / e.", ["Choisir...", "lambda", "R"], "lambda", "therm7_t5"),
            ("6. Une vieille fenêtre simple vitrage engendre des déperditions de chaleur ..........", ["Choisir...", "élevées", "nulles"], "élevées", "therm7_t6"),
            ("7. Réduire la valeur du coefficient U permet de bloquer le .......... perdu.", ["Choisir...", "flux", "volume"], "flux", "therm7_t7"),
            ("8. Multiplier l'épaisseur d'isolant par deux permet de diviser par deux le coefficient ..........", ["Choisir...", "U", "R"], "U", "therm7_t8"),
            ("9. Le béton banché nu présente une valeur de transmission thermique très ..........", ["Choisir...", "élevée", "basse"], "élevée", "therm7_t9"),
            ("10. La réglementation environnementale RE2020 impose de limiter le coefficient ..........", ["Choisir...", "U", "lambda"], "U", "therm7_t10")
        ]

    # 3. RENDU DES DEUX COLONNES D'ÉVALUATION STREAMLIT
    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 7 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab7_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox("", options=["Choisir..."] + q_data["options"], key=f"therm_at7_final_g_{q_data['id']}", disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 7 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm7_clean:
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=f"{cle}_therm7_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_quantite_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 6 (La quantité de chaleur) sur deux colonnes."""
    import random

    # # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE DE LA QUANTITÉ DE CHALEUR
    questions_therm6_sources = [
        {
            "id": "qt6_1", 
            "q": "Quelle lettre majuscule symbolise la quantité de chaleur échangée ?", 
            "options": ["Q", "W", "C"], 
            "rep": "Q"
        },
        {
            "id": "qt6_2", 
            "q": "Dans l'équation calorimétrique sensible, quel terme représente l'écart de température (Tf - Ti) ?", 
            "options": ["Delta T (ΔT)", "Lambda (λ)", "Alpha (α)"], 
            "rep": "Delta T (ΔT)"
        },
        {
            "id": "qt6_3", 
            "q": "Quelle unité du Système International mesure de façon réglementaire la quantité de chaleur ?", 
            "options": ["Le Joule", "La calorie", "Le Watt"], 
            "rep": "Le Joule"
        },
        {
            "id": "qt6_4", 
            "q": "Comment appelle-t-on l'énergie thermique mise en jeu lors d'une simple variation de température sans transition de phase ?", 
            "options": ["La chaleur sensible", "La chaleur latente", "Le flux conducteur"], 
            "rep": "La chaleur sensible"
        },
        {
            "id": "qt6_5", 
            "q": "Quelle est la valeur approximative de la capacité thermique massique de l'eau liquide pure ?", 
            "options": ["4 180 J/(kg.K)", "1 500 J/(kg.K)", "130 J/(kg.K)"], 
            "rep": "4 180 J/(kg.K)"
        },
        {
            "id": "qt6_6", 
            "q": "Si un corps solide cède de la chaleur à son environnement, que fait sa température ?", 
            "options": ["Elle diminue obligatoirement", "Elle augmente fortement", "Elle reste strictement constante"], 
            "rep": "Elle diminue obligatoirement"
        },
        {
            "id": "qt6_7", 
            "q": "Quelle unité exprime la capacité thermique massique 'c' d'un corps ?", 
            "options": ["J/(kg.K)", "J/kg", "Watt/m²"], 
            "rep": "J/(kg.K)"
        },
        {
            "id": "qt6_8", 
            "q": "Parmi ces corps, lequel possède la plus petite capacité thermique massique, surchauffant au moindre apport ?", 
            "options": ["Le plomb massif", "L'eau pure", "L'huile de cuisine"], 
            "rep": "Le plomb massif"
        },
        {
            "id": "qt6_9", 
            "q": "Si l'on multiplie la masse d'un corps par deux, l'énergie nécessaire pour le chauffer d'un même écart est :", 
            "options": ["Doublée", "Divisée par deux", "Strictement identique"], 
            "rep": "Doublée"
        },
        {
            "id": "qt6_10", 
            "q": "L'appareil de laboratoire isolé thermiquement qui sert à mesurer ces transferts de chaleur est :", 
            "options": ["Un calorimètre", "Un manomètre", "Un thermocouple"], 
            "rep": "Un calorimètre"
        }
    ]

    if "ordre_quiz_tab6_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm6_sources)
        st.session_state.ordre_quiz_tab6_therm_aleatoire = questions_therm6_sources

    # # 2. BASE DE DONNÉES DU TEXTE À TROUS DE LA QUANTITÉ DE CHALEUR
    if "champs_therm6_clean" not in st.session_state:
        st.session_state.champs_therm6_clean = [
            ("1. La quantité de chaleur sensible est symbolisée par la lettre majuscule ..........", ["Choisir...", "Q", "T"], "Q", "therm6_t1"),
            ("2. L'unité officielle de l'énergie thermique et de la chaleur est le ..........", ["Choisir...", "Joule", "Watt"], "Joule", "therm6_t2"),
            ("3. Le chauffage d'un corps sans changement d'état mobilise de la chaleur ..........", ["Choisir...", "sensible", "latente"], "sensible", "therm6_t3"),
            ("4. L'eau possède une .......... thermique massique extrêmement élevée de 4180 J/(kg.K).", ["Choisir...", "capacité", "conductivité"], "capacité", "therm6_t4"),
            ("5. Le terme .......... T correspond à la soustraction de la température finale et initiale.", ["Choisir...", "Delta", "Alpha"], "Delta", "therm6_t5"),
            ("6. Les métaux ont une capacité thermique très .......... et chauffent donc très vite.", ["Choisir...", "faible", "élevée"], "faible", "therm6_t6"),
            ("7. Un corps qui se refroidit en cédant de l'énergie possède un signe Q ..........", ["Choisir...", "négatif", "positif"], "négatif", "therm6_t7"),
            ("8. L'unité de la constante de capacité massique se note J/(kg...........).", ["Choisir...", "K", "W"], "K", "therm6_t8"),
            ("9. Un doublement de la masse à chauffer implique une quantité de chaleur ..........", ["Choisir...", "doublée", "inchangée"], "doublée", "therm6_t9"),
            ("10. Les mesures expérimentales de chaleurs s'effectuent dans un .......... de laboratoire.", ["Choisir...", "calorimètre", "thermomètre"], "calorimètre", "therm6_t10")
        ]

    # # 3. RENDU DES DEUX COLONNES D'ÉVALUATION STREAMLIT
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 6 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab6_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"therm_at6_final_g_{q_data['id']}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 6 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm6_clean:
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_therm6_clean", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )


def afficher_atelier_isolants_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 5 (Les conducteurs et les isolants) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE DES CONDUCTEURS ET ISOLANTS
    questions_therm5_sources = [
        {"id": "qt5_1", "q": "Quelle lettre de l'alphabet grec désigne la conductivité thermique d'un matériau ?", "options": ["Lambda (λ)", "Phi (Φ)", "Rho (ρ)"], "rep": "Lambda (λ)"},
        {"id": "qt5_2", "q": "Quelle est l'unité légale de la conductivité thermique dans le Système International ?", "options": ["W/(m.K)", "Joule/kg", "W/m²"], "rep": "W/(m.K)"},
        {"id": "qt5_3", "q": "Parmi les matériaux suivants, lequel possède la conductivité thermique la plus élevée ?", "options": ["Le cuivre", "Le verre", "Le bois"], "rep": "Le cuivre"},
        {"id": "qt5_4", "q": "Quelle est la valeur maximale limite du lambda pour qu'un matériau soit qualifié d'isolant thermique ?", "options": ["0,05 W/(m.K)", "1,0 W/(m.K)", "0,5 W/(m.K)"], "rep": "0,05 W/(m.K)"},
        {"id": "qt5_5", "q": "Quel élément immobile, prisonnier des fibres ou des alvéoles, fait le pouvoir des isolants ?", "options": ["L'air", "L'eau", "Le vide"], "rep": "L'air"},
        {"id": "qt5_6", "q": "Pourquoi les métaux sont-ils d'excellents conducteurs de chaleur ?", "options": ["En raison de la présence d'électrons libres", "Parce qu'ils ont une densité faible", "Parce qu'ils absorbent le rayonnement"], "rep": "En raison de la présence d'électrons libres"},
        {"id": "qt5_7", "q": "La laine de verre et le polystyrène expansé sont des matériaux dits :", "options": ["Isolants thermiques", "Conducteurs thermiques", "Réfractaires purs"], "rep": "Isolants thermiques"},
        {"id": "qt5_8", "q": "Si l'on double l'épaisseur d'un panneau isolant, qu'advient-il du flux de chaleur qui le traverse ?", "options": ["Il est divisé par deux", "Il est doublé", "Il reste strictement identique"], "rep": "Il est divisé par deux"},
        {"id": "qt5_9", "q": "Quel isolant thermique naturel d'origine végétale est couramment utilisé en panneaux rigides ?", "options": ["Le liège expansé", "La laine de verre", "Le béton cellulaire"], "rep": "Le liège expansé"},
        {"id": "qt5_10", "q": "Dans l'industrie, pour évacuer la chaleur d'un processeur, on utilise un dissipateur en :", "options": ["Aluminium", "Plastique PVC", "Bois de sapin"], "rep": "Aluminium"}
    ]

    if "ordre_quiz_tab5_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm5_sources)
        st.session_state.ordre_quiz_tab5_therm_aleatoire = questions_therm5_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DES CONDUCTEURS ET ISOLANTS
    if "champs_therm5_clean" not in st.session_state:
        st.session_state.champs_therm5_clean = [
            ("1. La conductivité thermique est désignée par la lettre grecque ..........", ["Choisir...", "lambda", "phi"], "lambda", "therm5_t1"),
            ("2. Les .......... possèdent une conductivité thermique élevée supérieure à 50 W/(m.K).", ["Choisir...", "métaux", "isolants"], "métaux", "therm5_t2"),
            ("3. Un matériau est un isolant si son lambda est inférieur à .......... W/(m.K).", ["Choisir...", "0,05", "1,5"], "0,05", "therm5_t3"),
            ("4. La laine de verre emprisonne de l'.......... immobile pour bloquer la conduction.", ["Choisir...", "air", "eau"], "air", "therm5_t4"),
            ("5. Plus la valeur du lambda est faible, plus le matériau est ..........", ["Choisir...", "isolant", "conducteur"], "isolant", "therm5_t5"),
            ("6. Le cuivre est un excellent .......... thermique utilisé dans les échangeurs.", ["Choisir...", "conducteur", "isolant"], "conducteur", "therm5_t6"),
            ("7. Augmenter l'.......... d'une paroi permet de réduire le flux de chaleur perdu.", ["Choisir...", "épaisseur", "surface"], "épaisseur", "therm5_t7"),
            ("8. L'unité de la conductivité thermique se note W/(m...........).", ["Choisir...", "K", "J"], "K", "therm5_t8"),
            ("9. Le polystyrène expansé est un isolant thermique d'origine ..........", ["Choisir...", "synthétique", "animale"], "synthétique", "therm5_t9"),
            ("10. Les électrons .......... permettent aux métaux de transmettre rapidement l'agitation.", ["Choisir...", "libres", "liés"], "libres", "therm5_t10")
        ]

    # 3. RENDU DES DEUX COLONNES D'ÉVALUATION STREAMLIT
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 5 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"therm_at5_final_g_{q_data['id']}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 5 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm5_clean:
            # Extraction explicite et sécurisée des 4 éléments du tuple pour éliminer le crash
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_therm5_clean", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )

def afficher_atelier_modes_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 4 (Les modes de transfert) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE DES MODES DE TRANSFERT
    questions_therm4_sources = [
        {"id": "qt4_1", "q": "Quel mode de transfert thermique se propage sans aucun déplacement macroscopique de matière au sein des solides ?", "options": ["La conduction", "La convection", "Le rayonnement"], "rep": "La conduction"},
        {"id": "qt4_2", "q": "Quel mécanisme de transfert de chaleur implique nécessairement un déplacement physique de matière fluide ?", "options": ["La convection", "La conduction", "Le rayonnement"], "rep": "La convection"},
        {"id": "qt4_3", "q": "Quel scientifique français a formalisé en 1822 les lois mathématiques régissant la conduction de la chaleur ?", "options": ["Joseph Fourier", "Sadi Carnot", "Antoine Lavoisier"], "rep": "Joseph Fourier"},
        {"id": "qt4_4", "q": "Quel mode de transfert peut se propager efficacement à travers le vide absolu de l'espace ?", "options": ["Le rayonnement", "La conduction", "La convection"], "rep": "Le rayonnement"},
        {"id": "qt4_5", "q": "Quel type d'ondes électromagnétiques invisibles transporte l'énergie thermique lors d'un transfert par rayonnement ?", "options": ["Les ondes infrarouges", "Les rayons ultraviolets", "Les rayons X"], "rep": "Les ondes infrarouges"},
        {"id": "qt4_6", "q": "Quel astronome a mis en évidence le rayonnement infrarouge en mesurant la température au-delà du spectre du prisme ?", "options": ["William Herschel", "Isaac Newton", "James Watt"], "rep": "William Herschel"},
        {"id": "qt4_7", "q": "Dans une pièce chauffée par un radiateur, la montée de l'air chaud et la descente de l'air froid correspondent à :", "options": ["Des courants de convection", "Une conduction gazeuse", "Un rayonnement thermique"], "rep": "Des courants de convection"},
        {"id": "qt4_8", "q": "La loi de Newton régit mathématiquement l'expression du flux thermique associé à quel mode ?", "options": ["La convection", "La conduction", "Le rayonnement"], "rep": "La convection"},
        {"id": "qt4_9", "q": "La constante de Stefan-Boltzmann intervient dans le calcul du flux thermique de quel type de transfert ?", "options": ["Le rayonnement", "La conduction", "La convection"], "rep": "Le rayonnement"},
        {"id": "qt4_10", "q": "Pourquoi les manches des poêles de cuisine sont-ils souvent fabriqués en bois ou en plastique ?", "options": ["Pour limiter le transfert par conduction", "Pour bloquer les courants de convection", "Pour réfléchir le rayonnement infrarouge"], "rep": "Pour limiter le transfert par conduction"}
    ]

    if "ordre_quiz_tab4_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm4_sources)
        st.session_state.ordre_quiz_tab4_therm_aleatoire = questions_therm4_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DES MODES DE TRANSFERT
    if "champs_therm4_clean" not in st.session_state:
        st.session_state.champs_therm4_clean = [
            ("1. La .......... transmet l'agitation atomique de proche en proche dans les solides.", ["Choisir...", "conduction", "convection"], "conduction", "therm4_t1"),
            ("2. Le déplacement de matière au sein des fluides caractérise la ..........", ["Choisir...", "convection", "conduction"], "convection", "therm4_t2"),
            ("3. Le rayonnement infrarouge ne nécessite aucun support de ..........", ["Choisir...", "matière", "température"], "matière", "therm4_t3"),
            ("4. Joseph Fourier a établi la loi analytique de la .......... thermique.", ["Choisir...", "conduction", "convection"], "conduction", "therm4_t4"),
            ("5. William Herschel a découvert le rayonnement invisible ..........", ["Choisir...", "infrarouge", "ultraviolet"], "infrarouge", "therm4_t5"),
            ("6. La loi de Newton permet de modéliser l'échange par ..........", ["Choisir...", "convection", "rayonnement"], "convection", "therm4_t6"),
            ("7. La propagation de l'énergie solaire à travers le vide s'effectue par ..........", ["Choisir...", "rayonnement", "conduction"], "rayonnement", "therm4_t7"),
            ("8. L'agitation cinétique se transmet sans déplacement de particules lors de la ..........", ["Choisir...", "conduction", "convection"], "conduction", "therm4_t8"),
            ("9. Le flux thermique s'exprime dans le Système International en ..........", ["Choisir...", "Watts", "Joules"], "Watts", "therm4_t9"),
            ("10. La constante de Stefan-Boltzmann régit l'émission par ..........", ["Choisir...", "rayonnement", "conduction"], "rayonnement", "therm4_t10")
        ]

    # 3. RENDU DES DEUX COLONNES D'ÉVALUATION STREAMLIT
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 4 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "", 
                options=["Choisir..."] + q_data["options"], 
                key=f"therm_at4_final_g_{q_data['id']}", 
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 4 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm4_clean:
            # Extraction explicite et sécurisée des 4 éléments du tuple pour éliminer le crash
            enonce, choix, attendu, cle = ligne
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox(
                    "", 
                    choix, 
                    key=f"{cle}_therm4_clean", 
                    disabled=verrouille, 
                    label_visibility="collapsed"
                )


def afficher_atelier_chaleur_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (La chaleur) sur deux colonnes."""
    import random

    # # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE ET HISTORIQUE DE LA CHALEUR
    questions_therm3_sources = [
        {
            "id": "qt3_1",
            "q": "Quelle est la définition scientifique exacte de la chaleur ?",
            "options": ["Un transfert d'énergie thermique entre deux corps", "Le degré d'agitation interne des molécules", "Un fluide immatériel pesable"],
            "rep": "Un transfert d'énergie thermique entre deux corps",
        },
        {
            "id": "qt3_2",
            "q": "Quelle unité historique mesurait la quantité de chaleur nécessaire pour élever d'un degré un gramme d'eau ?",
            "options": ["La calorie", "Le Joule", "Le Watt"],
            "rep": "La calorie",
        },
        {
            "id": "qt3_3",
            "q": "Quel savant a mis en évidence la chaleur latente lors de la fusion de la glace ?",
            "options": ["Joseph Black", "James Watt", "Joseph Fourier"],
            "rep": "Joseph Black",
        },
        {
            "id": "qt3_4",
            "q": "Quelle lettre majuscule symbolise universellement la quantité de chaleur dans les équations physiques ?",
            "options": ["Q", "T", "W"],
            "rep": "Q",
        },
        {
            "id": "qt3_5",
            "q": "Dans quelle expérience Joule a-t-il lié le travail mécanique à l'élévation de température ?",
            "options": ["L'expérience des palettes brassant l'eau", "L'observation du forage des canons", "L'invention de la machine à feu"],
            "rep": "L'expérience des palettes brassant l'eau",
        },
        {
            "id": "qt3_6",
            "q": "Comment qualifie-t-on un transfert de chaleur s'effectuant à température constante lors d'un changement d'état ?",
            "options": ["Un transfert de chaleur latente", "Un transfert de chaleur sensible", "Un flux par conduction pure"],
            "rep": "Un transfert de chaleur latente",
        },
        {
            "id": "qt3_7",
            "q": "Que subit la température d'un corps pur lors d'un apport de chaleur sensible sans changement d'état ?",
            "options": ["Elle augmente obligatoirement", "Elle reste strictement constante", "Elle diminue de moitié"],
            "rep": "Elle augmente obligatoirement",
        },
        {
            "id": "qt3_8",
            "q": "Quel physicien a réfuté le fluide calorique en observant la chaleur produite par le frottement mécanique lors du forage de canons ?",
            "options": ["Comte Rumford", "Antoine Lavoisier", "Sadi Carnot"],
            "rep": "Comte Rumford",
        },
        {
            "id": "qt3_9",
            "q": "Lorsque deux corps en contact atteignent la même température, le transfert thermique global est :",
            "options": ["Strictement nul (Équilibre)", "Infini et instantané", "Uniquement descendant"],
            "rep": "Strictement nul (Équilibre)",
        },
        {
            "id": "qt3_10",
            "q": "La formule reliant la chaleur sensible à la masse et à la capacité thermique s'exprime par :",
            "options": ["Q = m.c.(Tf - Ti)", "Q = m.L", "Q = U.A.dT"],
            "rep": "Q = m.c.(Tf - Ti)",
        }
    ]

    # Initialisation de l'ordre aléatoire des questions du Quiz
    if "ordre_quiz_tab3_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm3_sources)
        st.session_state.ordre_quiz_tab3_therm_aleatoire = questions_therm3_sources

    # # 2. BASE DE DONNÉES DU TEXTE À TROUS DE LA CHALEUR
    if "champs_therm3_clean" not in st.session_state:
        st.session_state.champs_therm3_clean = [
            (
                "1. La chaleur désigne un .......... d'énergie entre deux systèmes.",
                ["Choisir...", "transfert", "fluide"],
                "transfert",
                "therm3_t1",
            ),
            (
                "2. L'unité légale de la quantité de chaleur est le ..........",
                ["Choisir...", "Joule", "Calorie"],
                "Joule",
                "therm3_t2",
            ),
            (
                "3. Joseph Black a découvert la chaleur .......... liée aux changements d'état.",
                ["Choisir...", "latente", "sensible"],
                "latente",
                "therm3_t3",
            ),
            (
                "4. L'élévation de température d'un corps sans changement d'état met en jeu de la chaleur ..........",
                ["Choisir...", "sensible", "latente"],
                "sensible",
                "therm3_t4",
            ),
            (
                "5. L'expérience des .......... de Joule a prouvé la conservation de l'énergie.",
                ["Choisir...", "palettes", "vitres"],
                "palettes",
                "therm3_t5",
            ),
            (
                "6. La chaleur se déplace spontanément du corps chaud vers le corps ..........",
                ["Choisir...", "froid", "isole"],
                "froid",
                "therm3_t6",
            ),
            (
                "7. Le symbole mathématique de la quantité de chaleur est la lettre ..........",
                ["Choisir...", "Q", "W"],
                "Q",
                "therm3_t7",
            ),
            (
                "8. Le Comte Rumford a réfuté le calorique en forant des ..........",
                ["Choisir...", "canons", "tuyaux"],
                "canons",
                "therm3_t8",
            ),
            (
                "9. L'absence de transfert thermique entre deux corps en contact indique l'.......... thermique.",
                ["Choisir...", "équilibre", "blocage"],
                "équilibre",
                "therm3_t9",
            ),
            (
                "10. La constante 'c' de l'équation correspond à la .......... thermique massique.",
                ["Choisir...", "capacité", "conductivité"],
                "capacité",
                "therm3_t10",
            ),
        ]

    # # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 3 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at3_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm3_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm3_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )


def afficher_atelier_temperature_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (La température) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ TECHNIQUE ET HISTORIQUE DE LA TEMPÉRATURE
    questions_therm2_sources = [
        {
            "id": "qt2_1",
            "q": "Qui a inventé le premier instrument de mesure thermique de l'histoire, appelé le thermoscope ?",
            "options": ["Galilée", "Anders Celsius", "Lord Kelvin"],
            "rep": "Galilée",
        },
        {
            "id": "qt2_2",
            "q": "Quelle unité du Système International (SI) est l'unité légale et absolue de la température ?",
            "options": ["Le Kelvin", "Le degré Celsius", "Le degré Fahrenheit"],
            "rep": "Le Kelvin",
        },
        {
            "id": "qt2_3",
            "q": "Quelle température Celsius correspond exactement au zéro absolu (0 K) ?",
            "options": ["-273,15 °C", "0 °C", "-100 °C"],
            "rep": "-273,15 °C",
        },
        {
            "id": "qt2_4",
            "q": "Sur quel phénomène physique repose le fonctionnement des thermomètres analogiques à cadran ou à colonne ?",
            "options": ["La dilatation thermique", "La fusion moléculaire", "La conduction électrique"],
            "rep": "La dilatation thermique",
        },
        {
            "id": "qt2_5",
            "q": "Quelle température de référence fixe le point d'ébullition de l'eau pure sous une pression atmosphérique normale en échelle Celsius ?",
            "options": ["100 °C", "0 °C", "32 °C"],
            "rep": "100 °C",
        },
        {
            "id": "qt2_6",
            "q": "Pourquoi le mercure est-il aujourd'hui interdit dans la fabrication des thermomètres grand public ?",
            "options": ["En raison de sa haute toxicité", "Parce qu'il ne se dilate pas assez", "Parce qu'il coûte trop cher à produire"],
            "rep": "En raison de sa haute toxicité",
        },
        {
            "id": "qt2_7",
            "q": "Quel fluide coloré remplace très couramment le mercure dans les thermomètres domestiques classiques ?",
            "options": ["L'alcool (Éthanol)", "L'huile de moteur", "L'eau distillée"],
            "rep": "L'alcool (Éthanol)",
        },
        {
            "id": "qt2_8",
            "q": "Dans l'échelle Fahrenheit, à quelle valeur numérique correspond le point de fusion de la glace ?",
            "options": ["32 °F", "0 °F", "100 °F"],
            "rep": "32 °F",
        },
        {
            "id": "qt2_9",
            "q": "Au niveau microscopique, que mesure concrètement la température d'un corps ?",
            "options": ["Le degré d'agitation de ses molécules", "La quantité totale de matière", "Le volume de son enveloppe externe"],
            "rep": "Le degré d'agitation de ses molécules",
        },
        {
            "id": "qt2_10",
            "q": "Comment appelle-t-on le capteur électronique industriel qui utilise la variation de sa résistance avec la température (ex: Pt100) ?",
            "options": ["Une thermistance", "Un thermocouple", "Un pyromètre optique"],
            "rep": "Une thermistance",
        },
    ]

    if "ordre_quiz_tab2_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm2_sources)
        st.session_state.ordre_quiz_tab2_therm_aleatoire = questions_therm2_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS DE LA TEMPÉRATURE
    if "champs_therm2_clean" not in st.session_state:
        st.session_state.champs_therm2_clean = [
            (
                "1. Galilée a conçu le premier appareil de repérage nommé le ..........",
                ["Choisir...", "thermoscope", "baromètre"],
                "thermoscope",
                "therm2_t1",
            ),
            (
                "2. Le thermomètre à mercure a été stabilisé par le physicien ..........",
                ["Choisir...", "Fahrenheit", "Celsius"],
                "Fahrenheit",
                "therm2_t2",
            ),
            (
                "3. L'échelle centésimale fixant le zéro sur la glace fondante revient à ..........",
                ["Choisir...", "Celsius", "Kelvin"],
                "Celsius",
                "therm2_t3",
            ),
            (
                "4. Au niveau atomique, la température traduit le niveau d'.......... des particules.",
                ["Choisir...", "agitation", "blocage"],
                "agitation",
                "therm2_t4",
            ),
            (
                "5. L'absence totale de mouvement moléculaire définit le zéro ..........",
                ["Choisir...", "absolu", "relatif"],
                "absolu",
                "therm2_t5",
            ),
            (
                "6. Le fonctionnement d'un thermomètre mécanique classique utilise la ..........",
                ["Choisir...", "dilatation", "compression"],
                "dilatation",
                "therm2_t6",
            ),
            (
                "7. L'éthanol coloré est un liquide employé pour mesurer les températures ..........",
                ["Choisir...", "domestiques", "industrielles"],
                "domestiques",
                "therm2_t7",
            ),
            (
                "8. Pour passer des degrés Celsius aux Kelvins, on ajoute la valeur ..........",
                ["Choisir...", "273,15", "100"],
                "273,15",
                "therm2_t8",
            ),
            (
                "9. Un capteur industriel basé sur la soudure de deux métaux est un ..........",
                ["Choisir...", "thermocouple", "pyromètre"],
                "thermocouple",
                "therm2_t9",
            ),
            (
                "10. La mesure sans contact à distance d'un corps chaud utilise le rayonnement ..........",
                ["Choisir...", "infrarouge", "ultraviolet"],
                "infrarouge",
                "therm2_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique de l'Atelier 2 (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at2_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm2_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm2_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )




def afficher_atelier_histoire_verrouille(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    # 1. BASE DE DONNÉES DU QUIZ HISTORIQUE THERMIQUE
    questions_therm1_sources = [
        {
            "id": "qth1",
            "q": "Quel célèbre chimiste français du 18e siècle considérait la chaleur comme un fluide immatériel nommé le calorique ?",
            "options": [
                "Antoine Lavoisier",
                "Sadi Carnot",
                "James Prescott Joule",
            ],
            "rep": "Antoine Lavoisier",
        },
        {
            "id": "qth2",
            "q": "Quelle grandeur physique Guillaume Amontons puis Lord Kelvin ont-ils théorisé en fixant l'absence totale d'agitation moléculaire ?",
            "options": ["Le zéro absolu", "La capacité thermique", "Le flux de conduction"],
            "rep": "Le zéro absolu",
        },
        {
            "id": "qth3",
            "q": "Quel ingénieur français a publié en 1824 l'ouvrage fondateur décrivant la puissance motrice du feu et le cycle des machines thermiques ?",
            "options": [
                "Sadi Carnot",
                "Joseph Fourier",
                "Anders Celsius",
            ],
            "rep": "Sadi Carnot",
        },
        {
            "id": "qth4",
            "q": "Quelle expérience célèbre de James Prescott Joule en 1843 a permis de lier définitivement le travail mécanique à la chaleur ?",
            "options": ["L'expérience des palettes brassant l'eau", "L'invention du thermomètre à mercure", "La découverte du rayonnement infrarouge"],
            "rep": "L'expérience des palettes brassant l'eau",
        },
        {
            "id": "qth5",
            "q": "Quel mathématicien et physicien français a formulé en 1822 la loi mathématique rigoureuse de la conduction thermique ?",
            "options": ["Joseph Fourier", "Antoine Lavoisier", "Benjamin Thompson"],
            "rep": "Joseph Fourier",
        },
        {
            "id": "qth6",
            "q": "Quel astronome suédois a proposé en 1742 une échelle de température centésimale basée sur les points de fusion et d'ébullition de l'eau ?",
            "options": ["Anders Celsius", "Daniel Gabriel Fahrenheit", "William John Macquorn Rankine"],
            "rep": "Anders Celsius",
        },
        {
            "id": "qth7",
            "q": "En quelle année Lord Kelvin a-t-il proposé son échelle de température thermodynamique absolue commençant à zéro ?",
            "options": ["1848", "1789", "1912"],
            "rep": "1848",
        },
        {
            "id": "qth8",
            "q": "Quel physicien germano-hollandais a perfectionné le thermomètre en utilisant du mercure et une échelle fixant la glace à 32 degrés ?",
            "options": ["Daniel Gabriel Fahrenheit", "Anders Celsius", "William Thomson"],
            "rep": "Daniel Gabriel Fahrenheit",
        },
        {
            "id": "qth9",
            "q": "Selon la thermodynamique moderne, quelle est la nature microscopique de la chaleur ?",
            "options": [
                "Une agitation désordonnée des atomes",
                "Un fluide pesant circulant entre les corps",
                "Un déplacement d'électrons libres",
            ],
            "rep": "Une agitation désordonnée des atomes",
        },
        {
            "id": "qth10",
            "q": "Quelle unité du Système International (SI), officielle depuis 1948, mesure à la fois le travail, l'énergie et la quantité de chaleur ?",
            "options": [
                "Le Joule",
                "La Calorie",
                "Le Watt",
            ],
            "rep": "Le Joule",
        },
    ]

    # Initialisation de l'ordre aléatoire des questions dans la session Streamlit
    if "ordre_quiz_tab1_therm_aleatoire" not in st.session_state:
        random.shuffle(questions_therm1_sources)
        st.session_state.ordre_quiz_tab1_therm_aleatoire = questions_therm1_sources

    # 2. BASE DE DONNÉES DU TEXTE À TROUS HISTORIQUE THERMIQUE
    if "champs_therm1_clean" not in st.session_state:
        st.session_state.champs_therm1_clean = [
            (
                "1. Au 18e siècle, Lavoisier définit la chaleur comme un fluide appelé ..........",
                ["Choisir...", "calorique", "phlogistique"],
                "calorique",
                "therm1_t1",
            ),
            (
                "2. La révolution industrielle du 19e siècle repose sur les machines ..........",
                ["Choisir...", "thermiques", "hydrauliques"],
                "thermiques",
                "therm1_t2",
            ),
            (
                "3. La découverte de Joule en 1843 montre que la chaleur est une ..........",
                ["Choisir...", "énergie", "matière"],
                "énergie",
                "therm1_t3",
            ),
            (
                "4. Le modèle de Fourier décrit mathématiquement le transfert par ..........",
                ["Choisir...", "conduction", "rayonnement"],
                "conduction",
                "therm1_t4",
            ),
            (
                "5. L'échelle de température absolue basée sur le zéro absolu revient à ..........",
                ["Choisir...", "Kelvin", "Celsius"],
                "Kelvin",
                "therm1_t5",
            ),
            (
                "6. Un corps chaud dont les molécules s'agitent possède de l'énergie ..........",
                ["Choisir...", "thermique", "potentielle"],
                "thermique",
                "therm1_t6",
            ),
            (
                "7. L'étude de la chaleur et de ses conversions en travail est la ..........",
                ["Choisir...", "thermodynamique", "cinématique"],
                "thermodynamique",
                "therm1_t7",
            ),
            (
                "8. Sadi Carnot a mis en évidence le rendement maximal d'un ..........",
                ["Choisir...", "cycle", "fluide"],
                "cycle",
                "therm1_t8",
            ),
            (
                "9. L'unité historique de la chaleur, avant le Joule, était la ..........",
                ["Choisir...", "calorie", "frigorie"],
                "calorie",
                "therm1_t9",
            ),
            (
                "10. La mesure de la température s'est développée grâce au ..........",
                ["Choisir...", "thermomètre", "manomètre"],
                "thermomètre",
                "therm1_t10",
            ),
        ]

    # 3. RENDU DES DEUX COLONNES STREAMLIT
    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Technique et Historique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_therm_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            st.selectbox(
                "",
                options=["Choisir..."] + q_data["options"],
                key=f"therm_at1_final_g_{q_data['id']}",
                disabled=verrouille,
                label_visibility="collapsed",
            )

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_therm1_clean:
            enonce, choix, cle = ligne[0], ligne[1], ligne[-1]
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt:
                st.write(enonce)
            with c_sel:
                st.selectbox(
                    "",
                    choix,
                    key=f"{cle}_therm1_clean",
                    disabled=verrouille,
                    label_visibility="collapsed",
                )

                
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
    st.header("Histoire et Découverte de la Thermique")
    st.write(
        "Découvrez comment l'humanité a compris la nature de la chaleur, passant d'un fluide imaginaire à une agitation microscopique :"
    )

    # =============================================================================
    # SECTION HISTORIQUE ET SCIENTIFIQUES CLÉS
    # =============================================================================
    col_hist_1, col_hist_img1 = st.columns(2)
    
    with col_hist_1:
        st.markdown("##### La théorie du « Calorique »")
        st.write(
            "Pendant longtemps, les scientifiques comme Antoine Lavoisier pensaient que la chaleur "
            "était un fluide invisible et immatériel appelé le **calorique**. Selon cette théorie, "
            "un corps chaud possédait simplement plus de ce fluide qu'un corps froid."
        )

    with col_hist_img1:

        if os.path.exists("Lavoisier.jpg"):
            st.image(
                "Lavoisier.jpg",
                caption="Antoine Lavoisier"
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    col_hist_2, col_hist_img2 = st.columns(2)
    
    with col_hist_2:
        st.markdown("##### La révolution thermodynamique")
        st.write(
            "Au XIXe siècle, des physiciens comme James Prescott Joule et Sadi Carnot démontrent que "
            "la chaleur n'est pas un fluide, mais une **forme d'énergie** liée à l'agitation des "
            "atomes. C'est la naissance de la thermodynamique moderne, essentielle pour l'industrie, "
            "le bâtiment et la maintenance."
        )
    with col_hist_img2:
        col_hist_img21, col_hist_img22 = st.columns(2)
        with col_hist_img21:
            if os.path.exists("Joule.jpg"):
                st.image(
                    "Joule.jpg",
                    caption="James Prescott Joule",
                )
            else:
                st.warning(
                    "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )

        with col_hist_img22:
            if os.path.exists("Carnot.jpg"):
                st.image(
                    "Carnot.jpg",
                    caption=" Sadi Carnot ",
                )
            else:
                st.warning(
                    "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                )
                  
    st.write("---")

    # =============================================================================
    # BANDE DESSINÉE HUMORISTIQUE EN 4 CASES : LE DRAME DES CALORIES PERDUES
    # =============================================================================
    col_gauche_texte, col_droite_img = st.columns(2)

    with col_gauche_texte:
        st.write(
            "**La BD humoristique textuelle : Le drame des calories perdues**")
        
        st.info(
            "**Cas 1 :** Un groupe d'atomes à l'intérieur d'une maison chauffée est tranquillement installé "
            "dans la structure de la paroi. Ils vibrent joyeusement ensemble et discutent avec leurs voisins : "
            "« Tout va bien les gars, la parfaite cohésion est là, on forme un bloc d'isolation indestructible ! ».\n\n"
            
            "**Cas 2 :** Une baisse brutale des températures survient à l'extérieur. L'air froid hivernal, "
            "très gourmand, attrape l'atome de la paroi par le bras et crie : "
            "« Hé toi ! Donne-moi tes charges ! Tes précieux joules d'énergie m'intéressent grandement ! ».\n\n"
            
            "**Cas 3 :** L'atome de la paroi, dépouillé de son énergie de protection, commence à se refroidir "
            "et à se détacher du réseau. Il panique en voyant sa température baisser : "
            "« Oh non ! Je viens de subir un transfert thermique ! Je ne suis plus un atome chaud et agité, "
            "je me transforme en conducteur froid ! C'est la liquéfaction ! ».\n\n"
            
            "**Cas 4 :** La chaleur évadée désormais flotte dans l'atmosphère froide sous forme de perte pure, "
            "laissant un trou béant dans le bilan énergétique de la poutre. Les atomes de froid s'enfuient "
            "en ricanant avec leur butin : "
            "« Affaire classée ! Encore un système chauffé terrassé par notre pouvoir absorbant ! »."
        )

    with col_droite_img:

        if os.path.exists("chaleur_caricature.jpg"):
            st.image(
                "chaleur_caricature.jpg",
                caption="Illustration humoristique du drame des calories perdues",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
            
    st.write("---")
    if "suite_verrouille_tab1_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab1_therm = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_therm

    # Affichage du module de questions spécifique à l'histoire de la thermique
    afficher_atelier_histoire_verrouille(verrouille=verrou_at1)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Historique.",
        key="check_certif_therm1_final_net",
        disabled=verrou_at1,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1",
        key="btn_export_suite1_therm_official",
        use_container_width=True,
        disabled=verrou_at1,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction automatisée du Quiz Technique
            score_q1 = 0.0
            if "ordre_quiz_tab1_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # 2. Correction automatisée sécurisée du Texte à trous
            score_t1 = 0.0
            if "champs_therm1_clean" in st.session_state:
                for ligne in st.session_state.champs_therm1_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm1_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t1 += 1.0

            # 3. Sauvegarde des scores et verrouillage automatique de la session
            st.session_state.score_suite1_therm_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_therm_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_therm = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_therm = True
            st.rerun()

    # --- COMPILATION DU BILAN FICHIER HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab1_therm", False):
        from datetime import datetime
        scr1_t1 = st.session_state.get("score_suite1_therm_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_therm_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_therm", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(
            f"ATELIER HISTORIQUE SCELLÉ | Note de session : {tot_s_t1:.1f} / 20"
        )

        html_export_therm1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 1 : Contexte historique des transferts thermiques et évolution des modèles</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab1_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm1_clean, 1):
                enonce_texte = ligne
                attendu_texte = ligne
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm1 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Rendu du bouton de téléchargement natif pour le fichier HTML compilé (.html)
        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 1 (.HTML)",
            data=html_export_therm1,
            file_name=preparer_nom_fichier("Atelier_1_Historique").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )



with tab2:
    st.header("La Température et la Mesure de l'Agitation Thermique")
    st.write(
        "Découvrez l'histoire des échelles de température, les inventeurs des premiers capteurs, "
        "et observez en direct le phénomène physique de la dilatation volumique des fluides :"
    )

    # =============================================================================
    # SECTION HISTORIQUE : LES ENCIENS MODÈLES ET LES HOMMES
    # =============================================================================
    col_t2_h1, col_t2_h2 = st.columns(2)
    
    with col_t2_h1:
        st.markdown("##### Les Pionniers du Thermomètre")
        st.write(
            "**Galilée (1592) :** Il invente le thermoscope, un tube de verre où l'air se dilate et déplace de l'eau, "
            "mais l'absence d'échelle graduée fixe empêche une mesure quantitative précise.\n\n"
            "**Daniel Gabriel Fahrenheit (1714) :** Il révolutionne la métrologie en fabriquant le premier "
            "thermomètre fiable à mercure. Il fixe son zéro en mélangeant de la glace, de l'eau et du sel d'ammonium."
        )

        col_t21_h11, col_t21_h21 = st.columns(2)
        
        with col_t21_h11:
            col_t21_h111, col_t21_h211 = st.columns(2)
            with col_t21_h111:
                if os.path.exists("Galilee.jpg"):
                    st.image(
                        "Galilee.jpg",
                        caption="Galilée",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Galilee.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

            with col_t21_h211:
                if os.path.exists("thermoscope.jpg"):
                    st.image(
                        "thermoscope.jpg",
                        caption="thermoscope de Galilée",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'thermoscope.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

        with col_t21_h21:
            col_t21_h311, col_t21_h411 = st.columns(2)
            with col_t21_h311:
                if os.path.exists("Fahrenheit.jpg"):
                    st.image(
                        "Fahrenheit.jpg",
                        caption="Daniel Gabriel Fahrenheit",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Fahrenheit.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

            with col_t21_h411:
                if os.path.exists("mercure.jpg"):
                    st.image(
                        "mercure.jpg",
                        caption="thermomètre à mercure",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'mercure.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )
            
    with col_t2_h2:
        st.markdown("##### L'Évolution des Unités")
        st.write(
            "**Anders Celsius (1742) :** Il propose une échelle centésimale inversée (0 pour l'eau bouillante, 100 pour la glace), "
            "remise dans le bon sens après sa mort : 0 degré pour la glace fondante et 100 degrés pour l'ébullition.\n\n"
            "**Lord Kelvin (1848) :** Il définit l'échelle thermodynamique absolue. Le zéro absolu (-273,15 degrés Celsius) "
            "représente l'état d'immobilisation totale de la matière."
        )

        col_t21_h31, col_t36_h36 = st.columns(2)
        
        with col_t21_h31:
            col_t21_c1, col_t21_c2 = st.columns(2)
            with col_t21_c1:
                if os.path.exists("Celsius.jpg"):
                    st.image(
                        "Celsius.jpg",
                        caption="Anders Celsius",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Celsius.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application.")

            with col_t21_c2:
                if os.path.exists("thermomercure.jpg"):
                    st.image(
                        "thermomercure.jpg",
                        caption="thermomètre degré Celsius",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'thermomercure.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

        with col_t36_h36:
            col_t36_k1, col_t36_k2 = st.columns(2)
            with col_t36_k1:
                if os.path.exists("Kelvin.jpg"):
                    st.image(
                        "Kelvin.jpg",
                        caption="Lord Kelvin",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'Kelvin.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )

            with col_t36_k2:
                if os.path.exists("themokelvin.jpg"):
                    st.image(
                        "themokelvin.jpg",
                        caption="mesure et extrapolation pour trouver le 0K",
                        use_container_width=True
                    )
                else:
                    st.warning(
                        "L'image 'themokelvin.jpg.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
                    )




    st.write("---")
    st.subheader("Modélisation microscopique : À quoi correspond la température ?")
    st.write(
        "La température traduit graphiquement le niveau d'agitation cinétique désordonnée "
        "des particules au cœur de la matière :"
    )

    img_col_gauche, img_col_droite = st.columns(2)

    with img_col_gauche:
        # Affichage de l'image de gauche (Basse température)
        if os.path.exists("froid.jpg"):
            st.image(
                "froid.jpg",
                caption="Basse température : faible vitesse d'agitation",
                use_container_width=True
            )
        else:
            st.warning(
                "L'image 'froid.jpg' est introuvable. Placez l'illustration dans le répertoire de l'application."
            )

    with img_col_droite:
        # Affichage de l'image de droite (Haute température)
        if os.path.exists("chaud.jpg"):
            st.image(
                "chaud.jpg",
                caption="Haute température : grande vitesse d'agitation",
                use_container_width=True
            )
        else:
            st.warning(
                "L'image 'chaud.jpg' est introuvable. Placez l'illustration dans le répertoire de l'application."
            )

    st.write("---")
    st.subheader("Convertisseur interactif d'unités de température")
    st.write(
        "Utilisez les commandes ci-dessous pour convertir une valeur d'une échelle à une autre "
        "et observez les formules de transformation associées :"
    )

    # Grille de saisie à 3 colonnes pour configurer la conversion
    conv_col1, conv_col2, conv_col3 = st.columns([1.0, 1.0, 1.2])

    with conv_col1:
        unite_source = st.selectbox(
            "Unité de départ :",
            ["Degré Celsius (°C)", "Kelvin (K)", "Degré Fahrenheit (°F)"],
            key="t2_conv_unite_source"
        )

    with conv_col2:
        valeur_saisie = st.number_input(
            "Valeur à convertir :",
            value=20.0,
            step=0.5,
            format="%.2f",
            key="t2_conv_valeur_saisie"
        )

    with conv_col3:
        unite_cible = st.selectbox(
            "Unité d'arrivée :",
            ["Degré Celsius (°C)", "Kelvin (K)", "Degré Fahrenheit (°F)"],
            key="t2_conv_unite_cible"
        )

    # Initialisation des variables de calcul
    resultat_conv = valeur_saisie
    formule_latex = r"T_{\text{cible}} = T_{\text{source}}"

    # Logique mathématique des conversions
    if unite_source == "Degré Celsius (°C)":
        if unite_cible == "Kelvin (K)":
            resultat_conv = valeur_saisie + 273.15
            formule_latex = r"T(\text{K}) = T(°\text{C}) + 273{,}15"
        elif unite_cible == "Degré Fahrenheit (°F)":
            resultat_conv = (valeur_saisie * 9/5) + 32
            formule_latex = r"T(°\text{F}) = T(°\text{C}) \times \frac{9}{5} + 32"

    elif unite_source == "Kelvin (K)":
        # Sécurité pour le zéro absolu
        if valeur_saisie < 0:
            st.error("Erreur physique : Une température en Kelvin ne peut pas être négative (Zéro absolu).")
        if unite_cible == "Degré Celsius (°C)":
            resultat_conv = valeur_saisie - 273.15
            formule_latex = r"T(°\text{C}) = T(\text{K}) - 273{,}15"
        elif unite_cible == "Degré Fahrenheit (°F)":
            resultat_conv = ((valeur_saisie - 273.15) * 9/5) + 32
            formule_latex = r"T(°\text{F}) = (T(\text{K}) - 273{,}15) \times \frac{9}{5} + 32"

    elif unite_source == "Degré Fahrenheit (°F)":
        if unite_cible == "Degré Celsius (°C)":
            resultat_conv = (valeur_saisie - 32) * 5/9
            formule_latex = r"T(°\text{C}) = (T(°\text{F}) - 32) \times \frac{5}{9}"
        elif unite_cible == "Kelvin (K)":
            resultat_conv = ((valeur_saisie - 32) * 5/9) + 273.15
            formule_latex = r"T(\text{K}) = (T(°\text{F}) - 32) \times \frac{5}{9} + 273{,}15"

    # Affichage du résultat dans un encadré propre
    if not (unite_source == "Kelvin (K)" and valeur_saisie < 0):
        st.markdown("**Formule de conversion appliquée :**")
        st.latex(formule_latex)
        
        # Extraction propre du symbole d'unité (ex: '°C' au lieu de 'Degré Celsius (°C)')
        symb_src = unite_source.split(" (")[1][:-1] if " (" in unite_source else unite_source
        symb_cib = unite_cible.split(" (")[1][:-1] if " (" in unite_cible else unite_cible

        # Boîte de résultat finale purgée des arguments invalides
        st.markdown(
            f"<div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; border-left: 4px solid #1e3a8a; font-size: 16px; font-weight: bold; color: #0f172a;'>"
            f"Résultat de la conversion : {valeur_saisie:.2f} {symb_src} = {resultat_conv:.2f} {symb_cib}"
            f"</div>",
            unsafe_allow_html=True
        )

    st.write("---")
    # =============================================================================
    # CONFIGURATION DOUBLE COLONNE : TEXTE BLEU A GAUCHE / IMAGE ET GRAPHISME A DROITE
    # =============================================================================
    col_gauche_texte_t2, col_droite_img_t2 = st.columns(2)

    with col_gauche_texte_t2:
        st.write(
            "**La BD humoristique textuelle : Le thermomètre en folie**"
        )
        
        st.info(
            "**Cas 1 :** À l'état initial, les molécules d'un fluide sont calmes et immobiles. "
            "Elles dorment paisiblement à la température de zéro absolu dans leur bulbe en verre : "
            "« Chut, aucun mouvement ici, l'immobilité thermodynamique est totale ! ».\n\n"
            
            "**Cas 2 :** Une source de chaleur extérieure arrive soudainement. Le feu attrape les molécules "
            "par le bras et injecte de l'énergie thermique en hurlant : "
            "« Debout là-dedans ! Donnez-moi vos mouvements ! Il est temps de vous agiter énergiquement ! ».\n\n"
            
            "**Cas 3 :** Les molécules, excitées par l'apport d'énergie, paniquent et commencent à vibrer "
            "dans tous les sens. Manquant de place, elles poussent les parois du thermomètre : "
            "« Oh non ! On subit une augmentation de température ! On a trop de joules, "
            "il faut qu'on s'écarte, c'est la dilatation volumique ! ».\n\n"
            
            "**Cas 4 :** La colonne de liquide s'est violemment élevée le long du tube en verre, "
            "brisant le sommet du thermomètre sous la pression de l'agitation. Les molécules de chaleur s'échappent "
            "en ricanant : "
            "« Affaire classée ! Encore un capteur en verre terrassé par notre puissance cinétique ! »."
        )

    with col_droite_img_t2:
        if os.path.exists("temperature_caricature.jpg"):
            st.image(
                "temperature_caricature.jpg",
                caption="Illustration humoristique du mécanisme de dilatation thermique",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'temperature_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )
    # =============================================================================
    # SIMULATEUR DYNAMIQUE : DILATATION DES LIQUIDES THERMOMÉTRIQUES
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Dilatation et choix du liquide de mesure")
    st.write(
        "Sélectionnez le fluide de votre choix et ajustez la température pour observer "
        "la montée ou la descente de la colonne liquide dans le tube capillaire en verre :"
    )

    # Dictionnaire de configuration réelle des liquides thermométriques
    fluides_thermiques = {
        "Alcool coloré (Éthanol)": {
            "couleur": "#ef4444", 
            "usage": "Usage domestique standard. Utilisé pour les températures ambiantes et négatives.",
            "min_t": -50, "max_t": 70
        },
        "Mercure (Historique)": {
            "couleur": "#94a3b8", 
            "usage": "Interdit aujourd'tui en raison de sa toxicité. Grande précision, large plage de mesure.",
            "min_t": -35, "max_t": 350
        },
        "Huile minérale": {
            "couleur": "#eab308", 
            "usage": "Alternative écologique moderne pour les thermomètres de cuisine et de jardin.",
            "min_t": -10, "max_t": 120
        }
    }

    # Configuration des commandes par l'étudiant
    col_param_1, col_param_2 = st.columns([1.1, 1.0])
    
    with col_param_1:
        choix_fluide = st.selectbox(
            "Sélectionnez le liquide thermométrique :",
            list(fluides_thermiques.keys()),
            key="t2_choix_liquide_dilatation"
        )
        
        cfg_f = fluides_thermiques[choix_fluide]
        
        # Sélection de la température dynamique bridée selon les propriétés du fluide choisi
        temperature_saisie = st.slider(
            f"Ajustez la température (°C) :",
            min_value=int(cfg_f["min_t"]),
            max_value=int(cfg_f["max_t"]),
            value=20,
            step=1,
            key="t2_slider_temperature"
        )
        
    with col_param_2:
        st.markdown("**Propriétés de laboratoire du fluide sélectionné :**")
        st.info(f"**Application :** {cfg_f['usage']}\n\n**Plage d'état liquide sécurisée :** de {cfg_f['min_t']} °C à {cfg_f['max_t']} °C.")

    # =============================================================================
    # RENDU VISUEL SCIENTIFIQUE DU THERMOMÈTRE (MATPLOTLIB)
    # =============================================================================
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig, ax = plt.subplots(figsize=(6, 5))
    
    # 1. Dessin de la structure extérieure en verre du thermomètre
    # Le réservoir sphérique en bas
    ax.add_patch(patches.Circle((2.5, 1.2), radius=0.4, facecolor='#f8fafc', edgecolor='#1e293b', lw=2.5, zorder=1))
    # Le tube capillaire vertical de mesure
    ax.add_patch(patches.Rectangle((2.35, 1.2), 0.3, 4.8, facecolor='#f8fafc', edgecolor='#1e293b', lw=2.5, zorder=1))
    
    # 2. Calcul du niveau de dilatation linéaire (hauteur de la colonne)
    # On normalise la température choisie entre 0% et 100% de la hauteur du tube
    t_min_curseur = cfg_f["min_t"]
    t_max_curseur = cfg_f["max_t"]
    ratio = (temperature_saisie - t_min_curseur) / (t_max_curseur - t_min_curseur)
    
    # Hauteur minimale fixe du liquide = 1.2 (remplit le réservoir) + extension proportionnelle
    hauteur_remplissage_capillaire = 0.2 + (ratio * 4.3)

    # 3. Dessin du liquide en couleur réelle
    # Remplissage du bulbe bas
    ax.add_patch(patches.Circle((2.5, 1.2), radius=0.36, color=cfg_f["couleur"], zorder=2))
    # Remplissage de la colonne de dilatation dans le capillaire
    ax.add_patch(patches.Rectangle((2.39, 1.2), 0.22, hauteur_remplissage_capillaire, color=cfg_f["couleur"], zorder=2))

    # 4. Tracé précis des graduations de l'échelle à droite du verre
    for i in range(11):
        # Positionnement des paliers de 0 à 10
        pos_y = 1.4 + (i * 0.43)
        val_temp_grad = t_min_curseur + i * (t_max_curseur - t_min_curseur) / 10
        ax.plot([2.65, 2.75], [pos_y, pos_y], color='#1e293b', lw=1, zorder=3)
        ax.text(2.85, pos_y, f"{int(val_temp_grad)} °C", color='#475569', fontsize=8, va='center', zorder=3)

    # Graduations intermédiaires fines
    for i in range(50):
        pos_y_fine = 1.4 + (i * 0.086)
        ax.plot([2.65, 2.70], [pos_y_fine, pos_y_fine], color='#64748b', lw=0.5, zorder=3)

    # 5. Rendu textuel de la mesure actuelle
    ax.text(1.5, 5.5, f"TEMPÉRATURE : {temperature_saisie} °C", color='#0f172a', fontsize=12, fontweight='bold', bbox=dict(boxstyle="round,pad=0.4", fc="#f1f5f9", ec="#cbd5e1", lw=1.5))
    
    # Ajustements géométriques des axes
    ax.set_xlim(0.5, 4.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')

    # Affichage propre dans Streamlit
    st.write("")
    st.pyplot(fig)
    st.write("---")




    st.write("---")
    if "suite_verrouille_tab2_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab2_therm = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_therm

    # Affichage du module de questions
    afficher_atelier_temperature_verrouille(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Température.",
        key="check_certif_therm2_final_net",
        disabled=verrou_at2,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2",
        key="btn_export_suite2_therm_official",
        use_container_width=True,
        disabled=verrou_at2,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q2 = 0.0
            if "ordre_quiz_tab2_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t2 = 0.0
            if "champs_therm2_clean" in st.session_state:
                for ligne in st.session_state.champs_therm2_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm2_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t2 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite2_therm_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_therm_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_therm = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab2_therm", False):
        from datetime import datetime
        scr1_t2 = st.session_state.get("score_suite2_therm_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_therm_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_therm", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TEMPÉRATURE SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_therm2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Température Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 2 : Échelles de température, principes de mesure et capteurs</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm2 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 2 (.HTML)",
            data=html_export_therm2,
            file_name=preparer_nom_fichier("Atelier_2_Temperature").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )



with tab3:
    st.header("La Chaleur et le Transfert d'Énergie Thermique")
    st.write(
        "Comprenez la différence fondamentale entre la température et la chaleur, découvrez "
        "les expériences historiques et observez les transferts d'énergie en direct :"
    )

    # =============================================================================
    # 2. COURS HISTORIQUE : LES SAVANTS ET LES EXPÉRIENCES
    # =============================================================================
    col_t3_h1, col_t3_h2 = st.columns(2)
    
    with col_t3_h1:
        st.markdown("##### Les Pionniers de la Quantification")
        st.write(
            "**Joseph Black (1761) :** Ce médecin écossais découvre la chaleur latente. Il remarque "
            "que l'apport de chaleur pour faire fondre de la glace n'augmente pas sa température tant "
            "que la fusion n'est pas totale. Il introduit ainsi la distinction entre intensité (température) et quantité (chaleur).\n\n"
            "**Benjamin Thompson / Comte Rumford (1798) :** En observant le forage des canons, il démontre "
            "que le frottement mécanique produit une quantité de chaleur infinie. Il assène le premier coup fatal à la théorie du fluide calorique."
        )

        col_t31_h11, col_t31_h21 = st.columns(2)
        with col_t31_h11:
            col_t31_c1, col_t31_c2 = st.columns(2)
            with col_t31_c1:
                if os.path.exists("Black.jpg"):
                    st.image("Black.jpg", caption="Joseph Black", use_container_width=True)
                else:
                    st.warning("L'image 'Black.jpg' est introuvable.")
            with col_t31_c2:
                if os.path.exists("calorimetreblack.jpg"):
                    st.image("calorimetreblack.jpg", caption="Calorimètre historique", use_container_width=True)
                else:
                    st.warning("L'image 'calorimetreblack.jpg' est introuvable.")
        with col_t31_h21:
            col_t31_c3, col_t31_c4 = st.columns(2)
            with col_t31_c3:
                if os.path.exists("Rumford.jpg"):
                    st.image("Rumford.jpg", caption="Comte Rumford", use_container_width=True)
                else:
                    st.warning("L'image 'Rumford.jpg' est introuvable.")
            with col_t31_c4:
                if os.path.exists("canon.jpg"):
                    st.image("canon.jpg", caption="Forage des canons", use_container_width=True)
                else:
                    st.warning("L'image 'canon.jpg' est introuvable.")
            
    with col_t3_h2:
        st.markdown("##### L'Équivalent Mécanique de la Chaleur")
        st.write(
            "**James Prescott Joule (1843) :** Grâce à sa célèbre expérience de la cuve munie de palettes en rotation "
            "actionnées par la chute de masses, il établit une équivalence stricte entre le travail mécanique et la chaleur.\n\n"
            "**L'Établissement du Joule :** Ses mesures rigoureuses prouvent qu'une quantité de travail mécanique "
            "fournie engendre toujours une élévation prévisible de température, fixant l'unité de la chaleur (le Joule)."
        )


        col_t32_c1, col_t32_c2 = st.columns(2)
        with col_t32_c1:
            if os.path.exists("Joule.jpg"):
                st.image("Joule.jpg", caption="James Joule", use_container_width=True)
            else:
                st.warning("L'image 'Joule.jpg' est introuvable.")
        with col_t32_c2:
            if os.path.exists("palettesjoule.jpg"):
                st.image("palettesjoule.jpg", caption="Expérience des palettes", use_container_width=True)
            else:
                st.warning("L'image 'palettesjoule.jpg' est introuvable.")

    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE : LE DRAME DES CALORIES PERDUES
    # =============================================================================
    col_gauche_texte_t3, col_droite_img_t3 = st.columns(2)

    with col_gauche_texte_t3:  # Réutilisation de votre structure à deux colonnes symétriques
        st.write(
            "**La BD humoristique textuelle : Le drame des calories perdues**"
        )
        
        st.info(
            "**Cas 1 :** Un groupe d'atomes à l'intérieur d'une maison chauffée est tranquillement installé "
            "dans la structure de la paroi. Ils vibrent joyeusement ensemble et discutent avec leurs voisins : "
            "« Tout va bien les gars, la parfaite cohésion est là, on forme un bloc d'isolation indestructible ! ».\n\n"
            
            "**Cas 2 :** Une baisse brutale des températures survient à l'extérieur. L'air froid hivernal, "
            "très gourmand, attrape l'atome de la paroi par le bras et crie : "
            "« Hé toi ! Donne-moi tes charges ! Tes précieux joules d'énergie m'intéressent grandement ! ».\n\n"
            
            "**Cas 3 :** L'atome de la paroi, dépouillé de son énergie de protection, commence à se refroidir "
            "et à se détacher du réseau. Il panique en voyant sa température baisser : "
            "« Oh non ! Je viens de subir un transfert thermique ! Je ne suis plus un atome chaud et agité, "
            "je me transforme en conducteur froid ! C'est la dissipation ! ».\n\n"
            
            "**Cas 4 :** La chaleur évadée désormais flotte dans l'atmosphère froide sous forme de perte pure, "
            "laissant un trou béant dans le bilan énergétique de la poutre. Les atomes de froid s'enfuient "
            "en ricanant avec leur butin : "
            "« Affaire classée ! Encore un système chauffé terrassé par notre pouvoir absorbant ! »."
        )

    with col_droite_img_t3:
        if os.path.exists("chaleur_caricature.jpg"):
            st.image(
                "chaleur_caricature.jpg",
                caption="Illustration humoristique du drame des calories perdues",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'chaleur_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")

    st.write("---")
    st.subheader("Laboratoire Virtuel : Calorimétrie avancée et équilibres de phases")
    st.write(
        "Configurez jusqu'à 5 fluides parmi une bibliothèque de 24 corps réels. Le moteur "
        "de calcul intègre les capacités thermiques ainsi que les chaleurs latentes en cas "
        "de changement d'état (fusion, solidification, vaporisation) au cours du mélange :"
    )

    # DÉFINITION IMPÉRATIVE DU DICTIONNAIRE AVANT SON UTILISATION
    bibliotheque_24_liquides = {
        "Eau pure": {"c": 4180, "rho": 1.00, "T_f": 0, "T_e": 100, "L_f": 334000, "L_v": 2260000, "col": "#bae6fd"},
        "Lait entier": {"c": 3890, "rho": 1.03, "T_f": -0.5, "T_e": 100.5, "L_f": 320000, "L_v": 2240000, "col": "#f8fafc"},
        "Bière standard": {"c": 4050, "rho": 1.01, "T_f": -2, "T_e": 95, "L_f": 310000, "L_v": 1900000, "col": "#fef08a"},
        "Vin rouge": {"c": 3780, "rho": 0.99, "T_f": -5, "T_e": 85, "L_f": 280000, "L_v": 1500000, "col": "#7f1d1d"},
        "Vin blanc": {"c": 3790, "rho": 0.99, "T_f": -5, "T_e": 85, "L_f": 280000, "L_v": 1500000, "col": "#fef9c3"},
        "Éthanol (Alcool)": {"c": 2440, "rho": 0.79, "T_f": -114, "T_e": 78, "L_f": 109000, "L_v": 841000, "col": "#fecdd3"},
        "Huile végétale": {"c": 2000, "rho": 0.92, "T_f": -10, "T_e": 300, "L_f": 80000, "L_v": 350000, "col": "#fef08a"},
        "Glycérol": {"c": 2400, "rho": 1.26, "T_f": 18, "T_e": 290, "L_f": 200000, "L_v": 826000, "col": "#fed7aa"},
        "Acétone": {"c": 2160, "rho": 0.79, "T_f": -95, "T_e": 56, "L_f": 98000, "L_v": 525000, "col": "#ddd6fe"},
        "Méthanol": {"c": 2530, "rho": 0.79, "T_f": -97, "T_e": 65, "L_f": 99000, "L_v": 1100000, "col": "#e2e8f0"},
        "Benzène": {"c": 1740, "rho": 0.88, "T_f": 5.5, "T_e": 80, "L_f": 127000, "L_v": 394000, "col": "#cbd5e1"},
        "Mercure liquide": {"c": 139, "rho": 13.55, "T_f": -39, "T_e": 357, "L_f": 11400, "L_v": 295000, "col": "#94a3b8"},
        "Sodium fondu": {"c": 1380, "rho": 0.97, "T_f": 98, "T_e": 883, "L_f": 113000, "L_v": 426000, "col": "#64748b"},
        "Plomb liquide": {"c": 150, "rho": 10.66, "T_f": 327, "T_e": 1749, "L_f": 23000, "L_v": 858000, "col": "#475569"},
        "Huile de moteur": {"c": 1900, "rho": 0.89, "T_f": -20, "T_e": 250, "L_f": 70000, "L_v": 280000, "col": "#a1a1aa"},
        "Ammoniac liquide": {"c": 4700, "rho": 0.68, "T_f": -78, "T_e": -33, "L_f": 332000, "L_v": 1370000, "col": "#a5f3fc"},
        "Fluide R134a": {"c": 1420, "rho": 1.21, "T_f": -103, "T_e": -26, "L_f": 215000, "L_v": 217000, "col": "#cffafe"},
        "Azote cryogénique": {"c": 2040, "rho": 0.81, "T_f": -210, "T_e": -196, "L_f": 25700, "L_v": 199000, "col": "#ccfbf1"},
        "Essence standard": {"c": 2220, "rho": 0.75, "T_f": -40, "T_e": 150, "L_f": 95000, "L_v": 315000, "col": "#fef9c3"},
        "Gazole / Diesel": {"c": 2000, "rho": 0.85, "T_f": -5, "T_e": 280, "L_f": 85000, "L_v": 290000, "col": "#fef08a"},
        "Acide sulfurique": {"c": 1390, "rho": 1.84, "T_f": 10, "T_e": 337, "L_f": 103000, "L_v": 510000, "col": "#e9d5ff"},
        "Éthylène glycol": {"c": 2400, "rho": 1.11, "T_f": -13, "T_e": 197, "L_f": 181000, "L_v": 800000, "col": "#f5d0fe"},
        "Eau de mer": {"c": 3990, "rho": 1.02, "T_f": -2, "T_e": 101, "L_f": 325000, "L_v": 2240000, "col": "#7dd3fc"},
        "Aniline": {"c": 2060, "rho": 1.02, "T_f": -6, "T_e": 184, "L_f": 112000, "L_v": 479000, "col": "#fae8ff"}
    }

    nb_melanges = st.slider(
        "Nombre de liquides à intégrer :", 
        min_value=2, 
        max_value=5, 
        value=2, 
        step=1, 
        key="t3_nb_liquides_melange_24"
    )

    volume_total = 0.0
    somme_m_c = 0.0
    somme_m_c_T = 0.0
    fluides_presents = []

    st.write("")
    st.markdown("**Configuration des compartiments fluides :**")
    colonnes_fluides = st.columns(nb_melanges)

    for i in range(nb_melanges):
        with colonnes_fluides[i]:
            st.markdown(f"**Fluide {i+1}**")
            liq_nom = st.selectbox(f"Nature :", list(bibliotheque_24_liquides.keys()), key=f"t3_m24_nat_{i}")
            liq_vol = st.slider(f"Volume (L) :", min_value=0.1, max_value=5.0, value=1.0, step=0.1, key=f"t3_m24_vol_{i}")
            
            p_therm = bibliotheque_24_liquides[liq_nom]
            
            t_min_curseur = int(max(-220, p_therm["T_f"]))
            t_max_curseur = int(min(400, p_therm["T_e"]))
            if t_min_curseur >= t_max_curseur: 
                t_min_curseur, t_max_curseur = t_max_curseur - 20, t_max_curseur + 20
                
            liq_temp = st.slider(f"Température (°C) :", min_value=t_min_curseur, max_value=t_max_curseur, value=int((t_min_curseur + t_max_curseur)/2), step=1, key=f"t3_m24_tmp_{i}")
            
            masse = liq_vol * p_therm["rho"]
            volume_total += liq_vol
            somme_m_c += (masse * p_therm["c"])
            somme_m_c_T += masse * p_therm["c"] * liq_temp
            
            fluides_presents.append({
                "nom": liq_nom, 
                "vol": liq_vol, 
                "temp": liq_temp, 
                "masse": masse, 
                "prop": p_therm
            })

    # Moteur mathématique calorimétrique prédictif (Calcul de la température de convergence)
    if somme_m_c > 0:
        T_equil_brute = somme_m_c_T / somme_m_c
    else:
        T_equil_brute = 20.0

    # Algorithme de vérification des transitions de phase et calcul de la composition finale
    T_finale_calculee = T_equil_brute
    phase_statut = "Monophasique (Mélange liquide limpide)"
    
    # On va stocker le volume de chaque liquide restant sous forme liquide à la fin
    composition_finale = []
    volume_liquide_total_final = 0.0

    # Détection des paliers d'ébullition ou de solidification
    for f in fluides_presents:
        vol_liquide_restant = f["vol"]
        etat_composant_final = "Liquide"
        
        # Cas où le mélange est trop chaud pour le fluide : Vaporisation
        if T_equil_brute >= f["prop"]["T_e"]:
            T_finale_calculee = f["prop"]["T_e"]
            phase_statut = "Biphasique (Ébullition et présence de gaz)"
            vol_liquide_restant = 0.0
            etat_composant_final = "Totalement évaporé (Gaz)"
        
        # Cas où le mélange est trop froid pour le fluide : Solidification
        elif T_equil_brute <= f["prop"]["T_f"]:
            T_finale_calculee = f["prop"]["T_f"]
            phase_statut = "Biphasique (Précipité solide / Solidification)"
            etat_composant_final = "Solidifié (Glace / Cristal)"
            
        volume_liquide_total_final += vol_liquide_restant
        composition_finale.append({
            "nom": f["nom"],
            "vol_initial": f["vol"],
            "vol_final": vol_liquide_restant,
            "etat": etat_composant_final
        })

    # =============================================================================
    # RENDU DE LA GRAPHIQUE DU LABORATOIRE INTERACTIF (MATPLOTLIB)
    # =============================================================================
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_mel20, ax_mel20 = plt.subplots(figsize=(9, 3.8))
    
    # Rendu individuel des éprouvettes graduées d'introduction
    for i, f in enumerate(fluides_presents):
        x_pos = 0.4 + (i * 1.3)
        ax_mel20.add_patch(patches.Rectangle((x_pos, 0.7), 0.7, 1.4 * (f["vol"] / 5.0), color=f["prop"]["col"], alpha=0.8, zorder=1))
        ax_mel20.add_patch(patches.Polygon([[x_pos, 2.3], [x_pos, 0.7], [x_pos + 0.7, 0.7], [x_pos + 0.7, 2.3]], closed=False, fill=False, color='#475569', lw=1.5, zorder=2))
        ax_mel20.text(x_pos + 0.35, 0.3, f"F{i+1}\n{f['temp']} °C", color='#1e293b', fontsize=8, ha='center', fontweight='bold')

    # Grande enceinte de confinement adiabatique à droite
    x_cadre = 7.2
    ax_mel20.add_patch(patches.Rectangle((x_cadre, 0.7), 2.2, 1.8 * (volume_liquide_total_final / 25.0) if volume_liquide_total_final > 0 else 0.1, color='#cbd5e1', alpha=0.8, zorder=1))
    ax_mel20.add_patch(patches.Polygon([[x_cadre, 3.0], [x_cadre, 0.7], [x_cadre + 2.2, 0.7], [x_cadre + 2.2, 3.0]], closed=False, fill=False, color='#0f172a', lw=2.5, zorder=2))
    ax_mel20.text(x_cadre + 1.1, 0.3, "CONFINEMENT\nFINAL", color='#0f172a', fontsize=8.5, ha='center', fontweight='bold')

    # Flèche directionnelle d'écoulement du flux de matière
    ax_mel20.arrow(0.4 + (nb_melanges * 1.3), 1.4, 1.0, 0, head_width=0.12, head_length=0.12, fc='#0f172a', ec='#0f172a', lw=2)

    ax_mel20.set_xlim(0, 9.8)
    ax_mel20.set_ylim(0, 3.3)
    ax_mel20.axis('off')
    st.pyplot(fig_mel20)

    # 4. Bloc d'affichage des résultats de laboratoire pur
    st.markdown("**Résultats métrologiques mesurés à l'équilibre :**")
    
    html_m20_box = f"""
    <div style='display: flex; gap: 15px; margin-bottom: 15px;'>
        <div style='flex: 1; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 4px solid #1e3a8a; font-size: 15px; font-weight: bold; color: #0f172a; text-align: center;'>
            Volume Liquide Résiduel : {volume_liquide_total_final:.2f} L
        </div>
        <div style='flex: 1; background-color: #f1f5f9; padding: 12px; border-radius: 6px; border-left: 4px solid #ea580c; font-size: 15px; font-weight: bold; color: #0f172a; text-align: center;'>
            Température Finale Réelle : {T_finale_calculee:.2f} °C
        </div>
    </div>
    <div style='background-color: #f8fafc; padding: 10px; border-radius: 4px; border: 1px dashed #cbd5e1; font-size: 13px; color: #475569; text-align: center; font-weight: bold; margin-bottom: 15px;'>
        Régime thermodynamique observé : {phase_statut}
    </div>
    """
    st.markdown(html_m20_box, unsafe_allow_html=True)

    st.markdown("**Analyse qualitative de la solution finale :**")
    
    # Initialisation de la structure de la table sans retours à la ligne indentés
    tableau_html = "<table style='width: 100%; border-collapse: collapse; background-color: white; font-size: 13px; text-align: left;'>"
    tableau_html += "<thead><tr style='background-color: #0f172a; color: white;'>"
    tableau_html += "<th style='padding: 8px;'>Nom du fluide</th>"
    tableau_html += "<th style='padding: 8px;'>Volume initial</th>"
    tableau_html += "<th style='padding: 8px;'>Volume sous forme liquide à la fin</th>"
    tableau_html += "<th style='padding: 8px;'>État physique final</th>"
    tableau_html += "</tr></thead><tbody>"
    
    for c in composition_finale:
        style_ligne = "color: #ef4444; font-weight: bold;" if "évaporé" in c["etat"] else ""
        
        # Ajout des lignes de manière parfaitement continue pour éviter l'interprétation bloc de code de Streamlit
        tableau_html += f"<tr style='border-bottom: 1px solid #e2e8f0;'>"
        tableau_html += f"<td style='padding: 8px;'>{c['nom']}</td>"
        tableau_html += f"<td style='padding: 8px;'>{c['vol_initial']:.1f} L</td>"
        tableau_html += f"<td style='padding: 8px;'>{c['vol_final']:.1f} L</td>"
        tableau_html += f"<td style='padding: 8px; {style_ligne}'>{c['etat']}</td>"
        tableau_html += f"</tr>"
        
    tableau_html += "</tbody></table>"
    
    # Rendu final sécurisé
    st.markdown(tableau_html, unsafe_allow_html=True)

    
    st.write("---")
    if "suite_verrouille_tab3_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab3_therm = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_therm

    # Affichage du module de questions spécifique à l'Atelier de la Chaleur
    afficher_atelier_chaleur_verrouille(verrouille=verrou_at3)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Chaleur.",
        key="check_certif_therm3_final_net",
        disabled=verrou_at3,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3",
        key="btn_export_suite3_therm_official",
        use_container_width=True,
        disabled=verrou_at3,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t3 = 0.0
            if "champs_therm3_clean" in st.session_state:
                for ligne in st.session_state.champs_therm3_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm3_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t3 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite3_therm_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_therm_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_therm = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab3_therm", False):
        from datetime import datetime
        scr1_t3 = st.session_state.get("score_suite3_therm_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_therm_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_therm", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER CHALEUR SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_therm3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Chaleur Thermique - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 3 : Principes fondamentaux, équivalence mécanique et calcul de la chaleur</p>
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

        if "ordre_quiz_tab3_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm3 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 3 (.HTML)",
            data=html_export_therm3,
            file_name=preparer_nom_fichier("Atelier_3_Chaleur").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )


with tab4:
    st.header("Les Modes de Transfert Thermique")
    st.write(
        "Découvrez comment l'énergie thermique se déplace d'un point à un autre à travers "
        "la matière ou le vide, et analysez les trois mécanismes fondamentaux :"
    )


    # =============================================================================
    # 2. COURS HISTORIQUE : LES SCIENTIFIQUES ET LES RECHERCHES
    # =============================================================================
    col_t4_h1, col_t4_h2 = st.columns(2)
    
    with col_t4_h1:
        st.markdown("##### La Formulation Mathématique du Flux")
        st.write(
            "**Joseph Fourier (1822) :** Ce mathématicien et physicien français publie sa célèbre "
            "Théorie analytique de la chaleur. Il y formule la loi de la conduction thermique, "
            "démontrant que le flux de chaleur est proportionnel au gradient de température.\n\n"
            "**La Conduction Microscopique :** C'est le seul mode de transfert thermique capable de "
            "s'effectuer au sein des solides de proche en proche, par transmission directe de "
            "l'agitation cinétique entre les atomes, sans déplacement macroscopique de matière."
        )

        col_t41_h11, col_t41_h21 = st.columns(2)
        with col_t41_h11:
            col_t41_c1, col_t41_c2 = st.columns(2)
            with col_t41_c1:
                if os.path.exists("Fourier.jpg"):
                    st.image("Fourier.jpg", caption="Joseph Fourier")
                else:
                    st.warning("L'image 'Fourier.jpg' est introuvable.")
            with col_t41_c2:
                if os.path.exists("conduction_lab.jpg"):
                    st.image("conduction_lab.jpg", caption="Barre de conduction")
                else:
                    st.warning("L'image 'conduction_lab.jpg' est introuvable.")
        with col_t41_h21:
            if os.path.exists("convection_mouv.jpg"):
                st.image("convection_mouv.jpg", caption="Mouvement de convection")
            else:
                st.warning("L'image 'convection_mouv.jpg' est introuvable.")

            
    with col_t4_h2:
        st.markdown("##### La Découverte du Rayonnement Invisible")
        st.write(
            "**William Herschel (1800) :** En faisant passer la lumière solaire à travers un prisme, "
            "cet astronome britannique mesure la température de chaque couleur. Il découvre que "
            "la chaleur maximale se situe au-delà du rouge visible, mettant en évidence le rayonnement infrarouge.\n\n"
            "**Le Rayonnement et la Convection :** Contrairement à la conduction, la convection implique "
            "un déplacement de fluide (gaz ou liquide). Le rayonnement, quant à lui, est le seul mode "
            "pouvant se propager dans le vide absolu sous forme d'ondes électromagnétiques."
        )

        col_t42_h31, col_t42_h32 = st.columns(2)
        with col_t42_h31:
            col_t42_c1, col_t42_c2 = st.columns(2)
            with col_t42_c1:
                if os.path.exists("Herschel.jpg"):
                    st.image("Herschel.jpg", caption="William Herschel")
                else:
                    st.warning("L'image 'Herschel.jpg' est introuvable.")
            with col_t42_c2:
                if os.path.exists("prismeherschel.jpg"):
                    st.image("prismeherschel.jpg", caption="Expérience du prisme")
                else:
                    st.warning("L'image 'prismeherschel.jpg' est introuvable.")
        with col_t42_h32:
                if os.path.exists("rayonnementsolaire.jpg"):
                    st.image("rayonnementsolaire.jpg", caption="Rayonnement")
                else:
                    st.warning("L'image 'rayonnementsolaire.jpg' est introuvable.")


    st.write("---")

    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE : LA GRANDE ÉVASION DES CALORIES
    # =============================================================================
    col_gauche_texte_t4, col_droite_img_t4 = st.columns(2)

    with col_gauche_texte_t4:
        st.write(
            "**La BD humoristique textuelle : La grande évasion des calories**"
        )
        
        st.info(
            "**Cas 1 :** Dans la poêle en cuivre, les atomes métalliques du manche reçoivent les coups "
            "de boutoir des flammes du gaz. Ils se mettent à trépigner sur place : "
            "« Attention les gars, ça chauffe par en bas ! Transmettez l'agitation de proche en proche "
            "sans bouger de vos sièges, c'est la conduction ! ».\n\n"
            
            "**Cas 2 :** Dans la casserole d'eau, les molécules du fond deviennent légères en chauffant. "
            "Elles montent en flèche vers la surface pendant que le liquide froid redescend : "
            "« En route pour l'ascenseur thermique ! On transporte la matière en bandes organisées, "
            "c'est la convection ! ».\n\n"
            
            "**Cas 3 :** À distance, les rayons du soleil traversent le vide spatial et viennent frapper "
            "la peau. Aucun contact, aucun atome pour aider, mais les photons transportent le flux : "
            "« Pas besoin de matière pour voyager ! On traverse le néant à la vitesse de la lumière, "
            "c'est le rayonnement infrarouge ! ».\n\n"
            
            "**Cas 4 :** Toutes les énergies se sont dissipées dans l'environnement. Le feu s'éteint, "
            "les flux s'arrêtent et le froid conclut la manœuvre : "
            "« Affaire classée ! Les trois complices ont dispersé tous les joules du système, "
            "l'équilibre des températures est scellé ! »."
        )

    with col_droite_img_t4:
        if os.path.exists("transfert_caricature.jpg"):
            st.image(
                "transfert_caricature.jpg",
                caption="Illustration humoristique des trois modes de transfert",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'transfert_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # 3. LABORATOIRE VIRTUEL INTERACTIF : SIMULATEUR DE FLUX THERMIQUE
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Dynamique des trois modes de transfert")
    st.write(
        "Sélectionnez un mode de transfert et observez comment les paramètres physiques "
        "modifient l'intensité du flux d'énergie transmis :"
    )

    t4_sim_mode = st.selectbox(
        "Sélectionnez le mécanisme de transfert thermique à analyser :",
        ["Conduction (Dans un solide)", "Convection (Déplacement de fluide)", "Rayonnement (Ondes infrarouges)"],
        key="t4_sim_choix_mode"
    )

    t4_col_s1, t4_col_s2 = st.columns(2)

    with t4_col_s1:
        dt_temperature = st.slider("Écart de température (dT en °C) :", min_value=5, max_value=80, value=30, key="t4_sim_dt")
    with t4_col_s2:
        surface_echange = st.slider("Surface d'échange (A en m²) :", min_value=1.0, max_value=10.0, value=2.0, step=0.5, key="t4_sim_surface")

    # Modélisation mathématique simplifiée du flux thermique nominal (en Watts)
    if "Conduction" in t4_sim_mode:
        flux_calcule = 1.5 * surface_echange * dt_temperature / 0.05  # Simulation avec lambda fixe, e=5cm
        formule_loi = r"\Phi = \frac{\lambda \cdot A \cdot \Delta T}{e} \quad \text{(Loi de Fourier)}"
        color_theme = "#0284c7"
    elif "Convection" in t4_sim_mode:
        flux_calcule = 15.0 * surface_echange * dt_temperature       # Simulation avec h=15 W/(m².K)
        formule_loi = r"\Phi = h \cdot A \cdot \Delta T \quad \text{(Loi de Newton)}"
        color_theme = "#10b981"
    else:
        flux_calcule = 5.67e-8 * surface_echange * ((dt_temperature + 273.15)**4 - 293.15**4) * 0.9 # Stefan-Boltzmann avec T_env=20°C, emiss=0.9
        formule_loi = r"\Phi = \epsilon \cdot \sigma \cdot A \cdot (T_1^4 - T_2^4) \quad \text{(Loi de Stefan-Boltzmann)}"
        color_theme = "#ea580c"

    st.markdown("**Équation physique de référence appliquée au modèle :**")
    st.latex(formule_loi)

    # Rendu graphique dynamique du flux (Matplotlib vectoriel)
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_flux, ax_fl = plt.subplots(figsize=(8, 2.5))
    
    # Représentation de l'enceinte de flux
    ax_fl.add_patch(patches.Rectangle((0.5, 0.5), 1.5, 1.5, color="#ef4444", alpha=0.7))
    ax_fl.add_patch(patches.Rectangle((5.0, 0.5), 1.5, 1.5, color="#3b82f6", alpha=0.7))
    
    ax_fl.text(1.25, 1.25, "Source\nChaude", color="white", fontweight="bold", ha="center", va="center")
    ax_fl.text(5.75, 1.25, "Milieu\nFroid", color="white", fontweight="bold", ha="center", va="center")

    epaisseur_fleche = min(12.0, max(1.5, flux_calcule / 150.0))
    ax_fl.arrow(2.2, 1.25, 2.5, 0, head_width=0.25, head_length=0.25, fc=color_theme, ec=color_theme, lw=epaisseur_fleche)
    ax_fl.text(3.45, 1.6, r"Flux thermique $\Phi$", color=color_theme, fontsize=10, fontweight="bold", ha="center")

    ax_fl.set_xlim(0, 7.2)
    ax_fl.set_ylim(0, 2.5)
    ax_fl.axis('off')
    st.pyplot(fig_flux)

    # Affichage du résultat numérique dans un conteneur HTML stylisé
    html_flux_box = f"""
    <div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; border-left: 4px solid {color_theme}; font-size: 16px; font-weight: bold; color: #0f172a; text-align: center;'>
        Puissance thermique transférée : {abs(flux_calcule):.1f} Watts (W)
    </div>
    """
    st.markdown(html_flux_box, unsafe_allow_html=True)



    st.write("---")
    if "suite_verrouille_tab4_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab4_therm = False
    verrou_at4 = st.session_state.suite_verrouille_tab4_therm

    # Affichage du module de questions spécifique à l'Atelier des Modes de Transfert
    afficher_atelier_modes_verrouille(verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur les Modes de Transfert.",
        key="check_certif_therm4_final_net",
        disabled=verrou_at4,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4",
        key="btn_export_suite4_therm_official",
        use_container_width=True,
        disabled=verrou_at4,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q4 = 0.0
            if "ordre_quiz_tab4_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at4_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t4 = 0.0
            if "champs_therm4_clean" in st.session_state:
                for ligne in st.session_state.champs_therm4_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm4_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t4 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite4_therm_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_therm_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4_therm = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab4_therm", False):
        from datetime import datetime
        scr1_t4 = st.session_state.get("score_suite4_therm_p1", 0.0)
        scr2_t4 = st.session_state.get("score_suite4_therm_p2", 0.0)
        tot_s_t4 = st.session_state.get("score_final_suite4_therm", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MODES DE TRANSFERT SCELLÉ | Note de session : {tot_s_t4:.1f} / 20")

        html_export_therm4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Modes de Transfert - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 4 : Analyse de la conduction, de la convection et du rayonnement électromagnétique</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s_t4:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at4_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm4 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm4_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm4_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm4_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm4 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm4 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 4 (.HTML)",
            data=html_export_therm4,
            file_name=preparer_nom_fichier("Atelier_4_Modes_Transfert").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )




with tab5:
    st.header("Les Conducteurs et les Isolants Thermiques")
    st.write(
        "Comprenez pourquoi certains matériaux transmettent instantanément la chaleur alors "
        "que d'autres la bloquent, et découvrez la notion de conductivité thermique :"
    )

    # =============================================================================
    # 2. COURS TECHNIQUE : LA CONDUCTIVITÉ THERMIQUE (LAMBDA)
    # =============================================================================
    col_t5_h1, col_t5_h2 = st.columns(2)
    
    with col_t5_h1:
        st.markdown("##### Les Matériaux Conducteurs")
        st.write(
            "**La conductivité thermique ($\lambda$) :** C'est la grandeur physique qui caractérise la capacité "
            "d'un matériau à transmettre la chaleur. Elle s'exprime en Watts par mètre-Kelvin (W/(m.K)).\n\n"
            "**Les Métaux :** Les matériaux comme le cuivre, l'aluminium ou l'acier possèdent un $\lambda$ très élevé "
            "(supérieur à 50 W/(m.K)). Ils sont utilisés lorsqu'on cherche à évacuer rapidement la chaleur "
            "(radiateurs de refroidissement, échangeurs thermiques, ustensiles de cuisine)."
        )

        col_t51_h11, col_t51_h21 = st.columns(2)
        with col_t51_h11:
            col_t51_c1, col_t51_c2 = st.columns(2)
            with col_t51_c1:
                if os.path.exists("cuivre.jpg"):
                    st.image("cuivre.jpg", caption="Dissipateur cuivre", use_container_width=True)
                else:
                    st.warning("L'image 'cuivre.jpg' est introuvable.")
            with col_t51_c2:
                if os.path.exists("radiateur_m.jpg"):
                    st.image("radiateur_m.jpg", caption="Dissipateur alu", use_container_width=True)
                else:
                    st.warning("L'image 'radiateur_m.jpg' est introuvable.")
        with col_t51_h21:
            col_t51_c3, col_t51_c4 = st.columns(2)
            with col_t51_c3:
                if os.path.exists("acier.jpg"):
                    st.image("acier.jpg", caption="Barre d'acier", use_container_width=True)
                else:
                    st.warning("L'image 'acier.jpg' est introuvable.")
            with col_t51_c4:
                if os.path.exists("echangeur.jpg"):
                    st.image("echangeur.jpg", caption="Échangeur industriel", use_container_width=True)
                else:
                    st.warning("L'image 'echangeur.jpg' est introuvable.")
            
    with col_t5_h2:
        st.markdown("##### Les Matériaux Isolants")
        st.write(
            "**Les Isolants :** Un matériau est considéré comme un isolant thermique si sa conductivité thermique $\lambda$ "
            "is inférieure à 0,05 W/(m.K). Le secret d'un bon isolant réside presque toujours dans de l'air immobile emprisonné.\n\n"
            "**Exemples du bâtiment :** La laine de verre, le polystyrène expansé, le liège ou la ouate de cellulose "
            "bloquent la conduction car leurs structures empêchent les molécules d'air de se déplacer et de transmettre "
            "les chocs cinétiques thermiques."
        )

        col_t52_h31, col_t52_h32 = st.columns(2)
        with col_t52_h31:
            col_t52_c1, col_t52_c2 = st.columns(2)
            with col_t52_c1:
                if os.path.exists("laine_verre.jpg"):
                    st.image("laine_verre.jpg", caption="Laine de verre", use_container_width=True)
                else:
                    st.warning("L'image 'laine_verre.jpg' est introuvable.")
            with col_t52_c2:
                if os.path.exists("poly_exp.jpg"):
                    st.image("poly_exp.jpg", caption="Polystyrène", use_container_width=True)
                else:
                    st.warning("L'image 'poly_exp.jpg' est introuvable.")
        with col_t52_h32:
            col_t52_c3, col_t52_c4 = st.columns(2)
            with col_t52_c3:
                if os.path.exists("liege.jpg"):
                    st.image("liege.jpg", caption="Panneau de liège", use_container_width=True)
                else:
                    st.warning("L'image 'liege.jpg' est introuvable.")
            with col_t52_c4:
                if os.path.exists("double_vitrage.jpg"):
                    st.image("double_vitrage.jpg", caption="Lame d'air vitrage", use_container_width=True)
                else:
                    st.warning("L'image 'double_vitrage.jpg' est introuvable.")

    st.write("---")

    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE : LE BOUCLIER CONTRE LE FROID
    # =============================================================================
    col_gauche_texte_t5, col_droite_img_t5 = st.columns(2)

    with col_gauche_texte_t5:
        st.write(
            "**La BD humoristique textuelle : Le bouclier contre le froid**"
        )
        
        st.info(
            "**Cas 1 :** Au cœur d'une barre de cuivre, les électrons libres et les atomes sont collés les uns "
            "aux autres. Dès qu'un joule arrive, ils se le passent à toute vitesse : "
            "« Allez, ça file ! On est des conducteurs d'élite, la chaleur traverse à fond de train, "
            "notre lambda est immense ! ».\n\n"
            
            "**Cas 2 :** Face à eux, dans un panneau de laine de roche, les molécules d'air sont piégées "
            "dans des millions de petites alvéoles immobiles. La chaleur tente d'entrer : "
            "« Oh non, impossible de passer ! Les atomes sont isolés et ne peuvent pas s'entrechoquer. "
            "Le flux est totalement bloqué ! ».\n\n"
            
            "**Cas 3 :** Le froid hivernal arrive en force et percute la paroi extérieure de la maison. "
            "Il se heurte à la couche isolante protectrice : "
            "« Maudit matériau ! Mes calories ne peuvent pas s'échapper, l'isolant thermique fait office "
            "de bouclier impénétrable ! ».\n\n"
            
            "**Cas 4 :** À l'intérieur, la température reste stable et douce sans consommer d'énergie. "
            "Le système est protégé et le technicien sourit devant son bilan : "
            "« Affaire classée ! Un bon choix de conductivité thermique a sauvé nos joules et préservé "
            "le confort de l'habitation ! »."
        )

    with col_droite_img_t5:
        if os.path.exists("isolant_caricature.jpg"):
            st.image(
                "isolant_caricature.jpg",
                caption="Illustration humoristique du bouclier isolant",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'isolant_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")
    # =============================================================================
    # 3. LABORATOIRE VIRTUEL INTERACTIF : BANC D'ESSAI DES MATÉRIAUX
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Banc d'essai comparatif de conduction")
    st.write(
        "Sélectionnez différents matériaux de même épaisseur soumis à un même écart de température "
        "et observez l'impact direct de la valeur du lambda ($\lambda$) sur l'intensité du flux perdu :"
    )

    # Bibliothèque des valeurs réelles de conductivité thermique lambda
    catalogue_lambda = {
        "Cuivre pur (Métal très conducteur)": 390.0,
        "Aluminium (Métal conducteur)": 230.0,
        "Acier doux": 50.0,
        "Verre standard": 1.2,
        "Béton plein": 1.4,
        "Bois de sapin": 0.13,
        "Laine de verre (Isolant performant)": 0.035,
        "Polystyrène expansé (PSE)": 0.032,
        "Liège expansé": 0.040,
        "Air immobile (Théorique)": 0.026
    }

    t5_sim_mat = st.selectbox(
        "Sélectionnez le matériau à tester sur le banc d'essai :",
        list(catalogue_lambda.keys()),
        key="t5_sim_choix_mat"
    )

    lambda_choisi = catalogue_lambda[t5_sim_mat]

    # CONFIGURATION DES TROIS CURSEURS SÉPARÉS
    col_t5_p1, col_t5_p2, col_t5_p3 = st.columns(3)
    
    with col_t5_p1:
        t_interieur = st.slider("Température INTÉRIEURE (Face chaude - °C) :", min_value=15, max_value=50, value=25, key="t5_sim_tin_libre")
    with col_t5_p2:
        t_exterieur = st.slider("Température EXTÉRIEURE (Face froide - °C) :", min_value=-20, max_value=15, value=5, key="t5_sim_tout_libre")
    with col_t5_p3:
        t5_epaisseur = st.slider("Épaisseur de la paroi (e - centimètres) :", min_value=1, max_value=40, value=10, key="t5_sim_ep_libre")

    # Calcul rigoureux du gradient de température (dT) et du flux selon la loi de Fourier
    t5_dt = t_interieur - t_exterieur
    e_metres = t5_epaisseur / 100.0
    flux_surfacique = lambda_choisi * 1.0 * t5_dt / e_metres

    # Rendu du schéma Matplotlib vectoriel dynamique
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_banc, ax_ba = plt.subplots(figsize=(8, 2.5))
    
    # Couleur du bloc central proportionnelle au caractère isolant (Bleu isolant, Rouge conducteur)
    couleur_bloc_mat = "#94a3b8" if lambda_choisi > 1.0 else "#bae6fd"
    if lambda_choisi > 100: couleur_bloc_mat = "#fecdd3"

    # Dessin du banc d'essai
    ax_ba.add_patch(patches.Rectangle((0.5, 0.4), 1.2, 1.6, color="#ef4444", alpha=0.7)) # Côté chaud
    ax_ba.add_patch(patches.Rectangle((1.7, 0.4), 1.5, 1.6, color=couleur_bloc_mat, edgecolor='#1e293b', lw=1.5)) # Le matériau
    ax_ba.add_patch(patches.Rectangle((3.2, 0.4), 1.2, 1.6, color="#3b82f6", alpha=0.7)) # Côté froid

    # AFFICHAGE DYNAMIQUE DES DEUX TEMPÉRATURES LIBRES SUR LE SCHÉMA
    ax_ba.text(1.1, 1.2, f"Intérieur\n{t_interieur}°C", color="white", fontweight="bold", ha="center", va="center", fontsize=8)
    
    # Extraire proprement le nom court du matériau
    nom_court_mat = t5_sim_mat.split(" (")[0]
    ax_ba.text(2.45, 1.2, f"{nom_court_mat}\n{t5_epaisseur} cm\n$\lambda$ = {lambda_choisi:.3f}", color="#0f172a", fontweight="bold", ha="center", va="center", fontsize=8)
    
    ax_ba.text(3.8, 1.2, f"Extérieur\n{t_exterieur}°C", color="white", fontweight="bold", ha="center", va="center", fontsize=8)

    # Flèche de flux proportionnelle
    taille_fleche = min(12.0, max(1.5, flux_surfacique / 1000.0)) if lambda_choisi > 0.1 else 1.0
    ax_ba.arrow(4.6, 1.2, 1.5, 0, head_width=0.2, head_length=0.2, fc="#475569", ec="#475569", lw=taille_fleche)
    ax_ba.text(5.3, 1.5, "Flux traversant", color="#475569", fontsize=9, fontweight="bold", ha="center")

    ax_ba.set_xlim(0, 6.8)
    ax_ba.set_ylim(0, 2.4)
    ax_ba.axis('off')
    st.pyplot(fig_banc)

    # =============================================================================
    # CALCUL ET AFFICHAGE DÉTAILLÉ DE LA DÉPERDITION THERMIQUE
    # =============================================================================
    st.markdown("**Calcul de la déperdition thermique surfacique :**")
    st.latex(
        r"\Phi = \frac{\lambda \times \Delta T}{e} = "
        rf"\frac{{{lambda_choisi:.3f} \times ({t_interieur} - {t_exterieur})}}{{{e_metres:.3f}\text{{ m}}}}"
    )
    
    html_deperdition_box = (
        f"<div style='background-color: #f1f5f9; padding: 15px; border-radius: 6px; "
        f"border-left: 4px solid #0f172a; font-size: 16px; font-weight: bold; color: #0f172a; text-align: center;'>"
        f"Déperdition thermique calculée : {flux_surfacique:.1f} Watts par mètre carré (W/m²)"
        f"</div>"
    )
    st.markdown(html_deperdition_box, unsafe_allow_html=True)
    st.write("---")

    st.write("---")
    if "suite_verrouille_tab5_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab5_therm = False
    verrou_at5 = st.session_state.suite_verrouille_tab5_therm

    # Affichage du module de questions spécifique à l'Atelier des Conducteurs et Isolants
    afficher_atelier_isolants_verrouille(verrouille=verrou_at5)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur les Conducteurs et Isolants.",
        key="check_certif_therm5_final_net",
        disabled=verrou_at5,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5",
        key="btn_export_suite5_therm_official",
        use_container_width=True,
        disabled=verrou_at5,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q5 = 0.0
            if "ordre_quiz_tab5_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t5 = 0.0
            if "champs_therm5_clean" in st.session_state:
                for ligne in st.session_state.champs_therm5_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm5_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t5 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite5_therm_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_therm_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5_therm = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5_therm = True
            st.st_rerun() if hasattr(st, "st_rerun") else st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab5_therm", False):
        from datetime import datetime
        scr1_t5 = st.session_state.get("score_suite5_therm_p1", 0.0)
        scr2_t5 = st.session_state.get("score_suite5_therm_p2", 0.0)
        tot_s_t5 = st.session_state.get("score_final_suite5_therm", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER CONDUCTEURS ET ISOLANTS SCELLÉ | Note de session : {tot_s_t5:.1f} / 20")

        html_export_therm5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Conducteurs Isolants - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 5 : Analyse de la conductivité thermique, des conducteurs et des isolants</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s_t5:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm5 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm5_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm5_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm5_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm5 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm5 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 5 (.HTML)",
            data=html_export_therm5,
            file_name=preparer_nom_fichier("Atelier_5_Conducteurs_Isolants").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )


with tab6:
    st.header("La Quantité de Chaleur et la Capacité Thermique")
    
    st.write(
        "**Définition :** La quantité de chaleur sensible ($Q$, exprimée en Joules) absorbée ou cédée par un corps "
        "lors d'une variation de température dépend de sa masse ($m$), de l'écart de température ($\Delta T$) "
        "et d'une grandeur propre à sa nature chimique appelée la **capacité thermique massique** ($c$, exprimée en $\\text{J}/(\\text{kg}\\cdot\\text{K})$)."
    )


    # =============================================================================
    # 2. COURS HISTORIQUE ET TECHNIQUE : L'ÉQUATION FONCTIONNELLE
    # =============================================================================
    col_t6_h1, col_t6_h2 = st.columns(2)
    
    with col_t6_h1:
        st.markdown("##### La Notion de Chaleur Sensible")
        st.write(
            "**L'Équation Fondamentale :** Lorsqu'un corps ne change pas d'état physique (il reste liquide ou solide), "
            "l'apport de chaleur modifie sa température. On parle alors de **chaleur sensible**.\n\n"
            "**L'influence de la nature chimique :** Chaque corps réagit différemment à l'apport d'énergie. "
            "L'eau pure a une capacité thermique exceptionnellement élevée ($c = 4180\\text{ J}/(\\text{kg}\\cdot\\text{K})$), "
            "ce qui en fait un excellent fluide caloporteur pour stocker ou transporter la chaleur dans les chauffages centraux."
        )

        col_t61_h11, col_t61_h21 = st.columns(2)
        with col_t61_h11:
            col_t61_c1, col_t61_c2 = st.columns(2)
            with col_t61_c1:
                if os.path.exists("eau_calorique.jpg"):
                    st.image("eau_calorique.jpg", caption="Eau caloporteuse", use_container_width=True)
                else:
                    st.warning("L'image 'eau_calorique.jpg' est introuvable.")
            with col_t61_c2:
                if os.path.exists("cuve_stockage.jpg"):
                    st.image("cuve_stockage.jpg", caption="Stockage thermique", use_container_width=True)
                else:
                    st.warning("L'image 'cuve_stockage.jpg' est introuvable.")
        with col_t61_h21:
            col_t61_c3, col_t61_c4 = st.columns(2)
            with col_t61_c3:
                if os.path.exists("chauffage_central.jpg"):
                    st.image("chauffage_central.jpg", caption="Circuit de chauffage", use_container_width=True)
                else:
                    st.warning("L'image 'chauffage_central.jpg' est introuvable.")
            with col_t61_c4:
                if os.path.exists("inertie_sol.jpg"):
                    st.image("inertie_sol.jpg", caption="Inertie des chapes", use_container_width=True)
                else:
                    st.warning("L'image 'inertie_sol.jpg' est introuvable.")
            
    with col_t6_h2:
        st.markdown("##### Les Constantes des Solides et Métaux")
        st.write(
            "**Le comportement des métaux :** Contrairement à l'eau, les métaux possèdent des capacités thermiques "
            "massiques très faibles (généralement inférieures à $900\\text{ J}/(\\text{kg}\\cdot\\text{K})$).\n\n"
            "**Conséquence sur le thermomètre :** À cause de cette faible valeur, une toute petite quantité de "
            "chaleur provoque une élévation de température fulgurante du métal. C'est pourquoi les ustensiles "
            "de cuisine métalliques deviennent brûlants presque instantanément au contact d'une plaque de cuisson."
        )

        col_t62_h31, col_t62_h32 = st.columns(2)
        with col_t62_h31:
            col_t62_c1, col_t62_c2 = st.columns(2)
            with col_t62_c1:
                if os.path.exists("bloc_metal.jpg"):
                    st.image("bloc_metal.jpg", caption="Inertie métallique", use_container_width=True)
                else:
                    st.warning("L'image 'bloc_metal.jpg' est introuvable.")
            with col_t62_c2:
                if os.path.exists("poele_cuisine.jpg"):
                    st.image("poele_cuisine.jpg", caption="Ustensiles de cuisine", use_container_width=True)
                else:
                    st.warning("L'image 'poele_cuisine.jpg' est introuvable.")
        with col_t62_h32:
            col_t62_c3, col_t62_c4 = st.columns(2)
            with col_t62_c3:
                if os.path.exists("fusion_industrie.jpg"):
                    st.image("fusion_industrie.jpg", caption="Chauffage industriel", use_container_width=True)
                else:
                    st.warning("L'image 'fusion_industrie.jpg' est introuvable.")
            with col_t62_c4:
                if os.path.exists("calculateur_j.jpg"):
                    st.image("calculateur_j.jpg", caption="Mesure de l'énergie", use_container_width=True)
                else:
                    st.warning("L'image 'calculateur_j.jpg' est introuvable.")



    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE : LA SOIF DE JOULES DES ATOMES
    # =============================================================================
    col_gauche_texte_t6, col_droite_img_t4 = st.columns(2)

    with col_gauche_texte_t6:
        st.write(
            "**La BD humoristique textuelle : La soif de joules des atomes**"
        )
        
        st.info(
            "**Cas 1 :** Un kilogramme d'eau pure dort paisiblement à 20 °C dans une casserole. "
            "Ses atomes demandent énormément d'énergie pour daigner s'agiter d'un seul petit degré : "
            "« Attention, on est l'eau ! Notre capacité thermique massique est gigantesque, il nous faut "
            "4 180 Joules pour grimper de 1 °C, préparez les brûleurs ! ».\n\n"
            
            "**Cas 2 :** Juste à côté, un bloc d'un kilogramme de plomb reçoit la même flamme. "
            "Ses atomes, beaucoup moins gourmands, s'excitent instantanément : "
            "« Oh, c'est trop facile pour nous ! Avec notre petit $c$ de 130 Joules, la moindre étincelle "
            "nous fait surchauffer, on grimpe en température à toute vitesse ! ».\n\n"
            
            "**Cas 3 :** L'enseignant jette un coup d'œil au thermomètre et prépare le calcul de l'énergie "
            "totale reçue par le système en multipliant tout le monde : "
            "« C'est l'heure de l'addition ! Masse, capacité et thermomètre, tout le monde s'aligne "
            "dans l'équation magique $Q = m \cdot c \cdot \Delta T$ ! ».\n\n"
            
            "**Cas 4 :** L'énergie a été entièrement transférée, l'eau bout et le plomb est brûlant. "
            "Le compteur de Joules s'arrête net sur la valeur exacte calculée : "
            "« Affaire classée ! La matière a absorbé son quota exact de calories, les lois de la calorimétrie "
            "ont encore frappé avec une précision atomique ! »."
        )

    with col_droite_img_t4:
        if os.path.exists("quantite_caricature.jpg"):
            st.image(
                "quantite_caricature.jpg",
                caption="Illustration humoristique de l'absorption thermique",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'quantite_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")
    # =============================================================================
    # 3. LABORATOIRE VIRTUEL INTERACTIF : ESTIMATEUR D'ÉNERGIE CHALEUR
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de calcul de quantité de chaleur")
    st.write(
        "Sélectionnez un corps, ajustez sa masse ainsi que ses températures initiale "
        "et finale pour calculer en direct l'énergie thermique totale requise :"
    )

    # Référentiel des constantes c réelles
    catalogue_capacites = {
        "Eau pure (Fluide caloporteur haut de gamme)": 4180,
        "Lait entier": 3890,
        "Bière standard": 4050,
        "Éthanol (Alcool pur)": 2440,
        "Huile végétale de cuisine": 2000,
        "Glace d'eau (-10°C)": 2100,
        "Béton de construction": 880,
        "Verre blanc": 840,
        "Aluminium pur": 897,
        "Acier doux standard": 450,
        "Cuivre pur": 385,
        "Plomb massif": 130
    }

    t6_sim_corps = st.selectbox(
        "Sélectionnez le corps à chauffer ou refroidir :",
        list(catalogue_capacites.keys()),
        key="t6_sim_choix_corps"
    )

    c_physique = catalogue_capacites[t6_sim_corps]

    col_t6_p1, col_t6_p2, col_t6_p3 = st.columns(3)
    with col_t6_p1:
        t6_masse = st.slider("Masse du corps à étudier (m en kg) :", min_value=0.1, max_value=10.0, value=1.0, step=0.1, key="t6_sim_m")
    with col_t6_p2:
        t6_t_init = st.slider("Température INITIALE (Ti en °C) :", min_value=-20, max_value=100, value=20, key="t6_sim_ti")
    with col_t6_p3:
        t6_t_final = st.slider("Température FINALE (Tf en °C) :", min_value=-20, max_value=100, value=60, key="t6_sim_tf")

    # Calcul de la quantité de chaleur sensible
    t6_delta_t = t6_t_final - t6_t_init
    chaleur_joules = t6_masse * c_physique * t6_delta_t
    chaleur_kilojoules = chaleur_joules / 1000.0

    # Rendu du schéma Matplotlib vectoriel
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_quantite, ax_q = plt.subplots(figsize=(8.5, 2.5))
    
    # Couleur du contenant proportionnelle à la température finale
    couleur_thermique = "#3b82f6" if t6_t_final < 25 else "#ef4444"
    
    # Dessin de l'enceinte de chauffage calorimétrique
    ax_q.add_patch(patches.Rectangle((1.0, 0.4), 2.5, 1.5, facecolor='#f1f5f9', edgecolor='#1e293b', lw=2))
    ax_q.add_patch(patches.Rectangle((1.2, 0.4), 2.1, 1.1 * (t6_masse / 10.0) + 0.2, color=couleur_thermique, alpha=0.6))
    
    # Extraction propre du nom du corps pour l'affichage textuel interne
    nom_court_corps = t6_sim_corps.split(" (")[0]
    ax_q.text(2.25, 1.1, f"{nom_court_corps}\n{t6_masse:.1f} kg", color='#0f172a', fontweight='bold', ha='center', fontsize=9)
    
    # Flèche d'apport ou de libération d'énergie (Flux de chaleur)
    if chaleur_joules >= 0:
        ax_q.arrow(4.5, 1.15, 1.2, 0, head_width=0.15, head_length=0.15, fc='#ef4444', ec='#ef4444', lw=2.5)
        ax_q.text(5.1, 1.4, f"Chaleur absorbée\n+ {abs(chaleur_kilojoules):.1f} kJ", color='#b91c1c', fontsize=9, fontweight='bold', ha='center')
    else:
        ax_q.arrow(5.7, 1.15, -1.2, 0, head_width=0.15, head_length=0.15, fc='#3b82f6', ec='#3b82f6', lw=2.5)
        ax_q.text(5.1, 1.4, f"Chaleur cédée\n- {abs(chaleur_kilojoules):.1f} kJ", color='#1d4ed8', fontsize=9, fontweight='bold', ha='center')

    ax_q.set_xlim(0, 7.5)
    ax_q.set_ylim(0, 2.3)
    ax_q.axis('off')
    st.pyplot(fig_quantite)

    # Démonstration du calcul de l'équation physique
    st.markdown("**Formule littérale et application numérique :**")
    st.latex(
        r"Q = m \times c \times (T_f - T_i) = "
        rf"{t6_masse:.1f}\text{{ kg}} \times {c_physique} \times ({t6_t_final} - {t6_t_init}) = {chaleur_joules:,.1f}\text{{ Joules}}"
    )

    st.write("---")
    if "suite_verrouille_tab6_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab6_therm = False
    verrou_at6 = st.session_state.suite_verrouille_tab6_therm

    # Affichage du module de questions spécifique à l'Atelier de la Quantité de Chaleur
    afficher_atelier_quantite_verrouille(verrouille=verrou_at6)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 6")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Quantité de Chaleur.",
        key="check_certif_therm6_final_net",
        disabled=verrou_at6,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6",
        key="btn_export_suite6_therm_official",
        use_container_width=True,
        disabled=verrou_at6,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q6 = 0.0
            if "ordre_quiz_tab6_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab6_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q6 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t6 = 0.0
            if "champs_therm6_clean" in st.session_state:
                for ligne in st.session_state.champs_therm6_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm6_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t6 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite6_therm_p1 = round(float(score_q6), 1)
            st.session_state.score_suite6_therm_p2 = round(float(score_t6), 1)
            st.session_state.score_final_suite6_therm = round(float(score_q6 + score_t6), 1)
            st.session_state.suite_verrouille_tab6_therm = True
            st.st_rerun() if hasattr(st, "st_rerun") else st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab6_therm", False):
        from datetime import datetime
        scr1_t6 = st.session_state.get("score_suite6_therm_p1", 0.0)
        scr2_t6 = st.session_state.get("score_suite6_therm_p2", 0.0)
        tot_s_t6 = st.session_state.get("score_final_suite6_therm", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER QUANTITÉ DE CHALEUR SCELLÉ | Note de session : {tot_s_t6:.1f} / 20")

        html_export_therm6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Quantité de Chaleur - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 6 : Formulation mathématique et calcul de la quantité de chaleur sensible</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s_t6:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab6_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm6 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm6_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm6_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm6_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm6 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm6 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 6 (.HTML)",
            data=html_export_therm6,
            file_name=preparer_nom_fichier("Atelier_6_Quantite_Chaleur").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )

with tab7:
    st.header("Le Coefficient de Transmission Thermique (U)")
    
    # =============================================================================
    # DÉFINITION TECHNIQUE DE L'ATELIER 7
    # =============================================================================
    st.write(
        "**Définition :** Le **coefficient de transmission thermique** (noté $U$ et exprimé en Watts par mètre carré-Kelvin, $\\text{W}/(\\text{m}^2\\cdot\\text{K})$) "
        "caractérise la performance thermique globale d'une paroi ou d'une structure. Il indique la quantité de chaleur "
        "qui traverse une surface de $1\\text{ m}^2$ de cette paroi pour un écart de température de $1\\text{ degré}$ entre l'intérieur et l'extérieur.\n\n"
        "Pour une paroi simple d'épaisseur $e$ (en mètres) et de conductivité thermique $\lambda$, il est inversement proportionnel à sa résistance :"
    )
    st.latex(r"U = \frac{1}{R_t} = \frac{\lambda}{e}")
    st.write("---")


    # =============================================================================
    # 2. COURS TECHNIQUE : L'INTERPRÉTATION DU COEFFICIENT U
    # =============================================================================
    col_t7_h1, col_t7_h2 = st.columns(2)
    
    with col_t7_h1:
        st.markdown("##### Les Parois à Fort Coefficient U")
        st.write(
            "**Une structure dissipative :** Un coefficient $U$ élevé indique qu'un matériau laisse "
            "librement passer le flux thermique. C'est le cas des matériaux denses non isolés (béton banché, vitrages simples, tôles métalliques).\n\n"
            "**Conséquences directes :** Ces parois génèrent d'importantes déperditions de chaleur en hiver. "
            "Elles provoquent également le phénomène inconfortable de 'paroi froide', où la surface intérieure des murs "
            "est glaciale, ce qui favorise la condensation de l'humidité ambiante."
        )

        col_t71_h11, col_t71_h21 = st.columns(2)
        with col_t71_h11:
            col_t71_c1, col_t71_c2 = st.columns(2)
            with col_t71_c1:
                if os.path.exists("passoire_thermique.jpg"):
                    st.image("passoire_thermique.jpg", caption="Paroi dissipative", use_container_width=True)
                else:
                    st.warning("L'image 'passoire_thermique.jpg' est introuvable.")
            with col_t71_c2:
                if os.path.exists("simple_vitrage.jpg"):
                    st.image("simple_vitrage.jpg", caption="Simple vitrage nu", use_container_width=True)
                else:
                    st.warning("L'image 'simple_vitrage.jpg' est introuvable.")
        with col_t71_h21:
            col_t71_c3, col_t71_c4 = st.columns(2)
            with col_t71_c3:
                if os.path.exists("condensation_mur.jpg"):
                    st.image("condensation_mur.jpg", caption="Condensation de surface", use_container_width=True)
                else:
                    st.warning("L'image 'condensation_mur.jpg' est introuvable.")
            with col_t71_c4:
                if os.path.exists("beton_nu.jpg"):
                    st.image("beton_nu.jpg", caption="Mur en béton plein", use_container_width=True)
                else:
                    st.warning("L'image 'beton_nu.jpg' est introuvable.")
            
    with col_t7_h2:
        st.markdown("##### Les Parois à Faible Coefficient U")
        st.write(
            "**L'objectif de performance (RE2020) :** Pour concevoir des bâtiments économes en énergie, "
            "les ingénieurs cherchent à abaisser au maximum la valeur de $U$. Les murs extérieurs actuels visent "
            "généralement un $U \\le 0,22\\text{ W}/(\\text{m}^2\\cdot\\text{K})$.\n\n"
            "**Comment y parvenir :** Cela nécessite d'associer des matériaux de structure à de fortes épaisseurs "
            "d'isolants performants (laine minérale, polyuréthane). Réduire le coefficient $U$ permet de maintenir "
            "la chaleur à l'intérieur et de supprimer les ponts thermiques structurels."
        )

        col_t72_h31, col_t72_h32 = st.columns(2)
        with col_t72_h31:
            col_t72_c1, col_t72_c2 = st.columns(2)
            with col_t72_c1:
                if os.path.exists("isolation_exterieure.jpg"):
                    st.image("isolation_exterieure.jpg", caption="Pose d'un isolant", use_container_width=True)
                else:
                    st.warning("L'image 'isolation_exterieure.jpg' est introuvable.")
            with col_t72_c2:
                if os.path.exists("re2020_batiment.jpg"):
                    st.image("re2020_batiment.jpg", caption="Bâtiment basse conso", use_container_width=True)
                else:
                    st.warning("L'image 're2020_batiment.jpg' est introuvable.")
        with col_t72_h32:
            col_t72_c3, col_t72_c4 = st.columns(2)
            with col_t72_c3:
                if os.path.exists("camera_thermique.jpg"):
                    st.image("camera_thermique.jpg", caption="Contrôle infrarouge", use_container_width=True)
                else:
                    st.warning("L'image 'camera_thermique.jpg' est introuvable.")
            with col_t72_c4:
                if os.path.exists("double_vitrage_performance.jpg"):
                    st.image("double_vitrage_performance.jpg", caption="Vitrage isolant", use_container_width=True)
                else:
                    st.warning("L'image 'double_vitrage_performance.jpg' est introuvable.")

    st.write("---")

    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE EN 4 CASES : LA FUITE DES WATTS
    # =============================================================================
    col_gauche_texte_t7, col_droite_img_t7 = st.columns(2)

    with col_gauche_texte_t7:
        st.write(
            "**La BD humoristique textuelle : La fuite des Watts**"
        )
        
        st.info(
            "**Cas 1 : Le passoire thermique.** Une vieille vitre simple vitrage de 4 mm sépare le salon chauffé du jardin gelé. "
            "Les calories s'approchent en courant du vitrage : "
            "« Chic alors ! Regardez ce coefficient $U$ immense de 5,8 W/(m².K) ! C'est une véritable autoroute, "
            "on va s'échapper vers l'extérieur sans aucun effort ! ».\n\n"
            
            "**Cas 2 : Le barrage du double vitrage.** Juste à côté, un double vitrage moderne à isolation renforcée barre la route : "
            "« Halte-là, les Joules ! Notre coefficient $U$ a été rabaissé à seulement 1,1 W/(m².K). "
            "La fuite est coupée, vous restez sagement à l'intérieur pour chauffer la maison ! ».\n\n"
            
            "**Cas 3 : L'analyse de l'expert.** Le technicien de maintenance examine la façade à la caméra thermique : "
            "« Plus la valeur du coefficient $U$ est proche de zéro, plus la paroi est performante et retient l'énergie. "
            "C'est la règle d'or de la rénovation énergétique ! ».\n\n"
            
            "**Cas 4 : Le triomphe de l'isolation.** Grâce aux parois à faible émission, la facture de chauffage s'effondre. "
            "Le compteur d'énergie se stabilise : "
            "« Affaire classée ! Le contrôle du coefficient de transmission a dompté le flux perdu. "
            "Les calories sont sous haute surveillance ! »."
        )

    with col_droite_img_t7:
        if os.path.exists("transmission_caricature.jpg"):
            st.image(
                "transmission_caricature.jpg",
                caption="Illustration humoristique du coefficient de transmission thermique global",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'transmission_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")
    st.subheader("Laboratoire Virtuel : Analyseur dynamique multicouche - Maison individuelle de 130 m²")
    st.write(
        "Modélisez les déperditions thermiques globales d'une maison de plein pied de 130 m² au sol. "
        "Ajustez la composition des parois et les températures pour évaluer la puissance requise et l'énergie consommée sur 24h :"
    )

    # Référentiel des conductivités thermiques lambda réelles
    catalogue_materiaux = {
        # --- ISOLANTS THERMIQUES INNOVANTS ET ÉCOLOGIQUES ---
        "Mousse de polyuréthane (Isolant d'élite)": 0.024,
        "Polystyrène extrudé (XPS)": 0.029,
        "Polystyrène expansé (PSE)": 0.032,
        "Isolant en fibre de coton (Coton recyclé / Métisse)": 0.039,
        "Isolant en ouate de cellulose": 0.039,
        "Laine de verre (Isolant minéral standard)": 0.035,
        "Laine de roche en panneau": 0.038,
        "Fibre de bois semi-rigide": 0.040,
        "Liège expansé en plaque": 0.042,
        "Film thermo-réflecteur mince (Isolant mince multicouche)": 0.033,
        
        # --- BOIS ET MATÉRIAUX BIOSSOURCÉS ---
        "Bois de sapin / résineux": 0.13,
        "Bois dur (Chêne / Hêtre)": 0.18,
        "Panneau de particules (OSB / Contreplaqué)": 0.14,
        "Béton de chanvre": 0.07,
        
        # --- BRIQUES ET BLOCS DE CONSTRUCTION ---
        "Béton cellulaire (Siporex / Thermopierre)": 0.12,
        "Brique de terre cuite creuse isolante (Monomur)": 0.14,
        "Brique de terre cuite creuse standard": 0.45,
        "Bloc de béton de granulats légers (Ponce)": 0.35,
        "Bloc de béton de granulats (Parpaing creux)": 1.05,
        "Brique de terre cuite pleine": 1.15,
        "Brique de terre crue compressée (Adobe)": 1.00,
        
        # --- BÉTONS, LIANTS ET ENDUITS ---
        "Béton de pierre ponce": 0.40,
        "Plâtre / Plaque de plâtre (BA13)": 0.25,
        "Enduit de façade extérieur (Mortier de ciment)": 1.15,
        "Béton plein standard": 1.75,
        "Béton armé plein (Forte densité)": 2.30,
        
        # --- ROCHES ET PIERRES NATURELLES ---
        "Pierre calcaire tendre": 1.40,
        "Ardoise de couverture": 2.20,
        "Pierre calcaire dure (Pierre de taille)": 2.80,
        "Granit / Grès massif": 3.00,
        
        # --- AUTRES MATÉRIAUX DE PAROI ---
        "Verre de vitrage standard": 1.20,
        "Lame d'air immobile (Théorique)": 0.026
    }
    
    # --- 1. CONFIGURATION DE L'ENVIRONNEMENT DE LA MAISON DE 130 M² ---
    col_env1, col_env2 = st.columns(2)
    with col_env1:
        t_int_libre = st.slider("Température INTÉRIEURE désirée dans la maison (°C) :", min_value=15, max_value=30, value=20, key="t7_adv_tint")
    with col_env2:
        t_ext_libre = st.slider("Température EXTÉRIEURE hivernale (°C) :", min_value=-20, max_value=20, value=0, key="t7_adv_text")

    # Modélisation géométrique d'une maison de plein pied de 130 m² (hauteur sous plafond 2.5m)
    # Surface enveloppe déperditive = Murs périphériques (114 m²) + Toiture de plein pied (130 m²) = 244 m²
    surface_enveloppe_totale = 244.0

    st.info(
        "Caractéristiques structurelles de l'habitation : Maison de plein pied d'une surface habitable de 130 m². "
        "La surface totale développée des parois en contact avec l'extérieur (murs et toiture) est estimée à 244 m²."
    )

    # --- 2. CONFIGURATION DYNAMIQUE JUSQU'À 6 COUCHES ---
    st.markdown("##### Composition des parois de l'enveloppe (de l'Intérieur vers l'Extérieur) :")
    nb_couches = st.radio("Nombre de couches constituant la paroi :", [1, 2, 3, 4, 5, 6], index=2, horizontal=True, key="t7_adv_nb_c")
    
    r_total_paroi = 0.0
    epaisseurs_visuelles = []
    # Palette de couleurs étendue pour différencier jusqu'à 6 couches de manière esthétique
    couleurs_visuelles = ["#f8fafc", "#cbd5e1", "#e2e8f0", "#94a3b8", "#64748b", "#475569"]
    labels_visuels = []

    # Génération en grilles dynamiques de 3 colonnes pour gérer proprement l'affichage de 6 lignes de curseurs
    lignes_boutons = int(np.ceil(int(nb_couches) / 3))
    for l in range(lignes_boutons):
        cols_c = st.columns(3)
        for idx_col in range(3):
            i = l * 3 + idx_col
            if i < int(nb_couches):
                with cols_c[idx_col]:
                    st.markdown(f"**Couche {i+1}**")
                    mat_c = st.selectbox(
                        f"Matériau :", 
                        list(catalogue_materiaux.keys()), 
                        index=min(i * 2 + 3, len(catalogue_materiaux) - 1) if i > 0 else 5,
                        key=f"t7_adv_mat_{i}"
                    )
                    ep_c = st.slider(f"Épaisseur (cm) :", min_value=1, max_value=40, value=15 if i < 2 else 2, key=f"t7_adv_ep_{i}")
                    
                    lambda_c = catalogue_materiaux[mat_c]
                    e_m_c = ep_c / 100.0
                    r_c = e_m_c / lambda_c
                    r_total_paroi += r_c
                    
                    epaisseurs_visuelles.append(ep_c)
                    labels_visuels.append(f"Couche {i+1}\n{ep_c} cm")

    # Échanges superficiels réglementaires (Rsi + Rse = 0.17 m².K/W)
    r_total_global = r_total_paroi + 0.17
    u_global_composé = 1.0 / r_total_global
    delta_t_libre = t_int_libre - t_ext_libre
    
    # Calculs de flux et d'énergie pour la structure de 130 m²
    flux_surfacique_w = u_global_composé * delta_t_libre
    puissance_totale_perdue_w = flux_surfacique_w * surface_enveloppe_totale
    energie_24h_kwh = (puissance_totale_perdue_w * 24.0) / 1000.0

    # Constante de temps d'équilibre thermique de la maison de 130 m²
    capacite_thermique_maison = 780000.0
    if puissance_totale_perdue_w > 0:
        tau_secondes = capacite_thermique_maison / (u_global_composé * surface_enveloppe_totale)
        temps_equilibre_heures = (3.0 * tau_secondes) / 3600.0
    else:
        temps_equilibre_heures = 0.0

    # --- 3. RENDU GRAPHIQUE DES 6 COUCHES ---
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_multi, ax_mu = plt.subplots(figsize=(10, 3.0))
    
    ax_mu.add_patch(patches.Rectangle((0.0, 0.4), 1.5, 1.6, color="#ef4444", alpha=0.5))
    ax_mu.text(0.75, 1.2, f"Maison\n{t_int_libre} °C", color="#b91c1c", fontweight="bold", ha="center", va="center", fontsize=9)

    x_depart = 1.5
    for idx, ep_cm in enumerate(epaisseurs_visuelles):
        # Adaptation proportionnelle de l'échelle horizontale pour faire tenir proprement 6 couches à l'écran
        largeur_visuelle = 0.3 + (ep_cm / 40.0) * 0.8
        ax_mu.add_patch(patches.Rectangle((x_depart, 0.4), largeur_visuelle, 1.6, facecolor=couleurs_visuelles[idx], edgecolor='#0f172a', lw=1.5))
        ax_mu.text(x_depart + (largeur_visuelle / 2), 1.2, labels_visuels[idx], color='#0f172a', fontweight='bold', ha='center', va='center', fontsize=7.5)
        x_depart += largeur_visuelle

    ax_mu.add_patch(patches.Rectangle((x_depart, 0.4), 1.5, 1.6, color="#3b82f6", alpha=0.5))
    ax_mu.text(x_depart + 0.75, 1.2, f"Extérieur\n{t_ext_libre} °C", color="#1d4ed8", fontweight="bold", ha="center", va="center", fontsize=9)

    taille_fleche_adv = min(15.0, max(1.5, puissance_totale_perdue_w / 500.0)) if delta_t_libre > 0 else 1.2
    ax_mu.arrow(0.5, 0.6, x_depart + 0.5, 0, head_width=0.15, head_length=0.15, fc='#475569', ec='#475569', lw=taille_fleche_adv)

    ax_mu.set_xlim(-0.2, x_depart + 1.7)
    ax_mu.set_ylim(0, 2.4)
    ax_mu.axis('off')
    st.pyplot(fig_multi)

    # --- 4. PANNEAU DES MESURES DYNAMIQUES ET METRICS ---
    st.markdown("##### Bilan Énergétique Global de l'Habitation :")
    c_res1, c_res2, c_res3 = st.columns(3)
    with c_res1:
        st.metric(label="Coefficient Global U de l'enveloppe", value=f"{u_global_composé:.3f} W/(m².K)")
    with c_res2:
        st.metric(label="Déperdition de puissance instantanée", value=f"{puissance_totale_perdue_w:.1f} Watts")
    with c_res3:
        st.metric(label="Résistance Thermique Totale R_tot", value=f"{r_total_global:.3f} m².K/W")

    html_bilan_24h = f"""
    <div style="background-color: #f8fafc; padding: 16px; border-radius: 8px; border: 1px solid #e2e8f0; margin-top: 10px;">
        <p style="margin: 0; font-size: 14px; color: #1e293b;">
            <b>Énergie nécessaire sur une journée de 24 heures</b> pour maintenir la maison à {t_int_libre}°C : 
            <span style="color: #b91c1c; font-size: 16px; font-weight: bold;">{energie_24h_kwh:.2f} kWh</span>
        </p>
        <p style="margin: 8px 0 0 0; font-size: 14px; color: #1e293b;">
            <b>Temps estimé pour atteindre l'équilibre avec l'extérieur</b> (si coupure totale du chauffage) : 
            <span style="color: #1d4ed8; font-size: 16px; font-weight: bold;">{temps_equilibre_heures:.1f} heures</span>
        </p>
    </div>
    """
    st.markdown(html_bilan_24h, unsafe_allow_html=True)

    # --- 5. DÉTAIL DES ÉQUATIONS DE TRANSMISSION ET APPLICATIONS NUMÉRIQUES ---
    st.markdown("**Détail des calculs de physique thermique (Maison de 130 m² - Multicouche) :**")

    st.markdown("1. Résistance thermique globale des parois ($R_{\\text{total}} = R_{si} + \\sum \\frac{e_i}{\\lambda_i} + R_{se}$) :")
    expression_r = "R_{\\text{total}} = 0{,}13"
    for i in range(int(nb_couches)):
        mat_nom = st.session_state.get(f"t7_adv_mat_{i}", list(catalogue_materiaux.keys())[5])
        l_val = catalogue_materiaux[mat_nom]
        ep_cm = st.session_state.get(f"t7_adv_ep_{i}", 10)
        expression_r += rf" + \frac{{{ep_cm/100:.3f}}}{{{l_val:.3f}}}"
    expression_r += rf" + 0{{,}}04 = {r_total_global:.3f}\text{{ m}}^2\cdot\text{{K}}/\text{{W}}"
    st.latex(expression_r)

    st.markdown("2. Puissance thermique instantanée perdue par l'enveloppe de 244 m² :")
    formule_phi = rf"\Phi = U \times A \times (T_{{\text{{intérieur}}}} - T_{{\text{{extérieur}}}}) = {u_global_composé:.3f} \times {surface_enveloppe_totale} \times ({t_int_libre} - {t_ext_libre}) = {puissance_totale_perdue_w:.1f}\text{{ Watts}}"
    st.latex(formule_phi)

    st.markdown("3. Énergie totale consommée pour compenser les pertes sur une journée de 24 heures :")
    formule_e = rf"E_{{24\text{{h}}}} = \frac{{\Phi \times 24\text{{ h}}}}{{1000}} = \frac{{{puissance_totale_perdue_w:.1f} \times 24}}{{1000}} = {energie_24h_kwh:.2f}\text{{ kWh}}"
    st.latex(formule_e)
    st.write("---")

    
    
    if "suite_verrouille_tab7_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab7_therm = False
    verrou_at7 = st.session_state.suite_verrouille_tab7_therm

    # Affichage du module de questions spécifique à l'Atelier du Coefficient de Transmission
    afficher_atelier_transmission_verrouille(verrouille=verrou_at7)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 7")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat7 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur le Coefficient de Transmission.",
        key="check_certif_therm7_final_net",
        disabled=verrou_at7,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7",
        key="btn_export_suite7_therm_official",
        use_container_width=True,
        disabled=verrou_at7,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat7:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q7 = 0.0
            if "ordre_quiz_tab7_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab7_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q7 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t7 = 0.0
            if "champs_therm7_clean" in st.session_state:
                for ligne in st.session_state.champs_therm7_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm7_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t7 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite7_therm_p1 = round(float(score_q7), 1)
            st.session_state.score_suite7_therm_p2 = round(float(score_t7), 1)
            st.session_state.score_final_suite7_therm = round(float(score_q7 + score_t7), 1)
            st.session_state.suite_verrouille_tab7_therm = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab7_therm", False):
        from datetime import datetime
        scr1_t7 = st.session_state.get("score_suite7_therm_p1", 0.0)
        scr2_t7 = st.session_state.get("score_suite7_therm_p2", 0.0)
        tot_s_t7 = st.session_state.get("score_final_suite7_therm", 0.0)
        timestamp_suite7 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER COEFFICIENT DE TRANSMISSION SCELLÉ | Note de session : {tot_s_t7:.1f} / 20")

        html_export_therm7 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Coefficient Transmission - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 7 : Analyse et calcul du coefficient de transmission thermique global U</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t7:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t7:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t7:.1f} / 10</strong><br>
                Note Totale de l'Atelier 7 : <strong>{tot_s_t7:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab7_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab7_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm7 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm7 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm7_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm7_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm7_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm7 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm7 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 7 (.HTML)",
            data=html_export_therm7,
            file_name=preparer_nom_fichier("Atelier_7_Transmission_Thermique").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )


with tab8:
    st.header("La Résistance Thermique (R)")
    
    # =============================================================================
    # DÉFINITION TECHNIQUE DE L'ATELIER 8
    # =============================================================================
    st.write(
        "**Définition :** La **résistance thermique** (notée $R$ ou $R_t$, exprimée en mètres carrés-Kelvin par Watt, $\\text{m}^2\\cdot\\text{K}/\\text{W}$) "
        "caractérise la capacité d'une paroi matérielle à s'opposer au passage du flux de chaleur. "
        "Plus la valeur de la résistance thermique est grande, plus la paroi ralentit le transfert d'énergie et s'avère isolante.\n\n"
        "Pour une couche de matériau unique, elle dépend directement de son épaisseur $e$ (en mètres) et de sa conductivité thermique $\lambda$ :"
    )
    st.latex(r"R = \frac{e}{\lambda}")
    st.write("---")


    # =============================================================================
    # 2. COURS TECHNIQUE : L'IMPORTANCE DU COEFFICIENT R
    # =============================================================================
    col_t8_h1, col_t8_h2 = st.columns(2)
    
    with col_t8_h1:
        st.markdown("##### Les Faibles Résistances Thermiques")
        st.write(
            "**Une paroi passive :** Lorsque la valeur de $R$ est proche de zéro, la paroi n'oppose quasiment aucun "
            "obstacle à la chaleur. C'est le cas typique des métaux ou d'un simple vitrage mince.\n\n"
            "**Conséquences industrielles :** Une faible résistance thermique est recherchée lorsqu'on souhaite "
            "transférer ou dissiper de l'énergie au maximum (fond de poêle en cuivre, tubes de chaudière, dissipateurs thermiques de composants électroniques)."
        )

        col_t81_h11, col_t81_h21 = st.columns(2)
        with col_t81_h11:
            col_t81_c1, col_t81_c2 = st.columns(2)
            with col_t81_c1:
                if os.path.exists("faible_r.jpg"):
                    st.image("faible_r.jpg", caption="Paroi non isolante", use_container_width=True)
                else:
                    st.warning("L'image 'faible_r.jpg' est introuvable.")
            with col_t81_c2:
                if os.path.exists("dissipateur_circuit.jpg"):
                    st.image("dissipateur_circuit.jpg", caption="Refroidissement rapide", use_container_width=True)
                else:
                    st.warning("L'image 'dissipateur_circuit.jpg' est introuvable.")
        with col_t81_h21:
            col_t81_c3, col_t81_c4 = st.columns(2)
            with col_t81_c3:
                if os.path.exists("metal_chaud.jpg"):
                    st.image("metal_chaud.jpg", caption="Ustensile conducteur", use_container_width=True)
                else:
                    st.warning("L'image 'metal_chaud.jpg' est introuvable.")
            with col_t81_c4:
                if os.path.exists("tuyau_chaudiere.jpg"):
                    st.image("tuyau_chaudiere.jpg", caption="Échangeur efficace", use_container_width=True)
                else:
                    st.warning("L'image 'tuyau_chaudiere.jpg' est introuvable.")
            
    with col_t8_h2:
        st.markdown("##### Les Fortes Résistances Thermiques")
        st.write(
            "**La barrière isolante :** Dans l'isolation des bâtiments, on recherche les valeurs de $R$ les plus "
            "grandes possibles. Les normes modernes exigent souvent un $R \\ge 4$ pour les murs et $R \\ge 7$ pour les combles.\n\n"
            "**Le choix des matériaux :** Pour maximiser $R$, on utilise des isolants de faible conductivité "
            "(laine de roche, polystyrène) et on applique de fortes épaisseurs (généralement de 15 à 30 cm) afin d'allonger le chemin thermique des calories."
        )

        col_t82_h31, col_t82_h32 = st.columns(2)
        with col_t82_h31:
            col_t82_c1, col_t82_c2 = st.columns(2)
            with col_t82_c1:
                if os.path.exists("forte_resistance.jpg"):
                    st.image("forte_resistance.jpg", caption="Forte épaisseur isolante", use_container_width=True)
                else:
                    st.warning("L'image 'forte_resistance.jpg' est introuvable.")
            with col_t82_c2:
                if os.path.exists("isolation_combles.jpg"):
                    st.image("isolation_combles.jpg", caption="Combles protégés", use_container_width=True)
                else:
                    st.warning("L'image 'isolation_combles.jpg' est introuvable.")
        with col_t82_h32:
            col_t82_c3, col_t82_c4 = st.columns(2)
            with col_t82_c3:
                if os.path.exists("laine_roche_panneau.jpg"):
                    st.image("laine_roche_panneau.jpg", caption="Panneau de laine", use_container_width=True)
                else:
                    st.warning("L'image 'laine_roche_panneau.jpg' est introuvable.")
            with col_t82_c4:
                if os.path.exists("confort_interieur.jpg"):
                    st.image("confort_interieur.jpg", caption="Maison économe", use_container_width=True)
                else:
                    st.warning("L'image 'confort_interieur.jpg' est introuvable.")

    st.write("---")


    # =============================================================================
    # 1. BANDE DESSINÉE HUMORISTIQUE EN 4 CASES : LE LABYRINTHE DES JOULES
    # =============================================================================
    col_gauche_texte_t8, col_droite_img_t8 = st.columns(2)

    with col_gauche_texte_t8:
        st.write(
            "**La BD humoristique textuelle : Le labyrinthe des Joules**"
        )
        
        st.info(
            "**Cas 1 : L'obstacle invisible.** Les calories se ruent à l'assaut d'un panneau d'isolant de forte épaisseur : "
            "« Attention les gars, freinez des quatre fers ! Devant nous se dresse une résistance thermique $R$ immense de 5 m².K/W, "
            "on va s'épuiser avant même d'avoir traversé le premier tiers de la paroi ! ».\n\n"
            
            "**Cas 2 : Le piège de l'épaisseur.** Les Joules tentent de forcer le passage mais se retrouvent englués : "
            "« C'est un véritable labyrinthe ! Plus l'épaisseur grandit, plus le coefficient $R$ augmente et nous retient prisonniers. "
            "La conduction n'a plus aucune force ici, battons en retraite ! ».\n\n"
            
            "**Cas 3 : Le diagnostic de l'ingénieur.** L'ingénieur en génie climatique ajuste l'épaisseur sur son plan : "
            "« C'est mathématique ! Pour maximiser la résistance thermique et bloquer le flux traversant, "
            "il suffit d'augmenter l'épaisseur $e$ ou de choisir un matériau au $\lambda$ minuscule. ».\n\n"
            
            "**Cas 4 : La victoire de la barrière.** La maison garde sa chaleur sans effort tout l'hiver : "
            "« Affaire classée ! La résistance thermique a dressé un rempart infranchissable. "
            "Vos précieux Joules restent bien au chaud à la maison ! »."
        )

    with col_droite_img_t8:
        if os.path.exists("resistance_caricature.jpg"):
            st.image(
                "resistance_caricature.jpg",
                caption="Illustration humoristique du pouvoir d'opposition de la résistance thermique",
                use_container_width=True,
            )
        else:
            st.warning(
                "L'image 'resistance_caricature.jpg' est introuvable. Placez l'illustration générée dans le répertoire de l'application."
            )

    st.write("---")

    # =============================================================================
    # 3. LABORATOIRE VIRTUEL : CHOIX LIBRE DU MATÉRIAU ET DES TEMPÉRATURES
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Analyseur dynamique de la résistance d'opposition")
    st.write(
        "Sélectionnez le matériau à tester, définissez librement les températures intérieure et extérieure, "
        "puis faites varier l'épaisseur pour observer l'évolution de la résistance et du flux bloqué :"
    )

    # Référentiel complet des 30 matériaux (Isolants coton, ouate et structure)
    catalogue_complet_r = {
        "Mousse de polyuréthane (Isolant d'élite)": 0.024,
        "Polystyrène extrudé (XPS)": 0.029,
        "Polystyrène expansé (PSE)": 0.032,
        "Isolant en fibre de coton (Coton recyclé / Métisse)": 0.039,
        "Isolant en ouate de cellulose": 0.039,
        "Laine de verre (Isolant minéral standard)": 0.035,
        "Laine de roche en panneau": 0.038,
        "Fibre de bois semi-rigide": 0.040,
        "Liège expansé en plaque": 0.042,
        "Film thermo-réflecteur mince (Multicouche)": 0.033,
        "Bois de sapin / résineux": 0.130,
        "Béton cellulaire (Siporex / Thermopierre)": 0.120,
        "Brique de terre cuite creuse standard": 0.450,
        "Bloc de béton de granulats (Parpaing creux)": 1.050,
        "Brique de terre cuite pleine": 1.150,
        "Plâtre / Plaque de plâtre (BA13)": 0.250,
        "Enduit de façade extérieur (Mortier)": 1.150,
        "Béton armé plein (Forte densité)": 2.300
    }

    # Choix libre du matériau pour l'Atelier 8
    t8_mat_choisi = st.selectbox(
        "Sélectionnez le matériau de la paroi unitaire à étudier :", 
        list(catalogue_complet_r.keys()), 
        index=3, 
        key="t8_sim_mat_libre"
    )
    lambda_r = catalogue_complet_r[t8_mat_choisi]

    # Commandes curseurs de réglage libres (Matière, Températures et Surface)
    col_b8_1, col_b8_2, col_b8_3 = st.columns(3)
    with col_b8_1:
        t8_ep_cm = st.slider("Épaisseur de la couche (e en cm) :", min_value=1, max_value=40, value=12, key="t8_sim_ep_libre")
    with col_b8_2:
        t_int_t8 = st.slider("Température de la face INTÉRIEURE (°C) :", min_value=15, max_value=35, value=21, key="t8_sim_tint_libre")
    with col_b8_3:
        t_ext_t8 = st.slider("Température de la face EXTÉRIEURE (°C) :", min_value=-20, max_value=20, value=-2, key="t8_sim_text_libre")

    surface_pont_t8 = st.slider("Surface totale de la paroi étudiée (m²) :", min_value=5.0, max_value=100.0, value=30.0, step=1.0, key="t8_sim_surf_libre")

    # Calculs physiques de résistance et de flux sur 24h
    e_m_r = t8_ep_cm / 100.0
    r_seul = e_m_r / lambda_r
    r_total_global = r_seul + 0.17  # Intégration des coefficients d'échange d'ambiance Rsi + Rse
    t8_dt = t_int_t8 - t_ext_t8
    flux_pont_w = (t8_dt / r_total_global) * surface_pont_t8
    energie_perdue_24h_kwh = (flux_pont_w * 24.0) / 1000.0

    # Rendu graphique dynamique sans superposition
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    fig_r_local, ax_rl = plt.subplots(figsize=(8.5, 2.5))
    
    ax_rl.add_patch(patches.Rectangle((0.5, 0.4), 1.5, 1.5, facecolor='#fee2e2', alpha=0.6))  # Intérieur chaud
    width_rupteur = 0.5 + (t8_ep_cm / 40.0) * 1.5
    ax_rl.add_patch(patches.Rectangle((2.0, 0.4), width_rupteur, 1.5, facecolor='#fef08a' if lambda_r < 0.05 else '#cbd5e1', edgecolor='#0f172a', lw=1.5))
    ax_rl.add_patch(patches.Rectangle((2.0 + width_rupteur, 0.4), 1.5, 1.5, facecolor='#e0f2fe', alpha=0.6))  # Extérieur froid

    ax_rl.text(1.25, 1.15, f"Intérieur\n{t_int_t8} °C", color='#b91c1c', fontweight='bold', ha='center', va='center', fontsize=9)
    ax_rl.text(2.0 + (width_rupteur / 2), 1.15, f"R-Barrière\n{t8_ep_cm} cm", color='#0f172a', fontweight='bold', ha='center', va='center', fontsize=8)
    ax_rl.text(2.0 + width_rupteur + 0.75, 1.15, f"Extérieur\n{t_ext_t8} °C", color='#1d4ed8', fontweight='bold', ha='center', va='center', fontsize=9)

    lw_fleche_r = min(15.0, max(1.5, flux_pont_w / 100.0)) if t8_dt > 0 else 1.2
    ax_rl.arrow(1.0, 0.6, 2.5 + width_rupteur, 0, head_width=0.15, head_length=0.15, fc='#475569', ec='#475569', lw=lw_fleche_r)

    ax_rl.set_xlim(0, 7.5)
    ax_rl.set_ylim(0, 2.3)
    ax_rl.axis('off')
    st.pyplot(fig_r_local)

    # Affichage des metrics
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        st.metric(label="Résistance Thermique Globale (R_tot)", value=f"{r_total_global:.3f} m².K/W")
    with c_res2:
        st.metric(label="Déperdition de puissance instantanée", value=f"{flux_pont_w:.1f} Watts")
    with c_m3:
        st.metric(label="Conductivité lambda du matériau", value=f"{lambda_r:.3f} W/(m.K)")

    # Synthèse énergétique sur 24 heures sans emoji
    html_synth_r = f"""
    <div style="background-color: #f8fafc; padding: 15px; border-radius: 6px; border: 1px solid #e2e8f0; margin-top: 10px;">
        <p style="margin: 0; font-size: 14px; color: #1e293b;">
            <b>Énergie thermique totale dissipée en 24 heures</b> sous cet écart de température : 
            <span style="color: #b91c1c; font-size: 15px; font-weight: bold;">{energie_perdue_24h_kwh:.2f} kWh</span>
        </p>
    </div>
    """
    st.markdown(html_synth_r, unsafe_allow_html=True)

    # Détail des applications numériques avec correction des accolades pour f-string
    st.markdown("**Démonstration des calculs de résistance d'opposition :**")
    st.latex(rf"R_{{\text{{matériau}}}} = \frac{{e}}{{\lambda}} = \frac{{{e_m_r:.3f}\text{{ m}}}}{{{lambda_r:.3f}}} = {r_seul:.3f}\quad\text{{m}}^2\cdot\text{{K}}/\text{{W}}")
    st.latex(rf"\Phi = \frac{{\Delta T \times A}}{{R_{{\text{{total}}}}}} = \frac{{{t8_dt} \times {surface_pont_t8}}}{{{r_total_global:.3f}}} = {flux_pont_w:.1f}\text{{ Watts}}")
    st.latex(rf"E_{{24\text{{h}}}} = \frac{{\Phi \times 24\text{{ h}}}}{{1000}} = \frac{{{flux_pont_w:.1f} \times 24}}{{1000}} = {energie_perdue_24h_kwh:.2f}\text{{ kWh}}")
    st.write("---")

    if "suite_verrouille_tab9_therm" not in st.session_state:
        st.session_state.suite_verrouille_tab9_therm = False
    verrou_at9 = st.session_state.suite_verrouille_tab9_therm

    # Affichage opérationnel des questions
    afficher_atelier_monocouche_verrouille(verrouille=verrou_at9)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat9 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier sur la Paroi Monocouche.",
        key="check_certif_therm9_final_net",
        disabled=verrou_at9,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9",
        key="btn_export_suite9_therm_official",
        use_container_width=True,
        disabled=verrou_at9,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat9:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q9 = 0.0
            if "ordre_quiz_tab9_therm_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab9_therm_aleatoire:
                    saisie = st.session_state.get(f"therm_at9_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q9 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t9 = 0.0
            if "champs_therm9_clean" in st.session_state:
                for ligne in st.session_state.champs_therm9_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm9_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t9 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite9_therm_p1 = round(float(score_q9), 1)
            st.session_state.score_suite9_therm_p2 = round(float(score_t9), 1)
            st.session_state.score_final_suite9_therm = round(float(score_q9 + score_t9), 1)
            st.session_state.suite_verrouille_tab9_therm = True
            st.st_rerun() if hasattr(st, "st_rerun") else st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab9_therm", False):
        from datetime import datetime
        scr1_t9 = st.session_state.get("score_suite9_therm_p1", 0.0)
        scr2_t9 = st.session_state.get("score_suite9_therm_p2", 0.0)
        tot_s_t9 = st.session_state.get("score_final_suite9_therm", 0.0)
        timestamp_suite9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PAROI MONOCOUCHE SCELLÉ | Note de session : {tot_s_t9:.1f} / 20")

        html_export_therm9 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Paroi Monocouche - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}

                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 9 : Analyse mathématique et calcul du flux conducteur à travers une paroi monocouche simple</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t9:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t9:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t9:.1f} / 10</strong><br>
                Note Totale de l'Atelier 9 : <strong>{tot_s_t9:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab9_therm_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab9_therm_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at9_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm9 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm9 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm9_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm9_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm9_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm9 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm9 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 9 (.HTML)",
            data=html_export_therm9,
            file_name=preparer_nom_fichier("Atelier_9_Paroi_Monocouche").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )


with tab9:
    st.header("Application dans le Domaine de la Maintenance")
    
    # BANQUE DE DONNÉES DES 4 SCÉNARIOS DE MAINTENANCE
    if "scenario_maintenance_choisi" not in st.session_state:
        st.session_state.scenario_maintenance_choisi = "Électricité : Surchauffe de discontacteur"

    # Système de tirage au sort par bouton
    col_tirage, col_statut = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage:
        if st.button("TIRER UN EXERCICE DE MAINTENANCE AU HASARD", key="btn_tirage_hasard_t9", use_container_width=True):
            liste_scenarios = [
                "Électricité : Surchauffe de discontacteur",
                "Mécanique : Échauffement de roulement",
                "Réseaux : Dysfonctionnement de purgeur vapeur",
                "Thermique : Embouage de radiateur central"
            ]
            import random
            # On s'assure de changer de scénario pour le tirage
            actuel = st.session_state.scenario_maintenance_choisi
            possibles = [s for s in liste_scenarios if s != actuel]
            st.session_state.scenario_maintenance_choisi = random.choice(possibles)
            # Réinitialisation des ordres de quiz pour forcer le recalcul lié au nouveau scénario
            if "ordre_quiz_tab9_maint_aleatoire" in st.session_state:
                del st.session_state.ordre_quiz_tab9_maint_aleatoire
            if "champs_therm9_maint_clean" in st.session_state:
                del st.session_state.champs_therm9_maint_clean
            st.rerun()

    scen = st.session_state.scenario_maintenance_choisi
    st.success(f"Exercice actif affecté : {scen}")
    st.write("---")

    # =============================================================================
    # 1. ENONCÉ DE L'EXERCICE ET BANDE DESSINÉE HUMORISTIQUE TEXTUELLE (DYNAMIQUE)
    # =============================================================================
    col_gauche_bd, col_droite_cours = st.columns(2)  # Déclaration propre de col_droite_cours ici

    with col_gauche_bd:
        st.markdown("##### Enoncé de l'exercice et contexte")
        if scen == "Électricité : Surchauffe de discontacteur":
            st.info(
                "**Cas 1 : L'alerte invisible.** Les connexions d'un discontacteur triphasé se desserrent sous l'effet des vibrations d'une machine : "
                "« Attention, le courant passe mal ! La résistance de contact grimpe, les Joules s'accumulent à l'intérieur ! ».\n\n"
                "**Cas 2 : L'œil de l'expert.** Le technicien inspecte l'armoire à la caméra thermique : "
                "« Un point rouge vif apparaît à plus de 85 °C sur la phase 2. Le profil met en évidence un défaut critique ! ».\n\n"
                "**Cas 3 : L'action corrective.** L'opérateur coupe le secteur, ouvre le coffret et resserre les bornes : "
                "« En éliminant cette résistance parasite, la puissance dissipée s'effondre et on évite le sinistre ! ».\n\n"
                "**Cas 4 : Le verdict.** L'armoire est remise sous tension, la caméra affiche une température normale de 35 °C : "
                "« Affaire classée ! La thermographie a sauvé la chaîne de production d'un arrêt coûteux ! »"
            )
        elif scen == "Mécanique : Échauffement de roulement":
            st.info(
                "**Cas 1 : La friction masquée.** Le joint d'étanchéité d'un roulement à billes de moteur rompt, entraînant une fuite de graisse : "
                "« À l'aide, on tourne à sec ! Le frottement mécanique augmente, nos bagues surchauffent ! ».\n\n"
                "**Cas 2 : Le scan thermique.** Lors de sa ronde préventive, le technicien vise le palier de transmission : "
                "« L'arbre dissipe un flux thermique anormal de friction, le capot atteint 95 °C ! ».\n\n"
                "**Cas 3 : La lubrification.** Le technicien procède au remplacement du roulement et fait l'appoint de lubrifiant : "
                "« On remplace la pièce endommagée et on restaure le film d'huile pour stopper la création de chaleur ! ».\n\n"
                "**Cas 4 : La regulation.** Le moteur redémarre, le palier se stabilise durablement sous le seuil de vigilance : "
                "« Affaire classée ! L'analyse thermographique a empêché le grippage destructeur de l'arbre ! »"
            )
        elif scen == "Réseaux : Dysfonctionnement de purgeur vapeur":
            st.info(
                "**Cas 1 : Le blocus interne.** Sur une ligne de vapeur haute pression, un purgeur se bloque en position ouverte : "
                "« Quelle passoire ! La vapeur s'échappe directement vers le réseau de condensats sans donner ses Joules latents ! ».\n\n"
                "**Cas 2 : Le relevé amont-aval.** Le technicien de membrane mesure les températures à l'entrée et à la sortie de l'organe : "
                "« Pas de saut thermique ! L'amont et l'aval sont identiques à 140 °C, le purgeur fuit à plein canal ! ».\n\n"
                "**Cas 3 : Le remplacement.** La vanne d'isolement est fermée, le technicien installe une cartouche neuve : "
                "« On remplace l'élément de régulation défaillant pour piéger la vapeur et conserver l'énergie ! ».\n\n"
                "**Cas 4 : L'économie.** Le réseau est rouvert, le saut thermique attendu réapparaît instantanément : "
                "« Affaire classée ! Le flux perdu est stoppé, le rendement de la chaudière remonte en flèche ! »"
            )
        else: # Embouage de radiateur central
            st.info(
                "**Cas 1 : La sédimentation.** Les oxydes métalliques s'accumulent au fond d'un radiateur en acier d'un bureau : "
                "« On étouffe ici ! Les boues créent une couche sédimentaire opaque qui bloque la convection de l'eau ! ».\n\n"
                "**Cas 2 : La thermographie de surface.** L'expert scanne la face avant de l'émetteur de chaleur : "
                "« C'est flagrant ! Le haut du radiateur est chaud à 60 °C tandis que la moitié inférieure reste glaciale à 22 °C ! ».\n\n"
                "**Cas 3 : L'action de désembouage.** Une pompe hydrodynamique injecte un produit nettoyant dans le circuit : "
                "« On décape et on rince le réseau pour évacuer les boues et restaurer la surface active d'échange ! ».\n\n"
                "**Cas 4 : Le confort restauré.** Le radiateur présente à nouveau une température homogène et diffuse ses Watts : "
                "« Affaire classée ! La caméra confirme le rétablissement du flux. Le bureau retrouve son confort ! »"
            )

    with col_droite_cours:  # Utilisation de la même variable pour insérer la caricature et le cours
        st.markdown("##### Illustration caricaturale du cas")
        # Sélection de la caricature spécifique au scénario tiré
        if scen == "Électricité : Surchauffe de discontacteur":
            fichier_img = "maintenance_elec.jpg"
            caption_img = "Caricature d'une borne électrique en surchauffe par effet Joule"
            texte_bd_bleu = (
                "**La BD humoristique : La révolte du discontacteur**\n\n"
                "**Cas 1 :** Les vis se desserrent. La borne crie : « Ça coince ici, la résistance monte ! ».\n"
                "**Cas 2 :** L'infrarouge s'active : « Alerte au point chaud, la phase 2 passe au rouge vif ! ».\n"
                "**Cas 3 :** Le tournevis intervient : « On resserre tout au couple, la puissance s'effondre ! ».\n"
                "**Cas 4 :** Retour au calme à 35 °C : « Affaire classée, l'incendie est évité avec succès ! »"
            )
        elif scen == "Mécanique : Échauffement de roulement":
            fichier_img = "maintenance_meca.jpg"
            caption_img = "Caricature d'un roulement mécanique subissant d'intenses frottements"
            texte_bd_bleu = (
                "**La BD humoristique : Les billes en surchauffe**\n\n"
                "**Cas 1 :** Plus de graisse dans la cage : « Au secours, on tourne à sec, le métal frotte ! ».\n"
                "**Cas 2 :** Le boîtier monte à 95 °C : « La friction cinétique nous transforme en radiateur ! ».\n"
                "**Cas 3 :** Injection de lubrifiant neuf : « Le film d'huile est restauré, la chaleur capitule ! ».\n"
                "**Cas 4 :** L'arbre tourne sans un bruit : « Affaire classée, le grippage mécanique est maté ! »"
            )
        elif scen == "Réseaux : Dysfonctionnement de purgeur vapeur":
            fichier_img = "maintenance_vapeur.jpg"
            caption_img = "Caricature de la fuite de chaleur latente sur un purgeur bloqué"
            texte_bd_bleu = (
                "**La BD humoristique : La fuite des Joules latents**\n\n"
                "**Cas 1 :** Le clapet reste bloqué ouvert : « C'est les vacances, tout le monde dehors ! ».\n"
                "**Cas 2 :** La vapeur s'échappe en direct : « On file sans donner notre chaleur latente de vaporisation ! ».\n"
                "**Cas 3 :** Pose d'une cartouche neuve : « Clapet verrouillé, la vapeur est prise au piège ! ».\n"
                "**Cas 4 :** Le saut thermique réapparaît : « Affaire classée, les économies d'énergie sont validées ! »"
            )
        else:
            fichier_img = "maintenance_radiateur.jpg"
            caption_img = "Caricature d'une paroi de radiateur obstruée par les sédiments"
            texte_bd_bleu = (
                "**La BD humoristique : L'étouffement du radiateur**\n\n"
                "**Cas 1 :** Les boues se déposent au fond : « On s'installe ici et on bloque tout le monde ! ».\n"
                "**Cas 2 :** Le bas reste gelé à 22 °C : « La résistance sédimentaire fait chuter le coefficient U ! ».\n"
                "**Cas 3 :** Rinçage à la pompe hydrodynamique : « Fin de la grève, les sédiments sont évacués ! ».\n"
                "**Cas 4 :** Chaleur homogène dans tout le bureau : « Affaire classée, le flux thermique a repris sa course ! »"
            )

        # Affichage de l'image
        if os.path.exists(fichier_img):
            st.image(fichier_img, caption=caption_img, use_container_width=True)
        else:
            st.caption(caption_img)
            
        # Affichage de l'énoncé textuel humoristique dans un fond bleu (st.info) comme d'habitude
        st.info(texte_bd_bleu)

    # =============================================================================
    # 2. COURS TECHNIQUE ET MINIATURES (DYNAMIQUE)
    # =============================================================================
    with col_droite_cours:
        st.markdown("##### Base de connaissances techniques")
        if scen == "Électricité : Surchauffe de discontacteur":
            st.write(
                "Un mauvais serrage augmente la résistance électrique de contact ($R$). Au passage du courant ($I$), "
                "la puissance thermique dissipée par effet Joule répond à l'équation $P = R \\cdot I^2$. "
                "Cette chaleur se transmet par conduction aux éléments voisins, provoquant la fusion des isolants plastiques."
            )
        elif scen == "Mécanique : Échauffement de roulement":
            st.write(
                "Le manque de lubrifiant détruit le film d'huile protecteur. Le contact direct métal-métal génère un "
                "frottement intense. L'énergie mécanique se convertit en flux de chaleur parasite. La température grimpe "
                "jusqu'au point de recuit de l'acier, causant la rupture brutale de la transmission."
            )
        elif scen == "Réseaux : Dysfonctionnement de purgeur vapeur":
            st.write(
                "Un purgeur de vapeur doit évacuer l'eau condensée tout en bloquant la vapeur calorifique. S'il fuit, "
                "la vapeur s'échappe en emportant sa chaleur latente de vaporisation ($L_v = 2260\\text{ kJ/kg}$). "
                "Cela crée une perte financière massive par gaspillage de combustible à la chaudière."
            )
        else: # Embouage de radiateur central
            st.write(
                "L'embouage réduit le débit d'eau chaude circulante et crée une couche isolante interne de faible conductivité "
                "thermique. La résistance thermique de la paroi augmente localement, ce qui fait chuter le coefficient "
                "de transmission global ($U$) de l'appareil. Le radiateur ne parvient plus à chauffer la pièce."
            )

        col_mini_1, col_mini_2 = st.columns(2)
        with col_mini_1:
            if os.path.exists("maint_tech_1.jpg"): st.image("maint_tech_1.jpg", use_container_width=True)
            else: st.caption("Image diagnostic infrarouge")
        with col_mini_2:
            if os.path.exists("maint_tech_2.jpg"): st.image("maint_tech_2.jpg", use_container_width=True)
            else: st.caption("Image intervention maintenance")

    st.write("---")

    # =============================================================================
    # 3. LABORATOIRE VIRTUEL INTERACTIF (DYNAMIQUE)
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de mesures de maintenance")
    
    col_p1, col_p2 = st.columns(2)
    if scen == "Électricité : Surchauffe de discontacteur":
        with col_p1:
            val_i = st.slider("Intensité du courant électrique (I en Ampères) :", min_value=10, max_value=80, value=32, key="l9_m_i")
            val_r = st.slider("Résistance parasite de contact (R en Ohms) :", min_value=0.01, max_value=0.40, value=0.12, step=0.01, key="l9_m_r")
        
        puissance_calculee = val_r * (val_i ** 2)
        temp_borne = 25 + (puissance_calculee * 0.4)
        st.metric(label="Puissance dissipée par effet Joule", value=f"{puissance_calculee:.1f} Watts")
        st.latex(rf"P = R \times I^2 = {val_r:.2f} \times {val_i}^2 = {puissance_calculee:.1f}\text{{ W}}")
        st.info(f"Température mesurée sur la borne : {temp_borne:.1f} °C (Seuil critique à 80 °C)")

    elif scen == "Mécanique : Échauffement de roulement":
        with col_p1:
            vitesse_rpm = st.slider("Vitesse de rotation de l'arbre (tr/min) :", min_value=500, max_value=3000, value=1500, step=100, key="l9_m_rpm")
            coeff_frot = st.slider("Coefficient de frottement (Défaut de graisse) :", min_value=0.01, max_value=0.20, value=0.15, step=0.01, key="l9_m_f")
        
        puissance_calculee = vitesse_rpm * coeff_frot * 0.5
        temp_palier = 20 + (puissance_calculee * 0.3)
        
        st.metric(label="Puissance thermique de friction dégagée", value=f"{puissance_calculee:.1f} Watts")
        st.latex(rf"P_{{\text{{friction}}}} = k \times \omega \times f = {puissance_calculee:.1f}\text{{ W}}")
        st.info(f"Température du boîtier de roulement : {temp_palier:.1f} °C (Seuil de vigilance à 65 °C)")

    elif scen == "Réseaux : Dysfonctionnement de purgeur vapeur":
        with col_p1:
            debit_fuite = st.slider("Débit de fuite de vapeur (kg/h) :", min_value=0.5, max_value=10.0, value=2.0, step=0.5, key="l9_m_db")
        
        puissance_calculee = (debit_fuite / 3600.0) * 2260000.0
        perte_24h_kwh = (puissance_calculee * 24.0) / 1000.0
        
        st.metric(label="Débit de fuite énergétique instantané", value=f"{puissance_calculee:.1f} Watts")
        st.latex(rf"\Phi = \dot{{m}} \times L_v = {puissance_calculee:.1f}\text{{ W}}")
        st.info(f"Perte totale accumulée sur une journée de 24 heures : {perte_24h_kwh:.1f} kWh")

    else: # Embouage de radiateur central
        with col_p1:
            pourcent_embouage = st.slider("Taux d'embouage du radiateur (%) :", min_value=0, max_value=80, value=40, step=5, key="l9_m_emb")
        
        puissance_nominale = 2000.0
        puissance_calculee = puissance_nominale * (1 - (pourcent_embouage / 100.0))
        surface_perdue = 1.8 * (pourcent_embouage / 100.0)
        
        st.metric(label="Puissance d'émission thermique réelle du radiateur", value=f"{puissance_calculee:.1f} Watts")
        # Correction de l'accolade fermante sur \text{réelle}
        st.latex(rf"P_{{\text{{réelle}}}} = P_{{\text{{nominale}}}} \times (1 - \eta_{{\text{{embouage}}}}) = {puissance_calculee:.1f}\text{{ W}}")
        st.info(f"Surface de transfert rendue totalement inactive par les boues : {surface_perdue:.2f} m²")
        
    with col_p2:
        # Rendu Matplotlib générique unifié pour le banc d'essai de maintenance
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        fig_m, ax_m = plt.subplots(figsize=(6, 2.5))
        couleur_diag = "#ef4444" if puissance_calculee > 800 else "#10b981"
        ax_m.add_patch(patches.Rectangle((0.5, 0.4), 3.0, 1.4, facecolor='#cbd5e1', edgecolor='#0f172a', lw=1.5))
        ax_m.add_patch(patches.Rectangle((1.5, 0.7), 1.0, 0.8, facecolor=couleur_diag, alpha=0.8))
        ax_m.text(2.0, 1.1, "Zone Cible", color='white', fontweight='bold', ha='center', va='center', fontsize=9)
        ax_m.text(4.2, 1.1, f"Signal capté :\n{puissance_calculee:.1f} W", color='#0f172a', fontweight='bold', fontsize=9)
        ax_m.set_xlim(0, 6.0)
        ax_m.set_ylim(0, 2.2)
        ax_m.axis('off')
        st.pyplot(fig_m)

    st.write("---")       
    if "suite_verrouille_tab9_maint" not in st.session_state:
        st.session_state.suite_verrouille_tab9_maint = False
    verrou_at9 = st.session_state.suite_verrouille_tab9_maint

    # Affichage opérationnel des questions spécifiques adaptées au cas de maintenance tiré
    afficher_atelier_maintenance_dynamique(scen, verrouille=verrou_at9)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 9")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat9 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier d'application de la Maintenance.",
        key="check_certif_therm9_maint_net",
        disabled=verrou_at9,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 9",
        key="btn_export_suite9_maint_official",
        use_container_width=True,
        disabled=verrou_at9,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat9:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Technique (10 pts)
            score_q9 = 0.0
            if "ordre_quiz_tab9_maint_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab9_maint_aleatoire:
                    saisie = st.session_state.get(f"therm_at9_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q9 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t9 = 0.0
            if "champs_therm9_maint_clean" in st.session_state:
                for ligne in st.session_state.champs_therm9_maint_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm9_maint_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t9 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite9_maint_p1 = round(float(score_q9), 1)
            st.session_state.score_suite9_maint_p2 = round(float(score_t9), 1)
            st.session_state.score_final_suite9_maint = round(float(score_q9 + score_t9), 1)
            st.session_state.suite_verrouille_tab9_maint = True
            st.st_rerun() if hasattr(st, "st_rerun") else st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab9_maint", False):
        from datetime import datetime
        scr1_t9 = st.session_state.get("score_suite9_maint_p1", 0.0)
        scr2_t9 = st.session_state.get("score_suite9_maint_p2", 0.0)
        tot_s_t9 = st.session_state.get("score_final_suite9_maint", 0.0)
        timestamp_suite9 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER MAINTENANCE SCELLÉ | Note de session : {tot_s_t9:.1f} / 20")

        html_export_therm9 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Application Maintenance - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 9 : Application technologique et relevés thermographiques au domaine de la Maintenance</p>
                <p>Scénario résolu : {scen}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite9}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t9:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t9:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t9:.1f} / 10</strong><br>
                Note Totale de l'Atelier 9 : <strong>{tot_s_t9:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab9_maint_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab9_maint_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at9_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm9 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm9 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm9_maint_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm9_maint_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm9_maint_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm9 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm9 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 9 (.HTML)",
            data=html_export_therm9,
            file_name=preparer_nom_fichier("Atelier_9_Application_Maintenance").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )


with tab10:
    st.header("Application dans le Domaine des Travaux Publics")
    
    # BANQUE DE DONNÉES DES 4 SCÉNARIOS DES TRAVAUX PUBLICS
    if "scenario_tp_choisi" not in st.session_state:
        st.session_state.scenario_tp_choisi = "Béton massif : Exothermie d'une pile de pont"

    # Système de tirage au sort par bouton
    col_tirage_tp, col_statut_tp = st.columns([0.4, 0.6], vertical_alignment="center")
    with col_tirage_tp:
        if st.button("TIRER UN EXERCICE DE TP AU HASARD", key="btn_tirage_hasard_t10", use_container_width=True):
            liste_scenarios_tp = [
                "Béton massif : Exothermie d'une pile de pont",
                "Ouvrage d'art : Fissuration thermique de tablier",
                "Viabilité hivernale : Coulage par temps de gel",
                "Génie civil : Prise sous-marine et flux conducteur"
            ]
            import random
            actuel_tp = st.session_state.scenario_tp_choisi
            possibles_tp = [s for s in liste_scenarios_tp if s != actuel_tp]
            st.session_state.scenario_tp_choisi = random.choice(possibles_tp)
            # Réinitialisation des ordres de quiz pour forcer le recalcul lié au nouveau scénario
            if "ordre_quiz_tab10_tp_aleatoire" in st.session_state:
                del st.session_state.ordre_quiz_tab10_tp_aleatoire
            if "champs_therm10_tp_clean" in st.session_state:
                del st.session_state.champs_therm10_tp_clean
            st.rerun()

    scen_tp = st.session_state.scenario_tp_choisi
    st.success(f"Exercice de TP actif affecté : {scen_tp}")
    st.write("---")

    # =============================================================================
    # DÉFINITION TECHNIQUE ADAPTATIVE DE L'ATELIER 10 (TRAVAUX PUBLICS)
    # =============================================================================
    if scen_tp == "Béton massif : Exothermie d'une pile de pont":
        def_scen_tp = (
            "Lors du coulage de structures massives en **Travaux Publics**, la réaction d'hydratation du ciment "
            "libère une quantité importante d'énergie thermique. Le béton frais agissant comme un isolant capacitif, "
            "la chaleur s'accumule au cœur du bloc. Ce phénomène exothermique crée un fort gradient de température "
            "avec la surface extérieure. L'analyse des transferts de chaleur permet de dimensionner les systèmes "
            "de refroidissement par tubes d'eau intégrés."
        )
    elif scen_tp == "Ouvrage d'art : Fissuration thermique de tablier":
        def_scen_tp = (
            "Sur les **chantiers d'ouvrages d'art**, le coulage d'un tablier de pont en béton armé est soumis à de fortes "
            "contraintes thermomécaniques. L'écart de température ($\Delta T$) entre le cœur chaud en cure et la surface "
            "refroidie par l'air ambiant engendre des contraintes de traction. Si ce gradient thermique dépasse la valeur "
            "critique de 20 °C, des fissures structurelles apparaissent, menaçant l'étanchéité et la durabilité de l'ouvrage."
        )
    elif scen_tp == "Viabilité hivernale : Coulage par temps de gel":
        def_scen_tp = (
            "Le coulage du béton par **temps de gel** constitue un défi thermique pour le conducteur de travaux. Si l'eau "
            "présente dans le béton frais gèle avant la fin de la prise, son changement d'état en glace détruit la matrice "
            "cristalline du ciment. La maintenance du chantier impose l'utilisation de bâches isolantes d'une forte "
            "résistance thermique ($R$) et l'apport de chaleur sensible via des brûleurs pour maintenir le béton au-dessus de 5 °C."
        )
    else: # Prise sous-marine et flux conducteur
        def_scen_tp = (
            "Pour les fondations d'ouvrages maritimes, le bétonnage **sous-marin** nécessite de maîtriser le flux thermique "
            "conducteur cédé à l'eau environnante. L'eau de mer possède une capacité thermique massique gigantesque, "
            "agissant comme un puits thermique infini. Un refroidissement trop rapide de la paroi extérieure du bloc de béton "
            "perturbe la cinétique chimique de prise, exigeant l'adjonction d'adjuvants accélérateurs de durcissement."
        )

    st.write(f"**Définition et contexte du cas :** {def_scen_tp}")
    st.write("---")

    # =============================================================================
    # 1. ENONCÉ DE L'EXERCICE ET CARICATURES ASSOCIÉES (DYNAMIQUE)
    # =============================================================================
    col_gauche_bd_tp, col_droite_cours_tp = st.columns([0.3, 0.4])

    with col_gauche_bd_tp:
        st.markdown("##### Enoncé de l'exercice et contexte")
        if scen_tp == "Béton massif : Exothermie d'une pile de pont":
            st.info(
                "**Cas 1 : Le grand coulage.** Des tonnes de béton frais remplissent le coffrage d'une pile de pont : "
                "« C'est parti ! Le ciment s'hydrate et commence à libérer ses Joules chimiques au cœur du bloc massif ! ».\n\n"
                "**Cas 2 : La surchauffe interne.** La conductivité thermique du béton étant faible, la chaleur sensible s'accumule : "
                "« Le centre du bloc atteint 65 °C alors que la surface est à 15 °C. Le gradient de température s'accentue ! ».\n\n"
                "**Cas 3 : La parade de l'ingénieur.** Le conducteur de travaux active un réseau de tubes d'eau glacée : "
                "« On extrait activement les calories pour aplanir le profil thermique et sauver la cohésion du béton ! ».\n\n"
                "**Cas 4 : L'ouvrage pérenne.** La température est maîtrisée, le bloc durcit de manière parfaitement homogène : "
                "« Affaire classée ! L'exothermie et la conduction ont été domptées, la structure est validée ! »"
            )

            texte_bd_bleu_tp = (
                "**La BD humoristique : Le cœur brûlant du béton**\n\n"
                "**Cas 1 :** Hydratation générale : « C'est la fête du ciment, les Joules se libèrent ! ».\n\n"
                "**Cas 2 :** Blocage du flux : « Le béton conduit très mal, la chaleur sensible reste prisonnière au centre ! ».\n\n"
                "**Cas 3 :** Activation des tubes d'eau : « On pompe les calories pour aplatir la courbe thermique ! ».\n\n"
                "**Cas 4 :** Durcissement réussi : « Affaire classée, la pile de pont est solide et sans fissure ! »"
            )
            # Affichage juste en dessous
            st.info(texte_bd_bleu_tp)

        elif scen_tp == "Ouvrage d'art : Fissuration thermique de tablier":
            st.info(
                "**Cas 1 : La cure du tablier.** Le tablier de pont vient d'être coulé en pleine nuit d'hiver : "
                "« La réaction commence ! Le cœur monte en température tandis que l'air glacial refroidit la surface ! ».\n\n"
                "**Cas 2 : Le seuil critique.** L'ingénieur mesure l'écart thermique entre l'intérieur et l'extérieur : "
                "« L'écart dépasse les 25 °C ! Des contraintes de traction thermique apparaissent sur la peau du béton ! ».\n\n"
                "**Cas 3 : La bâche thermique.** Les ouvriers déploient immédiatement des matelas isolants sur le tablier : "
                "« En augmentant la résistance R en surface, on freine le flux perdu et on réduit le gradient destructeur ! ».\n\n"
                "**Cas 4 : Le pont sauvé.** Les fissures sont évitées, la peau du béton reste lisse et étanche : "
                "« Affaire classée ! Les lois de la dilatation thermique ont été contenues à temps ! »"
            )

            texte_bd_bleu_tp = (
                "**La BD humoristique : La peau du béton sous tension**\n\n"
                "**Cas 1 :** Le tablier refroidit par l'extérieur : « Le cœur est brûlant mais ma peau est glacée ! ».\n\n"
                "**Cas 2 :** Écart de 25 °C : « Le gradient thermique tire trop fort, les micro-fissures arrivent ! ».\n\n"
                "**Cas 3 :** Pose des matelas isolants : « On augmente la résistance R pour réchauffer la surface ! ».\n\n"
                "**Cas 4 :** Profil lissé : « Affaire classée, les contraintes de traction thermique ont capitulé ! »"
            )
            # Affichage juste en dessous
            st.info(texte_bd_bleu_tp)
            
        elif scen_tp == "Viabilité hivernale : Coulage par temps de gel":
            st.info(
                "**Cas 1 : L'assaut du gel.** Le thermomètre du chantier descend à -5 °C pendant le coulage des fondations : "
                "« Alerte, les Joules s'échappent ! Si l'eau gèle, le réseau cristallin du ciment sera brisé ! ».\n\n"
                "**Cas 2 : La menace du changement d'état.** Les molécules d'eau s'approchent du point de solidification : "
                "« À 0 °C, on va libérer notre chaleur latente pour devenir des cristaux de glace destructeurs ! ».\n\n"
                "**Cas 3 : Le chauffage de cure.** L'équipe déploie des radiants thermiques et des bâches isolantes : "
                "« On apporte de la chaleur sensible pour maintenir la masse au-dessus de 5 °C et mener la prise à terme ! ».\n\n"
                "**Cas 4 : La résistance acquise.** Le béton a pris sa résistance mécanique sans subir l'action du gel : "
                "« Affaire classée ! Les barrières isolantes ont protégé les réactions chimiques du ciment ! »"
            )

            texte_bd_bleu_tp = (
                "**La BD humoristique : La bataille du zéro degré**\n\n"
                "**Cas 1 :** Chute du thermomètre : « Sauvez les Watts, le gel attaque les fondations ! ».\n\n"
                "**Cas 2 :** Solidification latente : « À 0 °C, l'eau veut se changer en glace et briser les cristaux ! ».\n\n"
                "**Cas 3 :** Allumage des radiants : « Apport de chaleur sensible immédiat sous les bâches R ! ».\n\n"
                "**Cas 4 :** Prise sécurisée : « Affaire classée, le réseau cristallin du ciment est intact ! »"
            )
            # Affichage juste en dessous
            st.info(texte_bd_bleu_tp)

        else: # Prise sous-marine et flux conducteur
            st.info(
                "**Cas 1 : L'immersion.** Le béton est coulé au tube plongeur dans l'eau froide de l'océan : "
                "« Quel choc ! L'océan nous entoure et commence à piller nos précieuses calories d'hydratation ! ».\n\n"
                "**Cas 2 : Le puits thermique.** L'eau de mer absorbe le flux sans monter en température : "
                "« Ma capacité thermique massique est gigantesque ! Je refroidis la peau extérieure du bloc en un éclair ! ».\n\n"
                "**Cas 3 : L'accélérateur de prise.** L'ingénieur ajoute un adjuvant accélérateur au mélange : "
                "« On booste la cinétique chimique pour dégager les Joules mais plus vite que le flux conducteur perdu dans la mer ! ».\n\n"
                "**Cas 4 : Le massif scellé.** Les fondations maritimes ont durci correctement sous l'eau : "
                "« Affaire classée ! L'équilibre entre le flux thermique perdu et la chimie du ciment a été trouvé ! »"
            )

            texte_bd_bleu_tp = (
                "**La BD humoristique : L'océan pilleur de Joules**\n\n"
                "**Cas 1 :** Immersion du béton sous l'eau : « Brrr, la mer commence à aspirer nos calories ! ».\n\n"
                "**Cas 2 :** Capacité thermique géante : « Je suis l'océan, j'absorbe votre flux sans broncher ! ».\n\n"
                "**Cas 3 :** Adjuvant accélérateur : « On accélère la chimie pour produire du Joule plus vite que la fuite ! ».\n\n"
                "**Cas 4 :** Prise sous-marine validée : « Affaire classée, les fondations maritimes sont scellées ! »"
            )
            # Affichage juste en dessous
            st.info(texte_bd_bleu_tp)

    # =============================================================================
    # 2. COURS TECHNIQUE ET CARICATURE EN FOND BLEU (DYNAMIQUE)
    # =============================================================================
    with col_droite_cours_tp:
        st.markdown("##### Illustration du cas")
        
        # Initialisation des deux variables d'images pour chaque scénario
        if scen_tp == "Béton massif : Exothermie d'une pile de pont":
            fichier_reel = "exothermipiledepont.jpg"
            fichier_caricature = "tp_exothermie.jpg"
            caption_reel = "Image réelle : Suivi de la pile de pont"
            caption_caricature = "Caricature de l'accumulation de chaleur au cœur du béton massif"

        elif scen_tp == "Ouvrage d'art : Fissuration thermique de tablier":
            fichier_reel = "Fissurationthermiquetablier.jpg"
            fichier_caricature = "tp_fissuration.jpg"
            caption_reel = "Image réelle : Mesure du tablier d'ouvrage d'art"
            caption_caricature = "Caricature des contraintes de traction sur la peau du béton"

        elif scen_tp == "Viabilité hivernale : Coulage par temps de gel":
            fichier_reel = "Coulagepartempsgel.jpg"
            fichier_caricature = "tp_gel.jpg"
            caption_reel = "Image réelle : Chantier hivernal sous protection thermique"
            caption_caricature = "Caricature de la menace de solidification de l'eau dans le ciment"

        else:
            fichier_reel = "Prisesousmarine.jpg"
            fichier_caricature = "tp_sous_marin.jpg"
            caption_reel = "Image réelle : Coulage de fondation en milieu maritime"
            caption_caricature = "Caricature de l'océan comme puits thermique infini"

        # 1. Affichage supérieur : L'image réelle du cas (nom long)
        if os.path.exists(fichier_reel):
            st.image(fichier_reel, caption=caption_reel, use_container_width=150)
        else:
            st.caption(caption_reel)

        # 2. Affichage inférieur : L'image de la caricature (nom court)
        if os.path.exists(fichier_caricature):
            st.image(fichier_caricature, caption=caption_caricature, use_container_width=150)
        else:
            st.caption(caption_caricature)

            
    st.write("---")

    # =============================================================================
    # 3. LABORATOIRE VIRTUEL INTERACTIF (DYNAMIQUE ET SANS EMOJI)
    # =============================================================================
    st.subheader("Laboratoire Virtuel : Simulateur de calculs thermiques en Génie Civil")
    
    col_p1_tp, col_p2_tp = st.columns(2)
    if scen_tp == "Béton massif : Exothermie d'une pile de pont":
        with col_p1_tp:
            dosage_ciment = st.slider("Dosage en ciment du béton (kg/m³) :", min_value=250, max_value=450, value=350, step=10, key="l10_tp_p1")
            exothermie_ciment = st.slider("Chaleur d'hydratation du liant (kJ/kg) :", min_value=150, max_value=350, value=260, step=10, key="l10_tp_p2")
        
        energie_degagee_mj = (dosage_ciment * exothermie_ciment) / 1000.0
        elevation_temp = energie_degagee_mj * 1000.0 / (2400 * 1.0) # Densité ~2400 kg/m³, Cp ~1 kJ/kg.K
        
        st.metric(label="Énergie thermique libérée par l'exothermie", value=f"{energie_degagee_mj:.1f} MJ/m³")
        # Utilisation de simples barres obliques pour le code LaTeX standardisé en Python sans couper la ligne
        formule_q = rf"Q_{{\text{{chimique}}}} = \frac{{m_{{\text{{ciment}}}} \times q_{{\text{{hydratation}}}}}}{{1000}} = \frac{{{dosage_ciment} \times {exothermie_ciment}}}{{1000}} = {energie_degagee_mj:.1f}\text{{ MJ/m³}}"
        st.latex(formule_q)
        st.info(f"Élévation de température théorique au cœur du massif : +{elevation_temp:.1f} °C")

    elif scen_tp == "Ouvrage d'art : Fissuration thermique de tablier":
        with col_p1_tp:
            temp_coeur = st.slider("Température mesurée au cœur du tablier (°C) :", min_value=30, max_value=75, value=58, key="l10_tp_p1_f")
            temp_peau = st.slider("Température de la surface extérieure (°C) :", min_value=5, max_value=30, value=12, key="l10_tp_p2_f")
        
        gradient_paroi = temp_coeur - temp_peau
        st.metric(label="Gradient thermique cœur / surface (dT)", value=f"{gradient_paroi:.1f} °C")
        st.latex(rf"\Delta T_{{\text{{gradient}}}} = T_{{\text{{cœur}}}} - T_{{\text{{surface}}}} = {temp_coeur} - {temp_peau} = {gradient_paroi:.1f}\text{{ °C}}")
        
        if gradient_paroi > 20.0:
            st.error("Risque de fissuration élevé : Le gradient thermique dépasse le seuil critique de 20 °C. Pose d'isolants requise.")
        else:
            st.success("Structure sécurisée : Le gradient de température est inférieur au seuil critique de 20 °C.")

    elif scen_tp == "Viabilité hivernale : Coulage par temps de gel":
        with col_p1_tp:
            epaisseur_bache = st.slider("Épaisseur du matelas isolant de cure (e en cm) :", min_value=1, max_value=10, value=4, key="l10_tp_p1_g")
            t_exterieure_gel = st.slider("Température de l'air extérieur (°C) :", min_value=-15, max_value=5, value=-4, key="l10_tp_p2_g")
        
        lambda_bache = 0.038
        r_bache = (epaisseur_bache / 100.0) / lambda_bache
        flux_perdu_surface = (5 - t_exterieure_gel) / (r_bache + 0.17)
        
        st.metric(label="Résistance thermique de la barrière R", value=f"{r_bache:.3f} m².K/W")
        st.latex(rf"R = \frac{{e}}{{\lambda}} = \frac{{{epaisseur_bache/100:.3f}}}{{{lambda_bache:.3f}}} = {r_bache:.3f}\text{{ m²}}\cdot\text{{K/W}}")
        st.info(f"Flux thermique de déperdition surfacique : {flux_perdu_surface:.1f} W/m²")

    else: # Prise sous-marine
        with col_p1_tp:
            surface_immersion = st.slider("Surface du bloc de fondation exposée à la mer (m²) :", min_value=5, max_value=80, value=30, key="l10_tp_p1_s")
            t_mer = st.slider("Température de l'eau de mer (°C) :", min_value=4, max_value=18, value=11, key="l10_tp_p2_s")
        
        u_paroi_eau = 5.5
        flux_mer_w = u_paroi_eau * surface_immersion * (35 - t_mer)
        
        st.metric(label="Flux thermique conducteur cédé à l'océan", value=f"{flux_mer_w:.1f} Watts")
        st.latex(rf"\Phi = U \times A \times \Delta T = 5{{,}}5 \times {surface_immersion} \times (35 - {t_mer}) = {flux_mer_w:.1f}\text{{ W}}")
        st.info("L'eau de mer agit comme un puits thermique infini en raison de sa gigantesque capacité volumique.")

    with col_p2_tp:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        fig_tp, ax_tp = plt.subplots(figsize=(6, 2.5))
        ax_tp.add_patch(patches.Rectangle((0.5, 0.4), 3.0, 1.4, facecolor='#e2e8f0', edgecolor='#0f172a', lw=1.5))
        ax_tp.add_patch(patches.Circle((2.0, 1.1), 0.4, facecolor='#bfdbfe', edgecolor='#1e3a8a', lw=1.5))
        ax_tp.text(2.0, 1.1, "Ouvrage", color='#1e3a8a', fontweight='bold', ha='center', va='center', fontsize=9)
        ax_tp.text(4.2, 1.1, "Banc d'essai\nGénie Civil\nTP", color='#0f172a', fontweight='bold', fontsize=9)
        ax_tp.set_xlim(0, 6.0)
        ax_tp.set_ylim(0, 2.2)
        ax_tp.axis('off')
        st.pyplot(fig_tp)

    st.write("---")

    # =============================================================================
    # APPEL CRUCIAL DU MODULE DE RENDU DES QUESTIONNAIRES DYNAMIQUES
    # =============================================================================
    if "suite_verrouille_tab10_tp" not in st.session_state:
        st.session_state.suite_verrouille_tab10_tp = False
    verrou_at10_tp = st.session_state.suite_verrouille_tab10_tp

    # Cette ligne manquante déclenche l'affichage complet des questions et des trous
    afficher_atelier_tp_dynamique(scen_tp, verrouille=verrou_at10_tp)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 10")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat10 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier d'application des Travaux Publics.",
        key="check_certif_therm10_tp_net",
        disabled=verrou_at10_tp,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 10",
        key="btn_export_suite10_tp_official",
        use_container_width=True,
        disabled=verrou_at10_tp,
    ):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat10:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 pts)
            score_q10 = 0.0
            if "ordre_quiz_tab10_tp_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab10_tp_aleatoire:
                    saisie = st.session_state.get(f"therm_at10_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip():
                        score_q10 += 1.0

            # 2. Correction du Texte à trous (10 pts)
            score_t10 = 0.0
            if "champs_therm10_tp_clean" in st.session_state:
                for ligne in st.session_state.champs_therm10_tp_clean:
                    enonce_t, choix_t, attendu_t, cle_t = ligne
                    saisie_t = st.session_state.get(f"{cle_t}_therm10_tp_clean", "Choisir...")
                    if str(saisie_t).strip() == str(attendu_t).strip():
                        score_t10 += 1.0

            # 3. Sauvegarde définitive dans la session et rafraîchissement
            st.session_state.score_suite10_tp_p1 = round(float(score_q10), 1)
            st.session_state.score_suite10_tp_p2 = round(float(score_t10), 1)
            st.session_state.score_final_suite10_tp = round(float(score_q10 + score_t10), 1)
            st.session_state.suite_verrouille_tab10_tp = True
            st.rerun()

    # --- COMPILATION ET TÉLÉCHARGEMENT DU BILAN HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab10_tp", False):
        from datetime import datetime
        scr1_t10 = st.session_state.get("score_suite10_tp_p1", 0.0)
        scr2_t10 = st.session_state.get("score_suite10_tp_p2", 0.0)
        tot_s_t10 = st.session_state.get("score_final_suite10_tp", 0.0)
        timestamp_suite10 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER TRAVAUX PUBLICS SCELLÉ | Note de session : {tot_s_t10:.1f} / 20")

        html_export_therm10 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Application TP - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Évaluation de Physique Thermique</h1>
                <p>Atelier 10 : Application technologique au domaine des Travaux Publics (Ouvrages d'art)</p>
                <p>Scénario résolu : {scen_tp}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite10}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t10:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t10:.1f} / 10</strong><br>
                Note obtenue à la Synthèse de Cours : <strong>{scr2_t10:.1f} / 10</strong><br>
                Note Totale de l'Atelier 10 : <strong>{tot_s_t10:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab10_tp_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab10_tp_aleatoire, 1):
                saisie = st.session_state.get(f"therm_at10_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_therm10 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_therm10 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "champs_therm10_tp_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_therm10_tp_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]

                saisie_texte = st.session_state.get(f"{cle_variable}_therm10_tp_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_therm10 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        html_export_therm10 += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TÉLÉCHARGER LE RAPPORT INDIVIDUEL DE L'ATELIER 10 (.HTML)",
            data=html_export_therm10,
            file_name=preparer_nom_fichier("Atelier_10_Application_TP").replace(".txt", ".html"),
            mime="text/html",
            use_container_width=True,
        )














