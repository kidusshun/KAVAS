import uuid
import numpy as np
from scipy.spatial.distance import cosine
from psycopg2.extensions import connection

import psycopg2
from pgvector.psycopg2 import register_vector


def identify_user(embedding: np.ndarray, conn: connection) -> str | None:
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute(
            f"SELECT id,name, voice_embedding <=> %s AS similarity FROM users ORDER BY similarity LIMIT %s",
            (embedding, 1),
        )

        result = cur.fetchone()

    if result is None:
        return None
    if result[2] < 0.6:  # Adjust threshold as needed
        return result[0]
    else:
        return None


def add_user_to_db(embedding: np.ndarray,user_id:uuid.UUID, conn: connection):
    register_vector(conn)
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (id, voice_embedding) VALUES (%s,%s) RETURNING id",
            (str(user_id), embedding),
        )
        user = cur.fetchone()
        conn.commit()

    return (user[0],user[2]) if user else None
