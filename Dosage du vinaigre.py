# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime
import random
import math

# --- CONFIGURATION INITIALE DE LA PAGE ---
st.set_page_config(
    page_title="TP vinaigre",
    layout="wide"
)

# --- INITIALISATION DE L'ÉTAT DE L'APPLICATION (SESSION STATE) ---
if "nom" not in st.session_state: st.session_state.nom = ""
if "prenom" not in st.session_state: st.session_state.prenom = ""
if "classe" not in st.session_state: st.session_state.classe = ""
if "heure" not in st.session_state: st.session_state.heure = datetime.now().strftime("%d/%m/%Y %H:%M")
if "ph_eq" not in st.session_state: st.session_state.ph_eq = 7.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.1


# Données métiers issues de votre dictionnaire Tkinter
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

# Variables d'état expérimentales et modes examen
if "points_ve_ph" not in st.session_state: st.session_state.points_ve_ph = []
if "ph_actuel" not in st.session_state: st.session_state.ph_actuel = 7.0
if "ph_eq_reel" not in st.session_state: st.session_state.ph_eq_reel = 7.0
if "c_titrant" not in st.session_state: st.session_state.c_titrant = 0.0
if "c_titre" not in st.session_state: st.session_state.c_titre = 0.0
if "v_eq" not in st.session_state: st.session_state.v_eq = 0.0

if "mode_examen_tab1" not in st.session_state: st.session_state.mode_examen_tab1 = False
if "mode_examen_tab2" not in st.session_state: st.session_state.mode_examen_tab2 = False
if "mode_examen_tab31" not in st.session_state: st.session_state.mode_examen_tab31 = False
if "mode_examen_tab32" not in st.session_state: st.session_state.mode_examen_tab32 = False

# --- 1. EN-TÊTE FIXE (Haut de la page) ---
st.markdown("### TP vinaigre")

header_cols = st.columns([2, 2, 1, 2])
with header_cols[0]:
    nom_affiche = st.session_state.nom if st.session_state.nom else "Non renseigné"
    prenom_affiche = st.session_state.prenom if st.session_state.prenom else "Non renseigné"
    st.markdown(f"**Nom et Prénom :** {nom_affiche} {prenom_affiche}")
with header_cols[1]:
    classe_affiche = st.session_state.classe if st.session_state.classe else "Non renseignée"
    st.markdown(f"**Classe :** {classe_affiche}")
with header_cols[2]:
    st.markdown("**Date et heure :**")
with header_cols[3]:
    st.markdown(f"{st.session_state.heure}")

st.divider()

# --- REGROUPEMENT DU CONTROLE EXAMEN DANS LA BARRE LATERALE ---
with st.sidebar:
    st.markdown("### CONTROLE EXAMEN")
    
    st.session_state.mode_examen_tab1 = st.checkbox(
        "Activer le Mode Examen (Onglet 1)", 
        value=st.session_state.mode_examen_tab1,
        disabled=st.session_state.get("examen_verrouille_tab1", False),
        key="checkbox_examen_tab1"
    )
    
    st.session_state.mode_examen_tab2 = st.checkbox(
        "Activer le Mode Examen (Atelier 2)", 
        value=st.session_state.mode_examen_tab2,
        disabled=st.session_state.get("examen_verrouille_tab2", False),
        key="checkbox_examen_tab2"
    )
    
    st.session_state.mode_examen_tab31 = st.checkbox(
        "Activer le Mode Examen GAUCHE",
        value=st.session_state.mode_examen_tab31,
        disabled=st.session_state.get("examen_verrouille_tab31", False),
        key="chk_exam_31"
    )
    
    st.session_state.mode_examen_tab32 = st.checkbox(
        "Activer le Mode Examen DROIT",
        value=st.session_state.mode_examen_tab32,
        disabled=st.session_state.get("examen_verrouille_tab32", False),
        key="chk_exam_32"
    )

# --- 2. CRÉATION DES ONGLETS (NOTEBOOK CONTROLLER) ---
tab0, tab1, tab2, tab3 = st.tabs([
    "Identification",
    "Généralités sur le vinaigre",
    "Dosage colorimétrique du vinaigre",
    "Calcul théorique sur le vinaigre et vérification de l'inscription sur la bouteille"
])
# ==========================================
# ONGLET 0 : IDENTIFICATION DE L'ÉLÈVE
# ==========================================
with tab0:
    st.subheader("Identification de l'élève")
    
    if "verrouille" not in st.session_state:
        st.session_state.verrouille = False

    with st.container(border=True):
        st.markdown("**Formulaire des Travaux Pratiques**")
        
        nom_saisi = st.text_input("Nom :", value=st.session_state.nom, disabled=st.session_state.verrouille)
        prenom_saisi = st.text_input("Prénom :", value=st.session_state.prenom, disabled=st.session_state.verrouille)
        classe_saisi = st.text_input("Groupe / Classe :", value=st.session_state.classe, disabled=st.session_state.verrouille)
        
        if not st.session_state.verrouille:
            if st.button("Valider mes informations", type="primary"):
                if not nom_saisi.strip() or not prenom_saisi.strip() or not classe_saisi.strip():
                    st.error("Veuillez compléter entièrement vos données avant de valider.")
                else:
                    st.session_state.nom = nom_saisi.strip()
                    st.session_state.prenom = prenom_saisi.strip()
                    st.session_state.classe = classe_saisi.strip()
                    st.session_state.verrouille = True
                    st.success(f"Validation effectuée. Le formulaire est maintenant verrouillé.")
                    st.rerun()
        else:
            st.info("Les informations de session sont enregistrées et verrouillées.")
            if st.button("Modifier les informations"):
                st.session_state.verrouille = False
                st.rerun()
# ==========================================
# ONGLET 1 : GÉNÉRALITÉS SUR LE VINAIGRE
# ==========================================
with tab1:
    st.header("Generalites sur le vinaigre")
    
    # --- MISE EN PAGE : DEUX COLONNES (GAUCHE / DROITE) ---
    col_gauche, col_droite = st.columns([1, 1])
    
    # --------------------------------------------------------
    # COLONNE GAUCHE : LE DOCUMENT ET LA BOUTEILLE GRAPHIQUE
    # --------------------------------------------------------
    with col_gauche:
        st.subheader("Document d'etude")
        
        # Texte du document
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
        
        # Generation de la bouteille 2D via Matplotlib (Remplaçant du Canvas Tkinter)
        fig_bouteille, ax = plt.subplots(figsize=(4, 6), facecolor="#bae6fd")
        ax.set_facecolor("#bae6fd")
        
        # 1. Corps et col de la bouteille
        bouchon = patches.Rectangle((4, 8.5), 2, 0.8, color="#d0d8dc", ec="#b0bec5")
        col = patches.Polygon([[4.2, 8.5], [5.8, 8.5], [6.5, 7], [3.5, 7]], color="white", ec="#b0bec5")
        corps = patches.Rectangle((2.5, 1), 5, 6, color="white", ec="#b0bec5")
        
        # 2. Etiquette verte
        etiquette = patches.Rectangle((2.7, 1.5), 4.6, 4, color="#008040")
        
        # 3. Logo Eco+
        logo_fond = patches.Rectangle((4.2, 2.2), 1.6, 1.2, color="#0033cc")
        
        # Ajout des formes au graphique
        ax.add_patch(bouteille_fond := patches.Circle((5, 1), 2.5, color="white", ec="white"))
        ax.add_patch(corps)
        ax.add_patch(col)
        ax.add_patch(bouchon)
        ax.add_patch(etiquette)
        ax.add_patch(logo_fond)
        
        # Rainures de la bouteille
        for y in np.linspace(1.2, 6.8, 8):
            ax.plot([2.55, 7.45], [y, y], color="#e2e8f0", linewidth=1)
            
        # Textes sur l'etiquette
        ax.text(5, 5.0, "VINAIGRE", color="white", weight="bold", fontsize=14, ha="center")
        ax.text(5, 4.5, "D'ALCOOL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 4.1, "CRISTAL", color="white", weight="bold", fontsize=10, ha="center")
        ax.text(5, 3.0, "Eco", color="white", weight="bold", fontsize=12, ha="center")
        ax.text(5, 2.5, "+", color="#ffcc00", weight="bold", fontsize=14, ha="center")
        ax.text(3.3, 2.0, "8°", color="white", weight="bold", fontsize=11, ha="center")
        ax.text(6.7, 2.0, "1 L", color="white", weight="bold", fontsize=11, ha="center")
        
        # Configurations d'affichage de la bouteille
        ax.set_xlim(1, 9)
        ax.set_ylim(0, 10)
        ax.axis("off")
        
        st.pyplot(fig_bouteille)

    # --------------------------------------------------------
    # COLONNE DROITE : LES DONNÉES ATOMIQUES ET LE QUIZ 1
    # --------------------------------------------------------
    with col_droite:
        st.subheader("Donnees et Legendes Atomiques")
        
        col_leg1, col_leg2, col_leg3 = st.columns(3)
        with col_leg1:
            st.caption("**Hydrogene (H)**\n\nSphere blanche\nM(H) = 1 g/mol")
        with col_leg2:
            st.caption("**Carbone (C)**\n\nSphere noire\nM(C) = 12 g/mol")
        with col_leg3:
            st.caption("**Oxygene (O)**\n\nSphere rouge\nM(O) = 16 g/mol")
            
        st.divider()

        
        fig_mol, ax_mol = plt.subplots(figsize=(6, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # Coordonnees des atomes (ramenees a une echelle standard Matplotlib)
        c_methyl = np.array([2.8, 2.5])
        c_carboxy = np.array([4.2, 2.5])
        double_o = np.array([4.6, 3.4])
        oh_o = np.array([5.1, 1.9])
        oh_h = np.array([5.9, 1.7])
        
        h1_m = np.array([2.3, 3.5])
        h2_m = np.array([2.3, 1.5])
        h3_m = np.array([3.2, 3.6])

        # Fonction imbriquee pour tracer les liaisons
        def tracer_liaison(p1, p2, double=False):
            if double:
                # Calcul du vecteur normal pour decaler les deux barres de la double liaison
                v = p2 - p1
                n = np.array([-v[1], v[0]])
                n = (n / np.linalg.norm(n)) * 0.06
                ax_mol.plot([p1[0] + n[0], p2[0] + n[0]], [p1[1] + n[1], p2[1] + n[1]], color="#333333", linewidth=3, zorder=1)
                ax_mol.plot([p1[0] - n[0], p2[0] - n[0]], [p1[1] - n[1], p2[1] - n[1]], color="#333333", linewidth=3, zorder=1)
            else:
                ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Traces des liaisons
        tracer_liaison(c_methyl, c_carboxy)
        tracer_liaison(c_methyl, h1_m)
        tracer_liaison(c_methyl, h2_m)
        tracer_liaison(c_methyl, h3_m)
        tracer_liaison(c_carboxy, double_o, double=True)
        tracer_liaison(c_carboxy, oh_o)
        tracer_liaison(oh_o, oh_h)

        # Fonction imbriquee pour tracer les atomes
        def tracer_atome(p, symbole):
            if symbole == 'C':
                couleur, texte_couleur = "#2b3e50", "white"
            elif symbole == 'O':
                couleur, texte_couleur = "#e74c3c", "white"
            elif symbole == 'H':
                couleur, texte_couleur = "#ecf0f1", "black"
            else:
                couleur, texte_couleur = "#95a5a6", "black"
                
            cercle = patches.Circle((p[0], p[1]), 0.22, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2)
            ax_mol.add_patch(cercle)
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=10, ha="center", va="center", zorder=3)

        # Affichage des atomes par-dessus les liaisons
        tracer_atome(c_methyl, 'C')
        tracer_atome(c_carboxy, 'C')
        tracer_atome(double_o, 'O')
        tracer_atome(oh_o, 'O')
        tracer_atome(h1_m, 'H')
        tracer_atome(h2_m, 'H')
        tracer_atome(h3_m, 'H')
        tracer_atome(oh_h, 'H')

        # Ajustements de la fenetre Matplotlib
        ax_mol.set_xlim(1.5, 6.5)
        ax_mol.set_ylim(1.0, 4.2)
        ax_mol.axis("off")
        
        st.pyplot(fig_mol)
        st.divider()

        # --- CODE DU QUIZ 1 ALÉATOIRE ---
        st.subheader("Quiz 1 : Formulaire d'evaluation")

        # Initialisation stable de la liste des questions pour eviter un melange permanent a chaque clic
        if "ordre_quiz1" not in st.session_state:
            base_quiz1 = [
                {"id": "q1_1", "q": "La molecule du vinaigre est :", "type": "menu", "options": ["acide", "neutre", "basique"], "rep": "acide"},
                {"id": "q1_2", "q": "Calculer la masse molaire moleculaire du vinaigre en g/mol: ", "type": "entry", "rep": "60"},
                {"id": "q1_3", "q": "Quel est le nom chimique de la molecule du vinaigre ?", "type": "entry", "rep": "acide acetique"},
                {"id": "q1_4", "q": "Quel est le nombre d'atome de carbone que possede la molecule de vinaigre ?", "type": "entry", "rep": "2"},
                {"id": "q1_5", "q": "Quel est le nombre d'atome d'hydrohene que possede la molecule de vinaigre ?", "type": "entry", "rep": "4"},
                {"id": "q1_6", "q": "Quel est le nombre d'atome d''oxygene que possede la molecule de vinaigre ?", "type": "entry", "rep": "2"},
                {"id": "q1_7", "q": "Quelle est la formule brute de vinaigre ?", "type": "menu", "options": ["C4H2O2", "C2H4O2", "C2H2O4", "C2H2O2"], "rep": "C2H4O2"},
            ]
            random.shuffle(base_quiz1)
            st.session_state.ordre_quiz1 = base_quiz1

        score1 = 0
        
        # Rendu des elements tires du cycle de donnees stable
        for item in st.session_state.ordre_quiz1:
            if item["type"] == "menu":
                # Ajout d'une option vide par defaut pour eviter la pre-selection automatique de la bonne reponse
                opts = [""] + item["options"] if "" not in item["options"] else item["options"]
                reponse = st.selectbox(item["q"], options=opts, key=f"select_{item['id']}")
            else:
                reponse = st.text_input(item["q"], key=f"input_{item['id']}").strip().lower()

            # Mode de verification des reponses
            if reponse != "":
                if reponse == item["rep"]:
                    score1 += 1
                    if not st.session_state.mode_examen_tab1:
                        st.success("Correct")
                else:
                    if not st.session_state.mode_examen_tab1:
                        st.error("Incorrect")

        # --- LOGIQUE D'ÉTAT DU MODE EXAMEN ET DE VALIDATION (Ancien valider_tout1 et basculer) ---
        if "examen_verrouille_tab1" not in st.session_state:
            st.session_state.examen_verrouille_tab1 = False
        if "quiz1_soumis" not in st.session_state:
            st.session_state.quiz1_soumis = False

            
            # Declenchement du basculement (Ancien basculer_mode_examen_protection1)
        if st.session_state.mode_examen_tab1 and not st.session_state.get("examen_verrouille_tab1", False):
            st.session_state.examen_verrouille_tab1 = True
            st.session_state.quiz1_soumis = False
            random.shuffle(st.session_state.ordre_quiz1)
            for item in st.session_state.ordre_quiz1:
                if f"select_{item['id']}" in st.session_state: st.session_state[f"select_{item['id']}"] = ""
                if f"input_{item['id']}" in st.session_state: st.session_state[f"input_{item['id']}"] = ""
            st.rerun()

        st.divider()

        # Bouton de validation global (Ancien valider_tout1)
        # Il est rendu inactif ("disabled") uniquement si l'examen est soumis et verrouille
        desactiver_validation = st.session_state.quiz1_soumis and st.session_state.mode_examen_tab1

        if st.button("Valider mes reponses", type="primary", disabled=desactiver_validation):
            # Verification de l'identification de l'eleve
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.error("Action impossible ! Veuillez inscrire votre NOM et votre PRENOM dans l'onglet Identification avant de pouvoir valider.")
            else:
                st.session_state.quiz1_soumis = True
                
                if st.session_state.mode_examen_tab1:
                    st.success("Copie d'examen enregistree avec succes pour correction.")
                else:
                    st.success(f"Validation effectuee. Votre score running est de : {score1} / {len(st.session_state.ordre_quiz1)}")
                st.rerun()

        # Affichage persistant du score final en mode entrainement libre
        if st.session_state.quiz1_soumis and not st.session_state.mode_examen_tab1:
            st.metric(
                label=f"Score de {st.session_state.nom.replace(' ', '_')}", 
                value=f"{score1} / {len(st.session_state.ordre_quiz1)}"
            )

        # Option de reinitialisation (Ancien reinitialiser1) - Interdit en plein examen
        if not st.session_state.mode_examen_tab1 and st.session_state.quiz1_soumis:
            if st.button("Refaire l'exercice (Mode Entrainement)"):
                st.session_state.quiz1_soumis = False
                for item in st.session_state.ordre_quiz1:
                    if f"select_{item['id']}" in st.session_state: st.session_state[f"select_{item['id']}"] = ""
                    if f"input_{item['id']}" in st.session_state: st.session_state[f"input_{item['id']}"] = ""
                st.rerun()
        # --- LOGIQUE CHIMIQUE ET EXPORT HTML (Ancien exporter_rapport1) ---
        lignes_html_tableau = ""
        score1 = 0
        
        # Parcours des questions pour calculer le score final et peupler le tableau HTML
        for idx, item in enumerate(st.session_state.ordre_quiz1):
            # Récupération de la saisie utilisateur depuis le session_state de Streamlit
            if item["type"] == "menu":
                reponse_eleve = st.session_state.get(f"select_{item['id']}", "").strip()
            else:
                reponse_eleve = st.session_state.get(f"input_{item['id']}", "").strip()
            
            reponse_correcte = item["rep"].strip()
            intitule_q = item["q"].strip()
            
            # Gestion des réponses vides
            if reponse_eleve == "" or reponse_eleve == "-------":
                statut_badge = '<span class="status-fail">INCORRECT</span>'
                reponse_eleve_affiche = "Aucune reponse"
            elif reponse_eleve.lower() == reponse_correcte.lower():
                score1 += 1
                statut_badge = '<span class="status-pass">CORRECT</span>'
                reponse_eleve_affiche = reponse_eleve
            else:
                statut_badge = '<span class="status-fail">INCORRECT</span>'
                reponse_eleve_affiche = reponse_eleve

            # Construction des lignes pour le fichier HTML
            lignes_html_tableau += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
                <td>{intitule_q}</td>
                <td style="color: #64748b;">{reponse_eleve_affiche}</td>
                <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
                <td style="text-align: center;">{statut_badge}</td>
            </tr>
            """

        # Code HTML calqué sur votre modèle original bleu moderne
        nom_eleve_html = st.session_state.nom.strip().upper() if st.session_state.nom else "ELEVE"
        
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Généralités sur le vinaigre</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: { "#16a34a" if score1>=4 else "#dc2626" }; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; }}
        td {{ padding: 14px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #dcfce7; color: #16a34a; border-radius: 4px; }}
        .status-fail {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #fee2e2; color: #ef4444; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score1} / 7</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Éleve :</strong> {nom_eleve_html}<br>
            <strong>Evaluation type QCM :</strong> Généralités sur le vinaigre
        </div>
    </div>
    <div class="section-title">Résultats et correction du QCM</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%;">Intitule de la question posée</th>
                <th style="width: 19%;">Votre reponse saisie</th>
                <th style="width: 19%;">Valeur attendue / Correction</th>
                <th style="width: 12%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau}
        </tbody>
    </table>
</body>
</html>
"""

        # Préparation du nom de fichier propre
        classe_fichier = st.session_state.classe if st.session_state.classe else "Classe"
        nom_fichier_html = f"Generalites_sur_le_vinaigre_{nom_eleve_html}_{classe_fichier}.html"
        for car in ["*", "?", ":", "/", "\\", "<", ">", "|", '"', " "]:
            nom_fichier_html = nom_fichier_html.replace(car, "_")

        # Rendu des boutons d'actions en bas d'onglet
        col_actions = st.columns(2)
        
        with col_actions[0]:
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.warning("Veuillez inscrire votre nom sur l'accueil pour activer l'export du rapport.")
            else:
                # Bouton d'exportation web direct
                st.download_button(
                    label="Exporter le rapport HTML",
                    data=html_content,
                    file_name=nom_fichier_html,
                    mime="text/html",
                    key="btn_export_html_tab1"
                )
                
        with col_actions[1]:
            # Option de réinitialisation libre (Ancien reinitialiser1)
            # Bloquée si le mode examen est actif (Verrou de sécurité CCF)
            if st.session_state.mode_examen_tab1:
                st.text("Reinitialisation impossible en Mode Examen")
            elif st.session_state.quiz1_soumis:
                if st.button("Recommencer l'exercice", key="reset_tab1_final"):
                    st.session_state.quiz1_soumis = False
                    st.session_state.examen_verrouille_tab1 = False
                    for item in st.session_state.ordre_quiz1:
                        if f"select_{item['id']}" in st.session_state: st.session_state[f"select_{item['id']}"] = ""
                        if f"input_{item['id']}" in st.session_state: st.session_state[f"input_{item['id']}"] = ""
                    st.rerun()




# ==========================================
# ONGLET 2 : DOSAGE COLORIMÉTRIQUE ET pH-MÉTRIQUE
# ==========================================
with tab2:
    st.header("Dosage colorimetrique du vinaigre")
    st.caption("Dosage de 10 mL d'une solution de 100 mL de vinaigre dilue 10 fois par de la soude")

    # --- INITIALISATION DE L'ÉTAT PROPRE A L'ONGLET 2 ---
    if "c_base" not in st.session_state: st.session_state.c_base = 0.1
    if "pas_ml" not in st.session_state: st.session_state.pas_ml = 1.0
    if "v_verse" not in st.session_state: st.session_state.v_verse = 0.0
    if "masse_reelle_g" not in st.session_state: st.session_state.masse_reelle_g = random.uniform(0.80, 0.90)

    # Parametres physico-chimiques fixes
    pKa = 4.76  # Constante d'acidite de l'acide acetique
    M_vinaigre = 60.0
    densite_vinaigre = 1.05
    v_acide_ml = 10.0
    v_max_ml = 25.0

    # Calcul theorique de la concentration en acide dose (dilue)
    # n_acide = (masse / M) * facteur_dilution deduit de votre formulation originale
    n_acide_ini = (st.session_state.masse_reelle_g) * densite_vinaigre / M_vinaigre
    c_acide_dose = n_acide_ini / 0.010  # Prise d'essai de 10mL

    # Calcul exact du volume equivalent theorique : Ca * Va = Cb * Veq -> Veq = (Ca * Va) / Cb
    v_eq_theorique = (c_acide_dose * v_acide_ml) / st.session_state.c_base

    # --- ZONE DE REGLAGE DES PARAMETRES (Haut de l'onglet) ---
    with st.container(border=True):
        st.subheader("Parametres de la solution titrante et du goutte-a-goutte")
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.session_state.c_base = st.number_input(
                "Concentration de la soude C_b (mol/L) :", 
                min_value=0.01, max_value=2.0, value=st.session_state.c_base, step=0.01
            )
        with col_p2:
            st.session_state.pas_ml = st.slider(
                "Pas du compte-goutte (mL) :", 
                min_value=0.1, max_value=2.0, value=st.session_state.pas_ml, step=0.1
            )
        with col_p3:
            # Choix de l'indicateur colore
            liste_indicateurs = list(st.session_state.indicateurs.keys())
            choix_ind = st.selectbox("Selectionner un indicateur colore :", options=liste_indicateurs, index=0)

    st.divider()

    # --- SIMULATION MATRICIELLE DU DOSAGE pH-METRIQUE ---
    # Generation de la courbe complete en arriere-plan pour le tracé
    volumes_simules = np.arange(0, v_max_ml + 0.1, 0.1)
    phs_simules = []

    for v in volumes_simules:
        # Équation simplifiee Henderson-Hasselbalch pour un titrage acide faible / base forte
        if v < v_eq_theorique:
            # Avant l'equivalence : Solution tampon
            rapport = v / (v_eq_theorique - v) if (v_eq_theorique - v) > 0 else 1000
            ph = pKa + math.log10(rapport) if rapport > 0 else pKa - 2
        elif abs(v - v_eq_theorique) < 0.1:
            # À l'equivalence
            ph = 8.7
        else:
            # Apres l'equivalence : Exces de base forte
            exces_oh = (st.session_state.c_base * (v - v_eq_theorique)) / (v_acide_ml + v)
            pOH = -math.log10(exces_oh) if exces_oh > 0 else 7
            ph = 14 - pOH
        # Restriction des bornes physiques du pH
        phs_simules.append(max(1.0, min(13.9, ph)))

    # --- AJOUT INTERACTIF DE SOUDE ---
    st.subheader("Ajout progressif de la solution titrante")
    st.session_state.v_verse = st.slider(
        "Volume de soude total verse V_B (mL) :", 
        min_value=0.0, max_value=v_max_ml, value=st.session_state.v_verse, step=st.session_state.pas_ml
    )

    # Récupération du pH actuel indexé sur le slider
    idx_actuel = min(int(st.session_state.v_verse * 10), len(volumes_simules) - 1)
    ph_actuel = phs_simules[idx_actuel]


    # --- MISE EN PAGE INTERACTIVE : SCHÉMA DU MONTAGE & GRAPHIQUE ---
    col_visuel, col_graph = st.columns([1, 1.2])

    with col_visuel:
        st.write("**Schema du Montage pH-metrique**")
        
        # Determination de la teinte selon le pH actuel (Ancien get_indicateur_couleur)
        ind_data = st.session_state.indicateurs[choix_ind]
        if ph_actuel < ind_data["ph_min"]:
            couleur_solution = ind_data["couleur_acide"]
            nom_zone_teinte = ind_data["nom_acide"]
        elif ph_actuel > ind_data["ph_max"]:
            couleur_solution = ind_data["couleur_base"]
            nom_zone_teinte = ind_data["nom_base"]
        else:
            couleur_solution = ind_data["couleur_zone"]
            nom_zone_teinte = ind_data["nom_zone"]

        # --- RE-CRÉATION DU SCHÉMA VECTORIEL DU MONTAGE (Ancien dessiner_montage_initial) ---
        fig_montage, ax_mo = plt.subplots(figsize=(4, 5), facecolor="white")
        ax_mo.set_facecolor("white")
        
        # 1. La potence de laboratoire
        ax_mo.add_patch(patches.Rectangle((1.0, 0.5), 0.3, 9.0, color="#7f8c8d")) # Tige verticale
        ax_mo.add_patch(patches.Rectangle((1.3, 8.0), 3.2, 0.15, color="#95a5a6")) # Bras horizontal
        
        # 2. La burette graduee et son niveau de liquide (Ancien mettre_a_jour_niveaux_liquides)
        # Calcul de la diminution du volume dans la burette
        hauteur_liquide_burette = 3.5 * (1.0 - (st.session_state.v_verse / v_max_ml))
        ax_mo.add_patch(patches.Rectangle((3.6, 4.5), 0.6, 4.0, facecolor="none", edgecolor="#34495e", linewidth=2)) # Corps burette
        ax_mo.add_patch(patches.Rectangle((3.62, 4.52), 0.56, hauteur_liquide_burette, facecolor="#aed6f1", alpha=0.8)) # Liquide bleu ciel
        ax_mo.add_patch(patches.Rectangle((3.8, 4.1), 0.2, 0.4, color="#2c3e50")) # Robinet
        
        # 3. La Goutte en suspension ou en chute libre
        ax_mo.add_patch(patches.Circle((3.9, 3.7), 0.08, color="#aed6f1"))
        
        # 4. Le becher et son niveau de liquide qui monte
        hauteur_liquide_becher = 1.0 + 1.2 * (st.session_state.v_verse / v_max_ml)
        ax_mo.add_patch(patches.Polygon([[2.6, 1.0], [2.6, 3.2], [4.8, 3.2], [4.8, 1.0]], facecolor="none", edgecolor="#34495e", linewidth=3)) # Verre du becher
        ax_mo.add_patch(patches.Rectangle((2.65, 1.05), 2.1, hauteur_liquide_becher, facecolor=couleur_solution, alpha=0.75)) # Solution coloree
        
        # 5. L'agitateur magnetique et le barreau aimante oscillant
        ax_mo.add_patch(patches.Rectangle((2.2, 0.3), 3.0, 0.7, facecolor="#bdc3c7", edgecolor="#7f8c8d", linewidth=2)) # Socle
        # Simulation graphique de l'agitation : le barreau change d'angle selon le volume verse
        angle_barreau = 5 if int(st.session_state.v_verse * 10) % 2 == 0 else -5
        barreau = patches.Rectangle((3.1, 1.1), 1.2, 0.15, facecolor="#ffffff", edgecolor="#7f8c8d", angle=angle_barreau)
        ax_mo.add_patch(barreau)
        
        # 6. La sonde pH-metrique plongeante
        ax_mo.add_patch(patches.Rectangle((4.3, 1.6), 0.3, 3.0, color="#34495e")) # Corps de la sonde
        ax_mo.plot([4.45, 4.45, 5.5], [4.6, 7.5, 7.5], color="#34495e", linewidth=2) # Fil de liaison
        
        # 7. Le boitier afficheur du pH-metre digital
        ax_mo.add_patch(patches.Rectangle((5.5, 6.5), 2.2, 1.5, facecolor="#2c3e50", edgecolor="#1a252f", linewidth=2))
        ax_mo.text(6.6, 7.2, f"pH: {ph_actuel:.2f}", color="#2ecc71", fontfamily="monospace", weight="bold", fontsize=11, ha="center")
        ax_mo.text(3.7, 0.05, f"Teinte : {nom_zone_teinte}", color="#1e293b", fontsize=9, ha="center")
        
        ax_mo.set_xlim(0.5, 8.0)
        ax_mo.set_ylim(0.0, 9.5)
        ax_mo.axis("off")
        st.pyplot(fig_montage)



    # --- TABLEAU DE SUIVI DES MESURES TRANSPOSÉ (Ancien ajouter_colonne_tableau) ---
    st.subheader("Tableau de suivi (3 lignes - Colonnes multiples)")
    
    # Extraction des points de mesure bases sur le pas de l'eleve
    indices_mesures = list(range(0, idx_actuel + 1))
    
    colonnes_vol = []
    colonnes_ph = []
    colonnes_obs = []
    
    for idx in indices_mesures:
        v_pt = volumes_simules[idx]
        ph_pt = phs_simules[idx]
        
        # Recupération de l'observation de teinte pour la cellule associee
        ind_d = st.session_state.indicateurs[choix_ind]
        if ph_pt < ind_d["ph_min"]: obs = ind_d["nom_acide"]
        elif ph_pt > ind_d["ph_max"]: obs = ind_d["nom_base"]
        else: obs = ind_d["nom_zone"]
            
        colonnes_vol.append(f"{v_pt:.2f}")
        colonnes_ph.append(f"{ph_pt:.2f}")
        colonnes_obs.append(obs)


    # Structure en lignes de grille (Conforme a votre matrice originale)
    if len(colonnes_vol) > 0:
        grille_suivi = pd.DataFrame([colonnes_vol, colonnes_ph, colonnes_obs], 
                                    index=["Soude versee V_B (mL)", "pH mesure", "Observations / Teinte"])
        st.dataframe(grille_suivi, use_container_width=True)
    else:
            st.caption("Faites glisser le curseur d'ajout de volume ci-dessus pour initialiser la premiere colonne du tableau.")

            # --- INITIALISATION CHIMIQUE UNIQUE (Équivalent de reset_simulation) ---
    if "reinit_declenche" not in st.session_state or st.button("Reinitialiser la simulation / Changer de flacon"):
        # Tirage de la masse en grammes (entre 80 et 90 mg comme votre formule original : 80 a 90 / 1000)
        st.session_state.masse_reelle_g = random.uniform(80.0, 90.0) / 1000.0
        st.session_state.v_verse = 0.0
        st.session_state.reinit_declenche = True

    # Récupération locale des constantes définies dans votre code
    pKa = 4.17  # Valeur de votre pKa pour le calcul
    Ka = 10**(-pKa)
    M_vinaigre = 60.0
    V_ini = 10.0  # Volume initial dans le bécher en mL
    v_max_ml = 25.0

    # Application de vos formules physiques exactes
    C_base = st.session_state.c_base if "c_base" in st.session_state else 0.1
    n_acide_ini = st.session_state.masse_reelle_g / M_vinaigre

    # Calcul exact du volume équivalent attendu (en mL)
    if C_base > 0:
        v_eq_theorique = (n_acide_ini / C_base) * 1000.0
        # Calcul logarithmique exact du pH à l'équivalence selon votre formule
        concentration_eq = n_acide_ini / ((v_eq_theorique + V_ini) / 1000.0)
        ph_eq_theorique = 0.5 * (pKa + 14.0 + math.log10(concentration_eq))
    else:
        v_eq_theorique = 0.0
        ph_eq_theorique = 7.0

    # Affichage des informations textuelles du flacon (Équivalent de lbl_info)
    st.info(f"Compose : Vinaigre | Masse pesee (aleatoire) : {st.session_state.masse_reelle_g * 1000.0:.1f} mg | Soude titrante : {C_base} mol/L")
        
    # --- FONCTION DE CALCUL DU pH (Copie conforme de votre algorithme calculer_ph) ---
    def extraire_ph_point(v_b_ml):
        v_b = v_b_ml / 1000.0
        v_a_total = V_ini / 1000.0
        n_b = v_b * C_base
        v_tot = v_a_total + v_b
        
        if v_tot <= 0 or n_acide_ini <= 0:
            return 1.0
            
        if n_b < n_acide_ini:
            if n_b == 0:
                c_acide_ini = n_acide_ini / v_a_total
                return max(1.0, 0.5 * (pKa - math.log10(c_acide_ini)))
            ratio = n_b / n_acide_ini
            # Équation d'Henderson-Hasselbalch basée sur votre ratio
            return max(1.0, min(13.0, pKa + math.log10(ratio / (1.0 - ratio))))
        else:
            ratio = n_b / n_acide_ini
            if ratio == 1.0: # Équivalence exacte
                return ph_eq_theorique
            return min(13.5, 14.0 + math.log10(n_acide_ini / v_tot) + math.log10(ratio - 1.0))

    # 1. Generation de la courbe mathematique complete en arriere-plan
    volumes_simules = np.arange(0, v_max_ml + 0.1, 0.1)
    ph_simules = [extraire_ph_point(v) for v in volumes_simules]

    # 2. Recuperation du point actuel selectionne par l'eleve
    idx_actuel = min(int(st.session_state.v_verse * 10), len(volumes_simules) - 1)
    ph_actuel = ph_simules[idx_actuel]

    # 3. Determination dynamique de la teinte pour le montage et le tableau
    ind_data = st.session_state.indicateurs[choix_ind]
    if ph_actuel < ind_data["ph_min"]:
        couleur_solution = ind_data["couleur_acide"]
        nom_zone_teinte = ind_data["nom_acide"]
    elif ph_actuel > ind_data["ph_max"]:
        couleur_solution = ind_data["couleur_base"]
        nom_zone_teinte = ind_data["nom_base"]
    else:
        couleur_solution = ind_data["couleur_zone"]
        nom_zone_teinte = ind_data["nom_zone"]


    with col_graph:
        st.write("**Courbe de pH-metrie associee**")
        
        # Boutons d'analyse geometrique places au-dessus de la courbe dans la colonne droite
        col_an1, col_an2 = st.columns(2)
        with col_an1:
            activer_tangentes = st.checkbox("Afficher la Methode des tangentes", key="chk_tangentes")
        with col_an2:
            activer_derivee = st.checkbox("Afficher la Methode de la derivee seconde", key="chk_derivee")
            
        fig_curve, ax_cu = plt.subplots(figsize=(6, 4.8))
        
        # Trace progressif de la courbe bleue calque sur le curseur
        ax_cu.plot(volumes_simules[:idx_actuel+1], ph_simules[:idx_actuel+1], color="#2563eb", linewidth=2.5, label="pH = f(V_B)")
        ax_cu.scatter([st.session_state.v_verse], [ph_actuel], color="red", s=60, zorder=5)
        
        # --- CODE ALGORITHMIQUE : MÉTHODE DES TANGENTES ---
        if activer_tangentes:
            V_arr = np.array(volumes_simules[:idx_actuel+1])
            pH_arr = np.array(ph_simules[:idx_actuel+1])
            idx_avant = np.where(V_arr < veq_theorique_mL - 3)[0]
            idx_apres = np.where(V_arr > veq_theorique_mL + 3)[0]
            
            if len(idx_avant) > 2 and len(idx_apres) > 2:
                p1 = np.polyfit(V_arr[idx_avant[-3:]], pH_arr[idx_avant[-3:]], 1)
                p2 = np.polyfit(V_arr[idx_apres[:3]], pH_arr[idx_apres[:3]], 1)
                
                v_plot = np.linspace(0, v_max_ml, 200)
                t1 = p1[0] * v_plot + p1[1]
                t2 = p2[0] * v_plot + p2[1]
                
                ax_cu.plot(v_plot, t1, 'r--', alpha=0.7, label="Tangente 1")
                ax_cu.plot(v_plot, t2, 'r--', alpha=0.7, label="Tangente 2")
                ax_cu.axvline(x=veq_theorique_mL, color='g', linestyle=':', lw=2, label=f"V_E = {veq_theorique_mL:.2f} mL")
                ax_cu.plot(veq_theorique_mL, ph_eq_reel, 'go', markersize=8)
                st.toast(f"Methode des tangentes appliquee : V_eq = {veq_theorique_mL:.2f} mL")
                
        # --- CODE ALGORITHMIQUE : DERIVÉE SECONDE ---
        if activer_derivee:
            ax_cu.axvline(x=veq_theorique_mL, color='m', linestyle='-.', lw=2, label=f"Equivalence : {veq_theorique_mL:.2f} mL")
            ax_cu.plot(veq_theorique_mL, ph_eq_reel, 'mo', markersize=8)
            st.toast(f"Methode de la derivee seconde appliquee : V_eq = {veq_theorique_mL:.2f} mL")
            
        ax_cu.set_xlabel("Volume de soude verse V_B (mL)")
        ax_cu.set_ylabel("pH")
        ax_cu.set_xlim(0, v_max_ml + 1)
        ax_cu.set_ylim(0, 14)
        ax_cu.grid(True, linestyle=":")
        ax_cu.legend(loc="lower right")
        st.pyplot(fig_curve)

    # --- MOTEUR DE CALCUL THÉORIQUE DE L'ÉQUIVALENCE (Ancien reinitialiser) ---
    C_base = st.session_state.c_base if "c_base" in st.session_state else 0.1
    V_ini = 10.0  # Volume titré fixe en mL
    M_vinaigre = 60.0
    pKa = 4.17
    v_max_ml = 25.0

    # Quantité et concentration initiale calculées sur la masse réelle tirée au flacon
    n_acide_total = st.session_state.masse_reelle_g / M_vinaigre
    c_titre = n_acide_total / (V_ini / 1000.0) if V_ini > 0 else 0.0

    # Validation des intervalles physiques de sécurité (Ancien bloc Try/Except ValueError)
    if not (5.0 <= V_ini <= 25.0) or c_titre <= 0 or C_base <= 0:
        st.error("Erreur : Saisies de simulation incorrectes. Verifiez les intervalles physico-chimiques.")
    else:
        # Calcul du volume équivalent théorique (en Litres puis converti en mL)
        veq_theorique_L = (c_titre * (V_ini / 1000.0)) / C_base
        veq_theorique_mL = veq_theorique_L * 1000.0

        # Formule pH équivalence acide faible (base faible dans l'eau) : 7 + 0.5*(pKa + log C_eq)
        c_eq = (c_titre * (V_ini / 1000.0)) / ((V_ini / 1000.0) + veq_theorique_L)
        ph_eq_reel = round(7.0 + 0.5 * (pKa + math.log10(c_eq)), 3)
        ph_eq_reel = max(7.05, min(11.5, ph_eq_reel))

    # --- PANNEAU DE RAPPEL DU PROFESSEUR (Anciens labels verts label_theorie_eq) ---
    with st.expander("Consulter les reperes theoriques attendus (Professeur)", expanded=False):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown(f"**Donnees fixees :**")
            st.markdown(f"➜ Concentration titrante ($C_b$) = {C_base} mol/L")
            st.markdown(f"➜ Masse molaire ($M$) = {M_vinaigre} g/mol")
            st.markdown(f"➜ Volume titre ($V_{{ini}}$) = {V_ini} mL")
        with col_t2:
            st.markdown(f"**Valeurs a l'equivalence attendues :**")
            st.info(f"Attendu : $V_{{eq}}$ = {veq_theorique_mL:.2f} mL\n\n$pH_{{{{eq}}}}$ = {ph_eq_reel:.2f}")

    # --- SIMULATION DE LA PROGRESSION (Ancien update_simulation) ---
    # Si le volume max est versé, on affiche l'état final stabilisé
    if st.session_state.v_verse >= v_max_ml:
        st.success(f"➜ Equivalence atteinte : V_eq = {veq_theorique_mL:.2f} mL | pH_eq = {ph_eq_reel:.2f}")
        
        # Injection des repères dans les champs de session pour l'onglet 3
        st.session_state.v_eq_calcule = round(veq_theorique_mL, 2)
        st.session_state.ph_eq_calcule = round(ph_eq_reel, 2)

            
        ax_cu.set_xlabel("Volume de soude verse V_B (mL)")
        ax_cu.set_ylabel("pH")
        ax_cu.set_xlim(0, v_max_ml + 1)
        ax_cu.set_ylim(0, 14)
        ax_cu.grid(True, linestyle=":")
        ax_cu.legend(loc="lower right")
        st.pyplot(fig_curve)

    st.divider()

    # --- INITIALISATION DE L'ORDRE DU QUIZ 2 (Ancien setup_quiz2 avec brassage stable) ---
    if "ordre_quiz2" not in st.session_state:
        base_quiz2 = [
            {"id": "q2_1", "q": "Quel indicateur colore est le mieux adapte au dosage ?", "type": "menu", "options": ["Hélianthine", "Bleu de Thymol", "Bleu de Bromothymol (BBT)", "Jaune d'Alizarin R"], "rep": "Bleu de Bromothymol (BBT)"},
            {"id": "q2_2", "q": "Quel est le role d'un indicateur colore ?", "type": "menu", "options": ["mettre une couleur dans le solution de départ", "repérer l'équivalence", "connaître la valeur du pH"], "rep": "repérer l'équivalence"},
            {"id": "q2_3", "q": "Quelle est le volume titre en mL ?", "type": "entry", "rep": "10"},
            {"id": "q2_4", "q": "Quelle est la valeur du volume equivalent de votre experience en mL ?", "type": "entry", "rep": "dynamique_v_eq"},
            {"id": "q2_5", "q": "Quelle est la valeur de la concentration de l'espece titrante de votre experience en mol/L ?", "type": "entry", "rep": "dynamique_c_base"},
            {"id": "q2_6", "q": "Quelle est la valeur du pH equivalent de votre experience ?", "type": "entry", "rep": "dynamique_ph_eq"}
        ]
        random.shuffle(base_quiz2)
        st.session_state.ordre_quiz2 = base_quiz2

    st.subheader("Quiz 2 : Formulaire d'evaluation du dosage")
    
    if "quiz2_soumis" not in st.session_state:
        st.session_state.quiz2_soumis = False

    score2 = 0
    reponses_eleve_q2 = {}

    # Rendu et notation du QCM (Ancien valider_tout2)
    for item in st.session_state.ordre_quiz2:
        if item["type"] == "menu":
            opts = [""] + item["options"]
            reponses_eleve_q2[item["id"]] = st.selectbox(item["q"], options=opts, key=f"sel_q2_{item['id']}")
            bonne_rep = str(item["rep"]).strip().lower()
            est_correct = (reponses_eleve_q2[item["id"]].strip().lower() == bonne_rep)
        else:
            reponses_eleve_q2[item["id"]] = st.text_input(item["q"], key=f"inp_q2_{item['id']}").strip().replace(",", ".")
            
            # Gestion des verifications dynamiques selon l'intitule de la question
            q_lower = item["q"].lower()
            val_saisie = reponses_eleve_q2[item["id"]]
            
            if "volume" in q_lower and "equivalent" in q_lower:
                target = veq_theorique_mL
                try: est_correct = (abs(float(val_saisie) - target) < 0.1)
                except ValueError: est_correct = False
            elif "ph" in q_lower and "equivalent" in q_lower:
                target = ph_eq_reel
                try: est_correct = (abs(float(val_saisie) - target) < 0.1)
                except ValueError: est_correct = False
            elif "concentration" in q_lower:
                target = C_base
                try: est_correct = (abs(float(val_saisie) - target) < 0.01)
                except ValueError: est_correct = False
            else:
                target = str(item["rep"]).strip().lower()
                est_correct = (val_saisie.lower() == target)

        if reponses_eleve_q2[item["id"]] != "":
            if est_correct:
                score2 += 1
                if not st.session_state.mode_examen_tab2: st.success("Correct")
            else:
                if not st.session_state.mode_examen_tab2: st.error("Incorrect")

    # Bouton global de soumission du Quiz 2
    if st.button("Valider et enregistrer le Quiz 2", key="btn_soumission_q2"):
        if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
            st.error("Action impossible ! Veuillez inscrire votre NOM et votre PRENOM dans l'onglet Identification.")
        else:
            st.session_state.quiz2_soumis = True
            st.session_state.v_eq = veq_theorique_mL  # Transmission securisee pour l'onglet 3
            st.session_state.c_titrant = C_base
            st.session_state.ph_eq = ph_eq_reel
            st.success("Copie validee et enregistree pour l'analyse finale.")
    # --- LOGIQUE DU MODE EXAMEN ET REINITIALISATION (Ancien basculer_mode_examen_protection2 / reinitialiser2) ---
    if "examen_verrouille_tab2" not in st.session_state:
        st.session_state.examen_verrouille_tab2 = False

       
        # Logique de basculement et brassage automatique (Ancien basculer_mode_examen_protection2)
        if st.session_state.mode_examen_tab2 and not st.session_state.get("examen_verrouille_tab2", False):
            st.session_state.mode_examen_tab2 = True
            st.session_state.examen_verrouille_tab2 = True  # Verrou de blocage du retour en arrière
            st.session_state.quiz2_soumis = False
            
            # Mélange immédiat de l'ordre des questions en mémoire
            random.shuffle(st.session_state.ordre_quiz2)
            
            # Remise à zéro complète de tous les champs de saisie de l'élève
            for item in st.session_state.ordre_quiz2:
                if f"sel_q2_{item['id']}" in st.session_state: st.session_state[f"sel_q2_{item['id']}"] = ""
                if f"inp_q2_{item['id']}" in st.session_state: st.session_state[f"inp_q2_{item['id']}"] = ""
            
            st.rerun()

    # --- OPTIONS DE REINITIALISATION (Ancien reinitialiser2) ---
    # Placé en fin d'onglet sous le bouton de validation du Quiz 2
    if st.session_state.quiz2_soumis:
        if st.session_state.mode_examen_tab2:
            st.text("Reinitialisation impossible en Mode Examen")
        else:
            # En mode entraînement libre, l'élève peut réinitialiser pour recommencer
            if st.button("Refaire l'exercice (Mode Entrainement)", key="reset_tab2_final"):
                st.session_state.quiz2_soumis = False
                st.session_state.examen_verrouille_tab2 = False
                st.session_state.mode_examen_tab2 = False
                
                # Nettoyage des saisies utilisateurs
                for item in st.session_state.ordre_quiz2:
                    if f"sel_q2_{item['id']}" in st.session_state: st.session_state[f"sel_q2_{item['id']}"] = ""
                    if f"inp_q2_{item['id']}" in st.session_state: st.session_state[f"inp_q2_{item['id']}"] = ""
                
                st.rerun()
    # --- LOGIQUE D'EXPORTATION DU RAPPORT HTML (Ancien exporter_rapport2) ---
    lignes_html_tableau = ""
    score2 = 0
    total_questions = len(st.session_state.get("ordre_quiz2", []))

    if total_questions > 0:
        for idx, item in enumerate(st.session_state.ordre_quiz2):
            intitule_q = item.get("q", "").strip()
            
            # Récupération de la saisie utilisateur depuis l'interface Streamlit
            if item["type"] == "menu":
                reponse_eleve = st.session_state.get(f"sel_q2_{item['id']}", "").strip()
            else:
                reponse_eleve = st.session_state.get(f"inp_q2_{item['id']}", "").strip()

            if reponse_eleve == "" or reponse_eleve == "-------":
                reponse_eleve_affiche = "Aucune reponse"
                est_correct = False
            else:
                reponse_eleve_affiche = reponse_eleve
                
                # Algorithme de recalcul dynamique des cibles de correction
                q_lower = intitule_q.lower()
                if "volume" in q_lower and "equivalent" in q_lower:
                    try: est_correct = (abs(float(reponse_eleve) - veq_theorique_mL) < 0.1)
                    except ValueError: est_correct = False
                elif "ph" in q_lower and "equivalent" in q_lower:
                    try: est_correct = (abs(float(reponse_eleve) - ph_eq_reel) < 0.1)
                    except ValueError: est_correct = False
                elif "concentration" in q_lower:
                    try: est_correct = (abs(float(reponse_eleve) - C_base) < 0.01)
                    except ValueError: est_correct = False
                else:
                    est_correct = (reponse_eleve.lower() == str(item["rep"]).strip().lower())

            # Formatage de la valeur attendue pour l'affichage de la correction
            if "volume" in q_lower and "equivalent" in q_lower: reponse_correcte = f"{veq_theorique_mL:.2f}"
            elif "ph" in q_lower and "equivalent" in q_lower: reponse_correcte = f"{ph_eq_reel:.2f}"
            elif "concentration" in q_lower: reponse_correcte = f"{C_base:.2f}"
            else: reponse_correcte = str(item["rep"])

            if est_correct:
                score2 += 1
                statut_badge = '<span class="status-pass">CORRECT</span>'
            else:
                statut_badge = '<span class="status-fail">INCORRECT</span>'

            lignes_html_tableau += f"""
            <tr>
                <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
                <td>{intitule_q}</td>
                <td style="color: #64748b;">{reponse_eleve_affiche}</td>
                <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
                <td style="text-align: center;">{statut_badge}</td>
            </tr>
            """

        note_sur_20 = (score2 / total_questions) * 20 if total_questions > 0 else 0.0
        nom_eleve_html = st.session_state.nom.strip().upper() if st.session_state.nom else "ELEVE"

        # Modèle de compte-rendu HTML bleu calqué sur votre code initial
        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Analyse du dosage du vinaigre - Onglet 2</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: { "#16a34a" if score2>=(total_questions/2) else "#dc2626" }; }}
        .score-box .sub {{ font-size: 11px; color: #64748b; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; }}
        td {{ padding: 14px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #dcfce7; color: #16a34a; border-radius: 4px; }}
        .status-fail {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #fee2e2; color: #ef4444; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score2} / {total_questions}</div>
            <div class="sub">({note_sur_20:.2f} / 20)</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Eleve :</strong> {nom_eleve_html}<br>
            <strong>Evaluation :</strong> Analyse du dosage du vinaigre - Atelier 2
        </div>
    </div>
    <div class="section-title">Resultats et correction du QCM</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%;">Intitule de la question posee</th>
                <th style="width: 19%;">Votre reponse saisie</th>
                <th style="width: 19%;">Valeur attendue / Correction</th>
                <th style="width: 12%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau}
        </tbody>
    </table>
</body>
</html>
"""

        # Uniformisation du nom du fichier
        classe_fichier = st.session_state.classe if st.session_state.classe else "Classe"
        nom_fichier_html2 = f"Analyse_dosage_vinaigre_QCM2_{nom_eleve_html}_{classe_fichier}.html"
        for car in ["*", "?", ":", "/", "\\", "<", ">", "|", '"', " "]:
            nom_fichier_html2 = nom_fichier_html2.replace(car, "_")

        # Affichage du bouton de téléchargement web
        st.markdown("---")
        if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
            st.warning("Veuillez renseigner votre nom sur l'accueil pour activer l'exportation du rapport 2.")
        else:
            st.download_button(
                label="Exporter le rapport d'analyse du dosage (HTML)",
                data=html_content,
                file_name=nom_fichier_html2,
                mime="text/html",
                key="btn_export_html_tab2"
            )

# ==========================================
# ONGLET 3 : CALCULS THÉORIQUES ET VÉRIFICATION DE LA BOUTEILLE
# ==========================================
with tab3:
    st.header("Calcul theorique sur le vinaigre et verification de l'inscription sur la bouteille")

    # --- 1. ZONE DE RAPPEL DU PROTOCOLE ET DES RÉSULTATS ---
    with st.container(border=True):
        st.subheader("Rappels sur les resultats de votre dosage")
        st.info(
            "On a dilue 10 mL de vinaigre pur dans une fiole de 100 mL a l'aide d'une pipette jaugee. "
            "Pour le dosage on a preleve 10 mL de cette solution diluee."
        )
        
        # Récupération sécurisée des valeurs expérimentales de l'onglet 2
        v_eq_ml = st.session_state.v_eq
        c_titrant = st.session_state.c_titrant
        ph_eq = st.session_state.ph_eq
        v_titre_ml = 10.0
        masse_molaire = 60.0

        col_rap_g, col_rap_d = st.columns(2)
        with col_rap_g:
            st.markdown(f"**Donnees de votre dosage :**")
            st.markdown(f"➜ Volume equivalent $V_{{eq}}$ = {v_eq_ml:.2f} mL")
            st.markdown(f"➜ pH a l'equivalence = {ph_eq:.2f}")
            st.markdown(f"➜ Concentration de la soude = {c_titrant:.2f} mol/L")
        with col_rap_d:
            st.markdown(f"**Constantes du systeme :**")
            st.markdown(f"➜ Volume de solution titre = {v_titre_ml:.1f} mL")
            st.markdown(f"➜ Masse molaire de l'acide acetique = {masse_molaire:.1f} g/mol")

    st.divider()



    # --- 3. LOGIQUE DES CALCULS CHIMIQUES ATTENDUS (DYNAMIQUES) ---
    v_l_attendu = v_eq_ml / 1000.0
    n_soude_attendu = c_titrant * v_l_attendu
    n_vinaigre_dose_attendu = n_soude_attendu
    c_vinaigre_dose_attendu = n_vinaigre_dose_attendu / (v_titre_ml / 1000.0) if v_eq_ml > 0 else 0.0
    masse_g_dosee_attendu = n_vinaigre_dose_attendu * masse_molaire
    masse_mg_dosee_attendu = "%e" % (masse_g_dosee_attendu * 1000.0) # Gestion écriture scientifique si nécessaire
    cm_g_l_dosee_attendu = c_vinaigre_dose_attendu * masse_molaire
    cm_mg_l_dosee_attendu = cm_g_l_dosee_attendu * 1000.0

    rapport_dilution = 10.0
    n_fiole_attendu = n_vinaigre_dose_attendu * (100.0 / 10.0)
    n_bouteille_1l_attendu = c_vinaigre_dose_attendu * rapport_dilution
    c_bouteille_attendu = c_vinaigre_dose_attendu * rapport_dilution
    masse_bouteille_g_attendu = c_bouteille_attendu * masse_molaire
    masse_bouteille_mg_attendu = masse_bouteille_g_attendu * 1000.0
    cm_bouteille_g_l_attendu = c_bouteille_attendu * masse_molaire
    cm_bouteille_mg_l_attendu = cm_bouteille_g_l_attendu * 1000.0

    # --- 4. AFFICHAGE DES FORMULAIRES EN DEUX COLONNES (GAUCHE / DROITE) ---
    col_workspace_g, col_workspace_d = st.columns(2)

    # --- COLONNE DE GAUCHE : QUIZ 31 (Analyse de la solution dosée) ---
    with col_workspace_g:
        st.subheader("Quiz Gauche : Analyse de la solution dosee")
        
        # Définition stable des questions en session pour conserver l'ordre
        if "ordre_quiz31" not in st.session_state:
            base_quiz31 = [
                {"id": "q31_1", "q": "Convertir le volume equivalent en litre :"},
                {"id": "q31_2", "q": "Calculer le nombre de mole de soude versee :"},
                {"id": "q31_3", "q": "En deduire le nombre de mole de vinaigre dosee :"},
                {"id": "q31_4", "q": "Calculer la concentration molaire en vinaigre dosee en mol/L :"},
                {"id": "q31_5", "q": "Calculer la masse de vinaigre dosee en gramme :"},
                {"id": "q31_6", "q": "En deduire la masse de vinaigre dosee en milligramme :"},
                {"id": "q31_7", "q": "Calculer la concentration massique de vinaigre dosee en g/L :"},
                {"id": "q31_8", "q": "Calculer la concentration massique de vinaigre dosee en mg/L :"}
            ]
            st.session_state.ordre_quiz31 = base_quiz31

        score31 = 0
        reponses_eleve_q31 = {}
        correction_dynamique_q31 = {}

        # Moteur d'évaluation calqué fidèlement sur l'algorithme valider_tout31
        v_eq_local = st.session_state.v_eq
        c_base_local = st.session_state.c_titrant
        v_ini_val = 10.0 # Volume fixe du prélèvement dosé (10 mL)

        # Recalcul de sécurité en arrière-plan des valeurs théoriques attendues
        val_l = v_eq_local / 1000.0
        val_n_soude = val_l * c_base_local
        val_n_vinaigre = val_n_soude
        val_c_vinaigre = val_n_vinaigre / (v_ini_val / 1000.0) if v_ini_val != 0 else 0.0
        val_masse_g = val_n_vinaigre * 60.0
        val_masse_mg = val_masse_g * 1000.0
        val_cm_g = val_masse_g / (v_ini_val / 1000.0) if v_ini_val != 0 else 0.0
        val_cm_mg = val_masse_mg / (v_ini_val / 1000.0) if v_ini_val != 0 else 0.0

        # Rendu des entrées numériques à l'écran
        for item in st.session_state.ordre_quiz31:
            q_lower = item["q"].lower()
            
            # Association de la bonne réponse calculée
            if "convertir le volume" in q_lower: bonne_rep = val_l
            elif "soude" in q_lower: bonne_rep = val_n_soude
            elif "deduire le nombre de mole de vinaigre" in q_lower: bonne_rep = val_n_vinaigre
            elif "concentration molaire" in q_lower: bonne_rep = val_c_vinaigre
            elif "gramme" in q_lower: bonne_rep = val_masse_g
            elif "milligramme" in q_lower: bonne_rep = val_masse_mg
            elif "g/l" in q_lower: bonne_rep = val_cm_g
            elif "mg/l" in q_lower: bonne_rep = val_cm_mg
            else: bonne_rep = 0.0

            # Sauvegarde de la valeur de correction formatée sans zéros inutiles
            item["rep_calculee"] = f"{bonne_rep:.6f}".rstrip('0').rstrip('.')
            if item["rep_calculee"] == "": item["rep_calculee"] = "0"

            # Champ de saisie utilisateur
            reponses_eleve_q31[item["id"]] = st.text_input(item["q"], key=f"inp_q31_{item['id']}").strip().replace(",", ".")
            val_saisie = reponses_eleve_q31[item["id"]]

            # Évaluation en temps réel (marge d'erreur < 0.05 identique à votre code)
            if val_saisie != "":
                try:
                    est_correct = (abs(float(val_saisie) - bonne_rep) < 0.05)
                except ValueError:
                    est_correct = False
                
                item["est_correct"] = est_correct
                item["reponse_saisie_eleve"] = val_saisie

                if est_correct:
                    score31 += 1
                    if not st.session_state.mode_examen_tab31: st.success("Correct")
                else:
                    if not st.session_state.mode_examen_tab31: st.error("Incorrect")

        # Bouton d'enregistrement global du bloc gauche
        if st.button("Valider le Quiz Gauche", key="btn_validation_q31"):
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.error("Action impossible ! Veuillez inscrire votre NOM et votre PRENOM dans l'onglet Identification.")
            else:
                st.session_state.examen_verrouille_tab31 = True
                st.success(f"Resultats gauches verrouilles. Note enregistree : {score31} / {len(st.session_state.ordre_quiz31)}")
    # --- LOGIQUE D'ÉTAT ET PROTECTION EXAMEN GAUCHE (Ancien basculer_mode_examen_protection31) ---
    if "examen_verrouille_tab31" not in st.session_state:
        st.session_state.examen_verrouille_tab31 = False
    if "quiz31_soumis" not in st.session_state:
        st.session_state.quiz31_soumis = False

    # Le basculement et le verrouillage sont pilotés par le composant d'en-tête de la barre latérale
    if st.session_state.mode_examen_tab31 and not st.session_state.examen_verrouille_tab31:
        st.session_state.examen_verrouille_tab31 = True  # Verrou de blocage CCF
        st.session_state.quiz31_soumis = False
        
        # Nettoyage immédiat des réponses d'entraînement de l'élève
        for item in st.session_state.get("ordre_quiz31", []):
            if f"inp_q31_{item['id']}" in st.session_state: 
                st.session_state[f"inp_q31_{item['id']}"] = ""
        st.rerun()

    # --- ACTION COMPLÉMENTAIRE DE RÉINITIALISATION LIBRE (Ancien reinitialiser31) ---
    # Ce bouton est affiché en bas du bloc gauche uniquement si l'élève n'est pas en mode examen actif
    if st.session_state.quiz31_soumis:
        if st.session_state.mode_examen_tab31:
            st.caption("Reinitialisation verrouillee en Mode Examen")
        else:
            if st.button("Recommencer le Quiz Gauche (Entrainement)", key="reset_q31_free"):
                st.session_state.quiz31_soumis = False
                st.session_state.examen_verrouille_tab31 = False
                st.session_state.mode_examen_tab31 = False
                
                # Nettoyage des champs textuels
                for item in st.session_state.get("ordre_quiz31", []):
                    if f"inp_q31_{item['id']}" in st.session_state: 
                        st.session_state[f"inp_q31_{item['id']}"] = ""
                st.rerun()

            # --- COLONNE DE DROITE : QUIZ 32 (Analyse de la bouteille commerciale) ---
    with col_workspace_d:
        st.subheader("Quiz Droit : Analyse de la bouteille commerciale")
        
        # Définition stable des questions en session pour conserver l'ordre
        if "ordre_quiz32" not in st.session_state:
            base_quiz32 = [
                {"id": "q32_1", "q": "Donner le rapport de dilution ?", "type": "entry"},
                {"id": "q32_2", "q": "En déduire le nombre de mole de vinaigre dans la fiole :", "type": "entry"},
                {"id": "q32_3", "q": "En déduire le nombre de mole de vinaigre dans la bouteille :", "type": "entry"},
                {"id": "q32_4", "q": "Calculer la concentration molaire en vinaigre de la bouteille en mol/L :", "type": "entry"},
                {"id": "q32_5", "q": "Calculer la masse de vinaigre dans la bouteille en gramme :", "type": "entry"},
                {"id": "q32_6", "q": "En déduire la masse de vinaigre dans la bouteille en milligramme :", "type": "entry"},
                {"id": "q32_8", "q": "Calculer la concentration massique de vinaigre de la bouteille en g/L :", "type": "entry"},
                {"id": "q32_9", "q": "Calculer la concentration massique de vinaigre de la bouteille en mg/L :", "type": "entry"},
                {"id": "q32_7", "q": "Conlure sur l'affichage de la bouteille :", "type": "menu", "options": ["l 'affichage correspond à la valeur trouvée", "l 'affichage ne correspond pas à la valeur trouvée", "l 'affichage correspond  à la valeur trouvée avec une petite différence"]}
            ]
            st.session_state.ordre_quiz32 = base_quiz32

        score32 = 0
        reponses_eleve_q32 = {}

        # Moteur d'évaluation calqué fidèlement sur l'algorithme valider_tout32
        v_eq_local = st.session_state.v_eq
        c_base_local = st.session_state.c_titrant
        M_vinaigre = 60.0

        # Recalculs analytiques rigoureux selon vos formules de chimie
        val_n_fiole = (c_base_local * (v_eq_local / 1000.0)) * 10.0
        val_c_bouteille = ((c_base_local * (v_eq_local / 1000.0)) / 0.010) * 10.0
        val_n_bouteille = val_c_bouteille * 1.0
        val_masse_bouteille_g = val_c_bouteille * M_vinaigre
        val_masse_bouteille_mg = val_masse_bouteille_g * 1000.0
        val_cm_bouteille_g = val_c_bouteille * M_vinaigre
        val_cm_bouteille_mg = val_cm_bouteille_g * 1000.0

        # Rendu dynamique à l'écran
        for item in st.session_state.ordre_quiz32:
            q_lower = item["q"].lower()
            est_numerique = True

            # Association de la bonne réponse calculée
            if "rapport de dilution" in q_lower: 
                bonne_rep = 10.0
            elif "dans la fiole" in q_lower: 
                bonne_rep = val_n_fiole
            elif "dans la bouteille" in q_lower and "nombre de mole" in q_lower: 
                bonne_rep = val_n_bouteille
            elif "concentration molaire" in q_lower: 
                bonne_rep = val_c_bouteille
            elif "milligramme" in q_lower: 
                bonne_rep = val_masse_bouteille_mg
            elif "mg/l" in q_lower: 
                bonne_rep = val_cm_bouteille_mg
            elif "gramme" in q_lower: 
                bonne_rep = val_masse_bouteille_g
            elif "g/l" in q_lower: 
                bonne_rep = val_cm_bouteille_g
            else:
                est_numerique = False

            # Sauvegarde de la valeur attendue formatée pour le futur exportateur HTML
            if est_numerique:
                item["rep_calculee"] = f"{bonne_rep:.6f}".rstrip('0').rstrip('.')
                if item["rep_calculee"] == "": item["rep_calculee"] = "0"
            else:
                item["rep_calculee"] = "l 'affichage correspond à la valeur trouvée" # Remplacement de l'alternative textuelle

            # Rendu du champ correspondant
            if item["type"] == "menu":
                opts = [""] + item["options"]
                reponses_eleve_q32[item["id"]] = st.selectbox(item["q"], options=opts, key=f"sel_q32_{item['id']}")
                val_saisie = reponses_eleve_q32[item["id"]]
                est_correct = (val_saisie in ["l 'affichage correspond à la valeur trouvée", "l 'affichage correspond  à la valeur trouvée avec une petite différence"])
            else:
                reponses_eleve_q32[item["id"]] = st.text_input(item["q"], key=f"inp_q32_{item['id']}").strip().replace(",", ".")
                val_saisie = reponses_eleve_q32[item["id"]]
                if val_saisie != "":
                    try:
                        est_correct = (abs(float(val_saisie) - bonne_rep) < 0.05)
                    except ValueError:
                        est_correct = False
                else:
                    est_correct = False

            # Affichage adaptatif des badges de validation (Masqué en mode examen)
            if val_saisie != "":
                item["est_correct"] = est_correct
                item["reponse_saisie_eleve"] = val_saisie

                if est_correct:
                    score32 += 1
                    if not st.session_state.mode_examen_tab32: st.success("Correct")
                else:
                    if not st.session_state.mode_examen_tab32: st.error("Incorrect")

        # Bouton d'enregistrement global du bloc droit
        if st.button("Valider le Quiz Droit", key="btn_validation_q32"):
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.error("Action impossible ! Veuillez inscrire votre NOM et votre PRENOM dans l'onglet Identification.")
            else:
                st.session_state.examen_verrouille_tab32 = True
                st.success(f"Resultats droits verrouilles. Note enregistree : {score32} / {len(st.session_state.ordre_quiz32)}")

    # --- LOGIQUE D'ETAT ET PROTECTION EXAMEN DROIT (Ancien basculer_mode_examen_protection32) ---
    if "examen_verrouille_tab32" not in st.session_state:
        st.session_state.examen_verrouille_tab32 = False
    if "quiz32_soumis" not in st.session_state:
        st.session_state.quiz32_soumis = False

    # Le basculement et le verrouillage sont synchronisés par le composant de la barre latérale
    if st.session_state.mode_examen_tab32 and not st.session_state.examen_verrouille_tab32:
        st.session_state.examen_verrouille_tab32 = True  # Verrou de blocage CCF
        st.session_state.quiz32_soumis = False
        
        # Nettoyage immédiat des réponses d'entraînement de l'élève
        for item in st.session_state.get("ordre_quiz32", []):
            if f"inp_q32_{item['id']}" in st.session_state: st.session_state[f"inp_q32_{item['id']}"] = ""
            if f"sel_q32_{item['id']}" in st.session_state: st.session_state[f"sel_q32_{item['id']}"] = ""
        st.rerun()

    # --- ACTION COMPLEMENTAIRE DE REINITIALISATION LIBRE (Ancien reinitialiser32) ---
    # Ce bouton est affiché en bas du bloc droit uniquement si l'élève n'est pas en mode examen actif
    if st.session_state.quiz32_soumis:
        if st.session_state.mode_examen_tab32:
            st.caption("Reinitialisation verrouillee en Mode Examen")
        else:
            if st.button("Recommencer le Quiz Droit (Entrainement)", key="reset_q32_free"):
                st.session_state.quiz32_soumis = False
                st.session_state.examen_verrouille_tab32 = False
                st.session_state.mode_examen_tab32 = False
                
                # Nettoyage des champs textuels et sélections
                for item in st.session_state.get("ordre_quiz32", []):
                    if f"inp_q32_{item['id']}" in st.session_state: st.session_state[f"inp_q32_{item['id']}"] = ""
                    if f"sel_q32_{item['id']}" in st.session_state: st.session_state[f"sel_q32_{item['id']}"] = ""
                st.rerun()

                # --- LOGIQUE D'EXPORTATION DU RAPPORT HTML GAUCHE (Ancien exporter_rapport31) ---
        lignes_html_tableau31 = ""
        score31_export = 0
        total_questions31 = len(st.session_state.get("ordre_quiz31", []))

        if total_questions31 > 0:
            for idx, item in enumerate(st.session_state.ordre_quiz31):
                intitule_q = item.get("q", "").strip()
                reponse_eleve = st.session_state.get(f"inp_q31_{item['id']}", "").strip()
                
                # Alignement sur les variables de calculs analytiques de l'Atelier 3
                q_lower = intitule_q.lower()
                if "convertir le volume" in q_lower: bonne_rep = val_l
                elif "soude" in q_lower: bonne_rep = val_n_soude
                elif "deduire le nombre de mole de vinaigre" in q_lower: bonne_rep = val_n_vinaigre
                elif "concentration molaire" in q_lower: bonne_rep = val_c_vinaigre
                elif "gramme" in q_lower: bonne_rep = val_masse_g
                elif "milligramme" in q_lower: bonne_rep = val_masse_mg
                elif "g/l" in q_lower: bonne_rep = val_cm_g
                elif "mg/l" in q_lower: bonne_rep = val_cm_mg
                else: bonne_rep = 0.0

                reponse_correcte = f"{bonne_rep:.6f}".rstrip('0').rstrip('.')
                if reponse_correcte == "": reponse_correcte = "0"

                if reponse_eleve == "":
                    reponse_eleve_affiche = "Aucune reponse"
                    est_correct = False
                else:
                    reponse_eleve_affiche = reponse_eleve
                    try:
                        est_correct = (abs(float(reponse_eleve) - bonne_rep) < 0.05)
                    except ValueError:
                        est_correct = False

                if est_correct:
                    score31_export += 1
                    statut_badge = '<span class="status-pass">CORRECT</span>'
                else:
                    statut_badge = '<span class="status-fail">INCORRECT</span>'

                lignes_html_tableau31 += f"""
                <tr>
                    <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
                    <td>{intitule_q}</td>
                    <td style="color: #64748b;">{reponse_eleve_affiche}</td>
                    <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
                    <td style="text-align: center;">{statut_badge}</td>
                </tr>
                """

            note_sur_20_31 = (score31_export / total_questions31) * 20 if total_questions31 > 0 else 0.0
            nom_eleve_html = st.session_state.nom.strip().upper() if st.session_state.nom else "ELEVE"

            html_content31 = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Analyse du dosage du vinaigre - Onglet 3 Gauche</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: { "#16a34a" if score31_export>=(total_questions31/2) else "#dc2626" }; }}
        .score-box .sub {{ font-size: 11px; color: #64748b; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; }}
        td {{ padding: 14px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #dcfce7; color: #16a34a; border-radius: 4px; }}
        .status-fail {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #fee2e2; color: #ef4444; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score31_export} / {total_questions31}</div>
            <div class="sub">({note_sur_20_31:.2f} / 20)</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Eleve :</strong> {nom_eleve_html}<br>
            <strong>Evaluation :</strong> Calculs theoriques - Solution dosee (Atelier 3 Gauche)
        </div>
    </div>
    <div class="section-title">Resultats et correction du QCM</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%;">Intitule de la question posee</th>
                <th style="width: 19%;">Votre reponse saisie</th>
                <th style="width: 19%;">Valeur attendue / Correction</th>
                <th style="width: 12%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau31}
        </tbody>
    </table>
</body>
</html>
"""
            classe_fichier = st.session_state.classe if st.session_state.classe else "Classe"
            nom_fichier_html31 = f"Calculs_Theoriques_Solution_Dosee_{nom_eleve_html}_{classe_fichier}.html"
            for car in ["*", "?", ":", "/", "\\", "<", ">", "|", '"', " "]:
                nom_fichier_html31 = nom_fichier_html31.replace(car, "_")

            st.markdown("---")
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.warning("Veuillez renseigner votre nom sur l'accueil pour exporter le rapport gauche.")
            else:
                st.download_button(
                    label="Exporter le rapport du Quiz Gauche (HTML)",
                    data=html_content31,
                    file_name=nom_fichier_html31,
                    mime="text/html",
                    key="btn_export_html_tab31"
                )
            
                # --- LOGIQUE D'EXPORTATION DU RAPPORT HTML DROIT (Ancien exporter_rapport32) ---
        lignes_html_tableau32 = ""
        score32_export = 0
        total_questions32 = len(st.session_state.get("ordre_quiz32", []))

        if total_questions32 > 0:
            for idx, item in enumerate(st.session_state.ordre_quiz32):
                intitule_q = item.get("q", "").strip()
                
                if item["type"] == "menu":
                    reponse_eleve = st.session_state.get(f"sel_q32_{item['id']}", "").strip()
                else:
                    reponse_eleve = st.session_state.get(f"inp_q32_{item['id']}", "").strip()
                
                # Alignement sur les formules analytiques recalculees de la bouteille
                q_lower = intitule_q.lower()
                est_num = True
                
                if "rapport de dilution" in q_lower: bonne_rep = 10.0
                elif "dans la fiole" in q_lower: bonne_rep = val_n_fiole
                elif "dans la bouteille" in q_lower and "nombre de mole" in q_lower: bonne_rep = val_n_bouteille
                elif "concentration molaire" in q_lower: bonne_rep = val_c_bouteille
                elif "milligramme" in q_lower: bonne_rep = val_masse_bouteille_mg
                elif "mg/l" in q_lower: bonne_rep = val_cm_bouteille_mg
                elif "gramme" in q_lower: bonne_rep = val_masse_bouteille_g
                elif "g/l" in q_lower: bonne_rep = val_cm_bouteille_g
                else: est_num = False

                if est_num:
                    reponse_correcte = f"{bonne_rep:.6f}".rstrip('0').rstrip('.')
                    if reponse_correcte == "": reponse_correcte = "0"
                else:
                    reponse_correcte = "l 'affichage correspond à la valeur trouvée"

                if reponse_eleve == "":
                    reponse_eleve_affiche = "Aucune reponse"
                    est_correct = False
                else:
                    reponse_eleve_affiche = reponse_eleve
                    if est_num:
                        try: est_correct = (abs(float(reponse_eleve) - bonne_rep) < 0.05)
                        except ValueError: est_correct = False
                    else:
                        est_correct = (reponse_eleve in ["l 'affichage correspond à la valeur trouvée", "l 'affichage correspond  à la valeur trouvée avec une petite différence"])

                if est_correct:
                    score32_export += 1
                    statut_badge = '<span class="status-pass">CORRECT</span>'
                else:
                    statut_badge = '<span class="status-fail">INCORRECT</span>'

                lignes_html_tableau32 += f"""
                <tr>
                    <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
                    <td>{intitule_q}</td>
                    <td style="color: #64748b;">{reponse_eleve_affiche}</td>
                    <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
                    <td style="text-align: center;">{statut_badge}</td>
                </tr>
                """

            note_sur_20_32 = (score32_export / total_questions32) * 20 if total_questions32 > 0 else 0.0
            nom_eleve_html = st.session_state.nom.strip().upper() if st.session_state.nom else "ELEVE"

            html_content32 = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Analyse du dosage du vinaigre - Onglet 3 Droit</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: { "#16a34a" if score32_export>=(total_questions32/2) else "#dc2626" }; }}
        .score-box .sub {{ font-size: 11px; color: #64748b; }}
        .section-title {{ font-size: 16px; font-weight: bold; color: #1e40af; margin-top: 35px; margin-bottom: 16px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; background: white; }}
        th {{ background-color: #475569; color: #ffffff; padding: 12px 14px; font-size: 13px; font-weight: bold; }}
        td {{ padding: 14px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
        tr:nth-child(even) td {{ background-color: #f8fafc; }}
        .status-pass {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #dcfce7; color: #16a34a; border-radius: 4px; }}
        .status-fail {{ display: inline-block; padding: 6px 12px; font-size: 11px; font-weight: bold; background-color: #fee2e2; color: #ef4444; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header-blue">
        <div class="score-box">
            <div class="title">NOTE FINALE</div>
            <div class="value">{score32_export} / {total_questions32}</div>
            <div class="sub">({note_sur_20_32:.2f} / 20)</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Eleve :</strong> {nom_eleve_html}<br>
            <strong>Evaluation :</strong> Calculs theoriques - Bouteille commerciale (Atelier 3 Droit)
        </div>
    </div>
    <div class="section-title">Resultats et correction du QCM</div>
    <table>
        <thead>
            <tr>
                <th style="width: 5%; text-align: center;">N°</th>
                <th style="width: 45%;">Intitule de la question posee</th>
                <th style="width: 19%;">Votre reponse saisie</th>
                <th style="width: 19%;">Valeur attendue / Correction</th>
                <th style="width: 12%; text-align: center;">Statut</th>
            </tr>
        </thead>
        <tbody>
            {lignes_html_tableau32}
        </tbody>
    </table>
</body>
</html>
"""
            classe_fichier = st.session_state.classe if st.session_state.classe else "Classe"
            nom_fichier_html32 = f"Calculs_Theoriques_Bouteille_Commerciale_{nom_eleve_html}_{classe_fichier}.html"
            for car in ["*", "?", ":", "/", "\\", "<", ">", "|", '"', " "]:
                nom_fichier_html32 = nom_fichier_html32.replace(car, "_")

            st.markdown("---")
            if not st.session_state.nom.strip() or not st.session_state.prenom.strip():
                st.warning("Veuillez renseigner votre nom sur l'accueil pour exporter le rapport droit.")
            else:
                st.download_button(
                    label="Exporter le rapport du Quiz Droit (HTML)",
                    data=html_content32,
                    file_name=nom_fichier_html32,
                    mime="text/html",
                    key="btn_export_html_tab32"
                )
