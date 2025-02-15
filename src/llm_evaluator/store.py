import logging
from dataclasses import dataclass
from typing import Optional
import duckdb

from llm_evaluator import TestCase
from llm_evaluator.schema import TestCaseResult, Response, Suite

logger = logging.getLogger(__name__)

def unique_key(suite: Suite, case: TestCase, hyperparameters: dict) -> tuple:
    """Generate a unique key for a test result."""
    suite_name = suite.name
    if suite.version:
        suite_name += f"--{suite.version}"

    def empty(v):
        return v is None or (isinstance(v, (str, list, dict)) and not v)
    return suite_name, case.input, case.ideal or "", {k: v for k, v in hyperparameters.items() if not empty(v)}



@dataclass
class Store:
    """A persistent store using DuckDB to cache test results with JSON support for Pydantic models.

    Example:

        >>> store = Store("test-cache.db")
        >>> case = TestCase(input="1+1", ideal="2")
        >>> suite = Suite(name="test", cases=[case], matrix={"hyperparameters": {}})
        >>> response = Response(text="2")
        >>> result = TestCaseResult(case=case, response=response, hyperparameters={"model": "gpt-4"})
        >>> store.add_result(suite, result)
        >>> cached = store.get_result(suite, case, {"model": "gpt-4"})
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
                test_case VARCHAR,
                ideal VARCHAR,
                hyperparameters JSON,
                result JSON,
                PRIMARY KEY (suite_name, test_case, ideal, hyperparameters)
            )
        """)

    def add_result(self, suite: Suite, result: TestCaseResult):
        """Add a result to the store."""
        self._conn.execute("""
            INSERT OR REPLACE INTO results 
            (suite_name, test_case, ideal, hyperparameters, result)
            VALUES (?, ?, ?, ?, ?)
        """, (
            *unique_key(suite, result.case, result.hyperparameters),
            result.model_dump_json(exclude_unset=True),
        ))
        logger.debug(f"Added result for {suite.name} {result.case} {result.hyperparameters}")
        self._conn.commit()

    def get_result(self, suite: Suite, case: TestCase, hyperparameters: dict) -> Optional[TestCaseResult]:
        """Get a result from the store."""
        result = self._conn.execute("""
            SELECT result
            FROM results
            WHERE suite_name = ?
            AND test_case = ?
            AND ideal = ?
            AND hyperparameters = ?
        """, (
            *unique_key(suite, case, hyperparameters),
        )).fetchone()

        logger.debug(f"Present: {result is not None} when looking up {suite.name} {case} {hyperparameters}")

        if result:
            return TestCaseResult.model_validate_json(result[0])
        return None

    @property
    def size(self) -> int:
        """Get the number of results in the store."""
        return self._conn.execute("SELECT COUNT(*) FROM results").fetchone()[0]

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
