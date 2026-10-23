
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
        for ligne in st.session_state.champs_hydro1_clean:
            enonce = ligne
            choix = ligne
            cle = ligne[-1]
            
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
    st.subheader("Simulateur dynamique de roue hydraulique romaine")
    st.write(
        "Modifiez le curseur ci-dessous pour changer le débit de l'eau de la rivière (en litres par seconde). "
        "Le graphique Matplotlib recalculera la vitesse de rotation de la roue à aubes et la puissance mécanique récupérée."
    )
    
    debit_riviere = st.slider("Ajuster le débit de la rivière (L/s) :", min_value=0, max_value=200, value=80, step=20, key="slider_debit_h1")
    
    col_graph, col_bd = st.columns([0.55, 0.45])
    
    with col_graph:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        # Calcul de la vitesse angulaire fictive (proportionnelle au débit)
        vitesse_rotation = debit_riviere * 0.15
        puissance_recoltee = debit_riviere * 9.81 * 2.0 * 0.7  # Formule simplifiée P = rho * q * g * h * rendement
        
        fig, ax = plt.subplots(figsize=(5, 3.8), facecolor="white")
        ax.set_facecolor("white")
        
        # Dessin du canal d'eau (fond bleu clair si débit > 0)
        if debit_riviere > 0:
            ax.add_patch(patches.Rectangle((0, 0), 5, 0.8, facecolor="#38bdf8", alpha=0.5))
            
        # Dessin de la roue (centre fixe à x=2.5, y=1.5, rayon=1.0)
        ax.add_patch(patches.Circle((2.5, 1.5), 1.0, facecolor="none", edgecolor="#1e293b", linewidth=3))
        ax.add_patch(patches.Circle((2.5, 1.5), 0.15, facecolor="#475569"))
        
        # Dessin des aubes (rayons) de la roue hydraulique
        nb_aubes = 8
        for a in range(nb_aubes):
            angle_rad = np.radians(a * (360 / nb_aubes) + (debit_riviere * 0.5))  # Rotation simulée
            x_aube = 2.5 + 1.2 * np.cos(angle_rad)
            y_aube = 1.5 + 1.2 * np.sin(angle_rad)
            ax.plot([2.5, x_aube], [1.5, y_aube], color="#475569", linewidth=2)
            
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 3)
        ax.axis("off")
        st.pyplot(fig)
        st.caption(f"Rendu : Roue en mouvement | Vitesse estimée : {vitesse_rotation:.1f} tr/min | Puissance : {puissance_recoltee:.0f} Watts")

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
                .header-box {{ background-color: #0f172a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
















