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
    "Les protections",
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
tab7 = onglets[7]

def afficher_simulateur_incidents_et_consequences():
    import streamlit as st
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches

    st.markdown("### Simulateur d'Incidents Électriques et Conséquences")
    st.write(
        "Comparez le comportement d'une installation moderne aux normes "
        "avec une installation défectueuse ou obsolète lors d'un incident."
    )

    # --- CONFIGURATION DU TYPE D'INSTALLATION ---
    st.markdown("##### 1. État de l'armoire électrique")
    installation_conforme = st.radio(
        "Sélectionnez le niveau de sécurité du tableau :",
        options=["Aux normes actuelles (Disjoncteurs et Différentiel 30 mA opérationnels)", 
                 "Vétuste / Défectueux (Protections bloquées ou absentes)"],
        index=0,
        key="radio_conformite_tab7"
    )

    is_conforme = (installation_conforme == "Aux normes actuelles (Disjoncteurs et Différentiel 30 mA opérationnels)")

    # --- SÉLECTION DE L'INCIDENT ---
    st.markdown("##### 2. Choix de l'incident domestique")
    incident = st.selectbox(
        "Choisissez une situation à tester :",
        options=[
            "Aucun - Fonctionnement normal",
            "Surcharge : Four + Bouilloire + Machine sur une multiprise",
            "Court-circuit : Un enfant met des ciseaux métalliques dans une prise",
            "Défaut d'isolement : Fuite d'eau interne dans le lave-vaisselle qui touche la carcasse"
        ],
        key="select_incident_tab7"
    )

    st.divider()

    # --- TRAITEMENT DES SCÉNARIOS ET RENDU VISUEL ---
    fig, ax = plt.subplots(figsize=(4, 5))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    if incident == "Aucun - Fonctionnement normal":
        st.success("Situation : Tout va bien. Le courant circule de manière stable dans les conducteurs.")
        
        # Dessin Manette HAUTE (ON)
        ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#e2e8f0'))
        ax.add_patch(patches.Rectangle((0.4, 0.4), 0.2, 0.3, color='#1e293b'))
        ax.plot([0.5, 0.5], [0.55, 0.85], color='#ef4444', linewidth=10, solid_capstyle='round')
        ax.add_patch(patches.Circle((0.5, 0.25), 0.06, color='#10b981'))
        ax.text(0.5, 0.22, "I", color='white', fontsize=12, fontweight='bold', ha='center')
        ax.set_title("DISJONCTEUR ENCLENCHÉ (ON)")
        st.pyplot(fig)

    elif incident == "Surcharge : Four + Bouilloire + Machine sur une multiprise":
        if is_conforme:
            st.info("Cas Conforme : Le disjoncteur divisionnaire détecte l'échauffement des câbles.")
            st.error("Action du tableau : Le disjoncteur thermique saute correctement et coupe la ligne.")
            st.success("Conséquence : Les câbles refroidissent. Aucun risque d'incendie.")
            
            # Dessin Manette BASSE (OFF)
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "SURCHARGE", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
            ax.set_title("DISJONCTEUR OUVERT (OFF)")
        else:
            st.error("Cas Vétuste : Il ne se passe absolument rien au tableau. Le vieux fusible ou disjoncteur reste bloqué.")
            st.warning("Conséquence dramatique : Le courant excessif continue de traverser la multiprise. Les fils fondent sous l'effet Joule, le plastique s'enflamme : DÉBUT D'INCENDIE HABITATION.")
            
            # Dessin Manette bloquée en HAUT malgré le danger
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#991b1b'))
            ax.text(0.5, 0.5, "FEU / INCENDIE", color='white', fontsize=12, fontweight='bold', ha='center')
            ax.set_title("DÉFAILLANCE SYSTÈME")
        st.pyplot(fig)

    elif incident == "Court-circuit : Un enfant met des ciseaux métalliques dans une prise":
        if is_conforme:
            st.info("Cas Conforme : L'intensité monte à plusieurs milliers d'ampères. Le déclencheur magnétique réagit en moins de 10 millisecondes.")
            st.error("Action du tableau : Le disjoncteur saute instantanément avec un claquement sec.")
            st.success("Conséquence : Le courant est coupé avant même que l'arc électrique n'ait pu brûler l'enfant ou détruire la prise.")
            
            # Dessin Manette BASSE (OFF)
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "COURT-CIRCUIT", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
            ax.set_title("DISJONCTEUR OUVERT (OFF)")
        else:
            st.error("Cas Vétuste : Les contacts restent soudés ou le vieux fusible ne fond pas. Il ne se passe rien au tableau.")
            st.warning("Conséquence dramatique : Une explosion de chaleur se produit au niveau de la prise de courant. L'arc électrique provoque de graves brûlures aux mains et au visage de l'enfant et projette des matières en fusion.")
            
            # Dessin Explosion
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#7f1d1d'))
            ax.text(0.5, 0.5, "EXPLOSION PRISE", color='white', fontsize=11, fontweight='bold', ha='center')
            ax.set_title("DANGER DE MORT")
        st.pyplot(fig)

    elif incident == "Défaut d'isolement : Fuite d'eau interne dans le lave-vaisselle qui touche la carcasse":
        if is_conforme:
            st.info("Cas Conforme : L'eau conduit l'électricité vers l'enveloppe en métal de la machine. Le courant de fuite part vers le fil de Terre (PE).")
            st.error("Action du tableau : L'interrupteur différentiel voit la fuite dépasser 30 mA et coupe immédiatement l'électricité de toute la rangée.")
            st.success("Conséquence : Si une personne touche la machine à laver, elle ne sentira rien du tout. Elle est sauvée de l'électrocution.")
            
            # Dessin Manette BASSE (OFF)
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "FUITE 30mA", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
            ax.set_title("DIFFÉRENTIEL OUVERT (OFF)")
        else:
            st.error("Cas Vétuste : Pas de dispositif différentiel 30 mA ou absence de prise de terre. Il ne se passe rien au niveau du tableau.")
            st.warning("Conséquence dramatique : La carcasse métallique reste sous une tension de 230V. Dès que quelqu'un touche l'appareil les pieds sur le carrelage, le courant traverse son cœur pour rejoindre le sol : ÉLECTROCUTION (ARRÊT CARDIAQUE DE L'UTILISATEUR).")
            
            # Dessin Alerte Électrocution
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#7f1d1d'))
            ax.text(0.5, 0.5, "ÉLECTROCUTION", color='white', fontsize=11, fontweight='bold', ha='center')
            ax.set_title("CHOC ÉLECTRIQUE MORTEL")
        st.pyplot(fig)

    return


def afficher_questions_protections_dynamiques(verrouille=False):
    import streamlit as st
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from datetime import datetime, timedelta

    # Ordre fixe stable pour le module des Protections - Tab 7
    ordre_fixe_protections = [
        {"id": "p7_1", "q": "Quel appareil est conçu spécifiquement pour protéger les personnes contre les risques d'électrocution ?", "options": ["Le dispositif différentiel 30 mA", "Le disjoncteur divisionnaire", "Le parafoudre"], "rep": "Le dispositif différentiel 30 mA"},
        {"id": "p7_2", "q": "À partir de quelle intensité de courant traversant le corps humain le risque de fibrillation cardiaque devient-il immédiat ?", "options": ["30 mA", "10 mA", "500 mA"], "rep": "30 mA"},
        {"id": "p7_3", "q": "Quel fil conducteur de l'installation possède une double fonction d'acheminement du courant et de couleur bleue obligatoire ?", "options": ["Le Neutre", "La Phase", "La Terre"], "rep": "Le Neutre"},
        {"id": "p7_4", "q": "Quelle anomalie électrique est détectée par le déclencheur thermique d'un disjoncteur divisionnaire ?", "options": ["La surcharge électrique", "Le court-circuit", "La fuite à la terre"], "rep": "La surcharge électrique"},
        {"id": "p7_5", "q": "Quelle est la valeur maximale réglementaire de la résistance d'une prise de terre selon la norme NF C 15-100 en habitation ?", "options": ["100 Ohms", "50 Ohms", "500 Ohms"], "rep": "100 Ohms"},
        {"id": "p7_6", "q": "Quel dispositif protège l'onduleur et les appareils électroniques sensibles contre les surtensions causées par la foudre ?", "options": ["Le parafoudre", "Le disjoncteur général", "L'interrupteur différentiel"], "rep": "Le parafoudre"},
        {"id": "p7_7", "q": "Quelle action mensuelle est recommandée pour s'assurer du bon fonctionnement mécanique d'un interrupteur différentiel ?", "options": ["Appuyer sur le bouton Test", "Couper le disjoncteur général", "Mesurer la tension aux bornes"], "rep": "Appuyer sur le bouton Test"},
        {"id": "p7_8", "q": "Si la Phase et le Neutre entrent directement en contact, quelle anomalie majeure se produit instantanément ?", "options": ["Un court-circuit", "Une surcharge", "Une baisse de tension"], "rep": "Un court-circuit"},
        {"id": "p7_9", "q": "Où est envoyé le courant de fuite par le dispositif différentiel lorsqu'un défaut d'isolement survient sur un équipement ?", "options": ["Vers la prise de terre", "Vers le réseau public", "Vers le conducteur neutre"], "rep": "Vers la prise de terre"},
        {"id": "p7_10", "q": "Quel type de disjoncteur s'ouvre lorsque l'intensité totale consommée dépasse la puissance souscrite de l'abonnement ?", "options": ["Le disjoncteur général", "Le disjoncteur divisionnaire", "Le disjoncteur de branchement"], "rep": "Le disjoncteur général"}
    ]
    
    st.session_state.ordre_quiz_protec_tab7 = ordre_fixe_protections
    col_double_quiz_prot, col_double_trous_prot = st.columns(2)

    with col_double_quiz_prot:
        st.markdown("##### Quiz sur la protection des personnes et installations (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_protections, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"protec_at7_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_prot:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Pour éviter l'électrocution, le seuil de sensibilité humaine maximum toléré est fixé à")
        with c2: st.selectbox("", ["Choisir...", "30 mA", "500 mA", "10 A"], key="protec_t1_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le dispositif différentiel coupe le circuit s'il repère une différence entre la phase et le")
        with c4: st.selectbox("", ["Choisir...", "neutre", "terre", "parafoudre"], key="protec_t2_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'évacuation des courants de défaut vers le sol est assurée par la prise de")
        with c6: st.selectbox("", ["Choisir...", "terre", "courant", "phase"], key="protec_t3_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c4_1, c4_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c4_1: st.write("4. Une surconsommation d'appareils sur une même ligne engendre une dangereuse")
        with c4_2: st.selectbox("", ["Choisir...", "surcharge", "surtension", "fréquence"], key="protec_t4_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c5_1, c5_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5_1: st.write("5. Le contact accidentel et direct entre le fil de phase et le fil de neutre crée un")
        with c5_2: st.selectbox("", ["Choisir...", "court-circuit", "défaut d'isolement", "effet Joule"], key="protec_t5_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c6_1, c6_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c6_1: st.write("6. La protection thermique intégrée au disjoncteur divisionnaire protège contre la")
        with c6_2: st.selectbox("", ["Choisir...", "surcharge", "foudre", "tension"], key="protec_t6_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c7_1, c7_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7_1: st.write("7. La protection magnétique d'un disjoncteur réagit instantanément lors d'un")
        with c7_2: st.selectbox("", ["Choisir...", "court-circuit", "courant faible", "vieillissement"], key="protec_t7_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c8_1, c8_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c8_1: st.write("8. Le composant chargé de dévier l'énergie de la foudre vers le sol s'appelle le")
        with c8_2: st.selectbox("", ["Choisir...", "parafoudre", "fusible", "contacteur"], key="protec_t8_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c9_1, c9_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9_1: st.write("9. La norme réglementant l'ensemble de l'installation électrique intérieure est la")
        with c9_2: st.selectbox("", ["Choisir...", "NF C 15-100", "NF C 13-100", "ISO 9001"], key="protec_t9_tab7_final", disabled=verrouille, label_visibility="collapsed")

        c10_1, c10_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c10_1: st.write("10. Pour s'assurer de l'efficacité de la terre, sa résistance mesurée doit être inférieure à")
        with c10_2: st.selectbox("", ["Choisir...", "100 Ohms", "500 Ohms", "10 Ohms"], key="protec_t10_tab7_final", disabled=verrouille, label_visibility="collapsed")                     



def afficher_questions_generalites_energie_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le module de l'Energie Electrique - Tab 5
    ordre_fixe_energie = [
        {"id": "e1_1", "q": "Quelle formule relie l'énergie électrique E à la puissance P et au temps t ?", "options": ["E = P * t", "E = P / t", "E = U * I"], "rep": "E = P * t"},
        {"id": "e1_2", "q": "Quelle est l'unité légale de l'énergie dans le Système International (SI) ?", "options": ["Le Joule", "Le Watt", "Le Wattheure"], "rep": "Le Joule"},
        {"id": "e1_3", "q": "Quelle unité pratique est principalement utilisée par les fournisseurs d'électricité pour facturer l'énergie ?", "options": ["Le kilowattheure (kWh)", "Le Joule (J)", "Le Kilowatt (kW)"], "rep": "Le kilowattheure (kWh)"},
        {"id": "e1_4", "q": "Un appareil d'une puissance de 1000 W fonctionne pendant 2 heures. Quelle énergie a-t-il consommée ?", "options": ["2 kWh", "500 Wh", "2000 J"], "rep": "2 kWh"},
        {"id": "e1_5", "q": "Quel appareil de mesure est installé en tête d'une installation domestique pour comptabiliser l'énergie consommée ?", "options": ["Le compteur électrique", "Le wattmètre", "Le disjoncteur"], "rep": "Le compteur électrique"},
        {"id": "e1_6", "q": "Comment qualifie-t-on l'énergie thermique dissipée inutilement par un conducteur à cause de sa résistance électrique ?", "options": ["L'effet Joule", "L'effet photovoltaïque", "L'effet thermoélectrique"], "rep": "L'effet Joule"},
        {"id": "e1_7", "q": "Si on double le temps d'utilisation d'un récepteur sans changer sa puissance, comment évolue l'énergie consommée ?", "options": ["Elle double", "Elle reste identique", "Elle est divisée par deux"], "rep": "Elle double"},
        {"id": "e1_8", "q": "Quelle grandeur physique représente la quantité d'énergie qu'un appareil peut '.convertir par unité de temps ?", "options": ["La puissance", "La tension", "L'intensité"], "rep": "La puissance"},
        {"id": "e1_9", "q": "En courant continu, quelle formule permet de calculer la puissance P à partir de la tension U et de l'intensité I ?", "options": ["P = U * I", "P = U / I", "P = R * I"], "rep": "P = U * I"},
        {"id": "e1_10", "q": "Quel est le principal composant d'une installation électrique chargé de couper le courant en cas de surconsommation d'énergie globale ?", "options": ["Le disjoncteur général", "L'interrupteur horaire", "Le télérupteur"], "rep": "Le disjoncteur général"}
    ]
    
    st.session_state.ordre_quiz_elec_tab5 = ordre_fixe_energie
    col_double_quiz_ener, col_double_trous_ener = st.columns(2)

    with col_double_quiz_ener:
        st.markdown("##### Quiz sur l'énergie électrique (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_energie, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"energie_at5_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_ener:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La grandeur qui comptabilise le travail total fourni par un courant électrique est l'")
        with c2: st.selectbox("", ["Choisir...", "énergie", "puissance", "tension"], key="energie_t1_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'unité de mesure d'énergie correspondant à un watt pendant une seconde est le")
        with c4: st.selectbox("", ["Choisir...", "Joule", "Watt", "Volt"], key="energie_t2_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour simplifier la facturation, on utilise le kilowattheure qui équivaut à")
        with c6: st.selectbox("", ["Choisir...", "3600000 J", "1000 J", "3600 J"], key="energie_t3_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c4_1, c4_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c4_1: st.write("4. La vitesse à laquelle cette énergie est consommée ou délivrée définit la")
        with c4_2: st.selectbox("", ["Choisir...", "puissance", "fréquence", "période"], key="energie_t4_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c5_1, c5_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5_1: st.write("5. Le dégagement de chaleur provoqué par le passage du courant se nomme l'effet")
        with c5_2: st.selectbox("", ["Choisir...", "Joule", "Ohm", "Volta"], key="energie_t5_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c6_1, c6_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c6_1: st.write("6. Un appareil qui convertit l'énergie électrique en énergie mécanique est un")
        with c6_2: st.selectbox("", ["Choisir...", "moteur", "résistor", "générateur"], key="energie_t6_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c7_1, c7_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7_1: st.write("7. Le rapport entre l'énergie utile restituée et l'énergie absorbée est le")
        with c7_2: st.selectbox("", ["Choisir...", "rendement", "facteur", "calibre"], key="energie_t7_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c8_1, c8_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c8_1: st.write("8. Le compteur intelligent déployé en France pour mesurer l'énergie se nomme")
        with c8_2: st.selectbox("", ["Choisir...", "Linky", "Gazpar", "Aquarius"], key="energie_t8_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c9_1, c9_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9_1: st.write("9. Un kilowatt (kW) correspond à une puissance de conversion égale à")
        with c9_2: st.selectbox("", ["Choisir...", "1000 W", "100 W", "10000 W"], key="energie_t9_tab5_final", disabled=verrouille, label_visibility="collapsed")

        c10_1, c10_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c10_1: st.write("10. Pour réduire la consommation d'énergie, on doit privilégier les appareils de classe")
        with c10_2: st.selectbox("", ["Choisir...", "A", "G", "E"], key="energie_t10_tab5_final", disabled=verrouille, label_visibility="collapsed")                     

    return




def afficher_questions_generalites_puissance_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le module de la Puissance Électrique
    ordre_fixe_puissance = [
        {"id": "p1_1", "q": "Quelle grandeur physique correspond à l'énergie consommée ou fournie par unité de temps ?", "options": ["La puissance", "La tension", "L'intensité"], "rep": "La puissance"},
        {"id": "p1_2", "q": "Quel ingénieur écossais a donné son nom à l'unité de mesure de la puissance électrique ?", "options": ["James Watt", "Alessandro Volta", "André-Marie Ampère"], "rep": "James Watt"},
        {"id": "p1_3", "q": "En courant continu ou alternatif purement résistif, quelle formule lie la puissance à la tension U et à l'intensité I ?", "options": ["P = U * I", "P = U / I", "P = R * I"], "rep": "P = U * I"},
        {"id": "p1_4", "q": "Quelle formule exprime la puissance dissipée uniquement par effet Joule dans une résistance R ?", "options": ["P = R * I^2", "P = U^2 * R", "P = R * I"], "rep": "P = R * I^2"},
        {"id": "p1_5", "q": "Quel appareil historique à disque tournant mesurait la consommation d'énergie (liée à la puissance au cours du temps) ?", "options": ["Le compteur électromécanique", "Le wattmètre thermique", "Le galvanomètre"], "rep": "Le compteur électromécanique"},
        {"id": "p1_6", "q": "Quelle notation standard symbolise la grandeur de la puissance électrique dans les formules ?", "options": ["P", "W", "E"], "rep": "P"},
        {"id": "p1_7", "q": "Comment qualifie-t-on la puissance maximale qu'une installation peut supporter avant le déclenchement du disjoncteur ?", "options": ["La puissance souscrite", "La puissance réactive", "La puissance thermique"], "rep": "La puissance souscrite"},
        {"id": "p1_8", "q": "Quel outil moderne numérique affiche en temps réel la puissance instantanée consommée par un logement ?", "options": ["Le compteur Linky", "La pince wattmétrique", "L'oscilloscope"], "rep": "Le compteur Linky"},
        {"id": "p1_9", "q": "Si vous branchez simultanément trop d'appareils de forte puissance sur une multiprise, quel phénomène se produit ?", "options": ["Une surintensité par surcharge", "Une surtension réseau", "Une baisse de fréquence"], "rep": "Une surintensité par surcharge"},
        {"id": "p1_10", "q": "Quelle est l'unité de mesure couramment utilisée pour facturer l'énergie électrique, correspondant à une puissance de 1kW pendant une heure ?", "options": ["Le kilowatt-heure (kWh)", "Le Watt par seconde", "Le Joule-heure"], "rep": "Le kilowatt-heure (kWh)"}
    ]
    
    st.session_state.ordre_quiz_elec_tab4 = ordre_fixe_puissance
    col_double_quiz_elec, col_double_trous_elec = st.columns(2)

    with col_double_quiz_elec:
        st.markdown("##### Quiz sur la puissance et l'effet Joule (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_puissance, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"at4_quiz_puissance_q{idx}_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_elec:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La quantité d'énergie transformée par seconde définit la")
        with c2: st.selectbox("", ["Choisir...", "puissance", "tension", "résistance"], key="at4_puissance_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'unité légale de la puissance électrique dans le système international est le")
        with c4: st.selectbox("", ["Choisir...", "Watt", "Joule", "Volt"], key="at4_puissance_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Le produit de la tension par l'intensité donne la puissance")
        with c6: st.selectbox("", ["Choisir...", "active", "réactive", "apparente"], key="at4_puissance_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. La conversion d'énergie électrique en chaleur s'appelle l'effet")
        with c8: st.selectbox("", ["Choisir...", "Joule", "Peltier", "Seebeck"], key="at4_puissance_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. La formule de cette perte thermique par effet Joule s'écrit R fois I au")
        with c10: st.selectbox("", ["Choisir...", "carré", "cube", "double"], key="at4_puissance_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Les compteurs historiques qui mesuraient l'énergie globale étaient")
        with c12: st.selectbox("", ["Choisir...", "électromécaniques", "statiques", "inductifs"], key="at4_puissance_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Aujourd'hui, la relève de la puissance instantanée est automatisée par le compteur")
        with c14: st.selectbox("", ["Choisir...", "Linky", "Gazpar", "Volta"], key="at4_puissance_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. Accumuler trop d'appareils énergivores sur une même ligne crée une")
        with c16: st.selectbox("", ["Choisir...", "surcharge", "surtension", "coupure"], key="at4_puissance_t8", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. La puissance multipliée par la durée de fonctionnement donne l'")
        with c18: st.selectbox("", ["Choisir...", "énergie", "fréquence", "tension"], key="at4_puissance_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Pour facturer les abonnés, les fournisseurs utilisent le kilowatt-")
        with c20: st.selectbox("", ["Choisir...", "heure", "seconde", "jour"], key="at4_puissance_t10", disabled=verrouille, label_visibility="collapsed")
        
        
    return   



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

def afficher_questions_generalites_tension_dynamiques(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le module de la Tension Electrique
    ordre_fixe_tension = [
        {"id": "v1_1", "q": "Quelle grandeur physique correspond à la différence de potentiel électrique entre deux points ?", "options": ["La tension", "L'intensité", "La résistance"], "rep": "La tension"},
        {"id": "v1_2", "q": "Quel physicien italien a donné son nom à l'unité de mesure de la tension électrique ?", "options": ["Alessandro Volta", "André-Marie Ampère", "Georg Ohm"], "rep": "Alessandro Volta"},
        {"id": "v1_3", "q": "En milieu sec, quelle est la valeur limite de la tension de sécurité en courant alternatif (Très Basse Tension) ?", "options": ["50 V", "12 V", "230 V"], "rep": "50 V"},
        {"id": "v1_4", "q": "Quelle est la valeur de la tension de sécurité recommandée en milieu mouillé ou immergé ?", "options": ["12 V", "50 V", "24 V"], "rep": "12 V"},
        {"id": "v1_5", "q": "Comment appelle-t-on le contact d'une personne avec un conducteur actif normalement sous tension ?", "options": ["Un contact direct", "Un contact indirect", "Un court-circuit"], "rep": "Un contact direct"},
        {"id": "v1_6", "q": "Quelle notation standard symbolise la grandeur de la tension électrique dans les formules ?", "options": ["U", "I", "R"], "rep": "U"},
        {"id": "v1_7", "q": "Quel type de contact se produit lorsqu'une personne touche la carcasse métallique d'un appareil défectueux mis accidentellement sous tension ?", "options": ["Un contact indirect", "Un contact direct", "Une surtension"], "rep": "Un contact indirect"},
        {"id": "v1_8", "q": "Quel appareil utilise-t-on en parallèle pour mesurer directement la tension aux bornes d'un dipôle ?", "options": ["Le voltmètre", "L'ampèremètre", "Le ohmmètre"], "rep": "Le voltmètre"},
        {"id": "v1_9", "q": "Quelle est la tension nominale standard délivrée entre la phase et le neutre d'une prise domestique en France ?", "options": ["230 V", "400 V", "110 V"], "rep": "230 V"},
        {"id": "v1_10", "q": "Selon la loi d'Ohm, si la tension U augmente pour une résistance R constante, comment évolue l'intensité I ?", "options": ["Elle augmente proportionnellement", "Elle diminue", "Elle reste stable"], "rep": "Elle augmente proportionnellement"}
    ]
    
    st.session_state.ordre_quiz_elec_tab2 = ordre_fixe_tension
    col_double_quiz_elec, col_double_trous_elec = st.columns(2)

    with col_double_quiz_elec:
        st.markdown("##### Quiz sur la tension et les potentiels (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tension, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"tension_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_elec:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. La force qui pousse les électrons et crée une différence de potentiel est la")
        with c2: st.selectbox("", ["Choisir...", "tension", "intensité", "puissance"], key="tension_t1_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. L'unité internationale de mesure de la tension est le")
        with c4: st.selectbox("", ["Choisir...", "Volt", "Ampère", "Ohm"], key="tension_t2_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. Pour mesurer une tension électrique, le voltmètre doit se brancher en")
        with c6: st.selectbox("", ["Choisir...", "parallèle", "série", "dérivation"], key="tension_t3_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c4_1, c4_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c4_1: st.write("4. En milieu parfaitement sec, la tension limite de sécurité vaut")
        with c4_2: st.selectbox("", ["Choisir...", "50 V", "12 V", "24 V"], key="tension_t4_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c5_1, c5_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5_1: st.write("5. Lorsque le corps est immergé dans l'eau, cette limite descend à")
        with c5_2: st.selectbox("", ["Choisir...", "12 V", "24 V", "50 V"], key="tension_t5_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c6_1, c6_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c6_1: st.write("6. Toucher directement une phase sous tension constitue un contact")
        with c6_2: st.selectbox("", ["Choisir...", "direct", "indirect", "inductif"], key="tension_t6_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c7_1, c7_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7_1: st.write("7. Toucher une masse métallique sous tension suite à un défaut est un contact")
        with c7_2: st.selectbox("", ["Choisir...", "indirect", "direct", "capacitif"], key="tension_t7_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c8_1, c8_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c8_1: st.write("8. Sur le réseau domestique grand public, la tension mesurée est de")
        with c8_2: st.selectbox("", ["Choisir...", "230 V", "400 V", "110 V"], key="tension_t8_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c9_1, c9_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9_1: st.write("9. L'unité de la résistance électrique intervenant dans la loi d'expression de U est le")
        with c9_2: st.selectbox("", ["Choisir...", "Ohm", "Volt", "Watt"], key="tension_t9_tab2_final", disabled=verrouille, label_visibility="collapsed")

        c10_1, c10_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c10_1: st.write("10. Une élévation dangereuse ou anormale de la tension sur une installation s'appelle une")
        with c10_2: st.selectbox("", ["Choisir...", "surtension", "sous-tension", "coupure"], key="tension_t10_tab2_final", disabled=verrouille, label_visibility="collapsed")                     

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


def afficher_questions_generalites_electricite_dynamiques1(verrouille=False):
    import streamlit as st

    # Ordre fixe stable pour le module d'Electricite Generale - Tab 1
    ordre_fixe_generale = [
        {"id": "g1_1", "q": "Quelle particule élémentaire porte la charge électrique négative responsable du courant dans les métaux ?", "options": ["L'électron", "Le proton", "Le neutron"], "rep": "L'électron"},
        {"id": "g1_2", "q": "Quel savant américain a prouvé la nature électrique de la foudre à l'aide d'un cerf-volant ?", "options": ["Benjamin Franklin", "Thomas Edison", "Nikola Tesla"], "rep": "Benjamin Franklin"},
        {"id": "g1_3", "q": "Comment qualifie-t-on un matériau qui ne laisse pas passer le courant électrique ?", "options": ["Un isolant", "Un conducteur", "Un semi-conducteur"], "rep": "Un isolant"},
        {"id": "g1_4", "q": "Quel type de courant est produit par une pile ou une batterie chimique ?", "options": ["Le courant continu", "Le courant alternatif", "Le courant triphasé"], "rep": "Le courant continu"},
        {"id": "g1_5", "q": "Quelle est la principale source de production d'électricité décarbonée à grande échelle en France ?", "options": ["L'énergie nucléaire", "Le charbon", "Le gaz naturel"], "rep": "L'énergie nucléaire"},
        {"id": "g1_6", "q": "Quel composant d'un circuit électrique permet d'ouvrir ou de fermer le passage des électrons ?", "options": ["L'interrupteur", "Le fusible", "La résistance"], "rep": "L'interrupteur"},
        {"id": "g1_7", "q": "Comment appelle-t-on le déplacement ordonné de charges électriques dans un conducteur ?", "options": ["Le courant électrique", "La tension", "Le magnétisme"], "rep": "Le courant électrique"},
        {"id": "g1_8", "q": "Quel scientifique a inventé la première pile électrique en empilant des disques de cuivre et de zinc ?", "options": ["Alessandro Volta", "Michael Faraday", "James Watt"], "rep": "Alessandro Volta"},
        {"id": "g1_9", "q": "Quel est le risque principal pour l'Homme lors de la traversée du corps par un courant électrique ?", "options": ["L'électrisation", "La combustion", "L'inductance"], "rep": "L'électrisation"},
        {"id": "g1_10", "q": "Quel physicien français a donné son nom à l'unité de mesure de l'intensité du courant électrique ?", "options": ["André-Marie Ampère", "Charles de Coulomb", "Henri Becquerel"], "rep": "André-Marie Ampère"}
    ]
    
    st.session_state.ordre_quiz_elec_tab1 = ordre_fixe_generale
    col_double_quiz_gen, col_double_trous_gen = st.columns(2)

    with col_double_quiz_gen:
        st.markdown("##### Quiz sur l'électricité générale (10 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_generale, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"generale_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_double_trous_gen:
        st.markdown("##### Synthèse de cours (Texte à trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le courant électrique correspond à un déplacement ordonné de particules appelées")
        with c2: st.selectbox("", ["Choisir...", "électrons", "protons", "neutrons"], key="generale_t1_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Un matériau qui permet le passage du courant électrique se nomme un")
        with c4: st.selectbox("", ["Choisir...", "conducteur", "isolant", "diélectrique"], key="generale_t2_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. À l'inverse, l'air, le verre ou le plastique se comportent comme un")
        with c6: st.selectbox("", ["Choisir...", "isolant", "conducteur", "générateur"], key="generale_t3_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c4_1, c4_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c4_1: st.write("4. La première pile électrique de l'histoire a été inventée par le savant")
        with c4_2: st.selectbox("", ["Choisir...", "Volta", "Ampère", "Ohm"], key="generale_t4_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c5_1, c5_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5_1: st.write("5. Une pile chimique délivre un courant continu dont le sens va du pôle plus vers le pôle")
        with c5_2: st.selectbox("", ["Choisir...", "moins", "neutre", "terre"], key="generale_t5_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c6_1, c6_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c6_1: st.write("6. Un circuit électrique minimal doit comporter un récepteur et un")
        with c6_2: st.selectbox("", ["Choisir...", "générateur", "ampèremètre", "voltmètre"], key="generale_t6_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c7_1, c7_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7_1: st.write("7. Pour interrompre la circulation du courant à volonté, on insère un")
        with c7_2: st.selectbox("", ["Choisir...", "interrupteur", "fusible", "disjoncteur"], key="generale_t7_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c8_1, c8_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c8_1: st.write("8. Le courant fourni par les prises de courant de nos habitations est un courant")
        with c8_2: st.selectbox("", ["Choisir...", "alternatif", "continu", "statique"], key="generale_t8_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c9_1, c9_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9_1: st.write("9. La traversée accidentelle du corps humain par un courant électrique est une")
        with c9_2: st.selectbox("", ["Choisir...", "électrisation", "électrocution", "surcharge"], key="generale_t9_tab1_final", disabled=verrouille, label_visibility="collapsed")

        c10_1, c10_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c10_1: st.write("10. Lorsque le passage du courant électrique provoque directement la mort, on parle d'")
        with c10_2: st.selectbox("", ["Choisir...", "électrocution", "électrisation", "court-circuit"], key="generale_t10_tab1_final", disabled=verrouille, label_visibility="collapsed")                     

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


with tab1:
    st.title("Histoire et Fondements de l'Électricité")
    st.write("---")

    # ==========================================
    # SECTION 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    st.header("Histoire et Fondements de l'Électricité")
    
    st.subheader("1. Nature du Courant Électrique")
    st.write(
        "L'électricité n'a pas été inventée, elle a été découverte. Elle correspond à la manifestation de charges électriques "
        "portées par les constituants de l'atome. Dans un circuit métallique, le courant électrique est provoqué par le déplacement "
        "d'électrons libres (charges négatives) qui se déplacent de borne en borne."
    )
    
    st.subheader("2. Les Grandes Étapes Historiques")
    st.write(
        "- **L'Antiquité :** Thalès de Milet observe l'électricité statique en frottant de l'ambre jaune (appelé 'elektron' en grec) qui attire de petits corps légers.\n"
        "- **1800 - La Pile de Volta :** Alessandro Volta invente le premier générateur capable de fournir un courant continu stable en empilant des disques de métaux séparés par des feutres imbibés d'acide.\n"
        "- **La Guerre des Courants (Fin XIXe) :** Thomas Edison défend le courant continu pour l'éclairage urbain tandis que Nikola Tesla et George Westinghouse démontrent la supériorité du courant alternatif pour le transport de l'électricité sur de longues distances."
    )
    
    st.subheader("3. Sécurité et Effets sur l'Organisme")
    st.write(
        "Le corps humain est conducteur. Le passage d'un courant électrique à travers le corps peut provoquer des contractions "
        "musculaires, des brûlures ou un arrêt cardiaque. Il convient de distinguer l'électrisation (le courant traverse le corps) "
        "de l'électrocution (l'électrisation entraîne un décès immédiat)."
    )

    st.write("---")

    col_imga1, col_imga2 = st.columns(2)
    with col_imga1:
        # Remplacez "amperemetre_aiguille.jpg" par le nom exact de votre fichier
        try:
            st.image("amperemetre_aiguille.jpg", caption="Modèle analogique à aiguille (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'amperemetre_aiguille.jpg' dans le dossier du script pour afficher l'image.")

    with col_imga2:
        # Remplacez "amperemetre_numerique.jpg" par le nom exact de votre fichier
        try:
            st.image("amperemetre_numerique.jpg", caption="Modèle numérique de laboratoire (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'amperemetre_numerique.jpg' dans le dossier du script pour afficher l'image.")

    # ==========================================
    # SECTION 2 : SIMULATION LUDIQUE D'UN CIRCUIT
    # ==========================================
    st.header("Simulation Ludique : Mon Premier Circuit Électrique")
    st.write(
        "Manipulez les composants ci-dessous pour allumer le récepteur en toute sécurité."
    )
    
    col_g1, col_g2 = st.columns(2)
        
    with col_g1:
        st.subheader("Contrôle des Organes du Circuit")
        etat_generateur = st.radio("Source d'alimentation (Générateur) :", ["Éteint", "Allumé (Pile 9V)"], key="gen_radio_tab1")
        etat_interrupteur = st.selectbox("Position de l'interrupteur :", ["Ouvert (Le courant ne passe pas)", "Fermé (Le courant circule)"], key="int_select_tab1")
        type_recepteur = st.selectbox("Choisir le composant récepteur :", ["Lampe à incandescence", "Moteur rotatif", "Avertisseur sonore (Buzzer)"], key="rec_select_tab1")

    with col_g2:
        st.subheader("État de l'Installation")
        
        if etat_generateur == "Allumé (Pile 9V)" and etat_interrupteur == "Fermé (Le courant circule)":
            st.success("CIRCUIT ACTIF : Le courant circule en boucle fermée.")
            if type_recepteur == "Lampe à incandescence":
                st.info("Résultat : La lampe s'éclaire intensément.")
            elif type_recepteur == "Moteur rotatif":
                st.info("Résultat : L'axe du moteur tourne à vitesse nominale.")
            else:
                st.info("Résultat : L'avertisseur émet un signal sonore continu.")
        elif etat_generateur == "Allumé (Pile 9V)" and etat_interrupteur == "Ouvert (Le courant ne passe pas)":
            st.warning("CIRCUIT INACTIF : Le circuit est ouvert au niveau de l'interrupteur. Les électrons sont bloqués.")
        elif etat_generateur == "Éteint":
            st.error("CIRCUIT HORS TENSION : Le générateur est éteint. Il n'y a aucune force pour pousser les électrons.")


    st.write("---")

    if "vin_verrouille_tab1" not in st.session_state:
        st.session_state.vin_verrouille_tab1 = False

    verrou_at1 = st.session_state.vin_verrouille_tab1

    # Appel de la fonction pour afficher le quiz et la synthese
    try:
        afficher_questions_generalites_electricite_dynamiques1(verrouille=verrou_at1)
    except NameError:
        st.error("Erreur : La fonction afficher_questions_generalites_electricite_dynamiques1 n'est pas definie.")

    st.write("---")
    st.subheader("Validation du module Électricité Générale")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.", 
        key="check_certif_elec_final_net_tab1", 
        disabled=verrou_at1
    )


# --- ACTIONNEUR DE NOTATION AUTOMATIQUE (ATELIER 1) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_elec1_official_net", use_container_width=True, disabled=verrou_at1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (10 points)
            score_q1 = 0.0
            if "ordre_quiz_elec_tab1" in st.session_state:
                for q_item in st.session_state.ordre_quiz_elec_tab1:
                    reponse_eleve = st.session_state.get(f"generale_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q1 += 1.0

            # 2. Correction des Textes à trous (10 points)
            score_t1 = sum([
                st.session_state.get("generale_t1_tab1_final") == "électrons",
                st.session_state.get("generale_t2_tab1_final") == "conducteur",
                st.session_state.get("generale_t3_tab1_final") == "isolant",
                st.session_state.get("generale_t4_tab1_final") == "Volta",
                st.session_state.get("generale_t5_tab1_final") == "moins",
                st.session_state.get("generale_t6_tab1_final") == "générateur",
                st.session_state.get("generale_t7_tab1_final") == "interrupteur",
                st.session_state.get("generale_t8_tab1_final") == "alternatif",
                st.session_state.get("generale_t9_tab1_final") == "électrisation",
                st.session_state.get("generale_t10_tab1_final") == "électrocution"
            ])

            st.session_state.score_vin1_p1 = round(float(score_q1), 1)
            st.session_state.score_vin1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_vin1 = round(float(score_q1 + score_t1), 1)
            st.session_state.vin_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION ET AFFICHAGE DU RAPPORT (SORTI DU BLOC BOUTON) ---
    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER GENERAL SCELLE | Note de session : {tot_s:.1f} / 20")

        # Isolation du CSS pour éviter les conflits d'accolades avec les f-strings
        css_styles = """
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }
            .header-box { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }
            .score-badge { position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }
            .sub-title { font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            th { background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }
            td { padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }
            .status-correct { color: #10b981; font-weight: bold; text-transform: uppercase; }
            .status-incorrect { color: #ef4444; font-weight: bold; text-transform: uppercase; }
        """

        # 1. Initialisation et début du document HTML
        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Electricite Generale - {n_eleve}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 1 : Fondements, Histoire et Securite Electrique</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                - Note obtenue au Quiz : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 2. Injection des lignes de correction du Quiz
        if "ordre_quiz_elec_tab1" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab1, 1):
                saisie = st.session_state.get(f"generale_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_elec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"
                
        # 3. Transition vers la table des textes à trous
        html_export_elec += """
                </tbody>
            </table>
            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours (Trou)</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 4. Injection des lignes de correction de la Synthèse
        phrases_trous1 = [
            ("Le courant electrique correspond a un deplacement ordonne de particules appelees...", "électrons", "generale_t1_tab1_final"),
            ("Un materiau qui permet le passage du courant electrique se nomme un...", "conducteur", "generale_t2_tab1_final"),
            ("A l'inverse, l'air, le verre ou le plastique se comportent comme un...", "isolant", "generale_t3_tab1_final"),
            ("La premiere pile electrique de l'histoire a ete inventee par le savant...", "Volta", "generale_t4_tab1_final"),
            ("Une pile chimique delivre un courant continu dont le sens va du pole plus vers le pole...", "moins", "generale_t5_tab1_final"),
            ("Un circuit electrique minimal doit comporter un recepteur et un...", "générateur", "generale_t6_tab1_final"),
            ("Pour interrompre la circulation du courant a volonte, on insere un...", "interrupteur", "generale_t7_tab1_final"),
            ("Le courant fourni par les prises de courant de nos habitations is un courant...", "alternatif", "generale_t8_tab1_final"),
            ("La traversee accidentelle du corps humain par un courant electrique is une...", "électrisation", "generale_t9_tab1_final"),
            ("Lorsque le passage du courant electrique provoque directement la mort, on parle d'...", "électrocution", "generale_t10_tab1_final")
        ]

        for num, (texte, attendu, key_var) in enumerate(phrases_trous1, 1):
            saisie = st.session_state.get(key_var, "Non repondu")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_elec += f"<tr><td>{num}</td><td>{texte}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 5. Fermeture définitive des balises HTML
        html_export_elec += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # 6. Bouton de téléchargement officiel du rapport
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_elec,
            file_name=f"Rapport_General_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.title("Atelier Pédagogique : La Tension Électrique et ses Dangers")
    st.write("---")

    # ==========================================
    # SECTION 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    st.header("Document de Cours : La Tension Électrique")
    
    st.subheader("1. Origine et Définition de la Tension")
    st.write(
        "La tension électrique correspond à la différence de potentiel électrique entre deux points d'un circuit. "
        "Elle représente la force qui met en mouvement les électrons. Elle s'exprime en **Volts (V)**, en hommage à "
        "Alessandro Volta. Mathématiquement, selon la loi d'Ohm, elle est liée à la résistance et à l'intensité par la formule $U = R \cdot I$."
    )
    
    st.subheader("2. Évolution des Appareils de Mesure : De l'Ancien à nos Jours")

    # Affichage de vos propres photos stockées localement
    st.markdown("##### Galerie d'observation : Les types de voltmètres")

    col_volt1, col_volt2 = st.columns(2)
    with col_volt1:
        # Remplacez "voltmetre_aiguille.jpg" par le nom exact de votre fichier
        try:
            st.image("voltmetre_aiguille.jpg", caption="Modèle électromécanique à aiguille (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'voltmetre_aiguille.jpg' dans le dossier du script pour afficher l'image.")

    with col_volt2:
        # Remplacez "voltmetre_numerique.jpg" par le nom exact de votre fichier
        try:
            st.image("voltmetre_numerique.jpg", caption="Modèle numérique multimètre (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'voltmetre_numerique.jpg' dans le dossier du script pour afficher l'image.")

    st.write(
        "- **Le Voltmètre électromécanique à aiguille (Ancien) :** Utilisait un équipage mobile magnétique couplé à une grande résistance "
        "série pour dévier une aiguille sur un cadran gradué. Sa précision dépendait de la qualité de lecture de l'opérateur.\n"
        "- **Le Voltmètre Numérique (Moderne) :** Utilise un convertisseur analogue-numérique à haute impédance d'entrée "
        "pour afficher directement la valeur exacte de la différence de potentiel sur un écran LCD.\n"
        "- **L'Oscilloscope Numérique (Actuel) :** Permet non seulement de mesurer les valeurs efficaces et crêtes de la tension, "
        "mais également de visualiser sa forme d'onde (sinusoïdale, continue, triangulaire) en fonction du temps."
    )
    
    st.subheader("3. Dangers de la Tension et Seuils de Sécurité")
    st.write(
        "La tension détermine la quantité de courant qui traversera le corps selon l'état d'isolement de la peau. "
        "Les normes de sécurité définissent les tensions limites de sécurité (Très Basse Tension) en courant alternatif (50 Hz) :"
    )
    
    # Présentation des seuils sous forme narrative conforme aux règles d'affichage sans table
    st.markdown("##### Seuils de tension limite de sécurité et niveaux de risque sous 230 V :")
    st.write("- **Milieu sec :** Tension limite de 50 V. Niveau de risque sous 230 V : Mortel par défaut.")
    st.write("- **Milieu humide ou transpiration :** Tension limite de 24 V. Niveau de risque sous 230 V : Systématiquement mortel.")
    st.write("- **Milieu mouillé ou pieds dans l'eau :** Tension limite de 12 V. Niveau de risque sous 230 V : Foudroyant et mortel.")
    st.write("- **Milieu immergé ou blessure :** Tension limite de 12 V. Niveau de risque sous 230 V : Immédiatement mortel.")

    st.write("---")

    # ==========================================
    # SECTION 2 : SIMULATION DE TENSIONS & CONTACTS
    # ==========================================
    st.header("Simulation Dynamique : Différence de Potentiel et Types de Contacts")
    st.write(
        "Le risque d'électrisation dépend du potentiel de la source touchée et du chemin de retour du courant vers la Terre."
    )
    
    col_v1, col_v2 = st.columns(2)
    
    with col_v1:
        st.subheader("Configuration de la Source de Tension")
        tension_source_v = st.slider("Tension de la source électrique (Volt)", 5, 1000, 230, step=5, key="slider_tension_tab2_unique")
        type_contact_v = st.radio(
            "Sélectionnez le type de situation ou défaut :",
            ["Contact Direct (Phase touchée directement)", "Contact Indirect (Carcasse métallique en défaut touche la phase)"],
            key="radio_contact_tab2_unique"
        )
        
        isolement_terre = st.selectbox(
            "État de la liaison à la Terre de la carcasse (pour le contact indirect) :",
            ["Absente ou coupée (Danger)", "Correctement reliée avec disjoncteur fonctionnel"],
            key="select_terre_tab2_unique"
        )

    with col_v2:
        st.subheader("Diagnostic de Risque et Conséquences")
        
        if type_contact_v == "Contact Direct (Phase touchée directement)":
            st.error(f"DANGER IMPÉRATIF ! Différence de potentiel directe de {tension_source_v} V appliquée au corps humain.")
            if tension_source_v > 50:
                st.markdown("**Verdict :** Tension supérieure au seuil de sécurité en milieu sec (50V). Risque d'électrisation majeure ou d'électrocution.")
            else:
                st.markdown("**Verdict :** Sous le seuil de sécurité en milieu sec, mais reste dangereuse si la peau est humide.")
        
        else:
            if isolement_terre == "Absente ou coupée (Danger)":
                st.error(f"DANGER INVISIBLE ! La carcasse métallique est portée au potentiel de la phase : {tension_source_v} V.")
                st.markdown(
                    "**Conséquences :** Au moindre toucher, la personne sert de conducteur de rechange vers la Terre. "
                    "C'est un contact indirect mortel car aucun courant de fuite initial ne fait sauter les protections avant le contact."
                )
            else:
                st.success(f"SÉCURITÉ ACTIVE : Le courant de défaut est évacué vers la Terre par le fil Vert/Jaune.")
                st.markdown(
                    "**Conséquences :** La différence de potentiel sur la carcasse chute instantanément. "
                    "Le disjoncteur différentiel détecte la fuite et coupe l'alimentation en quelques millisecondes, protégeant l'utilisateur."
                )

    st.write("---")

    # ==========================================
    # VISUELS ACADÉMIQUES : CIRCUITS ET TENSION
    # ==========================================
    st.markdown("##### Étude expérimentale : Mesure de la différence de potentiel")

    col_circ_v1, col_circ_v2 = st.columns(2)
    with col_circ_v1:
        try:
            st.image("circuit_serie_tension.jpg", caption="Montage en série : Le voltmètre est connecté en dérivation aux bornes de chaque récepteur. Application de la loi d'additivité des tensions (loi des mailles) : U_générateur = U1 + U2.", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_serie_tension.jpg' pour l'affichage du schéma en série.")

    with col_circ_v2:
        try:
            st.image("circuit_derivation_tension.jpg", caption="Montage en dérivation : Le voltmètre branché aux bornes de n'importe quelle branche mesure la même valeur. Application de la loi d'unicité de la tension : U_générateur = U1 = U2.", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_derivation_tension.jpg' pour l'affichage du schéma en dérivation.")

    st.write("---")


    st.subheader("Validation du module Tension Electrique")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # --- INITIALISATION DU VERROU ---
    if "vin_verrouille_tab2" not in st.session_state:
        st.session_state.vin_verrouille_tab2 = False

    verrou_at2 = st.session_state.vin_verrouille_tab2


    try:
        afficher_questions_generalites_tension_dynamiques(verrouille=verrou_at2)
    except NameError:
        pass

    # --- CERTIFICATION ---
    case_certif_vin2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 2.", 
        key="check_certif_elec_final_net_tab2", 
        disabled=verrou_at2
    )


    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE TENSION (ATELIER 2) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_elec2_official_net", use_container_width=True, disabled=verrou_at2):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin2:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz de Tension (10 points)
            score_q2 = 0.0
            if "ordre_quiz_elec_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_elec_tab2:
                    reponse_eleve = st.session_state.get(f"tension_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 1.0

            # 2. Correction des Textes à trous de Tension (10 points)
            score_t2 = sum([
                st.session_state.get("tension_t1_tab2_final") == "tension",
                st.session_state.get("tension_t2_tab2_final") == "Volt",
                st.session_state.get("tension_t3_tab2_final") == "parallèle",
                st.session_state.get("tension_t4_tab2_final") == "50 V",
                st.session_state.get("tension_t5_tab2_final") == "12 V",
                st.session_state.get("tension_t6_tab2_final") == "direct",
                st.session_state.get("tension_t7_tab2_final") == "indirect",
                st.session_state.get("tension_t8_tab2_final") == "230 V",
                st.session_state.get("tension_t9_tab2_final") == "Ohm",
                st.session_state.get("tension_t10_tab2_final") == "surtension"
            ])

            st.session_state.score_vin2_p1 = round(float(score_q2), 1)
            st.session_state.score_vin2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_vin2 = round(float(score_q2 + score_t2), 1)
            st.session_state.vin_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 2 (SORTI DU BOUTON) ---
    if st.session_state.get("vin_verrouille_tab2", False):
        scr1 = st.session_state.get("score_vin2_p1", 0.0)
        scr2 = st.session_state.get("score_vin2_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin2", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin2 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER TENSION SCELLE | Note de session : {tot_s:.1f} / 20")

        # Isolation des styles CSS pour prevenir les conflits d'accolades avec la f-string
        css_styles = """
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }
            .header-box { background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }
            .score-badge { position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }
            .sub-title { font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; margin-bottom: 10px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; margin-bottom: 25px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
            th { background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }
            td { padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }
            .status-correct { color: #10b981; font-weight: bold; text-transform: uppercase; }
            .status-incorrect { color: #ef4444; font-weight: bold; text-transform: uppercase; }
        """

        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Tension Electrique - {n_eleve}</title>
            <style>
                {css_styles}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Atelier 2 : Potentiels, Contacts et Tensions de Securite</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                - Note obtenue au Quiz Proprietes de la Tension : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 2 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_elec_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab2, 1):
                saisie = st.session_state.get(f"tension_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_elec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours (Trou)</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous2 = [
            ("La force qui pousse les electrons et cree une difference de potentiel est la...", "tension", "tension_t1_tab2_final"),
            ("L'unite internationale de mesure de la tension est le...", "Volt", "tension_t2_tab2_final"),
            ("Pour mesurer une tension electrique, le voltmetre doit se brancher en...", "parallele", "tension_t3_tab2_final"),
            ("En milieu amazonien parfaitement sec, la tension limite de securite vaut...", "50 V", "tension_t4_tab2_final"),
            ("En milieu mouille / immerge, la tension limite de securite descend a...", "12 V", "tension_t5_tab2_final"),
            ("Toucher directement une piece conductrice active sous tension constitue un contact...", "direct", "tension_t6_tab2_final"),
            ("Toucher une carcasse metallique mise accidentellement sous tension est un contact...", "indirect", "tension_t7_tab2_final"),
            ("La tension nominale du reseau de distribution d'une prise domestique standard vaut...", "230 V", "tension_t8_tab2_final"),
            ("La loi d'expression reliant la tension aux bornes d'un resistor s'exprime en...", "Ohm", "tension_t9_tab2_final"),
            ("Une elevation dangereuse ou destructive de la tension sur le reseau est une...", "surtension", "tension_t10_tab2_final")
        ]

        for num, (texte, attendu, key_var) in enumerate(phrases_trous2, 1):
            saisie = st.session_state.get(key_var, "Non repondu")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_elec += f"<tr><td>{num}</td><td>{texte}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>
        </body>
        </html>
        """

        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_elec,
            file_name=f"Rapport_Tension_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )
                    

with tab3:

    st.title("Atelier Pédagogique : L'Intensité Électrique et ses Dangers")
    st.write("---")

    # ==========================================
    # SECTION 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    st.header("Document de Cours : L'Intensité Électrique")

    st.subheader("1. Origine et Définition de l'Intensité")
    st.write(
        "L'intensité du courant électrique correspond au débit de charges électriques à travers "
        "la section d'un conducteur par unité de temps. Elle s'exprime en **Ampères (A)**, en hommage à "
        "André-Marie Ampère. Mathématiquement, $I = Q / t$, où $Q$ est la charge en Coulombs et $t$ le temps en secondes."
    )

    st.subheader("2. Évolution des Appareils de Mesure : De l'Ancien à nos Jours")

    # Affichage de vos propres photos stockees localement
    st.markdown("##### Galerie d'observation : Les types d'ampèremètres")

    col_img1, col_img2 = st.columns(2)
    with col_img1:
        # Remplacez "amperemetre_aiguille.jpg" par le nom exact de votre fichier
        try:
            st.image("amperemetre_aiguille.jpg", caption="Modèle analogique à aiguille (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'amperemetre_aiguille.jpg' dans le dossier du script pour afficher l'image.")

    with col_img2:
        # Remplacez "amperemetre_numerique.jpg" par le nom exact de votre fichier
        try:
            st.image("amperemetre_numerique.jpg", caption="Modèle numérique de laboratoire (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'amperemetre_numerique.jpg' dans le dossier du script pour afficher l'image.")

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

    # Présentation des seuils sous forme descriptive sans tableau conforme aux instructions
    st.markdown("##### Seuils critiques d'intensité et effets physiologiques :")
    st.write("- **0.5 mA :** Seuil de perception (léger picotement).")
    st.write("- **10 mA :** Seuil de non-lâcher (tétanisation musculaire involontaire).")
    st.write("- **30 mA :** Seuil de paralysie respiratoire (asphyxie).")
    st.write("- **500 mA ou plus :** Fibrillation ventriculaire (arrêt cardiaque irréversible sans défibrillateur).")

    st.write("---")

    # ==========================================
    # SECTION 2 : SIMULATION DE CIRCUITS
    # ==========================================
    st.header("Simulation Dynamique : Circuit en Dérivation et Court-circuit")
    st.write(
        "Un circuit en dérivation (ou parallèle) divise le courant. La loi des nœuds s'applique : "
        "l'intensité totale est égale à la somme des intensités des branches ($I_{totale} = I_1 + I_2 + ...$)."
    )

    col_sim1, col_sim2 = st.columns(2)

    with col_sim1:
        st.subheader("Configuration des Récepteurs")
        tension_source = st.slider("Tension du générateur (Volt)", 5, 240, 230, step=5, key="slider_tension_at_intensite")
        R1 = st.slider("Résistance de la Lampe 1 (Ohm)", 10, 1000, 500, step=10, key="slider_r1_at_intensite")
        R2 = st.slider("Résistance de la Lampe 2 (Ohm)", 10, 1000, 250, step=10, key="slider_r2_at_intensite")
        
        simuler_court_circuit = st.checkbox("Provoquer un COURT-CIRCUIT (Rapprochement direct Phase/Neutre)", value=False, key="check_cc_at_intensite")

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

    st.write("---")

    # ==========================================
    # VISUELS ACADÉMIQUES : CIRCUITS ET INTENSITÉ
    # ==========================================
    st.markdown("##### Étude expérimentale : Distribution du débit de charges")

    col_circ_i1, col_circ_i2 = st.columns(2)
    with col_circ_i1:
        try:
            st.image("circuit_serie_intensite.jpg", caption="Montage en série : L'ampèremètre est inséré en série dans l'unique boucle de courant. Application de la loi d'unicité de l'intensité : I_totale = I1 = I2.", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_serie_intensite.jpg' pour l'affichage du schéma en série.")

    with col_circ_i2:
        try:
            st.image("circuit_derivation_intensite.jpg", caption="Montage en dérivation : Mesure des courants par branche. Application de la loi des nœuds : l'intensité totale de la branche principale est égale à la somme des intensités des branches dérivées (I_totale = I1 + I2).", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_derivation_intensite.jpg' pour l'affichage du schéma en dérivation.")

    st.write("---")


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


with tab4:
    st.title("Atelier Pédagogique : La Puissance Électrique et l'Effet Joule")
    st.write("---")

    # ==========================================
    # SECTION 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    st.header("Document de Cours : La Puissance Électrique")

    st.subheader("1. Origine et Définition de la Puissance")
    st.write(
        "La puissance électrique représente la quantité d'énergie qu'un appareil peut échanger (consommer ou fournir) "
        "par unité de temps. Elle s'exprime en **Watts (W)**, en hommage à James Watt. "
        "En courant continu, elle se calcule par le produit de la tension et de l'intensité : $P = U \cdot I$."
    )

    st.subheader("2. Évolution des Appareils de Mesure : De l'Ancien à nos Jours")

    # Affichage de vos propres photos stockées localement
    st.markdown("##### Galerie d'observation : Les types d'appareils de puissance")

    col_puis1, col_puis2 = st.columns(2)
    with col_puis1:
        # Remplacez "compteur_ancien.jpg" par le nom exact de votre fichier
        try:
            st.image("compteur_ancien.jpg", caption="Compteur électromécanique à disque (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'compteur_ancien.jpg' dans le dossier du script pour afficher l'image.")

    with col_puis2:
        # Remplacez "wattmetre_numerique.jpg" par le nom exact de votre fichier
        try:
            st.image("wattmetre_numerique.jpg", caption="Wattmètre numérique de laboratoire (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'wattmetre_numerique.jpg' dans le dossier du script pour afficher l'image.")

    st.write(
        "- **Le Compteur Électromécanique (Ancien) :** Disposait d'un disque en aluminium entraîné en rotation "
        "par le champ magnétique des bobines d'intensité et de tension. La vitesse du disque était proportionnelle à la puissance consommée.\n"
        "- **Le Wattmètre Numérique de table (Moderne) :** Échantillonne simultanément les signaux de tension et de courant "
        "pour calculer instantanément la puissance active, réactive et le facteur de puissance ($\cos \phi$).\n"
        "- **Le Compteur Intelligent Linky (Actuel) :** Mesure en permanence la puissance apparente en Volt-Ampères (VA) "
        "et transmet quotidiennement les courbes de charge, permettant de surveiller le dépassement de la puissance souscrite."
    )

    st.subheader("3. Conséquences des Surcharges et Effet Joule")
    st.write(
        "Lorsqu'un courant traverse un conducteur doté d'une résistance $R$, une partie de la puissance est perdue sous "
        "forme de chaleur ($P = R \cdot I^2$). Si trop d'appareils de forte puissance (radiateur, four, bouilloire) sont "
        "branchés sur une multiprise, l'intensité globale dépasse les limites admissibles, ce qui provoque une surcharge thermique."
    )

    st.write("---")

    # ==========================================
    # SECTION 2 : SIMULATION DE PUISSANCE & SURCHARGE
    # ==========================================
    st.header("Simulation Dynamique : Accumulation de Puissance et Risque de Surcharge")
    st.write(
        "Simulez le branchement d'appareils domestiques sur une même ligne limitée par une puissance souscrite contractuelle."
    )

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.subheader("Paramètres de l'Installation")
        puissance_limite = st.selectbox("Puissance souscrite par l'abonné (kVA / kW) :", [3, 6, 9, 12], key="select_limite_tab4_unique")
        puissance_limite_w = puissance_limite * 1000
        
        st.write("Cochez les appareils en fonctionnement :")
        four = st.checkbox("Four Électrique (2500 W)", value=False, key="check_four_tab4_unique")
        machine = st.checkbox("Lave-linge (2000 W)", value=False, key="check_machine_tab4_unique")
        radiateur = st.checkbox("Radiateur (1500 W)", value=False, key="check_rad_tab4_unique")
        bouilloire = st.checkbox("Bouilloire (1200 W)", value=False, key="check_bouilloire_tab4_unique")
        tv = st.checkbox("Téléviseur et Box (150 W)", value=True, key="check_tv_tab4_unique")

    with col_p2:
        st.subheader("Bilan Énergétique de la Ligne")
        
        puissance_totale_w = (four * 2500) + (machine * 2000) + (radiateur * 1500) + (bouilloire * 1200) + (tv * 150)
        
        st.metric(label="Puissance Totale Appelée", value=f"{puissance_totale_w} W", delta=f"Limite : {puissance_limite_w} W", delta_color="inverse")
        
        if puissance_totale_w > puissance_limite_w:
            st.error("DISJONCTION ! La puissance appelée dépasse votre puissance souscrite contractuelle.")
            st.markdown(
                "**Conséquence :** Le disjoncteur général de l'installation ou le compteur Linky coupe l'alimentation "
                "pour protéger le réseau contre une surintensité thermique destructrice par effet Joule."
            )
        else:
            st.success("INSTALLATION STABLE : La consommation respecte les limites du disjoncteur.")
            st.markdown("La marge de puissance restante avant coupure est de : **" + str(puissance_limite_w - puissance_totale_w) + " W**.")

    st.write("---")

    # ==========================================
    # VISUELS ACADÉMIQUES : PUISSANCE ET SURCHARGE
    # ==========================================
    st.markdown("##### Analyse des risques thermiques : Puissance absorbée et surintensité")

    col_circ_p1, col_circ_p2 = st.columns(2)
    with col_circ_p1:
        try:
            st.image("circuit_normal_puissance.jpg", caption="Régime nominal stable : Chaque récepteur convertit sa puissance unitaire (P = U * I). La puissance totale appelée (P_totale = P1 + P2) reste inférieure à la puissance de disjonction contractuelle.", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_normal_puissance.jpg' pour l'affichage de l'installation stable.")

    with col_circ_p2:
        try:
            st.image("circuit_surcharge_puissance.jpg", caption="Régime de surcharge thermique : L'accumulation d'appareils de forte puissance en parallèle provoque une hausse critique de l'intensité totale. Risque immédiat d'incendie par effet Joule (P = R * I^2) avant déclenchement du disjoncteur.", use_container_width=True)
        except:
            st.info("En attente du fichier 'circuit_surcharge_puissance.jpg' pour l'affichage du schéma de surcharge.")

    st.write("---")

    if "vin_verrouille_tab4" not in st.session_state:
        st.session_state.vin_verrouille_tab4 = False

    verrou_at4 = st.session_state.vin_verrouille_tab4

    # Appel propre de la fonction d'affichage de la puissance (Quiz + Trous)
    try:
        afficher_questions_generalites_puissance_dynamiques(verrouille=verrou_at4)
    except NameError:
        pass

    st.write("---")
    st.subheader("Validation du module Puissance Électrique")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin4 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 4.", 
        key="check_certif_elec_final_net_tab4", 
        disabled=verrou_at4
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE PUISSANCE (ATELIER 4) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_elec4_official_net", use_container_width=True, disabled=verrou_at4):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_vin4:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz de Puissance (10 points)
            score_q4 = 0.0
            if "ordre_quiz_elec_tab4" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_elec_tab4, 1):
                    reponse_eleve = st.session_state.get(f"at4_quiz_puissance_q{idx}_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q4 += 1.0

            # 2. Correction des Textes à trous de Puissance (10 points)
            score_t4 = sum([
                st.session_state.get("at4_puissance_t1") == "puissance",
                st.session_state.get("at4_puissance_t2") == "Watt",
                st.session_state.get("at4_puissance_t3") == "apparente",
                st.session_state.get("at4_puissance_t4") == "Joule",
                st.session_state.get("at4_puissance_t5") == "carré",
                st.session_state.get("at4_puissance_t6") == "électromécaniques",
                st.session_state.get("at4_puissance_t7") == "Linky",
                st.session_state.get("at4_puissance_t8") == "surcharge",
                st.session_state.get("at4_puissance_t9") == "énergie",
                st.session_state.get("at4_puissance_t10") == "heure"
            ])

            st.session_state.score_vin4_p1 = round(float(score_q4), 1)
            st.session_state.score_vin4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_vin4 = round(float(score_q4 + score_t4), 1)
            st.session_state.vin_verrouille_tab4 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 4 ---
    if st.session_state.get("vin_verrouille_tab4", False):
        scr1 = st.session_state.get("score_vin4_p1", 0.0)
        scr2 = st.session_state.get("score_vin4_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin4", 0.0)

        timestamp_vin4 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER PUISSANCE SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Puissance Électrique - {n_eleve}</title>
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
                <p>Atelier 4 : Puissance Électrique, Énergie et Pertes par Effet Joule</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_vin4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                &bull; Note obtenue au Quiz Propriétés de la Puissance : <strong>{scr1:.1f} / 10</strong><br>
                &bull; Note obtenue à la Synthèse : <strong>{scr2:.1f} / 10</strong><br>
                &bull; Note Totale de l'Atelier 4 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_elec_tab4" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab4, 1):
                saisie = st.session_state.get(f"at4_quiz_puissance_q{num}_{q_item['id']}", "Choisir...")
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

        phrases_trous4 = [
            ("1. La quantité d'énergie transformée par seconde définit la", "puissance", "at4_puissance_t1"),
            ("2. L'unité légale de la puissance électrique dans le système international est le", "Watt", "at4_puissance_t2"),
            ("3. Le produit de la tension par l'intensité donne la puissance", "apparente", "at4_puissance_t3"),
            ("4. La conversion d'énergie électrique en chaleur s'appelle l'effet", "Joule", "at4_puissance_t4"),
            ("5. La formule de cette perte thermique par effet Joule s'écrit R fois I au", "carré", "at4_puissance_t5"),
            ("6. Les compteurs historiques qui mesuraient l'énergie globale étaient", "électromécaniques", "at4_puissance_t6"),
            ("7. Aujourd'hui, la relève de la puissance instantanée est automatisée par le compteur", "Linky", "at4_puissance_t7"),
            ("8. Accumuler trop d'appareils énergivores sur une même ligne crée une", "surcharge", "at4_puissance_t8"),
            ("9. La puissance multipliée par la durée de fonctionnement donne l'", "énergie", "at4_puissance_t9"),
            ("10. Pour facturer les abonnés, les fournisseurs utilisent le kilowatt-", "heure", "at4_puissance_t10")
        ]

        for num, (texte, attendu, cle_session) in enumerate(phrases_trous4, 1):
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
            file_name=f"Bilan_Puissance_Electricite_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )

with tab5:
    st.title("Atelier Pédagogique : L'Énergie Électrique et sa Mesure")
    st.write("---")

    # ==========================================
    # SECTION 1 : DOCUMENT DE COURS & HISTOIRE
    # ==========================================
    st.header("Document de Cours : L'Énergie Électrique")

    st.subheader("1. Définition et Formule de l'Énergie")
    st.write(
        "L'énergie électrique correspond à la quantité globale de travail fournie par un courant électrique "
        "pendant une durée déterminée. Elle dépend directement de la puissance de l'appareil et de son temps de fonctionnement. "
        "La formule fondamentale s'exprime par la relation : $E = P \cdot t$."
    )
    st.write(
        "- **L'unité légale :** Dans le Système International (SI), l'énergie s'exprime en **Joules (J)**, où 1 Joule équivaut à 1 Watt converti pendant 1 seconde.\n"
        "- **L'unité pratique :** Pour la facturation de volumes importants, les fournisseurs d'électricité utilisent le **kilowattheure (kWh)**. Un kilowattheure correspond à 3 600 000 Joules."
    )

    st.subheader("2. Évolution de la Mesure de l'Énergie consommée")

    # Affichage de vos propres photos stockées localement
    st.markdown("##### Galerie d'observation : Les types de compteurs d'énergie")

    col_ener1, col_ener2 = st.columns(2)
    with col_ener1:
        # Remplacez "compteur_disque.jpg" par le nom exact de votre fichier
        try:
            st.image("compteur_disque.jpg", caption="Compteur d'énergie ancien à disque (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'compteur_disque.jpg' dans le dossier du script pour afficher l'image.")

    with col_ener2:
        # Remplacez "compteur_linky.jpg" par le nom exact de votre fichier
        try:
            st.image("compteur_linky.jpg", caption="Compteur connecté moderne Linky (Photo atelier)", use_container_width=True)
        except:
            st.info("Placez le fichier 'compteur_linky.jpg' dans le dossier du script pour afficher l'image.")

    st.write(
        "- **Le Compteur d'Énergie à Disque (Ancien) :** Comptabilisait l'énergie de manière purement mécanique. Chaque rotation complète "
        "du disque en aluminium correspondait à une quantité fixe de Wattheures consommés (constante du compteur C, notée en Wh/tr).\n"
        "- **Le Compteur Électronique (Intermédiaire) :** Utilisait un système statique avec un écran LCD. Le calcul de l'énergie s'effectuait par intégration numérique des signaux de courant et de tension, matérialisé par un voyant lumineux clignotant à chaque Wattheure consommé.\n"
        "- **Le Compteur Connecté Linky (Actuel) :** Enregistre en temps réel l'énergie active consommée en kilowattheures. Il mémorise la courbe de charge par pas de temps et communique automatiquement les index de consommation à distance via les lignes électriques (courants porteurs en ligne)."
    )

    st.write("---")

    # ==========================================
    # SECTION 2 : SIMULATION DE CONSOMMATION & FACTURATION
    # ==========================================
    st.header("Simulation Dynamique : Consommation d'Énergie et Estimation du Coût")
    st.write(
        "Estimez l'énergie cumulée en kilowattheures sur une période donnée et calculez le coût financier associé."
    )

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        st.subheader("Paramètres d'Utilisation")
        prix_kwh = st.number_input("Tarif de l'électricité (Euros par kWh) :", min_value=0.05, max_value=0.60, value=0.25, step=0.01, key="prix_kwh_tab5")
        duree_jours = st.slider("Durée d'observation de l'installation (en jours) :", min_value=1, max_value=30, value=7, key="duree_slider_tab5")
        
        st.write("Déterminez les heures quotidiennes d'utilisation pour chaque appareil :")
        h_four = st.slider("Four Électrique (2500 W) - Heures par jour :", min_value=0.0, max_value=5.0, value=1.0, step=0.5, key="h_four_tab5")
        h_machine = st.slider("Lave-linge (2000 W) - Heures par jour :", min_value=0.0, max_value=4.0, value=0.5, step=0.5, key="h_mach_tab5")
        h_radiateur = st.slider("Radiateur (1500 W) - Heures par jour :", min_value=0.0, max_value=24.0, value=6.0, step=1.0, key="h_rad_tab5")
        h_tv = st.slider("Téléviseur (150 W) - Heures par jour :", min_value=0.0, max_value=12.0, value=4.0, step=1.0, key="h_tv_tab5")

    with col_e2:
        st.subheader("Bilan Énergétique et Financier")
        
        # Calcul de l'énergie journalière en Wh puis conversion en kWh
        wh_jour = (h_four * 2500) + (h_machine * 2000) + (h_radiateur * 1500) + (h_tv * 150)
        kwh_total = (wh_jour / 1000) * duree_jours
        cout_total = kwh_total * prix_kwh
        
        st.metric(label="Énergie Totale Consommée", value=f"{kwh_total:.2f} kWh", delta=f"Sur {duree_jours} jours")
        st.metric(label="Coût Total Estimé", value=f"{cout_total:.2f} EUR")
        
        st.info("Note de Cours : Le compteur électrique Linky incrémente son index de l'exacte valeur de kilowattheures affichée ci-dessus.")
        
        if kwh_total > 200:
            st.warning("Consommation élevée détectée. Pensez à vérifier la classe énergétique de vos appareils ou à optimiser le temps de fonctionnement des récepteurs thermiques.")
        else:
            st.success("Consommation modérée. L'empreinte énergétique de cette installation reste dans la moyenne basse standard.")

    st.write("---")

    if "vin_verrouille_tab5" not in st.session_state:
        st.session_state.vin_verrouille_tab5 = False

    verrou_at5 = st.session_state.vin_verrouille_tab5

    # Appel propre de la fonction d'affichage du tab5
    try:
        afficher_questions_generalites_energie_dynamiques(verrouille=verrou_at5)
    except NameError:
        pass

    st.write("---")
    st.subheader("Validation du module Énergie Électrique")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin5 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 5.", 
        key="check_certif_elec_final_net_tab5", 
        disabled=verrou_at5
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE ÉNERGIE (ATELIER 5) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_elec5_official_net", use_container_width=True, disabled=verrou_at5):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusée : Saisissez votre identity dans l'onglet 'Identification'.")
        elif not case_certif_vin5:
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz d'Énergie (10 points)
            score_q5 = 0.0
            if "ordre_quiz_elec_tab5" in st.session_state:
                for q_item in st.session_state.ordre_quiz_elec_tab5:
                    reponse_eleve = st.session_state.get(f"energie_at5_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q5 += 1.0

            # 2. Correction des Textes à trous d'Énergie (10 points)
            score_t5 = sum([
                st.session_state.get("energie_t1_tab5_final") == "énergie",
                st.session_state.get("energie_t2_tab5_final") == "Joule",
                st.session_state.get("energie_t3_tab5_final") == "3600000 J",
                st.session_state.get("energie_t4_tab5_final") == "puissance",
                st.session_state.get("energie_t5_tab5_final") == "Joule",
                st.session_state.get("energie_t6_tab5_final") == "moteur",
                st.session_state.get("energie_t7_tab5_final") == "rendement",
                st.session_state.get("energie_t8_tab5_final") == "Linky",
                st.session_state.get("energie_t9_tab5_final") == "1000 W",
                st.session_state.get("energie_t10_tab5_final") == "A"
            ])

            st.session_state.score_vin5_p1 = round(float(score_q5), 1)
            st.session_state.score_vin5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_vin5 = round(float(score_q5 + score_t5), 1)
            st.session_state.vin_verrouille_tab5 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 5 ---
    if st.session_state.get("vin_verrouille_tab5", False):
        scr1 = st.session_state.get("score_vin5_p1", 0.0)
        scr2 = st.session_state.get("score_vin5_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin5", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin5 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER ENERGIE SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_elec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Energie Electrique - {n_eleve}</title>
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
                <p>Atelier 5 : Conversion, Puissance et Mesure de l'Energie</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #991b1b;">
                - Note obtenue au Quiz Proprietes de l'Energie : <strong>{scr1:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 5 : <strong>{tot_s:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_elec_tab5" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_elec_tab5, 1):
                saisie = st.session_state.get(f"energie_at5_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_elec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours (Trou)</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous5 = [
            ("La grandeur qui comptabilise le travail total fourni par un courant electrique est l'...", "énergie", "energie_t1_tab5_final"),
            ("L'unite de mesure d'energie correspondant a un watt pendant une seconde est le...", "Joule", "energie_t2_tab5_final"),
            ("Pour simplifier la facturation, on utilise le kilowattheure qui equivaut a...", "3600000 J", "energie_t3_tab5_final"),
            ("La vitesse a laquelle cette energie est consommee ou delivree definit la...", "puissance", "energie_t4_tab5_final"),
            ("Le degagement de chaleur provoque par le passage du courant se nomme l'effet...", "Joule", "energie_t5_tab5_final"),
            ("Un appareil qui convertit l'energie electrique en energie mecanique est un...", "moteur", "energie_t6_tab5_final"),
            ("Le rapport entre l'energie utile restituee et l'energie absorbee est le...", "rendement", "energie_t7_tab5_final"),
            ("Le compteur intelligent deploye en France pour mesurer l'energie se nomme...", "Linky", "energie_t8_tab5_final"),
            ("Un kilowatt (kW) correspond a une puissance de conversion egale a...", "1000 W", "energie_t9_tab5_final"),
            ("Pour reduire la consommation d'energie, on doit privilegier les appareils de classe...", "A", "energie_t10_tab5_final")
        ]

        for num, (texte, attendu, key_var) in enumerate(phrases_trous5, 1):
            saisie = st.session_state.get(key_var, "Non repondu")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_elec += f"<tr><td>{num}</td><td>{texte}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_elec += """
                </tbody>
            </table>
        </body>
        </html>
        """

        # --- BOUTON DE TELECHARGEMENT DU BILAN COMPILE ---
        st.download_button(
            label="TELECHARGER LE RAPPORT OFFICIEL (HTML)",
            data=html_export_elec,
            file_name=f"Rapport_Energie_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )


with tab6:

    st.header("Protection des Personnes et des Installations")
    st.write(
        "Une installation électrique moderne s'appuie sur deux piliers de sécurité fondamentaux : "
        "la protection des êtres humains contre les chocs électriques et la protection des équipements "
        "contre les anomalies du réseau."
    )

    # --- SECTION INTERACTIVE : CALCULATEUR DE CONFORMITÉ ---
    st.subheader("Calculateur de conformité de la Prise de Terre")
    st.write(
        "Selon la norme NF C 15-100, la résistance de la prise de terre doit être adaptée "
        "à la sensibilité du disjoncteur différentiel pour éviter que la tension de défaut ne dépasse 50 Volts."
    )

    # Saisie utilisateur pour la résistance de la terre
    resistance_terre = st.number_input(
        "Entrez la résistance de votre prise de terre (en Ohms) :",
        min_value=0.0,
        max_value=500.0,
        value=35.0,
        step=1.0,
        help="La valeur idéale doit être la plus basse possible.",
    )

    # Validation de la conformité réglementaire
    if resistance_terre <= 100.0:
        st.success(
            f"Conforme : Avec {resistance_terre} Ohms, votre prise de terre respecte la limite "
            f"maximale autorisée de 100 Ohms pour une protection différentielle standard de 500 mA."
        )
    else:
        st.error(
            f"Non conforme : Votre valeur de {resistance_terre} Ohms dépasse la limite maximale de 100 Ohms. "
            f"Il y a un risque d'électrisation en cas de défaut d'isolement. Vous devez améliorer la prise de terre."
        )

    st.divider()

    # --- SECTION CONTENU ET IMAGES JPG ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Protection des Personnes : Le Différentiel 30 mA")
        st.info(
            "**Son rôle exclusif :** Éviter l'électrocution des êtres humains en détectant les fuites de courant "
            "avant qu'elles ne deviennent mortelles."
        )

        # Intégration de l'image JPG pour le différentiel
        try:
            st.image(
                "differentiel.jpg",
                caption="Schéma d'un dispositif différentiel 30 mA",
                use_container_width=True,
            )
        except Exception:
            st.caption(
                "(Fichier 'differentiel.jpg' introuvable dans le répertoire du script)"
            )

        st.markdown("""
        ### Le seuil critique de 30 mA
        Le corps humain étant conducteur, le choix d'un seuil de déclenchement à **30 mA (milliampères)** répond à des critères médicaux stricts :
        * **En dessous de 30 mA :** Le courant provoque une secousse ou une contraction musculaire (tétanisation), mais reste généralement sans danger mortel.
        * **Au-dessus de 30 mA :** Risque immédiat de paralysie respiratoire et de fibrillation cardiaque (arrêt du cœur) si le courant traverse le corps plus de quelques fractions de seconde.
        
        ### Le principe de la balance
        Le dispositif différentiel compare en permanence le courant qui entre et celui qui sort :
        1. **Le flux entrant :** L'électricité arrive par le fil de **Phase** (rouge, marron ou noir).
        2. **Le flux sortant :** L'électricité repart par le fil de **Neutre** (bleu).
        3. **La détection de fuite :** Si un appareil est défectueux ou si une personne touche un conducteur dénudé, le courant s'échappe vers la **Terre**.
        4. **La coupure instantanée :** Dès que l'écart entre l'entrée et la sortie atteint **0,03 Ampère (30 mA)**, le mécanisme coupe le circuit en moins de **40 millisecondes**.
        """)

        st.warning(
            "**Règle NF C 15-100 :** Tous les circuits de l'habitation doivent obligatoirement être protégés "
            "par un dispositif 30 mA. Actionnez le bouton **Test (T)** une fois par mois pour vérifier son bon fonctionnement."
        )

    with col2:
        st.subheader("2. Protection des Installations : Disjoncteurs et Parafoudre")
        st.info(
            "**Leur rôle exclusif :** Protéger les câbles et les appareils électriques contre les dégradations, "
            "les surcharges et les incendies."
        )

        # Intégration de l'image JPG pour les disjoncteurs
        try:
            st.image(
                "disjoncteur.jpg",
                caption="Exemple de disjoncteur divisionnaire et parafoudre",
                use_container_width=True,
            )
        except Exception:
            st.caption(
                "(Fichier 'disjoncteur.jpg' introuvable dans le répertoire du script)"
            )

        st.markdown("""
        ### Les surcharges et courts-circuits (Disjoncteurs)
        Les disjoncteurs divisionnaires veillent à ce que les fils électriques ne surchauffent pas :
        * **La surcharge :** Trop d'appareils branchés en même temps sur une même prise font chauffer le câble. Le disjoncteur thermique détecte cette hausse de température et coupe avant l'incendie.
        * **Le court-circuit :** Si la Phase et le Neutre se touchent directement, l'intensité monte à plusieurs milliers d'ampères. Le disjoncteur magnétique réagit de façon immédiate pour stopper le danger.
        
        ### Les surtensions externes (Le Parafoudre)
        Les agressions peuvent venir de l'extérieur, notamment lors d'un impact de foudre sur le réseau public :
        * **Le pic de tension :** Une décharge de foudre peut envoyer plusieurs milliers de volts dans vos prises (alors que vos appareils sont conçus pour 230 V).
        * **Le rôle du parafoudre :** Il agit comme une soupape de sécurité. Dès qu'une tension anormale se présente à l'entrée du tableau, il dévie instantanément cette énergie destructrice directement vers la **Prise de terre**, protégeant ainsi le compteur Linky et vos appareils électroniques sensibles.
        """)

        st.success(
            "**Le duo gagnant :** Une bonne protection des installations est totalement inefficace "
            "sans une **mise à la terre de très bonne qualité** (résistance inférieure à 100 Ohms) pour évacuer les courants de défaut."
        )



    # --- DEBUT DU SIMULATEUR D'INCIDENTS EMBARQUÉ ---
    st.write("---")
    st.markdown("### Simulateur expérimental d'Incidents Électriques")
    
    installation_conforme = st.radio(
        "Sélectionnez la configuration technique de l'armoire :",
        options=["Aux normes actuelles (Disjoncteurs et Différentiel opérationnels)", 
                 "Vétuste / Obsolète (Protections bloquées ou absentes)"],
        index=0,
        key="radio_simulation_conformite_tab7",
        disabled=verrou_at7 # <-- CORRIGÉ ICI (remplacé verrouille par verrou_at7)
    )

    is_conforme = (installation_conforme == "Aux normes actuelles (Disjoncteurs et Différentiel opérationnels)")

    incident = st.selectbox(
        "Choisissez l'incident à reproduire au laboratoire :",
        options=[
            "Aucun - Fonctionnement stable",
            "Surcharge : Appareils de cuisson multiples",
            "Court-circuit : Insertion de ciseaux métalliques",
            "Défaut d'isolement : Infiltration d'eau carcasse métal"
        ],
        key="selectbox_incident_simulation_tab7",
        disabled=verrou_at7
    )

    texte_statut = "Fonctionnement standard"
    texte_action = "Aucune action requise"
    texte_consequence = "L'installation demeure totalement sécurisée."
    couleur_fond_html = "#f8fafc"

    fig, ax = plt.subplots(figsize=(4, 5))
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    if incident == "Aucun - Fonctionnement stable":
        st.success("Statut : Réseau électrique équilibré. Aucun flux de défaut mesuré.")
        ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#e2e8f0'))
        ax.add_patch(patches.Rectangle((0.4, 0.4), 0.2, 0.3, color='#1e293b'))
        ax.plot([0.5, 0.5], [0.55, 0.85], color='#ef4444', linewidth=10, solid_capstyle='round')
        ax.add_patch(patches.Circle((0.5, 0.25), 0.06, color='#10b981'))
        ax.text(0.5, 0.22, "I", color='white', fontsize=12, fontweight='bold', ha='center')
        ax.set_title("DISJONCTEUR FERMÉ (ON)")

    elif incident == "Surcharge : Appareils de cuisson multiples":
        if is_conforme:
            texte_statut = "Surcharge de ligne détectée"
            texte_action = "Le déclencheur thermique s'ouvre automatiquement"
            texte_consequence = "Les conducteurs refroidissent instantanément. Préservation de l'intégrité de la ligne de distribution. Risque d'incendie nul."
            st.info(f"Analyse : {texte_statut}.")
            st.error(f"Action : {texte_action}.")
            st.success(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "SURCHARGE", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
        else:
            texte_statut = "Surcharge prolongée non détectée"
            texte_action = "Aucune ouverture automatique du circuit (protection défaillante)"
            texte_consequence = "Échauffement critique par effet Joule. Fusion des gaines isolantes en PVC, inflammation des supports muraux entraînant un début d'incendie de l'habitation."
            couleur_fond_html = "#fef2f2"
            st.error(f"Analyse : {texte_statut}.")
            st.warning(f"Action : {texte_action}.")
            st.error(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#991b1b'))
            ax.text(0.5, 0.5, "FEU / SURCHAUFFE", color='white', fontsize=11, fontweight='bold', ha='center')

    elif incident == "Court-circuit : Insertion de ciseaux métalliques":
        if is_conforme:
            texte_statut = "Court-circuit franc (Impédance nulle)"
            texte_action = "Le déclencheur magnétique coupe le circuit en moins de 10 millisecondes"
            texte_consequence = "L'arc électrique est instantanément soufflé. L'intégrité physique de l'utilisateur est préservée. Absence de détérioration du matériel."
            st.info(f"Analyse : {texte_statut}.")
            st.error(f"Action : {texte_action}.")
            st.success(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "COURT-CIRCUIT", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
        else:
            texte_statut = "Court-circuit non interrompu"
            texte_action = "Aucune rupture physique du courant, contacts soudés par l'intensité"
            texte_consequence = "Création d'un arc électrique de forte puissance. Projection de matières de cuivre en fusion, brûlures thermiques sévères au niveau des mains et du visage, risque de choc traumatique direct."
            couleur_fond_html = "#fef2f2"
            st.error(f"Analyse : {texte_statut}.")
            st.warning(f"Action : {texte_action}.")
            st.error(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#7f1d1d'))
            ax.text(0.5, 0.5, "EXPLOSION ARC", color='white', fontsize=11, fontweight='bold', ha='center')

    elif incident == "Défaut d'isolement : Infiltration d'eau carcasse métal":
        if is_conforme:
            texte_statut = "Fuite de courant supérieure à 30 mA vers la terre"
            texte_action = "Le tore de l'interrupteur différentiel bascule instantanément"
            texte_consequence = "Mise hors tension immédiate de la ligne. La tension de contact accidentelle est supprimée. Risque de fibrillation ou d'électrisation totalement écarté."
            st.info(f"Analyse : {texte_statut}.")
            st.error(f"Action : {texte_action}.")
            st.success(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#cbd5e1'))
            ax.add_patch(patches.Rectangle((0.4, 0.3), 0.2, 0.3, color='#1e293b'))
            ax.plot([0.5, 0.5], [0.45, 0.15], color='#64748b', linewidth=10, solid_capstyle='round')
            ax.text(0.5, 0.5, "DÉFAUT TERRE", color='#b91c1c', fontsize=10, fontweight='bold', ha='center')
        else:
            texte_statut = "Défaut d'isolement permanent sans coupure"
            texte_action = "Le tableau reste inactif (absence ou défaillance du module 30 mA)"
            texte_consequence = "La carcasse externe de l'appareil est portée à un potentiel de 230 Volts. Lors du contact avec l'utilisateur, le corps fait office de conducteur de retour vers le sol : ÉLECTROCUTION DIRECTE PAR TRAVERSÉE CARDIAQUE."
            couleur_fond_html = "#fef2f2"
            st.error(f"Analyse : {texte_statut}.")
            st.warning(f"Action : {texte_action}.")
            st.error(f"Bilan : {texte_consequence}")
            
            ax.add_patch(patches.Rectangle((0.2, 0.1), 0.6, 0.8, color='#7f1d1d'))
            ax.text(0.5, 0.5, "ELECTROCUTION", color='white', fontsize=11, fontweight='bold', ha='center')

    st.pyplot(fig)

    # 3. Générateur de la fiche expérimentale HTML
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    timestamp_fiche = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

    html_fiche_incident = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Fiche de Laboratoire Securite - {n_eleve}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: {couleur_fond_html}; color: #0f172a; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; border: 1px solid #cbd5e1; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ border-bottom: 3px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 25px; }}
            h1 {{ color: #1e3a8a; margin: 0; font-size: 22px; }}
            .meta {{ font-size: 13px; color: #475569; margin-top: 5px; }}
            .block-title {{ font-weight: bold; font-size: 14px; text-transform: uppercase; color: #334155; margin-top: 20px; border-left: 4px solid #1e3a8a; padding-left: 10px; }}
            .content-text {{ font-size: 14px; margin-top: 8px; background: #f1f5f9; padding: 12px; border-radius: 4px; line-height: 1.5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Fiche d'Analyse de Risque et Securite Electrique</h1>
                <div class="meta">Operateur : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Genere le : {timestamp_fiche}</div>
            </div>
            <div class="block-title">Configuration Initiale du Laboratoire</div>
            <div class="content-text"><strong>Type d'armoire :</strong> {installation_conforme}</div>
            <div class="block-title">Nature de l'Incident Propose</div>
            <div class="content-text"><strong>Evenement declencheur :</strong> {incident}</div>
            <div class="block-title">Analyse du Comportement de l'Installation</div>
            <div class="content-text"><strong>Reaction du systeme automatique :</strong> {texte_action}</div>
            <div class="block-title">Diagnostic General et Consequences Physiques</div>
            <div class="content-text" style="background: #f8fafc; border: 1px solid #e2e8f0;">{texte_consequence}</div>
        </div>
    </body>
    </html>
    """

    st.download_button(
        label="Exporter et telecharger la fiche bilan de l'incident (HTML)",
        data=html_fiche_incident,
        file_name=f"Fiche_Securite_Incident_{n_eleve}.html",
        mime="text/html",
        use_container_width=True,
        disabled=verrou_at7
    )


    st.write("---")

    if "vin_verrouille_tab7" not in st.session_state:
        st.session_state.vin_verrouille_tab7 = False

    verrou_at7 = st.session_state.vin_verrouille_tab7

    # Appel propre de la fonction d'affichage du tab7
    try:
        afficher_questions_protections_dynamiques(verrouille=verrou_at7)
    except NameError:
        pass

    st.write("---")
    st.subheader("Validation du module Protections et Securite")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin7 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier 7.", 
        key="check_certif_protec_final_net_tab7", 
        disabled=verrou_at7
    )

    # --- ACTIONNEUR DE NOTATION AUTOMATIQUE PROTECTIONS (ATELIER 7) ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 7", key="btn_export_protec7_official_net", use_container_width=True, disabled=verrou_at7):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin7:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz des Protections (10 points)
            score_q7 = 0.0
            if "ordre_quiz_protec_tab7" in st.session_state:
                for q_item in st.session_state.ordre_quiz_protec_tab7:
                    reponse_eleve = st.session_state.get(f"protec_at7_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q7 += 1.0

            # 2. Correction des Textes à trous des Protections (10 points)
            score_t7 = sum([
                st.session_state.get("protec_t1_tab7_final") == "différentiel",
                st.session_state.get("protec_t2_tab7_final") == "30 mA",
                st.session_state.get("protec_t3_tab7_final") == "Test",
                st.session_state.get("protec_t4_tab7_final") == "surcharge",
                st.session_state.get("protec_t5_tab7_final") == "magnétique",
                st.session_state.get("protec_t6_tab7_final") == "Phase",
                st.session_state.get("protec_t7_tab7_final") == "parafoudre",
                st.session_state.get("protec_t8_tab7_final") == "terre",
                st.session_state.get("protec_t9_tab7_final") == "NF C 15-100",
                st.session_state.get("protec_t10_tab7_final") == "sauté"
            ])

            st.session_state.score_vin7_p1 = round(float(score_q7), 1)
            st.session_state.score_vin7_p2 = round(float(score_t7), 1)
            st.session_state.score_final_vin7 = round(float(score_q7 + score_t7), 1)
            st.session_state.vin_verrouille_tab7 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML DE L'ATELIER 7 ---
    if st.session_state.get("vin_verrouille_tab7", False):
        scr1_p = st.session_state.get("score_vin7_p1", 0.0)
        scr2_p = st.session_state.get("score_vin7_p2", 0.0)
        tot_s_p = st.session_state.get("score_final_vin7", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin7 = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER PROTECTIONS SCELLE | Note de session : {tot_s_p:.1f} / 20")

        html_export_protec = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Protections et Securite - {n_eleve}</title>
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
                <p>Atelier 7 : Protection des personnes, des installations et mise a la terre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin7}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_p:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                - Note obtenue au Quiz Proprietes des Protections : <strong>{scr1_p:.1f} / 10</strong><br>
                - Note obtenue a la Synthese : <strong>{scr2_p:.1f} / 10</strong><br>
                - Note Totale de l'Atelier 7 : <strong>{tot_s_p:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_protec_tab7" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_protec_tab7, 1):
                saisie = st.session_state.get(f"protec_at7_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_protec += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_protec += """
                </tbody>
            </table>

            <div class="sub-title">CORRECTION DETAILLEE DES TROUS DE SYNTHESE</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Enonce de Cours (Trou)</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        phrases_trous7 = [
            ("Pour eviter l'electrocution, le seuil de sensibilite humaine maximum tolere est fixe a...", "30 mA", "protec_t1_tab7_final"),
            ("Le dispositif differentiel coupe le circuit s'il repere une difference entre la phase et le...", "neutre", "protec_t2_tab7_final"),
            ("L'evacuation des courants de defaut vers le sol est assuree par la prise de...", "terre", "protec_t3_tab7_final"),
            ("Une surconsommation d'appareils sur une meme ligne engendre une dangereuse...", "surcharge", "protec_t4_tab7_final"),
            ("Le contact accidentel et direct entre le fil de phase et le fil de neutre cree un...", "court-circuit", "protec_t5_tab7_final"),
            ("La protection thermique integree au disjoncteur divisionnaire protege contre la...", "surcharge", "protec_t6_tab7_final"),
            ("La protection magnetique d'un disjoncteur reagit instantanement lors d'un...", "court-circuit", "protec_t7_tab7_final"),
            ("Le composant charge de devier l'energie de la foudre vers le sol s'appelle le...", "parafoudre", "protec_t8_tab7_final"),
            ("La norme reglementant l'ensemble de l'installation electrique interieure est la...", "NF C 15-100", "protec_t9_tab7_final"),
            ("Pour s'assurer de l'efficacite de la terre, sa resistance mesuree doit etre inferieure a...", "100 Ohms", "protec_t10_tab7_final")
        ]

        for num, (enonce, attendu, cle_state) in enumerate(phrases_trous7, 1):
            saisie = st.session_state.get(cle_state, "Choisir...")
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_protec += f"<tr><td>{num}</td><td>{enonce}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_protec += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        # Optionnel : Ajout d'un bouton de téléchargement du fichier HTML généré
        st.download_button(
            label="Telecharger le rapport officiel de l'Atelier 7 (HTML)",
            data=html_export_protec,
            file_name=f"Rapport_Atelier_7_{n_eleve}_{p_eleve}.html",
            mime="text/html",
            use_container_width=True
        )



    
with tab7:

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
