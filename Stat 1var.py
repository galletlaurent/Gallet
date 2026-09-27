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
st.title("Application statistiques à une variable")
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

def afficher_questions_statistiques2_dynamiques(df_donnees, verrouille=False):
    import numpy as np
    
    # Securite absolue contre le NameError au demarrage
    if "df_session_tab2" not in st.session_state:
        return {}, {}
        
    v_total_n = st.session_state.get("circ_vrai_total_n", 10.0)
    v_max_fr = st.session_state.get("circ_max_freq", 40.0)
    v_min_fr = st.session_state.get("circ_min_freq", 10.0)
    v_labels = st.session_state.get("circ_labels_presents", ["A", "B"])
    v_label_premier = v_labels[0] if len(v_labels) > 0 else "Aucun"

    col_double_quiz_dyn2, col_double_trous_dyn2 = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DIVERSIFIÉ DE 10 QUESTIONS ---
    with col_double_quiz_dyn2:
        st.markdown("##### Quiz sur VOTRE repartition circulaire (10 questions - 10 pts)")
        
        if "ordre_quiz_dyn_s2" not in st.session_state:
            st.session_state.ordre_quiz_dyn_s2 = [f"q{i}" for i in range(1, 11)]

        dict_reponses_quiz = {}
        
        for num_idx, q_id in enumerate(st.session_state.ordre_quiz_dyn_s2, 1):
            cle_select = f"col_g_quiz_dyn_s2_{q_id}"
            
            if q_id == "q1":
                q_txt = "L'effectif total N de votre serie de donnees s'eleve a :"
                opts = [f"{v_total_n:.0f}", f"{v_total_n + 5:.0f}", "100"]
            elif q_id == "q2":
                q_txt = "La frequence maximale calculee au sein de votre distribution vaut :"
                opts = [f"{v_max_fr:.1f}%", f"{v_max_fr + 5.5:.1f}%", "50.0%"]
            elif q_id == "q3":
                q_txt = "La frequence minimale calculee au sein de votre distribution vaut :"
                opts = [f"{v_min_fr:.1f}%", f"{v_min_fr - 2.5:.1f}%", "0.0%"]
            elif q_id == "q4":
                q_txt = "Quel est le nom du premier caractere (xi) renseigne dans votre grille ?"
                opts = [f"{v_label_premier}", "Total", "Inconnu"]
            elif q_id == "q5":
                q_txt = "Pour convertir une frequence (f) en angle de secteur circulaire, on multiplie la frequence par :"
                opts = ["3.6 (car 360° / 100%)", "360", "1.0"]
            elif q_id == "q6":
                q_txt = "La somme des angles de tous les secteurs d'un diagramme circulaire complet vaut :"
                opts = ["360 degres", "100 degres", "180 degres"]
            elif q_id == "q7":
                q_txt = "La somme de toutes les frequences calculees doit obligatoirement totaliser :"
                opts = ["100%", "360%", "L'effectif global N"]
            elif q_id == "q8":
                q_txt = "Si une part du diagramme circulaire represente pile un quart du gâteau, son angle vaut :"
                opts = ["90 degres", "25 degres", "45 degres"]
            elif q_id == "q9":
                q_txt = "Le gâteau ou le diagramme circulaire complet est ideal pour representer graphiquement :"
                opts = ["Des structures de repartition (parts de marche, budgets)", "Des evolutions temporelles", "Des fonctions continues"]
            elif q_id == "q10":
                q_txt = "Le rapport de l'effectif d'une modalite ni sur l'effectif total N definit sa :"
                opts = ["Frequence", "Amplitude", "Moyenne"]

            cle_opts_shuffle = f"opts_shuffled_dyn_s2_{q_id}"
            if cle_opts_shuffle not in st.session_state:
                v_correcte = opts[0]
                import random
                copie_opts = list(opts)
                random.shuffle(copie_opts)
                st.session_state[cle_opts_shuffle] = ["Choisir..."] + copie_opts
                st.session_state[f"correct_ans_dyn_s2_{q_id}"] = v_correcte

            val_p = st.session_state.get(cle_select, "Choisir...")
            idx = st.session_state[cle_opts_shuffle].index(val_p) if val_p in st.session_state[cle_opts_shuffle] else 0
            
            st.write(f"**{num_idx}.** {q_txt}")
            dict_reponses_quiz[f"{q_id}_stat2"] = st.selectbox("", st.session_state[cle_opts_shuffle], index=idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE 10 CASES COMPACTES ---
    with col_double_trous_dyn2:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: _ = st.write("1. Le diagramme circulaire decoupe un gâteau en plusieurs")
        with c2: t1 = st.selectbox("", ["Choisir...", "Secteurs", "Batons", "Classes"], key="st2_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: _ = st.write("2. La surface de chaque secteur est proportionnelle a l'")
        with c4: t2 = st.selectbox("", ["Choisir...", "Effectif ni", "Caractere xi"], key="st2_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: _ = st.write("3. La totalite du disque verifie un angle geometrique de")
        with c6: t3 = st.selectbox("", ["Choisir...", "360°", "100°", "180°"], key="st2_t3", disabled=verrouille, label_visibility="collapsed")

        c4_1, c4_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c4_1: _ = st.write("4. Un demi-disque represente une frequence relative de")
        with c4_2: t4 = st.selectbox("", ["Choisir...", "50%", "25%", "100%"], key="st2_t4", disabled=verrouille, label_visibility="collapsed")

        c5_1, c5_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5_1: _ = st.write("5. Le calcul ni/N multiplie par 100 s'appelle la")
        with c5_2: t5 = st.selectbox("", ["Choisir...", "Frequence", "Amplitude"], key="st2_t5", disabled=verrouille, label_visibility="collapsed")

        c6_1, c6_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c6_1: _ = st.write("6. L'unite de mesure des angles de l'atelier s'exprime en")
        with c6_2: t6 = st.selectbox("", ["Choisir...", "Degres", "Radians", "Pourcentages"], key="st2_t6", disabled=verrouille, label_visibility="collapsed")

        c7_1, c7_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7_1: _ = st.write("7. La somme de toutes les parts du gâteau équivaut a")
        with c7_2: t7 = st.selectbox("", ["Choisir...", "100%", "50%", "360%"], key="st2_t7", disabled=verrouille, label_visibility="collapsed")

        c8_1, c8_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c8_1: _ = st.write("8. Le diagramme circulaire met en valeur la structure de")
        with c8_2: t8 = st.selectbox("", ["Choisir...", "Repartition", "Dispersion"], key="st2_t8", disabled=verrouille, label_visibility="collapsed")

        c9_1, c9_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9_1: _ = st.write("9. Le coefficient de proportionnalite pour l'angle vaut f multiplied by")
        with c9_2: t9 = st.selectbox("", ["Choisir...", "3.6", "360", "0.25"], key="st2_t9", disabled=verrouille, label_visibility="collapsed")

        c10_1, c10_2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c10_1: _ = st.write("10. Cet outil graphique traite aussi les variables qualitatives ou")
        with c10_2: t10 = st.selectbox("", ["Choisir...", "Textuelles", "Continues"], key="st2_t10", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6, "t7": t7, "t8": t8, "t9": t9, "t10": t10
        }
        
def afficher_questions_statistiques_dynamiques(df_donnees, verrouille=False):
    import numpy as np
    import pandas as pd

    # 1. MOTEUR DE PRE-CALCULS DES VALEURS DU TABLEAU POUR LES QUESTIONS
    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    # Valeurs de secours par defaut si le tableau est vide
    v_eff_total = 10
    v_moyenne = 10.0
    v_mediane = 10.0
    v_etendue = 5.0
    v_max_xi = 12.0
    v_min_xi = 7.0

    if not df_filtre.empty:
        try:
            nums = df_filtre["Caractere (xi)"].astype(float).to_numpy()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            weighted = np.repeat(nums, effs.astype(int))
            
            if len(weighted) > 0:
                v_eff_total = int(np.sum(effs))
                v_moyenne = round(float(np.average(nums, weights=effs)), 2)
                v_mediane = round(float(np.median(weighted)), 2)
                v_min_xi = round(float(np.min(nums)), 2)
                v_max_xi = round(float(np.max(nums)), 2)
                v_etendue = round(float(v_max_xi - v_min_xi), 2)
        except:
            pass

    col_double_quiz_dyn, col_double_trous_dyn = st.columns(2)

    # --- COLONNE DE GAUCHE : LE QUIZ DYNAMIQUE DE 10 QUESTIONS ---
    with col_double_quiz_dyn:
        st.markdown(f"##### Quiz sur VOTRE serie de donnees (10 questions - 10 pts)")
        
        # Initialisation fixe de l'ordre pour eviter le melange au clic
        if "ordre_quiz_dyn_s1" not in st.session_state:
            st.session_state.ordre_quiz_dyn_s1 = [f"q{i}" for i in range(1, 11)]

        dict_reponses_quiz = {}
        
        for num_idx, q_id in enumerate(st.session_state.ordre_quiz_dyn_s1, 1):
            cle_select = f"col_g_quiz_dyn_s1_{q_id}"
            
            # Generation des questions et des options selon les donnees reelles du tableau
            if q_id == "q1":
                q_txt = f"Quelle est la valeur exacte de l'effectif total (N) de votre serie ?"
                opts = [f"{v_eff_total}", f"{v_eff_total + 2}", f"{v_eff_total * 2}"]
            elif q_id == "q2":
                q_txt = f"La valeur calculee de la moyenne ponderee de votre serie vaut :"
                opts = [f"{v_moyenne}", f"{v_moyenne + 1.50:.2f}", f"{v_moyenne - 0.75:.2f}"]
            elif q_id == "q3":
                q_txt = f"La valeur centrale de la mediane de votre distribution est :"
                opts = [f"{v_mediane}", f"{v_mediane + 2.00:.2f}", f"{v_mediane / 2.00:.2f}"]
            elif q_id == "q4":
                q_txt = f"L'etendue totale de votre serie (Valeur max - Valeur min) vaut :"
                opts = [f"{v_etendue}", f"{v_etendue + 4.00:.2f}", "10.00"]
            elif q_id == "q5":
                q_txt = f"Quelle est la plus petite valeur du caractere (xi min) saisie ?"
                opts = [f"{v_min_xi}", f"{v_min_xi - 1.00:.2f}", "0.00"]
            elif q_id == "q6":
                q_txt = f"Quelle est la plus grande valeur du caractere (xi max) saisie ?"
                opts = [f"{v_max_xi}", f"{v_max_xi + 3.50:.2f}", f"{v_max_xi * 1.5:.2f}"]
            elif q_id == "q7":
                q_txt = f"Dans un diagramme en batons, l'axe vertical (ordonnees) represente :"
                opts = ["Les effectifs (ni)", "Les caracteres (xi)", "Les angles en degres"]
            elif q_id == "q8":
                q_txt = f"Dans un diagramme en batons, l'axe horizontal (abscisses) represente :"
                opts = ["Les caracteres (xi)", "Les effectifs (ni)", "Les frequences en %"]
            elif q_id == "q9":
                q_txt = f"La somme de toutes les frequences calculees d'une serie doit toujours valoir :"
                opts = ["100% (ou 1)", "50%", "L'effectif total N"]
            elif q_id == "q10":
                q_txt = f"Si l'on multiplie tous les effectifs par 2, la moyenne de la serie :"
                opts = ["Reste strictement inchangee", "Est multipliee par 2", "Est divisee par 2"]

            # Securisation des choix uniques melanges une seule fois
            cle_opts_shuffle = f"opts_shuffled_dyn_s1_{q_id}"
            if cle_opts_shuffle not in st.session_state:
                v_correcte = opts[0]
                import random
                copie_opts = list(opts)
                random.shuffle(copie_opts)
                st.session_state[cle_opts_shuffle] = ["Choisir..."] + copie_opts
                st.session_state[f"correct_ans_dyn_s1_{q_id}"] = v_correcte

            val_p = st.session_state.get(cle_select, "Choisir...")
            idx = st.session_state[cle_opts_shuffle].index(val_p) if val_p in st.session_state[cle_opts_shuffle] else 0
            
            st.write(f"**{num_idx}.** {q_txt}")
            dict_reponses_quiz[f"{q_id}_stat1"] = st.selectbox("", st.session_state[cle_opts_shuffle], index=idx, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS DE 10 CASES COMPACTES ---
    with col_double_trous_opt1 if 'col_double_trous_opt1' in locals() else col_double_trous_dyn:
        st.markdown("##### Synthese de cours (Texte a trous - 10 cases - 10 pts)")
        
        # Structuration de 10 lignes descriptives compactes
        c1, c2 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c1: st.write("1. Le diagramme en batons modelise une variable")
        with c2: t1 = st.selectbox("", ["Choisir...", "Discrete", "Continue"], key="st1_t1", disabled=verrouille, label_visibility="collapsed")

        c3, c4 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c3: st.write("2. La somme des produits xi*ni divisee par N donne la")
        with c4: t2 = st.selectbox("", ["Choisir...", "Moyenne", "Mediane"], key="st1_t2", disabled=verrouille, label_visibility="collapsed")

        c5, c6 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c5: st.write("3. La valeur partageant la serie en deux blocs de 50% est la")
        with c6: t3 = st.selectbox("", ["Choisir...", "Mediane", "Moyenne"], key="st1_t3", disabled=verrouille, label_visibility="collapsed")

        c7, c8 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c7: st.write("4. L'indicateur de dispersion associe a la moyenne est l'")
        with c8: t4 = st.selectbox("", ["Choisir...", "Ecart-type", "Etendue"], key="st1_t4", disabled=verrouille, label_visibility="collapsed")

        c9, c10 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c9: st.write("5. Le premier quartile Q1 correspond a au moins")
        with c10: t5 = st.selectbox("", ["Choisir...", "25%", "50%", "75%"], key="st1_t5", disabled=verrouille, label_visibility="collapsed")

        c11, c12 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c11: st.write("6. Le troisieme quartile Q3 correspond a au moins")
        with c12: t6 = st.selectbox("", ["Choisir...", "75%", "25%", "100%"], key="st1_t6", disabled=verrouille, label_visibility="collapsed")

        c13, c14 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c13: st.write("7. La difference entre la valeur max et min est l'")
        with c14: t7 = st.selectbox("", ["Choisir...", "Etendue", "Variance"], key="st1_t7", disabled=verrouille, label_visibility="collapsed")

        c15, c16 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c15: st.write("8. L'effectif d'une valeur note ni represente sa")
        with c16: t8 = st.selectbox("", ["Choisir...", "Frequence", "Frequence absolue"], key="st1_t8", disabled=verrouille, label_visibility="collapsed")

        c17, c18 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c17: st.write("9. Le rapport de ni sur l'effectif global N est la")
        with c18: t9 = st.selectbox("", ["Choisir...", "Frequence", "Moyenne"], key="st1_t9", disabled=verrouille, label_visibility="collapsed")

        c19, c20 = st.columns([0.70, 0.30], vertical_alignment="bottom")
        with c19: st.write("10. Graphiquement, la hauteur du baton depend de l'")
        with c20: t10 = st.selectbox("", ["Choisir...", "Effectif ni", "Caractere xi"], key="st1_t10", disabled=verrouille, label_visibility="collapsed")

        dict_trous = {
            "t1": t1, "t2": t2, "t3": t3, "t4": t4, "t5": t5, "t6": t6, "t7": t7, "t8": t8, "t9": t9, "t10": t10
        }

    return dict_reponses_quiz, dict_trous












def calculer_et_tracer_circulaire_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs dans le tableau pour generer le diagramme circulaire."
    
    st.session_state.circ_vrai_total_n = 0.0
    st.session_state.circ_max_freq = 0.0
    st.session_state.circ_min_freq = 0.0
    st.session_state.circ_labels_presents = []

    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            total_n = np.sum(effs)

            if total_n > 0:
                freqs = (effs / total_n) * 100.0
                angles = (effs / total_n) * 360.0

                st.session_state.circ_vrai_total_n = float(total_n)
                st.session_state.circ_max_freq = round(float(np.max(freqs)), 1)
                st.session_state.circ_min_freq = round(float(np.min(freqs)), 1)
                st.session_state.circ_labels_presents = labels

                # Generation textuelle pour le panneau de resultats
                lignes_stats = [f"Effectif Total N = {total_n:.0f}"]
                for lbl, fr, ang in zip(labels, freqs, angles):
                    lignes_stats.append(f"• {lbl} : {fr:.1f}% ({ang:.1f}°)")
                stats_text = "\n".join(lignes_stats)

                # Trace du diagramme circulaire Matplotlib
                theme_sombre_colors = plt.cm.Dark2(np.linspace(0, 1, len(labels)))
                wedges, texts, autotexts = ax.pie(
                    freqs, labels=labels, autopct='%1.1f%%', 
                    startangle=90, colors=theme_sombre_colors,
                    textprops=dict(color="#cbd5e1", fontsize=8)
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontsize(8)
                    autotext.set_weight('bold')
        except Exception:
            stats_text = "Erreur de calcul. Verifiez que les effectifs saisis sont numeriques."

    st.session_state.stats2_affichage_texte = stats_text
    return fig

def calculer_et_tracer_batons_matplotlib(df_donnees):
    import numpy as np
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 3.8), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    
    stats_text = "Saisissez des valeurs numeriques dans le tableau pour lancer les calculs."
    
    # Réinitialisation des variables de calcul dynamique de session
    st.session_state.vrai_total_n = 0.0
    st.session_state.vraie_moyenne = 0.0
    st.session_state.vraie_mediane = 0.0
    st.session_state.vrai_q1 = 0.0
    st.session_state.vrai_q3 = 0.0
    st.session_state.vrai_etendue = 0.0
    
    df_filtre = df_donnees.dropna(subset=["Caractere (xi)", "Effectif (ni)"])
    df_filtre = df_filtre[(df_filtre["Caractere (xi)"].astype(str).str.strip() != "") & (df_filtre["Effectif (ni)"].astype(str).str.strip() != "")]

    if not df_filtre.empty:
        try:
            nums = df_filtre["Caractere (xi)"].astype(float).to_numpy()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()

            weighted = np.repeat(nums, effs.astype(int))

            if len(weighted) == 0:
                stats_text = "Saisissez des effectifs superieurs ou egaux a 1 pour lancer l'analyse."
            else:
                moy = np.average(nums, weights=effs)
                std = np.sqrt(np.average((nums - moy)**2, weights=effs))
                med = np.median(weighted)
                q1, q3 = np.percentile(weighted, [25, 75])
                etendue = np.max(nums) - np.min(nums)
                total_n = np.sum(effs)

                # Stockage des vraies valeurs physiques calculées
                st.session_state.vrai_total_n = float(total_n)
                st.session_state.vraie_moyenne = round(float(moy), 2)
                st.session_state.vraie_mediane = round(float(med), 2)
                st.session_state.vrai_q1 = round(float(q1), 2)
                st.session_state.vrai_q3 = round(float(q3), 2)
                st.session_state.vrai_etendue = round(float(etendue), 2)

                stats_text = (
                    f"Moyenne : {moy:.2f}\n"
                    f"Ecart-type : {std:.2f}\n"
                    f"Mediane : {med:.2f}\n"
                    f"Premier Quartile Q1 : {q1:.2f} | Troisieme Quartile Q3 : {q3:.2f}"
                )

            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            
        except Exception:
            labels = df_filtre["Caractere (xi)"].astype(str).tolist()
            effs = df_filtre["Effectif (ni)"].astype(float).to_numpy()
            ax.bar(labels, effs, width=0.2, color="#38bdf8", zorder=3)
            ax.grid(True, which="both", color="#334155", linestyle=":", lw=0.8)
            stats_text = "Statistiques indisponibles pour caracteres qualitatifs."

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
        
        # APPEL UNIQUE DU MOTEUR INTERNE SÉCURISÉ (df_filtre est genere a l'interieur de cette fonction)
        fig_batons = calculer_et_tracer_batons_matplotlib(st.session_state.df_session_tab1)
        st.pyplot(fig_batons, use_container_width=True)

    # =========================================================================
    # RECONSTRUCTION DU BLOC DE VALIDATION FINALE SUR 20 POINTS SANS EMOJI
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    if "stat1_verrouille" not in st.session_state:
        st.session_state.stat1_verrouille = False

    # Appel permanent de la fonction dynamique bicolonne
    dict_q1, dict_t1 = afficher_questions_statistiques_dynamiques(
        st.session_state.df_session_tab1, 
        verrouille=st.session_state.stat1_verrouille
    )

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete l'integralite des 20 questions de l'Atelier 1.", 
        key="check_certif_stat1_officiel_20pts", 
        disabled=st.session_state.stat1_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_stat1_official_20pts", use_container_width=True, disabled=st.session_state.stat1_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz adaptatif (10 questions x 1.0 point)
            score_quiz = 0.0
            for i in range(1, 11):
                q_key = f"q{i}"
                saisie_e = st.session_state.get(f"col_g_quiz_dyn_s1_{q_key}", "Choisir...")
                attendu_e = st.session_state.get(f"correct_ans_dyn_s1_{q_key}")
                if str(saisie_e) == str(attendu_e):
                    score_quiz += 1.0

            # 2. Correction automatique du Texte a trous (10 cases x 1.0 point)
            score_trous = 0.0
            attendus_trous = {
                "t1": "Discrete", "t2": "Moyenne", "t3": "Mediane", "t4": "Ecart-type",
                "t5": "25%", "t6": "75%", "t7": "Etendue", "t8": "Frequence absolue",
                "t9": "Frequence", "t10": "Effectif ni"
            }
            for tk, tv in attendus_trous.items():
                if st.session_state.get(f"stat1_{tk}") == tv:
                    score_trous += 1.0

            st.session_state.score_stat1_p1 = round(score_quiz, 1)
            st.session_state.score_stat1_p2 = round(score_trous, 1)
            st.session_state.score_final_stat1 = round(score_quiz + score_trous, 1)
            st.session_state.stat1_verrouille = True
            st.rerun()

    # LE GENERATEUR DU DOCUMENT HTML OFFICIEL APRÈS VERROUILLAGE
    if st.session_state.stat1_verrouille:
        scr1 = st.session_state.get("score_stat1_p1", 0.0)
        scr2 = st.session_state.get("score_stat1_p2", 0.0)
        tot_s = st.session_state.get("score_final_opt1" if "score_final_opt1" in st.session_state else "score_final_stat1", 0.0)

        from datetime import datetime, timedelta
        timestamp_stat1 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 1 SCELLE | Note globale de l'eleve : {tot_s} / 20")

        attendus_trous = {
            "t1": "Discrete", "t2": "Moyenne", "t3": "Mediane", "t4": "Ecart-type",
            "t5": "25%", "t6": "75%", "t7": "Etendue", "t8": "Frequence absolue",
            "t9": "Frequence", "t10": "Effectif ni"
        }

        html_export_stat1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 1 - {n_eleve}</title>
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Diagramme en Batons</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308;">
                &bull; Partie 1 : Quiz de validation adaptatif : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours (10 trous) : <strong>{scr2} / 10</strong>
            </p>

            <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ DYNAMIQUE (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Item</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu Technique</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s1_{qk}", "Choisir...")
            attendu = st.session_state.get(f"correct_ans_dyn_s1_{qk}")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat1 += f"<tr><td>Question {i}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat1 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Case</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu theorique</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for tk, tv in attendus_trous.items():
            saisie = st.session_state.get(f"stat1_{tk}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat1 += f"<tr><td>Trou {tk.replace('t','')}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{tv}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat1 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse statistique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Statistiques1_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER VOTRE RAPPORT D'ATELIER 1 SUR VOTRE COMPUTER",
            data=html_export_stat1,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Atelier 2 : Analyse Statistique & Diagramme Circulaire")
    
    # Initialisation permanente du nombre de lignes de saisie en memoire
    if "nbr_lignes_tab2" not in st.session_state: 
        st.session_state.nbr_lignes_tab2 = 5
    if "stat2_verrouille" not in st.session_state: 
        st.session_state.stat2_verrouille = False

    # =========================================================================
    # ARCHITECTURE EN COLONNES : GRILLE DE SAISIE / RENDU DU GÂTEAU
    # =========================================================================
    col_g_tableau2, col_d_graphique2 = st.columns([1.2, 1.8])

    with col_g_tableau2:
        with st.container(border=True):
            st.markdown("<p style='color:#1e3a8a; font-weight:bold; margin-bottom:5px;'>GRILLE DES DONNÉES STATISTIQUES (CIRCULAIRE)</p>", unsafe_allow_html=True)
            st.number_input("Nombre de lignes necessaires (categories) :", min_value=1, max_value=50, value=5, step=1, key="nbr_lignes_tab2")
            
            import pandas as pd
            if "df_session_tab2" not in st.session_state or len(st.session_state.df_session_tab2) != st.session_state.nbr_lignes_tab2:
                st.session_state.df_session_tab2 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab2,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab2
                })

            df_edite2 = st.data_editor(st.session_state.df_session_tab2, use_container_width=True, hide_index=True, key="editeur_grille_tab2")
            st.session_state.df_session_tab2 = df_edite2

            if st.button("Reinitialiser la grille ", key="btn_reset_tab2", use_container_width=True):
                st.session_state.df_session_tab2 = pd.DataFrame({
                    "Caractere (xi)": [""] * st.session_state.nbr_lignes_tab2,
                    "Effectif (ni)": [""] * st.session_state.nbr_lignes_tab2
                })
                st.rerun()

        with st.container(border=True):
            st.markdown("**Frequences relatives & Secteurs angulaires :**")
            st.text(st.session_state.get("stats2_affichage_texte", "En attente de saisies..."))

    with col_d_graphique2:
        st.subheader("Distribution en secteurs")
        fig_circulaire = calculer_et_tracer_circulaire_matplotlib(st.session_state.df_session_tab2)
        st.pyplot(fig_circulaire, use_container_width=True)

    # C'EST ICI ET UNIQUEMENT ICI QUE L'APPEL DOIT EXISTER (BIEN INDENTÉ)
    st.write("---")
    dict_q2, dict_t2 = afficher_questions_statistiques2_dynamiques(
        st.session_state.df_session_tab2, 
        verrouille=st.session_state.stat2_verrouille
    )
    # =========================================================================
    # INJECTION DES QUESTIONNAIRES ET PROCESSUS DE NOTATION FINALE SUR 20 PTS
    # =========================================================================
    st.write("---")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complete l'integralite des 20 questions de l'Atelier 2.", 
        key="check_certif_stat2_officiel_20pts", 
        disabled=st.session_state.stat2_verrouille
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_stat2_official_20pts", use_container_width=True, disabled=st.session_state.stat2_verrouille):
        if not st.session_state.get("verrouille", False): 
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            # 1. Correction automatique du Quiz adaptatif (10 questions x 1.0 point)
            score_quiz2 = 0.0
            for i in range(1, 11):
                q_key = f"q{i}"
                saisie_e = st.session_state.get(f"col_g_quiz_dyn_s2_{q_key}", "Choisir...")
                attendu_e = st.session_state.get(f"correct_ans_dyn_s2_{q_key}")
                if str(saisie_e) == str(attendu_e):
                    score_quiz2 += 1.0

            # 2. Correction automatique du Texte a trous (10 cases x 1.0 point)
            score_trous2 = 0.0
            attendus_trous2 = {
                "t1": "Secteurs", "t2": "Effectif ni", "t3": "360°", "t4": "50%",
                "t5": "Frequence", "t6": "Degres", "t7": "100%", "t8": "Repartition",
                "t9": "3.6", "t10": "Textuelles"
            }
            for tk, tv in attendus_trous2.items():
                if st.session_state.get(f"stat2_{tk}") == tv:
                    score_trous2 += 1.0

            st.session_state.score_stat2_p1 = round(score_quiz2, 1)
            st.session_state.score_stat2_p2 = round(score_trous2, 1)
            st.session_state.score_final_stat2 = round(score_quiz2 + score_trous2, 1)
            st.session_state.stat2_verrouille = True
            st.rerun()

    # LE GENERATEUR DU DOCUMENT HTML OFFICIEL APRÈS LE SCELLE DE LA NOTE
    if st.session_state.stat2_verrouille:
        scr1 = st.session_state.get("score_stat2_p1", 0.0)
        scr2 = st.session_state.get("score_stat2_p2", 0.0)
        tot_s = st.session_state.get("score_final_stat2", 0.0)

        from datetime import datetime, timedelta
        timestamp_stat2 = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER STATISTIQUES 2 SCELLE | Note globale de l'eleve : {tot_s} / 20")

        attendus_trous2 = {
            "t1": "Secteurs", "t2": "Effectif ni", "t3": "360°", "t4": "50%",
            "t5": "Frequence", "t6": "Degres", "t7": "100%", "t8": "Repartition",
            "t9": "3.6", "t10": "Textuelles"
        }

        html_export_stat2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statistiques 2 - {n_eleve}</title>
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
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_stat2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 20</div>
            </div>

            <div class="sub-title">Recapitulatif de session - Diagramme Circulaire</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308;">
                &bull; Partie 1 : Quiz de validation adaptatif (10 items) : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Synthese de cours (10 trous) : <strong>{scr2} / 10</strong>
            </p>

        <div class="sub-title">PARTIE 1 : DETAILS DU QUIZ CIRCULAIRE DYNAMIQUE (10 PTS)</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 10%;">Item</th>
                    <th style="width: 40%; text-align: center;">Saisie Eleve</th>

                        <th style="width: 25%; text-align: center;">Attendu Technique</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for i in range(1, 11):
            qk = f"q{i}"
            saisie = st.session_state.get(f"col_g_quiz_dyn_s2_{qk}", "Choisir...")
            attendu = st.session_state.get(f"correct_ans_dyn_s2_{qk}")
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat2 += f"<tr><td>Question {i}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat2 += """
                </tbody>
            </table>

            <div class="sub-title">PARTIE 2 : DETAILS DE LA SYNTHESE DE COURS (10 PTS)</div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 10%;">Case</th>
                        <th style="width: 40%; text-align: center;">Saisie Eleve</th>
                        <th style="width: 25%; text-align: center;">Attendu theorique</th>
                        <th style="width: 25%; text-align: center;">Verdict</th>
                    </tr>
                </thead>
                <tbody>
        """

        for tk, tv in attendus_trous2.items():
            saisie = st.session_state.get(f"stat2_{tk}", "Choisir...")
            v_lbl = "CORRECT" if str(saisie) == str(tv) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_stat2 += f"<tr><td>Trou {tk.replace('t','')}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{tv}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_stat2 += """
                </tbody>
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel d'analyse statistique genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """

        nom_f = f"Rapport_Evaluation_Statistiques2_{n_eleve}_{c_eleve}"
        for c in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]: 
            nom_f = nom_f.replace(c, "_")

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT DE L'ATELIER 2 SUR VOTRE ORDINATEUR",
            data=html_export_stat2,
            file_name=f"{nom_f}.html",
            mime="text/html",
            use_container_width=True
        )



























