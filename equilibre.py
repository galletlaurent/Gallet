
# -*- coding: utf-8 -*-

import streamlit as st

st.set_page_config(
    page_title="Application équilibre des forces en statique",
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
st.title("Application équilibre des forces en statique")
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
    "Base de sustentation",
    "Equilibre à deux forces",
    "Equilibre à trois forces",
    "Equilibre à plus de trois forces",
    "Exemples"
])

tab0 = onglets[0]
tab1 = onglets[1]
tab2 = onglets[2]
tab3 = onglets[3]
tab4 = onglets[4]
tab5 = onglets[5]
tab6 = onglets[6]

COURS_COLORS = ['#FF4B4B', '#0068C9', '#29B09D', '#FFABAB', '#781C81', '#FFC614', '#9D4EDD']
SEUIL_STATIQUE = 1e-2

# --- Votre fonction de generation de nom de fichier ---
def preparer_nom_fichier(nom_onglet):
    """Genere un nom de fichier standardise et unique pour l'export des rapports."""
    nom_propre = str(st.session_state.get("nom_var", "ELEVE")).replace(" ", "_")
    prenom_propre = str(st.session_state.get("prenom_var", "PRENOM")).replace(" ", "_")
    classe_propre = str(st.session_state.get("classe_var", "GROUPE")).replace(" ", "_")

    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    return f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"

# --- Fonction utilitaire pour generer le contenu du fichier texte ---
def generer_contenu_rapport(nom_onglet, forces_list, est_stat, rx, ry, r_norme):
    nom = st.session_state.get("nom_var", "ELEVE")
    prenom = st.session_state.get("prenom_var", "PRENOM")
    classe = st.session_state.get("classe_var", "GROUPE")
    
    texte = f"RAPPORT DE TRAVAIL PRATIQUE - STATIQUE\n"
    texte += f"----------------------------------------\n"
    texte += f"Eleve : {nom} {prenom}\nClasse/Groupe : {classe}\n"
    texte += f"Date de generation : {datetime.now().strftime('%Y-%m-%d a %H:%M:%S')}\n"
    texte += f"Activite : {nom_onglet}\n"
    texte += f"----------------------------------------\n\n"
    texte += f"DONNEES DES FORCES SAISIES :\n"
    
    for f in forces_list:
        texte += f" - Force F{f['id']} : {f['norme']:.2f} N | Angle : {f['angle']:.1f}° | Fx : {f['fx']:.2f} N | Fy : {f['fy']:.2f} N\n"
        
    texte += f"\nRESULTATS ANALYTIQUES :\n"
    texte += f" - Somme des Fx : {rx:.2f} N\n"
    texte += f" - Somme des Fy : {ry:.2f} N\n"
    texte += f" - Norme de la resultante : {r_norme:.2f} N\n"
    texte += f" Statut mecanique : {'EQUILIBRE STATIQUE VALIDE' if est_stat else 'SYSTEME EN DESEQUILIBRE'}\n"
    return texte

# --- Fonction generique pour analyser et tracer les systemes de forces ---
def analyser_systeme_forces(nb_forces, suffixe_clef, nom_onglet):
    st.subheader("Parametres des Vecteurs Forces")
    forces_data = []
    cols = st.columns(nb_forces)

    for i in range(nb_forces):
        with cols[i]:
            st.write(f"**Force F_{i+1}**")
            if nb_forces == 2:
                def_n, def_a = 10.0, 0.0 if i == 0 else 180.0
            elif nb_forces == 3:
                def_n, def_a = (10.0, 30.0) if i == 0 else ((10.0, 150.0) if i == 1 else (17.32, -90.0))
            else:
                def_n, def_a = 10.0, (360.0 / nb_forces) * i

            norme = st.number_input(f"Norme (N)", min_value=0.0, value=float(def_n), step=1.0, key=f"n_{suffixe_clef}_{i}")
            angle_deg = st.number_input(f"Angle (°)", min_value=-360.0, max_value=360.0, value=float(def_a), step=15.0, key=f"a_{suffixe_clef}_{i}")
            
            angle_rad = np.radians(angle_deg)
            forces_data.append({
                "id": i+1, "norme": norme, "angle": angle_deg,
                "fx": norme * np.cos(angle_rad), "fy": norme * np.sin(angle_rad)
            })

    # Calculs de la resultante
    sum_fx = sum(f["fx"] for f in forces_data)
    sum_fy = sum(f["fy"] for f in forces_data)
    resultante = np.sqrt(sum_fx**2 + sum_fy**2)
    is_static = resultante < SEUIL_STATIQUE

    # Zone de Verdict
    st.write("---")
    st.subheader("Evaluation de l'Equilibre")
    c1, c2, c3 = st.columns(3)
    c1.metric("Somme Fx", f"{sum_fx:.2f} N")
    c2.metric("Somme Fy", f"{sum_fy:.2f} N")
    c3.metric("Resultante R", f"{resultante:.2f} N")

    if is_static:
        st.success("Le point materiel est en equilibre statique (la somme des forces est nulle).")
    else:
        st.error(f"Desequilibre detecte. Il manque une force de {resultante:.2f} N a {np.degrees(np.arctan2(-sum_fy, -sum_fx)):.1f}° pour equilibrer le systeme.")

    # Graphiques
    st.write("---")
    st.subheader("Representations Graphiques")
    g_tab1, g_tab2 = st.tabs(["Forces Concourantes (Origine)", "Dynamique (Bout a Bout)"])
    
    with g_tab1:
        fig1, ax1 = plt.subplots(figsize=(4, 4))
        
        # Liste pour collecter toutes les coordonnees x et y afin de calibrer l'echelle exacte
        points_x = [0.0]
        points_y = [0.0]
        
        for f in forces_data:
            if f["norme"] > 0:
                ax1.quiver(0, 0, f["fx"], f["fy"], angles='xy', scale_units='xy', scale=1, color=COURS_COLORS[(f["id"]-1)%len(COURS_COLORS)], label=f"F{f['id']}")
                points_x.append(f["fx"])
                points_y.append(f["fy"])
                
        if not is_static:
            ax1.quiver(0, 0, sum_fx, sum_fy, angles='xy', scale_units='xy', scale=1, color='black', linestyle='--', label="Resultante R")
            points_x.append(sum_fx)
            points_y.append(sum_fy)
            
        # Calcul de l'echelle symetrique dynamique basee sur la valeur absolue maximale trouvee
        max_coord = max(max(abs(x) for x in points_x), max(abs(y) for y in points_y), 1.0)
        lim = max_coord * 1.15
        
        ax1.set_xlim(-lim, lim)
        ax1.set_ylim(-lim, lim)
        ax1.axhline(0, color='black', linewidth=0.5)
        ax1.axvline(0, color='black', linewidth=0.5)
        ax1.grid(True, linestyle='--', alpha=0.3)
        ax1.set_aspect('equal')
        ax1.legend(loc="upper right")
        st.pyplot(fig1)

    with g_tab2:
        fig2, ax2 = plt.subplots(figsize=(4, 4))
        
        # Collecte des sommets du polygone pour calibrer son echelle propre
        poly_x = [0.0]
        poly_y = [0.0]
        cx, cy = 0.0, 0.0
        
        for f in forces_data:
            if f["norme"] > 0:
                ax2.quiver(cx, cy, f["fx"], f["fy"], angles='xy', scale_units='xy', scale=1, color=COURS_COLORS[(f["id"]-1)%len(COURS_COLORS)])
                cx += f["fx"]
                cy += f["fy"]
                poly_x.append(cx)
                poly_y.append(cy)
                
        ax2.plot(0, 0, 'gX', markersize=8, label="Depart")
        
        if not is_static:
            ax2.quiver(cx, cy, -sum_fx, -sum_fy, angles='xy', scale_units='xy', scale=1, color='red', linestyle='--', label="Fermeture")
            poly_x.append(cx - sum_fx)
            poly_y.append(cy - sum_fy)
            
        # Ajustement automatique de la fenetre graphique autour du polygone complet
        min_x, max_x = min(poly_x), max(poly_x)
        min_y, max_y = min(poly_y), max(poly_y)
        
        # On s'assure d'une envergure minimale pour eviter les divisions par zero sur les cas statiques parfaits
        range_x = max(max_x - min_x, 1.0)
        range_y = max(max_y - min_y, 1.0)
        max_range = max(range_x, range_y)
        
        centre_x = (min_x + max_x) / 2
        centre_y = (min_y + max_y) / 2
        half_side = (max_range / 2) * 1.20
        
        ax2.set_xlim(centre_x - half_side, centre_x + half_side)
        ax2.set_ylim(centre_y - half_side, centre_y + half_side)
        ax2.axhline(0, color='black', linewidth=0.3, linestyle=':')
        ax2.axvline(0, color='black', linewidth=0.3, linestyle=':')
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.set_aspect('equal')
        ax2.legend()
        st.pyplot(fig2)


def obtenir_banque_metiers():
    """Retourne la banque de données des scénarios et des questions par métier."""
    return {
        "routier": {
            "nom": "Transport Routier et Logistique",
            "scenarios": [
                {
                    "titre": "Cas A : Arrimage d'un bloc de béton sur remorque",
                    "description": "Un camion transporte un bloc de 5 tonnes. En virage, le bloc subit son poids vertical (50 kN), la réaction du plateau et deux sangles obliques d'arrimage F1 et F2. Les sangles doivent compenser la force centrifuge latérale de 15 kN pour maintenir l'équilibre statique.",
                    "forces": 4
                },
                {
                    "titre": "Cas B : Remorquage d'un camion en panne en côte",
                    "description": "Un poids lourd est immobilisé sur une pente à 8%. Il est retenu par le câble du treuil d'une dépanneuse F1 et une cale de sécurité F2. Le système est modélisé par 3 forces concourantes (Poids, Traction câble, Réaction cale) devant s'annuler.",
                    "forces": 3
                }
            ],
            "quiz": [
                {"id": "mr1", "q": "Lors de l'arrimage d'une charge, quel est le rôle des sangles de tension ?", "options": ["Créer des forces opposées aux forces d'inertie", "Augmenter la masse du véhicule", "Modifier la direction des roues"], "rep": "Créer des forces opposées aux forces d'inertie"},
                {"id": "mr2", "q": "Si un chargement glisse vers l'arrière au démarrage, la somme des forces sur l'axe horizontal était :", "options": ["Non nulle (résultante vers l'arrière)", "Strictement égale à zéro", "Infinie vers le haut"], "rep": "Non nulle (résultante vers l'arrière)"},
                {"id": "mr3", "q": "Pour un camion stationné sur un pont plat, la réaction des essieux est :", "options": ["Verticale et opposée au poids total", "Horizontale vers l'avant", "Nulle en permanence"], "rep": "Verticale et opposée au poids total"}
            ],
            "trous": [
                ("1. Un arrimage correct empêche tout ......... de la cargaison.", ["Choisir...", "glissement", "allègement"], "glissement", "m_t1"),
                ("2. Sur une pente, la force de gravité possède une composante .........", ["Choisir...", "tangentielle", "nulle"], "tangentielle", "m_t2")
            ]
        },
        "travaux_publics": {
            "nom": "Travaux Publics et Génie Civil",
            "scenarios": [
                {
                    "titre": "Cas A : Équilibre d'une grue à tour de chantier",
                    "description": "Une grue soulève une prédalle de 3 tonnes. Le système est en statique sous l'action du poids de la charge, du contrepoids de la grue, de la réaction de la structure centrale en béton et de la force du vent latéral (2 kN).",
                    "forces": 4
                },
                {
                    "titre": "Cas B : Tirant d'ancrage d'un mur de soutènement",
                    "description": "Un mur de soutènement retient la poussée de la terre (30 kN). Il est stabilisé par un tirant d'ancrage oblique en acier F1 et la réaction de la semelle de fondation F2. Les trois actions mécaniques s'équilibrent au point nodal.",
                    "forces": 3
                }
            ],
            "quiz": [
                {"id": "mtp1", "q": "Dans une grue de chantier, le contrepoids sert mécaniquement à :", "options": ["Créer un équilibre de moment et de forces opposées", "Décorer la structure arrière", "Alléger la flèche"], "rep": "Créer un équilibre de moment et de forces opposées"},
                {"id": "mtp2", "q": "Si les fondations d'un mur de soutènement cèdent, c'est que la résultante des forces :", "options": ["A dépassé la capacité de résistance du sol", "Était parfaitement nulle", "Était verticale ascendante"], "rep": "A dépassé la capacité de résistance du sol"},
                {"id": "mtp3", "q": "L'action de la poussée des terres sur un blindage de fouille est modélisée par une force :", "options": ["Horizontale ou oblique perpendiculaire au blindage", "Toujours verticale ascendante", "Nulle en surface"], "rep": "Horizontale ou oblique perpendiculaire au blindage"}
            ],
            "trous": [
                ("1. Le contrepoids stabilise la grue en évitant le ......... du châssis.", ["Choisir...", "basculement", "levage"], "basculement", "m_t1"),
                ("2. Un tirant d'ancrage travaille exclusivement en ......... axiale.", ["Choisir...", "traction", "torsion"], "traction", "m_t2")
            ]
        },
        "maintenance": {
            "nom": "Maintenance Industrielle",
            "scenarios": [
                {
                    "titre": "Cas A : Dépose d'un moteur d'usine au palan",
                    "description": "Un moteur industriel de 800 kg est suspendu à un portique de maintenance par deux chaînes obliques F1 et F2 formant un V. Le technicien exerce une force de guidage horizontale F3 pour aligner le moteur sur son bâti.",
                    "forces": 4
                },
                {
                    "titre": "Cas B : Tension de courroie sur un groupe motopompe",
                    "description": "Une poulie de transmission subit l'action de tension du brin tendu F1, du brin mou F2 et la réaction de l'arbre moteur F3. En régime permanent établi, le système d'axes de la poulie est considéré en équilibre statique.",
                    "forces": 3
                }
            ],
            "quiz": [
                {"id": "mm1", "q": "Lors de l'utilisation d'un palan de levage, que se passe-t-il si les chaînes sont trop obliques ?", "options": ["La tension dans chaque chaîne augmente fortement", "La force de gravité diminue", "Le moteur devient plus léger"], "rep": "La tension dans chaque chaîne augmente fortement"},
                {"id": "mm2", "q": "Un arbre moteur au repos supportant une poulie tendue subit une réaction de palier qui :", "options": ["Annule la résultante des tensions de courroie", "Tourne à vide", "Est toujours nulle"], "rep": "Annule la résultante des tensions de courroie"},
                {"id": "mm3", "q": "L'immobilité d'un réducteur mécanique sur son support boulonné prouve que :", "options": ["La somme des forces et fixations équilibre le poids et le couple", "Les boulons ne subissent aucune force", "La gravité n'agit plus"], "rep": "La somme des forces et fixations équilibre le poids et le couple"}
            ],
            "trous": [
                ("1. Une élingue trop horizontale subit une ......... mécanique excessive.", ["Choisir...", "tension", "compression"], "tension", "m_t1"),
                ("2. Les boulons d'ancrage s'opposent au ......... du bâti moteur.", ["Choisir...", "arrachement", "graissage"], "arrachement", "m_t2")
            ]
        },
        "geometre": {
            "nom": "Géomètre et Topographie",
            "scenarios": [
                {
                    "titre": "Cas A : Stabilisation d'un mât de mesure par haubans",
                    "description": "Un mât topographique de grande hauteur est ancré au sol par 3 haubans périphériques répartis à 120°. Le mât subit la force verticale de compression de son poids et les 3 tractions obliques des câbles tendus.",
                    "forces": 4
                },
                {
                    "titre": "Cas B : Implantation d'un jalon sur terrain rocheux suspect",
                    "description": "Un jalon lourd de visée subit l'action du vent horizontal (50 N), le poids propre de sa structure et la force de maintien oblique appliquée par la rotule de son trépied de fixation au sol.",
                    "forces": 3
                }
            ],
            "quiz": [
                {"id": "mg1", "q": "Pourquoi répartit-on les haubans d'un mât de mesure de manière régulière à 120° ?", "options": ["Pour obtenir une résultante horizontale nulle sur le mât", "Pour doubler la hauteur de visée", "Pour annuler la gravité verticale"], "rep": "Pour obtenir une résultante horizontale nulle sur le mât"},
                {"id": "mg2", "q": "Si le trépied d'un théodolite glisse sur un sol gelé, géométriquement cela signifie que :", "options": ["La force tangentielle dépasse l'adhérence du sol", "L'appareil est parfaitement de niveau", "La force résultante est nulle"], "rep": "La force tangentielle dépasse l'adhérence du sol"},
                {"id": "mg3", "q": "Le fil à plomb d'un géomètre indique une direction de force qui est toujours :", "options": ["Perpendiculaire à la surface théorique de la Terre", "Parallèle à l'axe optique horizontal", "Inclinée à 45 degrés"], "rep": "Perpendiculaire à la surface théorique de la Terre"}
            ],
            "trous": [
                ("1. Les haubans maintiennent le mât en annulant l'effet du ......... latéral.", ["Choisir...", "vent", "soleil"], "vent", "m_t1"),
                ("2. L'ancrage au sol oppose une réaction pour empêcher l'......... des pointes.", ["Choisir...", "enfoncement", "alignement"], "enfoncement", "m_t2")
            ]
        }
    }

def afficher_atelier_metier_complet(metier_cle, scenario_index, verrouille=False):
    """Affiche le module d'exercice adapte au metier selectionne avec un schema de principe."""
    import streamlit as st
    import matplotlib.pyplot as plt

    banque = obtenir_banque_metiers()
    data = banque[metier_cle]
    scen = data["scenarios"][scenario_index]
    
    st.info(f"**Application metier : {scen['titre']}**\n\n{scen['description']}")
    
    # --- GENERATION DU SCHEMA DE PRINCIPE VISUEL ---
    st.subheader("Schema de principe de la situation mecanique")
    
    fig_sch, ax_sch = plt.subplots(figsize=(6, 2.5))
    ax_sch.plot(0, 0, 'o', color='#0f172a', markersize=10, label="Point d'etude")
    
    # Dessin des vecteurs de guidage fixes selon le metier et le cas tire au sort
    if metier_cle == "routier":
        if scenario_index == 0: # Sangles camion
            ax_sch.quiver([0, 0, 0], [0, 0, 0], [15, -10, -10], [0, 15, -15], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D'])
            ax_sch.text(12, 2, "Centrifuge", color='#ef4444', fontsize=9)
            ax_sch.text(-12, 12, "Sangle F1", color='#0068C9', fontsize=9)
            ax_sch.text(-12, -12, "Sangle F2", color='#29B09D', fontsize=9)
        else: # Treuil cote
            ax_sch.quiver([0, 0, 0], [0, 0, 0], [-10, 15, -5], [-20, 10, 10], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D'])
            ax_sch.text(-8, -18, "Poids P", color='#ef4444', fontsize=9)
            ax_sch.text(10, 8, "Treuil F1", color='#0068C9', fontsize=9)
            ax_sch.text(-8, 8, "Cale F2", color='#29B09D', fontsize=9)
            
    elif metier_cle == "travaux_publics":
        if scenario_index == 0: # Grue
            ax_sch.quiver([0, 0, 0, 0], [0, 0, 0, 0], [0, 0, -15, 8], [-20, 15, 0, 0], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D', '#781C81'])
            ax_sch.text(1, -16, "Poids Charge", color='#ef4444', fontsize=9)
            ax_sch.text(1, 12, "Contrepoids", color='#0068C9', fontsize=9)
            ax_sch.text(-14, 2, "Structure", color='#29B09D', fontsize=9)
            ax_sch.text(6, 2, "Vent", color='#781C81', fontsize=9)
        else: # Mur soutenement
            ax_sch.quiver([0, 0, 0], [0, 0, 0], [20, -15, -5], [0, 10, -10], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D'])
            ax_sch.text(14, 2, "Poussee Terre", color='#ef4444', fontsize=9)
            ax_sch.text(-14, 8, "Tirant F1", color='#0068C9', fontsize=9)
            ax_sch.text(-12, -10, "Semelle F2", color='#29B09D', fontsize=9)
            
    elif metier_cle == "maintenance":
        if scenario_index == 0: # Moteur palan
            ax_sch.quiver([0, 0, 0, 0], [0, 0, 0, 0], [0, -10, 10, -12], [-20, 15, 15, 0], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D', '#781C81'])
            ax_sch.text(1, -16, "Poids Moteur", color='#ef4444', fontsize=9)
            ax_sch.text(-10, 12, "Chaine F1", color='#0068C9', fontsize=9)
            ax_sch.text(8, 12, "Chaine F2", color='#29B09D', fontsize=9)
            ax_sch.text(-14, -3, "Guidage F3", color='#781C81', fontsize=9)
        else: # Poulie courroie
            ax_sch.quiver([0, 0, 0], [0, 0, 0], [15, 12, -27], [5, -5, 0], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D'])
            ax_sch.text(10, 6, "Brin Tendu F1", color='#ef4444', fontsize=9)
            ax_sch.text(8, -8, "Brin Mou F2", color='#0068C9', fontsize=9)
            ax_sch.text(-24, 2, "Arbre F3", color='#29B09D', fontsize=9)
            
    elif metier_cle == "geometre":
        if scenario_index == 0: # Mat haubans
            ax_sch.quiver([0, 0, 0, 0], [0, 0, 0, 0], [0, -12, 6, 6], [-20, -5, 10, -10], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D', '#781C81'])
            ax_sch.text(1, -16, "Poids Mat", color='#ef4444', fontsize=9)
            ax_sch.text(-14, -3, "Hauban 1", color='#0068C9', fontsize=9)
            ax_sch.text(4, 11, "Hauban 2", color='#29B09D', fontsize=9)
            ax_sch.text(4, -11, "Hauban 3", color='#781C81', fontsize=9)
        else: # Jalon
            ax_sch.quiver([0, 0, 0], [0, 0, 0], [15, 0, -15], [0, -15, 15], angles='xy', scale_units='xy', scale=1, color=['#ef4444', '#0068C9', '#29B09D'])
            ax_sch.text(10, 2, "Vent Longe", color='#ef4444', fontsize=9)
            ax_sch.text(1, -12, "Poids Jalon", color='#0068C9', fontsize=9)
            ax_sch.text(-14, 12, "Trepie F1", color='#29B09D', fontsize=9)

    # Parametrage des axes du schema de principe
    ax_sch.set_xlim(-30, 30)
    ax_sch.set_ylim(-22, 22)
    ax_sch.axhline(0, color='grey', linewidth=0.5, linestyle=':')
    ax_sch.axvline(0, color='grey', linewidth=0.5, linestyle=':')
    ax_sch.set_aspect('equal')
    ax_sch.axis('off') # Masque la grille numerique de fond pour faire un vrai schema epure
    st.pyplot(fig_sch)
    
    # --- SUITE DU MODULE (LABORATOIRE ET SAISIE) ---
    st.write("---")
    analyser_systeme_forces(nb_forces=scen["forces"], suffixe_clef=f"metier_{metier_cle}", nom_onglet=f"Atelier_6_{metier_cle}")
    
    st.write("---")
    col_quiz, col_trous = st.columns(2)
    
    with col_quiz:
        st.markdown(f"##### Quiz Technique : {data['nom']}")
        for idx, q_data in enumerate(st.session_state.quiz_metier_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"met_at_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthese Applicative (Texte à trous)")
        for enonce, choix, _, cle in st.session_state.trous_metier_statiques:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
            

def afficher_atelier_plus_trois_forces_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 5 (Équilibre à plus de trois forces) sur deux colonnes."""
    import random
    import streamlit as st

    questions_plus_f_sources = [
        {"id": "qpf1", "q": "Pour un système à N forces en équilibre, la géométrie du dynamique bout à bout forme un :", "options": ["Polygone fermé à N côtés", "Triangle équilatéral unique", "Cercle de rayon infini"], "rep": "Polygone fermé à N côtés"},
        {"id": "qpf2", "q": "La condition analytique d'équilibre reste-t-elle identique quel que soit le nombre de forces ?", "options": ["Oui, la somme de toutes les composantes Fx et Fy doit rester nulle", "Non, il faut ajouter un axe de projection par force", "Seulement si le nombre de forces est pair"], "rep": "Oui, la somme de toutes les composantes Fx et Fy doit rester nulle"},
        {"id": "qpf3", "q": "Si un point subit 4 forces et que la somme des 3 premières donne un vecteur unique V, la 4ème force doit être :", "options": ["Directement opposée à V (-V)", "Perpendiculaire à V", "Égale à zéro"], "rep": "Directement opposée à V (-V)"},
        {"id": "qpf4", "q": "Comment évolue la complexité du tracé graphique lorsque le nombre de forces augmente ?", "options": ["Le nombre de segments du polygone augmente mais la règle de fermeture reste la même", "Le polygone devient obligatoirement un carré", "La méthode graphique devient mathématiquement fausse"], "rep": "Le nombre de segments du polygone augmente mais la règle de fermeture reste la même"},
        {"id": "qpf5", "q": "Si le polygone de 5 forces se referme exactement sur lui-même, on en déduit que :", "options": ["L'accélération du point matériel est nulle (statique)", "Le système possède une force résultante motrice", "Toutes les forces ont la même norme"], "rep": "L'accélération du point matériel est nulle (statique)"},
        {"id": "qpf6", "q": "Dans un système concourant complexe, modifier l'intensité d'une seule force :", "options": ["Rompt l'équilibre global sauf si une another force compense exactement", "Ne change rien si le système contient plus de 6 forces", "Modifie uniquement l'axe horizontal X"], "rep": "Rompt l'équilibre global sauf si une autre force compense exactement"},
        {"id": "qpf7", "q": "Pour équilibrer parfaitement 4 forces de même norme distribuées de manière régulière, l'écart angulaire entre chaque force successive doit être de :", "options": ["90 degrés", "120 degrés", "45 degrés"], "rep": "90 degrés"},
        {"id": "qpf8", "q": "Si la somme des projections horizontales donne un résultat non nul, le point matériel va :", "options": ["Subir une accélération sur l'axe horizontal X", "Rester en équilibre statique parfait", "Se déplacer uniquement sur l'axe vertical Y"], "rep": "Subir une accélération sur l'axe horizontal X"},
        {"id": "qpf9", "q": "La méthode de décomposition analytique par tableau de composants (Fx, Fy) est recommandée pour N forces car :", "options": ["Elle permet d'additionner simplement les valeurs numériques axe par axe", "Elle élimine le besoin d'utiliser les fonctions cosinus et sinus", "Elle limite le nombre de forces utilisables à un maximum de 4"], "rep": "Elle permet d'additionner simplement les valeurs numériques axe par axe"},
        {"id": "qpf10", "q": "Lorsque le polygone des forces reste ouvert, le vecteur reliant l'extrémité finale à l'origine de départ est :", "options": ["La force équilibrante nécessaire à la statique", "La force résultante de déséquilibre", "La force de frottement cinétique"], "rep": "La force équilibrante nécessaire à la statique"},
    ]

    if "ordre_quiz_tab5_aleatoire" not in st.session_state:
        random.shuffle(questions_plus_f_sources)
        st.session_state.ordre_quiz_tab5_aleatoire = questions_plus_f_sources

    champs_plus_f = [
        ("1. Un ensemble de plusieurs forces concourantes converge vers un seul .........", ["Choisir...", "point", "axe"], "point", "pf_t1_final"),
        ("2. Leur dynamique graphique complet engendre un .......... complexe.", ["Choisir...", "polygone", "segment"], "polygone", "pf_t2_final"),
        ("3. L'équilibre statique exige une somme vectorielle strictement ...........", ["Choisir...", "nulle", "positive"], "nulle", "pf_t3_final"),
        ("4. Une trajectoire accélérée indique la présence d'un ......", ["Choisir...", "déséquilibre", "équilibre"], "déséquilibre", "pf_t4_final"),
        ("5. La méthode par tableau additionne les composantes sur chaque ........", ["Choisir...", "axe", "angle"], "axe", "pf_t5_final"),
        ("6. La dernière force ferme la trajectoire géométrique du .........", ["Choisir...", "dynamique", "repère"], "dynamique", "pf_t6_final"),
        ("7. Augmenter le nombre de vecteurs ne change pas la condition d'.......", ["Choisir...", "équilibre", "mesure"], "équilibre", "pf_t7_final"),
        ("8. Le retour exact à l'origine valide l'absence de force ..........", ["Choisir...", "résultante", "normale"], "résultante", "pf_t8_final"),
        ("9. Chaque force oblique se scinde en coordonnées horizontales et ..........", ["Choisir...", "verticales", "parallèles"], "verticales", "pf_t9_final"),
        ("10. Un polygone ouvert nécessite l'action d'une force .........", ["Choisir...", "équilibrante", "motrice"], "équilibrante", "pf_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Cas à Plus de 3 Forces (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"pf_at_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Cours Forces Multiples (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_plus_f:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
            
def afficher_atelier_trois_forces_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 4 (Équilibre à trois forces) sur deux colonnes."""
    import random
    import streamlit as st

    questions_3f_sources = [
        {"id": "q3f1", "q": "Pour que trois forces non parallèles soient en équilibre, leurs lignes d'action doivent être obligatoirement :", "options": ["Concourantes (se couper en un point)", "Parallèles entre elles", "Perpendiculaires deux à deux"], "rep": "Concourantes (se couper en un point)"},
        {"id": "q3f2", "q": "Géométriquement, le dynamique de trois forces en équilibre forme un :", "options": ["Triangle fermé", "Rectangle parfait", "Segment rectiligne plat"], "rep": "Triangle fermé"},
        {"id": "q3f3", "q": "Si un point est soumis à trois forces de 10 N chacune en équilibre, quel est l'écart angulaire régulier entre elles ?", "options": ["120 degrés", "90 degrés", "60 degrés"], "rep": "120 degrés"},
        {"id": "q3f4", "q": "Si la somme vectorielle de deux premières forces vaut un vecteur R, la troisième force F3 doit être :", "options": ["Égale et opposée à R (F3 = -R)", "Identique à R (F3 = R)", "Perpendiculaire à R"], "rep": "Égale et opposée à R (F3 = -R)"},
        {"id": "q3f5", "q": "Trois forces s'appliquant sur un point ont pour coordonnées cumulées (Fx=0, Fy=5). Le système est-il équilibré ?", "options": ["Non, il y a un mouvement vers le haut", "Oui, car Fx été nulle", "Oui, le point reste immobile"], "rep": "Non, il y a un mouvement vers le haut"},
        {"id": "q3f6", "q": "Lorsque le triangle des forces est tracé bout à bout, la pointe du troisième vecteur arrive :", "options": ["Exactement à l'origine du premier vecteur", "À une distance égale à la moyenne des normes", "À l'infini"], "rep": "Exactement à l'origine du premier vecteur"},
        {"id": "q3f7", "q": "Le théorème des trois forces stipule que si deux droites d'action se coupent en un point P, la troisième passe par :", "options": ["Ce même point P", "L'origine du repère uniquement", "Le milieu du segment opposé"], "rep": "Ce même point P"},
        {"id": "q3f8", "q": "Un solide glisse à vitesse constante sur un plan incliné avec frottement. Il subit le poids, la réaction normale et la friction. Le système est en statique ?", "options": ["Oui, la vitesse étant constante, la somme des 3 forces est nulle", "Non, car l'objet est en déplacement", "Seulement si le plan est vertical"], "rep": "Oui, la vitesse étant constante, la somme des 3 forces est nulle"},
        {"id": "q3f9", "q": "Si le triangle des forces tracé bout à bout reste ouvert, l'espace vide restant représente :", "options": ["La force résultante de déséquilibre", "La force d'appui", "Une erreur de mesure impossible en physique"], "rep": "La force résultante de déséquilibre"},
        {"id": "q3f10", "q": "La condition analytique complète pour l'équilibre à trois forces nécessite :", "options": ["La nullité simultanée de la somme des Fx et de la somme des Fy", "Que chaque force individuelle soit nulle", "Que l'angle total cumulé dépasse 360 degrés"], "rep": "La nullité simultanée de la somme des Fx et de la somme des Fy"},
    ]

    if "ordre_quiz_tab4_aleatoire" not in st.session_state:
        random.shuffle(questions_3f_sources)
        st.session_state.ordre_quiz_tab4_aleatoire = questions_3f_sources

    champs_3f = [
        ("1. Trois forces coplanaires non parallèles convergent en un point .........", ["Choisir...", "concourant", "distant"], "concourant", "3f_t1_final"),
        ("2. Leur représentation géométrique bout à bout crée un ..........", ["Choisir...", "triangle", "cercle"], "triangle", "3f_t2_final"),
        ("3. Pour stabiliser le point matériel, la résultante doit être ...........", ["Choisir...", "nulle", "maximale"], "nulle", "3f_t3_final"),
        ("4. Une fermeture manquante sur le graphique traduit un ......", ["Choisir...", "déséquilibre", "alignement"], "déséquilibre", "3f_t4_final"),
        ("5. La somme algébrique des projections horizontales vaut ........", ["Choisir...", "zéro", "le triple"], "zéro", "3f_t5_final"),
        ("6. La troisième force neutralise la résultante des ......... premières.", ["Choisir...", "deux", "quatre"], "deux", "3f_t6_final"),
        ("7. Modifier un seul paramètre rompt immédiatement l'.......", ["Choisir...", "équilibre", "alignement"], "équilibre", "3f_t7_final"),
        ("8. Le polygone fermé confirme la validité de la méthode ..........", ["Choisir...", "graphique", "analytique"], "graphique", "3f_t8_final"),
        ("9. Les forces concourantes agissent sur un unique point ..........", ["Choisir...", "matériel", "virtuel"], "matériel", "3f_t9_final"),
        ("10. En statique, le vecteur final retourne à la position de .........", ["Choisir...", "départ", "fermeture"], "départ", "3f_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Cas à 3 Forces (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"3f_at_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Cours 3 Forces (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_3f:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
            
def afficher_atelier_deux_forces_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 3 (Équilibre à deux forces) sur deux colonnes."""
    import random
    import streamlit as st

    questions_2f_sources = [
        {"id": "q2f1", "q": "Si un point matériel est soumis à deux forces en équilibre, leurs directions sont obligatoirement :", "options": ["Confondues (colinéaires)", "Perpendiculaires", "Quelconques"], "rep": "Confondues (colinéaires)"},
        {"id": "q2f2", "q": "Pour deux forces en équilibre, si F1 vaut 15 N, que vaut obligatoirement F2 ?", "options": ["15 N", "-15 N (une norme est positive)", "0 N"], "rep": "15 N"},
        {"id": "q2f3", "q": "Quel est l'écart angulaire exact entre deux forces s'équilibrant sur une même droite ?", "options": ["180 degrés", "90 degrés", "0 degré"], "rep": "180 degrés"},
        {"id": "q2f4", "q": "Graphiquement, le dynamique de deux forces en équilibre se traduit par :", "options": ["Un aller-retour sur le même segment", "Un triangle rectangle", "Une boucle circulaire"], "rep": "Un aller-retour sur le même segment"},
        {"id": "q2f5", "q": "Si deux forces ont la même norme et la même direction mais le même sens :", "options": ["Le système accélère, il n'y a pas équilibre", "Le système reste immobile", "La résultante est nulle"], "rep": "Le système accélère, il n'y a pas équilibre"},
        {"id": "q2f6", "q": "L'énoncé 'Deux forces opposées s'annulent' impose que les forces agissent sur :", "options": ["Le même point matériel", "Deux objets différents", "Des axes perpendiculaires"], "rep": "Le même point matériel"},
        {"id": "q2f7", "q": "Si F1 a un angle de 45 degrés, quel angle doit avoir F2 pour l'équilibrer ?", "options": ["225 degrés (45 + 180)", "135 degrés", "-45 degrés"], "rep": "225 degrés (45 + 180)"},
        {"id": "q2f8", "q": "Un solide suspendu à un fil vertical subit son poids et la tension du fil. Ces forces sont :", "options": ["Directement opposées et verticales", "Perpendiculaires entre elles", "D'intensités différentes"], "rep": "Directement opposées et verticales"},
        {"id": "q2f9", "q": "La relation vectorielle fondamentale pour deux forces F1 et F2 en équilibre est :", "options": ["F1 + F2 = 0", "F1 - F2 = 0", "F1 * F2 = 0"], "rep": "F1 + F2 = 0"},
        {"id": "q2f10", "q": "Si la somme de deux forces n'est pas nulle, le vecteur manquant pour assurer la statique s'appelle :", "options": ["La force équilibrante", "La force résultante", "La force motrice"], "rep": "La force équilibrante"},
    ]

    if "ordre_quiz_tab3_aleatoire" not in st.session_state:
        random.shuffle(questions_2f_sources)
        st.session_state.ordre_quiz_tab3_aleatoire = questions_2f_sources

    champs_2f = [
        ("1. Deux forces en équilibre possèdent la même droite d'.........", ["Choisir...", "action", "intensité"], "action", "2f_t1_final"),
        ("2. Les sens de ces deux vecteurs forces doivent être ..........", ["Choisir...", "opposés", "identiques"], "opposés", "2f_t2_final"),
        ("3. Leurs valeurs numériques ou normes doivent être ...........", ["Choisir...", "égales", "proportionnelles"], "égales", "2f_t3_final"),
        ("4. La résultante analytique R d'un système équilibré vaut ......", ["Choisir...", "zéro", "le double"], "zéro", "2f_t4_final"),
        ("5. Deux forces colinéaires opposées forment un polygone ........", ["Choisir...", "fermé", "ouvert"], "fermé", "2f_t5_final"),
        ("6. Modifier l'intensité de F1 sans changer F2 crée un .........", ["Choisir...", "déséquilibre", "alignement"], "déséquilibre", "2f_t6_final"),
        ("7. La tension du câble s'oppose exactement à l'effet du .......", ["Choisir...", "poids", "vent"], "poids", "2f_t7_final"),
        ("8. Sur l'axe de projection, les valeurs algébriques sont ..........", ["Choisir...", "opposées", "nulles"], "opposées", "2f_t8_final"),
        ("9. L'absence de mouvement prouve que la somme vectorielle est ..........", ["Choisir...", "nulle", "infinie"], "nulle", "2f_t9_final"),
        ("10. Si le système glisse ou tombe, les deux forces sont .........", ["Choisir...", "différentes", "égales"], "différentes", "2f_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Cas à 2 Forces (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"2f_at_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Cours 2 Forces (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_2f:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")
            

def afficher_atelier_base_sustentation_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 2 (Base de sustentation) sur deux colonnes."""
    import random
    import streamlit as st

    questions_sustent_sources = [
        {"id": "qs1", "q": "La base de sustentation correspond geometriquement au plus petit polygone :", "options": ["Convexe enveloppant les appuis", "Concave reliant les appuis", "Regulier centre sur l'origine"], "rep": "Convexe enveloppant les appuis"},
        {"id": "qs2", "q": "Pour assurer l'equilibre statique, la ligne d'action verticale du poids doit :", "options": ["Couper la base de sustentation", "Froler l'exterieur des appuis", "Etre parallele au sol"], "rep": "Couper la base de sustentation"},
        {"id": "qs3", "q": "Si un athlete ecarte ses deux pieds au sol, la surface de sa base de sustentation :", "options": ["Augmente", "Diminue", "Reste rigoureusement identique"], "rep": "Augmente"},
        {"id": "qs4", "q": "Si un individu se tient debout en appui sur un seul pied, sa base de sustentation est :", "options": ["Reduite a la surface de ce seul pied", "Le rectangle delimitant ses deux jambes", "Un point virtuel sans surface"], "rep": "Reduite a la surface de ce seul pied"},
        {"id": "qs5", "q": "Quel savant de la Renaissance a etudie les ajustements posturaux lies au centre de masse ?", "options": ["Leonard de Vinci", "Isaac Newton", "Rene Descartes"], "rep": "Leonard de Vinci"},
        {"id": "qs6", "q": "En biomecanique, l'abaissement de la position du centre de gravite a pour effet d' :", "options": ["Accroitre la stabilite", "Provoquer un basculement immediat", "Reduire les points d'appui"], "rep": "Accroitre la stabilite"},
        {"id": "qs7", "q": "Lorsque la projection verticale du centre de gravite sort du polygone d'appui :", "options": ["Le solide bascule", "L'equilibre devient indifferent", "La force gravitationnelle s'annule"], "rep": "Le solide bascule"},
        {"id": "qs8", "q": "L'ouvrage mecanique de reference 'De Motu Animalium' (1680) a ete redige par :", "options": ["Giovanni Alfonso Borelli", "Archimede de Syracuse", "Galileo Galilei"], "rep": "Giovanni Alfonso Borelli"},
        {"id": "qs9", "q": "Les verins stabilisateurs deployes sur une grue mobile servent specifiquement a :", "options": ["Elargir la base de sustentation", "Reduire la masse totale de la grue", "Augmenter l'altitude de la fleche"], "rep": "Elargir la base de sustentation"},
        {"id": "qs10", "q": "La stabilite d'un corps pose sur un plan est inversement proportionnelle a :", "options": ["La hauteur de son centre de gravite", "La surface totale de ses appuis", "La norme de sa force de reaction"], "rep": "La hauteur de son centre de gravite"},
    ]

    if "ordre_quiz_tab2_aleatoire" not in st.session_state:
        random.shuffle(questions_sustent_sources)
        st.session_state.ordre_quiz_tab2_aleatoire = questions_sustent_sources

    # Conservation stricte de vos tuples d'origine à 4 éléments
    champs_s = [
        ("1. Le polygone geometrique reliant les appuis au sol est la base de .........", ["Choisir...", "sustentation", "translation"], "sustentation", "sust_t1_final"),
        ("2. L'equilibre d'un solide exige que la projection de G se situe a l'..........", ["Choisir...", "interieur", "exterieur"], "interieur", "sust_t2_final"),
        ("3. Ecarter les pieds permet d'obtenir une stabilite accrue en .......... la base.", ["Choisir...", "agrandissant", "reduisant"], "agrandissant", "sust_t3_final"),
        ("4. Une hauteur reduite du centre de gravite favorise un meilleur ..........", ["Choisir...", "equilibre", "mouvement"], "equilibre", "sust_t4_final"),
        ("5. Lorsque le vecteur poids sort de la zone d'appui, l'objet subit un ..........", ["Choisir...", "basculement", "glissement"], "basculement", "sust_t5_final"),
        ("6. Archimede a pose les premieres lois statiques des figures ..........", ["Choisir...", "planes", "espace"], "planes", "sust_t6_final"),
        ("7. Pour une grue, l'usage de verins elargit la geometrie des ..........", ["Choisir...", "appuis", "cables"], "appuis", "sust_t7_final"),
        ("8. Modifier sa posture corporelle entraine un deplacement du centre de ..........", ["Choisir...", "gravite", "symetrie"], "gravite", "sust_t8_final"),
        ("9. Le polygone minimal englobant tous les contacts au sol doit etre ..........", ["Choisir...", "convexe", "concave"], "convexe", "sust_t9_final"),
        ("10. Avancer rapidement un pied lors d'une chute permet le .......... de l'equilibre.", ["Choisir...", "retablissement", "blocage"], "retablissement", "sust_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Base de Sustentation (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"sust_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthese Base de Sustentation (Texte a trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_s:
            c_txt, c_sel = st.columns([0.70, 0.30], vertical_alignment="bottom")
            with c_txt: st.write(enonce)
            with c_sel: st.selectbox("", choix, key=cle, disabled=verrouille, label_visibility="collapsed")





def afficher_atelier_decomposition_complet(verrouille=False):
    """Affiche le Quiz et le Texte à trous de l'Atelier 1 (Décomposition des forces) sur deux colonnes."""
    import random

    questions_decompo_sources = [
        {"id": "qd1", "q": "La decomposition d'une force dans un plan orthonorme genere :", "options": ["Deux composantes perpendiculaires", "Trois forces paralleles", "Une seule force de norme double"], "rep": "Deux composantes perpendiculaires"},
        {"id": "qd2", "q": "La composante horizontale Fx d'une force F faisant un angle alpha avec l'axe X vaut :", "options": ["F * cos(alpha)", "F * sin(alpha)", "F / cos(alpha)"], "rep": "F * cos(alpha)"},
        {"id": "qd3", "q": "Si une force est entierement verticale et dirigee vers le haut, sa composante Fx vaut :", "options": ["0", "Sa norme totale", "Une valeur negative"], "rep": "0"},
        {"id": "qd4", "q": "La methode analytique consiste a remplacer un vecteur force par :", "options": ["La somme de ses composantes projetees", "Un vecteur de sens oppose", "Une valeur scalaire fixe"], "rep": "La somme de ses composantes projetees"},
        {"id": "qd5", "q": "Lors d'une projection, si l'angle alpha d'une force vaut 90 degres, sa composante Fy est egale a :", "options": ["La norme totale de la force", "Zero", "La moitie de la norme"], "rep": "La norme totale de la force"},
        {"id": "qd6", "q": "Le repere couramment utilise pour decomposer les forces en statique est :", "options": ["Un repere orthonorme (O, X, Y)", "Un repere polaire a une dimension", "Une echelle logarithmique"], "rep": "Un repere orthonorme (O, X, Y)"},
        {"id": "qd7", "q": "Decomposer graphiquement une force revient geometriquement a construire :", "options": ["Un rectangle ou parallelogramme", "Un cercle trigonometrique complet", "Une ligne droite infinie"], "rep": "Un rectangle ou parallelogramme"},
        {"id": "qd8", "q": "Une force possede une composante Fx negative si le vecteur est oriente vers :", "options": ["La gauche", "La droite", "Le haut"], "rep": "La gauche"},
        {"id": "qd9", "q": "Pour valider la resultante totale analytique, on effectue la somme de :", "options": ["Toutes les composantes sur le meme axe", "Toutes les normes entre elles", "Tous les angles des forces"], "rep": "Toutes les composantes sur le meme axe"},
        {"id": "qd10", "q": "Connaissant Fx et Fy, comment retrouve-t-on la norme totale F de la force ?", "options": ["Par le theoreme de Pythagore", "En faisant l'addition Fx + Fy", "Par une simple soustraction"], "rep": "Par le theoreme de Pythagore"},
    ]

    if "ordre_quiz_tab1_aleatoire" not in st.session_state:
        random.shuffle(questions_decompo_sources)
        st.session_state.ordre_quiz_tab1_aleatoire = questions_decompo_sources

    # Conservation stricte de vos tuples d'origine à 4 éléments
    champs_d = [
        ("1. Decomposer une force permet d'obtenir ses composantes .........", ["Choisir...", "orthogonales", "paralleles"], "orthogonales", "dec_t1_final"),
        ("2. Les vecteurs associes aux composantes ne doivent pas se ..........", ["Choisir...", "chevaucher", "aligner"], "chevaucher", "dec_t2_final"),
        ("3. La projection sur l'axe horizontal X utilise la fonction ...........", ["Choisir...", "cosinus", "sinus"], "cosinus", "dec_t3_final"),
        ("4. La projection sur l'axe vertical Y utilise la fonction ......", ["Choisir...", "sinus", "cosinus"], "sinus", "dec_t4_final"),
        ("5. Une composante horizontale et une verticale forment un triangle ........", ["Choisir...", "rectangle", "equilateral"], "rectangle", "dec_t5_final"),
        ("6. Trouver le signe d'une composante depend du ......... des axes.", ["Choisir...", "sens", "nombre"], "sens", "dec_t6_final"),
        ("7. Diviser une force en deux projections facilite l'application des ....... de base.", ["Choisir...", "formules", "angles"], "formules", "dec_t7_final"),
        ("8. L'intensité reelle de la force demeure .......... peu importe le repere.", ["Choisir...", "invariante", "variable"], "invariante", "dec_t8_final"),
        ("9. Un vecteur oblique se decompose en une partie horizontale et une ..........", ["Choisir...", "verticale", "oblique"], "verticale", "dec_t9_final"),
        ("10. Combiner les sous-composantes permet d'evaluer la resultante.........", ["Choisir...", "totale", "partielle"], "totale", "dec_t10_final"),
    ]

    col_quiz, col_trous = st.columns(2)
    with col_quiz:
        st.markdown("##### Quiz Décomposition des Forces (10 questions - 10 pts)")
        for idx, q_data in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
            st.write(f"**{idx}.** {q_data['q']}")
            cle_select = f"dec_at6_final_g_{q_data['id']}"
            opts_affichees = ["Choisir..."] + q_data["options"]
            st.selectbox("", options=opts_affichees, key=cle_select, disabled=verrouille, label_visibility="collapsed")

    with col_trous:
        st.markdown("##### Synthèse Décomposition (Texte à trous - 10 cases - 10 pts)")
        for enonce, choix, _, cle in champs_d:
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
    st.header("Histoire et Fondements de la Statique")

    st.subheader("Un peu d'histoire : Les grands fondateurs")
    st.write("Découvrez les scientifiques majeurs dont les travaux ont permis de bâtir les lois de la statique moderne.")

    st.write("---")

    # --- 1. ARCHIMÈDE ---
    st.markdown("### 1. Archimède de Syracuse (IIIe siècle av. J.-C.)")

    arc_col1, arc_col2 = st.columns(2)
    with arc_col1:
        if os.path.exists("portrait_archimede.jpg"):
            st.image("portrait_archimede.jpg", caption="Portrait d'Archimède", use_container_width=True)
        else:
            st.info("Illustration : Portrait historique d'Archimède de Syracuse.")
    with arc_col2:
        if os.path.exists("decouverte_archimede.jpg"):
            st.image("decouverte_archimede.jpg", caption="La loi du levier et de la balance", use_container_width=True)
        else:
            st.info("Illustration : Schéma mécanique d'un levier en équilibre sur son point d'appui.")
            
    st.markdown("""
    **Son apport fondamental :**  
    Archimède pose les premières lois géométriques et mathématiques de la statique dans son traité *De l'équilibre des figures planes*. 
    En étudiant les leviers et les balances, il formalise le concept de **centre de gravité**. Pour lui, l'équilibre est purement 
    géométrique et se définit comme une balance parfaite des poids autour d'un point de pivot. Sa célèbre phrase *"Donnez-moi un 
    point d'appui et je souleverai la Terre"* illustre la loi mathématique du moment d'une force.
    """)

    st.write("---")

    # --- 2. SIMON STEVIN ---
    st.markdown("### 2. Simon Stevin (XVIe siècle)")

    stev_col1, stev_col2 = st.columns(2)
    with stev_col1:
        if os.path.exists("portrait_stevin.jpg"):
            st.image("portrait_stevin.jpg", caption="Portrait de Simon Stevin", use_container_width=True)
        else:
            st.info("Illustration : Portrait du mathématicien et ingénieur hollandais Simon Stevin.")
    with stev_col2:
        if os.path.exists("decouverte_stevin.jpg"):
            st.image("decouverte_stevin.jpg", caption="Le plan incliné et le triangle des forces", use_container_width=True)
        else:
            st.info("Illustration : Représentation historique du 'Cloothkrans' (couronne de sphères) sur un plan incliné.")
            
    st.markdown("""
    **Son apport fondamental :**  
    Ce scientifique et ingénieur hollandais révolutionne la mécanique en découvrant la loi de la composition des forces. À travers l'étude 
    du plan incliné, il démontre comment plusieurs forces obliques agissent sur un même objet. C'est lui qui introduit le principe 
    fondamental du **triangle des forces**, posant ainsi les bases scientifiques de la statique graphique moderne qui permet de résoudre 
    des problèmes mécaniques par le dessin vectoriel.
    """)

    st.write("---")

    # --- 3. ISAAC NEWTON ---
    st.markdown("### 3. Isaac Newton (XVIIe siècle)")

    newt_col1, newt_col2 = st.columns(2)
    with newt_col1:
        if os.path.exists("portrait_newton.jpg"):
            st.image("portrait_newton.jpg", caption="Portrait d'Isaac Newton", use_container_width=True)
        else:
            st.info("Illustration : Portrait du physicien britannique Isaac Newton.")
    with newt_col2:
        if os.path.exists("decouverte_newton.jpg"):
            st.image("decouverte_newton.jpg", caption="Les lois du mouvement (Principia)", use_container_width=True)
        else:
            st.info("Illustration : Diagramme des forces d'action et de réaction réciproques.")
            
    st.markdown("""
    **Son apport fondamental :**  
    En 1687, dans son ouvrage majeur *Principia Mathematica*, Isaac Newton formalise sa première loi appelée **principe d'inertie**. 
    Cette loi stipule que tout corps persévère dans son état de repos ou de mouvement rectiligne uniforme si les forces qui s'exercent 
    sur lui s'annulent. Newton apporte ainsi un cadre théorique universel : l'immobilité (la statique) devient un cas particulier de la 
    dynamique où l'accélération du système est rigoureusement nulle.
    """)

    st.write("---")

    # --- 4. PIERRE VARIGNON ---
    st.markdown("### 4. Pierre Varignon (XVIIe siècle)")

    var_col1, var_col2 = st.columns(2)
    with var_col1:
        if os.path.exists("portrait_varignon.jpg"):
            st.image("portrait_varignon.jpg", caption="Portrait de Pierre Varignon", use_container_width=True)
        else:
            st.info("Illustration : Portrait du mathématicien français Pierre Varignon.")
    with var_col2:
        if os.path.exists("decouverte_varignon.jpg"):
            st.image("decouverte_varignon.jpg", caption="Le théorème des moments et le polygone des forces", use_container_width=True)
        else:
            st.info("Illustration : Tracé géométrique d'un polygone de forces concourantes en équilibre.")
            
    st.markdown("""
    **Son apport fondamental :**  
    Le mathématicien français Pierre Varignon unifie définitivement les approches de ses prédécesseurs. Dans son *Projet d'une nouvelle 
    mécanique*, il énonce le théorème des moments et démontre la stricte équivalence entre la géométrie et l'algèbre. Il prive que 
    l'équilibre géométrique d'un système (la fermeture parfaite du **polygone des forces**) correspond mathématiquement à l'équilibre 
    algébrique (la somme des projections des composantes sur les axes X et Y est égale à zéro).
    """)

    # --- TEXTE EXPLICATIF PHYSIQUE ---
    st.write("---")
    st.subheader("Explication physique de l'équilibre")
    st.markdown("""
    Pour qu'un point matériel reste parfaitement immobile dans notre repère, les forces qui agissent sur lui doivent s'annuler mutuellement. Si ce n'était pas le cas, l'objet se mettrait en mouvement et accélérerait.

    Pour vérifier cet équilibre, deux approches complémentaires existent :

    1. **L'approche analytique (Algébrique) :**
       On projette chaque force sur deux axes perpendiculaires (X et Y). On calcule les composantes $F_x$ et $F_y$ pour chaque force grâce à la trigonométrie :
       $$ F_x = F \\cdot \\cos(\\alpha) $$
       $$ F_y = F \\cdot \\sin(\\alpha) $$
       Le système est en équilibre si et seulement si la somme de toutes les composantes horizontales est nulle ($\sum F_x = 0$) **et** la somme de toutes les composantes verticales est nulle ($\sum F_y = 0$).
       
    2. **L'approche graphique (Géométrique) :**
       On dessine le premier vecteur force. À partir de la pointe de ce premier vecteur, on dessine le deuxième, puis le troisième, et ainsi de suite. 
       * Si le système est en équilibre, la pointe du tout dernier vecteur vient se repositionner **exactement sur le point de départ** du premier vecteur. On dit alors que le **polygone des forces est fermé**.
       * Si le polygone reste ouvert, l'espace vide entre le point de départ et le point d'arrivée représente la **force résultante** (le déséquilibre).
    """)

    st.write("---")        
    if "suite_verrouille_tab1" not in st.session_state:
        st.session_state.suite_verrouille_tab1 = False
    verrou_at1 = st.session_state.suite_verrouille_tab1

    afficher_atelier_decomposition_complet(verrouille=verrou_at1)
    
    st.write("---")
    st.subheader("Synthese et validation de l'Atelier 1")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat1 = st.checkbox(
        "Je certifie avoir complete les questions de l'Atelier Decomposition.",
        key="check_certif_generalites_final_net",
        disabled=verrou_at1,
    )
    
    # --- 4. BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 1", key="btn_export_suite1_official_net", use_container_width=True, disabled=verrou_at1):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusee : Saisissez votre identite dans l'onglet 'Identification'.")
        elif not case_certif_stat1: 
            st.error("Action refusee : Cochez la case de certification.")
        else:
            score_q1 = 0.0
            if "ordre_quiz_tab1_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab1_aleatoire:
                    reponse_eleve = st.session_state.get(f"dec_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q1 += 1.0

            # Verification des bonnes reponses du texte a trous adapte a la statique
            score_t1 = sum(
                [
                    st.session_state.get("dec_t1_final") == "orthogonales",
                    st.session_state.get("dec_t2_final") == "chevaucher",
                    st.session_state.get("dec_t3_final") == "cosinus",
                    st.session_state.get("dec_t4_final") == "sinus",
                    st.session_state.get("dec_t5_final") == "rectangle",
                    st.session_state.get("dec_t6_final") == "sens",
                    st.session_state.get("dec_t7_final") == "formules",
                    st.session_state.get("dec_t8_final") == "invariante",
                    st.session_state.get("dec_t9_final") == "verticale",
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
        st.success(f"ATELIER DECOMPOSITION SCELLE | Note de session : {tot_s:.1f} / 20")

        html_export_suites = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Decomposition - {n_eleve}</title>
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
                <h1>Rapport d'Evaluation de Mecanique - Statique</h1>
                <p>Atelier 1 : Decomposition vectorielle des forces</p>
                <p>Eleve : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scelle le : {timestamp_suite1}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s:.1f}</span> / 20</div>
            </div>
            <div class="sub-title">Recapitulatif des Notes Generees</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Decomposition : <strong>{scr1:.1f} / 10</strong><br>
                Note obtenue a la Synthese du cours : <strong>{scr2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 1 : <strong>{tot_s:.1f} / 20</strong>
            </p>
            <div class="sub-title">CORRECTION DETAILLEE DU QUIZ (ORDRE D'AFFICHAGE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posee</th><th>Saisie Eleve</th><th>Attendu Academique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        # Rectification ici : Appel de la liste de session stockee a l'atelier 1
        if "ordre_quiz_tab1_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab1_aleatoire, 1):
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
            label="Telecharger le rapport d'evaluation officiel de l'Atelier 1 (.html)",
            data=html_export_suites,
            file_name=nom_fichier_html,
            mime="text/html",
            use_container_width=True
        )


with tab2:
    st.header("Base de sustentation")
    
    # Section 1 : Théorie
    st.subheader("1. Approche historique et theorique")
    st.write("""
    L'etude de la stabilite des corps remonte aux fondements de la statique geometrique. **Archimede de Syracuse** 
    pose les premieres bases de la geometrie des centres de gravite dans son traite *De l'equilibre des figures planes*. 
    Plus tard, au XVIIe siecle, **Giovanni Alfonso Borelli** formalise le fait que le maintien de la station debout 
    exige que la projection verticale du centre de gravite tombe precisement entre les pieds.
    
    ### Definition mecanique
    La base de sustentation est la surface geometrique plane convexe minimale qui enveloppe l'ensemble des points 
    d'appui d'un corps avec le sol. 
    
    Pour qu'un solide reste en equilibre statique, la droite d'action verticale de son poids (passant par le centre 
    de gravite G) doit imperativement intersecter la surface de cette base de sustentation.
    """)
    
    # Section 2 : Exemples en images (Fichiers JPG)
    st.subheader("2. Exemples d'application")
    
    col1, col2 = st.columns(2)

    with col1:
        # Verification de la presence du fichier geometrique ou basculement textuel
        if os.path.exists("grue_stabilite.jpg"):
            st.image("grue_stabilite.jpg", caption="Exemple 1 : Engin de chantier mecanique")
        else:
            st.info("Illustration : Vue d'une grue mobile de levage avec ses quatre stabilisateurs hydrauliques deployes au maximum sur le sol.")
            
        st.write("""
        **Analyse de la stabilite :** Les verins hydrauliques (stabilisateurs) ecartent les points de contact avec 
        le sol bien au-dela des roues du camion. Cela agrandit la base de sustentation pour eviter le basculement 
        lors du levage de charges lourdes reculees.
        """)
        
    with col2:
        # Verification de la presence du fichier biomecanique ou basculement textuel
        if os.path.exists("athlete_posture.jpg"):
            st.image("athlete_posture.jpg", caption="Exemple 2 : Biomecanique humaine")
        else:
            st.info("Illustration : Posture basse d'un athlete en position de garde, les appuis ecartes au-dela de la largeur des epaules.")
            
        st.write("""
        **Analyse de la stabilite :** L'athlete augmente sa stabilite en ecartant les pieds (agrandissement de la 
        base de sustentation) et en flechissant les jambes (abaissement du centre de gravite G). Cette configuration 
        demande une force exterieure beaucoup plus elevee pour provoquer un basculement.
        """)

    # Section 3 : Caricature pedagogique en 4 images
    st.subheader("Caricature de la stabilité (Séquence en 4 étapes)")

    # Séparation en deux colonnes : 60% pour le texte en bleu, 40% pour l'image unique
    col_texte, col_image = st.columns([0.6, 0.4])

    with col_texte:
        # Utilisation de st.info pour afficher l'ensemble du texte dans un encadré bleu avec les accents
        st.info("""
        ### Analyse de la stabilité et du basculement
        
        **Étape 1 : Posture initiale**
        Le personnage est immobile. La ligne de gravité tombe au centre des pieds joints. L'équilibre est assuré mais précaire.
        
        **Étape 2 : Déplacement de G**
        En poussant une charge, le corps s'incline. Le centre de gravité se déplace vers l'avant, frôlant la limite de la base.
        
        **Étape 3 : Perte d'équilibre**
        La projection de G sort de la base de sustentation. Le poids génère un moment de rotation : la chute est amorcée.
        
        **Étape 4 : Rétablissement**
        Le personnage avance un pied. Cette action crée instantanément une nouvelle base de sustentation plus large, englobant à nouveau la ligne de gravité.
        """)

    with col_image:
        # Remplacer "caricature_base_sustentation.jpg" par le nom exact de votre fichier image unique
        nom_image_caricature = "caricature_base_sustentation.jpg"
        
        if os.path.exists(nom_image_caricature):
            st.image(nom_image_caricature, caption="Séquence complète du basculement", use_container_width=True)
        else:
            st.warning(f"L'image {nom_image_caricature} est manquante sur le serveur.")
    st.write("---")        
    if "suite_verrouille_tab2" not in st.session_state:
        st.session_state.suite_verrouille_tab2 = False
    verrou_at2 = st.session_state.suite_verrouille_tab2

    # Insertion de la zone de questions/trous pour le tab 2
    afficher_atelier_base_sustentation_complet(verrouille=verrou_at2)

    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 2")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat2 = st.checkbox(
        "Je certifie avoir complété les questions et réglé le système de base de sustentation.",
        key="check_certif_tab2_final_net",
        disabled=verrou_at2,
    )

    # --- BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 2", key="btn_export_suite2_official_net", use_container_width=True, disabled=verrou_at2):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat2: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q2 = 0.0
            if "ordre_quiz_tab2_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab2_aleatoire:
                    reponse_eleve = st.session_state.get(f"sust_at6_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q2 += 1.0

            # Vérification des bonnes réponses du texte à trous du tab 2
            score_t2 = sum(
                [
                    st.session_state.get("sust_t1_final") == "sustentation",
                    st.session_state.get("sust_t2_final") == "interieur",
                    st.session_state.get("sust_t3_final") == "agrandissant",
                    st.session_state.get("sust_t4_final") == "equilibre",
                    st.session_state.get("sust_t5_final") == "basculement",
                    st.session_state.get("sust_t6_final") == "planes",
                    st.session_state.get("sust_t7_final") == "appuis",
                    st.session_state.get("sust_t8_final") == "gravite",
                    st.session_state.get("sust_t9_final") == "convexe",
                    st.session_state.get("sust_t10_final") == "retablissement",
                ]
            )

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
        
        st.success(f"ATELIER 2 SCELLÉ | Note globale de l'Atelier : {tot_s2:.1f} / 20")
        
        html_export_tab2 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Base de Sustentation - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Mécanique - Statique</h1>
                <p>Atelier 2 : Stabilité et base de sustentation</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite2}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s2:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Base de Sustentation : <strong>{scr1_2:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_2:.1f} / 10</strong><br>
                Note Totale de l'Atelier 2 : <strong>{tot_s2:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab2_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab2_aleatoire, 1):
                saisie = st.session_state.get(f"sust_at6_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tab2 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab2 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html2 = preparer_nom_fichier("Rapport_Atelier_2").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 2 (.html)",
            data=html_export_tab2,
            file_name=nom_fichier_html2,
            mime="text/html",
            use_container_width=True
        )






with tab3:

    st.header("Cas a 2 Forces")
    st.subheader("Caricature de l'équilibre à deux forces (Séquence en 4 étapes)")

    # Séparation en deux colonnes : 60% pour le texte en bleu, 40% pour l'image unique
    col_texte, col_image = st.columns([0.6, 0.4])   

    with col_texte:
        # Utilisation de st.info pour afficher l'ensemble du texte dans un encadré bleu avec les accents
        st.info("""
        ### Analyse de la statique à deux forces opposées
        
        **Étape 1 : Situation d'équilibre initial**
        Un personnage tire sur une corde fixée à un anneau mural rigide. Le système est parfaitement immobile car la force de traction et la réaction du mur ont la même droite d'action, des normes égales et des sens opposés.
        
        **Étape 2 : Augmentation de l'intensité**
        Le personnage prend davantage d'appui et tire deux fois plus fort. Simultanément, la force de réaction du support augmente instantanément de la même valeur. Les deux vecteurs s'allongent mais l'équilibre statique reste maintenu.
        
        **Étape 3 : Rupture de la droite d'action**
        La fixation murale glisse brusquement vers le haut le long d'un rail vertical. Les deux forces n'ont plus la même droite d'action commune. Cela crée un couple de forces qui engendre un mouvement de rotation du système.
        
        **Étape 4 : Déséquilibre et mouvement**
        La corde se rompt définitivement. La force de reaction s'annule instantanément tandis que la force de traction interne provoque la chute du personnage vers l'arrière. La somme vectorielle n'est plus nulle.
        """)

    with col_image:
        # Remplacer "caricature_deux_forces.jpg" par le nom exact de votre fichier image unique
        nom_image_2f = "caricature_deux_forces.jpg"
        
        if os.path.exists(nom_image_2f):
            st.image(nom_image_2f, caption="Séquence complète de l'équilibre à deux forces", use_container_width=True)
        else:
            st.warning(f"L'image {nom_image_2f} est manquante sur le serveur.")        
    st.write("Deux forces s'équilibrent si elles ont la meme droite d'action, des normes egales et des sens opposes.")
    analyser_systeme_forces(nb_forces=2, suffixe_clef="2f", nom_onglet="Equilibre_2_forces")

    st.write("---")        
    if "suite_verrouille_tab3" not in st.session_state:
        st.session_state.suite_verrouille_tab3 = False
    verrou_at3 = st.session_state.suite_verrouille_tab3

    # Insertion de la zone de questions/trous pour le tab 3
    afficher_atelier_deux_forces_complet(verrouille=verrou_at3)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 3")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat3 = st.checkbox(
        "Je certifie avoir complété les questions et réglé le système à deux forces.",
        key="check_certif_tab3_final_net",
        disabled=verrou_at3,
    )
    
    # --- BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 3", key="btn_export_suite3_official_net", use_container_width=True, disabled=verrou_at3):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat3: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q3 = 0.0
            if "ordre_quiz_tab3_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab3_aleatoire:
                    reponse_eleve = st.session_state.get(f"2f_at_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q3 += 1.0

            # Vérification des bonnes réponses du texte à trous du tab 3
            score_t3 = sum(
                [
                    st.session_state.get("2f_t1_final") == "action",
                    st.session_state.get("2f_t2_final") == "opposés",
                    st.session_state.get("2f_t3_final") == "égales",
                    st.session_state.get("2f_t4_final") == "zéro",
                    st.session_state.get("2f_t5_final") == "fermé",
                    st.session_state.get("2f_t6_final") == "déséquilibre",
                    st.session_state.get("2f_t7_final") == "poids",
                    st.session_state.get("2f_t8_final") == "opposées",
                    st.session_state.get("2f_t9_final") == "nulle",
                    st.session_state.get("2f_t10_final") == "différentes",
                ]
            )

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
        
        st.success(f"ATELIER 3 SCELLÉ | Note globale de l'Atelier : {tot_s3:.1f} / 20")
        
        html_export_tab3 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Équilibre 2 Forces - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Mécanique - Statique</h1>
                <p>Atelier 3 : Équilibre d'un solide soumis à deux forces</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite3}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s3:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz 2 Forces : <strong>{scr1_3:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_3:.1f} / 10</strong><br>
                Note Totale de l'Atelier 3 : <strong>{tot_s3:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab3_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab3_aleatoire, 1):
                saisie = st.session_state.get(f"2f_at_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tab3 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab3 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html3 = preparer_nom_fichier("Rapport_Atelier_3").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 3 (.html)",
            data=html_export_tab3,
            file_name=nom_fichier_html3,
            mime="text/html",
            use_container_width=True
        )



with tab4:
    st.header("Cas à 3 Forces")
    st.subheader("Caricature de l'équilibre à trois forces (Séquence en 4 étapes)")

    # Séparation en deux colonnes : 60% pour le texte en bleu, 40% pour l'image unique
    col_texte, col_image = st.columns([0.6, 0.4])

    with col_texte:
        # Utilisation de st.info pour afficher l'ensemble du texte dans un encadré bleu avec les accents
        st.info("""
        ### Analyse de la statique à trois forces concourantes
        
        **Étape 1 : Posture d'équilibre stable**
        Un panneau publicitaire est suspendu à un anneau central. Il reste parfaitement immobile sous l'action de trois forces coplanaires : son poids vertical dirigé vers le bas, et les deux tensions obliques des câbles de fixation latérale. Les trois droites d'action se coupent en un point unique concourant, et le dynamique vectoriel forme un triangle parfaitement fermé.
        
        **Étape 2 : Perturbation par une force externe**
        Une rafale de vent horizontal constante vient frapper le panneau. Le système pivote légèrement et trouve une nouvelle position d'équilibre inclinée. Le poids, la tension des câbles modifiée et la force de poussée du vent forment un nouveau système concourant où la somme vectorielle reste nulle, fermant toujours le triangle des forces.
        
        **Étape 3 : Rupture géométrique des lignes d'action**
        L'un des câbles d'attache se détache du mur et se bloque sur un support plus bas. Les lignes d'action du poids et des deux tensions de câbles ne convergent plus vers le même point d'intersection. Le non-concours des forces détruit immédiatement les conditions de la statique et crée un couple de rotation.
        
        **Étape 4 : Rupture mécanique et chute**
        Le second câble cède sous la contrainte géométrique. Les tensions s'annulent instantanément, laissant le panneau soumis à son seul poids vertical et à la poussée résiduelle du vent. Le triangle des forces reste grand ouvert, ce qui engendre un mouvement de translation accéléré vers le sol : le système s'effondre.
        """)

    with col_image:
        # Remplacer "caricature_trois_forces.jpg" par le nom exact de votre fichier image unique
        nom_image_3f = "caricature_trois_forces.jpg"
        
        if os.path.exists(nom_image_3f):
            st.image(nom_image_3f, caption="Séquence complète de l'équilibre à trois forces", use_container_width=True)
        else:
            st.warning(f"L'image {nom_image_3f} est manquante sur le serveur.")

    
    st.write("Pour 3 forces non paralleles en équilibre, leurs droites d'action sont obligatoirement concourantes (se coupent au meme point) et leur dynamique forme un triangle ferme.")
    analyser_systeme_forces(nb_forces=3, suffixe_clef="3f", nom_onglet="Equilibre_3_forces")

    st.write("---")        
    if "suite_verrouille_tab4" not in st.session_state:
        st.session_state.suite_verrouille_tab4 = False
    verrou_at4 = st.session_state.suite_verrouille_tab4

    # Insertion de la zone de questions/trous pour le tab 4
    afficher_atelier_trois_forces_complet(verrouille=verrou_at4)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 4")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat4 = st.checkbox(
        "Je certifie avoir complété les questions et réglé le système à trois forces.",
        key="check_certif_tab4_final_net",
        disabled=verrou_at4,
    )
    
    # --- BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 4", key="btn_export_suite4_official_net", use_container_width=True, disabled=verrou_at4):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat4: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q4 = 0.0
            if "ordre_quiz_tab4_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab4_aleatoire:
                    reponse_eleve = st.session_state.get(f"3f_at_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q4 += 1.0

            # Vérification des bonnes réponses du texte à trous du tab 4
            score_t4 = sum(
                [
                    st.session_state.get("3f_t1_final") == "concourant",
                    st.session_state.get("3f_t2_final") == "triangle",
                    st.session_state.get("3f_t3_final") == "nulle",
                    st.session_state.get("3f_t4_final") == "déséquilibre",
                    st.session_state.get("3f_t5_final") == "zéro",
                    st.session_state.get("3f_t6_final") == "deux",
                    st.session_state.get("3f_t7_final") == "équilibre",
                    st.session_state.get("3f_t8_final") == "graphique",
                    st.session_state.get("3f_t9_final") == "matériel",
                    st.session_state.get("3f_t10_final") == "départ",
                ]
            )

            st.session_state.score_suite4_p1 = round(float(score_q4), 1)
            st.session_state.score_suite4_p2 = round(float(score_t4), 1)
            st.session_state.score_final_suite4 = round(float(score_q4 + score_t4), 1)
            st.session_state.suite_verrouille_tab4 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 4 ---
    if st.session_state.get("suite_verrouille_tab4", False):
        scr1_4 = st.session_state.get("score_suite4_p1", 0.0)
        scr2_4 = st.session_state.get("score_suite4_p2", 0.0)
        tot_s4 = st.session_state.get("score_final_suite4", 0.0)
        timestamp_suite4 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER 4 SCELLÉ | Note globale de l'Atelier : {tot_s4:.1f} / 20")
        
        html_export_tab4 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Équilibre 3 Forces - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Mécanique - Statique</h1>
                <p>Atelier 4 : Équilibre d'un point soumis à trois forces</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite4}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s4:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz 3 Forces : <strong>{scr1_4:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_4:.1f} / 10</strong><br>
                Note Totale de l'Atelier 4 : <strong>{tot_s4:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab4_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab4_aleatoire, 1):
                saisie = st.session_state.get(f"3f_at_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tab4 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab4 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html4 = preparer_nom_fichier("Rapport_Atelier_4").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 4 (.html)",
            data=html_export_tab4,
            file_name=nom_fichier_html4,
            mime="text/html",
            use_container_width=True
        )





with tab5:
    st.header("Cas à Plus de 3 Forces")

    st.subheader("Caricature de l'équilibre à forces multiples (Séquence en 4 étapes)")

    # Séparation en deux colonnes : 60% pour le texte en bleu, 40% pour l'image unique
    col_texte, col_image = st.columns([0.6, 0.4])

    with col_texte:
        # Utilisation de st.info pour afficher l'ensemble du texte dans un encadré bleu avec les accents
        st.info("""
        ### Analyse de la statique à forces multiples concourantes
        
        **Étape 1 : Équilibre complexe initial**
        Une structure métallique lourde est maintenue en suspension au-dessus d'un chantier à l'aide de quatre filins d'acier distincts reliés à des ancrages différents. Malgré la multiplicité des actions, l'objet demeure parfaitement immobile. Graphiquement, la mise bout à bout des cinq vecteurs (le poids et les quatre tensions) engendre un polygone fermé à cinq côtés, validant la nullité de la résultante.
        
        **Étape 2 : Modification contrôlée des tensions**
        Les opérateurs activent deux treuils mécaniques pour réajuster la position de la charge. Les intensités et les angles de deux filins se modifient simultanément. La géométrie interne du dynamique se déforme en direct, mais le tracé vectoriel réussit à se refermer sur sa position d'origine : l'équilibre statique est préservé.
        
        **Étape 3 : Surcharge et ouverture du polygone**
        Un coup de vent violent et imprévu applique une force horizontale supplémentaire sur la structure, tandis que l'un des filins d'acier commence à se détendre anormalement. La somme analytique des composantes horizontales et verticales n'est plus égale à zéro. Graphiquement, le dynamique des forces ne parvient plus à se refermer, créant un vecteur résultant de déséquilibre.
        
        **Étape 4 : Défaillance en chaîne et mouvement**
        Le filin détendu cède sous le report brutal de la charge. Le déséquilibre devient majeur, et la force résultante non nulle provoque une accélération soudaine de la structure métallique. Le polygone reste largement ouvert, et la trajectoire du système se transforme en un mouvement de translation accéléré incontrôlable.
        """)

    with col_image:
        # Remplacer "caricature_plus_trois_forces.jpg" par le nom exact de votre fichier image unique
        nom_image_plus_f = "caricature_plus_trois_forces.jpg"
        
        if os.path.exists(nom_image_plus_f):
            st.image(nom_image_plus_f, caption="Séquence complète de l'équilibre à plus de trois forces", use_container_width=True)
        else:
            st.warning(f"L'image {nom_image_plus_f} est manquante sur le serveur.")
    
    nb_perso = st.slider("Selectionnez le nombre exact de forces a analyser :", min_value=4, max_value=8, value=4)
    analyser_systeme_forces(nb_forces=nb_perso, suffixe_clef="plus_f", nom_onglet="Equilibre_plus_3_forces")

    st.write("---")        
    if "suite_verrouille_tab5" not in st.session_state:
        st.session_state.suite_verrouille_tab5 = False
    verrou_at5 = st.session_state.suite_verrouille_tab5

    # Insertion de la zone de questions/trous pour le tab 5
    afficher_atelier_plus_trois_forces_complet(verrouille=verrou_at5)
    
    st.write("---")
    st.subheader("Synthèse et validation de l'Atelier 5")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat5 = st.checkbox(
        "Je certifie avoir complété les questions et réglé le système à forces multiples.",
        key="check_certif_tab5_final_net",
        disabled=verrou_at5,
    )
    
    # --- BLOC DE CORRECTION ET BOUTON VALIDER ---
    if st.button("VALIDER ET EXPORTER LE BILAN DE L'ATELIER 5", key="btn_export_suite5_official_net", use_container_width=True, disabled=verrou_at5):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat5: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q5 = 0.0
            if "ordre_quiz_tab5_aleatoire" in st.session_state:
                for q_item in st.session_state.ordre_quiz_tab5_aleatoire:
                    reponse_eleve = st.session_state.get(f"pf_at_final_g_{q_item['id']}", "Choisir...")
                    if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                        score_q5 += 1.0

            # Vérification des bonnes réponses du texte à trous du tab 5
            score_t5 = sum(
                [
                    st.session_state.get("pf_t1_final") == "point",
                    st.session_state.get("pf_t2_final") == "polygone",
                    st.session_state.get("pf_t3_final") == "nulle",
                    st.session_state.get("pf_t4_final") == "déséquilibre",
                    st.session_state.get("pf_t5_final") == "axe",
                    st.session_state.get("pf_t6_final") == "dynamique",
                    st.session_state.get("pf_t7_final") == "équilibre",
                    st.session_state.get("pf_t8_final") == "résultante",
                    st.session_state.get("pf_t9_final") == "verticales",
                    st.session_state.get("pf_t10_final") == "équilibrante",
                ]
            )

            st.session_state.score_suite5_p1 = round(float(score_q5), 1)
            st.session_state.score_suite5_p2 = round(float(score_t5), 1)
            st.session_state.score_final_suite5 = round(float(score_q5 + score_t5), 1)
            st.session_state.suite_verrouille_tab5 = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML TAB 5 ---
    if st.session_state.get("suite_verrouille_tab5", False):
        scr1_5 = st.session_state.get("score_suite5_p1", 0.0)
        scr2_5 = st.session_state.get("score_suite5_p2", 0.0)
        tot_s5 = st.session_state.get("score_final_suite5", 0.0)
        timestamp_suite5 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER 5 SCELLÉ | Note globale de l'Atelier : {tot_s5:.1f} / 20")
        
        html_export_tab5 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Forces Multiples - {n_eleve}</title>
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
                <h1>Rapport d'Évaluation de Mécanique - Statique</h1>
                <p>Atelier 5 : Équilibre d'un point soumis à plus de trois forces</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Scellé le : {timestamp_suite5}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s5:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Forces Multiples : <strong>{scr1_5:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_5:.1f} / 10</strong><br>
                Note Totale de l'Atelier 5 : <strong>{tot_s5:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        if "ordre_quiz_tab5_aleatoire" in st.session_state:
            for num, q_item in enumerate(st.session_state.ordre_quiz_tab5_aleatoire, 1):
                saisie = st.session_state.get(f"pf_at_final_g_{q_item['id']}", "Choisir...")
                attendu = q_item["rep"]
                v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
                v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
                html_export_tab5 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab5 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html5 = preparer_nom_fichier("Rapport_Atelier_5").replace(".txt", ".html")
        st.download_button(
            label="Télécharger le rapport d'évaluation officiel de l'Atelier 5 (.html)",
            data=html_export_tab5,
            file_name=nom_fichier_html5,
            mime="text/html",
            use_container_width=True
        )


with tab6:
    st.header("Applications Spécifiques aux Métiers")
    
    # Encadré méthodologique destiné à guider l'élève pas à pas
    st.markdown("""
    ### Protocole de Travail Pratique :
    
    1. **Sélection de votre spécialité :** Choisissez votre filière métier dans le menu déroulant ci-dessous. Un scénario de chantier et un questionnaire uniques vont être générés de manière aléatoire.
    2. **Analyse du cas technique :** Lisez attentivement la mise en situation réelle affichée dans l'encadré bleu (problème mécanique appliqué).
    3. **Résolution sur le Laboratoire Virtuel :** À l'aide des champs numériques, modifiez l'intensité et l'angle des forces pour simuler le problème. Ajustez-les jusqu'à ce que le message affiche **l'équilibre statique validé** (le dynamique des forces à droite doit former un polygone parfaitement fermé).
    4. **Évaluation théorique :** Répondez aux questions du Quiz technique (colonne de gauche) et complétez les mots manquants de la Synthèse applicative (colonne de droite).
    5. **Soumission et Export :** Cochez la case de certification, puis cliquez sur le bouton de validation. Récupérez ensuite votre fichier de rapport officiel au format `.html` généré automatiquement pour le transmettre à votre enseignant.
    """)
    st.write("---")
    st.write("Sélectionnez votre domaine professionnel. Un scénario de chantier, un quiz et une synthèse textuelle uniques vont être générés aléatoirement.")
    
    # Menu déroulant propre aux choix des métiers
    metier_choisi = st.selectbox(
        "Choisissez votre filière métier :",
        options=["routier", "travaux_publics", "maintenance", "geometre"],
        format_func=lambda x: {
            "routier": "Transport Routier et Logistique",
            "travaux_publics": "Travaux Publics et Génie Civil",
            "maintenance": "Maintenance Industrielle",
            "geometre": "Géomètre et Topographie"
        }[x],
        key="select_metier_onglet6"
    )
    
    # --- Gestion de l'aléa anti-triche par session de métier ---
    if f"indice_alea_{metier_choisi}" not in st.session_state:
        import random
        # Sélection aléatoire du scénario (index 0 ou index 1)
        st.session_state[f"indice_alea_{metier_choisi}"] = random.choice([0, 1])
        
        # Mélange et stockage des questions spécifiques à ce métier uniquement
        banque_ref = obtenir_banque_metiers()[metier_choisi]
        liste_q = list(banque_ref["quiz"])
        random.shuffle(liste_q)
        st.session_state.quiz_metier_aleatoire = liste_q
        st.session_state.trous_metier_statiques = banque_ref["trous"]
        
    cas_index_alea = st.session_state[f"indice_alea_{metier_choisi}"]
    
    if f"suite_verrouille_tab6_{metier_choisi}" not in st.session_state:
        st.session_state[f"suite_verrouille_tab6_{metier_choisi}"] = False
        
    verrou_at6 = st.session_state[f"suite_verrouille_tab6_{metier_choisi}"]
    
    # Affichage dynamique de l'exercice basé sur le tirage aléatoire du métier choisi
    afficher_atelier_metier_complet(metier_choisi, cas_index_alea, verrouille=verrou_at6)
    
    st.write("---")
    st.subheader("Validation et Exportation du module métier")
    p_eleve = st.session_state.get("prenom_var", "INCONNU").upper()
    n_eleve = st.session_state.get("nom_var", "INCONNU").upper()
    c_eleve = st.session_state.get("classe_var", "INCONNU").upper()

    case_certif_stat6 = st.checkbox(
        "Je certifie avoir complété les évaluations techniques liées à ma filière métier.",
        key=f"check_certif_tab6_{metier_choisi}",
        disabled=verrou_at6,
    )
    
    # --- BLOC DE CORRECTION ET BOUTON VALIDER TAB 6 ---
    if st.button("VALIDER ET EXPORTER LE BILAN METIER", key=f"btn_export_tab6_{metier_choisi}", use_container_width=True, disabled=verrou_at6):
        if st.session_state.get("nom_var", "Nom") in ["Nom", ""] or st.session_state.get("prenom_var", "Prenom") in ["Prenom", ""]:
            st.error("Action refusée : Saisissez votre identité dans l'onglet 'Identification'.")
        elif not case_certif_stat6: 
            st.error("Action refusée : Cochez la case de certification.")
        else:
            score_q6 = 0.0
            banque_verif = obtenir_banque_metiers()[metier_choisi]
            
            # Évaluation du quiz mélangé
            for q_item in st.session_state.quiz_metier_aleatoire:
                reponse_eleve = st.session_state.get(f"met_at_g_{q_item['id']}", "Choisir...")
                if str(reponse_eleve).strip() == str(q_item["rep"]).strip():
                    score_q6 += 1.0
                    
            # Évaluation du texte à trous spécifique (Note ramenée sur 10 pts)
            score_t6 = 0.0
            if st.session_state.get("m_t1") == banque_verif["trous"][0][2]:
                score_t6 += 5.0
            if st.session_state.get("m_t2") == banque_verif["trous"][1][2]:
                score_t6 += 5.0
                
            # Ramener le quiz sur 10 points également pour obtenir une note sur 20
            score_q6_normalise = round((score_q6 / len(banque_verif["quiz"])) * 10.0, 1)
            
            st.session_state[f"score_q_{metier_choisi}"] = score_q6_normalise
            st.session_state[f"score_t_{metier_choisi}"] = score_t6
            st.session_state[f"score_total_{metier_choisi}"] = round(score_q6_normalise + score_t6, 1)
            st.session_state[f"suite_verrouille_tab6_{metier_choisi}"] = True
            st.rerun()

    # --- COMPILATION DU DOCUMENT EXPORTABLE HTML METIER ---
    if st.session_state.get(f"suite_verrouille_tab6_{metier_choisi}", False):
        scr1_6 = st.session_state.get(f"score_q_{metier_choisi}", 0.0)
        scr2_6 = st.session_state.get(f"score_t_{metier_choisi}", 0.0)
        tot_s6 = st.session_state.get(f"score_total_{metier_choisi}", 0.0)
        timestamp_suite6 = datetime.now().strftime("%Y-%m-%d a %H:%M:%S")
        
        st.success(f"ATELIER TP METIER SCELLE | Note finale : {tot_s6:.1f} / 20")
        
        banque_html = obtenir_banque_metiers()[metier_choisi]
        scen_html = banque_html["scenarios"][cas_index_alea]

        html_export_tab6 = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Rapport Statique Metier - {n_eleve}</title>
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
                <h1>Rapport d'Application Professionnelle - Statique</h1>
                <p>Branche Spécialisée : {banque_html['nom']}</p>
                <p>Scénario Évalué : {scen_html['titre']}</p>
                <p>Élève : {p_eleve} {n_eleve} &nbsp;&nbsp;|&nbsp;&nbsp; Classe : {c_eleve}</p>
                <p style="font-size: 12px; opacity: 0.7;">Généré automatiquement le : {timestamp_suite6}</p>
                <div class="score-badge">SCORE<br><span style="font-size: 32px;">{tot_s6:.1f}</span> / 20</div>
            </div>
            
            <div class="sub-title">Récapitulatif des Notes Obtenues</div>
            <p style="font-size: 14px; background: white; padding: 15px; border-left: 4px solid #1e3a8a;">
                Note obtenue au Quiz Technique : <strong>{scr1_6:.1f} / 10</strong><br>
                Note obtenue à la Synthèse : <strong>{scr2_6:.1f} / 10</strong><br>
                Note Totale de l'Atelier 6 : <strong>{tot_s6:.1f} / 20</strong>
            </p>

            <div class="sub-title">CORRECTION DÉTAILLÉE DU QUIZ (ORDRE DE SESSION)</div>
            <table>
                <thead>
                    <tr><th>N°</th><th>Question Posée</th><th>Saisie Élève</th><th>Attendu Académique</th><th>Verdict</th></tr>
                </thead>
                <tbody>
        """

        for num, q_item in enumerate(st.session_state.quiz_metier_aleatoire, 1):
            saisie = st.session_state.get(f"met_at_g_{q_item['id']}", "Choisir...")
            attendu = q_item["rep"]
            v_lbl = "CORRECT" if str(saisie).strip() == str(attendu).strip() else "INCORRECT"
            v_class = "status-correct" if v_lbl == "CORRECT" else "status-incorrect"
            html_export_tab6 += f"<tr><td>{num}</td><td>{q_item['q']}</td><td>{saisie}</td><td>{attendu}</td><td class='{v_class}'>{v_lbl}</td></tr>"

        html_export_tab6 += """
                </tbody>
            </table>
        </body>
        </html>
        """
        nom_fichier_html6 = preparer_nom_fichier(f"Rapport_Atelier_6_{metier_choisi}").replace(".txt", ".html")
        st.download_button(abel="Télécharger le rapport d'évaluation officiel de l'Atelier 6 (.html)",
            data=html_export_tab6,
            file_name=nom_fichier_html6,
            mime="text/html",
            use_container_width=True
            )






















