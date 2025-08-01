"""Booking start and end time and booking date data types updated.

Revision ID: 4d0becc63ea2
Revises: 2ea7f4a9a7ed
Create Date: 2025-07-22 14:36:21.835472

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '4d0becc63ea2'
down_revision = '2ea7f4a9a7ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.alter_column('start_time',
               existing_type=mysql.DATETIME(),
               type_=sa.Time(),
               existing_nullable=False)
        batch_op.alter_column('end_time',
               existing_type=mysql.DATETIME(),
               type_=sa.Time(),
               existing_nullable=False)
        batch_op.alter_column('booking_date',
               existing_type=mysql.DATETIME(),
               type_=sa.Date(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.alter_column('booking_date',
               existing_type=sa.Date(),
               type_=mysql.DATETIME(),
               existing_nullable=False)
        batch_op.alter_column('end_time',
               existing_type=sa.Time(),
               type_=mysql.DATETIME(),
               existing_nullable=False)
        batch_op.alter_column('start_time',
               existing_type=sa.Time(),
               type_=mysql.DATETIME(),
               existing_nullable=False)

    # ### end Alembic commands ###
