"""roles

Revision ID: b875511063f0
Revises: 96bbc9c949ce
Create Date: 2025-11-04 01:03:40.467462

"""

""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b875511063f0"
down_revision: Union[str, Sequence[str], None] = "96bbc9c949ce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    participantrole_enum = postgresql.ENUM(
        "owner", "admin", "member", name="participantrole"
    )
    participantrole_enum.create(op.get_bind(), checkfirst=True)

    chattype_enum = postgresql.ENUM("personal", "group", name="chattype")
    chattype_enum.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        "chat_participants",
        "role",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.Enum("owner", "admin", "member", name="participantrole"),
        postgresql_using="role::participantrole",
    )

    op.execute("UPDATE chat_participants SET role = 'member' WHERE role IS NULL;")

    # 4️⃣ Теперь можно безопасно сделать колонку NOT NULL
    op.alter_column("chat_participants", "role", nullable=False)

    op.add_column(
        "chats", sa.Column("created_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.alter_column(
        "messages",
        "timestamp",
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "messages",
        "timestamp",
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True,
    )

    op.drop_column("chats", "created_at")

    op.alter_column(
        "chat_participants",
        "role",
        existing_type=sa.Enum("owner", "admin", "member", name="participantrole"),
        type_=sa.VARCHAR(length=50),
        postgresql_using="role::text",
        nullable=True,
    )

    op.execute("DROP TYPE IF EXISTS participantrole CASCADE;")
    op.execute("DROP TYPE IF EXISTS chattype CASCADE;")
