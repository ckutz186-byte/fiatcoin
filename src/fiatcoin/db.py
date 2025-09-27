import sqlite3
from typing import Optional


class Database:
    def __init__(self, path: str = "kv_store.db"):
        self.conn = sqlite3.connect(path)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value BLOB
            )
        """)
        self.conn.commit()

    def put(self, key: str, value: bytes) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
            (key, value),
        )
        self.conn.commit()

    def get(self, key: str) -> Optional[bytes]:
        cur = self.conn.execute(
            "SELECT value FROM kv_store WHERE key = ?",
            (key,),
        )
        row = cur.fetchone()
        return row[0] if row else None

    def delete(self, key: str) -> None:
        self.conn.execute(
            "DELETE FROM kv_store WHERE key = ?",
            (key,),
        )
        self.conn.commit()

    def exists(self, key: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM kv_store WHERE key = ?",
            (key,),
        )
        return cur.fetchone() is not None

    def keys(self) -> list[str]:
        cur = self.conn.execute("SELECT key FROM kv_store")
        return [row[0] for row in cur.fetchall()]

    def values(self) -> list[bytes]:
        cur = self.conn.execute("SELECT value FROM kv_store")
        return [row[0] for row in cur.fetchall()]

    def items(self) -> list[tuple[str, bytes]]:
        cur = self.conn.execute("SELECT key, value FROM kv_store")
        return [(row[0], row[1]) for row in cur.fetchall()]

    def clear(self) -> None:
        self.conn.execute("DELETE FROM kv_store")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()