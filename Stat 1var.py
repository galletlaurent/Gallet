# -*- coding: utf-8 -*-

import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application de statistiques à une variable",
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
st.title("Application de Probabilités")
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)

# =============================================================================
# INITIALISATION SECURISEE DU SESSION STATE (A l'ouverture de l'application)
# =============================================================================
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
if "date_heure" not in st.session_state:
    st.session_state.date_heure = datetime.now().strftime("%d/%m/%Y %H:%M")
if "roulette_dernier_numero" not in st.session_state:
    st.session_state.roulette_dernier_numero = 0


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
    "1. Le diagramme bâton",
    "2. le diagramme circulaire",
    "3. le graphique",
    "4. le diagramme à moustache",
    "5. l'histogramme",
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]



def calculer_et_tracer_batons_matplotlib(df_donnees):
    """Calcule les indicateurs statistiques ponderes et genere le diagramme en batons.
    Version vectorielle synchrone pour Streamlit.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    # Initialisation des textes par defaut en cas de tableau vide ou incomplet
    stats_text = "Saisissez des valeurs numeriques dans le tableau pour lancer les calculs."
    
    # Nettoyage et filtrage des lignes incompletes du tableau d'edition
    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].get("", "") != "") & (df_filtre["Effectif (ni)"].get("", "") != "")]

    if not df_filtre.empty:
        try:
            # Extraction et conversion numerique des donnees
            nums = df_filtre["Caractere (xi)"].astype(float).to_numpy()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()

            # Reconstruction de la serie brute repete pour la mediane et les quartiles
            weighted = np.repeat(nums, effs.astype(int))

            # Calculs des indicateurs statistiques ponderes (Formules d'origines)
            moy = np.average(nums, weights=effs)
            std = np.sqrt(np.average((nums - moy)**2, weights=effs))
            med = np.median(weighted)
            q1, q3 = np.percentile(weighted, [25, 75])

            stats_text = (
                f"Moyenne : {moy:.2f}\n"
                f"Ecart-type : {std:.2f}\n"
                f"Mediane : {med:.2f}\n"
                f"Premier Quartile Q1 : {q1:.2f} | Troisieme Quartile Q3 : {q3:.2f}"
            )

            # Trace du diagramme en batons Matplotlib (Equivalent de self.ax1.bar)
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            
        except Exception:
            # Gestion du cas des caracteres textuels (Qualitatifs)
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            stats_text = "Statistiques (Moyenne, Mediane, Q1/Q3) indisponibles pour caracteres qualitatifs / textuels."

    # Habillage cosmetique sombre de la figure
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Caractere (xi)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("Effectif (ni)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Diagramme en batons de la serie", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats1_affichage_texte = stats_text
    return fig


with tab1:
    st.header("Atelier 1 : Analyse Statistique & Diagramme en Batons")
    
    # Initialisation du nombre de lignes de saisie en memoire
    if "nbr_lignes_tab1" not in st.session_state: 
        st.session_state.nbr_lignes_tab1 = 5

    # =========================================================================
    # ARCHITECTURE EN COLONNES : GRILLE DE SAISIE / GRAPHIQUE SYNCHRONE
    # =========================================================================
    col_g_tableau, col_d_graphique = st.columns([1.2, 1.8])

    # --- PANNEAU DE GAUCHE : TABLEAU DE SAISIE ET BOUTONS ---
    with col_g_tableau:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES DONNÉES STATISTIQUES</p>", unsafe_allow_html=True)
            
            # Saisie dynamique du nombre de lignes
            st.number_input("Nombre de valeurs differentes (lignes) :", min_value=1, max_value=50, value=5, step=1, key="nbr_lignes_tab1")
            
            # Construction du DataFrame d'accueil
            import pandas as pd
            if "df_session_tab1" not in st.session_state or len(st.session_state.df_session_tab1) != st.session_state.nbr_lignes_tab1:
                st.session_state.df_session_tab1 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab1,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab1
                })

            # Editeur de donnees interactif réactif
            df_edite = st.data_editor(
                st.session_state.df_session_tab1, 
                use_container_width=True, 
                hide_index=True,
                key="editeur_grille_tab1"
            )
            
            # Sauvegarde immediate des valeurs saisies
            st.session_state.df_session_tab1 = df_edite

            # Bouton de reinitialisation
            if st.button("Reinitialiser la grille", key="btn_reset_tab1", use_container_width=True):
                st.session_state.df_session_tab1 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab1,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab1
                })
                st.rerun()

        # CONSOLE DES STATISTIQUES DESCRIPTIVES
        with st.container(border=True):
            st.markdown("**Console d'analyse descriptive :**")
            st.text(st.session_state.get("stats1_affichage_texte", "En attente de saisies..."))

    # --- PANNEAU DE DROITE : LE DIAGRAMME EN BÂTONS EN DIRECT ---
    with col_d_graphique:
        st.subheader("Rendu graphique de la distribution")
            
            # Execution du moteur de calcul et tracé Matplotlib
            fig_batons = calculer_et_tracer_batons_matplotlib(st.session_state.df_session_tab1)
            st.pyplot(fig_batons, use_container_width=True)
            
            # Execution synchrone du moteur graphique avec le DataFrame edite
            fig_batons = calculer_et_tracer_batons_matplotlib(st.session_state.df_session_tab1)
            st.pyplot(fig_batons, use_container_width=True)e)
            q1, q3 = np.percentile(weighted, [25, 75])

            stats_text = (
                f"Moyenne : {moy:.2f}\n"
                f"Ecart-type : {std:.2f}\n"
                f"Mediane : {med:.2f}\n"
                f"Premier Quartile Q1 : {q1:.2f} | Troisieme Quartile Q3 : {q3:.2f}"
            )

            # Trace du diagramme en batons Matplotlib
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            
        except Exception:
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            stats_text = "Statistiques (Moyenne, Mediane, Q1/Q3) indisponibles pour caracteres qualitatifs / textuels."

    # Habillage cosmetique sombre de la figure
    ax.spines['bottom'].set_color('#94a3b8')
    ax.spines['left'].set_color('#94a3b8')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#94a3b8', labelsize=8)
    ax.set_xlabel("Caractere (xi)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_ylabel("Effectif (ni)", color="#cbd5e1", fontsize=9, fontweight="bold")
    ax.set_title("Diagramme en batons de la serie", color="#38bdf8", fontsize=9, fontweight="bold")

    st.session_state.stats1_affichage_texte = stats_text
    return fig

    # =========================================================================
    # SYSTEME DE QUESTIONNAIRE D'EVALUATION - ATELIER 1 (10 POINTS)
    # =========================================================================
    st.write("---")
    col_g_q1, col_d_q1 = st.columns(2)

    with col_g_q1:
        st.markdown("##### Quiz de connaissances : Le diagramme en batons (10 pts)")
        if "ordre_questions_stat1" not in st.session_state:
            questions_s1_base = [
                ("q1", "Dans un diagramme en batons, la hauteur de chaque baton est proportionnelle a :"),
                ("q2", "La moyenne d'une serie statistique ponderee se calcule en divisant la somme des produits xi*ni par :"),
                ("q3", "La mediane divise la population etudiee en combien de parts egales :"),
                ("q4", "L'ecart-type mesure la dispersion des valeurs de la serie autour de :")
            ]
            import random
            random.shuffle(questions_s1_base)
            st.session_state.ordre_questions_stat1 = questions_s1_base

        dict_quiz_s1 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_stat1, 1):
            cle_qs1 = f"col_g_quiz_stat1_{q_id}"
            cle_opts_unique = f"opts_stat1_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q1": copie_opts = ["L'effectif ni de la valeur", "La valeur du caractere xi", "L'etendue totale"]
                elif q_id == "q2": copie_opts = ["L'effectif total N", "Le nombre de colonnes", "La valeur maximale"]
                elif q_id == "q3": copie_opts = ["Deux parts egales (50% au-dessus, 50% en dessous)", "Quatre parts", "Dix parts"]
                elif q_id == "q4": copie_opts = ["La moyenne", "La mediane", "La valeur minimale"]
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            val_p = st.session_state.get(cle_qs1, "Choisir...")
            idx = st.session_state[cle_opts_unique].index(val_p) if val_p in st.session_state[cle_opts_unique] else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_s1[f"{q_id}_stat1"] = st.selectbox("", st.session_state[cle_opts_unique], index=idx, key=cle_qs1, disabled=st.session_state.get("stat1_verrouille", False), label_visibility="collapsed")

    with col_d_q1:
        st.markdown("##### Synthese de cours (Texte a trous - 10 pts)")
        
        co1_1, co1_2 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_1: st.write("Le diagramme en batons est utilise pour representer une variable quantitative")
        with co1_2: t1 = st.selectbox("", ["Choisir...", "Discrete", "Continue", "Qualitative"], key="stat1_t1", disabled=st.session_state.get("stat1_verrouille", False), label_visibility="collapsed")
        
        co1_3, co1_4 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_3: st.write("Le premier quartile Q1 correspond a au moins 25% de l'effectif")
        with co1_4: t2 = st.selectbox("", ["Choisir...", "Cumule", "Relatif", "Marginal"], key="stat1_t2", disabled=st.session_state.get("stat1_verrouille", False), label_visibility="collapsed")

        co1_5, co1_6 = st.columns([0.75, 0.25], vertical_alignment="bottom")
        with co1_5: st.write("La difference entre la valeur maximale et minimale s'appelle l'")
        with co1_6: t3 = st.selectbox("", ["Choisir...", "Etendue", "Ecart-type", "Variance"], key="stat1_t3", disabled=st.session_state.get("stat1_verrouille", False), label_visibility="collapsed")

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION DU BILAN HTML
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    if "stat1_verrouille" not in st.session_state:
        st.session_state.stat1_verrouille = False

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de l'Atelier 1.", 
        key="check_certif_stat1_officiel_20pts", 
        disabled=st.session_state.stat1_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_stat1_official_20pts", use_container_width=True, disabled=st.session_state.stat1_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            attendus_qs1_v = {
                "q1": "L'effectif ni de la valeur", "q2": "L'effectif total N", 
                "q3": "Deux parts egales (50% au-dessus, 50% en dessous)", "q4": "La moyenne"
            }
            score_quiz_stat1 = sum([2.5 for qk, qv in attendus_qs1_v.items() if st.session_state.get(f"col_g_quiz_stat1_{qk}") == qv])

            score_trous_stat1 = 0.0
            if st.session_state.get("stat1_t1") == "Discrete": score_trous_stat1 += 3.33
            if st.session_state.get("stat1_t2") == "Cumule": score_trous_stat1 += 3.33
            if st.session_state.get("stat1_t3") == "Etendue": score_trous_stat1 += 3.34

            st.session_state.score_stat1_p1 = round(score_quiz_stat1, 1)
            st.session_state.score_stat1_p2 = round(min(10.0, score_trous_stat1), 1)
            st.session_state.score_final_stat1 = round(score_quiz_stat1 + min(10.0, score_trous_stat1), 1)
            st.session_state.stat1_verrouille = True
            st.rerun()

    if st.session_state.stat1_verrouille:
        scr1 = st.session_state.get("score_stat1_p1", 0.0)
        scr2 = st.session_state.get("score_stat1_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat1", 0.0)

        from datetime import datetime, timedelta
        timestamp_stat1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 1 SCELLE | Note de session : {tot_s} / 20")

        attendus_qs1_v = {
            "q1": "L'effectif ni de la valeur", "q2": "L'effectif total N", 
            "q3": "Deux parts egales (50% au-dessus, 50% en dessous)", "q4": "La moyenne"
        }
        attendus_ts1_v = {"t1": "Discrete", "t2": "Cumule", "t3": "Etendue"}

        html_export_stat1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; position: relative; }}
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de competences - Statistiques 1</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05); margin-bottom: 25px;">
                &bull; Partie 1 : Quiz de Connaissances (4 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de Cours (Texte a trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : QUIZ DE STATISTIQUES (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_q, (q_id, q_txt) in enumerate(attendus_qs1_v.items(), 1):
            saisie = st.session_state.get(f"col_g_quiz_stat1_{q_id}", "Choisir...")
            attendu = attendus_qs1_v[q_id]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat1 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : SYNTHESE DE COURS (TEXTE A TROUS - 10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">N°</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for idx_t, (t_key, t_val) in enumerate(attendus_ts1_v.items(), 1):
            saisie = st.session_state.get(f"stat1_{t_key}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(t_val) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat1 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{t_val}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Statistiques1_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 1 SUR VOTRE ORDINATEUR",
            data=html_export_stat1,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
            )



