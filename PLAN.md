# Game Engine – Byggplan

## Status
Uppdatera efter varje steg: `[ ]` = ej påbörjat, `[~]` = pågår, `[x]` = klart

---

## Grund-demo – KLAR
Alla steg nedan är implementerade och fungerar.

- [x] Steg 1 – Fönster och game loop
- [x] Steg 2 – Grid-data och terräng
- [x] Steg 3 – ECS och första pjäsen
- [x] Steg 4 – Input och rörelse
- [x] Steg 5 – Turn-system och energi

---

## Etapp 1 – Combat och units

### Steg 1 – Flera unit-typer
**Mål:** Melee och archer finns på kartan med distinkta egenskaper.

**Klar när:**
- Melee och archer definierade som unit-typer med olika stats
- Rörelse och attack är separata handlingar
- Varje unit har hp, attack, räckvidd och rörelsevärden som namngivna konstanter

**Status:** [x]

---

### Steg 2 – Combat-system
**Mål:** Units kan attackera varandra och ta skada.

**Klar när:**
- AttackAction definierad och hanterad
- Units kan attackera inom räckvidd på sin tur
- Skada beräknas och hp minskar
- Unit dör när hp når 0 och tas bort från kartan
- Poäng ges för att döda en unit

**Status:** [x]

---

### Steg 3 – Combat-regler
**Mål:** Opportunity attacks och ranged i närstrid fungerar.

**Klar när:**
- Opportunity attack – 2x skada om unit lämnar ruta intill fiende som kan attackera
- Ranged units gör halv skada i närstrid
- Archer har tre lägen: move only, shoot and move, shoot and stay

**Status:** [x]

---

### Steg 4 – Hero
**Mål:** Hero finns på kartan med sina grundegenskaper.

**Klar när:**
- Hero definierad med egna stats, ungefär dubbelt så stark som melee
- Hero räknas inte mot pop space
- Hero kan bygga byggnader och är inte låst under bygget
- Poäng ges för att döda hero (5p)

**Status:** [x]
*Not: "Hero kan bygga utan att låsas" implementeras i Etapp 3 (BuildSystem). Övriga krav uppfyllda.*

---

## Etapp 2 – Terräng och Fog of War

### Steg 1 – Utökad terräng
**Mål:** Alla fyra terrängtyper finns och fungerar korrekt.

**Klar när:**
- GRASS, THICK_WOOD, MOUNTAIN, HUNTING_GROUNDS definierade som data
- Thick wood och mountain blockerar rörelse
- Kartplacering: wood närmast base, mountain lite längre, hunting grounds mot mitten
- Terrängtyper har vision_blocking-egenskap

**Status:** [x]

---

### Steg 2 – Fog of War
**Mål:** Spelaren ser bara vad deras units kan se.

**Klar när:**
- Tre celltillstånd: VISIBLE, SEEN, UNKNOWN
- Synlighet beräknas per tur baserat på unit-position och line of sight
- Thick wood och mountain blockerar sikt efter en ruta in
- Tidigare sedda celler visas mörklagda
- Toggle för att stänga av fog of war för debugging

**Status:** [x]

---

### Steg 3 – Kartstorlek och startpositioner
**Mål:** 50x50 karta med korrekt placering av terräng och startpositioner.

**Klar när:**
- Kartan är 50x50
- Spelarna startar på varsin sida
- Terräng genereras med korrekt placering relativt base
- Shrine placerad nära varje spelares startområde

**Status:** [x]

---

## Etapp 3 – Resurser och Byggnader

### Steg 1 – Resurssystem
**Mål:** Resurser finns och genereras per tur.

**Klar när:**
- ResourceStore per spelare med food, wood, stone, metal, shrine_power
- Base genererar liten mängd food och wood varje tur
- UI visar resurserna för aktiv spelare

**Status:** [ ]

---

### Steg 2 – Byggnadssystem
**Mål:** Units kan bygga byggnader som placeras på kartan.

**Klar när:**
- BuildAction definierad och hanterad
- Melee och archer kan bygga, hero bygger utan att låsas
- Byggnader är entities med egna komponenter
- Byggnader har hp och kan ta skada och förstöras
- Poäng ges för att förstöra en byggnad (2p), base ger 10p

**Status:** [ ]

---

### Steg 3 – Alla byggnadstyper
**Mål:** Alla fem byggnader fungerar med sina regler.

**Klar när:**
- Base, wood camp, mine camp, military camp, hunting ground camp implementerade
- Byggnadsbegränsningar: max 4 resursbyggnader totalt, max 2 military camps
- Hunting ground camp kan bara byggas på hunting grounds-terräng
- Byggnader låser upp rätt units och abilities
- Pop space fungerar korrekt

**Status:** [ ]

---

### Steg 4 – Uppgraderingar
**Mål:** Units och hero kan uppgraderas.

**Klar när:**
- Stats-uppgraderingar måste hämtas fysiskt från rätt byggnad
- Ability-uppgraderingar låses upp automatiskt via byggnad
- Hero-specifika pickups (pilbåge, rustning) kan hämtas
- Uppgraderingar kostar resurser och shrine power
- Charge fungerar för melee efter uppgradering

**Status:** [ ]

---

### Steg 5 – Shrine
**Mål:** Shrine fungerar med kontroll och shrine power.

**Klar när:**
- Shrine är en neutral punkt på kartan
- Tas i kontroll genom att en unit går dit
- Genererar 1 shrine power per tur, cap definierat som konstant
- Hero kan respawna vid kontrollerad shrine
- Hero ledarskapsaura kan låsas upp och aktiveras med shrine power

**Status:** [ ]

---

## Etapp 4 – Progression och balans

### Steg 1 – Scout och anti-archer
**Mål:** Scout och anti-archer är implementerade och fungerar.

**Klar när:**
- Scout med tre lägen: normal, travel mode, scout mode
- Anti-archer med korrekt damage-profil mot archers
- Scout låses upp via military camp, anti-archer via hunting ground camp

**Status:** [ ]

---

### Steg 2 – Vinstkondition och poängsystem
**Mål:** Spelet har ett tydligt slut.

**Klar när:**
- Poängsystem fungerar för alla händelser
- Spelet avslutas när en spelare når poänggränsen
- Poänggräns och poängvärden definierade som data, enkla att justera

**Status:** [ ]

---

### Steg 3 – Balansering och playtesting
**Mål:** Spelet känns balanserat och strategiskt.

**Klar när:**
- Alla startvärden i BALANCE.md är testade och justerade
- Inga dominanta strategier som alltid vinner
- De tre öppningsspelsstilarna är alla viabla

**Status:** [ ]

---

## Noteringar

### Etapp 1 – Combat och units (2026-03-31)

**Opportunity attack konsumerar inte attackerens tur**
- **Vad**: Opportunity attack är en fri reaktion – den konsumerar inte fiendens `has_attacked`.
- **Varför**: Gör punishment-mekaniken starkare och mer strategisk; stämmer med DESIGN.md:s formulering "kan attackera dig" (förmåga, inte action).
- **Påverkar**: MovementSystem._apply_opportunity_attacks, combat-balans

**Archer mode cyclas med M-tangent**
- **Vad**: Spelaren växlar archer-läge (move only / shoot+move / shoot+stay) med M-tangenten.
- **Varför**: Enkel och intuitiv tangent, visas i UI:t som "[M]" bredvid lägesnamnet.
- **Påverkar**: main.py input-loop, renderer UIState

**Input-routing i main.py, inte i MovementSystem**
- **Vad**: process_click() togs bort ur MovementSystem. Istället hanterar handle_click() i main.py click-routing och avgör om det är select, move eller attack.
- **Varför**: Systems ska inte känna till varandra (arkitekturprincip). Routing hör hemma i applagret.
- **Påverkar**: MovementSystem (handle_select, handle_move är nu publika), main.py

**vision_blocking tillagd i TerrainType**
- **Vad**: TerrainType fick fältet `vision_blocking: bool`. Används ännu inte (Fog of War är Etapp 2).
- **Varför**: ARCHITECTURE.md specificerar fältet. Lägger grunden för Etapp 2 utan att bryta befintlig kod.
- **Påverkar**: engine/grid.py, game/rules.py

**Hero "bygga utan att låsas" skjuts upp till Etapp 3**
- **Vad**: Hero skapas med korrekt stats och UnitKind.HERO. Byggfunktionalitet saknas.
- **Varför**: BuildSystem implementeras i Etapp 3. Hero-flaggan UnitKind.HERO finns redan och BuildSystem kan enkelt kolla den när det byggs.
- **Påverkar**: Steg 4 i Etapp 1 (godkänt), Etapp 3 Steg 2

---

### Etapp 2 – Terräng och Fog of War (2026-03-31)

**FogState och FogSystem separerade efter ansvar**
- **Vad**: `FogState`-enumet placerades i `engine/grid.py` (bredvid `Cell`), inte i `engine/fog.py`.
- **Varför**: Annars cirkulär import – `fog.py` importerar `Grid`, men `Grid` hade behövt importera `FogState` från `fog.py`.
- **Påverkar**: engine/grid.py, engine/fog.py

**FogSystem tar (col, row, los)-listor, inte ECS-komponenter**
- **Vad**: `FogSystem.update()` tar `list[tuple[int,int,int]]` från main.py, inte `Vision`/`OwnedBy` direkt.
- **Varför**: engine/ ska vara rent – inga game-specifika imports. main.py gör ECS-uppslaget och skickar ner data.
- **Påverkar**: engine/fog.py, main.py (_get_unit_los_data)

**Shrines placeras inte på grid (grid.place_entity anropas inte)**
- **Vad**: Shrine-entities har Position + Renderable + Shrine men blockerar inte rörelse.
- **Varför**: Kontrollogik (Etapp 3) kräver att units kan gå dit. grid.place_entity är ett rörelseblock, ej ett logikblock.
- **Påverkar**: main.py, Etapp 3 Steg 5

**16 px celler, ENTITY_PADDING=2, liten font**
- **Vad**: 50×50 grid → 16 px celler (800×800 gridyta + 90 UI = 890 px totalt). Entity padding och font skalas ner.
- **Varför**: Måste få plats i ett rimligt fönster. 16 px ger tillräcklig detalj för labels och HP-bar.
- **Påverkar**: engine/renderer.py (alla cell/font-konstanter)

---

## ⚠️ Framtida idéer
*Denna sektion ändras ENDAST när användaren explicit ber om det.*

**Units och combat**
- Hero XP och leveling
- Unit XP – veterans och specialstatus, typ archer som dödat 3 units blir sniper med +1 range
- Accuracy-system för archers och charge
- Höjdskillnad – high ground ger archer extra range/damage
- Archer förbereda position – ge upp rörelse för x turer mot extra skada
- Assassin unit från shrine som specialiserar på hero
- Units som kan röra sig i skog
- Units bygger olika byggnader olika snabbt

**Byggnader och ekonomi**
- Resurslinjer med vagnar mellan camps och base
- Armory som centralt uppgraderingsställe
- Flera nivåer av uppgraderingar
- Ytterligare uppgraderingstyper
- Anti-archer bygger torn
- Tower som byggnad

**Karta och terräng**
- Höjdskillnad och high ground
- Fler terrängtyper
- Fler shrines på kartan mot mitten för respawn-val

**Shrine och progression**
- Fler shrine entities och speciella units
- Hero-specifika shrine powers
- Merchant/bandit camp som hero kan interagera med
- Fler vinstkonditioner, typ capture the flag

**Spelupplevelse**
- Settings-meny för att justera spelregler och poänggränser
- AI-motståndare med olika svårighetsnivåer tränad via reinforcement learning
- Gymnasium-wrapper för RL-träning
- Flera speltyper med olika regler

**Tekniskt**
- Max 2 av samma resursbyggnad som fallback om balansen kräver det