from sqlalchemy import Table, MetaData, String, Column
from migrate import *


def upgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    menu_item = Table('menu_item', meta, autolaod=True)
    image_col = Column('image', String(300))
    image_col.create(menu_item)


def downgrade(migrate_engine):
    meta = MetaData(bind=migrate_engine)
    menu_item = Table('menu_item', meta, autoload=True)
    menu_item.c.image.drop()
