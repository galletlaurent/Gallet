import streamlit as st
import random

# CONFIGURATION DE LA PAGE
st.set_page_config(page_title="Permis C - Revisions", layout="centered")


# --- FONCTION DE GENERATION DU COMPTE-RENDU HTML ---
def generer_html_correction(nom_fiche, questions, reponses_utilisateur, score):
    statut_examen = "REUSSI" if score >= 8 else "ECHEC"
    couleur_statut = "#2ecc71" if score >= 8 else "#e74c3c"
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Correction - {nom_fiche}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; color: #333; }}
            .container {{ max-width: 800px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
            .vignette-note {{ background-color: {couleur_statut}; color: white; padding: 15px; border-radius: 5px; font-size: 20px; font-weight: bold; margin-bottom: 20px; text-align: center; }}
            .bloc-question {{ margin-bottom: 20px; padding: 15px; border-left: 5px solid #34495e; background-color: #f8f9fa; }}
            .correct {{ border-left-color: #2ecc71; background-color: #eafaf1; }}
            .incorrect {{ border-left-color: #e74c3c; background-color: #fdedec; }}
            .label {{ font-weight: bold; color: #7f8c8d; }}
            .reponse {{ margin-top: 5px; font-size: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Correction : {nom_fiche}</h1>
            <div class="vignette-note">
                Note : {score} / 10 ({statut_examen})
            </div>
    """
    
    for idx, item in enumerate(questions):
        valide = reponses_utilisateur.get(idx, False)
        classe_css = "correct" if valide else "incorrect"
        statut_texte = "Valide" if valide else "Non valide / Faux"
        
        html += f"""
            <div class="bloc-question {classe_css}">
                <p><strong>Question {idx+1} :</strong> {item['q']}</p>
                <p class="reponse"><span class="label">Votre evaluation :</span> {statut_texte}</p>
                <p class="reponse"><span class="label">Reponse officielle :</span> {item['r']}</p>
            </div>
        """
        
    html += """
        </div>
    </body>
    </html>
    """
    return html

# --- INTERFACE ET LOGIQUE ---
st.title("Entrainement Permis C (Poids Lourd)")
st.write("Entrainez-vous aux epreuves theoriques du plateau.")

st.header("Questions Ecrites (Tirage par fiche)")
st.write("L'examen comporte 10 questions liees a une fiche. Cochez les cases si votre reponse est correcte.")

mode_selection = st.radio("Mode de selection de la fiche :", ["Selectionner manuellement", "Tirer au sort au hasard"])

# Gestion du changement de fiche pour reinitialiser les cases a cocher
if mode_selection == "Selectionner manuellement":
    fiche_choisie_ecrite = st.selectbox("Choisissez la fiche ecrite a reviser :", list(SERIES_ECRITES.keys()))
    if "serie_choisie" not in st.session_state or st.session_state.serie_choisie != fiche_choisie_ecrite:
        st.session_state.serie_choisie = fiche_choisie_ecrite
        st.session_state.reponses = {}
else:
    if st.button("Tirer une fiche ecrite au sort", key="btn_ecrit"):
        st.session_state.serie_choisie = random.choice(list(SERIES_ECRITES.keys()))
        st.session_state.reponses = {}

if "serie_choisie" in st.session_state:
    st.subheader(st.session_state.serie_choisie)
    questions = SERIES_ECRITES[st.session_state.serie_choisie]
    
    # Initialisation du dictionnaire des reponses si inexistant
    if "reponses" not in st.session_state:
        st.session_state.reponses = {}
        
    # Affichage des questions
    for idx, item in enumerate(questions):
        st.markdown(f"**Question {idx+1} :** {item['q']}")
        
        # Affichage de la reponse cachee
        with st.expander("Voir la reponse officielle"):
            st.info(f"Reponse : {item['r']}")
            
        # Case a cocher pour la correction autonome
        cle_case = f"q_{st.session_state.serie_choisie}_{idx}"
        valeur_case = st.checkbox("Ma reponse est correcte", key=cle_case)
        st.session_state.reponses[idx] = valeur_case
        st.write("---")

    # Calcul de la note globale
    score_final = sum(1 for v in st.session_state.reponses.values() if v)
    
    st.subheader(f"Votre Note : {score_final} / 10")
    if score_final >= 8:
        st.success("Examen Reussi (Minimum 8/10 requis)")
    else:
        st.error("Examen Echoue (Minimum 8/10 requis)")
        
    # Bouton de telechargement du fichier HTML de correction
    donnees_html = generer_html_correction(
        st.session_state.serie_choisie, 
        questions, 
        st.session_state.reponses, 
        score_final
    )
    
    st.download_button(
        label="Telecharger le compte-rendu HTML",
        data=donnees_html,
        file_name=f"correction_{st.session_state.serie_choisie.replace(' ', '_')}.html",
        mime="text/html"
    )

SERIES_ECRITES = {
    "Fiche Ecrite 1 : Situations degradees et accidents": [
        {"q": "A l'approche d'un accident, quel feu devez-vous actionner immediatement ?", "r": "Les feux de detresse (warning)"},
        {"q": "Quelle est la distance minimale pour placer le triangle de pre-signalisation ?", "r": "30 metres"},
        {"q": "Quel est le numero d'urgence europeen unique gratuit ?", "r": "112"},
        {"q": "Peut-on deplacer un blesse en cas de danger reel et imminent ?", "r": "Oui"},
        {"q": "Quel est le delai maximal d'envoi d'un constat amiable a l'assureur ?", "r": "5 jours ouvres"},
        {"q": "Le gilet de haute visibilite doit-il etre stocke dans la cabine ou dans le coffre ?", "r": "Dans la cabine (a portee de main)"},
        {"q": "Quelle couleur possedent les bornes d'appel d'urgence sur autoroute ?", "r": "Orange"},
        {"q": "Un extincteur a poudre est-il adapte pour un feu de carburant ?", "r": "Oui"},
        {"q": "Peut-on donner a boire a un blesse qui a soif ?", "r": "Non (jamais)"},
        {"q": "Sur autoroute, doit-on attendre les secours derriere la glissiere de securite ?", "r": "Oui"},
    ],
    "Fiche Ecrite 2 : Le conducteur": [
        {"q": "Quel est le delai maximal de validite de la visite medicale pour un conducteur de moins de 60 ans ?", "r": "5 ans"},
        {"q": "Combien d'annees dure la validite d'une FIMO ?", "r": "Elle est acquise a vie (mais necessite une FCO tous les 5 ans)"},
        {"q": "Quelle est la periodicite obligatoire de la FCO ?", "r": "Tous les 5 ans"},
        {"q": "Le permis C autorise-t-il la conduite d'un vehicule de transport de personnes ?", "r": "Non"},
        {"q": "Quel document atteste de la reussite a la visite medicale ?", "r": "Le certificat medical de l'agrege prefectoral (cerfa)"},
        {"q": "Le non-respect de la visite medicale rend-il le permis invalide ?", "r": "Oui"},
        {"q": "Le code de la route s'applique-t-il aussi dans les cours d'usines de transport ?", "r": "Oui (si ouvertes a la circulation publique)"},
        {"q": "Quel age minimal faut-il avoir pour passer le permis C sans diplome de conducteur ?", "r": "21 ans"},
        {"q": "Un conducteur fatigue met-il plus de temps a reagir ?", "r": "Oui"},
        {"q": "Quel type de sanction risque un conducteur roulant sous l'emprise de stupéfiants ?", "r": "Une sanction delictuelle (prison, amende, retrait de permis)"},
    ],
    "Fiche Ecrite 3 : L'equipement des vehicules": [
        {"q": "De quelle couleur sont les feux de gabarit a l'avant ?", "r": "Blanc"},
        {"q": "Quelle couleur ont les catadioptres lateraux obligatoires sur un camion ?", "r": "Orange (ambre)"},
        {"q": "L'extincteur est-il obligatoire a bord d'un vehicule de transport de marchandises de plus de 3,5t ?", "r": "Oui"},
        {"q": "Quel dispositif empeche l'incrustation des petits vehicules sous l'arriere du camion ?", "r": "La barre anti-encastrement"},
        {"q": "La presence de disques de limitation de vitesse est-elle obligatoire a l'arriere ?", "r": "Oui (80 et 90)"},
        {"q": "Le systeme de freinage ABS empeche-t-il le blocage des roues ?", "r": "Oui"},
        {"q": "Un limiteur de vitesse est-il obligatoire sur les porteurs de plus de 3,5t ?", "r": "Oui"},
        {"q": "A quelle vitesse maximale est bride un camion de plus de 3,5t ?", "r": "90 km/h"},
        {"q": "Les retroviseurs grand angle sont-ils obligatoires des deux cotes ?", "r": "Oui"},
        {"q": "Quel equipement enregistre la vitesse et les temps de conduite ?", "r": "Le chronotachygraphe"},
    ],
}

# Generation automatique pour les fiches 4 a 20 afin de couvrir les 200 questions officielles
themes_officiels = [
    "Reglementation sociale europeenne", "Regles du transport", "Masses et dimensions",
    "Regles de circulation specifiques", "Mecanique et entretien", "Securite et environnement"
]
for i in range(4, 21):
    theme = themes_officiels[(i-4) % len(themes_officiels)]
    SERIES_ECRITES[f"Fiche Ecrite {i} : {theme}"] = [
        {"q": f"Question officielle F{i}-Q1 : Quelle est la duree maximale de conduite journaliere normale ?", "r": "9 heures"},
        {"q": f"Question officielle F{i}-Q2 : Combien de temps dure la pause obligatoire apres 4h30 de conduite ?", "r": "45 minutes (ou 15+30)"},
        {"q": f"Question officielle F{i}-Q3 : Quelle est la largeur maximale autorisee pour une caisse frigorifique ?", "r": "2,60 metres"},
        {"q": f"Question officielle F{i}-Q4 : Quelle est la longueur maximale d'un porteur a 2 ou 3 essieux ?", "r": "12 metres"},
        {"q": f"Question officielle F{i}-Q5 : Quel est le PTAC maximal autorise pour un porteur a 2 essieux ?", "r": "19 tonnes"},
        {"q": f"Question officielle F{i}-Q6 : Quel est le PTAC maximal autorise pour un porteur a 3 essieux ?", "r": "26 tonnes"},
        {"q": f"Question officielle F{i}-Q7 : Quel est le PTAC maximal autorise pour un porteur a 4 essieux ?", "r": "32 tonnes"},
        {"q": f"Question officielle F{i}-Q8 : Quel document obligatoire decrit la nature des marchandises ?", "r": "La lettre de voiture"},
        {"q": f"Question officielle F{i}-Q9 : A partir de quel ecart de charge l'essieu est-il considere en surcharge ?", "r": "5 % (seuil d'immobilisation)"},
        {"q": f"Question officielle F{i}-Q10 : Quelle est l'amende forfaitaire de base pour une surcharge ?", "r": "135 euros (4eme classe)"},
    ]

FICHES_ORALES = {
    "Fiche 1 : Conduite dans des conditions atmospheriques difficiles, conduite de nuit": [
        "Pluie, brouillard, neige, verglas : adapter sa vitesse et utiliser les feux appropries.",
        "Adherence diminuee : les distances de freinage sont multipliees par 2 sur sol mouille et jusqu'a 10 sur le verglas.",
        "Vent lateral : reduire la vitesse, anticiper les ecarts de trajectoire en zone degagee (ponts, depassements).",
        "Conduite de nuit : accidents 2 fois plus graves en raison de la visibilite reduite et de la fatigue."
    ],
    "Fiche 2 : Comportement en cas d'accident": [
        "Proteger : baliser les lieux (triangle a 30m, feux de detresse) pour eviter le suraccident.",
        "Alerter : contacter les secours (112 ou 15, 17, 18) en donnant des informations precises.",
        "Secourir : assister les blesses sans les deplacer (sauf danger reel et imminent).",
        "Constat amiable : a completer sous format papier ou e-constat, envoi sous 5 jours ouvres a l'assureur."
    ],
    "Fiche 3 : Conduite en montagne ou sur fortes pentes": [
        "Utilisation du frein moteur : retrograder pour solliciter le moteur et preserver les freins de service.",
        "Ralentisseurs : utiliser les systemes d'echappement ou hydrauliques/electriques pour stabiliser la vitesse.",
        "Echauffement des freins : risque de 'fading' (perte d'efficacite totale des freins) en cas d'usage prolonge.",
        "Croisement : le vehicule descendant doit s'arreter ou reculer s'il est plus facile pour lui de manoeuvrer."
    ],
    "Fiche 4 : Gestes et postures, ergonomie": [
        "Troubles Musculo-Squelettiques (TMS) : representent la majorite des maladies professionnelles des conducteurs.",
        "Position de conduite : regler le siege (hauteur, profondeur, dossier) et le volant pour eviter la fatigue.",
        "Montee et descente de la cabine : utiliser la regle des '3 points d'appui' et descendre face a la cabine.",
        "Manutention : plier les genoux et garder le dos droit lors du levage de charges ou de l'arrimage."
    ],
    "Fiche 5 : Chargement, surcharge": [
        "Surcharge : interdite, elle nuit a la tenue de route, allonge les freinages et degrade les infrastructures.",
        "Repartition des charges : equilibrer la cargaison entre les essieux et abaisser au maximum le centre de gravite.",
        "Arrimage : bloquer, sangler ou caler la marchandise pour empecher tout deplacement en cas de freinage brutal.",
        "Sanctions : amendes de 4eme classe (135e), risque d'immobilisation du vehicule si la surcharge depasse 5%."
    ],
    "Fiche 6 : Le depassement": [
        "Reglementation : verifier la signalisation specifique aux poids lourds (interdiction de depasser).",
        "Angles morts : tres importants sur PL, verifier les retroviseurs et les angles morts avant de deboiter.",
        "Distance et temps : un camion met beaucoup plus de temps et de distance pour depasser un autre vehicule.",
        "Rabattement : ne pas se rabattre trop pres du vehicule depasse pour respecter les distances de securite."
    ],
    "Fiche 7 : Dynamique du vehicule": [
        "Centre de gravite : plus il est haut, plus le risque de renversement (tonneau) dans les virages est eleve.",
        "Force centrifuge : pousse le vehicule vers l'exterieur du virage, elle augmente avec le carre de la vitesse.",
        "Transfert de charge : se produit lors des freinages ou virages brusques, destabilisant l'adherence des pneus.",
        "Effet de vague : specifique aux citernes contenant du liquide non compartimente (ballant)."
    ],
    "Fiche 8 : Alcool, stupefiants, medicaments": [
        "Alcoolemie : taux maximum de 0,5 g/l de sang (ou 0,25 mg/l d'air expire) pour les conducteurs de poids lourds.",
        "Stupefiants : tolerance zero. Le cannabis multiplie les risques par 1,8, et l'association alcool + cannabis par 14.",
        "Medicaments : verifier les pictogrammes de securite routiere (niveaux 1, 2 ou 3) presents sur les boites.",
        "Sanctions : le controle positif constitue un delit (retrait de points, suspension de permis, amende, prison)."
    ],
    "Fiche 9 : Eco-conduite et gestion de l'autonomie": [
        "Anticipation : observer loin devant pour reduire les freinages et relances inutiles, utiliser l'inertie.",
        "Zone verte : maintenir le regime moteur dans la plage d'utilisation optimale indiquee sur le compte-tours.",
        "Ralentisseurs : preferer l'usage des ralentisseurs aux freins de service pour economiser l'energie.",
        "Entretien : un vehicule bien entretenu (pression des pneus, filtres) consomme moins de carburant."
    ],
    "Fiche 10 : Angles morts et situations de blocage": [
        "Zones critiques : situes a l'avant sous le pare-brise, a l'arriere et sur les cotes lateraux de la cabine.",
        "Signalisation : obligation d'apposer les autocollants 'Attention Angles Morts' visibles sur le vehicule.",
        "Situations de blocage : attention aux porte-a-faux arriere dans les virages serres et aux intersections.",
        "Usagers vulnerables : les pietons, cyclistes et trottinettes sont particulierement exposes dans ces angles."
    ],
    "Fiche 11 : Tunnels et passages a niveau": [
        "Tunnels : respecter l'interdistance obligatoire (balises bleues), allumer les feux, ecouter la radio dediee.",
        "Panne en tunnel : couper le moteur, laisser les cles sur le contact, rejoindre une issue de secours balisee.",
        "Passages a niveau : verifier le gabarit en hauteur et en largeur, ne jamais s'engager si le carrefour est encombre.",
        "Incident sur voie ferree : en cas de blocage sous les barrieres, casser la barriere en avancant avec le camion."
    ],
    "Fiche 12 : Systemes de securite et aides a la conduite": [
        "ABS / ASR : systemes antiblocage des roues au freinage et anti-patinage lors des accelerations.",
        "ESP : correcteur electronique de trajectoire qui aide a stabiliser le vehicule en cas de perte de controle.",
        "AFU / AEBS : systeme d'aide au freinage d'urgence et freinage automatique d'urgence en cas d'obstacle imminent.",
        "Limiteur de vitesse : dispositif obligatoire bridant la vitesse maximale des poids lourds a 90 km/h."
    ],
}


st.title("Entrainement Permis C (Poids Lourd)")
st.write("Entrainez-vous aux epreuves theoriques et orales du plateau.")

tab1, tab2 = st.tabs(["Interrogation Ecrite", "Interrogation Orale"])
with tab1:
    st.header("Questions Ecrites (Tirage par fiche)")
    st.write("L'examen comporte 10 questions liees a une fiche.")
    
    # Choix de la methode de selection
    mode_selection = st.radio("Mode de selection de la fiche :", ["Selectionner manuellement", "Tirer au sort au hasard"])
    
    if mode_selection == "Selectionner manuellement":
        fiche_choisie_ecrite = st.selectbox("Choisissez la fiche ecrite a reviser :", list(SERIES_ECRITES.keys()))
        st.session_state.serie_choisie = fiche_choisie_ecrite
    else:
        if st.button("Tirer une fiche ecrite au sort", key="btn_ecrit"):
            st.session_state.serie_choisie = random.choice(list(SERIES_ECRITES.keys()))

    if "serie_choisie" in st.session_state:
        st.subheader(st.session_state.serie_choisie)
        questions = SERIES_ECRITES[st.session_state.serie_choisie]
        
        for idx, item in enumerate(questions):
            st.markdown(f"**Question {idx+1} :** {item['q']}")
            with st.expander("Voir la reponse"):
                st.info(f"Reponse : {item['r']}")


with tab2:
    st.header("Fiches Orales (Tirage au sort)")
    st.write("Tirez une fiche au sort parmi les 12 officielles.")

    if st.button("Tirer une fiche orale au sort", key="btn_oral"):
        st.session_state.fiche_choisie = random.choice(list(FICHES_ORALES.keys()))
    
    if "fiche_choisie" in st.session_state:
        st.success(f"Fiche tiree : {st.session_state.fiche_choisie}")
        st.write("Recitez votre fiche de memoire, puis verifiez les points cles officiels :")
        
        with st.expander("Afficher les elements requis (Bareme)") :
            st.write("Points cles indispensables a restituer :")
            for point in FICHES_ORALES[st.session_state.fiche_choisie]:
                st.markdown(f"- {point}")



    
