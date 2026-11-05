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


banque_questions = [
    {
        "question": "À quoi sert le contrôle des pneumatiques avant le départ ?",
        "type": "texte",
    },
    {
        "question": "Un voyant rouge de pression d'huile s'allume. Que faites-vous ?",
        "type": "choix",
        "choix": [
            "Je continue jusqu'à destination",
            "Je m'arrête dès que possible en sécurité",
            "J'accélère pour atteindre un garage",
            "J'ignore le voyant",
        ],
    },
    {
        "question": "Pourquoi faut-il répartir correctement le chargement ?",
        "type": "texte",
    },
    {
        "question": "Que peut provoquer un chargement mal arrimé ?",
        "type": "choix",
        "choix": [
            "Un déplacement de la charge",
            "Une baisse automatique de consommation",
            "Une meilleure visibilité",
            "Aucun effet sur la conduite",
        ],
    },
    {
        "question": "Que vérifiez-vous avant d'atteler une remorque ?",
        "type": "texte",
    },
    {
        "question": "Pourquoi faut-il contrôler les angles morts ?",
        "type": "texte",
    },
    {
        "question": "Que faire en cas de fatigue importante au volant ?",
        "type": "choix",
        "choix": [
            "Faire une pause dans un endroit sûr",
            "Rouler plus vite pour finir le trajet",
            "Ouvrir la fenêtre et continuer",
            "Ignorer la fatigue",
        ],
    },
    {
        "question": "Pourquoi adapter sa vitesse avant un virage ?",
        "type": "choix",
        "choix": [
            "Pour limiter le risque de déport ou de renversement",
            "Pour éviter d'utiliser les rétroviseurs",
            "Pour augmenter la charge utile",
            "Pour économiser les clignotants",
        ],
    },
    {
        "question": "Que devez-vous faire avant de quitter le véhicule à l'arrêt ?",
        "type": "texte",
    },
    {
        "question": "Pourquoi contrôler le fonctionnement des feux avant un trajet ?",
        "type": "texte",
    },
    {
        "question": "Que faire si un pneu semble endommagé avant le départ ?",
        "type": "choix",
        "choix": [
            "Faire contrôler le pneu avant de partir",
            "Augmenter la vitesse",
            "Le regonfler sans vérifier et partir",
            "Ne rien faire s'il reste de la bande de roulement",
        ],
    },
    {
        "question": "À quoi sert le frein de stationnement ?",
        "type": "texte",
    },
    {
        "question": "Pourquoi faut-il vérifier les niveaux du véhicule ?",
        "type": "texte",
    },
    {
        "question": "Que signifie une distance de sécurité suffisante ?",
        "type": "choix",
        "choix": [
            "Avoir le temps de réagir et de s'arrêter",
            "Rouler près du véhicule devant",
            "Empêcher les autres de dépasser",
            "Garder exactement cinq mètres en toute situation",
        ],
    },
    {
        "question": "Pourquoi le freinage d'un véhicule chargé demande-t-il de l'anticipation ?",
        "type": "texte",
    },
    {
        "question": "Que devez-vous faire avant une marche arrière ?",
        "type": "choix",
        "choix": [
            "Vérifier la zone et manœuvrer lentement",
            "Reculer rapidement",
            "Regarder uniquement devant",
            "Faire confiance aux capteurs sans contrôle",
        ],
    },
    {
        "question": "Quel est le rôle des rétroviseurs lors d'une manœuvre ?",
        "type": "texte",
    },
    {
        "question": "Pourquoi faut-il éviter les gestes brusques avec un poids lourd ?",
        "type": "texte",
    },
    {
        "question": "Que faire en cas de perte de visibilité due au brouillard ?",
        "type": "choix",
        "choix": [
            "Réduire l'allure et augmenter les distances",
            "Suivre de près les feux du véhicule devant",
            "Accélérer pour sortir du brouillard",
            "Éteindre tous les feux",
        ],
    },
    {
        "question": "Pourquoi faut-il adapter la conduite à l'état de la chaussée ?",
        "type": "texte",
    },
    {
        "question": "Que faire si la cargaison risque de se déplacer ?",
        "type": "choix",
        "choix": [
            "S'arrêter en sécurité et sécuriser le chargement",
            "Continuer jusqu'à destination",
            "Freiner brutalement",
            "Ouvrir les portes en roulant",
        ],
    },
    {
        "question": "Expliquez l'utilité de l'arrimage du chargement.",
        "type": "texte",
    },
    {
        "question": "Pourquoi faut-il vérifier la fermeture des portes de la caisse ?",
        "type": "texte",
    },
    {
        "question": "Comment réagir face à un obstacle soudain ?",
        "type": "choix",
        "choix": [
            "Rester maître du véhicule et freiner de façon adaptée",
            "Donner un coup de volant brusque sans regarder",
            "Accélérer systématiquement",
            "Regarder uniquement l'obstacle",
        ],
    },
    {
        "question": "Pourquoi faut-il anticiper les intersections avec un véhicule long ?",
        "type": "texte",
    },
    {
        "question": "Que devez-vous vérifier au niveau de l'attelage ?",
        "type": "texte",
    },
    {
        "question": "Pourquoi faut-il tenir compte du gabarit du véhicule ?",
        "type": "choix",
        "choix": [
            "Pour éviter les obstacles bas, étroits ou limités en hauteur",
            "Pour choisir la couleur du véhicule",
            "Pour réduire la pression des pneus",
            "Pour éviter de contrôler les panneaux",
        ],
    },
    {
        "question": "Que faire avant de franchir un passage étroit ou limité en hauteur ?",
        "type": "choix",
        "choix": [
            "Vérifier que le gabarit du véhicule permet le passage",
            "S'engager rapidement",
            "Suivre le véhicule précédent sans vérifier",
            "Se fier uniquement au GPS",
        ],
    },
    {
        "question": "Pourquoi faut-il éviter de surcharger le véhicule ?",
        "type": "texte",
    },
    {
        "question": "Que faire si le chargement masque la plaque ou les feux ?",
        "type": "choix",
        "choix": [
            "Réorganiser le chargement pour rendre les équipements visibles",
            "Partir comme cela",
            "Éteindre les feux",
            "Rouler uniquement de jour",
        ],
    },
    {
        "question": "Pourquoi faut-il maintenir une allure régulière et adaptée ?",
        "type": "texte",
    },
    {
        "question": "Que faire si vous constatez une anomalie importante lors des contrôles ?",
        "type": "choix",
        "choix": [
            "Ne pas partir avant d'avoir fait vérifier l'anomalie",
            "La noter et continuer",
            "Rouler plus lentement sans rien vérifier",
            "Attendre qu'un voyant s'allume",
        ],
    },
    {
        "question": "Pourquoi faut-il signaler ses changements de direction suffisamment tôt ?",
        "type": "texte",
    },
    {
        "question": "Que risque un conducteur qui ne contrôle pas régulièrement son environnement ?",
        "type": "choix",
        "choix": [
            "Ne pas détecter un danger ou un usager",
            "Économiser du carburant",
            "Améliorer la stabilité",
            "Réduire automatiquement la distance d'arrêt",
        ],
    },
    {
        "question": "Pourquoi faut-il être particulièrement prudent lors d'un dépassement ?",
        "type": "texte",
    },
    {
        "question": "Que devez-vous faire si vous devez vous arrêter sur la chaussée à la suite d'une panne ?",
        "type": "texte",
    },
    {
        "question": "Quel comportement adopter à proximité des usagers vulnérables ?",
        "type": "choix",
        "choix": [
            "Réduire l'allure et leur laisser un espace suffisant",
            "Passer au plus près pour limiter la durée du dépassement",
            "Klaxonner systématiquement",
            "Ne pas modifier sa conduite",
        ],
    },
    {
        "question": "Pourquoi faut-il vérifier que le chargement est compatible avec le trajet prévu ?",
        "type": "texte",
    },
    {
        "question": "Que faire après avoir constaté un bruit anormal du véhicule ?",
        "type": "choix",
        "choix": [
            "S'arrêter en sécurité et rechercher l'origine ou faire contrôler",
            "Augmenter le volume de la radio",
            "Accélérer pour vérifier si le bruit disparaît",
            "Continuer sans surveillance",
        ],
    },
]


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
    st.header("Fiches orales permis C")

with tab4:
    st.subheader("Fiche d'entraînement — permis C")
    st.caption("Une fiche contient 20 questions tirées au hasard parmi 40.")

    if len(banque_questions) != 40:
        st.error(
            f"La banque contient {len(banque_questions)} questions au lieu de 40."
        )
    else:
        # Crée la première fiche une seule fois.
        if "fiche_permis_c" not in st.session_state:
            st.session_state.fiche_permis_c = random.sample(
                banque_questions, 20
            )

        # Nouveau tirage : 20 questions différentes parmi les 40.
        if st.button("Tirer une nouvelle fiche", key="nouvelle_fiche_permis_c"):
            st.session_state.fiche_permis_c = random.sample(
                banque_questions, 20
            )

            # Efface les réponses précédentes.
            for cle in list(st.session_state.keys()):
                if cle.startswith("reponse_permis_c_"):
                    del st.session_state[cle]

            st.rerun()

        # Affiche les 20 questions tirées.
        for numero, item in enumerate(
            st.session_state.fiche_permis_c, start=1
        ):
            st.markdown(f"**Question {numero}. {item['question']}**")

            if item["type"] == "choix":
                st.selectbox(
                    "Choisissez une réponse",
                    ["— Sélectionnez —"] + item["choix"],
                    key=f"reponse_permis_c_{numero}",
                )
            else:
                st.text_area(
                    "Votre réponse",
                    key=f"reponse_permis_c_{numero}",
                    height=90,
                )




if "suite_verrouille_tab4_permis_c" not in st.session_state:
    st.session_state.suite_verrouille_tab4_permis_c = False

verrou_permis_c = st.session_state.suite_verrouille_tab4_permis_c

# La banque doit contenir exactement 40 questions.
if len(banque_questions) != 40:
    st.error(
        f"La banque doit contenir 40 questions. "
        f"Elle en contient actuellement {len(banque_questions)}."
    )
else:
    # Génère une fiche de 20 questions une seule fois,
    # ou après clic sur le bouton "Nouvelle fiche".
    if "fiche_permis_c" not in st.session_state:
        st.session_state.fiche_permis_c = random.sample(banque_questions, 20)

    if st.button(
        "GÉNÉRER UNE NOUVELLE FICHE DE 20 QUESTIONS",
        key="btn_nouvelle_fiche_permis_c",
        use_container_width=True,
        disabled=verrou_permis_c,
    ):
        st.session_state.fiche_permis_c = random.sample(banque_questions, 20)

        # Efface les anciennes réponses
        for cle in list(st.session_state.keys()):
            if cle.startswith("reponse_permis_c_"):
                del st.session_state[cle]

        st.rerun()

    st.subheader("Fiche d'entraînement — Permis C")
    st.caption("20 questions tirées au hasard parmi une banque de 40.")

    for numero, item in enumerate(st.session_state.fiche_permis_c, start=1):
        st.markdown(f"**Question {numero} — {item['question']}**")

        if item["type"] == "choix":
            st.radio(
                "Choisissez une réponse :",
                item["choix"],
                key=f"reponse_permis_c_{numero}",
                disabled=verrou_permis_c,
                index=None,
            )
        else:
            st.text_area(
                "Votre réponse :",
                key=f"reponse_permis_c_{numero}",
                disabled=verrou_permis_c,
                height=90,
            )

    st.write("---")
    st.subheader("Correction")

    afficher_correction = st.checkbox(
        "Afficher les réponses corrigées",
        key="afficher_correction_permis_c",
    )

    if afficher_correction:
        for numero, item in enumerate(st.session_state.fiche_permis_c, start=1):
            st.markdown(f"**Question {numero}**")
            st.write(item["question"])
            st.success(f"Réponse : {item['reponse']}")

    st.write("---")
    st.subheader("Synthèse et validation de l'atelier")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_permis_c = st.checkbox(
        "Je certifie avoir répondu aux questions de l'atelier Permis C.",
        key="check_certif_permis_c_final",
        disabled=verrou_permis_c,
    )

    if st.button(
        "VALIDER L'ATELIER PERMIS C",
        key="btn_valider_permis_c",
        use_container_width=True,
        disabled=verrou_permis_c,
    ):
        if not case_certif_permis_c:
            st.warning("Coche la case de certification avant de valider.")
        else:
            st.session_state.suite_verrouille_tab4_permis_c = True
            st.success(
                f"Atelier validé pour {p_eleve} {n_eleve} "
                f"— classe {c_eleve}."
            )
            st.rerun()

    if verrou_permis_c:
        st.info("Cet atelier a été validé et verrouillé.")







with tab5:
    st.header("Fiches orales permis CE")

with tab6:
    st.header("Fiches écrites permis CE")
















