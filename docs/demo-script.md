# Script de démo (3 minutes) — Life / Career Strategy Copilot

Objectif: rejouer une démo complète, sans improvisation, jusqu’au plan d’action exportable.

## Préparation (avant la démo)
- Ouvrir l’application sur `http://localhost:3000`.
- Charger les données d’exemple de `docs/sample_input.json`.
- Garder `docs/sample_plan.json` ouvert dans un onglet (référence du résultat attendu).

---

## Timeline et talk track (mot à mot)

### 0:00 → 0:20 — Intro (écran d’accueil)
**Ce que tu montres**
- Page d’accueil du copilot.

**Ce que tu dis**
> « En 3 minutes, je vais vous montrer comment passer d’une situation floue à un plan de carrière concret sur 90 jours. Le but n’est pas de discuter, mais de décider quoi faire, dans quel ordre, et avec quels indicateurs. »

---

### 0:20 → 0:45 — Entry (écran `/entry`)
**Ce que tu fais**
- Coller la réponse `entryAnswer` de `sample_input.json`.
- Cliquer sur **Continuer**.

**Ce que tu dis**
> « Je commence par une réponse libre: le contexte réel, les tensions, et ce que j’essaie de résoudre maintenant. En un clic, l’app crée une session de décision. »

---

### 0:45 → 1:10 — Goal Framing (écran `/goal-framing`)
**Ce que tu fais**
- Coller `goal.northStar` et `goal.constraints` depuis `sample_input.json`.
- Cliquer sur **Valider le cadrage**.

**Ce que tu dis**
> « Ensuite, je force un cadrage net: une north star et des contraintes explicites. Ça évite les plans vagues et les conseils génériques. »

---

### 1:10 → 1:40 — Options (écran `/options`)
**Ce que tu fais**
- Afficher les 3 options proposées.
- Sélectionner l’option dont le titre correspond à `selectedOption.title` dans `sample_input.json`.

**Ce que tu dis**
> « Le système transforme le cadrage en options stratégiques comparables. Je choisis l’option la plus cohérente avec l’objectif et les contraintes. »

---

### 1:40 → 2:10 — Checklist / Plan (écran `/checklist`)
**Ce que tu fais**
- Montrer la checklist générée.
- Mentionner que la structure cible est dans `sample_plan.json` (objectif, mois 1/2/3, KPIs, risques).

**Ce que tu dis**
> « Ici, on passe de l’intention à l’exécution. On obtient une séquence d’actions vérifiable, avec des livrables et des métriques. »

---

### 2:10 → 2:35 — Export (écran `/export`)
**Ce que tu fais**
- Lancer l’export du plan.
- Montrer rapidement le fichier exporté.

**Ce que tu dis**
> « En sortie, j’ai un artefact partageable: mon plan 90 jours, prêt à être exécuté et revu avec un manager, un mentor ou un coach. »

---

### 2:35 → 3:00 — Aha moment + conclusion
**Aha moment (à dire exactement)**
> « L’aha moment, c’est ici: je ne me demande plus *quoi faire*. Je sais exactement quoi faire dans les 90 prochains jours — et comment mesurer si ça marche. »

**Conclusion (à dire exactement)**
> « Ce copilot n’est pas un chatbot carrière. C’est un moteur de décision qui produit de la clarté opérationnelle. »

---

## Check de répétabilité (DoD)
Pour valider « rejouable sans improviser », vérifier:
1. Le script est suivi dans l’ordre, sans sauter d’écran.
2. Les textes saisis viennent exclusivement de `docs/sample_input.json`.
3. Le résultat montré est conforme à la structure de `docs/sample_plan.json`.
4. La phrase d’aha moment est dite mot à mot.
