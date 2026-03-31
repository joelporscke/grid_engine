# Game Engine – Byggplan

## Status
Uppdatera efter varje steg: `[ ]` = ej påbörjat, `[x]` = klart

---

## Steg 1 – Fönster och game loop
**Mål:** Ett Pygame-fönster öppnas och visar ett 20x20 rutnät. Ingenting mer.

**Klar när:**
- Fönster öppnas utan fel
- 20x20 grid ritas ut med synliga cellkanter
- Fönstret går att stänga

**Status:** [x]

---

## Steg 2 – Grid-data och terräng
**Mål:** Rutnätet har data bakom sig. Celler har terrängtyp och renderaren läser från den datan.

**Klar när:**
- `Grid` och `Cell` klasser finns i `engine/grid.py`
- Terrängtyper definierade som data med egenskaper (`passable`, `color`)
- Kartan har en mix av GRASS och FOREST
- Renderaren ritar olika färger beroende på terrängtyp

**Status:** [x]

---

## Steg 3 – ECS och första pjäsen
**Mål:** ECS-strukturen finns och en pjäs renderas på kartan.

**Klar när:**
- `EntityId`, Component Store och grundkomponenter finns i `engine/ecs.py`
- `Position` och `Movement` komponenter definierade i `game/components.py`
- En entity skapas med Position och renderas som en färgad fyrkant på rätt cell

**Status:** [x]

---

## Steg 4 – Input och rörelse
**Mål:** Spelaren kan klicka på en pjäs och flytta den till en angränsande cell.

**Klar när:**
- Klick på pjäs markerar den
- Klick på angränsande ledig cell flyttar pjäsen
- Skog blockerar rörelse
- Input genererar Actions, inte direkt spellogik
- Event-system används för kommunikation mellan systems

**Status:** [x]

---

## Steg 5 – Turn-system och energi
**Mål:** Två spelare turas om. Rörelse kostar energi.

**Klar när:**
- Två spelare, en pjäs var
- 3 energi per tur, ett steg kostar 1
- "Avsluta tur"-knapp byter aktiv spelare och återställer energi
- UI visar aktiv spelare och kvarvarande energi

**Status:** [x]

---

## Noteringar
*Lägg till beslut, problem eller förändringar här löpande så att nya Claude Code-sessioner har full kontext.*

*Varje notering ska innehålla:*
- **Vad** – vad som ändrades eller bestämdes
- **Varför** – beslutet bakom
- **Påverkar** – vilket steg eller vilken del av arkitekturen det rör
