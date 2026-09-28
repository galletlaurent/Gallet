# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application dosage du vinaigre",
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

# =============================================================================
# RENDU DU TITRE DE L'APPLICATION ET CRÉDITS (Lignes uniques sans coupure)
# =============================================================================
st.title("Application dosage du vinaigre")
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

# Variables d'état expérimentales et modes examen
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1

if "indicateurs" not in st.session_state:
    st.session_state.indicateurs = {
        "Bleu de Bromothymol (BBT)": { "ph_min": 6.0, "ph_max": 7.6,  "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#4CAF50", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Hélianthine": { "ph_min": 3.1, "ph_max": 4.4,  "couleur_acide": "#E91E63", "nom_acide": "Rouge", "couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFC107", "nom_base": "Jaune" },
        "Phénolphtaléine": { "ph_min": 8.2, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F8BBD0", "nom_zone": "Rose pâle",  "couleur_base": "#E91E63", "nom_base": "Rose fuchsia" },
        "Bleu de Thymol": { "ph_min": 1.2, "ph_max": 2.8,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FFEB3B", "nom_zone": "Jaune", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Hélianthine / Orange de méthyle": {"ph_min": 3.2, "ph_max": 4.4,  "couleur_acide": "#F44336", "nom_acide": "Rouge", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Vert de Bromocrésol": { "ph_min": 3.8, "ph_max": 5.4, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#8BC34A", "nom_zone": "Vert", "couleur_base": "#2196F3", "nom_base": "Bleu" },
        "Rouge de Méthyle": { "ph_min": 4.2, "ph_max": 6.2, "couleur_acide": "#F44336", "nom_acide": "Rouge","couleur_zone": "#FF5722", "nom_zone": "Orange", "couleur_base": "#FFEB3B", "nom_base": "Jaune" },
        "Bleu de Bromophténol": { "ph_min": 3.0, "ph_max": 4.6, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#00BCD4", "nom_zone": "Vert-Bleu", "couleur_base": "#3F51B5", "nom_base": "Bleu violet" },
        "Phénolphtaléine (Zone large)": { "ph_min": 8.0, "ph_max": 10.0, "couleur_acide": "#E0F7FA", "nom_acide": "Incolore", "couleur_zone": "#F48FB1", "nom_zone": "Rose", "couleur_base": "#C2185B", "nom_base": "Rose soutenu" },
        "Jaune d'Alizarin R": {"ph_min": 10.1, "ph_max": 12.0, "couleur_acide": "#FFEB3B", "nom_acide": "Jaune", "couleur_zone": "#FF9800", "nom_zone": "Orange", "couleur_base": "#F44336", "nom_base": "Rouge" }
    }

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
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]





def afficher_questions_vinaigre1_dynamiques(verrouille=False):
    import streamlit as st
    import random
    
    if "vin_verrouille_tab1" not in st.session_state:
        return {}, {}

    # Initialisation et melange unique obligatoire de vos 7 questions d'origine + 3 completes
    if "ordre_quiz1" not in st.session_state:
        base_quiz1 = [
            {"id": "q1_1", "q": "La molecule du vinaigre est :", "type": "menu", "options": ["acide", "neutre", "basique"], "rep": "acide"},
            {"id": "q1_2", "q": "Calculer la masse molaire moleculaire du vinaigre en g/mol: ", "type": "menu", "options": ["60", "46", "18"], "rep": "60"},
            {"id": "q1_3", "q": "Quel est le nom chimique de la molecule du vinaigre ?", "type": "menu", "options": ["acide acetique", "acide methanoique", "acide chlorhydrique"], "rep": "acide acetique"},
            {"id": "q1_4", "q": "Quel est le nombre d'atome de carbone que possede la molecule de vinaigre ?", "type": "menu", "options": ["2", "1", "4"], "rep": "2"},
            {"id": "q1_5", "q": "Quel est le nombre d'atome d'hydrohene que possede la molecule de vinaigre ?", "type": "menu", "options": ["4", "2", "6"], "rep": "4"},
            {"id": "q1_6", "q": "Quel est le nombre d'atome d''oxygene que possede la molecule de vinaigre ?", "type": "menu", "options": ["2", "1", "3"], "rep": "2"},
            {"id": "q1_7", "q": "Quelle est la formule brute de vinaigre ?", "type": "menu", "options": ["C4H2O2", "C2H4O2", "C2H2O4", "C2H2O2"], "rep": "C2H4O2"},
            {"id": "q1_8", "q": "D'apres la legende atomique, quelle est la masse molaire de l'element Carbone (C) ?", "type": "menu", "options": ["12 g/mol", "1 g/mol", "16 g/mol"], "rep": "12 g/mol"},
            {"id": "q1_9", "q": "D'apres la legende atomique, quelle est la masse molaire de l'element Oxygene (O) ?", "type": "menu", "options": ["16 g/mol", "12 g/mol", "1 g/mol"], "rep": "16 g/mol"},
            {"id": "q1_10", "q": "D'apres la legende atomique, la sphere blanche represente l'atome d' :", "type": "menu", "options": ["Hydrogene (H)", "Carbone (C)", "Oxygene (O)"], "rep": "Hydrogene (H)"}
        ]
        # Sauvegarde du melange obligatoire en session
        copie_base = list(base_quiz1)
        random.shuffle(copie_base)
        st.session_state.ordre_quiz1 = copie_base

    col_double_quiz_v1, col_double_trous_v1 = st.columns(2)

    # --- COLONNE DE GAUCHE : L'ORDRE DES 10 QUESTIONS ME LANGÉES ---
    with col_double_quiz_v1:
        st.markdown("##### Quiz de nomenclature moleculaire (10 questions - 10 pts)")
        dict_reponses_quiz = {}
        
        for idx, q_data in enumerate(st.session_state.ordre_quiz1, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"vin_cl_g_{q_data['id']}"
            
            # Melange local des options pour eviter l'ordre fixe des propositions
            cle_shuff_opts = f"opts_shuff_{q_data['id']}"
            if cle_shuff_opts not in st.session_state:
                opts_copie = list(q_data["options"])
                random.shuffle(opts_copie)
                st.session_state[cle_shuff_opts] = ["Choisir..."] + opts_copie
                
            val_p = st.session_state.get(cle_select, "Choisir...")
            sel_idx = st.session_state[cle_shuff_opts].index(val_p) if val_p in st.session_state[cle_shuff_opts] else 0
            
            dict_reponses_quiz[q_data["id"]] = st.selectbox(
                "", st.session_state[cle_shuff_opts], 
                index=sel_idx, key=cle_select, 
                disabled=verrouille, label_visibility="collapsed"
            )

    # --- COLONNE DE DROITE : LES 10 TROUS DE SYNTHÈSE ASSOCIES ---
    with col_double_trous_v1:
        st.markdown("##### Synthese des proprietes acido-basiques (10 trous - 10 pts)")
        dict_trous = {}
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le vinaigre commercial est une solution aqueuse d'acide")
        with c2: dict_trous["t1"] = st.selectbox("", ["Choisir...", "Ethanoique", "Methanoique"], key="vin_t1_s1", disabled=verrouille, label_visibility="collapsed")
        
        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. Le groupe fonctionnel de cet acide organique est le groupe")
        with c4: dict_trous["t2"] = st.selectbox("", ["Choisir...", "Carboxyle", "Hydroxyle"], key="vin_t2_s1", disabled=verrouille, label_visibility="collapsed")
        
        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. L'acide acetique appartient a la categorie des acides")
        with c6: dict_trous["t3"] = st.selectbox("", ["Choisir...", "Faibles", "Forts"], key="vin_t3_s1", disabled=verrouille, label_visibility="collapsed")
        
        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. Sa reaction de neutralisation lors d'un titrage est")
        with c8: dict_trous["t4"] = st.selectbox("", ["Choisir...", "Totale", "Limitee"], key="vin_t4_s1", disabled=verrouille, label_visibility="collapsed")
        
        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le pKa du couple de l'acide acetique a 25°C vaut")
        with c10: dict_trous["t5"] = st.selectbox("", ["Choisir...", "4.8", "7.0", "9.2"], key="vin_t5_s1", disabled=verrouille, label_visibility="collapsed")
        
        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. L'espece chimique titrante employee dans la burette est la")
        with c12: dict_trous["t6"] = st.selectbox("", ["Choisir...", "Soude", "Acide"], key="vin_t6_s1", disabled=verrouille, label_visibility="collapsed")
        
        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. Les ions sodium Na+ presents sont des ions qualifies de")
        with c14: dict_trous["t7"] = st.selectbox("", ["Choisir...", "Spectateurs", "Actifs"], key="vin_t7_s1", disabled=verrouille, label_visibility="collapsed")
        
        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'unite internationale de la concentration molaire est")
        with c16: dict_trous["t8"] = st.selectbox("", ["Choisir...", "mol/L", "g/mol", "g/L"], key="vin_t8_s1", disabled=verrouille, label_visibility="collapsed")
        
        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le virage de couleur de l'indicateur signale l'")
        with c18: dict_trous["t9"] = st.selectbox("", ["Choisir...", "Equivalence", "Dissociation"], key="vin_t9_s1", disabled=verrouille, label_visibility="collapsed")
        
        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Diluer une solution acide fait tendre sa valeur de pH vers")
        with c20: dict_trous["t10"] = st.selectbox("", ["Choisir...", "7.0", "0.0", "14.0"], key="vin_t10_s1", disabled=verrouille, label_visibility="collapsed")

    return dict_reponses_quiz, dict_trous



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
            key="btn_validation_identite_maitre",
            disabled=st.session_state.get("verrouille", False)
        ):
            # Appel de votre fonction globale de validation créée à l'étape précédente
            valider_saisie()
            
            # Rechargement propre pour appliquer instantanément le verrouillage visuel des champs
            if st.session_state.get("verrouille", False):
                st.rerun()


with tab1:
    st.header("Atelier 1 : Generalites sur le vinaigre")
    
    if "vin_verrouille_tab1" not in st.session_state: 
        st.session_state.vin_verrouille_tab1 = False

    # Architecture en deux colonnes de l'Atelier conforme a hier
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'etude")
        
        texte_document = (
            "Le vinaigre est une solution aqueuse composee majoritairement d'acide acetique. "
            "C'est un produit naturel et biodegradable issu de la biotransformation de l'alcool ethylique "
            "present dans les vins ou les cidres. La denomination vinaigre est reservee au produit obtenu "
            "exclusivement par le procede biologique de la double fermentation, alcoolique et acetique, "
            "de denrees et boissons d'origine agricole ou de leurs dilutions aqueuses (Decret n°88-1207 du 30 decembre 1988). "
            "Le degre d’acidite d’un vinaigre, indique sur la bouteille, represente l’acidite totale rapportee "
            "a la masse d’acide acetique exprimee en grammes pour 100 grammes de vinaigre."
        )
        st.info(texte_document)
        
        # Rendu graphique de la bouteille 2D via Matplotlib
        fig_bouteille, ax = plt.subplots(figsize=(4, 5.2), facecolor="#bae6fd")
        ax.set_facecolor("#bae6fd")
        
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#d0d8dc", ec="#b0bec5")
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7], [3.5, 7]], color="white", ec="#b0bec5")
        corps = patches.Rectangle((2.5, 1), 5, 6, color="white", ec="#b0bec5")
        etiquette = patches.Rectangle((2.7, 1.5), 4.6, 4, color="#008040")
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#0033cc")
        
        ax.add_patch(patches.Circle((5, 1), 2.5, color="white", ec="white"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#e2e8f0", linewidth=1)
            
        ax.text(5, 5.0, "VINAIGRE", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.5, "D'ALCOOL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "CRISTAL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 3.0, "Eco", color="white", weight="bold", fontsize=12, ha="center")
        ax.text(5, 2.5, "+", color="#ffcc00", weight="bold", fontsize=14, ha="center")
        ax.text(3.3, 2.0, "8°", color="white", weight="bold", fontsize=11, ha="center")
        ax.text(6.7, 2.0, "1 L", color="white", weight="bold", fontsize=11, ha="center")
        
        ax.set_xlim(1, 9)
        ax.set_ylim(0, 10)
        ax.axis("off")
        st.pyplot(fig_bouteille)

    # --------------------------------------------------------
    # COLONNE DROITE : LES DONNÉES ATOMIQUES ET LA MOLÉCULE
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Donnees et Legendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1: st.caption("**Hydrogene (H)**\n\nSphere blanche\nM(H) = 1 g/mol")
        with col_leg2: st.caption("**Carbone (C)**\n\nSphere noire\nM(C) = 12 g/mol")
        with col_leg3: st.caption("**Oxygene (O)**\n\nSphere rouge\nM(O) = 16 g/mol")
            
        st.divider()

        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        c_methyl = np.array([2.8, 2.5])
        c_carboxy = np.array([4.2, 2.5])
        double_o = np.array([4.6, 3.4])
        oh_o = np.array([5.1, 1.9])
        oh_h = np.array([5.9, 1.7])
        h1_m = np.array([2.3, 3.5])
        h2_m = np.array([2.3, 1.5])
        h3_m = np.array([3.2, 3.6])

        def tracer_liaison(p1, p2, double=False):
            if double:
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        tracer_liaison(c_methyl, c_carboxy)
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_o)
        tracer_liaison(oh_o, oh_h)

        def tracer_atome(p, symbole):
            if symbole == 'C': couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O': couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H': couleur, texte_couleur = "#ecf0f1", "black"
            else: couleur, texte_couleur = "#95a5a6", "black"
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        tracer_atome(c_methyl, 'C')
        tracer_atome(c_carboxy, 'C')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_o, 'O')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')
        tracer_atome(oh_h, 'H')

        ax_mol.set_xlim(1.5, 6.5)
        ax_mol.set_ylim(1.0, 4.2)
        ax_mol.axis("off")
        st.pyplot(fig_mol)
        st.divider()

    # =========================================================================
    # LOGIQUE DE COUPLAGE DES CONFIGURATIONS DE NOTATION DYNAMIQUES
    # =========================================================================
    res_q1, res_t1 = afficher_questions_vinaigre1_dynamiques(
        verrouille=st.session_state.vin_verrouille_tab1
    )

    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_vin1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 1.", 
        key="check_certif_vin1", 
        disabled=st.session_state.vin_verrouille_tab1
    )

    if st.button("VALIDER AND EXPORTER LE BILAN DE L'ATELIER 1", key="btn_validation_vin1", use_container_width=True, disabled=st.session_state.vin_verrouille_tab1):
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_vin1:
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if st.session_state.get("vin_q1_s1") == "Acide ethanoique": score_q1 += 1.0
            if st.session_state.get("vin_q2_s1") == "CH3COOH": score_q1 += 1.0
            if st.session_state.get("vin_q3_s1") == "CH3COO-": score_q1 += 1.0
            if st.session_state.get("vin_q4_s1") == "60 g/mol": score_q1 += 1.0
            if st.session_state.get("vin_q5_s1") == "Ceder un ou plusieurs protons H+": score_q1 += 1.0
            if st.session_state.get("vin_q6_s1") == "Totale et rapide": score_q1 += 1.0
            if st.session_state.get("vin_q7_s1") == "Entre 2 et 3": score_q1 += 1.0
            if st.session_state.get("vin_q8_s1") == "La masse en grammes d'acide pur dans 100g de vinaigre": score_q1 += 1.0
            if st.session_state.get("vin_q9_s1") == "Blouse, lunettes de protection et gants": score_q1 += 1.0
            if st.session_state.get("vin_q10_s1") == "Une pipette jaugee": score_q1 += 1.0

            score_t1 = 0.0
            if st.session_state.get("vin_t1_s1") == "Ethanoique": score_t1 += 1.0
            if st.session_state.get("vin_t2_s1") == "Carboxyle": score_t1 += 1.0
            if st.session_state.get("vin_t3_s1") == "Faibles": score_t1 += 1.0
            if st.session_state.get("vin_t4_s1") == "Totale": score_t1 += 1.0
            if st.session_state.get("vin_t5_s1") == "4.8": score_t1 += 1.0
            if st.session_state.get("vin_t6_s1") == "Soude": score_t1 += 1.0
            if st.session_state.get("vin_t7_s1") == "Reaction": score_t1 += 1.0
            if st.session_state.get("vin_t8_s1") == "mol/L": score_t1 += 1.0
            if st.session_state.get("vin_t9_s1") == "Equivalence": score_t1 += 1.0
            if st.session_state.get("vin_t10_s1") == "Augmente": score_t1 += 1.0

            st.session_state.score_vin1_p1 = round(score_q1, 1)
            st.session_state.score_vin1_p2 = round(score_t1, 1)
            st.session_state.score_final_vin1 = round(score_q1 + score_t1, 1)
            st.session_state.vin_verrouille_tab1 = True
            
            st.rerun()

    if st.session_state.get("vin_verrouille_tab1", False):
        scr1 = st.session_state.get("score_vin1_p1", 0.0)
        scr2 = st.session_state.get("score_vin1_p2", 0.0)
        tot_s = st.session_state.get("score_final_vin1", 0.0)

        from datetime import datetime, timedelta
        timestamp_vin1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER VINAIGRE 1 SCELLE | Note de session : {tot_s} / 20")

        html_export_vin1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Vinaigre 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #047857; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <p>Atelier : Generalites sur le vinaigre</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_vin1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Nomenclature et Proprietes</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #047857;">
                &bull; Partie 1 : Quiz de validation nomenclature (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours acido-basique (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ THEORIQUE MOLECULAIRE</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Question Posee</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 20%; text-align: center;">Attendu Academique</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Generation dynamique des en-tetes de questions issus de votre dictionnaire ordonne de session
        for idx, q_data in enumerate(st.session_state.ordre_quiz1, 1):
            saisie = st.session_state.get(f"vin_cl_g_{q_data['id']}", "Choisir...")
            attendu = q_data["rep"]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin1 += f"""<tr>
                <td>{idx}</td>
                <td>{q_data['q']}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{attendu}</td>
                <td class='{v_class}' style='text-align:center;'>{v_lbl}</td>
            </tr>"""

        html_export_vin1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 5%;">N°</th>
                        <th style="width: 45%;">Phrase a trous completee</th>
                        <th style="width: 15%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 20%; text-align: center;">Attendu Academique</th>
                        <th style="width: 15%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        # En-têtes textuels des phrases à trous correspondantes pour l'affichage integral dans le tableau
        phrases_trous1 = [
            ("1. Le vinaigre commercial est une solution aqueuse d'acide...", "Ethanoique"),
            ("2. Le groupe fonctionnel de cet acide organique est le groupe...", "Carboxyle"),
            ("3. L'acide acetique appartient a la categorie des acides...", "Faibles"),
            ("4. Sa reaction de neutralisation lors d'un titrage est...", "Totale"),
            ("5. Le pKa du couple de l'acide acetique a 25°C vaut...", "4.8"),
            ("6. L'espece chimique titrante employee dans la burette est la...", "Soude"),
            ("7. Les ions sodium Na+ presents sont des ions qualifies de...", "Spectateurs"),
            ("8. L'unite internationale de la concentration molaire est...", "mol/L"),
            ("9. Le virage de couleur de l'indicateur signale l'...", "Equivalence"),
            ("10. Diluer une solution acide fait tendre sa valeur de pH vers...", "7.0")
        ]

        for i, (phrase, tv) in enumerate(phrases_trous1, 1):
            saisie = st.session_state.get(f"vin_t{i}_s1", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_vin1 += f"""<tr>
                <td>{i}</td>
                <td>{phrase}</td>
                <td style='text-align:center;'>{saisie}</td>
                <td style='text-align:center;'>{tv}</td>
                <td class='{v_class}' style='text-align:center;'>{v_lbl}</td>
            </tr>"""

        html_export_vin1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse chimique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f1 = f"Rapport_Evaluation_Vinaigre1_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f1 = nom_f1.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_vin1,
            file_name=f"{nom_f1}.html",
            mime="text/html",
            use_container_width=True
        )







