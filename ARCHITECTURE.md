# Game Engine Architecture

## Syfte
En enkel, turbaserad 2D grid-baserad spelmotor byggd i Python. Motorn ska vara generisk nog att driva både brädspelsliknande spel och turbaserade strategispel. Första demot är en 20x20 karta med två spelare och grundläggande rörelse.

---

## Teknisk spec
- **Python**: 3.12+
- **Pygame**: 2.x (använd alltid moderna Pygame 2.x API:er, inga deprecated anrop)
- **Kodstil**: Type hints på alla funktioner, dataclasses för komponenter, f-strings för strängformatering
- **Inga externa beroenden** utöver Pygame
- **Inga magic numbers** – alla numeriska värden ska definieras som namngivna konstanter
- **Spellogik ska aldrig bero på hårdkodade värden** – terrängegenskaper, rörelsekostnad, attackvärden osv ska alltid definieras som data

---

## Mappstruktur

```
game/
├── engine/          # Generisk motor – inget spelspecifikt här
│   ├── ecs.py       # Entity Component System
│   ├── grid.py      # Grid och Cell
│   ├── renderer.py  # Rendering
│   ├── input.py     # Input-hantering
│   ├── events.py    # Event-system
│   └── turn.py      # Turn-system
│
├── game/            # Spelspecifik logik – använder motorn
│   ├── components.py  # Spelets komponenter (Health, Movement osv)
│   ├── systems.py     # Spelets system (MovementSystem, osv)
│   ├── actions.py     # Action-definitioner
│   └── rules.py       # Spelregler
│
├── assets/          # Sprites, ljud osv (tomt i början)
└── main.py          # Entry point
```

---

## ECS – Entity Component System

### Entity
En entity är bara ett unikt heltal (ID). Ingen logik, ingen data.

```python
EntityId = int
```

### Component
Ren data, inga metoder. Alltid en dataclass.

```python
@dataclass
class Position:
    x: int
    y: int

@dataclass
class Movement:
    range: int
    energy: int
    max_energy: int
    has_moved: bool = False
```

### Component Store
Central datastruktur som håller alla komponenter indexerade på entity ID.

```python
components: dict[type, dict[EntityId, Component]]
```

Exempel på lookup:
- Alla entities med Movement: `components[Movement].keys()`
- Movement för entity 42: `components[Movement][42]`

### System
Logik som opererar på entities med rätt kombination av komponenter. System känner inte till varandra – de kommunicerar via events.

---

## Actions

Input genererar alltid en Action – aldrig direkt spellogik. Actions är data.

```python
@dataclass
class MoveAction:
    entity_id: EntityId
    target: tuple[int, int]

@dataclass
class EndTurnAction:
    player_id: int
```

System lyssnar på actions och avgör om de är tillåtna enligt regler.

---

## Event-system

System kommunicerar via events, inte direkt med varandra. Håller systemen separerade.

```python
# Sända ett event
events.emit("entity_moved", {"entity_id": 42, "to": (3, 7)})

# Lyssna på ett event
events.on("entity_moved", callback)
```

---

## Grid

Varje cell innehåller:
- `terrain_type` – enum (GRASS, FOREST osv)
- `entity_id` – EntityId eller None

Terrängtyper definieras som data med egenskaper:

```python
@dataclass
class TerrainType:
    name: str
    passable: bool
    color: tuple[int, int, int]
```

Spelregler läser terrängegenskaper – de hårdkodar aldrig terrängnamn.

---

## Separation motor / spel

`engine/` innehåller aldrig spelspecifik logik. Den vet inte om soldater, skog eller energi. Den tillhandahåller verktyg – ECS, grid, rendering, events, input.

`game/` använder motorn och definierar spelets regler, komponenter och system.

---

## Rendering

Renderaren är dum – den fattar inga beslut. Varje frame:
1. Läser grid-state och ritar terräng
2. Läser entity-state och ritar pjäser
3. Ritar UI (aktiv spelare, energi, markerad pjäs)

Renderaren ritar om allt från scratch varje frame.
