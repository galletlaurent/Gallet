
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application les différents types de dosage",
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
st.title("Application les différents types de dosage")
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
    "Historique et pourquoi faire des dosages",
    "Dosage colorimétrique",
    "Dosage conductimétrique",
    "Dosage spectrophotométrique",
    "Dosage pH-métrique",
    "Dosage en retour"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]


def afficher_atelier_definition_ph(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'onglet 1 (Définition du pH) sur deux colonnes."""
    import random

    # 1. Base de données des questions du Quiz (Sans émoji)
    questions_ph1_sources = [
        {"id": "qph1", "q": "Quel chimiste danois a inventé la notion de pH en 1909 ?", "options": ["Søren Sorensen", "Antoine Lavoisier", "Svante Arrhenius"], "rep": "Søren Sorensen"},
        {"id": "qph2", "q": "Que signifie littéralement l'abréviation de pH introduite par Sorensen ?", "options": ["Potentiel Hydrogène", "Pression Hydrogène", "Pourcentage Hydrogène"], "rep": "Potentiel Hydrogène"},
        {"id": "qph3", "q": "Dans quel laboratoire industriel l'échelle de pH a-t-elle été développée pour la fermentation ?", "options": ["La brasserie Carlsberg", "Les usines Pasteur", "Les laboratoires Solvay"], "rep": "La brasserie Carlsberg"},
        {"id": "qph4", "q": "Comment qualifie-t-on une solution dont la valeur de pH est égale à 3,5 ?", "options": ["Acide", "Basique", "Neutre"], "rep": "Acide"},
        {"id": "qph5", "q": "Quelle formule chimique représente l'ion oxonium responsable de l'acidité ?", "options": ["H3O+", "OH-", "Cl-"], "rep": "H3O+"},
        {"id": "qph6", "q": "Quelle formule chimique représente l'ion hydroxyde responsable de la basicité ?", "options": ["OH-", "H3O+", "Na+"], "rep": "OH-"},
        {"id": "qph7", "q": "Si l'on ajoute un grand volume d'eau pure dans un acide, vers quelle valeur le pH se dirige-t-on ?", "options": ["7", "0", "14"], "rep": "7"},
        {"id": "qph8", "q": "Dans le modèle moléculaire de l'ion oxonium, que représente la boule rouge centrale ?", "options": ["L'atome d'oxygène", "L'atome d'hydrogène", "La charge positive"], "rep": "L'atome d'oxygène"},
        {"id": "qph9", "q": "Combien d'atomes d'hydrogène (boules blanches) comporte l'ion oxonium H3O+ ?", "options": ["3 atomes", "2 atomes", "1 atome"], "rep": "3 atomes"},
        {"id": "qph10", "q": "Quel opérateur mathématique est utilisé devant la concentration pour calculer le pH ?", "options": ["Le logarithme négatif (-log)", "La racine carrée", "La multiplication par 14"], "rep": "Le logarithme négatif (-log)"}
    ]

    if "ordre_quiz_tab1_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph1_sources)
        st.session_state.ordre_quiz_tab1_ph_aleatoire = questions_ph1_sources

    # 2. INITIALISATION ET DÉCLARATION FORCÉE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_ph1_clean" not in st.session_state:
        st.session_state.champs_ph1_clean = [
            ("1. Le concept historique de pH a été introduit par le chercheur ..........", ["Choisir...", "Sorensen", "Lavoisier"], "Sorensen", "ph1_t1"),
            ("2. Les initiales pH signifient le Potentiel .......... de la solution.", ["Choisir...", "Hydrogène", "Hydrate"], "Hydrogène", "ph1_t2"),
            ("3. Un milieu dont la valeur de pH est inférieure à 7 est ..........", ["Choisir...", "acide", "basique"], "acide", "ph1_t3"),
            ("4. Lorsque le pH est supérieur à 7, la solution aqueuse est ..........", ["Choisir...", "basique", "neutre"], "basique", "ph1_t4"),
            ("5. L'égalité exacte pH = 7 définit la zone de neutralité de l'..........", ["Choisir...", "eau", "acide"], "eau", "ph1_t5"),
            ("6. Diluer une solution acide fait .......... sa valeur de pH vers 7.", ["Choisir...", "augmenter", "diminuer"], "augmenter", "ph1_t6"),
            ("7. L'ion oxonium H3O+ caractérise chimiquement l'..........", ["Choisir...", "acidité", "basicité"], "acidité", "ph1_t7"),
            ("8. L'atome d'oxygène de l'ion oxonium est modélisé par une boule ..........", ["Choisir...", "rouge", "blanche"], "rouge", "ph1_t8"),
            ("9. Les trois hydrogènes sont représentés par des boules ..........", ["Choisir...", "blanches", "noires"], "blanches", "ph1_t9"),
            ("10. Le calcul du pH repose sur l'utilisation mathématique du ..........", ["Choisir...", "logarithme", "calibre"], "logarithme", "ph1_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Historique et Conceptuel (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at1_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse de l'Atelier 1 (Texte à trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph1_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph1_clean", disabled=verrouille, label_visibility="collapsed")
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
    st.header("Définition du pH")
    
    # --- FOCUS HISTORIQUE : SØREN SORENSEN ---
    st.subheader("Histoire des Sciences : L'invention du pH")
    st.write(
        "La notion de pH a été inventée en 1909 par le chimiste danois Søren Sorensen "
        "alors qu'il dirigeait les laboratoires de la célèbre brasserie Carlsberg à Copenhague.\n\n"
        "Cherchant un moyen précis de contrôler la fermentation de la bière et la qualité des protéines, "
        "il a eu l'idée de mesurer la concentration des ions hydrogène en solution. "
        "Il a introduit le terme de pH, qui signifie Potentiel Hydrogène.\n\n"
        "Quelques années plus tard, en 1924, la formule moderne et définitive du pH a été formalisée "
        "en fonction de la concentration en ions oxonium [H3O+] exprimée en moles par litre :\n\n"
        "**pH = -log [H3O+]**"
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET DÉFINITION ---
    st.subheader("L'Échelle de pH")
    st.write(
        "Le pH permet de connaître l’acidité d’une solution, il varie entre 0 et 14. "
        "Si le **0 <= pH < 7**, la solution est **acide**. Si le **pH = 7** la solution est **neutre**. "
        "Si **7 < pH <= 14** la solution est **basique**.\n\n"
        "Plus on dilue une solution plus le pH se rapproche de 7.\n\n"
        "Les ions responsables de l’acidité sont les **ions oxonium** (H+ ou H3O+).\n"
        "Les ions responsables de la basicité sont les **ions hydroxyde** (OH-)."
    )
    
    col_ph1, col_ph2 = st.columns(2)
    with col_ph1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre l'échelle de pH, on peut imaginer une caricature représentant une balance chimique. "
            "Dans le camp de l'acidité (pH de 0 à 6), les petits personnages Oxonium (H3O+) sont ultra-majoritaires "
            "et font pencher la balance. Dans le camp de la basicité (pH de 8 à 14), ce sont les personnages Hydroxyde (OH-) "
            "qui dominent le terrain. À la neutralité exacte (pH = 7), c'est une zone de paix parfaite où il y a "
            "autant d'Oxoniums que d'Hydroxydes, formant de l'eau pure."
        )
        try:
            st.image("caricature_ph.jpg", caption="Caricature de la balance entre acidité, neutralité et basicité")
        except Exception:
            st.warning("L'image 'caricature_ph.jpg' est introuvable.")

    with col_ph2:
        st.write("**Le schéma scientifique et la loi**")
        st.write(
            "Sur un schéma normalisé, l'échelle de pH s'organise le long d'une frise de couleurs allant du rouge vif "
            "pour les acides forts, au vert pour les milieux neutres, jusqu'au violet foncé pour les bases fortes.\n\n"
            "La dilution d'une solution acide augmente son pH pour le rapprocher de 7, tandis que la dilution "
            "d'une solution basique diminue son pH pour le rapprocher également de 7. Diluer revient à calmer "
            "l'agressivité chimique en tendant vers la neutralité de l'eau."
        )
        try:
            st.image("echelle_ph.jpg", caption="Échelle scientifique normalisée du pH de 0 à 14")
        except Exception:
            st.warning("L'image 'echelle_ph.jpg' est introuvable.")
            
    st.divider()
    
    # --- FOCUS STRUCTURE MOLÉCULAIRE : L'ION OXONIUM ---
    st.subheader("Structure microscopique : L'ion oxonium H3O+")
    st.write(
        "L'ion oxonium, responsable de l'acidité, est une molécule d'eau (H2O) qui a capturé un ion hydrogène (H+) "
        "supplémentaire. Voici sa modélisation moléculaire tridimensionnelle :"
    )
    
    col_mol1, col_mol2 = st.columns([0.4, 0.6])
    with col_mol1:
        st.markdown("**Données et Légendes Atomiques**")
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1: 
            st.caption("**Hydrogène (H)**\n\nSphère blanche\nM(H) = 1 g/mol")
        with col_leg2: 
            st.caption("**Oxygène (O)**\n\nSphère rouge\nM(O) = 16 g/mol")
            
        st.write(
            "**Formule chimique brute : H3O+**\n\n"
            "L'atome d'oxygène central établit trois liaisons de type covalente simple "
            "avec trois atomes d'hydrogène répartis de façon trigonale pyramidale. "
            "Le signe plus en haut à droite indique une perte globale d'un électron."
        )

    with col_mol2:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        fig_mol, ax_mol = plt.subplots(figsize=(5, 4), facecolor="white")
        ax_mol.set_facecolor("white")
        
        # Coordonnees geometriques de la pyramide trigonale projetee a plat (Centree sur l'Oxygene)
        c_oxygene = np.array([4.0, 2.5])
        h1_ox = np.array([2.6, 2.5])      # Branche gauche
        h2_ox = np.array([4.7, 3.7])      # Branche haut droite
        h3_ox = np.array([4.7, 1.3])      # Branche bas droite

        # Fonction de tracé des liaisons covalentes
        def tracer_liaison_ph(p1, p2):
            ax_mol.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#333333", linewidth=3, zorder=1)

        # Tracé des 3 liaisons covalentes simples O-H
        tracer_liaison_ph(c_oxygene, h1_ox)
        tracer_liaison_ph(c_oxygene, h2_ox)
        tracer_liaison_ph(c_oxygene, h3_ox)

        # Fonction de tracé des atomes spheriques
        def tracer_atome_ph(p, symbole):
            if symbole == 'O': 
                couleur, texte_couleur = "#e74c3c", "white" # Rouge pour l'Oxygene
            elif symbole == 'H': 
                couleur, texte_couleur = "#ecf0f1", "black" # Blanc/Gris pour l'Hydrogene
            else: 
                couleur, texte_couleur = "#95a5a6", "black"
            
            ax_mol.add_patch(patches.Circle((p[0], p[1]), 0.25, facecolor=couleur, edgecolor="#1a252f", linewidth=2, zorder=2))
            ax_mol.text(p[0], p[1], symbole, color=texte_couleur, weight="bold", fontsize=11, ha="center", va="center", zorder=3)

        # Rendu des atomes
        tracer_atome_ph(c_oxygene, 'O')
        tracer_atome_ph(h1_ox, 'H')
        tracer_atome_ph(h2_ox, 'H')
        tracer_atome_ph(h3_ox, 'H')

        # Ajout du signe de charge positive globale de l'ion en haut a droite
        ax_mol.text(5.5, 3.8, "+", color="#e74c3c", weight="bold", fontsize=20, ha="center", va="center")

        # Configuration des limites du plan de vue moleculaire
        ax_mol.set_xlim(2.0, 6.0)
        ax_mol.set_ylim(0.8, 4.2)
        ax_mol.axis("off")
        
        # Injection du rendu Matplotlib natif dans Streamlit
        st.pyplot(fig_mol)

    if "suite_verrouille_tab1_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab1_ph = False
    verrou_at1 = st.session_state.suite_verrouille_tab1_ph

    afficher_atelier_definition_ph(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    
    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Définition du pH.",
        key="check_certif_ph1_final_net",
        disabled=verrou_at1,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_ph_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_ph_aleatoire:
                    reponse_eleve = st.session_state.get(f"ph_at1_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = 0.0
            if "champs_ph1_clean" in st.session_state:
                for ligne in st.session_state.champs_ph1_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph1_clean", "Choisir...") == attendu:
                        score_t1 += 1.0

            st.session_state.score_suite1_ph_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_ph_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1_ph = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 1 ---
    if st.session_state.get("suite_verrouille_tab1_ph", False):
        scr1_t1 = st.session_state.get("score_suite1_ph_p1", 0.0)
        scr2_t1 = st.session_state.get("score_suite1_ph_p2", 0.0)
        tot_s_t1 = st.session_state.get("score_final_suite1_ph", 0.0)
        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        # AJOUTEZ IMPÉRATIVEMENT CES TROIS LIGNES ICI POUR FIXER LE CRASH :
        p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
        n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
        c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

        st.success(f"ATELIER DÉFINITION PH SCELLÉ | Note de session : {tot_s_t1:.1f} / 20")

        html_export_ph1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Définition pH - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Sciences Physiques</h1>
                <p>Atelier 1 : Echelle de pH, acidite, basicite, structures moleculaires et histoire</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t1:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #be123c;">
                Note obtenue au Quiz de Cours : <strong>{scr1_t1:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2_t1:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s_t1:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz
        if "ordre_quiz_tab1_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at1_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph1 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Transition vers le second tableau pour le texte à trous de l'Atelier 1
        html_export_ph1 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction de la synthèse de texte
        if "champs_ph1_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph1_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph1_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                
                html_export_ph1 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture du rapport HTML de l'Atelier 1
        html_export_ph1 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph1 = preparer_nom_fichier("Rapport_Definition_pH").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 1 (.html)",
            data=html_export_ph1,
            file_name=nom_fichier_html_ph1,
            mime="text/html",
            use_container_width=True
        )



















                
