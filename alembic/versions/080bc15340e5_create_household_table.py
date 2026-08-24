"""create household table

Revision ID: 080bc15340e5
Revises: 072568cc4f38
Create Date: 2026-08-22 18:50:05.896484

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "080bc15340e5"
down_revision: str | Sequence[str] | None = "072568cc4f38"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "household",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_household")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("household")
