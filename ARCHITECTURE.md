# Game Engine Architecture

## Syfte
En turbaserad 2D grid-baserad spelmotor byggd i Python. Nuvarande projekt är ett turbaserat strategispel på en 50x50 karta med resurser, byggnader, fog of war och flera unit-typer.

---

## Teknisk spec
- **Python**: 3.13
- **Pygame**: 2.6.1 (använd alltid moderna Pygame 2.x API:er, inga deprecated anrop)
- **Kodstil**: Type hints på alla funktioner, dataclasses för komponenter, f-strings för strängformatering
- **Externa beroenden**: Pygame-CE 2.x och pygame_gui. Inga ytterligare bibliotek läggs till utan explicit instruktion
- **Inga magic numbers** – alla numeriska värden ska definieras som namngivna konstanter
- **Spellogik ska aldrig bero på hårdkodade värden** – terrängegenskaper, rörelsekostnad, attackvärden osv ska alltid definieras som data

---

## Mappstruktur

```
game/
├── engine/               # Generisk motor – inget spelspecifikt här
│   ├── ecs.py            # Entity Component System
│   ├── grid.py           # Grid och Cell
│   ├── renderer.py       # Rendering
│   ├── input.py          # Input-hantering
│   ├── events.py         # Event-system
│   ├── turn.py           # Turn-system
│   └── fog.py            # Fog of war – cell-tillstånd och synlighet
│
├── game/                 # Spelspecifik logik – använder motorn
│   ├── components.py     # Spelets komponenter (Health, Movement osv)
│   ├── systems.py        # Spelets system (MovementSystem, CombatSystem osv)
│   ├── actions.py        # Action-definitioner
│   ├── rules.py          # Spelregler
│   ├── resources.py      # Resursdefinitioner och resurshantering
│   └── buildings.py      # Byggnadsdefinitioner och byggnadslogik
│
├── assets/               # Sprites, ljud osv
└── main.py               # Entry point
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
class AttackAction:
    attacker_id: EntityId
    target_id: EntityId

@dataclass
class BuildAction:
    builder_id: EntityId
    building_type: str
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
- `terrain_type` – enum (GRASS, THICK_WOOD, MOUNTAIN, HUNTING_GROUNDS)
- `entity_id` – EntityId eller None
- `fog_state` – FogState enum (VISIBLE, SEEN, UNKNOWN)

Terrängtyper definieras som data med egenskaper:

```python
@dataclass
class TerrainType:
    name: str
    passable: bool
    vision_blocking: bool
    color: tuple[int, int, int]
```

Spelregler läser terrängegenskaper – de hårdkodar aldrig terrängnamn.

---

## Fog of War

Hanteras i `engine/fog.py`. Varje cell har ett av tre tillstånd:

```python
class FogState(Enum):
    UNKNOWN = 0   # Aldrig sedd – ritas svart
    SEEN = 1      # Tidigare sedd – ritas mörklagd
    VISIBLE = 2   # Synlig just nu – ritas normalt
```

Synlighet beräknas per tur baserat på varje units position och line of sight. Terrängtyper med `vision_blocking=True` blockerar sikt efter en ruta in. Fog of war kan toggleas av för debugging.

---

## Resurssystem

Resurser definieras som data i `game/resources.py`. Varje spelare har ett resurslager.

```python
@dataclass
class ResourceStore:
    food: int = 0
    wood: int = 0
    stone: int = 0
    metal: int = 0
    shrine_power: int = 0
```

Produktionsvärden och kostnader definieras som namngivna konstanter – aldrig hårdkodade i system eller regler.

---

## Byggnadssystem

Byggnader är entities med komponenter precis som units. `game/buildings.py` definierar byggnadstyper som data.

```python
@dataclass
class BuildingType:
    name: str
    cost: dict[str, int]       # Resurskostnad
    hp: int
    pop_space: int             # Pop space som byggnaden ger
    production: dict[str, int] # Resurser som produceras per tur
    build_time: int            # Turer att bygga
    slots: int                 # Antal unit-slots
    unlocks: list[str]         # Units eller abilities som låses upp
```

Byggnadsplaceringsregler läser terrängegenskaper – de hårdkodar aldrig terrängnamn.

---

## Separation motor / spel

`engine/` innehåller aldrig spelspecifik logik. Den vet inte om soldater, skog, resurser eller regler. Den tillhandahåller verktyg – ECS, grid, rendering, events, input, fog of war.

`game/` använder motorn och definierar spelets regler, komponenter, system, resurser och byggnader.

---

## Rendering

Renderaren är dum – den fattar inga beslut. Varje frame:
1. Läser grid-state och ritar terräng filtrerat genom fog of war
2. Läser entity-state och ritar units och byggnader
3. Ritar UI – aktiv spelare, resurser, pop space, markerad entity, poäng

Renderaren ritar om allt från scratch varje frame.