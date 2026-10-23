
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application transmission d'informations ",
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
st.title("Application transmission d'informations")
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
    "Les ondes radio",
    "Le téléphone à la maison",
    "Les téléphones portables: smartphone",
    "La fibre optique",
    "Le réseau satellite",
    "Le WIFI",
    "Le bluetooth",
    "Les brouilleurs d'onde"
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

def afficher_atelier_historique_telecom(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 1 sur deux colonnes étanches."""
    import random

    questions_sources_h = [
        {"id": "t_hist_1", "q": "Qui est l'inventeur français du télégraphe optique déployé pendant la Révolution française ?", "options": ["Claude Chappe", "Samuel Morse", "Alexander Graham Bell"], "rep": "Claude Chappe"},
        {"id": "t_hist_2", "q": "Quelle était la contrainte majeure du système de sémaphore optique de Chappe ?", "options": ["Il était inutilisable la nuit, par temps de brouillard ou de forte pluie", "Il nécessitait des câbles en cuivre sous terre", "Il propageait des ondes radio nocives"], "rep": "Il était inutilisable la nuit, par temps de brouillard ou de forte pluie"},
        {"id": "t_hist_3", "q": "En quelle année Samuel Morse a-t-il réalisé la première démonstration publique de son télégraphe électrique ?", "options": ["1837", "1792", "1914"], "rep": "1837"},
        {"id": "t_hist_4", "q": "Quel composant physique a permis de s'affranchir de la visibilité directe entre les stations ?", "options": ["Le fil conducteur électrique en cuivre (puis de fer)", "La lentille de télescope à fort grossissement", "La bobine d'induction Tesla"], "rep": "Le fil conducteur électrique en cuivre (puis de fer)"},
        {"id": "t_hist_5", "q": "Comment le télégraphe de Morse transcrit-il les messages à distance ?", "options": ["Par l'émission d'impulsions électriques courtes et longues (points et traits)", "Par la projection d'ombres chinoises sur un écran blanc", "Par la voix convertie en vibrations magnétiques"], "rep": "Par l'émission d'impulsions électriques courtes et longues (points et traits)"},
        {"id": "t_hist_6", "q": "Quelle pièce mécanique le télégraphiste manipule-t-il manuellement pour envoyer le signal ?", "options": ["Le manipulateur (ou clé télégraphique)", "Le sémaphore de toiture", "Le cadran rotatif"], "rep": "Le manipulateur (ou clé télégraphique)"},
        {"id": "t_hist_7", "q": "Quel élément à l'arrivée traduit l'impulsion électrique en un clic mécanique audible ou un tracé d'encre ?", "options": ["L'électroaimant (récepteur)", "La pile Volta", "Le miroir parabolique"], "rep": "L'électroaimant (récepteur)"}
    ]

    if "ordre_quiz_tab1_telecom_aleatoire" not in st.session_state:
        random.shuffle(questions_sources_h)
        st.session_state.ordre_quiz_tab1_telecom_aleatoire = questions_sources_h

    st.session_state.champs_telecom1_clean = [
        ("1. Le télégraphe optique a été conçu par l'ingénieur français Claude ..........", ["Choisir...", "Chappe", "Morse"], "Chappe", "telecom1_t1"),
        ("2. Ce mécanisme transmettait des données par la position de bras ..........", ["Choisir...", "articulés", "électriques"], "articulés", "telecom1_t2"),
        ("3. Le système Chappe nécessitait une ligne de visée .......... entre les tours.", ["Choisir...", "directe", "enterrée"], "directe", "telecom1_t3"),
        ("4. Samuel Morse a remplacé les signaux visuels par des impulsions ..........", ["Choisir...", "électriques", "lumineuses"], "électriques", "telecom1_t4"),
        ("5. Le code Morse repose sur l'association de points et de ..........", ["Choisir...", "traits", "lettres"], "traits", "telecom1_t5"),
        ("6. L'opérateur utilise un .......... pour ouvrir et fermer le circuit.", ["Choisir...", "manipulateur", "clapet"], "manipulateur", "telecom1_t6"),
        ("7. À la réception, un .......... attire une armature pour créer le clic audible.", ["Choisir...", "électroaimant", "ressort"], "électroaimant", "telecom1_t7")
    ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique (7 questions - 10 pts)")
        if "ordre_quiz_tab1_telecom_aleatoire" in st.session_state:
            if "inc_local_tel1" not in st.session_state: st.session_state.inc_local_tel1 = 0
            st.session_state.inc_local_tel1 += 1
            
            for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_telecom_aleatoire, 1):
                st.write(f"**{idx}.** {q_data['q']}")
                cle_select = f"quiz_tel1_{q_data['id']}_inst_{st.session_state.inc_local_tel1}_{idx}"
                st.selectbox("", options=["Choisir..."] + q_data["options"], key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 pts)")
        if "champs_telecom1_clean" in st.session_state:
            for idx, ligne in enumerate(st.session_state.champs_telecom1_clean, 1):
                enonce = ligne[0]
                choix = ligne[1]
                cle = ligne[-1]
                c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
                with c_txt: st.write(enonce)
                with c_sel: st.selectbox("", choix, key=f"trous_tel1_{cle}_inst_{idx}", disabled=verrouille, label_visibility="collapsed")


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
    st.header("L'Origine des Télécommunications : Les Télégraphes")
    
    # --- DÉCLARATION DES VERROUS ET SÉCURITÉS ---
    if "suite_verrouille_tab1_telecom" not in st.session_state:
        st.session_state.suite_verrouille_tab1_telecom = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_telecom

    # --- PERSONNAGE CLÉ 1 : CLAUDE CHAPPE ---
    st.subheader("Claude Chappe et le Télégraphe Optique (1792)")
    st.write(
        "**Le Personnage :** En pleine Révolution française, l'ingénieur **Claude Chappe** réalise un coup de génie "
        "en créant le tout premier réseau de télécommunication d'envergure nationale [I1]. Face à la menace des invasions étrangères, "
        "la France avait un besoin vital de transmettre les ordres militaires plus vite que les chevaux des messagers.\n\n"
        "**Fonctionnement extrêmement détaillé :** Le système repose sur des **tours de sémaphores** distantes de 10 à 15 km [I1]. "
        "Au sommet de chaque tour est dressé un mât en bois équipé d'un grand bras pivotant horizontal appelé **Régulateur**, "
        "portant à ses extrémités deux petits bras articulés mobiles appelés **Indicateurs**. "
        "En manipulant un ingénieux système de poulies et de cordages depuis l'intérieur de la tour, l'opérateur pouvait configurer "
        "**92 positions géométriques distinctes**. Chaque configuration correspondait à un numéro de page et de ligne d'un dictionnaire secret, "
        "permettant de traduire les formes en mots complets. Les stationnaires des tours voisines observaient les signaux à l'aide de lunettes "
        "astronomiques et recopiaient immédiatement la position pour la transmettre à la tour suivante. C'est le premier réseau à transfert de paquets physiques !"
    )

    # --- SIMULATEUR INTERACTIF DU SÉMAPHORE DE CHAPPE ---
    st.write("**Laboratoire interactif : Positionnement des bras mécaniques Chappe**")
    angle_reg = st.slider("Orienter le bras Régulateur central (degrés) :", min_value=-90, max_value=90, value=0, step=45, key="slide_reg_chappe")
    angle_ind = st.slider("Orienter les Indicateurs d'extrémités (degrés) :", min_value=-90, max_value=90, value=45, step=45, key="slide_ind_chappe")

    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    import numpy as np
    import time

    fig_ch, ax_ch = plt.subplots(figsize=(6, 2.8), facecolor="white")
    ax_ch.set_facecolor("white")
    # Dessin de la tour en pierre
    ax_ch.add_patch(patches.Rectangle((2.2, 0.0), 0.6, 1.0, facecolor="#94a3b8", edgecolor="#475569", linewidth=2))
    ax_ch.plot([2.5, 2.5], [1.0, 1.8], color="black", linewidth=3) # Mât fixe
    
    # Calcul cinématique du bras régulateur central (longueur 1.2)
    rad_reg = np.radians(angle_reg)
    x1 = 2.5 - 0.6 * np.cos(rad_reg)
    y1 = 1.8 - 0.6 * np.sin(rad_reg)
    x2 = 2.5 + 0.6 * np.cos(rad_reg)
    y2 = 1.8 + 0.6 * np.sin(rad_reg)
    ax_ch.plot([x1, x2], [y1, y2], color="#b91c1c", linewidth=5, solid_capstyle="round", zorder=3) # Régulateur
    
    # Petits bras indicateurs aux extrémités (longueur 0.3)
    rad_ind = np.radians(angle_ind + angle_reg)
    ax_ch.plot([x1, x1 - 0.3 * np.sin(rad_ind)], [y1, y1 + 0.3 * np.cos(rad_ind)], color="#1e293b", linewidth=3, zorder=4)
    ax_ch.plot([x2, x2 + 0.3 * np.sin(rad_ind)], [y2, y2 - 0.3 * np.cos(rad_ind)], color="#1e293b", linewidth=3, zorder=4)
    
    ax_ch.set_xlim(1.0, 4.0)
    ax_ch.set_ylim(0.0, 2.6)
    ax_ch.axis("off")
    st.pyplot(fig_ch)
    plt.close(fig_ch)
    
    st.divider()

    # --- PERSONNAGE CLÉ 2 : SAMUEL MORSE ---
    st.subheader("Samuel Morse et le Télégraphe Électrique (1837)")
    st.write(
        "**Le Personnage :** L'artiste et inventeur américain **Samuel Morse**, frappé par le drame d'avoir appris la mort de sa femme "
        "plusieurs jours après son enterrement à cause de la lenteur du courrier, consacre sa vie à dompter l'électricité pour créer "
        "une communication instantanée [I2]. En s'associant avec Alfred Vail, il développe le code universel qui porte son nom.\n\n"
        "**Fonctionnement extrêmement détaillé :** Le télégraphe filaire révolutionne l'histoire en s'affranchissant totalement de la météo "
        "et de la visibilité directe. Le circuit comprend trois blocs indissociables :\n"
        "1. **La source d'énergie :** Une pile chimique (type Daniell) fournissant un courant électrique continu de basse tension.\n"
        "2. **L'émetteur (Le Manipulateur) :** Un interrupteur mécanique à levier inversé maintenu ouvert par un ressort. L'opérateur appuie "
        "sur le bouton en bois pour fermer le circuit et laisser passer le courant. Un appui bref génère un **point** (impulsion électrique de 0,1s), "
        "un appui long génère un **trait** (impulsion électrique de 0,3s).\n"
        "3. **Le récepteur (L'Électroaimant) :** À des centaines de kilomètres, le courant traverse une bobine de fil de cuivre enroulée autour "
        "d'un noyau de fer doux. Ce bobinage se transforme instantanément en aimant puissant (effet d'induction électromagnétique) et attire "
        "une palette métallique articulée. Cette palette vient frapper une butée dans un 'clic' sec audible, ou presse une pointe encrée contre "
        "une bande de papier déroulante, transcrivant physiquement l'alphabet Morse."
    )

    # --- SIMULATEUR DU SIGNAL ÉLECTRIQUE MORSE ---
    st.write("**Banc d'essai cinématique : Commutation du circuit Morse**")
    bouton_morse = st.radio("Manipulateur de ligne électrique :", options=["Circuit Ouvert (Pas de courant)", "Impulsion Courte (POINT .)", "Impulsion Longue (TRAIT -)"], index=0, horizontal=True)

    fig_mo, ax_mo = plt.subplots(figsize=(6, 1.8), facecolor="white")
    ax_mo.set_facecolor("white")
    
    # Tracé du fil de ligne reliant l'émetteur au récepteur
    color_ligne = "#ef4444" if "Impulsion" in bouton_morse else "#94a3b8"
    ax_mo.plot([1.0, 5.0], [0.8, 0.8], color=color_ligne, linewidth=3, label="Ligne de cuivre aérienne")
    
    # Dessin symbolique de la pile et du manipulateur
    ax_mo.add_patch(patches.Rectangle((0.6, 0.6), 0.3, 0.4, facecolor="#334155")) # Pile
    ax_mo.text(0.75, 1.1, "Pile Volta", ha="center", fontsize=8)
    
    # État du levier émetteur
    y_contact = 1.1 if "Pas" in bouton_morse else 0.8
    ax_mo.plot([1.0, 1.4], [0.8, y_contact], color="black", linewidth=4) # Levier interrupteur
    
    # Dessin de l'électroaimant récepteur à droite
    ax_mo.add_patch(patches.Rectangle((5.0, 0.5), 0.5, 0.6, facecolor="#475569")) # Bobine
    ax_mo.text(5.25, 1.2, "Électroaimant", ha="center", fontsize=8)
    
    # Palette de script d'arrivée
    y_palette = 0.5 if "Pas" in bouton_morse else 0.62
    ax_mo.plot([5.6, 6.0], [y_palette, y_palette], color="black", linewidth=4) # Palette réceptrice
    
    ax_mo.set_xlim(0, 6.5)
    ax_mo.set_ylim(0, 1.5)
    ax_mo.axis("off")
    st.pyplot(fig_mo)
    plt.close(fig_mo)
    
    if "POINT" in bouton_morse: st.success("Signal en ligne : Courant émis pendant 40ms -> . (Lettre E)")
    elif "TRAIT" in bouton_morse: st.error("Signal en ligne : Courant émis pendant 120ms -> - (Lettre T)")
    else: st.info("Ligne au repos : Tension nulle, pas d'électromagnétisme.")

    st.divider()

    # --- CARICATURE / BD HUMORISTIQUE TEXTUELLE ---
    st.write("**La BD humoristique textuelle : Le jour où la météo s'en est mêlée**")
    st.info(
        "**Case 1 (Caricature de Claude Chappe) :** Claude Chappe est debout au sommet de sa tour, sa longue vue "
        "coincée sous le bras, agitant ses cordages avec ferveur : 'Vite ! Envoyons le message secret à Napoléon !'. "
        "Les bras en bois tournent joyeusement : 'Schliiiit !'.\n\n"
        "**Case 2 (Le Drame) :** Un énorme nuage noir et farceur crève juste au-dessus de la colline. "
        "Une pluie torrentielle et un brouillard à couper au couteau enveloppent la station suivante. "
        "Le stationnaire voisin, les yeux collés à sa longue vue pleine d'eau, râle : 'Je ne vois même pas le mât ! "
        "Le message est noyé !'.\n\n"
        "**Case 3 (Caricature de Samuel Morse) :** Samuel Morse arrive avec un grand sourire en coin, un rouleau de fil de cuivre "
        "sous le bras et sa pile chimique à la main : 'Laissez tomber vos télescopes les gars ! Mon fluide magique passe "
        "à travers la tempête sans mouiller son chapeau !'.\n\n"
        "**Case 4 (La Victoire) :** L'opérateur Morse tape frénétiquement sur son manipulateur : 'Clic-clac-clic !'. "
        "À 500 kilomètres de là, sous un orage terrible, l'électroaimant récepteur tape joyeusement sur sa bande de papier "
        "au sec : 'Message reçu instantanément ! Fin de la préhistoire des télécoms !'."
    )

    st.divider()

    # --- ZONE DES EXERCICES ET SCELLÉ DE L'ATELIER 1 ---
    afficher_atelier_historique_telecom(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    case_certif_tel1 = st.checkbox("Je certifie avoir complété les questions de l'Atelier 1.", key="check_certif_tel1_final", disabled=verrou_at1)

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_tel1_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_tel1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Note du Quiz
            score_q1 = 0.0
            if "ordre_quiz_tab1_telecom_aleatoire" in st.session_state:
                for idx, q_item in enumerate(st.session_state.ordre_quiz_tab1_telecom_aleatoire, 1):
                    inc = st.session_state.get("inc_local_tel1", 1)









































                    
