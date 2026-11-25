import os

from sqlalchemy import select
from dotenv import load_dotenv

from app.database import SessionLocal
from app.models.user import User
from app.security.password import hash_password


load_dotenv()


DEMO_USERS = [
    {
        "full_name": "Ayşe Yılmaz",
        "email": "dogrulanmis@ornek.edu.tr"
    },
    {
        "full_name": "Deniz Kaya",
        "email": "deniz@ornek.edu.tr"
    }
]


def seed_demo_users():
    password = os.getenv("DEMO_USER_PASSWORD")

    if not password or not 8 <= len(password) <= 128:
        raise RuntimeError(
            "DEMO_USER_PASSWORD must be between "
            "8 and 128 characters."
        )

    db = SessionLocal()
    added_count = 0
    skipped_count = 0

    try:
        for demo_user in DEMO_USERS:
            existing_user = db.scalar(
                select(User).where(
                    User.email == demo_user["email"]
                )
            )

            if existing_user is not None:
                skipped_count += 1
                continue

            user = User(
                full_name=demo_user["full_name"],
                email=demo_user["email"],
                password_hash=hash_password(password),
                is_verified=True,
                is_admin=False
            )

            db.add(user)
            added_count += 1

        db.commit()

        print(f"{added_count} demo users added.")
        print(f"{skipped_count} existing users skipped.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_users()