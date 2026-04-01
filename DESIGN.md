# Game Design Document – GridEngine

## Spelkänsla och vision
Ett turbaserat strategispel där varje beslut räknas. Spelet ska kännas genomtänkt och strategiskt – inte ett race om vem som pumpar ut flest units snabbast. Resurser, position och timing ska vara viktigare än volym. Inspirerat av Age of Empires 2, Heroes of Might and Magic och Warhammer men i ett mindre och mer fokuserat format. Två spelare möts på en gemensam karta där ekonomi, kartpositionering och army composition avgör utgången.

---

## Vinstkondition
Första spelaren till 15 poäng vinner, eller om motståndaren ger upp.

Poäng ges för:
- Döda en unit: 1p
- Förstöra en byggnad: 2p
- Döda hero: 5p
- Förstöra fiendens base: 10p

Poängsystemet är konfigurerbart – gränsvärden och poängvärden definieras som data och ska vara enkla att justera i settings framöver.

---

## Karta
- Storlek: 50x50
- Spelarna ska kunna mötas efter 5-10 turer vid aggressivt spel, 15-20 turer vid defensivt spel

### Kartplacering av resursterräng
- Wood närmast base
- Mountain lite längre från base än wood
- Hunting grounds längst bort mot mitten av kartan – risk/reward
- Shrine placerad nära varje spelares startområde

---

## Terräng
- **Grass** – normal rörelse
- **Thick Wood** – blockerar rörelse, wood camp byggs vid kanten. Man ser en ruta in, aldrig igenom
- **Mountain** – blockerar rörelse, mine camp byggs vid kanten. Man ser en ruta in, aldrig igenom
- **Hunting Grounds** – speciell terräng mot mitten av kartan, hunting ground camp byggs här

---

## Fog of War
- Tre tillstånd per cell: synlig, tidigare sedd, okänd
- Togglebar för debugging

---

## Units

### Melee
- Hög rörelse, robust hp, kort räckvidd
- Rörelse och attack är separata
- **Charge** – uppgradering. Gå sista rutan gratis och bonusskada på första attacken. Funkar mot alla unit-typer. Ger initiativefördel i melee vs melee

### Archer
- Lägre rörelse än melee, lång räckvidd
- Marginellt bättre line of sight än melee
- Tre lägen per tur:
  - Move only – full rörelse, ingen attack
  - Shoot and move – skjuter, tar ett steg efter, reducerad skada
  - Shoot and stay – ingen rörelse, full skada
- Positioneringsenhet – planera var den ska stå innan strid

### Scout
- Låses upp via Military Camp
- Tre lägen:
  - Normal – standard rörelse och line of sight
  - Travel mode – dubbel rörelse, minimal line of sight
  - Scout mode – kraftigt begränsad rörelse, dubbel line of sight
- Primärt informationsenhet, sekundärt flankeringsenhet mot ranged
- Kräver uppgradering för att kunna bygga byggnader

### Anti-archer
- Låses upp via Hunting Ground Camp
- Kortare räckvidd än archer
- Extra damage mot archers, lite mindre damage mot annat
- Samma eller mer rörelse än archer, ingen attack penalty
- Självständigt strategiskt syfte även utan archers att countra

### Hero
- En per spelare, startar på kartan tillsammans med base
- Räknas inte mot pop space
- Börjar ungefär dubbelt så stark som melee
- Byggs upp under spelets gång via pickups – pilbåge hämtas i wood camp, rustning hämtas i mine camp
- Värd 5p vid död
- Respawn kräver kontroll av en shrine – din eller fiendens
- **Ledarskapsaura** – aktiv förmåga som spelaren manuellt aktiverar, 
inte en passiv effekt. Låses upp via shrine power. Tre typer att låsa upp, 
en i taget. När aktiverad påverkar den units inom en viss radius under ett 
begränsat antal turer, sedan går den på CD. Kostar shrine power att både 
låsa upp och aktivera:
  - Ranged bonus – ökar skada för ranged units inom radius
  - Melee bonus – ökar skada för melee units inom radius
  - Heal – återställer hp för units inom radius
  - Var och en har egen radius, aktiveringskostnad i shrine power och CD

### Population cap
- Varje byggnad ger +1 pop space, military camp ger +2
- Melee och archer tillgängliga från start
- Scout och anti-archer låses upp via byggnader
- Hero räknas inte mot pop space

---

## Combat-regler

### Turordning
- Man attackerar bara på sin egen tur
- Rörelse och attack är separata handlingar

### Opportunity attack
- Om du lämnar en ruta intill en fiende som kan attackera dig tar du 2x skada från den
- Gäller även om flera units kan attackera – du tar 2x från var och en

### Ranged i närstrid
- Ranged units gör halv skada i närstrid jämfört med sin ranged attack

---

## Resurser
- **Food** – genereras av base och hunting ground camp. Units kostar food att producera
- **Wood** – genereras av base (liten mängd) och wood camp. Units och byggnader kostar wood
- **Sten** – genereras av mine camp. Krävs för byggnader och uppgraderingar
- **Metall** – genereras av mine camp. Krävs för vapen och rustningsuppgraderingar
- **Shrine power** – genereras av shrine, 1 per tur vid kontroll, cap 10-15. Används för hero aura, respawn och uppgraderingar

---

## Byggnader

### Base
- Startar på kartan, en per spelare
- Producerar melee och archer
- Genererar liten mängd food och wood varje tur
- Mest hp av alla byggnader, ungefär 3x övriga

### Wood Camp
- Producerar wood varje tur
- Låser upp: rörelse+1 för archer, hero pilbåge
- Standard hp

### Mine Camp
- Spelaren väljer fokus mellan sten och metall
- Låser upp: rustningsuppgradering, hero rustning, attackuppgradering
- Standard hp

### Military Camp
- Producerar melee, archer och scout
- Ger +2 pop space
- Kräver sten och metall att bygga
- Låser upp scout
- Lite mer hp än vanliga camps

### Hunting Ground Camp
- Kan bara byggas på hunting ground-terräng
- Producerar food varje tur
- Låser upp anti-archer
- Standard hp

### Unit-interaktion med byggnader
- Byggnader har slots
- En unit assignad till en byggnad ger +1 produktionsbonus
- En unit i en byggnad kan försvara den om fienden attackerar

---

## Shrine
- Neutral punkt på kartan nära varje spelares startområde
- Tas i kontroll genom att en unit går dit
- Motståndaren kan sno den genom att gå dit med sin unit
- Genererar 1 shrine power per tur vid kontroll, cap 10-15

---

## Uppgraderingar

### Stats – måste hämtas fysiskt från rätt byggnad
- Attack, hp, rörelse för units

### Abilities – låses upp automatiskt via byggnad, behöver inte hämtas
- Charge för melee
- Byggförmåga för scout
- Rörelse+1 för archer

### Hero-specifikt – måste hämtas fysiskt
- Pilbåge från wood camp
- Rustning från mine camp

### Kostnad
- Resurser + shrine power
- En nivå per uppgradering från start

---

## Bygga byggnader

### Vem kan bygga
- Melee, archer och hero kan bygga som standard
- Scout kräver uppgradering för att kunna bygga
- Nya units har ingen byggförmåga som default

### Byggtid och rörelselåsning
- Hero: 1 tur, inte låst – kan röra sig och bygga samma tur
- Archer: 1 tur, låst under bygget
- Melee: 2 turer, låst under bygget
- Scout: långsammare än melee, kräver uppgradering

### Tre distinkta öppningsspelsstilar
- Wood camp först – stabil ekonomi, archer-fokus
- Mine camp först – tidig military camp, aggressiv unit-spawn framåt
- Hunting ground – wood-investering tidigt, bättre food senare, anti-archer