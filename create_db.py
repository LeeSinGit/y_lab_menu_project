from database import Base, engine
from models import Dish, Menu, Submenu


print('Creating DB ...')

Base.metadata.create_all(engine)
