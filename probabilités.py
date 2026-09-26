import streamlit as st

# =============================================================================
# CONFIGURATION ET DEPLOYEMENT PLEIN ÉCRAN (OBLIGATOIREMENT À LA LIGNE 1)
# =============================================================================
st.set_page_config(
    page_title="Application de Probabilites",
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
    "1. Jeux de hasard 1",
    "2. Jeux de hasard 2",
    "3. Tableau de probabilités",
    "4. Arbre de probabilités",
    "5. Espérance et variance",
    "6. Loi exponentielle ",
    "7. Loi binomiale ",    
    "8. Loi de Poisson",
    "9. Loi de Gauss (loi normale)"
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



def afficher_questions_atelier5(verrouille=False):
    col_double_quiz_at5, col_double_trous_at5 = st.columns(2)

    sol_m = st.session_state.get("at5_scenario", {})
    # Récupération des valeurs sous forme textuelle pour le QCM
    e_x = f"{sol_m.get('E_X', 0.0):.2f}"
    v_x = f"{sol_m.get('V_X', 0.0):.4f}"
    p1 = f"{sol_m.get('p1', 0.0):.2f}"
    p2 = f"{sol_m.get('p2', 0.0):.2f}"
    p3 = f"{sol_m.get('p3', 0.0):.2f}"

    filiere_active = st.session_state.get("var_filiere_selectbox_at5", "Conducteur Routier")
    
    # Contextualisation dynamique du paragraphe selon le métier sélectionné
    contextes_trous = {
        "Conducteur Routier": "filiere du transport routier, nous modelisons les distances de livraison.",
        "Maintenance des Véhicules": "filiere de la maintenance automobile, nous suivons les temps d'intervention.",
        "Travaux Publics (TP)": "filiere des travaux publics, nous analysons les couts des materiaux."
    }
    texte_metier = contextes_trous.get(filiere_active, contextes_trous["Conducteur Routier"])

    # --- COLONNE DE GAUCHE : LE QUIZ NUMÉRIQUE MÉLANGÉ ---
    with col_double_quiz_at5:
        st.markdown("##### Quiz de calculs (10 questions) - Atelier 5")
        
        if "ordre_questions_at5" not in st.session_state:
            questions_at5_base = [
                ("q1", "L'esperance mathematique E(X) calculee pour votre exercice vaut :"),
                ("q2", "La variance V(X) mesure la dispersion, pour votre exercice elle vaut :"),
                ("q3", "Si la somme des probabilites P(X=xi) ne vaut pas 1, la loi est :"),
                ("q4", "La formule de la variance soustrait au total de E(X²) le terme :"),
                ("q5", "L'esperance mathematique peut etre assimilee graphiquement a une :"),
                ("q6", "Si tous les gains xi sont multiplies par 2, l'esperance E(2X) est :"),
                ("q7", "La probabilite manquante du tableau se calcule par la methode de la :"),
                ("q8", "Pour la ligne des produits xi * p_i, la somme totale de cette ligne donne :"),
                ("q9", "L'ecart-type correspond mathematiquement a la racine carree de la :"),
                ("q10", "La somme obligatoire de la ligne des probabilites d'une loi vaut :")
            ]
            import random
            random.shuffle(questions_at5_base)
            st.session_state.ordre_questions_at5 = questions_at5_base

        dict_quiz_at5 = {}
        opts_num = ["Choisir...", e_x, v_x, p1, p2, p3, "1.00", "0.00"]
        opts_num = list(dict.fromkeys(opts_num))

        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_at5, 1):
            cle_q5 = f"col_g_quiz_at5_{q_id}"
            cle_opts_unique = f"opts_at5_shuffled_{q_id}"
            
            if cle_opts_unique not in st.session_state:
                if q_id == "q3": copie_opts = ["Invalide", "Continue", "Symetrique"]
                elif q_id == "q4": copie_opts = ["[E(X)]²", "E(X²)", "2*E(X)"]
                elif q_id == "q5": copie_opts = ["Moyenne ponderee", "Mediane", "Valeur maximale"]
                elif q_id == "q6": copie_opts = ["Multipliee par 2", "Inchangee", "Au carree"]
                elif q_id == "q7": copie_opts = ["Soustraction a 1", "Multiplication", "Somme simple"]
                elif q_id == "q8": copie_opts = ["L'esperance E(X)", "La variance V(X)", "Le total 1.00"]
                elif q_id == "q9": copie_opts = ["Variance", "Esperance", "Probabilite"]
                elif q_id == "q10": copie_opts = ["1.00", "0.00", "0.50"]
                else: copie_opts = list(set(opts_num[1:]))
                
                import random
                random.shuffle(copie_opts)
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            opts_melangees = st.session_state[cle_opts_unique]
            val_p = st.session_state.get(cle_q5, "Choisir...")
            idx = opts_melangees.index(val_p) if val_p in opts_melangees else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_at5[f"{q_id}_at5"] = st.selectbox("", opts_melangees, index=idx, key=cle_q5, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : LE TEXTE À TROUS EN PARAGRAPHE CONTINU DYNAMIQUE ---
    with col_double_trous_at5:
        st.markdown("##### Synthese de cours (Texte a trous) - Atelier 5")
        
        c5_1, c5_2, c5_3 = st.columns([0.75, 0.25, 0.05], vertical_alignment="bottom")
        with c5_1: st.write(f"Dans cette etude appliquee a la {texte_metier} L'indicateur de tendance centrale nomme l'")
        with c5_2: t1 = st.selectbox("", ["Choisir...", "Esperance", "Variance", "Ecart-type"], key="at5_t1", disabled=verrouille, label_visibility="collapsed")
        with c5_3: st.write("se")

        c5_4, c5_5, c5_6 = st.columns([0.55, 0.25, 0.20], vertical_alignment="bottom")
        with c5_4: st.write("calcule en effectuant la somme des produits de chaque gain par sa probabilite. Sa valeur finale est de")
        with c5_5: t2 = st.selectbox("", opts_num, key="at5_t2", disabled=verrouille, label_visibility="collapsed")
        with c5_6: st.write(". Pour etudier la")

        c5_7, c5_8, c5_9 = st.columns([0.35, 0.25, 0.40], vertical_alignment="bottom")
        with c5_7: st.write("dispersion des risques, on calcule la")
        with c5_8: t3 = st.selectbox("", ["Choisir...", "Variance", "Esperance", "Issue"], key="at5_t3", disabled=verrouille, label_visibility="collapsed")
        with c5_9: st.write("en appliquant la formule de Koenig-Huygens.")

        c5_10, c5_11, c5_12 = st.columns([0.45, 0.25, 0.30], vertical_alignment="bottom")
        with c5_10: st.write("Cette methode soustrait le carre de l'esperance au total des")
        with c5_11: t4 = st.selectbox("", ["Choisir...", "xi² * p_i", "xi * p_i", "p_i"], key="at5_t4", disabled=verrouille, label_visibility="collapsed")
        with c5_12: st.write(". On trouve ainsi une")

        c5_13, c5_14, c5_15 = st.columns([0.30, 0.25, 0.45], vertical_alignment="bottom")
        with c5_13: st.write("variance egale a V(X) =")
        with c5_14: t5 = st.selectbox("", opts_num, key="at5_t5", disabled=verrouille, label_visibility="collapsed")
        with c5_15: st.write(". La somme de la ligne complete de toutes les")

        st.write("probabilites attribuees aux evenements doit imperativement completer l'unite numerique, assurant la conformite totale du modele mathematique.")

        dict_trous_at5 = {
            "t1_at5": t1, "t2_at5": t2, "t3_at5": t3, "t4_at5": t4, "t5_at5": t5
        }

    return dict_quiz_at5, dict_trous_at5

def dessiner_arbre_atelier4(verrouille=False):
    st.markdown("<h3 style='text-align: center; color: #1e3a8a; font-family: Arial; font-size: 16px; font-weight: bold; margin-bottom: 10px;'>Arbre de Probabilités Interactif</h3>", unsafe_allow_html=True)
    
    if "at4_scenario" not in st.session_state:
        p_A = round(random.uniform(0.55, 0.75), 2)
        p_Abar = round(1.00 - p_A, 2)
        p_S_sachant_A = round(random.uniform(0.05, 0.15), 2)
        p_Sbar_sachant_A = round(1.00 - p_S_sachant_A, 2)
        p_S_sachant_B = round(random.uniform(0.18, 0.28), 2)
        p_Sbar_sachant_B = round(1.00 - p_S_sachant_B, 2)
        
        st.session_state.at4_scenario = {
            "p_A": p_A, "p_A_bar": p_Abar,
            "p_B_sachant_A": p_S_sachant_A, "p_B_bar_sachant_A": p_Sbar_sachant_A,
            "p_B_sachant_A_bar": p_S_sachant_B, "p_B_bar_sachant_A_bar": p_Sbar_sachant_B,
            "f1": round(p_A * p_S_sachant_A, 4), "f2": round(p_A * p_Sbar_sachant_A, 4),
            "f3": round(p_Abar * p_S_sachant_B, 4), "f4": round(p_Abar * p_Sbar_sachant_B, 4)
        }

    scen = st.session_state.at4_scenario
    afficher_corr = "true" if st.session_state.get("at4_afficher_correction", False) else "false"
    dis_attr = "disabled" if verrouille else ""

    html_arbre_fusionne = f"""
    <div style="background-color: #ffffff; border: 2px solid #cbd5e1; border-radius: 6px; padding: 10px; width: 1200px; height: 600px; position: relative; font-family: Arial, sans-serif; margin: 0 auto; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);">
        
        <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 1;">
            <line x1="40" y1="210" x2="200" y2="105" style="stroke:black; stroke-width:2;" />
            <line x1="40" y1="210" x2="200" y2="315" style="stroke:black; stroke-width:2;" />
            <line x1="260" y1="105" x2="430" y2="52" style="stroke:black; stroke-width:1.5;" />
            <line x1="260" y1="105" x2="430" y2="157" style="stroke:black; stroke-width:1.5;" />
            <line x1="260" y1="315" x2="430" y2="262" style="stroke:black; stroke-width:1.5;" />
            <line x1="260" y1="315" x2="430" y2="367" style="stroke:black; stroke-width:1.5;" />
        </svg>

        <div style="position: absolute; top: 92px; left: 200px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">A</div>
        <div style="position: absolute; top: 302px; left: 200px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">Ā</div>
        <div style="position: absolute; top: 38px; left: 430px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">B</div>
        <div style="position: absolute; top: 143px; left: 430px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">B̄</div>
        <div style="position: absolute; top: 248px; left: 430px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">B</div>
        <div style="position: absolute; top: 353px; left: 430px; font-weight: bold; color: #1e3a8a; border: 2px solid #1e3a8a; background-color: #e0f2fe; padding: 4px 10px; border-radius: 4px; font-size: 11px; z-index: 3;">B̄</div>

        <div style="position: absolute; top: 43px; left: 485px; font-size: 11px; font-weight: bold;">P(A &cap; B) =</div>
        <div style="position: absolute; top: 148px; left: 485px; font-size: 11px; font-weight: bold;">P(A &cap; B̄) =</div>
        <div style="position: absolute; top: 253px; left: 485px; font-size: 11px; font-weight: bold;">P(Ā &cap; B) =</div>
        <div style="position: absolute; top: 358px; left: 485px; font-size: 11px; font-weight: bold;">P(Ā &cap; B̄) =</div>

        <!-- ENTRÉES INTERACTIVES SCELLÉES -->
        <input id="v1" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_A']}" {dis_attr} style="position: absolute; top: 125px; left: 80px; width: 65px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="v2" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_A_bar']}" {dis_attr} style="position: absolute; top: 265px; left: 80px; width: 65px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">

        <input id="v3" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_B_sachant_A']}" {dis_attr} style="position: absolute; top: 55px; left: 310px; width: 60px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="v4" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_B_bar_sachant_A']}" {dis_attr} style="position: absolute; top: 145px; left: 310px; width: 60px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="v5" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_B_sachant_A_bar']}" {dis_attr} style="position: absolute; top: 250px; left: 310px; width: 60px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="v6" type="number" min="0" max="1" step="0.01" data-ans="{scen['p_B_bar_sachant_A_bar']}" {dis_attr} style="position: absolute; top: 340px; left: 310px; width: 60px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">

        <input id="f1" type="number" min="0" max="1" step="0.0001" data-ans="{scen['f1']}" {dis_attr} style="position: absolute; top: 38px; left: 565px; width: 75px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="f2" type="number" min="0" max="1" step="0.0001" data-ans="{scen['f2']}" {dis_attr} style="position: absolute; top: 143px; left: 565px; width: 75px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="f3" type="number" min="0" max="1" step="0.0001" data-ans="{scen['f3']}" {dis_attr} style="position: absolute; top: 248px; left: 565px; width: 75px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
        <input id="f4" type="number" min="0" max="1" step="0.0001" data-ans="{scen['f4']}" {dis_attr} style="position: absolute; top: 353px; left: 565px; width: 75px; border: 1px solid #cbd5e1; border-radius: 4px; text-align: center; font-size: 11px; z-index: 5;">
    </div>

    <!-- CODE MOTEUR : CORRECTION ET REMPLACEMENT DES VALEURS DANS LES CASES -->
    <script>
        function executerCorrectionEtRemplacement() {{
            const inputs = document.querySelectorAll('input[type="number"]');
            inputs.forEach(input => {{
                const saisie = parseFloat(input.value) || 0;
                const attendu = parseFloat(input.getAttribute('data-ans'));
                const tolerance = input.id.startsWith('f') ? 0.001 : 0.01;
                
                // Formater l'affichage selon le niveau (4 décimales pour les intersections F)
                const valeurFormatee = input.id.startsWith('f') ? attendu.toFixed(4) : attendu.toFixed(2);
                
                if (Math.abs(saisie - attendu) < tolerance) {{
                    // REUSSITE : Reste vert
                    input.style.border = "2px solid #10b981";
                    input.style.backgroundColor = "#e6f4ea";
                    input.style.color = "#137333";
                    input.style.fontWeight = "bold";
                }} else {{
                    // ERREUR : La bonne reponse ecrase la saisie et s'affiche en rouge
                    input.value = valeurFormatee;
                    input.style.border = "2px solid #ef4444";
                    input.style.backgroundColor = "#fce8e6";
                    input.style.color = "#c5221f";
                    input.style.fontWeight = "bold";
                }}
            }});
        }}
        
        if ({afficher_corr}) {{
            executerCorrectionEtRemplacement();
        }}
    </script>
    """
    
    st.components.v1.html(html_arbre_fusionne, height=750, width=1200)
    return scen

def verifier_et_marquer_atelier4():
    # 1. RECUPERATION DES DONNEES ET SOLUTIONS
    if "at4_scenario" not in st.session_state:
        st.error("Aucun exercice genere. Veuillez cliquer sur GENERER UN NOUVEL EXERCICE.")
        return

    sol = st.session_state.at4_scenario
    
    # 2. CAPTURE CHIRURGICALE DES SAISIES DE L'ARBRE DEPUIS LA MEMOIRE D'URL
    v1 = st.session_state.get("v_at4_1", 0.0)
    v2 = st.session_state.get("v_at4_2", 0.0)
    v3 = st.session_state.get("v_at4_3", 0.0)
    v4 = st.session_state.get("v_at4_4", 0.0)
    v5 = st.session_state.get("v_at4_5", 0.0)
    v6 = st.session_state.get("v_at4_6", 0.0)
    f1 = st.session_state.get("v_at4_f1", 0.0)
    f2 = st.session_state.get("v_at4_f2", 0.0)
    f3 = st.session_state.get("v_at4_f3", 0.0)
    f4 = st.session_state.get("v_at4_f4", 0.0)

    # 3. VERIFICATION DE LA PARFAITE CONFORMITE NUMERIQUE (8 POINTS)
    score_p1 = 0
    if abs(v1 - sol["p_A"]) < 0.01: score_p1 += 1
    if abs(v2 - sol["p_A_bar"]) < 0.01: score_p1 += 1
    if abs(v3 - sol["p_B_sachant_A"]) < 0.01: score_p1 += 1
    if abs(v4 - sol["p_B_bar_sachant_A"]) < 0.01: score_p1 += 1
    if abs(v5 - sol["p_B_sachant_A_bar"]) < 0.01: score_p1 += 1
    if abs(v6 - sol["p_B_bar_sachant_A_bar"]) < 0.01: score_p1 += 1
    if abs(f1 - sol["f1"]) < 0.001: score_p1 += 1
    if abs(f2 - sol["f2"]) < 0.001: score_p1 += 1
    if abs(f3 - sol["f3"]) < 0.001: score_p1 += 1
    if abs(f4 - sol["f4"]) < 0.001: score_p1 += 1

    # 4. VERIFICATION DES DICTIONNAIRES DE QUIZ ET TROUS (20 POINTS)
    attendus_q4 = {"q1_at4": "1", "q2_at4": "Multiplier les probabilites entre elles", "q3_at4": "Conditionnelle", "q4_at4": "P(A et B) / P(B)", "q5_at4": "Au second niveau en sommant les chemins menant a lui", "q6_at4": "P(A)", "q7_at4": "6", "q8_at4": "L'evenement contraire de A", "q9_at4": "0.6", "q10_at4": "L'extremite d'un chemin unique"}
    attendus_t4 = {"t1_at4": "Branches", "t2_at4": "Initial (Racine)", "t3_at4": "Multiplier", "t4_at4": "Additionner", "t5_at4": "1", "t6_at4": "Realise", "t7_at4": "Incompatibles", "t8_at4": "Conditionnelle", "t9_at4": "Chemin (Issue)", "t10_at4": "Hasard (Probabilites)"}
    
    score_p2 = sum([1 for qk, qv in attendus_q4.items() if st.session_state.get(f"col_g_quiz_at4_{qk}") == qv])
    score_p3 = sum([1 for tk, tv in attendus_t4.items() if st.session_state.get(f"col_d_trous_at4_{tk}") == tv])

    # Consolidation de la note finale globale
    st.session_state.score_final_at4 = score_p1 + score_p2 + score_p3
    st.session_state.at4_afficher_correction = True

def afficher_questions_atelier1(verrouille=False):
    col_maitre_quiz, col_maitre_trous = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ FRACTIONS DE L'ATELIER 1
    # -------------------------------------------------------------------------
    with col_maitre_quiz:
        st.subheader("Quiz theorique (10 questions)")
        st.write("Repondez aux questions de cours ci-dessous :")

        if "banque_quiz_at1" not in st.session_state:
            st.session_state.banque_quiz_at1 = [
                {"id": "q1", "q": "Question 1 : Si un evenement a 3 chances sur 4 de se realiser, sa probabilite est de :", "opts": ["Choisir...", "0.25", "0.50", "0.75", "1.33"]},
                {"id": "q2", "q": "Question 2 : Quelle est la probabilite d'obtenir un nombre pair (2, 4, 6) avec le de cubique :", "opts": ["Choisir...", "1/6", "2/6", "3/6 (1/2)", "4/6"]},
                {"id": "q3", "q": "Question 3 : Quelle est la probabilite d'obtenir une figure (Valet, Dame, Roi) dans le jeu de 32 cartes :", "opts": ["Choisir...", "4/32", "8/32", "12/32 (3/8)", "16/32"]},
                {"id": "q4", "q": "Question 4 : L'evenement contraire de 'obtenir un 6' au de a pour probabilite :", "opts": ["Choisir...", "0", "1/6", "5/6", "1"]},
                {"id": "q5", "q": "Question 5 : La probabilite d'un evenement est obligatoirement un nombre compris entre :", "opts": ["Choisir...", "-1 et 1", "0 et 1", "0 et 6", "1 et 100"]},
                {"id": "q6", "q": "Question 6 : Si on tire le 7 de Pique, cet evenement is qualifie d'evenement :", "opts": ["Choisir...", "Impossible", "Certain", "Elementaire", "Compose"]},
                {"id": "q7", "q": "Question 7 : Quelle est la probabilite d'obtenir un multiple de 3 (3 ou 6) sur le de :", "opts": ["Choisir...", "1/6", "2/6 (1/3)", "3/6", "4/6"]},
                {"id": "q8_at1", "q": "Question 8 : Quelle est la probabilite de tirer soit un Roi soit un As dans le jeu de 32 cartes :", "opts": ["Choisir...", "2/32", "4/32", "8/32 (1/4)", "12/32"]},
                {"id": "q9", "q": "Question 9 : Un de a 6 faces est truque pour que le 6 sorte plus souvent. La somme des probabilites vaut :", "opts": ["Choisir...", "0.5", "1", "2", "6"]},
                {"id": "q10", "q": "Question 10 : Si la probabilite d'un evenement A est 0.3, celle de son evenement contraire est :", "opts": ["Choisir...", "0", "0.3", "0.7", "1"]}
            ]
            random.shuffle(st.session_state.banque_quiz_at1)

        for item_quiz in st.session_state.banque_quiz_at1:
            cle_q = f"col_g_quiz_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"], 
                options=item_quiz["opts"], 
                index=idx_defaut, 
                key=cle_q,
                disabled=verrouille
            )

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS DE L'ATELIER 1
    # -------------------------------------------------------------------------
    with col_maitre_trous:
        st.subheader("Texte a trous (10 menus)")
        st.write("Completez le texte d'analyse ci-dessous :")

        if "banque_trous_at1" not in st.session_state:
            st.session_state.banque_trous_at1 = [
                {"id": "t1", "label": "Question A : Nombre de faces d'un de cubique regulier :", "options": ["Choisir...", "2", "4", "6", "8", "12"]},
                {"id": "t2", "label": "Question B : Probabilite theorique d'obtenir la face 6 sur le de :", "options": ["Choisir...", "1/2", "1/4", "1/6", "4/6", "1"]},
                {"id": "t3", "label": "Question C : Nombre total de cartes dans le paquet utilise :", "options": ["Choisir...", "12", "32", "36", "52", "54"]},
                {"id": "t4", "label": "Question D : Nombre de familles (couleurs) differentes dans ce jeu :", "options": ["Choisir...", "1", "2", "3", "4", "8"]},
                {"id": "t5", "label": "Question E : Nombre de cartes par famille (ex: nombre de Piques) :", "options": ["Choisir...", "4", "7", "8", "10", "13"]},
                {"id": "t6", "label": "Question F : Probabilite theorique de tirer un As dans ce jeu :", "options": ["Choisir...", "1/32", "2/32", "4/32 (1/8)", "8/32 (1/4)", "0"]},
                {"id": "t7", "label": "Question G : Probabilite theorique de tirer un Coeur dans ce jeu :", "options": ["Choisir...", "1/32", "4/32 (1/8)", "8/32 (1/4)", "16/32 (1/2)", "1"]},
                {"id": "t8", "label": "Question H : Un evenement dont la probabilite est egale a 1 est un evenement :", "options": ["Choisir...", "Impossible", "Probable", "Incertain", "Certain", "Contraire"]},
                {"id": "t9", "label": "Question I : Un evenement dont la probabilite est egale a 0 est un evenement :", "options": ["Choisir...", "Impossible", "Probable", "Incertain", "Certain", "Contraire"]},
                {"id": "t10", "label": "Question J : La somme des probabilites de toutes les faces distinctes du de vaut :", "options": ["Choisir...", "0", "0.5", "1", "6", "100"]}
            ]
            random.shuffle(st.session_state.banque_trous_at1)

        for item_trous in st.session_state.banque_trous_at1:
            cle_t = f"col_d_trous_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"], 
                options=item_trous["options"], 
                index=idx_defaut_t, 
                key=cle_t,
                disabled=verrouille
            )


def afficher_questions_atelier2(verrouille=False):
    col_maitre_quiz_at2, col_double_trous_at2 = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LE QUIZ THEORIQUE DE 10 QUESTIONS MELEES
    # -------------------------------------------------------------------------
    with col_maitre_quiz_at2:
        st.subheader("Quiz theorique (10 questions) - Atelier 2")
        st.write("Repondez aux questions de cours ci-dessous :")

        if "banque_quiz_at2" not in st.session_state:
            st.session_state.banque_quiz_at2 = [
                {"id": "q1_at2", "q": "Question 1 : Combien de cases contient la roulette europeenne :", "opts": ["Choisir...", "36", "37", "38"]},
                {"id": "q2_at2", "q": "Question 2 : Probabilite obtenir le numero 7 unique :", "opts": ["Choisir...", "1/36", "1/37", "1/2"]},
                {"id": "q3_at2", "q": "Question 3 : La probabilite de miser sur la categorie Rouge vaut :", "opts": ["Choisir...", "18/36", "18/37", "1/2"]},
                {"id": "q4_at2", "q": "Question 4 : L'avantage de la roulette pour le casino vient de :", "opts": ["Choisir...", "La case Zero", "Des numeros noirs", "De la bille"]},
                {"id": "q5_at2", "q": "Question 5 : En augmentant les lancers, la frequence rejoint :", "opts": ["Choisir...", "La probabilite theoretique", "Zero", "L'infini"]},
                {"id": "q6_at2", "q": "Question 6 : Cette convergence s'appelle la loi des grands :", "opts": ["Choisir...", "Nombres", "Ecarts", "Calculs"]},
                {"id": "q7_at2", "q": "Question 7 : Sur 3 rouleaux et 7 symboles, la probabilite de Jackpot vaut :", "opts": ["Choisir...", "1/7", "1/49", "1/343"]},
                {"id": "q8_at2", "q": "Question 8 : Obtenir un nombre Pair ou Impair sont deux issues :", "opts": ["Choisir...", "Contraires (hors zero)", "Incompatibles", "Certaines"]},
                {"id": "q9_at2", "q": "Question 9 : Sur 10 lancers, la fluctuation d'echantillonnage est :", "opts": ["Choisir...", "Forte", "Nulle", "Inexistante"]},
                {"id": "q10_at2", "q": "Question 10 : La probabilite d'obtenir la case Verte (le Zero) vaut :", "opts": ["Choisir...", "0", "1/37", "1"]}
            ]
            random.shuffle(st.session_state.banque_quiz_at2)

        for item_quiz in st.session_state.banque_quiz_at2:
            cle_q = f"col_g_quiz_at2_{item_quiz['id']}"
            val_precedente = st.session_state.get(cle_q, "Choisir...")
            idx_defaut = item_quiz["opts"].index(val_precedente) if val_precedente in item_quiz["opts"] else 0

            st.selectbox(
                label=item_quiz["q"], 
                options=item_quiz["opts"], 
                index=idx_defaut, 
                key=cle_q,
                disabled=verrouille
            )

    # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LE TEXTE A TROUS CASINO
    # -------------------------------------------------------------------------
    with col_double_trous_at2:
        st.markdown("##### Analyse de cours Casino (10 menus)")
        
        if "bq_t_at2" not in st.session_state:
            st.session_state.bq_t_at2 = [
                {"id": "t1_at2", "label": "Trou A : Le numero Zero de la roulette porte la couleur :", "options": ["Choisir...", "Rouge", "Noir", "Vert"]},
                {"id": "t2_at2", "label": "Trou B : Le nombre total de compartiments rouges vaut :", "options": ["Choisir...", "12", "18", "36"]},
                {"id": "t3_at2", "label": "Trou C : Le nombre total de compartiments noirs vaut :", "options": ["Choisir...", "12", "18", "36"]},
                {"id": "t4_at2", "label": "Trou D : Les 10 000 lancers demontrent la loi des grands :", "options": ["Choisir...", "Nombres", "Hasards", "Ecarts"]},
                {"id": "t5_at2", "label": "Trou E : La probabilite d'un gain est un nombre entre :", "options": ["Choisir...", "-1 et 0", "0 et 1", "0 et 36"]},
                {"id": "t6_at2", "label": "Trou F : Plus l'echantillon grandit, plus la fluctuation :", "options": ["Choisir...", "Diminue", "Augmente", "S'annule"]},
                {"id": "t7_at2", "label": "Trou G : L'evenement contraire de 'Miser sur le Noir' inclut :", "options": ["Choisir...", "Rouge et Vert", "Passe", "Manque"]},
                {"id": "t8_at2", "label": "Trou H : Plus il y a de rouleaux, plus le Jackpot est :", "options": ["Choisir...", "Facile", "Difficile", "Stable"]},
                {"id": "t9_at2", "label": "Trou I : Tomber sur la face 38 a la roulette est un evenement :", "options": ["Choisir...", "Certain", "Impossible", "Probable"]},
                {"id": "t10_at2", "label": "Trou J : Le tapis de la roulette comporte une case unique pour le :", "options": ["Choisir...", "As", "Jeton", "Zero"]}
            ]
            random.shuffle(st.session_state.bq_t_at2)

        for item_trous in st.session_state.bq_t_at2:
            cle_t = f"col_d_trous_at2_{item_trous['id']}"
            val_precedente_t = st.session_state.get(cle_t, "Choisir...")
            idx_defaut_t = item_trous["options"].index(val_precedente_t) if val_precedente_t in item_trous["options"] else 0

            st.selectbox(
                label=item_trous["label"], 
                options=item_trous["options"], 
                index=idx_defaut_t, 
                key=cle_t,
                disabled=verrouille
            )

def afficher_questions_atelier3(verrouille=False):
    col_double_quiz_at3, col_double_trous_at3 = st.columns(2)

    # Récupération des données dynamiques du tableau de l'Atelier 3
    sol = st.session_state.get("solution_courante", {})
    if isinstance(sol, dict) and len(sol) > 0:
        p_A_et_B = f"{sol.get((0, 0), 0.20):.2f}"
        p_A_et_Bbar = f"{sol.get((0, 1), 0.25):.2f}"
        p_A = f"{sol.get((0, 2), 0.45):.2f}"
        p_Abar_et_B = f"{sol.get((1, 0), 0.20):.2f}"
        p_Abar_et_Bbar = f"{sol.get((1, 1), 0.35):.2f}"
        p_Abar = f"{sol.get((1, 2), 0.55):.2f}"
        p_B = f"{sol.get((2, 0), 0.40):.2f}"
        p_Bbar = f"{sol.get((2, 1), 0.60):.2f}"
    else:
        p_A_et_B = p_A_et_Bbar = p_A = p_Abar_et_B = p_Abar_et_Bbar = p_Abar = p_B = p_Bbar = "0.50"

    # =========================================================================
    # CORRECTIF DE LA LIGNE 494 : DÉCLARATION LOCALE STABLE DE OPTS_BASE
    # =========================================================================
    opts_base = ["Choisir...", p_A_et_B, p_A_et_Bbar, p_A, p_Abar_et_B, p_Abar_et_Bbar, p_Abar, p_B, p_Bbar, "1.00", "0.00"]
    opts_base = list(dict.fromkeys(opts_base))

    filiere_active = st.session_state.get("var_filiere_selectbox", "Conducteur Routier")

    # --- COLONNE DE GAUCHE : LE QUIZ NUMÉRIQUE DE CALCULS ET FORMULES ---
    with col_double_quiz_at3:
        st.markdown("##### Quiz de calculs (10 questions) - Atelier 3")
        st.write("Saisissez le résultat numérique exact (questions et options mélangées) :")
        
        opts_brutes = [p_A_et_B, p_A_et_Bbar, p_A, p_Abar_et_B, p_Abar_et_Bbar, p_Abar, p_B, p_Bbar, "1.00", "0.00"]
        
        # Initialisation et mélange de l'ordre des questions de l'Atelier 3
        if "ordre_questions_at3" not in st.session_state:
            questions_at3_base = [
                ("q1", "La valeur de la probabilite de l'intersection $P(A \\cap B)$ est egale a :"),
                ("q2", "La valeur calculee pour la probabilite croisee $P(\\overline{{A}} \\cap \\overline{{B}})$ vaut :"),
                ("q3", "La probabilite marginale lue dans le tableau pour la ligne $P(A)$ vaut :"),
                ("q4", "La probabilite globale lue pour la colonne de la panne $P(B)$ vaut :"),
                ("q5", "La valeur de la probabilite de l'evenement contraire $P(\\overline{{B}})$ vaut :"),
                ("q6", "Par la formule $P(A) + P(B) - P(A \\cap B)$, la probabilite de l'union vaut :"),
                ("q7", "La valeur calculee pour la probabilite de l'evenement contraire $P(\\overline{{A}})$ vaut :"),
                ("q8", "La probabilite de l'union $P(\\overline{{A}} \\cup B)$ par formule de cours donne :"),
                ("q9", "La valeur de la cellule pour l'intersection mixte $P(\\overline{{A}} \\cap B)$ vaut :"),
                ("q10", "La valeur calculee pour l'intersection croisee $P(A \\cap \\overline{{B}})$ vaut :")
            ]
            random.shuffle(questions_at3_base) # MÉLANGE ALÉATOIRE DES QUESTIONS
            st.session_state.ordre_questions_at3 = questions_at3_base

        dict_quiz_at3 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_at3, 1):
            cle_q3 = f"col_g_quiz_at3_{q_id}"
            cle_opts_unique = f"opts_at3_shuffled_{q_id}"
            
            # Mélange des options pour cette question
            if cle_opts_unique not in st.session_state:
                copie_opts = list(set(opts_brutes))
                random.shuffle(copie_opts) # MÉLANGE ALÉATOIRE DES OPTIONS
                st.session_state[cle_opts_unique] = ["Choisir..."] + copie_opts
                
            opts_melangees = st.session_state[cle_opts_unique]
            val_p = st.session_state.get(cle_q3, "Choisir...")
            idx = opts_melangees.index(val_p) if val_p in opts_melangees else 0
            
            cq_txt, cq_sel = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with cq_txt: st.write(f"{num_idx}. {q_txt}")
            with cq_sel:
                dict_quiz_at3[f"{q_id}_at3"] = st.selectbox("", opts_melangees, index=idx, key=cle_q3, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : TEXTE À TROUS EN PARAGRAPHE CONTINU (COMME L'IMAGE) ---
    with col_double_trous_at3:
        st.markdown("##### Synthese de cours (Texte a trous) - Atelier 3")
        
        # Enchaînement fluide des phrases avec listes déroulantes compactes inline
        st.write(f"Dans cette etude dediee a la filiere **{filiere_active}**, nous analysons deux evenements principaux : l'evenement")
        t1 = st.selectbox("Trou 1 : Événement principal haut", ["Choisir...", "A", "B", "A ∩ B"], key="at3_t1", disabled=verrouille, label_visibility="collapsed")
        
        st.write("et l'evenement")
        t2 = st.selectbox("Trou 2 : Événement principal bas", ["Choisir...", "B", "Ā", "B̄"], key="at3_t2", disabled=verrouille, label_visibility="collapsed")
        
        st.write(f"D'apres les enregistrements fournis dans votre enonce de session, la probabilite de l'intersection P(A ∩ B) est egale a")
        t3 = st.selectbox("Trou 3 : Valeur intersection", opts_base, key="at3_t3", disabled=verrouille, label_visibility="collapsed")
        
        st.write("tandis que la probabilite globale de l'evenement A vaut P(A) =")
        t4 = st.selectbox("Trou 4 : Valeur P(A)", opts_base, key="at3_t4", disabled=verrouille, label_visibility="collapsed")
        
        st.write("et celle de B vaut P(B) =")
        t5 = st.selectbox("Trou 5 : Valeur P(B)", opts_base, key="at3_t5", disabled=verrouille, label_visibility="collapsed")
        
        st.write("La somme de toutes les issues possibles dans l'univers complet est obligatoirement egale a")
        t6 = st.selectbox("Trou 6 : Total univers", ["Choisir...", "0.00", "0.50", "1.00"], key="at3_t6", disabled=verrouille, label_visibility="collapsed")
        
        st.write("Pour calculer la probabilite de l'evenement")
        t7 = st.selectbox("Trou 7 : Événement contraire", ["Choisir...", "contraire de A", "compatible", "independant"], key="at3_t7", disabled=verrouille, label_visibility="collapsed")
        
        st.write("de A (note Ā), on soustrait P(A) a 1. Enfin, dans un tableau croise, les cases d'intersections calculent la probabilite de l'intersection de deux evenements, tandis que les extremites des lignes et des colonnes calculent la probabilite")
        t8 = st.selectbox("Trou 8 : Probabilités marginales", ["Choisir...", "marginale (globale)", "conditionnelle", "impossible"], key="at3_t8", disabled=verrouille, label_visibility="collapsed")
        st.write("finale.")

        dict_trous_at3 = {
            "t1_at3": t1, "t2_at3": t2, "t3_at3": t3, "t4_at3": t4,
            "t5_at3": t5, "t6_at3": t6, "t7_at3": t7, "t8_at3": t8
        }

    return dict_quiz_at3, dict_trous_at3

def afficher_questions_atelier4(verrouille=False):
    col_double_quiz_at4, col_double_trous_at4 = st.columns(2)

    # Récupération des données dynamiques de l'arbre généré dans l'Atelier 4
    sol_m = st.session_state.get("at4_scenario", {})
    if isinstance(sol_m, dict) and len(sol_m) > 0:
        p_A = f"{sol_m.get('p_A', 0.65):.2f}"
        p_A_bar = f"{sol_m.get('p_A_bar', 0.35):.2f}"
        p_B_A = f"{sol_m.get('p_B_sachant_A', 0.10):.2f}"
        p_Bbar_A = f"{sol_m.get('p_B_bar_sachant_A', 0.90):.2f}"
        p_B_Abar = f"{sol_m.get('p_B_sachant_A_bar', 0.20):.2f}"
        p_Bbar_Abar = f"{sol_m.get('p_B_bar_sachant_A_bar', 0.80):.2f}"
        f1 = f"{sol_m.get('f1', 0.0650):.4f}"
        f2 = f"{sol_m.get('f2', 0.5850):.4f}"
        f3 = f"{sol_m.get('f3', 0.0700):.4f}"
        f4 = f"{sol_m.get('f4', 0.2800):.4f}"
    else:
        p_A = p_A_bar = p_B_A = p_Bbar_A = p_B_Abar = p_Bbar_Abar = "0.50"
        f1 = f2 = f3 = f4 = "0.2500"

    # =========================================================================
    # CORRECTIF DE LA LIGNE 601 : DECLARATION UNIFIEE DE OPTS_BASE_AT4
    # =========================================================================
    opts_base_at4 = ["Choisir...", p_A, p_A_bar, p_B_A, p_Bbar_A, p_B_Abar, p_Bbar_Abar, f1, f2, f3, f4, "1.00", "0.00"]
    opts_base_at4 = list(dict.fromkeys(opts_base_at4))

    filiere_active = st.session_state.get("var_filiere_selectbox_at4", "Conducteur Routier")

    # --- COLONNE DE GAUCHE : LE QUIZ NUMÉRIQUE DE L'ARBRE ---
    with col_double_quiz_at4:
        st.markdown("##### Quiz de calculs (10 questions) - Atelier 4")
        st.write("Complétez les affirmations (questions et options mélangées) :")
        
        opts_brutes_at4 = [p_A, p_A_bar, p_B_A, p_Bbar_A, p_B_Abar, p_Bbar_Abar, f1, f2, f3, f4, "1.00", "0.00"]
        
        # Initialisation et mélange de l'ordre des questions de l'Atelier 4
        if "ordre_questions_at4" not in st.session_state:
            questions_at4_base = [
                ("q1", "La probabilite de choisir la premiere branche haute $P(A)$ vaut :"),
                ("q2", "La valeur calculee au bout du premier chemin complet $P(A \\cap B)$ vaut :"),
                ("q3", "La probabilite conditionnelle lue sur la branche secondaire $P_A(B)$ vaut :"),
                ("q4", "La probabilite affectee a la branche principale inferieure $P(\\overline{{A}})$ vaut :"),
                ("q5", "La probabilite conditionnelle de la sous-branche inferieure $P_{{\\overline{{A}}}}(\\overline{{B}})$ vaut :"),
                ("q6", "Le calcul de la derniere issue croisee du bas $P(\\overline{{A}} \\cap \\overline{{B}})$ donne :"),
                ("q7", "La valeur de la probabilite conditionnelle intermediaire $P_A(\\overline{{B}})$ vaut :"),
                ("q8", "La probabilite de l'intersection de la troisieme feuille $P(\\overline{{A}} \\cap B)$ vaut :"),
                ("q9", "Le long d'un chemin complet, les probabilites successives doivent obligatoirement se :"),
                ("q10", "La somme totale des 4 feuilles terminales de l'arbre ($F_1+F_2+F_3+F_4$) vaut :")
            ]
            random.shuffle(questions_at4_base) # MÉLANGE ALÉATOIRE DES QUESTIONS
            st.session_state.ordre_questions_at4 = questions_at4_base

        dict_quiz_at4 = {}
        for num_idx, (q_id, q_txt) in enumerate(st.session_state.ordre_questions_at4, 1):
            cle_q4 = f"col_g_quiz_at4_{q_id}"
            cle_opts_unique_at4 = f"opts_at4_shuffled_{q_id}"
            
            # Mélange des options pour cette question
            if cle_opts_unique_at4 not in st.session_state:
                if q_id == "q9":
                    copie_opts = ["Multiplier", "Additionner", "Soustraire"]
                elif q_id == "q10":
                    copie_opts = ["0.00", "0.50", "1.00"]
                else:
                    copie_opts = list(set(opts_brutes_at4))
                
                random.shuffle(copie_opts) # MÉLANGE ALÉATOIRE DES OPTIONS
                st.session_state[cle_opts_unique_at4] = ["Choisir..."] + copie_opts
                
            opts_melangees_at4 = st.session_state[cle_opts_unique_at4]
            val_p = st.session_state.get(cle_q4, "Choisir...")
            idx = opts_melangees_at4.index(val_p) if val_p in opts_melangees_at4 else 0
            
            c4_q, c4_s = st.columns([0.75, 0.25], vertical_alignment="bottom")
            with c4_q: st.write(f"{num_idx}. {q_txt}")
            with c4_s:
                dict_quiz_at4[f"{q_id}_at4"] = st.selectbox("", opts_melangees_at4, index=idx, key=cle_q4, disabled=verrouille, label_visibility="collapsed")

    # --- COLONNE DE DROITE : TEXTE À TROUS EN PARAGRAPHE CONTINU (ARBRE) ---
    with col_double_trous_at4:
        st.markdown("##### Synthese de cours (Texte a trous) - Atelier 4")
        
        st.write(f"Dans cette etude dediee a la filiere **{filiere_active}**, nous analysons un arbre pondere de décision. L'evenement principal de premier niveau est note")
        t1 = st.selectbox("Trou A1", ["Choisir...", "A", "B", "B sachant A"], key="at4_t1", disabled=verrouille, label_visibility="collapsed")
        
        st.write("D'apres les enregistrements de votre session, la probabilite de ce premier choix vaut P(A) =")
        t2 = st.selectbox("Trou A2", opts_base_at4, key="at4_t2", disabled=verrouille, label_visibility="collapsed")
        
        st.write("La somme des probabilites des branches issues d'un meme nœud initial est obligatoirement egale a")
        t3 = st.selectbox("Trou A3", ["Choisir...", "0.00", "0.50", "1.00"], key="at4_t3", disabled=verrouille, label_visibility="collapsed")
        
        st.write("ce qui permet de deduire la branche de l'evenement contraire note")
        t4 = st.selectbox("Trou A4", ["Choisir...", "Ā", "B̄", "A ∩ B"], key="at4_t4", disabled=verrouille, label_visibility="collapsed")
        
        st.write(". Au second niveau de l'arbre, les branches portent des probabilites")
        t5 = st.selectbox("Trou A5", ["Choisir...", "conditionnelles", "simples", "marginales"], key="at4_t5", disabled=verrouille, label_visibility="collapsed")
        
        st.write(", comme par exemple la valeur de P_A(B) qui est egale a")
        t6 = st.selectbox("Trou A6", opts_base_at4, key="at4_t6", disabled=verrouille, label_visibility="collapsed")
        
        st.write(". Enfin, pour calculer la probabilite de l'extremite complete d'un parcours (l'issue finale), on réalise une multiplication, ce qui donne pour la premiere feuille P(A ∩ B) =")
        t7 = st.selectbox("Trou A7", opts_base_at4, key="at4_t7", disabled=verrouille, label_visibility="collapsed")
        st.write("au bout du chemin.")

        dict_trous_at4 = {
            "t1_at4": t1, "t2_at4": t2, "t3_at4": t3, "t4_at4": t4,
            "t5_at4": t5, "t6_at4": t6, "t7_at4": t7
        }

    return dict_quiz_at4, dict_trous_at4


# =============================================================================
# ONGLET 0 : FORMULAIRE D'IDENTIFICATION DE L'ÉLÈVE
# =============================================================================
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
    # 1. Garde-fou sécurité (Alignement : 4 espaces)


    st.header("1. Jeux de hasard 1 : Dé et Jeu de 32 cartes")
    
    # =========================================================================
    # INITIALISATION SECURISEE DES MEMOIRES DE STATISTIQUES (OBLIGATOIRE)
    # =========================================================================
    if "de_total_lancers" not in st.session_state:
        st.session_state.de_total_lancers = 0
    if "de_stats" not in st.session_state:
        st.session_state.de_stats = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
    if "dernier_de" not in st.session_state:
        st.session_state.dernier_de = None

    if "cartes_total_tirages" not in st.session_state:
        st.session_state.cartes_total_tirages = 0
    if "cartes_valeurs_stats" not in st.session_state:
        st.session_state.cartes_valeurs_stats = {"7": 0, "8": 0, "9": 0, "10": 0, "Valet": 0, "Dame": 0, "Roi": 0, "As": 0}
    if "cartes_couleurs_stats" not in st.session_state:
        st.session_state.cartes_couleurs_stats = {"Carreau": 0, "Pique": 0, "Coeur": 0, "Trefe": 0}
    if "derniere_carte" not in st.session_state:
        st.session_state.derniere_carte = None
        
    # =========================================================================
    # CONFIGURATION DES COLONNES ET DES BOUTONS DE JEU
    # =========================================================================

    col_de_gauche, col_de_droite = st.columns(2)

    with col_de_gauche:
        if st.button("Lancer le Dé libre", key="btn_lancer_de_unitaire_at1"):
            with st.spinner("Le de roule sur la table..."):
                placeholder_animation = st.empty()
                faces_animation = ["", "", "", "", "", ""]
                for _ in range(4):
                    faux_tirage = random.choice(faces_animation)
                    placeholder_animation.markdown(
                        f"""
                        <div style="background-color: #f1f5f9; border: 2px dashed #3b82f6; border-radius: 8px; padding: 20px; text-align: center; margin-top: 15px;">
                            <span style="font-size: 16px; font-weight: bold; color: #3b82f6; font-style: italic;">Suspense...</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.15)
                placeholder_animation.empty()

            tirage_de = random.randint(1, 6)
            st.session_state.dernier_de = tirage_de
            st.session_state.de_stats[tirage_de] += 1
            st.session_state.de_total_lancers += 1
            st.rerun()

        if st.session_state.get("dernier_de"):
            st.markdown(
                f"""
                <div style="background-color: #f8fafc; border: 2px solid #cbd5e1; border-radius: 8px; padding: 20px; text-align: center; margin-top: 15px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
                    <span style="font-size: 16px; font-weight: bold; color: #475569;">Resultat du lancer :</span><br>
                    <span style="font-size: 48px; font-weight: bold; color: #2563eb; line-height: 1.5;">[ {st.session_state.dernier_de} ]</span><br>
                    <span style="font-size: 18px; font-weight: bold; color: #1e3a8a; text-transform: uppercase;">Face {st.session_state.dernier_de}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_de_droite:
        st.markdown("**Pourcentages d'obtention du Dé :**")
        total_d = st.session_state.de_total_lancers
        if total_d > 0:
            for face in range(1, 7):
                cpt = st.session_state.de_stats.get(face, 0)
                pct = (cpt / total_d) * 100
                st.write(f"Face {face} : **{pct:.1f}%** ({cpt}/{total_d})")
        else:
            st.write("Aucun lancer effectue.")

    st.write("---")

    # =========================================================================
    # PARTIE B : LE JEU DE CARTES (Visuel à gauche, Statistiques à droite)
    # =========================================================================
    # CORRECTIF CRITIQUE : Déclaration explicite des deux colonnes pour les cartes
    col_carte_gauche, col_carte_droite = st.columns(2)

    with col_carte_gauche:
        if st.button("Tirer une Carte", key="btn_tirer_carte_unitaire_at1"):
            with st.spinner("Melange du paquet de 32 cartes..."):
                placeholder_carte = st.empty()
                for i in range(5):
                    statut_melange = "MELANGE EN COURS" if i % 2 == 0 else "COUPE DU PAQUET"
                    placeholder_carte.markdown(
                        f"""
                        <div style="background-color: #2563eb; border: 3px solid #ffffff; border-radius: 12px; padding: 30px; text-align: center; margin-top: 15px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3);">
                            <span style="font-size: 14px; font-weight: bold; color: #ffffff; letter-spacing: 1px; text-transform: uppercase;">{statut_melange}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    time.sleep(0.12)
                placeholder_carte.empty()

            valeurs_32 = ["7", "8", "9", "10", "Valet", "Dame", "Roi", "As"]
            couleurs_32 = ["Carreau", "Pique", "Coeur", "Trefe"]
            v_tiree = random.choice(valeurs_32)
            c_tiree = random.choice(couleurs_32)

            st.session_state.derniere_carte = {"valeur": v_tiree, "couleur": c_tiree}
            st.session_state.cartes_valeurs_stats[v_tiree] += 1
            st.session_state.cartes_couleurs_stats[c_tiree] += 1
            st.session_state.cartes_total_tirages += 1
            st.rerun()

        if st.session_state.get("derniere_carte"):
            v_c = st.session_state.derniere_carte["valeur"]
            c_c = st.session_state.derniere_carte["couleur"]
            couleur_theme = "#dc2626" if c_c in ["Carreau", "Coeur"] else "#0f172a"
            abreviation = "10" if v_c == "10" else v_c
            st.markdown(
                f"""
                <div style="background-color: #ffffff; border: 8px solid {couleur_theme}; border-radius: 16px; padding: 25px; text-align: center; margin-top: 15px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); width: 100%; max-width: 220px; margin-left: auto; margin-right: auto;">
                    <div style="text-align: left; font-size: 18px; font-weight: bold; color: {couleur_theme}; margin-top: -15px; margin-left: -10px;">
                        {abreviation}<br><span style="font-size: 11px; text-transform: uppercase;">{c_c[:4]}</span>
                    </div>
                    <div style="font-size: 22px; font-weight: bold; color: {couleur_theme}; margin: 20px 0; text-transform: uppercase; letter-spacing: 0.5px;">
                        {c_c}
                    </div>
                    <div style="font-size: 26px; font-weight: bold; color: #1e293b; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;">
                        {v_c}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            
    with col_carte_droite:
        st.markdown("**Pourcentages par Couleur / Valeur :**")
        total_c = st.session_state.cartes_total_tirages
        if total_c > 0:
            c1, c2 = st.columns(2)
            with c1:
                st.write("**Couleurs :**")
                for col in ["Carreau", "Pique", "Coeur", "Trefe"]:
                    cpt = st.session_state.cartes_couleurs_stats[col]
                    st.write(f"{col} : **{(cpt/total_c)*100:.1f}%**")
            with c2:
                st.write("**Valeurs :**")
                for val in [
                    "7",
                    "8",
                    "9",
                    "10",
                    "Valet",
                    "Dame",
                    "Roi",
                    "As",
                ]:
                    cpt = st.session_state.cartes_valeurs_stats[val]
                    st.write(f"{val} : **{(cpt/total_c)*100:.1f}%**")
        else:
            st.write("Aucun tirage effectué. Cliquez sur le bouton.")

    # =========================================================================
    # PARTIE C : LOI DES GRANDS NOMBRES (GRAPHIQUE DES 10 000 LANCERS/TIRAGES)
    # =========================================================================
    st.write("---")
    st.subheader("Loi des Grands Nombres - Simulation de 10 000 événements")
    st.write(
        "Sélectionnez le mode pour observer la convergence des fréquences réelles vers les probabilités théoriques."
    )

    choix_simulation = st.radio(
        "Choisissez l'élément à simuler en masse :",
        options=["Dé (6 faces)", "Carte (Valeurs)", "Carte (Couleurs)"],
        horizontal=True,
        key="radio_choix_sim_10000",
    )

    if st.button(
        "Lancer la grande simulation de 10 000 tirages",
        key="btn_lancer_10000_at1",
    ):
        n_sim = 10000
        fig, ax = plt.subplots(figsize=(7, 3.8), dpi=100)

        if choix_simulation == "Dé (6 faces)":
            resultats = [random.randint(1, 6) for _ in range(n_sim)]
            labels = ["1", "2", "3", "4", "5", "6"]
            freqs = [resultats.count(f) / n_sim for f in range(1, 7)]
            p_theo = 1.0 / 6.0

            ax.bar(labels, freqs, color="#3b82f6", edgecolor="#1d4ed8", width=0.5)
            ax.axhline(
                y=p_theo,
                color="#ef4444",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/6 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Dé libre : Répartition des fréquences sur {n_sim} lancers",
                fontweight="bold",
            )

        elif choix_simulation == "Carte (Valeurs)":
            valeurs = ["7", "8", "9", "10", "Valet", "Dame", "Roi", "As"]
            resultats = [random.choice(valeurs) for _ in range(n_sim)]
            freqs = [resultats.count(v) / n_sim for v in valeurs]
            p_theo = 1.0 / 8.0

            ax.bar(valeurs, freqs, color="#ec4899", edgecolor="#be185d", width=0.55)
            ax.axhline(
                y=p_theo,
                color="#10b981",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/8 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Jeu de 32 : Fréquence des Valeurs sur {n_sim} tirages",
                fontweight="bold",
            )

        elif choix_simulation == "Carte (Couleurs)":
            couleurs = ["Carreau", "Pique", "Coeur", "Trefe"]
            resultats = [random.choice(couleurs) for _ in range(n_sim)]
            freqs = [resultats.count(c) / n_sim for c in couleurs]
            p_theo = 1.0 / 4.0

            ax.bar(
                couleurs, freqs, color="#f59e0b", edgecolor="#b45309", width=0.45
            )
            ax.axhline(
                y=p_theo,
                color="#ef4444",
                linestyle="--",
                linewidth=1.5,
                label=f"Théorie (1/4 = {p_theo*100:.1f}%)",
            )
            ax.set_title(
                f"Jeu de 32 : Fréquence des Couleurs sur {n_sim} tirages",
                fontweight="bold",
            )

        ax.set_ylabel("Fréquence observée")
        ax.set_ylim(0, max(freqs) * 1.3)
        ax.legend(loc="upper right", fontsize=9)
        ax.grid(axis="y", linestyle=":", alpha=0.6)

        plt.tight_layout()
        st.pyplot(fig, clear_figure=True)


    if "at1_verrouille" not in st.session_state:
        st.session_state.at1_verrouille = False

    st.write("---")
    
    # Appel de la fonction : Modifiable ou Gelée dynamiquement au clic du bas
    afficher_questions_atelier1(verrouille=st.session_state.at1_verrouille)

        # =========================================================================
        # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML)
        # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 1")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at1 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de cet atelier.", 
        key="check_certif_at1_officiel",
        value=True if st.session_state.at1_verrouille else False,
        disabled=st.session_state.at1_verrouille
    )

    btn_clique_at1 = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", 
        key="btn_export_at1_premium", 
        use_container_width=True,
        disabled=st.session_state.at1_verrouille
    )

    if btn_clique_at1 and not st.session_state.at1_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at1:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        else:
            st.session_state.at1_verrouille = True
            st.rerun()

    if st.session_state.at1_verrouille:
        score_quiz = 0
        verdicts_quiz = {}
        attendus_quiz = {
            "q1": "0.75", "q2": "3/6 (1/2)", "q3": "12/32 (3/8)", "q4": "5/6", "q5": "0 et 1",
            "q6": "Elementaire", "q7": "2/6 (1/3)", "q8_at1": "8/32 (1/4)", "q9": "1", "q10": "0.7"
        }
        for q_id, q_correct in attendus_quiz.items():
            saisie_q = st.session_state.get(f"col_g_quiz_{q_id}", "Choisir...")
            if saisie_q == q_correct:
                score_quiz += 1
                verdicts_quiz[q_id] = "CORRECT"
            else:
                verdicts_quiz[q_id] = "INCORRECT"

        score_trous = 0
        verdicts_trous = {}
        attendus_trous = {
            "t1": "6", "t2": "1/6", "t3": "32", "t4": "4", "t5": "8",
            "t6": "4/32 (1/8)", "t7": "8/32 (1/4)", "t8": "Certain", "t9": "Impossible", "t10": "1"
        }
        for t_id, t_correct in attendus_trous.items():
            saisie_t = st.session_state.get(f"col_d_trous_{t_id}", "Choisir...")
            if saisie_t == t_correct:
                score_trous += 1
                verdicts_trous[t_id] = "CORRECT"
            else:
                verdicts_trous[t_id] = "INCORRECT"

        note_finale_sur_20 = score_quiz + score_trous

        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 1 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at1}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{note_finale_sur_20}</span> / 20</div>
            </div>

            <div class="sub-title">Detail des points acquis</div>
            <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                &bull; Questionnaire de fractions (QCM) : <strong>{score_quiz} / 10</strong><br>
                &bull; Synthese de texte (Texte a trous) : <strong>{score_trous} / 10</strong>
            </p>

            <div class="sub-title">Statistiques des lancers de l'élève en direct</div>
            <p style="font-size: 13px; color: #475569;">
                Total lancers de de : {st.session_state.get("de_total_lancers", 0)} (Derniere face : {st.session_state.get("dernier_de", "Aucun")})<br>
                Total tirages de cartes : {st.session_state.get("cartes_total_tirages", 0)} (Derniere carte : {st.session_state.get("derniere_carte", "Aucune")})
            </p>

            <div class="sub-title">Partie 2 : Questionnaire de fractions (QCM)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule de la Question</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        questions_mapping = {
            "q1": "Chances 3 sur 4", "q2": "Probabilite Nombre pair au de",
            "q3": "Probabilite d'obtenir une Figure", "q4": "Evenement contraire d'obtenir 6",
            "q5": "Bornes d'une probabilite", "q6": "Nature de l'evenement 7 de Pique",
            "q7": "Multiple de 3 avec le de cubique", "q8_at1": "Tirer un Roi OU un As",
            "q9": "De truque : Somme totale des probas", "q10": "Evenement contraire de P(A) = 0.3"
        }

        for idx_q, q_id in enumerate(["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8_at1", "q9", "q10"], 1):
            saisie = st.session_state.get(f"col_g_quiz_{q_id}", "Choisir...")
            attendu = attendus_quiz[q_id]
            verdict = verdicts_quiz.get(q_id, "INCORRECT")
            v_class = "status-correct" if verdict == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_q}</td><td>{questions_mapping[q_id]}</td><td>{saisie}</td><td>{attendu}</td><td style="text-align: center;" class="{v_class}">{verdict}</td></tr>
            """

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de texte (Texte a trous)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule du Trou</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        trous_mapping = {
            "t1": "Nombre de faces du de", "t2": "Probabilite face 6",
            "t3": "Nombre total de cartes", "t4": "Nombre de familles",
            "t5": "Nombre de cartes par famille", "t6": "Probabilite As",
            "t7": "Probabilite Coeur", "t8": "Evenement probabilite 1",
            "t9": "Evenement probabilite 0", "t10": "Somme probas faces de"
        }

        for idx_t, t_id in enumerate(["t1", "t2", "t3", "t4", "t5", "t6", "t7", "t8", "t9", "t10"], 1):
            saisie_t = st.session_state.get(f"col_d_trous_{t_id}", "Choisir...")
            attendu_t = attendus_trous[t_id]
            verdict_t = verdicts_trous.get(t_id, "INCORRECT")
            v_class_t = "status-correct" if verdict_t == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_t}</td><td>{trous_mapping[t_id]}</td><td>{saisie_t}</td><td>{attendu_t}</td><td style="text-align: center;" class="{v_class_t}">{verdict_t}</td></tr>
            """

        html_export_premium += """
            </table>
        </body>
        </html>
        """

        st.success("Bilan de l'Atelier 1 verrouille et genere avec succes !")
        nom_fichier_clean = f"Rapport_Evaluation_Atelier1_{n_eleve}_{c_eleve}"
        for car in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_fichier_clean = nom_fichier_clean.replace(car, "_")

        # Récupération automatique de la variable de contenu existante de l'Atelier 1
        contenu_rapport_at1 = globals().get("html_export", globals().get("html_content", globals().get("html_export_premium", "")))

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT SUR VOTRE ORDINATEUR",
            data=contenu_rapport_at1,
            file_name=f"{nom_fichier_clean}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.success("Le rapport d'evaluation technique complet a ete genere avec succes.")


with tab2:


    st.header("2. Jeux de hasard 2 : Roulette et Casino Machine")

    # =========================================================================
    # INITIALISATION UNIFIEE DES MEMOIRES DE SESSION
    # =========================================================================
    if "atelier2_valide" not in st.session_state:
        st.session_state.atelier2_valide = False
    if "roulette_stats_gains" not in st.session_state:
        st.session_state.roulette_stats_gains = {"GAGNE": 0, "PERDU": 0}
    if "roulette_dernier_numero" not in st.session_state:
        st.session_state.roulette_dernier_numero = 0
    if "roulette_derniere_couleur" not in st.session_state:
        st.session_state.roulette_derniere_couleur = "Vert"
    if "slot_dernier_tirage" not in st.session_state:
        st.session_state.slot_dernier_tirage = []
    if "slot_stats_gains" not in st.session_state:
        st.session_state.slot_stats_gains = {"JACKPOT": 0, "PETIT GAIN": 0, "PERDU": 0}
    # Séparation en deux colonnes maîtresses étanches
    col_master_roulette, col_master_slot = st.columns(2)

    # -------------------------------------------------------------------------
    # COLONNE DE GAUCHE : LA ROULETTE (TAPIS ET ROUE COMPLÈTEMENT ANIMÉE)
    # -------------------------------------------------------------------------
    with col_master_roulette:
        st.subheader("La Roulette de Casino")
        st.write("Misez sur une categorie ou sur un numero unique :")

        type_pari = st.radio(
            "Type de pari :",
            options=["Categorie", "Numero Unique"],
            horizontal=True,
            key="radio_type_pari_at2_final"
        )

        pari_selectionne = ""
        numero_choisi = 0

        if type_pari == "Categorie":
            pari_selectionne = st.selectbox(
                "Selectionnez votre groupe de numeros :",
                options=["Rouge", "Noir", "Pair (Even)", "Impair (Odd)", "Manque (1-18)", "Passe (19-36)"],
                key="selectbox_categorie_roulette"
            )
            texte_jeton = pari_selectionne
        else:
            numero_choisi = st.number_input(
                "Saisissez votre numero unique (0 a 36) :",
                min_value=0, max_value=36, value=7, step=1,
                key="num_input_roulette_at2_unique"
            )
            pari_selectionne = f"{numero_choisi}"
            texte_jeton = f"NUMERO {numero_choisi}"

        # Rendu du Tapis de mise horizontal bloqué en largeur
        html_tapis_regle = f"""
        <div style="background-color: #065f46; border: 4px solid #ffffff; border-radius: 8px; width: 480px; padding: 15px; font-family: Arial, sans-serif; box-shadow: 0 8px 16px rgba(0,0,0,0.3); margin-bottom: 20px;">
            <table style="width: 100%; border-collapse: collapse; text-align: center; color: #ffffff; font-weight: bold;">
                <tr style="height: 35px;">
                    <td rowspan="3" style="background-color: #16a34a; border: 2px solid #ffffff; width: 40px; font-size: 18px;">0</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">3</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">6</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">9</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">12</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">15</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">18</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">21</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">24</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">27</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">30</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">33</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">36</td>
                </tr>
                <tr style="height: 35px;">
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">2</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">5</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">8</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">11</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">14</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">17</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">20</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">23</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">26</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">29</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">32</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">35</td>
                </tr>
                <tr style="height: 35px;">
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">1</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">4</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">7</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">10</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">13</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">16</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">19</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">22</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">25</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">28</td>
                    <td style="background-color: #0f172a; border: 2px solid #ffffff;">31</td>
                    <td style="background-color: #dc2626; border: 2px solid #ffffff;">34</td>
                </tr>
                <tr style="height: 30px; font-size: 11px;">
                    <td></td>
                    <td colspan="4" style="border: 2px solid #ffffff;">1st 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">2nd 12</td>
                    <td colspan="4" style="border: 2px solid #ffffff;">3rd 12</td>
                </tr>
                <tr style="height: 30px; font-size: 10px;">
                    <td></td>
                    <td colspan="2" style="border: 2px solid #ffffff;">1-18</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">EVEN</td>
                    <td colspan="2" style="background-color: #dc2626; border: 2px solid #ffffff;">ROUGE</td>
                    <td colspan="2" style="background-color: #0f172a; border: 2px solid #ffffff;">NOIR</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">ODD</td>
                    <td colspan="2" style="border: 2px solid #ffffff;">19-36</td>
                </tr>
            </table>
            <div style="text-align: center; margin-top: 15px;">
                <span style="background-color: #f59e0b; color: #0f172a; padding: 4px 15px; border-radius: 4px; font-size: 12px; font-weight: bold; border: 1px solid #ffffff;">
                    JETON : {texte_jeton.upper()}
                </span>
            </div>
        </div>
        """
        st.components.v1.html(html_tapis_regle, height=450)

        # Structure fixe de la roulette européenne
        ordre_cylindre = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        rouges_roulette = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        pas_angulaire = 360.0 / 37.0

        # ZONE DE L'ANIMATION INTERACTIVE
        placeholder_roue = st.empty()

        # 1. INITIALISATION DE SÉCURITÉ AU REPOS (DÈS LE DÉMARRAGE DU TP)
        if st.session_state.roulette_dernier_numero is None:
            fig_repos, ax_repos = plt.subplots(figsize=(4, 4), dpi=100)
            ax_repos.axis("off")
            fig_repos.patch.set_facecolor('#065f46')
            ax_repos.set_facecolor('#065f46')

            ax_repos.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
            ax_repos.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

            for idx_s, num_case in enumerate(ordre_cylindre):
                theta1 = idx_s * pas_angulaire
                theta2 = (idx_s + 1) * pas_angulaire
                c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                ax_repos.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))

                angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                ax_repos.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

            for idx_s in range(38):
                a_rad = np.radians(idx_s * pas_angulaire)
                ax_repos.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

            ax_repos.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
            ax_repos.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

            angle_zero_rad = np.radians((ordre_cylindre.index(0) * pas_angulaire) + (pas_angulaire / 2.0))
            ax_repos.add_patch(plt.Circle((1.32 * np.cos(angle_zero_rad), 1.32 * np.sin(angle_zero_rad)), radius=0.05, color="#ffffff", zorder=12))
            ax_repos.text(0, -2.2, "ROULETTE PRETE\nMisez sur le tapis puis lancez !", color="#ffffff", fontsize=10, fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", facecolor="#1e293b", edgecolor="#cbd5e1", lw=1.5), zorder=14)

            plt.tight_layout()
            with placeholder_roue:
                st.pyplot(fig_repos, clear_figure=True)

        # 2. DECLENCHEMENT DU BOUTON DE LANCER
        if st.button("LANCER LA ROULETTE", key="btn_lancer_roulette_officiel_at2", use_container_width=True):
            numero_tire = random.randint(0, 36)
            st.session_state.roulette_dernier_numero = numero_tire
            couleur_finale = "Vert" if numero_tire == 0 else ("Red" if numero_tire in rouges_roulette else "Black")
            st.session_state.roulette_derniere_couleur = couleur_finale

            # Animation de la bille en mouvement
            for frame in range(10):
                fig_anim, ax_anim = plt.subplots(figsize=(4, 4), dpi=100)
                ax_anim.axis("off")
                fig_anim.patch.set_facecolor('#065f46')
                ax_anim.set_facecolor('#065f46')

                ax_anim.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
                ax_anim.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

                for idx_s, num_case in enumerate(ordre_cylindre):
                    theta1 = idx_s * pas_angulaire
                    theta2 = (idx_s + 1) * pas_angulaire
                    c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                    ax_anim.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))
                    
                    angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                    ax_anim.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

                for idx_s in range(38):
                    a_rad = np.radians(idx_s * pas_angulaire)
                    ax_anim.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

                ax_anim.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
                ax_anim.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

                angle_bille_anim = np.radians(frame * 72.0)
                ax_anim.add_patch(plt.Circle((1.32 * np.cos(angle_bille_anim), 1.32 * np.sin(angle_bille_anim)), radius=0.06, color="#ffffff", zorder=12))

                plt.tight_layout()
                with placeholder_roue:
                    st.pyplot(fig_anim, clear_figure=True)
                time.sleep(0.08)

            # Analyse des gains unitaires
            victoire = False
            if type_pari == "Categorie":
                if pari_selectionne == "Rouge" and couleur_finale == "Red": victoire = True
                elif pari_selectionne == "Noir" and couleur_finale == "Black": victoire = True
                elif pari_selectionne == "Pair (Even)" and numero_tire != 0 and numero_tire % 2 == 0: victoire = True
                elif pari_selectionne == "Impair (Odd)" and numero_tire % 2 != 0: victoire = True
                elif pari_selectionne == "Manque (1-18)" and 1 <= numero_tire <= 18: victoire = True
                elif pari_selectionne == "Passe (19-36)" and 19 <= numero_tire <= 36: victoire = True
            else:
                if numero_tire == numero_choisi: victoire = True

            if victoire:
                st.session_state.roulette_stats_gains["GAGNE"] += 1
                st.session_state.roulette_verdict_texte = f"GAGNE ! (+ {35 if type_pari != 'Categorie' else 1} jetons)"
            else:
                st.session_state.roulette_stats_gains["PERDU"] += 1
                st.session_state.roulette_verdict_texte = "PERDU"

            # 3. TRACÉ EXCLUSIF DE LA ROULETTE FINALE GAGNANTE (ANTI-CLIGNOTEMENT CRITIQUE)
            fig_fin, ax_fin = plt.subplots(figsize=(4, 4), dpi=100)
            ax_fin.axis("off")
            fig_fin.patch.set_facecolor('#065f46')
            ax_fin.set_facecolor('#065f46')

            ax_fin.add_patch(plt.Circle((0, 0), radius=1.8, color="#3e2723", zorder=1))
            ax_fin.add_patch(plt.Circle((0, 0), radius=1.5, color="#1a0c00", zorder=2))

            index_case_gagnante = 0
            for idx_s, num_case in enumerate(ordre_cylindre):
                theta1 = idx_s * pas_angulaire
                theta2 = (idx_s + 1) * pas_angulaire
                if num_case == numero_tire:
                    index_case_gagnante = idx_s

                c_seg = "#16a34a" if num_case == 0 else ("#dc2626" if num_case in rouges_roulette else "#0f172a")
                ax_fin.add_patch(patches.Wedge((0, 0), r=1.5, theta1=theta1, theta2=theta2, width=0.35, facecolor=c_seg, edgecolor="none", zorder=3))

                angle_txt = np.radians(theta1 + pas_angulaire / 2.0)
                ax_fin.text(1.32 * np.cos(angle_txt), 1.32 * np.sin(angle_txt), f"{num_case}", color="#ffffff", fontsize=6, fontweight="bold", ha="center", va="center", rotation=(theta1 + pas_angulaire / 2.0) - 90, zorder=5)

            for idx_s in range(38):
                a_rad = np.radians(idx_s * pas_angulaire)
                ax_fin.plot([1.15 * np.cos(a_rad), 1.5 * np.cos(a_rad)], [1.15 * np.sin(a_rad), 1.5 * np.sin(a_rad)], color="#f59e0b", linewidth=1, zorder=4)

            ax_fin.add_patch(plt.Circle((0, 0), radius=1.1, color="#b5651d", zorder=6))
            ax_fin.add_patch(plt.Circle((0, 0), radius=0.8, color="#ffe082", zorder=7))

            angle_bille_fixe_rad = np.radians((index_case_gagnante * pas_angulaire) + (pas_angulaire / 2.0))
            ax_fin.add_patch(plt.Circle((1.32 * np.cos(angle_bille_fixe_rad), 1.32 * np.sin(angle_bille_fixe_rad)), radius=0.05, color="#ffffff", zorder=12))

            trad_c = "VERT" if numero_tire == 0 else ("ROUGE" if numero_tire in rouges_roulette else "NOIR")
            bg_badge = "#16a34a" if trad_c == "VERT" else ("#dc2626" if trad_c == "ROUGE" else "#0f172a")
            ax_fin.text(0, -2.2, f"NUMERO : {numero_tire} ({trad_c})\n{st.session_state.roulette_verdict_texte}", color="#ffffff", fontsize=10, fontweight="bold", ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", facecolor=bg_badge, edgecolor="#f59e0b", lw=1.5), zorder=14)
            
            plt.tight_layout()
            with placeholder_roue:
                st.pyplot(fig_fin, clear_figure=True)
        # =========================================================================
        # 4. COMPTEUR ET GRAPHIQUE EN DIRECT POUR LES LANCERS UNITAIRES DE LA ROULETTE
        # =========================================================================
        st.write("")
        fig_r, ax_r = plt.subplots(figsize=(4, 2.5), dpi=100)
        labels_r = ["GAGNE", "PERDU"]
        counts_r = [
            st.session_state.roulette_stats_gains.get("GAGNE", 0), 
            st.session_state.roulette_stats_gains.get("PERDU", 0)]
            
        ax_r.bar(labels_r, counts_r, color=["#10b981", "#ef4444"], edgecolor="#111827", width=0.4)
        ax_r.set_title("Bilan lancers unitaires", fontsize=9, fontweight="bold")
        ax_r.grid(axis="y", linestyle=":", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_r, clear_figure=True)

            # Ligne de séparation réglementaire avant la simulation
        st.write("---")

        # =========================================================================
        # 5. SIMULATION DE MASSE INTERACTIVE (10 000 TIRAGES SUR LE PARI EN COURS)
        # =========================================================================
        st.write("---")
        st.markdown("**Simulation de masse (10 000 tirages) :**")
        
        if type_pari == "Categorie":
            texte_pari_sim = f"la categorie '{pari_selectionne}'"
        else:
            texte_pari_sim = f"le Numero unique {numero_choisi}"
            
        st.write(f"Ce simulateur va tester 10 000 lancers consecutifs sur {texte_pari_sim}.")

        if st.button("Lancer la simulation (10 000 Roulettes)", key="btn_sim_10000_roulette_maitre", use_container_width=True):
            n_sim = 10000
            cpt_victoires = 0
            p_theorique = 18.0 / 37.0 if type_pari == "Categorie" else 1.0 / 37.0
            rouges_list = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]

            for _ in range(n_sim):
                tirage = random.randint(0, 36)
                victoire_sim = False
                
                if type_pari == "Categorie":
                    if tirage != 0:
                        is_rouge = tirage in rouges_list
                        if pari_selectionne == "Rouge" and is_rouge: victoire_sim = True
                        elif pari_selectionne == "Noir" and not is_rouge: victoire_sim = True
                        elif pari_selectionne == "Pair (Even)" and tirage % 2 == 0: victoire_sim = True
                        elif pari_selectionne == "Impair (Odd)" and tirage % 2 != 0: victoire_sim = True
                        elif pari_selectionne == "Manque (1-18)" and tirage <= 18: victoire_sim = True
                        elif pari_selectionne == "Passe (19-36)" and tirage > 18: victoire_sim = True
                else:
                    if tirage == numero_choisi: 
                        victoire_sim = True
                        
                if victoire_sim: 
                    cpt_victoires += 1

            fig_sim_r, ax_sim_r = plt.subplots(figsize=(4, 2.5), dpi=100)
            ax_sim_r.bar(["GAGNE", "PERDU"], [cpt_victoires/n_sim, (n_sim-cpt_victoires)/n_sim], color=["#10b981", "#1e293b"], edgecolor="#111827", width=0.45)
            ax_sim_r.axhline(y=p_theorique, color="#ef4444", linestyle="--", label=f"Theorie ({p_theorique*100:.1f}%)")
            ax_sim_r.set_ylim(0, 1.1)
            ax_sim_r.legend(loc="upper right", fontsize=7)
            plt.tight_layout()
            
            st.pyplot(fig_sim_r, clear_figure=True)
            st.write(f"Frequence obtenue : **{(cpt_victoires/n_sim)*100:.2f}%** ({cpt_victoires} victoires).")
 # -------------------------------------------------------------------------
    # COLONNE DE DROITE : LA SLOT MACHINE CONFIGURABLE
    # -------------------------------------------------------------------------
    with col_master_slot:
        st.markdown("<h3 style='text-align: center; color: #eab308; font-family: Arial; font-weight: bold;'>CASINO MACHINE</h3>", unsafe_allow_html=True)
        st.write("")

        # Curseurs de configuration dynamique de la machine
        n_rouleaux = st.slider("Nombre de rouleaux (colonnes) :", min_value=3, max_value=5, value=3, step=1, key="slider_slot_rouleaux")
        n_symboles = st.slider("Nombre de symboles disponibles :", min_value=4, max_value=8, value=7, step=1, key="slider_slot_symboles")
        st.write("")

        # BOUTON DU BRAS MÉCANIQUE EN TEXTE BRUT
        # BOUTON DU BRAS MÉCANIQUE EN TEXTE BRUT
        if st.button("ACTIONNER LE BRAS (SPIN)", key="btn_actionner_slot_premium", use_container_width=True):
            with st.spinner("Defilement des rouleaux mecaniques..."):
                placeholder_slot = st.empty()
                
                # Effet d'animation de rotation : les chiffres s'emballent
                for _ in range(5):
                    faux_tirage = [str(random.randint(1, n_symboles)) for _ in range(n_rouleaux)]
                    
                    # Construction propre du conteneur HTML global pour l'animation
                    html_animation = """
                    <div style="display: flex; justify-content: center; gap: 15px; margin: 20px 0;">
                    """
                    
                    for chiffre in faux_tirage:
                        html_animation += f"""
                        <div style="background-color: #27272a; border: 3px solid #eab308; border-radius: 12px; width: 80px; height: 120px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                            <span style="font-family: Arial, sans-serif; font-size: 48px; font-weight: bold; color: #a1a1aa;">{chiffre}</span>
                        </div>
                        """
                    
                    # Fermeture correcte du conteneur global APRES le dessin des chiffres
                    html_animation += "</div>"
                    
                    # CORRECTIF ABSOLU : On utilise st.components.v1.html pour forcer l'affichage graphique réel pendant le mouvement
                    with placeholder_slot:
                        st.components.v1.html(html_animation, height=140)
                    
                    time.sleep(0.10)
                
                placeholder_slot.empty()

            # Tirage réel basé sur la configuration de l'élève
            tirage_reel = [random.randint(1, n_symboles) for _ in range(n_rouleaux)]
            st.session_state.slot_dernier_tirage = tirage_reel

            # Calcul des règles de gains de la machine
            if len(set(tirage_reel)) == 1:
                st.session_state.slot_verdict = "JACKPOT !"
                st.session_state.slot_couleur_theme = "#eab308"
            elif len(set(tirage_reel)) < len(tirage_reel):
                st.session_state.slot_verdict = "PETIT GAIN"
                st.session_state.slot_couleur_theme = "#3b82f6"
            else:
                st.session_state.slot_verdict = "PERDU"
                st.session_state.slot_couleur_theme = "#ef4444"
            st.rerun()

        # RENDU FIXE DE LA MACHINE AU REPOS OU APRES UN TIRAGE (Calque sur l'image)
        if not st.session_state.get("slot_dernier_tirage"):
            affichage_chiffres = ["7" for _ in range(n_rouleaux)]
            verdict_actuel = "Appuyez sur le bras pour lancer !"
            couleur_cadre = "#eab308"
        else:
            affichage_chiffres = [str(x) for x in st.session_state.slot_dernier_tirage]
            verdict_actuel = st.session_state.slot_verdict
            couleur_cadre = st.session_state.slot_couleur_theme

        # Reconstruction propre et etanche du tableau fixe pour eviter l'affichage de code brut
        html_machine = """
        <div style="display: flex; justify-content: center; gap: 15px; margin: 10px 0;">
        """
        
        for chiffre in affichage_chiffres:
            html_machine += f"""
            <div style="background-color: #2e2e38; border: 4px solid {couleur_cadre}; border-radius: 14px; width: 90px; height: 135px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 16px rgba(0,0,0,0.4);">
                <span style="font-family: Arial, sans-serif; font-size: 56px; font-weight: bold; color: #ffffff; line-height: 1;">{chiffre}</span>
            </div>
            """
        
        html_machine += "</div>"

        # CORRECTIF ABSOLU : On force l'affichage graphique reel via st.components.v1.html
        st.components.v1.html(html_machine, height=160)

        # Affichage du bandeau de resultat inferieur
        st.markdown(
            f"""
            <div style='text-align: center; font-family: Arial, sans-serif; font-size: 18px; font-weight: bold; color: #ffffff; letter-spacing: 0.5px; margin-top: 15px;'>
                {verdict_actuel}
            </div>
            """,
            unsafe_allow_html=True
        )

        # COMPTEUR ET GRAPHIQUE EN DIRECT POUR LES SPINS UNITAIRES DE LA SLOT MACHINE
        if "slot_stats_gains" not in st.session_state:
            st.session_state.slot_stats_gains = {"JACKPOT": 0, "PETIT GAIN": 0, "PERDU": 0}

        # Synchronisation au repos après un lancer réel
        if st.session_state.get("slot_dernier_tirage"):
            v_s = st.session_state.slot_verdict
            if v_s == "JACKPOT !":
                st.session_state.slot_stats_gains["JACKPOT"] = st.session_state.slot_stats_gains.get("JACKPOT", 0) + 1
            elif v_s == "PETIT GAIN":
                st.session_state.slot_stats_gains["PETIT GAIN"] = st.session_state.slot_stats_gains.get("PETIT GAIN", 0) + 1
            else:
                st.session_state.slot_stats_gains["PERDU"] = st.session_state.slot_stats_gains.get("PERDU", 0) + 1
            # On vide l'état temporaire pour ne pas incrémenter en boucle au rechargement
            st.session_state.slot_dernier_tirage = []

        st.write("")
        fig_s, ax_s = plt.subplots(figsize=(4.5, 3), dpi=100)
        labels_s = ["JACKPOT", "PETIT GAIN", "PERDU"]
        counts_s = [
            st.session_state.slot_stats_gains.get("JACKPOT", 0),
            st.session_state.slot_stats_gains.get("PETIT GAIN", 0),
            st.session_state.slot_stats_gains.get("PERDU", 0)
        ]
        
        ax_s.bar(labels_s, counts_s, color=["#eab308", "#3b82f6", "#cbd5e1"], edgecolor="#1e293b", width=0.45)
        ax_s.set_title("Bilan cumulé de la Slot Machine", fontsize=10, fontweight="bold")
        ax_s.set_ylabel("Nombre de spins")
        ax_s.grid(axis="y", linestyle=":", alpha=0.5)
        plt.tight_layout()
        st.pyplot(fig_s, clear_figure=True)
        
        st.write("---")
        st.markdown("**Simulation de masse de la Slot Machine (10 000 lancers) :**")
        st.write(f"Ce simulateur va tester 10 000 spins avec votre configuration : **{n_rouleaux} rouleaux** et **{n_symboles} symboles**.")

        if st.button("Lancer la simulation (10 000 Spins)", key="btn_sim_10000_slot"):
            n_sim = 10000
            cpt_jackpot = 0
            cpt_petit_gain = 0
            cpt_perdu = 0

            # Calcul des probabilités théoriques réelles selon vos curseurs
            p_theorique_jackpot = 1.0 / (n_symboles ** (n_rouleaux - 1))

            # Simulation mathématique en boucle des 10 000 tirages
            for _ in range(n_sim):
                tirage_sim = [random.randint(1, n_symboles) for _ in range(n_rouleaux)]
                nb_uniques = len(set(tirage_sim))
                
                if nb_uniques == 1:
                    cpt_jackpot += 1
                elif nb_uniques < n_rouleaux:
                    cpt_petit_gain += 1
                else:
                    cpt_perdu += 1

            # Calcul des fréquences observées
            f_jackpot = cpt_jackpot / n_sim
            f_petit = cpt_petit_gain / n_sim
            f_perdu = cpt_perdu / n_sim

            # Tracé du graphique Matplotlib
            fig_sim_s, ax_sim_s = plt.subplots(figsize=(4.5, 3), dpi=100)
            labels_sim_s = ["JACKPOT", "PETIT GAIN", "PERDU"]
            freqs_sim_s = [f_jackpot, f_petit, f_perdu]

            ax_sim_s.bar(labels_sim_s, freqs_sim_s, color=["#eab308", "#3b82f6", "#cbd5e1"], edgecolor="#1e293b", width=0.5)
            ax_sim_s.axhline(y=p_theorique_jackpot, color="#ef4444", linestyle="--", linewidth=1.5, label=f"Theorie Jackpot ({p_theorique_jackpot*100:.3f}%)")
            
            ax_sim_s.set_title("Loi des Grands Nombres : Slot Machine", fontsize=9, fontweight="bold")
            ax_sim_s.set_ylabel("Frequence observee")
            ax_sim_s.set_ylim(0, max(freqs_sim_s) * 1.25)
            ax_sim_s.legend(loc="upper right", fontsize=7)
            ax_sim_s.grid(axis="y", linestyle=":", alpha=0.5)
            plt.tight_layout()

            # Rendu immédiat sous le visuel de la slot
            st.pyplot(fig_sim_s, clear_figure=True)
            st.write(f"Resultat final : **{cpt_jackpot} Jackpots** obtenus sur 10 000 spins (Frequence : **{f_jackpot*100:.3f}%**).")

    # =========================================================================
    # CONFIGURATION DES COLONNES DU QUIZ ET DU TEXTE A TROUS - ATELIER 2
    # =========================================================================
    if "at2_verrouille" not in st.session_state:
        st.session_state.at2_verrouille = False

    st.write("---")
    
    afficher_questions_atelier2(verrouille=st.session_state.at2_verrouille)

    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML)
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 2")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at2 = st.checkbox(
        "Je certifie avoir complete l'integralite des questionnaires de cet atelier.", 
        key="check_certif_at2_officiel",
        value=True if st.session_state.at2_verrouille else False,
        disabled=st.session_state.at2_verrouille
    )

    btn_clique = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", 
        key="btn_export_at2_premium", 
        use_container_width=True,
        disabled=st.session_state.at2_verrouille
    )

    if btn_clique and not st.session_state.at2_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at2:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        else:
            st.session_state.at2_verrouille = True
            st.rerun()

    if st.session_state.at2_verrouille:
        score_quiz_at2 = 0
        verdicts_quiz_at2 = {}
        attendus_quiz_at2 = {
            "q1_at2": "37", "q2_at2": "1/37", "q3_at2": "18/37", "q4_at2": "La case Zero", "q5_at2": "La probabilite theoretique",
            "q6_at2": "Nombres", "q7_at2": "1/343", "q8_at2": "Contraires (hors zero)", "q9_at2": "Forte", "q10_at2": "1/37"
        }
        for q_id, q_correct in attendus_quiz_at2.items():
            saisie_q = st.session_state.get(f"col_g_quiz_at2_{q_id}", "Choisir...")
            if saisie_q == q_correct:
                score_quiz_at2 += 1
                verdicts_quiz_at2[q_id] = "CORRECT"
            else:
                verdicts_quiz_at2[q_id] = "INCORRECT"

        score_trous_at2 = 0
        verdicts_trous_at2 = {}
        attendus_trous_at2 = {
            "t1_at2": "Vert", "t2_at2": "18", "t3_at2": "18", "t4_at2": "Nombres", "t5_at2": "0 et 1",
            "t6_at2": "Diminue", "t7_at2": "Rouge et Vert", "t8_at2": "Difficile", "t9_at2": "Impossible", "t10_at2": "Zero"
        }
        for t_id, t_correct in attendus_trous_at2.items():
            saisie_t = st.session_state.get(f"col_d_trous_at2_{t_id}", "Choisir...")
            if saisie_t == t_correct:
                score_trous_at2 += 1
                verdicts_trous_at2[t_id] = "CORRECT"
            else:
                verdicts_trous_at2[t_id] = "INCORRECT"

        note_finale_sur_20 = score_quiz_at2 + score_trous_at2

        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 2 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 20px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 30px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at2}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{note_finale_sur_20}</span> / 20</div>
            </div>

            <div class="sub-title">Detail des points acquis</div>
            <p style="font-size: 14px; background: white; padding: 12px; border-left: 4px solid #eab308;">
                &bull; Questionnaire de la roulette (QCM) : <strong>{score_quiz_at2} / 10</strong><br>
                &bull; Synthese de texte (Texte a trous) : <strong>{score_trous_at2} / 10</strong>
            </p>

            <div class="sub-title">Partie 2 : Questionnaire de la roulette (QCM)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule de la Question</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        for idx_q, q_id in enumerate(["q1_at2", "q2_at2", "q3_at2", "q4_at2", "q5_at2", "q6_at2", "q7_at2", "q8_at2", "q9_at2", "q10_at2"], 1):
            saisie = st.session_state.get(f"col_g_quiz_at2_{q_id}", "Choisir...")
            attendu = attendus_quiz_at2[q_id]
            verdict = verdicts_quiz_at2.get(q_id, "INCORRECT")
            v_class = "status-correct" if verdict == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_q}</td><td>Question {idx_q}</td><td>{saisie}</td><td>{attendu}</td><td style="text-align: center;" class="{v_class}">{verdict}</td></tr>
            """

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de texte (Texte a trous)</div>
            <table>
                <tr>
                    <th style="width: 50px;">N°</th>
                    <th>Intitule du Trou</th>
                    <th>Saisie Eleve</th>
                    <th>Valeur Attendue</th>
                    <th style="text-align: center;">Verdict</th>
                </tr>
        """

        for idx_t, t_id in enumerate(["t1_at2", "t2_at2", "t3_at2", "t4_at2", "t5_at2", "t6_at2", "t7_at2", "t8_at2", "t9_at2", "t10_at2"], 1):
            saisie_t = st.session_state.get(f"col_d_trous_at2_{t_id}", "Choisir...")
            attendu_t = attendus_trous_at2[t_id]
            verdict_t = verdicts_trous_at2.get(t_id, "INCORRECT")
            v_class_t = "status-correct" if verdict_t == "CORRECT" else "status-incorrect"
            html_export_premium += f"""
                <tr><td>{idx_t}</td><td>Trou {idx_t}</td><td>{saisie_t}</td><td>{attendu_t}</td><td style="text-align: center;" class="{v_class_t}">{verdict_t}</td></tr>
            """

        html_export_premium += """
            </table>
        </body>
        </html>
        """

        st.success("Bilan de l'Atelier 2 verrouille et genere avec succes !")
        nom_fichier_clean = f"Rapport_Evaluation_Atelier2_{n_eleve}_{c_eleve}"
        for car in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_fichier_clean = nom_fichier_clean.replace(car, "_")

        # Récupération automatique de la variable de contenu existante de l'Atelier 1
        contenu_rapport_at2 = globals().get("html_export", globals().get("html_content", globals().get("html_export_premium", "")))

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT SUR VOTRE ORDINATEUR",
            data=contenu_rapport_at2,
            file_name=f"{nom_fichier_clean}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.success("Le rapport d'evaluation technique complet a ete genere avec succes.")







with tab3:

    st.header("Atelier 3 - Tableau de probabilités")

    # Initialisation des variables d'etat specifiques a l'Atelier 3
    if "at3_verrouille" not in st.session_state:
        st.session_state.at3_verrouille = False

    # Menu deroulant pour le choix de la filiere
    filiere_choisie = st.selectbox(
        "Choisissez votre filiere professionnelle :",
        ["Conducteur Routier", "Maintenance des Vehicules", "Travaux Publics (TP)"],
        key="var_filiere_selectbox",
        disabled=st.session_state.at3_verrouille
    )
    btn_gen_at3 = st.button("GENERER UN NOUVEL EXERCICE", key="btn_generer_at3", disabled=st.session_state.at3_verrouille)

    if btn_gen_at3:
        if filiere_choisie == "Choisir...":
            st.error("Veuillez d'abord selectionner une filiere valide.")
        else:
            if "ordre_questions_at3" in st.session_state:
                del st.session_state["ordre_questions_at3"]
            
            # 1. TIRAGE SÉCURISÉ : D'abord les totaux marginaux pour garantir la cohérence
            p_A = round(random.uniform(0.40, 0.65), 2)
            p_B = round(random.uniform(0.35, 0.60), 2)
            
            p_Abar = round(1.00 - p_A, 2)
            p_Bbar = round(1.00 - p_B, 2)
            
            # 2. Tirage contrôlé de l'intersection : obligatoirement inférieure aux totaux
            max_possible = min(p_A, p_B) - 0.05
            p_A_et_B = round(random.uniform(0.10, max_possible), 2)
            
            # 3. Déduction mathématique exacte de toutes les autres cases (100% cohérent)
            p_A_et_Bbar = round(p_A - p_A_et_B, 2)
            p_Abar_et_B = round(p_B - p_A_et_B, 2)
            p_Abar_et_Bbar = round(p_Abar - p_Abar_et_B, 2)

            # Sauvegarde de la solution officielle stable
            st.session_state.solution_courante = {
                (0, 0): p_A_et_B,    (0, 1): p_A_et_Bbar,    (0, 2): p_A,
                (1, 0): p_Abar_et_B, (1, 1): p_Abar_et_Bbar, (1, 2): p_Abar,
                (2, 0): p_B,         (2, 1): p_Bbar,         (2, 2): 1.00
            }

            # Choix des 3 indices à donner à l'élève pour l'énoncé
            toutes_coords = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1)]
            st.session_state.at3_visible_coords = random.sample(toutes_coords, 3)

            noms_probabilites = {
                (0,0): "$P(A \\cap B)$", (0,1): "$P(A \\cap \\overline{{B}})$", (0,2): "$P(A)$",
                (1,0): "$P(\\overline{{A}} \\cap B)$", (1,1): "$P(\\overline{{A}} \\cap \\overline{{B}})$", (1,2): "$P(\\overline{{A}})$",
                (2,0): "$P(B)$", (2,1): "$P(\\overline{{B}})$"
            }

            c1, c2, c3 = st.session_state.at3_visible_coords
            val1 = st.session_state.solution_courante[c1]
            val2 = st.session_state.solution_courante[c2]
            val3 = st.session_state.solution_courante[c3]

            contextes = {
                "Conducteur Routier": {"A": "le camion roule a l'Euro 6 (eco)", "B": "le trajet est regional"},
                "Maintenance des Vehicules": {"A": "la panne est d'origine electrique", "B": "le vehicule est un utilitaire leger"},
                "Travaux Publics (TP)": {"A": "le chantier utilise une pelle hydraulique", "B": "le sol est rocheux"}
            }
            ctx = contextes.get(filiere_choisie, contextes["Conducteur Routier"])

            st.session_state.enonce_textuel_at3 = (
                f"[Enonce Filiere : {filiere_choisie}]\n\n"
                f"Soit l'evenement A : \"{ctx['A']}\" et l'evenement B : \"{ctx['B']}\".\n\n"
                f"Les enregistrements indiquent les 3 valeurs de probabilites suivantes :\n"
                f"- La probabilite {noms_probabilites[c1]} est de **{val1:.2f}**.\n"
                f"- La probabilite {noms_probabilites[c2]} est de **{val2:.2f}**.\n"
                f"- La probabilite {noms_probabilites[c3]} est de **{val3:.2f}**.\n\n"
                f"Exercice : Utilisez ces 3 valeurs pour completer la grille ci-dessous."
            )

            # Remise à blanc complète des saisies de l'étudiant
            for idx_cell in range(1, 10):
                st.session_state[f"cell_at3_{idx_cell}"] = ""
            
            st.session_state.at3_afficher_correction = False
            st.rerun()

    # Affichage de l'enonce courant s'il existe
    if "enonce_textuel_at3" in st.session_state:
        st.info(st.session_state.enonce_textuel_at3)
    else:
        st.warning("Veuillez cliquer sur le bouton ci-dessus pour generer votre enonce d'exercice.")

    st.write("---")
    
    # =========================================================================
    # PARTIE 1 : LA GRILLE INTERACTIVE VIDE A COMPLETER (TABLEAU A DOUBLE ENTREE)
    # =========================================================================
    st.subheader("Grille de probabilites croisees a completer")
    
    # 1. EN-TÊTE DES COLONNES DU TABLEAU (TITRES PROPRES)
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c1: st.markdown("<p style='font-weight:bold; color:#1e3a8a; text-align:center;'>Événement B</p>", unsafe_allow_html=True)
    with c2: st.markdown("<p style='font-weight:bold; color:#1e3a8a; text-align:center;'>Événement B̄</p>", unsafe_allow_html=True)
    with c3: st.markdown("<p style='font-weight:bold; color:#1e3a8a; text-align:center;'>TOTAL</p>", unsafe_allow_html=True)

    sol_at3 = st.session_state.get("solution_courante", {})
    afficher_corr_at3 = st.session_state.get("at3_afficher_correction", False)

    # 2. INJECTION CSS POUR PEINDRE LES BORDURES EN VERT OU ROUGE SANS TOUCHER AU TEXTE ELEVE
    def style_cellule_at3(cle_cell, val_attendue, tolerance=0.01):
        if not afficher_corr_at3:
            return
        saisie_brute = str(st.session_state.get(cle_cell, "")).strip()
        try:
            valeur_saisie = float(saisie_brute.replace(",", "."))
            is_correct = abs(valeur_saisie - val_attendue) < tolerance
        except ValueError:
            is_correct = False

        c_b = "#10b981" if is_correct else "#ef4444"
        c_f = "#e6f4ea" if is_correct else "#fce8e6"
        c_t = "#137333" if is_correct else "#c5221f"
        
        st.markdown(
            f"""
            <style>
                div[data-testid="stTextInput"]:has(input[id="{cle_cell}"]) input {{
                    border: 2px solid {c_b} !important;
                    background-color: {c_f} !important;
                    color: {c_t} !important;
                    font-weight: bold !important;
                    text-align: center !important;
                }}
            </style>
            """, 
            unsafe_allow_html=True
        )

    # 3. TRACÉ DES LIGNES COMPACTES (LES 9 CASES SONT BLANCHES ET ÉDITABLES)
    # Ligne 1 : Evenement A
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>Événement A</div>", unsafe_allow_html=True)
    with c1:
        st.text_input("A_B", value=st.session_state.get("cell_at3_1", ""), key="cell_at3_1", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_1", sol_at3.get((0, 0), 0.0))
    with c2:
        st.text_input("A_Bbar", value=st.session_state.get("cell_at3_2", ""), key="cell_at3_2", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_2", sol_at3.get((0, 1), 0.0))
    with c3:
        st.text_input("A_total", value=st.session_state.get("cell_at3_3", ""), key="cell_at3_3", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_3", sol_at3.get((0, 2), 0.0))

    # Ligne 2 : Evenement Abar
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>Événement Ā</div>", unsafe_allow_html=True)
    with c1:
        st.text_input("Abar_B", value=st.session_state.get("cell_at3_4", ""), key="cell_at3_4", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_4", sol_at3.get((1, 0), 0.0))
    with c2:
        st.text_input("Abar_Bbar", value=st.session_state.get("cell_at3_5", ""), key="cell_at3_5", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_5", sol_at3.get((1, 1), 0.0))
    with c3:
        st.text_input("Abar_total", value=st.session_state.get("cell_at3_6", ""), key="cell_at3_6", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_6", sol_at3.get((1, 2), 0.0))

    # Ligne 3 : Totaux horizontaux
    c0, c1, c2, c3 = st.columns([1.5, 1, 1, 1])
    with c0: st.markdown("<div style='background-color:#e2e8f0; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>TOTAL</div>", unsafe_allow_html=True)
    with c1:
        st.text_input("B_total", value=st.session_state.get("cell_at3_7", ""), key="cell_at3_7", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_7", sol_at3.get((2, 0), 0.0))
    with c2:
        st.text_input("Bbar_total", value=st.session_state.get("cell_at3_8", ""), key="cell_at3_8", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_8", sol_at3.get((2, 1), 0.0))
    with c3:
        st.text_input("Univers_total", value=st.session_state.get("cell_at3_9", ""), key="cell_at3_9", label_visibility="collapsed", disabled=st.session_state.at3_verrouille)
        if sol_at3: style_cellule_at3("cell_at3_9", 1.00)

    st.write("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
    
    # 4. BOUTON DE CORRECTION INTERMÉDIAIRE (ALLUME LE STYLE BORDURE SANS MODIFIER LA VALEUR TAPÉE)
    if st.button("VERIFIER LES REPONSES DU TABLEAU", key="btn_verifier_grille_at3", disabled=st.session_state.at3_verrouille, use_container_width=True):
        if "solution_courante" not in st.session_state:
            st.error("Veuillez d'abord generer un exercice avec le bouton en haut.")
        else:
            st.session_state.at3_afficher_correction = True
            st.rerun()
    # =========================================================================
    # MODULE DE NOTATION ET D'EXPORTATION EN PAGE WEB COMPATIBLE (HTML) - ATELIER 3
    # =========================================================================
    st.write("---")
    afficher_questions_atelier3(verrouille=st.session_state.at3_verrouille)
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 3")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at3 = st.checkbox(
        "Je certifie avoir complete l'integralite du tableau et des questionnaires de cet atelier.", 
        key="check_certif_at3_officiel_8pts",
        value=True if st.session_state.at3_verrouille else False,
        disabled=st.session_state.at3_verrouille
    )

    btn_clique_at3 = st.button(
        "VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", 
        key="btn_export_at3_premium_8pts", 
        use_container_width=True,
        disabled=st.session_state.at3_verrouille
    )

    if btn_clique_at3 and not st.session_state.at3_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Veuillez renseigner et valider votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at3:
            st.error("Action refusee : Vous devez cocher la case de certification avant de clore l'atelier.")
        elif "solution_courante" not in st.session_state:
            st.error("Action refusee : Veuillez d'abord generer un exercice en cliquant sur le bouton en haut.")
        else:
            st.session_state.at3_verrouille = True
            st.rerun()

    if st.session_state.at3_verrouille:
        sol = st.session_state.solution_courante
        
        # =========================================================================
        # 1. EVALUATION DE LA GRILLE FILTRÉE (8 POINTS MAXIMUM - 1 PT PAR CASE)
        # =========================================================================
        mapping_correction = {
            "cell_at3_1": ((0, 0), "P(A ∩ B)"), 
            "cell_at3_2": ((0, 1), "P(A ∩ B̄)"), 
            "cell_at3_3": ((0, 2), "P(A)"),
            "cell_at3_4": ((1, 0), "P(Ā ∩ B)"), 
            "cell_at3_5": ((1, 1), "P(Ā ∩ B̄)"), 
            "cell_at3_6": ((1, 2), "P(Ā)"),
            "cell_at3_7": ((2, 0), "P(B)"),     
            "cell_at3_8": ((2, 1), "P(B̄)")
        }
        score_tableau = 0
        verdicts_tableau = {}
        for key_state, (coordonnees, libelle) in mapping_correction.items():
            saisie_brute = st.session_state.get(key_state, "").strip()
            
            # RÈGLE ANTI-TRICHE : Si la case est laissée vide, elle vaut d'office 0 point
            if not saisie_brute:
                verdicts_tableau[key_state] = "INCORRECT (VIDE)"
                continue
                
            try:
                val_num = float(saisie_brute.replace(",", "."))
                if abs(val_num - float(sol[coordonnees])) <= 0.01:
                    score_tableau += 1
                    verdicts_tableau[key_state] = "CORRECT"
                else: 
                    verdicts_tableau[key_state] = "INCORRECT"
            except (ValueError, KeyError): 
                verdicts_tableau[key_state] = "INCORRECT"

        # =========================================================================
        # 2. EVALUATION DU QUIZ QCM HARMONISÉ (10 POINTS MAXIMUM)
        # =========================================================================
    if st.session_state.at3_verrouille:
        sol = st.session_state.solution_courante
        
        # 1. RÉCUPÉRATION DES VARIABLES DE L'ÉNONCÉ DU TABLEAU
        p_A_et_B = f"{sol[(0, 0)]:.2f}"
        p_Abar_et_Bbar = f"{sol[(1, 1)]:.2f}"
        p_A = f"{sol[(0, 2)]:.2f}"
        p_B = f"{sol[(2, 0)]:.2f}"
        p_Bbar = f"{sol[(2, 1)]:.2f}"
        p_Abar = f"{sol[(1, 2)]:.2f}"
        val_union1 = f"{sol[(0, 2)] + sol[(2, 0)] - sol[(0, 0)]:.2f}"
        val_union2 = f"{sol[(1, 2)] + sol[(2, 0)] - sol[(1, 0)]:.2f}"
        p_Abar_et_B = f"{sol[(1, 0)]:.2f}"
        p_A_et_Bbar = f"{sol[(0, 1)]:.2f}"

        # 2. DICTIONNAIRES DE VÉRIFICATION POUR LES COMPOSANTS
        attendus_q3_local = {
            "q1_at3": p_A_et_B, "q2_at3": p_Abar_et_Bbar, "q3_at3": p_A, "q4_at3": p_B, "q5_at3": p_Bbar,
            "q6_at3": val_union1, "q7_at3": p_Abar, "q8_at3": val_union2, "q9_at3": p_Abar_et_B, "q10_at3": p_A_et_Bbar
        }
        attendus_t3_local = {
            "t1_at3": "A", "t2_at3": "B", "t3_at3": p_A_et_B, "t4_at3": p_A, "t5_at3": p_B,
            "t6_at3": "1.00", "t7_at3": "contraire de A", "t8_at3": "marginale (globale)"
        }

        # 3. RECONSTRUCTION ET COMPILATION DES NOTES SUR 28 POINTS
        mapping_correction = {
            "cell_at3_1": (0, 0), "cell_at3_2": (0, 1), "cell_at3_3": (0, 2),
            "cell_at3_4": (1, 0), "cell_at3_5": (1, 1), "cell_at3_6": (1, 2),
            "cell_at3_7": (2, 0), "cell_at3_8": (2, 1)
        }
        score_tableau = 0
        verdicts_tableau = {}
        for key_state, coordonnees in mapping_correction.items():
            saisie_brute = str(st.session_state.get(key_state, "")).strip().replace(",", ".")
            try:
                if abs(float(saisie_brute) - float(sol[coordonnees])) <= 0.01:
                    score_tableau += 1
                    verdicts_tableau[key_state] = "CORRECT"
                else:
                    verdicts_tableau[key_state] = "INCORRECT"
            except:
                verdicts_tableau[key_state] = "INCORRECT"

        scr1_at3 = score_tableau
        scr2_at3 = sum([1 for qk, qv in attendus_q3_local.items() if st.session_state.get(f"col_g_quiz_at3_{qk.split('_')}") == qv])
        brut_trous = sum([1 for t_k, t_v in attendus_t3_local.items() if st.session_state.get(f"at3_{t_k.split('_')}") == t_v])
        scr3_at3 = round(brut_trous * (10 / 8), 2)
        total_scr_at3 = round(scr1_at3 + scr2_at3 + scr3_at3, 1)

        st.success(f"ATELIER 3 SCELLÉ | Eleve : {p_eleve} {n_eleve} ({c_eleve})")
        st.info(f"NOTE DU COMPTE-RENDU : {total_scr_at3} / 28")

        # 4. STRUCTURE MAÎTRE DU DOCUMENT D'EXPORT HTML
        html_export_premium = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 3 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
                .status-correct {{ color: #10b981; font-weight: bold; text-transform: uppercase; }}
                .status-incorrect {{ color: #ef4444; font-weight: bold; text-transform: uppercase; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1 style="margin: 0; font-size: 22px;">Professeur Laurent GALLET</h1>
                <p style="margin: 5px 0 0 0; opacity: 0.9;">Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="margin: 5px 0 0 0; opacity: 0.7; font-size: 12px;">Scelle le : {timestamp_at3}</p>
                <div class="score-badge">NOTE<br><span style="font-size: 32px;">{total_scr_at3}</span> / 28</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de compétences - Atelier 3</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                &bull; Partie 1 : Completion de la Grille (8 cellules) : <strong>{scr1_at3} / 8</strong><br>
                &bull; Partie 2 : Questionnaire Numerique (Quiz) : <strong>{scr2_at3} / 10</strong><br>
                &bull; Partie 3 : Synthese de Cours (Texte a trous) : <strong>{scr3_at3} / 10</strong>
            </p>

            <div class="sub-title">Partie 1 : Tableau de Contingence Croisee</div>
            <table>
                <tr><th>Cellule cible</th><th>Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr>
        """

        # Lignes automatiques de la Grille
        for k_cell, coor_v in mapping_correction.items():
            v_sai = st.session_state.get(k_cell, "")
            v_att = sol[coor_v]
            v_lbl = verdicts_tableau[k_cell]
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{k_cell}</td><td style='text-align:center;'>{v_sai}</td><td style='text-align:center;'>{v_att:.2f}</td><td class='{v_class}' style='text-align:center;'>{v_lbl}</td></tr>"

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 2 : Quiz de calculs et formules (10 Pts)</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th>Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr>
        """

        # Lignes automatiques du Quiz
        for idx_q, q_key in enumerate(["q1_at3", "q2_at3", "q3_at3", "q4_at3", "q5_at3", "q6_at3", "q7_at3", "q8_at3", "q9_at3", "q10_at3"], 1):
            saisie = st.session_state.get(f"col_g_quiz_at3_{q_key.split('_')}", "Choisir...")
            attendu = attendus_q3_local[q_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_premium += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de cours (Texte a trous - 10 Pts)</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th>Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align:center;">Verdict</th></tr>
        """

        # Lignes automatiques du Texte à trous
        for idx_t, t_key in enumerate(["t1_at3", "t2_at3", "t3_at3", "t4_at3", "t5_at3", "t6_at3", "t7_at3"], 1):
            saisie = st.session_state.get(f"at3_{t_key.split('_')}", "Choisir...")
            attendu = attendus_t3_local[t_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_premium += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_premium += """
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                Document officiel de controle statistique genere automatiquement &bull; Professeur Laurent GALLET
            </div>
        </body>
        </html>
        """
        st.success("Bilan de l'Atelier 3 verrouille et genere avec succes !")
        nom_fichier_clean = f"Rapport_Evaluation_Atelier3_{n_eleve}_{c_eleve}"
        for car in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_fichier_clean = nom_fichier_clean.replace(car, "_")


        contenu_rapport_at3 = globals().get("html_export", globals().get("html_content", globals().get("html_export_premium", "")))

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT SUR VOTRE ORDINATEUR",
            data=contenu_rapport_at3,
            file_name=f"{nom_fichier_clean}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.success("Le rapport d'evaluation technique complet a ete genere avec succes.")





with tab4:

    st.header("Atelier 4 - Arbre de probabilités")

    # Initialisation des variables d'etat specifiques a l'Atelier 3
    if "at4_verrouille" not in st.session_state:
        st.session_state.at4_verrouille = False

    col_cmd_at4, col_arbre_at4 = st.columns([1, 3])

        # -------------------------------------------------------------------------
        # PANNEAU DE COMMANDE DE GAUCHE (CADRE TECHNIQUE)
        # -------------------------------------------------------------------------
    with col_cmd_at4:
        # 1. Mémorisation et lecture de la filière sélectionnée en Session State
        cle_filiere_at4 = "var_filiere_selectbox_at4"
        if cle_filiere_at4 not in st.session_state:
            st.session_state[cle_filiere_at4] = "Choisir..."

        # Recherche de l'index pour figer la sélection lors du st.rerun()
        options_fil = ["Choisir...", "Conducteur Routier", "Maintenance", "Travaux Publics"]
        idx_fil_at4 = options_fil.index(st.session_state[cle_filiere_at4]) if st.session_state[cle_filiere_at4] in options_fil else 0

        filiere_arbre = st.selectbox(
            "Choisir la filiere :", 
            options=options_fil,
            index=idx_fil_at4,
            key="sb_filiere_at4_premium"
        )
        st.session_state[cle_filiere_at4] = filiere_arbre

        st.markdown(
            """<div style="background-color: #ffffff; border: 1px solid #cbd5e1; border-radius: 4px; padding: 10px; font-size: 12px; margin-bottom: 15px; color: #1e293b;">
            Selectionnez une filiere ci-dessus puis cliquez sur "Generer un exercice".
            </div>""", 
            unsafe_allow_html=True
        )

        col_btn_1, col_btn_2, col_btn_3 = st.columns(3)
        with col_btn_1:
            btn_gen_at4 = st.button("Generer un ex...", key="btn_at4_gen_opt", use_container_width=True)
        with col_btn_2:
            btn_corr_at4 = st.button("Corriger", key="btn_at4_corr_opt", use_container_width=True)
        with col_btn_3:
            btn_raz_at4 = st.button("Effacer tout", key="btn_at4_raz_opt", use_container_width=True)

        # 2. ACTIONS INDÉPENDANTES DES TROIS BOUTONS MAÎTRES (ALIGNEMENT 12 ESPACES)
        if btn_raz_at4:
            st.session_state.atelier4_valide = False
            st.session_state.at4_afficher_correction = False
            if "enonce_textuel_at4" in st.session_state:
                del st.session_state["enonce_textuel_at4"]
            if "at4_scenario" in st.session_state:
                del st.session_state["at4_scenario"]
            st.session_state[cle_filiere_at4] = "Choisir..."
            st.rerun()

        if btn_gen_at4:
            if "ordre_questions_at4" in st.session_state:
                del st.session_state["ordre_questions_at4"]
            if filiere_arbre == "Choisir...":
                st.error("Veuillez d'abord selectionner une filiere valide.")
            else:
                p_A = round(random.uniform(0.55, 0.75), 2)
                p_Abar = round(1.00 - p_A, 2)
                p_S_sachant_A = round(random.uniform(0.05, 0.15), 2)
                p_Sbar_sachant_A = round(1.00 - p_S_sachant_A, 2)
                p_S_sachant_B = round(random.uniform(0.18, 0.28), 2)
                p_Sbar_sachant_B = round(1.00 - p_S_sachant_B, 2)
                
                p_A_et_S = round(p_A * p_S_sachant_A, 4)
                p_A_et_Sbar = round(p_A * p_Sbar_sachant_A, 4)
                p_Abar_et_S = round(p_Abar * p_S_sachant_B, 4)
                p_Abar_et_Sbar = round(p_Abar * p_Sbar_sachant_B, 4)

                if round(p_A_et_S + p_A_et_Sbar + p_Abar_et_S + p_Abar_et_Sbar, 4) != 1.0000:
                    p_Abar_et_Sbar = round(1.0000 - (p_A_et_S + p_A_et_Sbar + p_Abar_et_S), 4)

                st.session_state.at4_scenario = {
                    "p_A": p_A, "p_A_bar": p_Abar,
                    "p_B_sachant_A": p_S_sachant_A, "p_B_bar_sachant_A": p_Sbar_sachant_A,
                    "p_B_sachant_A_bar": p_S_sachant_B, "p_B_bar_sachant_A_bar": p_Sbar_sachant_B,
                    "f1": p_A_et_S, "f2": p_A_et_Sbar, "f3": p_Abar_et_S, "f4": p_Abar_et_Sbar
                }

                contextes_at4 = {
                    "Conducteur Routier": {"A": "le camion roule a l'Euro 6 (eco)", "B": "le trajet subit un retard"},
                    "Maintenance": {"A": "la panne est d'origine electrique", "B": "la piece necessite un remplacement total"},
                    "Travaux Publics": {"A": "le chantier utilise une pelle hydraulique", "B": "le sol engendre une usure critique"}
                }
                ctx_at4 = contextes_at4[filiere_arbre]

                scenario_at4 = random.randint(1, 3)
                if scenario_at4 == 1:
                    texte_donnees_at4 = f"- La probabilite globale $P(A)$ est de {p_A:.2f}.\n- Sachant l'evenement A realise, la probabilite d'obtenir B vaut {p_S_sachant_A:.2f}.\n- Sachant l'evenement $\\overline{{A}}$ realise, la probabilite d'obtenir B vaut {p_S_sachant_B:.2f}."
                elif scenario_at4 == 2:
                    texte_donnees_at4 = f"- La probabilite globale de l'evenement contraire $P(\\overline{{A}})$ est de {p_Abar:.2f}.\n- La probabilite conditionnelle $P_A(B)$ vaut {p_S_sachant_A:.2f}.\n- La probabilite conditionnelle $P_{{\\overline{{A}}}}(\\overline{{B}})$ vaut {p_Sbar_sachant_B:.2f}."
                else:
                    texte_donnees_at4 = f"- La probabilite globale $P(A)$ est de {p_A:.2f}.\n- La probabilite de l'intersection finale $P(A \\cap B)$ est de {p_A_et_S:.4f}.\n- La probabilite conditionnelle $P_{{\\overline{{A}}}}(B)$ vaut {p_S_sachant_B:.2f}."

                st.session_state.enonce_textuel_at4 = (
                    f"[Enonce Filiere : {filiere_arbre}]\n\n"
                    f"Soit l'evenement A : \"{ctx_at4['A']}\" et l'evenement B : \"{ctx_at4['B']}\".\n\n"
                    f"Les releves d'atelier indiquent que :\n"
                    f"{texte_donnees_at4}\n\n"
                    f"Exercice : Utilisez ces informations pour completer l'arbre de probabilites ci-contre."
                )
                
                # Initialisation des cases memoires HTML lors d'une nouvelle generation
                for k_init in ["v1", "v2", "v3", "v4", "v5", "v6", "f1", "f2", "f3", "f4"]:
                    st.session_state[f"html_v_{k_init}"] = 0.0

                st.session_state.at4_afficher_correction = False
                st.session_state.atelier4_valide = False
                st.rerun()

        # REPOSITIONNEMENT DU BOUTON CORRIGER ICI (8 ESPACES POUR ETRE LU APRES LES INPUTS)
        if btn_corr_at4:
            verifier_et_marquer_atelier4()
            st.rerun()

        # 3. AFFICHAGE DE L'ÉNONCÉ STABILISÉ (8 ESPACES)
        if "enonce_textuel_at4" in st.session_state and st.session_state[cle_filiere_at4] != "Choisir...":
            st.info(st.session_state.enonce_textuel_at4)


    # -------------------------------------------------------------------------
    # GRAND COMPOSANT GRAPHIQUE DE DROITE : FUSION ETANCHE DES TRAITS ET INPUTS
    # -------------------------------------------------------------------------
    with col_arbre_at4:
        saisies_arbre_at4 = dessiner_arbre_atelier4(verrouille=st.session_state.get("at4_verrouille", False))

        
                # --- APPEL DE LA COMMANDE DE SÉPARATION EN DEUX COLONNES MAITRESSES ---
    st.write("---")
    col_double_quiz_at4, col_double_trous_at4 = st.columns(2)



    st.write("---")
    dict_quiz_at4, dict_trous_at4 = afficher_questions_atelier4(
        verrouille=st.session_state.get("at4_verrouille", False)
    )
        # =========================================================================
        # 2. DISPOSITIF DE SCELLÉ ET DE VALIDATION DEFINITIVE
        # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 4")

    if "at4_verrouille" not in st.session_state:
        st.session_state.at4_verrouille = False

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    date_heure_tp = st.session_state.get("tp_date_heure", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    case_certif_at4 = st.checkbox(
        "Je certifie avoir complete l'integralite de l'arbre et des questionnaires de l'Atelier 4.", 
        key="check_certif_at4_final_30pts", 
        disabled=st.session_state.at4_verrouille
    )
    
    if not st.session_state.at4_verrouille:
        if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_validation_definitive_at4_premium", use_container_width=True):
            if "at4_scenario" not in st.session_state:
                st.error("Action refusee : Veuillez d'abord generer un exercice en cliquant sur 'GENERER UN NOUVEL EXERCICE'.")
            elif not case_certif_at4:
                st.error("Action refusee : Vous devez cocher la case de certification.")
            else:
                sol = st.session_state.at4_scenario
                
                # Formatage des attendus textuels
                p_A = f"{sol.get('p_A', 0.0):.2f}"
                p_A_bar = f"{sol.get('p_A_bar', 0.0):.2f}"
                p_B_A = f"{sol.get('p_B_sachant_A', 0.0):.2f}"
                p_Bbar_A = f"{sol.get('p_B_bar_sachant_A', 0.0):.2f}"
                p_B_Abar = f"{sol.get('p_B_sachant_A_bar', 0.0):.2f}"
                p_Bbar_Abar = f"{sol.get('p_B_bar_sachant_A_bar', 0.0):.2f}"
                f1 = f"{sol.get('f1', 0.0):.4f}"
                f2 = f"{sol.get('f2', 0.0):.4f}"
                f3 = f"{sol.get('f3', 0.0):.4f}"
                f4 = f"{sol.get('f4', 0.0):.4f}"

                # --- PARTIE 1 : VALIDATION FILTRÉE DE L'ARBRE (10 POINTS MAXIMUM) ---
                mapping_arbre = {
                    "v_at4_1": (sol["p_A"], 0.01), "v_at4_2": (sol["p_A_bar"], 0.01),
                    "v_at4_3": (sol["p_B_sachant_A"], 0.01), "v_at4_4": (sol["p_B_bar_sachant_A"], 0.01),
                    "v_at4_5": (sol["p_B_sachant_A_bar"], 0.01), "v_at4_6": (sol["p_B_bar_sachant_A_bar"], 0.01),
                    "v_at4_f1": (sol["f1"], 0.001), "v_at4_f2": (sol["f2"], 0.001),
                    "v_at4_f3": (sol["f3"], 0.001), "v_at4_f4": (sol["f4"], 0.001)
                }
                
                score_at4_p1 = 0
                for key_a, (val_att_a, tol_a) in mapping_arbre.items():
                    sai_brute_a = str(st.session_state.get(key_a, "0.0")).strip()
                    # RÈGLE ANTI-TRICHE : Pas de points si la case est vide ou non modifiée
                    if not sai_brute_a or sai_brute_a in ["0.0", "0.00", "0.0000"]:
                        continue
                    try:
                        val_num_a = float(sai_brute_a.replace(",", "."))
                        if abs(val_num_a - val_att_a) < tol_a:
                            score_at4_p1 += 1
                    except:
                        pass

                # --- PARTIE 2 : QUIZ DE CALCULS (10 POINTS) ---
                attendus_q4 = {"q1_at4": p_A, "q2_at4": f1, "q3_at4": p_B_A, "q4_at4": p_A_bar, "q5_at4": p_Bbar_Abar, "q6_at4": f4, "q7_at4": p_Bbar_A, "q8_at4": f3, "q9_at4": "Multiplier", "q10_at4": "1.00"}
                score_at4_p2 = sum([1 for qk, qv in attendus_q4.items() if st.session_state.get(f"col_g_quiz_at4_{qk}") == qv])
                
                # --- PARTIE 3 : SYNTHÈSE DE COURS À TROUS (10 POINTS) ---
                attendus_t4 = {"t1_at4": "Branches", "t2_at4": p_A, "t3_at4": "1.00", "t4_at4": "Ā", "t5_at4": "conditionnelles", "t6_at4": p_B_A, "t7_at4": f1, "t8_at4": "conditionnelle", "t9_at4": "Chemin (Issue)", "t10_at4": "Hasard (Probabilites)"}
                score_at4_p3 = sum([1 for tk, tv in attendus_t4.items() if st.session_state.get(f"col_d_trous_at4_{tk}") == tv])
                
                st.session_state.score_at4_p1 = score_at4_p1
                st.session_state.score_at4_p2 = score_at4_p2
                st.session_state.score_at4_p3 = score_at4_p3
                st.session_state.score_final_at4 = score_at4_p1 + score_at4_p2 + score_at4_p3
                st.session_state.at4_verrouille = True
                st.rerun()

    # =========================================================================
    # 3. MOTEUR D'EXPORTATION PREMIUM ET CORRECTION INTÉGRALE HTML
    # =========================================================================
    if st.session_state.at4_verrouille:
        sol = st.session_state.get("at4_scenario", {})
        
        # 1. EXTRACTION ET SÉCURISATION CHIRURGICALE DES VARIABLES DE L'ARBRE (AT4)
        p_A = f"{sol.get('p_A', 0.0):.2f}"
        p_A_bar = f"{sol.get('p_A_bar', 0.0):.2f}"
        p_B_A = f"{sol.get('p_B_sachant_A', 0.0):.2f}"
        p_Bbar_A = f"{sol.get('p_B_bar_sachant_A', 0.0):.2f}"
        p_B_Abar = f"{sol.get('p_B_sachant_A_bar', 0.0):.2f}"
        p_Bbar_Abar = f"{sol.get('p_B_bar_sachant_A_bar', 0.0):.2f}"
        f1 = f"{sol.get('f1', 0.0):.4f}"
        f2 = f"{sol.get('f2', 0.0):.4f}"
        f3 = f"{sol.get('f3', 0.0):.4f}"
        f4 = f"{sol.get('f4', 0.0):.4f}"

        scr1 = st.session_state.get("score_at4_p1", 0)
        scr2 = st.session_state.get("score_at4_p2", 0)
        scr3 = st.session_state.get("score_at4_p3", 0)
        total_scr = st.session_state.get("score_final_at4", 0)
        
        st.success(f"ATELIER 4 SCELLÉ | Eleve : {p_eleve} {n_eleve} ({c_eleve})")
        st.info(f"NOTE DU COMPTE-RENDU : {total_scr} / 30")

        # 2. DICTIONNAIRES MAÎTRES DE COMPARAISON POUR L'ARBRE (AT4)
        attendus_q4_reel = {
            "q1_at4": p_A, "q2_at4": f1, "q3_at4": p_B_A, "q4_at4": p_A_bar, "q5_at4": p_Bbar_Abar,
            "q6_at4": f4, "q7_at4": p_Bbar_A, "q8_at4": f3, "q9_at4": "Multiplier", "q10_at4": "1.00"
        }
        attendus_t4_reel = {
            "t1_at4": "Branches", "t2_at4": p_A, "t3_at4": "1.00", "t4_at4": "Ā", "t5_at4": "conditionnelles",
            "t6_at4": p_B_A, "t7_at4": f1, "t8_at4": "conditionnelle", "t9_at4": "Chemin (Issue)", "t10_at4": "Hasard (Probabilites)"
        }

        # 3. STRUCTURE ET EN-TÊTE DU DOCUMENT HTML DE L'ATELIER 4
        html_export_premium_at4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 4 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
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
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {date_heure_tp}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{total_scr}</span> / 30</div>
            </div>

            <div class="sub-title">Recapitulatif des scores de compétences - Atelier 4</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #eab308; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                &bull; Partie 1 : Remplissage de l'Arbre Graphique : <strong>{scr1} / 10</strong><br>
                &bull; Partie 2 : Questionnaire Numerique (Quiz) : <strong>{scr2} / 10</strong><br>
                &bull; Partie 3 : Synthese de Cours (Texte a trous) : <strong>{scr3} / 10</strong>
            </p>

            <div class="sub-title">Partie 1 : Completion Numerique de l'Arbre</div>
            <table>
                <tr><th>Identifiant de la case</th><th style='text-align:center;'>Saisie Eleve</th><th style='text-align:center;'>Attendu</th><th style='text-align:center;'>Verdict</th></tr>
        """

        # Lignes dynamiques de l'arbre
        mapping_html_at4 = [
            ("v_at4_1", sol.get("p_A", 0.0), 2), ("v_at4_2", sol.get("p_A_bar", 0.0), 2), 
            ("v_at4_3", sol.get("p_B_sachant_A", 0.0), 2), ("v_at4_4", sol.get("p_B_bar_sachant_A", 0.0), 2), 
            ("v_at4_5", sol.get("p_B_sachant_A_bar", 0.0), 2), ("v_at4_6", sol.get("p_B_bar_sachant_A_bar", 0.0), 2), 
            ("v_at4_f1", sol.get("f1", 0.0), 4), ("v_at4_f2", sol.get("f2", 0.0), 4),
            ("v_at4_f3", sol.get("f3", 0.0), 4), ("v_at4_f4", sol.get("f4", 0.0), 4)
        ]
        for k_h, att_h, format_digits in mapping_html_at4:
            sai_h = str(st.session_state.get(k_h, "0.0")).strip()
            if not sai_h or sai_h in ["0.0", "0.00", "0.0000", ""]:
                verd_h = "INCORRECT (VIDE)"
            else:
                try:
                    val_h = float(sai_h.replace(",", "."))
                    tol_h = 0.001 if format_digits == 4 else 0.01
                    verd_h = "CORRECT" if abs(val_h - att_h) < tol_h else "INCORRECT"
                except:
                    verd_h = "INCORRECT"
            v_cl_h = "status-correct" if verd_h == "CORRECT" else "status-incorrect"
            att_f = f"{att_h:.4f}" if format_digits == 4 else f"{att_h:.2f}"
            html_export_premium_at4 += f"<tr><td>{k_h}</td><td style='text-align:center;'>{sai_h}</td><td style='text-align:center;'>{att_f}</td><td class='{v_cl_h}' style='text-align:center;'>{verd_h}</td></tr>"

        html_export_premium_at4 += """
            </table>
            <div class="sub-title">Partie 2 : Quiz de calculs et formules (10 Pts)</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align: center;">Verdict</th></tr>
        """
        
        # 4. INJECTION DES VERDICTS CORRIGÉS DU QUIZ DE L'ARBRE (AT4)
        for idx_q, q_key in enumerate(["q1_at4", "q2_at4", "q3_at4", "q4_at4", "q5_at4", "q6_at4", "q7_at4", "q8_at4", "q9_at4", "q10_at4"], 1):
            saisie = st.session_state.get(f"col_g_quiz_at4_{q_key.split('_')}", "Choisir...")
            attendu = attendus_q4_reel[q_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_premium_at4 += f"<tr><td>{idx_q}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_premium_at4 += """
            </table>
            <div class="sub-title">Partie 3 : Synthese de cours (Texte a trous - 10 Pts)</div>
            <table>
                <tr><th style="width: 50px;">N°</th><th style="text-align:center;">Saisie Eleve</th><th style="text-align:center;">Attendu</th><th style="text-align: center;">Verdict</th></tr>
        """
        
        # 5. INJECTION DES VERDICTS CORRIGÉS DES TROUS DE L'ARBRE (AT4)
        for idx_t, t_key in enumerate(["t1_at4", "t2_at4", "t3_at4", "t4_at4", "t5_at4", "t6_at4", "t7_at4", "t8_at4", "t9_at4", "t10_at4"], 1):
            saisie = st.session_state.get(f"col_d_trous_at4_{t_key.split('_')}", "Choisir...")
            attendu = attendus_t4_reel[t_key]
            v_lbl = "CORRECT" if str(saisie) == str(attendu) else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_premium_at4 += f"<tr><td>{idx_t}</td><td style='text-align:center;'>{saisie}</td><td style='text-align:center;'>{attendu}</td><td class='{v_class}' style='text-align: center;'>{v_lbl}</td></tr>"

        html_export_premium_at4 += """
            </table>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">
                Document officiel de controle statistique genere automatiquement &bull; Professeur Laurent GALLET
            </div>
        </body>
        </html>
        """
        st.success("Bilan de l'Atelier 4 verrouille et genere avec succes !")
        nom_fichier_clean = f"Rapport_Evaluation_Atelier4_{n_eleve}_{c_eleve}"
        for car in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_fichier_clean = nom_fichier_clean.replace(car, "_")


        contenu_rapport_at4 = globals().get("html_export", globals().get("html_content", globals().get("html_export_premium_at4", "")))

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT SUR VOTRE ORDINATEUR",
            data=contenu_rapport_at4,
            file_name=f"{nom_fichier_clean}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.success("Le rapport d'evaluation technique complet a ete genere avec succes.")


with tab5:
    st.header("Atelier 5 : Espérance Mathématique & Variance")
    
    # =========================================================================
    # RAPPEL DE COURS PRÉCIS (FORMAT LATEX)
    # =========================================================================
    st.markdown("""
    <div style="background-color: #f8fafc; border-left: 4px solid #1e3a8a; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
        <p style="font-weight: bold; color: #1e3a8a; margin-top: 0;">Rappel des Formules du Cours :</p>
        <ul>
            <li><strong>Somme des probabilités :</strong> $\sum p_i = p_1 + p_2 + p_3 = 1$</li>
            <li><strong>Espérance Mathématique (Valeur moyenne) :</strong> $E(X) = \sum x_i \cdot p_i = x_1p_1 + x_2p_2 + x_3p_3$</li>
            <li><strong>Variance (Indicateur de dispersion) :</strong> $V(X) = \sum (x_i)^2 \cdot p_i - [E(X)]^2$</li>
        </ul>
    </div>
    """,unsafe_allow_html=True)

    col_g_cmd_at5, col_d_table_at5 = st.columns([1.5, 3])

        # =========================================================================
        # PANNEAU DE CONTRÔLE GAUCHE (GÉNÉRATION & SCÉNARIOS DYNAMIQUES)
        # =========================================================================
    with col_g_cmd_at5:
            st.subheader("Configuration de la Loi")

            if "at5_verrouille" not in st.session_state:
                st.session_state.at5_verrouille = False

            filiere_at5 = st.selectbox(
                "Choisissez votre filiere professionnelle :",
                ["Conducteur Routier", "Maintenance des Vehicules", "Travaux Publics (TP)"],
                key="var_filiere_selectbox_at5",
                disabled=st.session_state.at5_verrouille
            )
            
            btn_gen_at5 = st.button("GENERER UN NOUVEL EXERCICE", key="btn_generer_at5", disabled=st.session_state.at5_verrouille)

            if btn_gen_at5:
                # 1. Nettoyage complet du cache anti-triche
                if "ordre_questions_at5" in st.session_state:
                    del st.session_state["ordre_questions_at5"]
                    
                for clean_q in ["q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10"]:
                    cle_cache = f"opts_at5_shuffled_{clean_q}"
                    if cle_cache in st.session_state:
                        del st.session_state[cle_cache]
                    st.session_state[f"col_g_quiz_at5_{clean_q}"] = "Choisir..."

                # 2. Tirage de probabilites coherentes (Somme = 1.00)
                p1 = round(random.uniform(0.18, 0.32), 2)
                p2 = round(random.uniform(0.35, 0.48), 2)
                p3 = round(1.00 - (p1 + p2), 2)

                # -------------------------------------------------------------------------
                # GENERATION ALEATOIRE CONFIGURÉE ET SÉCURISÉE DES VALEURS XI
                # -------------------------------------------------------------------------
                if filiere_at5 == "Conducteur Routier":
                    x1 = random.randint(5, 25)
                    x2 = random.randint(35, 70)
                    x3 = random.randint(85, 150)
                    ctx_txt = "Les variables xi representent les distances de livraison en km, et p_i la probabilite associee."
                    unite_txt = "km"
                elif filiere_at5 == "Maintenance des Vehicules":
                    x1 = random.choice([20, 30, 45])
                    x2 = random.choice([60, 75, 90])
                    x3 = random.choice([120, 150, 180])
                    ctx_txt = "Les variables xi representent la duree d'immobilisation en minutes, et p_i la probabilite associee."
                    unite_txt = "minutes"
                else:
                    x1 = random.randint(100, 300)
                    x2 = random.randint(400, 750)
                    x3 = random.randint(850, 1400)
                    ctx_txt = "Les variables xi representent le cout des consommables de chantier en euros, et p_i la probabilite associee."
                    unite_txt = "euros"

                # 3. CALCULS MATHEMATIQUES OFFICIELS EXACTS DE L'ATELIER 5
                e_x = round((x1 * p1) + (x2 * p2) + (x3 * p3), 2)
                sum_x2_p = (x1**2 * p1) + (x2**2 * p2) + (x3**2 * p3)
                v_x = round(sum_x2_p - (e_x**2), 4)

                # 4. SAUVEGARDE FORCEE DU SCENARIO DANS LA MEMOIRE DE SESSION
                st.session_state.at5_scenario = {
                    "x1": x1, "x2": x2, "x3": x3,
                    "p1": p1, "p2": p2, "p3": p3,
                    "E_X": e_x, "V_X": v_x, "sum_x2_p": sum_x2_p
                }

                # 5. REDACTION DE L'ENONCE DYNAMIQUE SANS EMOJI
                st.session_state.enonce_textuel_at5 = (
                    f"**Enonce de Session ({filiere_at5}) :**\n\n"
                    f"{ctx_txt}\n\n"
                    f"- Pour $x_1 = {x1}$ {unite_txt}, la probabilite est $p_1 = {p1:.2f}$.\n"
                    f"- Pour $x_2 = {x2}$ {unite_txt}, la probabilite est $p_2 = {p2:.2f}$.\n\n"
                    f"Exercice : Calculez la probabilite manquante $p_3$ sachant que la somme de toutes les issues vaut 1. Completez ensuite toutes les cases de la grille pour determiner l'esperance et la variance."
                )
                
                # 6. RESET TOTAL DE LA GRILLE POUR LA CONSERVER ENTIEREMENT VIDE AU DEPART
                for idx_clr in range(1, 10):
                    st.session_state[f"cell_at5_{idx_clr}"] = ""
                st.session_state["cell_at5_ex"] = ""
                st.session_state["cell_at5_vx"] = ""
                
                st.session_state.at5_afficher_correction = False
                st.rerun()

            # BOUTONS AUXILIAIRES DE CORRECTION ET DE LIVRET DE RAZ
            st.write("---")
            c_b1, c_b2 = st.columns(2)
            with c_b1:
                if st.button("Corriger l'exercice", key="btn_at5_corr_visuelle", disabled=st.session_state.at5_verrouille, use_container_width=True):
                    st.session_state.at5_afficher_correction = True
                    st.rerun()
            with c_b2:
                if st.button("Effacer tout", key="btn_at5_raz", disabled=st.session_state.at5_verrouille, use_container_width=True):
                    st.session_state.at5_afficher_correction = False
                    for idx_clr in range(1, 10): st.session_state[f"cell_at5_{idx_clr}"] = ""
                    st.session_state["cell_at5_ex"] = ""
                    st.session_state["cell_at5_vx"] = ""
                    st.rerun()

    # =========================================================================
    # INTÉGRATION DE L'ÉNONCÉ BLEU PLEIN ÉCRAN (SORTI DU WITH COL_G)
    # =========================================================================
    if "enonce_textuel_at5" in st.session_state:
        st.info(st.session_state.enonce_textuel_at5)
    else:
        st.warning("Veuillez choisir votre filiere et cliquer sur 'GENERER UN NOUVEL EXERCICE' pour afficher votre enonce.")

    st.write("---")

    # =========================================================================
    # GRILLE INTERACTIVE CENTRALE (DESSIN DE LA LOI EN TABLEAU DE DROITE)
    # =========================================================================
    with col_d_table_at5:
        st.subheader("Grille de calculs de la Loi de Probabilité")
        
        sol_at5 = st.session_state.get("at5_scenario", {})
        afficher_corr_at5 = st.session_state.get("at5_afficher_correction", False)

        def style_cellule_at5(cle_cell, val_attendue, tolerance=0.01):
            if not afficher_corr_at5: return
            saisie_brute = str(st.session_state.get(cle_cell, "")).strip()
            try:
                valeur_saisie = float(saisie_brute.replace(",", "."))
                is_correct = abs(valeur_saisie - val_attendue) < tolerance
            except: is_correct = False
            c_b = "#10b981" if is_correct else "#ef4444"
            c_f = "#e6f4ea" if is_correct else "#fce8e6"
            c_t = "#137333" if is_correct else "#c5221f"
            st.markdown(f'<style>div[data-testid="stTextInput"]:has(input[id="{cle_cell}"]) input {{ border: 2px solid {c_b} !important; background-color: {c_f} !important; color: {c_t} !important; font-weight: bold !important; text-align: center !important; }}</style>', unsafe_allow_html=True)

        # En-tête de la Loi dynamique selon le tirage
        ch0, ch1, ch2, ch3, ch4 = st.columns([1.5, 1, 1, 1, 1])
        with ch0: st.markdown("<p style='font-weight:bold; color:#1e3a8a; text-align:center;'>xi / pi</p>", unsafe_allow_html=True)
        with ch1: st.markdown(f"<p style='font-weight:bold; text-align:center;'>x1 = {sol_at5.get('x1', 0)}</p>", unsafe_allow_html=True)
        with ch2: st.markdown(f"<p style='font-weight:bold; text-align:center;'>x2 = {sol_at5.get('x2', 0)}</p>", unsafe_allow_html=True)
        with ch3: st.markdown(f"<p style='font-weight:bold; text-align:center;'>x3 = {sol_at5.get('x3', 0)}</p>", unsafe_allow_html=True)
        with ch4: st.markdown("<p style='font-weight:bold; color:#1e3a8a; text-align:center;'>TOTAL</p>", unsafe_allow_html=True)

        # Ligne des probabilités
        cl1_0, cl1_1, cl1_2, cl1_3, cl1_4 = st.columns([1.5, 1, 1, 1, 1])
        with cl1_0: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>P(X = xi)</div>", unsafe_allow_html=True)
        with cl1_1: 
            st.text_input("p1_in", value=st.session_state.get("cell_at5_1", ""), key="cell_at5_1", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_1", sol_at5["p1"])
        with cl1_2:
            st.text_input("p2_in", value=st.session_state.get("cell_at5_2", ""), key="cell_at5_2", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_2", sol_at5["p2"])
        with cl1_3: 
            st.text_input("p3_in", value=st.session_state.get("cell_at5_3", ""), key="cell_at5_3", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_3", sol_at5["p3"])
        with cl1_4: 
            st.text_input("tot_p_in", value=st.session_state.get("cell_at5_4", ""), key="cell_at5_4", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            style_cellule_at5("cell_at5_4", 1.00)

        # Ligne des produits xi * pi
        cl2_0, cl2_1, cl2_2, cl2_3, cl2_4 = st.columns([1.5, 1, 1, 1, 1])
        with cl2_0: st.markdown("<div style='background-color:#f1f5f9; padding:8px; border-radius:4px; font-weight:bold; text-align:center;'>xi * P(X=xi)</div>", unsafe_allow_html=True)
        with cl2_1: 
            st.text_input("x1p1_in", value=st.session_state.get("cell_at5_5", ""), key="cell_at5_5", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_5", round(sol_at5["x1"]*sol_at5["p1"], 2))
        with cl2_2: 
            st.text_input("x2p2_in", value=st.session_state.get("cell_at5_6", ""), key="cell_at5_6", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
        if sol_at5: style_cellule_at5("cell_at5_6", round(sol_at5["x2"]*sol_at5["p2"], 2))
        with cl2_3: 
            st.text_input("x3p3_in", value=st.session_state.get("cell_at5_7", ""), key="cell_at5_7", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_7", round(sol_at5["x3"]*sol_at5["p3"], 2))
        with cl2_4: 
            st.text_input("tot_ex_in", value=st.session_state.get("cell_at5_8", ""), key="cell_at5_8", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
            if sol_at5: style_cellule_at5("cell_at5_8", sol_at5["E_X"])

    # Blocs Espérance et Variance finaux
    st.write("<div style='margin-top:15px;'></div>", unsafe_allow_html=True)
    cv_1, cv_2 = st.columns(2)
    with cv_1:
        st.write("**Esperance Mathematique E(X) :**")
        st.text_input("ex_final", value=st.session_state.get("cell_at5_ex", ""), key="cell_at5_ex", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
        if sol_at5: style_cellule_at5("cell_at5_ex", sol_at5["E_X"])
    with cv_2:
        st.write("**Variance Geometrique V(X) :**")
        st.text_input("vx_final", value=st.session_state.get("cell_at5_vx", ""), key="cell_at5_vx", label_visibility="collapsed", disabled=st.session_state.at5_verrouille)
        if sol_at5: style_cellule_at5("cell_at5_vx", sol_at5["V_X"], tolerance=0.05)

    # =========================================================================
    # RE-INJECTION DES QUESTIONNAIRES MELANGES ET INVERSES SANS COPIE
    # =========================================================================
    st.write("---")
    dict_q5, dict_t5 = afficher_questions_atelier5(verrouille=st.session_state.at5_verrouille)

    # =========================================================================
    # VALIDATION DÉFINITIVE ET RAPPORT HTML TECHNIQUE /30 POINTS
    # =========================================================================
    st.write("---")
    st.subheader("Validation et Generation du Bilan Officiel - Atelier 5")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
    timestamp_at5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

    case_certif_at5 = st.checkbox(
        "Je certifie avoir complete l'integralite du tableau et des questionnaires de l'Atelier 5.", 
        key="check_certif_at5_officiel_30pts",
        disabled=st.session_state.at5_verrouille
    )

    btn_clique_at5 = st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_at5_official_30pts", use_container_width=True, disabled=st.session_state.at5_verrouille)

    if btn_clique_at5 and not st.session_state.at4_verrouille:
        if not st.session_state.get("verrouille", False):
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_at5:
            st.error("Action refusee : Cochez la case de certification.")
        elif "at5_scenario" not in st.session_state:
            st.error("Action refusee : Generez d'abord un exercice.")
        else:
            sol = st.session_state.at5_scenario
            
            # Partie 1 : Notation exclusive de la Grille (10 Pts)
            score_grille_at5 = 0
            mapping_at5 = {
                "cell_at5_1": sol["p1"], "cell_at5_2": sol["p2"], "cell_at5_3": sol["p3"], "cell_at5_4": 1.00,
                "cell_at5_5": sol["x1"]*sol["p1"], "cell_at5_6": sol["x2"]*sol["p2"], "cell_at5_7": sol["x3"]*sol["p3"],
                "cell_at5_8": sol["E_X"], "cell_at5_ex": sol["E_X"], "cell_at5_vx": sol["V_X"]
            }
            for k_s, v_s in mapping_at5.items():
                s_b = str(st.session_state.get(k_s, "")).strip()
                if not s_b or s_b in ["", "0.0", "0.00"]: continue  # Anti-triche strict
                try:
                    if abs(float(s_b.replace(",",".")) - float(v_s)) <= 0.05: score_grille_at5 += 1
                except: pass

            # Partie 2 : Quiz (10 Pts)
            e_x_f = f"{sol['E_X']:.2f}"
            v_x_f = f"{sol['V_X']:.4f}"
            attendus_q5_v = {"q1": e_x_f, "q2": v_x_f, "q3": "Invalide", "q4": "[E(X)]²", "q5": "Moyenne ponderee", "q6": "Multipliee par 2", "q7": "Soustraction a 1", "q8": "L'esperance E(X)", "q9": "Variance", "q10": "1.00"}
            score_quiz_at5 = sum([1 for qk, qv in attendus_q5_v.items() if st.session_state.get(f"col_g_quiz_at5_{qk}_at5") == qv])

            # Partie 3 : Trous (10 Pts)
            attendus_t5_v = {"t1": "Esperance", "t2": f"{sol['E_X']:.2f}", "t3": "Variance", "t4": "xi² * p_i", "t5": f"{sol['V_X']:.2f}"}
            brut_trous_at5 = sum([1 for tk, tv in attendus_t5_v.items() if st.session_state.get(f"at5_{tk}") == tv])
            score_trous_at5 = round(brut_trous_at5 * (10 / 5), 2)

            st.session_state.score_at5_p1 = score_grille_at5
            st.session_state.score_at5_p2 = score_quiz_at5
            st.session_state.score_at5_p3 = score_trous_at5
            st.session_state.score_final_at5 = round(score_grille_at5 + score_quiz_at5 + score_trous_at5, 1)
            st.session_state.at5_verrouille = True
            st.rerun()

    if st.session_state.at5_verrouille:
        sol = st.session_state.at5_scenario
        scr1 = st.session_state.get("score_at5_p1", 0)
        scr2 = st.session_state.get("score_at5_p2", 0)
        scr3 = st.session_state.get("score_at5_p3", 0)
        tot_s = st.session_state.get("score_final_at5", 0)

        st.success(f"ATELIER 5 SCELLÉ | Note : {tot_s} / 30")

        html_export_at5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Atelier 5 - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #1e3a8a; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
                .score-badge {{ position: absolute; top: 20px; right: 20px; background-color: #eab308; color: #1e293b; padding: 15px 25px; border-radius: 8px; font-size: 24px; font-weight: bold; text-align: center; border: 2px solid white; }}
                .sub-title {{ font-weight: bold; color: #475569; margin-top: 25px; text-transform: uppercase; font-size: 13px; border-bottom: 2px solid #cbd5e1; padding-bottom: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; margin-bottom: 20px; background: white; border-radius: 4px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                th {{ background-color: #0f172a; color: white; padding: 12px; font-size: 14px; text-align: left; }}
                td {{ padding: 12px; font-size: 13px; border-bottom: 1px solid #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="header-box">
                <h1>Professeur Laurent GALLET</h1>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_at5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s}</span> / 30</div>
            </div>
            <div class="sub-title">Recapitulatif des scores - Atelier 5</div>
            <p>&bull; Grille de calculs : <strong>{scr1} / 10</strong> | &bull; Quiz de cours : <strong>{scr2} / 10</strong> | &bull; Texte a trous : <strong>{scr3} / 10</strong></p>
            <div style="text-align: center; margin-top: 40px; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; padding-top: 15px;">Document officiel genere automatiquement &bull; Professeur Laurent GALLET</div>
        </body>
        </html>
        """
        
        st.success("Bilan de l'Atelier 5 verrouille et genere avec succes !")
        nom_fichier_clean = f"Rapport_Evaluation_Atelier5_{n_eleve}_{c_eleve}"
        for car in ["/", "\\", "*", "?", '"', "<", ">", "|", ":"]:
            nom_fichier_clean = nom_fichier_clean.replace(car, "_")


        contenu_rapport_at5 = globals().get("html_export", globals().get("html_content", globals().get("html_export_premium_at5", "")))

        st.download_button(
            label="CLIQUEZ ICI POUR ENREGISTRER LE RAPPORT SUR VOTRE ORDINATEUR",
            data=contenu_rapport_at5,
            file_name=f"{nom_fichier_clean}.html",
            mime="text/html",
            use_container_width=True
        )
        
        st.success("Le rapport d'evaluation technique complet a ete genere avec succes.")









































