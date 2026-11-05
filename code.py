# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application Permis - Revisions",
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
st.title("Application Permis - Revisions")
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


def afficher_validation_orale(num_fiche):
    """Affiche l'encadré officiel de validation pour les ateliers oraux
    avec l'identité complète de l'élève.
    """
    nom = st.session_state.get("nom_var", "NON RENSEIGNÉ")
    prenom = st.session_state.get("prenom_var", "Non renseigné")
    classe = st.session_state.get("classe_var", "NON RENSEIGNÉ")

    st.write("---")
    st.subheader("Validation officielle de la préparation")
    
    container_style = """
    <div style='border: 2px solid #000000; padding: 20px; border-radius: 5px; background-color: #f9f9f9;'>
        <p><b>Nom :</b> {}</p>
        <p><b>Prénom :</b> {}</p>
        <p><b>Classe :</b> {}</p>
        <p><b>Évaluation :</b> Interrogation Orale — Fiche {}</p>
        <hr style='border: 1px solid #cccccc;'>
        <h4 style='margin: 0; color: #2ea44f;'>Statut : Fiche validée et verrouillée</h4>
    </div>
    """.format(nom, prenom, classe, num_fiche)
    
    st.markdown(container_style, unsafe_allow_html=True)
    st.write("---")



def calculer_et_afficher_note(liste_questions, prefixe_session, num_fiche):
    """Calcule le score base sur les reponses fournies (QCM) ou saisies (texte)
    et affiche le rapport officiel de l'evaluation.
    """
    score = 0
    total_questions = len(liste_questions) if isinstance(liste_questions, list) else 0
    
    # Parcours complet de toutes les questions de la fiche
    if isinstance(liste_questions, list):
        for idx, q in enumerate(liste_questions):
            cle_reponse = f"{prefixe_session}_{idx}_{num_fiche}"
            rep_eleve = st.session_state.get(cle_reponse, "")
            
            if q.get("type") == "choix":
                # Pour un QCM, on verifie si la reponse est exacte
                if rep_eleve == q.get("reponse"):
                    score += 1
            else:
                # Pour de l'oral/texte, on verifie que le champ n'est pas vide
                if str(rep_eleve).strip() and str(rep_eleve).strip() != "Choisir une reponse...":
                    score += 1

    nom = st.session_state.get("nom_var", "NON RENSEIGNE")
    prenom = st.session_state.get("prenom_var", "Non renseigne")
    classe = st.session_state.get("classe_var", "NON RENSEIGNE")

    st.write("---")
    st.subheader("Resultats officiels de l'evaluation")
    
    container_style = """
    <div style='border: 2px solid #000000; padding: 20px; border-radius: 5px; background-color: #f9f9f9;'>
        <p><b>Nom :</b> {}</p>
        <p><b>Prenom :</b> {}</p>
        <p><b>Classe :</b> {}</p>
        <p><b>Evaluation :</b> Fiche {}</p>
        <hr style='border: 1px solid #cccccc;'>
        <h4 style='margin: 0; color: #1f77b4;'>Questions traitees : {} / {}</h4>
    </div>
    """.format(nom, prenom, classe, num_fiche, score, total_questions)
    
    st.markdown(container_style, unsafe_allow_html=True)
    st.write("---")

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
    if not banque_questions_permis_am or not isinstance(
        banque_questions_permis_am, list
    ):
        banque_questions_permis_am = [{
            "type": "choix",
            "question": "Quelle est la vitesse maximale par construction d'un cyclomoteur de moins de 50 cm³ ?",
            "choix": ["45 km/h", "50 km/h", "60 km/h"],
            "reponse": "45 km/h",
        }]

    # Correction de la structure et nettoyage de la coquille d'index repérée sur votre écran
    for index, fiche in enumerate(banque_questions_permis_am, start=1):
        fiche["numero"] = index
        # Si la clé 'choix' est absente ou mal placée pour un type choix, on initialise une liste propre
        if fiche["type"] == "choix" and "choix" not in fiche:
            fiche["choix"] = [
                "Interdit le franchissement",
                "Permet le chevauchement",
                "Aucune règle",
            ]
    
def charger_banque_permis_b():
    """Retourne la banque contenant 20 questions pour le Permis B."""
    return [
        {"type": "choix", "question": "Quelle est la vitesse maximale autorisée sur autoroute par temps sec pour un jeune conducteur (permis probatoire) ?", "choix": ["110 km/h", "130 km/h", "100 km/h"], "reponse": "110 km/h"},
        {"type": "choix", "question": "Quelle est l'utilité du système de freinage ABS en cas de freinage d'urgence ?", "choix": ["Réduire considérablement la distance de freinage.","Empêcher le blocage des roues pour garder le contrôle de la trajectoire."," Augmenter la puissance des freins arrière." ], "reponse": "Empêcher le blocage des roues pour garder le contrôle de la trajectoire."},
        {"type": "choix", "question": "Le taux d'alcoolémie limite dans le sang pour un conducteur en permis probatoire est de :", "choix": ["0,20 g/l", "0,50 g/l", "0,00 g/l"], "reponse": "0,20 g/l"},
        {"type": "choix", "question": "Quelles sont les conditions météorologiques qui obligent à réduire sa vitesse à 50 km/h sur l'ensemble du réseau routier ?", "choix": ["En cas de fortes chutes de grêle uniquement.","Lorsque la visibilité descend en dessous de 50 mètres.","Dès l'apparition des premiers flocons de neige." ], "reponse": "Lorsque la visibilité descend en dessous de 50 mètres."},
        {"type": "choix", "question": "L'utilisation d'un téléphone tenu en main en conduisant entraîne un retrait de :", "choix": ["3 points", "2 points", "4 points"], "reponse": "3 points"},
        {"type": "choix", "question": "Qu'est-ce que l'aquaplaning et comment y faire face ?", "choix": ["Une perte d'adhérence des pneus due à une pellicule d'eau; il faut débrayer sans freiner.", "Un échauffement des plaquettes de frein; il faut pomper sur la pédale.", "Une perte de contrôle dans les virages due à la force centrifuge."], "reponse": "Une perte d'adhérence des pneus due à une pellicule d'eau; il faut débrayer sans freiner."},
        {"type": "choix", "question": "Quelle est la durée de la période probatoire pour un conducteur ayant suivi la conduite accompagnée (AAC) ?", "choix": ["2 ans", "3 ans", "1 an"], "reponse": "2 ans"},
        {"type": "choix", "question": "Pourquoi la fatigue visuelle augmente-t-elle le danger lors de la conduite de nuit ?", "choix": ["Elle diminue l'acuité visuelle, altère la perception des reliefs et augmente le temps de réaction.", "Elle rend les feux de route moins puissants.", "Elle supprime l'efficacité des rétroviseurs extérieurs."], "reponse": "Elle diminue l'acuité visuelle, altère la perception des reliefs et augmente le temps de réaction."},
        {"type": "choix", "question": "Le refus de priorité à un piéton engagé entraîne la perte de :", "choix": ["6 points", "4 points", "3 points"], "reponse": "6 points"},
        {"type": "choix", "question": "Expliquez l'effet de la force centrifuge sur un véhicule circulant dans un virage.", "choix": ["C'est la force qui pousse le véhicule vers l'extérieur de la courbe.", "C'est la force qui plaque le véhicule au sol au freinage.", "C'est l'adhérence maximale des roues arrière."], "reponse": "C'est la force qui pousse le véhicule vers l'extérieur de la courbe."},
        {"type": "choix", "question": "Sur une route à double sens sans séparateur central, la vitesse maximale générale est fixée à :", "choix": ["80 km/h", "90 km/h", "70 km/h"], "reponse": "80 km/h"},
        {"type": "choix", "question": "Qu'est-ce que le phénomène du 'tunnel visuel' provoqué par l'augmentation de la vitesse ?", "choix": ["Plus la vitesse augmente, plus le champ visuel se rétrécit sur le centre de la route.", "L'éblouissement provoqué par les feux des autres voitures.", "L'obligation d'allumer ses feux dans les zones sombres."], "reponse": "Plus la vitesse augmente, plus le champ visuel se rétrécit sur le centre de la route."},
        {"type": "choix", "question": "Le délai d'élimination de l'alcool par l'organisme pour un verre d'alcool standard est d'environ :", "choix": ["1 heure à 2 heures", "30 minutes", "4 heures"], "reponse": "1 heure à 2 heures"},
        {"type": "choix", "question": "La différence de comportement entre un voyant moteur orange et un voyant moteur rouge est :", "choix": ["Orange indique une anomalie à vérifier; rouge impose un arrêt de sécurité immédiat.", "Orange indique une surconsommation; rouge indique une panne d'essence.", "Il n'y a aucune différence d'urgence entre les deux couleurs."], "reponse": "Orange indique une anomalie à vérifier; rouge impose un arrêt de sécurité immédiat."},
        {"type": "choix", "question": "L'oubli de l'utilisation des clignotants lors d'un changement de direction est passible d'un retrait de :", "choix": ["3 points", "2 points", "1 point"], "reponse": "3 points"},
        {"type": "choix", "question": "Qu'est-ce que la 'distance de réaction' et quels facteurs peuvent l'allonger ?", "choix": ["Distance parcourue avant de freiner; allongée par la fatigue, l'alcool ou le téléphone.", "Distance nécessaire pour immobiliser les roues.", "Espace de sécurité réglementaire sur autoroute."], "reponse": "Distance parcourue avant de freiner; allongée par la fatigue, l'alcool ou le téléphone."},
        {"type": "choix", "question": "Un conducteur commet un grand excès de vitesse dès lors qu'il dépasse la limitation de :", "choix": ["50 km/h ou plus", "30 km/h", "40 km/h"], "reponse": "50 km/h ou plus"},
        {"type": "choix", "question": "Quel est le risque de circuler avec des amortisseurs usés ou défectueux ?", "choix": ["Augmentation des distances de freinage et mauvaise tenue de route.", "Une baisse immédiate de la pression des pneus.", "Le blocage du système ABS."], "reponse": "Augmentation des distances de freinage et mauvaise tenue de route."},
        {"type": "choix", "question": "Le stationnement dangereux (bloquant la visibilité dans un virage ou un sommet de côte) entraîne un retrait de :", "choix": ["3 points", "1 point", "6 points"], "reponse": "3 points"},
        {"type": "choix", "question": "Pourquoi la distance de freinage est-elle multipliée par deux sur chaussée mouillée ?", "choix": ["L'eau diminue l'adhérence entre le pneu et la route.", "Le moteur perd de sa puissance sous la pluie.", "Le système ABS s'active en continu."], "reponse": "L'eau diminue l'adhérence entre le pneu et la route."},
        {"type": "choix", "question": "Le délit de fuite après avoir causé un accident est une infraction grave passible :", "choix": ["D'une peine de prison, d'une lourde amende et d'un retrait de 6 points", "D'une simple amende forfaitaire de première classe", "D'une suspension de permis de 3 mois maximum"], "reponse": "D'une peine de prison, d'une lourde amende et d'un retrait de 6 points"},
        {"type": "choix", "question": "Expliquez la règle des deux secondes pour maintenir une distance de sécurité minimale.", "choix": ["Il doit s'écouler au moins 2 secondes entre mon véhicule et celui qui me précède.", "Je dois mettre 2 secondes pour changer de rapport de vitesse.", "C'est le temps d'arrêt obligatoire devant un feu orange clignotant."], "reponse": "Il doit s'écouler au moins 2 secondes entre mon véhicule et celui qui me précède."},
        {"type": "choix", "question": "Un excès de vitesse inférieur à 20 km/h hors agglomération entraîne la perte de :", "choix": ["1 point", "2 points", "3 points"], "reponse": "1 point"},
        {"type": "choix", "question": "Quel est le danger lié au phénomène de somnolence au volant ?", "choix": ["Il provoque des micro-sommeils entraînant une perte totale de contrôle.", "Il diminue la distance de freinage.", "Il supprime l'angle mort gauche."], "reponse": "Il provoque des micro-sommeils entraînant une perte totale de contrôle."},
        {"type": "choix", "question": "Le taux d'alcoolémie maximal autorisé pour un conducteur expérimenté (hors période probatoire) est de :", "choix": ["0,50 g/l de sang", "0,20 g/l de sang", "0,80 g/l de sang"], "reponse": "0,50 g/l de sang"},
        {"type": "choix", "question": "En l'absence de toute signalisation à une intersection, quelle règle de priorité s'applique ?", "choix": ["La priorité à droite", "La priorité au véhicule le plus rapide", "La priorité à la voie la plus large"], "reponse": "La priorité à droite"},
        {"type": "choix", "question": "À l'approche d'un rond-point équipé d'un panneau 'Cédez le passage', la priorité est aux véhicules :", "choix": ["Déjà engagés sur l'anneau", "Qui s'engagent en même temps que moi", "Arrivant par les rues de droite"], "reponse": "Déjà engagés sur l'anneau"},
        {"type": "choix", "question": "Quel est le comportement attendu à l'intersection d'un feu jaune clignotant en bas ?", "choix": ["Passer avec prudence en appliquant les règles de priorité habituelles", "S'arrêter impérativement comme à un feu rouge", "Accélérer pour dégager le carrefour au plus vite"], "reponse": "Passer avec prudence en appliquant les règles de priorité habituelles"},
        {"type": "choix", "question": "Devant un panneau 'Stop', l'arrêt complet des roues du véhicule est :", "choix": ["Obligatoire dans tous les cas", "Facultatif si la voie est totalement libre", "Obligatoire uniquement si un piéton traverse"], "reponse": "Obligatoire dans tous les cas"},
        {"type": "choix", "question": "Quelle est la différence fondamentale d'obligation entre un panneau Stop et un Cédez le passage ?", "choix": ["Le Stop impose l'arrêt complet obligatoire, le Cédez le passage permet de passer si c'est libre", "Le Cédez le passage est réservé aux vélos", "Le Stop est facultatif la nuit"], "reponse": "Le Stop impose l'arrêt complet obligatoire, le Cédez le passage permet de passer si c'est libre"},
        {"type": "choix", "question": "Le panneau triangulaire pointant vers le haut avec une croix noire à l'intérieur annonce :", "choix": ["Une priorité à droite obligatoire au prochain croisement", "Une intersection prioritaire", "Une fin de route prioritaire"], "reponse": "Une priorité à droite obligatoire au prochain croisement"},
        {"type": "choix", "question": "Dans quel ordre doivent passer les véhicules à une intersection sans aucune signalisation ?", "choix": ["Chaque conducteur doit laisser passer le véhicule qui se présente sur sa droite", "Le véhicule qui va tout droit passe toujours en premier", "Le plus gros véhicule est prioritaire"], "reponse": "Chaque conducteur doit laisser passer le véhicule qui se présente sur sa droite"},
        {"type": "choix", "question": "Un signal lumineux rouge fixe impose l'arrêt :", "choix": ["Avant le feu ou au niveau de la ligne d'effet", "Uniquement si des piétons traversent", "Au milieu du carrefour"], "reponse": "Avant le feu ou au niveau de la ligne d'effet"},
        {"type": "choix", "question": "Quel comportement adopter lorsque vous croisez un véhicule d'urgence (police, pompiers) avec gyrophares et sirènes activés ?", "choix": ["Ralentir, serrer à droite ou s'arrêter si nécessaire pour lui dégager le passage", "Klaxonner pour prévenir les piétons", "Maintenir son allure sans changer de trajectoire"], "reponse": "Ralentir, serrer à droite ou s'arrêter si nécessaire pour lui dégager le passage"},
        {"type": "choix", "question": "Lorsque le feu est vert mais que le carrefour est encombré, je doit :", "choix": ["M'arrêter avant l'intersection pour ne pas bloquer le carrefour", "M'engager quand même car le feu me donne la priorité", "Klaxonner pour faire avancer les autres"], "reponse": "M'arrêter avant l'intersection pour ne pas bloquer le carrefour"},
        {"type": "choix", "question": "Quelle trajectoire faut-il adopter pour tourner à gauche dans une rue à double sens ?", "choix": ["Avancer vers le centre du carrefour sans couper le virage", "Serrer complètement le trottoir de gauche", "Couper le virage le plus court possible"], "reponse": "Avancer vers le centre du carrefour sans couper le virage"},
        {"type": "choix", "question": "Le clignotant gauche est obligatoire pour s'insérer sur un rond-point si l'on prend :", "choix": ["La sortie située à gauche ou pour faire demi-tour", "La première sortie à droite", "La sortie située directement en face"], "reponse": "La sortie située à gauche ou pour faire demi-tour"},
        {"type": "choix", "question": "Pourquoi faut-il serrer le plus à droite possible lors d'un virage à forte inclinaison sans visibilité ?", "choix": ["Pour éviter toute collision frontale avec un véhicule arrivant en sens inverse", "Pour rouler sur l'herbe en cas de besoin", "Pour mieux voir le paysage à droite"], "reponse": "Pour éviter toute collision frontale avec un véhicule arrivant en sens inverse"},
        {"type": "choix", "question": "À une intersection, l'agent de police qui me présente son profil signifie que :", "choix": ["Je peux passer avec prudence", "Je dois m'arrêter immédiatement", "Je dois couper mon moteur"], "reponse": "Je peux passer avec prudence"},
        {"type": "choix", "question": "Qu'indique une flèche jaune clignotante associée à un feu rouge fixe ?", "choix": ["Elle autorise à tourner dans sa direction en cédant la priorité aux piétons et autres voies", "Elle signale que le feu est en panne", "Elle m'oblige à faire demi-tour"], "reponse": "Elle autorise à tourner dans sa direction en cédant la priorité aux piétons et autres voies"},
        {"type": "choix", "question": "Une ligne transversale blanche continue peinte au sol indique l'emplacement d'un :", "choix": ["Panneau Stop", "Panneau Cédez le passage", "Passage piéton protégé"], "reponse": "Panneau Stop"},
        {"type": "choix", "question": "Quelle est la règle de priorité lors d'un croisement difficile sur une route de montagne en pente ?", "choix": ["Le véhicule qui descend doit s'arrêter le premier pour laisser passer celui qui monte", "Le véhicule qui monte doit reculer", "Le véhicule le plus rapide passe en premier"], "reponse": "Le véhicule qui descend doit s'arrêter le premier pour laisser passer celui qui monte"},
        {"type": "choix", "question": "Lors d'un changement de file, le conducteur prioritaire est :", "choix": ["Le véhicule qui circule déjà dans la file cible", "Le véhicule qui a allumé son clignotant en premier", "Le véhicule le plus rapide"], "reponse": "Le véhicule qui circule déjà dans la file cible"},
        {"type": "choix", "question": "Expliquez comment se placer sur les voies d'un rond-point à deux voies si vous allez tout droit :", "choix": ["Rester sur la voie de droite extérieure tout au long de l'anneau", "Se placer obligatoirement sur la voie de gauche intérieure", "Rouler au milieu à cheval sur les deux voies"], "reponse": "Rester sur la voie de droite extérieure tout au long de l'anneau"},
        {"type": "choix", "question": "Dans une intersection, le feu jaune fixe annonce le feu rouge et impose l'arrêt sauf si :", "choix": ["Le conducteur est trop près pour s'arrêter en toute sécurité", "Le conducteur est très pressé", "Il n'y a personne sur les côtés"], "reponse": "Le conducteur est trop près pour s'arrêter en toute sécurité"},
        {"type": "choix", "question": "Qu'est-ce qu'une priorité de passage ponctuelle annoncée par un panneau de danger ?", "choix": ["Le conducteur bénéficie de la priorité uniquement à la prochaine intersection", "La route est prioritaire jusqu'à la fin de la ville", "Il faut céder le passage aux bus uniquement"], "reponse": "Le conducteur bénéficie de la priorité uniquement à la prochaine intersection"},
        {"type": "choix", "question": "Un panneau carré bleu avec un pictogramme blanc d'une flèche pointant vers le haut indique :", "choix": ["Une route à sens unique", "Une obligation de tourner tout droit", "Une entrée d'autoroute"], "reponse": "Une route à sens unique"},
        {"type": "choix", "question": "Pourquoi est-il interdit de dépasser un véhicule à une intersection régie par une priorité à droite ?", "choix": ["Un véhicule arrivant sur la droite pourrait s'engager et être masqué par le dépassement", "La vitesse y est limitée à 20 km/h de nuit", "Le klaxon y est obligatoire"], "reponse": "Un véhicule arrivant sur la droite pourrait s'engager et être masqué par le dépassement"},
        {"type": "choix", "question": "Dans un carrefour à sens giratoire, les clignotants sont obligatoires pour :", "choix": ["Signaler tout changement de voie ou de sortie", "S'engager uniquement", "Faire des appels de phares"], "reponse": "Signaler tout changement de voie ou de sortie"},
        {"type": "choix", "question": "Expliquez le principe du croisement à l'indonésienne :", "choix": ["Les véhicules tournant à gauche se croisent l'un devant l'autre sans contourner le centre", "Les véhicules se croisent par l'arrière", "Le véhicule le plus lourd passe toujours en premier"], "reponse": "Les véhicules tournant à gauche se croisent l'un devant l'autre sans contourner le centre"},
        {"type": "choix", "question": "Un panneau de forme ronde avec une bordure rouge indique :", "choix": ["Une interdiction", "Une obligation", "Une direction conseillée"], "reponse": "Une interdiction"},
        {"type": "choix", "question": "Quelle est la signification d'un panneau triangulaire à fond jaune ?", "choix": ["Un danger temporaire lié à des travaux ou un aménagement provisoire", "Une zone touristique protégée", "Une priorité à droite absolue"], "reponse": "Un danger temporaire lié à des travaux ou un aménagement provisoire"},
        {"type": "choix", "question": "Un panneau rond à fond bleu avec un liseré blanc indique :", "choix": ["Une obligation", "Une interdiction", "Une simple indication de confort"], "reponse": "Une obligation"},
        {"type": "choix", "question": "Quelle est la signification d'une ligne de dissuasion discontinue aux traits rapprochés ?", "choix": ["Elle interdit le dépassement, sauf pour les véhicules très lents (vélos, tracteurs)", "Elle annonce un rétrécissement de la chaussée par la gauche", "Elle autorise le stationnement sur le bas-côté de la route"], "reponse": "Elle interdit le dépassement, sauf pour les véhicules très lents (vélos, tracteurs)"},
        {"type": "choix", "question": "Le panneau carré bleu comportant la lettre 'P' blanche indique :", "choix": ["Un parking ou une zone de stationnement autorisée", "Une interdiction de s'arrêter sur la chaussée", "L'emplacement d'un poste de secours"], "reponse": "Un parking ou une zone de stationnement autorisée"},
        {"type": "choix", "question": "Un panneau de forme rectangulaire ou carrée à fond bleu sert à donner :", "choix": ["Une indication ou une information utile pour la conduite", "Une interdiction stricte de circuler", "Une obligation de changer de direction"], "reponse": "Une indication ou une information utile pour la conduite"},
        {"type": "choix", "question": "Un panneau de forme triangulaire avec une bordure rouge annonce :", "choix": ["Un danger", "Une fin d'obligation", "Une zone de stationnement payant"], "reponse": "Un danger"},
        {"type": "choix", "question": "Quelle est la fonction d'une ligne d'avertissement composée de flèches de rabattement ?", "choix": ["Elle annonce l'approche d'une ligne continue et interdit de commencer un dépassement", "Elle indique une direction obligatoire au prochain carrefour", "Elle délimite les places réservées aux transports en commun"], "reponse": "Elle annonce l'approche d'une ligne continue et interdit de commencer un dépassement"},
        {"type": "choix", "question": "Le panneau rond blanc barré d'une seule bande noire diagonale indique :", "choix": ["La fin de toutes les interdictions précédemment notifiées aux conducteurs", "Une interdiction d'accès à tous les véhicules à moteur", "L'approche d'une zone de péage autoroutier"], "reponse": "La fin de toutes les interdictions précédemment notifiées aux conducteurs"},
        {"type": "choix", "question": "Qu'indique un panonceau rectangulaire placé juste en dessous d'un panneau principal ?", "choix": ["Il apporte des précisions sur la portée, la distance ou la catégorie d'usagers visée", "Il signale que le panneau principal est temporaire", "Il indique que la règle ne s'applique que le week-end"], "reponse": "Il apporte des précisions sur la portée, la distance ou la catégorie d'usagers visée"},
        {"type": "choix", "question": "Une ligne jaune peinte de manière discontinue sur la bordure du trottoir interdit :", "choix": ["Le stationnement mais permet l'arrêt", "L'arrêt et le stationnement de jour comme de nuit", "La circulation des deux-roues motorisés"], "reponse": "Le stationnement mais permet l'arrêt"},
        {"type": "choix", "question": "Un panneau de forme hexagonale rouge impose aux conducteurs :", "choix": ["L'arrêt complet obligatoire et l'obligation de céder le passage", "Une limitation de vitesse stricte à 50 km/h", "Une interdiction de faire demi-tour"], "reponse": "L'arrêt complet obligatoire et l'obligation de céder le passage"},
        {"type": "choix", "question": "Un panneau carré à fond blanc bordé de rouge avec un pictogramme noir indique :", "choix": ["L'entrée d'une zone résidentielle à vitesse limitée", "Une obligation de tourner au prochain carrefour", "Une fin de route prioritaire"], "reponse": "L'entrée d'une zone résidentielle à vitesse limitée"},
        {"type": "choix", "question": "Comment est signalée l'entrée d'une route à accès réglementé (voie rapide) ?", "choix": ["Par un panneau bleu comportant le pictogramme d'une voiture blanche", "Par un panneau bleu représentant une double chaussée séparée", "Par un panneau rond bordé de rouge"], "reponse": "Par un panneau bleu comportant le pictogramme d'une voiture blanche"},
        {"type": "choix", "question": "Les balises blanches à chapeau rouge situées sur le bord de la route servent à :", "choix": ["Délimiter le tracé des virages", "Indiquer une zone de verglas fréquent", "Annoncer une barrière de péage"], "reponse": "Délimiter le tracé des virages"},
        {"type": "choix", "question": "Qu'indique la présence d'une ligne peinte en bleu délimitant des places de stationnement ?", "choix": ["Une zone de stationnement gratuite mais limitée dans le temps (disque obligatoire)", "Une zone de stationnement réservée aux livraisons", "Une zone de stationnement payante par horodateur"], "reponse": "Une zone de stationnement gratuite mais limitée dans le temps (disque obligatoire)"},
        {"type": "choix", "question": "Le panneau triangulaire représentant deux flèches de sens opposés indique :", "choix": ["Une circulation à double sens immédiate", "Une route à sens unique", "Un rétrécissement de la chaussée par la droite"], "reponse": "Une circulation à double sens immédiate"},
        {"type": "choix", "question": "En dehors des agglomérations, un panneau de danger est implanté environ :", "choix": ["150 mètres avant le danger", "50 mètres avant le danger", "300 mètres avant le danger"], "reponse": "150 mètres avant le danger"},
        {"type": "choix", "question": "Un panneau d'obligation de couleur bleue barré d'un liseré rouge indique :", "choix": ["La fin d'une obligation spécifique", "Une interdiction immédiate de circuler", "L'entrée d'une zone de contrôle radar"], "reponse": "La fin d'une obligation spécifique"},
        {"type": "choix", "question": "En agglomération, à quelle distance avant le danger un panneau de danger est-il implanté ?", "choix": ["Environ 50 mètres", "Environ 150 mètres", "Immédiatement au niveau du danger"], "reponse": "Environ 50 mètres"},
        {"type": "choix", "question": "Une flèche de rabattement peinte au sol tournée vers la droite m'avertit :", "choix": ["Que ma voie va être supprimée et que je dois me rabattre", "Que je dois obligatoirement tourner au prochain carrefour", "Que la route devient prioritaire"], "reponse": "Que ma voie va être supprimée et que je dois me rabattre"},
        {"type": "choix", "question": "Qu'indique une balise de signalisation blanche avec un anneau rouge située à une intersection ?", "choix": ["Elle sert à renforcer la visibilité d'un carrefour dangereux", "Elle indique une zone de stationnement interdite", "Elle annonce la fin d'une autoroute"], "reponse": "Elle sert à renforcer la visibilité d'un carrefour dangereux"},
        {"type": "choix", "question": "Le panneau rectangulaire blanc écrit 'RAPPEL' sous une limitation de vitesse sert à :", "choix": ["Confirmer que la limitation précédente reste en vigueur", "Annoncer une nouvelle zone de contrôle radar", "Indiquer la fin de la zone de danger"], "reponse": "Confirmer que la limitation précédente reste en vigueur"},
        {"type": "choix", "question": "Qu'indique la présence d'un damier rouge et blanc au bout d'une descente dangereuse ?", "choix": ["Une voie de détresse pour les véhicules dont les freins ont rompu", "Une zone de contrôle technique obligatoire", "L'entrée d'un garage privé"], "reponse": "Une voie de détresse pour les véhicules dont les freins ont rompu"},
        {"type": "choix", "question": "Les lignes blanches transversales formées de petits carrés discontinus annoncent :", "choix": ["Une ligne de Cédez le passage", "Une ligne d'arrêt pour un panneau Stop", "Une zone de travaux temporaires"], "reponse": "Une ligne de Cédez le passage"},
        {"type": "choix", "question": "Quelle est la signification d'une ligne continue peinte en jaune sur le bord du trottoir ?", "choix": ["Elle indique l'interdiction totale de s'arrêter et de stationner le long du trottoir", "Elle autorise le stationnement des livraisons uniquement", "Elle délimite un arrêt d'autobus"], "reponse": "Elle indique l'interdiction totale de s'arrêter et de stationner le long du trottoir"},
        {"type": "choix", "question": "Un panneau rond bleu affichant le nombre '30' impose :", "choix": ["Une vitesse minimale obligatoire de 30 km/h", "Une limitation de vitesse maximale à ne pas dépasser", "Une simple vitesse recommandée pour le confort"], "reponse": "Une vitesse minimale obligatoire de 30 km/h"},
        {"type": "choix", "question": "Qu'indique un panneau rectangulaire de couleur marron ?", "choix": ["Un panneau culturel ou touristique signalant un monument ou site naturel", "Une zone de travaux forestiers dangereux", "Une interdiction d'accès aux véhicules polluants"], "reponse": "Un panneau culturel ou touristique signalant un monument ou site naturel"},
        {"type": "choix", "question": "Le marquage au sol composé d'une zone zébrée blanche (îlot de canalisation) :", "choix": ["Est strictement interdit à la circulation, à l'arrêt et au stationnement", "Peut être franchi pour effectuer un dépassement en cas de bouchon", "Sert de zone d'arrêt d'urgence pour les deux-roues"], "reponse": "Est strictement interdit à la circulation, à l'arrêt et au stationnement"},
        {"type": "choix", "question": "Qu'est-ce qu'une zone de rencontre signalée par un panneau carré bleu représentant des piétons et une voiture ?", "choix": ["Une zone urbaine où les piétons sont prioritaires partout et la vitesse limitée à 20 km/h", "Un espace réservé uniquement au covoiturage", "Une portion de route où le dépassement est obligatoire"], "reponse": "Une zone urbaine où les piétons sont prioritaires partout et la vitesse limitée à 20 km/h"},
        {"type": "choix", "question": "Le panneau triangulaire représentant un train noir sans barrière annonce :", "choix": ["Un passage à niveau sans barrière ni garde", "L'approche d'une gare ferroviaire", "Une traversée de tramway urbain"], "reponse": "Un passage à niveau sans barrière ni garde"},
        {"type": "choix", "question": "Quelle est la signification d'un feu de signalisation rouge clignotant ?", "choix": ["Il impose l'arrêt immédiat et absolu (passage à niveau, pont mobile, pompiers)", "Il indique que le feu va passer au vert dans 3 secondes", "Il signale une panne de l'ensemble du carrefour"], "reponse": "Il impose l'arrêt immédiat et absolu (passage à niveau, pont mobile, pompiers)"},
        {"type": "choix", "question": "Un panneau carré bleu avec un pictogramme blanc de vélo indique :", "choix": ["Une piste ou bande conseillée et réservée aux cyclistes", "Une obligation d'allumer ses feux de position", "Une interdiction d'accès aux deux-roues motorisés"], "reponse": "Une piste ou bande conseillée et réservée aux cyclistes"},
        {"type": "choix", "question": "Qu'indique un panneau de direction de forme rectangulaire avec un fond vert ?", "choix": ["Une direction menant vers des villes importantes par le réseau principal hors autoroute", "Une route forestière à accès réglementé", "Une zone écologique de circulation restreinte"], "reponse": "Une direction menant vers des villes importantes par le réseau principal hors autoroute"},
        {"type": "choix", "question": "Un panneau circulaire blanc avec une bordure rouge représentant un camion noir interdit l'accès aux :", "choix": ["Véhicules de transport de marchandises de plus de 3,5 tonnes", "Camping-cars et caravanes uniquement", "Véhicules de secours en intervention"], "reponse": "Véhicules de transport de marchandises de plus de 3,5 tonnes"},
        {"type": "choix", "question": "Quelle est la signalisation au sol qui délimite la bande d'arrêt d'urgence sur autoroute ?", "choix": ["Une ligne discontinue composée de longs traits blancs de 39 mètres espacés de 13 mètres", "Une ligne continue blanche ininterrompue", "Une ligne jaune de dissuasion"], "reponse": "Une ligne discontinue composée de longs traits blancs de 39 mètres espacés de 13 mètres"},
        {"type": "choix", "question": "Une balise blanche cylindrique barrée de deux bandes rouges diagonales annonce un passage à niveau à :", "choix": ["100 mètres", "150 mètres", "50 mètres"], "reponse": "100 mètres"},
        {"type": "choix", "question": "Que signifie la présence de bandes rugueuses transversales peintes au sol à l'approche d'un carrefour ?", "choix": ["Elles créent des vibrations pour alerter le conducteur et l'inciter à ralentir", "Elles indiquent une zone de chaînage obligatoire en hiver", "Elles délimitent un espace de stationnement réservé"], "reponse": "Elles créent des vibrations pour alerter le conducteur et l'inciter à ralentir"},
        {"type": "choix", "question": "Le panneau triangulaire avec une flèche épaisse verticale coupée par une fine ligne transversale indique :", "choix": ["Que je suis prioritaire uniquement à la prochaine intersection", "Une intersection avec priorité à droite générale", "L'approche d'une fin d'autoroute"], "reponse": "Que je suis prioritaire uniquement à la prochaine intersection"},
        {"type": "choix", "question": "Quelle est la fonction d'un miroir parabolique installé à une intersection urbaine ?", "choix": ["Permettre de vérifier l'arrivée de véhicules lorsque la visibilité latérale est masquée", "Permettre aux forces de l'ordre de contrôler la vitesse", "Alerter les piétons de l'approche d'une voiture"], "reponse": "Permettre de vérifier l'arrivée de véhicules lorsque la visibilité latérale est masquée"},
        {"type": "choix", "question": "Un panneau de forme ronde barré de rouge représentant une cigarette interdite s'applique :", "choix": ["Aux stations-services et zones de stockage de carburant", "À l'ensemble de l'habitacle des voitures particulières", "Uniquement lors de la conduite de nuit"], "reponse": "Aux stations-services et zones de stockage de carburant"},
        {"type": "choix", "question": "Qu'indique une balise de sommet ou de contournement de couleur blanche et bleue avec des flèches ?", "choix": ["Le côté par lequel le conducteur doit obligatoirement contourner un obstacle", "Une zone de verglas fréquent sur 500 mètres", "L'approche d'un poste de péage"], "reponse": "Le côté par lequel le conducteur doit obligatoirement contourner un obstacle"},
        {"type": "choix", "question": "Le marquage au sol composé de grandes lignes de couleur zigzag jaunes délimite :", "choix": ["Un arrêt de bus interdit à la circulation et au stationnement", "Une zone de livraison accessible uniquement le matin", "Un emplacement de recharge pour véhicules électriques"], "reponse": "Un arrêt de bus interdit à la circulation et au stationnement"},
        {"type": "choix", "question": "Quelle est la signification d'un panneau carré à fond noir avec des flèches blanches pointant vers la gauche ?", "choix": ["Un jalonnement ou balise renforçant le tracé d'un virage serré et dangereux", "Une indication de direction vers une sortie d'autoroute", "Une interdiction de tourner à droite au prochain carrefour"], "reponse": "Un jalonnement ou balise renforçant le tracé d'un virage serré et dangereux"},
        {"type": "choix", "question": "Une ligne mixte composée d'une ligne continue accolée à une ligne discontinue autorise le dépassement si :", "choix": ["La ligne discontinue est située du côté de ma voie de circulation", "La ligne continue est située de mon côté", "La visibilité vers l'avant est supérieure à 2 kilomètres"], "reponse": "La ligne discontinue est située du côté de ma voie de circulation"},
        {"type": "choix", "question": "Qu'indique un panneau d'agglomération (nom de la commune encadré de rouge) sur les règles de conduite ?", "choix": ["Il déclenche automatiquement la limitation à 50 km/h et l'interdiction de klaxonner", "Il indique une zone de péage urbain obligatoire", "Il met fin à toutes les règles de priorité de droite"], "reponse": "Il déclenche automatiquement la limitation à 50 km/h et l'interdiction de klaxonner"},
        {"type": "choix", "question": "Le panneau rond bleu affichant un pictogramme de cavalier sur son cheval indique :", "choix": ["Un chemin obligatoire pour les cavaliers", "Une zone de danger avec risque de traversée d'animaux domestiques", "L'accès réservé aux centres hippiques proches"], "reponse": "Un chemin obligatoire pour les cavaliers"},
        {"type": "choix", "question": "Qu'indique un panneau de fin d'agglomération (nom barré d'une ligne rouge diagonale) ?", "choix": ["La fin des règles urbaines, la vitesse repassant généralement à 80 ou 90 km/h", "L'obligation d'allumer ses feux de croisement immédiatement", "L'entrée sur une section d'autoroute gratuite"], "reponse": "La fin des règles urbaines, la vitesse repassant généralement à 80 ou 90 km/h"},
        {"type": "choix", "question": "Un feu de signalisation en forme de croix rouge fixe au-dessus d'une voie autoroutière signifie :", "choix": ["La voie est strictement fermée à la circulation", "La voie est réservée aux véhicules de secours uniquement", "La vitesse y est limitée à 30 km/h pour travaux"], "reponse": "La voie est strictement fermée à la circulation"},
        {"type": "choix", "question": "Quelle est la signification d'un marquage au sol composé de flèches directionnelles fléchées dans une voie ?", "choix": ["Des flèches d'assignation obligeant à suivre la direction indiquée une fois engagé", "Une simple recommandation d'itinéraire pour éviter les bouchons", "Une zone de dépassement réservée aux véhicules lents"], "reponse": "Des flèches d'assignation obligeant à suivre la direction indiquée une fois engagé"},
        {"type": "choix", "question": "À quelle distance minimale devez-vous placer le triangle de présignalisation en cas de panne sur route ?", "choix": ["30 mètres", "15 mètres", "50 mètres"], "reponse": "30 mètres"},
        {"type": "choix", "question": "Quelles vérifications intérieures devez-vous réaliser dès votre installation au poste de conduite ?", "choix": ["Réglage du siège, du volant, des trois rétroviseurs et attache de la ceinture", "Vérification du niveau d'huile et de liquide de frein", "Nettoyage des vitres et du tableau de bord"], "reponse": "Réglage du siège, du volant, des trois rétroviseurs et attache de la ceinture"},
        {"type": "choix", "question": "Quelle est la distance de sécurité minimale à laisser en dépassant un cycliste hors agglomération ?", "choix": ["1,50 mètre", "1 mètre", "2 mètres"], "reponse": "1,50 mètre"},
        {"type": "choix", "question": "Qu'indique l'indice de charge inscrit sur le flanc d'un pneumatique ?", "choix": ["Le poids maximal que le pneumatique peut supporter", "La pression maximale recommandée", "La vitesse maximale autorisée"], "reponse": "Le poids maximal que le pneumatique peut supporter"},
        {"type": "choix", "question": "Avant d'entamer un dépassement sur route à double sens, la visibilité vers l'avant doit être d'au moins :", "choix": ["500 mètres", "200 mètres", "1 kilomètre"], "reponse": "500 mètres"},
        {"type": "choix", "question": "Pourquoi est-il strictement interdit de dépasser un véhicule qui est déjà en train d'en dépasser un autre sur une route à double sens ?", "choix": ["Le troisième véhicule circulerait complètement sur la voie opposée, créant un risque majeur de collision frontale", "Cela augmente inutilement la consommation de carburant", "Le système ABS risquerait de se désactiver"], "reponse": "Le troisième véhicule circulerait complètement sur la voie opposée, créant un risque majeur de collision frontale"},
        {"type": "choix", "question": "Sur autoroute, le dépassement par la droite est autorisé :", "choix": ["Uniquement dans les embouteillages en files ininterrompues", "Si le véhicule de gauche roule trop lentement", "Si j'allume mes feux de détresse"], "reponse": "Uniquement dans les embouteillages en files ininterrompues"},
        {"type": "choix", "question": "Qu'indique la présence d'une ligne de flèches de rabattement courbées vers la droite juste après une ligne discontinue ?", "choix": ["Elle avertit que la ligne va devenir continue et qu'il faut se rabattre immédiatement", "Elle indique une direction obligatoire au prochain carrefour", "Elle délimite les places réservées aux transports en commun"], "reponse": "Elle avertit que la ligne va devenir continue et qu'il faut se rabattre immédiatement"},
        {"type": "choix", "question": "Pendant le dépassement d'un camion, le principal danger lié au vent est :", "choix": ["L'effet d'aspiration puis l'écart provoqué par la rafale en sortant de sa zone", "Une augmentation de la consommation de carburant", "Une perte d'efficacité des freins"], "reponse": "L'effet d'aspiration puis l'écart provoqué par la rafale en sortant de sa zone"},
        {"type": "choix", "question": "Qu'est-ce que l'angle mort et comment le vérifier avant de déboîter ?", "choix": ["Zone invisible dans les rétroviseurs; il faut tourner brièvement la tête pour vérifier directement", "L'espace situé directement sous les roues du véhicule", "La zone de vision masquée par le soleil rasant"], "reponse": "Zone invisible dans les rétroviseurs; il faut tourner brièvement la tête pour vérifier directement"},
        {"type": "choix", "question": "Lorsqu'un véhicule s'apprête à vous dépasser, vous devez :", "choix": ["Maintenir votre vitesse et serrer à droite", "Ralentir pour l'aider", "Accélérer légèrement"], "reponse": "Maintenir votre vitesse et serrer à droite"},
        {"type": "choix", "question": "Quelles conditions doivent être réunies pour avoir le droit de dépasser par la droite ?", "choix": ["Le véhicule devant a signalé son intention de tourner à gauche et a laissé l'espace nécessaire", "Le véhicule devant circule sur l'autoroute à moins de 80 km/h", "La visibilité est parfaite et la chaussée comporte trois voies"], "reponse": "Le véhicule devant a signalé son intention de tourner à gauche et a laissé l'espace nécessaire"},
        {"type": "choix", "question": "Le dépassement d'un cycliste est autorisé sur une ligne continue si :", "choix": ["La visibilité est bonne et que l'on chevauche la ligne sans la franchir complètement", "Le cycliste roule à moins de 10 km/h", "C'est interdit dans tous les cas"], "reponse": "La visibilité est bonne et que l'on chevauche la ligne sans la franchir complètement"},
        {"type": "choix", "question": "Quelle est la sanction encourue en cas de franchissement d'une ligne blanche continue ?", "choix": ["Une amende forfaitaire, un retrait de 3 points et un risque de suspension de permis", "Un simple avertissement écrit de première classe", "Une amende mais aucun retrait de points"], "reponse": "Une amende forfaitaire, un retrait de 3 points et un risque de suspension de permis"},
        {"type": "choix", "question": "Sur une chaussée à trois voies à sens unique, pour rouler normalement, je me place :", "choix": ["Sur la voie de droite", "Sur la voie du milieu", "Sur n'importe quelle voie libre"], "reponse": "Sur la voie de droite"},
        {"type": "choix", "question": "Pourquoi faut-il être particulièrement vigilant lors du dépassement d'un véhicule articulé par temps de pluie ?", "choix": ["Le camion génère d'importantes projections d'eau sale qui masquent la visibilité", "La force centrifuge est doublée autour du camion", "Le vent latéral empêche de maintenir une trajectoire rectiligne"], "reponse": "Le camion génère d'importantes projections d'eau sale qui masquent la visibilité"},
        {"type": "choix", "question": "Dans une côte raide, si le croisement est difficile entre deux véhicules de même gabarit, la priorité est au véhicule :", "choix": ["Qui monte", "Qui descend", "Le plus rapide"], "reponse": "Qui monte"},
        {"type": "choix", "question": "Expliquez la procédure complète des contrôles visuels à effectuer avant d'effectuer un dépassement.", "choix": ["Regarder devant, vérifier le rétroviseur intérieur, extérieur gauche et contrôler l'angle mort gauche", "Regarder le tableau de bord et vérifier la pression des pneus", "Klaxonner pour avertir les usagers devant"], "reponse": "Regarder devant, vérifier le rétroviseur intérieur, extérieur gauche et contrôler l'angle mort gauche"},
        {"type": "choix", "question": "Il est interdit de dépasser à l'approche d'un passage piéton :", "choix": ["Sauf si aucun piéton n'est visible ou engagé", "Uniquement de nuit", "Sauf s'il s'agit d'un deux-roues lent"], "reponse": "Sauf si aucun piéton n'est visible ou engagé"},
        {"type": "choix", "question": "Quel est le risque de se rabattre trop tôt devant un poids lourd après l'avoir dépassé ?", "choix": ["Couper sa distance de sécurité; le camion n'aura pas l'espace nécessaire pour freiner en urgence", "Provoquer une usure prématurée de ses propres pneus", "Désactiver le limiteur de vitesse du camion"], "reponse": "Couper sa distance de sécurité; le camion n'aura pas l'espace nécessaire pour freiner en urgence"},
        {"type": "choix", "question": "Sur une autoroute à 3 voies, les véhicules de transport de marchandises de plus de 3,5 tonnes :", "choix": ["Ne peuvent pas utiliser la voie située la plus à gauche", "Doivent circuler uniquement sur la voie du milieu", "Peuvent utiliser toutes les voies librement"], "reponse": "Ne peuvent pas utiliser la voie située la plus à gauche"},
        {"type": "choix", "question": "Qu'indique une ligne de rive discontinue sur le bord droit de la chaussée ?", "choix": ["Elle délimite la frontière entre les voies normales et l'accotement ou la bande d'arrêt d'urgence", "Elle annonce une intersection prioritaire", "Elle indique une zone de stationnement autorisée de nuit"], "reponse": "Elle délimite la frontière entre les voies normales et l'accotement ou la bande d'arrêt d'urgence"},
        {"type": "choix", "question": "Lors d'un croisement de nuit sur route non éclairée, je dois passer mes feux :", "choix": ["De route en feux de croisement", "De croisement en feux de position", "De route en feux de détresse"], "reponse": "De route en feux de croisement"},
        {"type": "choix", "question": "Pourquoi la distance de dépassement augmente-t-elle considérablement sur une voie rapide ?", "choix": ["La différence de vitesse entre le véhicule qui dépasse et celui dépassé est souvent faible", "Le relief de la route allonge le temps de réaction", "Le vent de face freine le véhicule qui déboîte"], "reponse": "La différence de vitesse entre le véhicule qui dépasse et celui dépassé est souvent faible"},
        {"type": "choix", "question": "Le franchissement d'une ligne continue pour dépasser un tracteur agricole est :", "choix": ["Strictement interdit", "Autorisé si le tracteur roule à moins de 30 km/h", "Autorisé en effectuant des appels de phares"], "reponse": "Strictement interdit"},
        {"type": "choix", "question": "Quel comportement adopter si un véhicule arrivant en face effectue un dépassement dangereux et se trouve sur votre voie ?", "choix": ["Ralentir fortement, serrer le plus possible à droite et faire des appels de phares", "Accélérer pour passer avant lui", "Maintenir son allure au centre de la route"], "reponse": "Ralentir fortement, serrer le plus possible à droite et faire des appels de phares"},
        {"type": "choix", "question": "Lors d'un croisement sur une chaussée rétrécie, si un obstacle est présent sur ma voie :", "choix": ["Je dois m'arrêter et céder le passage au véhicule en face", "Je passe en premier car je suis le plus rapide", "J'allume mes feux de route pour forcer le passage"], "reponse": "Je dois m'arrêter et céder le passage au véhicule en face"},
        {"type": "choix", "question": "Pourquoi est-il interdit de dépasser dans un virage sur une route à double sens sans marquage au sol ?", "choix": ["Le manque de visibilité empêche de s'assurer qu'aucun véhicule n'arrive en sens inverse", "La force centrifuge annule la puissance du moteur", "Les pneus perdent toute leur pression dans les courbes"], "reponse": "Le manque de visibilité empêche de s'assurer qu'aucun véhicule n'arrive en sens inverse"},
        {"type": "choix", "question": "Lorsque la ligne axiale est composée de traits de 3 mètres espacés de 1,33 mètre, il s'agit d'une ligne :", "choix": ["D'annonce ou de dissuasion", "De guidage", "De stop"], "reponse": "D'annonce ou de dissuasion"},
        {"type": "choix", "question": "Qu'est-ce qu'un dépassement dit 'en accordéon' dans les embouteillages ?", "choix": ["Un changement de file incessant qui ralentit en réalité l'ensemble du trafic", "Un dépassement effectué en utilisant les avertisseurs sonores", "Une manœuvre de sécurité obligatoire sur autoroute"], "reponse": "Un changement de file incessant qui ralentit en réalité l'ensemble du trafic"},
        {"type": "choix", "question": "Le dépassement par la gauche d'un tramway circulant au milieu d'une rue à double sens est :", "choix": ["Strictement interdit sauf s'il s'agit d'une rue à sens unique", "Autorisé en klaxonnant", "Conseillé pour dégager la voie rapidement"], "reponse": "Strictement interdit sauf s'il s'agit d'une rue à sens unique"},
        {"type": "choix", "question": "Quelle distance de sécurité minimale doit-on conserver avec le véhicule de devant à l'arrêt dans un embouteillage ?", "choix": ["On doit pouvoir apercevoir ses roues arrière touchant le sol", "Une distance minimale de 50 mètres", "Aucune, on peut se coller au pare-chocs"], "reponse": "On doit pouvoir apercevoir ses roues arrière touchant le sol"},
        {"type": "choix", "question": "Un dépassement est considéré comme terminé dès lors que l'on aperçoit le véhicule dépassé dans :", "choix": ["Le rétroviseur intérieur", "Le rétroviseur extérieur gauche", "La vitre latérale droite"], "reponse": "Le rétroviseur intérieur"},
        {"type": "choix", "question": "Quelle est la règle de priorité si deux véhicules de gabarits différents (une voiture et un bus) se croisent en forte pente ?", "choix": ["Le véhicule le plus léger (la voiture) doit faire marche arrière", "Le véhicule le plus lourd (le bus) doit reculer", "Le véhicule qui descend passe toujours en premier"], "reponse": "Le véhicule le plus léger (la voiture) doit faire marche arrière"},
        {"type": "choix", "question": "La ligne discontinue normale de guidage comporte des traits de 3 mètres espacés de :", "choix": ["10 mètres", "5 mètres", "1,33 mètre"], "reponse": "10 mètres"},
        {"type": "choix", "question": "Pourquoi le dépassement est-il interdit aux sommets de côtes sur les routes à double sens ?", "choix": ["Le relief masque totalement la visibilité sur les véhicules pouvant arriver en face", "La force motrice est insuffisante en montée", "Le code de la route l'interdit uniquement de nuit"], "reponse": "Le relief masque totalement la visibilité sur les véhicules pouvant arriver en face"},
        {"type": "choix", "question": "Lors d'un croisement difficile en agglomération entre une voiture et un véhicule de travaux publics, la priorité est à :", "choix": ["La voiture particulière", "Au véhicule de travaux publics", "Au véhicule le plus imposant"], "reponse": "La voiture particulière"},
        {"type": "choix", "question": "Quelle est l'utilité d'une bande de sélection de trajectoire peinte à l'entrée d'une intersection ?", "choix": ["Guider visuellement les conducteurs pour éviter qu'ils ne se heurtent en tournant", "Indiquer une zone de stationnement payante", "Permettre le dépassement par la droite"], "reponse": "Guider visuellement les conducteurs pour éviter qu'ils ne se heurtent en tournant"},
        {"type": "choix", "question": "Sur une chaussée à sens unique, le dépassement de plusieurs véhicules à la suite est :", "choix": ["Autorisé si la voie de gauche reste libre", "Strictement interdit", "Autorisé uniquement pour les véhicules de secours"], "reponse": "Autorisé si la voie de gauche reste libre"},
        {"type": "choix", "question": "Qu'indique le panneau d'interdiction de dépasser représentant une voiture rouge à côté d'une voiture noire ?", "choix": ["Il interdit le dépassement de tous les véhicules à moteur à plus de deux roues", "Il interdit le dépassement des vélos et cyclomoteurs uniquement", "Il signale une fin de route prioritaire à 150 mètres"], "reponse": "Il interdit le dépassement de tous les véhicules à moteur à plus de deux roues"},
        {"type": "choix", "question": "Si un conducteur accélère alors que vous êtes en train de le dépasser, il commet une infraction passible :", "choix": ["D'une amende forfaitaire et d'un retrait de 2 points", "D'un simple avertissement verbal", "D'une annulation immédiate de son assurance"], "reponse": "D'une amende forfaitaire et d'un retrait de 2 points"},
        {"type": "choix", "question": "Pourquoi faut-il redoubler de prudence en dépassant un ensemble de véhicules (camion avec remorque) ?", "choix": ["La longueur totale à franchir est importante, ce qui allonge le temps sur la voie opposée", "Le camion risque d'accélérer soudainement en descente", "Le système ABS se désactive automatiquement"], "reponse": "La longueur totale à franchir est importante, ce qui allonge le temps sur la voie opposée"},
        {"type": "choix", "question": "La zone d'incertitude autour d'un piéton marchant au bord d'une route correspond à :", "choix": ["L'espace imaginaire dans lequel il pourrait se déplacer soudainement", "Sa zone d'audition maximale", "Sa vitesse moyenne de déplacement"], "reponse": "L'espace imaginaire dans lequel il pourrait se déplacer soudainement"},
        {"type": "choix", "question": "Le marquage de lignes blanches continues reliant un trottoir à un îlot central :", "choix": ["Est une zone de protection interdisant tout franchissement", "Sert de zone de stationnement pour les livraisons", "Peut être franchi en cas de trafic encombré"], "reponse": "Est une zone de protection interdisant tout franchissement"},
        {"type": "choix", "question": "Le dépassement d'un véhicule de déneigement (chasse-neige) en intervention sur la chaussée est :", "choix": ["Strictement interdit dans tous les cas", "Autorisé si sa vitesse est inférieure à 20 km/h", "Autorisé en faisant des appels de phares"], "reponse": "Strictement interdit dans tous les cas"},
        {"type": "choix", "question": "Pourquoi l'utilisation des feux de détresse est-elle obligatoire lorsque vous êtes le dernier véhicule d'une file d'attente sur autoroute ?", "choix": ["Pour alerter les conducteurs arrivant derrière du ralentissement brutal", "Pour indiquer que l'on va changer de file", "Pour économiser la batterie du véhicule"], "reponse": "Pour alerter les conducteurs arrivant derrière du ralentissement brutal"},
        {"type": "choix", "question": "Sur une route à double sens, si la ligne médiane comporte des flèches de rabattement pointant vers moi :", "choix": ["Le dépassement m'est totalement interdit dans mon sens de circulation", "Je peux commencer un dépassement si la voie est libre", "La route passe immédiatement à sens unique"], "reponse": "Le dépassement m'est totalement interdit dans mon sens de circulation"},
        {"type": "choix", "question": "Comment adapter son comportement lors du croisement d'un convoi exceptionnel ?", "choix": ["Ralentir fortement et se garer sur le côté si l'accompagnement l'ordonne", "Klaxonner pour lui indiquer notre présence", "Accélérer pour passer avant que la route ne soit bloquée"], "reponse": "Ralentir fortement et se garer sur le côté si l'accompagnement l'ordonne"},
        {"type": "choix", "question": "Le déplacement des piétons le long d'une chaussée sans trottoir doit se faire :", "choix": ["En marchant face aux voitures (côté gauche de la route)", "Du côté droit dans le sens de la circulation", "Sur la ligne médiane séparatrice"], "reponse": "En marchant face aux voitures (côté gauche de la route)"},
        {"type": "choix", "question": "Quelle est l'utilité des lignes de guidage blanches peintes au milieu des grands carrefours urbains ?", "choix": ["Permettre aux conducteurs de maintenir leur couloir de circulation en tournant", "Délimiter les futures zones de travaux", "Indiquer les emplacements réservés aux piétons"], "reponse": "Permettre aux conducteurs de maintenir leur couloir de circulation en tournant"},
        {"type": "choix", "question": "Dans quelle situation devez-vous obligatoirement allumer vos feux de brouillard arrière ?", "choix": ["Uniquement en cas de brouillard ou de chute de neige", "Sous une forte pluie battante", "Dès que la nuit tombe"], "reponse": "Uniquement en cas de brouillard ou de chute de neige"},
        {"type": "choix", "question": "Qu'indique le voyant de couleur bleu allumé sur le tableau de bord ?", "choix": ["L'activation des feux de route (pleins phares)", "L'activation des feux de croisement", "Une surchauffe du liquide de refroidissement"], "reponse": "L'activation des feux de route (pleins phares)"},
        {"type": "choix", "question": "Par temps de pluie intense, quels feux devez-vous allumer pour circuler en toute légalité ?", "choix": ["Les feux de croisement et éventuellement les feux de brouillard avant", "Les feux de position seuls", "Les feux de brouillard arrière"], "reponse": "Les feux de croisement et éventuellement les feux de brouillard avant"},
        {"type": "choix", "question": "Pourquoi est-il strictement interdit d'allumer ses feux de brouillard arrière sous une pluie intense ?", "choix": ["Leur forte intensité se répercute dans l'eau et éblouit violemment l'arrière", "Ils risquent de faire surchauffer les fusibles", "Ils coupent automatiquement l'aide au freinage ABS"], "reponse": "Leur forte intensité se répercute dans l'eau et éblouit violemment l'arrière"},
        {"type": "choix", "question": "Les feux de position seuls permettent d'être vu mais ne permettent pas de mieux voir. Ils s'utilisent :", "choix": ["Uniquement en agglomération bien éclairée", "Sur route nationale non éclairée", "Par temps de brouillard dense"], "reponse": "Uniquement en agglomération bien éclairée"},
        {"type": "choix", "question": "Qu'est-ce que l'éblouissement par ricochet dans le rétroviseur intérieur et comment l'éviter ?", "choix": ["Les phares arrière se reflètent; on l'évite en basculant le miroir en position nuit", "C'est l'effet du soleil rasant; on l'évite avec le pare-soleil", "C'est un reflet des vitres latérales; on doit les baisser légèrement"], "reponse": "Les phares arrière se reflètent; on l'évite en basculant le miroir en position nuit"},
        {"type": "choix", "question": "En circulant de nuit sur une route nationale non éclairée, sans aucun véhicule devant ni en face, j'utilise :", "choix": ["Les feux de route", "Les feux de croisement", "Les feux de position"], "reponse": "Les feux de route"},
        {"type": "choix", "question": "Quel est le comportement réflexe à adopter si le véhicule arrivant en face refuse de couper ses feux de route ?", "choix": ["Fixer le bord droit de la chaussée (la ligne de rive) pour ne pas être aveuglé", "Allumer ses propres pleins phares pour répliquer", "Fermer les yeux pendant deux secondes"], "reponse": "Fixer le bord droit de la chaussée (la ligne de rive) pour ne pas être aveuglé"},
        {"type": "choix", "question": "Les feux de brouillard avant peuvent compléter ou remplacer les feux de croisement en cas de :", "choix": ["Brouillard, forte chute de neige ou pluie intense", "Simple tombée de la nuit en ville", "Circulation dans un long tunnel bien éclairé"], "reponse": "Brouillard, forte chute de neige ou pluie intense"},
        {"type": "choix", "question": "Pourquoi le passage de l'ombre à la lumière à la sortie d'un long tunnel est-il dangereux ?", "choix": ["Il provoque un éblouissement pendant lequel l'œil met quelques secondes à s'adapter", "Il désactive les essuie-glaces automatiques", "Il modifie instantanément la pression des pneus"], "reponse": "Il provoque un éblouissement pendant lequel l'œil met quelques secondes à s'adapter"},
        {"type": "choix", "question": "Le voyant de feux de croisement sur le tableau de bord est de couleur :", "choix": ["Verte", "Bleue", "Orange"], "reponse": "Verte"},
        {"type": "choix", "question": "Quelles sont les vérifications à faire sur les balais d'essuie-glace avant l'arrivée de l'hiver ?", "choix": ["Contrôler l'état du caoutchouc (pas de craquelures) et s'assurer qu'ils ne laissent pas de traces", "Vérifier leur couleur d'origine", "Les démonter et les nettoyer au savon de Marseille"], "reponse": "Contrôler l'état du caoutchouc (pas de craquelures) et s'assurer qu'ils ne laissent pas de traces"},
        {"type": "choix", "question": "Le givre présent sur le pare-brise et les vitres latérales doit être :", "choix": ["Entièrement gratté et éliminé avant de prendre la route", "Éliminé uniquement devant les yeux du conducteur", "Laissé tel quel, il fondra tout seul avec la vitesse"], "reponse": "Entièrement gratté et éliminé avant de prendre la route"},
        {"type": "choix", "question": "Qu'est-ce que l'effet de 'miroir d'eau' provoqué par les premières minutes d'une averse après une période sèche ?", "choix": ["La pluie se mélange à la poussière et à l'huile, créant une pellicule grasse très glissante", "Le reflet du ciel sur la chaussée qui éblouit le conducteur", "Une évaporation rapide de l'eau qui crée du brouillard localisé"], "reponse": "La pluie se mélange à la poussière et à l'huile, créant une pellicule grasse très glissante"},
        {"type": "choix", "question": "De nuit, le clignotant doit être allumé :", "choix": ["Pour toute manœuvre de changement de direction ou de dépassement (comme de jour)", "Uniquement en cas de présence visible d'autres usagers", "Uniquement hors agglomération sur route non éclairée"], "reponse": "Pour toute manœuvre de changement de direction ou de dépassement (comme de jour)"},
        {"type": "choix", "question": "Quel est le danger lié à la conduite avec un soleil rasant (lever ou coucher du soleil) ?", "choix": ["Un éblouissement de face direct qui rend la signalisation et les piétons presque invisibles", "Une surchauffe immédiate du moteur", "Une perte d'efficacité totale du système de freinage ABS"], "reponse": "Un éblouissement de face direct qui rend la signalisation et les piétons presque invisibles"},
        {"type": "choix", "question": "Les feux diurnes (feux de jour à LED à l'avant) servent à :", "choix": ["Rendre le véhicule plus visible pour les autres usagers en plein jour", "Mieux éclairer les panneaux de signalisation de nuit", "Remplacer complètement les feux de position à la tombée de la nuit"], "reponse": "Rendre le véhicule plus visible pour les autres usagers en plein jour"},
        {"type": "choix", "question": "Pourquoi la conduite par temps de brouillard intense fatigue-t-elle beaucoup plus rapidement ?", "choix": ["Elle demande une concentration visuelle permanente pour tenter de deviner les obstacles", "Le taux d'humidité dans l'habitacle diminue l'oxygène", "Le système de ventilation fait beaucoup plus de bruit"], "reponse": "Elle demande une concentration visuelle permanente pour tenter de deviner les obstacles"},
        {"type": "choix", "question": "En cas de panne complète d'éclairage de nuit sur route nationale, je dois :", "choix": ["Me garer immédiatement sur le côté et actionner mes feux de détresse", "Continuer à rouler lentement jusqu'à la prochaine intersection éclairée", "Suivre de très près les feux arrière d'une autre voiture"], "reponse": "Me garer immédiatement sur le côté et actionner mes feux de détresse"},
        {"type": "choix", "question": "Comment dégivrer efficacement et rapidement l'intérieur de son pare-brise embué ?", "choix": ["Activer la fonction de désembuage thermique maximale combinée à la climatisation", "Ouvrir toutes les fenêtres au maximum en roulant", "Essuyer le verre avec sa main nue"], "reponse": "Activer la fonction de désembuage thermique maximale combinée à la climatisation"},
        {"type": "choix", "question": "Les feux de croisement éclairent la chaussée vers l'avant sur une distance minimale de :", "choix": ["30 mètres", "50 mètres", "15 mètres"], "reponse": "30 mètres"},
        {"type": "choix", "question": "Pourquoi les feux de croisement éclairent-ils de manière asymétrique (plus loin du côté droit) ?", "choix": ["Pour éclairer au maximum le bas-côté afin de détecter les piétons ou animaux", "Pour éviter d'éblouir les oiseaux dans les arbres", "Il s'agit d'un simple défaut de fabrication d'origine"], "reponse": "Pour éclairer au maximum le bas-côté afin de détecter les piétons ou animaux"},
        {"type": "choix", "question": "Les feux de route doivent éclairer efficacement la chaussée sur une distance minimale de :", "choix": ["100 mètres", "50 mètres", "200 mètres"], "reponse": "100 mètres"},
        {"type": "choix", "question": "Quel est le risque de rouler avec des optiques de phares encrassées par de la boue ou de la poussière ?", "choix": ["Une baisse importante de l'intensité lumineuse des phares", "Une surconsommation immédiate de la batterie", "Un dysfonctionnement du voyant bleu au tableau de bord"], "reponse": "Une baisse importante de l'intensité lumineuse des phares"},
        {"type": "choix", "question": "Le voyant des feux de position sur le combiné de bord est représenté par :", "choix": ["Une ampoule verte rayonnant vers les côtés", "Un projecteur bleu orienté vers l'avant", "Un triangle orange clignotant"], "reponse": "Une ampoule verte rayonnant vers les côtés"},
        {"type": "choix", "question": "Quelles précautions prendre en circulant sur route lors des premières chutes de neige sans pneus hiver ?", "choix": ["Réduire fortement sa vitesse, augmenter les distances de sécurité et conduire avec douceur", "Accélérer pour augmenter l'adhérence des roues au sol", "Utiliser le frein à main dans chaque virage serré"], "reponse": "Réduire fortement sa vitesse, augmenter les distances de sécurité et conduire avec douceur"},
        {"type": "choix", "question": "De nuit, le stationnement sur la chaussée d'une route nationale non éclairée oblige à allumer :", "choix": ["Les feux de position ou de stationnement", "Les feux de détresse uniquement", "Rien du tout, c'est totalement interdit de s'y garer"], "reponse": "Les feux de position ou de stationnement"},
        {"type": "choix", "question": "Pourquoi l'utilisation des feux de route est-elle inefficace dans un brouillard très épais ?", "choix": ["La lumière se reflète sur les gouttes d'eau et crée un mur blanc éblouissant", "Les feux de route s'éteignent automatiquement par forte humidité", "Le faisceau lumineux est dévié vers le bas de la route"], "reponse": "La lumière se reflète sur les gouttes d'eau et crée un mur blanc éblouissant"},
        {"type": "choix", "question": "Lorsque la visibilité est inférieure à 50 mètres à cause du brouillard sur autoroute, la vitesse maximale est de :", "choix": ["50 km/h", "70 km/h", "90 km/h"], "reponse": "50 km/h"},
        {"type": "choix", "question": "Qu'est-ce que l'effet de sillage produit par les pneus d'un gros véhicule par temps de pluie ?", "choix": ["Un nuage de fines gouttelettes pulvérisées en l'air qui sature la visibilité", "Une augmentation de la puissance aérodynamique du moteur", "Une réduction immédiate du risque d'aquaplaning à l'arrière"], "reponse": "Un nuage de fines gouttelettes pulvérisées en l'air qui sature la visibilité"},
        {"type": "choix", "question": "Un projecteur de phare mal réglé orienté trop vers le haut présente le risque de :", "choix": ["Éblouir dangereusement les usagers arrivant en face", "Éclairer le ciel et user l'ampoule prématurément", "Diminuer l'efficacité de la charge de la batterie"], "reponse": "Éblouir dangereusement les usagers arrivant en face"},
        {"type": "choix", "question": "Comment vérifier le bon fonctionnement de l'ensemble des feux extérieurs de votre véhicule seul ?", "choix": ["Allumer les feux un par un et observer leur reflet sur un mur à l'arrêt", "Rouler rapidement et regarder les voyants du tableau de bord", "Faire confiance au système informatique embarqué sans contrôle"], "reponse": "Allumer les feux un par un et observer leur reflet sur un mur à l'arrêt"},
        {"type": "choix", "question": "Le dispositif de réglage de la hauteur des phares situé sur le tableau de bord s'utilise :", "choix": ["Lorsque le véhicule est fortement chargé ou tracte une remorque", "Uniquement pendant la période hivernale de nuit", "De manière automatique selon l'état de la météo"], "reponse": "Lorsque le véhicule est fortement chargé ou tracte une remorque"},
        {"type": "choix", "question": "Pourquoi la distance de sécurité doit-elle être augmentée au passage dans un tunnel ?", "choix": ["Le manque de lumière et le confinement augmentent le temps de perception du freinage", "Les pneus surchauffent plus rapidement sur le bitume d'un tunnel", "Le klaxon y est strictement interdit de jour"], "reponse": "Le manque de lumière et le confinement augmentent le temps de perception du freinage"},
        {"type": "choix", "question": "Le klaxon (avertisseur sonore) est autorisé de nuit en agglomération :", "choix": ["Uniquement en cas de danger immédiat et absolu", "Pour saluer un piéton sur le trottoir", "Pour signaler son dépassement aux intersections"], "reponse": "Uniquement en cas de danger immédiat et absolu"},
        {"type": "choix", "question": "Qu'indique le voyant de couleur orange représentant des lignes ondulées horizontales traversées par des flèches ?", "choix": ["L'activation du système de dégivrage de la lunette arrière thermique", "Un manque de pression d'air dans le pneu arrière droit", "L'activation automatique de la climatisation"], "reponse": "L'activation du système de dégivrage de la lunette arrière thermique"},
        {"type": "choix", "question": "Sur une chaussée enneigée, l'adhérence des pneumatiques standards par rapport à une route sèche est divisée par :", "choix": ["4", "2", "10"], "reponse": "4"},
        {"type": "choix", "question": "Pourquoi les lunettes de soleil de catégorie 4 (très foncées) sont-elles interdites pour la conduite ?", "choix": ["Elles filtrent trop de lumière et altèrent la perception des feux de signalisation", "Elles provoquent des rayures sur le pare-brise", "Elles réduisent l'angle mort intérieur"], "reponse": "Elles filtrent trop de lumière et altèrent la perception des feux de signalisation"},
        {"type": "choix", "question": "De nuit, l'évaluation de la vitesse des autres véhicules rencontrés est :", "choix": ["Plus difficile et moins précise que de jour", "Plus facile grâce au contraste de la lumière des phares", "Strictement identique à celle mesurée en plein jour"], "reponse": "Plus difficile et moins précise que de jour"},
        {"type": "choix", "question": "Quelles précautions prendre en circulant sur une route jonchée de feuilles mortes mouillées en automne ?", "choix": ["Réduire sa vitesse et éviter les freinages ou coups de volant brusques", "Accélérer pour balayer les feuilles avec le pare-chocs", "Allumer ses feux de brouillard arrière immédiatement"], "reponse": "Réduire sa vitesse et éviter les freinages ou coups de volant brusques"},
        {"type": "choix", "question": "Un pare-brise comportant une fissure située dans le champ de vision direct du conducteur :", "choix": ["Nécessite un remplacement obligatoire sous peine de refus au contrôle technique", "Peut être réparé simplement avec une pastille adhésive de protection", "Est toléré par les forces de l'ordre si la fissure fait moins de 30 cm"], "reponse": "Nécessite un remplacement obligatoire sous peine de refus au contrôle technique"},
        {"type": "choix", "question": "Quel est l'effet de l'alcool sur le champ visuel périphérique du conducteur ?", "choix": ["Il rétrécit le champ visuel latéral, empêchant de détecter les dangers sur les côtés", "Il augmente la netteté des reliefs de nuit", "Il supprime l'angle mort des rétroviseurs"], "reponse": "Il rétrécit le champ visuel latéral, empêchant de détecter les dangers sur les côtés"},
        {"type": "choix", "question": "En cas de fortes vagues de chaleur, le risque d'éclatement d'un pneumatique augmente si celui-ci est :", "choix": ["Sous-gonflé", "Sur-gonflé", "Neuf et jamais utilisé"], "reponse": "Sous-gonflé"},
        {"type": "choix", "question": "Qu'indique l'allumage intermittent automatique des feux de détresse lors d'un freinage ?", "choix": ["Le déclenchement de l'aide au freinage d'urgence suite à une pression brutale", "Une surchauffe immédiate des plaquettes de freins avant", "Une perte d'adhérence totale liée à un aquaplaning"], "reponse": "Le déclenchement de l'aide au freinage d'urgence suite à une pression brutale"},
        {"type": "choix", "question": "La distance parcourue pendant le temps de reaction moyen d'un conducteur sain à 90 km/h est de :", "choix": ["25 mètres", "15 mètres", "40 mètres"], "reponse": "25 mètres"},
        {"type": "choix", "question": "Pourquoi est-il conseillé d'allumer ses feux de croisement dès que le ciel s'assombrit (gros nuages d'orage) ?", "choix": ["Pour être détecté beaucoup plus tôt par les autres conducteurs", "Pour éviter que la foudre ne frappe la carrosserie", "Pour recharger plus rapidement le circuit électrique"], "reponse": "Pour être détecté beaucoup plus tôt par les autres conducteurs"},
        {"type": "choix", "question": "Le rétroviseur extérieur droit doit être réglé de manière à apercevoir :", "choix": ["Le flanc droit du véhicule dans le quart inférieur gauche du miroir", "Uniquement la ligne de ciel pour éviter les angles morts", "La banquette arrière et les passagers"], "reponse": "Le flanc droit du véhicule dans le quart inférieur gauche du miroir"},
        {"type": "choix", "question": "Qu'est-ce que l'aquaplaning partiel et comment se manifeste-t-il au poste de conduite ?", "choix": ["Une perte de consistance du volant qui devient soudainement très léger et mou", "Un bruit métallique strident provenant des roues avant", "Un blocage automatique de la pédale d'embrayage"], "reponse": "Une perte de consistance du volant qui devient soudainement très léger et mou"},
        {"type": "choix", "question": "De nuit, le franchissement d'un sommet de côte sans visibilité impose de :", "choix": ["Passer brièvement en feux de croisement pour ne pas éblouir un usager masqué", "Rester en feux de route pour voir le plus loin possible", "Klaxonner énergiquement jusqu'au sommet"], "reponse": "Passer brièvement en feux de croisement pour ne pas éblouir un usager masqué"},
        {"type": "choix", "question": "Quelle est la fonction des essuie-glaces automatiques équipés d'un capteur de pluie ?", "choix": ["Adapter automatiquement la vitesse de balayage selon l'intensité de l'eau", "Nettoyer les phares avant dès que la chaussée est boueuse", "Couper le moteur en cas d'inondation majeure de la route"], "reponse": "Adapter automatiquement la vitesse de balayage selon l'intensité de l'eau"}


]
    # Sécurité si la fonction retourne du vide ou n'est pas une liste valide
    if not banque_questions_permis_b or not isinstance(banque_questions_permis_b, list):
        banque_questions_permis_b = [{
            "type": "choix",
            "question": "Quelle est la vitesse maximale autorisee sur autoroute par temps sec pour un jeune conducteur ?",
            "choix": ["110 km/h", "130 km/h", "100 km/h"],
            "reponse": "110 km/h",
        }]

    # Ajout dynamique de la cle numero et nettoyage des structures pour vos 200 QCM
    for index, fiche in enumerate(banque_questions_permis_b, start=1):
        fiche["numero"] = index
        # Securite pour s'assurer que chaque QCM possede bien une liste de choix exploitable
        if fiche.get("type") == "choix" and ("choix" not in fiche or not fiche["choix"]):
            fiche["choix"] = ["Option A", "Option B", "Option C"]

    # ENVOI FINAL DE LA BANQUE COMPLETE ET SECURISEE
    return banque_questions_permis_b
def charger_ecrite_permis_c_fiche_1():
    return [
        {
            "type": "choix",
            "question": "Fiche 1 — Dans le transport, les accidents avec blessures du chauffeur sont plus nombreux en circulation que hors circulation. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 1 — Quelle est la catégorie du permis exigée pour conduire un véhicule de transport en commun comportant 45 places circulant à vide ?",
            "choix": [],
            "reponse": "D ou Le permis D"
        },
        {
            "type": "choix",
            "question": "Fiche 1 — Pendant une pause, êtes-vous autorisé à ranger le chargement du véhicule ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 1 — Ce signal interdit-il l'accès aux véhicules mesurant plus de 3,50 m de hauteur, chargement compris ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 1 — Comment appelle-t-on les transports exécutés à titre onéreux pour le compte d'un client ?",
            "choix": [],
            "reponse": "Publics ou Compte d'autrui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 1 — En règle générale, de quelle longueur maximale un chargement muni d'une signalisation réglementaire peut-il dépasser l'arrière du véhicule ?",
            "choix": [],
            "reponse": "3 m"
        },
        {
            "type": "ecrite",
            "question": "Fiche 1 — Vous conduisez un tracteur solo de 19 t de PTAC et 38 t de PTRA. A quelle vitesse êtes-vous limité sur route à sens unique prioritaire ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "choix",
            "question": "Fiche 1 — Parmi les types de graissage moteur, il existe le graissage par pression. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "choix",
            "question": "Fiche 1 — La rémunération mensuelle d'un conducteur salarié peut être calculated en fonction de la charge transportée pendant le mois. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 1 — En cas de panne du chronotachygraphe, le délai maximal de remise en état, à compter de la panne, est fixé à ...?",
            "choix": [],
            "reponse": "1 semaine ou 7 jours"
        }
    ]

def charger_ecrite_permis_c_fiche_2():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 2 — Pour diminuer les risques d'accident, lors de la montée ou de la descente d'un camion, de combien de points d'appui le conducteur doit-il se servir ?",
            "choix": [],
            "reponse": "3"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — Le poids indiqué dans ce signal (2.5t) concerne-t-il le poids maximal autorisé que peut supporter l'essieu ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — Si, dans la même journée, vous conduisez un véhicule avec un chronotachygraphe numérique après avoir conduit un véhicule avec un chronotachygraphe à disque, devez-vous conserver le disque avec vous ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — Une huile multigrade classée SAE 20 W 40 peut-être utilisée uniquement en hiver ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 2 — Suite au contrôle technique périodique, lorsque le véhicule est refusé sans interdiction de circuler, dans quel délai maximum la contre-visite doit-elle être effectuée pour éviter une visite technique complète ?",
            "choix": [],
            "reponse": "1 mois"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — Vous conduisez un camion de 2,50 m de large ne comportant pas de caisse réfrigérée. Votre chargement peut-il atteindre 2,60 m de large ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 2 — Un véhicule isolé de 26 t de PTAC doit comporter à l'arrière un ou des disque(s) de limitation de vitesse. Quelle(s) est ou sont la ou les vitesse(s) indiquée(s) à l'arrière de ce camion ?",
            "choix": [],
            "reponse": "80 - 90 ou 80 km/h - 90 km/h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 2 — Au-delà de quel taux de surcharge (en pourcentage - %) le camion pourra-t-il être immobilisé, jusqu'au déchargement de l'excédent ?",
            "choix": [],
            "reponse": "5 ou 5 % ou 5 pour cent"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — La rémunération mensuelle d'un conducteur salarié peut être calculée en fonction de la distance parcourue pendant le mois. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "choix",
            "question": "Fiche 2 — En règle générale, existe-t-il une commande indépendante de frein de secours à l'intérieur des véhicules lourds neufs ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        }
    ]

def charger_ecrite_permis_c_fiche_3():
    return [
        {
            "type": "choix",
            "question": "Fiche 3 — Le nombre 33 dans le rectangle du haut de la plaque orange placée à l'arrière d'un camion signifie : 'produit très inflammable'. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "choix",
            "question": "Fiche 3 — En cas de récidive de grand excès de vitesse, une suspension du permis de conduire peut être assortie d'un permis limité à la conduite professionnelle (permis blanc) si l'infraction a été commise avec la voiture personnelle du chauffeur. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "choix",
            "question": "Fiche 3 — Si vous avez à imprimer un ticket à partir d'un chronotachygraphe numérique, devez-vous inscrire votre nom sur le ticket, si votre carte 'conducteur' est retirée de l'appareil au moment de l'impression ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 3 — Vous conduisez sans vous arrêter depuis 8 h 40 ce matin. Il est 12 h 40. Etes-vous en infraction ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 3 — Suite au contrôle technique périodique, quelle lettre figure sur le certificat d'immatriculation lorsque le véhicule est refusé sans interdiction de circuler ?",
            "choix": [],
            "reponse": "S ou La lettre S"
        },
        {
            "type": "choix",
            "question": "Fiche 3 — Le chargement d'un véhicule peut-il dépasser 4 m de haut ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 3 — Au-delà de quel tonnage les camions sont-ils concernés par les interdictions de circuler de fin de semaine ?",
            "choix": [],
            "reponse": "7,5 t ou 7,5 tonnes"
        },
        {
            "type": "choix",
            "question": "Fiche 3 — Mon véhicule a un poids à vide de 5 tonnes et un PTAC de 12 tonnes. Ce signal me concerne-t-il ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 3 — Le contrôle et le remplissage du circuit de refroidissement s'effectuent plutôt moteur chaud ou moteur froid ?",
            "choix": [],
            "reponse": "Moteur à froid ou A froid."
        },
        {
            "type": "ecrite",
            "question": "Fiche 3 — En règle générale, à quelle vitesse doit être réglé le limiteur de vitesse d'un camion neuf ?",
            "choix": [],
            "reponse": "90 km/h"
        }
    ]

def charger_ecrite_permis_c_fiche_4():
    return [
        {
            "type": "choix",
            "question": "Fiche 4 — En moyenne, il y a plus d'accidents graves impliquant un poids lourd les samedis et veilles de jours fériés que les jours de semaine. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Après l'obtention (hors diplômes professionnels) de votre premier permis de conduire du groupe lourd, devez-vous obligatoirement suivre une Formation Initiale Minimale Obligatoire (FIMO) pour le transport de biens dans des buts privés ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 4 — Après 4 h 30 de conduite continue, quelle est la durée minimale de la pause que vous devez respecter ?",
            "choix": [],
            "reponse": "45 mn"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Vous venez d'obtenir votre permis C, pouvez-vous conduire un véhicule équipé d'un chronotachygraphe numérique avant d'avoir reçu votre carte conducteur ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Vous effectuez un transport sous convention T.I.R. Les portes du véhicule doivent-elles être scellées ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Vous transportez du béton liquide. Votre camion (isolé) comporte 4 essieux. Lors de la pesée avant de partir, le ticket annonce 32,8 t. Avez-vous le droit de prendre la route ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 4 — Vous conduisez un camion de plus de 7,5 t de PTAC. En règle générale, quand débute l'interdiction de circulation en fin de semaine ?",
            "choix": [],
            "reponse": "Samedi à 22 h ou Samedi à 10 h du soir"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Sur cette chaussée la hauteur des arbres est susceptible d'être inférieure à 4,30 m. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 4 — En règle générale, les véhicules lourds utilisent deux batteries de 12 volts montées en ... ?",
            "choix": [],
            "reponse": "Série"
        },
        {
            "type": "choix",
            "question": "Fiche 4 — Est-il autorisé de monter des pneus de types différents sur un même essieu, roues jumelées ou non (en dehors de la roue de secours), sur un véhicule récent ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        }
    ]

def charger_ecrite_permis_c_fiche_5():
    return [
        {
            "type": "choix",
            "question": "Fiche 5 — Une plaque orange sans aucune inscription, placée à l'arrière d'un camion signifie qu'il s'agit d'un transport de matières dangereuses circulant à vide. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "choix",
            "question": "Fiche 5 — Cette limitation de vitesse peut-elle concerner les véhicules autres que les trains routiers, trains doubles et véhicules articulés ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 5 — Si, dans la même journée, vous conduisez un véhicule avec un chronotachygraphe à disque après avoir conduit un véhicule avec un chronotachygraphe numérique, devez-vous utiliser un disque vierge ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 5 — Le châssis d'un véhicule lourd est principalement constitué de longerons et de ... ?",
            "choix": [],
            "reponse": "Traverses"
        },
        {
            "type": "ecrite",
            "question": "Fiche 5 — Quel est le document, lié à l'entreprise, qui doit se trouver dans un véhicule, de plus de 3,5 t de PMA, qui effectue un transport de marchandises pour compte d'autrui ?",
            "choix": [],
            "reponse": "Copie conforme de la licence communautaire"
        },
        {
            "type": "ecrite",
            "question": "Fiche 5 — Quelle est la charge utile d'un véhicule dont le PTAC est de 19 t et le poids à vide de 7 t ?",
            "choix": [],
            "reponse": "12 t"
        },
        {
            "type": "ecrite",
            "question": "Fiche 5 — Votre véhicule (isolé) a un PTAC de 16 t. Sur route prioritaire à double sens, quelle est la vitesse maximale autorisée ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "choix",
            "question": "Fiche 5 — Un conducteur effectuant un transport de matières dangereuses dans un véhicule fourgon doit-il obligatoirement avoir suivi une formation particulière ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 5 — Vous avez interrompu votre conduite pendant 1 h 15 mn. Ce temps peut-il être pris en compte pour le calcul du temps de repos journalier ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 5 — Dans un camion neuf, le conducteur doit-il obligatoirement attacher sa ceinture de sécurité ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        }
    ]

def charger_ecrite_permis_c_fiche_6():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 6 — Quand je circule en Espagne, quel numéro de téléphone est-il conseillé d'utiliser pour appelers les secours à partir d'un portable ?",
            "choix": [],
            "reponse": "112"
        },
        {
            "type": "choix",
            "question": "Fiche 6 — Débrancher ou modifier les réglages du limiteur de vitesse peut entraîner une suspension du permis de conduire, même s'il n'y a pas eu d'excès de vitesse constaté. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "choix",
            "question": "Fiche 6 — Après 3 h de conduite continue, s'arrêter 10 mn sur un parking est-il considéré comme une pause ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 6 — Ce signal concerne-t-il uniquement les véhicules affectés au transport de marchandises excédant 3 500 kg de PTAC ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 6 — La licence de transport intérieur permet d'effectuer des transports de tout tonnage à condition de rester en France. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 6 — Vous chargez du sable dans un véhicule isolé, quelle est la charge maximale autorisée sur l'essieu le plus chargé du groupe d'essieux moteur ?",
            "choix": [],
            "reponse": "11,5 t ou 11,500 t ou 11 t 500"
        },
        {
            "type": "ecrite",
            "question": "Fiche 6 — Vous conduisez un camion neuf de 19 t de PTAC. A quelle vitesse êtes-vous limité en agglomération, sur une portion de route relevée à 70 km/h ?",
            "choix": [],
            "reponse": "50 km/h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 6 — Certains éléments de la chaîne cinématique nécessitent d'être vidangés ou ... ?",
            "choix": [],
            "reponse": "Graissés"
        },
        {
            "type": "ecrite",
            "question": "Fiche 6 — Vous attendez votre tour pour décharger sans connaître le temps d'attente. Sur quel symbole devez-vous positionner le sélecteur d'activité du chronotachygraphe ?",
            "choix": [],
            "reponse": "Autres tâches, marteaux ou marteaux"
        },
        {
            "type": "choix",
            "question": "Fiche 6 — Une pierre coincée entre des roues jumelées peut entraîner l'éclatement d'un pneumatique. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        }
    ]

def charger_ecrite_permis_c_fiche_7():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 7 — Citez un type d'extincteur couramment utilisé pour éteindre une voiture en flamme.",
            "choix": [],
            "reponse": "Poudre ou Mousse ou CO₂"
        },
        {
            "type": "ecrite",
            "question": "Fiche 7 — En France, à partir de quelle quantité d'alcool pur par litre de sang un conducteur de camion titulaire du permis de conduire depuis plus de trois ans encourt-il une sanction ?",
            "choix": [],
            "reponse": "0,50 g/l"
        },
        {
            "type": "choix",
            "question": "Fiche 7 — La descente dangereuse annoncée possède-t-elle un dénivelé de 100 mètres pour chaque kilomètre parcouru ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 7 — Vous avez perdu votre 'carte conducteur', pouvez-vous conduire en utilisant la carte 'entreprise' que possède votre employeur ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 7 — Effectuer un transport sous le régime 'TIR' permet de simplifier les formalités douanières. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 7 — Vous conduisez un camion comportant une caisse bâchée. Quelle peut être sa largeur maximale ?",
            "choix": [],
            "reponse": "2,55 m"
        },
        {
            "type": "ecrite",
            "question": "Fiche 7 — Vous conduisez un camion neuf de 26 t de PTAC. A quelle vitesse êtes-vous limité sur autoroute ?",
            "choix": [],
            "reponse": "90 km/h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 7 — Qu'aspire le moteur diesel lors du premier temps appelé « admission » ?",
            "choix": [],
            "reponse": "De l'air"
        },
        {
            "type": "ecrite",
            "question": "Fiche 7 — En règle générale, quelle est la durée minimale normale (non réduite) de repos hebdomadaire pour un conducteur de camions ?",
            "choix": [],
            "reponse": "45 h"
        },
        {
            "type": "choix",
            "question": "Fiche 7 — Vous chargez du gravier. Vous voulez connaître la charge maximale autorisée par essieu, vous pouvez la trouver sur la plaque du constructeur. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        }
    ]

def charger_ecrite_permis_c_fiche_8():
    return [
        {
            "type": "choix",
            "question": "Fiche 8 — Le modèle allemand, italien ou espagnol d'un constat européen d'accident, comporte-t-il les mêmes rubriques que le modèle français ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 8 — Je possède les catégories B - C et CE. Conduire ma voiture personnelle après avoir pris de la drogue peut entraîner la perte de la catégorie B de mon permis de conduire uniquement. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 8 — Au bout de combien de jours, au maximum, l'entreprise doit-elle 'télécharger' les données de votre carte conducteur ?",
            "choix": [],
            "reponse": "28 ou 28 jours"
        },
        {
            "type": "choix",
            "question": "Fiche 8 — Le temps de conduite pour venir à l'entreprise, le matin, avec votre véhicule personnel doit-il être ajouté au temps de conduite de votre véhicule lourd ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 8 — Comment appelle-t-on les transports exécutés à titre non onéreux servant à transporter les marchandises de sa propre entreprise ?",
            "choix": [],
            "reponse": "Compte propre ou Privé"
        },
        {
            "type": "ecrite",
            "question": "Fiche 8 — Quelle est la longueur maximale d'un camion isolé à 2 essieux ?",
            "choix": [],
            "reponse": "12 m"
        },
        {
            "type": "ecrite",
            "question": "Fiche 8 — Vous conduisez un camion neuf de 19 t de PTAC. A quelle vitesse êtes-vous limité sur route non prioritaire ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 8 — Ce signal concerne-t-il les véhicules affectés au transport de produits dangereux ou au transport de produits explosifs ?",
            "choix": [],
            "reponse": "Produits explosifs ou Explosifs"
        },
        {
            "type": "choix",
            "question": "Fiche 8 — Le turbocompresseur a pour fonction de diminuer l'air admis dans les cylindres ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 8 — En circulation, le fait de freiner désactive obligatoirement le régulateur de vitesse. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        }
    ]

def charger_ecrite_permis_c_fiche_9():
    return [
        {
            "type": "choix",
            "question": "Fiche 9 — Le signal de détresse peut-il remplacer le triangle de présignalisation pour un véhicule d'un PTAC de plus de 3,5 t ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 9 — Le non-respect des limitations de tonnage pour le passage sur les ponts peut-il entraîner une suspension du permis de conduire ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 9 — En double équipage, le temps passé sur la couchette d'un véhicule en circulation, est-il considéré comme repos journalier ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 9 — Cette signalisation de présignalisation peut annoncer une barrière de dégel : vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 9 — Suite au contrôle technique périodique, quelle lettre figure sur le certificat d'immatriculation lorsque le véhicule est accepté ?",
            "choix": [],
            "reponse": "A ou La lettre A"
        },
        {
            "type": "ecrite",
            "question": "Fiche 9 — En règle générale, quel est le PTAC maximal d'un véhicule isolé comportant 2 essieux ?",
            "choix": [],
            "reponse": "19 t"
        },
        {
            "type": "ecrite",
            "question": "Fiche 9 — Vous conduisez un camion de plus de 7,5 t de PTAC. Quand finit l'interdiction de circulation en fin de semaine ?",
            "choix": [],
            "reponse": "Dimanche à 22 h ou Dimanche à 10 h du soir"
        },
        {
            "type": "ecrite",
            "question": "Fiche 9 — Le circuit d'alimentation d'un moteur diesel se compose, entre autres éléments, de deux pompes : l'une est dite pompe d'injection haute pression, l'autre est dite pompe... ?",
            "choix": [],
            "reponse": "D'alimentation"
        },
        {
            "type": "ecrite",
            "question": "Fiche 9 — Votre véhicule est équipé d'un chronotachygraphe numérique. Vous avez perdu votre carte 'conducteur', combien de jours, au maximum, pouvez vous conduire sans carte ?",
            "choix": [],
            "reponse": "15 ou 15 jours"
        },
        {
            "type": "choix",
            "question": "Fiche 9 — Dans un camion neuf, le passager doit-il obligatoirement attacher sa ceinture de sécurité ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        }
    ]

def charger_ecrite_permis_c_fiche_10():
    return [
        {
            "type": "choix",
            "question": "Fiche 10 — Dans une longue descente, en cas de rupture de freins, si j'utilise une voie de détresse, le véhicule que je conduis sera-t-il gravement endommagé ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 10 — Quel symbole devez-vous afficher sur l'écran du chronotachygraphe numérique lorsque vous nettoyez votre véhicule ?",
            "choix": [],
            "reponse": "Autres tâches, marteaux ou marteaux"
        },
        {
            "type": "choix",
            "question": "Fiche 10 — La réglementation sociale européenne s'applique-t-elle à un conducteur non salarié propriétaire de son véhicule ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 10 — Ce signal concerne-t-il uniquement les véhicules isolés ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 10 — Pour un camion carrossé dans un atelier agréé, quel est le délai maximal pour le présenter à la première visite technique ?",
            "choix": [],
            "reponse": "12 mois ou 1 an"
        },
        {
            "type": "choix",
            "question": "Fiche 10 — Dans la définition du poids à vide, les différents réservoirs sont-ils remplis ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 10 — Hors agglomération, sur une route à double sens, vous suivez un camion à 70 km/h. Quel intervalle de sécurité minimum devez-vous respecter ?",
            "choix": [],
            "reponse": "50 m"
        },
        {
            "type": "choix",
            "question": "Fiche 10 — Les filtres à carburant ou filtres principaux sont situés entre la pompe d'alimentation et la pompe d'injection haute pression. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 10 — Le conducteur doit pouvoir présenter les preuves de son activité pour la journée en cours et pour les ... jours précédents ?",
            "choix": [],
            "reponse": "56 ou 56 jours"
        },
        {
            "type": "ecrite",
            "question": "Fiche 10 — Au-delà de quel PTAC les véhicules de transport de marchandises doivent-ils être équipés d'un dispositif complémentaire de signalisation arrière ?",
            "choix": [],
            "reponse": "6 t"
        }
    ]

def charger_ecrite_permis_c_fiche_11():
    return [
        {
            "type": "choix",
            "question": "Fiche 11 — En cas d'accident dans lequel votre véhicule est en cause, les forces de l'ordre peuvent-elles saisir votre carte 'conducteur' ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 11 — Quelle est la catégorie du permis exigée pour conduire un tracteur 'en solo' de 10 t de PTAC et de 38 t de PTRA quand il circule non attelé d'une semi-remorque ?",
            "choix": [],
            "reponse": "C ou Le permis C"
        },
        {
            "type": "choix",
            "question": "Fiche 11 — Le conducteur peut-il bacher ou débacher son véhicule pendant une pause ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 11 — Je circule avec un véhicule mesurant 2,30 m de large. A hauteur de ce signal, puis-je continuer sur cette route ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 11 — Comment s'appelle le document qui doit accompagner la marchandise lors de tout transport pour compte d'autrui ?",
            "choix": [],
            "reponse": "Lettre de voiture"
        },
        {
            "type": "ecrite",
            "question": "Fiche 11 — Quelle est la longueur maximale d'un camion isolé à 3 essieux ?",
            "choix": [],
            "reponse": "12 m"
        },
        {
            "type": "choix",
            "question": "Fiche 11 — Votre camion, en charge, transporte des denrées périssables, avez-vous le droit de continuer votre trajet le samedi après 22 h ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 11 — L'embrayage est un organe mécanique nécessaire au passage des vitesses sur les seules boîtes mécaniques ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 11 — Quand le repos journalier est fractionné, quelle doit être la durée minimale totale de ce repos ?",
            "choix": [],
            "reponse": "12 h ou 12 heures"
        },
        {
            "type": "choix",
            "question": "Fiche 11 — Vous suivez un véhicule dont les dispositifs réfléchissants sont triangulaires. Ce véhicule est probablement un véhicule isolé. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        }
    ]

def charger_ecrite_permis_c_fiche_12():
    return [
        {
            "type": "choix",
            "question": "Fiche 12 — Avec votre véhicule, vous avez détérioré des panneaux de signalisation. Devez-vous obligatoirement le signaler à votre compagnie d'assurance ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — Ce signal m'annonce-t-il une voie de détresse qui sera située sur ma gauche ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 12 — Quelle est la durée maximale autorisée de conduite continue pour un conducteur de camion ?",
            "choix": [],
            "reponse": "4 h 30 ou 4 h 30 mn"
        },
        {
            "type": "ecrite",
            "question": "Fiche 12 — Quel symbole devez-vous afficher sur l'écran du chronotachygraphe numérique lorsque vous partez déjeuner ?",
            "choix": [],
            "reponse": "Pause, repos ou lit"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — Faut-il un seul certificat d'immatriculation pour un ensemble de véhicules constitué d'un camion de 19 t de PTAC auquel on a attelé une bétonnière sur roues de 400 kg ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — En règle générale, le chargement peut-il dépasser l'aplomb avant du véhicule ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 12 — Au-dessous de quelle hauteur libre d'un pont celle-ci sera-t-elle signalée ?",
            "choix": [],
            "reponse": "4,30 m"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — Circuler avec un seul pneu lisse ou détérioré peut entraîner l'immobilisation du véhicule jusqu'à son remplacement. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — La marche arrière sert à inverser le sens de rotation de l'arbre de transmission ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 12 — Le circuit électrique alimentant le chronotachygraphe est-il indépendant du circuit alimentant le coupe-batterie ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        }
    ]

def charger_ecrite_permis_c_fiche_13():
    return [
        {
            "type": "choix",
            "question": "Fiche 13 — Les accidents corporels entre un poids lourd et une voiture sont majoritairement des accidents avec des véhicules circulant dans le même sens. Vrai ou Faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "choix",
            "question": "Fiche 13 — Je circule, à vide, avec un véhicule de 5 tonnes de poids à vide et de 15 tonnes de PTAC. A hauteur de ce signal, puis-je passer ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 13 — Un premier arrêt de 15 mn sur un parking peut-il être considéré comme une pause ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 13 — Quel symbole devez-vous afficher sur l'écran du chronotachygraphe lors des vérifications du véhicule avant le départ ?",
            "choix": [],
            "reponse": "Autres tâches, marteaux ou marteaux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 13 — Que signifie la mention 'TIR' placée sur une plaque à l'arrière du véhicule ?",
            "choix": [],
            "reponse": "Transit International Routier"
        },
        {
            "type": "choix",
            "question": "Fiche 13 — Le poids réel d'un véhicule peut-il être égal à son PTAC ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 13 — En agglomération, vous suivez un camion. Quel intervalle de sécurité minimum devez-vous respecter ?",
            "choix": [],
            "reponse": "Distance parcourue en 2 secondes ou 2 s"
        },
        {
            "type": "choix",
            "question": "Fiche 13 — Dans une entreprise, le chargement est effectué par un manutentionnaire. Une fois terminé, vous appartient-il d'effectuer le contrôle de l'arrimage avant de démarrer ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 13 — Un pont court permet d'obtenir un couple plus important et une vitesse du véhicule plus faible. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 13 — Quelle est la périodicité des vérifications techniques obligatoires pour les chronotachygraphes ?",
            "choix": [],
            "reponse": "2 ans"
        }
    ]

def charger_ecrite_permis_c_fiche_14():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 14 — Si une partie de votre chargement est tombée sur la chaussée, par quel dispositif obligatoire devez-vous prévenir les autres usagers ?",
            "choix": [],
            "reponse": "Un triangle de présignalisation"
        },
        {
            "type": "ecrite",
            "question": "Fiche 14 — Après l'obtention (hors diplômes professionnels) de votre premier permis de conduire du groupe lourd, quelle formation devez-vous effectuer avant de pouvoir conduire un véhicule dans le cadre d'un transport public de marchandises ?",
            "choix": [],
            "reponse": "FIMO ou Formation Initiale Minimale Obligatoire"
        },
        {
            "type": "choix",
            "question": "Fiche 14 — Si vous avez à imprimer un ticket à partir d'un chronotachygraphe numérique, devez-vous inscrire votre nom sur le ticket, si votre carte 'conducteur' est insérée dans l'appareil au moment de l'impression ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 14 — Quelle est la durée de validité de votre carte 'conducteur' ?",
            "choix": [],
            "reponse": "5 ans"
        },
        {
            "type": "choix",
            "question": "Fiche 14 — La dernière visite technique de votre camion date de 8 mois. Etes-vous en infraction en le conduisant ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 14 — En règle générale, quel est le PTAC maximal d'un véhicule isolé de 3 essieux ?",
            "choix": [],
            "reponse": "26 t"
        },
        {
            "type": "choix",
            "question": "Fiche 14 — En général, un véhicule tracteur en solo est-il soumis aux mêmes limitations de vitesse que s'il est attelé ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 14 — Ce signal peut-il concerner les véhicules transportant une faible quantité de produits polluants ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 14 — Le mécanisme de direction comprend une « bielle pendante ». Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 14 — En cas d'obligation, une paire de chaînes à neige doit être montée sur les roues motrices ou sur les roues directrices ?",
            "choix": [],
            "reponse": "Les roues motrices"
        }
    ]

def charger_ecrite_permis_c_fiche_15():
    return [
        {
            "type": "choix",
            "question": "Fiche 15 — Un chiffre doublé (ex: 33) dans le rectangle du haut de la plaque orange placée à l'arrière d'un camion signifie : 'produit de nature à polluer les eaux'. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 15 — Avec le permis C, quel est le PTAC maximum de la remorque que vous pouvez atteler derrière votre camion ?",
            "choix": [],
            "reponse": "750 kg"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — Le conducteur d'un véhicule de dépannage, est-il soumis à la réglementation sociale européenne, dans un rayon de 100 km autour de son point d'attache ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — Un conducteur peut-il demander une copie papier des données numériques, liées à son activité, qui sont conservées dans l'entreprise ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — La lettre de voiture doit détailler la nature des marchandises transportées. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 15 — Quelle est la charge utile d'un véhicule dont le PTAC est de 32 t et le poids à vide de 9 t ?",
            "choix": [],
            "reponse": "23 t"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — Sur le périphérique parisien, les camions peuvent circuler à 80 km/h. Vrai ou Faux ?",
            "choix": ["Oui", "Non"],
            "reponse": "Faux"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — Ce signal m'indique un arrêt d'autobus. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 15 — Quel type de suspension équipe généralement les véhicules lourds permettant de régler la hauteur du véhicule ?",
            "choix": [],
            "reponse": "La suspension pneumatique ou Pneumatique"
        },
        {
            "type": "choix",
            "question": "Fiche 15 — Le principal avantage du système de freinage antibloquant est-il de réduire les distances de freinage ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        }
    ]

def charger_ecrite_permis_c_fiche_16():
    return [
        {
            "type": "choix",
            "question": "Fiche 16 — Le constat amiable d'accident peut-il constituer une preuve de responsabilité ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — Un conducteur ramenant, à vide, un camion citerne de carburant, non dégazé, doit-il obligatoirement avoir suivi une formation particulière ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — Ce signal concerne-t-il les véhicules affectés aux seuls transports de produits polluants ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — Sur un ticket imprimé à partir du chronotachygraphe numérique, peut-on trouver les temps de conduite et les temps passés aux autres tâches ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — La licence communautaire permet-elle d'effectuer des transports dans toute l'Union européenne ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 16 — Quelle charge maximale autorisée peut supporter un essieu isolé ?",
            "choix": [],
            "reponse": "13 t"
        },
        {
            "type": "ecrite",
            "question": "Fiche 16 — Vous conduisez un camion neuf de 19 t de PTAC. A quelle vitesse êtes-vous limité sur route prioritaire ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — Le recreusage des pneumatiques est-il une opération qui peut s'effectuer uniquement par un spécialiste ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 16 — Vous avez fait une coupure de 4 h (repos), quelle sera, au minimum, la durée de la période de repos suivante pour être en règle vis-à-vis du repos journalier ?",
            "choix": [],
            "reponse": "9 h ou 9 heures"
        },
        {
            "type": "choix",
            "question": "Fiche 16 — Vous chargez du sable. Vous voulez connaître la charge maximale autorisée par essieu, vous pouvez la trouver sur la plaque de tare et de surface. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        }
    ]

def charger_ecrite_permis_c_fiche_17():
    return [
        {
            "type": "choix",
            "question": "Fiche 17 — Dans le transport routier, c'est pendant le travail, hors conduite, que l'on dénombre le plus fort taux d'accidents chez les conducteurs ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 17 — En cas d'excès de vitesse de 42 km/h, je pourrai repartir si je reconnais l'infraction ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 17 — Pendant une pause, êtes-vous autorisé à décharger le véhicule ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "ecrite",
            "question": "Fiche 17 — Vous avez fait une coupure de 2 h, quelle sera, au minimum, la durée (non réduite) de la période de repos que vous devrez prendre à la fin de votre journée de travail pour être en règle vis-à-vis du repos journalier ?",
            "choix": [],
            "reponse": "11 h ou 11 heures"
        },
        {
            "type": "choix",
            "question": "Fiche 17 — La date limite de validité de la dernière visite technique est-elle inscrite sur le certificat d'immatriculation du véhicule ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 17 — Vous conduisez un camion comportant une caisse réfrigérée. Quelle peut être sa largeur maximale ?",
            "choix": [],
            "reponse": "2,60 m"
        },
        {
            "type": "ecrite",
            "question": "Fiche 17 — Je conduis un camion de 26 t de PTAC et de 10 t de PV. Pour emprunter une route où une barrière de dégel à 12 t avec mention demi-charge autorisée est en place, quel doit être le poids maximum de mon chargement ?",
            "choix": [],
            "reponse": "8 t ou 8 tonnes"
        },
        {
            "type": "choix",
            "question": "Fiche 17 — Par temps sec, ce signal me concerne-t-il ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 17 — Lorsque the conducteur serre le frein de parc, le cylindre de frein à ressort se remplit d'air. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Faux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 17 — Quelle est la profondeur minimale (en millimètre - mm) des rainures principales d'un pneumatique de poids lourd ?",
            "choix": [],
            "reponse": "1 mm ou 1"
        }
    ]

def charger_ecrite_permis_c_fiche_18():
    return [
        {
            "type": "choix",
            "question": "Fiche 18 — En cas d'accident, les données du chronotachygraphe numérique peuvent-elles servir de preuve devant un tribunal ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 18 — Si je perds tous les points de mon permis de conduire à la suite d'infractions commises au volant de ma voiture personnelle, pourrai-je continuer à conduire mon camion ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 18 — Ce signal interdit le dépassement à tous les véhicules dont le PTAC est supérieur à 3,5 tonnes.",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 18 — Vous conduisez sans vous arrêter depuis 8 h ce matin. Il est 12 h 40. Etes-vous en infraction ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 18 — Lors d'un contrôle des temps de conduite et de repos sur la route, en plus de la journée en cours, sur quelle période devez-vous pouvoir présenter les données ?",
            "choix": [],
            "reponse": "56 ou 56 jours"
        },
        {
            "type": "choix",
            "question": "Fiche 18 — Vous conduisez un véhicule isolé à 2 essieux. Est-il possible d'être en surcharge sur l'essieu arrière si le poids réel ne dépasse pas le PTAC ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 18 — Vous conduisez un camion neuf de 19 t de PTAC. A quelle vitesse êtes-vous limité sur route à sens unique prioritaire ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "choix",
            "question": "Fiche 18 — Le circuit de freinage européen rend le freinage de l'essieu avant indépendant du freinage de l'essieu arrière. Vrai ou faux ?",
            "choix": ["Vrai", "Faux"],
            "reponse": "Vrai"
        },
        {
            "type": "ecrite",
            "question": "Fiche 18 — Vous vous arrêtez pour faire le plein de carburant. Sur quel symbole devez-vous positionner le sélecteur d'activité du chronotachygraphe ?",
            "choix": [],
            "reponse": "Autres tâches, marteaux ou marteaux"
        },
        {
            "type": "ecrite",
            "question": "Fiche 18 — Au-delà de quel PTAC un extincteur à poudre de 6 kg minimum, placé à l'extérieur, doit-il équiper un camion neuf ?",
            "choix": [],
            "reponse": "7,5 t"
        }
    ]

def charger_ecrite_permis_c_fiche_19():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 19 — Sur autoroute, en cas d'incident, pour appeler les secours, vaut-il mieux utiliser une borne d'appel ou son téléphone portable ?",
            "choix": [],
            "reponse": "La borne d'appel"
        },
        {
            "type": "choix",
            "question": "Fiche 19 — Sur une route à double sens limitée à 70 km/h, lors d'un contrôle routier, votre carte conducteur indique que vous rouliez à 80 km/h. Pouvez-vous être sanctionné ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 19 — Vous rentrez chez vous le soir avec le camion de l'entreprise. Le matin, le temps de conduite pour vous rendre au dépôt est-il compté comme du temps de conduite ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 19 — Après 2 heures de conduite, quelle est la durée minimale d'un premier arrêt pouvant être pris en compte comme pause ?",
            "choix": [],
            "reponse": "15 mn"
        },
        {
            "type": "choix",
            "question": "Fiche 19 — Dans le cadre d'un transport public, peut-il y avoir une lettre de voiture (avec état récapitulatif) dans le véhicule pour plusieurs voyages ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 19 — Quelle est la majoration maximale autorisée du PTAC pour un véhicule équipé d'un dispositif ralentisseur pesant 400 kg ?",
            "choix": [],
            "reponse": "400 kg"
        },
        {
            "type": "ecrite",
            "question": "Fiche 19 — Vous conduisez un tracteur solo de 19 t de PTAC et 38 t de PTRA. A quelle vitesse êtes-vous limité sur route non prioritaire ?",
            "choix": [],
            "reponse": "60 km/h"
        },
        {
            "type": "choix",
            "question": "Fiche 19 — En agglomération, ce signal est-il implanté 50 mètres avant le carrefour à sens giratoire ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 19 — Le dispositif antiblocage de roues (ABS) peut-il fonctionner en même temps que le ou les dispositifs ralentisseurs ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 19 — Où doit se trouver l'extincteur obligatoire sur un véhicule isolé neuf de transport de marchandises de plus de 7,5 t à l'intérieur ou à l'extérieur ?",
            "choix": [],
            "reponse": "A l'extérieur"
        }
    ]

def charger_ecrite_permis_c_fiche_20():
    return [
        {
            "type": "ecrite",
            "question": "Fiche 20 — Que signifie une plaque de couleur orange, comportant 2 rectangles sans inscription, placée à l'arrière d'un camion ?",
            "choix": [],
            "reponse": "Transport de matières dangereuses"
        },
        {
            "type": "choix",
            "question": "Fiche 20 — Lors d'un contrôle sur la route, est-il obligatoire de pouvoir présenter votre carte de qualification conducteur (CQC) ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 20 — Hors agglomération, ce signal est-il implanté 100 mètres avant le carrefour à sens giratoire ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 20 — Vous avez interrompu votre conduite pendant 45 mn. Ce temps peut-il être pris en compte pour le calcul du temps de repos journalier ?",
            "choix": ["Oui", "Non"],
            "reponse": "Non"
        },
        {
            "type": "choix",
            "question": "Fiche 20 — Dans le cadre du transport public, peut-il y avoir une seule lettre de voiture (avec état récapitulatif) dans le véhicule pour un transport comportant plusieurs destinataires dans la même journée ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "choix",
            "question": "Fiche 20 — Vous transportez du béton liquide. Votre camion (isolé) comporte 4 essieux. Lors de la pesée avant de partir, le ticket annonce 30,5 t. Avez-vous le droit de prendre la route ?",
            "choix": ["Oui", "Non"],
            "reponse": "Oui"
        },
        {
            "type": "ecrite",
            "question": "Fiche 20 — Vous conduisez un tracteur solo de 19 t de PTAC et 38 t de PTRA. A quelle vitesse êtes-vous limité sur route prioritaire ?",
            "choix": [],
            "reponse": "80 km/h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 20 — En principe, le ralentisseur hydraulique est situé sur ... ?",
            "choix": [],
            "reponse": "La transmission ou L'arbre de transmission"
        },
        {
            "type": "ecrite",
            "question": "Fiche 20 — En règle générale, quelle est la durée minimale normale (non réduite) obligatoire de repos journalier lorsque celui-ci n'est pas fractionné ?",
            "choix": [],
            "reponse": "11 h"
        },
        {
            "type": "ecrite",
            "question": "Fiche 20 — Quel type d'extincteur faut-il éviter d'utiliser pour éteindre les flammes d'un feu d'hydrocarbure ?",
            "choix": [],
            "reponse": "Un extincteur à eau ou A eau"
        }
    ]




def charger_orale_permis_c_fiche_1():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 1 — Conduite et comportement.",
        "questions": [
            {
                "id": 1,
                "topic": "Dimensions et trajectoire",
                "question": "Lors d'un virage serré à gauche avec un véhicule lourd possédant un important porte-à-faux arrière, quel phénomène physique devez-vous impérativement anticiper ?",
                "choix": [
                    "L'arrière du véhicule déporte vers la gauche, du même côté que le virage.",
                    "L'arrière du véhicule déporte vers la droite (phénomène de balayage).",
                    "Les roues avant se soulèvent du sol.",
                    "Le véhicule n'a aucun mouvement particulier à l'arrière."
                ],
                "reponse": "L'arrière du véhicule déporte vers la droite (phénomène de balayage)."
            },
            {
                "id": 2,
                "topic": "Masse et énergie cinétique",
                "question": "Si vous doublez la vitesse de votre poids lourd (en passant de 45 km/h à 90 km/h par exemple), par combien est multipliée son énergie cinétique ?",
                "choix": ["Par 2", "Par 8", "Par 4", "Par 16"],
                "reponse": "Par 4"
            },
            {
                "id": 3,
                "topic": "Centre de gravité et stabilité",
                "question": "Parmi les situations suivantes, laquelle augmente le plus le risque de basculement (renversement) d'un poids lourd en virage ?",
                "choix": [
                    "Un chargement placé trop haut et mal arrimé.",
                    "Un centre de gravité très bas et une charge parfaitement calée au plancher.",
                    "Une vitesse réduite bien en deçà des limitations.",
                    "Des pneumatiques en parfait état et correctement gonflés."
                ],
                "reponse": "Un chargement placé trop haut et mal arrimé."
            },
            {
                "id": 4,
                "topic": "Angles morts",
                "question": "Où se situe principalement l'angle mort le plus critique pour un conducteur de poids lourd s'apprêtant à tourner à droite en agglomération ?",
                "choix": [
                    "Directement à l'arrière, au centre de la benne ou de la caisse.",
                    "Sur le toit de la cabine.",
                    "Immédiatement le long du flanc droit et à l'avant droit de la cabine.",
                    "À plus de 100 mètres en amont du véhicule."
                ],
                "reponse": "Immédiatement le long du flanc droit et à l'avant droit de la cabine."
            },
            {
                "id": 5,
                "topic": "Inertie et freinage",
                "question": "Pourquoi la distance d'arrêt d'un poids lourd lourdement chargé est-elle considérablement plus longue que celle d'un véhicule léger ?",
                "choix": [
                    "Parce que les pneus de poids lourds n'ont aucune adhérence sur le bitume sec.",
                    "À cause de l'inertie importante générée par la masse élevée du véhicule.",
                    "Parce que les freins pneumatiques sont instantanément inefficaces au premier appui.",
                    "Uniquement à cause de la largeur hors-tout du véhicule."
                ],
                "reponse": "À cause de l'inertie importante générée par la masse élevée du véhicule."
            },
            {
                "id": 6,
                "topic": "Dimensions réglementaires",
                "question": "Quelle est, de manière générale, la hauteur maximale autorisée pour un véhicule ou un chargement circulant sur la voie publique en France (hors transports exceptionnels) ?",
                "choix": ["3,50 mètres", "3,80 mètres", "4,50 mètres", "4,00 mètres"],
                "reponse": "4,00 mètres"
            },
            {
                "id": 7,
                "topic": "Comportement et conditions climatiques",
                "question": "Quel est l'effet principal d'un fort vent latéral sur un poids lourd bâché ou à grand volume circulant à vide ?",
                "choix": [
                    "Il favorise le déport latéral du véhicule ou un risque de renversement.",
                    "Il plaque solidement le véhicule sur la chaussée.",
                    "Il améliore la stabilité directionnelle.",
                    "Il réduit systématiquement la consommation de carburant."
                ],
                "reponse": "Il favorise le déport latéral du véhicule ou un risque de renversement."
            },
            {
                "id": 8,
                "topic": "Répartition de la masse",
                "question": "Pourquoi est-il dangereux de concentrer l'essentiel de la charge à l'extrême avant de la zone de chargement d'un porteur ?",
                "choix": [
                    "Cela allège excessivement l'essieu directeur et fait perdre toute adhérence au train avant.",
                    "Cela surcharge l'essieu directeur, altère la direction et déséquilibre le freinage.",
                    "Cela n'a aucune conséquence sur la mécanique ou la tenue de route.",
                    "Cela provoque obligatoirement le déjaugeage du moteur."
                ],
                "reponse": "Cela surcharge l'essieu directeur, altère la direction et déséquilibre le freinage."
            },
            {
                "id": 9,
                "topic": "Inertie et descentes",
                "question": "Dans une longue descente abrupte, quelle méthode permet de maîtriser la vitesse du poids lourd sans risquer de détruire les freins de service par surchauffe ?",
                "choix": [
                    "Maintenir le pied en continu sur la pédale de frein de service.",
                    "Se mettre au point mort pour laisser rouler le véhicule en roue libre.",
                    "Utiliser le frein moteur (rapport adapté engagé) et les ralentisseurs auxiliaires.",
                    "Couper le contact du moteur pour économiser du carburant."
                ],
                "reponse": "Utiliser le frein moteur (rapport adapté engagé) et les ralentisseurs auxiliaires."
            },
            {
                "id": 10,
                "topic": "Comportement et empattement",
                "question": "Lors d'un virage serré à droite en agglomération, quel est le risque principal lié à l'empattement long d'un poids lourd ?",
                "choix": [
                    "Le soulèvement systématique du train arrière.",
                    "L'accélération spontanée du véhicule vers l'avant.",
                    "Le recul intempestif de la remorque.",
                    "Le mordage du trottoir ou de l'accotement par les roues arrière intérieures ('couper la corde')."
                ],
                "reponse": "Le mordage du trottoir ou de l'accotement par les roues arrière intérieures ('couper la corde')."
            }
        ]
    }


def charger_orale_permis_c_fiche_2():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 2 — Éléments de sécurité et réglementation.",
        "questions": [
            {
                "id": 1,
                "topic": "Temps de conduite journalier",
                "question": "En réglementation sociale européenne (RSE), quelle est la durée maximale de conduite journalière standard pour un conducteur de poids lourd ?",
                "choix": ["8 heures", "9 heures", "10 heures", "11 heures"],
                "reponse": "9 heures"
            },
            {
                "id": 2,
                "topic": "Dépassement du temps de conduite",
                "question": "Combien de fois par semaine un conducteur est-il autorisé à prolonger sa conduite journalière jusqu'à 10 heures maximum ?",
                "choix": ["1 fois", "2 fois", "3 fois", "Aucune fois"],
                "reponse": "2 fois"
            },
            {
                "id": 3,
                "topic": "Temps de pause obligatoire",
                "question": "Après une période de conduite continue de 4 heures et 30 minutes, quelle doit être la durée minimale de la pause d'un seul bloc ?",
                "choix": ["15 minutes", "30 minutes", "45 minutes", "1 heure"],
                "reponse": "45 minutes"
            },
            {
                "id": 4,
                "topic": "Fractionnement de la pause",
                "question": "Si un conducteur décide de fractionner sa pause obligatoire au cours des 4h30 de conduite, comment doit-il procéder réglementairement ?",
                "choix": [
                    "Une pause de 15 minutes d'abord, puis une pause de 30 minutes ensuite.",
                    "Une pause de 30 minutes d'abord, puis une pause de 15 minutes ensuite.",
                    "Trois pauses de 15 minutes réparties équitablement.",
                    "Le fractionnement n'est pas autorisé."
                ],
                "reponse": "Une pause de 15 minutes d'abord, puis une pause de 30 minutes ensuite."
            },
            {
                "id": 5,
                "topic": "Repos journalier normal",
                "question": "Dans le cadre d'une période de 24 heures, quelle est la durée minimale d'un repos journalier normal (non réduit) ?",
                "choix": ["9 heures", "11 heures", "12 heures", "24 heures"],
                "reponse": "11 heures"
            },
            {
                "id": 6,
                "topic": "Équipement de contrôle",
                "question": "Quel appareil électronique, obligatoire à bord des véhicules de transport de marchandises de plus de 3,5 tonnes, enregistre l'activité du conducteur ?",
                "choix": ["Le limiteur de vitesse", "Le chronotachygraphe (ou mouchard)", "Le GPS professionnel", "L'éthylotest anti-démarrage"],
                "reponse": "Le chronotachygraphe (ou mouchard)"
            },
            {
                "id": 7,
                "topic": "Contrôle routier et documents",
                "question": "Lors d'un contrôle routier, sur combien de jours précédents le conducteur doit-il être capable de présenter les données de son activité (carte conducteur ou disques) ?",
                "choix": ["Le jour même et les 7 jours précédents", "Le jour même et les 14 jours précédents", "Le jour même et les 28 jours précédents", "Le jour même et les 56 jours précédents"],
                "reponse": "Le jour même et les 28 jours précédents"
            },
            {
                "id": 8,
                "topic": "Équipement de sécurité obligatoire",
                "question": "Parmi les équipements de sécurité suivants, lequel est spécifiquement obligatoire à bord d'un poids lourd (en plus du gilet jaune et du triangle) ?",
                "choix": ["Une boîte de fusibles de rechange", "Au moins un extincteur en état de fonctionner", "Une boussole de secours", "Une trousse de premiers secours"],
                "reponse": "Au moins un extincteur en état de fonctionner"
            },
            {
                "id": 9,
                "topic": "Signalisation spécifique",
                "question": "Les disques de limitation de vitesse (par exemple 80 et 90) apposés à l'arrière d'un véhicule de transport de marchandises sont obligatoires pour :",
                "choix": [
                    "Tous les véhicules de plus de 3,5 tonnes de PTAC.",
                    "Uniquement les véhicules articulés.",
                    "Uniquement les véhicules transportant des matières dangereuses.",
                    "Tous les utilitaires légers de plus de 1,5 tonne."
                ],
                "reponse": "Tous les véhicules de plus de 3,5 tonnes de PTAC."
            },
            {
                "id": 10,
                "topic": "Conduite maximale hebdomadaire",
                "question": "Quelle est la limite maximale absolue de temps de conduite cumulée sur une seule semaine ?",
                "choix": ["48 heures", "56 heures", "60 heures", "90 heures"],
                "reponse": "56 heures"
            }
        ]
    }

def charger_orale_permis_c_fiche_3():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 3 — Comportement en cas d'accident / Incendie.",
        "questions": [
            {
                "id": 1,
                "topic": "Première action sur zone",
                "question": "En arrivant le premier sur le lieu d'un accident, quelle est la toute première démarche de la règle 'P.A.S.' que vous devez appliquer ?",
                "choix": ["Alerter les secours", "Secourir les victimes", "Protéger les lieux pour éviter un suraccident", "Rechercher des témoins"],
                "reponse": "Protéger les lieux pour éviter un suraccident"
            },
            {
                "id": 2,
                "topic": "Protection du site",
                "question": "Quel équipement spécifique au conducteur de poids lourd est indispensable pour signaler sa présence sur les voies lors de la protection de la zone ?",
                "choix": ["Le gilet de haute visibilité rétro-réfléchissant", "La lampe torche de la cabine", "Le disque de stationnement", "La carte conducteur"],
                "reponse": "Le gilet de haute visibilité rétro-réfléchissant"
            },
            {
                "id": 3,
                "topic": "Alerte des secours",
                "question": "Quel est le numéro de téléphone d'urgence unique européen à composer gratuitement depuis n'importe quel téléphone pour joindre les secours ?",
                "choix": ["15", "17", "18", "112"],
                "reponse": "112"
            },
            {
                "id": 4,
                "topic": "Informations lors de l'alerte",
                "question": "Parmi les informations suivantes, laquelle est cruciale lors de l'alerte si votre poids lourd est impliqué ou témoin ?",
                "choix": [
                    "Le prix des marchandises transportées.",
                    "La localisation précise et la présence éventuelle de matières dangereuses (plaques orange).",
                    "La marque et l'année de mise en circulation du camion.",
                    "Le numéro de votre permis de conduire."
                ],
                "reponse": "La localisation précise et la présence éventuelle de matières dangereuses (plaques orange)."
            },
            {
                "id": 5,
                "topic": "Comportement envers les blessés",
                "question": "Face à une victime d'accident de la route inconsciente mais qui respire normalement, quelle est la position d'attente recommandée ?",
                "choix": [
                    "Assise sur le bord de la route.",
                    "Sur le dos, les jambes surélevées.",
                    "En Position Latérale de Sécurité (PLS).",
                    "Sur le ventre."
                ],
                "reponse": "En Position Latérale de Sécurité (PLS)."
            },
            {
                "id": 6,
                "topic": "Début d'incendie moteur",
                "question": "En cas de début d'incendie sous le capot moteur ou la cabine, comment devez-vous utiliser votre extincteur ?",
                "choix": [
                    "Ouvrir grand le capot d'un coup sec pour jeter toute la poudre.",
                    "Attaquer la base des flammes par de petites ouvertures sans ouvrir grand le capot.",
                    "Vider l'extincteur sur les pneus arrière d'abord.",
                    "Attendre que les flammes s'éteignent d'elles-mêmes."
                ],
                "reponse": "Attaquer la base des flammes par de petites ouvertures sans ouvrir grand le capot."
            },
            {
                "id": 7,
                "topic": "Type d'extincteur standard",
                "question": "Quel type d'extincteur équipe généralement les cabines de poids lourds pour éteindre la majorité des types de feux (A, B, C) ?",
                "choix": ["L'extincteur à eau pure", "L'extincteur à poudre polyvalente", "L'extincteur au CO2 pur", "L'extincteur à mousse uniquement"],
                "reponse": "L'extincteur à poudre polyvalente"
            },
            {
                "id": 8,
                "topic": "Évacuation d'un tunnel en feu",
                "question": "Si un incendie se déclare dans un tunnel et immobilise votre véhicule, quelle doit être votre réaction immédiate ?",
                "choix": [
                    "Rester confiné à l'intérieur de la cabine en fermant les fenêtres.",
                    "Couper le moteur, laisser les clés sur le contact et fuir vers l'issue de secours la plus proche.",
                    "Tenter une marche arrière sur plusieurs kilomètres.",
                    "Dételer la remorque pour sauver uniquement le tracteur."
                ],
                "reponse": "Couper le moteur, laisser les clés sur le contact et fuir vers l'issue de secours la plus proche."
            },
            {
                "id": 9,
                "topic": "Risque lié aux pneumatiques",
                "question": "Pourquoi l'échauffement anormal des freins en descente présente-t-il un risque d'incendie majeur sur un poids lourd ?",
                "choix": [
                    "Il peut provoquer l'inflammation directe des pneumatiques ou des projections de graisse.",
                    "Il coupe instantanément l'alimentation en carburant.",
                    "Il fait exploser les batteries du véhicule.",
                    "Il n'y a aucun risque d'incendie lié aux freins."
                ],
                "reponse": "Il peut provoquer l'inflammation directe des pneumatiques ou des projections de graisse."
            },
            {
                "id": 10,
                "topic": "Le constat amiable",
                "question": "En cas d'accident purement matériel avec un autre usager, dans quel délai réglementaire maximum devez-vous transmettre le constat amiable à votre assureur ?",
                "choix": ["24 heures", "48 heures", "5 jours ouvrés", "15 jours"],
                "reponse": "5 jours ouvrés"
            }
        ]
    }

def charger_orale_permis_c_fiche_4():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 4 — Conduite en conditions difficiles / Montagne.",
        "questions": [
            {
                "id": 1,
                "topic": "Vitesse par temps de pluie",
                "question": "Sur autoroute, lorsque la chaussée est mouillée, à combien est réduite la vitesse maximale autorisée pour un véhicule de transport de marchandises de plus de 3,5 tonnes dont le PTAC n'excède pas 12 tonnes ?",
                "choix": ["90 km/h", "80 km/h", "70 km/h", "60 km/h"],
                "reponse": "80 km/h"
            },
            {
                "id": 2,
                "topic": "Visibilité et brouillard",
                "question": "En cas de brouillard épais avec une visibilité inférieure à 50 mètres, quelle est la vitesse maximale absolue pour tous les véhicules, y compris les poids lourds sur autoroute ?",
                "choix": ["70 km/h", "60 km/h", "50 km/h", "30 km/h"],
                "reponse": "50 km/h"
            },
            {
                "id": 3,
                "topic": "Distance de sécurité en tunnel",
                "question": "En circulation, quelle distance minimale de sécurité devez-vous obligatoirement maintenir avec le véhicule devant vous à l'intérieur d'un tunnel ?",
                "choix": ["50 mètres", "100 mètres ou 2 diodes de balisage bleues", "150 mètres", "Une distance égale à deux camions"],
                "reponse": "100 mètres ou 2 diodes de balisage bleues"
            },
            {
                "id": 4,
                "topic": "Croisement en montagne / pente",
                "question": "Sur une route de montagne étroite, lorsque le croisement est impossible entre un véhicule isolé (porteur) et un ensemble de véhicules (articulé), qui doit faire marche arrière ?",
                "choix": [
                    "L'ensemble de véhicules doit reculer.",
                    "Le véhicule le plus lourd doit reculer.",
                    "Le véhicule isolé doit faire marche arrière.",
                    "Celui qui est en descente doit toujours reculer."
                ],
                "reponse": "Le véhicule isolé doit faire marche arrière."
            },
            {
                "id": 5,
                "topic": "Priorité en forte pente",
                "question": "Lors du croisement difficile de deux véhicules de même catégorie sur une route à forte pente, quel véhicule doit s'arrêter le premier pour faciliter le passage ?",
                "choix": [
                    "Le véhicule qui monte.",
                    "Le véhicule qui descend.",
                    "Le véhicule qui transporte des marchandises périssables.",
                    "Le véhicule le plus large."
                ],
                "reponse": "Le véhicule qui descend."
            },
            {
                "id": 6,
                "topic": "Phénomène d'aquaplaning",
                "question": "Quel facteur lié aux caractéristiques d'un poids lourd à vide augmente le risque d'aquaplaning (perte d'adhérence sur film d'eau) par rapport à un véhicule chargé ?",
                "choix": [
                    "La pression au sol plus faible des pneumatiques.",
                    "La hauteur excessive de la cabine.",
                    "La longueur de l'empattement.",
                    "Une température trop basse des freins."
                ],
                "reponse": "La pression au sol plus faible des pneumatiques."
            },
            {
                "id": 7,
                "topic": "Équipements hivernaux",
                "question": "Quel dispositif amovible obligatoire en zone montagneuse (période hivernale selon la loi Montagne) doit être monté sur les roues motrices en cas de route fortement enneigée ?",
                "choix": ["Des pneus lisses haute performance", "Des chaînes à neige métalliques ou chaussettes homologuées", "Des barres anti-encastrement", "Des élargisseurs de voies"],
                "reponse": "Des chaînes à neige métalliques ou chaussettes homologuées"
            },
            {
                "id": 8,
                "topic": "Adhérence et verglas",
                "question": "Quelle est la principale source de danger concernant l'utilisation des ralentisseurs auxiliaires (hydraulique ou électromagnétique) sur une route verglacée ?",
                "choix": [
                    "Le risque de blocage des roues motrices entraînant une mise en portefeuille ou une perte de contrôle.",
                    "La surchauffe immédiate du liquide de refroidissement.",
                    "L'usure instantanée des disques de frein.",
                    "L'augmentation brutale de la consommation de carburant."
                ],
                "reponse": "Le risque de blocage des roues motrices entraînant une mise en portefeuille ou une perte de contrôle."
            },
            {
                "id": 9,
                "topic": "Utilisation des voies de détresse",
                "question": "À quoi sert une voie de détresse (généralement signalée par un damier rouge et blanc) située en bas d'une longue descente ?",
                "choix": [
                    "À s'arrêter pour faire la pause RSE.",
                    "À permettre l'arrêt d'un véhicule lourd dont les freins de service sont devenus inopérants.",
                    "À doubler les véhicules plus lents par la droite.",
                    "À faciliter le demi-tour des véhicules de secours."
                ],
                "reponse": "À permettre l'arrêt d'un véhicule lourd dont les freins de service sont devenus inopérants."
            },
            {
                "id": 10,
                "topic": "Barrières de dégel",
                "question": "Qu'indique la mise en place d'une barrière de dégel sur un itinéraire routier ?",
                "choix": [
                    "Que la route est fermée pour cause de chutes de pierres.",
                    "Une interdiction temporaire de circuler pour les véhicules dépassant un certain tonnage afin de préserver la chaussée.",
                    "Une obligation d'allumer ses feux de brouillard.",
                    "La gratuité temporaire du péage autoroutier."
                ],
                "reponse": "Une interdiction temporaire de circuler pour les véhicules dépassant un certain tonnage afin de préserver la chaussée."
            }
        ]
    }

def charger_orale_permis_c_fiche_5():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 5 — Gestes et postures / Ergonomie.",
        "questions": [
            {
                "id": 1,
                "topic": "Troubles Musculosquelettiques (TMS)",
                "question": "Quelle est la principale cause d'arrêts de travail liés aux risques professionnels chez les conducteurs de poids lourds hors accidents de la route ?",
                "choix": [
                    "Les troubles musculosquelettiques (TMS) touchant le dos et les articulations.",
                    "Les baisses d'acuité visuelle.",
                    "Les migraines chroniques.",
                    "Les maladies infectieuses."
                ],
                "reponse": "Les troubles musculosquelettiques (TMS) touchant le dos et les articulations."
            },
            {
                "id": 2,
                "topic": "Descente de la cabine",
                "question": "Quelle est la méthode réglementaire et sécuritaire pour descendre de la cabine d'un poids lourd afin d'éviter les chutes ou entorses ?",
                "choix": [
                    "Sauter directement sur le sol en fléchissant les genoux.",
                    "Descendre face à la route en s'appuyant sur la portière.",
                    "Descendre face à la cabine en utilisant la méthode des '3 points d'appui' (mains et pieds sur les marchepieds).",
                    "Se laisser glisser le long du siège."
                ],
                "reponse": "Descendre face à la cabine en utilisant la méthode des '3 points d'appui' (mains et pieds sur les marchepieds)."
            },
            {
                "id": 3,
                "topic": "Manutention manuelle de charge",
                "question": "Pour ramasser un colis lourd posé au sol lors d'une livraison, quelle posture le conducteur doit-il adopter pour protéger sa colonne vertébrale ?",
                "choix": [
                    "Garder les jambes tendues et plier le dos en avant.",
                    "Fléchir les genoux, garder le dos droit et porter la charge au plus près du corps.",
                    "Faire une rotation rapide du tronc en soulevant le colis.",
                    "Prendre appui uniquement sur un seul bras."
                ],
                "reponse": "Fléchir les genoux, garder le dos droit et porter la charge au plus près du corps."
            },
            {
                "id": 4,
                "topic": "Équipements de Protection Individuelle (EPI)",
                "question": "Quel Équipement de Protection Individuelle (EPI) est obligatoirement requis lors des opérations de manutention, d'arrimage ou de débâchage ?",
                "choix": [
                    "Des lunettes de soleil polarisantes.",
                    "Des gants de manutention et des chaussures de sécurité.",
                    "Une combinaison de pluie intégrale.",
                    "Un casque antibruit."
                ],
                "reponse": "Des gants de manutention et des chaussures de sécurité."
            },
            {
                "id": 5,
                "topic": "Réglage du siège conducteur",
                "question": "Pourquoi est-il crucial de régler correctement la suspension et la hauteur du siège pneumatique avant de prendre la route ?",
                "choix": [
                    "Uniquement pour voir plus loin au-dessus des voitures.",
                    "Pour amortir les vibrations de la route et prévenir les pathologies lombaires.",
                    "Pour réduire la consommation de carburant.",
                    "Pour empêcher le volant de se bloquer."
                ],
                "reponse": "Pour amortir les vibrations de la route et prévenir les pathologies lombaires."
            },
            {
                "id": 6,
                "topic": "Hygiène de vie et conduite",
                "question": "Quel facteur lié à l'hygiène de vie aggrave considérablement la fatigue et le risque de somnolence lors d'un long trajet ?",
                "choix": [
                    "Une alimentation trop riche et lourde lors des pauses de repas.",
                    "Une hydratation régulière à l'eau plate.",
                    "L'écoute d'émissions de radio d'information.",
                    "Le maintien d'une température fraîche dans la cabine."
                ],
                "reponse": "Une alimentation trop riche et lourde lors des pauses de repas."
            },
            {
                "id": 7,
                "topic": "Risque lié au débâchage",
                "question": "Lors du bâchage ou du débâchage manuel d'une carrosserie de type 'savoyarde' ou d'une semi-remorque, quel est le risque d'accident majeur pour le conducteur ?",
                "choix": [
                    "Le risque de coupure avec les papiers de bord.",
                    "La chute de hauteur depuis le plateau ou l'échelle du véhicule.",
                    "L'asphyxie par manque d'air sous la bâche.",
                    "L'explosion des pneumatiques."
                ],
                "reponse": "La chute de hauteur depuis le plateau ou l'échelle du véhicule."
            },
            {
                "id": 8,
                "topic": "Postures prolongées",
                "question": "Après plusieurs heures de conduite immobile sur l'autoroute, que recommande la médecine du travail lors des pauses RSE ?",
                "choix": [
                    "Rester assis en cabine pour économiser son énergie.",
                    "S'étirer, marcher quelques minutes et mobiliser ses articulations.",
                    "Faire une sieste d'au moins 4 heures immédiatement.",
                    "Vérifier la pression des pneus à main nue."
                ],
                "reponse": "S'étirer, marcher quelques minutes et mobiliser ses articulations."
            },
            {
                "id": 9,
                "topic": "Travaux en hauteur et sécurité",
                "question": "Pour contrôler un chargement situé en hauteur ou nettoyer son pare-brise, quel comportement le conducteur doit-il proscrire ?",
                "choix": [
                    "Utiliser l'échelle intégrée ou une passerelle sécurisée.",
                    "Monter sur les moyeux de roues ou utiliser des éléments de carrosserie non prévus comme appuis.",
                    "Porter des chaussures de sécurité antidérapantes.",
                    "Prendre appui sur des poignées fixes."
                ],
                "reponse": "Monter sur les moyeux de roues ou utiliser des éléments de carrosserie non prévus comme appuis."
            },
            {
                "id": 10,
                "topic": "Vigilance et baisse d'attention",
                "question": "Quel signal corporel précurseur doit alerter immédiatement un conducteur qu'il est en train de subir des phases de micro-sommeils ?",
                "choix": [
                    "Des picotements dans les yeux, des bâillements répétés et des raideurs dans la nuque.",
                    "Une sensation de faim subite.",
                    "Une amélioration de la vision nocturne.",
                    "Une baisse automatique du volume de l'autoradio."
                ],
                "reponse": "Des picotements dans les yeux, des bâillements répétés et des raideurs dans la nuque."
            }
        ]
    }

def charger_orale_permis_c_fiche_6():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 6 — Chargement.",
        "questions": [
            {
                "id": 1,
                "topic": "Définition de la Charge Utile",
                "question": "Comment calcule-t-on mathématiquement la Charge Utile (CU) maximale que peut transporter un véhicule porteur ?",
                "choix": [
                    "Poids à Vide (PV) + Poids Total Autorisé en Charge (PTAC)",
                    "Poids Total Autorisé en Charge (PTAC) - Poids à Vide (PV)",
                    "Poids Total Roulant Autorisé (PTRA) - Poids à Vide (PV)",
                    "Le poids de la cabine uniquement"
                ],
                "reponse": "Poids Total Autorisé en Charge (PTAC) - Poids à Vide (PV)"
            },
            {
                "id": 2,
                "topic": "Risque lié à la surcharge",
                "question": "Quelle est la principale conséquence mécanique et sécuritaire d'une surcharge du véhicule sur la route ?",
                "choix": [
                    "Une diminution de la consommation de carburant.",
                    "Une augmentation importante de la distance de freinage et un risque de rupture des organes de suspension.",
                    "Une amélioration de la tenue de route en virage.",
                    "Une réduction du risque d'éclatement des pneumatiques."
                ],
                "reponse": "Une augmentation importante de la distance de freinage et un risque de rupture des organes de suspension."
            },
            {
                "id": 3,
                "topic": "Responsabilité du chargement",
                "question": "Lors d'un contrôle routier constatant une mauvaise répartition de la charge ou un défaut d'arrimage flagrant, qui est pénalement responsable de la sécurité du véhicule en marche ?",
                "choix": [
                    "Le client destinataire de la marchandise.",
                    "L'expéditeur uniquement.",
                    "Le conducteur du véhicule.",
                    "Le fabricant des sangles d'arrimage."
                ],
                "reponse": "Le conducteur du véhicule."
            },
            {
                "id": 4,
                "topic": "Techniques d'arrimage",
                "question": "Quel dispositif est principalement utilisé pour empêcher les marchandises de glisser ou de basculer vers l'avant lors d'un freinage d'urgence ?",
                "choix": [
                    "Des sangles d'arrimage à cliquet fixées aux anneaux d'ancrage du plateau.",
                    "Du film plastique étirable classique.",
                    "De la colle à bois.",
                    "Le simple fait de fermer les portes arrière."
                ],
                "reponse": "Des sangles d'arrimage à cliquet fixées aux anneaux d'ancrage du plateau."
            },
            {
                "id": 5,
                "topic": "Surcharge par essieu",
                "question": "En France, en dehors de la surcharge du PTAC global, quel autre dépassement de masse lié au chargement est lourdement sanctionné ?",
                "choix": [
                    "Le dépassement du poids maximal autorisé sous un seul essieu (surcharge à l'essieu).",
                    "Le dépassement du poids du réservoir de carburant.",
                    "Le poids du conducteur en cabine.",
                    "Le poids des rétroviseurs extérieurs."
                ],
                "reponse": "Le dépassement du poids maximal autorisé sous un seul essieu (surcharge à l'essieu)."
            },
            {
                "id": 6,
                "topic": "Dépassement de chargement à l'arrière",
                "question": "À l'arrière d'un véhicule de transport de marchandises, jusqu'à quelle distance maximale le chargement peut-il dépasser l'extrémité du véhicule (avec signalisation appropriée) ?",
                "choix": ["1 mètre", "2 mètres", "3 mètres", "5 mètres"],
                "reponse": "3 mètres"
            },
            {
                "id": 7,
                "topic": "Signalisation du chargement",
                "question": "À partir de quel dépassement de la marchandise à l'arrière du véhicule est-il obligatoire d'installer un dispositif réfléchissant complété par un feu rouge si la visibilité est réduite ou de nuit ?",
                "choix": ["Dès le premier centimètre", "Dès que le dépassement excède 1 mètre", "Uniquement s'il dépasse de 2 mètres", "Ce n'est jamais obligatoire"],
                "reponse": "Dès que le dépassement excède 1 mètre"
            },
            {
                "id": 8,
                "topic": "Transport de liquides (effet de carène liquide)",
                "question": "Quel danger spécifique présente la conduite d'une citerne contenant du liquide non compartimentée et remplie seulement à moitié ?",
                "choix": [
                    "Une baisse immédiate de la pression d'huile moteur.",
                    "L'effet de roulis et de vagues (carène liquide) qui déplace la masse de gauche à droite ou d'avant en arrière, risquant de renverser le camion.",
                    "Une surchauffe des pneumatiques arrière.",
                    "L'évaporation instantanée du produit."
                ],
                "reponse": "L'effet de roulis et de vagues (carène liquide) qui déplace la masse de gauche à droite ou d'avant en arrière, risquant de renverser le camion."
            },
            {
                "id": 9,
                "topic": "Dépassement à l'avant",
                "question": "Est-il autorisé de faire dépasser un chargement rigide à l'avant de l'aplomb antérieur de votre véhicule lourd ?",
                "choix": [
                    "Oui, jusqu'à 1 mètre.",
                    "Oui, si le chargement est léger.",
                    "Non, le chargement ne doit jamais dépasser l'aplomb avant du véhicule.",
                    "Oui, de nuit uniquement."
                ],
                "reponse": "Non, le chargement ne doit jamais dépasser l'aplomb avant du véhicule."
            },
            {
                "id": 10,
                "topic": "Le code de blocage / calage",
                "question": "Lors du chargement de blocs de béton ou de palettes lourdes, quel élément place-t-on souvent sur le plancher pour augmenter le coefficient de friction (frottement) ?",
                "choix": [
                    "Des tapis ou bandes en caoutchouc antidérapants.",
                    "De la graisse industrielle.",
                    "Des feuilles de papier cartonné lisse.",
                    "De la paille."
                ],
                "reponse": "Des tapis ou bandes en caoutchouc antidérapants."
            }
        ]
    }

def charger_orale_permis_c_fiche_7():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 7 — Dépassement.",
        "questions": [
            {
                "id": 1,
                "topic": "Réglementation sur autoroute",
                "question": "Sur une autoroute à 3 voies ou plus, quelles voies un véhicule de transport de marchandises de plus de 3,5 tonnes ou de plus de 7 mètres de long a-t-il l'interdiction d'emprunter ?",
                "choix": [
                    "La voie de droite.",
                    "La deuxième voie.",
                    "Toutes les voies situées le plus à gauche au-delà des deux premières voies de droite.",
                    "L'interdiction ne s'applique qu'aux voitures."
                ],
                "reponse": "Toutes les voies situées le plus à gauche au-delà des deux premières voies de droite."
            },
            {
                "id": 2,
                "topic": "Évaluation du temps de dépassement",
                "question": "Pourquoi le dépassement entre deux poids lourds (communément appelé 'course de limaces') est-il particulièrement délicat ?",
                "choix": [
                    "Parce que la différence de vitesse est souvent très faible, ce qui allonge considérablement la distance et le temps de dépassement.",
                    "Parce que les camions n'ont pas le droit de rouler à plus de 50 km/h.",
                    "Parce que les moteurs se coupent automatiquement en cas de dépassement.",
                    "Il n'est jamais délicat."
                ],
                "reponse": "Parce que la différence de vitesse est souvent très faible, ce qui allonge considérablement la distance et le temps de dépassement."
            },
            {
                "id": 3,
                "topic": "Interdiction de dépassement",
                "question": "Que signifie le panneau rond à bord rouge représentant une voiture noire à gauche et un camion rouge à droite ?",
                "choix": [
                    "Interdiction aux voitures de dépasser les poids lourds.",
                    "Interdiction à tous les véhicules de transports de marchandises de plus de 3,5 tonnes de PTAC de dépasser tous les véhicules à moteur (sauf deux-roues sans side-car).",
                    "Obligation pour les camions de circuler à gauche.",
                    "Fin d'interdiction de dépasser pour les poids lourds."
                ],
                "reponse": "Interdiction à tous les véhicules de transports de marchandises de plus de 3,5 tonnes de PTAC de dépasser tous les véhicules à moteur (sauf deux-roues sans side-car)."
            },
            {
                "id": 4,
                "topic": "Effet d'aspiration",
                "question": "Lorsqu'un poids lourd dépasse un usager vulnérable (cycliste, piéton, deux-roues), quel phénomène aérodynamique peut mettre cet usager en grand danger ?",
                "choix": [
                    "L'effet d'aspiration créé par le déplacement d'air, suivi d'un effet de souffle qui peut déséquilibrer l'usager.",
                    "Une augmentation brutale de l'adhérence du deux-roues.",
                    "Une baisse de la température ambiante.",
                    "Un freinage d'urgence automatique de l'usager."
                ],
                "reponse": "L'effet d'aspiration créé par le déplacement d'air, suivi d'un effet de souffle qui peut déséquilibrer l'usager."
            },
            {
                "id": 5,
                "topic": "Distance latérale minimale",
                "question": "Quelle distance latérale minimale devez-vous laisser entre votre poids lourd et un cycliste lors d'un dépassement en agglomération ?",
                "choix": ["0,50 mètre", "1,00 mètre", "1,50 mètre", "2,00 mètres"],
                "reponse": "1,00 mètre"
            },
            {
                "id": 6,
                "topic": "Distance latérale hors agglomération",
                "question": "Quelle distance latérale minimale devez-vous laisser entre votre poids lourd et un piéton ou un cycliste lors d'un dépassement hors agglomération ?",
                "choix": ["1,00 mètre", "1,20 mètre", "1,50 mètre", "2,50 mètres"],
                "reponse": "1,50 mètre"
            },
            {
                "id": 7,
                "topic": "Dépassement aux intersections",
                "question": "Est-il autorisé de dépasser un véhicule à moteur à une intersection où vous devez céder la priorité (par exemple un carrefour à priorité à droite) ?",
                "choix": [
                    "Oui, si le véhicule devant avance lentement.",
                    "Non, le dépassement est strictement interdit aux intersections où le conducteur ne bénéficie pas de la priorité de passage.",
                    "Oui, de jour uniquement.",
                    "Oui, si vous utilisez l'avertisseur sonore."
                ],
                "reponse": "Non, le dépassement est strictement interdit aux intersections où le conducteur ne bénéficie pas de la priorité de passage."
            },
            {
                "id": 8,
                "topic": "Comportement du véhicule dépassé",
                "question": "Lorsqu'un autre véhicule est en train de vous dépasser, quelle est votre obligation réglementaire en tant que conducteur du véhicule dépassé ?",
                "choix": [
                    "Accélérer pour l'empêcher de passer.",
                    "Maintenir sa vitesse constante (et ne pas accélérer) ou ralentir légèrement si la situation l'exige pour faciliter sa manœuvre.",
                    "Activer immédiatement vos feux de détresse.",
                    "Serrer au maximum vers la gauche."
                ],
                "reponse": "Maintenir sa vitesse constante (et ne pas accélérer) ou ralentir légèrement si la situation l'exige pour faciliter sa manœuvre."
            },
            {
                "id": 9,
                "topic": "Dépassement d'un engin de service hivernal",
                "question": "Est-il autorisé de dépasser un engin de service hivernal (chasse-neige ou saleuse) en action sur la chaussée (gyrophares bleus allumés) ?",
                "choix": [
                    "Oui, si sa vitesse est inférieure à 30 km/h.",
                    "Non, il est strictement interdit de dépasser un engin de service hivernal en cours de travail avec ses avertisseurs spéciaux activés.",
                    "Oui, uniquement sur autoroute.",
                    "Oui, par la droite si la voie est libre."
                ],
                "reponse": "Non, il est strictement interdit de dépasser un engin de service hivernal en cours de travail avec ses avertisseurs spéciaux activés."
            },
            {
                "id": 10,
                "topic": "Rabattement après dépassement",
                "question": "Quand pouvez-vous vous rabattre en toute sécurité devant le véhicule que vous venez de dépasser avec votre poids lourd ?",
                "choix": [
                    "Dès que l'arrière de votre caisse a dépassé sa cabine de 10 centimètres.",
                    "Lorsque vous apercevez distinctement l'intégralité du véhicule dépassé dans votre rétroviseur intérieur (ou principal droit) et que la distance de sécurité est suffisante.",
                    "Dès que le véhicule dépassé vous fait des appels de phares agressifs.",
                    "Immédiatement après avoir coupé la ligne blanche."
                ],
                "reponse": "Lorsque vous apercevez distinctement l'intégralité du véhicule dépassé dans votre rétroviseur intérieur (ou principal droit) et que la distance de sécurité est suffisante."
            }
        ]
    }
def charger_orale_permis_c_fiche_8():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 8 — Dynamique du véhicule.",
        "questions": [
            {
                "id": 1,
                "topic": "Force centrifuge en virage",
                "question": "Comment évolue la force centrifuge (qui pousse le véhicule vers l'extérieur du virage) si vous doublez la vitesse de votre poids lourd ?",
                "choix": [
                    "Elle reste identique.",
                    "Elle est doublée.",
                    "Elle est triplée.",
                    "Elle est quadruplée."
                ],
                "reponse": "Elle est quadruplée."
            },
            {
                "id": 2,
                "topic": "Rayon de courbure et force centrifuge",
                "question": "Pour une même vitesse, comment varie la force centrifuge si le rayon du virage devient deux fois plus serré (court) ?",
                "choix": [
                    "La force centrifuge diminue de moitié.",
                    "La force centrifuge est doublée.",
                    "La force centrifuge est quadruplée.",
                    "La force centrifuge s'annule."
                ],
                "reponse": "La force centrifuge est doublée."
            },
            {
                "id": 3,
                "topic": "Transfert de charge au freinage",
                "question": "Lors d'un freinage violent avec un porteur, que subit la charge en termes de transfert de masse ?",
                "choix": [
                    "La masse se transfère vers l'arrière du véhicule.",
                    "La masse se transfère vers l'avant du véhicule, écrasant le train directeur.",
                    "La masse se déporte uniquement sur le flanc droit.",
                    "Il n'y a aucun transfert de charge possible."
                ],
                "reponse": "La masse se transfère vers l'avant du véhicule, écrasant le train directeur."
            },
            {
                "id": 4,
                "topic": "Distance de réaction",
                "question": "Qu'est-ce que la distance de réaction lors de la conduite d'un poids lourd ?",
                "choix": [
                    "La distance parcourue entre la perception du danger et l'action sur la pédale de frein.",
                    "La distance nécessaire pour immobiliser complètement le véhicule.",
                    "La distance parcourue entre l'action sur le frein et l'arrêt total.",
                    "La distance minimale de sécurité avec le véhicule de devant."
                ],
                "reponse": "La distance parcourue entre la perception du danger et l'action sur la pédale de frein."
            },
            {
                "id": 5,
                "topic": "Calcul de la distance d'arrêt",
                "question": "Sur chaussée sèche, quelle est la formule simplifiée pour estimer rapidement la distance d'arrêt totale (réaction + freinage) en mètres ?",
                "choix": [
                    "Multiplier le chiffre des dizaines de la vitesse par lui-même (Vitesse au carré).",
                    "Multiplier le chiffre des dizaines de la vitesse par 3.",
                    "Multiplier la vitesse globale par 2.",
                    "Diviser la vitesse par le poids à vide."
                ],
                "reponse": "Multiplier le chiffre des dizaines de la vitesse par lui-même (Vitesse au carré)."
            },
            {
                "id": 6,
                "topic": "Adhérence et état des pneus",
                "question": "Quel système d'assistance électronique empêche le blocage des roues lors d'un freinage d'urgence, préservant ainsi l'adhérence et la trajectoire du camion ?",
                "choix": ["L'EBS", "L'ESP", "L'ABS", "L'ASR"],
                "reponse": "L'ABS"
            },
            {
                "id": 7,
                "topic": "Contrôle de trajectoire (ESP)",
                "question": "Quelle est la fonction principale du système électronique de contrôle de trajectoire (ESP) sur un véhicule lourd ?",
                "choix": [
                    "Empêcher le patinage des roues motrices au démarrage.",
                    "Corriger la trajectoire en freinant de manière sélective une ou plusieurs roues pour éviter le tête-à-queue ou le renversement.",
                    "Régler automatiquement l'espacement avec les voitures.",
                    "Augmenter la puissance du moteur en côte."
                ],
                "reponse": "Corriger la trajectoire en freinant de manière sélective une ou plusieurs roues pour éviter le tête-à-queue ou le renversement."
            },
            {
                "id": 8,
                "topic": "Effet du vent sur la trajectoire",
                "question": "Lors de la sortie d'une zone abritée (comme la fin d'un dépassement de grand bâtiment ou d'un autre camion), quel phénomène dynamique déstabilise la trajectoire ?",
                "choix": [
                    "Une perte immédiate de pression des pneus.",
                    "La reprise soudaine de la force du vent latéral (effet de gifle).",
                    "Un blocage automatique du différentiel.",
                    "Une accélération brutale du moteur."
                ],
                "reponse": "La reprise soudaine de la force du vent latéral (effet de gifle)."
            },
            {
                "id": 9,
                "topic": "Le sous-virage",
                "question": "Qu'est-ce que le phénomène de sous-virage pour un véhicule lourd ?",
                "choix": [
                    "Le train arrière qui glisse et veut passer devant.",
                    "Le véhicule qui refuse de tourner et tire tout droit vers l'extérieur du virage malgré les roues braquées.",
                    "Un virage effectué à une vitesse trop faible.",
                    "Un problème mécanique lié à la boîte de vitesses."
                ],
                "reponse": "Le véhicule qui refuse de tourner et tire tout droit vers l'extérieur du virage malgré les roues braquées."
            },
            {
                "id": 10,
                "topic": "État de la chaussée et freinage",
                "question": "Sur une chaussée mouillée ou glissante, par combien est généralement multipliée la distance de freinage d'un poids lourd ?",
                "choix": ["Par 1,5", "Par 2", "Par 3", "Par 4"],
                "reponse": "Par 2"
            }
        ]
    }

def charger_orale_permis_c_fiche_9():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 9 — Alcool, stupéfiants et médicaments.",
        "questions": [
            {
                "id": 1,
                "topic": "Seuil d'alcoolémie légal",
                "question": "Pour un conducteur de poids lourd en situation de conduite professionnelle, quel est le taux d'alcoolémie maximal autorisé dans le sang ?",
                "choix": [
                    "0,20 g/l de sang (soit 0,10 mg/l d'air expiré).",
                    "0,50 g/l de sang (soit 0,25 mg/l d'air expiré).",
                    "0,80 g/l de sang (soit 0,40 mg/l d'air expiré).",
                    "Le seuil est fixé à zéro absolu."
                ],
                "reponse": "0,50 g/l de sang (soit 0,25 mg/l d'air expiré)."
            },
            {
                "id": 2,
                "topic": "Alcoolémie délictuelle",
                "question": "À partir de quel taux d'alcool dans le sang la contravention se transforme-t-elle en délit routier ?",
                "choix": ["0,50 g/l", "0,80 g/l", "1,20 g/l", "2,00 g/l"],
                "reponse": "0,80 g/l"
            },
            {
                "id": 3,
                "topic": "Élimination de l'alcool",
                "question": "En moyenne, de combien baisse le taux d'alcool par heure chez un individu en bonne santé ?",
                "choix": [
                    "De 0,05 g/l à 0,10 g/l de sang par heure.",
                    "De 0,10 g/l à 0,15 g/l de sang par heure.",
                    "De 0,30 g/l de sang par heure.",
                    "L'élimination est instantanée si l'on boit du café chaud."
                ],
                "reponse": "De 0,10 g/l à 0,15 g/l de sang par heure."
            },
            {
                "id": 4,
                "topic": "Effet de l'alcool sur la vision",
                "question": "Quel est l'effet direct de l'alcool sur le champ visuel du conducteur ?",
                "choix": [
                    "Il élargit la vision périphérique.",
                    "Il rétrécit le champ visuel (effet tunnel) et altère la perception des distances.",
                    "Il améliore la vision nocturne.",
                    "Il n'a aucun impact sur les yeux."
                ],
                "reponse": "Il rétrécit le champ visuel (effet tunnel) et altère la perception des distances."
            },
            {
                "id": 5,
                "topic": "Dépistage des stupéfiants",
                "question": "Quel test est utilisé en premier lieu par les forces de l'ordre pour dépister la consommation de stupéfiants lors d'un contrôle ?",
                "choix": [
                    "Un test urinaire.",
                    "Un test salivaire.",
                    "Une prise de sang immédiate au bord de la route.",
                    "Un contrôle de la température corporelle."
                ],
                "reponse": "Un test salivaire."
            },
            {
                "id": 6,
                "topic": "Durée des effets du cannabis",
                "question": "Pourquoi la consommation de cannabis est-elle particulièrement traître pour la conduite d'un véhicule lourd ?",
                "choix": [
                    "Ses effets euphorisants ou somnolents peuvent persister plusieurs heures après la consommation, et le produit reste détectable longtemps.",
                    "Il fait accélérer le camion automatiquement.",
                    "Il nettoie les poumons du conducteur.",
                    "Les effets s'estompent au bout de 5 minutes seulement."
                ],
                "reponse": "Ses effets euphorisants ou somnolents peuvent persister plusieurs heures après la consommation, et le produit reste détectable longtemps."
            },
            {
                "id": 7,
                "topic": "Médicaments et conduite",
                "question": "Quel pictogramme de couleur rouge présent sur les boîtes de médicaments interdit strictement la conduite ?",
                "choix": [
                    "Niveau 1 — Soyez prudent.",
                    "Niveau 2 — Soyez très prudent.",
                    "Niveau 3 — Attention, danger : ne pas conduire. Demandez l'avis d'un médecin.",
                    "Aucun pictogramme n'interdit la conduite."
                ],
                "reponse": "Niveau 3 — Attention, danger : ne pas conduire. Demandez l'avis d'un médecin."
            },
            {
                "id": 8,
                "topic": "Sanction pour conduite sous stupéfiants",
                "question": "Quelle est la perte automatique de points sur le permis de conduire en cas de contrôle positif aux stupéfiants ou d'alcoolémie délictuelle ?",
                "choix": ["2 points", "4 points", "6 points", "Le permis est annulé à vie immédiatement sans retrait de points"],
                "reponse": "6 points"
            },
            {
                "id": 9,
                "topic": "Refus de se soumettre au contrôle",
                "question": "Que risque un conducteur de poids lourd qui refuse de se soumettre aux vérifications de l'état alcoolique ou de l'usage de stupéfiants ?",
                "choix": [
                    "Une simple amende de courtoisie.",
                    "Les mêmes sanctions pénales maximales que si le test était positif et délictuel (jusqu'à 2 ans d'emprisonnement et 4 500 € d'amende).",
                    "Rien, le contrôle est facultatif.",
                    "Uniquement un avertissement écrit de son entreprise."
                ],
                "reponse": "Les mêmes sanctions pénales maximales que si le test était positif et délictuel (jusqu'à 2 ans d'emprisonnement et 4 500 € d'amende)."
            },
            {
                "id": 10,
                "topic": "Éthylotest Anti-Démarrage (EAD)",
                "question": "Qu'est-ce qu'un système EAD (Éthylotest Anti-Démarrage) ?",
                "choix": [
                    "Un appareil qui mesure la vitesse du véhicule.",
                    "Un dispositif connecté au démarreur qui empêche le véhicule de démarrer si le taux d'alcool mesuré dans le souffle est supérieur au seuil programmé.",
                    "Un radar automatique de cabine.",
                    "Un système d'alerte pour la fatigue."
                ],
                "reponse": "Un dispositif connecté au démarreur qui empêche le véhicule de démarrer si le taux d'alcool mesuré dans le souffle est supérieur au seuil programmé."
            }
        ]
    }

def charger_orale_permis_c_fiche_10():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 10 — Angles morts.",
        "questions": [
            {
                "id": 1,
                "topic": "Nombre de zones d'angles morts",
                "question": "De combien de grandes zones d'angles morts principales un poids lourd standard (porteur) est-il entouré ?",
                "choix": ["1 seule zone (à l'arrière)", "2 zones (gauche et droite)", "4 zones principales (avant, arrière, côté gauche et côté droit)", "Aucune, les rétroviseurs couvrent tout"],
                "reponse": "4 zones principales (avant, arrière, côté gauche et côté droit)"
            },
            {
                "id": 2,
                "topic": "Signalisation obligatoire",
                "question": "Depuis 2021 en France, quelle obligation de signalisation s'applique aux véhicules de plus de 3,5 tonnes pour circuler en milieu urbain ?",
                "choix": [
                    "Une bande réfléchissante blanche tout autour de la caisse.",
                    "La pose de stickers ou plaques matérialisant la position des angles morts à l'arrière et sur les côtés du véhicule.",
                    "Un gyrophare orange allumé en permanence.",
                    "L'inscription du nom du conducteur sur la portière."
                ],
                "reponse": "La pose de stickers ou plaques matérialisant la position des angles morts à l'arrière et sur les côtés du véhicule."
            },
            {
                "id": 3,
                "topic": "Emplacement des stickers latéraux",
                "question": "Où doivent être positionnés les dispositifs de signalisation des angles morts sur les côtés d'un camion porteur ?",
                "choix": [
                    "Sur les vitres de la cabine uniquement.",
                    "Dans le premier mètre à partir de l'avant du véhicule (hors surfaces vitrées) à une hauteur comprise entre 0,90 m et 1,50 m du sol.",
                    "Au milieu exact de la carrosserie.",
                    "Tout en haut de la carrosserie pour être vus de loin."
                ],
                "reponse": "Dans le premier mètre à partir de l'avant du véhicule (hors surfaces vitrées) à une hauteur comprise entre 0,90 m et 1,50 m du sol."
            },
            {
                "id": 4,
                "topic": "L'angle mort avant",
                "question": "Pourquoi la zone située immédiatement devant la cabine d'un camion à cabine avancée constitue-t-elle un angle mort critique ?",
                "choix": [
                    "Parce que la hauteur du pare-brise empêche de voir un piéton de petite taille ou un deux-roues arrêté juste au ras du pare-chocs.",
                    "Parce que le moteur dégage trop de chaleur à cet endroit.",
                    "Parce que les essuie-glaces n'y passent pas.",
                    "Cette zone n'est pas un angle mort."
                ],
                "reponse": "Parce que la hauteur du pare-brise empêche de voir un piéton de petite taille ou un deux-roues arrêté juste au ras du pare-chocs."
            },
            {
                "id": 5,
                "topic": "Rétroviseurs spécifiques",
                "question": "Quel rétroviseur obligatoire, placé au-dessus du pare-brise côté passager, permet de surveiller l'angle mort situé juste au ras de l'avant du camion ?",
                "choix": ["Le rétroviseur grand angle", "Le rétroviseur de proximité (ou antéviseur)", "Le rétroviseur d'accostage", "Le rétroviseur intérieur standard"],
                "reponse": "Le rétroviseur de proximité (ou antéviseur)"
            },
            {
                "id": 6,
                "topic": "Le rétroviseur d'accostage",
                "question": "À quoi sert le rétroviseur d'accostage orienté vers le bas et placé au-dessus de la portière droite ?",
                "choix": [
                    "À vérifier la hauteur des ponts.",
                    "À surveiller la zone située le long du flanc droit de la cabine, notamment la roue avant droite et le trottoir.",
                    "À regarder les passagers à l'intérieur de la cabine.",
                    "À régler la trajectoire sur autoroute."
                ],
                "reponse": "À surveiller la zone située le long du flanc droit de la cabine, notamment la roue avant droite et le trottoir."
            },
            {
                "id": 7,
                "topic": "Le tourne-à-droite",
                "question": "Lors d'un changement de direction à droite en intersection, que devez-vous absolument faire pour sécuriser vos angles morts ?",
                "choix": [
                    "Klaxonner en continu en fermant les yeux.",
                    "Vérifier plusieurs fois vos rétroviseurs droits et votre vitre latérale droite pour détecter un deux-roues masqué qui remonterait par la droite.",
                    "Accélérer brusquement pour passer avant les piétons.",
                    "Regarder uniquement le rétroviseur gauche."
                ],
                "reponse": "Vérifier plusieurs fois vos rétroviseurs droits et votre vitre latérale droite pour détecter un deux-roues masqué qui remonterait par la droite."
            },
            {
                "id": 8,
                "topic": "Systèmes technologiques d'aide",
                "question": "Quel équipement technologique moderne, de plus en plus intégré aux véhicules lourds, alerte le conducteur par un signal visuel ou sonore de la présence d'un usager dans l'angle mort latéral ?",
                "choix": ["Le régulateur de vitesse", "Les systèmes de détection radar ou caméras d'angles morts (BSD / Blind Spot Detection)", "Le tachygraphe numérique", "L'alerte de franchissement de ligne"],
                "reponse": "Les systèmes de détection radar ou caméras d'angles morts (BSD / Blind Spot Detection)"
            },
            {
                "id": 9,
                "topic": "Angle mort arrière",
                "question": "Sur un camion frigorifique ou un fourgon tôlé sans vitres arrière, quelle est l'étendue de l'angle mort arrière ?",
                "choix": [
                    "Elle s'arrête à 1 mètre derrière le véhicule.",
                    "Elle s'étend sur toute la largeur de la caisse et sur plusieurs dizaines de mètres en profondeur, masquant totalement les véhicules qui suivent de près.",
                    "Il n'y a pas d'angle mort si l'on roule vite.",
                    "Elle est de 50 centimètres maximum."
                ],
                "reponse": "Elle s'étend sur toute la largeur de la caisse et sur plusieurs dizaines de mètres en profondeur, masquant totalement les véhicules qui suivent de près."
            },
            {
                "id": 10,
                "topic": "Manœuvre de marche arrière",
                "question": "En l'absence de caméra de recul fonctionnelle, quelle est la règle de sécurité la plus sûre pour effectuer une marche arrière dans une zone fréquentée ?",
                "choix": [
                    "Reculer le plus vite possible pour libérer la voie.",
                    "Se faire guider par une personne située à l'extérieur, placée hors de la trajectoire et visible dans les rétroviseurs.",
                    "Ouvrir la portière et regarder en arrière en tendant le bras.",
                    "Se fier uniquement à son instinct."
                ],
                "reponse": "Se faire guider par une personne située à l'extérieur, placée hors de la trajectoire et visible dans les rétroviseurs."
            }
        ]
    }

def charger_orale_permis_c_fiche_11():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 11 — Tunnels et voies ferrées / Passages à niveau.",
        "questions": [
            {
                "id": 1,
                "topic": "Gabarit et passage à niveau",
                "question": "Avant de franchir un passage à niveau, quelle caractéristique de votre poids lourd devez-vous impérativement vérifier par rapport aux panneaux de signalisation ?",
                "choix": [
                    "Le niveau de carburant.",
                    "La hauteur maximale (gabarit) et la garde au sol pour éviter de rester bloqué sur les voies.",
                    "La marque des pneumatiques.",
                    "La couleur de la carrosserie."
                ],
                "reponse": "La hauteur maximale (gabarit) et la garde au sol pour éviter de rester bloqué sur les voies."
            },
            {
                "id": 2,
                "topic": "Immobilisation sur voie ferrée",
                "question": "Si votre poids lourd se retrouve coincé sur une voie ferrée alors que les barrières commencent à se fermer, que devez-vous faire ?",
                "choix": [
                    "Descendre du camion et tenter de lever les barrières à la main.",
                    "Démarrer en première et enfoncer la barrière (conçue pour se casser) pour dégager immédiatement les voies.",
                    "Attendre l'arrivée du train en allumant les feux de détresse.",
                    "Tenter une manœuvre de marche arrière complexe."
                ],
                "reponse": "Démarrer en première et enfoncer la barrière (conçue pour se casser) pour dégager immédiatement les voies."
            },
            {
                "id": 3,
                "topic": "Signalisation du passage à niveau",
                "question": "Que signifie un feu rouge clignotant situé aux abords d'un passage à niveau ?",
                "choix": [
                    "Arrêt obligatoire et immédiat avant le signal.",
                    "Autorisation de passer avec prudence.",
                    "Ralentissement obligatoire uniquement.",
                    "Le passage à niveau est en panne."
                ],
                "reponse": "Arrêt obligatoire et immédiat avant le signal."
            },
            {
                "id": 4,
                "topic": "Distance entre deux passages à niveau",
                "question": "Pourquoi est-il interdit de s'engager sur un passage à niveau si la circulation est dense de l'autre côté ?",
                "choix": [
                    "Pour éviter de consommer trop de carburant au ralenti.",
                    "Parce que vous risquez de vous retrouver immobilisé sur la voie ferrée par la file de voitures devant vous.",
                    "Parce que le sol y est plus glissant.",
                    "C'est autorisé pour les poids lourds prioritaires."
                ],
                "reponse": "Parce que vous risquez de vous retrouver immobilisé sur la voie ferrée par la file de voitures devant vous."
            },
            {
                "id": 5,
                "topic": "Distance de sécurité en tunnel (à l'arrêt)",
                "question": "En cas d'arrêt forcé dû aux embouteillages à l'intérieur d'un tunnel, quelle distance minimale devez-vous maintenir avec le véhicule qui vous précède ?",
                "choix": ["1 mètre", "2 mètres", "5 mètres", "Au moins 10 mètres"],
                "reponse": "Au moins 10 mètres"
            },
            {
                "id": 6,
                "topic": "Balisage lumineux en tunnel",
                "question": "Que représentent les diodes bleues espacées régulièrement sur les parois d'un tunnel routier ?",
                "choix": [
                    "Une décoration pour le confort visuel.",
                    "Des repères de distance de sécurité en circulation (souvent maintenir 2 diodes d'écart avec le véhicule de devant).",
                    "La présence de radars de contrôle de vitesse.",
                    "L'emplacement des issues de secours uniquement."
                ],
                "reponse": "Des repères de distance de sécurité en circulation (souvent maintenir 2 diodes d'écart avec le véhicule de devant)."
            },
            {
                "id": 7,
                "topic": "Panne de véhicule sous un tunnel",
                "question": "Si votre camion tombe en panne sous un tunnel, où devez-vous tenter de l'immobiliser en priorité ?",
                "choix": [
                    "Au milieu exact de la chaussée.",
                    "Sur un emplacement d'arrêt d'urgence (refuge) ou le plus près possible du bord droit, puis couper le moteur.",
                    "Le plus près possible du bord gauche.",
                    "Devant une issue de secours en bloquant la porte."
                ],
                "reponse": "Sur un emplacement d'arrêt d'urgence (refuge) ou le plus près possible du bord droit, puis couper le moteur."
            },
            {
                "id": 8,
                "topic": "Alerte en tunnel",
                "question": "En cas d'urgence ou de panne dans un tunnel, quel moyen de communication est-il fortement recommandé d'utiliser plutôt que son téléphone portable ?",
                "choix": [
                    "La radio CB (Citizen Band).",
                    "Les niches de sécurité équipées d'un poste d'appel d'urgence (téléphone SOS).",
                    "Faire des signes par la fenêtre aux autres usagers.",
                    "Klaxonner en continu."
                ],
                "reponse": "Les niches de sécurité équipées d'un poste d'appel d'urgence (téléphone SOS)."
            },
            {
                "id": 9,
                "topic": "Éclairage obligatoire en tunnel",
                "question": "Quels feux devez-vous obligatoirement allumer avant de pénétrer dans un tunnel, même si celui-ci est parfaitement éclairé ?",
                "choix": ["Les feux de position seuls", "Les feux de croisement", "Les feux de route", "Les feux de brouillard arrière"],
                "reponse": "Les feux de croisement"
            },
            {
                "id": 10,
                "topic": "Franchissement profil surélevé",
                "question": "Quel panneau de danger spécifique peut annoncer un risque de blocage pour les remorques ou camions bas aux passages à niveau ?",
                "choix": [
                    "Le panneau de profil surélevé ou 'dos d'âne' (risque d'encastrement ou de toucher le sol).",
                    "Le panneau de virage à droite.",
                    "Le panneau de chaussée glissante.",
                    "Le panneau de rétrécissement de chaussée."
                ],
                "reponse": "Le panneau de profil surélevé ou 'dos d'âne' (risque d'encastrement ou de toucher le sol)."
            }
        ]
    }

def charger_orale_permis_c_fiche_12():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 12 — Aides à la conduite.",
        "questions": [
            {
                "id": 1,
                "topic": "Limiteur de vitesse obligatoire",
                "question": "En France, à quelle vitesse maximale absolue est bridé électroniquement le limiteur de vitesse obligatoire d'un camion porteur de plus de 3,5 tonnes (catégorie C) ?",
                "choix": ["80 km/h", "90 km/h", "100 km/h", "110 km/h"],
                "reponse": "90 km/h"
            },
            {
                "id": 2,
                "topic": "Régulateur de vitesse adaptatif (ACC)",
                "question": "Quelle est la fonction principale du régulateur de vitesse adaptatif (ACC) par rapport à un régulateur classique ?",
                "choix": [
                    "Il augmente automatiquement la puissance dans les côtes.",
                    "Il ajuste automatiquement la vitesse du camion pour maintenir une distance de sécurité constante avec le véhicule qui le précède.",
                    "Il empêche le camion de dépasser par la droite.",
                    "Il coupe le moteur en cas d'embouteillage."
                ],
                "reponse": "Il ajuste automatiquement la vitesse du camion pour maintenir une distance de sécurité constante avec le véhicule qui le précède."
            },
            {
                "id": 3,
                "topic": "Aide au Freinage d'Urgence (AEBS)",
                "question": "Qu'est-ce que le système AEBS (Advanced Emergency Braking System) désormais obligatoire sur les camions neufs ?",
                "choix": [
                    "Un système qui nettoie les disques de frein automatiquement.",
                    "Un dispositif radar/caméra qui détecte un risque de collision imminente et déclenche un freinage d'urgence automatique si le conducteur ne réagit pas.",
                    "Un ralentisseur hydraulique sur l'échappement.",
                    "Une alerte de pression des pneumatiques."
                ],
                "reponse": "Un dispositif radar/caméra qui détecte un risque de collision imminente et déclenche un freinage d'urgence automatique si le conducteur ne réagit pas."
            },
            {
                "id": 4,
                "topic": "Alerte de franchissement de ligne (LDWS)",
                "question": "Comment le système LDWS avertit-il le conducteur d'un écart de trajectoire involontaire sans activation du clignotant ?",
                "choix": [
                    "Par un signal sonore, une vibration dans le siège ou dans le volant du côté du franchissement.",
                    "En coupant les phares du véhicule.",
                    "En serrant automatiquement le frein de parc.",
                    "Par un message vocal envoyé à l'entreprise."
                ],
                "reponse": "Par un signal sonore, une vibration dans le siège ou dans le volant du côté du franchissement."
            },
            {
                "id": 5,
                "topic": "Aide au démarrage en côte",
                "question": "Quelle action le système d'aide au démarrage en côte effectue-t-il pour faciliter la manœuvre du conducteur ?",
                "choix": [
                    "Il augmente le régime moteur au maximum.",
                    "Il maintient la pression de freinage quelques secondes après le relâché de la pédale pour empêcher le camion de reculer.",
                    "Il enclenche les roues directrices arrière.",
                    "Il active automatiquement les feux de détresse."
                ],
                "reponse": "Il maintient la pression de freinage quelques secondes après le relâché de la pédale pour empêcher le camion de reculer."
            },
            {
                "id": 6,
                "topic": "Limites du système radar",
                "question": "Quelle condition climatique peut fortement perturber ou désactiver les capteurs radar et caméras des aides à la conduite ?",
                "choix": [
                    "Un grand soleil d'été sans nuages.",
                    "De fortes chutes de neige, une pluie torrentielle ou de la boue masquant les capteurs.",
                    "Un vent de dos modéré.",
                    "Une température extérieure de 20°C."
                ],
                "reponse": "De fortes chutes de neige, une pluie torrentielle ou de la boue masquant les capteurs."
            },
            {
                "id": 7,
                "topic": "Responsabilité du conducteur",
                "question": "Si un accident survient alors que le régulateur de vitesse adaptatif (ACC) était activé, qui est tenu pour responsable ?",
                "choix": [
                    "Le constructeur du camion.",
                    "Le conducteur, car les aides électroniques ne remplacent jamais la vigilance et le contrôle humain.",
                    "L'éditeur de la carte GPS.",
                    "Le véhicule qui précédait le camion."
                ],
                "reponse": "Le conducteur, car les aides électroniques ne remplacent jamais la vigilance et le contrôle humain."
            },
            {
                "id": 8,
                "topic": "Caméras de recul et rétrovision",
                "question": "Quel est l'avantage principal des systèmes de rétrovision par caméra (MirrorCam) remplaçant les rétroviseurs physiques ?",
                "choix": [
                    "Ils permettent de regarder des films pendant les pauses.",
                    "Ils suppriment une partie des angles morts, s'adaptent aux mouvements de la remorque et améliorent l'aérodynamisme.",
                    "Ils réduisent la hauteur du camion.",
                    "Ils suppriment l'obligation d'avoir un permis de conduire."
                ],
                "reponse": "Ils suppriment une partie des angles morts, s'adaptent aux mouvements de la remorque et améliorent l'aérodynamisme."
            },
            {
                "id": 9,
                "topic": "Système de surveillance de vigilance",
                "question": "Comment l'ordinateur de bord détecte-t-il une baisse de vigilance ou de la fatigue chez le conducteur ?",
                "choix": [
                    "En mesurant le poids du conducteur sur l'assise.",
                    "En analysant les micro-corrections anormales du volant et les trajectoires hésitantes via une caméra ou des capteurs directionnels.",
                    "En calculant le nombre d'arrêts de péage.",
                    "Le camion ne possède aucun moyen de détecter la fatigue."
                ],
                "reponse": "En analysant les micro-corrections anormales du volant et les trajectoires hésitantes via une caméra ou des capteurs directionnels."
            },
            {
                "id": 10,
                "topic": "Assistance à la conduite efficace",
                "question": "Pour une conduite économique et sécurisée (Éco-conduite), comment doit être utilisé le régulateur de vitesse ?",
                "choix": [
                    "De manière continue, même en agglomération dense ou sur route glissante.",
                    "Avec anticipation, en le désactivant à l'approche des zones complexes ou dangereuses (travaux, verglas, descente forte).",
                    "Uniquement lorsque le camion est en surcharge.",
                    "Jamais, il est interdit de l'utiliser en mission professionnelle."
                ],
                "reponse": "Avec anticipation, en le désactivant à l'approche des zones complexes ou dangereuses (travaux, verglas, descente forte)."
            }
        ]
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
    charger_orale_permis_c_fiche_12()
]

for index, fiche in enumerate(banque_ecrites_permis_c, start=1):
    if isinstance(fiche, list):
        for question in fiche:
            question["numero_fiche"] = index
    elif isinstance(fiche, dict):
        fiche["numero_fiche"] = index

# Indexation des Fiches Orales Permis C
for index, fiche in enumerate(banque_orales_permis_c, start=1):
    if isinstance(fiche, list):
        for question in fiche:
            question["numero_fiche"] = index
    elif isinstance(fiche, dict):
        fiche["numero_fiche"] = index
    
def charger_ecrite_permis_ce_fiche_1():
    return [
        {"type": "choix", "question": "Fiche CE 1 — Les accidents corporels entre un poids lourd et une voiture sont majoritairement des accidents avec des véhicules circulant dans le même sens. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 1 — Le non-respect des limitations de tonnage pour le passage sur les ponts peut-il entraîner une suspension du permis de conduire ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 1 — La rémunération mensuelle d'un conducteur salarié peut être calculée en fonction de la distance parcourue pendant le mois. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 1 — Parmi les types de graissage moteur, il existe le graissage par barbotage. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 1 — Quelle est la périodicité des visites techniques auxquelles sont soumis les véhicules de transport de marchandises de plus de 3,5 t de PTAC ?", "choix": [], "reponse": "12 mois ou 1 an"},
        {"type": "ecrite", "question": "Fiche CE 1 — Quel sera le poids maximal d'un ensemble composé de : Porteur PTRA: 44 t et PTAC: 26 t ; Remorque PTAC: 26 t et Poids à Vide: 7 t ?", "choix": [], "reponse": "44 t"},
        {"type": "ecrite", "question": "Fiche CE 1 — En cas de remorquage occasionnel, quelle est la vitesse maximale autorisée ?", "choix": [], "reponse": "25 km/h"},
        {"type": "choix", "question": "Fiche CE 1 — Ce signal (3.5m) interdit-il l'accès aux véhicules mesurant plus de 3,50 m de hauteur, chargement compris ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 1 — Vous rentrez chez vous le soir avec le camion de l'entreprise. Le matin, le temps de conduite pour vous rendre au dépôt est-il compté comme du temps de conduite ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 1 — Comment appelle-t-on le dispositif qui assure le freinage pratiquement simultané de tous les véhicules d'un ensemble ?", "choix": [], "reponse": "Le frein continu ou Le frein principal ou Le frein de service"}
    ]

def charger_ecrite_permis_ce_fiche_2():
    return [
        {"type": "choix", "question": "Fiche CE 2 — Un chiffre doublé (ex: 33) dans le rectangle du haut de la plaque orange placée à l'arrière d'un camion signifie : 'produit de nature à polluer les eaux'. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 2 — Des interdictions de circulation peuvent être mises en place pour les poids lourds lors des pics de pollution atmosphérique. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 2 — Vous conduisez sans vous arrêter depuis 8 h 40 ce matin. Il est 12 h 40. Etes-vous en infraction ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 2 — Une huile multigrade classée SAE 20 W 40 peut-être utilisée uniquement en hiver ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 2 — Suite au contrôle technique périodique, quelle lettre figure sur le certificat d'immatriculation lorsque le véhicule est accepté ?", "choix": [], "reponse": "A ou La lettre A"},
        {"type": "choix", "question": "Fiche CE 2 — Est-il possible d'atteler une remorque de 26 t de PTAC, chargée au maximum, derrière un camion de 19 t de PTAC, chargé au maximum, alors que le PTRA indiqué sur la plaque de poids et surface du camion est de 40 t ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 2 — Vous conduisez un camion de plus de 7,5 t de PTAC. Quand finit l'interdiction de circulation en fin de semaine ?", "choix": [], "reponse": "Dimanche à 22 h ou Dimanche à 10 h du soir"},
        {"type": "choix", "question": "Fiche CE 2 — Le poids indiqué dans ce signal (2.5t) concerne-t-il le poids maximal autorisé que peut supporter l'essieu ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 2 — Vous vous arrêtez pour faire le plein de carburant. Sur quel symbole devez-vous positionner le sélecteur d'activité du chronotachygraphe ?", "choix": [], "reponse": "Autres tâches, marteaux ou marteaux"},
        {"type": "choix", "question": "Fiche CE 2 — Existe-t-il des véhicules équipés de 2 ralentisseurs ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_3():
    return [
        {"type": "choix", "question": "Fiche CE 3 — Les accidents graves de poids lourds sont en majorité des accidents sans autre usager impliqué. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 3 — Vous conduisez votre véhicule personnel avec une alcoolémie de 1 g/l de sang. En cas de condamnation, votre permis poids lourds peut-il être annulé ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 3 — En double équipage, en France, vous êtes assis à côté du conducteur depuis 1 h. Pouvez-vous reprendre le volant ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 3 — Vous chargez du sable dans un véhicule isolé, quelle est la charge maximale autorisée sur l'essieu le plus chargé du groupe d'essieux moteur ?", "choix": [], "reponse": "11,5 t ou 11,500 t ou 11 t 500"},
        {"type": "choix", "question": "Fiche CE 3 — Mon véhicule a un poids à vide de 5 tonnes et un PTAC de 12 tonnes. Ce signal (5,5 t) me concerne-t-il ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 3 — Le contrôle et le remplissage du circuit de refroidissement s'effectuent plutôt moteur chaud ou moteur froid ?", "choix": [], "reponse": "Moteur à froid ou A froid."},
        {"type": "choix", "question": "Fiche CE 3 — Votre camion, en charge, transporte des denrées périssables, avez-vous le droit de continuer votre trajet le samedi après 22 h ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 3 — Pour effectuer un transport national, pouvez-vous laisser la plaque avec la mention 'TIR' visible à l'arrière de votre véhicule ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 3 — Sauf cas d'urgence, quelle est la durée de conduite maximale journalière autorisée en tenant compte des dérogations possibles ?", "choix": [], "reponse": "10 h ou 10 heures"},
        {"type": "ecrite", "question": "Fiche CE 3 — En règle générale, à quelle vitesse doit être réglé le limiteur de vitesse d'un tracteur routier neuf ?", "choix": [], "reponse": "90 km/h"}
    ]

def charger_ecrite_permis_ce_fiche_4():
    return [
        {"type": "choix", "question": "Fiche CE 4 — Ma remorque a un contour de sécurité arrière rétroréfléchissant de couleur rouge. En panne, je suis obligé de la laisser dételée sur la chaussée. Est-il obligatoire de placer le triangle de présignalisation ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 4 — Dans une entreprise, le chargement est effectué par un manutentionnaire. Une fois terminé, vous appartient-il d'effectuer le contrôle de l'arrimage avant de démarrer ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 4 — Au bout de combien de jours, au maximum, l'entreprise doit-elle 'télécharger' les données de votre carte conducteur ?", "choix": [], "reponse": "28 ou 28 jours"},
        {"type": "ecrite", "question": "Fiche CE 4 — Quelle est la longueur maximale autorisée d'un ensemble porte-voitures ?", "choix": [], "reponse": "20,35 m"},
        {"type": "ecrite", "question": "Fiche CE 4 — Comment s'appelle le document qui doit accompagner la marchandise lors de tout transport pour compte d'autrui ?", "choix": [], "reponse": "Lettre de voiture"},
        {"type": "ecrite", "question": "Fiche CE 4 — En règle générale, les véhicules lourds utilisent deux batteries de 12 volts montées en ... ?", "choix": [], "reponse": "Série"},
        {"type": "choix", "question": "Fiche CE 4 — Un pont dont la hauteur libre est de 5 m (au plus bas) sera obligatoirement signalé par un panneau de hauteur limitée. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 4 — Sur cette chaussée (Arbres inclinés), la hauteur des arbres est susceptible d'être inférieure à 4,30 m. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 4 — Vous avez fait une coupure de 2 h, quelle sera, au minimum, la durée (non réduite) de la période de repos que vous devrez prendre à la fin de votre journée de travail pour être en règle vis-à-vis du repos journalier ?", "choix": [], "reponse": "11 h ou 11 heures"},
        {"type": "choix", "question": "Fiche CE 4 — Dans un camion neuf, le passager doit-il obligatoirement attacher sa ceinture de sécurité ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]
def charger_ecrite_permis_ce_fiche_5():
    return [
        {"type": "choix", "question": "Fiche CE 5 — Le modèle français de constat amiable peut-il être utilisé dans les autres pays de l'Union européenne ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 5 — En transport public, le destinataire doit-il vérifier l'état apparent de la marchandise ou des colis au moment de l'livraison en présence du conducteur ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 5 — En règle générale, vous est-il possible de modifier les activités enregistrées par le chronotachygraphe sur votre carte ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 5 — Le châssis d'un véhicule lourd est principalement constitué de longerons et de ... ?", "choix": [], "reponse": "Traverses"},
        {"type": "choix", "question": "Fiche CE 5 — Cette limitation de vitesse (50) peut-elle concerner les véhicules autres que les trains routiers, trains doubles et véhicules articulés ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 5 — Est-il possible d'atteler une remorque de 19 t de PTAC, chargée au maximum, derrière un camion de 19 t de PTAC, chargé au maximum, alors que le PTRA indiqué sur la plaque de poids et surface du camion est de 40 t ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 5 — Vous conduisez un ensemble routier neuf de 40 t de PTRA. A quelle vitesse êtes-vous limité sur autoroute ?", "choix": [], "reponse": "90 km/h"},
        {"type": "ecrite", "question": "Fiche CE 5 — En transport public, à bord de votre véhicule, vous devez posséder l'original ou une copie conforme de la licence communautaire de transport ?", "choix": [], "reponse": "Une copie conforme"},
        {"type": "ecrite", "question": "Fiche CE 5 — En règle générale, quelle est la durée minimale normale (non réduite) de repos hebdomadaire pour un conducteur de camions ?", "choix": [], "reponse": "45 h"},
        {"type": "choix", "question": "Fiche CE 5 — Une semi-remorque dételée doit-elle être munie d'un extincteur en état de fonctionner ?", "choix": ["Oui", "Non"], "reponse": "Non"}
    ]

def charger_ecrite_permis_ce_fiche_6():
    return [
        {"type": "choix", "question": "Fiche CE 6 — En cas d'accident, les données du chronotachygraphe numérique peuvent-elles servir de preuve devant un tribunal ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 6 — Au-delà de quel taux de surcharge (en pourcentage - %) le camion pourra-t-il être immobilisé, jusqu'au déchargement de l'excédent ?", "choix": [], "reponse": "5 ou 5 % ou 5 pour cent"},
        {"type": "choix", "question": "Fiche CE 6 — Si, dans la même journée, vous conduisez un véhicule avec un chronotachygraphe numérique après avoir conduit un véhicule avec un chronotachygraphe à disque, devez-vous conserver le disque avec vous ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 6 — Certains éléments de la chaîne cinématique nécessitent d'être vidangés ou ... ?", "choix": [], "reponse": "Graissés"},
        {"type": "choix", "question": "Fiche CE 6 — Ce signal (interdiction de dépasser pour véhicules lourds) concerne-t-il uniquement les véhicules affectés au transport de marchandises excédant 3 500 kg de PTAC ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 6 — Je dois conduire un train routier de 32 t de PTRA dont la somme des PTAC est de 38 t. Quel doit être le poids maximum du train routier lors d'une pesée sur bascule ?", "choix": [], "reponse": "32 t"},
        {"type": "ecrite", "question": "Fiche CE 6 — Vous conduisez un tracteur solo de 19 t de PTAC et 38 t de PTRA. A quelle vitesse êtes-vous limité sur autoroute ?", "choix": [], "reponse": "90 km/h"},
        {"type": "choix", "question": "Fiche CE 6 — La lettre de voiture doit détailler la nature des marchandises transportées. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 6 — Quand le repos journalier est fractionné, quelle doit être la durée minimale totale de ce repos ?", "choix": [], "reponse": "12 h ou 12 heures"},
        {"type": "choix", "question": "Fiche CE 6 — Vous chargez du gravier. Vous voulez connaître la charge maximale autorisée par essieu, vous pouvez la trouver sur la plaque du constructeur. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"}
    ]

def charger_ecrite_permis_ce_fiche_7():
    return [
        {"type": "choix", "question": "Fiche CE 7 — Une plaque orange sans aucune inscription, placée à l'arrière d'un camion signifie qu'il s'agit d'un transport de matières dangereuses circulant à vide. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "ecrite", "question": "Fiche CE 7 — Quelle est la catégorie du permis exigée pour conduire un véhicule de transport en commun articulé comportant 60 places circulant à vide ?", "choix": [], "reponse": "D ou Le permis D"},
        {"type": "ecrite", "question": "Fiche CE 7 — Quelle est, en heures, la durée maximale autorisée de conduite par période de deux semaines consécutives ?", "choix": [], "reponse": "90 h"},
        {"type": "ecrite", "question": "Fiche CE 7 — Qu'aspire le moteur diesel lors du premier temps appelé « admission » ?", "choix": [], "reponse": "De l'air"},
        {"type": "ecrite", "question": "Fiche CE 7 — Lors de la mise en circulation d'un véhicule de transport de marchandises de plus de 3,5 t, vendu carrossé, quel est le délai maximal autorisé pour le présenter à la première visite technique ?", "choix": [], "reponse": "1 an ou 12 mois"},
        {"type": "ecrite", "question": "Fiche CE 7 — Quelle est la charge utile d'un véhicule dont le PTAC est de 26 t et le poids à vide de 7 t ?", "choix": [], "reponse": "19 t"},
        {"type": "ecrite", "question": "Fiche CE 7 — Je conduis un véhicule articulé de 38 t de PTRA pesant 14 t à vide. Pour emprunter une route où une barrière de dégel à 12 t avec mention demi-charge autorisée est en place, quel doit être le poids maximum de mon chargement ?", "choix": [], "reponse": "12 t ou 12 tonnes"},
        {"type": "choix", "question": "Fiche CE 7 — La descente dangereuse annoncée possède-t-elle un dénivelé de 100 mètres pour chaque kilomètre parcouru ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 7 — Vous avez interrompu votre conduite pendant 1 h 15 mn. Ce temps peut-il être pris en compte pour le calcul du temps de repos journalier ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 7 — Sur la plaque du constructeur d'un véhicule porteur-remorqueur, on trouve inscrite la longueur maximale de l'ensemble que l'on peut constituer avec ce véhicule. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"}
    ]

def charger_ecrite_permis_ce_fiche_8():
    return [
        {"type": "choix", "question": "Fiche CE 8 — Un X (ex: X362) inscrit à côté du nombre dans le rectangle du haut de la plaque orange placée à l'arrière d'un camion signifie : 'produit ayant une réaction dangereuse avec l'eau'. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 8 — À partir de quel âge la périodicité du contrôle médical obligatoire pour le renouvellement du permis de conduire catégories C ou CE est-elle de 2 ans ?", "choix": [], "reponse": "60 ans"},
        {"type": "choix", "question": "Fiche CE 8 — Un premier arrêt de 15 mn sur un parking peut-il être considéré comme une pause ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 8 — La somme des PTAC d'un train routier est de 45 t et son PTRA est de 40 t. Quel poids réel ne faut-il pas dépasser ?", "choix": [], "reponse": "40 t"},
        {"type": "ecrite", "question": "Fiche CE 8 — Ce signal concerne-t-il les véhicules affectés au transport de produits dangereux ou au transport de produits explosifs ?", "choix": [], "reponse": "Produits explosifs ou Explosifs"},
        {"type": "choix", "question": "Fiche CE 8 — Le turbocompresseur a pour fonction de diminuer l'air admis dans les cylindres ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 8 — Vous conduisez un tracteur solo de 19 t de PTAC et 38 t de PTRA. À quelle vitesse êtes-vous limité sur route à sens unique prioritaire ?", "choix": [], "reponse": "80 km/h"},
        {"type": "choix", "question": "Fiche CE 8 — Le transport de pièces de grande longueur qui dépassent d'1 mètre à l'avant du camion entre dans la catégorie des transports exceptionnels. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 8 — Un chauffeur a conduit 20 heures la semaine précédente. Selon la réglementation sociale européenne, combien d'heures maximum peut-il conduire la semaine en cours ?", "choix": [], "reponse": "56 h ou 56 heures"},
        {"type": "choix", "question": "Fiche CE 8 — L'extincteur prévu pour les semi-remorques peut être placé sur le tracteur. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"}
    ]
def charger_ecrite_permis_ce_fiche_9():
    return [
        {"type": "choix", "question": "Fiche CE 9 — En cas d'accident dans lequel votre véhicule est en cause, les forces de l'ordre peuvent-elles imprimer le ticket qui correspond à la journée en cours ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 9 — Après l'obtention du permis CE, un conducteur possédant le permis C et travaillant déjà dans une entreprise de transport doit-il suivre une formation complémentaire avant de conduire un véhicule articulé ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 9 — En double équipage, le temps passé sur la couchette d'un véhicule en circulation, est-il considéré comme repos journalier ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 9 — Quel sera le Poids Maximal Autorisé (PMA) pour le véhicule articulé suivant : Tracteur PTRA: 38 t et PV: 10 t ; Semi-remorque PTAC: 22 t et PV: 7 t ?", "choix": [], "reponse": "32 t"},
        {"type": "choix", "question": "Fiche CE 9 — La date limite de validité de la dernière visite technique est-elle inscrite sur le certificat d'immatriculation du véhicule ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 9 — Le circuit d'alimentation d'un moteur diesel se compose, entre autres éléments, de deux pompes : l'une est dite pompe d'injection haute pression, l'autre est dite pompe... ?", "choix": [], "reponse": "D'alimentation"},
        {"type": "ecrite", "question": "Fiche CE 9 — En cas de remorquage occasionnel d'un véhicule isolé de transport de marchandises, quelle est la longueur maximale autorisée de l'ensemble constitué ?", "choix": [], "reponse": "30 m"},
        {"type": "choix", "question": "Fiche CE 9 — Cette signalisation de présignalisation (Déviation 12t) peut annoncer une barrière de dégel : vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 9 — Le conducteur d'un camion de plus de 7,5 t effectuant une collecte de fruits est-il soumis à la réglementation sociale européenne ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 9 — Le principal avantage du système de freinage antibloquant est-il de réduire les distances de freinage ?", "choix": ["Oui", "Non"], "reponse": "Non"}
    ]

def charger_ecrite_permis_ce_fiche_10():
    return [
        {"type": "choix", "question": "Fiche CE 10 — Les accidents mortels entre un poids lourd et une voiture sont majoritairement des accidents avec des véhicules circulant dans le même sens. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 10 — Après un contrôle du poids, serez-vous passible d'une amende si la surcharge correspond à 4% (4 pour cent) du poids maximal autorisé ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 10 — Après 2 heures de conduite, quelle est la durée minimale d'un premier arrêt pouvant être pris en compte comme pause ?", "choix": [], "reponse": "15 mn"},
        {"type": "choix", "question": "Fiche CE 10 — Les filtres à carburant ou filtres principaux sont situés entre la pompe d'alimentation et la pompe d'injection haute pression. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 10 — Ce signal (Camion 10m) concerne-t-il uniquement les véhicules isolés ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 10 — Quel sera le Poids Maximal Autorisé (PMA) pour l'ensemble suivant : Porteur remorqueur PTRA: 44 t et PTAC: 26 t ; Remorque PTAC: 26 t et PV: 7 t ?", "choix": [], "reponse": "44 t"},
        {"type": "ecrite", "question": "Fiche CE 10 — Si les disques à l'arrière d'un camion (isolé), de 38 t de PTRA, sont '80 - 90', quels sont les disques placés à l'arrière de la remorque lorsque le train routier est formé ?", "choix": [], "reponse": "60 - 80 - 90"},
        {"type": "choix", "question": "Fiche CE 10 — Un véhicule qui circule sous le régime 'TIR' doit comporter un scellement effectué par la douane du pays d'origine. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 10 — Un chauffeur a conduit 40 heures la semaine précédente. Selon la réglementation sociale européenne, combien d'heures maximum peut-il conduire la semaine en cours ?", "choix": [], "reponse": "50 h ou 50 heures"},
        {"type": "choix", "question": "Fiche CE 10 — Ai-je le droit d'atteler une semi-remorque dont le type des pneumatiques est différent de celui du véhicule tracteur ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_11():
    return [
        {"type": "choix", "question": "Fiche CE 11 — Le constat amiable d'accident peut-il constituer une preuve de responsabilité ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 11 — Circuler avec un seul pneu lisse ou détérioré n'entraîne pas de contravention si le véhicule possède une roue de secours en bon état. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 11 — La rémunération mensuelle d'un conducteur salarié peut être calculée en fonction de la charge transportée pendant le mois. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "ecrite", "question": "Fiche CE 11 — Quel sera le Poids Maximal Autorisé (PMA) pour l'ensemble suivant : Porteur remorqueur PTRA: 44 t et PTAC: 26 t ; Remorque PTAC: 14 t et PV: 5 t ?", "choix": [], "reponse": "40 t"},
        {"type": "ecrite", "question": "Fiche CE 11 — Comment appelle-t-on les transports exécutés à titre onéreux pour le compte d'un client ?", "choix": [], "reponse": "Publics ou Compte d'autrui"},
        {"type": "choix", "question": "Fiche CE 11 — L'embrayage est un organe mécanique nécessaire au passage des vitesses sur les seules boîtes mécaniques ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 11 — Hors agglomération, sur une route à double sens, vous suivez un camion à 70 km/h. Quel intervalle de sécurité minimum devez-vous respecter ?", "choix": [], "reponse": "50 m"},
        {"type": "choix", "question": "Fiche CE 11 — Je circule avec un véhicule mesurant 2,30 m de large. A hauteur de ce signal (2.3m), puis-je continuer sur cette route ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 11 — En règle générale, quelle est la durée maximale de conduite journalière autorisée en respectant les temps de repos ?", "choix": [], "reponse": "9 h"},
        {"type": "choix", "question": "Fiche CE 11 — Le frein de rupture agit-il uniquement sur les roues du véhicule remorqué ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_12():
    return [
        {"type": "choix", "question": "Fiche CE 12 — Le modèle allemand, italien ou espagnol d'un constat européen d'accident, comporte-t-il les mêmes rubriques que le modèle français ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 12 — Débrancher ou modifier les réglages du limiteur de vitesse peut entraîner une suspension du permis de conduire, même s'il n'y a pas eu d'excès de vitesse constaté. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 12 — Le conducteur peut-il bâcher ou débâcher son véhicule pendant une pause ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 12 — Quel est le PTRA maximal d'un véhicule articulé comportant 4 essieux ?", "choix": [], "reponse": "38 t"},
        {"type": "choix", "question": "Fiche CE 12 — Ce signal m'annonce-t-il une voie de détresse qui sera située sur ma gauche ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 12 — La marche arrière sert à inverser le sens de rotation de l'arbre de transmission ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 12 — Sur une autoroute à 4 voies, un véhicule articulé de 15 m de long peut-il effectuer un dépassement en empruntant la 3ème voie ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 12 — Faut-il un seul certificat d'immatriculation pour un ensemble de véhicules constitué d'un camion de 26 t auquel on a attelé un compresseur sur roues de 800 kg ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 12 — En règle générale, quelle est la durée minimale normale (non réduite) obligatoire de repos journalier lorsque celui-ci n'est pas fractionné ?", "choix": [], "reponse": "11 h"},
        {"type": "ecrite", "question": "Fiche CE 12 — Si les disques à l'arrière du tracteur d'un véhicule articulé sont '60 - 80 - 90', quels sont les disques placés à l'arrière de la semi-remorque ?", "choix": [], "reponse": "60 - 80 - 90"}
    ]

def charger_ecrite_permis_ce_fiche_13():
    return [
        {"type": "choix", "question": "Fiche CE 13 — Dans une longue descente, en cas de rupture de freins, si j'utilisation une voie de détresse, le véhicule que je conduis sera-t-il gravement endommagé ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 13 — Je possède les catégories B - C et CE. Conduire ma voiture personnelle après avoir pris de la drogue peut entraîner la perte de la catégorie B de mon permis de conduire uniquement. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "ecrite", "question": "Fiche CE 13 — Quelle est la durée maximale autorisée de conduite continue pour un conducteur de camion ?", "choix": [], "reponse": "4 h 30 ou 4 h 30 mn"},
        {"type": "ecrite", "question": "Fiche CE 13 — Quelle est la majoration maximale autorisée du PTRA d'un véhicule articulé équipé de 2 dispositifs ralentisseurs : un de 600 kg sur le tracteur et un de 400 kg sur la remorque ?", "choix": [], "reponse": "500 kg"},
        {"type": "ecrite", "question": "Fiche CE 13 — Lors d'un contrôle des temps de conduite et de repos sur la route, en plus de la journée en cours, sur quelle période devez-vous pouvoir présenter les données ?", "choix": [], "reponse": "56 ou 56 jours"},
        {"type": "choix", "question": "Fiche CE 13 — Un pont court permet d'obtenir un couple plus important et une vitesse du véhicule plus faible. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 13 — Sur une autoroute à 3 voies, un véhicule articulé de 15 m de long peut-il effectuer un dépassement en empruntant la 2ème voie ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 13 — Je circule, à vide, avec un véhicule de 5 tonnes de poids à vide et de 15 tonnes de PTAC. A hauteur de ce signal (5.5t), puis-je passer ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 13 — Pouvez-vous prendre votre temps de repos en couchette lorsque le véhicule est à l'arrêt ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 13 — Le système de freinage électronique (EBS) contrôle la répartition du freinage entre le véhicule tracteur et la remorque qui en sont équipés ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_14():
    return [
        {"type": "ecrite", "question": "Fiche CE 14 — Pour diminuer les risques d'accident, lors de la montée ou de la descente d'un camion, de combien de points d'appui le conducteur doit-il se servir ?", "choix": [], "reponse": "3"},
        {"type": "choix", "question": "Fiche CE 14 — Lors d'un contrôle sur la route, est-il obligatoire de pouvoir présenter votre carte de qualification conducteur (CQC) ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 14 — Après 4 h 30 de conduite continue, quelle est la durée minimale de la pause que vous devez respecter ?", "choix": [], "reponse": "45 mn"},
        {"type": "choix", "question": "Fiche CE 14 — La longueur d'un véhicule articulé se calcule en additionnant la longueur du tracteur routier et la longueur de la semi-remorque. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 14 — Ce signal (mat. dangereuses) peut-il concerner les véhicules transportant une faible quantité de produits polluants ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 14 — Le mécanisme de l'assistance de direction comprend une « bielle pendante ». Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "ecrite", "question": "Fiche CE 14 — Vous conduisez un ensemble routier neuf de 40 t de PTRA. À quelle vitesse êtes-vous limité sur route à sens unique prioritaire ?", "choix": [], "reponse": "80 km/h"},
        {"type": "choix", "question": "Fiche CE 14 — Tout véhicule effectuant un transport international doit porter à l'arrière une plaque avec la mention 'TIR'. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 14 — L'amplitude de la journée de travail d'un conducteur routier comprend le temps de service et les pauses. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 14 — En général, un véhicule articulé neuf doit être équipé d'un extincteur à poudre de 6 kg placé à l'extérieur. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"}
    ]

def charger_ecrite_permis_ce_fiche_15():
    return [
        {"type": "choix", "question": "Fiche CE 15 — Les accidents corporels entre un poids lourd et une voiture se produisent en majorité dans les intersections. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "ecrite", "question": "Fiche CE 15 — Quelle est la périodicité des Formations Continues Obligatoires des conducteurs routiers ?", "choix": [], "reponse": "5 ans ou Quinquennale"},
        {"type": "choix", "question": "Fiche CE 15 — Après 3 h de conduite continue, s'arrêter 10 mn sur un parking est-il considéré comme une pause ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 15 — Quand j'attelle une semi-remorque porte-voitures à mon tracteur, quelle longueur ne doit pas dépasser le véhicule articulé ainsi constitué ?", "choix": [], "reponse": "16,50 m"},
        {"type": "ecrite", "question": "Fiche CE 15 — Combien de certificat(s) d'immatriculation est/sont attribué(s) à un véhicule articulé ?", "choix": [], "reponse": "2"},
        {"type": "ecrite", "question": "Fiche CE 15 — Quel type de suspension équipe généralement les véhicules lourds permettant de régler la hauteur du véhicule ?", "choix": [], "reponse": "La suspension pneumatique ou Pneumatique"},
        {"type": "ecrite", "question": "Fiche CE 15 — Le véhicule porteur-remorqueur d'un train routier a un PTRA de 38 t. Quelles sont les vitesses indiquées à l'arrière de la remorque ?", "choix": [], "reponse": "60-80-90 ou 60 km/h 80 km/h 90 km/h"},
        {"type": "choix", "question": "Fiche CE 15 — Ce signal (Voie bleue autobus) m'indique un arrêt d'autobus. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 15 — En double équipage, en France, vous êtes assis à côté du conducteur. Votre temps de conduite continue est-il interrompu ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 15 — En circulation, le fait de freiner désactive obligatoirement le régulateur de vitesse. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"}
    ]

def charger_ecrite_permis_ce_fiche_16():
    return [
        {"type": "ecrite", "question": "Fiche CE 16 — Quand je circule en Espagne, quel numéro de téléphone est-il conseillé d'utiliser pour appeler les secours à partir d'un portable ?", "choix": [], "reponse": "112"},
        {"type": "choix", "question": "Fiche CE 16 — Si je perds tous les points de mon permis de conduire à la suite d'infractions commises au volant de ma voiture personnelle, pourrai-je continuer à conduire mon camion ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 16 — Vous avez interrompu votre conduite pendant 45 mn. Ce temps peut-il être pris en compte pour le calcul du temps de repos journalier ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 16 — Mon camion de 20 t de PTAC est chargé au maximum. Son PTRA est de 40 t, si je dois atteler une remorque de 26 t de PTAC, quel doit être le poids réel maximal de la remorque ?", "choix": [], "reponse": "20 t"},
        {"type": "choix", "question": "Fiche CE 16 — Dans le cadre du transport public, peut-il y avoir une seule lettre de voiture (avec état récapitulatif) dans le véhicule pour un transport comportant plusieurs destinataires dans la même journée ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 16 — Le recreusage des pneumatiques est-il une opération qui peut s'effectuer uniquement par un spécialiste ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 16 — Vous conduisez un véhicule de 38 t de PTRA. En règle générale, quand débute l'interdiction de circulation en fin de semaine ?", "choix": [], "reponse": "Samedi à 22 h ou Samedi à 10 h du soir"},
        {"type": "choix", "question": "Fiche CE 16 — Ce signal (Silencieux orange) concerne-t-il les véhicules affectés aux seuls transports de produits polluants ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 16 — Votre véhicule est équipé d'un chronotachygraphe numérique. Vous avez perdu votre carte 'conducteur', combien de jours, au maximum, pouvez vous conduire sans carte ?", "choix": [], "reponse": "15 ou 15 jours"},
        {"type": "choix", "question": "Fiche CE 16 — Un dolly (ou diabolo) pesant 600 kg doit-il être immatriculé ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]
def charger_ecrite_permis_ce_fiche_17():
    return [
        {"type": "choix", "question": "Fiche CE 17 — En moyenne, il y a plus d'accidents graves impliquant un poids lourd les samedis et veilles de jours fériés que les jours de semaine. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 17 — Sur une route à double sens limitée à 70 km/h, lors d'un contrôle routier, votre carte conducteur indique que vous rouliez à 80 km/h. Pouvez-vous être sanctionné ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 17 — La réglementation sociale européenne s'applique-t-elle à un conducteur non salarié propriétaire de son véhicule ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 17 — Lorsque le conducteur serre le frein de parc, le cylindre de frein à ressort se remplit d'air. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "ecrite", "question": "Fiche CE 17 — Suite au contrôle technique périodique, lorsque le véhicule est refusé sans interdiction de circuler, dans quel délai maximum la contre-visite doit-elle être effectuée pour éviter une visite technique complète ?", "choix": [], "reponse": "1 mois"},
        {"type": "choix", "question": "Fiche CE 17 — Mon camion a un PTRA de 40 t et un PV de 10 t. Si le camion est vide, ai-je le droit d'atteler une remorque dont le poids réel est de 15 t ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 17 — Vous conduisez un véhicule articulé neuf de 38 t de PTRA. À quelle vitesse êtes-vous limité sur route non prioritaire ?", "choix": [], "reponse": "60 km/h"},
        {"type": "choix", "question": "Fiche CE 17 — Par temps sec, ce signal me concerne-t-il (Accotement meuble) ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 17 — Vous attendez votre tour pour décharger sans connaître le temps d'attente. Sur quel symbole devez-vous positionner le sélecteur d'activité du chronotachygraphe ?", "choix": [], "reponse": "Autres tâches, marteaux ou marteaux"},
        {"type": "choix", "question": "Fiche CE 17 — Les disques de limitation de vitesse apposés à l'arrière d'une semi-remorque sont-ils identiques à ceux du tracteur routier ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_18():
    return [
        {"type": "choix", "question": "Fiche CE 18 — Un X (ex: X83) inscrit à côté du nombre dans le rectangle du haut de la plaque orange placée à l'arrière d'un camion signifie : 'produit très inflammable'. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 18 — En cas de récidive de grand excès de vitesse, une suspension du permis de conduire peut être assortie d'un permis limité à la conduite professionnelle (permis blanc) si l'infraction a été commise avec la voiture personnelle du chauffeur. Vrai ou Faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 18 — Vous conduisez sans vous arrêter depuis 8 h ce matin. Il est 12 h 40. Etes-vous en infraction ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 18 — Le circuit de freinage européen rend le freinage de l'essieu avant indépendant du freinage de l'essieu arrière. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Vrai"},
        {"type": "choix", "question": "Fiche CE 18 — La licence de transport intérieur permet d'effectuer un transport avec un véhicule de 38 t à condition de rester en France. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 18 — Mon camion a un PTRA de 40 t et un PV de 10 t. Si le camion est vide, ai-je le droit d'atteler une remorque dont le poids réel est de 13 t ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 18 — Vous conduisez un véhicule articulé neuf de 38 t de PTRA. À quelle vitesse êtes-vous limité sur route prioritaire à chaussées séparées ?", "choix": [], "reponse": "80 km/h"},
        {"type": "choix", "question": "Fiche CE 18 — Ce signal interdit le dépassement à tous les véhicules dont le PTAC est supérieur à 3,5 tonnes ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 18 — Un chauffeur a conduit 50 heures la semaine précédente. Selon la réglementation sociale européenne, combien d'heures maximum peut-il conduire la semaine en cours ?", "choix": [], "reponse": "40 h ou 40 heures"},
        {"type": "choix", "question": "Fiche CE 18 — Le système de contrôle électronique de stabilité (ESP) agit principalement en virage ?", "choix": ["Oui", "Non"], "reponse": "Oui"}
    ]

def charger_ecrite_permis_ce_fiche_19():
    return [
        {"type": "choix", "question": "Fiche CE 19 — Dans le transport routier, c'est pendant le travail, hors conduite, que l'on dénombre le plus fort taux d'accidents chez les conducteurs ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 19 — Vous n'avez pas mis de carte dans le chronotachygraphe numérique, lors d'un contrôle sur route, sera-t-il possible de contrôler vos temps de conduite ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 19 — En double équipage, lorsque le véhicule est en circulation depuis plus de 45 minutes, le conducteur qui n'est pas au volant est-il considéré au repos ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 19 — Le dispositif antiblocage de roues (ABS) peut-il fonctionner en même temps que le ou les dispositifs ralentisseurs ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 19 — Suite au contrôle technique périodique, quelle lettre figure sur le certificat d'immatriculation lorsque le véhicule est refusé avec interdiction de circuler ?", "choix": [], "reponse": "R ou La lettre R"},
        {"type": "ecrite", "question": "Fiche CE 19 — Vous chargez du sable dans une semi-remorque, quelle peut-être la charge maximale autorisée sur l'essieu le plus chargé du groupe d'essieux arrière ?", "choix": [], "reponse": "10,5 t ou 10,500 t ou 10 t 500"},
        {"type": "ecrite", "question": "Fiche CE 19 — Je conduis un camion de 26 t de PTAC et de 10 t de PV. Pour emprunter une route où une barrière de dégel à 12 t avec mention demi-charge autorisée est en place, quel doit être le poids maximum de mon chargement ?", "choix": [], "reponse": "8 t ou 8 tonnes"},
        {"type": "choix", "question": "Fiche CE 19 — En agglomération, ce signal (giratoire) est-il implanté 50 mètres avant le carrefour à sens giratoire ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "ecrite", "question": "Fiche CE 19 — Vous avez fait une coupure de 4 h (repos), quelle sera, au minimum, la durée de la période de repos suivante pour être en règle vis-à-vis du repos journalier ?", "choix": [], "reponse": "9 h ou 9 heures"},
        {"type": "ecrite", "question": "Fiche CE 19 — En général, de combien d'extincteur(s) doit être équipé un véhicule articulé neuf ?", "choix": [], "reponse": "2"}
    ]

def charger_ecrite_permis_ce_fiche_20():
    return [
        {"type": "choix", "question": "Fiche CE 20 — En cas d'accident dans lequel votre véhicule est en cause, les forces de l'ordre peuvent-elles saisir votre carte 'conducteur' ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 20 — Votre permis porte la mention '01 : dispositif de correction et/ou de protection de la vision'. Avez-vous le droit de conduire sans porter de lunettes ou de lentilles ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "ecrite", "question": "Fiche CE 20 — Un temps de conduite de 4 h 30 peut être fractionné, au plus, par combien de pause(s) ?", "choix": [], "reponse": "2"},
        {"type": "ecrite", "question": "Fiche CE 20 — Vous conduisez un train-routier. Quelle peut être sa longueur maximale ?", "choix": [], "reponse": "18,75 m"},
        {"type": "ecrite", "question": "Fiche CE 20 — Comment appelle-t-on les transports exécutés à titre onéreux pour le compte d'un client ?", "choix": [], "reponse": "Publics ou Compte d'autrui"},
        {"type": "ecrite", "question": "Fiche CE 20 — En principe, le ralentisseur hydraulique est situé sur ... ?", "choix": [], "reponse": "La transmission ou L'arbre de transmission"},
        {"type": "choix", "question": "Fiche CE 20 — Un pont dont la hauteur libre est de 5 m (au plus bas) sera obligatoirement signalé par un panneau de hauteur limitée. Vrai ou faux ?", "choix": ["Vrai", "Faux"], "reponse": "Faux"},
        {"type": "choix", "question": "Fiche CE 20 — Hors agglomération, ce signal est-il implanté 100 mètres avant le carrefour à sens giratoire ?", "choix": ["Oui", "Non"], "reponse": "Non"},
        {"type": "choix", "question": "Fiche CE 20 — Vous conduisez un véhicule spécialisé de dépannage. Êtes-vous soumis à la réglementation sociale européenne concernant les temps de conduite et de repos si vous ramenez une voiture de Lille à Marseille ?", "choix": ["Oui", "Non"], "reponse": "Oui"},
        {"type": "choix", "question": "Fiche CE 20 — Les disques de limitation de vitesse apposés à l'arrière d'une remorque sont-ils identiques à ceux placés à l'arrière du camion ?", "choix": ["Oui", "Non"], "reponse": "Non"}
    ]



def charger_orale_permis_ce_fiche_1():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 1 (Permis CE) — Conduite et comportement.",
        "questions": [
            {
                "id": 1,
                "topic": "Trajectoire et articulation",
                "question": "Lors d'un virage serré, quel phénomène lié à l'articulation de l'ensemble (tracteur + semi-remorque) devez-vous surveiller dans vos rétroviseurs ?",
                "choix": [
                    "La semi-remorque qui se soulève du sol.",
                    "Le phénomène de coupure de trajectoire : les roues de la remorque passent beaucoup plus à l'intérieur du virage que le tracteur.",
                    "L'allongement automatique de la flèche d'attelage.",
                    "La remorque qui recule spontanément."
                ],
                "reponse": "Le phénomène de coupure de trajectoire : les roues de la remorque passent beaucoup plus à l'intérieur du virage que le tracteur."
            },
            {
                "id": 2,
                "topic": "Risque de mise en portefeuille",
                "question": "Qu'est-ce que le phénomène de 'mise en portefeuille' spécifique aux ensembles de véhicules ?",
                "choix": [
                    "Le fait de perdre ses papiers et sa carte conducteur dans la cabine.",
                    "Un pliage brutal de l'articulation entre le tracteur et la remorque, souvent lors d'un freinage violent sur chaussée glissante.",
                    "Un rangement optimal des palettes à l'intérieur de la caisse.",
                    "Le blocage des portes arrière de la remorque."
                ],
                "reponse": "Un pliage brutal de l'articulation entre le tracteur et la remorque, souvent lors d'un freinage violent sur chaussée glissante."
            },
            {
                "id": 3,
                "topic": "Inertie et distance d'arrêt",
                "question": "Avec un ensemble CE pouvant atteindre un PTRA de 44 tonnes, comment évolue l'énergie cinétique à vide par rapport au véhicule chargé à bloc ?",
                "choix": [
                    "Elle reste identique car la vitesse est la même.",
                    "Elle est considérablement plus élevée lorsque l'ensemble est chargé, ce qui augmente fortement la distance de freinage.",
                    "Elle s'annule grâce aux ralentisseurs.",
                    "Elle est plus faible à charge qu'à vide."
                ],
                "reponse": "Elle est considérablement plus élevée lorsque l'ensemble est chargé, ce qui augmente fortement la distance de freinage."
            },
            {
                "id": 4,
                "topic": "Masse maximale (PTRA)",
                "question": "En France, quelle est la masse maximale totale autorisée (PTRA) standard pour un ensemble articulé comportant plus de 4 essieux (généralement 5 ou 6 essieux) ?",
                "choix": ["19 tonnes", "32 tonnes", "38 tonnes", "44 tonnes"],
                "reponse": "44 tonnes"
            },
            {
                "id": 5,
                "topic": "Angles morts de l'ensemble",
                "question": "Pourquoi l'angle mort droit est-il encore plus dangereux sur un ensemble CE (tracteur + semi) lors d'un changement de direction ?",
                "choix": [
                    "Parce que la longueur totale accentue la zone invisible et que l'alignement des rétroviseurs se brise dès que le tracteur commence à pivoter.",
                    "Parce que la remorque n'a pas de rétroviseurs.",
                    "Parce que le passager cache la vue.",
                    "Il n'y a pas de différence avec un porteur solo."
                ],
                "reponse": "Parce que la longueur totale accentue la zone invisible et que l'alignement des rétroviseurs se brise dès que le tracteur commence à pivoter."
            },
            {
                "id": 6,
                "topic": "Centre de gravité d'une semi-remorque",
                "question": "Quel est le danger principal en courbe si le chargement de votre semi-remorque a un centre de gravité très élevé ?",
                "choix": [
                    "Une usure prématurée des essuie-glaces.",
                    "Un risque majeur de basculement (renversement) latéral sous l'effet de la force centrifuge, même à vitesse modérée.",
                    "Une augmentation de la pression d'huile du moteur.",
                    "Le blocage du pivot d'attelage."
                ],
                "reponse": "Un risque majeur de basculement (renversement) latéral sous l'effet de la force centrifuge, même à vitesse modérée."
            },
            {
                "id": 7,
                "topic": "Le porte-à-faux arrière",
                "question": "Lorsqu'on tourne le volant à gauche avec une semi-remorque possédant un grand porte-à-faux arrière, que fait l'extrémité arrière de la remorque ?",
                "choix": [
                    "Elle se déporte vers la droite (phénomène de balayage extérieur).",
                    "Elle se déporte vers la gauche.",
                    "Elle reste parfaitement alignée sur l'axe de la route.",
                    "Elle s'abaisse vers le sol."
                ],
                "reponse": "Elle se déporte vers la droite (phénomène de balayage extérieur)."
            },
            {
                "id": 8,
                "topic": "Stabilité au vent latéral",
                "question": "Quel type d'ensemble CE est le plus sensible aux fortes rafales de vent latéral lorsqu'il circule à vide ?",
                "choix": [
                    "Une citerne de transport de carburant.",
                    "Un ensemble tracteur + semi-remorque fourgon de grand volume ou bâchée.",
                    "Un porte-engins surbaissé.",
                    "Le vent n'a aucun effet sur un ensemble à vide."
                ],
                "reponse": "Un ensemble tracteur + semi-remorque fourgon de grand volume ou bâchée."
            },
            {
                "id": 9,
                "topic": "Répartition de la charge (Report)",
                "question": "Lors du chargement d'une semi-remorque, pourquoi est-il crucial de positionner une partie du poids vers l'avant de la remorque ?",
                "choix": [
                    "Pour faire joli.",
                    "Pour assurer un report de charge suffisant sur la sellette du tracteur (pression sur le pivot) afin de garantir la motricité du train arrière du tracteur.",
                    "Pour alléger totalement les freins de la remorque.",
                    "Pour vider le réservoir plus vite."
                ],
                "reponse": "Pour assurer un report de charge suffisant sur la sellette du tracteur (pression sur le pivot) afin de garantir la motricité du train arrière du tracteur."
            },
            {
                "id": 10,
                "topic": "Inertie et descentes en montagne",
                "question": "En forte descente avec un ensemble de 44 tonnes, que se passe-t-il si vous sollicitez uniquement le frein de service (pédale) ?",
                "choix": [
                    "Le moteur s'arrête automatiquement.",
                    "Les freins surchauffent rapidement (fading), perdent toute efficacité et risquent de provoquer un incendie des pneumatiques.",
                    "La remorque se dételle toute seule.",
                    "Le camion consomme moins d'air comprimé."
                ],
                "reponse": "Les freins surchauffent rapidement (fading), perdent toute efficacité et risquent de provoquer un incendie des pneumatiques."
            }
        ]
    }

def charger_orale_permis_ce_fiche_2():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 2 (Permis CE) — Comportement en cas d'accident / Incendie.",
        "questions": [
            {
                "id": 1,
                "topic": "Première action — Règle P.A.S.",
                "question": "Quelle est la première action obligatoire de la règle P.A.S. lorsque votre ensemble routier arrive le premier sur les lieux d'un accident ?",
                "choix": [
                    "Alerter immédiatement le centre de secours.",
                    "Secourir les victimes au sol.",
                    "Protéger les lieux pour éviter un suraccident.",
                    "Faire signer un constat amiable aux conducteurs."
                ],
                "reponse": "Protéger les lieux pour éviter un suraccident."
            },
            {
                "id": 2,
                "topic": "Protection d'un ensemble articulé",
                "question": "En raison de la longueur de votre ensemble routier CE (jusqu'à 18,75 m), comment devez-vous utiliser vos feux pour protéger la zone de l'accident ?",
                "choix": [
                    "Allumer les feux de route (pleins phares) vers les accidentés.",
                    "Activer immédiatement les feux de détresse du tracteur et s'assurer que ceux de la remorque fonctionnent également.",
                    "Éteindre l'intégralité des feux pour économiser la batterie.",
                    "Allumer uniquement le plafonnier de la cabine."
                ],
                "reponse": "Activer immédiatement les feux de détresse du tracteur et s'assurer que ceux de la remorque fonctionnent également."
            },
            {
                "id": 3,
                "topic": "Alerte et signalisation matières dangereuses",
                "question": "Si votre semi-remorque transporte des marchandises et se retrouve impliquée dans un accident, quelle information cruciale devez-vous donner aux secours lors de l'alerte ?",
                "choix": [
                    "Le montant total de l'assurance de la remorque.",
                    "Le code de la route du pays d'origine.",
                    "La présence de plaques orange et les numéros d'identification de danger/matière s'il s'agit de marchandises dangereuses.",
                    "Le prénom du responsable de quai qui a chargé le camion."
                ],
                "reponse": "La présence de plaques orange et les numéros d'identification de danger/matière s'il s'agit de marchandises dangereuses."
            },
            {
                "id": 4,
                "topic": "Numéros d'urgence",
                "question": "Quel est le numéro de téléphone d'urgence unique européen à privilégier pour joindre gratuitement les secours depuis votre mobile ?",
                "choix": ["15", "17", "18", "112"],
                "reponse": "112"
            },
            {
                "id": 5,
                "topic": "Extincteurs obligatoires sur ensemble CE",
                "question": "En dehors des réglementations spécifiques (Matières dangereuses/ADR), quelle est la dotation minimale réglementaire en extincteurs à bord d'un ensemble articulé (Tracteur + Semi) ?",
                "choix": [
                    "Un seul petit extincteur de 2 kg en cabine.",
                    "Un extincteur pour la cabine et au moins un extincteur externe (généralement 6 kg à poudre) destiné à la remorque.",
                    "Aucun extincteur n'est obligatoire.",
                    "Un extincteur à eau de 50 litres."
                ],
                "reponse": "Un extincteur pour la cabine et au moins un extincteur externe (généralement 6 kg à poudre) destiné à la remorque."
            },
            {
                "id": 6,
                "topic": "Feu de pneumatique sur la remorque",
                "question": "Un blocage de frein sur l'essieu arrière de la semi-remorque provoque un début d'incendie sur un pneumatique. Quelle action mécanique devez-vous tenter si cela est encore possible sans danger ?",
                "choix": [
                    "Continuer à rouler le plus vite possible pour souffler les flammes.",
                    "Immobiliser l'ensemble en sécurité, dételer le tracteur et l'isoler à distance pour protéger la partie motrice.",
                    "Jeter du sable sur le pare-brise du tracteur.",
                    "Mettre le contact au point mort et attendre dans la cabine."
                ],
                "reponse": "Immobiliser l'ensemble en sécurité, dételer le tracteur et l'isoler à distance pour protéger la partie motrice."
            },
            {
                "id": 7,
                "topic": "Utilisation de l'extincteur sur le feu",
                "question": "Comment devez-vous projeter l'agent d'extinction d'un extincteur à poudre sur un début d'incendie ?",
                "choix": [
                    "Viser le haut des flammes pour couper la fumée.",
                    "Attaquer la base des flammes en se positionnant face au vent (le vent dans le dos).",
                    "Vider l'extincteur en l'air au-dessus de la cabine.",
                    "Secouer l'extincteur sans retirer la goupille."
                ],
                "reponse": "Attaquer la base des flammes en se positionnant face au vent (le vent dans le dos)."
            },
            {
                "id": 8,
                "topic": "Secourisme — Victime inconsciente",
                "question": "Sur les lieux de l'accident, une victime est inconsciente mais respire. Quelle action de secourisme devez-vous pratiquer en attendant les secours ?",
                "choix": [
                    "L'asseoir contre une roue de la remorque.",
                    "L'allonger sur le dos et lui donner à boire.",
                    "La placer en Position Latérale de Sécurité (PLS) pour libérer ses voies aériennes.",
                    "Lui pratiquer un massage cardiaque immédiat."
                ],
                "reponse": "La placer en Position Latérale de Sécurité (PLS) pour libérer ses voies aériennes."
            },
            {
                "id": 9,
                "topic": "Le constat amiable avec une remorque",
                "question": "Lors de la rédaction d'un constat amiable après un accident matériel impliquant votre ensemble CE, quel véhicule devez-vous déclarer en priorité dans la partie identification ?",
                "choix": [
                    "Uniquement le tracteur, la remorque n'étant qu'un accessoire.",
                    "Le tracteur ET la remorque (en mentionnant bien les deux numéros d'immatriculation différents).",
                    "Uniquement la remorque.",
                    "Aucun des deux, il faut remplir un constat par roue."
                ],
                "reponse": "Le tracteur ET la remorque (en mentionnant bien les deux numéros d'immatriculation différents)."
            },
            {
                "id": 10,
                "topic": "Délai de transmission de constat",
                "question": "Quel est le délai légal maximum pour faire parvenir votre constat amiable dument rempli à votre compagnie d'assurance (ou à votre entreprise) ?",
                "choix": ["24 heures", "48 heures", "5 jours ouvrés", "10 jours"],
                "reponse": "5 jours ouvrés"
            }
        ]
    }

def charger_orale_permis_ce_fiche_3():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 3 (Permis CE) — Conduite en conditions difficiles / Montagne.",
        "questions": [
            {
                "id": 1,
                "topic": "Priorité de passage en forte pente",
                "question": "Lors d'un croisement difficile sur une route de montagne à forte pente entre deux véhicules de catégories différentes (un autobus et votre ensemble articulé CE), quel véhicule doit s'arrêter le premier pour faciliter le passage ?",
                "choix": [
                    "L'autobus doit s'arrêter en premier.",
                    "L'ensemble articulé CE doit s'arrêter en premier.",
                    "Le véhicule qui monte doit obligatoirement s'arrêter.",
                    "Celui qui a la plus grande vitesse."
                ],
                "reponse": "L'ensemble articulé CE doit s'arrêter en premier."
            },
            {
                "id": 2,
                "topic": "Marche arrière obligatoire en pente",
                "question": "Sur une route étroite de montagne, si le croisement est impossible et qu'une marche arrière est indispensable, quel véhicule doit reculer lorsque l'un est un camion porteur isolé et l'autre est votre ensemble articulé CE ?",
                "choix": [
                    "L'ensemble articulé CE doit reculer, car il est plus lourd.",
                    "Le véhicule isolé (porteur) doit faire marche arrière.",
                    "Le véhicule qui descend doit toujours reculer, peu importe sa configuration.",
                    "Les deux conducteurs doivent tirer au sort."
                ],
                "reponse": "Le véhicule isolé (porteur) doit faire marche arrière."
            },
            {
                "id": 3,
                "topic": "Motricité et verglas / neige",
                "question": "En hiver sur une route enneigée, quel est le risque principal pour le tracteur routier lors du démarrage en côte avec une semi-remorque fortement chargée à l'arrière ?",
                "choix": [
                    "Une baisse de pression du système de freinage.",
                    "Le patinage des roues motrices du tracteur par manque d'adhérence (perte de motricité due à un délessement ou une mauvaise répartition de charge).",
                    "Le détachement automatique de la sellette d'attelage.",
                    "Un emballement immédiat du moteur."
                ],
                "reponse": "Le patinage des roues motrices du tracteur par manque d'adhérence (perte de motricité due à un délessement ou une mauvaise répartition de charge)."
            },
            {
                "id": 4,
                "topic": "Utilisation du blocage de différentiel",
                "question": "Dans quelle situation précise devez-vous activer le blocage de différentiel sur l'essieu moteur de votre tracteur ?",
                "choix": [
                    "À haute vitesse sur l'autoroute sous une forte pluie.",
                    "Uniquement à très faible vitesse ou à l'arrêt, pour vous dégager d'une zone glissante (boue, neige, verglas) en ligne droite.",
                    "Dans tous les virages serrés en montagne.",
                    "Lors de chaque manœuvre de mise à quai."
                ],
                "reponse": "Uniquement à très faible vitesse ou à l'arrêt, pour vous dégager d'une zone glissante (boue, neige, verglas) en ligne droite."
            },
            {
                "id": 5,
                "topic": "Risque des ralentisseurs sur sol glissant",
                "question": "Pourquoi l'utilisation intensive d'un ralentisseur auxiliaire puissant (hydraulique ou électromagnétique) est-elle dangereuse sur route verglacée avec un ensemble CE ?",
                "choix": [
                    "Elle peut provoquer un blocage des roues motrices du tracteur, entraînant une perte de contrôle ou une mise en portefeuille rapide de l'ensemble.",
                    "Elle fait fondre instantanément les plaquettes de frein.",
                    "Elle désactive automatiquement le système ABS.",
                    "Elle coupe l'alimentation en air comprimé de la remorque."
                ],
                "reponse": "Elle peut provoquer un blocage des roues motrices du tracteur, entraînant une perte de contrôle ou une mise en portefeuille rapide de l'ensemble."
            },
            {
                "id": 6,
                "topic": "Loi Montagne et équipements",
                "question": "En période hivernale dans les zones soumises à la loi Montagne, quelles sont les obligations d'équipement pour un ensemble articulé CE si vous n'avez pas de pneus hiver ?",
                "choix": [
                    "Disposer de chaînes à neige métalliques amovibles permettant d'équiper au moins deux roues motrices.",
                    "Avoir des pneus lisses pour mieux glisser.",
                    "Transporter un sac de sel de 50 kg en cabine.",
                    "L'utilisation de chaînes est interdite sur les ensembles articulés."
                ],
                "reponse": "Disposer de chaînes à neige métalliques amovibles permettant d'équiper au moins deux roues motrices."
            },
            {
                "id": 7,
                "topic": "Vitesse sous la pluie (PTRA > 12t)",
                "question": "Sur autoroute, par temps de pluie, quelle est la vitesse maximale autorisée pour un ensemble articulé CE dont le PTRA est supérieur à 12 tonnes ?",
                "choix": ["90 km/h", "80 km/h", "70 km/h", "60 km/h"],
                "reponse": "80 km/h"
            },
            {
                "id": 8,
                "topic": "Gestion de la vitesse en longue descente",
                "question": "Pour aborder une longue et forte descente en montagne avec un ensemble de 44 tonnes, quelle est la règle d'or pour préserver vos freins de service ?",
                "choix": [
                    "Engager un rapport de vitesse élevé et freiner par de longs appuis continus.",
                    "Sélectionner un rapport de boîte court dès le sommet (frein moteur) et utiliser principalement les ralentisseurs auxiliaires.",
                    "Descendre au point mort pour laisser rouler l'ensemble librement.",
                    "Couper le moteur pour augmenter la résistance mécanique."
                ],
                "reponse": "Sélectionner un rapport de boîte court dès le sommet (frein moteur) et utiliser principalement les ralentisseurs auxiliaires."
            },
            {
                "id": 9,
                "topic": "Voie de détresse",
                "question": "Que devez-vous faire si, au milieu d'une descente de col, vous perdez totalement l'efficacité de vos freins (fading) et que vous apercevez un panneau à damier rouge et blanc ?",
                "choix": [
                    "Serrer immédiatement le frein de parc au maximum.",
                    "S'engager sur la voie de détresse pour immobiliser l'ensemble en sécurité dans le bac à gravier.",
                    "Tenter de dépasser tous les véhicules par la gauche.",
                    "Klaxonner et continuer sa trajectoire sur la route principale."
                ],
                "reponse": "S'engager sur la voie de détresse pour immobiliser l'ensemble en sécurité dans le bac à gravier."
            },
            {
                "id": 10,
                "topic": "Distance de sécurité en tunnel",
                "question": "Hors agglomération et sous les tunnels, quelle distance minimale de sécurité obligatoire devez-vous maintenir avec le véhicule qui vous précède si votre ensemble CE dépasse 3,5 tonnes ou 7 mètres de long ?",
                "choix": ["15 mètres", "30 mètres", "50 mètres", "100 mètres (ou 2 diodes bleues de balisage)"],
                "reponse": "100 mètres (ou 2 diodes bleues de balisage)"
            }
        ]
    }

def charger_orale_permis_ce_fiche_4():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 4 (Permis CE) — Gestes et postures / Ergonomie.",
        "questions": [
            {
                "id": 1,
                "topic": "Troubles Musculosquelettiques (TMS)",
                "question": "Quelles zones du corps des conducteurs routiers de l'ensemble CE sont les plus touchées par les Troubles Musculosquelettiques (TMS) dus aux postures prolongées et aux vibrations ?",
                "choix": [
                    "Les chevilles et les pieds uniquement.",
                    "La colonne vertébrale (région lombaire et cervicale) ainsi que les épaules.",
                    "Les poignets et les doigts uniquement.",
                    "Le système digestif."
                ],
                "reponse": "La colonne vertébrale (région lombaire et cervicale) ainsi que les épaules."
            },
            {
                "id": 2,
                "topic": "Manutention des béquilles de la semi-remorque",
                "question": "Lors du levage manuel des béquilles d'une semi-remorque chargée à l'aide de la manivelle, quelle est la bonne posture à adopter pour éviter les blessures au dos ?",
                "choix": [
                    "Garder les jambes tendues, se pencher en avant et forcer uniquement avec les bras.",
                    "Fléchir les genoux, garder le dos droit, se placer face à l'effort et utiliser le poids de son corps.",
                    "Tourner la manivelle le plus vite possible d'un seul bras en regardant ailleurs.",
                    "Faire une torsion brutale du tronc en fin de course."
                ],
                "reponse": "Fléchir les genoux, garder le dos droit, se placer face à l'effort et utiliser le poids de son corps."
            },
            {
                "id": 3,
                "topic": "Accès à la passerelle du tracteur",
                "question": "Quelle est la règle de sécurité absolue pour monter sur la passerelle située derrière la cabine afin de brancher les cordons (air, électricité) ?",
                "choix": [
                    "Sauter depuis le sol directement sur le châssis.",
                    "Utiliser les marches et poignées dédiées en respectant la règle des '3 points d'appui' (face au véhicule).",
                    "Prendre appui sur les flexibles d'air pour se hisser.",
                    "Monter en gardant les mains dans les poches."
                ],
                "reponse": "Utiliser les marches et poignées dédiées en respectant la règle des '3 points d'appui' (face au véhicule)."
            },
            {
                "id": 4,
                "topic": "Équipements de Protection Individuelle (EPI)",
                "question": "Quels Équipements de Protection Individuelle (EPI) sont indispensables lors des phases de décrochage, d'arrimage ou de manipulation des portes de la remorque ?",
                "choix": [
                    "Une veste imperméable simple.",
                    "Des gants de manutention et des chaussures de sécurité antidérapantes (avec coque de protection).",
                    "Un casque antibruit de chantier.",
                    "Des lunettes de protection teintées."
                ],
                "reponse": "Des gants de manutention et des chaussures de sécurité antidérapantes (avec coque de protection)."
            },
            {
                "id": 5,
                "topic": "Risque lié à l'ouverture des portes arrière",
                "question": "Quel geste de sécurité un conducteur de semi-remorque fourgon ou bâchée doit-il adopter lors de l'ouverture des portes arrière à destination ?",
                "choix": [
                    "Ouvrir les deux crémones d'un coup sec en restant bien au centre face aux portes.",
                    "S'ouvrir la voie en restant sur le côté pour éviter toute chute de marchandise mal arrimée qui aurait bougé pendant le transport.",
                    "Se suspendre aux barres de fermeture pour faire contrepoids.",
                    "Ouvrir les portes sans regarder à l'intérieur."
                ],
                "reponse": "S'ouvrir la voie en restant sur le côté pour éviter toute chute de marchandise mal arrimée qui aurait bougé pendant le transport."
            },
            {
                "id": 6,
                "topic": "Ergonomie du siège pneumatique",
                "question": "Pourquoi est-il indispensable de régler précisément la suspension du siège conducteur en fonction de son propre poids avant le départ ?",
                "choix": [
                    "Pour pouvoir toucher le plafond de la cabine.",
                    "Pour amortir efficacement les vibrations basse fréquence du châssis et préserver les disques intervertébraux.",
                    "Pour augmenter la vitesse maximale du véhicule.",
                    "Pour réduire le bruit du moteur à l'intérieur."
                ],
                "reponse": "Pour amortir efficacement les vibrations basse fréquence du châssis et préserver les disques intervertébraux."
            },
            {
                "id": 7,
                "topic": "Hygiène de vie — Alimentation et vigilance",
                "question": "Quel type de repas est fortement déconseillé avant une longue période de conduite de nuit pour éviter les coups de pompe et la somnolence ?",
                "choix": [
                    "Un repas léger à base de protéines et de légumes.",
                    "Un repas très copieux, riche en graisses et en sucres rapides.",
                    "Une simple hydratation régulière à l'eau plate.",
                    "La prise d'un fruit frais."
                ],
                "reponse": "Un repas très copieux, riche en graisses et en sucres rapides."
            },
            {
                "id": 8,
                "topic": "Symptômes de fatigue au volant",
                "question": "Quel est le premier signe physique d'alerte indiquant qu'un conducteur doit s'arrêter immédiatement pour faire une pause, bien avant la fin de ses 4h30 réglementaires ?",
                "choix": [
                    "Une sensation de faim légère.",
                    "Des picotements dans les yeux, des raideurs de la nuque et des fixations prolongées du regard.",
                    "Une envie de chanter.",
                    "Une augmentation de l'acuité visuelle nocturne."
                ],
                "reponse": "Des picotements dans les yeux, des raideurs de la nuque et des fixations prolongées du regard."
            },
            {
                "id": 9,
                "topic": "Descente de la cabine du tracteur",
                "question": "Quelle est la principale cause d'entorse de la cheville ou de fracture chez les conducteurs lors du retour à l'arrêt ?",
                "choix": [
                    "Le fait de tourner le volant trop vite.",
                    "Le fait de sauter directement de la cabine vers le sol au lieu de descendre à reculons face aux marches.",
                    "La manipulation de la carte chronotachygraphe.",
                    "Le serrage du frein de parc."
                ],
                "reponse": "Le fait de sauter directement de la cabine vers le sol au lieu de descendre à reculons face aux marches."
            },
            {
                "id": 10,
                "topic": "Manutention des barres de calage",
                "question": "Pour installer des barres de calage ou d'arrimage lourdes à l'intérieur de la semi-remorque, que doit privilégier le conducteur ?",
                "choix": [
                    "Travailler à bout de bras en étendant le dos au maximum.",
                    "Se rapprocher au plus près de la zone de fixation, garder un bon alignement du corps et verrouiller les bras près du tronc.",
                    "Utiliser une seule main en restant en équilibre sur une palette.",
                    "Forcer par des à-coups violents."
                ],
                "reponse": "Se rapprocher au plus près de la zone de fixation, garder un bon alignement du corps et verrouiller les bras près du tronc."
            }
        ]
    }

def charger_orale_permis_ce_fiche_5():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 5 (Permis CE) — Chargement.",
        "questions": [
            {
                "id": 1,
                "topic": "Calcul de la Charge Utile (CU)",
                "question": "Comment détermine-t-on la Charge Utile (CU) maximale qu'un ensemble articulé (tracteur + semi-remorque) peut transporter légalement ?",
                "choix": [
                    "PTRA de l'ensemble - Poids à Vide (PV) du tracteur seul.",
                    "PTRA (Poids Total Roulant Autorisé) - Somme des Poids à Vide (PV) du tracteur et de la semi-remorque.",
                    "PTAC de la semi-remorque + PTAC du tracteur.",
                    "Le poids maximal indiqué sur les pneus de la remorque."
                ],
                "reponse": "PTRA (Poids Total Roulant Autorisé) - Somme des Poids à Vide (PV) du tracteur et de la semi-remorque."
            },
            {
                "id": 2,
                "topic": "Poids réel et limites de circulation",
                "question": "Lors du transport de marchandises, quelle règle absolue concernant le poids réel de votre ensemble articulé devez-vous respecter en circulation ?",
                "choix": [
                    "Le poids réel ne doit jamais dépasser le PTAC du tracteur.",
                    "Le poids réel global ne doit jamais dépasser le PTRA (Poids Total Roulant Autorisé) inscrit sur la carte grise du tracteur, ni les limites réglementaires de la route (ex: 44t).",
                    "Le poids réel doit être identique à vide et en charge.",
                    "Il n'y a aucune limite de poids réel tant que la marchandise rentre dans la remorque."
                ],
                "reponse": "Le poids réel global ne doit jamais dépasser le PTRA (Poids Total Roulant Autorisé) inscrit sur la carte grise du tracteur, ni les limites réglementaires de la route (ex: 44t)."
            },
            {
                "id": 3,
                "topic": "Report de charge et motricité",
                "question": "Quel est l'objectif principal de positionner le chargement d'une semi-remorque de manière à appliquer une force verticale suffisante sur le pivot d'attelage (la sellette du tracteur) ?",
                "choix": [
                    "Permettre au tracteur de consommer moins d'adblue.",
                    "Garantir une adhérence et une motricité optimales des roues motrices du tracteur, tout en maintenant le guidage du train avant directeur.",
                    "Alléger totalement l'essieu arrière de la semi-remorque.",
                    "Empêcher les portes de la remorque de s'ouvrir."
                ],
                "reponse": "Garantir une adhérence et une motricité optimales des roues motrices du tracteur, tout en maintenant le guidage du train avant directeur."
            },
            {
                "id": 4,
                "topic": "Surcharge à l'essieu",
                "question": "En dehors du dépassement du PTRA global, quel autre type de surcharge liée à la répartition de la marchandise est sévèrement sanctionné sur un ensemble CE ?",
                "choix": [
                    "La surcharge sous un essieu isolé ou sous un groupe d'essieux (ex: le tridem arrière de la semi-remorque).",
                    "Le poids excessif des rétroviseurs extérieurs.",
                    "Le volume d'air consommé par les suspensions pneumatiques.",
                    "Le poids des sangles d'arrimage inutilisées."
                ],
                "reponse": "La surcharge sous un essieu isolé ou sous un groupe d'essieux (ex: le tridem arrière de la semi-remorque)."
            },
            {
                "id": 5,
                "topic": "Responsabilité pénale du chargement",
                "question": "Si un contrôle routier met en évidence un défaut d'arrimage majeur ou une surcharge de l'ensemble articulé en mouvement, qui est pénalement responsable ?",
                "choix": [
                    "Le cariste qui a conduit le transpalette au chargement.",
                    "Le conducteur de l'ensemble routier.",
                    "Le client final qui réceptionne la marchandise.",
                    "Le concessionnaire qui a vendu le tracteur."
                ],
                "reponse": "Le conducteur de l'ensemble routier."
            },
            {
                "id": 6,
                "topic": "Conséquence d'une charge trop en arrière",
                "question": "Quel est le risque si vous concentrez l'intégralité d'un chargement lourd à l'extrême arrière d'une semi-remorque ?",
                "choix": [
                    "Cela va faire lever les roues arrière de la remorque.",
                    "Cela déleste l'arrière du tracteur, réduit sa motricité et augmente considérablement le risque d'embardée, de lacet ou de mise en portefeuille.",
                    "Cela améliore le freinage du train avant.",
                    "Le moteur du tracteur va surchauffer instantanément."
                ],
                "reponse": "Cela déleste l'arrière du tracteur, réduit sa motricité et augmente considérablement le risque d'embardée, de lacet ou de mise en portefeuille."
            },
            {
                "id": 7,
                "topic": "Arrimage et forces d'inertie",
                "question": "Lors d'un freinage d'urgence avec un ensemble chargé à 44 tonnes, vers où se développent principalement les forces d'inertie de la marchandise ?",
                "choix": [
                    "Vers le haut, tendant à soulever le toit de la remorque.",
                    "Vers l'avant, poussant violemment contre la face avant de la remorque et vers le tracteur.",
                    "Vers l'arrière, tirant le camion vers l'arrière.",
                    "Les forces s'annulent automatiquement à cause de l'ABS."
                ],
                "reponse": "Vers l'avant, poussant violemment contre la face avant de la remorque et vers le tracteur."
            },
            {
                "id": 8,
                "topic": "Matériel d'arrimage réglementaire",
                "question": "Quel équipement mécanique équipé d'un tendeur à cliquet est le plus adapté pour arrimer solidement des machines lourdes ou des palettes sur le plateau d'une semi-remorque ?",
                "choix": [
                    "Des cordes en nylon classiques de scoutisme.",
                    "Des sangles d'arrimage textiles homologuées (portant une étiquette bleue indiquant la capacité LC) ou des chaînes d'arrimage.",
                    "Du ruban adhésif d'emballage renforcé.",
                    "Des sandows élastiques de coffre de voiture."
                ],
                "reponse": "Des sangles d'arrimage textiles homologuées (portant une étiquette bleue indiquant la capacité LC) ou des chaînes d'arrimage."
            },
            {
                "id": 9,
                "topic": "Effet de vagues (Citerne liquide)",
                "question": "Quel danger dynamique majeur présente la conduite d'une semi-remorque citerne transportant du liquide, si les compartiments (cuves) ne sont pas totalement remplis ?",
                "choix": [
                    "Le liquide va s'évaporer à cause de la vitesse.",
                    "L'effet de carène liquide (mouvement de vague du fluide) qui déplace brutalement la masse lors des virages ou freinages, risquant de coucher l'ensemble.",
                    "Une usure instantanée de la sellette d'attelage.",
                    "Le blocage du chronotachygraphe."
                ],
                "reponse": "L'effet de carène liquide (mouvement de vague du fluide) qui déplace brutalement la masse lors des virages ou freinages, risquant de coucher l'ensemble."
            },
            {
                "id": 10,
                "topic": "Utilisation des tapis antidérapants",
                "question": "Pourquoi place-t-on fréquemment des bandes de caoutchouc antidérapantes sous les palettes lourdes avant de les sangler ?",
                "choix": [
                    "Pour éviter de rayer le plancher en bois de la remorque.",
                    "Pour augmenter considérablement le coefficient de frottement (friction), réduisant ainsi le nombre de sangles nécessaires pour bloquer la charge.",
                    "Pour absorber les bruits de roulement à l'intérieur de la caisse.",
                    "Pour surélever la marchandise en cas d'infiltration d'eau."
                ],
                "reponse": "Pour augmenter considérablement le coefficient de frottement (friction), réduisant ainsi le nombre de sangles nécessaires pour bloquer la charge."
            }
        ]
    }

def charger_orale_permis_ce_fiche_6():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 6 (Permis CE) — Dépassement.",
        "questions": [
            {
                "id": 1,
                "topic": "Longueur et temps de manœuvre",
                "question": "En raison de la longueur maximale importante d'un ensemble articulé (jusqu'à 16,50 m pour une semi et 18,75 m pour un train routier), quel facteur lié au dépassement est considérablement augmenté par rapport à un porteur solo ?",
                "choix": [
                    "Le niveau d'huile du moteur.",
                    "Le temps de manœuvre et la distance nécessaire pour dépasser et se rabattre en toute sécurité.",
                    "L'acuité visuelle du conducteur.",
                    "La pression d'air dans les circuits de freinage."
                ],
                "reponse": "Le temps de manœuvre et la distance nécessaire pour dépasser et se rabattre en toute sécurité."
            },
            {
                "id": 2,
                "topic": "Réglementation sur autoroute à 3 voies",
                "question": "Sur une autoroute comportant 3 voies de circulation ou plus dans votre sens, quelles voies votre ensemble articulé CE de plus de 7 mètres de long a-t-il strictement l'interdiction d'emprunter ?",
                "choix": [
                    "La voie de droite.",
                    "La deuxième voie en partant de la droite.",
                    "Toutes les voies situées le plus à gauche au-delà des deux premières voies de droite.",
                    "L'interdiction ne concerne que la bande d'arrêt d'urgence."
                ],
                "reponse": "Toutes les voies situées le plus à gauche au-delà des deux premières voies de droite."
            },
            {
                "id": 3,
                "topic": "Panneau d'interdiction de dépasser (B3)",
                "question": "Que signifie le panneau d'interdiction de dépasser représentant une voiture noire à gauche et un camion rouge à droite pour un conducteur de permis CE ?",
                "choix": [
                    "Il interdit le dépassement à tous les véhicules de transport de marchandises de plus de 3,5 tonnes de PTAC (sauf dépassement de deux-roues sans side-car).",
                    "Il oblige les camions à doubler par la droite.",
                    "Il indique une zone de stationnement pour les remorques.",
                    "Il interdit aux voitures de doubler l'ensemble routier."
                ],
                "reponse": "Il interdit le dépassement à tous les véhicules de transport de marchandises de plus de 3,5 tonnes de PTAC (sauf dépassement de deux-roues sans side-car)."
            },
            {
                "id": 4,
                "topic": "Perturbation aérodynamique (Effet de souffle)",
                "question": "Lors du dépassement d'un usager vulnérable (cycliste, piéton, deux-roues motorisé), quel phénomène physique généré par la grande surface latérale de votre semi-remorque présente un risque majeur pour lui ?",
                "choix": [
                    "Un refroidissement brutal de l'air ambiant.",
                    "L'effet de souffle et d'aspiration aérodynamique qui peut déséquilibrer l'usager et le projeter sous les roues de la remorque.",
                    "Une augmentation instantanée de la friction de ses pneus.",
                    "Un déclenchement de son freinage d'urgence."
                ],
                "reponse": "L'effet de souffle et d'aspiration aérodynamique qui peut déséquilibrer l'usager et le projeter sous les roues de la remorque."
            },
            {
                "id": 5,
                "topic": "Distance latérale en agglomération",
                "question": "Quelle distance latérale minimale obligatoire devez-vous laisser entre le gabarit de votre ensemble routier et un cycliste ou un piéton lors d'un dépassement en agglomération ?",
                "choix": ["0,50 mètre", "1,00 mètre", "1,50 mètre", "2,00 mètres"],
                "reponse": "1,00 mètre"
            },
            {
                "id": 6,
                "topic": "Distance latérale hors agglomération",
                "question": "Quelle distance latérale minimale obligatoire devez-vous laisser lors du dépassement d'un cycliste, d'un piéton ou d'un cavalier sur une route hors agglomération ?",
                "choix": ["1,00 mètre", "1,20 mètre", "1,50 mètre", "2,50 mètres"],
                "reponse": "1,50 mètre"
            },
            {
                "id": 7,
                "topic": "Comportement du véhicule dépassé",
                "question": "Lorsqu'un autre véhicule (camion ou voiture) est en train de dépasser votre ensemble articulé, quelle est votre obligation réglementaire ?",
                "choix": [
                    "Accélérer pour ne pas perdre de temps sur votre planning.",
                    "Maintenir votre vitesse constante (et ne pas accélérer) ou ralentir légèrement si nécessaire pour faciliter sa manœuvre de rabattement.",
                    "Donner de grands coups de volant vers la gauche pour l'avertir.",
                    "Allumer immédiatement vos feux de brouillard arrière."
                ],
                "reponse": "Maintenir votre vitesse constante (et ne pas accélérer) ou ralentir légèrement si necéssaire pour faciliter sa manœuvre de rabattement."
            },
            {
                "id": 8,
                "topic": "Rabattement après dépassement",
                "question": "Avec un ensemble routier long, à quel moment pouvez-vous vous rabattre devant le véhicule que vous venez de dépasser sans risquer de lui couper la route ?",
                "choix": [
                    "Dès que vous pensez avoir dépassé sa position de 5 mètres.",
                    "Lorsque vous apercevez distinctement l'intégralité du véhicule dépassé (ses deux phares) dans votre rétroviseur principal droit et que la distance de sécurité est suffisante.",
                    "Dès que le véhicule dépassé active ses feux de détresse.",
                    "Immédiatement après avoir coupé la ligne blanche continue."
                ],
                "reponse": "Lorsque vous apercevez distinctement l'intégralité du véhicule dépassé (ses deux phares) dans votre rétroviseur principal droit et que la distance de sécurité est suffisante."
            },
            {
                "id": 9,
                "topic": "Dépassement aux intersections",
                "question": "Est-il autorisé de dépasser un véhicule à moteur à une intersection de routes où vous devez céder la priorité de passage (ex: priorité à droite ou cédez le passage) ?",
                "choix": [
                    "Oui, si l'ensemble routier est prioritaire par sa taille.",
                    "Non, le dépassement est strictement interdit aux intersections sauf si vous circulez sur une voie prioritaire signalée.",
                    "Oui, de nuit uniquement.",
                    "Oui, en utilisant l'avertisseur sonore de manière préventive."
                ],
                "reponse": "Non, le dépassement est strictement interdit aux intersections sauf si vous circulez sur une voie prioritaire signalée."
            },
            {
                "id": 10,
                "topic": "Dépassement d'engin de service hivernal",
                "question": "Avez-vous le droit de dépasser une saleuse ou un chasse-neige en cours de travail sur la chaussée (gyrophares bleus activés) ?",
                "choix": [
                    "Oui, si l'engin roule à moins de 20 km/h.",
                    "Non, il est strictement interdit de dépasser un engin de service hivernal en action avec ses avertisseurs spéciaux allumés.",
                    "Oui, uniquement par la droite si la bande d'arrêt d'urgence est libre.",
                    "Oui, mais uniquement sur le réseau autoroutier."
                ],
                "reponse": "Non, il est strictement interdit de dépasser un engin de service hivernal en action avec ses avertisseurs spéciaux allumés."
            }
        ]
    }

def charger_orale_permis_ce_fiche_7():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 7 (Permis CE) — Dynamique du véhicule.",
        "questions": [
            {
                "id": 1,
                "topic": "Force centrifuge et vitesse",
                "question": "Si vous doublez la vitesse de votre ensemble articulé en entrée de courbe (par exemple de 40 km/h à 80 km/h), par combien est multipliée la force centrifuge qui pousse la semi-remorque vers l'extérieur ?",
                "choix": ["Par 2", "Par 3", "Par 4", "Par 8"],
                "reponse": "Par 4"
            },
            {
                "id": 2,
                "topic": "Effet de lacet (Coup de raquette)",
                "question": "Qu'est-ce que l'effet de lacet (ou oscillation latérale) qui peut affecter une remorque ou une semi-remorque à haute vitesse ?",
                "choix": [
                    "Une usure rapide des plaquettes de frein.",
                    "Un mouvement d'oscillation de gauche à droite de la remorque qui s'amplifie et peut entraîner le renversement ou la mise en portefeuille.",
                    "Un blocage des suspensions pneumatiques.",
                    "Le détachement soudain de la remorque."
                ],
                "reponse": "Un mouvement d'oscillation de gauche à droite de la remorque qui s'amplifie et peut entraîner le renversement ou la mise en portefeuille."
            },
            {
                "id": 3,
                "topic": "Transfert de charge en virage",
                "question": "Quel est l'impact dynamique d'un centre de gravité très élevé du chargement de la semi-remorque lors de l'inscription en virage ?",
                "choix": [
                    "Il améliore l'adhérence des pneus intérieurs.",
                    "Il accentue le transfert de charge vers les roues extérieures, augmentant considérablement le risque de basculement.",
                    "Il réduit la distance de freinage de l'ensemble.",
                    "Il n'a aucune influence sur la trajectoire."
                ],
                "reponse": "Il accentue le transfert de charge vers les roues extérieures, augmentant considérablement le risque de basculement."
            },
            {
                "id": 4,
                "topic": "Adhérence et état de la route",
                "question": "Par temps de pluie, sur une chaussée mouillée, par combien est généralement multipliée la distance de freinage d'un ensemble articulé de 44 tonnes ?",
                "choix": ["Par 1,5", "Par 2", "Par 3", "Par 4"],
                "reponse": "Par 2"
            },
            {
                "id": 5,
                "topic": "Système anti-mise en portefeuille",
                "question": "Quel système d'assistance électronique moderne de la remorque (couplé à l'EBS) aide à stabiliser la trajectoire et à freiner automatiquement pour éviter le renversement ou la mise en portefeuille ?",
                "choix": ["L'ABS", "Le chronotachygraphe", "Le système de contrôle de stabilité (ESC / RSS)", "Le limiteur de vitesse"],
                "reponse": "Le système de contrôle de stabilité (ESC / RSS)"
            },
            {
                "id": 6,
                "topic": "Distance de réaction",
                "question": "De quoi dépend principalement la distance parcourue pendant le temps de réaction du conducteur lors d'un freinage d'urgence ?",
                "choix": [
                    "De l'état d'usure des freins de la remorque.",
                    "Uniquement de la vitesse du véhicule et de l'état physique/vigilance du conducteur.",
                    "Du poids total roulant autorisé (PTRA).",
                    "De la météo uniquement."
                ],
                "reponse": "Uniquement de la vitesse du véhicule et de l'état physique/vigilance du conducteur."
            },
            {
                "id": 7,
                "topic": "Calcul de la distance d'arrêt sur le sec",
                "question": "Sur chaussée sèche, quelle est la formule simplifiée pour estimer rapidement la distance d'arrêt totale (en mètres) d'un véhicule lourd ?",
                "choix": [
                    "Multiplier le chiffre des dizaines de la vitesse par lui-même (Vitesse au carré).",
                    "Multiplier la vitesse globale par 3.",
                    "Diviser la vitesse par le nombre d'essieux.",
                    "Multiplier le chiffre des dizaines de la vitesse par 3."
                ],
                "reponse": "Multiplier le chiffre des dizaines de la vitesse par lui-même (Vitesse au carré)."
            },
            {
                "id": 8,
                "topic": "Transfert de charge longitudinal",
                "question": "Lors d'un freinage violent avec un ensemble articulé, vers où se transfère la masse dynamique du véhicule ?",
                "choix": [
                    "Vers l'arrière de la semi-remorque.",
                    "Vers l'avant de l'ensemble, ce qui écrase l'essieu avant du tracteur et déleste son essieu arrière moteur.",
                    "Uniquement sur le côté gauche.",
                    "Le poids reste parfaitement réparti de manière identique."
                ],
                "reponse": "Vers l'avant de l'ensemble, ce qui écrase l'essieu avant du tracteur et déleste son essieu arrière moteur."
            },
            {
                "id": 9,
                "topic": "Risque lié au vent latéral sur ensemble à vide",
                "question": "Quel phénomène physique perturbe la trajectoire d'un ensemble tracteur + semi-remorque fourgon à vide lors du passage sur un viaduc exposé ?",
                "choix": [
                    "L'effet de vent latéral qui s'exerce sur la grande surface de la carrosserie vide (effet voile), risquant de déporter ou de coucher l'ensemble.",
                    "Une surchauffe immédiate des moyeux de roues.",
                    "Une baisse de l'efficacité des freins pneumatiques.",
                    "Le dégonflage automatique des boudins de suspension."
                ],
                "reponse": "L'effet de vent latéral qui s'exerce sur la grande surface de la carrosserie vide (effet voile), risquant de déporter ou de coucher l'ensemble."
            },
            {
                "id": 10,
                "topic": "Perte d'adhérence (Aquaplaning)",
                "question": "Quel facteur lié à un ensemble articulé circulant totalement à vide favorise le phénomène d'aquaplaning sur une chaussée fortement inondée ?",
                "choix": [
                    "Une pression au sol par centimètre carré des pneumatiques plus faible qu'à charge, empêchant l'évacuation efficace du film d'eau.",
                    "La hauteur de la cabine.",
                    "La température trop basse des disques de frein.",
                    "La longueur totale du train routier."
                ],
                "reponse": "Une pression au sol par centimètre carré des pneumatiques plus faible qu'à charge, empêchant l'évacuation efficace du film d'eau."
            }
        ]
    }

def charger_orale_permis_ce_fiche_8():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 8 (Permis CE) — Alcool, stupéfiants et médicaments.",
        "questions": [
            {
                "id": 1,
                "topic": "Seuil d'alcoolémie légal",
                "question": "En situation de conduite professionnelle avec un ensemble CE, quel est le taux maximal d'alcoolémie autorisé dans le sang avant d'être en infraction ?",
                "choix": [
                    "0,20 g/l de sang (soit 0,10 mg/l d'air expiré).",
                    "0,50 g/l de sang (soit 0,25 mg/l d'air expiré).",
                    "0,80 g/l de sang (soit 0,40 mg/l d'air expiré).",
                    "La tolérance est fixée à zéro absolu."
                ],
                "reponse": "0,50 g/l de sang (soit 0,25 mg/l d'air expiré)."
            },
            {
                "id": 2,
                "topic": "Alcoolémie délictuelle",
                "question": "À partir de quel taux d'alcool dans le sang l'infraction constatée devient-elle un délit routier passible du tribunal correctionnel ?",
                "choix": ["0,50 g/l", "0,80 g/l", "1,20 g/l", "2,00 g/l"],
                "reponse": "0,80 g/l"
            },
            {
                "id": 3,
                "topic": "Vitesse d'élimination de l'alcool",
                "question": "En moyenne, de combien baisse le taux d'alcool dans le sang par heure chez un individu en bonne santé ?",
                "choix": [
                    "De 0,05 g/l par heure.",
                    "De 0,10 g/l à 0,15 g/l par heure.",
                    "De 0,30 g/l par heure.",
                    "L'élimination est instantanée si l'on boit deux grands cafés noirs."
                ],
                "reponse": "De 0,10 g/l à 0,15 g/l par heure."
            },
            {
                "id": 4,
                "topic": "Rétrécissement du champ visuel",
                "question": "Quel est l'effet physiologique majeur de l'alcool sur la vision périphérique du conducteur routier ?",
                "choix": [
                    "Il élargit le champ de vision pour mieux voir les angles morts.",
                    "Il rétrécit le champ visuel (effet tunnel) et perturbe gravement la notion de distance et de relief.",
                    "Il supprime totalement le besoin de porter des lunettes de vue.",
                    "Il n'a aucun impact mesurable sur le système oculaire."
                ],
                "reponse": "Il rétrécit le champ visuel (effet tunnel) et perturbe gravement la notion de distance et de relief."
            },
            {
                "id": 5,
                "topic": "Dépistage des stupéfiants",
                "question": "Quelle méthode est utilisée en première intention par les forces de l'ordre pour détecter la consommation de stupéfiants ?",
                "choix": [
                    "Un éthylotest électronique.",
                    "Un test salivaire rapide pratiqué sur le bord de la route.",
                    "Une analyse d'urine obligatoire en cabine.",
                    "Une pesée du véhicule."
                ],
                "reponse": "Un test salivaire rapide pratiqué sur le bord de la route."
            },
            {
                "id": 6,
                "topic": "Effets du cannabis",
                "question": "Pourquoi la consommation de cannabis est-elle particulièrement dangereuse pour la manœuvre d'un véhicule articulé ?",
                "choix": [
                    "Elle allonge le temps de réaction, diminue la coordination des mouvements nécessaires aux manœuvres complexes et ses effets peuvent réapparaître plusieurs heures après.",
                    "Elle bloque le fonctionnement de la boîte de vitesses.",
                    "Elle nettoie le système pulmonaire du conducteur.",
                    "Les effets disparaissent totalement après 10 minutes."
                ],
                "reponse": "Elle allonge le temps de réaction, diminue la coordination des mouvements nécessaires aux manœuvres complexes et ses effets peuvent réapparaître plusieurs heures après."
            },
            {
                "id": 7,
                "topic": "Pictogrammes des médicaments",
                "question": "Quel pictogramme présent sur les boîtes de médicaments interdit strictement la conduite d'un véhicule à moteur sans l'avis impératif d'un médecin ?",
                "choix": [
                    "Le triangle jaune (Niveau 1).",
                    "Le triangle orange (Niveau 2).",
                    "Le triangle rouge (Niveau 3 — Attention, danger : ne pas conduire).",
                    "Aucun sticker n'a de valeur légale sur la route."
                ],
                "reponse": "Le triangle rouge (Niveau 3 — Attention, danger : ne pas conduire)."
            },
            {
                "id": 8,
                "topic": "Perte de points automatique",
                "question": "Combien de points sont retirés d'office sur le permis de conduire en cas de contrôle positif pour conduite sous l'empire de stupéfiants ou d'alcoolémie délictuelle ?",
                "choix": ["2 points", "4 points", "6 points", "Le permis est annulé à vie sans retrait de points."],
                "reponse": "6 points"
            },
            {
                "id": 9,
                "topic": "Refus de contrôle routier",
                "question": "Que risque un conducteur de super lourd qui refuse de se soumettre aux vérifications d'alcoolémie ou de stupéfiants ?",
                "choix": [
                    "Une simple contravention forfaitaire de 135 €.",
                    "Les mêmes peines maximales que pour un délit routier avéré (jusqu'à 2 ans de prison, 4 500 € d'amende et un retrait de 6 points).",
                    "Rien, car le dépistage nécessite l'accord signé du conducteur.",
                    "Uniquement un blâme interne de son entreprise."
                ],
                "reponse": "Les mêmes peines maximales que pour un délit routier avéré (jusqu'à 2 ans de prison, 4 500 € d'amende et un retrait de 6 points)."
            },
            {
                "id": 10,
                "topic": "Dispositif EAD (Éthylotest)",
                "question": "Qu'est-ce qu'un système EAD (Éthylotest Anti-Démarrage) ?",
                "choix": [
                    "Un radar de cabine mesurant la fatigue faciale.",
                    "Un appareil intégré au système de démarrage qui bloque l'allumage du moteur si le taux d'alcool analysé dans le souffle dépasse le seuil réglementaire.",
                    "Un enregistreur de vitesse relié au chronotachygraphe.",
                    "Un appareil permettant de purger l'air des freins de la remorque."
                ],
                "reponse": "Un appareil intégré au système de démarrage qui bloque l'allumage du moteur si le taux d'alcool analysé dans le souffle dépasse le seuil réglementaire."
            }
        ]
    }


def charger_orale_permis_ce_fiche_9():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 9 (Permis CE) — Éco-conduite et conduite citoyenne.",
        "questions": [
            {
                "id": 1,
                "topic": "Principe de base de l'éco-conduite",
                "question": "Quelle est la règle d'or pour pratiquer l'éco-conduite au volant d'un ensemble articulé de 44 tonnes ?",
                "choix": [
                    "Rouler le plus vite possible pour passer moins de temps sur la route.",
                    "L'anticipation, afin de maintenir une vitesse maximale constante et d'éviter les freinages et relances inutiles.",
                    "Rouler toujours en surrégime pour nettoyer le filtre à particules.",
                    "Couper le moteur dans toutes les descentes."
                ],
                "reponse": "L'anticipation, afin de maintenir une vitesse maximale constante et d'éviter les freinages et relances inutiles."
            },
            {
                "id": 2,
                "topic": "Zone verte du compte-tours",
                "question": "Qu'indique la zone verte présente sur le compte-tours de votre tracteur routier ?",
                "choix": [
                    "La zone où le moteur fait le moins de bruit.",
                    "La plage de régime moteur idéale où le couple est maximal et la consommation de carburant est la plus faible.",
                    "Le niveau de liquide de refroidissement restant.",
                    "La vitesse maximale autorisée pour le camion."
                ],
                "reponse": "La plage de régime moteur idéale où le couple est maximal et la consommation de carburant est la plus faible."
            },
            {
                "id": 3,
                "topic": "Utilisation de l'inertie",
                "question": "Comment le conducteur d'un ensemble CE peut-il exploiter intelligemment l'inertie de sa remorque chargée en approche d'un rond-point ?",
                "choix": [
                    "Accélérer jusqu'au dernier moment puis freiner violemment.",
                    "Lâcher la pédale d'accélérateur très en amont pour laisser rouler le véhicule sur son élan sans consommer de carburant (coupure d'injection).",
                    "Se mettre au point mort pour utiliser la roue libre.",
                    "Activer immédiatement le ralentisseur au maximum dès que le rond-point est en vue."
                ],
                "reponse": "Lâcher la pédale d'accélérateur très en amont pour laisser rouler le véhicule sur son élan sans consommer de carburant (coupure d'injection)."
            },
            {
                "id": 4,
                "topic": "Impact de la pression des pneus",
                "question": "Quelle est la conséquence directe de pneumatiques sous-gonflés sur l'ensemble articulé (tracteur et semi-remorque) ?",
                "choix": [
                    "Une baisse de la consommation de carburant.",
                    "Une augmentation de la résistance au roulement entraînant une hausse importante de la consommation et un risque accru d'éclatement.",
                    "Une meilleure adhérence sur sol verglacé.",
                    "Une réduction du niveau sonore de la remorque."
                ],
                "reponse": "Une augmentation de la résistance au roulement entraînant une hausse importante de la consommation et un risque accru d'éclatement."
            },
            {
                "id": 5,
                "topic": "Aérodynamisme de l'ensemble",
                "question": "Quel accessoire de carrosserie placé sur le toit de la cabine du tracteur permet de réduire considérablement la résistance à l'air et la consommation ?",
                "choix": [
                    "Les gyrophares.",
                    "Le déflecteur de toit (visière de toit réglée à la hauteur de la semi-remorque).",
                    "La rampe de phares longue portée.",
                    "Le pare-buffle avant."
                ],
                "reponse": "Le déflecteur de toit (visière de toit réglée à la hauteur de la semi-remorque)."
            },
            {
                "id": 6,
                "topic": "Le système d'éco-conduite prédictif",
                "question": "Sur un camion moderne, à quoi sert le régulateur de vitesse prédictif associé aux données GPS (ex: I-See, Predictive Powertrain Control) ?",
                "choix": [
                    "À détecter la fatigue du conducteur.",
                    "À analyser le relief de la route en amont (côtes, descentes) pour adapter automatiquement les rapports de boîte et optimiser la consommation.",
                    "À éviter les radars automatiques.",
                    "À téléguider le camion sur l'autoroute."
                ],
                "reponse": "À analyser le relief de la route en amont (côtes, descentes) pour adapter automatiquement les rapports de boîte et optimiser la consommation."
            },
            {
                "id": 7,
                "topic": "Arrêt prolongé du moteur",
                "question": "À partir de quelle durée d'immobilisation (ex: livraison, attente à quai) est-il recommandé de couper le moteur pour éviter le gaspillage de carburant et la pollution ?",
                "choix": ["Dès 10 à 20 secondes d'arrêt.", "Uniquement si l'arrêt dépasse 30 minutes.", "Jamais, un moteur de camion doit tourner en continu.", "Uniquement la nuit."],
                "reponse": "Dès 10 à 20 secondes d'arrêt."
            },
            {
                "id": 8,
                "topic": "Conduite citoyenne en agglomération",
                "question": "Pour respecter les riverains et faire preuve de citoyenneté lors de traversées de villages de nuit, quel équipement le conducteur doit-il utiliser avec modération ?",
                "choix": [
                    "L'avertisseur sonore.",
                    "Les ralentisseurs auxiliaires bruyants (notamment le frein sur échappement / frein moteur à décompression) au profit des freins ou ralentisseurs hydrauliques silencieux.",
                    "Les feux de position.",
                    "Le chronotachygraphe."
                ],
                "reponse": "Les ralentisseurs auxiliaires bruyants (notamment le frein sur échappement / frein moteur à décompression) au profit des freins ou ralentisseurs hydrauliques silencieux."
            },
            {
                "id": 9,
                "topic": "Traitement des gaz d'échappement (AdBlue)",
                "question": "Quel est le rôle du liquide AdBlue injecté dans le système d'échappement (SCR) des poids lourds modernes ?",
                "choix": [
                    "Nettoyer les injecteurs de carburant.",
                    "Transformer la majorité des oxydes d'azote (NOx) polluants en vapeur d'eau et en azote inoffensif.",
                    "Augmenter le couple moteur à bas régime.",
                    "Lubrifier les soupapes d'échappement."
                ],
                "reponse": "Transformer la majorité des oxydes d'azote (NOx) polluants en vapeur d'eau et en azote inoffensif."
            },
            {
                "id": 10,
                "topic": "Planification d'itinéraire",
                "question": "En quoi l'utilisation d'un GPS spécifique aux poids lourds participe-t-elle à une démarche éco-citoyenne ?",
                "choix": [
                    "Il permet de rouler au-dessus des limitations de vitesse.",
                    "Il évite les détours inutiles, les zones interdites aux tonnages lourds et le blocage sous des ponts inadaptés, réduisant ainsi le stress, le carburant et le risque d'accident.",
                    "Il calcule automatiquement le salaire de la journée.",
                    "Il sélectionne uniquement les routes gratuites."
                ],
                "reponse": "Il évite les détours inutiles, les zones interdites aux tonnages lourds et le blocage sous des ponts inadaptés, réduisant ainsi le stress, le carburant et le risque d'accident."
            }
        ]
    }

def charger_orale_permis_ce_fiche_10():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 10 (Permis CE) — Angles morts.",
        "questions": [
            {
                "id": 1,
                "topic": "Effet de l'articulation sur les angles morts",
                "question": "Lors d'un virage serré avec un ensemble articulé, que se passe-t-il au niveau de la vision dans vos rétroviseurs latéraux ?",
                "choix": [
                    "Le champ de vision s'élargit automatiquement.",
                    "L'alignement des rétroviseurs se brise en raison de l'angle de l'articulation, masquant une grande partie du flanc de la semi-remorque et agrandissant l'angle mort.",
                    "La visibilité arrière reste parfaitement identique à la ligne droite.",
                    "Les rétroviseurs se rabattent électroniquement."
                ],
                "reponse": "L'alignement des rétroviseurs se brise en raison de l'angle de l'articulation, masquant une grande partie du flanc de la semi-remorque et agrandissant l'angle mort."
            },
            {
                "id": 2,
                "topic": "Signalisation officielle des angles morts",
                "question": "Pour un ensemble articulé (Tracteur + Semi), combien de dispositifs de signalisation (stickers/plaques) 'Attention Angles Morts' doivent être apposés au minimum sur le véhicule ?",
                "choix": [
                    "1 seul à l'arrière du tracteur.",
                    "2 dispositifs (un de chaque côté de la cabine).",
                    "5 dispositifs (2 sur le tracteur à l'avant, 2 sur les côtés de la semi-remorque et 1 à l'arrière de la semi-remorque).",
                    "Aucun, l'obligation ne concerne que les autobus."
                ],
                "reponse": "5 dispositifs (2 sur le tracteur à l'avant, 2 sur les côtés de la semi-remorque et 1 à l'arrière de la semi-remorque)."
            },
            {
                "id": 3,
                "topic": "Positionnement sur la semi-remorque",
                "question": "Où doivent être placés les stickers latéraux d'angles morts sur une semi-remorque ?",
                "choix": [
                    "À l'extrême arrière de la remorque.",
                    "Dans le premier mètre à partir du pivot d'attelage (sellette), à gauche et à droite, à une hauteur comprise entre 0,90 m et 1,50 m du sol.",
                    "Au milieu exact des bâches ou des parois tôlées.",
                    "Sur les bavettes de protection des roues."
                ],
                "reponse": "Dans le premier mètre à partir du pivot d'attelage (sellette), à gauche et à droite, à une hauteur comprise entre 0,90 m et 1,50 m du sol."
            },
            {
                "id": 4,
                "topic": "L'angle mort avant (antéviseur)",
                "question": "Quel rétroviseur spécifique permet de voir un piéton ou un deux-roues arrêté immédiatement au ras du pare-chocs avant de la cabine ?",
                "choix": [
                    "Le grand angle gauche.",
                    "L'antéviseur (ou rétroviseur de proximité avant), obligatoire sur les cabines avancées.",
                    "Le rétroviseur intérieur classique.",
                    "Le rétroviseur de la remorque."
                ],
                "reponse": "L'antéviseur (ou rétroviseur de proximité avant), obligatoire sur les cabines avancées."
            },
            {
                "id": 5,
                "topic": "Le rétroviseur d'accostage",
                "question": "Où est situé le rétroviseur d'accostage et quel angle mort permet-il de contrôler ?",
                "choix": [
                    "Sur le toit, pour surveiller la hauteur des ponts.",
                    "Au-dessus de la portière droite, orienté vers le bas pour surveiller la zone le long de la roue avant droite et de la cabine.",
                    "À l'arrière de la remorque pour les marches arrière.",
                    "Sous le châssis pour surveiller la transmission."
                ],
                "reponse": "Au-dessus de la portière droite, orienté vers le bas pour surveiller la zone le long de la roue avant droite et de la cabine."
            },
            {
                "id": 6,
                "topic": "Manœuvre de tourne-à-droite",
                "question": "Pourquoi le changement de direction à droite en intersection urbaine est-il la manœuvre la plus dangereuse concernant les angles morts ?",
                "choix": [
                    "Parce que le camion roule trop vite à ce moment-là.",
                    "Parce que l'importante zone aveugle le long du flanc droit masque totalement les cyclistes ou trottinettes qui tenteraient de remonter la file par la droite.",
                    "Parce que les freins répondent moins bien à droite.",
                    "Parce que le clignotant droit consomme plus d'énergie."
                ],
                "reponse": "Parce que l'importante zone aveugle le long du flanc droit masque totalement les cyclistes ou trottinettes qui tenteraient de remonter la file par la droite."
            },
            {
                "id": 7,
                "topic": "Technologie d'assistance (BSD)",
                "question": "À quoi servent les systèmes modernes de détection latérale d'angles morts (Blind Spot Detection / Sideguard Assist) ?",
                "choix": [
                    "À filmer la route pour les assurances.",
                    "À alerter le conducteur par un signal visuel (LED sur le montant de cabine) ou sonore si un usager vulnérable se trouve dans l'angle mort lors d'un virage.",
                    "À diriger automatiquement les roues de la remorque.",
                    "À corriger la pression des pneus en roulant."
                ],
                "reponse": "À alerter le conducteur par un signal visuel (LED sur le montant de cabine) ou sonore si un usager vulnérable se trouve dans l'angle mort lors d'un virage."
            },
            {
                "id": 8,
                "topic": "Rétrovision par caméra (MirrorCam)",
                "question": "Quel avantage dynamique majeur présente le remplacement des rétroviseurs physiques par des caméras à écran sur les montants de la cabine ?",
                "choix": [
                    "Ils permettent de réduire le poids du tracteur de 500 kg.",
                    "L'image affichée pivote et suit automatiquement l'extrémité arrière de la semi-remorque lors des virages, réduisant fortement la perte visuelle due à la cassure.",
                    "Ils fonctionnent sans électricité.",
                    "Ils rendent le camion invisible aux radars."
                ],
                "reponse": "L'image affichée pivote et suit automatiquement l'extrémité arrière de la semi-remorque lors des virages, réduisant fortement la perte visuelle due à la cassure."
            },
            {
                "id": 9,
                "topic": "L'angle mort arrière de la semi-remorque",
                "question": "Sur une semi-remorque fourgon de 13,60 m de long, quelle est la particularité de l'angle mort arrière ?",
                "choix": [
                    "Il n'existe pas si le véhicule roule à plus de 80 km/h.",
                    "Il est totalement aveugle sur toute la largeur de la caisse et s'étend sur plusieurs dizaines de mètres, interdisant de voir un véhicule léger qui suit de trop près.",
                    "Il est comblé par le rétroviseur central de cabine.",
                    "Il fait moins de 50 centimètres."
                ],
                "reponse": "Il est totalement aveugle sur toute la largeur de la caisse et s'étend sur plusieurs dizaines de mètres, interdisant de voir un véhicule léger qui suit de trop près."
            },
            {
                "id": 10,
                "topic": "Marche arrière et sécurité",
                "question": "Lors d'une manœuvre complexe de mise à quai en marche arrière, quelle est la meilleure mesure de sécurité pour pallier l'absence totale de visibilité directe ?",
                "choix": [
                    "Reculer rapidement en klaxonnant de manière continue.",
                    "Ouvrir la portière gauche et regarder uniquement en arrière.",
                    "Descendre effectuer une reconnaissance à pied (tour du véhicule) et, si possible, se faire guider par une personne qualifiée visible dans les rétroviseurs.",
                    "Se fier uniquement aux capteurs de stationnement."
                ],
                "reponse": "Descendre effectuer une reconnaissance à pied (tour du véhicule) et, si possible, se faire guider par une personne qualifiée visible dans les rétroviseurs."
            }
        ]
    }

def charger_orale_permis_ce_fiche_11():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 11 (Permis CE) — Tunnels et voies ferrées / Passages à niveau.",
        "questions": [
            {
                "id": 1,
                "topic": "Risque de blocage sur voie ferrée",
                "question": "Quel risque spécifique au permis CE présente le franchissement d'un passage à niveau avec un profil surélevé (dos d'âne) si vous tractez une semi-remorque surbaissée ou un porte-engins ?",
                "choix": [
                    "Une baisse automatique de la pression des pneus.",
                    "Le risque d'encastrement ou de talonnage (la remorque touche le sol et immobilise l'ensemble sur les rails).",
                    "Le détachement spontané de la remorque.",
                    "Le déclenchement du limiteur de vitesse."
                ],
                "reponse": "Le risque d'encastrement ou de talonnage (la remorque touche le sol et immobilise l'ensemble sur les rails)."
            },
            {
                "id": 2,
                "topic": "Action en cas de barrières qui se ferment",
                "question": "Si votre ensemble articulé de grande longueur (jusqu'à 16,50 m) est engagé sur les voies ferrées et que les barrières commencent à se fermer, quelle doit être votre réaction immédiate ?",
                "choix": [
                    "Arrêter le véhicule, descendre et courir appeler la gare.",
                    "Démarrer fermement en avant pour casser la barrière (conçue pour cela) et dégager immédiatement la voie ferrée.",
                    "Tenter une marche arrière rapide.",
                    "Rester immobile en allumant ses feux de détresse."
                ],
                "reponse": "Démarrer fermement en avant pour casser la barrière (conçue pour cela) et dégager immédiatement la voie ferrée."
            },
            {
                "id": 3,
                "topic": "Distance de sécurité en circulation sous tunnel",
                "question": "En circulation normale à l'intérieur d'un tunnel, quelle distance de sécurité minimale obligatoire devez-vous maintenir avec l'usager qui vous précède avec votre ensemble routier ?",
                "choix": [
                    "20 mètres.",
                    "50 mètres.",
                    "Au moins 100 mètres (souvent matérialisé par 2 diodes de balisage bleues sur les parois).",
                    "La longueur de deux tracteurs solos."
                ],
                "reponse": "Au moins 100 mètres (souvent matérialisé par 2 diodes de balisage bleues sur les parois)."
            },
            {
                "id": 4,
                "topic": "Distance de sécurité à l'arrêt sous tunnel",
                "question": "Si la circulation s'interrompt (embouteillage) sous un tunnel, à quelle distance minimale devez-vous immobiliser votre ensemble CE derrière le véhicule précédent ?",
                "choix": [
                    "Au ras du pare-chocs pour gagner de la place.",
                    "2 mètres.",
                    "Au moins 5 mètres.",
                    "Au moins 10 mètres."
                ],
                "reponse": "Au moins 10 mètres."
            },
            {
                "id": 5,
                "topic": "Signalisation lumineuse de danger",
                "question": "Aux abords d'un passage à niveau ou d'un tunnel, que signifie l'activation d'un feu rouge clignotant unique ou de deux feux rouges alternatifs ?",
                "choix": [
                    "Une invitation à passer très prudemment.",
                    "Un arrêt obligatoire et immédiat pour l'ensemble des usagers.",
                    "Une simple zone de ralentissement pour cause de travaux.",
                    "L'annonce que le système électronique est en maintenance."
                ],
                "reponse": "Un arrêt obligatoire et immédiat pour l'ensemble des usagers."
            },
            {
                "id": 6,
                "topic": "Feux obligatoires sous tunnel",
                "question": "Quels feux d'éclairage devez-vous obligatoirement activer avant d'entrer dans un tunnel routier, même si celui-ci bénéficie d'un éclairage public parfait ?",
                "choix": [
                    "Les feux de position seuls.",
                    "Les feux de croisement (codes).",
                    "Les feux de route (pleins phares).",
                    "Les feux de brouillard avant et arrière."
                ],
                "reponse": "Les feux de croisement (codes)."
            },
            {
                "id": 7,
                "topic": "Procédure de panne sous un tunnel",
                "question": "Si votre ensemble articulé tombe en panne mécanique sous un tunnel et ne peut plus avancer, que devez-vous faire en priorité après avoir serré le frein de parc ?",
                "choix": [
                    "Attendre l'assistance à l'intérieur de la cabine.",
                    "Couper le moteur, actionner les feux de détresse, laisser les clés sur le contact et vous diriger à pied vers l'issue de secours la plus proche.",
                    "Dételer immédiatement la remorque au milieu de la voie.",
                    "Tenter de réparer le moteur sur la chaussée."
                ],
                "reponse": "Couper le moteur, actionner les feux de détresse, laisser les clés sur le contact et vous diriger à pied vers l'issue de secours la plus proche."
            },
            {
                "id": 8,
                "topic": "Moyens d'alerte sous tunnel",
                "question": "Pour signaler une panne ou un incident grave dans un tunnel, quel moyen de communication devez-vous utiliser en priorité ?",
                "choix": [
                    "Votre téléphone portable personnel.",
                    "Le poste d'appel d'urgence (téléphone SOS) situé dans une niche de sécurité pour être en contact direct avec le PC de surveillance du tunnel.",
                    "La radio CB de votre cabine.",
                    "Faire des appels de phares aux camions circulant en sens inverse."
                ],
                "reponse": "Le poste d'appel d'urgence (téléphone SOS) situé dans une niche de sécurité pour être en contact direct avec le PC de surveillance du tunnel."
            },
            {
                "id": 9,
                "topic": "Surcharge et gabarit en tunnel",
                "question": "Pourquoi est-il rigoureusement interdit de s'engager sous un tunnel si la hauteur de votre semi-remorque dépasse la limite indiquée (ex: panneau de danger de gabarit à 4,20 m) ?",
                "choix": [
                    "Cela risque d'augmenter la consommation de carburant.",
                    "Pour éviter l'arrachage des systèmes de ventilation, d'éclairage ou de sécurité du tunnel, pouvant provoquer un accident ou un incendie majeur.",
                    "Cela perturbe les ondes radio de la cabine.",
                    "Cela annule les garanties d'assurance de la marchandise."
                ],
                "reponse": "Pour éviter l'arrachage des systèmes de ventilation, d'éclairage ou de sécurité du tunnel, pouvant provoquer un accident ou un incendie majeur."
            },
            {
                "id": 10,
                "topic": "Interdiction d'engagement (Passage à niveau)",
                "question": "Quelle règle devez-vous appliquer avant d'engager le gabarit long de votre ensemble routier sur les voies d'un passage à niveau ?",
                "choix": [
                    "S'assurer que le réservoir de carburant est plein.",
                    "S'assurer que la voie est totalement libre devant et qu'il y a assez d'espace de l'autre côté des voies pour que l'intégralité de la remorque puisse dégager sans s'arrêter.",
                    "Passer à la vitesse maximale pour franchir les rails plus vite.",
                    "Klaxonner pour prévenir les agents de la gare ferroviaire."
                ],
                "reponse": "S'assurer que la voie est totalement libre devant et qu'il y a assez d'espace de l'autre côté des voies pour que l'intégralité de la remorque puisse dégager sans s'arrêter."
            }
        ]
    }

def charger_orale_permis_ce_fiche_12():
    return {
        "type": "ecrite",
        "titre": "Fiche Orale 12 (Permis CE) — Aides à la conduite.",
        "questions": [
            {
                "id": 1,
                "topic": "Limiteur de vitesse obligatoire",
                "question": "En France, à quelle vitesse maximale absolue est bridé électroniquement le limiteur de vitesse obligatoire d'un ensemble articulé de la catégorie CE (Super Lourd) ?",
                "choix": ["80 km/h", "90 km/h", "100 km/h", "110 km/h"],
                "reponse": "90 km/h"
            },
            {
                "id": 2,
                "topic": "Régulateur de vitesse adaptatif (ACC)",
                "question": "Quelle est l'utilité principale du régulateur de vitesse adaptatif (ACC) pour la sécurité d'un ensemble articulé sur autoroute ?",
                "choix": [
                    "Il augmente la puissance du moteur lors du dépassement.",
                    "Il ajuste automatiquement la vitesse et utilise les systèmes de freinage pour maintenir la distance de sécurité réglementaire avec l'usager qui précède.",
                    "Il empêche le camion de basculer dans les virages.",
                    "Il coupe le moteur lors des arrêts prolongés au péage."
                ],
                "reponse": "Il ajuste automatiquement la vitesse et utilise les systèmes de freinage pour maintenir la distance de sécurité réglementaire avec l'usager qui précède."
            },
            {
                "id": 3,
                "topic": "Aide au Freinage d'Urgence (AEBS)",
                "question": "Quel est le rôle du système de freinage d'urgence autonome (AEBS) obligatoire sur les tracteurs routiers neufs ?",
                "choix": [
                    "Nettoyer les freins à tambour de la remorque.",
                    "Détecter un risque de collision imminente par radar/caméra et déclencher automatiquement un freinage d'urgence si le conducteur ne réagit pas.",
                    "Remplacer entièrement le ralentisseur hydraulique.",
                    "Bloquer les portes arrière de la semi-remorque en côte."
                ],
                "reponse": "Détecter un risque de collision imminente par radar/caméra et déclencher automatiquement un freinage d'urgence si le conducteur ne réagit pas."
            },
            {
                "id": 4,
                "topic": "Alerte de franchissement de ligne (LDWS)",
                "question": "Comment le système LDWS alerte-t-il le conducteur de l'ensemble routier lors d'une déviation de trajectoire sans clignotant ?",
                "choix": [
                    "Par un signal sonore, une vibration dans le volant ou dans l'assise du siège du côté où le véhicule dévie.",
                    "En allumant automatiquement les feux de détresse de la remorque.",
                    "En réduisant instantanément le couple moteur de moitié.",
                    "En envoyant un rapport d'alerte par e-mail à l'entreprise."
                ],
                "reponse": "Par un signal sonore, une vibration dans le volant ou dans l'assise du siège du côté où le véhicule dévie."
            },
            {
                "id": 5,
                "topic": "Limites des capteurs (Radar/Caméra)",
                "question": "Quelles conditions climatiques peuvent perturber ou désactiver temporairement les caméras et radars d'aides à la conduite de votre tracteur ?",
                "choix": [
                    "Un temps sec avec une température clémente de 22°C.",
                    "De fortes chutes de neige, un brouillard givrant intense ou des projections de boue accumulées sur les capteurs.",
                    "Un vent arrière léger.",
                    "Une conduite prolongée en zone ensoleillée."
                ],
                "reponse": "De fortes chutes de neige, un brouillard givrant intense ou des projections de boue accumulées sur les capteurs."
            },
            {
                "id": 6,
                "topic": "Responsabilité pénale et électronique",
                "question": "En cas d'accident survenant alors qu'une aide à la conduite (comme l'ACC ou l'AEBS) était activée, qui est tenu légalement pour responsable ?",
                "choix": [
                    "Le constructeur du tracteur routier.",
                    "Le conducteur de l'ensemble routier, car l'électronique est une assistance et ne remplace jamais la vigilance humaine.",
                    "L'entreprise qui a conçu les logiciels embarqués.",
                    "Le concessionnaire qui effectue la maintenance."
                ],
                "reponse": "Le conducteur de l'ensemble routier, car l'électronique est une assistance et ne remplace jamais la vigilance humaine."
            },
            {
                "id": 7,
                "topic": "Systèmes MirrorCam (Rétrovision par caméra)",
                "question": "Quel est l'avantage principal des caméras remplaçant les rétroviseurs physiques sur les ensembles CE ?",
                "choix": [
                    "Elles permettent d'écouter la radio en haute définition.",
                    "Elles pivotent et adaptent automatiquement le cadrage de l'écran pour suivre l'extrémité arrière de la semi-remorque lors des virages, réduisant ainsi l'angle mort dû à la cassure.",
                    "Elles suppriment l'obligation d'avoir des plaques d'immatriculation.",
                    "Elles fonctionnent sans aucune source d'énergie électrique."
                ],
                "reponse": "Elles pivotent et adaptent automatiquement le cadrage de l'écran pour suivre l'extrémité arrière de la semi-remorque lors des virages, réduisant ainsi l'angle mort dû à la cassure."
            },
            {
                "id": 8,
                "topic": "Système d'aide au démarrage en côte",
                "question": "Comment l'assistance au démarrage en côte sécurise-t-elle la manœuvre d'un ensemble de 44 tonnes ?",
                "choix": [
                    "En augmentant le régime du moteur jusqu'à sa limite maximale.",
                    "En maintenant automatiquement la pression de freinage pendant 2 à 3 secondes après le relâché de la pédale, évitant ainsi le recul dangereux de la remorque.",
                    "En activant instantanément le blocage de différentiel.",
                    "En coupant l'alimentation pneumatique des suspensions."
                ],
                "reponse": "En maintenant automatiquement la pression de freinage pendant 2 à 3 secondes après le relâché de la pédale, évitant ainsi le recul dangereux de la remorque."
            },
            {
                "id": 9,
                "topic": "Détection de la somnolence",
                "question": "Sur quels paramètres l'ordinateur de bord se base-t-il principalement pour détecter une fatigue ou une perte d'attention du conducteur ?",
                "choix": [
                    "Le poids exercé par le conducteur sur le plancher de la cabine.",
                    "L'analyse des micro-corrections brutales sur le volant et les oscillations anormales de la trajectoire sur les lignes de voies.",
                    "La température interne de la cabine.",
                    "Le nombre de changements de rapports de vitesses."
                ],
                "reponse": "L'analyse des micro-corrections brutales sur le volant et les oscillations anormales de la trajectoire sur les lignes de voies."
            },
            {
                "id": 10,
                "topic": "Régulateur de vitesse et conditions météo",
                "question": "Dans quelle situation météorologique est-il fortement recommandé de désactiver le régulateur de vitesse (classique ou adaptatif ACC) ?",
                "choix": [
                    "Par une belle journée ensoleillée sur autoroute dégagée.",
                    "Sur chaussée glissante, par temps de verglas, de neige ou de forte pluie (risque de perte d'adhérence non détectée à temps par le système).",
                    "Lors des trajets de jour uniquement.",
                    "Dès que le véhicule roule à moins de 80 km/h."
                ],
                "reponse": "Sur chaussée glissante, par temps de verglas, de neige ou de forte pluie (risque de perte d'adhérence non détectée à temps par le système)."
            }
        ]
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

for index, fiche_ce in enumerate(banque_ecrites_permis_ce, start=1):
    if isinstance(fiche_ce, list):
        for question in fiche_ce:
            question["numero_fiche"] = index
    elif isinstance(fiche_ce, dict):
        fiche_ce["numero_fiche"] = index

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

for index, fiche_ce in enumerate(banque_orales_permis_ce, start=1):
    if isinstance(fiche_ce, list):
        for question in fiche_ce:
            question["numero_fiche"] = index
    elif isinstance(fiche_ce, dict):
        fiche_ce["numero_fiche"] = index




        
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
    if "verrou_permis_am" not in st.session_state:
        st.session_state.verrou_permis_am = False

    v_permis_am = st.session_state.verrou_permis_am

    st.header("Interrogation Écrite / Orale — Permis AM")
    st.caption("Tirage au sort d'une question au hasard parmi la banque Permis AM.")

    # 1. Chargement et numérotation sécurisés de la banque sur place
    try:
        banque_locale_am = charger_banque_permis_am()
        if not banque_locale_am:
            raise ValueError
        for index, fiche in enumerate(banque_locale_am, start=1):
            fiche["numero"] = index
    except:
        banque_locale_am = [{
            "type": "choix",
            "numero": 1,
            "question": "Quelle est la vitesse maximale par construction d'un cyclomoteur de moins de 50 cm³ ?",
            "choix": ["45 km/h", "50 km/h", "60 km/h"],
            "reponse": "45 km/h"
        }]

    # 2. Initialisation initiale du tirage
    if "fiche_choisie_permis_am" not in st.session_state:
        st.session_state.fiche_choisie_permis_am = random.choice(banque_locale_am)

    # 3. Bouton de tirage corrigé (utilise la banque locale sécurisée)
    if st.button("TIRER UNE AUTRE QUESTION AU HASARD", key="btn_permis_am", disabled=v_permis_am, use_container_width=True):
        st.session_state.fiche_choisie_permis_am = random.choice(banque_locale_am)
        if "rep_permis_am" in st.session_state:
            del st.session_state["rep_permis_am"]
        st.rerun()

    fiche_am = st.session_state.fiche_choisie_permis_am
    st.markdown(f"### Question Numéro {fiche_am['numero']}")
    st.info(fiche_am["question"])

    if fiche_am["type"] == "choix":
        st.selectbox(
            "Sélectionnez votre réponse :",
            options=["Choisir une réponse..."] + fiche_am.get("choix", ["Option A", "Option B", "Option C"]),
            key="rep_permis_am",
            disabled=v_permis_am,
            index=0
        )
    else:
        st.text_area(
            "Votre réponse rédigée :",
            key="rep_permis_am",
            disabled=v_permis_am,
            placeholder="Saisissez votre texte ici...",
        )

    if st.checkbox("Afficher la réponse exacte", key="chk_permis_am"):
        st.success(f"Réponse attendue : {fiche_am['reponse']}")

    st.write("---")
    st.subheader("Synthese et validation")
    
    if not v_permis_am:
        certif_am = st.checkbox(
            "Je certifie avoir repondu a la question de l'atelier Permis AM.",
            key="cert_permis_am"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER PERMIS AM",
            key="val_permis_am",
            use_container_width=True,
        ):
            if not certif_am:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_permis_am = True
                st.rerun()
    else:
        # L'atelier est verrouille, on appelle la fonction automatique pour afficher l'identite et la note
        calculer_et_afficher_note(
            liste_questions=st.session_state.questions_permis_am,  # Verifiez le nom de votre liste de questions en session
            prefixe_session="rep_permis_am",                       # Adaptez avec le prefixe de vos cles de reponses AM
            num_fiche="Unique"                                     # Indiquez le numero de la fiche ou laissez "Unique"
        )
        
with tab2:
    if "verrou_permis_b" not in st.session_state:
        st.session_state.verrou_permis_b = False

    v_permis_b = st.session_state.verrou_permis_b

    st.header("Examen du Permis B")
    st.caption("Session d'entrainement : 20 questions de type QCM tirees au sort parmi la banque de donnees.")

    # Chargement complet de la banque (les 200 questions)
    banque_complete_b = charger_banque_permis_b()

    # Tirage au sort initial et fixe de 20 questions uniques
    if "questions_permis_b_session" not in st.session_state:
        nb_questions_a_tirer = min(20, len(banque_complete_b))
        st.session_state.questions_permis_b_session = random.sample(banque_complete_b, nb_questions_a_tirer)

    if st.button("GENERER UN NOUVEL EXAMEN BLANC", key="btn_permis_b", disabled=v_permis_b, use_container_width=True):
        nb_questions_a_tirer = min(20, len(banque_complete_b))
        st.session_state.questions_permis_b_session = random.sample(banque_complete_b, nb_questions_a_tirer)
        for key in list(st.session_state.keys()):
            if key.startswith("rep_permis_b_"):
                del st.session_state[key]
        st.rerun()

    liste_questions_session = st.session_state.questions_permis_b_session

    # Affichage dynamique des 20 questions de type QCM avec image a droite
    for idx, question_b in enumerate(liste_questions_session):
        if isinstance(question_b, dict) and "question" in question_b:
            
            # Securite absolue : conversion forcee en QCM si la question etait de type ecrite
            if question_b.get("type") != "choix" or not question_b.get("choix"):
                question_b["type"] = "choix"
                question_b["choix"] = ["Oui", "Non"]

            # Division de l'ecran : 3 parts pour le QCM, 1 part pour l'image JPG
            col_texte, col_image = st.columns([3, 1])

            # --- COLONNE DE GAUCHE : LE TEXTE DU QCM ---
            with col_texte:
                st.write(f"**Question {idx + 1} :** {question_b['question']}")
                
                st.selectbox(
                    "Selectionnez votre reponse :",
                    options=["Choisir une reponse..."] + question_b.get("choix", []),
                    key=f"rep_permis_b_{idx}_Unique",
                    disabled=v_permis_b,
                    index=0,
                )

            # --- COLONNE DE DROITE : L'IMAGE JPG ---
            with col_image:
                id_question = question_b.get("numero", idx + 1)
                chemin_image = f"image code/question_{id_question}.jpg"

                try:
                    st.image(chemin_image, use_container_width=True)
                except Exception:
                    st.caption(f"Image manquante: question_{id_question}.jpg")

            # --- ZONE DE CORRECTION ET DIVISEUR ---
            if v_permis_b:
                if st.checkbox("Afficher la reponse exacte", key=f"chk_permis_b_{idx}_Unique"):
                    st.success(f"Reponse attendue : {question_b.get('reponse')}")
                
            st.divider()

    st.write("---")
    st.subheader("Synthese et validation")
    
    if not v_permis_b:
        certif_b = st.checkbox(
            "Je certifie avoir repondu aux questions de l'atelier Permis B.",
            key="cert_permis_b"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER PERMIS B",
            key="val_permis_b",
            use_container_width=True,
        ):
            if not certif_b:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_permis_b = True
                st.rerun()
    else:
        # L'atelier est verrouille, on affiche l'identite de l'eleve et sa note sur les QCM
        calculer_et_afficher_note(
            liste_questions=liste_questions_session,  
            prefixe_session="rep_permis_b",                       
            num_fiche="Unique"                                    
        )

with tab3:
    if "verrou_orale_c" not in st.session_state:
        st.session_state.verrou_orale_c = False

    v_oral_c = st.session_state.verrou_orale_c

    st.header("Interrogation Orale - Permis C")
    st.caption("Tirage au sort d'une fiche complete parmi les 12 fiches.")

    if "fiche_orale_choisie_c" not in st.session_state:
        st.session_state.fiche_orale_choisie_c = random.choice(banque_orales_permis_c)

    if st.button("TIRER UNE AUTRE FICHE ORALE AU HASARD", key="btn_orale_c", disabled=v_oral_c, use_container_width=True):
        st.session_state.fiche_orale_choisie_c = random.choice(banque_orales_permis_c)
        for key in list(st.session_state.keys()):
            if key.startswith("rep_orale_c_"):
                del st.session_state[key]
        st.rerun()

    fiche_brute_o_c = st.session_state.fiche_orale_choisie_c

    # 1. Extraction et normalisation de la liste cachee dans la cle "questions"
    if isinstance(fiche_brute_o_c, dict) and "questions" in fiche_brute_o_c:
        liste_questions_orales_c = fiche_brute_o_c["questions"]
        num_fiche_o_c = fiche_brute_o_c.get("numero_fiche", "Non defini")
    elif isinstance(fiche_brute_o_c, list) and len(fiche_brute_o_c) > 0 and isinstance(fiche_brute_o_c[0], dict):
        liste_questions_orales_c = fiche_brute_o_c[0]["questions"] if "questions" in fiche_brute_o_c[0] else fiche_brute_o_c[0]
        num_fiche_o_c = fiche_brute_o_c[0].get("numero_fiche", "Non defini")
    elif isinstance(fiche_brute_o_c, dict):
        liste_questions_orales_c = fiche_brute_o_c.get("questions", [])
        num_fiche_o_c = fiche_brute_o_c.get("numero_fiche", "Non defini")
    else:
        liste_questions_orales_c = fiche_brute_o_c
        num_fiche_o_c = "Non defini"

    st.markdown(f"### Fiche Orale Numero {num_fiche_o_c}")
    st.divider()

    # 2. Affichage dynamique des questions orales
    for idx, question_o_c in enumerate(liste_questions_orales_c):
        if isinstance(question_o_c, dict) and "question" in question_o_c:
            st.write(f"**Question {idx + 1} :** {question_o_c['question']}")

            if question_o_c.get("type") == "choix":
                st.selectbox(
                    "Selectionnez votre reponse :",
                    options=["Choisir une reponse..."] + question_o_c.get("choix", []),
                    key=f"rep_orale_c_{idx}_{num_fiche_o_c}",
                    disabled=v_oral_c,
                    index=0,
                )
            else:
                st.text_area(
                    "Saisissez vos notes de preparation :",
                    key=f"rep_orale_c_{idx}_{num_fiche_o_c}",
                    disabled=v_oral_c,
                    placeholder="Ecrivez ici vos arguments pour l'examen oral...",
                )

            # S'affiche uniquement si l'atelier est valide/verrouille
            if v_oral_c:
                if st.checkbox("Afficher le guide de correction complet", key=f"chk_oral_c_{idx}_{num_fiche_o_c}"):
                    st.success(f"Elements cles attendus : {question_o_c.get('reponse', 'Non disponible')}")
                
            st.divider()

    st.write("---")
    st.subheader("Synthese et validation")
    
    if not v_oral_c:
        certif_oral_c = st.checkbox(
            "Je certifie avoir termine la preparation de cette fiche orale C.",
            key=f"cert_oral_c_{num_fiche_o_c}"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER ORAL C",
            key=f"val_oral_c_{num_fiche_o_c}",
            use_container_width=True,
        ):
            if not certif_oral_c:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_orale_c = True
                st.rerun()
    else:
        # L'atelier est verrouille, on affiche l'encadre officiel
        calculer_et_afficher_note(
            liste_questions=liste_questions_orales_c, 
            prefixe_session="rep_orale_c", 
            num_fiche=num_fiche_o_c
        )
        
with tab4:
    if "verrou_ecrite_c" not in st.session_state:
        st.session_state.verrou_ecrite_c = False
    v_ecrit_c = st.session_state.verrou_ecrite_c

    st.header("Interrogation Ecrite - Permis C")
    st.caption("Tirage au sort d'une fiche de questions parmi les 20 fiches.")

    if "fiche_ecrite_choisie_c" not in st.session_state:
        st.session_state.fiche_ecrite_choisie_c = random.choice(banque_ecrites_permis_c)

    if st.button("TIRER UNE AUTRE FICHE ECRITE AU HASARD", key="btn_ecrite_c", disabled=v_ecrit_c):
        st.session_state.fiche_ecrite_choisie_c = random.choice(banque_ecrites_permis_c)
        for key in list(st.session_state.keys()):
            if key.startswith("rep_ecrite_c_"):
                del st.session_state[key]
        st.rerun()

    fiche_brute = st.session_state.fiche_ecrite_choisie_c
    
    # Decapsulage automatique si c'est une liste de listes [[...]]
    if isinstance(fiche_brute, list) and len(fiche_brute) > 0 and isinstance(fiche_brute[0], list):
        liste_questions_ecrites_c = fiche_brute[0]
    elif isinstance(fiche_brute, dict):
        liste_questions_ecrites_c = [fiche_brute]
    else:
        liste_questions_ecrites_c = fiche_brute

    # Extraction blindee du numero de fiche sur le premier dictionnaire reel
    if isinstance(liste_questions_ecrites_c, list) and len(liste_questions_ecrites_c) > 0:
        premier_element = liste_questions_ecrites_c[0]
        if isinstance(premier_element, list) and len(premier_element) > 0:
            premier_element = premier_element[0]
        
        if isinstance(premier_element, dict):
            num_fiche_e = premier_element.get("numero_fiche", "Non defini")
        else:
            num_fiche_e = "Non defini"
    else:
        num_fiche_e = "Non defini"

    st.markdown(f"### Fiche Ecrite Numero {num_fiche_e}")

    for idx, question_e_c in enumerate(liste_questions_ecrites_c):
        # Securite si une question est encore isolee dans une sous-liste
        if isinstance(question_e_c, list) and len(question_e_c) > 0:
            question_e_c = question_e_c[0]

        if isinstance(question_e_c, dict) and "question" in question_e_c:
            st.write(f"**Question {idx + 1} :** {question_e_c['question']}")

            if question_e_c.get("type") == "choix":
                st.selectbox(
                    "Selectionnez votre reponse :",
                    options=["Choisir une reponse..."] + question_e_c.get("choix", []),
                    key=f"rep_ecrite_c_{idx}_{num_fiche_e}",
                    disabled=v_ecrit_c,
                    index=0,
                )
            else:
                st.text_area(
                    "Votre reponse redigee :",
                    key=f"rep_ecrite_c_{idx}_{num_fiche_e}",
                    disabled=v_ecrit_c,
                    placeholder="Saisissez votre texte ici...",
                )

            if v_ecrit_c:
                st.success(f"Reponse attendue : {question_e_c.get('reponse')}")
                
            st.divider()

    st.write("---")
    st.subheader("Synthese et validation")
    
    # Recupere le verrou directement depuis la memoire globale
    v_ecrit_c = st.session_state.get("verrou_ecrite_c", False)

    if not v_ecrit_c:
        # Utilisation d'une cle fixe securisee pour ne plus jamais planter sur num_fiche_e
        certif_ecrit_c = st.checkbox(
            "Je certifie avoir repondu aux questions de cette fiche ecrite C.",
            key="cert_ecrit_c_validation_fixe"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER ECRIT C",
            key="val_ecrit_c_validation_fixe",
            use_container_width=True
        ):
            if not certif_ecrit_c:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_ecrite_c = True
                st.rerun()
    else:
        # Recuperation de secours du numero de fiche
        fiche_actuelle_brute = st.session_state.get("fiche_ecrite_choisie_c", [])
        if isinstance(fiche_actuelle_brute, list) and len(fiche_actuelle_brute) > 0:
            if isinstance(fiche_actuelle_brute[0], dict):
                num_fiche_secu = fiche_actuelle_brute[0].get("numero_fiche", "Non defini")
            else:
                num_fiche_secu = "Non defini"
        elif isinstance(fiche_actuelle_brute, dict):
            num_fiche_secu = fiche_actuelle_brute.get("numero_fiche", "Non defini")
        else:
            num_fiche_secu = "Non defini"

        # L'atelier est valide, on affiche la note finale
        calculer_et_afficher_note(
            liste_questions=fiche_actuelle_brute, 
            prefixe_session="rep_ecrite_c", 
            num_fiche=num_fiche_secu
        )
      

with tab5:
    if "verrou_orale_ce" not in st.session_state:
        st.session_state.verrou_orale_ce = False

    v_oral_ce = st.session_state.verrou_orale_ce

    st.header("Interrogation Orale - Permis CE")
    st.caption("Tirage au sort d'une fiche complete parmi les 12 fiches.")

    if "fiche_orale_choisie_ce" not in st.session_state:
        st.session_state.fiche_orale_choisie_ce = random.choice(banque_orales_permis_ce)

    if st.button("TIRER UNE AUTRE FICHE ORALE AU HASARD", key="btn_orale_ce", disabled=v_oral_ce, use_container_width=True):
        st.session_state.fiche_orale_choisie_ce = random.choice(banque_orales_permis_ce)
        for key in list(st.session_state.keys()):
            if key.startswith("rep_orale_ce_"):
                del st.session_state[key]
        st.rerun()

    fiche_brute_o_ce = st.session_state.fiche_orale_choisie_ce

    # 1. Extraction et normalisation de la liste cachee dans la cle "questions"
    if isinstance(fiche_brute_o_ce, dict) and "questions" in fiche_brute_o_ce:
        liste_questions_orales_ce = fiche_brute_o_ce["questions"]
        num_fiche_o_ce = fiche_brute_o_ce.get("numero_fiche", "Non defini")
    elif isinstance(fiche_brute_o_ce, list) and len(fiche_brute_o_ce) > 0 and isinstance(fiche_brute_o_ce[0], dict):
        liste_questions_orales_ce = fiche_brute_o_ce[0]["questions"] if "questions" in fiche_brute_o_ce[0] else fiche_brute_o_ce[0]
        num_fiche_o_ce = fiche_brute_o_ce[0].get("numero_fiche", "Non defini")
    elif isinstance(fiche_brute_o_ce, dict):
        liste_questions_orales_ce = fiche_brute_o_ce.get("questions", [])
        num_fiche_o_ce = fiche_brute_o_ce.get("numero_fiche", "Non defini")
    else:
        liste_questions_orales_ce = fiche_brute_o_ce
        num_fiche_o_ce = "Non defini"

    st.markdown(f"### Fiche Orale Numero {num_fiche_o_ce}")
    st.divider()

    # 2. Affichage dynamique des questions orales
    for idx, question_o_ce in enumerate(liste_questions_orales_ce):
        if isinstance(question_o_ce, dict) and "question" in question_o_ce:
            st.write(f"**Question {idx + 1} :** {question_o_ce['question']}")

            if question_o_ce.get("type") == "choix":
                st.selectbox(
                    "Selectionnez votre reponse :",
                    options=["Choisir une reponse..."] + question_o_ce.get("choix", []),
                    key=f"rep_orale_ce_{idx}_{num_fiche_o_ce}",
                    disabled=v_oral_ce,
                    index=0,
                )
            else:
                st.text_area(
                    "Saisissez vos notes de preparation :",
                    key=f"rep_orale_ce_{idx}_{num_fiche_o_ce}",
                    disabled=v_oral_ce,
                    placeholder="Ecrivez ici vos arguments pour l'examen oral...",
                )

            # S'affiche uniquement si l'atelier est valide/verrouille
            if v_oral_ce:
                if st.checkbox("Afficher le guide de correction complet", key=f"chk_oral_ce_{idx}_{num_fiche_o_ce}"):
                    st.success(f"Elements cles attendus : {question_o_ce.get('reponse', 'Non disponible')}")
                
            st.divider()

    st.write("---")
    st.subheader("Synthese et validation")
    
    if not v_oral_ce:
        certif_oral = st.checkbox(
            "Je certifie avoir termine la preparation de cette fiche orale CE.",
            key=f"cert_oral_ce_{num_fiche_o_ce}"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER ORAL CE",
            key=f"val_oral_ce_{num_fiche_o_ce}",
            use_container_width=True,
        ):
            if not certif_oral:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_orale_ce = True
                st.rerun()
    else:
        calculer_et_afficher_note(
            liste_questions=liste_questions_orales_ce, 
            prefixe_session="rep_orale_ce", 
            num_fiche=num_fiche_o_ce
        )
        

with tab6:
    if "verrou_ecrite_ce" not in st.session_state:
        st.session_state.verrou_ecrite_ce = False

    v_ecrit_ce = st.session_state.verrou_ecrite_ce

    st.header("Interrogation Ecrite - Permis CE")
    st.caption("Tirage au sort d'une fiche de questions parmi les 20 fiches.")

    if "fiche_ecrite_choisie_ce" not in st.session_state:
        st.session_state.fiche_ecrite_choisie_ce = random.choice(banque_ecrites_permis_ce)

    if st.button("TIRER UNE AUTRE FICHE ECRITE AU HASARD", key="btn_ecrite_ce", disabled=v_ecrit_ce, use_container_width=True):
        st.session_state.fiche_ecrite_choisie_ce = random.choice(banque_ecrites_permis_ce)
        for key in list(st.session_state.keys()):
            if key.startswith("rep_ecrite_ce_"):
                del st.session_state[key]
        st.rerun()

    liste_questions_ecrites_ce = st.session_state.fiche_ecrite_choisie_ce
    
    # Extraction securisee du numero de fiche via le dictionnaire a l'index 0
    if isinstance(liste_questions_ecrites_ce, list) and len(liste_questions_ecrites_ce) > 0:
        if isinstance(liste_questions_ecrites_ce[0], dict):
            num_fiche_e_ce = liste_questions_ecrites_ce[0].get("numero_fiche", "Non defini")
        else:
            num_fiche_e_ce = "Non defini"
    elif isinstance(liste_questions_ecrites_ce, dict):
        num_fiche_e_ce = liste_questions_ecrites_ce.get("numero_fiche", "Non defini")
    else:
        num_fiche_e_ce = "Non defini"

    st.markdown(f"### Fiche Ecrite Numero {num_fiche_e_ce}")
    st.divider()

    for idx, question_e_ce in enumerate(liste_questions_ecrites_ce):
        if isinstance(question_e_ce, dict) and "question" in question_e_ce:
            st.write(f"**Question {idx + 1} :** {question_e_ce['question']}")

            if question_e_ce.get("type") == "choix":
                st.selectbox(
                    "Selectionnez votre reponse :",
                    options=["Choisir une reponse..."] + question_e_ce.get("choix", []),
                    key=f"rep_ecrite_ce_{idx}_{num_fiche_e_ce}",
                    disabled=v_ecrit_ce,
                    index=0,
                )
            else:
                st.text_area(
                    "Votre reponse redigee :",
                    key=f"rep_ecrite_ce_{idx}_{num_fiche_e_ce}",
                    disabled=v_ecrit_ce,
                    placeholder="Saisissez votre texte ici...",
                )

            # S'affiche uniquement si l'atelier est valide/verrouille
            if v_ecrit_ce:
                if st.checkbox("Afficher la reponse exacte", key=f"chk_ecrit_ce_{idx}_{num_fiche_e_ce}"):
                    st.success(f"Reponse attendue : {question_e_ce.get('reponse')}")
                
            st.divider()

    st.write("---")
    st.subheader("Synthese et validation")
    
    if not v_ecrit_ce:
        certif_ecrit = st.checkbox(
            "Je certifie avoir repondu aux questions de cette fiche ecrite CE.",
            key=f"cert_ecrit_ce_{num_fiche_e_ce}"
        )

        if st.button(
            "VALIDER ET VERROUILLER L'ATELIER ECRIT CE",
            key=f"val_ecrit_ce_{num_fiche_e_ce}",
            use_container_width=True,
        ):
            if not certif_ecrit:
                st.warning("Veuillez cocher la case de certification avant.")
            else:
                st.session_state.verrou_ecrite_ce = True
                st.rerun()
    else:
        # L'atelier est verrouille, on appelle la fonction pour afficher l'identite, la note et la fiche
        calculer_et_afficher_note(
            liste_questions=liste_questions_ecrites_ce, 
            prefixe_session="rep_ecrite_ce", 
            num_fiche=num_fiche_e_ce
        )



