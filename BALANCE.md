# Balance – GridEngine

## Om den här filen
Alla värden här är startvärden att testa och justera via playtesting. Inga värden är huggna i sten. Uppdatera efter varje testomgång med vad som kändes obalanserat och varför.

Alla värden definieras som namngivna konstanter i koden – aldrig hårdkodade.

---

## Kartstorlek
- **Grid**: 50x50
- **Mål**: Spelarna möts efter 5-10 turer vid aggressivt spel, 15-20 turer vid defensivt spel

---

## Vinstkondition
- **Poänggräns**: 15p
- **Döda unit**: 1p
- **Förstöra byggnad**: 2p
- **Döda hero**: 5p
- **Förstöra base**: 10p

---

## Units – relationer och startvärden

### Rörelse (energi per tur)
| Unit | Rörelse | Notering |
|------|---------|----------|
| Melee | 5 | Basvärde allt utgår från |
| Archer | 4 | Lägre rörelse, kompenseras med bygghastighet |
| Anti-archer | 4-5 | Samma eller mer än archer för att undvika kiting |
| Scout normal | 5 | Standard |
| Scout travel mode | 10 | Dubbel rörelse, minimal line of sight |
| Scout scout mode | 2 | Kraftigt begränsad rörelse, dubbel line of sight |
| Hero | 5 | Samma som melee, byggs upp via utrustning |

### Line of sight (rutor)
| Unit | Line of sight | Notering |
|------|--------------|----------|
| Melee | 5 | Basvärde |
| Archer | 6 | Marginellt bättre än melee |
| Anti-archer | 5 | Standard |
| Scout normal | 5 | Standard |
| Scout travel mode | 1 | Minimal |
| Scout scout mode | 10 | Dubbel |
| Hero | 5 | Standard |

### Stats – relationer
- **Hero hp**: ungefär 2x melee
- **Hero attack**: ungefär 2x melee
- **Archer räckvidd**: längre än anti-archer
- **Anti-archer räckvidd**: kortare än archer, längre än melee
- **Ranged i närstrid**: halv skada jämfört med ranged attack
- **Opportunity attack**: 2x skada

### Archer – lägesmodifierare
- **Shoot and move**: reducerad skada, exakt värde att testa
- **Shoot and stay**: full skada, inget rörelseavdrag

### Charge – melee uppgradering
- Gå sista rutan gratis mot alla unit-typer
- Bonusskada på första attacken efter charge, exakt värde att testa

---

## Byggnader – relationer och startvärden

### Byggtid och rörelselåsning
| Byggare | Byggtid | Låst |
|---------|---------|------|
| Hero | 1 tur | Nej – kan röra sig och bygga samma tur |
| Archer | 1 tur | Ja |
| Melee | 2 turer | Ja |
| Scout | Mer än melee | Ja – kräver uppgradering |

### Byggnads-hp – relationer
- **Base**: ungefär 3x övriga byggnader
- **Military camp**: lite mer än vanliga camps
- **Övriga camps**: standard hp

### Byggnadsbegränsningar
- Resursbyggnader (wood camp, mine camp, hunting ground camp): max 4 totalt
- Military camp: max 2
- Base och shrine: en per spelare

### Byggnader – line of sight
- Alla byggnader: 5 (samma som melee-basvärde)
---

## Resurser – produktion per tur

### Base
- Food: liten mängd, exakt värde att testa
- Wood: liten mängd, exakt värde att testa

### Wood Camp
- Wood: måttlig mängd per tur, exakt värde att testa

### Mine Camp
- Fokuserad resurs (sten eller metall): mer
- Icke-fokuserad resurs: mindre
- Exakta värden att testa

### Hunting Ground Camp
- Food: god mängd per tur, exakt värde att testa

### Shrine
- Shrine power: 1 per tur
- Cap: 10-15, exakt värde att testa

---

## Uppgraderingar – kostnadsprinciper
- Tidiga uppgraderingar kostar food och wood
- Senare uppgraderingar kräver sten och metall
- Alla uppgraderingar kostar shrine power utöver resurser
- Exakta kostnader sätts av Claude Code och justeras via playtesting

---

## Playtesting-log
*Lägg till observationer efter varje testomgång.*

*Format:*
- **Datum**:
- **Observation**: vad kändes obalanserat
- **Justering**: vad som ändrades
- **Resultat**: blev det bättre