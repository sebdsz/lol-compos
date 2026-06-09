# Compos LoL 5v5 — Page de référence HTML

**Date :** 2026-06-08
**Patch de référence :** 26.11 (méta juin 2026)
**Public :** groupe Platine+, rôles flex (chaque poste a un pick principal + alternatives)
**Livrable :** un fichier `compos-lol.html` autonome, ouvrable hors-ligne en double-clic.

---

## 1. Objectif

Fournir une page HTML de référence regroupant **12 compositions 5v5** réparties en 3 catégories :

- **4 compos Ultra Early** — gagner avant la 20e minute (dive, pick, pression de lane, invade).
- **4 compos Mid/Late** — pic de puissance au milieu de partie, 2-3 items (teamfight, wombo, burst, tempo objectifs).
- **4 compos Scale & Safe** — jouer la sécurité et exploser en late (hypercarry, split, poke, scalers).

Chaque compo précise les **picks** (avec alternatives flex) et le **ban absolu** = le champion qui menace le plus directement le plan de jeu de cette compo (le hard-counter à bannir en priorité).

> Note méta : picks ancrés sur le patch 26.11. Les archétypes et combos restent valables dans le temps ; ajuster les noms si un champion est nerf/buff lors d'un patch ultérieur.

---

## 2. Structure d'une carte de compo

Chaque compo est une carte contenant :

- **Nom + archétype** (tag visuel)
- **Difficulté** (Faible / Moyenne / Élevée)
- **Les 5 postes** : Top / Jungle / Mid / ADC / Support, chacun avec **pick principal + 1-2 alternatives flex**
- **Win condition** : comment on gagne concrètement
- **Power spike** : la fenêtre de minutes où on est le plus fort
- **Combo clé** : la séquence/synergie qui fait marcher la compo
- **Plan de jeu (timeline)** : 4-6 étapes horodatées (chips horaires + action), focalisées sur les objectifs pour les compos early
- **Ban absolu** : le champion à bannir en priorité + pourquoi

### Timings d'objectifs (patch 26 / saison 2026)
- 1er drake ~5:00 · **Voidgrubs 6:00** (despawn 14:45, max 6) · **héraut 15:00** (décalé depuis 14:00) · **baron 20:00**.
- **Plates de tour permanentes** (ne tombent plus à 14:00) — mais leur or **décote de -10/min dès 11:00** (cap -40) → push pour les plates avant la 11e min. Le rework tour 2026 récompense le push/split.
- Épics +15% de durabilité ; **Dragon Vengeance** stacke plus fort → le drake soul pèse davantage. Atakhan et Feats of Strength retirés (ne pas y faire référence).

---

## 3. Les 12 compositions

### Catégorie A — Ultra Early (gagner avant la 20e min)

#### A1 — Dive 6+ « All-in niveau 6 »  · Difficulté : Élevée
- **Top :** Renekton · *alt : Camille, Jax*
- **Jungle :** Xin Zhao · *alt : Nocturne, Lee Sin*
- **Mid :** Zed · *alt : Ekko, Akali*
- **ADC :** Kai'Sa · *alt : Lucian*
- **Support :** Nautilus · *alt : Leona, Rell*
- **Win condition :** dive la bot/mid dès le niveau 6, transformer les kills en objectifs et snowball avant le mid-game.
- **Power spike :** niveaux 6-9.
- **Combo clé :** engage tank (Nautilus Q hook / Leona E-Q) → Xin Zhao saute → Zed + Kai'Sa burst la cible isolée.
- **Ban absolu : Tahm Kench** — son W/R sauve la cible du dive et annule tout le gameplan d'all-in.

#### A2 — Pick / Roam « Catch & kill »  · Difficulté : Moyenne
- **Top :** Pantheon · *alt : Sett*
- **Jungle :** Elise · *alt : Nocturne*
- **Mid :** Twisted Fate · *alt : LeBlanc, Galio*
- **ADC :** Ashe · *alt : Varus*
- **Support :** Pyke · *alt : Bard, Blitzcrank*
- **Win condition :** vision + roams, chopper une cible isolée puis forcer un objectif en 5v4. *(TF = set-up/macro globale ; LeBlanc = exécution + snowball solo, elle burst la cible attrapée et fall off en late, identité early parfaite.)*
- **Power spike :** minutes 9-14 (ults globaux TF/Pantheon, roams supp).
- **Combo clé :** Ashe R / Blitz hook → Pyke ult (reset sur kill) → collapse 5v4.
- **Ban absolu : Morgana** — son Black Shield bloque hooks et engages à distance (Ashe R, Pyke/Blitz Q), neutralisant la condition de pick.

#### A3 — Lane Bully « Push & Pressure »  · Difficulté : Moyenne
- **Top :** Aurora · *alt : Renekton*
- **Jungle :** Nidalee · *alt : Graves*
- **Mid :** Lucian · *alt : Taliyah*
- **ADC :** Caitlyn · *alt : Draven*
- **Support :** Lux · *alt : Karma*
- **Win condition :** gagner les 3 lanes au CS et à la pression, prio carte → héraut → tours, fracturer avant l'arrivée des scalers.
- **Power spike :** minutes 3-12.
- **Combo clé :** poke Caitlyn + Lux pour zoner la lane → héraut vers 14 min → premières tours.
- **Ban absolu : Vladimir** — quasi imperdable en lane, scale et punit ta pression early en survivant jusqu'au late.

#### A4 — Invade « Level 1-3 cheese »  · Difficulté : Élevée
- **Top :** Jax · *alt : Camille*
- **Jungle :** Lee Sin · *alt : Xin Zhao, Nidalee*
- **Mid :** Galio · *alt : Ahri*
- **ADC :** Lucian · *alt : Kalista*
- **Support :** Rell · *alt : Leona, Nautilus*
- **Win condition :** contrôler la jungle ennemie, invade niveau 1-3, étouffer/retarder le jungler adverse, ganks répétés tôt.
- **Power spike :** minutes 2-9.
- **Combo clé :** invade lvl 3 avec lockdown (Rell/Leona) + Lee Sin → tuer le jgl ennemi → ganks en chaîne.
- **Ban absolu : Briar** — son duel précoce et son auto-sustain retournent les invades et punissent l'agression early.

---

### Catégorie B — Mid/Late (pic de puissance milieu de partie)

#### B1 — Wombo Combo « AoE engage »  · Difficulté : Moyenne
- **Top :** Malphite · *alt : Ornn*
- **Jungle :** Wukong · *alt : Sejuani, Amumu*
- **Mid :** Yasuo · *alt : Viktor, Orianna*
- **ADC :** Miss Fortune · *alt : Jinx*
- **Support :** Rell · *alt : Leona, Nautilus*
- **Win condition :** group à 5 dès 2 items, enchaîner les CC AoE et effacer les teamfights groupés.
- **Power spike :** minutes 20-30 (ults disponibles).
- **Combo clé :** Malphite R → Wukong R (knock-ups) → Yasuo R → Miss Fortune R canalisé sur la team clouée.
- **Ban absolu : Janna** — son ult de disengage (Monsoon) repousse l'engage et brise tout le wombo.

#### B2 — Burst / Pick assassins  · Difficulté : Élevée
- **Top :** Camille · *alt : Pantheon*
- **Jungle :** Nocturne · *alt : Kha'Zix*
- **Mid :** Zed · *alt : Sylas, Akali*
- **ADC :** Varus · *alt : Caitlyn*
- **Support :** Pyke · *alt : Thresh*
- **Win condition :** mid-game, lock + oneshot une cible prioritaire avec un combo d'assassins coordonné, jouer en 5v4.
- **Power spike :** minutes 15-25.
- **Combo clé :** Varus R / Camille R lock → Nocturne R → burst Zed + Pyke sur la cible.
- **Ban absolu : Lulu** — Wild Growth + polymorph annulent le burst sur la cible protégée et désamorcent les assassins.

#### B3 — Front-to-Back Bruiser  · Difficulté : Moyenne
- **Top :** Aatrox · *alt : K'Sante, Sett*
- **Jungle :** Sejuani · *alt : Vi, Xin Zhao*
- **Mid :** Orianna · *alt : Vladimir*
- **ADC :** Jinx · *alt : Aphelios*
- **Support :** Nautilus · *alt : Alistar, Leona*
- **Win condition :** front line solide + DPS sustained, gagner les teamfights mid-game autour des drakes et contrôler le drake soul.
- **Power spike :** minutes 20-30.
- **Combo clé :** Sejuani/Nautilus engage → Orianna Shockwave sur le regroupement → Jinx free DPS reset, Aatrox cleanup.
- **Ban absolu : Fiddlesticks** — son R (crowstorm + fear) efface une équipe groupée en front-to-back avant que ton DPS s'exprime.

#### B4 — Tempo / Contrôle d'objectifs  · Difficulté : Moyenne
- **Top :** Jax · *alt : Gnar*
- **Jungle :** Vi · *alt : Jarvan IV, Sejuani*
- **Mid :** Taliyah · *alt : Azir*
- **ADC :** Ezreal · *alt : Kai'Sa*
- **Support :** Bard · *alt : Rakan, Thresh*
- **Win condition :** dominer chaque set-up d'objectif via un pick, prendre tempo et drake soul en jouant les fights en 5v4.
- **Power spike :** minutes 15-28.
- **Combo clé :** Vi R lock le carry au pit de l'objectif → focus → objectif sécurisé en avantage numérique.
- **Ban absolu : Nocturne** — son R global + dash ignore ta vision et retourne tes set-ups d'objectifs.

---

### Catégorie C — Scale & Safe (sécuriser le late, exploser tard)

#### C1 — Hypercarry à protéger « Protect the Carry »  · Difficulté : Moyenne
- **Top :** Ornn · *alt : Shen*
- **Jungle :** Sejuani · *alt : Maokai*
- **Mid :** Orianna · *alt : Viktor, Syndra*
- **ADC :** Jinx · *alt : Kog'Maw, Aphelios*
- **Support :** Lulu · *alt : Milio, Janna*
- **Win condition :** survivre l'early, tout funnel sur l'ADC, atteindre 3-4 items et le protéger pour qu'il 1v9 les teamfights late. *(Orianna donne la peel + le Shockwave de teamfight ; Syndra possible comme dégâts secondaires mais on troque la peel contre du burst — il faut alors un jgl/supp qui peel les carries.)*
- **Power spike :** 30 min et plus.
- **Combo clé :** Lulu R + Orianna shield/ball sur Jinx → elle reset son DPS protégée par les 4 autres.
- **Ban absolu : Kha'Zix** — exploite l'isolement pour oneshot ton hypercarry malgré la peel.

#### C2 — Split Push 1-3-1  · Difficulté : Élevée
- **Top :** Tryndamere · *alt : Camille, Fiora*
- **Jungle :** Shyvana · *alt : Trundle*
- **Mid :** Azir · *alt : Cassiopeia*
- **ADC :** Sivir · *alt : Ezreal*
- **Support :** Tahm Kench · *alt : Galio*
- **Win condition :** étirer la map en 1-3-1, créer des side-lane threats imperdables, forcer des collapses et prendre tours/baron en cross-map.
- **Power spike :** 25 min et plus (menace de split en ligne).
- **Combo clé :** Trynda/Camille push une side et menace → l'ennemi collapse → ta team prend l'objectif en 4v3 (Galio/Tahm save à distance).
- **Ban absolu : Jax** — meilleur counter-split en 1v1, il neutralise ta menace de side lane.

#### C3 — Poke / Siège « Artillery »  · Difficulté : Moyenne
- **Top :** Jayce · *alt : Kennen*
- **Jungle :** Nidalee · *alt : Karthus*
- **Mid :** Xerath · *alt : Syndra, Ziggs, Vel'Koz*
- **ADC :** Ezreal · *alt : Varus*
- **Support :** Karma · *alt : Lux, Zilean*
- **Win condition :** poke la team ennemie sous 50% HP avant chaque fight, siéger les tours et gagner la guerre d'attrition sans s'engager. *(Xerath/Ziggs ont plus de portée pour le siège pur ; Syndra apporte en échange un vrai burst de pick QE+R que l'artillerie n'a pas.)*
- **Power spike :** minutes 18-30.
- **Combo clé :** layering du poke Xerath + Jayce + Ezreal → l'ennemi ne peut pas contester drake/tour.
- **Ban absolu : Malphite** — un seul R unstoppable ferme la distance et efface une ligne de poke squishy.

#### C4 — Scaling Insurance « Safe scalers »  · Difficulté : Moyenne
- **Top :** Kayle · *alt : Nasus*
- **Jungle :** Master Yi · *alt : Karthus*
- **Mid :** Kassadin · *alt : Veigar, Vladimir*
- **ADC :** Kog'Maw · *alt : Vayne*
- **Support :** Lulu · *alt : Soraka, Milio*
- **Win condition :** chaque lane prend un scaler safe imperdable, jouer défensif, surclasser l'adversaire par les stats en late, peu d'all-in early.
- **Power spike :** minutes 30-40 (le plus tardif).
- **Combo clé :** Lulu R sur Master Yi/Kog'Maw → peel totale → DPS % HP imparable en teamfight tardif.
- **Ban absolu : Renekton** — bully top early qui peut fermer la partie avant que ta compo atteigne son spike de scaling.

---

## 4. Conception de la page HTML

### Contraintes
- **Un seul fichier** `compos-lol.html`, 100 % autonome (CSS + JS inline, aucune dépendance externe, aucune image distante). Ouvrable hors-ligne par double-clic.
- Responsive (desktop + mobile).

### Thème visuel
- Sombre, inspiration Hextech : fond bleu nuit, accents or (#C8AA6E) et bleu (#0AC8B9).
- Code couleur par catégorie :
  - Ultra Early → rouge/orange (agressif)
  - Mid/Late → violet/bleu (tempo)
  - Scale & Safe → vert/or (patience)

### Mise en page
- **En-tête** : titre, sous-titre (patch 26.11, Platine+, rôles flex).
- **Barre de filtres** (sticky en haut) :
  - Boutons de catégorie : Tout / Ultra Early / Mid-Late / Scale & Safe.
  - Champ de recherche texte : filtre les compos contenant un champion saisi (sur picks + alternatives).
- **Grille de cartes** : une carte par compo, badge de catégorie + badge difficulté.
  - Vue repliée : nom, archétype, catégorie, difficulté, les 5 picks principaux (icônes texte par rôle).
  - Au clic → dépliage : alternatives flex par rôle, win condition, power spike, combo clé, ban absolu (mis en valeur en rouge).
- **Pied de page** : rappel méta + note « ajuster selon le patch courant ».

### Comportement (JS vanilla)
- Filtrage par catégorie : masque/affiche les cartes.
- Recherche : insensible à la casse/accents, match sur le nom de champion dans n'importe quel rôle/alternative ; surligne ou n'affiche que les compos correspondantes.
- Dépliage/repliage des cartes au clic (accordéon indépendant par carte).
- Aucune persistance nécessaire (pas de localStorage requis).

### Données
- Les 12 compos sont stockées dans un tableau JS (objet par compo) en haut du script, ce qui rend les ajustements de picks triviaux (modifier une valeur, pas le HTML).

---

## 5. Hors-scope (YAGNI)

- Pas de simulateur de draft interactif (choisi : page de référence).
- Pas d'images/icônes de champions distantes (rester hors-ligne et léger).
- Pas de backend, pas de build, pas de framework.
- Pas de gestion de patchs multiples / versioning des compos.

---

## 6. Critères de réussite

- Le fichier s'ouvre seul dans un navigateur, sans connexion.
- Les 12 compos s'affichent, filtrables par catégorie et par recherche de champion.
- Chaque carte expose picks + flex + win condition + spike + combo + ban absolu.
- Lisible sur mobile et desktop.
