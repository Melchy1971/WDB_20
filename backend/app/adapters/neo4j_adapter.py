from collections.abc import Callable
from typing import Any

from neo4j import GraphDatabase

from app.core.config import settings


class Neo4jAdapter:
    def __init__(self) -> None:
        self._driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )

    def check_connection(self) -> str:
        try:
            self._driver.verify_connectivity()
            return "up"
        except Exception:
            return "down"

    def execute_write(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        parameters = parameters or {}

        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def execute_read(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        parameters = parameters or {}

        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def close(self) -> None:
        self._driver.close()
