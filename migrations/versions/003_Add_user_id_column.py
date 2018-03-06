from sqlalchemy import *
from migrate import *
from sqlalchemy.orm import relationship

import sys
sys.path.append('../../database_setup.py')
from database_setup import User


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    menu_item = Table('menu_item', meta, autoload=True)
    restaurant = Table('restaurant', meta, autoload=True)
    user_id_col = Column('user_id', Integer, ForeignKey('user.id'))

    user_id_col.create(restaurant)
    user_id_col.create(menu_item)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    menu_item = Table('menu_item', meta, autoload=True)
    restaurant = Table('restaurant', meta, autoload=True)

    restaurant.c.user_id.drop()
    menu_item.c.user_id.drop()
