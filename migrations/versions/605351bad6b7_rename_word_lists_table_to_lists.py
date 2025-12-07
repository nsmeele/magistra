"""Rename word_lists table to lists

Revision ID: 605351bad6b7
Revises: fdaed3f806f3
Create Date: 2025-12-07 14:53:38.521650

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '605351bad6b7'
down_revision = 'fdaed3f806f3'
branch_labels = None
depends_on = None


def upgrade():
    # Rename table instead of drop/create to preserve data and constraints
    op.rename_table('word_lists', 'lists')


def downgrade():
    # Rename table back to original name
    op.rename_table('lists', 'word_lists')
