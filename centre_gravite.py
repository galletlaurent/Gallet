
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application centre de gravité",
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
st.title("Application centre de gravité")
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
    "Définition",
    "Centre de gravité simple",
    "Centre de gravité complexe",
    "Exemples"    
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]


def afficher_atelier_metiers_etanche(metier_selectionne, verrouille=False):
    """Gère le tirage aléatoire d'un scénario et affiche les schémas, QCM et textes à trous."""
    
    # BANQUE DES SCÉNARIOS ÉTANCHE (2 cas différents par métier)
    banque_cas = {
        "Transport Routier": [
            {
                "id_cas": "routier_A",
                "titre": "Scénario Camion-Citerne (Liquides)",
                "contexte": "Calcul du ballant et de l'effet de carène liquide sur un porteur. Ajustez le volume pour observer le déplacement du liquide.",
                "quiz": [
                    {"id": "rA1", "q": "Quel est le risque majeur lors du freinage d'une citerne compartimentée mal remplie ?", "options": ["Le déplacement du CG vers l'avant (délestage arrière)", "Une augmentation de la pression des pneus arrière", "Une baisse immédiate de la consommation"], "rep": "Le déplacement du CG vers l'avant (délestage arrière)"},
                    {"id": "rA2", "q": "Pour limiter le déplacement du centre de gravité dans les virages, on utilise :", "options": ["Des plaques antiroulis (cloisons brise-flots)", "Un limiteur de vitesse électronique", "Un châssis plus souple"], "rep": "Des plaques antiroulis (cloisons brise-flots)"}
                ],
                "trous": [
                    ("1. Le mouvement des liquides déplace le centre de ......... en virage.", ["Choisir...", "gravité", "pression"], "gravité", "mr_t1"),
                    ("2. Une citerne pleine est plus stable qu'une citerne ......... remplie.", ["Choisir...", "à moitié", "totalement"], "à moitié", "mr_t2")
                ]
            },
            {
                "id_cas": "routier_B",
                "titre": "Scénario Convoi Exceptionnel (Engins lourds)",
                "contexte": "Positionnement analytique d'une charge lourde sur une remorque porte-char pour équilibrer les essieux.",
                "quiz": [
                    {"id": "rB1", "q": "Si le centre de gravité de l'engin est placé trop en arrière de la flèche de la remorque :", "options": ["Il y a un risque de délestage de l'essieu moteur du tracteur", "Le camion freine beaucoup plus court", "Le châssis se courbe vers le bas"], "rep": "Il y a un risque de délestage de l'essieu moteur du tracteur"},
                    {"id": "rB2", "q": "Où doit se situer idéalement le CG de la charge par rapport au centre du train arrière ?", "options": ["Légèrement en avant du centre géométrique des essieux", "Exactement sur le pare-chocs arrière", "Le plus haut possible au-dessus du sol"], "rep": "Légèrement en avant du centre géométrique des essieux"}
                ],
                "trous": [
                    ("1. Un chargement trop haut augmente le risque de .........", ["Choisir...", "retournement", "crevaison"], "retournement", "mr_t3"),
                    ("2. Arrimer solidement bloque le déplacement du ......... pendant le transport.", ["Choisir...", "barycentre", "moteur"], "barycentre", "mr_t4")
                ]
            }
        ],
        "Travaux Publics": [
            {
                "id_cas": "tp_A",
                "titre": "Scénario Grue à tour (Équilibrage du contre-flèche)",
                "contexte": "Calcul du moment stabilisateur d'une grue face à une charge maximale de béton.",
                "quiz": [
                    {"id": "tpA1", "q": "Que se passe-t-il pour le CG global de la grue lorsque le chariot avance sur la flèche ?", "options": ["Le CG se déplace vers l'avant, augmentant le moment de basculement", "Le CG reste fixe au centre du mât", "Le contre-poids devient plus lourd"], "rep": "Le CG se déplace vers l'avant, augmentant le moment de basculement"},
                    {"id": "tpA2", "q": "Les blocs de béton à la base de la grue servent à :", "options": ["Abaisser le CG global pour ancrer la structure au sol", "Mesurer la hauteur de la tour", "Décorer la zone de chantier"], "rep": "Abaisser le CG global pour ancrer la structure au sol"}
                ],
                "trous": [
                    ("1. Pour rester stable, le moment résiduel doit être compensé par la .........", ["Choisir...", "vireuse", "base"], "base", "mtp_t1"),
                    ("2. Avancer le chariot éloigne le poids du mât, ce qui crée un ......... de force.", ["Choisir...", "bras de levier", "frottement"], "bras de levier", "mtp_t2")
                ]
            },
            {
                "id_cas": "tp_B",
                "titre": "Scénario Blindage de fouille (Poussée des terres)",
                "contexte": "Détermination du centre de poussée trapézoïdal pour l'installation de vérins hydrauliques.",
                "quiz": [
                    {"id": "tpB1", "q": "Pour une poussée des terres triangulaire (pression nulle en haut), où est le centre d'application ?", "options": ["Au 1/3 de la hauteur en partant de la base", "Exactement au milieu de la hauteur", "Tout en haut de la tranchée"], "rep": "Au 1/3 de la hauteur en partant de la base"},
                    {"id": "tpB2", "q": "Si les parois reçoivent une charge de nappe phréatique, le barycentre des forces :", "options": ["Se déplace vers le bas de la fouille", "Remonte à la surface", "S'annule complètement"], "rep": "Se déplace vers le bas de la fouille"}
                ],
                "trous": [
                    ("1. La terre exerce une pression hydrostatique dont le barycentre est au ......... inférieur.", ["Choisir...", "tiers", "quart"], "tiers", "mtp_t3"),
                    ("2. Les étais doivent soutenir la paroi au niveau du centre de ......... des forces.", ["Choisir...", "poussée", "torsion"], "poussée", "mtp_t4")
                ]
            }
        ],
        "Maintenance Industrielle": [
            {
                "id_cas": "maint_A",
                "titre": "Scénario Équilibrage de rotor de ventilation",
                "contexte": "Traitement analytique d'un balourd sur un extracteur d'air mécanique d'usine.",
                "quiz": [
                    {"id": "mA1", "q": "Un rotor mal équilibré signifie géométriquement que :", "options": ["Le centre de gravité ne coïncide pas avec l'axe de rotation", "La pièce est trop lourde pour le moteur", "Le diamètre extérieur n'est pas un cercle parfait"], "rep": "Le centre de gravité ne coïncide pas avec l'axe de rotation"},
                    {"id": "mA2", "q": "L'ajout d'une masse de correction à 180 degrés du défaut permet de :", "options": ["Ramener le centre de gravité sur l'axe de rotation", "Augmenter la vitesse de l'arbre mécanique", "Réduire la consommation électrique de moitié"], "rep": "Ramener le centre de gravité sur l'axe de rotation"}
                ],
                "trous": [
                    ("1. Le décalage du centre de masse provoque une force ......... centrifuge.", ["Choisir...", "tournante", "statique"], "tournante", "mm_t1"),
                    ("2. L'action corrective consiste à poser un contrepoids pour éliminer le .........", ["Choisir...", "balourd", "frottement"], "balourd", "mm_t2")
                ]
            },
            {
                "id_cas": "maint_B",
                "titre": "Scénario Pont Roulant (Chariot de levage)",
                "contexte": "Déplacement du centre de charge sur une poutre d'un hall industriel.",
                "quiz": [
                    {"id": "mB1", "q": "Où la poutre subit-elle la flexion maximale lorsque le chariot soulève une charge ?", "options": ["Lorsque le chariot est positionné au milieu de la portée", "Lorsque le chariot est garé contre un pilier de rive", "La position n'influence pas la flexion mécanique"], "rep": "Lorsque le chariot est positionné au milieu de la portée"},
                    {"id": "mB2", "q": "Les capteurs de surcharge mesurent la répartition du poids au niveau :", "options": ["Des galets de roulement d'extrémité", "Du crochet de levage uniquement", "Du câble de commande"], "rep": "Des galets de roulement d'extrémité"}
                ],
                "trous": [
                    ("1. Le déplacement de la charge modifie la réaction aux ......... du pont.", ["Choisir...", "appuis", "moteurs"], "appuis", "mm_t3"),
                    ("2. Calculer les moments permet d'éviter la rupture par ......... de la poutre.", ["Choisir...", "flexion", "traction"], "flexion", "mm_t4")
                ]
            }
        ],
        "Géomètre": [
            {
                "id_cas": "geo_A",
                "titre": "Scénario Division de parcelle irrégulière",
                "contexte": "Calcul du centre géométrique d'un polygone cadastral par relevé de coordonnées de bornes.",
                "quiz": [
                    {"id": "gA1", "q": "Pour trouver le centre géométrique (isobarycentre) d'un terrain polygonal, on effectue :", "options": ["La moyenne arithmétique des coordonnées de ses sommets", "Le produit des longueurs de tous les côtés", "La mesure de la diagonale la plus longue"], "rep": "La moyenne arithmétique des coordonnées de ses sommets"},
                    {"id": "gA2", "q": "Si la parcelle possède une forme en L, le centre géométrique calculé peut se situer :", "options": ["À l'extérieur des limites réelles du terrain", "Obligatoirement sur la borne principale", "Strictement au milieu du grand côté"], "rep": "À l'extérieur des limites réelles du terrain"}
                ],
                "trous": [
                    ("1. Le géomètre détermine l'isobarycentre à partir des coordonnées .........", ["Choisir...", "topographiques", "maritimes"], "topographiques", "mg_t1"),
                    ("2. Diviser une surface complexe nécessite une méthode de ......... analytique.", ["Choisir...", "triangulation", "peinture"], "triangulation", "mg_t2")
                ]
            },
            {
                "id_cas": "geo_B",
                "titre": "Scénario Profil de terrain (Remblais / Déblais)",
                "contexte": "Optimisation des mouvements de terre en équilibrant le centre de masse des déblais.",
                "quiz": [
                    {"id": "gB1", "q": "Pour équilibrer parfaitement un chantier de terrassement, le volume de déblai doit être :", "options": ["Égal au volume de remblai (barycentre des terres optimisé)", "Deux fois supérieur pour tasser le sol", "Totalement évacué en décharge externe"], "rep": "Égal au volume de remblai (barycentre des terres optimisé)"},
                    {"id": "gB2", "q": "La ligne neutre d'un profil en long représente la zone où :", "options": ["La hauteur de déblai est égale à la hauteur de remblai", "La terre est la plus rocheuse", "Les machines ne peuvent pas circuler"], "rep": "La hauteur de déblai est égale à la hauteur de remblai"}
                ],
                "trous": [
                    ("1. Éviter les transports inutiles consiste à lisser le cubage des .........", ["Choisir...", "terres", "plans"], "terres", "mg_t3"),
                    ("2. Le centre de masse du sol excavé définit le rayon de ......... moyen.", ["Choisir...", "rotation", "balayage"], "rotation", "mg_t4")
                ]
            }
        ]
    }

    # Tirage au sort anti-triche unique par session
    cle_session_cas = f"cas_attribue_{metier_selectionne.replace(' ', '_')}"
    if cle_session_cas not in st.session_state:
        st.session_state[cle_session_cas] = random.choice(banque_cas[metier_selectionne])
    
    cas = st.session_state[cle_session_cas]
    st.success(f"**Cas Pratique Assigné : {cas['titre']}**")
    st.write(f"*Contexte technique* : {cas['contexte']}")

    # --- BLOCK SCHÉMAS MATPLOTLIB DÉDIÉS ---
    fig, ax = plt.subplots(figsize=(6, 2.3))
    
    if cas["id_cas"] == "routier_A":
        ax.plot([-4, 4, 4, -4, -4], [-1, -1, 1, 1, -1], color="black", lw=2, label="Citerne")
        ax.fill_between([-4, 4], [-1, -1], [0.2, 0.2], color="skyblue", alpha=0.5, label="Liquide")
        ax.scatter(0, -0.4, color="red", marker="x", s=100, lw=2, label="CG")
    elif cas["id_cas"] == "routier_B":
        # RECTIFICATION : Coordonnées Y ajoutées [0, 0] pour la ligne de la remorque
        ax.plot([-5, 5], [0, 0], color="grey", lw=4, label="Remorque")
        ax.scatter([-4, 3, 4], [-0.5, -0.5, -0.5], color="black", s=120, label="Essieux")
        ax.bar([1.0], [1.5], width=1.8, color="orange", alpha=0.7, bottom=0, label="Charge")
    elif cas["id_cas"] == "tp_A":
        ax.plot([0, 0], [0, 3.5], color="black", lw=4, label="Mât")
        ax.plot([-2, 5], [3.5, 3.5], color="blue", lw=3, label="Flèche")
        # RECTIFICATION ICI : utilisation de markersize au lieu de s
        ax.plot([-1.8], [3.5], color="grey", marker="s", markersize=15)
        ax.scatter(3.0, 3.5, color="red", s=100, label="Benne")
    elif cas["id_cas"] == "tp_B":
        ax.fill_between([-3, -2], [-2, -2], [2, 2], color="brown", alpha=0.4)
        ax.fill_between([2, 3], [-2, -2], [2, 2], color="brown", alpha=0.4, label="Terre")
        ax.plot([-2, -2], [-2, 2], color="black", lw=3)
        ax.plot([2, 2], [-2, 2], color="black", lw=3, label="Blindage")
        ax.scatter([0], [-0.66], color="red", marker="v", s=150, label="Centre de poussée")
    elif cas["id_cas"] == "maint_A":
        angles = np.linspace(0, 2*np.pi, 100)
        ax.plot(np.cos(angles), np.sin(angles), color="grey", linestyle="--")
        ax.scatter(0.6, 0.0, color="orange", s=120, label="Balourd")
        ax.scatter(-0.6, 0.0, color="blue", marker="o", s=100, label="Correction")
        ax.scatter(0, 0, color="black", marker="+", s=100, label="Axe")
    elif cas["id_cas"] == "maint_B":
        # RECTIFICATION : Coordonnées Y ajoutées [0, 0] pour le chemin de roulement et le chariot
        ax.plot([-5, 5], [0, 0], color="black", lw=3, label="Poutre")
        ax.scatter([1.0], [0], color="orange", marker="v", s=150, label="Chariot")
    elif cas["id_cas"] == "geo_A":
        poly_x = [10.0, 45.0, 30.0, 10.0]
        poly_y = [12.0, 15.0, 58.0, 12.0]
        ax.plot(poly_x, poly_y, color="green", lw=2, label="Bornes")
        ax.fill(poly_x, poly_y, color="green", alpha=0.1)
        ax.scatter([28.33], [28.33], color="red", marker="x", s=100, label="Barycentre")
    elif cas["id_cas"] == "geo_B":
        x_terr = np.linspace(-5, 5, 50)
        y_terr = 0.3 * np.sin(x_terr) * x_terr
        ax.plot(x_terr, y_terr, color="green", lw=2, label="Profil Sol")
        ax.axhline(0, color="black", linestyle=":", label="Niveau Projet")
        ax.fill_between(x_terr, y_terr, 0, where=(y_terr>0), color="orange", alpha=0.3, label="Déblai")
        ax.fill_between(x_terr, y_terr, 0, where=(y_terr<0), color="blue", alpha=0.3, label="Remblai")
    ax.legend(loc="upper right", fontsize=8)
    ax.axis("off")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown("---")

    # --- MISE EN PAGE SUR DEUX COLONNES ---
    col_q, col_t = st.columns(2)
    
    with col_q:
        st.markdown("##### QCM de Spécialité Professionnelle")
        for num, q_data in enumerate(cas["quiz"], 1):
            st.write(f"**{num}.** {q_data['q']}")
            cle_rep = f"met_quiz_ans_{cas['id_cas']}_{q_data['id']}"
            choix = ["Choisir..."] + q_data["options"]
            st.selectbox("", choix, key=cle_rep, disabled=verrouille, label_visibility="collapsed")

    with col_t:
        st.markdown("##### Synthèse Technique Métier (Texte à trous)")
        for enonce, options, _, cle_trou in cas["trous"]:
            c_enon, c_sel = st.columns([0.65, 0.35], vertical_alignment="bottom")
            with c_enon:
                st.write(enonce)
            with c_sel:
                st.selectbox("", options, key=f"met_trou_ans_{cas['id_cas']}_{cle_trou}", disabled=verrouille, label_visibility="collapsed")




                
def afficher_atelier_decomposition_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 1 (Décomposition) sur deux colonnes."""
    questions_decompo_sources = [
        {"id": "qd1", "q": "Les surfaces elementaires issues d'un decoupage geometrique doivent etre :", "options": ["Disjointes (sans chevauchement)", "Superposees", "De tailles identiques"], "rep": "Disjointes (sans chevauchement)"},
        {"id": "qd2", "q": "Si une figure est divisee en trois morceaux, l'aire totale est egale a :", "options": ["La somme des aires des trois morceaux", "Le produit des trois aires", "L'aire du plus grand morceau"], "rep": "La somme des aires des trois morceaux"},
        {"id": "qd3", "q": "Pour calculer l'aire d'un polygone en forme de L, on peut le separer en :", "options": ["Deux rectangles", "Deux triangles equilateraux", "Trois cercles"], "rep": "Deux rectangles"},
        {"id": "qd4", "q": "Quelle methode consiste a calculer une grande surface et a enlever le vide ?", "options": ["La methode par soustraction", "La methode par translation", "La methode par produit"], "rep": "La methode par soustraction"},
        {"id": "qd5", "q": "Lors d'un decoupage, comment trouve-t-on une longueur interne manquante ?", "options": ["Par addition ou soustraction des cotes connus", "En utilisant obligatoirement le nombre Pi", "En mesurant directement a la regle"], "rep": "Par addition ou soustraction des cotes connus"},
        {"id": "qd6", "q": "Un triangle rectangle issu d'un decoupage de base B et de hauteur H a pour aire :", "options": ["(B * H) / 2", "B * H", "B + H"], "rep": "(B * H) / 2"},
        {"id": "qd7", "q": "Le decoupage d'un polygone change-t-il la valeur de sa surface totale ?", "options": ["Non, l'aire reste strictement invariante", "Oui, la surface augmente legerement", "Oui, la surface diminue"], "rep": "Non, l'aire reste strictement invariante"},
        {"id": "qd8", "q": "Une figure complexe qui contient un demi-disque evide (creux) se traite par :", "options": ["Soustraction de l'aire du demi-disque", "Addition de l'aire du cercle complet", "Multiplication des deux surfaces"], "rep": "Soustraction de l'aire du demi-disque"},
        {"id": "qd9", "q": "Pour valider une decomposition, la somme des aires partielles doit etre :", "options": ["Egale a l'aire de la figure initiale", "Plus grande que la figure initiale", "Inferieure a la surface de depart"], "rep": "Egale a l'aire de la figure initiale"},
        {"id": "qd10", "q": "Un polygone regulier a 6 cotes (hexagone) se decomposera plus facilement en :", "options": ["6 triangles", "2 carres", "4 cercles"], "rep": "6 triangles"},
    ]

    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_decompo_sources)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_decompo_sources

    # Conservation de vos tuples d'origine à 4 éléments
    champs_d = [
        ("1. Découper sans laisser de vide crée une partition .........", ["Choisir...", "exhaustive", "incomplete"], "exhaustive", "dec_t1_final"),
        ("2. Les morceaux crees lors du decoupage ne doivent pas se ..........", ["Choisir...", "chevaucher", "aligner"], "chevaucher", "dec_t2_final"),
        ("3. L'aire d'un polygone est une grandeur strictement ...........", ["Choisir...", "additive", "multiplicative"], "additive", "dec_t3_final"),
        ("4. La methode par soustraction retire la surface de la zone ......", ["Choisir...", "vide", "pleine"], "vide", "dec_t4_final"),
        ("5. Un rectangle et un triangle forment souvent une figure ........", ["Choisir...", "composite", "reguliere"], "composite", "dec_t5_final"),
        ("6. Trouver une dimension inconnue se fait par ......... de segments.", ["Choisir...", "soustraction", "mesure"], "soustraction", "dec_t6_final"),
        ("7. Diviser une forme complexe facilite l'application des ....... de base.", ["Choisir...", "formules", "angles"], "formules", "dec_t7_final"),
        ("8. L'aire totale demeure .......... peu importe le decoupage choisi.", ["Choisir...", "invariante", "variable"], "invariante", "dec_t8_final"),
        ("9. Un trapeze peut se decomposer en un rectangle et deux ..........", ["Choisir...", "triangles", "disques"], "triangles", "dec_t9_final"),
        ("10. Assembler des sous-surfaces permet d'evaluer une extension.........", ["Choisir...", "totale", "partielle"], "totale", "dec_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Décomposition (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dec_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Décomposition (Texte à trous - 10 cases - 10 pts)")
        # RECTIFICATION ICI : Décompression des 4 éléments avec le symbole _
        for enonce, choix, _, cle in champs_d:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_simple_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 2 (Système Simple) sur deux colonnes."""
    ordre_fixe_tab2 = [
        {"id": "qs1", "q": "Si deux points ont exactement la même masse, où se situe le centre de gravité ?", "options": ["Exactement au milieu des deux points", "Confondu avec le premier point", "À l'extérieur du segment"], "rep": "Exactement au milieu des deux points"},
        {"id": "qs2", "q": "Plus la masse d'un point augmente par rapport aux autres, plus le centre de gravité G :", "options": ["S'éloigne de ce point", "Se rapproche de ce point", "Reste immobile"], "rep": "Se rapproche de ce point"},
        {"id": "qs3", "q": "Dans un champ de pesanteur uniforme, le centre de gravité se confond avec :", "options": ["Le centre de masse", "L'orthocentre", "Le point d'origine (0,0)"], "rep": "Le centre de masse"},
        {"id": "qs4", "q": "Quelle est la valeur de la masse totale M d'un système de 3 points (m1, m2, m3) ?", "options": ["M = m1 + m2 + m3", "M = m1 * m2 * m3", "M = (m1 + m2 + m3) / 3"], "rep": "M = m1 + m2 + m3"},
        {"id": "qs5", "q": "Si un système de 2 points possède une masse totale M, la coordonnée X_G est calculée par :", "options": ["(m1*x1 + m2*x2) / M", "(m1*x1 * m2*x2) / M", "(x1 + x2) / M"], "rep": "(m1*x1 + m2*x2) / M"}
    ]

    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(ordre_fixe_tab2)
        st.session_state.ordre_quiz_tab2_aleatoire = ordre_fixe_tab2

    champs_s = [
        ("1. Le principe physique fondamental repose sur la loi du .........", ["Choisir...", "levier", "frottement"], "sim_t1_final"),
        ("2. Quand toutes les masses sont égales, G est l'......... du système.", ["Choisir...", "isobarycentre", "orthocentre"], "sim_t2_final"),
        ("3. Le centre de gravité se déplace vers le point le plus .........", ["Choisir...", "lourd", "léger"], "sim_t3_final"),
        ("4. Pour trouver G, on fait la moyenne ......... des coordonnées.", ["Choisir...", "pondérée", "arithmétique"], "sim_t4_final"),
        ("5. La coordonnée Y_G utilise les masses et les positions .........", ["Choisir...", "verticales", "horizontales"], "sim_t5_final")
    ]

    col_quiz2, col_trous2 = st.columns(2)
    with col_quiz2:
        st.markdown("##### Quiz Centre de Gravité Simple (5 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"sim_at2_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous2:
        st.markdown("##### Synthèse Système Simple (Texte à trous - 5 cases - 10 pts)")
        for enonce, choix, cle in champs_s:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

def afficher_atelier_complexe_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 3 (Système Complexe) sur deux colonnes."""
    ordre_fixe_tab3 = [
        {"id": "qc1", "q": "Pour calculer le centre de gravité d'une plaque percée d'un trou, on utilise :", "options": ["La méthode par soustraction (masse négative)", "La méthode par produit vectoriel", "L'addition simple des surfaces"], "rep": "La méthode par soustraction (masse négative)"},
        {"id": "qc2", "q": "Dans l'espace (3D), le calcul du centre de gravité nécessite en plus la coordonnée :", "options": ["Z_G", "R_G", "L'angle Théta"], "rep": "Z_G"},
        {"id": "qc3", "q": "Si un système possède un axe de symétrie géométrique et massique, le centre G :", "options": ["Se situe obligatoirement sur cet axe", "Est rejeté à l'infini", "Se place au point le plus bas"], "rep": "Se situe obligatoirement sur cet axe"},
        {"id": "qc4", "q": "L'isobarycentre de 4 points disposés aux sommets d'un carré parfait se trouve :", "options": ["À l'intersection des diagonales", "Sur l'un des sommets", "À l'extérieur du carré"], "rep": "À l'intersection des diagonales"},
        {"id": "qc5", "q": "En ingénierie mécanique, un centre de gravité placé très bas garantit :", "options": ["Une meilleure stabilité au renversement", "Une vitesse de pointe plus élevée", "Une diminution du poids total"], "rep": "Une meilleure stabilité au renversement"}
    ]

    # Initialisation unique de l'ordre aléatoire en mémoire de session
    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(ordre_fixe_tab3)
        st.session_state.ordre_quiz_tab3_aleatoire = ordre_fixe_tab3

    champs_c = [
        ("1. Un solide évidé possède une zone géométrique appelée .........", ["Choisir...", "creuse", "pleine"], "comp_t1_final"),
        ("2. Multiplier les points massiques complexifie la ......... algébrique.", ["Choisir...", "sommation", "division"], "comp_t2_final"),
        ("3. Le comportement dynamique dépend de la distribution des .........", ["Choisir...", "masses", "volumes"], "comp_t3_final"),
        ("4. Une figure composite réunit plusieurs sous-surfaces .........", ["Choisir...", "élémentaires", "infinies"], "comp_t4_final"),
        ("5. Valider la position de G requiert une grande ......... de saisie.", ["Choisir...", "précision", "vitesse"], "comp_t5_final")
    ]

    col_quiz3, col_trous3 = st.columns(2)
    with col_quiz3:
        st.markdown("##### Quiz Centre de Gravité Complexe (5 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"comp_at3_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous3:
        st.markdown("##### Synthèse Système Complexe (Texte à trous - 5 cases - 10 pts)")
        for enonce, choix, cle in champs_c:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")        

def afficher_atelier_metiers_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier Métiers sur deux colonnes."""
    ordre_fixe_tab4 = [
        {"id": "qm1", "q": "En transport routier, un centre de gravité placé trop haut provoque principalement :", "options": ["Un risque accru de retournement en virage", "Une augmentation de la vitesse maximale", "Une usure prématurée des freins uniquement"], "rep": "Un risque accru de retournement en virage"},
        {"id": "qm2", "q": "En travaux publics, avant le levage d'une structure composite, l'ingénieur doit :", "options": ["Déterminer le centre de gravité pour positionner les élingues", "Augmenter la puissance de la grue au hasard", "Mesurer uniquement la hauteur du sol"], "rep": "Déterminer le centre de gravité pour positionner les élingues"},
        {"id": "qm3", "q": "En maintenance, un défaut d'équilibrage d'une pièce tournante (barycentre excentré) génère :", "options": ["Des vibrations destructrices", "Une baisse immédiate de tension électrique", "Une lubrification automatique"], "rep": "Des vibrations destructrices"},
        {"id": "qm4", "q": "Pour un géomètre, la décomposition en surfaces élémentaires permet de trouver le CG d'un terrain :", "options": ["De forme irrégulière (polygone quelconque)", "Uniquement triangulaire", "Parfaitement circulaire"], "rep": "De forme irrégulière (polygone quelconque)"}
    ]
    st.session_state.ordre_quiz_tab4 = ordre_fixe_tab4

    champs_m = [
        ("1. Le chauffeur routier doit répartir les charges pour stabiliser le .........", ["Choisir...", "camion", "moteur"], "met_t1_final"),
        ("2. En TP, la position des points d'ancrage dépend du centre de .........", ["Choisir...", "gravité", "pression"], "met_t2_final"),
        ("3. En maintenance, réaligner le barycentre élimine le ......... de balourd.", ["Choisir...", "phénomène", "calcul"], "met_t3_final"),
        ("4. Le géomètre utilise des relevés de coordonnées pour sa .........", ["Choisir...", "polygonation", "peinture"], "met_t4_final")
    ]

    col_quiz4, col_trous4 = st.columns(2)
    with col_quiz4:
        st.markdown("##### Quiz Applications Métiers (4 questions - 10 pts)")
        for idx, q_data in enumerate(ordre_fixe_tab4, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"met_at4_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous4:
        st.markdown("##### Synthèse Métiers (Texte à trous - 4 cases - 10 pts)")
        for enonce, choix, cle in champs_m:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")

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
    st.header("Définition et Principes Théoriques")
    
    # --- SECTION HISTORIQUE ---
    st.subheader("Contexte Historique")
    st.write(
        "Le concept de centre de gravité trouve ses racines dans l'Antiquité. C'est le savant grec "
        "**Archimède de Syracuse** (IIIe siècle av. J.-C.) qui en pose les bases géométriques et mathématiques "
        "dans son traité *Sur l'équilibre des figures planes*. Il définit le barycentre en démontrant "
        "la loi du levier. Plus tard, à l'époque moderne, des physiciens comme **Christiaan Huygens** et "
        "**Isaac Newton** ont généralisé ces principes pour les appliquer à la mécanique céleste et aux "
        "systèmes dynamiques complexes."
    )
    
    st.markdown("---")
    
    # --- SECTION PHYSIQUE ---
    st.subheader("Définition Physique")
    st.write(
        "Le **centre de gravité** d'un corps ou d'un système de points matériels correspond au "
        "point d'application de la résultante des forces de gravité qui s'exercent sur lui. Dans un "
        "champ de pesanteur uniforme (ce qui est le cas à la surface de la Terre pour des objets de taille "
        "courante), le centre de gravité se confond strictement avec le **centre de masse**."
    )
    
    st.markdown("---")
    
    # --- SECTION UTILITÉ ---
    st.subheader("Utilité pratique et domaines d'application")
    st.write(
        "Le calcul du centre de gravité est indispensable dans de nombreuses disciplines industrielles :"
    )
    st.write("- **Ingénierie aéronautique et automobile** : Déterminer la position du centre de gravité d'un avion ou d'une voiture de course est crucial pour garantir sa stabilité aérodynamique, sa tenue de route et éviter les risques de retournement.")
    st.write("- **Génie civil et architecture** : Pour concevoir des ponts, des bâtiments ou des grues, les ingénieurs doivent s'assurer que la ligne d'action du centre de gravité tombe à l'intérieur de la base d'appui (la surface de sustentation) afin d'éviter l'effondrement.")
    st.write("- **Biomécanique et sport** : L'analyse du centre de gravité du corps humain permet d'optimiser l'équilibre des athlètes (gymnastique, judo) ou d'améliorer l'ergonomie des prothèses.")

    st.markdown("---")
    
    # --- SECTION FORMULATION MATHÉMATIQUE ---
    st.subheader("Formulation Mathématique")
    st.write(
        "Pour un système composé de $N$ points matériels, où chaque point $A_i$ possède "
        "une masse $m_i$ et des coordonnées $(x_i, y_i)$, la masse totale $M$ du système est définie par :"
    )
    st.latex(r"M = \sum_{i=1}^{N} m_i = m_1 + m_2 + \dots + m_N")
    
    st.write("Les coordonnées $(X_G, Y_G)$ du centre de gravité $G$ sont données par les relations suivantes :")
    
    col_formule_x, col_formule_y = st.columns(2)
    with col_formule_x:
        st.info("**Coordonnée X_G**")
        st.latex(r"X_G = \frac{1}{M} \sum_{i=1}^{N} m_i x_i = \frac{m_1 x_1 + m_2 x_2 + \dots + m_N x_N}{m_1 + m_2 + \dots + m_N}")
    with col_formule_y:
        st.info("**Coordonnée Y_G**")
        st.latex(r"Y_G = \frac{1}{M} \sum_{i=1}^{N} m_i y_i = \frac{m_1 y_1 + m_2 y_2 + \dots + m_N y_N}{m_1 + m_2 + \dots + m_N}")


    st.write("---")        
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_atelier_decomposition_complet(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 1")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    # La case à cocher accède maintenant à la variable sans lever d'erreur
    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Décomposition.",
        key="check_certif_generalites_final_net",
        disabled=verrou_at1,
    )
    # --- 4. BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            score_t1 = sum(
                [
                    st.session_state.get("dec_t1_final") == "exhaustive",
                    st.session_state.get("dec_t2_final") == "chevaucher",
                    st.session_state.get("dec_t3_final") == "additive",
                    st.session_state.get("dec_t4_final") == "vide",
                    st.session_state.get("dec_t5_final") == "composite",
                    st.session_state.get("dec_t6_final") == "soustraction",
                    st.session_state.get("dec_t7_final") == "formules",
                    st.session_state.get("dec_t8_final") == "invariante",
                    st.session_state.get("dec_t9_final") == "triangles",
                    st.session_state.get("dec_t10_final") == "totale",
                ]
            )

            st.session_state.score_suite1_p1 = round(float(score_q1), 1)
            st.session_state.score_suite1_p2 = round(float(score_t1), 1)
            st.session_state.score_final_suite1 = round(float(score_q1 + score_t1), 1)
            st.session_state.suite_verrouille_tab1 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 1 ---
    if st.session_state.get("suite_verrouille_tab1", False):
        scr1 = st.session_state.get("score_suite1_p1", 0.0)
        scr2 = st.session_state.get("score_suite1_p2", 0.0)
        tot_s = st.session_state.get("score_final_suite1", 0.0)

        timestamp_suite1 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER DÉCOMPOSITION SCELLÉ | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Décomposition - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Géométrie</h1>
                <p>Atelier 1 : Décomposition géométrique des surfaces complexes</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Décomposition : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue à la Synthèse du cours : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab6" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab6, 1):
                saisie = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_suites += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_suites += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html = preparer_nom_fichier("Rapport_Atelier_1").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 1 (.html)",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )

with tab2:
    st.header("Centre de Gravité Simple")
    st.write("Cette interface permet de calculer le centre de gravité pour un système de 2 ou 3 points.")

    if "suite_verrouille_tab2" not in st.session_state:
        st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    # --- 2. ENTRÉE DES DONNÉES ET GRAPHIQUE ---
    nb_points = st.radio("Sélectionnez le nombre de points :", [2, 3], horizontal=True, disabled=verrou_at2)     
    # Initialisation des structures de données
    masses = []
    coords_x = []
    coords_y = []
    
    # Création de colonnes dynamiques pour la saisie des données
    colonnes_saisie = st.columns(nb_points)
    
    for i in range(nb_points):
        with colonnes_saisie[i]:
            st.subheader(f"Point {i+1}")
            m = st.slider(f"Masse m{i+1} (kg)", min_value=1.0, max_value=50.0, value=10.0, step=0.5, key=f"m_simple_{i}")
            x = st.slider(f"Position X{i+1}", min_value=-10.0, max_value=10.0, value=float(i*4 - 4), step=0.5, key=f"x_simple_{i}")
            y = st.slider(f"Position Y{i+1}", min_value=-10.0, max_value=10.0, value=float(i*2 - 2), step=0.5, key=f"y_simple_{i}")
            
            masses.append(m)
            coords_x.append(x)
            coords_y.append(y)
            
    # --- CALCULS ---
    M_totale = sum(masses)
    X_G = sum(m * x for m, x in zip(masses, coords_x)) / M_totale
    Y_G = sum(m * y for m, y in zip(masses, coords_y)) / M_totale
    
    st.markdown("---")
    
    # Affichage des résultats numériques
    st.subheader("Résultats du calcul")
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric(label="Masse totale (M)", value=f"{M_totale:.2f} kg")
    with col_res2:
        st.metric(label="Coordonnée X_G", value=f"{X_G:.2f}")
    with col_res3:
        st.metric(label="Coordonnée Y_G", value=f"{Y_G:.2f}")
        
    # --- GRAPHIQUE ---
    st.subheader("Visualisation graphique")
    
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Tracé des points du système (la taille dépend de la masse)
    for i in range(nb_points):
        taille = masses[i] * 10  # Facteur d'échelle pour la visibilité
        ax.scatter(coords_x[i], coords_y[i], s=taille, label=f"Point {i+1} ({masses[i]} kg)", alpha=0.7)
        ax.text(coords_x[i] + 0.3, coords_y[i] + 0.3, f"P{i+1}", fontsize=10, weight='bold')
        
    # Tracé du centre de gravité (représenté par une croix rouge)
    ax.scatter(X_G, Y_G, color='red', marker='x', s=200, linewidths=3, label="Centre de gravité (G)")
    ax.text(X_G + 0.3, Y_G - 0.5, "G", color='red', fontsize=12, weight='bold')
    
    # Paramétrages des axes
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel("Axe X")
    ax.set_ylabel("Axe Y")
    ax.legend(loc="upper left")
    
    # Intégration du graphique dans Streamlit
    st.pyplot(fig)

    
    st.write("---")
    
    # --- 3. APPEL DES QUESTIONS (Maintenant verrou_at2 est bien défini en amont !) ---
    afficher_atelier_simple_complet(verrouille=verrou_at2)

    # --- 4. SYNTHÈSE ET VALIDATION ---
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier Simple")
    
    # (Supprimez le bloc d'initialisation du verrou qui était ici !)
    
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions de l'Atelier Simple.",
        key="check_certif_simple_final_net",
        disabled=verrou_at2,
    )



    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz (5 questions à 2 points chacune -> Max 10 points)
            score_q2 = 0.0
            if "ordre_quiz_tab2" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2:
                    reponse_eleve = st.session_state.get(f"sim_at2_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve) == str(q_item["rep"]):
                        score_q2 += 2.0

            # 2. Correction des Textes à trous (5 cases à 2 points chacune -> Max 10 points)
            score_t2 = sum(
                [
                    st.session_state.get("sim_t1_final") == "levier",
                    st.session_state.get("sim_t2_final") == "isobarycentre",
                    st.session_state.get("sim_t3_final") == "lourd",
                    st.session_state.get("sim_t4_final") == "pondérée",
                    st.session_state.get("sim_t5_final") == "verticales",
                ]
            ) * 2.0

            st.session_state.score_suite2_p1 = round(float(score_q2), 1)
            st.session_state.score_suite2_p2 = round(float(score_t2), 1)
            st.session_state.score_final_suite2 = round(float(score_q2 + score_t2), 1)
            st.session_state.suite_verrouille_tab2 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 2 ---
    if st.session_state.get("suite_verrouille_tab2", False):
        scr1_2 = st.session_state.get("score_suite2_p1", 0.0)
        scr2_2 = st.session_state.get("score_suite2_p2", 0.0)
        tot_s2 = st.session_state.get("score_final_suite2", 0.0)

        timestamp_suite2 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER SIMPLE SCELLÉ | Note de session : {tot_s2:.1f} / 20")

        html_export_simple = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Barycentre Simple - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #0d9488; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique-Mécanique</h1>
                <p>Atelier 2 : Centre de gravité simple</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s2:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #0d9488;">
                Note obtenue au Quiz Simple : <strong>{scr1_2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s2:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2, 1):
                saisie = st.session_state.get(f"sim_at2_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_simple += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_simple += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html_simple = preparer_nom_fichier("Rapport_Atelier_2").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_simple,
            file_name=nom_fichier_html_simple,
            mime="text/html",
            use_container_width=True
        )



with tab3:
    st.header("Centre de Gravité Complexe")
    st.write("Cette interface permet de gérer un grand nombre de points (de 4 à 10) à l'aide d'un tableau dynamique.")
    
    # --- GESTION DU VERROUILLAGE DE L'ATELIER 3 ---
    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    # Curseur pour le nombre de points complexes
    n_points_comp = st.slider("Sélectionnez le nombre de points du système :", min_value=4, max_value=10, value=5, step=1, disabled=verrou_at3)
    
    # Préparation des données par défaut pour le tableau éditable
    import pandas as pd
    if f"df_comp_{n_points_comp}" not in st.session_state:
        donnees_initiales = {
            "Point": [f"P{i+1}" for i in range(n_points_comp)],
            "Masse (kg)": [10.0] * n_points_comp,
            "Position X": [float(i * 2 - n_points_comp) for i in range(n_points_comp)],
            "Position Y": [float(((i**2) % 5) - 2) for i in range(n_points_comp)]
        }
        st.session_state[f"df_comp_{n_points_comp}"] = pd.DataFrame(donnees_initiales)

    # Affichage du tableau de données éditable
    st.write("Modifiez les valeurs directement dans le tableau ci-dessous :")
    df_edite = st.data_editor(
        st.session_state[f"df_comp_{n_points_comp}"],
        use_container_width=True,
        disabled=verrou_at3,
        hide_index=True
    )
    
    # Extraction des données modifiées
    try:
        masses_c = df_edite["Masse (kg)"].tolist()
        coords_xc = df_edite["Position X"].tolist()
        coords_yc = df_edite["Position Y"].tolist()
        
        # --- CALCULS PHYSIQUES ---
        M_totale_c = sum(masses_c)
        if M_totale_c <= 0:
            st.error("Erreur : La masse totale du système doit être strictement supérieure à 0.")
            X_Gc, Y_Gc = 0.0, 0.0
        else:
            X_Gc = sum(m * x for m, x in zip(masses_c, coords_xc)) / M_totale_c
            Y_Gc = sum(m * y for m, y in zip(masses_c, coords_yc)) / M_totale_c
    except Exception as e:
        st.error("Saisie invalide détectée dans le tableau. Veuillez vérifier vos nombres.")
        M_totale_c, X_Gc, Y_Gc = 1.0, 0.0, 0.0

    st.markdown("---")
    
    # Affichage des résultats numériques
    st.subheader("Résultats du calcul")
    col_resc1, col_resc2, col_resc3 = st.columns(3)
    with col_resc1:
        st.metric(label="Masse totale (M)", value=f"{M_totale_c:.2f} kg")
    with col_resc2:
        st.metric(label="Coordonnée X_G", value=f"{X_Gc:.2f}")
    with col_resc3:
        st.metric(label="Coordonnée Y_G", value=f"{Y_Gc:.2f}")
        
    # --- GRAPHIQUE ---
    st.subheader("Visualisation graphique")
    fig, ax = plt.subplots(figsize=(6, 4))
    
    for i in range(n_points_comp):
        # Facteur d'échelle adaptatif pour la taille des points graphiques
        taille = max(10, masses_c[i] * 5)
        ax.scatter(coords_xc[i], coords_yc[i], s=taille, alpha=0.6)
        ax.text(coords_xc[i] + 0.2, coords_yc[i] + 0.2, f"P{i+1}", fontsize=9)
        
    ax.scatter(X_Gc, Y_Gc, color='red', marker='x', s=200, linewidths=3, label="G (Centre de gravité)")
    ax.text(X_Gc + 0.3, Y_Gc - 0.5, "G", color='red', fontsize=12, weight='bold')
    
    ax.axhline(0, color='black', linewidth=0.5, linestyle='--')
    ax.axvline(0, color='black', linewidth=0.5, linestyle='--')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel("Axe X")
    ax.set_ylabel("Axe Y")
    st.pyplot(fig)

    
    st.write("---")

    afficher_atelier_complexe_complet(verrouille=verrou_at3)

    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3  # <--- Création de la variable pour la tab2
    
    st.subheader("Questions d'évaluation de l'Atelier Complexe")

    st.write("---")
    st.subheader("Synthèse et validation sur les cercles")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()
  
    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les mesures et calculs de l'Atelier Centre de Gravité Complexe.",
        key="check_certif_complexe_final_net",
        disabled=verrou_at3,
    )

    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # 1. Correction du Quiz Complexe (5 questions x 2 pts -> Max 10 pts)
            score_q3 = 0.0
            if "ordre_quiz_tab3" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3:
                    reponse_eleve = st.session_state.get(f"comp_at3_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 2.0

            # 2. Correction des Textes à trous Complexes (5 cases x 2 pts -> Max 10 pts)
            score_t3 = sum(
                [
                    st.session_state.get("comp_t1_final") == "creuse",
                    st.session_state.get("comp_t2_final") == "sommation",
                    st.session_state.get("comp_t3_final") == "masses",
                    st.session_state.get("comp_t4_final") == "élémentaires",
                    st.session_state.get("comp_t5_final") == "précision",
                ]
            ) * 2.0

            st.session_state.score_suite3_p1 = round(float(score_q3), 1)
            st.session_state.score_suite3_p2 = round(float(score_t3), 1)
            st.session_state.score_final_suite3 = round(float(score_q3 + score_t3), 1)
            st.session_state.suite_verrouille_tab3 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 3 ---
    if st.session_state.get("suite_verrouille_tab3", False):
        scr1_3 = st.session_state.get("score_suite3_p1", 0.0)
        scr2_3 = st.session_state.get("score_suite3_p2", 0.0)
        tot_s3 = st.session_state.get("score_final_suite3", 0.0)

        timestamp_suite3 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        st.success(f"ATELIER COMPLEXE SCELLÉ | Note de session : {tot_s3:.1f} / 20")

        html_export_complexe = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Barycentre Complexe - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #4338ca; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation de Physique-Mécanique</h1>
                <p>Atelier 3 : Centre de gravité complexe (système de {n_points_comp} points)</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Générées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4338ca;">
                Note obtenue au Quiz Complexe : <strong>{scr1_3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>

            <div class="sub-title">Coordonnées Finales Calculées</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #4338ca;">
                Masse totale du système (M) : <strong>{M_totale_c:.2f} kg</strong><br>
                Position X_G : <strong>{X_Gc:.2f}</strong><br>
                Position Y_G : <strong>{Y_Gc:.2f}</strong>
            </p>
        </body>
        </html>
        """
        
        nom_fichier_html_complexe = preparer_nom_fichier("Rapport_Atelier_3").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_complexe,
            file_name=nom_fichier_html_complexe,
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Applications Professionnelles et Métiers")
    st.write("Choisissez votre domaine de spécialité pour charger une étude de cas aléatoire sécurisée.")
    
    # --- 1. SÉCURITÉ DE LECTURE : INITIALISATION DU VERROU TOUT EN HAUT ---
    if "suite_verrouille_tab4" not in st.session_state:
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    # Menu déroulant de sélection du domaine métier
    metier_choisi = st.selectbox(
        "Sélectionnez votre domaine d'activité :",
        ["Transport Routier", "Travaux Publics", "Maintenance Industrielle", "Géomètre"],
        disabled=verrou_at4
    )

    st.markdown("---")

    # --- 2. APPEL DE LA DEF UNIQUE DU MODULE MÉTIER ÉTANCHE ---
    afficher_atelier_metiers_etanche(metier_choisi, verrouille=verrou_at4)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier Spécialisé")

    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété l'étude de cas et le questionnaire technique lié à mon métier.",
        key="check_certif_metiers_etanche",
        disabled=verrou_at4,
    )

    # --- 3. COMPOSANT DE CORRECTION AUTOMATIQUE ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_tab4_etanche", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "ELEVE") in ["ELEVE", ""] or st.session_state.get("prenom_var", "PRENOM") in ["PRENOM", ""]:
            st.error("Action refusée : Renseignez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            # Récupération du cas actuellement tiré au sort pour l'élève
            cle_session_cas = f"cas_attribue_{metier_choisi.replace(' ', '_')}"
            cas_actif = st.session_state.get(cle_session_cas)

            # A. Notation du QCM (2 questions -> Max 10 points soit 5 pts par bonne réponse)
            score_q4 = 0.0
            for q_item in cas_actif["quiz"]:
                reponse_saisie = st.session_state.get(f"met_quiz_ans_{cas_actif['id_cas']}_{q_item['id']}", "Choisir...")
                if str(reponse_saisie).strip() == str(q_item["rep"]).strip():
                    score_q4 += 5.0

            # B. Notation du Texte à trous (2 cases -> Max 10 points soit 5 pts par case exacte)
            score_t4 = 0.0
            for _, _, rep_attendue, cle_t in cas_actif["trous"]:
                reponse_trou = st.session_state.get(f"met_trou_ans_{cas_actif['id_cas']}_{cle_t}", "Choisir...")
                if str(reponse_trou).strip() == str(rep_attendue).strip():
                    score_t4 += 5.0

            # CORRECTION APPLIQUÉE : Stockage dans le bon dictionnaire de clé pour l'Atelier 4
            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    # --- 4. EXPORTATION DU RAPPORT HTML SCELLÉ ---
    if st.session_state.get("suite_verrouille_tab4", False):
        tot_s4 = st.session_state.get("score_final_suite4", 0.0)
        timestamp_suite4 = datetime.datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER MÉTIERS SCELLÉ | Note obtenue pour le domaine {metier_choisi} : {tot_s4:.1f} / 20")

        # Recherche du cas actif pour le récapitulatif
        cle_session_cas = f"cas_attribue_{metier_choisi.replace(' ', '_')}"
        cas_actif = st.session_state.get(cle_session_cas)

        html_export_metiers = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Applications Métiers - {n_eleve}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 30px; background-color: #f8fafc; color: #1e293b; }}
                .header-box {{ background-color: #b45309; color: white; padding: 20px; border-radius: 8px; margin-bottom: 25px; position: relative; }}
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
                <h1>Rapport d'Évaluation Spécialité Métiers</h1>
                <p>Domaine professionnel : {metier_choisi} ({cas_actif['titre']})</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Détail des corrections du Quiz Métier Tiré au Sort</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(cas_actif["quiz"], 1):
            saisie = st.session_state.get(f"met_quiz_ans_{cas_actif['id_cas']}_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_metiers += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_metiers += """
                </tbody>
            </table>
        </body>
        </html>
        """
        
        nom_fichier_html_metiers = preparer_nom_fichier("Rapport_Atelier_4").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_metiers,
            file_name=nom_fichier_html_metiers,
            mime="text/html",
            use_container_width=True
        )






    
