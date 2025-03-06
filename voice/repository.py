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


def add_user_to_db(embedding: np.ndarray,user_name:str | None, conn: connection):
    register_vector(conn)
    with conn.cursor() as cur:
        if user_name:
            cur.execute(
                "INSERT INTO users (id, name, voice_embedding) VALUES (%s,%s,%s) RETURNING id",
                (str(uuid.uuid4()), user_name, embedding),
            )
        else:
            cur.execute(
                "INSERT INTO users (id, voice_embedding) VALUES (%s,%s) RETURNING id",
                (str(uuid.uuid4()), embedding),
            )
        user_id = cur.fetchone()
        conn.commit()

    return user_id[0] if user_id else None
