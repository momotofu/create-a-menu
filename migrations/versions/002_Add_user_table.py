from sqlalchemy import *
from migrate import *

meta = MetaData()

user = Table(
    'user',
    meta,
    Column('id', Integer, primary_key=True),
    Column('name', String(80), nullable=False),
    Column('email', String(80), nullable=False),
    Column('picture', String(80))
    )

def upgrade(migrate_engine):
    meta.bind = migrate_engine
    user.create()

def downgrade(migrate_engine):
    meta.bind = migrate_engine
    user.drop()
