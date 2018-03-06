import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(80), nullable=False)
    picture = Column('picture', String(80), nullable=False)
    email = Column('email', String(80))

    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name': self.name,
            'picture': self.picture,
            'email': self.email
        }


class Restaurant(Base):
    __tablename__ = 'restaurant'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # returns object data in easily serializeable format
        return {
            'name' : self.name,
            'id' : self.id
        }




class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    image = Column(String(300))
    restaurant = relationship(Restaurant)
    user = relationship(User)

    @property
    def serialize(self):
        # returns object data in easily serializeable format
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            'price' : self.price,
            'course' : self.course
            }

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
