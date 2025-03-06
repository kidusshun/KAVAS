import uuid
import numpy as np
from .utils import preprocess_audio, get_speaker_embedding
from scipy.spatial.distance import cosine
from sqlalchemy.orm import Session
from sqlalchemy import text

import psycopg2
from pgvector.psycopg2 import register_vector


# Function to compare embeddings
def identify_speaker(known_embeddings, test_embedding) -> tuple[str, float]:
    min_distance = float("inf")
    identified_user = "unknown"

    for user_id, stored_embedding in known_embeddings.items():
        distance = cosine(stored_embedding, test_embedding)
        if distance < min_distance:
            min_distance = distance
            identified_user = user_id

    return (
        identified_user if min_distance < 0.3 else "Unknown"
    ), min_distance  # Adjust threshold


def identify_user(embedding: np.ndarray, db: Session) -> str | None:
    with psycopg2.connect(
        database="kavas",
        user="root",
        password="123456789",
        host="localhost",
        port="8502",
    ) as conn:
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


def add_user_to_db(embedding: np.ndarray,user_name:str | None, db: Session):
    with psycopg2.connect(
        database="kavas",
        user="root",
        password="123456789",
        host="localhost",
        port="8502",
    ) as conn:
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

    return user_id
