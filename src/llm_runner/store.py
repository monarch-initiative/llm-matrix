import logging
from dataclasses import dataclass
from typing import Optional
import duckdb
from pathlib import Path
from pydantic import BaseModel

from llm_runner import TestCase
from llm_runner.schema import TestCaseResult, Response

logger = logging.getLogger(__name__)

@dataclass
class Store:
    """A persistent store using DuckDB to cache test results with JSON support for Pydantic models.

    Example:

        >>> store = Store("cache.db")
        >>> case = TestCase(input="1+1")
        >>> response = Response(text="2")
        >>> result = TestCaseResult(case=case, response=response, hyperparameters={"model": "gpt-4"})
        >>> store.add_result("test", result)
        >>> cached = store.get_result("test", case, {"model": "gpt-4"})
        >>> assert cached.response == response
    """
    db_path: str
    _conn: Optional[duckdb.DuckDBPyConnection] = None

    def __post_init__(self):
        """Initialize the database connection and create the table if it doesn't exist."""
        self._conn = duckdb.connect(str(self.db_path))
        # Using JSON type for storing Pydantic models and hyperparameters
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                suite_name VARCHAR,
                test_case JSON,
                hyperparameters JSON,
                result JSON,
                PRIMARY KEY (suite_name, test_case, hyperparameters)
            )
        """)

    def add_result(self, suite_name: str, result: TestCaseResult):
        """Add a result to the store."""
        self._conn.execute("""
            INSERT OR REPLACE INTO results 
            (suite_name, test_case, hyperparameters, result)
            VALUES (?, ?, ?, ?)
        """, (
            suite_name,
            result.case.model_dump(exclude_unset=True),
            result.hyperparameters,
            result.model_dump(exclude_unset=True),
        ))
        logger.debug(f"Added result for {suite_name} {result.case} {result.hyperparameters}")
        self._conn.commit()

    def get_result(self, suite_name: str, case: TestCase, hyperparameters: dict) -> Optional[TestCaseResult]:
        """Get a result from the store."""
        result = self._conn.execute("""
            SELECT result
            FROM results
            WHERE suite_name = ?
            AND test_case = ?
            AND hyperparameters = ?
        """, (
            suite_name,
            case.model_dump(exclude_unset=True),
            hyperparameters,
        )).fetchone()

        logger.debug(f"Present: {result is not None} when looking up {suite_name} {case} {hyperparameters}")

        if result:
            return TestCaseResult.model_validate_json(result[0])
        return None

    def __del__(self):
        """Close the database connection when the object is destroyed."""
        if self._conn:
            self._conn.close()


# Example usage with context manager
@dataclass
class StoreContextManager:
    db_path: str

    def __enter__(self):
        self.store = Store(self.db_path)
        return self.store

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.store, '_conn'):
            self.store._conn.close()