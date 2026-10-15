# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application sécurité électrique",
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
st.title("Application sécurité électrique")
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
    "Généralités sur l'électricité",
    "La tension électrique",
    "L'intensité électrique",
    "La puissance électrique",
    "L'énergie électrique",
    "Les danger de l électricité",
    ""
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_questions_generalites_intensite_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le module de l'Intensité Électrique
    ordre_fixe_intensite = [
        {"id": "i1_1", "q": "Quelle formule mathématique définit l'intensité du courant électrique par rapport à la charge Q et au temps t ?", "options": ["I = Q / t", "I = Q * t", "I = t / Q"], "rep": "I = Q / t"},
        {"id": "i1_2", "q": "Quel physicien a donné son nom à l'unité de mesure de l'intensité électrique ?", "options": ["André-Marie Ampère", "Alessandro Volta", "James Prescott Joule"], "rep": "André-Marie Ampère"},
        {"id": "i1_3", "q": "Quel appareil historique utilisait une aiguille magnétique pour mesurer de faibles courants ?", "options": ["Le galvanomètre", "Le thermocouple", "L'oscilloscope"], "rep": "Le galvanomètre"},
        {"id": "i1_4", "q": "Quel outil moderne permet de mesurer l'intensité sans couper ni ouvrir le fil électrique ?", "options": ["La pince ampèremétrique", "Le multimètre en série", "Le voltmètre en parallèle"], "rep": "La pince ampèremétrique"},
        {"id": "i1_5", "q": "Dans un circuit en dérivation (parallèle), quelle loi régit le comportement des intensités ?", "options": ["La loi des noeuds", "La loi des mailles", "La loi d'unicité des tensions"], "rep": "La loi des noeuds"},
        {"id": "i1_6", "q": "Comment évolue l'intensité totale débitée par le générateur si l'on ajoute des branches en dérivation ?", "options": ["Elle augmente", "Elle diminue", "Elle reste strictement identique"], "rep": "Elle augmente"},
        {"id": "i1_7", "q": "Quelle est la valeur approximative de la résistance électrique lors d'un court-circuit franc ?", "options": ["Proche de 0 Ohm", "Proche de 230 Ohms", "Proche de l'infini"], "rep": "Proche de 0 Ohm"},
        {"id": "i1_8", "q": "Quel effet thermique, lié à une forte intensité, provoque la fusion des câbles et les incendies ?", "options": ["L'effet Joule", "L'effet Peltier", "L'effet photoélectrique"], "rep": "L'effet Joule"},
        {"id": "i1_9", "q": "À partir de quelle valeur d'intensité en courant alternatif survient la tétanisation musculaire (seuil de non-lâcher) ?", "options": ["10 mA", "0.5 mA", "30 mA"], "rep": "10 mA"},
        {"id": "i1_10", "q": "Quel composant de protection fond et ouvre le circuit en cas de surintensité ou de court-circuit ?", "options": ["Le fusible", "Le rhéostat", "Le condensateur"], "rep": "Le fusible"}
    ]
    
    st.session_state.ordre_quiz_elec_tab3 = ordre_fixe_intensite
    col_double_quiz_elec, col_double_trous_elec = st.columns(2)

    with col_double_quiz_elec:
        st.markdown("##### Quiz sur l'intensité et les circuits (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_intensite, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"at6_quiz_intensite_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_elec:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. L'intensité du courant représente le débit de charges électriques, notée")
        with c2: st.selectbox("", ["Choisir...", "I", "U", "R"], key="at6_intensite_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'unité de mesure officielle du débit d'électrons est l'")
        with c4: st.selectbox("", ["Choisir...", "Ampère", "Volt", "Ohm"], key="at6_intensite_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Les anciens appareils de mesure à aiguille mécanique s'appelaient des")
        with c6: st.selectbox("", ["Choisir...", "galvanomètres", "oscilloscopes", "wattmètres"], key="at6_intensite_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une mesure d'intensité sans contact direct avec le cuivre utilise une")
        with c8: st.selectbox("", ["Choisir...", "pince", "pointe", "aiguille"], key="at6_intensite_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le seuil de non-lâcher provoquant la tétanisation musculaire est de 10")
        with c10: st.selectbox("", ["Choisir...", "mA", "A", "kA"], key="at6_intensite_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Un montage où les récepteurs sont connectés en parallèle s'appelle en")
        with c12: st.selectbox("", ["Choisir...", "dérivation", "série", "cascade"], key="at6_intensite_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La somme des courants individuels des branches donne l'intensité")
        with c14: st.selectbox("", ["Choisir...", "totale", "nulle", "moyenne"], key="at6_intensite_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Mettre en contact accidentel direct la Phase et le Neutre crée un")
        with c16: st.selectbox("", ["Choisir...", "court-circuit", "isolement", "couplage"], key="at6_intensite_t8", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. L'échauffement thermique des câbles sous forte intensité provient de l'effet")
        with c18: st.selectbox("", ["Choisir...", "Joule", "Volta", "Hall"], key="at6_intensite_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour interrompre une surintensité dangereuse, on utilise un disjoncteur ou un")
        with c20: st.selectbox("", ["Choisir...", "fusible", "rhéostat", "inverseur"], key="at6_intensite_t10", disabled=verrouille, label_visibility="collapsed")
        
    return
                             
def afficher_questions_generalites_electricite_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour l'Atelier 6 Électricité
    ordre_fixe_elec = [
        {"id": "e1_1", "q": "Quelle loi physique lie la tension, la résistance et l'intensité du courant ?", "options": ["La loi d'Ohm", "La loi de Joule", "La loi de Newton"], "rep": "La loi d'Ohm"},
        {"id": "e1_2", "q": "À partir de quelle intensité de courant alternatif survient le risque d'asphyxie par paralysie respiratoire ?", "options": ["0.5 mA", "10 mA", "30 mA"], "rep": "30 mA"},
        {"id": "e1_3", "q": "Quel effet physiologique immédiat caractérise le seuil de non-lâcher (10 mA) ?", "options": ["La tétanisation musculaire", "La fibrillation ventriculaire", "Un simple picotement"], "rep": "La tétanisation musculaire"},
        {"id": "e1_4", "q": "Quel organe vital est principalement menacé par une fibrillation ventriculaire lors d'un choc électrique ?", "options": ["Le coeur", "Les poumons", "Le foie"], "rep": "Le coeur"},
        {"id": "e1_5", "q": "Comment évolue la résistance électrique du corps humain lorsque la peau est mouillée ?", "options": ["Elle diminue fortement", "Elle reste identique", "Elle augmente fortement"], "rep": "Elle diminue fortement"},
        {"id": "e1_6", "q": "Quelle est la valeur de la sensibilité maximale des disjoncteurs différentiels protégeant les personnes dans un logement ?", "options": ["30 mA", "500 mA", "16 A"], "rep": "30 mA"},
        {"id": "e1_7", "q": "Quelle est la valeur nominale de la tension alternative délivrée par une prise de courant domestique standard en France ?", "options": ["12 V", "230 V", "400 V"], "rep": "230 V"},
        {"id": "e1_8", "q": "Par convention, quel nom donne-t-on au contact direct d'une personne avec un conducteur actif normalement sous tension ?", "options": ["Un contact direct", "Un contact indirect", "Un court-circuit"], "rep": "Un contact direct"},
        {"id": "e1_9", "q": "Quelle grandeur électrique, exprimée en Ampères, est le facteur direct de la gravité des dommages dans le corps ?", "options": ["L'intensité du courant", "La tension de la source", "La résistance globale"], "rep": "L'intensité du courant"},
        {"id": "e1_10", "q": "Quelle est la première action à mener face à une victime d'électrisation avant de la toucher ?", "options": ["Couper le courant", "Pratiquer un massage cardiaque", "Arroser la victime d'eau"], "rep": "Couper le courant"}
    ]

    st.session_state.ordre_quiz_elec_tab6 = ordre_fixe_elec

    col_double_quiz_elec, col_double_trous_elec = st.columns(2)

    with col_double_quiz_elec:
        st.markdown("##### Quiz sur les risques électriques (10 questions - 10 pts)")
        
        for idx, q_data in enumerate(ordre_fixe_elec, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"elec_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            
            st.selectbox(
                "", 
                options=opts_affichees,
                key=cle_select,
                disabled=verrouille, 
                label_visibility="collapsed"
            )

    with col_double_trous_elec:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le passage du courant dans le corps obéit à la loi d'")
        with c2: st.selectbox("", ["Choisir...", "Ohm", "Joule", "Ampère"], key="elec_t1_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le courant dangereux traverse l'organisme si une différence de potentiel ou")
        with c4: st.selectbox("", ["Choisir...", "tension", "puissance", "fréquence"], key="elec_t2_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La barrière principale du corps face à l'électricité est assurée par la")
        with c6: st.selectbox("", ["Choisir...", "peau", "circulation", "masse musculaire"], key="elec_t3_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Une immersion ou une humidité élevée fait chuter fortement la")
        with c8: st.selectbox("", ["Choisir...", "résistance", "tension", "fréquence"], key="elec_t4_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. À partir de 10 mA, la contraction involontaire empêche le lâcher du")
        with c10: st.selectbox("", ["Choisir...", "conducteur", "disjoncteur", "fusible"], key="elec_t5_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le seuil critique provoquant l'asphyxie respiratoire est fixé à 30")
        with c12: st.selectbox("", ["Choisir...", "mA", "A", "V"], key="elec_t6_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Un courant très intense (plus de 500 mA) engendre une fibrillation du")
        with c14: st.selectbox("", ["Choisir...", "coeur", "poumon", "cerveau"], key="elec_t7_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. En aval d'une installation, la protection des personnes repose sur le")
        with c16: st.selectbox("", ["Choisir...", "différentiel", "fusible", "contacteur"], key="elec_t8_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le terme qualifiant les blessures ou effets du passage du courant est l'")
        with c18: st.selectbox("", ["Choisir...", "électrisation", "électrocution", "induction"], key="elec_t9_tab6_final", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. En cas d'accident, la priorité absolue est d'interrompre ou couper le")
        with c20: st.selectbox("", ["Choisir...", "courant", "secours", "câblage"], key="elec_t10_tab6_final", disabled=verrouille, label_visibility="collapsed")
        
    return

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

#with tab1:



#with tab2:
            

with tab3:

    st.title("Atelier Pédagogique : L'Intensité Électrique et ses Dangers")



    # --- ONGLES PRINCIPAUX ---
    tab_cours, tab_simulation, tab_images, tab_quiz = st.tabs([
        "Document de Cours & Histoire", 
        "Simulation de Circuits & Courts-circuits", 
        "Vos Photos / Schémas JPG", 
        "Quiz & Évaluation Officielle"
    ])

    # ==========================================
    # ONGLET 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    with tab_cours:
        st.header("Document de Cours : L'Intensité Électrique")
        
        st.subheader("1. Origine et Définition de l'Intensité")
        st.write(
            "L'intensité du courant électrique correspond au débit de charges électriques à travers "
            "la section d'un conducteur par unité de temps. Elle s'exprime en **Ampères (A)**, en hommage à "
            "André-Marie Ampère. Mathématiquement, $I = Q / t$, où $Q$ est la charge en Coulombs et $t$ le temps en secondes."
        )
        
        st.subheader("2. Évolution des Appareils de Mesure : De l'Ancien à nos Jours")
        st.write(
            "- **Le Galvanomètre thermique ou à aiguille (Ancien) :** Utilisait l'effet magnétique ou thermique du courant "
            "pour faire dévier une aiguille mécanique sur un cadran gradué. La lecture nécessitait des calculs de calibres complexes.\n"
            "- **L'Ampèremètre Numérique (Moderne) :** Mesure la chute de tension aux bornes d'une résistance interne connue (shunt) "
            "et affiche directement la valeur sur écran LCD de manière précise.\n"
            "- **La Pince Ampèremétrique (Actuel) :** Permet de mesurer l'intensité par induction magnétique autour du fil, "
            "sans avoir à ouvrir ou couper le circuit électrique."
        )
        
        st.subheader("3. Dangers de l'Ampérage sur l'Organisme")
        st.write(
            "Ce n'est pas la tension qui tue, mais l'intensité du courant qui traverse les organes vitaux. "
            "Voici les seuils critiques pour un courant alternatif de 50 Hz :"
        )
        df_seuils_cours = pd.DataFrame({
            "Intensité (mA)": ["0.5 mA", "10 mA", "30 mA", "500 mA ou plus"],
            "Effet Physiologique": [
                "Seuil de perception (léger picotement)", 
                "Seuil de non-lâcher (tétanisation musculaire involontaire)", 
                "Seuil de paralysie respiratoire (asphyxie)", 
                "Fibrillation ventriculaire (arrêt cardiaque irréversible sans défibrillateur)"
            ]
        })
        st.table(df_seuils_cours)

    # ==========================================
    # ONGLET 2 : SIMULATION DE CIRCUITS
    # ==========================================
    with tab_simulation:
        st.header("Simulation Dynamique : Circuit en Dérivation et Court-circuit")
        st.write(
            "Un circuit en dérivation (ou parallèle) divise le courant. La loi des nœuds s'applique : "
            "l'intensité totale est égale à la somme des intensités des branches ($I_{totale} = I_1 + I_2 + ...$)."
        )
        
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            st.subheader("Configuration des Récepteurs")
            tension_source = st.slider("Tension du générateur (Volt)", 5, 240, 230, step=5)
            R1 = st.slider("Résistance de la Lampe 1 (Ohm)", 10, 1000, 500, step=10)
            R2 = st.slider("Résistance de la Lampe 2 (Ohm)", 10, 1000, 250, step=10)
            
            simuler_court_circuit = st.checkbox("Provoquer un COURT-CIRCUIT (Rapprochement direct Phase/Neutre)", value=False)

        with col_sim2:
            st.subheader("Résultats et Mesures de l'Intensité")
            
            if simuler_court_circuit:
                # En court-circuit la résistance tend vers 0.1 Ohm (résistance des fils filaires)
                R_cc = 0.1
                i_total = tension_source / R_cc
                st.error(f"COURT-CIRCUIT DÉTECTÉ ! L'intensité s'emballe à : {i_total:.1f} A")
                st.markdown(
                    "**Conséquences du court-circuit :** Échauffement violent par effet Joule ($P = R \cdot I^2$), "
                    "fusion des isolants, risque d'incendie immédiat et destruction des équipements si aucun fusible ou disjoncteur ne coupe le circuit."
                )
            else:
                i1 = tension_source / R1
                i2 = tension_source / R2
                i_total = i1 + i2
                
                st.metric(label="Courant Branche 1 (I1)", value=f"{i1:.3f} A")
                st.metric(label="Courant Branche 2 (I2)", value=f"{i2:.3f} A")
                st.info(f"**Intensité Totale (Loi des nœuds) :** {i_total:.3f} A")
                st.write("Dans un circuit en dérivation, plus on ajoute d'appareils en parallèle, plus l'intensité totale demandée au générateur augmente.")


    with tab_images:
        st.header("Visualisation de vos documents JPG")
        st.write("Importez vos photos d'ampèremètres anciens, schémas de dérivation ou de courts-circuits ci-dessous.")
        
        fichiers_images = st.file_uploader(
            "Choisissez vos photos (.jpg ou .jpeg)", 
            type=["jpg", "jpeg"], 
            accept_multiple_files=True
        )
        
        if fichiers_images:
            for img_file in fichiers_images:
                st.image(img_file, caption=f"Fichier : {img_file.name}", use_container_width=True)
        else:
            st.info("En attente de l'importation de vos fichiers JPG.")



    if "vin_verrouille_tab3" not in st.session_state:
        st.session_state.vin_verrouille_tab3 = False

    verrou_at3 = st.session_state.vin_verrouille_tab3

    # Appel propre de la fonction d'affichage dans le tab3
    try:
        afficher_questions_generalites_electricite_dynamiques(verrouille=verrou_at3)
    except NameError:
        pass

    st.write("---")
    st.subheader("Validation du module Risques Électriques")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.", 
        key="check_certif_elec_final_net_tab3", 
        disabled=verrou_at3
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE (ONGLET 3) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_elec3_official_net", use_container_width=True, disabled=verrou_at3):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin3:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q3 = 0.0
            if "ordre_quiz_elec_tab6" in st.session_state:
                for q_item in st.session_state.ordre_quiz_elec_tab6:
                    reponse_eleve = st.session_state.get(f"elec_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q3 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t3 = sum([
                st.session_state.get("elec_t1_tab6_final") == "Ohm",
                st.session_state.get("elec_t2_tab6_final") == "tension",
                st.session_state.get("elec_t3_tab6_final") == "peau",
                st.session_state.get("elec_t4_tab6_final") == "résistance",
                st.session_state.get("elec_t5_tab6_final") == "conducteur",
                st.session_state.get("elec_t6_tab6_final") == "mA",
                st.session_state.get("elec_t7_tab6_final") == "coeur",
                st.session_state.get("elec_t8_tab6_final") == "différentiel",
                st.session_state.get("elec_t9_tab6_final") == "électrisation",
                st.session_state.get("elec_t10_tab6_final") == "courant"
            ])

            st.session_state.score_vin3_p1 = round(float(score_q3), 1)
            st.session_state.score_vin3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_vin3 = round(float(score_q3 + score_t3), 1)
            st.session_state.vin_verrouille_tab3 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 3 ---
    if st.session_state.get("vin_verrouille_tab3", False):
        scr1 = st.session_state.get("score_vin3_p1", 0.0)
        scr2 = st.session_state.get("score_vin3_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin3", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin3 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER RISQUES ÉLECTRIQUES SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Électricité Risques - {n_eleve}</title>
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
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 3 : Généralités et dangers de l'électricité</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Risques Électriques : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 3 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_elec_tab6" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab6, 1):
                saisie = st.session_state.get(f"elec_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_elec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous3 = [
            ("1. Le passage du courant dans le corps obéit à la loi d'", "Ohm", "elec_t1_tab6_final"),
            ("2. Le courant dangereux traverse l'organisme si une différence de potentiel ou", "tension", "elec_t2_tab6_final"),
            ("3. La barrière principale du corps face à l'électricité est assurée par la", "peau", "elec_t3_tab6_final"),
            ("4. Une immersion ou une humidité élevée fait chuter fortement la", "résistance", "elec_t4_tab6_final"),
            ("5. À partir de 10 mA, la contraction involontaire empêche le lâcher du", "conducteur", "elec_t5_tab6_final"),
            ("6. Le seuil critique provoquant l'asphyxie respiratoire est fixé à 30", "mA", "elec_t6_tab6_final"),
            ("7. Un courant très intense (plus de 500 mA) engendre une fibrillation du", "coeur", "elec_t7_tab6_final"),
            ("8. En aval d'une installation, la protection des personnes repose sur le", "différentiel", "elec_t8_tab6_final"),
            ("9. Le terme qualifiant les blessures ou effets du passage du courant est l'", "électrisation", "elec_t9_tab6_final"),
            ("10. En cas d'accident, la priorité absolue est d'interrompre ou couper le", "courant", "elec_t10_tab6_final")
        ]

        for num, (texte, attendu, cle_session) in enumerate(phrases_trous3, 1):
            saisie = st.session_state.get(cle_session, "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_elec += f"<tr><td>{num}</td><td>{texte} [...]</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="Télécharger le rapport officiel au format HTML",
            data=html_export_elec,
            file_name=f"Bilan_Risques_Electricite_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


        
#with tab4:



#with tab5:



with tab6:


    st.set_page_config(page_title="Simulateur des Dangers de l'Électricité", layout="wide")

    st.title("Simulateur Pédagogique : Les Dangers de l'Électricité")
    st.write(
        "Cette application simule le passage du courant électrique à travers le corps humain "
        "en fonction de la tension (Volt) et de la résistance (Ohm), selon la loi d'Ohm (I = U / R)."
    )

    # --- SECTION 1 : PARAMÈTRES DE SIMULATION ---
    st.header("1. Paramètres de la simulation")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Source de Tension")
        tension_type = st.radio(
            "Sélectionnez une situation courante :",
            ["Pile standard (9V)", "Prise domestique (230V)", "Haute Tension (1000V) ou plus", "Personnalisé"]
        )
        
        if tension_type == "Pile standard (9V)":
            tension = 9.0
        elif tension_type == "Prise domestique (230V)":
            tension = 230.0
        elif tension_type == "Haute Tension (1000V) ou plus":
            tension = 1000.0
        else:
            tension = st.slider("Tension personnalisée (Volt)", min_value=1.0, max_value=2000.0, value=230.0, step=1.0)
            
        st.metric(label="Tension choisie (U)", value=f"{tension} V")

    with col2:
        st.subheader("Résistance du Corps Humain")
        etat_peau = st.selectbox(
            "État de la peau / environnement :",
            ["Peau sèche (Résistance élevée ~ 50 000 Ω)", 
             "Peau humide / transpiration (~ 5 000 Ω)", 
             "Peau mouillée / pieds dans l'eau (~ 1 000 Ω)",
             "Peau immergée / blessure (~ 500 Ω)"]
        )
        
        if "séche" in etat_peau or "sèche" in etat_peau:
            resistance = 50000.0
        elif "humide" in etat_peau:
            resistance = 5000.0
        elif "mouillée" in etat_peau:
            resistance = 1000.0
        else:
            resistance = 500.0
            
        st.metric(label="Résistance estimée (R)", value=f"{int(resistance)} Ω")

    # --- SECTION 2 : CALCULS ET RÉSULTATS ---
    # Loi d'Ohm : I = U / R (en Ampères, multiplié par 1000 pour les mA)
    courant_ampere = tension / resistance
    courant_ma = courant_ampere * 1000

    st.header("2. Résultat du calcul (Loi d'Ohm)")
    st.info(f"**Intensité du courant traversant le corps (I = U / R) :** {courant_ma:.2f} mA (soit {courant_ampere:.4f} A)")

    # Détermination des effets physiologiques (Courant alternatif 50 Hz standard)
    danger_level = "Sûr"
    description = "Aucun effet ressenti."
    color = "green"

    if courant_ma >= 500:
        danger_level = "DANGER DE MORT IMMÉDIAT (Arrêt Cardiaque)"
        description = "Fibrillation ventriculaire irréversible en quelques millisecondes, arrêt cardiaque, brûlures internes graves."
        color = "red"
    elif courant_ma >= 30:
        danger_level = "DANGER CRITIQUE (Asphyxie)"
        description = "Seuil de paralysie respiratoire (asphyxie). Si le courant persiste, la mort par suffocation survient rapidement."
        color = "orange"
    elif courant_ma >= 10:
        danger_level = "RISQUE MODÉRÉ (Contraction / Tétanisation)"
        description = "Seuil de non-lâcher. Les muscles se contractent involontairement, impossible de lâcher la source électrique."
        color = "yellow"
    elif courant_ma >= 0.5:
        danger_level = "Perception / Secousse"
        description = "Seuil de perception. Légère sensation de picotement ou secousse musculaire sans conséquences graves immédiates."
        color = "blue"

    # Affichage du diagnostic de danger
    st.markdown(f"### Statut : <span style='color:{color}; font-weight:bold;'>{danger_level}</span>", unsafe_allow_html=True)
    st.warning(f"**Effet sur l'organisme :** {description}")

    # --- SECTION 3 : ÉCHELLE DU DANGER (RÉFÉRENCE) ---
    st.header("3. Échelle de référence des courants (50 Hz)")

    data = {
        "Intensité (mA)": ["0.5 mA", "10 mA", "30 mA", "500 mA+"],
        "Seuil / Effet": [
            "Seuil de perception (picotement)",
            "Seuil de non-lâcher (tétanisation musculaire)",
            "Seuil de paralysie respiratoire (asphyxie)",
            "Fibrillation ventriculaire (arrêt cardiaque)"
        ],
        "Gravité": ["Bénin", "Inquiétant", "Très Dangereux", "Mortel"]
    }
    df_seuils = pd.DataFrame(data)
    st.table(df_seuils)

    # Règles de sécurité fondamentales
    st.subheader("Rappels de sécurité")
    st.markdown("""
    - **30 mA** est la sensibilité maximale des disjoncteurs différentiels protégeant les vies humaines dans les habitations.
    - L'eau diminue drastiquement la résistance de la peau, rendant une tension de 230V systématiquement mortelle en milieu humide.
    """)

    if "vin_verrouille_tab6" not in st.session_state:
        st.session_state.vin_verrouille_tab6 = False

    verrou_at6 = st.session_state.vin_verrouille_tab6

    # Appel propre de la fonction d'affichage de l'Atelier 6
    try:
        afficher_questions_generalites_intensite_dynamiques(verrouille=verrou_at6)
    except NameError:
        pass

    st.write("---")
    st.subheader("Validation du module Intensité et Risques")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin6 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 6.", 
        key="check_certif_elec_final_net_tab6", 
        disabled=verrou_at6
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE INTENSITÉ (ATELIER 6) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 6", key="btn_export_elec6_official_net", use_container_width=True, disabled=verrou_at6):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin6:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz d'Intensité (10 points)
            score_q6 = 0.0
            if "ordre_quiz_elec_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_elec_tab3:
                    reponse_eleve = st.session_state.get(f"at6_quiz_intensite_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q6 += 1.0

            # 2. Correction des Textes à trous d'Intensité (10 points)
            score_t6 = sum([
                st.session_state.get("at6_intensite_t1") == "I",
                st.session_state.get("at6_intensite_t2") == "Ampère",
                st.session_state.get("at6_intensite_t3") == "galvanomètres",
                st.session_state.get("at6_intensite_t4") == "pince",
                st.session_state.get("at6_intensite_t5") == "mA",
                st.session_state.get("at6_intensite_t6") == "dérivation",
                st.session_state.get("at6_intensite_t7") == "totale",
                st.session_state.get("at6_intensite_t8") == "court-circuit",
                st.session_state.get("at6_intensite_t9") == "Joule",
                st.session_state.get("at6_intensite_t10") == "fusible"
            ])

            st.session_state.score_vin6_p1 = round(float(score_q6), 1)
            st.session_state.score_vin6_p2 = round(float(score_t6), 1)
            st.session_state.score_final_vin6 = round(float(score_q6 + score_t6), 1)
            st.session_state.vin_verrouille_tab6 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 6 ---
    if st.session_state.get("vin_verrouille_tab6", False):
        scr1 = st.session_state.get("score_vin6_p1", 0.0)
        scr2 = st.session_state.get("score_vin6_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin6", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin6 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER INTENSITÉ SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Intensité Électrique - {n_eleve}</title>
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
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 6 : Intensité, Dérivation et Courts-circuits</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Propriétés de l'Intensité : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 6 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_elec_tab3" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab3, 1):
                saisie = st.session_state.get(f"at6_quiz_intensite_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_elec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DÉTAILLÉE DES TROUS DE SYNTHÈSE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Énoncé de Cours</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous6 = [
            ("1. L'intensité du courant représente le débit de charges électriques, notée", "I", "at6_intensite_t1"),
            ("2. L'unité de mesure officielle du débit d'électrons est l'", "Ampère", "at6_intensite_t2"),
            ("3. Les anciens appareils de mesure à aiguille mécanique s'appelaient des", "galvanomètres", "at6_intensite_t3"),
            ("4. Une mesure d'intensité sans contact direct avec le cuivre utilise une", "pince", "at6_intensite_t4"),
            ("5. Le seuil de non-lâcher provoquant la tétanisation musculaire est de 10", "mA", "at6_intensite_t5"),
            ("6. Un montage où les récepteurs sont connectés en parallèle s'appelle en", "dérivation", "at6_intensite_t6"),
            ("7. La somme des courants individuels des branches donne l'intensité", "totale", "at6_intensite_t7"),
            ("8. Mettre en contact accidentel direct la Phase et le Neutre crée un", "court-circuit", "at6_intensite_t8"),
            ("9. L'échauffement thermique des câbles sous forte intensité provient de l'effet", "Joule", "at6_intensite_t9"),
            ("10. Pour interrompre une surintensité dangereuse, on utilise un disjoncteur ou un", "fusible", "at6_intensite_t10")
        ]

        for num, (texte, attendu, cle_session) in enumerate(phrases_trous6, 1):
            saisie = st.session_state.get(cle_session, "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_elec += f"<tr><td>{num}</td><td>{texte} [...]</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        st.download_button(
            label="Télécharger le rapport officiel au format HTML",
            data=html_export_elec,
            file_name=f"Bilan_Intensite_Electricite_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )    
