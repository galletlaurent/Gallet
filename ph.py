
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application le pH",
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
st.title("Application le pH")
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
    "Définition du pH",
    "La mesure du pH",
    "Les produits acides",
    "Les produits basiques",
    "Les dosages pH-métrique",
    "Calcul du pH"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]



def afficher_atelier_mesure_ph(verrouille=False):
    """Affiche le Quiz et le Texte a trous de l'onglet 2 (La mesure du pH) sur deux colonnes."""
    import random

    questions_ph2_sources = [
        {"id": "qm1", "q": "Quel papier indicateur a ete invente au quatorzieme siecle a partir de lichens ?", "options": ["Le papier de tournesol", "Le papier pH moderne", "Le papier filtre standard"], "rep": "Le papier de tournesol"},
        {"id": "qm2", "q": "Quel inventeur americain a developpe le tout premier pH-metre electronique en 1934 ?", "options": ["Arnold Beckman", "Søren Sorensen", "Thomas Edison"], "rep": "Arnold Beckman"},
        {"id": "qm3", "q": "Pour quelle industrie fruitiere de Californie le premier pH-metre a-t-elle ete cree ?", "options": ["L'industrie du jus de citron", "La fermentation du vin", "La culture des pommes"], "rep": "L'industrie du jus de citron"},
        {"id": "qm4", "q": "Avec quoi doit-on rincer la sonde en verre d'un pH-metre entre deux mesures ?", "options": ["De l'eau distillee", "De l'eau du robinet", "De l'acide"], "rep": "De l'eau distillee"},
        {"id": "qm5", "q": "Quelle epice jaune vire de façon spectaculaire au rouge-brun en milieu basique ?", "options": ["Le curcuma", "Le poivre noir", "Le gingembre"], "rep": "Le curcuma"},
        {"id": "qm6", "q": "Quelle couleur prend l'extrait de chou rouge lorsqu'il rencontre un milieu neut (pH=7) ?", "options": ["Violet", "Rouge vif", "Jaune"], "rep": "Violet"},
        {"id": "qm7", "q": "Quelle boisson courante s'eclaircit en jaune pâle sous l'action d'un jus d'acide ?", "options": ["Le the noir", "Le cafe", "Le lait de vache"], "rep": "Le the noir"},
        {"id": "qm8", "q": "Que risque-t-on de faire si l'on frotte la membrane sensible de la sonde ?", "options": ["La rayer ou creer des charges parasites faussant la mesure", "La rendre basique", "La dissoudre"], "rep": "La rayer ou creer des charges parasites faussant la mesure"},
        {"id": "qm9", "q": "Le jus de mon fruit vire au vert sombre en milieu basique. De quel fruit s'agit-il ?", "options": ["La myrtille", "Le citron", "La banane"], "rep": "La myrtille"},
        {"id": "qm10", "q": "Comment appelle-t-on le nuancier de couleur de reference du papier pH ?", "options": ["L'echelle des teintes", "Le tableau periodique", "L'etalonnage"], "rep": "L'echelle des teintes"}
    ]

    if "ordre_quiz_tab2_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph2_sources)
        st.session_state.ordre_quiz_tab2_ph_aleatoire = questions_ph2_sources

    # Liste de synthese structuree a 4 elements
    if "champs_ph2_clean" not in st.session_state:
        st.session_state.champs_ph2_clean = [
            ("1. Le papier de .......... vire au rouge avec l'acide depuis le Moyen Âge.", ["Choisir...", "tournesol", "chou"], "tournesol", "ph2_t1"),
            ("2. L'acidimetre electronique de haute precision a ete invente par ..........", ["Choisir...", "Beckman", "Sorensen"], "Beckman", "ph2_t2"),
            ("3. Ce premier pH-metre a ete cree pour analyser le jus de ..........", ["Choisir...", "citron", "pomme"], "citron", "ph2_t3"),
            ("4. L'element sensible plonge dans le flacon est l'..........", ["Choisir...", "electrode", "agitateur"], "electrode", "ph2_t4"),
            ("5. Nettoyer la sonde demande un rincage systematique a l'eau ..........", ["Choisir...", "distillee", "salée"], "distillee", "ph2_t5"),
            ("6. Le jus de chou rouge vire au violet stable en milieu ..........", ["Choisir...", "neutre", "acide"], "neutre", "ph2_t6"),
            ("7. Le curcuma deploie une teinte rouge-brun brique en milieu ..........", ["Choisir...", "basique", "acide"], "basique", "ph2_t7"),
            ("8. Frotter la membrane de verre est interdit pour eviter la ..........", ["Choisir...", "rayure", "fusion"], "rayure", "ph2_t8"),
            ("9. L'infusion de the noir s'eclaircit nettement en presence d'un ..........", ["Choisir...", "acide", "alcalin"], "acide", "ph2_t9"),
            ("10. Garder l'extremite de la sonde active exige un stockage ..........", ["Choisir...", "humide", "sec"], "humide", "ph2_t10")
        ]

    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown("##### Quiz Technique, Historique et Vegetal (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_ph_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"ph_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthese de l'Atelier 2 (Texte a trous - 10 cases - 10 pts)")
        for ligne in st.session_state.champs_ph2_clean:
            enonce = ligne[0]
            choix = ligne[1]
            cle = ligne[-1]
            
            c_txt, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_txt: 
                st.write(enonce)
            with c_sel: 
                st.selectbox("", choix, key=f"{cle}_ph2_clean", disabled=verrouille, label_visibility="collapsed")




def afficher_atelier_definition_ph(verrouille=False):
    """Affiche le Quiz et le Texte a trous de l'onglet 1 (Definition du pH) sur deux colonnes."""
    import random

    # 1. Base de donnees des questions du Quiz (Sans emoj)
    questions_ph1_sources = [
        {"id": "qph1", "q": "Quel chimiste danois a invente la notion de pH en 1909 ?", "options": ["Søren Sorensen", "Antoine Lavoisier", "Svante Arrhenius"], "rep": "Søren Sorensen"},
        {"id": "qph2", "q": "Que signifie litteralement l'abreviation de pH introduite par Sorensen ?", "options": ["Potentiel Hydrogene", "Pression Hydrogene", "Pourcentage Hydrogene"], "rep": "Potentiel Hydrogene"},
        {"id": "qph3", "q": "Dans quel laboratoire industriel l'echelle de pH a-t-elle ete developpee pour la fermentation ?", "options": ["La brasserie Carlsberg", "Les usines Pasteur", "Les laboratoires Solvay"], "rep": "La brasserie Carlsberg"},
        {"id": "qph4", "q": "Comment qualifie-t-on une solution dont la valeur de pH est egale a 3,5 ?", "options": ["Acide", "Basique", "Neutre"], "rep": "Acide"},
        {"id": "qph5", "q": "Quelle formule chimique represente l'ion oxonium responsable de l'acidite ?", "options": ["H3O+", "OH-", "Cl-"], "rep": "H3O+"},
        {"id": "qph6", "q": "Quelle formule chimique represente l'ion hydroxyde responsable de la basicite ?", "options": ["OH-", "H3O+", "Na+"], "rep": "OH-"},
        {"id": "qph7", "q": "Si l'on ajoute un grand volume d'eau pure dans un acide, vers quelle valeur le pH se dirige-t-on ?", "options": ["7", "0", "14"], "rep": "7"},
        {"id": "qph8", "q": "Dans le modele moleculaire de l'ion oxonium, que represente la boule rouge centrale ?", "options": ["L'atome d'oxygene", "L'atome d'hydrogene", "La charge positive"], "rep": "L'atome d'oxygene"},
        {"id": "qph9", "q": "Combien d'atomes d'hydrogene (boules blanches) comporte l'ion oxonium H3O+ ?", "options": ["3 atomes", "2 atomes", "1 atome"], "rep": "3 atomes"},
        {"id": "qph10", "q": "Quel operateur mathematique est utilise devant la concentration pour calculer le pH ?", "options": ["Le logarithme negatif (-log)", "La racine carree", "La multiplication par 14"], "rep": "Le logarithme negatif (-log)"}
    ]

    if "ordre_quiz_tab1_ph_aleatoire" not in st.session_state:
        random.shuffle(questions_ph1_sources)
        st.session_state.ordre_quiz_tab1_ph_aleatoire = questions_ph1_sources

    # 2. INITIALISATION ET DÉCLARATION FORCEE DE LA LISTE DE SYNTHÈSE CONTRE LES KEYERROR
    if "champs_ph1_clean" not in st.session_state:
        st.session_state.champs_ph1_clean = [
            ("1. Le concept historique de pH a ete introduit par le chercheur ..........", ["Choisir...", "Sorensen", "Lavoisier"], "Sorensen", "ph1_t1"),
            ("2. Les initiales pH signifient le Potentiel .......... de la solution.", ["Choisir...", "Hydrogene", "Hydrate"], "Hydrogene", "ph1_t2"),
            ("3. Un milieu dont la valeur de pH est inferieure a 7 est ..........", ["Choisir...", "acide", "basique"], "acide", "ph1_t3"),
            ("4. Lorsque le pH est superieur a 7, la solution aqueuse est ..........", ["Choisir...", "basique", "neutre"], "basique", "ph1_t4"),
            ("5. L'egalite exacte pH = 7 definit la zone de neutralite de l'..........", ["Choisir...", "eau", "acide"], "eau", "ph1_t5"),
            ("6. Diluer une solution acide fait .......... sa valeur de pH vers 7.", ["Choisir...", "augmenter", "diminuer"], "augmenter", "ph1_t6"),
            ("7. L'ion oxonium H3O+ caracterise chimiquement l'..........", ["Choisir...", "acidite", "basicite"], "acidite", "ph1_t7"),
            ("8. L'atome d'oxygene de l'ion oxonium est modelise par une boule ..........", ["Choisir...", "rouge", "blanche"], "rouge", "ph1_t8"),
            ("9. Les trois hydrogenes sont representes par des boules ..........", ["Choisir...", "blanches", "noires"], "blanches", "ph1_t9"),
            ("10. Le calcul du pH repose sur l'utilisation mathematique du ..........", ["Choisir...", "logarithme", "calibre"], "logarithme", "ph1_t10")
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
        st.markdown("##### Synthese de l'Atelier 1 (Texte a trous - 10 cases - 10 pts)")
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
    st.header("Definition du pH")
    
    # --- FOCUS HISTORIQUE : SØREN SORENSEN ---
    st.subheader("Histoire des Sciences : L'invention du pH")
    st.write(
        "La notion de pH a ete inventee en 1909 par le chimiste danois Søren Sorensen "
        "alors qu'il dirigeait les laboratoires de la celebre brasserie Carlsberg a Copenhague.\n\n"
        "Cherchant un moyen precis de controler la fermentation de la biere et la qualite des proteines, "
        "il a eu l'idee de mesurer la concentration des ions hydrogene en solution. "
        "Il a introduit le terme de pH, qui signifie Potentiel Hydrogene.\n\n"
        "Quelques annees plus tard, en 1924, la formule moderne et definitive du pH a ete formalisee "
        "en fonction de la concentration en ions oxonium [H3O+] exprimee en moles par litre :\n\n"
        "**pH = -log [H3O+]**"
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET DÉFINITION ---
    st.subheader("L'Echelle de pH")
    st.write(
        "Le pH permet de connaître l’acidite d’une solution, il varie entre 0 et 14. "
        "Si le **0 <= pH < 7**, la solution est **acide**. Si le **pH = 7** la solution est **neutre**. "
        "Si **7 < pH <= 14** la solution est **basique**.\n\n"
        "Plus on dilue une solution plus le pH se rapproche de 7.\n\n"
        "Les ions responsables de l’acidite sont les **ions oxonium** (H+ ou H3O+).\n"
        "Les ions responsables de la basicite sont les **ions hydroxyde** (OH-)."
    )
    
    col_ph1, col_ph2 = st.columns(2)
    with col_ph1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre l'echelle de pH, on peut imaginer une caricature representant une balance chimique. "
            "Dans le camp de l'acidite (pH de 0 a 6), les petits personnages Oxonium (H3O+) sont ultra-majoritaires "
            "et font pencher la balance. Dans le camp de la basicite (pH de 8 a 14), ce sont les personnages Hydroxyde (OH-) "
            "qui dominent le terrain. A la neutralite exacte (pH = 7), c'est une zone de paix parfaite ou il y a "
            "autant d'Oxoniums que d'Hydroxydes, formant de l'eau pure."
        )
        try:
            st.image("caricature_ph.jpg", caption="Caricature de la balance entre acidite, neutralite et basicite")
        except Exception:
            st.warning("L'image 'caricature_ph.jpg' est introuvable.")

    with col_ph2:
        st.write("**Le schema scientifique et la loi**")
        st.write(
            "Sur un schema normalise, l'echelle de pH s'organise le long d'une frise de couleurs allant du rouge vif "
            "pour les acides forts, au vert pour les milieux neutres, jusqu'au violet fonce pour les bases fortes.\n\n"
            "La dilution d'une solution acide augmente son pH pour le rapprocher de 7, tandis que la dilution "
            "d'une solution basique diminue son pH pour le rapprocher egalement de 7. Diluer revient a calmer "
            "l'agressivite chimique en tendant vers la neutralite de l'eau."
        )
        try:
            st.image("echelle_ph.jpg", caption="Echelle scientifique normalisee du pH de 0 a 14")
        except Exception:
            st.warning("L'image 'echelle_ph.jpg' est introuvable.")
            
    st.divider()
    
    # --- FOCUS STRUCTURE MOLÉCULAIRE : L'ION OXONIUM ---
    st.subheader("Structure microscopique : L'ion oxonium H3O+")
    st.write(
        "L'ion oxonium, responsable de l'acidite, est une molecule d'eau (H2O) qui a capture un ion hydrogene (H+) "
        "supplementaire. Voici sa modelisation moleculaire tridimensionnelle :"
    )
    
    col_mol1, col_mol2 = st.columns([0.4, 0.6])
    with col_mol1:
        st.write(
            "**Donnees et Legendes Atomiques**"
        )
        col_leg1, col_leg2 = st.columns(2)
        with col_leg1: 
            st.caption("**Hydrogene (H)**\n\nSphere blanche\nM(H) = 1 g/mol")
        with col_leg2: 
            st.caption("**Oxygene (O)**\n\nSphere rouge\nM(O) = 16 g/mol")
            
        st.write(
            "**Formule chimique brute : H3O+**\n\n"
            "L'atome d'oxygene central etablit trois liaisons de type covalente simple "
            "avec trois atomes d'hydrogene repartis de façon trigonale pyramidale. "
            "Le signe plus en haut a droite indique une perte globale d'un electron."
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

    # Affichage du module de questions specifique au pH
    afficher_atelier_definition_ph(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 1")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier Definition du pH.",
        key="check_certif_ph1_final_net",
        disabled=verrou_at1,
    )

    # Bouton de validation pour bloquer et generer les notes du Tab 1
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_ph_official", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
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
                    attendu = ligne[2]
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

        st.success(f"ATELIER DEFINITION PH SCELLE | Note de session : {tot_s_t1:.1f} / 20")

        html_export_ph1 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Definition pH - {n_eleve}</title>
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


with tab2:
    st.header("La mesure du pH")
    
    # --- FOCUS HISTORIQUE : DU TOURNESOL A BECKMAN ---
    st.subheader("Histoire des Sciences : L'evolution de la mesure")
    st.write(
        "Bien avant l'invention des appareils electroniques, les alchimistes et chimistes utilisaient "
        "des substances naturelles pour reperer l'acidite. Le plus celebre est le **papier de tournesol**, "
        "invente au quatorzieme siecle par le medecin espagnol Arnaldus de Villa Nova a partir d'extraits de lichens. "
        "Ce papier devenait rouge au contact d'un acide et bleu en milieu basique, offrant le tout premier repere visuel.\n\n"
        "La grande revolution technologique a lieu en **1934** en Californie. Le chimiste **Arnold Beckman** "
        "invente le tout premier **pH-metre electronique** (alors appele acidimetre). "
        "Conçu a la demande d'un ingenieur de l'industrie des agrumes qui cherchait un moyen fiable de mesurer "
        "l'acidite du jus de citron sans que les pigments ne faussent la lecture visuelle, cet appareil integrait "
        "une electrode de verre robuste couplee a un amplificateur de courant. Cette invention a fait entrer la chimie "
        "dans l'ere moderne de la haute precision."
    )
    
    st.divider()
    
    # --- SECTION 1 : COURS OFFICIEL ET DISPOSITIFS ---
    st.subheader("Les outils modernes du laboratoire")
    st.write(
        "Pour determiner experimentalement la valeur du pH d'une solution aqueuse au laboratoire, "
        "on utilise principalement deux dispositifs aux precisions et aux fonctionnements differents :\n\n"
        "* **Le papier pH :** Il s'agit d'un rouleau de papier impregne de plusieurs indicateurs colores. "
        "Au contact d'une goutte de solution, le papier change instantanement de couleur. En comparant "
        "cette couleur avec le nuancier present sur le boîtier, on obtient une valeur entiere de pH (precision a l'unite).\n"
        "* **Le pH-metre :** C'est un appareil de mesure electronique compose d'une sonde (electrode de verre) "
        "reliee a un boîtier voltmetrique convertisseur. Apres etalonnage, la sonde plongee dans le liquide mesure "
        "le potentiel electrique induit par les ions oxonium et affiche une valeur decimale tres precise (precision au dixieme ou au centieme)."
    )
    
    col_mes1, col_mes2 = st.columns(2)
    with col_mes1:
        st.write("**Explication par la caricature**")
        st.write(
            "Pour comprendre la difference entre ces deux outils, on peut imaginer une caricature comparant "
            "une regle en bois de charpentier et un pied a coulisse digital de haute precision. "
            "Le papier pH est comme l'oeil humain qui estime une longueur a la louche selon des nuances de couleurs. "
            "Le pH-metre, lui, agit comme un compteur d'ions electronique ultra-sensible capable de scanner "
            "le milieu microscopique pour compter chaque particule d'acide au millieme pres."
        )
        try:
            st.image("caricature_mesure_ph.jpg", caption="Caricature de la precision : Estimation visuelle contre scan electronique")
        except Exception:
            st.warning("L'image 'caricature_mesure_ph.jpg' est introuvable.")

    with col_mes2:
        st.write("**Le schema scientifique et la loi**")
        st.write(
            "Sur un schema de montage normalise, la mesure au papier pH impose l'utilisation d'une coupelle "
            "et d'un agitateur en verre pour deposer une goutte sans contaminer le flacon d'origine.\n\n"
            "La mesure au pH-metre exige quant a elle une manipulation rigoureuse : l'electrode est extremement "
            "fragile. Elle doit obligatoirement etre rincee a l'eau distillee entre chaque mesure, essuyee "
            "delicatement avec un papier absorbant sans etre frottee, et conservee dans une solution de stockage humide."
        )
        try:
            st.image("circuit_mesure_ph.jpg", caption="Protocole experimental de mesure au papier pH et au pH-metre electronique")
        except Exception:
            st.warning("L'image 'circuit_mesure_ph.jpg' est introuvable.")
            
    st.divider()

    # --- FOCUS : LES INDICATEURS COLORÉS NATURELS ---
    st.subheader("Chimie vegetale : Les indicateurs colores naturels")
    st.write(
        "Certaines plantes et vegetaux de notre environnement contiennent des pigments naturels sensibles au pH, "
        "appeles anthocyanes. Ces molecules changent de structure geometrique et donc de couleur "
        "selon la concentration en ions oxonium du milieu. Voici 5 exemples incontournables :"
    )
    
    col_ind1, col_ind2 = st.columns(2)
    with col_ind1:
        st.write(
            "**Les 5 indicateurs vegetaux selectionnes :**\n"
            "* **Le chou rouge :** L'indicateur naturel le plus spectaculaire. Il passe du rouge vif en milieu tres acide (pH < 3), au violet (pH neutre), puis au bleu, au vert et enfin au jaune en milieu tres basique.\n"
            "* **Le the noir :** Sa solution initialement ambre s'eclaircit nettement et devient jaune pâle en presence d'un acide (comme le jus de citron) et fonce fortement en milieu basique.\n"
            "* **Le jus de myrtille :** Il arbore une coloration rouge intense dans un milieu acide et vire au vert-olive sombre des que le milieu devient basique.\n"
            "* **Les petales de rose rouge :** L'infusion de ces petales donne un liquide qui passe du rose fuchsia en milieu acide au bleu-vert en milieu basique.\n"
            "* **Le curcuma :** Cette epice jaune vif reste jaune en milieu acide et neutre, mais vire de façon tres nette au rouge-brun brique en milieu basique (pH > 8)."
        )
    with col_ind2:
        try:
            st.image("indicateurs_naturels.jpg", caption="Nuancier de coloration des extraits vegetaux selon le pH")
        except Exception:
            st.warning("L'image 'indicateurs_naturels.jpg' est introuvable.")

    st.divider()

    # --- SECTION 2 : ZONE DE EXERCICES AND VERROUILLAGE DE L'ATELIER 2 ---
    if "suite_verrouille_tab2_ph" not in st.session_state:
        st.session_state.suite_verrouille_tab2_ph = False
    verrou_at2 = st.session_state.suite_verrouille_tab2_ph

    # Affichage du module de questions specifique a la mesure et a l'histoire
    afficher_atelier_mesure_ph(verrouille=verrou_at2)
    
    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 2")
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier La mesure du pH.",
        key="check_certif_ph2_final_net",
        disabled=verrou_at2,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_ph_official", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_ph_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_ph_aleatoire:
                    reponse_eleve = st.session_state.get(f"ph_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            score_t2 = 0.0
            if "champs_ph2_clean" in st.session_state:
                for ligne in st.session_state.champs_ph2_clean:
                    cle = ligne[-1]
                    attendu = ligne
                    if st.session_state.get(f"{cle}_ph2_clean", "Choisir...") == attendu:
                        score_t2 += 1.0

            st.session_state.score_suite2_ph_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_ph_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2_ph = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2_ph = True
            st.rerun()

    # --- COMPILATION DU BILAN HTML POUR L'ONGLET 2 ---
    if st.session_state.get("suite_verrouille_tab2_ph", False):
        scr1_t2 = st.session_state.get("score_suite2_ph_p1", 0.0)
        scr2_t2 = st.session_state.get("score_suite2_ph_p2", 0.0)
        tot_s_t2 = st.session_state.get("score_final_suite2_ph", 0.0)
        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")

        st.success(f"ATELIER MESURE PH SCELLE | Note de session : {tot_s_t2:.1f} / 20")

        html_export_ph2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Mesure pH - {n_eleve}</title>
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
                <p>Atelier 2 : Techniques de mesure du pH, protocoles et histoire de la mesure</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s_t2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0284c7;">
                Note obtenue au Quiz Technique : <strong>{scr1_t2:.1f} / 10</strong><br>
                Note obtenue a la Synthese : <strong>{scr2_t2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s_t2:.1f} / 20</strong>
            </p>
            
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 1. Injection des lignes de correction du Quiz
        if "ordre_quiz_tab2_ph_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_ph_aleatoire, 1):
                saisie = st.session_state.get(f"ph_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_ph2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        # 2. Transition vers le second tableau pour le texte à trous
        html_export_ph2 += """
                </tbody>
            </table>
            
            <div class="sub-title">CORRECTION DETAILLEE DE LA SYNTHESE (TEXTE A TROUS)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Phrase de Cours completee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # 3. Injection des lignes de correction du texte à trous
        if "champs_ph2_clean" in st.session_state:
            for num, ligne in enumerate(st.session_state.champs_ph2_clean, 1):
                enonce_texte = ligne[0]
                attendu_texte = ligne[2]
                cle_variable = ligne[-1]
                
                saisie_texte = st.session_state.get(f"{cle_variable}_ph2_clean", "Choisir...")
                v_lbl_t = "CORRECT" if str(saisie_texte).strip() == str(attendu_texte).strip() else "INCORRECT"
                v_class_t = "status-correct" if v_lbl_t == "CORRECT" else "status-incorrect"
                
                html_export_ph2 += f"<tr><td>{num}</td><td>{enonce_texte}</td><td>{saisie_texte}</td><td>{attendu_texte}</td><td class='{v_class_t}'>{v_lbl_t}</td></tr>"

        # 4. Fermeture propre du document
        html_export_ph2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_ph2 = preparer_nom_fichier("Rapport_Mesure_pH").replace(".txt", ".html")
        st.download_button(
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 2 (.html)",
            data=html_export_ph2,
            file_name=nom_fichier_html_ph2,
            mime="text/html",
            use_container_width=True
        )



































