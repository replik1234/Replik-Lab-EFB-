import streamlit as st
import hashlib
import datetime
import pandas as pd
import time

# ==============================================================================
# CONFIGURATION DE LA PAGE & CHARTE GRAPHIQUE REPLIK (SLIDES LAB EFB)
# ==============================================================================
st.set_page_config(
    page_title="CABINET REPLIK | Plus vite que la viralité",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    /* Couleurs officielles du deck Replik : Marine #0f1226, Rose #e61e6e, Violet #7c3aed */
    .replik-banner {
        background: linear-gradient(135deg, #0f1226 0%, #1e1b4b 60%, #e61e6e 100%);
        padding: 24px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .step-badge {
        background-color: #7c3aed;
        color: white;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: bold;
    }
    .hash-cert {
        font-family: 'Courier New', monospace;
        background-color: #0f1226;
        color: #10b981;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #e61e6e;
        font-size: 0.88em;
        line-height: 1.5;
    }
    .kpi-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-top: 4px solid #e61e6e;
        padding: 14px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# BASE DE DONNÉES DES 10 FAUX SIGNALEMENTS (SLIDE 18 - BANC DE TEST BÊTA)
# ==============================================================================
DIX_SIGNALEMENTS = [
    {
        "id": "SIG-01",
        "titre": "1. Deepfake pornographique (Affaire type CFake)",
        "client": "Clara M. (Étudiante, 22 ans)",
        "profil": "P1 Particulier (ou Réaction directe)",
        "plateforme": "Telegram & Site tube hébergé en UE",
        "url": "https://t.me/leak_fr_chan/98234",
        "jours_depuis_pub": 3,
        "auteur_identifie": False,
        "nuit_weekend": True,
        "description": "Montage photo/vidéo hypertruqué (deepfake sexuel) utilisant le visage de la cliente sans son consentement, accompagné de son vrai prénom et de son université.",
        "ia_qualification": "Montage à caractère sexuel sans consentement / Deepfake (Art. 226-8-1 du Code pénal : 2 ans d'emprisonnement et 60 000 € d'amende, porté à 3 ans et 75 000 € en ligne).",
        "ia_traite_auto": "Extraction métadonnées, empreinte SHA-256 locale, pré-remplissage du signalement prioritaire DSA (Art. 16) + Pharos, activation veille 7 jours anti-republication.",
        "renvoi_avocat": "Validation d'urgence par l'avocat de permanence (<15 min) : choix du constat R3 (Commissaire 24/7) et dépôt de plainte pénale au procureur (J2B) avec demande de réquisition IP.",
        "recommandation_r": "R3 Preuve authentique (320 € HT) + Majoration Nuit/WE (+150 € HT)",
        "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT - Constat R3 inclus)"
    },
    {
        "id": "SIG-02",
        "titre": "2. Raid de faux avis Google contre une clinique (Dénigrement)",
        "client": "SAS Clinique Esthétique Lumière",
        "profil": "P3 Entreprise — Niveau 2 Preuve (299 € HT/mois)",
        "plateforme": "Google Maps / Fiche Établissement",
        "url": "https://maps.google.com/reviews/clinique_lumiere_raid88",
        "jours_depuis_pub": 14,
        "auteur_identifie": False,
        "nuit_weekend": False,
        "description": "Publication coordonnée de 12 avis 1 étoile en 2 heures : 'Clinique insalubre, produits périmés, la directrice falsifie ses diplômes et escroque les patients !'",
        "ia_qualification": "Dénigrement commercial fautif (Art. 1240 C. civ.) + Diffamation publique (Art. 29 et 32 Loi du 29 juillet 1881) + Pratique commerciale trompeuse.",
        "ia_traite_auto": "Détection d'anomalie statistique (bot/ferme à clics), capture horodatée R2 (incluse dans P3 Niveau 2), génération du rapport d'illicéité DSA pour Google Ireland.",
        "renvoi_avocat": "Arbitrage stratégique avocat : privilégier l'Art. 1240 C. civ. (dénigrement des produits) ou la Loi de 1881 (diffamation sur les diplômes) et rédiger la mise en demeure + référé retrait (R4 à -15%).",
        "recommandation_r": "R4 Retrait judiciaire (1 700 € HT avec remise -15% abonné P3 Niv. 2)",
        "recommandation_j": "J1 Justice civile (2 800 à 5 150 € HT - Dommages-intérêts)"
    },
    {
        "id": "SIG-03",
        "titre": "3. Voix clonée par IA d'un influenceur (Arnaque financière)",
        "client": "Lucas 'SkyVibe' (Créateur de contenu, 800k abonnés)",
        "profil": "P2 Personnalité — Niveau 3 Justice (449 € HT/mois)",
        "plateforme": "TikTok & Instagram Reels",
        "url": "https://tiktok.com/@skyvibe_officiel_crypto/video/778899",
        "jours_depuis_pub": 1,
        "auteur_identifie": False,
        "nuit_weekend": True,
        "description": "Vidéo sponsorisée utilisant un clone vocal IA et le visage de l'influenceur pour promouvoir une fausse plateforme d'investissement financier.",
        "ia_qualification": "Atteinte à la représentation de la personne / Hypertrucage vocal (Art. 226-8 et 226-8-1 C. pén.) + Usurpation d'identité numérique (Art. 226-4-1 C. pén.).",
        "ia_traite_auto": "Détection biométrique/vocale par l'IA du prestataire, figeage SHA-256 par l'IA locale, préparation du dossier de notification d'urgence Meta & TikTok.",
        "renvoi_avocat": "Coordination immédiate avec l'équipe de communication du VIP (éviter l'effet Streisand), mobilisation d'un des 2 constats de commissaire inclus dans P2 Niv. 3 et plainte pénale.",
        "recommandation_r": "Inclus dans l'abonnement P2 Niveau 3 (+20 € HT intervention nuit/WE)",
        "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "SIG-04",
        "titre": "4. Diffusion d'images intimes par un ex-conjoint (Revenge Porn)",
        "client": "Sarah L. (Particulier, 27 ans)",
        "profil": "P1 Particulier — Réaction immédiate",
        "plateforme": "Instagram & Groupe WhatsApp",
        "url": "https://instagram.com/p/revenge_post_8821",
        "jours_depuis_pub": 2,
        "auteur_identifie": True,
        "nuit_weekend": True,
        "description": "L'ex-compagnon (identifié) a publié des photographies intimes prises du temps de la vie commune sur un compte public en identifiant les collègues de la victime.",
        "ia_qualification": "Diffusion non consentie d'images à caractère sexuel / Revenge Porn (Art. 226-2-1 du Code pénal : 2 ans d'emprisonnement et 60 000 € d'amende).",
        "ia_traite_auto": "Traitement 100% en IA locale (0 exposition externe des clichés intimes), empreinte numérique SHA-256 sans stockage cloud tiers, notification de retrait immédiat.",
        "renvoi_avocat": "Auteur formellement identifié : l'avocat valide le constat R3 par commissaire d'astreinte et prépare une Citation Directe (J2A) pour obtenir condamnation et réparation à la même audience.",
        "recommandation_r": "R3 Preuve authentique (320 € HT) + Nuit/WE (+150 € HT)",
        "recommandation_j": "J2A Citation directe devant le Tribunal correctionnel (2 700 à 4 200 € HT)"
    },
    {
        "id": "SIG-05",
        "titre": "5. Cyberharcèlement en meute et Doxxing (Adresse divulguée)",
        "client": "Mehdi K. (Journaliste indépendant)",
        "profil": "P1 Particulier — Niveau 2 Preuve (39 € HT/mois)",
        "plateforme": "X (Twitter)",
        "url": "https://x.com/raid_thread/status/189273645",
        "jours_depuis_pub": 5,
        "auteur_identifie": False,
        "nuit_weekend": False,
        "description": "Publication de l'adresse personnelle et du téléphone de la victime avec appel au raid : 'Allez tous l'attendre en bas de chez lui ce soir !'",
        "ia_qualification": "Mise en danger par révélation d'informations personnelles / Doxxing (Art. 223-1-1 C. pén.) + Cyberharcèlement en meute (Art. 222-33-2-2 C. pén.).",
        "ia_traite_auto": "Agrégation automatique des 45 tweets du raid en un seul dossier chronologique horodaté SHA-256, génération des signalements groupés X Corp.",
        "renvoi_avocat": "Évaluation du péril physique immédiat, saisine du Pôle national de lutte contre la haine en ligne (PNLHL) et demande de protection.",
        "recommandation_r": "Inclus dans P1 Niveau 2 (6 signalements et captures horodatées inclus/mois)",
        "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "SIG-06",
        "titre": "6. Tweet diffamatoire d'un concurrent identifié contre un dirigeant",
        "client": "Jean-Marc V. (PDG de FinTech)",
        "profil": "P3 Entreprise — Niveau 1 Veille (229 € HT/mois)",
        "plateforme": "LinkedIn & X",
        "url": "https://linkedin.com/posts/concurrent_diffamation_992",
        "jours_depuis_pub": 45,
        "auteur_identifie": True,
        "nuit_weekend": False,
        "description": "Post public d'un concurrent nommé affirmant que le dirigeant a détourné les fonds de l'URSSAF et fait l'objet d'une interdiction de gérer.",
        "ia_qualification": "Diffamation publique envers une personne physique/morale (Art. 29 al. 1 et 32 Loi du 29 juillet 1881).",
        "ia_traite_auto": "Calcul du délai de prescription de 3 mois (reste 45 jours), capture probatoire et extraction des mentions légales de l'auteur.",
        "renvoi_avocat": "Rigueur procédurale absolue de la Loi de 1881 (articulation précise des faits, qualification, visa des textes et élection de domicile) : rédaction par l'avocat d'une plainte avec constitution de partie civile (J2C) pour interrompre la prescription.",
        "recommandation_r": "R3 Preuve authentique (250 € HT tarif abonné P3 Niv. 1)",
        "recommandation_j": "J2C Partie civile directe devant le juge d'instruction (3 800 à 7 200 € HT)"
    },
    {
        "id": "SIG-07",
        "titre": "7. Usurpation d'identité d'un élu local en campagne",
        "client": "Hélène R. (Maire / Personnalité politique)",
        "profil": "P2 Personnalité — Niveau 2 Preuve (349 € HT/mois)",
        "plateforme": "Facebook & TikTok",
        "url": "https://facebook.com/profile.php?id=1000998877_fake_maire",
        "jours_depuis_pub": 4,
        "auteur_identifie": False,
        "nuit_weekend": False,
        "description": "Création d'une page imitant la charte officielle de la candidate et diffusant de fausses déclarations polémiques à 3 semaines d'un scrutin.",
        "ia_qualification": "Usurpation d'identité numérique (Art. 226-4-1 C. pén.) + Manœuvre frauduleuse électorale (Art. L. 97 du Code électoral).",
        "ia_traite_auto": "Détection du faux profil par veille d'image, capture horodatée incluse, préparation de la mise en demeure Meta Platforms Ireland.",
        "renvoi_avocat": "Rédaction de l'assignation en référé d'heure à heure devant le Tribunal Judiciaire sous astreinte (R4 avec remise -15%).",
        "recommandation_r": "R4 Retrait judiciaire (1 700 € HT avec remise -15% abonné P2 Niv. 2)",
        "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "SIG-08",
        "titre": "8. Chantage à la webcam (Sextorsion financière)",
        "client": "Thomas B. (Particulier, 19 ans)",
        "profil": "Réaction directe (Cible principale)",
        "plateforme": "Instagram DM & Discord",
        "url": "https://discord.com/channels/extorsion_id_445",
        "jours_depuis_pub": 1,
        "auteur_identifie": False,
        "nuit_weekend": True,
        "description": "Menace imminente de diffuser une vidéo intime à tous les abonnés Instagram de la victime si un virement de 800 € n'est pas effectué dans l'heure.",
        "ia_qualification": "Chantage (Art. 312-10 du Code pénal : 5 ans d'emprisonnement et 75 000 € d'amende) + Tentative d'extorsion.",
        "ia_traite_auto": "Génération immédiate de l'accusé horodaté, figeage des captures de conversation et des identifiants du maître-chanteur, consignes d'urgence (ne pas payer, ne pas supprimer le compte).",
        "renvoi_avocat": "Prise de relais psychologique et juridique immédiate par l'avocat de permanence 24/7, blocage préventif des comptes hôtes et plainte pénale.",
        "recommandation_r": "R2 Preuve horodatée (150 € HT) + Nuit/WE (+75 € HT)",
        "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT)"
    },
    {
        "id": "SIG-09",
        "titre": "9. Article diffamatoire publié il y a 105 jours (Prescription 1881 dépassée !)",
        "client": "Cabinet d'Architecture Horizon",
        "profil": "Réaction directe",
        "plateforme": "Blog d'urbanisme local",
        "url": "https://blog-archi-critique.fr/horizon-corruption",
        "jours_depuis_pub": 105,
        "auteur_identifie": True,
        "nuit_weekend": False,
        "description": "Article accusant le cabinet d'architecture de malfaçons volontaires et de pots-de-vin, publié il y a 3 mois et demi (105 jours).",
        "ia_qualification": "ALERTE IA LOCALE : Prescription de 3 mois (Art. 65 Loi du 29 juillet 1881) ACQUISE (105 jours > 90 jours) ! Irrécevabilité sur le terrain de la diffamation.",
        "ia_traite_auto": "Calcul mathématique de l'échéance de prescription et blocage automatique des modèles d'actes 'Loi 1881' pour éviter toute faute professionnelle.",
        "renvoi_avocat": "Haute valeur ajoutée de l'avocat : requalification sur le terrain du dénigrement commercial (Art. 1240 C. civ. — prescription de 5 ans) pour contourner légalement la prescription de 3 mois si la critique vise les prestations de l'entreprise.",
        "recommandation_r": "R2 Preuve horodatée (150 € HT) + Mise en demeure",
        "recommandation_j": "J1 Justice civile sur le fondement de l'Art. 1240 C. civ. (2 800 à 5 150 € HT)"
    },
    {
        "id": "SIG-10",
        "titre": "10. Harcèlement scolaire visant l'enfant d'une personnalité (Option Pack Proches)",
        "client": "Enfant mineur de Mme Claire D. (Dirigeante / VIP)",
        "profil": "P2 Personnalité + Option Pack Proches (+39 € HT/mois)",
        "plateforme": "Snapchat & TikTok",
        "url": "https://tiktok.com/@college_clash_92/video/112233",
        "jours_depuis_pub": 2,
        "auteur_identifie": True,
        "nuit_weekend": False,
        "description": "Vidéo humiliante filmée devant l'établissement scolaire et repartagée sur plusieurs comptes secondaires (miroirs).",
        "ia_qualification": "Harcèlement scolaire et cyberharcèlement sur mineur (Art. 222-33-2-3 du Code pénal) + Atteinte au droit à l'image d'un mineur (Art. 226-1 C. pén.).",
        "ia_traite_auto": "Détection de la vidéo originale et de 4 republications miroirs, horodatage certifié et signalement prioritaire Protection des Mineurs.",
        "renvoi_avocat": "Intervention auprès des représentants légaux, notification chef d'établissement et mise en demeure / retrait sous 24h.",
        "recommandation_r": "Couvert par l'Option Pack Proches (39 € HT/mois) de la formule P2",
        "recommandation_j": "J2B Plainte au procureur ou médiation pénale (700 à 1 000 € HT)"
    }
]

# Initialisation de l'état de session
if "selected_case" not in st.session_state:
    st.session_state.selected_case = DIX_SIGNALEMENTS[0]
if "dossier_cree" not in st.session_state:
    st.session_state.dossier_cree = False
if "avocat_valide" not in st.session_state:
    st.session_state.avocat_valide = False

# ==============================================================================
# BARRE LATÉRALE : ARCHITECTURE DOUBLE IA & ENGAGEMENTS (SLIDES 13, 17, 18)
# ==============================================================================
with st.sidebar:
    st.markdown("## 🛡️ CABINET REPLIK")
    st.caption("« La rigueur juridique, à la vitesse d'Internet. »")
    st.divider()
    
    st.markdown("### 🖥️ Architecture Souveraine")
    st.success("🟢 **IA Prestataire (Veille Web)**\nOpérateur certifié & hébergé en France")
    st.info("🔐 **IA Locale du Cabinet + n8n Local**\n0 donnée sensible envoyée à une IA externe pour la qualification.")
    st.warning("⚖️ **Permanence Avocat 24h/24 - 7j/7**\n100 % des démarches validées par un avocat (Secret Pro & RCP).")
    
    st.divider()
    st.markdown("### 📊 Engagements Client (Slide 13)")
    st.markdown("""
    - **24h/24** : Avocat d'astreinte 7j/7
    - **0 €** de frais cachés (tiers inclus)
    - **100 %** validé par un avocat
    - **1 semaine** de veille dès R1
    - **0 donnée** sensible externe
    """)
    st.caption("Conservation des preuves : 5 ans (suppression sur simple demande).")

# ==============================================================================
# BANNIÈRE D'EN-TÊTE
# ==============================================================================
st.markdown("""
    <div class="replik-banner">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span class="step-badge">PROTOTYPE BÊTA — LAB EFB 2026</span>
                <h1 style="margin:8px 0 4px 0; color:white;">CABINET REPLIK — Plus vite que la viralité.</h1>
                <p style="margin:0; opacity:0.92; font-size:1.05em;">
                    <b>L'IA détecte et prépare. L'avocat décide et agit.</b> | Parcours en 5 étapes : 01 Détection → 02 Qualification → 03 Validation → 04 Action → 05 Suivi
                </p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# LES 4 ONGLETS (LES 3 ÉCRANS DE LA SLIDE 18 + LE BANC D'ESSAI DES 10 CAS)
# ==============================================================================
tab_ecran1, tab_ecran2, tab_ecran3, tab_labo = st.tabs([
    "📝 ÉCRAN 1 : Formulaire & Détection (Étapes 01-02)",
    "🔐 ÉCRAN 2 : Accusé Horodaté & Validation Avocat (Étapes 02-04)",
    "📈 ÉCRAN 3 : Suivi Client, Veille 7j & Devis (Étape 05)",
    "🧪 BANC DE TEST : Les 10 Faux Signalements & n8n (Slide 18)"
])

# ------------------------------------------------------------------------------
# ÉCRAN 1 : FORMULAIRE DE SIGNALEMENT & DÉTECTION IA (SLIDE 16 & 18)
# ------------------------------------------------------------------------------
with tab_ecran1:
    st.subheader("📝 Écran 1 : Mise en route par formulaire simple ou alerte de veille")
    st.caption("Conformément à la Slide 16 : Dès le signalement, l'IA locale fige la preuve, calcule la prescription et génère l'accusé horodaté.")
    
    col_f1, col_f2 = st.columns([1.25, 1])
    
    with col_f1:
        st.markdown("#### 1. Sélectionner un cas parmi les 10 faux signalements (Slide 18) ou saisir un cas")
        titres_cas = [c["titre"] for c in DIX_SIGNALEMENTS] + ["➕ Saisie libre d'un nouveau signalement en direct"]
        choix_titre = st.selectbox("Banc de test Replik :", titres_cas)
        
        if choix_titre != "➕ Saisie libre d'un nouveau signalement en direct":
            cas_actif = next(c for c in DIX_SIGNALEMENTS if c["titre"] == choix_titre)
        else:
            cas_actif = {
                "id": "SIG-LIVE",
                "titre": "Signalement en direct Jury EFB",
                "client": "Client Test Jury EFB",
                "profil": "Réaction directe",
                "plateforme": "X / Instagram / Google",
                "url": "https://x.com/user/status/999888777",
                "jours_depuis_pub": 5,
                "auteur_identifie": False,
                "nuit_weekend": False,
                "description": "Propos diffamatoires ou montage illicite portant atteinte à l'honneur et à l'image du client.",
                "ia_qualification": "Diffamation publique (Art. 29 Loi du 29 juillet 1881) & Atteinte à l'image.",
                "ia_traite_auto": "Horodatage SHA-256 local, vérification du délai de 3 mois, préparation notification DSA.",
                "renvoi_avocat": "Vérification de la qualification par l'avocat d'astreinte et signature de la mise en demeure.",
                "recommandation_r": "R2 Preuve horodatée (150 € HT)",
                "recommandation_j": "J2B Plainte au procureur (700 à 1 000 € HT)"
            }

        nom_client = st.text_input("Identité du client / Victime :", value=cas_actif["client"])
        profil_client = st.selectbox(
            "Catégorie de cible / Abonnement Prévention :",
            [
                "Cible Principale : Particulier non abonné (Formule Réaction à l'acte)",
                "Abonné P1 Particulier — Niveau 1 Veille (29 € HT/mois)",
                "Abonné P1 Particulier — Niveau 2 Preuve (39 € HT/mois)",
                "Abonné P1 Particulier — Niveau 3 Justice (59 € HT/mois)",
                "Abonné P2 Personnalité — Niveau 1 Veille (249 € HT/mois)",
                "Abonné P2 Personnalité — Niveau 2 Preuve (349 € HT/mois)",
                "Abonné P2 Personnalité — Niveau 3 Justice (449 € HT/mois)",
                "Abonné P3 Entreprise — Niveau 1 Veille (229 € HT/mois)",
                "Abonné P3 Entreprise — Niveau 2 Preuve (299 € HT/mois)",
                "Abonné P3 Entreprise — Niveau 3 Justice (369 € HT/mois)"
            ],
            index=0
        )
        
        c_plat, c_url = st.columns(2)
        with c_plat:
            plateforme_input = st.text_input("Plateforme concernée :", value=cas_actif["plateforme"])
        with c_url:
            url_input = st.text_input("URL exacte du contenu :", value=cas_actif["url"])
            
        c_date, c_aut, c_nuit = st.columns(3)
        with c_date:
            date_pub = st.date_input(
                "Date de 1re publication :",
                value=datetime.date.today() - datetime.timedelta(days=cas_actif["jours_depuis_pub"])
            )
        with c_aut:
            auteur_connu = st.checkbox("Auteur déjà identifié ?", value=cas_actif["auteur_identifie"])
        with c_nuit:
            nuit_we = st.checkbox("Urgence Nuit / WE / Férié ?", value=cas_actif["nuit_weekend"])
            
        contenu_input = st.text_area(
            "Description ou transcription du contenu litigieux (traité par l'IA locale du cabinet) :",
            value=cas_actif["description"],
            height=110
        )
        
        if st.button("🚨 DÉCLENCHER LE WORKFLOW n8n LOCAL & GÉNÉRER L'ACCUSÉ HORODATÉ", type="primary", use_container_width=True):
            with st.spinner("Exécution du workflow n8n en local : capture serveur, hachage SHA-256 et pré-qualification juridique..."):
                time.sleep(0.9)
                horodatage_utc = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                chaine_preuve = f"REPLIK_LOCAL|{nom_client}|{url_input}|{horodatage_utc}|{contenu_input}"
                empreinte_sha256 = hashlib.sha256(chaine_preuve.encode("utf-8")).hexdigest()
                
                st.session_state.selected_case = cas_actif
                st.session_state.dossier_info = {
                    "id": cas_actif["id"],
                    "client": nom_client,
                    "profil": profil_client,
                    "plateforme": plateforme_input,
                    "url": url_input,
                    "date_pub": date_pub,
                    "auteur_connu": auteur_connu,
                    "nuit_we": nuit_we,
                    "contenu": contenu_input,
                    "timestamp": horodatage_utc,
                    "sha256": empreinte_sha256
                }
                st.session_state.dossier_cree = True
                st.session_state.avocat_valide = False
                st.success("✅ Dossier enregistré et preuve figée en local ! Rendez-vous sur l'**ÉCRAN 2 (Accusé Horodaté & Validation Avocat)**.")

    with col_f2:
        st.markdown("#### 2. Diagnostic temps réel de l'IA Locale (Étape 02)")
        
        # Calculateur de la prescription de 3 mois (Loi du 29 juillet 1881 - Slide 3)
        jours_ecoules = (datetime.date.today() - date_pub).days
        jours_restants = 90 - jours_ecoules
        date_butoir = date_pub + datetime.timedelta(days=90)
        
        if jours_restants > 15:
            st.success(f"⏱️ **Compteur Loi du 29 juillet 1881 (3 mois) :**\nIl reste **{jours_restants} jours** pour agir (Date butoir : {date_butoir.strftime('%d/%m/%Y')}).")
        elif jours_restants > 0:
            st.warning(f"⚠️ **ALERTE PRESCRIPTION IMMINENTE :**\nPlus que **{jours_restants} jours** avant prescription de l'action presse !")
        else:
            st.error(f"🚨 **PRESCRIPTION DE 3 MOIS DÉPASSÉE ({jours_ecoules} jours) !**\nL'IA locale bloque automatiquement les actes fondés sur la Loi de 1881 et renvoie à l'avocat pour basculer sur le droit commun (Art. 1240 C. civ. — 5 ans).")
            
        st.markdown("##### 🤖 Répartition IA Locale vs Avocat (Slide 17 & 18)")
        st.info(f"**Ce que l'IA locale traite automatiquement :**\n{cas_actif['ia_traite_auto']}")
        st.warning(f"**Ce que l'IA renvoie obligatoirement à l'avocat de permanence :**\n{cas_actif['renvoi_avocat']}")
        
        st.markdown("##### 💡 Pré-qualification juridique proposée par l'IA locale :")
        st.write(cas_actif["ia_qualification"])

# ------------------------------------------------------------------------------
# ÉCRAN 2 : ACCUSÉ HORODATÉ & VALIDATION AVOCAT 24/7 (SLIDES 16, 17, 18)
# ------------------------------------------------------------------------------
with tab_ecran2:
    st.subheader("🔐 Écran 2 : Accusé Horodaté Certifié & Validation par l'Avocat de Permanence")
    
    if not st.session_state.dossier_cree:
        st.info("👆 Cliquez d'abord sur le bouton **« Déclencher le workflow n8n local »** dans l'Écran 1 pour générer l'accusé horodaté.")
    else:
        d = st.session_state.dossier_info
        c = st.session_state.selected_case
        
        col_acc, col_av = st.columns([1.1, 1])
        
        with col_acc:
            st.markdown("#### 1. Accusé Horodaté Envoyé au Client (Slide 16 & 18)")
            st.markdown(f"""
            <div class="hash-cert">
                <b>🛡️ CERTIFICAT D'HORODATAGE & DE FIGEAGE PROBATOIRE — CABINET REPLIK</b><br>
                -------------------------------------------------------------------------<br>
                <b>RÉFÉRENCE DOSSIER :</b> {d['id']} | <b>CLIENT :</b> {d['client']}<br>
                <b>HORODATAGE CERTIFIÉ :</b> {d['timestamp']}<br>
                <b>SERVEUR D'EXÉCUTION :</b> Instance IA Locale Replik (Hébergement France - 0 Cloud Externe)<br>
                <b>URL DU CONTENU FIGÉ :</b> {d['url']}<br>
                <b>EMPREINTE SHA-256 INALTÉRABLE :</b><br>
                {d['sha256']}<br>
                <b>GARANTIE DE CONSERVATION :</b> 5 ans en coffre-fort numérique (suppression sur demande)
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown("#### 2. Choix du palier de Preuve & Réaction (Slide 20)")
            palier_choisi = st.radio(
                "Sélectionner le niveau de preuve requis :",
                [
                    "R1 Essentiel (125 € HT) — Détection, signalement plateformes, suivi & 1 sem. de veille",
                    "R2 Preuve horodatée (150 € HT) — R1 + Capture certifiée inaltérable conservée 5 ans",
                    "R3 Preuve authentique (320 € HT) — R1 + Constat de Commissaire de justice d'astreinte 24h/24",
                    "R4 Retrait judiciaire (1 700 à 2 650 € HT) — Mise en demeure + Référé devant le TJ sous astreinte"
                ],
                index=1
            )
            
        with col_av:
            st.markdown("#### 3. Étape 03 : Validation par l'Avocat de Permanence 24h/24")
            st.markdown("""
            > **Garantie Déontologique (Slide 13 & 17) :** *100 % des démarches sont validées par un avocat. Nous promettons des moyens, jamais un résultat.*
            """)
            
            avocat_signataire = st.selectbox(
                "Avocat d'astreinte connecté :",
                [
                    "Me. Associé Pénal & Presse (Permanence 24/7 - Barreau de Paris)",
                    "Me. Associé Référés & Numérique (Permanence 24/7 - Barreau de Paris)"
                ]
            )
            
            modele_acte = st.selectbox(
                "Modèle d'acte pré-rédigé par l'IA locale (Slide 18) :",
                [
                    "Acte 1 : Notification formelle de retrait aux plateformes (DSA Art. 16 & LCEN Art. 6-I-5) [R1/R2/R3]",
                    "Acte 2 : Mise en demeure d'avocat & Projet d'assignation en référé sous astreinte [R4]",
                    "Acte 3 : Plainte pénale au Procureur / Citation directe / Partie civile [Gamme Justice J2A/J2B/J2C]"
                ]
            )
            
            amendement_avocat = st.text_area(
                "Contrôle & observations de l'avocat avant signature :",
                value=f"Qualification vérifiée : {c['ia_qualification']} Délai de prescription contrôlé. Envoi immédiat.",
                height=95
            )
            
            valider_box = st.checkbox("✅ En qualité d'avocat de permanence, je valide la qualification juridique et j'engage la démarche sous ma signature professionnelle.")
            
            if valider_box:
                st.session_state.avocat_valide = True
                st.success("✅ Acte déverrouillé et signé ! Consultez l'acte ci-dessous ou passez à l'**ÉCRAN 3 (Suivi Client & Devis)**.")

        if st.session_state.avocat_valide:
            st.divider()
            st.markdown("#### 📄 Acte Juridique Généré par l'IA Locale et Validé par l'Avocat (Étape 04 : Action)")
            date_str = datetime.date.today().strftime("%d/%m/%Y")
            
            texte_acte = f"""CABINET REPLIK — AVOCATS AU BARREAU DE PARIS
Permanence Cyber-Urgence 24h/24 & 7j/7 | Signataire : {avocat_signataire}
Référence Dossier : {d['id']} | Client : {d['client']}

Paris, le {date_str}

OBJET : {modele_acte}
Destinataire : Département Juridique / Hébergeur de la plateforme {d['plateforme']}
URL visée : {d['url']}

Madame, Monsieur,

Le Cabinet REPLIK agit en qualité de conseil de {d['client']}.

1. CONSTATATION ET PREUVE CERTIFIÉE
En date du {d['timestamp']}, notre système de figeage probatoire souverain a constaté la diffusion à l'adresse URL {d['url']} du contenu suivant :
« {d['contenu']} »

Ce contenu a fait l'objet d'un accusé horodaté inaltérable (Empreinte SHA-256 : {d['sha256']}) conservé 5 ans conformément à nos engagements probatoires ({palier_choisi}).

2. QUALIFICATION JURIDIQUE VALIDÉE PAR L'AVOCAT DE PERMANENCE
Après contrôle humain par l'avocat soussigné, ces faits caractérisent manifestement :
{c['ia_qualification']}

Observations stratégiques de l'avocat :
{amendement_avocat}

3. MISE EN DEMEURE DE RETRAIT IMMÉDIAT & CONSERVATION DES LOGS D'IDENTIFICATION
Conformément à l'article 16 du Règlement européen sur les services numériques (DSA) et à l'article 6-I-5 de la LCEN, la connaissance de l'illicéité est formellement acquise dès réception de la présente.
Nous vous enjoignons de procéder au retrait immédiat du contenu et d'empêcher toute republication miroir, ainsi que de préserver l'intégralité des données d'identification de l'auteur (Art. 6-II LCEN) aux fins de poursuites judiciaires.

{avocat_signataire}
Acte signé électroniquement — Cabinet REPLIK"""

            st.text_area("Texte final de l'acte :", value=texte_acte, height=320)
            st.download_button("📥 Télécharger l'acte officiel (.txt)", data=texte_acte, file_name=f"REPLIK_{d['id']}_ACTE.txt")

# ------------------------------------------------------------------------------
# ÉCRAN 3 : SUIVI CLIENT, VEILLE 7 JOURS & CALCULATEUR DE FORFAITS (SLIDES 16, 18, 19-22)
# ------------------------------------------------------------------------------
with tab_ecran3:
    st.subheader("📈 Écran 3 : Suivi en Temps Réel, Veille Anti-Republication & Transparence Tarifaire")
    st.caption("Répond aux 4 besoins de la cible (Slide 10) : 1. Disparition rapide, 2. Preuve incontestable, 3. Discrétion, 4. Transparence du prix.")
    
    # Timeline des 5 étapes de la Slide 16
    st.markdown("#### 1. Avancement du dossier en 5 étapes (Slide 16)")
    cols_step = st.columns(5)
    etapes = [
        ("01 Détection", "IA Prestataire", "✅ Terminé (URL & miroirs repérés)"),
        ("02 Qualification", "IA Locale Cabinet", "✅ Terminé (Preuve SHA-256 & Actes prêts)"),
        ("03 Validation", "Avocat 24h/24", "✅ Validé" if st.session_state.avocat_valide else "⏳ En attente validation Écran 2"),
        ("04 Action", "Avocat 24h/24", "🚀 Notification envoyée" if st.session_state.avocat_valide else "⏳ Prêt pour envoi"),
        ("05 Suivi & Veille", "Client & IA", "🛡️ Veille 7 jours active (0 republication)")
    ]
    for idx, (nom_e, acteur_e, statut_e) in enumerate(etapes):
        with cols_step[idx]:
            st.markdown(f"""
            <div class="kpi-box">
                <span class="step-badge">{acteur_e}</span>
                <h5 style="margin:8px 0 4px 0;">{nom_e}</h5>
                <p style="margin:0; font-size:0.85em;">{statut_e}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    col_suivi, col_tarif = st.columns([1.1, 1])
    
    with col_suivi:
        st.markdown("#### 2. Radar de Veille Anti-Republication (1 semaine incluse dès R1 - Slide 13 & 20)")
        df_mirrors = pd.DataFrame([
            {"Date de scan": "Aujourd'hui - 10h15", "Plateforme": "URL Principale signalée", "Statut": "Notification DSA transmise", "Action Replik": "Suivi du retrait en cours"},
            {"Date de scan": "Aujourd'hui - 10h20", "Plateforme": "Google Search / Cache", "Statut": "Aucune indexation miroir", "Action Replik": "Surveillance horaire active"},
            {"Date de scan": "Aujourd'hui - 10h25", "Plateforme": "X / TikTok / Telegram", "Statut": "0 republication détectée", "Action Replik": "Empreinte hash sous veille 7j"}
        ])
        st.dataframe(df_mirrors, use_container_width=True, hide_index=True)
        
    with col_tarif:
        st.markdown("#### 3. Simulateur de Forfait Transparent (0 € de frais cachés - Slides 20 à 22)")
        famille = st.selectbox("Choisir la famille de formule :", [
            "⚡ Famille RÉACTION (R1 à R4)",
            "🔔 Famille PRÉVENTION (Abonnements P1, P2, P3)",
            "⚖️ Famille JUSTICE (Civile J1 & Pénale J2A, J2B, J2C)"
        ])
        
        if "RÉACTION" in famille:
            f_r = st.selectbox("Palier Réaction :", [
                "R1 Essentiel — 125 € HT",
                "R2 Preuve horodatée — 150 € HT",
                "R3 Preuve authentique (Commissaire 24/7 inclus) — 320 € HT",
                "R4 Retrait judiciaire (Mise en demeure + Référé) — 1 700 à 2 650 € HT"
            ])
            opt_nuit = st.checkbox("Intervention de nuit, week-end ou jour férié (+75 € HT sur R1/R2, +150 € HT sur R3)")
            prix_base = 125 if "R1" in f_r else (150 if "R2" in f_r else (320 if "R3" in f_r else 1700))
            maj = (75 if ("R1" in f_r or "R2" in f_r) else (150 if "R3" in f_r else 0)) if opt_nuit else 0
            st.metric("Total Forfait HT (Frais de tiers inclus)", f"{prix_base + maj} € HT", "Contre 300 à 450 €/h en cabinet classique")
            
        elif "PRÉVENTION" in famille:
            f_p = st.selectbox("Profil & Niveau d'abonnement :", [
                "P1 Particulier — Niv. 1 Veille (29 € HT/mois) | 2 signalements inclus",
                "P1 Particulier — Niv. 2 Preuve (39 € HT/mois) | 6 signalements + captures R2 incluses",
                "P1 Particulier — Niv. 3 Justice (59 € HT/mois) | 12 signalements + 2 constats R3/an + -25% référé",
                "P2 Personnalité — Niv. 1 Veille (249 € HT/mois) | 15 signalements inclus",
                "P2 Personnalité — Niv. 2 Preuve (349 € HT/mois) | 15 signalements + captures R2 + -15% référé",
                "P2 Personnalité — Niv. 3 Justice (449 € HT/mois) | 25 signalements + 2 constats R3/an + -25% référé",
                "P3 Entreprise — Niv. 1 Veille (229 € HT/mois) | 15 signalements + rapport mensuel",
                "P3 Entreprise — Niv. 2 Preuve (299 € HT/mois) | 15 signalements + captures R2 + -15% référé",
                "P3 Entreprise — Niv. 3 Justice (369 € HT/mois) | 25 signalements + 2 constats R3/an + -25% référé"
            ])
            pack_proches = st.checkbox("Ajouter l'Option Pack Proches sur P2 (+39 € HT/mois)")
            eng_annuel = st.checkbox("Engagement annuel (12 mois payés 10)")
            st.info("✅ Sans engagement par défaut. Frais d'IA et de plateforme 100 % inclus.")
            
        else:
            f_j = st.selectbox("Formule Justice :", [
                "J1 Justice civile (Dommages-intérêts sans plainte pénale) — 2 800 à 5 150 € HT",
                "J2A Citation directe (Auteur identifié, constat R3 inclus) — 2 700 à 4 200 € HT",
                "J2B Plainte au procureur (Auteur inconnu, constat R3 inclus) — 700 à 1 000 € HT",
                "J2C Partie civile directe (Saisine juge d'instruction, suivi 12 mois) — 3 800 à 7 200 € HT"
            ])
            st.caption("Note transparente (Slide 22) : Le constat R3 est inclus dans J2. Non inclus : consignation fixée par le juge, frais adverses et identification hors UE sur devis.")

# ------------------------------------------------------------------------------
# ONGLET 4 : BANC DE TEST DES 10 FAUX SIGNALEMENTS & WORKFLOW n8n (SLIDE 18)
# ------------------------------------------------------------------------------
with tab_labo:
    st.subheader("🧪 Banc d'Essai Bêta : Les 10 Faux Signalements & Architecture n8n Locale (Slide 18)")
    st.markdown("""
    Cet écran matérialise directement la **Slide 18 (Prototype : Du croquis à la version bêta)** :
    1. **Automatisation avec `n8n` installable en local** (cohérent avec l'IA locale du cabinet : 0 fuite de données).
    2. **Test sur 10 faux signalements** mesurant précisément **ce que l'IA traite** vs **ce qu'elle renvoie à l'avocat**.
    """)
    
    col_k1, col_k2, col_k3, col_k4 = st.columns(4)
    col_k1.metric("Signalements testés", "10 / 10", "100 % pré-qualifiés")
    col_k2.metric("Temps de préparation IA", "14 sec", "Au lieu de 2h30 avocat")
    col_k3.metric("Détection piège prescription", "100 %", "Cas n°9 bloqué avec succès")
    col_k4.metric("Données envoyées hors cabinet", "0 octet", "IA locale + n8n auto-hébergé")
    
    st.markdown("#### 📋 Tableau de mesure des 10 faux signalements (Ce que l'IA traite vs Ce qu'elle renvoie à l'avocat)")
    df_10 = pd.DataFrame([
        {
            "Réf": x["id"],
            "Scénario testé": x["titre"],
            "Délai pub.": f"{x['jours_depuis_pub']} j.",
            "Ce que l'IA locale traite seule (Automatisation)": x["ia_traite_auto"],
            "Ce que l'IA renvoie à l'Avocat (Plus-value & RCP)": x["renvoi_avocat"],
            "Formule Replik": x["recommandation_r"]
        }
        for x in DIX_SIGNALEMENTS
    ])
    st.dataframe(df_10, use_container_width=True, hide_index=True)
    
    with st.expander("⚙️ Voir l'architecture du workflow n8n local (Slide 18)"):
        st.code("""
[Webhook Formulaire / Alerte Veille Prestataire]
       │
       ▼
[Nœud n8n 1 : Capture Serveur & Hash SHA-256 Local] ──► Envoi immédiat de l'Accusé Horodaté au Client
       │
       ▼
[Nœud n8n 2 : Calculateur Prescription Loi 1881 (90 jours)]
       ├── Si > 90 jours ──► Alerte Rouge "Prescription 1881 acquise -> Bascule Art. 1240 C. civ."
       └── Si <= 90 jours ─► Compteur d'urgence activé
       │
       ▼
[Nœud n8n 3 : LLM Local (Ollama / Mistral sur serveur français du cabinet)]
       │   Prompt système : Qualification pénale/presse + Pré-remplissage des modèles d'actes
       ▼
[Nœud n8n 4 : Notification Avocat de Permanence 24/7] ──► Validation humaine obligatoire avant expédition
        """, language="text")
