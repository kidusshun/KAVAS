import uuid
import numpy as np
from .utils import preprocess_audio, get_speaker_embedding
from scipy.spatial.distance import cosine
from sqlalchemy.orm import Session
from sqlalchemy import text

import psycopg2
from pgvector.psycopg2 import register_vector


known_users = {
    "kidus": get_speaker_embedding(
        preprocess_audio(
            "C:/Users/Kidus/Documents/code/kifiya/KAVAS/experiments/kidus.wav"
        )
    ),
    "ephrem": get_speaker_embedding(
        preprocess_audio(
            "C:/Users/Kidus/Documents/code/kifiya/KAVAS/experiments/ephrem.wav"
        )
    ),
    "kalkidan": get_speaker_embedding(
        preprocess_audio(
            "C:/Users/Kidus/Documents/code/kifiya/KAVAS/experiments/kal_2.wav"
        )
    ),
    "tinsae": get_speaker_embedding(
        preprocess_audio(
            "C:/Users/Kidus/Documents/code/kifiya/KAVAS/experiments/tinsae.wav"
        )
    ),
    "leul": get_speaker_embedding(
        preprocess_audio(
            "C:/Users/Kidus/Documents/code/kifiya/KAVAS/experiments/leul.wav"
        )
    ),
}


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


def identify_user(embedding: np.ndarray, db: Session) -> str:
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
                f"SELECT id, voice_embedding <=> %s AS similarity FROM users ORDER BY similarity LIMIT %s",
                (embedding, 1),
            )

            result = cur.fetchone()

    if result is None:
        return "Unknown"
    if result[1] < 0.3:  # Adjust threshold as needed
        user = result[0]
    else:
        user = "Unknown"
    return user


def add_user_to_db(embedding: np.ndarray, db: Session):
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
                "INSERT INTO users (id, voice_embedding) VALUES (%s,%s) RETURNING id",
                (str(uuid.uuid4()), embedding),
            )
            user_id = cur.fetchone()
            conn.commit()

    return user_id
