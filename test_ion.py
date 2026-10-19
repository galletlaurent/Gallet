
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application test des ions",
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
st.title("Application test des ions")
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


# Déclaration officielle de la barre de navigation
# Les variables d'onglets sont liées à leurs index de liste respectifs
onglets = st.tabs([
    "Identification",
    "Test des ions",
    "Exemples",    
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]

def reinitialiser_selections():
    st.session_state["choix_famille"] = "Cations (Ions positifs)"
    st.session_state["choix_ion"] = "Ion Cuivre II (Cu²⁺)"

# Initialisation des variables de session si elles n'existent pas encore
if "choix_famille" not in st.session_state:
    st.session_state["choix_famille"] = "Cations (Ions positifs)"
if "choix_ion" not in st.session_state:
    st.session_state["choix_ion"] = "Ion Cuivre II (Cu²⁺)"

def afficher_questions_ions_securite_dynamiques(verrouille=False):
    """Affiche le QCM et le texte a trous pour l'atelier d'identification des ions."""
    ordre_fixe_tab_ions = [
        {
            "id": "qion1",
            "q": "Quel reactif permet de caracteriser la presence de l'ion Cuivre II (Cu2+) ?",
            "options": ["La soude", "Le nitrate d'argent", "Le chlorure de baryum"],
            "rep": "La soude",
        },
        {
            "id": "qion2",
            "q": "Quelle est la couleur du precipite obtenu lors du test de l'ion Fer II (Fe2+) ?",
            "options": ["Vert pale", "Rouille", "Bleu"],
            "rep": "Vert pale",
        },
        {
            "id": "qion3",
            "q": "Le precipite blanc qui noircit a la lumiere indique la presence de l'ion :",
            "options": ["Chlorure (Cl-)", "Sulfate (SO42-)", "Zinc (Zn2+)"],
            "rep": "Chlorure (Cl-)",
        },
        {
            "id": "qion4",
            "q": "Quel pictogramme de danger (SGH) est associe a la manipulation de la soude ?",
            "options": ["Corrosif (GHS05)", "Toxique (GHS06)", "Dangereux pour l'environnement (GHS09)"],
            "rep": "Corrosif (GHS05)",
        },
        {
            "id": "qion5",
            "q": "En cas de projection de produit chimique dans les yeux, il faut rincer pendant au moins :",
            "options": ["20 minutes", "5 minutes", "30 secondes"],
            "rep": "20 minutes",
        },
        {
            "id": "qion6",
            "q": "L'ion Sulfate (SO42-) est mis en evidence par l'apparition d'un precipite blanc avec du :",
            "options": ["Chlorure de baryum", "Nitrate d'argent", "Hydroxyde de sodium"],
            "rep": "Chlorure de baryum",
        },
        {
            "id": "qion7",
            "q": "Quel equipement de protection est optionnel lors d'une manipulation de solutions ioniques ?",
            "options": ["Aucun, blouse, lunettes et gants sont obligatoires", "Les lunettes de protection", "Les gants en nitrile"],
            "rep": "Aucun, blouse, lunettes et gants sont obligatoires",
        },
        {
            "id": "qion8",
            "q": "Dans l'equation-bilan de precipitation, l'etat physique du precipite est note :",
            "options": ["(s) pour solide", "(aq) pour aqueux", "(g) pour gaz"],
            "rep": "(s) pour solide",
        },
        {
            "id": "qion9",
            "q": "Le nitrate d'argent necessite le port de gants car il provoque sur la peau :",
            "options": ["Des taches noires tenaces", "Des brulures thermiques", "Une coloration bleue immediate"],
            "rep": "Des taches noires tenaces",
        },
        {
            "id": "qion10",
            "q": "Que forme l'association d'un cation metallique et des ions hydroxyde de la soude ?",
            "options": ["Un precipite (hydroxyde metallique)", "Un degagement gazeux", "Une dissolution complete"],
            "rep": "Un precipite (hydroxyde metallique)",
        },
    ]

    st.session_state.ordre_quiz_tab_ions = ordre_fixe_tab_ions

    col_quiz, col_trous = st.columns(2)

    with col_quiz:
        st.markdown("##### Quiz Identification et Securite (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab_ions, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ion_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthese Securite et Ions (Texte a trous - 10 cases - 10 pts)")
        champs_d = [
            ("1. La formation d'un solide insoluble en solution s'appelle une .........", ["Choisir...", "precipitation", "dissolution"], "precipitation", "ion_t1_final"),
            ("2. Pour detecter les ions metalliques positifs, on utilise de la ..........", ["Choisir...", "soude", "eau"], "soude", "ion_t2_final"),
            ("3. Le chlorure de baryum possede le pictogramme du produit ...........", ["Choisir...", "toxique", "inflammable"], "toxique", "ion_t3_final"),
            ("4. L'ion chlorure reagit avec le nitrate d'argent pour former un precipite ......", ["Choisir...", "blanc", "bleu"], "blanc", "ion_t4_final"),
            ("5. Les lunettes de protection evitent les risques de ........ oculaires.", ["Choisir...", "projection", "fatigue"], "projection", "ion_t5_final"),
            ("6. En cas d'accident cutane, il faut retirer les vetements .........", ["Choisir...", "contamines", "propres"], "contamines", "ion_t6_final"),
            ("7. Le symbole SGH en forme de losange rouge encadre un ......... de danger.", ["Choisir...", "pictogramme", "texte"], "pictogramme", "ion_t7_final"),
            ("8. L'hydroxyde de fer III est un solide de couleur ..........", ["Choisir...", "rouille", "verte"], "rouille", "ion_t8_final"),
            ("9. Un ion possedant une charge globale negative est un ..........", ["Choisir...", "anion", "cation"], "anion", "ion_t9_final"),
            ("10. Rincer abondamment a l'eau est le premier geste de ..........", ["Choisir...", "secours", "nettoyage"], "secours", "ion_t10_final"),
        ]

        for enonce, choix, _, cle in champs_d:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

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
    st.title("Test d'identification des ions en solution aqueuse")
    st.write(
        "Cette application intègre le protocole expérimental, les fiches de sécurité "
        "internationales SGH, les consignes d'urgence et les équations-bilans des réactions."
    )

    ions_data = {
        "Cations (Ions positifs)": {
            "Ion Cuivre II (Cu²⁺)": {
                "solution_tester": "Solution de sulfate de cuivre(II) (contenant les ions Cu²⁺)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "solution_cuivre.jpeg",
                "reactif": "Soude (Hydroxyde de sodium)", 
                "images_picto": ["SGH05.png"],
                "image_reaction": "ion_cuivre.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Rincer immédiatement et abondamment à l'eau tiède pendant au moins 15 minutes. Retirer les vêtements contaminés sous la douche.",
                    "yeux": "Rincer immédiatement à l'aide d'un lave-œil ou d'une douche oculaire pendant au moins 20 minutes en maintenant les paupières bien ouvertes. Consulter un médecin d'urgence.",
                    "ingestion": "Ne pas faire vomir. Rincer la bouche avec de l'eau et appeler immédiatement le centre antipoison ou le 15/112."
                },
                "couleur": "Bleu", 
                "precipite": "Hydroxyde de cuivre(II) Cu(OH)₂",
                "equation": r"Cu^{2+}_{(aq)} + 2OH^-_{(aq)} \rightarrow Cu(OH)_{2\,(s)}"
            },
            "Ion Fer II (Fe²⁺)": {
                "solution_tester": "Solution de sulfate de fer(II) (contenant les ions Fe²⁺)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "solution_fer2.jpg",
                "reactif": "Soude (Hydroxyde de sodium)", 
                "images_picto": ["SGH05.png"],
                "image_reaction": "ion_fer2.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Rincer immédiatement et abondamment à l'eau tiède pendant au moins 15 minutes. Retirer les vêtements contaminés sous la douche.",
                    "yeux": "Rincer immédiatement à l'aide d'un lave-œil ou d'une douche oculaire pendant au moins 20 minutes en maintenant les paupières bien ouvertes. Consulter un médecin d'urgence.",
                    "ingestion": "Ne pas faire vomir. Rincer la bouche avec de l'eau et appeler immédiatement le centre antipoison ou le 15/112."
                },
                "couleur": "Vert pâle", 
                "precipite": "Hydroxyde de fer(II) Fe(OH)₂",
                "equation": r"Fe^{2+}_{(aq)} + 2OH^-_{(aq)} \rightarrow Fe(OH)_{2\,(s)}"
            },
            "Ion Fer III (Fe³⁺)": {
                "solution_tester": "Solution de chlorure de fer(III) (contenant les ions Fe³⁺)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "solution_fer3.jpg",
                "reactif": "Soude (Hydroxyde de sodium)", 
                "images_picto": ["SGH05.png"],
                "image_reaction": "ion_fer3.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Rincer immédiatement et abondamment à l'eau tiède pendant au moins 15 minutes. Retirer les vêtements contaminés sous la douche.",
                    "yeux": "Rincer immédiatement à l'aide d'un lave-œil ou d'une douche oculaire pendant au moins 20 minutes en maintenant les paupières bien ouvertes. Consulter un médecin d'urgence.",
                    "ingestion": "Ne pas faire vomir. Rincer la bouche avec de l'eau et appeler immédiatement le centre antipoison ou le 15/112."
                },
                "couleur": "Rouille (Brun-orangé)", 
                "precipite": "Hydroxyde de fer(III) Fe(OH)₃",
                "equation": r"Fe^{3+}_{(aq)} + 3OH^-_{(aq)} \rightarrow Fe(OH)_{3\,(s)}"
            },
            "Ion Zinc (Zn²⁺)": {
                "solution_tester": "Solution de sulfate de zinc (contenant les ions Zn²⁺)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "tube_essai.jpg",
                "reactif": "Soude (Hydroxyde de sodium)", 
                "images_picto": ["SGH05.png"],
                "image_reaction": "ion_zinc.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Rincer immédiatement et abondamment à l'eau tiède pendant au moins 15 minutes. Retirer les vêtements contaminés sous la douche.",
                    "yeux": "Rincer immédiatement à l'aide d'un lave-œil ou d'une douche oculaire pendant au moins 20 minutes en maintenant les paupières bien ouvertes. Consulter un médecin d'urgence.",
                    "ingestion": "Ne pas faire vomir. Rincer la bouche avec de l'eau et appeler immédiatement le centre antipoison ou le 15/112."
                },
                "couleur": "Blanc (se redissout dans un excès de soude)", 
                "precipite": "Hydroxyde de zinc Zn(OH)₂",
                "equation": r"Zn^{2+}_{(aq)} + 2OH^-_{(aq)} \rightarrow Zn(OH)_{2\,(s)}"
            },
            "Ion Aluminium (Al³⁺)": {
                "solution_tester": "Solution de chlorure d'aluminium (contenant les ions Al³⁺)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "solution_aluminium.jpg",
                "reactif": "Soude (Hydroxyde de sodium)", 
                "images_picto": ["SGH05.png"],
                "image_reaction": "ion_aluminium.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Rincer immédiatement et abondamment à l'eau tiède pendant au moins 15 minutes. Retirer les vêtements contaminés sous la douche.",
                    "yeux": "Rincer immédiatement à l'aide d'un lave-œil ou d'une douche oculaire pendant au moins 20 minutes en maintenant les paupières bien ouvertes. Consulter un médecin d'urgence.",
                    "ingestion": "Ne pas faire vomir. Rincer la bouche avec de l'eau et appeler immédiatement le centre antipoison ou le 15/112."
                },
                "couleur": "Blanc", 
                "precipite": "Hydroxyde d'aluminium Al(OH)₃",
                "equation": r"Al^{3+}_{(aq)} + 3OH^-_{(aq)} \rightarrow Al(OH)_{3\,(s)}"
            }
        },
        "Anions (Ions négatifs)": {
            "Ion Chlorure (Cl⁻)": {
                "solution_tester": "Solution de chlorure de sodium (contenant les ions Cl⁻)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "tube_essai.jpg",
                "reactif": "Nitrate d'argent", 
                "images_picto": ["SGH05.png", "SGH09.png"],
                "image_reaction": "ion_chlorure.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Laver immédiatement à l'eau et au savon. Le nitrate d'argent provoque des taches noires inoffensives mais tenaces si la peau est exposée à la lumière.",
                    "yeux": "Rincer avec précaution à l'eau pendant plusieurs minutes. Enlever les lentilles de contact si la victime en porte et si elles peuvent être facilement enlevées. Continuer à rincer. Appeler un médecin.",
                    "ingestion": "Rincer la bouche. Consulter un médecin en cas de malaise."
                },
                "couleur": "Blanc (noircit à la lumière)", 
                "precipite": "Chlorure d'argent AgCl",
                "equation": r"Ag^+_{(aq)} + Cl^-_{(aq)} \rightarrow AgCl_{(s)}"
            },
            "Ion Sulfate (SO₄²⁻)": {
                "solution_tester": "Solution de sulfate de sodium (contenant les ions SO₄²⁻)",
                "contenant": "Tube à essai propre posé sur un porte-tubes",
                "image_pot": "tube_essai.jpg",
                "reactif": "Chlorure de baryum", 
                "images_picto": ["SGH06.png"],
                "image_reaction": "ion_sulfate.jpg",
                "epi": ["Blouse en coton", "Lunettes de protection étanches", "Gants en nitrile"],
                "secours": {
                    "peau": "Laver abondamment à l'eau et au savon. Retirer les vêtements souillés.",
                    "yeux": "Rincer abondamment à l'eau pendant plusieurs minutes. Consulter un ophtalmologiste en cas d'irritation persistant.",
                    "ingestion": "Danger de mort par ingestion. Rincer la bouche. Appeler immédiatement le 15/112."
                },
                "couleur": "Blanc", 
                "precipite": "Sulfate de baryum BaSO₄",
                "equation": r"Ba^{2+}_{(aq)} + SO_4^{2-}_{(aq)} \rightarrow BaSO_{4\,(s)}"
            }
        }
    }
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.header("Sélection du test")
        
        # Bouton de réinitialisation
        st.button("Réinitialiser les sélections", on_click=reinitialiser_selections)
        
        # Les composants sont liés aux clés du Session State
        famille = st.radio(
            "Choisissez la catégorie d'ion :", 
            list(ions_data.keys()),
            key="choix_famille"
        )
        
        # Vérification de la cohérence de l'ion choisi suite à un changement de famille
        liste_ions_disponibles = list(ions_data[famille].keys())
        
        if st.session_state["choix_ion"] not in liste_ions_disponibles:
            st.session_state["choix_ion"] = liste_ions_disponibles[0]
            
        nom_ion = st.selectbox(
            "Sélectionnez l'ion spécifique à identifier :", 
            liste_ions_disponibles,
            key="choix_ion"
        )
        
        info = ions_data[famille][nom_ion]
        
        st.write("---")
        st.subheader("Visuel du dispositif")
        try:
            st.image(
                info["image_pot"], 
                caption=info['contenant'], 
                width=250
            )
        except Exception as e:
            st.error(f"Image manquante : {info['image_pot']}")
    with col2:
        st.header("Fiche Expérimentale et Sécurité")
        
        st.subheader("Dispositif et Échantillon")
        st.markdown(f"**Contenant (le pot) :** {info['contenant']}")
        st.markdown(f"**Produit à tester :** {info['solution_tester']}")
        
        st.subheader("Réactif et Sécurité")
        st.markdown(f"**Réactif ajouté :** {info['reactif']}")
        st.markdown("**Pictogramme(s) de danger officiel(s) :**")
        
        img_cols = st.columns(max(len(info["images_picto"]), 1))
        for index, fichier_jpg in enumerate(info["images_picto"]):
            with img_cols[index]:
                try:
                    st.image(
                        fichier_jpg,
                        caption=fichier_jpg,
                        width=100
                    )
                except Exception as e:
                    st.error(f"Image manquante : {fichier_jpg}")
                    
        st.markdown("**Équipements de Protection Individuelle (EPI) obligatoires :**")
        for equipement in info["epi"]:
            st.markdown(f"- {equipement}")
            
        st.subheader("Conduite à tenir en cas d'accident (Premiers secours)")
        with st.expander("Consignes d'urgence en cas de contact accidentel", expanded=True):
            st.error(f"**Projection sur la peau :** {info['secours']['peau']}")
            st.error(f"**Projection dans les yeux :** {info['secours']['yeux']}")
            st.error(f"**En cas d'ingestion :** {info['secours']['ingestion']}")
            st.caption("Alerte générale : Informer immédiatement le professeur ou le responsable.")
            
        st.subheader("Réaction Chimique")
        st.markdown(f"**Observation visuelle :** Formation d'un précipité de couleur {info['couleur']}.")
        st.markdown(f"**Nom du produit formé (précipité) :** {info['precipite']}")
        
        try:
            st.image(
                info["image_reaction"],
                caption=f"Schéma : Ajout du réactif au goutte-à-goutte et coloration finale ({info['couleur']})",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Dessin de l'expérience manquant : {info['image_reaction']}")
            
        st.markdown("**Équation-bilan de la réaction :**")
        st.latex(info["equation"])

    st.write("---")
    if "ions_verrouille_tab" not in st.session_state:
        st.session_state.ions_verrouille_tab = False
    verrou_at_ions = st.session_state.ions_verrouille_tab

    afficher_questions_ions_securite_dynamiques(verrouille=verrou_at_ions)

    st.write("---")
    st.subheader("Synthèse et validation de l'atelier chimie")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ions = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier Identification des Ions et Securite.",
        key="check_certif_ions_final_net",
        disabled=verrou_at_ions,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER CHIMIE",
        key="btn_export_ions_official_net",
        use_container_width=True,
        disabled=verrou_at_ions,
    ):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_ions: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # Correction du Quiz (Atelier Ions)
            score_q_ions = 0.0
            if "ordre_quiz_tab_ions" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab_ions:
                    reponse = st.session_state.get(
                        f"ion_at6_final_g_{q_item['id']}", "Choisir..."
                    )
                    if str(reponse) == str(q_item["rep"]):
                        score_q_ions += 1.0

            # Correction des Trous (Atelier Ions)
            score_t_ions = sum(
                [
                    st.session_state.get("ion_t1_final") == "precipitation",
                    st.session_state.get("ion_t2_final") == "soude",
                    st.session_state.get("ion_t3_final") == "toxique",
                    st.session_state.get("ion_t4_final") == "blanc",
                    st.session_state.get("ion_t5_final") == "projection",
                    st.session_state.get("ion_t6_final") == "contamines",
                    st.session_state.get("ion_t7_final") == "pictogramme",
                    st.session_state.get("ion_t8_final") == "rouille",
                    st.session_state.get("ion_t9_final") == "anion",
                    st.session_state.get("ion_t10_final") == "secours",
                ]
            )

            st.session_state.score_ions_p1 = round(float(score_q_ions), 1)
            st.session_state.score_ions_p2 = round(float(score_t_ions), 1)
            st.session_state.score_final_ions = round(
                float(score_q_ions + score_t_ions), 1
            )
            st.session_state.ions_verrouille_tab = True
            st.rerun()

    # Génération du Document HTML Scellé (Atelier Ions)
    if st.session_state.get("ions_verrouille_tab", False):
        scr1 = st.session_state.get("score_ions_p1", 0.0)
        scr2 = st.session_state.get("score_ions_p2", 0.0)
        tot_s = st.session_state.get("score_final_ions", 0.0)

        from datetime import datetime, timedelta

        timestamp_ions = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d a %H:%M:%S"
        )

        st.success(
            f"ATELIER IDENTIFICATION DES IONS SCELLÉ | Note de session : {tot_s:.1f} / 20"
        )

        html_export_ions = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Identification des Ions et Securite - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0f766e; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
                .flex-container {{ display: flex; gap: 20px; margin-bottom: 25px; }}
                .flex-child {{ flex: 1; background: white; padding: 15px; border-radius: 4px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Rapport d'Evaluation de Chimie</h1>
                <p>Atelier : Identification des Ions et Securite au Laboratoire</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ions}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #7f7f7f;">
                Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier Chimie : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab_ions" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab_ions, 1):
                saisie = st.session_state.get(f"ion_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ions += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ions += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours avec Réponse</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous_ions = [
            ("1. La formation d'un solide insoluble en solution s'appelle une precipitation.", "ion_t1_final", "precipitation"),
            ("2. Pour detecter les ions metalliques positifs, on utilise de la soude.", "ion_t2_final", "soude"),
            ("3. Le chlorure de baryum possede le pictogramme du produit toxique.", "ion_t3_final", "toxique"),
            ("4. L'ion chlorure reagit avec le nitrate d'argent pour former un precipite blanc.", "ion_t4_final", "blanc"),
            ("5. Les lunettes de protection evitent les risques de projection oculaires.", "ion_t5_final", "projection"),
            ("6. En cas d'accident cutane, il faut retirer les vetements contamines.", "ion_t6_final", "contamines"),
            ("7. Le symbole SGH en forme de losange rouge encadre un pictogramme de danger.", "ion_t7_final", "pictogramme"),
            ("8. L'hydroxyde de fer III est un solide de couleur rouille.", "ion_t8_final", "rouille"),
            ("9. Un ion possedant une charge globale negative est un anion.", "ion_t9_final", "anion"),
            ("10. Rincer abondamment a l'eau est le premier geste de secours.", "ion_t10_final", "secours"),
        ]

        for num, (enonce, cle, attendu) in enumerate(phrases_trous_ions, 1):
            saisie = st.session_state.get(cle, "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_ions += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ions += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # Ajout du bouton de téléchargement pour le fichier HTML généré
        st.download_button(
            label="TELECHARGER LE RAPPORT D'EVALUATION EN HTML",
            data=html_export_ions,
            file_name=f"Rapport_Ions_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Applications concretes par domaine professionnel")
    st.write(
        "Selectionnez un domaine professionnel. Analysez la situation sur le terrain, "
        "puis choisissez le bon reactif chimique pour identifier l'ion suspect. Vous disposez de 3 tentatives maximum."
    )

    # Menu deroulant pour le choix du domaine professionnel
    domaine = st.selectbox(
        "Choisissez votre domaine d'activite :",
        ["Chauffeur Routier", "Maintenance des Engins", "Travaux Publics", "Géomètre"]
    )

    st.write("---")

    # Initialisation globale des compteurs de tentatives, notes et verrous dans le session_state
    if "essais_chauffeur" not in st.session_state:
        st.session_state.essais_chauffeur = 0
        st.session_state.verrou_chauffeur = False
        st.session_state.pts_chauffeur = 0
        
    if "essais_maintenance" not in st.session_state:
        st.session_state.essais_maintenance = 0
        st.session_state.verrou_maintenance = False
        st.session_state.pts_maintenance = 0
        
    if "essais_tp" not in st.session_state:
        st.session_state.essais_tp = 0
        st.session_state.verrou_tp = False
        st.session_state.pts_tp = 0
        
    if "essais_geometre" not in st.session_state:
        st.session_state.essais_geometre = 0
        st.session_state.verrou_geometre = False
        st.session_state.pts_geometre = 0

    if domaine == "Chauffeur Routier":
        st.subheader("Mission : Transport de matieres dangereuses et fuite de citerne")
        
        if "fuite_vol" not in st.session_state:
            st.session_state.fuite_vol = random.randint(10, 50)
            st.session_state.citerne_id = random.randint(1000, 9999)
            
        st.write(
            f"Lors du transport d'un lot de solutions industrielles (Citerne ID-{st.session_state.citerne_id}), "
            f"une fuite suspecte d'environ {st.session_state.fuite_vol} litres emane du raccord de purge. "
            f"Le liquide bleuatre s'ecoule sur le sol du centre de fret. Vous suspectez la presence d'ions Cuivre II (Cu2+)."
        )
        
        reactif_choisi = st.selectbox(
            "Quel reactif devez-vous utiliser pour confirmer la presence des ions Cuivre II ?",
            ["Choisir...", "Soude (Hydroxyde de sodium)", "Nitrate d'argent", "Chlorure de baryum"],
            key="quiz_chauffeur",
            disabled=st.session_state.verrou_chauffeur
        )
        
        # Ajout d'un bouton physique pour valider l'action sans subir les rechargements automatiques
        if not st.session_state.verrou_chauffeur:
            if st.button("Valider le choix du reactif", key="btn_valider_chauffeur"):
                if reactif_choisi == "Choisir...":
                    st.warning("Veuillez selectionner un reactif avant de valider.")
                elif reactif_choisi == "Soude (Hydroxyde de sodium)":
                    if st.session_state.essais_chauffeur == 0: st.session_state.pts_chauffeur = 10
                    elif st.session_state.essais_chauffeur == 1: st.session_state.pts_chauffeur = 6
                    elif st.session_state.essais_chauffeur == 2: st.session_state.pts_chauffeur = 3
                    st.session_state.verrou_chauffeur = True
                    st.rerun()
                else:
                    st.session_state.essais_chauffeur += 1
                    if st.session_state.essais_chauffeur >= 3:
                        st.session_state.pts_chauffeur = 0
                        st.session_state.verrou_chauffeur = True
                        st.rerun()
                    else:
                        st.error(f"Ce reactif ne permettra pas de detecter les ions Cuivre II. Tentatives : {st.session_state.essais_chauffeur}/3. Reessayez.")

        # Affichage du resultat fige une fois le verrou active
        if st.session_state.verrou_chauffeur:
            # On verifie si le choix final propose lors du verrouillage etait le bon
            if st.session_state.get("quiz_chauffeur") == "Soude (Hydroxyde de sodium)":
                st.success(f"Correct ! L'ajout de soude provoque la formation immediate d'un precipite bleu intense. Points gagnes : {st.session_state.pts_chauffeur} pts.")
                try:
                    st.image("citerne_route.jpg", caption=f"Incident securise : Fuite identifiee sur la citerne ID-{st.session_state.citerne_id}.", use_container_width=True)
                except Exception:
                    st.error("Image d'illustration manquante : citerne_route.jpg")
            else:
                st.error("Mission echouee (3 tentatives epuisees). La reponse attendue etait : Soude (Hydroxyde de sodium). Note : 0 pt.")
                
            st.markdown("**Consignes de securite ADR applicables immediatement :**")
            st.warning(
                "Le produit identifie est le sulfate de cuivre. Il est corrosif (GHS05) et dangereux pour l'environnement (GHS09). "
                "Enfilez vos gants en nitrile et vos lunettes de protection, puis balisez la zone pour empecher l'acces aux egouts."
            )

    # --- 2. MAINTENANCE DES ENGINS ---
    elif domaine == "Maintenance des Engins":
        st.subheader("Mission : Usure anormale et corrosion des blocs moteurs")
        
        if "moteur_heures" not in st.session_state:
            st.session_state.moteur_heures = random.randint(1500, 5000)
            st.session_state.fer_taux = round(random.uniform(5.5, 25.0), 1)
            
        st.write(
            f"Un engin de chantier affiche {st.session_state.moteur_heures} heures de service. Lors de la vidange "
            f"du circuit de refroidissement, le liquide presente une coloration suspecte. Vous suspectez une usure "
            f"des pieces en fonte liberant des ions Fer II (Fe2+) a hauteur de {st.session_state.fer_taux} mg/L."
        )
        
        reactif_choisi = st.selectbox(
            "Quel reactif devez-vous utiliser pour confirmer la presence des ions Fer II ?",
            ["Choisir...", "Soude (Hydroxyde de sodium)", "Nitrate d'argent", "Chlorure de baryum"],
            key="quiz_maintenance",
            disabled=st.session_state.verrou_maintenance
        )
        
        # Ajout du bouton de validation pour securiser le compteur d'essais
        if not st.session_state.verrou_maintenance:
            if st.button("Valider le choix du reactif", key="btn_valider_maintenance"):
                if reactif_choisi == "Choisir...":
                    st.warning("Veuillez selectionner un reactif avant de valider.")
                elif reactif_choisi == "Soude (Hydroxyde de sodium)":
                    if st.session_state.essais_maintenance == 0: st.session_state.pts_maintenance = 10
                    elif st.session_state.essais_maintenance == 1: st.session_state.pts_maintenance = 6
                    elif st.session_state.essais_maintenance == 2: st.session_state.pts_maintenance = 3
                    st.session_state.verrou_maintenance = True
                    st.rerun()
                else:
                    st.session_state.essais_maintenance += 1
                    if st.session_state.essais_maintenance >= 3:
                        st.session_state.pts_maintenance = 0
                        st.session_state.verrou_maintenance = True
                        st.rerun()
                    else:
                        st.error(f"Mauvais choix. Ce reactif ne precipite pas avec les ions Fer II. Tentatives : {st.session_state.essais_maintenance}/3. Reessayez.")

        # Affichage stable apres validation ou verrouillage
        if st.session_state.verrou_maintenance:
            if st.session_state.get("quiz_maintenance") == "Soude (Hydroxyde de sodium)":
                st.success(f"Correct ! L'ajout de soude met en evidence les ions Fer II par l'apparition d'un precipite vert pale. Points gagnes : {st.session_state.pts_maintenance} pts.")
                try:
                    st.image("maintenance_moteur.jpg", caption=f"Analyse d'atelier : Usure mesuree apres {st.session_state.moteur_heures} heures de service.", use_container_width=True)
                except Exception:
                    st.error("Image d'illustration manquante : maintenance_moteur.jpg")
            else:
                st.error("Mission echouee (3 tentatives epuisees). La reponse attendue etait : Soude (Hydroxyde de sodium). Note : 0 pt.")
                
            st.markdown("**Action de maintenance validee :**")
            st.write(
                "La corrosion du bloc moteur est confirmee. Vous devez purger integralement le circuit de refroidissement, "
                "rincer le bloc et injecter un liquide neuf enrichi en agents inhibiteurs de corrosion."
            )

    # --- 3. TRAVAUX PUBLICS ---
    elif domaine == "Travaux Publics":
        st.subheader("Mission : Pollution des eaux de fouille sur un chantier")
        
        if "fouille_prof" not in st.session_state:
            st.session_state.fouille_prof = round(random.uniform(2.0, 6.0), 1)
            st.session_state.eau_ph = round(random.uniform(8.2, 11.5), 1)
            
        st.write(
            f"Lors du coulage de fondations a une profondeur de {st.session_state.fouille_prof} metres, de l'eau "
            f"s'accumule dans la tranchee. Le pH mesure est anormalement eleve ({st.session_state.eau_ph}). Vous suspectez "
            "une pollution par des rejets d'adjuvants riches en ions Chlorure (Cl-)."
        )
        
        reactif_choisi = st.selectbox(
            "Quel reactif devez-vous verser pour confirmer la presence des ions Chlorure ?",
            ["Choisir...", "Soude (Hydroxyde de sodium)", "Nitrate d'argent", "Chlorure de baryum"],
            key="quiz_tp",
            disabled=st.session_state.verrou_tp
        )
        
        # Ajout du bouton de validation pour securiser le compteur d'essais
        if not st.session_state.verrou_tp:
            if st.button("Valider le choix du reactif", key="btn_valider_tp"):
                if reactif_choisi == "Choisir...":
                    st.warning("Veuillez selectionner un reactif avant de valider.")
                elif reactif_choisi == "Nitrate d'argent":
                    if st.session_state.essais_tp == 0: st.session_state.pts_tp = 10
                    elif st.session_state.essais_tp == 1: st.session_state.pts_tp = 6
                    elif st.session_state.essais_tp == 2: st.session_state.pts_tp = 3
                    st.session_state.verrou_tp = True
                    st.rerun()
                else:
                    st.session_state.essais_tp += 1
                    if st.session_state.essais_tp >= 3:
                        st.session_state.pts_tp = 0
                        st.session_state.verrou_tp = True
                        st.rerun()
                    else:
                        st.error(f"Erreur. Ce reactif ne permet pas d'isoler les anions chlorure. Tentatives : {st.session_state.essais_tp}/3. Reessayez.")

        # Affichage stable apres validation ou verrouillage
        if st.session_state.verrou_tp:
            if st.session_state.get("quiz_tp") == "Nitrate d'argent":
                st.success(f"Correct ! Le nitrate d'argent forme un precipite blanc dense qui noircit a la lumiere. Points gagnes : {st.session_state.pts_tp} pts.")
                try:
                    st.image("eau_fouille.jpg", caption=f"Prelevement environnemental : Analyse de l'eau de la tranchee a {st.session_state.fouille_prof} metres.", use_container_width=True)
                except Exception:
                    st.error("Image d'illustration manquante : eau_fouille.jpg")
            else:
                st.error("Mission echouee (3 tentatives epuisees). La reponse attendue etait : Nitrate d'argent. Note : 0 pt.")
                
            st.markdown("**Decision de chantier obligatoire :**")
            st.warning(
                "La pollution est averee. Il est strictement interdit de rejeter cette eau dans le reseau pluvial ou le milieu naturel. "
                "Deployez la pompe de chantier vers la cuve de neutralisation mobile avant de reprendre les travaux."
            )
    elif domaine == "Géomètre":
        st.subheader("Mission : Expertise de sol sur un ancien site industriel")

        # Initialisation de la note specifique au geometre
        if "pts_geometre" not in st.session_state:
            st.session_state.pts_geometre = 0

        if "sol_parcelle" not in st.session_state:
            st.session_state.sol_parcelle = random.choice(["A-102", "B-405", "C-88", "D-312"])
            st.session_state.sulfates_val = random.randint(400, 2500)
            
        st.write(
            f"Dans le cadre d'un diagnostic foncier sur la parcelle {st.session_state.sol_parcelle}, vous effectuez un forage. "
            f"L'eau de la nappe presente une forte agressivite potentielle pour les futurs betons, typique des ions Sulfate (SO42-) "
            f"dont la concentration estimee est de {st.session_state.sulfates_val} ppm."
        )
        
        reactif_choisi = st.selectbox(
            "Quel reactif devez-vous utiliser pour valider la presence des ions Sulfate ?",
            ["Choisir...", "Soude (Hydroxyde de sodium)", "Nitrate d'argent", "Chlorure de baryum"],
            key="quiz_geometre",
            disabled=st.session_state.verrou_geometre
        )
        
        # Ajout du bouton de validation pour securiser le compteur d'essais
        if not st.session_state.verrou_geometre:
            if st.button("Valider le choix du reactif", key="btn_valider_geometre"):
                if reactif_choisi == "Choisir...":
                    st.warning("Veuillez selectionner un reactif avant de valider.")
                elif reactif_choisi == "Chlorure de baryum":
                    if st.session_state.essais_geometre == 0: st.session_state.pts_geometre = 10
                    elif st.session_state.essais_geometre == 1: st.session_state.pts_geometre = 6
                    elif st.session_state.essais_geometre == 2: st.session_state.pts_geometre = 3
                    st.session_state.verrou_geometre = True
                    st.rerun()
                else:
                    st.session_state.essais_geometre += 1
                    if st.session_state.essais_geometre >= 3:
                        st.session_state.pts_geometre = 0
                        st.session_state.verrou_geometre = True
                        st.rerun()
                    else:
                        st.error(f"Ce reactif ne reagit pas avec l'ion sulfate. Tentatives : {st.session_state.essais_geometre}/3. Reessayez.")

        # Affichage stable apres validation ou verrouillage
        if st.session_state.verrou_geometre:
            if st.session_state.get("quiz_geometre") == "Chlorure de baryum":
                st.success(f"Correct ! Le chlorure de baryum reagit instantanement avec les sulfates pour former un precipite blanc. Points gagnes : {st.session_state.pts_geometre} pts.")
                try:
                    st.image("geometre_sol.jpg", caption=f"Mesures topographiques et carottage : Parcelle {st.session_state.sol_parcelle}.", use_container_width=True)
                except Exception:
                    st.error("Image d'illustration manquante : geometre_sol.jpg")
            else:
                st.error("Mission echouee (3 tentatives epuisees). La reponse attendue etait : Chlorure de baryum. Note : 0 pt.")
                
            st.markdown("**Recommandations officielles a inscrire dans votre rapport :**")
            st.write(
                f"La presence de sulfates ({st.session_state.sulfates_val} ppm) sur la parcelle {st.session_state.sol_parcelle} necessite "
                "l'usage obligatoire d'un ciment hautement sulfate (type ES ou PM) pour les fondations afin d'eviter l'eclatement des futurs batiments."
            )

    st.write("---")
    if "exemples_verrouille_tab" not in st.session_state:
        st.session_state.exemples_verrouille_tab = False
    verrou_at_exemples = st.session_state.exemples_verrouille_tab

    questions_par_metier = {
        "Chauffeur Routier": {
            "quiz": [
                {"id": "ch1", "q": "Quelle est la nature chimique de la fuite bleue ?", "options": ["Sulfate de cuivre", "Chlorure de sodium", "Acide chlorhydrique"], "rep": "Sulfate de cuivre"},
                {"id": "ch2", "q": "Quel equipement de securite ADR le chauffeur doit-il enfiler ?", "options": ["Gants nitrile et lunettes", "Casque antibruit", "Gilet haute visibilite simple"], "rep": "Gants nitrile et lunettes"},
                {"id": "ch3", "q": "Quel ion donne la coloration bleue au precipite ?", "options": ["Cuivre II (Cu2+)", "Fer II (Fe2+)", "Sulfate (SO42-)"], "rep": "Cuivre II (Cu2+)"},
                {"id": "ch4", "q": "Quel automatisme de securite le chauffeur doit-il appliquer au depot ?", "options": ["Baliser et confiner la fuite", "Laver a grande eau vers l'egout", "Continuer sa route"], "rep": "Baliser et confiner la fuite"},
                {"id": "ch5", "q": "Le code de danger GHS05 associe a la soude signifie :", "options": ["Produit corrosif", "Produit explosif", "Gaz sous pression"], "rep": "Produit corrosif"},
                {"id": "ch6", "q": "Ou le chauffeur trouve-t-of les consignes de securite ?", "options": ["Dans sa sacoche de bord (FDS/ADR)", "Sur internet", "Sur le tableau de bord"], "rep": "Dans sa sacoche de bord (FDS/ADR)"},
                {"id": "ch7", "q": "Quelle est la couleur attendue lors du test positif a la soude ?", "options": ["Bleu intense", "Vert bouteille", "Blanc opaque"], "rep": "Bleu intense"},
                {"id": "ch8", "q": "La fuite de sulfate de cuivre presente un risque majeur pour :", "options": ["L'environnement aquatique", "La carrosserie du camion", "Les pneus de l'engin"], "rep": "L'environnement aquatique"},
                {"id": "ch9", "q": "Quel est le role du laboratoire d'urgence dans ce cas ?", "options": ["Identifier l'ion pour adapter les secours", "Mesurer la charge", "Nettoyer la citerne"], "rep": "Identifier l'ion pour adapter les secours"},
                {"id": "ch10", "q": "Quel texte reglementaire encadre ce transport ?", "options": ["L'accord europeen ADR", "Le code de la route simple", "Le reglement interieur"], "rep": "L'accord europeen ADR"}
            ],
            "trous": [
                ("1. Le transport de produits chimiques est regi par la reglementation .........", ["Choisir...", "ADR", "SNCF"], "ADR", "ex_ch_t1"),
                ("2. Le liquide bleu contient des ions ......... mis en evidence par la soude.", ["Choisir...", "Cuivre II", "Sulfate"], "Cuivre II", "ex_ch_t2"),
                ("3. Le precipite obtenu presente une coloration caracteristique ..........", ["Choisir...", "bleue", "orange"], "bleue", "ex_ch_t3"),
                ("4. L'hydroxyde de sodium est une base forte tres .......... pour la peau.", ["Choisir...", "corrosive", "hydratante"], "corrosive", "ex_ch_t4"),
                ("5. Le chauffeur doit consulter la Fiche de .......... des Donnees Securite.", ["Choisir...", "Donnees", "Route"], "Donnees", "ex_ch_t5"),
                ("6. Pour proteger ses yeux des projections, le port de .......... est requis.", ["Choisir...", "lunettes", "visiere"], "lunettes", "ex_ch_t6"),
                ("7. Il faut empecher le produit de rejoindre le reseau des eaux ..........", ["Choisir...", "pluviales", "industrielles"], "pluviales", "ex_ch_t7"),
                ("8. L'identification chimique permet de connaitre les .......... du produit.", ["Choisir...", "dangers", "dimensions"], "dangers", "ex_ch_t8"),
                ("9. Le sulfate de cuivre est nocif pour les organismes ..........", ["Choisir...", "aquatiques", "terrestres"], "aquatiques", "ex_ch_t9"),
                ("10. Les secours appliquent un protocole de .......... de la zone polluee.", ["Choisir...", "neutralisation", "lavage"], "neutralisation", "ex_ch_t10")
            ]
        },
        "Maintenance des Engins": {
            "quiz": [
                {"id": "ma1", "q": "Quel ion provient de la degradation interne de la fonte du moteur ?", "options": ["Fer II (Fe2+)", "Cuivre II (Cu2+)", "Aluminium (Al3+)"], "rep": "Fer II (Fe2+)"},
                {"id": "ma2", "q": "Quelle est la couleur du precipite temoignant de la corrosion du bloc ?", "options": ["Vert pale", "Brun rouille", "Blanc"], "rep": "Vert pale"},
                {"id": "ma3", "q": "Quel reactif d'atelier utilise-t-on pour reveler les ions Fer II ?", "options": ["La soude", "Le nitrate d'argent", "L'acide chlorhydrique"], "rep": "La soude"},
                {"id": "ma4", "q": "Quelle operation mecanique immediate est validee par ce test ?", "options": ["Vidange et traitement anticorrosion", "Changement des pneus", "Reglage des phares"], "rep": "Vidange et traitement anticorrosion"},
                {"id": "ma5", "q": "Le fluide de refroidissement usage doit être jete :", "options": ["Dans un bac de recuperation specialise", "A l'egout de l'atelier", "Dans la benne tout-venant"], "rep": "Dans un bac de recuperation specialise"},
                {"id": "ma6", "q": "La presence de Fer II indique une degradation de quel type ?", "options": ["Chimique par corrosion", "Mecanique par friction", "Thermique par gel"], "rep": "Chimique par corrosion"},
                {"id": "ma7", "q": "Quel composant chimique previent ce phenomene dans un liquide neuf ?", "options": ["Un agent inhibiteur de corrosion", "De l'antigel pur", "De l'eau distillee"], "rep": "Un agent inhibiteur de corrosion"},
                {"id": "ma8", "q": "La formule du precipite d'hydroxyde de fer II est :", "options": ["Fe(OH)2", "Fe(OH)3", "FeCl2"], "rep": "Fe(OH)2"},
                {"id": "ma9", "q": "Quelle protection corporelle protege contre la soude en atelier ?", "options": ["La blouse et les gants nitrile", "Le bleu de travail en coton simple", "Le tablier de soudure"], "rep": "La blouse et les gants nitrile"},
                {"id": "ma10", "q": "Quel suivi permet d'anticiper la rupture du bloc moteur ?", "options": ["L'analyse reguliere des fluides", "Le controle visuel externe", "La mesure du niveau d'huile"], "rep": "L'analyse reguliere des fluides"}
            ],
            "trous": [
                ("1. La degradation des metaux en presence d'eau s'appelle la ..........", ["Choisir...", "corrosion", "abrasion"], "corrosion", "ex_ma_t1"),
                ("2. Le bloc moteur en fonte libere des cations de .......... dans le circuit.", ["Choisir...", "Fer II", "Zinc"], "Fer II", "ex_ma_t2"),
                ("3. Le reactif permettant de precipiter ces cations est la ..........", ["Choisir...", "soude", "baryum"], "soude", "ex_ma_t3"),
                ("4. La couleur du solide en suspension obtenu est ..........", ["Choisir...", "vert pale", "rouille"], "vert pale", "ex_ma_t4"),
                ("5. L'analyse des fluides previent la .......... mecanique de l'engin.", ["Choisir...", "panne", "vitesse"], "panne", "ex_ma_t5"),
                ("6. Le liquide de refroidissement contient un .......... pour bloquer la reaction.", ["Choisir...", "inhibiteur", "solvant"], "inhibiteur", "ex_ma_t6"),
                ("7. Les dechets chimiques de l'atelier suivent une filiere de .......... dediee.", ["Choisir...", "recyclage", "rejet"], "recyclage", "rejet"),
                ("8. Le technicien porte des gants en .......... pour manipuler les reactifs.", ["Choisir...", "nitrile", "laine"], "nitrile", "ex_ma_t7"),
                ("9. L'equation de precipitation produit un compose appele ..........", ["Choisir...", "hydroxyde", "chlorure"], "hydroxyde", "ex_ma_t8"),
                ("10. Ce diagnostic evite le remplacement complet du .......... moteur coutant cher.", ["Choisir...", "bloc", "radiateur"], "bloc", "ex_ma_t9")
            ]
        },
        "Travaux Publics": {
            "quiz": [
                {"id": "tp1", "q": "Quel ion indique une pollution par des adjuvants de betonnage ?", "options": ["Chlorure (Cl-)", "Sulfate (SO42-)", "Fer III (Fe3+)"], "rep": "Chlorure (Cl-)"},
                {"id": "tp2", "q": "Quel reactif permet de caracteriser la presence des chlorures ?", "options": ["Le nitrate d'argent", "Le chlorure de baryum", "L'hydroxyde de sodium"], "rep": "Le nitrate d'argent"},
                {"id": "tp3", "q": "Quelle particularite possede le precipite de chlorure d'argent ?", "options": ["Il noircit a la lumiere", "Il se dissout dans l'eau", "Il devient bleu"], "rep": "Il noircit a la lumiere"},
                {"id": "tp4", "q": "Une eau de fouille polluee doit être dirigee vers :", "options": ["Une unite de traitement/neutralisation mobile", "Le fosse communal", "La riviere adjacente"], "rep": "Une unite de traitement/neutralisation mobile"},
                {"id": "tp5", "q": "Quel parametre physique mesure en TP etait anormalement eleve ?", "options": ["Le pH de l'eau", "La temperature", "La turbidite"], "rep": "Le pH de l'eau"},
                {"id": "tp6", "q": "Pourquoi les chlorures sont-ils surveilles environnementalement ?", "options": ["Ils augmentent la salinite et nuisent a la faune", "Ils colorent l'eau en rouge", "Ils provoquent des odeurs"], "rep": "Ils augmentent la salinite et nuisent a la faune"},
                {"id": "tp7", "q": "La formule chimique du precipite blanc obtenu est :", "options": ["AgCl", "BaSO4", "NaCl"], "rep": "AgCl"},
                {"id": "tp8", "q": "En cas de test negatif au chlorure de baryum, on ecarte la presence de :", "options": ["Sulfates", "Chlorures", "Nitrates"], "rep": "Sulfates"},
                {"id": "tp9", "q": "Quelle autorite controle la conformite des rejets de chantiers ?", "options": ["Les inspecteurs de l'environnement (DREAL)", "Le chef d'equipe", "Le fournisseur de ciment"], "rep": "Les inspecteurs de l'environnement (DREAL)"},
                {"id": "tp10", "q": "Quelle installation de chantier stocke l'eau avant traitement ?", "options": ["Un bassin de decantation ou une cuve", "Une benne a gravats", "Une bache plastique simple"], "rep": "Un bassin de decantation ou une cuve"}
            ],
            "trous": [
                ("1. Les eaux stagnantes au fond des tranchees sont les eaux de ..........", ["Choisir...", "fouille", "source"], "fouille", "ex_tp_t1"),
                ("2. Un pH tres basique revele la presence de residus de ..........", ["Choisir...", "beton", "carburant"], "beton", "ex_tp_t2"),
                ("3. Le reactif utilise pour identifier l'anion chlorure is le .......... d'argent.", ["Choisir...", "nitrate", "sulfate"], "nitrate", "ex_tp_t3"),
                ("4. Le precipite blanc forme a la propriete de .......... au soleil.", ["Choisir...", "noircit", "fondre"], "noircit", "ex_tp_t4"),
                ("5. Le rejet direct de cette eau est interdit pour preserver le milieu ..........", ["Choisir...", "naturel", "urbain"], "naturel", "ex_tp_t5"),
                ("6. On installe une .......... de chantier pour vider la tranchee inondee.", ["Choisir...", "pompe", "grue"], "pompe", "ex_tp_t6"),
                ("7. Les additifs du ciment contiennent souvent des sels de .......... solubles.", ["Choisir...", "chlorure", "baryum"], "chlorure", "ex_tp_t7"),
                ("8. L'analyse chimique permet de valider le plan de gestion ..........", ["Choisir...", "environnemental", "financier"], "environnemental", "ex_tp_t8"),
                ("9. Le nitrate d'argent doit être manipule avec des gants pour eviter des ..........", ["Choisir...", "taches", "coupures"], "taches", "ex_tp_t9"),
                ("10. L'eau traitee doit être .......... avant son rejet final.", ["Choisir...", "neutralisee", "chauffee"], "neutralisee", "ex_tp_t10")
            ]
        },

        "Géomètre": {
            "quiz": [
                {"id": "ge1", "q": "Quel ion agressif pour le beton est recherche par le geometre ?", "options": ["Sulfate (SO42-)", "Chlorure (Cl-)", "Fer III (Fe3+)"], "rep": "Sulfate (SO42-)"},
                {"id": "ge2", "q": "Quel reactif specifique permet de caracteriser cet ion ?", "options": ["Le chlorure de baryum", "Le nitrate d'argent", "La soude"], "rep": "Le chlorure de baryum"},
                {"id": "ge3", "q": "Quelle est la couleur du precipite insoluble de sulfate de baryum ?", "options": ["Blanc", "Bleu", "Rouille"], "rep": "Blanc"},
                {"id": "ge4", "q": "Quelle est la consequence a long terme des sulfates sur un beton standard ?", "options": ["Son eclatement et sa fissuration", "Une augmentation de sa resistance", "Une impermeabilisation"], "rep": "Son eclatement et sa fissuration"},
                {"id": "ge5", "q": "Quel type de ciment le geometre conseille-t-il dans son rapport ?", "options": ["Ciment pour environnement sulfate (ES / PM)", "Ciment rapide", "Chaux aerienne"], "rep": "Ciment pour environnement sulfate (ES / PM)"},
                {"id": "ge6", "q": "Par quel moyen le geometre preleve-t-il l'eau en profondeur ?", "options": ["Par carottage et piezometre", "Avec un seau en surface", "Par observation satellite"], "rep": "Par carottage et piezometre"},
                {"id": "ge7", "q": "L'unite ppm utilisee pour la concentration signifie :", "options": ["Partie par million", "Poids par metre", "Precipite par minute"], "rep": "Partie par million"},
                {"id": "ge8", "q": "La presence de sulfates dans le sol provient generalement :", "options": ["D'anciens depots industriels ou du gypse", "De la pollution automobile", "De l'eau de pluie"], "rep": "D'anciens depots industriels ou du gypse"},
                {"id": "ge9", "q": "La formule du precipite de sulfate de baryum est :", "options": ["BaSO4", "BaCl2", "AgCl"], "rep": "BaSO4"},
                {"id": "ge10", "q": "A quel document officiel le geometre annexe-t-il ce diagnostic ?", "options": ["Le rapport d'expertise fonciere", "Le plan cadastral", "Le devis de terrassement"], "rep": "Le rapport d'expertise fonciere"}
            ],
            "trous": [
                ("1. Le geometre preleve des echantillons lors des operations de ..........", ["Choisir...", "carottage", "bornage"], "carottage", "ex_ge_t1"),
                ("2. L'eau souterraine de la nappe peut presenter une forte .......... chimique.", ["Choisir...", "agressivite", "purete"], "agressivite", "ex_ge_t2"),
                ("3. Pour identifier l'ion sulfate, on ajoute du chlorure de ..........", ["Choisir...", "baryum", "sodium"], "baryum", "ex_ge_t3"),
                ("4. La reaction produit instantanement un precipite de couleur ..........", ["Choisir...", "blanche", "verte"], "blanche", "ex_ge_t4"),
                ("5. Ce compose solide insoluble est le sulfate de ..........", ["Choisir...", "baryum", "cuivre"], "baryum", "ex_ge_t5"),
                ("6. Les sulfates provoquent a terme l'.......... des structures en beton.", ["Choisir...", "eclatement", "durcissement"], "eclatement", "ex_ge_t6"),
                ("7. L'analyse quantitative exprime la teneur en .......... (mg/L).", ["Choisir...", "ppm", "metres"], "ppm", "ex_ge_t7"),
                ("8. L'ingenieur structure doit choisir un ciment de type ..........", ["Choisir...", "ES", "standard"], "ES", "ES"),
                ("9. Ce diagnostic foncier securise la construction sur le plan ..........", ["Choisir...", "technique", "juridique"], "technique", "ex_ge_t8"),
                ("10. Le rapport redige est communique au maitre d'.......... du projet.", ["Choisir...", "ouvrage", "ecole"], "ouvrage", "ex_ge_t9")
            ]
        }
    }

    banque_active = questions_par_metier[domaine]
    st.session_state.ordre_quiz_exemples = banque_active["quiz"]

    col_quiz_ex, col_trous_ex = st.columns(2)

    with col_quiz_ex:
        st.markdown(f"##### Quiz Specifique : {domaine} (10 questions - 10 pts)")
        for idx, q_data in enumerate(banque_active["quiz"], 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ex_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrou_at_exemples, label_visibility="collapsed")

    with col_trous_ex:
        st.markdown(f"##### Synthese Textes a Trous : {domaine} (10 cases - 10 pts)")
        for enonce, choix, _, cle in banque_active["trous"]:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrou_at_exemples, label_visibility="collapsed")

    st.write("---")
    st.subheader("Synthese et validation des applications professionnelles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_ex = st.checkbox(
        f"Je certifie avoir complete les questions de l'Atelier Applications Metiers - Specialite {domaine}.",
        key="check_certif_ex_final_net",
        disabled=verrou_at_exemples,
    )

    if st.button(
        "VALIDER ET EXPORTER LE BILAN DES APPLICATIONS METIERS",
        key="btn_export_ex_official_net",
        use_container_width=True,
        disabled=verrou_at_exemples,
    ):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_ex: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # A. Correction du QCM dynamique - Max 10 pts
            score_q_ex = 0.0
            for q_item in banque_active["quiz"]:
                reponse = st.session_state.get(f"ex_at2_final_g_{q_item['id']}", "Choisir...")
                if str(reponse) == str(q_item["rep"]):
                    score_q_ex += 1.0

            # B. Correction des Trous dynamique - Max 10 pts
            score_t_ex = 0.0
            for _, _, attendu, cle in banque_active["trous"]:
                if st.session_state.get(cle) == attendu:
                    score_t_ex += 1.0

            # C. Recuperation de la note de terrain propre au metier choisi - Max 10 pts
            if domaine == "Chauffeur Routier":
                score_terrain_brut = st.session_state.get("pts_chauffeur", 0)
            elif domaine == "Maintenance des Engins":
                score_terrain_brut = st.session_state.get("pts_maintenance", 0)
            elif domaine == "Travaux Publics":
                score_terrain_brut = st.session_state.get("pts_tp", 0)
            else:
                score_terrain_brut = st.session_state.get("pts_geometre", 0)
                
            total_test_terrain = float(score_terrain_brut)

            st.session_state.score_terrain_total = round(total_test_terrain, 1)
            st.session_state.score_ex_p1 = round(float(score_q_ex), 1)
            st.session_state.score_ex_p2 = round(float(score_t_ex), 1)
            
            # Note globale sur 30 points (10 terrain + 10 quiz + 10 trous)
            st.session_state.score_final_ex = round(float(total_test_terrain + score_q_ex + score_t_ex), 1)
            st.session_state.exemples_verrouille_tab = True
            st.rerun()

    if st.session_state.get("exemples_verrouille_tab", False):
        scr_terrain = st.session_state.get("score_terrain_total", 0.0)
        scr1 = st.session_state.get("score_ex_p1", 0.0)
        scr2 = st.session_state.get("score_ex_p2", 0.0)
        tot_s = st.session_state.get("score_final_ex", 0.0)

        from datetime import datetime, timedelta
        timestamp_ex = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER APPLICATIONS PROFESSIONNELLES SCELLE | Note de session : {tot_s:.1f} / 30")

        html_export_ex = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Applications Professionnelles - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation - Chimie Appliquee</h1>
                <p>Atelier : Cas Reels de Terrain - Specialite activee : {domaine}</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_ex}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 30</div>
            </div>
            
            <div class="sub-title">Recapitulatif detaille des Notes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note Enquete de Terrain ({domaine}) : <strong>{scr_terrain:.1f} / 10</strong><br>
                Note obtenue au QCM dedie : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue aux Textes a Trous dedies : <strong>{scr2:.1f} / 10</strong><br>
                <strong>Note Totale de l'Atelier : {tot_s:.1f} / 30</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ SPECIALE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(banque_active["quiz"], 1):
            saisie = st.session_state.get(f"ex_at2_final_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_ex += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ex += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours avec Solution complete</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, (enonce, cle, attendu) in enumerate(banque_active["trous"], 1):
            saisie = st.session_state.get(cle, "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_ex += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_ex += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT DES APPLICATIONS PROFESSIONNELLES EN HTML",
            data=html_export_ex,
            file_name=f"Rapport_Applications_Metiers_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )































                    
