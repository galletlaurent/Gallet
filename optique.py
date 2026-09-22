# -*- coding: utf-8 -*-
from datetime import datetime
from itertools import combinations, product
import math
import random
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

# 1. CATALOGUE TECHNIQUE DES SELS MÉTALLIQUES (Test de flamme 400-900 nm)
if "catalogue_metaux" not in st.session_state:
    st.session_state.catalogue_metaux = {
        "Lithium (Li)": {
            "couleur": "#dc2626",
            "descr": "Rouge carmin eclatant (Raies visibles et IR thermique)",
            "raies": [
                (460.3, "#1d4ed8", 0.15),
                (610.3, "#ff6b00", 0.30),
                (670.8, "#ff0000", 0.95),
                (812.6, "#450a0a", 0.10),
            ],
        },
        "Sodium (Na)": {
            "couleur": "#f59e0b",
            "descr": "Jaune orange intense (Doublet D visible et raies proches IR)",
            "raies": [
                (589.0, "#ffcc00", 0.95),
                (589.6, "#ff9900", 0.90),
                (818.3, "#450a0a", 0.12),
                (819.4, "#450a0a", 0.15),
            ],
        },
        "Potassium (K)": {
            "couleur": "#c084fc",
            "descr": "Violet pale / Doublet Infrarouge critique et dominant a 766-769 nm",
            "raies": [
                (404.4, "#4c0519", 0.50),
                (766.5, "#450a0a", 0.95),
                (769.9, "#450a0a", 0.85),
            ],
        },
        "Cuivre (Cu)": {
            "couleur": "#06b6d4",
            "descr": "Vert-Cyan caracteristique (Raies oxydes et atomiques IR)",
            "raies": [
                (510.5, "#00ffcc", 0.40),
                (515.3, "#00ff66", 0.50),
                (521.8, "#15803d", 0.60),
                (793.3, "#450a0a", 0.15),
                (809.2, "#450a0a", 0.20),
            ],
        },
        "Bore (B)": {
            "couleur": "#22c55e",
            "descr": "Vert vif eclatant (Serie visible et proche IR)",
            "raies": [
                (546.0, "#16a34a", 0.30),
                (548.0, "#15803d", 0.40),
                (745.4, "#450a0a", 0.12),
            ],
        },
    }

if "produits_indices" not in st.session_state:
    st.session_state.produits_indices = {
        "Air (n = 1.00)": 1.00,
        "Eau (n = 1.33)": 1.33,
        "Plexiglas / PMMA (n = 1.49)": 1.49,
        "Kérosène / Fioul (n = 1.44)": 1.44,
        "Cyclohexane (n = 1.43)": 1.43,
        "Huile Moteur 10W40 (n = 1.47)": 1.47,
        "Huile Hydraulique HV46 (n = 1.46)": 1.46,
        "Liquide de Frein DOT4 (n = 1.44)": 1.44,
        "Liquide de Refroidissement / Glycol (n = 1.38)": 1.38,
        "Huile de Coupe / Soluble Usinage (n = 1.41)": 1.41,
        "Gazole / Diesel (n = 1.45)": 1.45,
    }

# 2. CATALOGUE TECHNIQUE DES SOURCES LUMINEUSES ET SIGNATURES SPECTRALES
if "lampes_data" not in st.session_state:
    st.session_state.lampes_data = {
        "Lumière du Soleil": {
            "type": "continu",
            "couleur_source": "#FFFDE7",
            "descr": "SPECTRE CONTINU (Étoile de type G2V avec raies de Fraunhofer)",
            "raies": [
                (400.0, "#7C3AED", 0.30),
                (445.0, "#2563EB", 0.50),
                (490.0, "#06B6D4", 0.70),
                (550.0, "#22C55E", 0.95),
                (590.0, "#EAB308", 0.90),
                (640.0, "#F97316", 0.75),
                (700.0, "#EF4444", 0.50),
                (760.0, "#450a0a", 0.30),
                (850.0, "#450a0a", 0.15),
            ],
        },
        "Lampe Halogène": {
            "type": "continu_chaude",
            "couleur_source": "#FFE082",
            "descr": "SPECTRE CONTINU (Filament de tungstène sous enveloppe quartz)",
            "raies": [
                (420.0, "#4F46E5", 0.15),
                (460.0, "#3B82F6", 0.30),
                (510.0, "#10B981", 0.45),
                (560.0, "#84CC16", 0.65),
                (600.0, "#F97316", 0.85),
                (650.0, "#EF4444", 0.95),
                (750.0, "#450a0a", 0.95),
                (850.0, "#450a0a", 0.99),
            ],
        },
        "Lampe à Incandescence Standard": {
            "type": "continu_chaude",
            "couleur_source": "#FFD54F",
            "descr": "SPECTRE CONTINU THERMIQUE FILAMENT STANDARD",
            "raies": [
                (430.0, "#4338CA", 0.10),
                (470.0, "#1D4ED8", 0.22),
                (520.0, "#047857", 0.40),
                (570.0, "#A3E635", 0.60),
                (610.0, "#EA580C", 0.80),
                (660.0, "#DC2626", 0.90),
                (740.0, "#450a0a", 0.95),
                (840.0, "#450a0a", 0.96),
            ],
        },
        "Corps Noir Élevé (5000K)": {
            "type": "continu",
            "couleur_source": "#F8FAFC",
            "descr": "SPECTRE CONTINU THÉORIQUE ÉQUILIBRE PLANCKIEN",
            "raies": [
                (410.0, "#6366F1", 0.60),
                (450.0, "#2563EB", 0.85),
                (500.0, "#06B6D4", 0.95),
                (550.0, "#22C55E", 0.90),
                (600.0, "#EAB308", 0.75),
                (650.0, "#EF4444", 0.60),
                (720.0, "#450a0a", 0.40),
                (820.0, "#450a0a", 0.20),
            ],
        },
        "Tube Fluorescent (Bureau)": {
            "type": "mixte",
            "couleur_source": "#F5F5F5",
            "descr": "SPECTRE MIXTE (Fonds thermique et raies de décharge)",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.29),
                (546.0, "#2E7D32", 0.49),
                (611.0, "#E65100", 0.70),
            ],
        },
        "Ampoule Fluocompacte": {
            "type": "raies",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE DE RAIES / BANDES FLUORESCENTES",
            "raies": [
                (436.0, "#311B92", 0.12),
                (487.0, "#00838F", 0.31),
                (544.0, "#2E7D32", 0.48),
                (587.0, "#FF8F00", 0.62),
                (611.0, "#C62828", 0.70),
            ],
        },
        "LED Blanche (Froide)": {
            "type": "led_froide",
            "couleur_source": "#E0F2F1",
            "descr": "SPECTRE MIXTE (Pic Bleu intense + cloche d'émission Jaune)",
            "raies": [
                (450.0, "#0000FF", 0.98),
                (520.0, "#00FF00", 0.35),
                (560.0, "#FFFF00", 0.55),
                (600.0, "#FF8000", 0.48),
                (645.0, "#FF0000", 0.30),
            ],
        },
        "Lampe au Deutérium (D2)": {
            "type": "raies",
            "couleur_source": "#EDE7F6",
            "descr": "SPECTRE DE LABO ATOMIQUE LOURD",
            "raies": [(486.0, "#00ffcc", 0.25), (656.1, "#ff0000", 0.80)],
        },
        "Lampe au Mercure (Hg)": {
            "type": "raies",
            "couleur_source": "#E0F7FA",
            "descr": "SPECTRE DE RAIES INTENSE UV-VISIBLE",
            "raies": [
                (404.7, "#4c0519", 0.02),
                (435.8, "#2563eb", 0.12),
                (546.1, "#22c55e", 0.49),
                (578.0, "#eab308", 0.59),
            ],
        },
        "Lampe au Sodium (Na)": {
            "type": "raies",
            "couleur_source": "#FFF3E0",
            "descr": "SPECTRE DE RAIES (DOUBLET D DE FRAUNHOFER)",
            "raies": [(589.0, "#ffcc00", 0.95), (589.6, "#ff9900", 0.90)],
        },
        "Lampe à l'Hélium (He)": {
            "type": "raies",
            "couleur_source": "#FFE0B2",
            "descr": "SPECTRE DE RAIES ATOMIQUE SIMPLE",
            "raies": [
                (447.1, "#1d4ed8", 0.16),
                (501.6, "#06b6d4", 0.34),
                (587.6, "#f59e0b", 0.63),
                (667.8, "#dc2626", 0.89),
            ],
        },
        "Lampe au Néon (Ne)": {
            "type": "raies",
            "couleur_source": "#FFCCBC",
            "descr": "SPECTRE DE RAIES TRÈS RICHE DANS LE ROUGE",
            "raies": [
                (585.2, "#f59e0b", 0.62),
                (614.3, "#ea580c", 0.71),
                (640.2, "#dc2626", 0.80),
                (692.9, "#991b1b", 0.97),
            ],
        },
        "Lampe à l'Argon (Ar)": {
            "type": "raies",
            "couleur_source": "#E8EAF6",
            "descr": "SPECTRE DE GAZ DE DÉCHARGE BLEUTÉ",
            "raies": [
                (420.0, "#581c87", 0.45),
                (430.0, "#4338ca", 0.30),
                (450.0, "#2563eb", 0.25),
                (488.0, "#06b6d4", 0.40),
                (696.5, "#991b1b", 0.50),
            ],
        },
        "Lampe au Krypton (Kr)": {
            "type": "raies",
            "couleur_source": "#F1F5F9",
            "descr": "SPECTRE ATOMIQUE KRYPTON COHÉRENT",
            "raies": [
                (431.9, "#4338ca", 0.15),
                (557.0, "#22c55e", 0.60),
                (587.1, "#f59e0b", 0.45),
                (642.1, "#dc2626", 0.35),
            ],
        },
        "Lampe au Xénon (Xe)": {
            "type": "raies",
            "couleur_source": "#E2E8F0",
            "descr": "SPECTRE DE DÉCHARGE FLASH CONTINU/RAIES",
            "raies": [
                (462.7, "#2563eb", 0.40),
                (467.1, "#3b82f6", 0.50),
                (473.4, "#06b6d4", 0.35),
                (529.2, "#22c55e", 0.20),
                (680.6, "#dc2626", 0.45),
            ],
        },
        "Lampe au Cadmium (Cd)": {
            "type": "raies",
            "couleur_source": "#D1C4E9",
            "descr": "SPECTRE DE RAIES MÉTALLIQUES STABLES",
            "raies": [
                (467.8, "#2563eb", 0.22),
                (479.9, "#06b6d4", 0.29),
                (508.6, "#22c55e", 0.36),
            ],
        },
        "Lampe au Zinc (Zn)": {
            "type": "raies",
            "couleur_source": "#ECEFF1",
            "descr": "SPECTRE DE RAIES VAPEUR MÉTAL HAUTE PRESSION",
            "raies": [
                (468.0, "#2563eb", 0.15),
                (472.2, "#1d4ed8", 0.20),
                (481.1, "#06b6d4", 0.35),
                (636.2, "#dc2626", 0.50),
            ],
        },
        "Lampe au Lithium (Li)": {
            "type": "raies",
            "couleur_source": "#FEE2E2",
            "descr": "SPECTRE D'ALCALIN LABO VIF (3 RAIES PHYSIQUES)",
            "raies": [
                (460.3, "#1d4ed8", 0.10),
                (610.3, "#ff6b00", 0.30),
                (670.8, "#ff0000", 0.90),
            ],
        },
        "Lampe au Potassium (K)": {
            "type": "raies",
            "couleur_source": "#F3E8FF",
            "descr": "SPECTRE ALCALIN DE LABO STABLE (SANS ERREUR 693 NM)",
            "raies": [
                (404.4, "#4c0519", 0.40),
                (766.5, "#450a0a", 0.95),
                (769.9, "#450a0a", 0.85),
            ],
        },
        "Lampe au Thallium (Tl)": {
            "type": "raies",
            "couleur_source": "#DCFCE7",
            "descr": "SPECTRE A RAIE VERTE UNIQUE PRÉPONDÉRANTE",
            "raies": [(535.0, "#22c55e", 0.95)],
        },
        "Vapeur d'Iode (I2 - Moléculaire)": {
            "type": "raies",
            "couleur_source": "#FAE8FF",
            "descr": "SPECTRE DE BANDES MOLÉCULAIRES DISCRETES",
            "raies": [
                (520.0, "#16a34a", 0.30),
                (535.0, "#15803d", 0.45),
                (550.0, "#84cc16", 0.50),
                (565.0, "#eab308", 0.40),
            ],
        },
    }

if "milieu_refraction_1" not in st.session_state:
    st.session_state.milieu_refraction_1 = "Air (n = 1.00)"
if "milieu_refraction_2" not in st.session_state:
    st.session_state.milieu_refraction_2 = "Eau (n = 1.33)"
if "var_angle_refraction_i1" not in st.session_state:
    st.session_state.var_angle_refraction_i1 = 30.0
if "var_texte_resultats_refraction" not in st.session_state:
    st.session_state.var_texte_resultats_refraction = ""

# Variables pour le controle d'examen de l'Atelier 4
if "mode_examen_tab4" not in st.session_state:
    st.session_state.mode_examen_tab4 = False
if "quiz4_valide" not in st.session_state:
    st.session_state.quiz4_valide = False
if "quiz4_score_txt" not in st.session_state:
    st.session_state.quiz4_score_txt = ""
# 3. INITIALISATION DES INTERRUPTEURS ET ETATS DE MANIPULATION
if "var_sel_metal" not in st.session_state:
    st.session_state.var_sel_metal = "Sodium (Na)"
if "source_lumineuse_choisie" not in st.session_state:
    st.session_state.source_lumineuse_choisie = "Lumière du Soleil"
if "var_combustion_active" not in st.session_state:
    st.session_state.var_combustion_active = False
if "var_versement_poudre" not in st.session_state:
    st.session_state.var_versement_poudre = False

# Variables de controle d'examen pour le volet 2
if "mode_examen_tab2" not in st.session_state:
    st.session_state.mode_examen_tab2 = False
if "quiz2_valide" not in st.session_state:
    st.session_state.quiz2_valide = False
if "quiz2_score_txt" not in st.session_state:
    st.session_state.quiz2_score_txt = ""

def gerer_changement_metal():
    """Moteur exclusif Atelier 2 : Interroge le catalogue de flammes."""
    nom_selectionne = st.session_state.var_sel_metal
    catalogue = st.session_state.catalogue_metaux
    if nom_selectionne in catalogue:
        return catalogue[nom_selectionne]
    return {"couleur": "#0d1117", "descr": "Aucune propriete enregistree."}


def declencher_test_flamme_web():
    """Moteur séquentiel de l'Atelier 2 : simule le versement de la poudre."""
    if st.session_state.var_combustion_active:
        st.session_state.var_combustion_active = False
        st.session_state.var_versement_poudre = False
        return

    st.session_state.var_versement_poudre = True
    st.session_state.var_combustion_active = False

    # Message d'attente textuel pur pendant le versement
    with st.spinner(
        "Action : Versement de l'echantillon de sel dans la coupelle en cours..."
    ):
        time.sleep(2.0)

    st.session_state.var_versement_poudre = False
    st.session_state.var_combustion_active = True


def dessiner_spectre_flamme_combustion():
    """Génère la figure du spectre d'émission atomique réel du métal (400 à 900 nm)."""
    metal_choisi = st.session_state.var_sel_metal
    info = st.session_state.catalogue_metaux[metal_choisi]

    fig, ax = plt.subplots(figsize=(10, 1.8), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(400, 900)
    ax.set_ylim(-0.2, 1.2)
    ax.axis("off")

    # Fond noir de la chambre d'analyse
    ax.add_patch(
        plt.Rectangle((400, 0), 500, 1.0, fill=True, facecolor="black", lw=0)
    )

    if st.session_state.var_combustion_active:
        for wl, couleur, intensite in info.get("raies", []):
            if 400 <= wl <= 900:
                ax.axvline(x=wl, color=couleur, lw=4, alpha=intensite)
                ax.text(
                    wl,
                    -0.25,
                    f"{wl}nm",
                    color="#94a3b8",
                    fontsize=7,
                    fontname="Courier",
                    ha="center",
                )
    else:
        ax.text(
            650,
            0.5,
            "[ Allumez le bruleur pour observer le spectre d'emission ]",
            color="#475569",
            fontsize=9,
            style="italic",
            ha="center",
            va="center",
        )

    # Règle graduée de référence (400 à 900 nm)
    for g in range(400, 901, 50):
        ax.plot([g, g], [1.0, 1.06], color="white", lw=1)
        ax.text(g, 1.15, str(g), color="#64748b", fontsize=7, ha="center")

    rect_cadre = plt.Rectangle(
        (400, 0), 500, 1.0, fill=False, edgecolor="#334155", lw=1.5
    )
    ax.add_patch(rect_cadre)

    return fig

def dessiner_montage_complet_atelier2():
    """Moteur graphique unifie de l'Atelier 2 : Dessine le banc d'optique complet

    et projette les faisceaux colores reels vers l'ecran.
    """
    nom_selectionne = st.session_state.source_lumineuse_choisie
    info = st.session_state.lampes_data[nom_selectionne]

    # Coordonnees fixes du banc d'optique calquees sur Tkinter
    x_lampe, y_lampe = 60, 120
    x_fente, x_lentille, x_prisme, y_axe = 190, 330, 520, 120
    x_ecran, y_ecran_haut, y_ecran_bas = 960, 30, 290
    h_spectre = y_ecran_bas - y_ecran_haut - 30

    fig, ax = plt.subplots(figsize=(11.6, 4.5), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, 1050)
    ax.set_ylim(0, 320)
    ax.invert_yaxis()  # Maintient le repere Y identique a Tkinter
    ax.axis("off")

    # 1. Trace des faisceaux lumineux geometriques avant le prisme
    ax.fill(
        [x_lampe + 25, x_fente, x_fente],
        [y_axe, y_axe - 12, y_axe + 12],
        color=info["couleur_source"],
        alpha=0.25,
    )
    ax.fill(
        [x_fente, x_fente, x_lentille, x_lentille],
        [y_axe - 12, y_axe + 12, y_axe + 45, y_axe - 45],
        color=info["couleur_source"],
        alpha=0.25,
    )
    ax.fill(
        [x_lentille, x_lentille, x_prisme - 20, x_prisme - 25],
        [y_axe - 45, y_axe + 45, y_axe + 35, y_axe - 20],
        color=info["couleur_source"],
        alpha=0.25,
    )

    # 2. Projection des rayons colores disperses apres le prisme
    x_sortie_prisme, y_sortie_prisme = x_prisme + 20, y_axe + 15

    if info["type"] in [
        "continu",
        "continu_chaude",
        "led_froide",
        "led_chaude",
        "mixte",
    ]:
        for i in range(int(h_spectre)):
            ratio = i / h_spectre
            c_hex = get_rgb_continu(
                ratio, info["type"]
            )  # Utilise le moteur chromatique de l'Atelier 1
            y_pixel_ecran = y_ecran_haut + 15 + i
            ax.plot(
                [x_sortie_prisme, x_ecran],
                [y_sortie_prisme, y_pixel_ecran],
                color=c_hex,
                lw=1.5,
                alpha=0.7,
            )

    if "raies" in info:
        for wl, couleur, pos_relative in info["raies"]:
            y_pixel_ecran = y_ecran_bas - 15 - int(pos_relative * h_spectre)
            ax.plot(
                [x_sortie_prisme, x_ecran],
                [y_sortie_prisme, y_pixel_ecran],
                color=couleur,
                lw=2.5,
                alpha=0.9,
            )

    # 3. Dessin des composants materiels du banc
    # Source
    ax.add_patch(
        plt.Circle(
            (x_lampe, y_lampe),
            25,
            facecolor=info["couleur_source"],
            edgecolor="white",
            lw=2,
        )
    )
    ax.add_patch(
        plt.Rectangle(
            (x_lampe - 10, y_lampe + 25), 20, 25, facecolor="#455A64"
        )
    )
    ax.text(
        x_lampe,
        y_lampe - 35,
        "Source",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Fente
    ax.plot([x_fente, x_fente], [y_axe - 50, y_axe - 12], color="#90A4AE", lw=5)
    ax.plot([x_fente, x_fente], [y_axe + 12, y_axe + 50], color="#90A4AE", lw=5)
    ax.text(
        x_fente,
        y_axe - 60,
        "Fente",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Lentille L
    ax.plot(
        [x_lentille, x_lentille], [y_axe - 65, y_axe + 65], color="#4FC3F7", lw=2.5
    )
    ax.text(
        x_lentille,
        y_axe - 75,
        "Lentille L",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Prisme
    ax.add_patch(
        plt.Polygon(
            [[x_prisme, y_axe - 50], [x_prisme - 40, y_axe + 40], [x_prisme + 50, y_axe + 40]],
            facecolor="#E0F7FA",
            edgecolor="#80DEEA",
            lw=2,
        )
    )
    ax.text(
        x_prisme + 5,
        y_axe - 62,
        "Prisme",
        color="white",
        fontsize=9,
        fontweight="bold",
        ha="center",
    )

    # Ecran
    ax.add_patch(
        plt.Rectangle(
            (x_ecran, y_ecran_haut),
            20,
            y_ecran_bas - y_ecran_haut,
            facecolor="#FFFFFF",
            edgecolor="#B0BEC5",
            lw=2,
        )
    )
    ax.text(
        x_ecran + 40,
        (y_ecran_haut + y_ecran_bas) / 2,
        "Ecran",
        color="white",
        fontsize=10,
        fontweight="bold",
        va="center",
        rotation=-90,
    )

    return fig


def dessiner_zoom_spectre_atelier2():
    """Génère la règle nanométrique horizontale zoomée du spectre de l'Atelier 2."""
    nom_selectionne = st.session_state.source_lumineuse_choisie
    info = st.session_state.lampes_data[nom_selectionne]
    largeur_s = 700

    fig, ax = plt.subplots(figsize=(10, 2.0), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, largeur_s)
    ax.set_ylim(-0.4, 1.4)
    ax.axis("off")

    if info["type"] in [
        "continu",
        "continu_chaude",
        "led_froide",
        "led_chaude",
        "mixte",
    ]:
        for i in range(largeur_s):
            ratio = i / largeur_s
            c_hex = get_rgb_continu(1.0 - ratio, info["type"])
            ax.plot([i, i], [0.02, 0.98], color=c_hex, lw=1.5, alpha=1.0)

    ax.add_patch(
        plt.Rectangle(
            (0, 0), largeur_s, 1.0, fill=False, edgecolor="white", lw=1.5
        )
    )

    if "raies" in info:
        for wl, couleur, pos_relative in info["raies"]:
            x_raie = int(pos_relative * largeur_s)
            ax.plot([x_raie, x_raie], [0.02, 0.98], color=couleur, lw=3.5)
            ax.text(
                x_raie,
                -0.25,
                f"{wl} nm",
                color="#ECEFF1",
                fontsize=8,
                fontname="Courier",
                fontweight="bold",
                ha="center",
            )

    for wl_test in range(400, 701, 50):
        x_grad = int(((wl_test - 400) / 300) * largeur_s)
        ax.plot([x_grad, x_grad], [1.0, 1.08], color="white", lw=1)
        if info["type"] not in ["raies"]:
            ax.text(
                x_grad,
                -0.25,
                f"{wl_test}",
                color="#90A4AE",
                fontsize=8,
                ha="center",
            )

    return fig

def dessiner_zoom_spectre_atelier2():
    """Génère la règle nanométrique horizontale zoomée du spectre de l'Atelier 2."""
    nom_selectionne = st.session_state.source_lumineuse_choisie
    info = st.session_state.lampes_data[nom_selectionne]
    largeur_s = 700

    fig, ax = plt.subplots(figsize=(10, 2.0), facecolor="#0d1117")
    ax.set_facecolor("#0d1117")
    ax.set_xlim(0, largeur_s)
    ax.set_ylim(-0.4, 1.4)
    ax.axis("off")

    # 1. Tracé du fond continu ou mixte (Bande colorée horizontale)
    if info["type"] in [
        "continu",
        "continu_chaude",
        "led_froide",
        "led_chaude",
        "mixte",
    ]:
        for i in range(largeur_s):
            ratio = i / largeur_s
            # Inversion physique : get_rgb_continu reçoit 1.0 - ratio
            c_hex = get_rgb_continu(1.0 - ratio, info["type"])
            ax.plot([i, i], [0.02, 0.98], color=c_hex, lw=1.5, alpha=1.0)

    # Dessin de l'encadré blanc autour de la bande de spectre
    rect_cadre = plt.Rectangle(
        (0, 0), largeur_s, 1.0, fill=False, edgecolor="white", lw=1.5
    )
    ax.add_patch(rect_cadre)

    # 2. Superposition des raies atomiques et de leurs étiquettes textuelles
    if "raies" in info:
        for wl, couleur, pos_relative in info["raies"]:
            x_raie = int(pos_relative * largeur_s)
            # Tracé de la raie brillante
            ax.plot([x_raie, x_raie], [0.02, 0.98], color=couleur, lw=3.5)
            # Affichage de la longueur d'onde sous la raie
            ax.text(
                x_raie,
                -0.25,
                f"{wl} nm",
                color="#ECEFF1",
                fontsize=8,
                fontname="Courier",
                fontweight="bold",
                ha="center",
            )

    # 3. Échelle de graduations globales de la règle de référence (400 à 700 nm)
    for wl_test in range(400, 701, 50):
        x_grad = int(((wl_test - 400) / 300) * largeur_s)
        # Trait de graduation blanc vers le haut
        ax.plot([x_grad, x_grad], [1.0, 1.08], color="white", lw=1)
        # Affichage du chiffre si ce n'est pas un spectre de raies pur (évite les chevauchements)
        if info["type"] not in ["raies"]:
            ax.text(
                x_grad,
                -0.25,
                f"{wl_test}",
                color="#90A4AE",
                fontsize=8,
                ha="center",
            )

    return fig

def valider_tout2(base_questions_2):
    """Controle l'identite, calcule le score du QCM 2 et fige les selections."""
    nom_eleve = st.session_state.nom_var.strip().upper()

    # 1. Verification d'identite stricte
    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.error(
            "Action interdite : Veuillez obligatoirement inscrire votre NOM sur l'onglet Identification avant de valider."
        )
        return

    score = 0
    # 2. Calcul du score d'apres les choix de l'etudiant
    for idx, item in enumerate(base_questions_2):
        reponse_utilisateur = st.session_state.reponses_quiz2.get(idx, "")
        if reponse_utilisateur == item["rep"]:
            score += 1

    # Enregistrement de l'etat de validation pour bloquer les widgets
    st.session_state.quiz2_valide = True

    # Generation de la chaine de texte du score final
    st.session_state.quiz2_score_txt = (
        f"Nom : {nom_eleve} | Score : {score} / 10"
    )

def generer_code_html_rapport2(base_questions_2):
    """Calcule le score et génère la chaîne HTML brute du rapport technique de l'Atelier 2."""
    nom_eleve = st.session_state.nom_var.strip().upper()

    score = 0
    lignes_html_tableau = ""

    for idx, item in enumerate(base_questions_2):
        reponse_eleve = st.session_state.reponses_quiz2.get(idx, "").strip()
        reponse_correcte = item["rep"].strip()
        intitule_q = item["q"].strip()

        if reponse_eleve == reponse_correcte:
            score += 1
            statut_badge = '<span class="status-pass">CORRECT</span>'
        else:
            statut_badge = '<span class="status-fail">INCORRECT</span>'

        if reponse_eleve == "":
            reponse_eleve = "Aucune reponse"

        lignes_html_tableau += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
            <td>{intitule_q}</td>
            <td style="color: #64748b;">{reponse_eleve}</td>
            <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
            <td style="text-align: center;">{statut_badge}</td>
        </tr>
        """

    note_sur_20 = (score / 10) * 20
    nom_source = st.session_state.var_sel_metal
    couleur_score = "#16a34a" if score == 10 else "#dc2626"

    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Spectres d'emission</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: {couleur_score}; }}
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
            <div class="value">{score} / 10</div>
            <div class="sub">soit {note_sur_20:.1f} / 20</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Éleve :</strong> {nom_eleve}<br>
            <strong>Evaluation type QCM :</strong> Atelier 2 - Spectres d'emission atomiques | Flacon utilise : {nom_source}
        </div>
    </div>
    <div class="section-title">Résultats et correction du QCM - Spectroscopie</div>
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
    return html_content, nom_eleve

def basculer_mode_examen_protection2():
    """Protocole de blocage strict pour le Mode Examen (Atelier 2).

    Fige les sources de lumière et les flacons sur une sélection aléatoire
    imposée.
    """
    nom_eleve = st.session_state.nom_var.strip().upper()

    # 1. Vérification d'identité préalable
    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.session_state.mode_examen_tab2 = False
        st.error(
            "Saisie obligatoire : Inscrivez votre NOM sur l'onglet Identification avant de cocher le Mode Examen."
        )
        return

    # 2. Si le mode examen est activé, on fige des paramètres imposés pour l'élève
    if st.session_state.mode_examen_tab2:
        # Sélection aléatoire verrouillée parmi ton catalogue de lampes
        liste_lampes_dispo = list(st.session_state.lampes_data.keys())
        st.session_state.source_lumineuse_choisie = random.choice(
            liste_lampes_dispo
        )

        # Sélection aléatoire verrouillée pour les flacons de sel
        liste_metaux_dispo = list(st.session_state.catalogue_metaux.keys())
        st.session_state.var_sel_metal = random.choice(liste_metaux_dispo)

        # Extinction obligatoire du brûleur autonome
        st.session_state.var_combustion_active = False
        st.session_state.var_versement_poudre = False

        # Réinitialisation forcée des sélections du QCM pour composer sous examen
        if "reponses_quiz2" in st.session_state:
            st.session_state.reponses_quiz2 = {
                i: "" for i in range(len(st.session_state.reponses_quiz2))
            }



def basculer_mode_examen_protection1():
    """Protocole de blocage strict pour le Mode Examen (Atelier 1).

    Fige les curseurs sur des valeurs aléatoires imposées et verrouille les
    contrôles.
    """
    nom_eleve = st.session_state.nom_var.strip().upper()

    # 1. Vérification d'identité préalable
    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.session_state.mode_examen_tab1 = False
        st.error(
            "Saisie obligatoire : Inscrivez votre NOM sur l'onglet Identification avant de cocher le Mode Examen."
        )
        return

    # 2. Si le mode examen vient d'être activé, on fige des paramètres aléatoires imposés
    if st.session_state.mode_examen_tab1:
        # Valeurs aléatoires imposées pour l'examen
        st.session_state.var_angle_incidence = float(random.randint(35, 60))
        st.session_state.var_indice_n = round(
            random.uniform(1.450, 1.650), 3
        )

        # Arrêt forcé et réinitialisation de la vitesse du disque
        st.session_state.anim_en_cours = False
        st.session_state.var_vitesse_disque = 5.0

        # Optionnel : réinitialiser le choix des réponses pour forcer l'élève à composer sous examen
        if "reponses_quiz1" in st.session_state:
            st.session_state.reponses_quiz1 = {
                i: "" for i in range(len(st.session_state.reponses_quiz1))
            }

def generer_code_html_rapport(base_questions):
    """Calcule le score et génère la chaîne HTML brute du rapport technique d'après le gabarit."""
    nom_eleve = st.session_state.nom_var.strip().upper()

    score = 0
    lignes_html_tableau = ""

    # Parcours des questions et compilation des lignes
    for idx, item in enumerate(base_questions):
        reponse_eleve = st.session_state.reponses_quiz1.get(idx, "").strip()
        reponse_correcte = item["rep"].strip()
        intitule_q = item["q"].strip()

        if reponse_eleve == reponse_correcte:
            score += 1
            statut_badge = '<span class="status-pass">CORRECT</span>'
        else:
            statut_badge = '<span class="status-fail">INCORRECT</span>'

        if reponse_eleve == "":
            reponse_eleve = "Aucune reponse"

        lignes_html_tableau += f"""
        <tr>
            <td style="text-align: center; font-weight: bold; color: #1e293b;">{idx+1}</td>
            <td>{intitule_q}</td>
            <td style="color: #64748b;">{reponse_eleve}</td>
            <td style="font-weight: 500; color: #1e293b;">{reponse_correcte}</td>
            <td style="text-align: center;">{statut_badge}</td>
        </tr>
        """

    note_sur_20 = (score / 10) * 20
    couleur_score = "#16a34a" if score == 10 else "#dc2626"

    # Construction du document HTML calqué sur ton style d'origine
    html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Resultats et correction - Decomposition de la lumiere</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background-color: #ffffff; color: #1e293b; }}
        .header-blue {{ background-color: #2563eb; color: #ffffff; padding: 24px; border-radius: 8px; position: relative; margin-bottom: 30px; border: 1px solid #1d4ed8; }}
        .header-title {{ font-size: 22px; font-weight: bold; margin-bottom: 14px; letter-spacing: 0.5px; }}
        .meta-info {{ font-size: 14px; line-height: 1.6; opacity: 0.95; }}
        .score-box {{ position: absolute; right: 24px; top: 24px; background-color: #ffffff; color: #2563eb; padding: 14px 24px; border-radius: 6px; text-align: center; border: 1px solid #e2e8f0; min-width: 120px; }}
        .score-box .title {{ font-size: 10px; font-weight: bold; color: #1e3a8a; text-transform: uppercase; margin-bottom: 4px; }}
        .score-box .value {{ font-size: 26px; font-weight: bold; color: {couleur_score}; }}
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
            <div class="value">{score} / 10</div>
            <div class="sub">soit {note_sur_20:.1f} / 20</div>
        </div>
        <div class="header-title">Professeur Laurent GALLET</div>
        <div class="meta-info">
            <strong>Éleve :</strong> {nom_eleve}<br>
            <strong>Evaluation type QCM :</strong> Atelier 1 - Spectroscopie et Disque de Newton
        </div>
    </div>
    <div class="section-title">Résultats et correction du QCM - Optique</div>
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
    return html_content, nom_eleve

                        
def reset_sous():
    """Remet à zéro la synthèse soustractive (Retour au Blanc)."""
    st.session_state.var_cyan = 0
    st.session_state.var_magenta = 0
    st.session_state.var_jaune = 0


def reset_rvb():
    """Remet à zéro la synthèse additive (Retour au Noir)."""
    st.session_state.var_rouge = 0
    st.session_state.var_vert = 0
    st.session_state.var_bleu = 0

def dessiner_synthese_couleurs():
    """Moteur de calcul physique : Mélange les couleurs CMJ et RVB

    d'après les curseurs présents dans le session_state.
    """
    # 1. Traitement de la Synthèse Soustractive (CMJ)
    # Formule physique : Le Cyan absorbe le Rouge, le Magenta absorbe le Vert, le Jaune absorbe le Bleu
    c = st.session_state.var_cyan
    m = st.session_state.var_magenta
    j = st.session_state.var_jaune

    r_sous = max(0, 255 - c)
    g_sous = max(0, 255 - m)
    b_sous = max(0, 255 - j)
    hex_sous = f"#{r_sous:02x}{g_sous:02x}{b_sous:02x}"
    st.session_state.var_txt_hex_sous = f"Simulation SOUS (RGB): {hex_sous.upper()}"

    # 2. Traitement de la Synthèse Additive (RVB)
    # Formule physique : Addition directe des intensités lumineuses reçues
    r_add = st.session_state.var_rouge
    g_add = st.session_state.var_vert
    b_add = st.session_state.var_bleu
    hex_rvb = f"#{r_add:02x}{g_add:02x}{b_add:02x}"
    st.session_state.var_txt_hex_rvb = f"Code Hex: {hex_rvb.upper()}"

    return hex_rvb, hex_sous


def valider_tout1(base_questions):
    """Contrôle l'identité, calcule le score du QCM 1 et applique le verrouillage définitif."""
    nom_eleve = st.session_state.nom_var.strip().upper()

    # 1. Vérification d'identité stricte
    if nom_eleve in ["", "NOM", "ELEVE", "INCONNU"]:
        st.error(
            "Action interdite : Veuillez obligatoirement inscrire votre NOM sur l'onglet Identification avant de valider."
        )
        return

    score = 0
    # 2. Calcul du score d'après les choix enregistrés
    for idx, item in enumerate(base_questions):
        reponse_utilisateur = st.session_state.reponses_quiz1.get(idx, "")
        if reponse_utilisateur == item["rep"]:
            score += 1

    # Enregistrement de l'état de validation
    st.session_state.quiz1_valide = True

    # Génération du texte de résultat
    if score == 10:
        st.session_state.quiz1_score_txt = (
            f"Nom : {nom_eleve} | Score : {score} / 10"
        )
    else:
        st.session_state.quiz1_score_txt = (
            f"Nom : {nom_eleve} | Score : {score} / 10"
        )

        
def mettre_a_jour_decomposition():
    """Moteur géométrique stable converti de Tkinter vers Matplotlib.

    Gère le repère inversé pour assurer la trajectoire parfaite des rayons
    (Incident -> Interne -> Émergent -> Écran).
    """
    angle_i_deg = st.session_state.var_angle_incidence
    n_base = st.session_state.var_indice_n

    # Dimensions fixes calquées sur le conteneur Tkinter
    w, h = 680, 260
    y0 = (h - 60) / 2.0  # Axe optique central horizontal

    fig, ax = plt.subplots(figsize=(8, 3.5), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.invert_yaxis()  # Inversion de l'axe Y indispensable pour correspondre à Tkinter
    ax.axis("off")

    angle_i = math.radians(angle_i_deg)
    angle_prisme = math.radians(60.0)

    # Géométrie du Prisme (Sommet en haut)
    x_sommet = 120.0
    y_sommet = y0 - 50.0
    x_gauche = x_sommet - 45.0
    y_gauche = y0 + 50.0
    x_droite = x_sommet + 45.0
    y_droite = y0 + 50.0

    # Tracé géométrique du prisme
    prisme = plt.Polygon(
        [[x_sommet, y_sommet], [x_gauche, y_gauche], [x_droite, y_droite]],
        facecolor="#e0f2fe",
        edgecolor="#38bdf8",
        linewidth=1.5,
        alpha=0.7,
    )
    ax.add_patch(prisme)
    ax.text(
        x_sommet,
        y_sommet - 15,
        "Prisme",
        color="white",
        fontsize=8,
        fontweight="bold",
        ha="center",
    )

    # Rayon incident de lumière blanche (Amont)
    x_entree = x_gauche + 15.0
    y_entree = y0 + 12.0
    x_src = 15.0
    y_src = y_entree - (x_entree - x_src) * math.tan(angle_i - math.radians(30))

    # Affichage du rayon blanc avec sa flèche indicative
    ax.plot([x_src, x_entree], [y_src, y_entree], color="#ffffff", lw=2)
    ax.annotate(
        "",
        xy=(x_entree, y_entree),
        xytext=(x_src, y_src),
        arrowprops=dict(arrowstyle="->", color="#ffffff", lw=1.5),
    )

    # Conversion mathématique Longueur d'onde (WL) -> Code RVB Hexadécimal
    def wl_to_rgb(wl):
        if 380 <= wl < 440:
            R, G, B = -(wl - 440) / (440 - 380), 0.0, 1.0
        elif 440 <= wl < 490:
            R, G, B = 0.0, (wl - 440) / (490 - 440), 1.0
        elif 490 <= wl < 510:
            R, G, B = 0.0, 1.0, -(wl - 510) / (510 - 490)
        elif 510 <= wl < 580:
            R, G, B = (wl - 510) / (580 - 510), 1.0, 0.0
        elif 580 <= wl < 645:
            R, G, B = 1.0, -(wl - 645) / (645 - 580), 0.0
        elif 645 <= wl <= 780:
            R, G, B = 1.0, 0.0, 0.0
        else:
            R, G, B = 0.0, 0.0, 0.0
        f = (
            1.0
            if 420 <= wl <= 700
            else (
                0.3 + 0.7 * (wl - 380) / (420 - 380)
                if wl < 420
                else 0.3 + 0.7 * (780 - wl) / (780 - 700)
            )
        )
        return f"#{int(R*f*255):02x}{int(G*f*255):02x}{int(B*f*255):02x}"

    dev_rouge = (
        dev_orange
    ) = (
        dev_jaune
    ) = (
        dev_vert
    ) = dev_bleu = dev_indigo = dev_violet = "Réflexion"
    y_impact_ecran_vert = -999.0
    x_ecran = w - 60.0

    # Balayage par pas de 1 nm pour construire le faisceau dispersé
    for wl in range(400, 701, 1):
        dn = 0.02 * ((550 / wl) ** 2 - 0.5)
        n_reel = n_base + dn

        try:
            sin_r1 = math.sin(angle_i) / n_reel
            if abs(sin_r1) <= 1.0:
                r1 = math.asin(sin_r1)
                r2 = angle_prisme - r1
                sin_i2 = n_reel * math.sin(r2)

                if abs(sin_i2) <= 1.0:
                    i2 = math.asin(sin_i2)
                    D_deg = math.degrees(angle_i + i2 - angle_prisme)

                    # Sauvegarde des déviations calculées pour les 7 couleurs fondamentales
                    if wl == 700:
                        dev_rouge = f"{D_deg:.1f}°"
                    if wl == 620:
                        dev_orange = f"{D_deg:.1f}°"
                    if wl == 580:
                        dev_jaune = f"{D_deg:.1f}°"
                    if wl == 530:
                        dev_vert = f"{D_deg:.1f}°"
                    if wl == 475:
                        dev_bleu = f"{D_deg:.1f}°"
                    if wl == 435:
                        dev_indigo = f"{D_deg:.1f}°"
                    if wl == 400:
                        dev_violet = f"{D_deg:.1f}°"

                    if wl == 550:
                        y_impact_ecran_vert = (
                            y0
                            + 10.0
                            + (dn * 10)
                            + (w - 60.0 - (x_sommet + 15.0 + (dn * 40)))
                            * math.tan(angle_i + i2 - angle_prisme - math.radians(30))
                        )

                    x_sortie = x_sommet + 15.0 + (dn * 40)
                    y_sortie = y0 + 10.0 + (dn * 10)
                    y_ecran = y_sortie + (x_ecran - x_sortie) * math.tan(
                        angle_i + i2 - angle_prisme - math.radians(30)
                    )

                    color_hex = wl_to_rgb(wl)
                    # Tracé des rayons intérieurs et extérieurs
                    ax.plot(
                        [x_entree, x_sortie],
                        [y_entree, y_sortie],
                        color=color_hex,
                        lw=1.5,
                    )
                    ax.plot(
                        [x_sortie, x_ecran],
                        [y_sortie, y_ecran],
                        color=color_hex,
                        lw=2,
                    )
        except ValueError:
            pass

    # Dessin de l'Écran d'observation blanc
    x_ecran_pos = w - 60.0
    y_ecran_haut = y0 - 30
    y_ecran_bas = y0 + 110
    ecran_rect = plt.Rectangle(
        (x_ecran_pos, y_ecran_haut),
        12,
        y_ecran_bas - y_ecran_haut,
        facecolor="#ffffff",
        edgecolor="#94a3b8",
        lw=1.5,
    )
    ax.add_patch(ecran_rect)
    ax.text(
        x_ecran_pos + 6,
        y0 + 40,
        "Écran",
        color="black",
        fontsize=8,
        fontweight="bold",
        va="center",
        ha="center",
        rotation=-90,
    )

    # Tracé de la grande bande de spectre observé en bas du graphique
    bx_debut = 160.0
    bx_fin = w - 60.0
    by_haut = h - 55.0
    by_bas = h - 25.0
    largeur_bande = bx_fin - bx_debut

    ax.text(
        bx_debut - 15,
        (by_haut + by_bas) / 2.0,
        "Spectre observé\nsur l'écran :",
        color="white",
        fontsize=8,
        fontweight="bold",
        ha="right",
        va="center",
    )

    if (
        y_ecran_haut <= y_impact_ecran_vert <= y_ecran_bas
        and y_impact_ecran_vert != -999.0
    ):
        if largeur_bande > 50:
            for px in range(int(largeur_bande)):
                wl_courante = 400 + (px / largeur_bande) * (700 - 400)
                couleur_px = wl_to_rgb(wl_courante)
                ax.plot(
                    [bx_debut + px, bx_debut + px],
                    [by_haut, by_bas],
                    color=couleur_px,
                    lw=1.5,
                )
            spectre_cadre = plt.Rectangle(
                (bx_debut, by_haut),
                largeur_bande,
                by_bas - by_haut,
                fill=False,
                edgecolor="white",
                lw=1.5,
            )
            ax.add_patch(spectre_cadre)
    else:
        spectre_vide = plt.Rectangle(
            (bx_debut, by_haut),
            largeur_bande,
            by_bas - by_haut,
            facecolor="black",
            edgecolor="#334155",
            lw=1.5,
        )
        ax.add_patch(spectre_vide)
        ax.text(
            (bx_debut + bx_fin) / 2.0,
            (by_haut + by_bas) / 2.0,
            "[ Aucun faisceau sur l'écran ]",
            color="#64748b",
            fontsize=8,
            style="italic",
            ha="center",
            va="center",
        )

    if largeur_bande > 50:
        for wl_repere in range(400, 701, 50):
            ratio = (wl_repere - 400) / (700 - 400)
            x_repere = bx_debut + ratio * largeur_bande
            ax.plot([x_repere, x_repere], [by_bas, by_bas + 4], color="#475569", lw=1)
            ax.text(
                x_repere,
                by_bas + 15,
                str(wl_repere),
                color="#64748b",
                fontsize=7,
                ha="center",
            )

    # Sauvegarde des résultats formates du texte de calcul
    st.session_state.var_texte_resultats_decomposition = (
        f"Analyse de dispersion :\n"
        f"• Incidence i = {angle_i_deg:.1f}° | Indice n = {n_base:.3f}\n"
        f"-----------------------------------------\n"
        f"• D_Rouge   = {dev_rouge}  | • D_Bleu   = {dev_bleu}\n"
        f"• D_Orange  = {dev_orange}  | • D_Indigo = {dev_indigo}\n"
        f"• D_Jaune   = {dev_jaune}  | • D_Violet = {dev_violet}\n"
        f"• D_Vert    = {dev_vert}"
    )

    return fig


def recuperer_couleurs_newton():
    """Renvoie le catalogue des 7 couleurs fondamentales d'Isaac Newton."""
    return [
        {"nom": "Rouge", "code": "#ef4444"},
        {"nom": "Orange", "code": "#f97316"},
        {"nom": "Jaune", "code": "#eab308"},
        {"nom": "Vert", "code": "#22c55e"},
        {"nom": "Bleu", "code": "#2563eb"},
        {"nom": "Indigo", "code": "#4f46e5"},
        {"nom": "Violet", "code": "#7c3aed"},
    ]


def dessiner_disque_newton():
    """Génère la figure Matplotlib du disque de Newton avec blanchiment physique

    calculé de manière linéaire selon la vitesse (0 à 25 tr/s).
    """
    # 1. Récupération des paramètres depuis le session_state
    vitesse = st.session_state.var_vitesse_disque
    anim_en_cours = st.session_state.anim_en_cours
    angle_rotation = getattr(st.session_state, "angle_rotation_disque", 0.0)

    # Configuration de la figure Matplotlib
    fig, ax = plt.subplots(figsize=(4, 4), facecolor="#0f172a")
    ax.set_facecolor("#0f172a")
    ax.set_xlim(-110, 110)
    ax.set_ylim(-110, 110)
    ax.axis("off")

    rayon_disque = 100.0
    ouverture_secteur = 360.0 / 7.0

    # Calcul mathématique du blanchiment (Maximum à 25 tours/seconde)
    if anim_en_cours:
        facteur_blanchiment = vitesse / 25.0
        if facteur_blanchiment > 1.0:
            facteur_blanchiment = 1.0
    else:
        facteur_blanchiment = 0.0

    # Base des 7 couleurs de Newton
    couleurs = recuperer_couleurs_newton()

    # Dictionnaire de conversion RVB d'origine
    rgb_base = {
        "#ef4444": (239, 68, 68),  # Rouge
        "#f97316": (249, 115, 22),  # Orange
        "#eab308": (234, 179, 8),  # Jaune
        "#22c55e": (34, 197, 94),  # Vert
        "#2563eb": (37, 99, 235),  # Bleu
        "#4f46e5": (79, 70, 229),  # Indigo
        "#7c3aed": (124, 58, 237),  # Violet
    }

    # Tracé des 7 secteurs avec transition continue vers le blanc pur
    for i, couleur in enumerate(couleurs):
        angle_depart = (angle_rotation + (i * ouverture_secteur)) % 360.0
        hex_code = couleur["code"]

        if hex_code in rgb_base:
            r, g, b = rgb_base[hex_code]
            # Interpolation linéaire vers le blanc (255, 255, 255)
            new_r = int(r + (255 - r) * facteur_blanchiment)
            new_g = int(g + (255 - g) * facteur_blanchiment)
            new_b = int(b + (255 - b) * facteur_blanchiment)
            # Conversion en format normalisé pour Matplotlib (0.0 à 1.0)
            color_plt = (new_r / 255.0, new_g / 255.0, new_b / 255.0)
        else:
            color_plt = hex_code

        # Création de la portion de cercle (Wedge) pour Matplotlib
        wedge = patches.Wedge(
            (0, 0),
            rayon_disque,
            angle_depart,
            angle_depart + ouverture_secteur,
            facecolor=color_plt,
            edgecolor=color_plt,
        )
        ax.add_patch(wedge)

    # Axe central fixe
    axe_central = plt.Circle(
        (0, 0), 5, facecolor="#1e293b", edgecolor="white", lw=1
    )
    ax.add_patch(axe_central)

    # Texte indicatif de l'état de la vitesse en haut à gauche
    txt_vitesse = f"{vitesse:.1f} tr/s" if anim_en_cours else "Statique"
    ax.text(
        -105,
        95,
        f"Vitesse : {txt_vitesse}",
        color="white",
        fontsize=9,
        fontweight="bold",
    )

    return fig

def gerer_action_disque():
    """Gère l'état d'activation et le calcul d'angle statique du disque de Newton."""
    if "angle_rotation_disque" not in st.session_state:
        st.session_state.angle_rotation_disque = 0.0

    vitesse = st.session_state.var_vitesse_disque

    if st.session_state.anim_en_cours:
        st.session_state.angle_rotation_disque = (
            st.session_state.angle_rotation_disque + (vitesse * 2.5)
        ) % 360.0

# 1. Configuration de la page principale
st.set_page_config(
    page_title="TP Physique : optique",
    layout="wide",  # Permet d'occuper tout l'écran de manière fluide
)

# --- SIGNATURE DE L'AUTEUR (Placée en bas de la barre latérale) ---
st.markdown("---")
st.markdown("<div style='text-align: right; color: red; font-style: italic;'>Créé et développé par Laurent GALLET</div>", unsafe_allow_html=True)


# Initialisation d'un flag de verrouillage dans le session_state s'il n'existe pas
if "verrouille" not in st.session_state:
    st.session_state.verrouille = False

# 2. Initialisation des variables de session
if "nom_var" not in st.session_state:
    st.session_state.nom_var = ""
if "prenom_var" not in st.session_state:
    st.session_state.prenom_var = ""
if "classe_var" not in st.session_state:
    st.session_state.classe_var = ""
if "heure_var" not in st.session_state:
    st.session_state.heure_var = datetime.now().strftime("%d/%m/%Y %H:%M")
if "mesures_sin_i" not in st.session_state:
    st.session_state.mesures_sin_i = []
if "mesures_sin_r" not in st.session_state:
    st.session_state.mesures_sin_r = []
if "mesures_deg_i" not in st.session_state:
    st.session_state.mesures_deg_i = []
if "mesures_deg_r" not in st.session_state:
    st.session_state.mesures_deg_r = []
if "var_angle_incidence" not in st.session_state:
    st.session_state.var_angle_incidence = 45.0
if "var_indice_n" not in st.session_state:
    st.session_state.var_indice_n = 1.515
if "var_texte_resultats_decomposition" not in st.session_state:
    st.session_state.var_texte_resultats_decomposition = ""
if "var_vitesse_disque" not in st.session_state:
    st.session_state.var_vitesse_disque = 5.0
if "var_mode_synthese" not in st.session_state:
    st.session_state.var_mode_synthese = "Additive"
if "var_opacite_synthese" not in st.session_state:
    st.session_state.var_opacite_synthese = 1.0
if "anim_en_cours" not in st.session_state:
    st.session_state.anim_en_cours = False
if "quiz1_valide" not in st.session_state:
    st.session_state.quiz1_valide = False
if "quiz1_score_txt" not in st.session_state:
    st.session_state.quiz1_score_txt = ""

    
# Couleurs et codes hexadécimaux
if "var_rouge" not in st.session_state: st.session_state.var_rouge = 0
if "var_vert" not in st.session_state: st.session_state.var_vert = 0
if "var_bleu" not in st.session_state: st.session_state.var_bleu = 0
if "var_cyan" not in st.session_state: st.session_state.var_cyan = 0
if "var_magenta" not in st.session_state: st.session_state.var_magenta = 0
if "var_jaune" not in st.session_state: st.session_state.var_jaune = 0    
# Initialisation des modes examen pour les onglets (tab1 à tab9)
for i in range(1, 10):
    key = f"mode_examen_tab{i}"
    if key not in st.session_state:
        st.session_state[key] = False
# 1. ÉQUIVALENT DE : valider_saisie(self)
def valider_saisie():
    nom = st.session_state.nom_var.strip()
    prenom = st.session_state.prenom_var.strip()
    classe = st.session_state.classe_var.strip()

    if not nom or not prenom or not classe:
        st.error(
            "Erreur : Veuillez compléter entièrement vos données et valider."
        )
    else:
        st.session_state.verrouille = True
        st.success(
            f"Validation effectuée pour : {nom} {prenom} {classe}. Le formulaire est maintenant verrouillé."
        )


# 2. ÉQUIVALENT DE : capturer_onglet_complet(self)
# Note : Sur le web, on génère un rapport texte/données téléchargeable au lieu d'une capture d'écran graphique.
def preparer_nom_fichier(nom_onglet):
    nom_propre = st.session_state.nom_var.replace(" ", "_")
    prenom_propre = st.session_state.prenom_var.replace(" ", "_")
    classe_propre = st.session_state.classe_var.replace(" ", "_")

    maintenant = datetime.now()
    heure_actuelle = maintenant.strftime("%H-%M-%S")
    date_texte = maintenant.strftime("%Y-%m-%d_%Hh%M")

    nom_fichier = f"{nom_propre}_{prenom_propre}_{classe_propre}_{date_texte}_{heure_actuelle}_{nom_onglet}.txt"
    return nom_fichier

# Déclaration officielle des 10 onglets de navigation
tabs = st.tabs([
    "Identification",
    "1. Décomposition de la lumière",
    "2. Les différentes lumières",
    "3. La loi de la réflexion",
    "4. La loi de la réfraction",
    "5. Les lentilles convergentes",
    "6. Les lentilles divergentes",
    "7. La lunette astronomique",
    "8. La lunette de Galilée",
    "9. Le microscope"
])

# Assignation des variables d'onglets (C'est ici que tab0 est créé !)
tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = tabs
with tab0:
    st.header("Identification")
    with st.container(border=True):
        st.markdown("### Travaux Pratiques")

        # Organisation en deux colonnes pour une interface propre
        col_champs, col_vide = st.columns([2, 1])

        with col_champs:
            # Champ de saisie : Nom
            nom_saisi = st.text_input(
                "Nom :",
                value=st.session_state.nom_var,
                disabled=st.session_state.verrouille,
            )
            # Champ de saisie : Prénom
            prenom_saisi = st.text_input(
                "Prénom :",
                value=st.session_state.prenom_var,
                disabled=st.session_state.verrouille,
            )
            # Champ de saisie : Groupe / Classe
            classe_saisie = st.text_input(
                "Groupe / Classe :",
                value=st.session_state.classe_var,
                disabled=st.session_state.verrouille,
            )

            # Sauvegarde immédiate des données dans le session_state
            st.session_state.nom_var = nom_saisi
            st.session_state.prenom_var = prenom_saisi
            st.session_state.classe_var = classe_saisie

            # Espacement avant le bouton
            st.write("")

            # Bouton de validation (simule le bouton Ok)
            if st.button("Ok", disabled=st.session_state.verrouille):
                valider_session()
                st.rerun()
                
def valider_session():
    nom = st.session_state.nom_var.strip()
    prenom = st.session_state.prenom_var.strip()
    groupe = st.session_state.classe_var.strip()  # Correspond à votre champ groupe/classe

    if not nom or not prenom or not groupe:
        st.warning(
            "Identification incomplète : Veuillez remplir l'ensemble des champs avant de commencer vos manipulations."
        )
    else:
        st.session_state.verrouille = True
        st.success(
            f"Session Ouverte : Bienvenue {prenom} {nom}.\nVotre session de TP pour le groupe {groupe} est désormais active."
        )



with tab1:
    st.subheader("Décomposition de la lumière")

    # Déclaration du catalogue de questions pour éviter les erreurs de lecture
    base_questions = [
        {"q": "Quel physicien célèbre a démontré le premier la décomposition de la lumière blanche à l'aide d'un prisme ?", "options": ["Isaac Newton", "Albert Einstein", "René Descartes"], "rep": "Isaac Newton"},
        {"q": "Comment qualifie-t-on une lumière composée d'une seule radiation colorée (une seule longueur d'onde) ?", "options": ["Monochromatique", "Polychromatique", "Isotrope"], "rep": "Monochromatique"},
        {"q": "Quel phénomène physique explique la séparation des longueurs d'onde lors de la traversée du prisme ?", "options": ["La dispersion", "La diffraction", "La réflexion totale"], "rep": "La dispersion"},
        {"q": "Comment varie l'indice de réfraction 'n' du verre en fonction de la fréquence de la lumière incidente ?", "options": ["L'indice n augmente quand la fréquence augmente", "L'indice n diminue quand la fréquence augmente", "L'indice n reste constant"], "rep": "L'indice n augmente quand la fréquence augmente"},
        {"q": "Quelle radiation lumineuse visible subit la déviation la plus forte (l'angle de déviation le plus grand) ?", "options": ["Le Violet", "Le Rouge", "Le Vert"], "rep": "Le Violet"},
        {"q": "Quelle radiation lumineuse visible subit la déviation la moins forte à la sortie du bloc de verre ?", "options": ["Le Rouge", "Le Bleu", "Le Jaune"], "rep": "Le Rouge"},
        {"q": "Quelle est la grandeur physique qui s'exprime en nanomètres (nm) pour caractériser une couleur du spectre ?", "options": ["La longueur d'onde lambda", "L'indice de réfraction n", "La célérité c"], "rep": "La longueur d'onde lambda"},
        {"q": "Quelle experience interactive présente à l'écran permet de reconstituer la lumière blanche par persistance rétinienne ?", "options": ["Le disque de Newton tournant", "La synthèse soustractive", "L'analyse dispersive"], "rep": "Le disque de Newton tournant"},
        {"q": "Comment appelle-t-on la superposition de lumières colorées pour créer une nouvelle teinte (Rouge + Vert = Jaune) ?", "options": ["La synthèse additive", "La synthèse soustractive", "La dispersion prismatique"], "rep": "La synthèse additive"},
        {"q": "Si on mélange les trois filtres Cyan, Magenta et Jaune en synthèse soustractive pure, quelle couleur obtient-on ?", "options": ["Du Noir", "Du Blanc", "Du Vert"], "rep": "Du Noir"}
    ]

    col_gauche, col_droite = st.columns(2)

    with col_gauche:
        with st.container(border=True):
            st.markdown("**Décomposition de la lumière du soleil**")
            
            # 1. ON ENREGISTRE D'ABORD LES CURSEURS
            st.session_state.var_angle_incidence = st.slider(
                "Angle d'incidence i (°):",
                min_value=10.0, max_value=80.0,
                value=st.session_state.var_angle_incidence,
                step=0.5, key="slider_angle",
                disabled=st.session_state.mode_examen_tab1
            )

            st.session_state.var_indice_n = st.slider(
                "Indice de base n :",
                min_value=1.30, max_value=1.80,
                value=st.session_state.var_indice_n,
                step=0.005, key="slider_indice",
                disabled=st.session_state.mode_examen_tab1
            )
            
            # 2. ON CORRIGE : ON FORCE LE CALCUL TECHNIQUE IMMÉDIATEMENT APRÈS LA LECTURE DES SLIDERS
            fig_decomposition = mettre_a_jour_decomposition()

            # 3. ON AFFICHE LE TEXTE CALCULÉ ET RAFRAÎCHI
            if st.session_state.var_texte_resultats_decomposition:
                st.code(st.session_state.var_texte_resultats_decomposition)
            else:
                st.info("Résultats de la décomposition")

        # --- CADRAN 2 : Recomposition ---
        with st.container(border=True):
            st.markdown("**Recomposition de la lumière du soleil**")
            
            label_bouton = "Arrêter le Disque" if st.session_state.anim_en_cours else "Lancer le Disque"
            if st.button(label_bouton, key="btn_disque_action", disabled=st.session_state.mode_examen_tab1):
                st.session_state.anim_en_cours = not st.session_state.anim_en_cours
                gerer_action_disque()
                st.rerun()

            st.session_state.var_vitesse_disque = st.slider(
                "Vitesse du disque (tr/s) :",
                min_value=1.0,
                max_value=40.0,
                value=st.session_state.var_vitesse_disque,
                step=1.0,
                key="slider_vitesse_disque"
            )


    with col_droite:
        # 4. ON AFFICHE LA FIGURE DÉJÀ CALCULÉE ET À JOUR
        st.pyplot(fig_decomposition)

        st.markdown("---")
        fig_disque = dessiner_disque_newton()
        st.pyplot(fig_disque)

    # --- ZONE INFERIEURE : QUIZ & CONTROLE ---
    st.markdown("---")
    col_quiz, col_controle = st.columns(2)

    with col_quiz:
        st.markdown("##### Évaluation : Décomposition de la lumière")
        if "reponses_quiz1" not in st.session_state:
            st.session_state.reponses_quiz1 = {i: "" for i in range(len(base_questions))}

        for idx, item in enumerate(base_questions):
            options_affichage = list(item["options"])
            st.session_state.reponses_quiz1[idx] = st.selectbox(
                f"{idx + 1}. {item['q']}",
                options=[""] + options_affichage,
                index=0 if st.session_state.reponses_quiz1[idx] == "" else options_affichage.index(st.session_state.reponses_quiz1[idx]) + 1,
                key=f"q1_{idx}",
                disabled=st.session_state.quiz1_valide
            )

    with col_controle:
        with st.container(border=True):
            st.markdown("<p style='color:darkblue; font-weight:bold; margin-bottom:0;'>CONTROLE EXAMEN</p>", unsafe_allow_html=True)
            
            mode_examen_avant = st.session_state.mode_examen_tab1
            st.session_state.mode_examen_tab1 = st.checkbox(
                "Mode Examen", 
                value=st.session_state.mode_examen_tab1,
                key="check_examen_tab1",
                disabled=st.session_state.quiz1_valide or mode_examen_avant
            )
            
            if st.session_state.mode_examen_tab1 and not mode_examen_avant:
                basculer_mode_examen_protection1()
                st.rerun()
            
            if st.session_state.quiz1_valide:
                st.info(st.session_state.quiz1_score_txt)

            if not st.session_state.quiz1_valide:
                confirmer = st.checkbox("Je confirme vouloir valider définitivement l'évaluation.", key="conf_quiz1")
                if st.button("Valider", key="btn_valider_tab1", use_container_width=True, disabled=not confirmer):
                    valider_tout1(base_questions)
                    st.rerun()
            else:
                st.button("Validation effectuée", key="btn_valider_tab1_dis", use_container_width=True, disabled=True)
                
            nom_eleve_check = st.session_state.nom_var.strip().upper()
            if nom_eleve_check in ["", "NOM", "ELEVE", "INCONNU"]:
                st.error("Export impossible : Veuillez inscrire votre NOM avant d'exporter.")
            else:
                html_export, nom_propre = generer_code_html_rapport(base_questions)
                nom_fichier = f"Note_de_calculs_Optique_{nom_propre}_Classe.html"
                for car in ["*", "?", ":", "/", "\\", "<", ">", "|", '"', " "]:
                    nom_fichier = nom_fichier.replace(car, "_")
                
                st.download_button(
                    label="Exporter le rapport HTML",
                    data=html_export,
                    file_name=nom_fichier,
                    mime="text/html",
                    use_container_width=True
                )
            
        # --- SYNTHÈSE ADDITIVE ET SOUSTRACTIVE ---
        with st.container(border=True):
            st.markdown("**Synthèse additive et soustractive**")

            # Appel automatique du moteur de calcul physique
            hex_rvb, hex_sous = dessiner_synthese_couleurs()

            col_add, col_sous = st.columns(2)
          
            # --- BLOC SYNTHÈSE ADDITIVE ---
            with col_add:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; font-weight:bold;'>Synthèse Additive</p>", unsafe_allow_html=True)
                    
                    # Récupération et conversion des couleurs RVB
                    r = st.session_state.var_rouge
                    v = st.session_state.var_vert
                    b = st.session_state.var_bleu
                    hex_rvb = f"#{r:02x}{v:02x}{b:02x}"
                    st.session_state.var_txt_hex_rvb = f"Code Hex: {hex_rvb.upper()}"
                    
                    # Zone d'affichage dynamique de la couleur additive (Fond noir par défaut)
                    st.markdown(
                        f'<div style="background-color: {hex_rvb}; height: 45px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 10px;"></div>', 
                        unsafe_allow_html=True
                    )
                    
                                        # Curseurs Sliders alignés verticalement
                    st.session_state.var_rouge = st.slider(
                        "Rouge", 0, 255, value=st.session_state.var_rouge, key="slide_rouge_tab1"
                    )
                    st.session_state.var_vert = st.slider(
                        "Vert", 0, 255, value=st.session_state.var_vert, key="slide_vert_tab1"
                    )
                    st.session_state.var_bleu = st.slider(
                        "Bleu", 0, 255, value=st.session_state.var_bleu, key="slide_bleu_tab1"
                    )
                                        
                    # Affichage de la valeur Hex
                    st.caption(st.session_state.var_txt_hex_rvb)
                    
                    # Bouton Réinitialiser RVB (Remise à 0)
                    if st.button("Réinitialiser RVB", key="btn_reset_rvb"):
                        reset_rvb()
                        st.rerun()


            # --- BLOC SYNTHÈSE SOUSTRACTIVE ---
            with col_sous:
                with st.container(border=True):
                    st.markdown("<p style='text-align:center; font-weight:bold;'>Synthèse Soustractive</p>", unsafe_allow_html=True)
                    
                    # Récupération des curseurs Cyan, Magenta, Jaune
                    c = st.session_state.var_cyan
                    m = st.session_state.var_magenta
                    j = st.session_state.var_jaune
                    
                    # Calcul de la simulation RGB pour la soustraction (Fond blanc par défaut - CMJ soustrait du Blanc)
                    r_sous = max(0, 255 - c)
                    v_sous = max(0, 255 - m)
                    b_sous = max(0, 255 - j)
                    hex_sous = f"#{r_sous:02x}{v_sous:02x}{b_sous:02x}"
                    st.session_state.var_txt_hex_sous = f"Simulation RGB: {hex_sous.upper()}"
                    
                    # Zone d'affichage dynamique de la couleur soustractive
                    st.markdown(
                        f'<div style="background-color: {hex_sous}; height: 45px; border: 1px solid #cbd5e1; border-radius: 4px; margin-bottom: 10px;"></div>', 
                        unsafe_allow_html=True
                    )
                    
                    # Curseurs Sliders pour CMJ
                    st.session_state.var_cyan = st.slider(
                        "Cyan", 0, 255, value=st.session_state.var_cyan, key="slide_cyan_tab1"
                    )
                    st.session_state.var_magenta = st.slider(
                        "Magenta",
                        0,
                        255,
                        value=st.session_state.var_magenta,
                        key="slide_magenta_tab1",
                    )
                    st.session_state.var_jaune = st.slider(
                        "Jaune", 0, 255, value=st.session_state.var_jaune, key="slide_jaune_tab1"
                    )
                    # Affichage de la simulation RGB
                    st.caption(st.session_state.var_txt_hex_sous)
                    
                    # Bouton Réinitialiser CMJ (Remise à 0)
                    if st.button("Réinitialiser CMJ", key="btn_reset_cmj"):
                        reset_sous()
                        st.rerun()



with tab2:
    st.subheader("2. Les différentes lumières")

    col_gauche2, col_droite2 = st.columns(2)
    # =====================================================================
    # COLONNE GAUCHE : MANIPULATION A - TEST DE FLAMME (Sels métalliques)
    # =====================================================================
    with col_gauche2:
        with st.container(border=True):
            st.markdown("##### Manipulation A : Test de flamme")
            st.caption(
                "Analyse des spectres d'emission par excitation thermique de sels metalliques."
            )

            # Menu deroulant pour le choix du flacon de sel
            liste_metaux = list(st.session_state.catalogue_metaux.keys())
            st.session_state.var_sel_metal = st.selectbox(
                "Choisir un flacon de sel :",
                options=liste_metaux,
                index=liste_metaux.index(st.session_state.var_sel_metal),
                key="select_metal_tab2_final",
                disabled=st.session_state.mode_examen_tab2,
            )

            # Recuperation des donnees du metal et mise a jour de la description
            info_metal = gerer_changement_metal()
            st.info(f"**Analyse :** {info_metal['descr']}")

            # Bouton d'action pour declencher la combustion sequentielle
            label_bouton = (
                "Eteindre le bruleur"
                if st.session_state.var_combustion_active
                else "Bruler l'echantillon (Test de flamme)"
            )
            if st.button(
                label_bouton, key="btn_flamme_tab2_final", use_container_width=True
            ):
                declencher_test_flamme_web()
                st.rerun()

            # Rendu visuel de la simulation de la flamme du bec bunsen
            st.markdown("**Visualisation du brûleur Bec Bunsen :**")
            if st.session_state.var_versement_poudre:
                st.markdown(
                    '<div style="background-color: #475569; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 2px dashed #94a3b8;"><span style="color: #ffffff; font-weight: bold;">Versement de la poudre en cours...</span></div>',
                    unsafe_allow_html=True,
                )
            elif st.session_state.var_combustion_active:
                st.markdown(
                    f'<div style="background-color: {info_metal["couleur"]}; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 1px solid #ffffff;"><span style="color: #0d1117; font-weight: bold;">Combustion active : {st.session_state.var_sel_metal}</span></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="background-color: #0d1117; height: 120px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 1px solid #334155;"><span style="color: #64748b; font-style: italic;">[ Bruleur eteint - Cliquez sur Bruler ]</span></div>',
                    unsafe_allow_html=True,
                )

        # Affichage du profil du spectre de raies de la flamme en dessous
        st.markdown("---")
        fig_flamme = dessiner_spectre_flamme_combustion()
        st.pyplot(fig_flamme)

    # =====================================================================
    # COLONNE DROITE : MANIPULATION B - BANC DE SPECTROSCOPIE (Lampes)
    # =====================================================================
    with col_droite2:
        with st.container(border=True):
            st.markdown("##### Manipulation B : Banc de spectroscopie")

            # Menu deroulant pour le choix de l'ampoule / source lumineuse
            liste_lampes = list(st.session_state.lampes_data.keys())
            st.session_state.source_lumineuse_choisie = st.selectbox(
                "Source lumineuse :",
                options=liste_lampes,
                index=liste_lampes.index(
                    st.session_state.source_lumineuse_choisie
                ),
                key="select_lampe_tab2_final",
                disabled=st.session_state.mode_examen_tab2,
            )

            # Identification et coloration de la boite du type de spectre de l'ampoule
            nom_selectionne = st.session_state.source_lumineuse_choisie
            info_lampe = st.session_state.lampes_data[nom_selectionne]

            descr_spectre = info_lampe["descr"]
            if "CONTINU" in descr_spectre.upper():
                st.info(f"**Type de spectre :** {descr_spectre}")
            elif "RAIES" in descr_spectre.upper():
                st.warning(f"**Type de spectre :** {descr_spectre}")
            else:
                st.success(f"**Type de spectre :** {descr_spectre}")

            # Rendu visuel geometrique complet du banc d'optique
            fig_banc_optique = dessiner_montage_complet_atelier2()
            st.pyplot(fig_banc_optique)

            # Rendu du zoom lineaire nanometrique inverse de l'ecran
            st.markdown("---")
            fig_spectre_zoom = dessiner_zoom_spectre_atelier2()
            st.pyplot(fig_spectre_zoom)

    # =====================================================================
    # ZONE BASSE : GRILLE D'EVALUATION ET CONTROLE DE L'EXAMEN
    # =====================================================================
    st.markdown("---")
    col_quiz2, col_controle2 = st.columns(2)

    # Generation des menus déroulants pour le questionnaire

    with col_quiz2:
        st.markdown("##### Évaluation : Les différentes lumières")

        # Grille officielle des 10 questions d'optique pour l'Atelier 2
        base_questions_2 = [
            {"q": "Quel type de spectre obtient-on en analysant la lumiere emise par un gaz d'atomes isoles excites ?", "options": ["Un spectre de raies d'emission", "Un spectre continu d'absorption", "Un spectre de bandes"], "rep": "Un spectre de raies d'emission"},
            {"q": "Quelle source lumineuse classique produit un spectre continu contenant toutes les radiations colorees ?", "options": ["Une lampe a incandescence", "Un laser de laboratoire", "Une lampe a vapeur de sodium"], "rep": "Une lampe a incandescence"},
            {"q": "Lors du test de flamme, quelle couleur caracteristique prend la combustion du chlorure de Sodium (Na) ?", "options": ["Jaune intense", "Vert brillant", "Violet pale"], "rep": "Jaune intense"},
            {"q": "Quelle couleur de flamme specifique permet d'identifyer la presence d'ions Cuivre (Cu) ?", "options": ["Vert-bleu", "Rouge carmin", "Jaune orange"], "rep": "Vert-bleu"},
            {"q": "Pourquoi les raies d'emission d'un element chimique constituent-elles sa signature ou carte d'identite ?", "options": ["Chaque element possede un ensemble unique de longueurs d'onde", "Elles changent de couleur avec la distance", "Elles dependent de l'age du prisme"], "rep": "Chaque element possede un ensemble unique de longueurs d'onde"},
            {"q": "Comment qualifie-t-on le spectre d'une etoile qui traverse une atmosphere gazeuse plus froide ?", "options": ["Un spectre de raies d'absorption", "Un spectre continu pur", "Un spectre polychromatique opaque"], "rep": "Un spectre de raies d'absorption"},
            {"q": "Quel instrument d'optique muni d'un element dispersif permet d'observer ces raies colorees ?", "options": ["Le spectroscope", "Le sonometre", "La lunette afocale"], "rep": "Le spectroscope"},
            {"q": "Quelle est l'unite de mesure utilisee pour reperer la position exacte d'une raie sur l'ecran ?", "options": ["Le nanometre (nm)", "Le Watt (W)", "Le Pascal (Pa)"], "rep": "Le nanometre (nm)"},
            {"q": "Si une source emet une raie unique a 589 nm, dans quel domaine de couleur se situe-t-elle ?", "options": ["Le Jaune", "Le Rouge", "Le Violet"], "rep": "Le Jaune"},
            {"q": "Le spectre de la lumiere émise par le Soleil reçu sur Terre est un spectre :", "options": ["Continu avec des raies d'absorption (Fraunhofer)", "De raies d'emission pur", "Monochromatique strict"], "rep": "Continu avec des raies d'absorption (Fraunhofer)"}
        ]

        # Structure d'enregistrement des réponses de l'Atelier 2
        if "reponses_quiz2" not in st.session_state:
            st.session_state.reponses_quiz2 = {i: "" for i in range(len(base_questions_2))}

        # Rendu des menus déroulants interactifs
        for idx, item in enumerate(base_questions_2):
            options_affichage = list(item["options"])
            
            st.session_state.reponses_quiz2[idx] = st.selectbox(
                f"{idx + 1}. {item['q']}",
                options=[""] + options_affichage,
                index=0 if st.session_state.reponses_quiz2[idx] == "" else options_affichage.index(st.session_state.reponses_quiz2[idx]) + 1,
                key=f"q2_real_{idx}",
                disabled=st.session_state.quiz2_valide
            )
    # Separation de la page en deux colonnes principales
    col_gauche2, col_droite2 = st.columns(2)

    # Cadran de validation et activation de la protection examen
    with col_controle2:
        with st.container(border=True):
            st.markdown(
                "<p style='color:darkblue; font-weight:bold; margin-bottom:0;'>CONTROLE EXAMEN</p>",
                unsafe_allow_html=True,
            )
    with col_controle2:
        with st.container(border=True):
            st.markdown(
                "<p style='color:darkblue; font-weight:bold; margin-bottom:0;'>CONTROLE EXAMEN</p>",
                unsafe_allow_html=True,
            )

            mode_examen2_avant = st.session_state.mode_examen_tab2
            st.session_state.mode_examen_tab2 = st.checkbox(
                "Mode Examen",
                value=st.session_state.mode_examen_tab2,
                key="check_examen_tab2_final",
                disabled=st.session_state.quiz2_valide or mode_examen2_avant,
            )

            if st.session_state.mode_examen_tab2 and not mode_examen2_avant:
                basculer_mode_examen_protection2()
                st.rerun()

            if st.session_state.quiz2_valide:
                st.info(st.session_state.quiz2_score_txt)

            if not st.session_state.quiz2_valide:
                confirmer2 = st.checkbox(
                    "Je confirme vouloir valider définitivement l'évaluation de l'Atelier 2.",
                    key="conf_quiz2_final_propre",
                )
                if st.button(
                    "Valider",
                    key="btn_valider_tab2_final",
                    use_container_width=True,
                    disabled=not confirmer2,
                ):
                    valider_tout2(base_questions_2)
                    st.rerun()
            else:
                st.button(
                    "Validation effectuée",
                    key="btn_valider_tab2_dis_final",
                    use_container_width=True,
                    disabled=True,
                )

                
with tab3:
    st.header("3. La loi de la réflexion")

with tab4:
    st.header("4. La loi de la réfraction")

with tab5:
    st.header("5. Les lentilles convergentes")

with tab6:
    st.header("6. Les lentilles divergentes")

with tab7:
    st.header("7. La lunette astronomique")

with tab8:
    st.header("8. La lunette de Galilée")

with tab9:
    st.header("9. Le microscope")
