# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Permis C - Revisions",
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
st.title("Application Permis C - Revisions")
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
    "Permis AM",
    "Permis B",
    "Fiches orales permis C",
    "Fiche écrites permis C",
    "Fiches orales permis CE",
    "Fiche écrites permis CE",

])

tab0 = onglets[0] 
tab1 = onglets[1] 
tab2 = onglets[2] 
tab3 = onglets[3] 
tab4 = onglets[4] 
tab5 = onglets[5]
tab6 = onglets[6] 


# --- 4. DÉFINITION ET CONFIGURATION DES ONGLETS STREAMLIT ---
onglets = st.tabs([
    "Identification",
    "Permis AM",
    "Permis B",
    "Fiches orales permis C",
    "Fiche écrites permis C",  # Index 4
    "Fiches orales permis CE",
    "Fiche écrites permis CE",
])

def charger_banque_permis_am():
    """Retourne la banque contenant 20 questions pour le Permis AM."""
    return [
        {"type": "choix", "question": "Quelle est la vitesse maximale par construction d'un cyclomoteur de moins de 50 cm³ ?", "choix": ["45 km/h", "50 km/h", "60 km/h"], "reponse": "45 km/h"},
        {"type": "ecrite", "question": "Quels sont les deux équipements de protection obligatoires et certifiés pour le conducteur ?", "choix": [], "reponse": "Le casque homologué attaché et les gants certifiés CE."},
        {"type": "choix", "question": "À partir de quel âge minimum est-il autorisé de conduire un cyclomoteur avec le permis AM ?", "choix": ["14 ans", "15 ans", "16 ans"], "reponse": "14 ans"},
        {"type": "ecrite", "question": "Quelle est la sanction principale si vous circulez avec un moteur débridé ?", "choix": [], "reponse": "Amende, immobilisation/confiscation du véhicule, et déchéance des garanties d'assurance."},
        {"type": "choix", "question": "Quel document est obligatoire pour circuler en cas de contrôle par les forces de l'ordre ?", "choix": ["Le certificat d'immatriculation (carte grise) et l'attestation d'assurance", "Le livret de famille", "Une pièce d'identité seule"], "reponse": "Le certificat d'immatriculation (carte grise) et l'attestation d'assurance"},
        {"type": "ecrite", "question": "Que devez-vous vérifier sur votre casque avant de prendre la route ?", "choix": [], "reponse": "Qu'il est à la bonne taille, en bon état (sans fissure), propre et correctement attaché."},
        {"type": "choix", "question": "Quel taux d'alcoolémie maximal par litre d'air expiré est toléré pour un conducteur novice ?", "choix": ["0,10 mg/l", "0,20 mg/l", "0,25 mg/l"], "reponse": "0,10 mg/l"},
        {"type": "ecrite", "question": "Pourquoi est-il dangereux de rouler dans l'angle mort d'un véhicule lourd ?", "choix": [], "reponse": "Parce que le conducteur ne vous voit pas et risque de vous percuter s'il tourne ou change de voie."},
        {"type": "choix", "question": "Le port du gilet de haute sécurité (gilet jaune) est-il obligatoire à cyclomoteur ?", "choix": ["Il doit être à bord et porté en cas d'arrêt d'urgence", "Oui, porté en permanence", "Non, jamais"], "reponse": "Il doit être à bord et porté en cas d'arrêt d'urgence"},
        {"type": "ecrite", "question": "Quelle distance de sécurité minimale devez-vous laisser avec le véhicule qui vous précède ?", "choix": [], "reponse": "Une distance équivalente à un temps de réaction et de freinage d'au moins 2 secondes."},
        {"type": "choix", "question": "Sur un cyclomoteur, l'assurance couvre-t-elle les dégâts si le passager ne porte pas de casque ?", "choix": ["Non, l'assurance peut refuser la prise en charge", "Oui, sans condition", "Uniquement si le passager est mineur"], "reponse": "Non, l'assurance peut refuser la prise en charge"},
        {"type": "ecrite", "question": "Que signifie la présence de bandes réfléchissantes obligatoires sur un casque ?", "choix": [], "reponse": "Assurer la visibilité nocturne du conducteur sous tous les angles."},
        {"type": "choix", "question": "Quelle est la catégorie de panneau indicateur de forme triangulaire ?", "choix": ["Un panneau de danger", "Un panneau d'interdiction", "Un panneau d'obligation"], "reponse": "Un panneau de danger"},
        {"type": "ecrite", "question": "Quelle est la principale cause d'accident grave chez les jeunes conducteurs de deux-roues ?", "choix": [], "reponse": "La vitesse excessive ou inadaptée combinée au manque d'expérience."},
        {"type": "choix", "question": "La consommation de cannabis au guidon multiplie le risque d'accident par :", "choix": ["2", "5", "10"], "reponse": "2"},
        {"type": "ecrite", "question": "Quel comportement adopter à l'approche d'un passage piéton occupé ?", "choix": [], "reponse": "Ralentir et s'arrêter pour laisser la priorité absolue au piéton engagé."},
        {"type": "choix", "question": "Une ligne continue au centre de la chaussée :", "choix": ["Interdit strictement le franchissement et le chevauchement", "Permet le dépassement des vélos", "Est une simple indication"], "reponse": "Interdit strictement le franchissement et le chevauchement"},
        {"type": "ecrite", "question": "Pourquoi faut-il allumer les feux de croisement même en plein jour à cyclomoteur ?", "choix": [], "reponse": "Pour être immédiatement visible par les autres usagers de la route."},
        {"type": "choix", "question": "Le transport d'un passager sur un cyclomoteur est autorisé si :", "choix": ["Le véhicule est conçu pour (siège et repose-pieds)", "Le passager a moins de 10 ans", "Le trajet fait moins de 5 km"], "reponse": "Le véhicule est conçu pour (siège et repose-pieds)"},
        {"type": "ecrite", "question": "Que devez-vous faire en premier lieu en présence d'un panneau 'Stop' ?", "choix": [], "reponse": "Marquer un arrêt absolu à la limite de la ligne transversale et céder le passage."}
    ]

def charger_banque_permis_b():
    """Retourne la banque contenant 20 questions pour le Permis B."""
    return [
        {"type": "choix", "question": "Quelle est la vitesse maximale autorisée sur autoroute par temps sec pour un jeune conducteur (permis probatoire) ?", "choix": ["110 km/h", "130 km/h", "100 km/h"], "reponse": "110 km/h"},
        {"type": "ecrite", "question": "Expliquez brièvement comment s'applique la règle de la priorité à droite en l'absence de signalisation.", "choix": [], "reponse": "On doit céder le passage à tout véhicule qui débouche d'une rue située sur notre droite."},
        {"type": "choix", "question": "Le taux d'alcoolémie limite dans le sang pour un conducteur en permis probatoire est de :", "choix": ["0,20 g/l", "0,50 g/l", "0,00 g/l"], "reponse": "0,20 g/l"},
        {"type": "ecrite", "question": "Quelle est l'utilité du système de freinage ABS en cas de freinage d'urgence ?", "choix": [], "reponse": "Empêcher le blocage des roues pour garder la maîtrise de la trajectoire du véhicule."},
        {"type": "choix", "question": "À quelle distance minimale devez-vous placer le triangle de présignalisation en cas de panne sur route ?", "choix": ["30 mètres", "15 mètres", "50 mètres"], "reponse": "30 mètres"},
        {"type": "ecrite", "question": "Quelles sont les conditions météorologiques qui obligent à réduire sa vitesse à 50 km/h sur l'ensemble du réseau routier ?", "choix": [], "reponse": "Une visibilité inférieure à 50 mètres (brouillard intense, fortes précipitations)."},
        {"type": "choix", "question": "L'utilisation d'un téléphone tenu en main en conduisant entraîne un retrait de :", "choix": ["3 points", "2 points", "4 points"], "reponse": "3 points"},
        {"type": "ecrite", "question": "Qu'est-ce que l'aquaplaning et comment y faire face ?", "choix": [], "reponse": "Perte d'adhérence des pneus due à une pellicule d'eau. Il faut débrayer et garder le volant droit sans freiner."},
        {"type": "choix", "question": "Quelle est la durée de la période probatoire pour un conducteur ayant suivi la conduite accompagnée (AAC) ?", "choix": ["2 ans", "3 ans", "1 an"], "reponse": "2 ans"},
        {"type": "ecrite", "question": "Quelles vérifications intérieures devez-vous réaliser dès votre installation au poste de conduite ?", "choix": [], "reponse": "Réglage du siège, du volant, des trois rétroviseurs et attache de la ceinture."},
        {"type": "choix", "question": "Le voyant de couleur rouge 'frein à main' allumé en circulant indique :", "choix": ["Une anomalie sur le système de freinage ou le frein serré", "Une simple usure des plaquettes", "Le bon fonctionnement de l'ABS"], "reponse": "Une anomalie sur le système de freinage ou le frein serré"},
        {"type": "ecrite", "question": "Dans quelle situation devez-vous obligatoirement allumer vos feux de brouillard arrière ?", "choix": [], "reponse": "Uniquement en cas de brouillard ou de chute de neige (interdit sous la pluie)."},
        {"type": "choix", "question": "Quelle est la distance de sécurité minimale à laisser en dépassant un cycliste en agglomération ?", "choix": ["1 mètre", "1,50 mètre", "2 mètres"], "reponse": "1 mètre"},
        {"type": "ecrite", "question": "Qu'indique l'indice de charge inscrit sur le flanc d'un pneumatique ?", "choix": [], "reponse": "Le poids maximal que le pneumatique peut supporter à sa pression nominale."},
        {"type": "choix", "question": "Le refus de priorité à un piéton engagé entraîne la perte de :", "choix": ["6 points", "4 points", "3 points"], "reponse": "6 points"},
        {"type": "ecrite", "question": "Pourquoi la fatigue visuelle augmente-t-elle le danger lors de la conduite de nuit ?", "choix": [], "reponse": "Elle diminue l'acuité visuelle, altère la perception des reliefs et augmente le temps de réaction."},
        {"type": "choix", "question": "En cas de contrôle, le défaut de contrôle technique à jour constitue une infraction passible :", "choix": ["D'une amende forfaitaire et d'une mise en fourrière potentielle", "D'un retrait de points", "D'une suspension de permis"], "reponse": "D'une amende forfaitaire et d'une mise en fourrière potentielle"},
        {"type": "ecrite", "question": "Expliquez l'effet de la force centrifuge sur un véhicule circulant dans un virage.", "choix": [], "reponse": "Force qui pousse le véhicule vers l'extérieur de la courbe, proportionnelle au carré de la vitesse."},
        {"type": "choix", "question": "Sur une route à double sens sans séparateur central, la vitesse maximale générale est fixée à :", "choix": ["80 km/h", "90 km/h", "70 km/h"], "reponse": "80 km/h"},
        {"type": "ecrite", "question": "Quel est le comportement attendu à l'intersection d'un feu jaune clignotant en bas ?", "choix": [], "reponse": "Passer avec prudence en appliquant les règles de priorité habituelles ou la signalisation associée."}
    ]


def charger_ecrite_permis_c_fiche_1():
    return {
        "type": "choix",
        "question": "Fiche Écrite 1 — Quelle est la vitesse maximale autorisée pour un véhicule de transport de marchandises de plus de 3.5 tonnes sur autoroute ?",
        "choix": ["80 km/h", "90 km/h", "110 km/h"],
        "reponse": "90 km/h"
    }

def charger_ecrite_permis_c_fiche_2():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 2 — Quel est le rôle principal du chronotachygraphe numérique ?",
        "choix": [],
        "reponse": "Enregistrer les temps de conduite, de repos, de travail et la vitesse du conducteur."
    }

def charger_ecrite_permis_c_fiche_3():
    return {
        "type": "choix",
        "question": "Fiche Écrite 3 — Quelle est la durée maximale de conduite journalière normale autorisée pour un conducteur de poids lourd ?",
        "choix": ["8 heures", "9 heures", "10 heures"],
        "reponse": "9 heures"
    }

def charger_ecrite_permis_c_fiche_4():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 4 — Qu'est-ce que la période de repos journalier régulier selon la RSE ?",
        "choix": [],
        "reponse": "Une période de repos ininterrompue d'au moins 11 heures."
    }

def charger_ecrite_permis_c_fiche_5():
    return {
        "type": "choix",
        "question": "Fiche Écrite 5 — À partir de quelle durée de conduite continue une pause de 45 minutes est-elle obligatoire ?",
        "choix": ["3 heures 30", "4 heures", "4 heures 30"],
        "reponse": "4 heures 30"
    }

def charger_ecrite_permis_c_fiche_6():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 6 — Expliquez comment fractionner la pause obligatoire de 45 minutes au cours de la conduite.",
        "choix": [],
        "reponse": "Par une première pause d'au moins 15 minutes suivie d'une seconde d'au moins 30 minutes."
    }

def charger_ecrite_permis_c_fiche_7():
    return {
        "type": "choix",
        "question": "Fiche Écrite 7 — Quelle est la limite maximale de la durée de conduite hebdomadaire ?",
        "choix": ["48 heures", "56 heures", "60 heures"],
        "reponse": "56 heures"
    }

def charger_ecrite_permis_c_fiche_8():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 8 — Quelle est la validité maximale de la carte de conducteur pour le chronotachygraphe ?",
        "choix": [],
        "reponse": "5 ans."
    }

def charger_ecrite_permis_c_fiche_9():
    return {
        "type": "choix",
        "question": "Fiche Écrite 9 — Quelle est la vitesse maximale autorisée pour un rigide de plus de 12 tonnes sur une route à double sens sans séparateur ?",
        "choix": ["80 km/h", "70 km/h", "90 km/h"],
        "reponse": "80 km/h"
    }

def charger_ecrite_permis_c_fiche_10():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 10 — Quelles sont les conditions pour pouvoir prolonger la conduite journalière à 10 heures ?",
        "choix": [],
        "reponse": "Cela est autorisé au maximum 2 fois par semaine."
    }

def charger_ecrite_permis_c_fiche_11():
    return {
        "type": "choix",
        "question": "Fiche Écrite 11 — À quelle fréquence minimale doit être effectué le contrôle technique d'un camion de plus de 3.5 tonnes ?",
        "choix": ["Tous les ans", "Tous les 6 mois", "Tous les 2 ans"],
        "reponse": "Tous les ans"
    }

def charger_ecrite_permis_c_fiche_12():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 12 — Quelles vérifications effectuez-vous sur les pneumatiques lors du contrôle de départ ?",
        "choix": [],
        "reponse": "L'absence de hernies ou de déchirures, la fixation des écrous, et la bonne pression visuelle."
    }

def charger_ecrite_permis_c_fiche_13():
    return {
        "type": "choix",
        "question": "Fiche Écrite 13 — Quel voyant rouge au tableau de bord indique une baisse critique de la pression d'air des freins ?",
        "choix": ["Le voyant de pression de freinage", "Le voyant de préchauffage", "Le voyant d'ABS"],
        "reponse": "Le voyant de pression de freinage"
    }

def charger_ecrite_permis_c_fiche_14():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 14 — Quel est le rôle de la bouteille anticongelante ou du dessicateur sur un circuit de freinage ?",
        "choix": [],
        "reponse": "Éliminer l'humidité contenue dans l'air comprimé pour éviter le gel des valves en hiver."
    }

def charger_ecrite_permis_c_fiche_15():
    return {
        "type": "choix",
        "question": "Fiche Écrite 15 — Quel dispositif de freinage ralentit le véhicule sans utiliser les freins à friction ?",
        "choix": ["Le ralentisseur (moteur ou hydraulique)", "Le frein de parc", "Le maître-cylindre"],
        "reponse": "Le ralentisseur (moteur ou hydraulique)"
    }

def charger_ecrite_permis_c_fiche_16():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 16 — Quelle la fonction principale du dispositif ABS ?",
        "choix": [],
        "reponse": "Éviter le blocage des roues lors d'un freinage d'urgence pour garder le contrôle de la trajectoire."
    }

def charger_ecrite_permis_c_fiche_17():
    return {
        "type": "choix",
        "question": "Fiche Écrite 17 — Quelle doit être la pression minimale d'air requise pour pouvoir desserrer le frein de stationnement ?",
        "choix": ["Environ 6 à 7 bars", "Environ 2 bars", "Environ 12 bars"],
        "reponse": "Environ 6 à 7 bars"
    }

def charger_ecrite_permis_c_fiche_18():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 18 — À quoi sert le système de suspension pneumatique sur un porteur lourd ?",
        "choix": [],
        "reponse": "Maintenir la hauteur du véhicule constante et améliorer la stabilité de la cargaison."
    }

def charger_ecrite_permis_c_fiche_19():
    return {
        "type": "choix",
        "question": "Fiche Écrite 19 — Quelle couleur possède le voyant indiquant l'activation du ralentisseur sur l'échappement ?",
        "choix": ["Orange ou Vert", "Rouge", "Bleu"],
        "reponse": "Orange ou Vert"
    }

def charger_ecrite_permis_c_fiche_20():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 20 — Que risquez-vous en cas de surcharge sur l'essieu moteur du véhicule ?",
        "choix": [],
        "reponse": "Une perte d'adhérence directionnelle à l'avant, une détérioration des routes et des sanctions financières."
    }

def charger_orale_permis_c_fiche_1():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 1 — Conduite et comportement.",
        "choix": [],
        "reponse": "Risques liés aux dimensions, à la masse, à l'inertie, aux angles morts et au centre de gravité élevé."
    }

def charger_orale_permis_c_fiche_2():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 2 — Prise en compte de l'environnement.",
        "choix": [],
        "reponse": "Éco-conduite, réduction des émissions polluantes, gestion du bruit et choix judicieux des itinéraires."
    }

def charger_orale_permis_c_fiche_3():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 3 — Équipements de sécurité des véhicules.",
        "choix": [],
        "reponse": "Rôle et fonctionnement de l'ABS, de l'EBS, de l'AEBS, des ceintures de sécurité, des airbags et des ralentisseurs."
    }

def charger_orale_permis_c_fiche_4():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 4 — Réglementation sociale européenne et documents.",
        "choix": [],
        "reponse": "Temps de conduite et de repos, utilisation de la carte chronotachygraphe, documents de bord et de transport (lettre de voiture)."
    }

def charger_orale_permis_c_fiche_5():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 5 — Chargement et surcharge.",
        "choix": [],
        "reponse": "Règles d'arrimage, répartition équilibrée des charges, limites réglementaires de PTAC et risques liés à la surcharge."
    }

def charger_orale_permis_c_fiche_6():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 6 — Éléments de mécanique et de sécurité.",
        "choix": [],
        "reponse": "Circuit d'air comprimé, freinage, suspension, direction, état d'usure et pression des pneumatiques."
    }

def charger_orale_permis_c_fiche_7():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 7 — Facteurs de risques et vigilance.",
        "choix": [],
        "reponse": "Fatigue, somnolence, baisse d'attention, risques liés à l'alcool, drogues, médicaments et distractions au volant."
    }

def charger_orale_permis_c_fiche_8():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 8 — Conduite en situations difficiles.",
        "choix": [],
        "reponse": "Gestion de la conduite sous la pluie, le brouillard, la neige, le verglas, face au vent latéral et conduite de nuit."
    }

def charger_orale_permis_c_fiche_9():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 9 — Situations d'urgence et accidents.",
        "choix": [],
        "reponse": "Comportement en cas de panne, d'incendie, protocole de passage dans les tunnels routiers, protection, alerte et secourisme."
    }

def charger_orale_permis_c_fiche_10():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 10 — Signalisation spécifique aux véhicules lourds.",
        "choix": [],
        "reponse": "Panneaux de restriction de tonnage, de hauteur, de largeur, disques de limitation de vitesse arrière et signalisation des angles morts."
    }

def charger_orale_permis_c_fiche_11():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 11 — Règles de circulation et priorités.",
        "choix": [],
        "reponse": "Interdictions d'emprunter certaines voies, règles de croisement et de dépassement, distances de sécurité spécifiques entre poids lourds."
    }

def charger_orale_permis_c_fiche_12():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 12 — Santé et hygiène de vie des conducteurs.",
        "choix": [],
        "reponse": "Troubles musculo-squelettiques (maux de dos), alimentation adaptée, importance du sommeil et examens médicaux périodiques."
    }

banque_ecrites_permis_c = [
    charger_ecrite_permis_c_fiche_1(),
    charger_ecrite_permis_c_fiche_2(),
    charger_ecrite_permis_c_fiche_3(),
    charger_ecrite_permis_c_fiche_4(),
    charger_ecrite_permis_c_fiche_5(),
    charger_ecrite_permis_c_fiche_6(),
    charger_ecrite_permis_c_fiche_7(),
    charger_ecrite_permis_c_fiche_8(),
    charger_ecrite_permis_c_fiche_9(),
    charger_ecrite_permis_c_fiche_10(),
    charger_ecrite_permis_c_fiche_11(),
    charger_ecrite_permis_c_fiche_12(),
    charger_ecrite_permis_c_fiche_13(),
    charger_ecrite_permis_c_fiche_14(),
    charger_ecrite_permis_c_fiche_15(),
    charger_ecrite_permis_c_fiche_16(),
    charger_ecrite_permis_c_fiche_17(),
    charger_ecrite_permis_c_fiche_18(),
    charger_ecrite_permis_c_fiche_19(),
    charger_ecrite_permis_c_fiche_20()
]

# Ajout dynamique de la clé "numero" pour éviter le plantage lors de l'affichage
for index, fiche in enumerate(banque_ecrites_permis_c, start=1):
    fiche["numero"] = index

banque_orales_permis_c = [
    charger_orale_permis_c_fiche_1(),
    charger_orale_permis_c_fiche_2(),
    charger_orale_permis_c_fiche_3(),
    charger_orale_permis_c_fiche_4(),
    charger_orale_permis_c_fiche_5(),
    charger_orale_permis_c_fiche_6(),
    charger_orale_permis_c_fiche_7(),
    charger_orale_permis_c_fiche_8(),
    charger_orale_permis_c_fiche_9(),
    charger_orale_permis_c_fiche_10(),
    charger_orale_permis_c_fiche_11(),
    charger_orale_permis_c_fiche_12(),
]

# Cette boucle ajoute automatiquement la clé "numero" à chaque fiche du tableau !
for index, fiche in enumerate(banque_orales_permis_c, start=1):
    fiche["numero"] = index
    
def charger_ecrite_permis_ce_fiche_1():
    return {
        "type": "choix",
        "question": "Fiche Écrite 1 — Quelle est la longueur maximale autorisée pour un ensemble articulé standard (tracteur + semi-remorque) en Europe ?",
        "choix": ["16,50 mètres", "18,75 mètres", "12,00 mètres"],
        "reponse": "16,50 mètres"
    }

def charger_ecrite_permis_ce_fiche_2():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 2 — Définissez précisément la notion de PTRA (Poids Total Roulant Autorisé).",
        "choix": [],
        "reponse": "La masse maximale limite fixée par l'administration que l'ensemble des véhicules reliés ne doit pas dépasser."
    }

def charger_ecrite_permis_ce_fiche_3():
    return {
        "type": "choix",
        "question": "Fiche Écrite 3 — Quelle est la longueur maximale autorisée pour un train routier (porteur + remorque) ?",
        "choix": ["18,75 mètres", "16,50 mètres", "20,00 mètres"],
        "reponse": "18,75 mètres"
    }

def charger_ecrite_permis_ce_fiche_4():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 4 — Qu'est-ce que le principe du report de charge sur un ensemble de véhicules ?",
        "choix": [],
        "reponse": "Technique de chargement optimisant le poids transféré sur l'essieu du tracteur sans dépasser la limite légale."
    }

def charger_ecrite_permis_ce_fiche_5():
    return {
        "type": "choix",
        "question": "Fiche Écrite 5 — La vitesse maximale d'un ensemble de plus de 12t sur route à double sens sans séparateur est de :",
        "choix": ["80 km/h", "70 km/h", "90 km/h"],
        "reponse": "80 km/h"
    }

def charger_ecrite_permis_ce_fiche_6():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 6 — Quel document de transport remplace obligatoirement la lettre de voiture nationale lors des acheminements internationaux ?",
        "choix": [],
        "reponse": "La lettre de voiture internationale CMR."
    }

def charger_ecrite_permis_ce_fiche_7():
    return {
        "type": "choix",
        "question": "Fiche Écrite 7 — À partir de quel PTRA la présence d'un deuxième extincteur est-elle obligatoire à bord de l'ensemble ?",
        "choix": ["Dès que le véhicule transporte des marchandises", "Uniquement en cas de transport ADR", "Au-dessus de 12 tonnes"],
        "reponse": "Dès que le véhicule transporte des marchandises"
    }

def charger_ecrite_permis_ce_fiche_8():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 8 — Quel est le rôle du dispositif de freinage de secours automatique d'une remorque ?",
        "choix": [],
        "reponse": "Serrer instantanément les freins de la remorque en cas de rupture physique de l'attelage en mouvement."
    }

def charger_ecrite_permis_ce_fiche_9():
    return {
        "type": "choix",
        "question": "Fiche Écrite 9 — Un ensemble de véhicules de plus de 3.5 tonnes circulant sous la pluie sur autoroute est limité à :",
        "choix": ["80 km/h", "90 km/h", "70 km/h"],
        "reponse": "80 km/h"
    }

def charger_ecrite_permis_ce_fiche_10():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 10 — Quelle est l'utilité du dispositif d'aide au démarrage en côte sur un tracteur routier lourd ?",
        "choix": [],
        "reponse": "Maintenir la pression de freinage quelques secondes pour éviter le recul de l'ensemble lors du lâcher de pédale."
    }

def charger_ecrite_permis_ce_fiche_11():
    return {
        "type": "choix",
        "question": "Fiche Écrite 11 — Le contrôle technique périodique d'une semi-remorque de plus de 3.5 tonnes doit être réalisé :",
        "choix": ["Chaque année", "Tous les 6 mois", "Tous les 2 ans"],
        "reponse": "Chaque année"
    }

def charger_ecrite_permis_ce_fiche_12():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 12 — Comment s'appelle l'élément d'accouplement fixé sous le châssis avant d'une semi-remorque ?",
        "choix": [],
        "reponse": "Le pivot d'attelage (ou King-Pin)."
    }

def charger_ecrite_permis_ce_fiche_13():
    return {
        "type": "choix",
        "question": "Fiche Écrite 13 — La masse maximale autorisée sous un essieu moteur isolé en France est de :",
        "choix": ["13 tonnes", "11,5 tonnes", "10 tonnes"],
        "reponse": "13 tonnes"
    }

def charger_ecrite_permis_ce_fiche_14():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 14 — Quelles sont les vérifications obligatoires concernant les béquilles d'une semi-remorque avant le départ ?",
        "choix": [],
        "reponse": "S'assurer qu'elles sont totalement remontées et que la manivelle de commande est repliée et verrouillée."
    }

def charger_ecrite_permis_ce_fiche_15():
    return {
        "type": "choix",
        "question": "Fiche Écrite 15 — Sur une autoroute à 3 voies, un ensemble routier dont la longueur dépasse 7 mètres :",
        "choix": ["A l'interdiction d'emprunter la voie la plus à gauche", "Peut circuler sur toutes les voies", "Doit rester sur la voie de droite"],
        "reponse": "A l'interdiction d'emprunter la voie la plus à gauche"
    }

def charger_ecrite_permis_ce_fiche_16():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 16 — Quel est l'impact de la force d'inertie de la remorque sur le tracteur lors d'une décélération ?",
        "choix": [],
        "reponse": "La remorque pousse le tracteur, augmentant la charge dynamique exercée sur l'arrière du véhicule moteur."
    }

def charger_ecrite_permis_ce_fiche_17():
    return {
        "type": "choix",
        "question": "Fiche Écrite 17 — Le certificat d'immatriculation d'un ensemble de véhicules comprend :",
        "choix": ["Deux cartes grises distinctes (tracteur et remorque)", "Une seule carte grise commune", "Une carte grise uniquement pour le tracteur"],
        "reponse": "Deux cartes grises distinctes (tracteur et remorque)"
    }

def charger_ecrite_permis_ce_fiche_18():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 18 — Quelles sont les sanctions en cas de dépassement du PTRA constaté lors d'un pesage ?",
        "choix": [],
        "reponse": "Une amende par tranche de dépassement de poids, immobilisation du véhicule et obligation de décharger."
    }

def charger_ecrite_permis_ce_fiche_19():
    return {
        "type": "choix",
        "question": "Fiche Écrite 19 — Le dispositif de signalisation des angles morts doit être apposé :",
        "choix": ["Sur le tracteur ET sur la remorque selon des emplacements réglementaires", "Uniquement à l'arrière de la remorque", "Uniquement sur les portières du tracteur"],
        "reponse": "Sur le tracteur ET sur la remorque selon des emplacements réglementaires"
    }

def charger_ecrite_permis_ce_fiche_20():
    return {
        "type": "ecrite",
        "question": "Fiche Écrite 20 — Pourquoi est-il primordial de vérifier le cordon ABS/EBS lors de l'attelage ?",
        "choix": [],
        "reponse": "Pour garantir la transmission des signaux de freinage antiblocage et de contrôle de stabilité à la remorque."
    }
def charger_orale_permis_ce_fiche_1():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 1 — Conduite d'un ensemble de véhicules.",
        "choix": [],
        "reponse": "Risques majeurs de mise en portefeuille, trajectoire déportée de la remorque dans les courbes et distances d'arrêt augmentées."
    }

def charger_orale_permis_ce_fiche_2():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 2 — Prise en compte de l'environnement pour ensembles.",
        "choix": [],
        "reponse": "Gestion fine de la consommation en fonction de la masse globale, éco-conduite et planification des itinéraires adaptés aux grands gabarits."
    }

def charger_orale_permis_ce_fiche_3():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 3 — Équipements spécifiques aux ensembles.",
        "choix": [],
        "reponse": "Rôle de la sellette, du pivot d'attelage, verrouillage mécanique, utilisation des béquilles et branchements pneumatiques (flexibles rouge et jaune)."
    }

def charger_orale_permis_ce_fiche_4():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 4 — Réglementation sociale européenne et documents de l'ensemble.",
        "choix": [],
        "reponse": "Contrôle des disques/cartes chronotachygraphe, temps de conduite, présence des cartes grises respectives du tracteur et de la remorque."
    }

def charger_orale_permis_ce_fiche_5():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 5 — Chargement, répartition et arrimage sur remorque.",
        "choix": [],
        "reponse": "Calcul du centre de gravité, centrage des éléments lourds au-dessus des essieux de la remorque, amarrage réglementaire et gestion du PTRA."
    }

def charger_orale_permis_ce_fiche_6():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 6 — Vérification mécanique et sécurité de l'attelage.",
        "choix": [],
        "reponse": "Contrôle du circuit de freinage continu automatique, étanchéité des mains d'accouplement pneumatiques et vérification des pneumatiques de l'ensemble."
    }

def charger_orale_permis_ce_fiche_7():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 7 — Risques liés à l'état physique du conducteur d'ensemble.",
        "choix": [],
        "reponse": "Fatigue accrue par l'effort de concentration lors des manœuvres complexes et gestion des temps de pause physiologiques."
    }

def charger_orale_permis_ce_fiche_8():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 8 — Conduite d'un ensemble en conditions difficiles.",
        "choix": [],
        "reponse": "Haute vulnérabilité au vent latéral dû à la surface de voilure des carrosseries, risques accrus de lacet et de dérapage sur sol glissant."
    }

def charger_orale_permis_ce_fiche_9():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 9 — Situations critiques et accidents spécifiques.",
        "choix": [],
        "reponse": "Procédure d'urgence en cas de décrochage accidentel de la remorque, utilisation du frein de secours automatique et extinction des incendies de remorque."
    }

def charger_orale_permis_ce_fiche_10():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 10 — Signalisation et gabarit de grande longueur.",
        "choix": [],
        "reponse": "Respect strict de la signalisation d'accès (hauteur, longueur maximale, tonnage), port des plaques d'identification de grande longueur à l'arrière."
    }

def charger_orale_permis_ce_fiche_11():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 11 — Règles de circulation et croisement des ensembles.",
        "choix": [],
        "reponse": "Calcul des trajectoires dans les carrefours, compensation de l'effet de balayage de la structure remorquée et respect des distances d'isolement réglementaires."
    }

def charger_orale_permis_ce_fiche_12():
    return {
        "type": "ecrite",
        "question": "Fiche Orale 12 — Santé au travail et prévention des risques de manutention.",
        "choix": [],
        "reponse": "Prévention des chutes lors des phases d'accrochage/décrochage, manipulation ergonomique des béquilles et prévention des risques articulaires."
    }

banque_ecrites_permis_ce = [
    charger_ecrite_permis_ce_fiche_1(),
    charger_ecrite_permis_ce_fiche_2(),
    charger_ecrite_permis_ce_fiche_3(),
    charger_ecrite_permis_ce_fiche_4(),
    charger_ecrite_permis_ce_fiche_5(),
    charger_ecrite_permis_ce_fiche_6(),
    charger_ecrite_permis_ce_fiche_7(),
    charger_ecrite_permis_ce_fiche_8(),
    charger_ecrite_permis_ce_fiche_9(),
    charger_ecrite_permis_ce_fiche_10(),
    charger_ecrite_permis_ce_fiche_11(),
    charger_ecrite_permis_ce_fiche_12(),
    charger_ecrite_permis_ce_fiche_13(),
    charger_ecrite_permis_ce_fiche_14(),
    charger_ecrite_permis_ce_fiche_15(),
    charger_ecrite_permis_ce_fiche_16(),
    charger_ecrite_permis_ce_fiche_17(),
    charger_ecrite_permis_ce_fiche_18(),
    charger_ecrite_permis_ce_fiche_19(),
    charger_ecrite_permis_ce_fiche_20()
]

# Injection automatique des numéros manquants pour éviter l'erreur d'affichage
for index, fiche in enumerate(banque_ecrites_permis_ce, start=1):
    fiche["numero"] = index

banque_orales_permis_ce = [
    charger_orale_permis_ce_fiche_1(),
    charger_orale_permis_ce_fiche_2(),
    charger_orale_permis_ce_fiche_3(),
    charger_orale_permis_ce_fiche_4(),
    charger_orale_permis_ce_fiche_5(),
    charger_orale_permis_ce_fiche_6(),
    charger_orale_permis_ce_fiche_7(),
    charger_orale_permis_ce_fiche_8(),
    charger_orale_permis_ce_fiche_9(),
    charger_orale_permis_ce_fiche_10(),
    charger_orale_permis_ce_fiche_11(),
    charger_orale_permis_ce_fiche_12()
]

# Injection automatique des numéros manquants pour éviter l'erreur d'affichage
for index, fiche in enumerate(banque_orales_permis_ce, start=1):
    fiche["numero"] = index

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
    st.header("Permis AM")

with tab2:
    st.header("Permis B")

with tab3:
    st.header("Interrogation Orale — Permis C")
    st.caption("Tirage au sort d'une fiche complète parmi les 12 fiches.")

    if "fiche_orale_choisie_c" not in st.session_state:
        st.session_state.fiche_orale_choisie_c = random.choice(
            banque_orales_permis_c
        )

    if st.button("TIRER UNE AUTRE FICHE ORALE AU HASARD", key="btn_orale_c"):
        st.session_state.fiche_orale_choisie_c = random.choice(
            banque_orales_permis_c
        )
        if "rep_orale_c" in st.session_state:
            del st.session_state["rep_orale_c"]
        st.rerun()

    fiche_o = st.session_state.fiche_orale_choisie_c
    st.markdown(f"### Fiche Orale Numéro {fiche_o.get('numero', 'Non défini')}")
    st.info(fiche_o["question"])

    st.text_area(
        "Saisissez vos notes de préparation :",
        key="rep_orale_c",
        placeholder="Écrivez ici vos arguments pour l'examen oral...",
    )

    if st.checkbox("Afficher le guide de correction complet", key="chk_oral_c"):
        st.success(f"Éléments clés attendus : {fiche_o['reponse']}")


# --- 5. CONFIGURATION DE L'ONGLET 4 : FICHES ÉCRITES PERMIS C (1 parmi 20) ---
with tab4:
    st.header("Interrogation Écrite — Permis C")
    st.caption("Tirage au sort d'une fiche de questions parmi les 20 fiches.")

    if "fiche_ecrite_choisie_c" not in st.session_state:
        st.session_state.fiche_ecrite_choisie_c = random.choice(
            banque_ecrites_permis_c
        )

    if st.button("TIRER UNE AUTRE FICHE ÉCRITE AU HASARD", key="btn_ecrite_c"):
        st.session_state.fiche_ecrite_choisie_c = random.choice(
            banque_ecrites_permis_c
        )
        if "rep_ecrite_c" in st.session_state:
            del st.session_state["rep_ecrite_c"]
        st.rerun()

    fiche_e = st.session_state.fiche_ecrite_choisie_c
    st.markdown(f"### Fiche Écrite Numéro {fiche_e['numero']}")
    st.info(fiche_e["question"])

    if fiche_e["type"] == "choix":
        st.selectbox(
            "Sélectionnez votre réponse :",
            options=["Choisir une réponse..."] + fiche_e["choix"],
            key="rep_ecrite_c",
            index=0,
        )
    else:
        st.text_area(
            "Votre réponse rédigée :",
            key="rep_ecrite_c",
            placeholder="Saisissez votre texte ici...",
        )

    if st.checkbox("Afficher la réponse exacte", key="chk_ecrit_c"):
        st.success(f"Réponse attendue : {fiche_e['reponse']}")


with tab5:
    if "verrou_orale_ce" not in st.session_state:
        st.session_state.verrou_orale_ce = False

    v_oral_ce = st.session_state.verrou_orale_ce

    st.header("Interrogation Orale — Permis CE")
    st.caption("Tirage au sort d'une fiche complète parmi les 12 fiches.")

    if "fiche_orale_choisie_ce" not in st.session_state:
        st.session_state.fiche_orale_choisie_ce = random.choice(
            banque_orales_permis_ce
        )

    if st.button(
        "TIRER UNE AUTRE FICHE ORALE AU HASARD",
        key="btn_orale_ce",
        disabled=v_oral_ce,
        use_container_width=True,
    ):
        st.session_state.fiche_orale_choisie_ce = random.choice(
            banque_orales_permis_ce
        )
        if "rep_orale_ce" in st.session_state:
            del st.session_state["rep_orale_ce"]
        st.rerun()

    fiche_o_ce = st.session_state.fiche_orale_choisie_ce
    st.markdown(f"### Fiche Orale Numéro {fiche_o_ce['numero']}")
    st.info(fiche_o_ce["question"])

    st.text_area(
        "Saisissez vos notes de préparation :",
        key="rep_orale_ce",
        disabled=v_oral_ce,
        placeholder="Écrivez ici vos arguments pour l'examen oral...",
    )

    if st.checkbox("Afficher le guide de correction complet", key="chk_oral_ce"):
        st.success(f"Éléments clés attendus : {fiche_o_ce['reponse']}")

    st.write("---")
    st.subheader("Synthèse et validation")
    certif_oral = st.checkbox(
        "Je certifie avoir terminé la préparation de cette fiche orale CE.",
        key="cert_oral_ce",
        disabled=v_oral_ce,
    )

    if st.button(
        "VALIDER ET VERROUILLER L'ATELIER ORAL CE",
        key="val_oral_ce",
        disabled=v_oral_ce,
        use_container_width=True,
    ):
        if not certif_oral:
            st.warning("Veuillez cocher la case de certification avant.")
        else:
            st.session_state.verrou_orale_ce = True
            st.rerun()

    if v_oral_ce:
        st.info("Cet atelier oral a été validé et verrouillé.")


# --- 5. CONFIGURATION DE L'ONGLET 6 : FICHES ÉCRITES PERMIS CE (1 parmi 20) ---
with tab6:
    if "verrou_ecrite_ce" not in st.session_state:
        st.session_state.verrou_ecrite_ce = False

    v_ecrit_ce = st.session_state.verrou_ecrite_ce

    st.header("Interrogation Écrite — Permis CE")
    st.caption("Tirage au sort d'une fiche de questions parmi les 20 fiches.")

    if "fiche_ecrite_choisie_ce" not in st.session_state:
        st.session_state.fiche_ecrite_choisie_ce = random.choice(
            banque_ecrites_permis_ce
        )

    if st.button(
        "TIRER UNE AUTRE FICHE ÉCRITE AU HASARD",
        key="btn_ecrite_ce",
        disabled=v_ecrit_ce,
        use_container_width=True,
    ):
        st.session_state.fiche_ecrite_choisie_ce = random.choice(
            banque_ecrites_permis_ce
        )
        if "rep_ecrite_ce" in st.session_state:
            del st.session_state["rep_ecrite_ce"]
        st.rerun()

    fiche_e_ce = st.session_state.fiche_ecrite_choisie_ce
    st.markdown(f"### Fiche Écrite Numéro {fiche_e_ce['numero']}")
    st.info(fiche_e_ce["question"])

    if fiche_e_ce["type"] == "choix":
        st.selectbox(
            "Sélectionnez votre réponse :",
            options=["Choisir une réponse..."] + fiche_e_ce["choix"],
            key="rep_ecrite_ce",
            disabled=v_ecrit_ce,
            index=0,
        )
    else:
        st.text_area(
            "Votre réponse rédigée :",
            key="rep_ecrite_ce",
            disabled=v_ecrit_ce,
            placeholder="Saisissez votre texte ici...",
        )

    if st.checkbox("Afficher la réponse exacte", key="chk_ecrit_ce"):
        st.success(f"Réponse attendue : {fiche_e_ce['reponse']}")

    st.write("---")
    st.subheader("Synthèse et validation")
    certif_ecrit = st.checkbox(
        "Je certifie avoir répondu aux questions de cette fiche écrite CE.",
        key="cert_ecrit_ce",
        disabled=v_ecrit_ce,
    )

    if st.button(
        "VALIDER ET VERROUILLER L'ATELIER ÉCRIT CE",
        key="val_ecrit_ce",
        disabled=v_ecrit_ce,
        use_container_width=True,
    ):
        if not certif_ecrit:
            st.warning("Veuillez cocher la case de certification avant.")
        else:
            st.session_state.verrou_ecrite_ce = True
            st.rerun()

    if v_ecrit_ce:
        st.info("Cet atelier écrit a été validé et verrouillé.")












