
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application verin hydraulique ",
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
st.title("Application verin hydraulique")
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
    "Historique",
    "Les distributeurs hydraulique",
    "Le vérin simple effet",
    "Le vérin double effet",
    "Vérins rotatifs et autres actionneurs",
    "Application 1 ",
    "Application 2 "

])

tab0 = onglets[0]
tab1 = onglets[1] 
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4] 
tab5 = onglets[5] 
tab6 = onglets[6] 
tab7 = onglets[7] 


def afficher_atelier_verin_simple_effet_hydraulique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 3 (Vérin simple effet) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_vse_1", "q": "Dans combien de directions un vérin simple effet hydraulique peut-il développer un effort moteur sous l'action du fluide ?", "options": ["Un seul sens de marche", "Deux sens opposés", "Uniquement en rotation continue"], "rep": "Un seul sens de marche"},
        {"id": "h_vse_2", "q": "Comment s'effectue généralement la rentrée de la tige sur un cric de levage hydraulique ?", "options": ["Sous l'action d'une charge extérieure (le poids du véhicule) lors de l'ouverture de la purge", "Grâce à une inversion du débit de la pompe", "Par aspiration de l'air ambiant"], "rep": "Sous l'action d'une charge extérieure (le poids du véhicule) lors de l'ouverture de la purge"},
        {"id": "h_vse_3", "q": "Combien d'orifices de raccordement fluidique possède le corps d'un vérin simple effet ?", "options": ["Un seul orifice", "Deux orifices indépendants", "Trois orifices avec drainage"], "rep": "Un seul orifice"},
        {"id": "h_vse_4", "q": "Quel type de distributeur est le standard minimal pour piloter la sortie et la rentrée d'un simple effet ?", "options": ["Un distributeur 3/2", "Un distributeur 4/3", "Un clapet anti-retour double"], "rep": "Un distributeur 3/2"},
        {"id": "h_vse_5", "q": "Quelle pièce cylindrique interne reçoit la poussée de l'huile et sépare les zones du cylindre ?", "options": ["Le piston", "La tige traversante", "Le nez de guidage"], "rep": "Le piston"},
        {"id": "h_vse_6", "q": "Que devient l'huile contenue dans la chambre lors de la rentrée de la tige provoquée par la charge ?", "options": ["Elle est refoulée vers le réservoir (bac à huile)", "Elle s'échappe dans l'atmosphère", "Elle est comprimée et s'échauffe indéfiniment"], "rep": "Elle est refoulée vers le réservoir (bac à huile)"},
        {"id": "h_vse_7", "q": "Pourquoi un vérin hydraulique permet-il un maintien en position fixe parfait par rapport à un vérin pneumatique ?", "options": ["Car l'huile est un fluide incompressible, ce qui empêche tout effet d'élasticité ou de rebond", "Car l'huile colle le piston", "Car la tige est plus lourde"], "rep": "Car l'huile est un fluide incompressible, ce qui empêche tout effet d'élasticité ou de rebond"},
        {"id": "h_vse_8", "q": "Quel est le rôle de l'orifice d'évent situé sur la chambre opposée (sans huile) d'un vérin simple effet ?", "options": ["Permettre à l'air de s'échapper ou d'entrer librement lors des mouvements du piston", "Injecter de la graisse de lubrification", "Mesurer la pression de service"], "rep": "Permettre à l'air de s'échapper ou d'entrer librement lors des mouvements du piston"},
        {"id": "h_vse_9", "q": "Si on applique une pression de 100 bars sur un piston de surface 10 cm², la force de poussée développée est de :", "options": ["10 000 Newtons", "1 000 Newtons", "100 Newtons"], "rep": "10 000 Newtons"},
        {"id": "h_vse_10", "q": "L'usage classique d'un vérin simple effet hydraulique en atelier mécanique concerne :", "options": ["Le levage de charges lourdes (crics, presses d'atelier)", "Les va-et-vient à très haute cadence", "La préhension de pièces légères fragiles"], "rep": "Le levage de charges lourdes (crics, presses d'atelier)"}
    ]

    if "ordre_quiz_tab3_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab3_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro3_clean = [
        ("1. Le vérin simple effet hydraulique ne possède qu'un seul .......... de pression.", ["Choisir...", "orifice", "tiroir"], "orifice", "hydro3_t1"),
        ("2. L'effort moteur développé s'exerce exclusivement dans .......... seul sens.", ["Choisir...", "un", "deux"], "un", "hydro3_t2"),
        ("3. La rentrée de la tige d'un cric exploite le poids de la .......... extérieure.", ["Choisir...", "charge", "pompe"], "charge", "hydro3_t3"),
        ("4. Pendant la rentrée, l'huile de la chambre est refoulée vers le ..........", ["Choisir...", "réservoir", "piston"], "réservoir", "hydro3_t4"),
        ("5. L'incompressibilité de l'huile permet d'obtenir un blocage rigide et ..........", ["Choisir...", "précis", "élastique"], "précis", "hydro3_t5"),
        ("6. L'évacuation ou l'aspiration de l'air interne utilise un orifice d'..........", ["Choisir...", "évent", "pression"], "évent", "hydro3_t6"),
        ("7. Piloter l'alimentation d'un simple effet requiert un distributeur ..........", ["Choisir...", "3/2", "4/3"], "3/2", "hydro3_t7"),
        ("8. La force de levage s'exprime dans l'unité internationale du ..........", ["Choisir...", "newton", "bar"], "newton", "hydro3_t8"),
        ("9. L'étanchéité glissante autour du piston est assurée par des .......... spécifiques.", ["Choisir...", "joints", "bagues"], "joints", "hydro3_t9"),
        ("10. Ce composant convertit la puissance fluide en puissance .......... rectiligne.", ["Choisir...", "mécanique", "thermique"], "mécanique", "hydro3_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 3 (Texte à trous - 10 cases - 10 pts)")
        if "champs_hydro3_clean" in st.session_state:
            for ligne in st.session_state.champs_hydro3_clean:
                # Extraction par index pour supprimer le texte brut technique
                enonce = ligne[0]  # Extrait uniquement la phrase de cours propre
                choix = ligne[1]   # Extrait uniquement la liste des options de sélection
                cle = ligne[-1]    # Extrait la clé unique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_hydro3_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_distributeurs_hydrauliques(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 2 (Les distributeurs) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_dist_1", "q": "Quelle est la fonction principale d'un distributeur dans un circuit hydraulique de puissance ?", "options": ["Distribuer (aiguiller l'huile sous pression)", "Convertir l'énergie en force", "Filtrer les impuretés du fluide"], "rep": "Distribuer (aiguiller l'huile sous pression)"},
        {"id": "h_dist_2", "q": "Que signifie la désignation d'un distributeur normalisé de type '4/3' ?", "options": ["4 orifices et 3 positions de fonctionnement", "4 bars de pression et 3 L/min de débit", "4 pistons reliés à 3 réservoirs"], "rep": "4 orifices et 3 positions de fonctionnement"},
        {"id": "h_dist_3", "q": "À quoi sert spécifiquement la position centrale (neutre) d'un distributeur 4/3 à centre fermé ?", "options": ["À bloquer instantanément le vérin en coupant la circulation d'huile", "À purger l'huile vers l'extérieur", "À augmenter la vitesse de la pompe"], "rep": "À bloquer instantanément le vérin en coupant la circulation d'huile"},
        {"id": "h_dist_4", "q": "Comment appelle-t-on la pièce cylindrique rectiligne interne qui coulisse pour ouvrir ou fermer les voies ?", "options": ["Le tiroir", "Le clapet de décharge", "La membrane"], "rep": "Le tiroir"},
        {"id": "h_dist_5", "q": "Par quelle lettre normalisée ISO désigne-t-on l'orifice d'entrée relié à la pompe de pression ?", "options": ["P (Pression)", "T (Tank / Réservoir)", "A (Utilisation)"], "rep": "P (Pression)"},
        {"id": "h_dist_6", "q": "Par quelle lettre normalisée ISO désigne-t-on l'orifice de retour relié au réservoir d'huile ?", "options": ["T (Tank)", "P (Pression)", "B (Utilisation)"], "rep": "T (Tank)"},
        {"id": "h_dist_7", "q": "Sur un schéma normalisé, comment modélise-t-on un orifice obturé (voie fermée) ?", "options": ["Par un symbole en forme de T", "Par une flèche oblique", "Par un cercle barré"], "rep": "Par un symbole en forme de T"},
        {"id": "h_dist_8", "q": "Quel type de commande utilise un signal électrique (bobine) pour déplacer mécaniquement le tiroir ?", "options": ["Une commande par électrovanne (solénoïde)", "Une commande par levier manuel", "Une commande par pédale"], "rep": "Une commande par électrovanne (solénoïde)"},
        {"id": "h_dist_9", "q": "Pourquoi les distributeurs hydrauliques de forte puissance possèdent-ils souvent un drainage externe ?", "options": ["Pour évacuer les fuites internes d'huile vers le réservoir sans bloquer le tiroir", "Pour refroidir la bobine", "Pour ajouter de l'huile neuve"], "rep": "Pour évacuer les fuites internes d'huile vers le réservoir sans bloquer le tiroir"},
        {"id": "h_dist_10", "q": "Dans quelle case d'un schéma normalisé à 3 positions raccorde-t-on les tuyaux de l'installation ?", "options": ["Dans la case centrale (position de repos)", "Dans la case de gauche", "Dans la case de droite"], "rep": "Dans la case centrale (position de repos)"}
    ]

    if "ordre_quiz_tab2_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab2_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro2_clean = [
        ("1. Le distributeur assure la fonction de .......... de l'énergie fluide.", ["Choisir...", "distribution", "conversion"], "distribution", "hydro2_t1"),
        ("2. Le premier chiffre d'un symbole normalisé indique le nombre d'..........", ["Choisir...", "orifices", "positions"], "orifices", "hydro2_t2"),
        ("3. Le second chiffre d'un symbole indique le nombre de .......... de fonctionnement.", ["Choisir...", "positions", "voies"], "positions", "hydro2_t3"),
        ("4. La pièce interne mobile qui coulisse pour orienter les flux est le ..........", ["Choisir...", "tiroir", "clapet"], "tiroir", "hydro2_t4"),
        ("5. L'orifice P est directement raccordé à la ligne de .......... de la pompe.", ["Choisir...", "pression", "réservoir"], "pression", "hydro2_t5"),
        ("6. L'huile usagée retourne au réservoir à travers l'orifice ..........", ["Choisir...", "T", "A"], "T", "hydro2_t6"),
        ("7. Un distributeur 4/3 possède rigoureusement .......... positions distinctes.", ["Choisir...", "trois", "deux"], "3", "hydro2_t7"),
        ("8. Le centre fermé permet d'immobiliser et de .......... l'actionneur.", ["Choisir...", "bloquer", "accélérer"], "bloquer", "hydro2_t8"),
        ("9. Une commande électrique s'appuie sur l'excitation d'un ..........", ["Choisir...", "solénoïde", "manomètre"], "solénoïde", "hydro2_t9"),
        ("10. Les flèches internes indiquent le sens de circulation du ..........", ["Choisir...", "fluide", "ressort"], "fluide", "hydro2_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 2 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_hydro2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_hydro2_clean", disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_historique_hydraulique(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Historique) sur deux colonnes."""
    import random

    questions_sources = [
        {"id": "h_hist_1", "q": "Quelle civilisation antique a largement développé les premiers moulins à eau pour moudre le grain ?", "options": ["Les Romains", "Les Mayas", "Les Vikings"], "rep": "Les Romains"},
        {"id": "h_hist_2", "q": "Quel ingénieur britannique a inventé la première presse hydraulique industrielle en 1795 ?", "options": ["Joseph Bramah", "James Watt", "Nikola Tesla"], "rep": "Joseph Bramah"},
        {"id": "h_hist_3", "q": "Quel savant français a énoncé le principe de transmission de la pression dans les liquides au XVIIe siècle ?", "options": ["Blaise Pascal", "René Descartes", "Antoine Lavoisier"], "rep": "Blaise Pascal"},
        {"id": "h_hist_4", "q": "Dans un moulin à eau traditionnel, quel composant mécanique reçoit directement la force du courant de la rivière ?", "options": ["La roue à aubes", "Le piston", "Le distributeur"], "rep": "La roue à aubes"},
        {"id": "h_hist_5", "q": "Quel est l'avantage historique majeur de la presse hydraulique par rapport aux mécanismes à leviers ?", "options": ["Multiplier les forces de manière considérable dans un espace réduit", "Fonctionner sans aucun fluide", "Produire de l'électricité"], "rep": "Multiplier les forces de manière considérable dans un espace réduit"},
        {"id": "h_hist_6", "q": "Quelle forme d'énergie est initialement captée par une roue hydraulique ?", "options": ["L'énergie cinétique et potentielle de l'eau", "L'énergie thermique du soleil", "L'énergie chimique"], "rep": "L'énergie cinétique et potentielle de l'eau"},
        {"id": "h_hist_7", "q": "Comment appelle-t-on la science qui étudie les fluides sous pression pour transmettre de la puissance ?", "options": ["L'oléohydraulique", "L'aérodynamique", "La thermodynamique"], "rep": "L'oléohydraulique"},
        {"id": "h_hist_8", "q": "Quel joint historique a permis d'assurer l'étanchéité des premiers pistons de Bramah sans bloquer le mouvement ?", "options": ["Le joint en cuir en forme de U", "La bague en plastique", "Le joint en silicone"], "rep": "Le joint en cuir en forme de U"},
        {"id": "h_hist_9", "q": "Les premiers réseaux de distribution d'énergie hydraulique dans les villes au XIXe siècle utilisaient :", "options": ["De l'eau sous pression", "De l'huile synthétique", "Du mercure lourd"], "rep": "De l'eau sous pression"},
        {"id": "h_hist_10", "q": "Le principe de Pascal affirme que dans un fluide incompressible en équilibre, la pression se transmet :", "options": ["Intégralement dans toutes les directions", "Uniquement vers le bas", "Uniquement vers la droite"], "rep": "Intégralement dans toutes les directions"}
    ]

    if "ordre_quiz_tab1_hydro_aleatoire" not in st.session_state:
        random.shuffle(questions_sources)
        st.session_state.ordre_quiz_tab1_hydro_aleatoire = questions_sources

    st.session_state.champs_hydro1_clean = [
        ("1. Les Romains utilisons l'énergie des rivières grâce aux moulins à ..........", ["Choisir...", "eau", "vent"], "eau", "hydro1_t1"),
        ("2. Le théorème de transmission de la pression a été formulé par ..........", ["Choisir...", "Pascal", "Bramah"], "Pascal", "hydro1_t2"),
        ("3. L'invention de la presse hydraulique est l'œuvre de Joseph ..........", ["Choisir...", "Bramah", "Watt"], "Bramah", "hydro1_t3"),
        ("4. Capter la force motrice du fluide utilise une roue à ..........", ["Choisir...", "aubes", "tiroirs"], "aubes", "hydro1_t4"),
        ("5. La presse hydraulique permet de multiplier considérablement les ..........", ["Choisir...", "forces", "vitesses"], "forces", "hydro1_t5"),
        ("6. L'huile industrielle moderne sert de fluide .......... pour la puissance.", ["Choisir...", "caloporteur", "transmetteur"], "transmetteur", "hydro1_t6"),
        ("7. Assurer l'étanchéité des premiers pistons utilisait un joint en ..........", ["Choisir...", "cuir", "caoutchouc"], "cuir", "hydro1_t7"),
        ("8. L'étude de l'utilisation technique de l'huile s'appelle l'..........", ["Choisir...", "oléohydraulique", "aéronautique"], "oléohydraulique", "hydro1_t8"),
        ("9. Dans un liquide au repos, la pression s'exerce de manière ..........", ["Choisir...", "isotrope", "unilatérale"], "isotrope", "hydro1_t9"),
        ("10. Ce parcours historique introduit la fonction d'alimentation en ..........", ["Choisir...", "débit", "chaleur"], "débit", "hydro1_t10")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_hydro_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"hydro_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        if "champs_hydro1_clean" in st.session_state:
            for ligne in st.session_state.champs_hydro1_clean:
                # Ajout obligatoire des crochets d'indexation pour découper le tuple
                enonce = ligne[0]  # Extrait uniquement la phrase de cours propre
                choix = ligne[1]   # Extrait uniquement la liste des options ['Choisir...', ...]
                cle = ligne[-1]    # Extrait la clé unique de session
                
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: 
                    st.write(enonce)
                with c_sel: 
                    st.selectbox("", choix, key=f"{cle}_hydro1_clean", disabled=verrouille, label_visibility="collapsed")




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
    st.header("Historique de l'hydraulique de puissance")
    
    st.subheader("De l'énergie de l'eau aux forces industrielles")
    st.write(
        "L'histoire de l'hydraulique se divise en deux grandes époques : l'hydraulique naturelle (hydrodynamique) "
        "et l'hydraulique industrielle de puissance (oléohydraulique).\n\n"
        "Dès l'Antiquité, les Romains exploitent l'énergie cinétique des cours d'eau en installant de grands moulins "
        "à eau munis de **roues à aubes**. Cette technologie convertit la puissance du courant en force mécanique rotative "
        "pour actionner des meules à grains ou des martinets de forge, remplaçant la force humaine ou animale.\n\n"
        "La véritable révolution s'opère au dix-huitième siècle. En s'appuyant sur les travaux mathématiques de "
        "**Blaise Pascal** (qui démontra qu'une pression appliquée sur un liquide enfermé se transmet intégralement dans toutes "
        "les directions), l'ingénieur mécanicien anglais **Joseph Bramah** invente en 1795 la première **presse hydraulique**.\n"
        "En injectant de l'eau sous pression à l'aide d'une petite pompe vers un grand piston esclave, Bramah réussit "
        "à multiplier les forces de manière phénoménale, ouvrant la voie aux engins de levage lourds modernes."
    )
    
    st.divider()
    
    # --- SIMULATEUR DYNAMIQUE : LA ROUE À AUBES INTERACTIVE ---
    
    col_graph, col_bd = st.columns([0.55, 0.45])
    
    with col_graph:
        if "angle_roue" not in st.session_state:
            st.session_state.angle_roue = 0.0
        if "animation_active" not in st.session_state:
            st.session_state.animation_active = False

        st.subheader("Simulateur de roue hydraulique en mouvement")
        
        # Commandes de la vanne
        c_btn1, c_btn2 = st.columns(2)
        with c_btn1:
            if st.button("OUVRIR LES VANNES (LANCER LA ROUE)", key="btn_run_wheel_fluid", use_container_width=True):
                st.session_state.animation_active = True
        with c_btn2:
            if st.button("FERMER LES VANNES (ARRÊTER)", key="btn_stop_wheel_fluid", use_container_width=True):
                st.session_state.animation_active = False

        # Curseur de débit
        debit_riviere = st.slider(
            "Ajuster le débit de la rivière (L/s) :", 
            min_value=0, 
            max_value=200, 
            value=80, 
            step=20, 
            key="slider_debit_h1_fluid"
        )

        # Création de zones réservées pour éviter que le texte et l'image ne sautent
        plot_placeholder = st.empty()
        metric_placeholder = st.empty()

        # Moteur de rendu graphique Matplotlib
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        def generer_figure_roue(angle):
            fig, ax = plt.subplots(figsize=(5, 3.8), facecolor="white")
            ax.set_facecolor("white")
            
            # Écoulement de l'eau en fond (si la roue tourne)
            if st.session_state.animation_active and debit_riviere > 0:
                ax.add_patch(patches.Rectangle((0, 0), 5, 0.8, facecolor="#38bdf8", alpha=0.5, zorder=1))
            
            # Corps de la roue
            ax.add_patch(patches.Circle((2.5, 1.5), 1.0, facecolor="none", edgecolor="#1e293b", linewidth=3, zorder=2))
            ax.add_patch(patches.Circle((2.5, 1.5), 0.15, facecolor="#475569", zorder=3))
            
            # Les 8 aubes
            nb_aubes = 8
            for a in range(nb_aubes):
                angle_rad = np.radians(a * (360 / nb_aubes) + angle)
                x_aube = 2.5 + 1.2 * np.cos(angle_rad)
                y_aube = 1.5 + 1.2 * np.sin(angle_rad)
                ax.plot([2.5, x_aube], [1.5, y_aube], color="#475569", linewidth=2.5, zorder=2)
                
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 3)
            ax.axis("off")
            return fig

        # --- BOUCLE D'ANIMATION LOCALE SANS RECHARGEMENT DE PAGE ---
        if st.session_state.animation_active and debit_riviere > 0:
            # Tant que l'animation est active, on met à jour uniquement les placeholders locaux
            while st.session_state.animation_active:
                vitesse_rotation = debit_riviere * 0.15
                puissance_recoltee = debit_riviere * 9.81 * 2.0 * 0.7
                
                # Mise à jour de l'image seule
                fig_actuelle = generer_figure_roue(st.session_state.angle_roue)
                plot_placeholder.pyplot(fig_actuelle)
                plt.close(fig_actuelle) # Fermeture immédiate de la figure pour libérer la mémoire RAM
                
                # Mise à jour des valeurs textuelles seules
                with metric_placeholder:
                    st.metric(label="Puissance mécanique récupérée", value=f"{puissance_recoltee:.0f} Watts", delta=f"{vitesse_rotation:.1f} tr/min")
                
                # Calcul du prochain angle
                st.session_state.angle_roue += (debit_riviere / 40.0)
                if st.session_state.angle_roue >= 360.0:
                    st.session_state.angle_roue = 0.0
                    
                # Pause courte pour stabiliser le framerate
                time.sleep(0.02)
        else:
            # Affichage fixe de sécurité si la roue est arrêtée
            fig_statique = generer_figure_roue(st.session_state.angle_roue)
            plot_placeholder.pyplot(fig_statique)
            plt.close(fig_statique)
            with metric_placeholder:
                st.metric(label="Puissance mécanique récupérée", value="0 Watts", delta="0.0 tr/min (Arrêté)")

    with col_bd:
        st.write("**La BD humoristique textuelle : L'astuce de Bramah**")
        st.info(
            "**Case 1 :** Un forgeron londonien du XVIIIe siècle s'épuise à frapper sur une enclume avec un énorme marteau en fer pour aplatir une barre de métal : 'Mes bras vont lâcher, il me faudrait la force de dix hommes !'.\n\n"
            "**Case 2 :** Joseph Bramah arrive dans l'atelier avec un grand sourire et pose une cuve métallique munie de deux tuyaux : 'Laisse ton marteau, l'ami ! On va faire travailler l'eau sous pression !'.\n\n"
            "**Case 3 :** Bramah actionne un tout petit levier de pompe sans aucun effort. À l'autre bout de la conduite, le grand piston descend avec la force d'un éléphant et écrase la barre de fer comme de la pâte à modeler : 'Crac !'.\n\n"
            "**Case 4 :** Le forgeron regarde ses bras musclés puis le piston avec stupéfaction. Bramah clin d'œil : 'C'est le secret de Blaise Pascal : tu pousses un centimètre cube d'eau d'un côté, et ça repousse cent centimètres carrés de l'autre !'."
        )
        
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 1 ---
    if "suite_verrouille_tab1_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab1_hydro = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_hydro

    # Affichage du module de questions spécifique à l'histoire
    afficher_atelier_historique_hydraulique(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 1.",
        key="check_certif_hydro1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_hydro_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q1 += 1.0

            score_t1 = 0.0
            if "champs_hydro1_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro1_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_hydro1_clean", "Choisir...") == attendu: score_t1 += 1.0

            st.session_state.score_suite1_hydro_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_hydro_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_hydro = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML SCÉLLÉ ---
    if st.session_state.get("suite_verrouille_tab1_hydro", False):
        scr1_t1 = st.session_state.get("score_suite1_hydro_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_hydro_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_hydro", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER 1 SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_hydro1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Historique Hydraulique - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Sciences Physiques</h1>
                <p>Atelier 1 : Historique de l'hydraulique et théorème de Pascal</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0f172a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab1_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 1
        if "champs_hydro1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 1
        html_export_hydro1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro1 = preparer_nom_fichier("Rapport_Histoire_Hydraulique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_hydro1,
            file_name=nom_fichier_html_hydro1,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Les distributeurs hydrauliques")
    
    # --- SECTION COURS : LES PRINCIPES DE LA DISTRIBUTION ---
    st.subheader("Rôle et architecture des pré-actionneurs hydrauliques")
    st.write(
        "Dans un circuit hydraulique industrielle de puissance, le distributeur fait office d'aiguilleur. "
        "Il reçoit l'huile sous haute pression en provenance directe de la pompe et l'oriente vers les canalisations "
        "utiles pour commander les actionneurs (vérins ou moteurs), tout en organisant le retour de l'huile viciée "
        "vers le réservoir central (bac).\n\n"
        "L'architecture interne repose sur un **tiroir métallique** rectifié au micron près qui coulisse à l'intérieur "
        "du corps de l'appareil. En se déplaçant, les collets du tiroir viennent masquer ou ouvrir les canaux internes. "
        "L'étanchéité reposant sur le film d'huile entre le tiroir et le corps, un léger débit de fuite interne existe "
        "toujours à haute pression, ce qui nécessite parfois un canal de drainage externe pour éviter le blocage mécanique."
    )
    
    st.divider()
    
    st.subheader("Lecture des symboles ISO normalisés : Le standard 4/3")
    st.write(
        "L'hydraulique utilise massivement des distributeurs à **3 positions (comme le 4/3)** pour permettre le blocage ou "
        "la mise en roue libre des mécanismes lourds. Sa codification s'énonce ainsi :\n"
        "* **Le premier chiffre (4) :** Indique le nombre d'orifices (P pour la Pression de la pompe, T pour le Tank/Réservoir, "
        "A et B pour les conduites reliées aux chambres de l'actionneur).\n"
        "* **Le second chiffre (3) :** Indique le nombre de cases carrées juxtaposées, modélisant les 3 configurations de flux possibles.\n\n"
        "Par convention internationale, les raccordements des canalisations extérieures sont toujours dessinés graphiquement "
        "sur la case centrale représentant la position de **repos / neutre**."
    )
    
    st.divider()
    
    # --- LAB INTERACTIF : SCHÉMA DYNAMIQUE DU TIROIR COMMUTABLE ---
    st.subheader("Simulateur graphique d'aiguillage de fluide")
    st.write(
        "Sélectionnez la position du distributeur 4/3 à l'aide des boutons ci-dessous. "
        "Le graphique Matplotlib redessinera instantanément la position du tiroir interne et colorera les flux d'huile active."
    )
    
    # Boutons radio horizontaux pour le choix de la position
    pos_choisie = st.radio(
        "Sélectionner l'état de la commande :",
        options=["Position de gauche (Voie croisée)", "Position centrale (Repos - Centre fermé)", "Position de droite (Voie droite)"],
        index=1,
        key="radio_pos_dist_h2",
        horizontal=True
    )
    
    col_dist_graph, col_dist_bd = st.columns([0.55, 0.45])

    with col_dist_graph:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig_ds, ax_ds = plt.subplots(figsize=(5.5, 4.2), facecolor="white")
        ax_ds.set_facecolor("white")
        
        # 1. Dessin du corps externe fixe du distributeur (Chambre d'alésage)
        ax_ds.add_patch(patches.Rectangle((0.8, 1.0), 3.4, 1.2, facecolor="#f8fafc", edgecolor="#475569", linewidth=3, zorder=1))
        
        # 2. Dessin des conduites fixes externes (Canalisations d'usine)
        ax_ds.plot([1.5, 1.5], [0.3, 1.0], color="#334155", linewidth=3, zorder=2) # P
        ax_ds.plot([3.5, 3.5], [0.3, 1.0], color="#334155", linewidth=3, zorder=2) # T
        ax_ds.plot([1.8, 1.8], [2.2, 2.9], color="#334155", linewidth=3, zorder=2) # A
        ax_ds.plot([3.2, 3.2], [2.2, 2.9], color="#334155", linewidth=3, zorder=2) # B
        
        # Lettrage normalisé ISO
        ax_ds.text(1.5, 0.05, "P\n(Pompe)", weight="bold", ha="center", color="#b91c1c", fontsize=10)
        ax_ds.text(3.5, 0.05, "T\n(Réservoir)", weight="bold", ha="center", color="#0284c7", fontsize=10)
        ax_ds.text(1.8, 3.05, "A", weight="bold", ha="center", color="#1e293b", fontsize=11)
        ax_ds.text(3.2, 3.05, "B", weight="bold", ha="center", color="#1e293b", fontsize=11)
        
        # 3. Logique mécanique des positions du tiroir
        if "gauche" in pos_choisie:
            dx_tiroir = -0.5
            annotation_etat = "ALIMENTATION DE B (HAUTE PRESSION) | RETOUR DE A VERS T"
            
            # Flèche Pression : P -> B (Croisé, vers le haut et la droite)
            ax_ds.arrow(1.5, 1.05, 1.6, 1.05, head_width=0.15, head_length=0.15, fc="#b91c1c", ec="#b91c1c", linewidth=4, length_includes_head=True, zorder=4)
            # Flèche Retour : A -> T (Croisé, vers le bas et la droite)
            ax_ds.arrow(1.8, 2.15, 1.6, -1.05, head_width=0.15, head_length=0.15, fc="#0284c7", ec="#0284c7", linewidth=4, length_includes_head=True, zorder=4)
            
        elif "droite" in pos_choisie:
            dx_tiroir = 0.5
            annotation_etat = "ALIMENTATION DE A (HAUTE PRESSION) | RETOUR DE B VERS T"
            
            # Flèche Pression : P -> A (Droit, vers le haut et la droite)
            ax_ds.arrow(1.5, 1.05, 0.25, 1.05, head_width=0.15, head_length=0.15, fc="#b91c1c", ec="#b91c1c", linewidth=4, length_includes_head=True, zorder=4)
            # Flèche Retour : B -> T (Droit, vers le bas et la droite)
            ax_ds.arrow(3.2, 2.15, 0.25, -1.05, head_width=0.15, head_length=0.15, fc="#0284c7", ec="#0284c7", linewidth=4, length_includes_head=True, zorder=4)
            
        else:
            dx_tiroir = 0.0
            annotation_etat = "CENTRE FERMÉ : TOUT EST BLOQUÉ (VÉRIN IMMOBILISÉ)"
            
            # Représentation graphique des symboles de voies obturées (T de blocage)
            # Blocage Pression au seuil inférieur
            ax_ds.plot([1.3, 1.7], [1.1, 1.1], color="#b91c1c", linewidth=4, zorder=5)
            # Blocage Réservoir
            ax_ds.plot([3.3, 3.7], [1.1, 1.1], color="#64748b", linewidth=4, zorder=5)
            # Blocage des orifices d'utilisation au seuil supérieur
            ax_ds.plot([1.6, 2.0], [2.1, 2.1], color="#64748b", linewidth=4, zorder=5)
            ax_ds.plot([3.0, 3.4], [2.1, 2.1], color="#64748b", linewidth=4, zorder=5)
            
        # 4. Dessin de la pièce mobile interne (Axe du tiroir + collets d'étanchéité)
        x_tiroir_base = 1.0 + dx_tiroir
        # Axe central gris
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base - 0.3, 1.45), 3.6, 0.3, facecolor="#64748b", edgecolor="#334155", linewidth=1.5, zorder=3))
        
        # Collets d'étanchéité (Les pistons internes qui ferment physiquement les trous)
        # Collet gauche
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base + 0.3, 1.05), 0.5, 1.1, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        # Collet droit
        ax_ds.add_patch(patches.Rectangle((x_tiroir_base + 2.2, 1.05), 0.5, 1.1, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        
        # 5. Habillage du graphique
        ax_ds.set_xlim(0, 5)
        ax_ds.set_ylim(-0.3, 3.5)
        ax_ds.axis("off")
        st.pyplot(fig_ds)
        
        # En-tête textuel coloré dynamique sous le schéma
        if "Centre" in annotation_etat:
            st.error(annotation_etat)
        else:
            st.success(annotation_etat)

    with col_dist_bd:
        st.write("**La BD humoristique textuelle : Le carrefour des vannes**")
        st.info(
            "**Case 1 :** Un groupe de molécules d'huile arrive à toute vitesse dans un tuyau, poussé par la pompe : "
            "'On arrive en ville à 200 bars, ouvrez la route !'. Elles tombent sur une barrière grise fermée.\n\n"
            "**Case 2 :** Un petit aiguilleur en casquette (le solénoïde électrique) appuie sur un bouton. "
            "Le gros tiroir métallique interne glisse latéralement dans un bruit de friction métallique : 'Schliiiit !'.\n\n"
            "**Case 3 :** Les canaux s'alignent. Les molécules d'huile s'engouffrent en ligne droite vers l'orifice A : "
            "'Voie dégagée ! Tout le monde fonce dans la chambre arrière du vérin pour soulever la grue !'.\n\n"
            "**Case 4 :** Soudain, l'automate coupe le courant. Le gros ressort de rappel repousse le tiroir au centre. "
            "Les molécules se retrouvent instantanément bloquées dans une impasse étanche : "
            "'Fin du voyage ! Centre fermé ! Tout le monde s'arrête sur place et maintient la charge en l'air !'."
        )
        
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab2_hydro = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_hydro

    # Affichage du module de questions spécifique aux distributeurs hydrauliques
    afficher_atelier_distributeurs_hydrauliques(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    
    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 2.",
        key="check_certif_hydro2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_hydro_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q2 += 1.0

            score_t2 = 0.0
            if "champs_hydro2_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro2_clean:
                    cle = ligne[-1]
                    attendu = ligne[2]
                    if st.session_state.get(f"{cle}_hydro2_clean", "Choisir...") == attendu: score_t2 += 1.0

            st.session_state.score_suite2_hydro_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_hydro_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_hydro = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_hydro", False):
        scr1_t2 = st.session_state.get("score_suite2_hydro_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_hydro_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_hydro", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")
        st.success(f"ATELIER DISTRIBUTEURS SCELLÉ | Note de session : {tot_s_t2:.1f} / 20")

        html_export_hydro2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Distributeurs Hydrauliques - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 2 : Organes de distribution, tiroirs micrométriques et symbolisation ISO 4/3</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Extraction et injection des lignes de correction du Quiz technique
        if "ordre_quiz_tab2_hydro_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_hydro_aleatoire, 1):
                saisie = st.session_state.get(f"hydro_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Extraction et injection des lignes de correction du texte à trous
        if "champs_hydro2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 2
        html_export_hydro2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro2 = preparer_nom_fichier("Rapport_Distributeurs_Hydrauliques").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_hydro2,
            file_name=nom_fichier_html_hydro2,
            mime="text/html",
            use_container_width=True
        )


with tab3:
    st.header("Le vérin simple effet")
    
    # --- SECTION COURS : LE VÉRIN SIMPLE EFFET ---
    st.subheader("Constitution et loi physique de l'actionneur unidirectionnel")
    st.write(
        "Un vérin simple effet (VSE) hydraulique est un actionneur linéaire conçu pour développer une force "
        "motrice dans **un seul sens de marche**. Le corps du vérin ne comporte qu'une seule chambre étanche "
        "destinée à recevoir l'huile sous haute pression.\n\n"
        "Le mouvement inverse (généralement la rentrée de la tige) n'est pas provoqué par le fluide. Il utilise "
        "soit l'action d'un ressort mécanique interne de rappel, soit l'action d'une **force extérieure** "
        "(comme le poids d'une voiture sur un cric d'atelier ou la gravité sur une table élévatrice).\n\n"
        "L'avantage majeur de l'hydraulique par rapport à la pneumatique réside dans l'**incompressibilité du liquide**. "
        "Lorsqu'on ferme la vanne d'admission, l'huile emprisonnée se comporte comme un bloc d'acier rigide : "
        "le vérin reste parfaitement figé à sa hauteur, sans aucun rebond ni affaissement élastique, garantissant "
        "une sécurité absolue lors du levage de charges lourdes."
    )
    
    st.divider()
    
    # --- LAB INTERACTIF : SIMULATEUR DE CRIC D'ATELIER DYNAMIQUE ---
    st.subheader("Simulateur graphique de cric de levage hydraulique")
    st.write(
        "Utilisez les boutons ci-dessous pour injecter l'huile (Sortie de la tige pour soulever la charge) "
        "ou ouvrir la vanne de retour (Rentrée de la tige sous le poids de la charge)."
    )
    
           
    col_vse_graph, col_vse_bd = st.columns([0.55, 0.45])
        
    with col_vse_graph:
        # --- INITIALISATION DE SÉCURITÉ DE L'ONGLET 3 (SIMPLE EFFET) ---
        if "pos_vse_hyd" not in st.session_state:
            st.session_state.pos_vse_hyd = 0.0
        if "vse_mouvement" not in st.session_state:
            st.session_state.vse_mouvement = "ARRET"
        if "temps_debut_vse" not in st.session_state:
            st.session_state.temps_debut_vse = 0.0
        if "temps_course_vse" not in st.session_state:
            st.session_state.temps_course_vse = 0.0

        st.subheader("Simulateur chronométré de cric de levage")
        st.write(
            "Sélectionnez le type d'huile hydraulique pour analyser l'impact de la viscosité cinématique "
            "sur le temps de course et le coulissement géométrique de la tige."
        )

        type_huile = st.selectbox(
            "Sélectionner l'application et le type de fluide hydraulique :",
            options=[
                "Automobile - Cric de levage d'atelier (Huile fluide ISO VG 32 - Faible frottement)",
                "Maintenance - Presse hydraulique d'atelier (Huile standard ISO VG 46 - Frottement moyen)",
                "Travaux Publics - Flèche de pelle mécanique (Huile minérale HV 46 - Très haute résistance)",
                "Agriculture - Vérin de benne de tracteur (Huile épaisse ISO VG 68 - Fort frottement fluide)"
            ],
            key="select_huile_vse_final_secured"
        )

        # Réglage du pas de course selon la viscosité choisie
        if "Automobile" in type_huile:
            pas_course = 0.05
            course_max_reelle_mm = 200.0  # Course courte pour un cric de voiture
        elif "Maintenance" in type_huile:
            pas_course = 0.03
            course_max_reelle_mm = 400.0  # Presse standard
        elif "Travaux Publics" in type_huile:
            pas_course = 0.022
            course_max_reelle_mm = 800.0  # Gros vérin de flèche TP
        else:  # Agriculture
            pas_course = 0.015
            course_max_reelle_mm = 1200.0 # Course gigantesque pour une benne de tracteur


        # Verrouillage automatique des boutons pendant le mouvement
        boutons_bloques = (st.session_state.vse_mouvement != "ARRET")

        c_cmd1, c_cmd2 = st.columns(2)
        with c_cmd1:
            if st.button("ALIMENTER L'ORIFICE 1 (SORTIE CHRONOMÉTRÉE)", key="btn_push_vse_real_fixed", use_container_width=True, disabled=boutons_bloques or st.session_state.pos_vse_hyd >= 1.0):
                st.session_state.vse_mouvement = "SORTIE"
                st.session_state.temps_debut_vse = time.time()
                st.rerun()
        with c_cmd2:
            if st.button("OUVRIR LE RETOUR AU BAC (RENTRÉE CHRONOMÉTRÉE)", key="btn_purge_vse_real_fixed", use_container_width=True, disabled=boutons_bloques or st.session_state.pos_vse_hyd <= 0.0):
                st.session_state.vse_mouvement = "RENTREE"
                st.session_state.temps_debut_vse = time.time()
                st.rerun()

        # Rendu géométrique Matplotlib Réaliste (Cric simple effet avec tige fixe qui glisse)
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig_v, ax_v = plt.subplots(figsize=(6, 3.5), facecolor="white")
        ax_v.set_facecolor("white")
        
        # 1. Corps fixe du cylindre (x=0.5 à x=3.5)
        ax_v.add_patch(patches.Rectangle((0.5, 1.0), 3.0, 1.4, facecolor="#f1f5f9", edgecolor="#475569", linewidth=2.5, zorder=1))
        # Nez de guidage étanche (Limite avant fixe à x=3.5)
        ax_v.plot([3.5, 3.5], [1.0, 2.4], color="#334155", linewidth=3, zorder=2)
        
        # Un seul orifice d'admission d'huile inférieur (Simple Effet)
        ax_v.plot([1.0, 1.0], [0.4, 1.0], color="#334155", linewidth=2.5, zorder=2)
        ax_v.text(1.0, 0.15, "Orifice 1", weight="bold", ha="center", fontsize=9)
        # Évent de décharge d'air supérieur (Pas d'huile à l'avant)
        ax_v.plot([3.0, 3.0], [2.4, 2.8], color="#64748b", linewidth=1.5, zorder=2)
        
        # 2. Calcul du déplacement interne basé sur pos_vse_hyd (Course max de 2.6 unités)
        course_vse_pixels = st.session_state.pos_vse_hyd * 2.6
        x_piston_vse = 0.6 + course_vse_pixels
        
        # Détermination de la couleur de l'huile dans la chambre unique
        if st.session_state.vse_mouvement == "SORTIE":
            color_fluide_vse = "#b91c1c" # Rouge (Haute Pression active)
        elif st.session_state.vse_mouvement == "RENTREE":
            color_fluide_vse = "#0284c7" # Bleu (Refoulement vers le réservoir)
        else:
            color_fluide_vse = "#eab308" # Ambre au repos
            
        # Remplissage dynamique de la chambre arrière étanche
        if x_piston_vse > 0.62:
            ax_v.add_patch(patches.Rectangle((0.52, 1.03), x_piston_vse - 0.52, 1.34, facecolor=color_fluide_vse, alpha=0.5, zorder=1))
            
        # 3. Piston intérieur mobile (Largeur fixe 0.3)
        ax_v.add_patch(patches.Rectangle((x_piston_vse, 1.03), 0.3, 1.34, facecolor="#1e293b", edgecolor="black", linewidth=1.5, zorder=3))
        
        # --- STRUCTURE RESPECTÉE : LA TIGE POSSÈDE UNE LONGUEUR STRICTEMENT FIXE ---
        # Elle ne s'étire pas, elle coulisse de gauche à droite car son point de départ 
        # est soudé à la face avant du piston (x_piston_vse + 0.3).
        longueur_tige_simple_effet = 3.5
        ax_v.add_patch(patches.Rectangle((x_piston_vse + 0.3, 1.45), longueur_tige_simple_effet, 0.5, facecolor="#94a3b8", edgecolor="#334155", linewidth=1.5, zorder=2))
        
        # Flèche vectorielle de force interne (Uniquement lors de la poussée de sortie)
        if st.session_state.vse_mouvement == "SORTIE":
            ax_v.arrow(0.55, 1.7, (x_piston_vse - 0.55), 0, head_width=0.12, head_length=0.12, fc="#b91c1c", ec="#b91c1c", linewidth=3, length_includes_head=True, zorder=4)
            
        # La flèche de charge reste fixée à l'extrémité de la longue barre en acier qui glisse
        x_bout_tige_vse = x_piston_vse + 0.3 + longueur_tige_simple_effet
        ax_v.arrow(x_bout_tige_vse + 0.6, 1.7, -0.5, 0, head_width=0.12, head_length=0.12, fc="black", ec="black", linewidth=2.5, length_includes_head=True, zorder=4)
        ax_v.text(x_bout_tige_vse + 0.1, 1.9, r"$\vec{F}_{\text{charge}}$", color="black", weight="bold", fontsize=11)
        
        # Champ large (xlim jusqu'à 8.5) pour voir coulisser la barre à 100% à l'extérieur
        ax_v.set_xlim(0, 8.5)
        ax_v.set_ylim(-0.2, 3.2)
        ax_v.axis("off")
        
        st.pyplot(fig_v)
        plt.close(fig_v)

        st.write("**Schéma normalisé d'implantation industrielle (Norme ISO 1219) :**")
        
        fig_symb, ax_symb = plt.subplots(figsize=(6, 1.4), facecolor="white")
        ax_symb.set_facecolor("white")
        
        # Enveloppe extérieure carrée du symbole ISO du vérin
        ax_symb.plot([1.5, 4.5, 4.5, 1.5, 1.5], [0.3, 0.3, 1.3, 1.3, 0.3], color="black", linewidth=2)
        
        # Orifice d'entrée unique à gauche du symbole
        ax_symb.plot([2.0, 2.0], [0.0, 0.3], color="black", linewidth=2)
        
        # Piston modélisé par une ligne verticale interne
        x_piston_symb = 1.8 + (st.session_state.pos_vse_hyd * 1.5)
        ax_symb.plot([x_piston_symb, x_piston_symb], [0.3, 1.3], color="black", linewidth=2.5)
        
        # Tige modélisée par une ligne horizontale sortante à droite
        ax_symb.plot([x_piston_symb, 5.5], [0.8, 0.8], color="black", linewidth=2.5)
        
        # Dessin du ressort de rappel normalisé (lignes brisées en zigzag dans la chambre avant)
        x_ressort_debut = x_piston_symb + 0.05
        x_ressort_fin = 4.45
        pas_z = (x_ressort_fin - x_ressort_debut) / 6.0
        
        if pas_z > 0.02:
            x_z = [x_ressort_debut]
            y_z = [0.8]
            for i in range(1, 6):
                x_z.append(x_ressort_debut + i * pas_z)
                y_z.append(1.1 if i % 2 == 1 else 0.5)
            x_z.append(x_ressort_fin)
            y_z.append(0.8)
            ax_symb.plot(x_z, y_z, color="black", linewidth=1.5, linestyle="-")
            
        ax_symb.set_xlim(0, 8.5)
        ax_symb.set_ylim(-0.2, 1.5)
        ax_symb.axis("off")
        
        st.pyplot(fig_symb)
        plt.close(fig_symb)



            # --- MACHINE D'ÉTATS ET STABILISATION DU CHRONOMÈTRE REAL-TIME ---
        # Course maximale réelle du vérin = 250 mm
        longueur_sortie_mm = st.session_state.pos_vse_hyd * course_max_reelle_mm

        # --- MACHINE D'ÉTATS ET STABILISATION DU CHRONOMÈTRE REAL-TIME ---
        if st.session_state.vse_mouvement != "ARRET":
            st.session_state.temps_course_vse = time.time() - st.session_state.temps_debut_vse
            
            if st.session_state.vse_mouvement == "SORTIE":
                st.session_state.pos_vse_hyd = min(1.0, st.session_state.pos_vse_hyd + pas_course)
                if st.session_state.pos_vse_hyd >= 1.0:
                    st.session_state.vse_mouvement = "ARRET"
                    
            elif st.session_state.vse_mouvement == "RENTREE":
                st.session_state.pos_vse_hyd = max(0.0, st.session_state.pos_vse_hyd - (pas_course * 1.2))
                if st.session_state.pos_vse_hyd <= 0.0:
                    st.session_state.vse_mouvement = "ARRET"

            # Affichage simultané du temps, du pourcentage et des millimètres sortis
            c_met1, c_met2 = st.columns(2)
            with c_met1:
                st.metric(label="Chronomètre dynamique de course", value=f"{st.session_state.temps_course_vse:.2f} s", delta=f"Course : {st.session_state.pos_vse_hyd * 100:.0f} %")
            with c_met2:
                st.metric(label="Longueur de sortie de la tige", value=f"{longueur_sortie_mm:.1f} mm", delta="En déplacement")
            
            time.sleep(0.04)
            st.rerun()
        else:
            c_met1, c_met2 = st.columns(2)
            with c_met1:
                st.metric(label="Temps de course mesuré (Dernier essai)", value=f"{st.session_state.temps_course_vse:.2f} s", delta=f"Tige immobile à {st.session_state.pos_vse_hyd * 100:.0f} %")
            with c_met2:
                st.metric(label="Longueur de sortie de la tige", value=f"{longueur_sortie_mm:.1f} mm", delta="Position verrouillée", delta_color="off")






    with col_vse_bd:
        st.write("**La BD humoristique textuelle : La panne de muscles**")
        st.info(
            "**Case 1 :** Un mécanicien tente désespérément de soulever l'avant d'un camion de cinq tonnes à bout de bras "
            "pour changer un pneu, le visage tout rouge : 'Je vais y laisser mes vertèbres !'.\n\n"
            "**Case 2 :** Son collègue glisse un petit cric bouteille hydraulique sous le châssis : "
            "'Pousse-toi de là, laisse faire la pression mécanique !'. Il raccorde le flexible de la pompe.\n\n"
            "**Case 3 :** Le fluide ambré sous haute pression s'engouffre par l'unique orifice du vérin. "
            "Le piston reçoit la poussée et déploie sa tige métallique qui soulève le camion comme s'il s'agissait "
            "d'une plume de canard : 'Hisse !'.\n\n"
            "**Case 4 :** Une fois la bonne hauteur atteinte, le mécanicien verrouille la vanne. "
            "L'huile scellée à double tour reste rigide comme du roc. Le camion reste suspendu au millimètre près : "
            "'Génial, ce fluide incompressible ! Je peux travailler dessous en toute sécurité !'."
        )
        
    st.divider()

    # --- SECTION LOGIQUE : ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 3 ---
    if "suite_verrouille_tab3_hydro" not in st.session_state:
        st.session_state.suite_verrouille_tab3_hydro = False
    verrou_at3 = st.session_state.suite_verrouille_tab3_hydro

    # Affichage de l'Atelier d'évaluation 3
    afficher_atelier_verin_simple_effet_hydraulique(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier 3.",
        key="check_certif_hydro3_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_hydro_official", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_hydro_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_hydro_aleatoire:
                    saisie = st.session_state.get(f"hydro_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(saisie).strip() == str(q_item["rep"]).strip(): score_q3 += 1.0

            score_t3 = 0.0
            if "champs_hydro3_clean" in st.session_state:
                for ligne in st.session_state.champs_hydro3_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_hydro3_clean", "Choisir...") == attendu: score_t3 += 1.0

            st.session_state.score_suite3_hydro_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_hydro_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3_hydro = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3_hydro = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 3 ---
    if st.session_state.get("suite_verrouille_tab3_hydro", False):
        scr1_t3 = st.session_state.get("score_suite3_hydro_p1", 0.0)
        scr2_t3 = st.session_state.get("score_suite3_hydro_p2", 0.0)
        tot_s_t3 = st.session_state.get("score_final_suite3_hydro", 0.0)
        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d à %H:%M:%S")

        st.success(f"ATELIER VÉRIN SIMPLE EFFET SCELLÉ | Note de session : {tot_s_t3:.1f} / 20")

        html_export_hydro3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vérin Simple Effet - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation Hydraulique</h1>
                <p>Atelier 3 : Constitution, incompressibilité et blocage rigide du vérin simple effet</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0369a1;">
                Note obtenue au Quiz Technique : <strong>{scr1_t3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_t3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s_t3:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz (Ordre de session)
        if "ordre_quiz_tab3_hydro_delta" in st.session_state or "ordre_quiz_tab3_hydro_aleatoire" in st.session_state:
            cle_session_quiz = "ordre_quiz_tab3_hydro_aleatoire" if "ordre_quiz_tab3_hydro_aleatoire" in st.session_state else "ordre_quiz_tab3_hydro_delta"
            for num, q_item in enumerate(st.session_state[cle_session_quiz], 1):
                saisie = st.session_state.get(f"hydro_at3_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_hydro3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Clôture du premier tableau et transition vers la synthèse à trous
        html_export_hydro3 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DÉTAILLÉE DE LA SYNTHÈSE (TEXTE À TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours complétée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous de l'Atelier 3
        if "champs_hydro3_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_hydro3_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_hydro3_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                html_export_hydro3 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture définitive du document HTML de l'Atelier 3
        html_export_hydro3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_hydro3 = preparer_nom_fichier("Rapport_Verin_Simple_Effet_Hydraulique").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_hydro3,
            file_name=nom_fichier_html_hydro3,
            mime="text/html",
            use_container_width=True
        )








