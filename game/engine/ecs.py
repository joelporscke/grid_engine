from __future__ import annotations

from typing import TypeVar, Type

EntityId = int

T = TypeVar("T")


class World:
    """Central ECS container. Holds all entities and their components."""

    def __init__(self) -> None:
        self._next_id: EntityId = 0
        self._components: dict[type, dict[EntityId, object]] = {}

    def create_entity(self) -> EntityId:
        entity_id: EntityId = self._next_id
        self._next_id += 1
        return entity_id

    def add_component(self, entity_id: EntityId, component: object) -> None:
        component_type: type = type(component)
        if component_type not in self._components:
            self._components[component_type] = {}
        self._components[component_type][entity_id] = component

    def remove_component(self, entity_id: EntityId, component_type: type) -> None:
        store = self._components.get(component_type)
        if store is not None:
            store.pop(entity_id, None)

    def get_component(self, entity_id: EntityId, component_type: Type[T]) -> T | None:
        return self._components.get(component_type, {}).get(entity_id)  # type: ignore[return-value]

    def get_all(self, component_type: Type[T]) -> dict[EntityId, T]:
        return self._components.get(component_type, {})  # type: ignore[return-value]

    def destroy_entity(self, entity_id: EntityId) -> None:
        """Remove all components for an entity, effectively destroying it."""
        for store in self._components.values():
            store.pop(entity_id, None)
