from database import SessionLocal, init_db
from seed_data import seed_demo_data


if __name__ == "__main__":
    init_db()
    with SessionLocal() as db:
        seed_demo_data(db)
    print("DataPulse database initialized.")
