from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def get_or_create_guest_user(db: Session, display_name: str) -> User:
    # No auth/session mechanism yet, so display_name is the only identity key
    # available. This means guests are deduped by name (not scoped per room),
    # which is a stand-in until real sessions/auth replace this.
    user = db.execute(
        select(User).where(User.display_name == display_name, User.is_guest.is_(True))
    ).scalar_one_or_none()
    if user is not None:
        return user

    user = User(display_name=display_name, is_guest=True)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
