"""alter users.role enum to include advisor

Revision ID: ec94cbd87b5f
Revises: 50fcd2931fbf
Create Date: 2025-10-30 11:19:34.220969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ec94cbd87b5f'
down_revision = '50fcd2931fbf'
branch_labels = None
depends_on = None


def upgrade():
    # Ajusta el ENUM de MySQL para incluir 'advisor'
    # Nota: Alembic no detecta cambios en ENUM automáticamente en MySQL,
    # por eso aplicamos un ALTER manual.
    op.execute("ALTER TABLE users MODIFY COLUMN role ENUM('admin','client','advisor') NOT NULL")


def downgrade():
    # Revertir a ENUM original sin 'advisor'
    op.execute("ALTER TABLE users MODIFY COLUMN role ENUM('admin','client') NOT NULL")
