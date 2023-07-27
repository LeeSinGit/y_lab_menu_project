from db.database import Base, engine
from models.models import Dish, Menu, Submenu


print('Creating DB ...')

Base.metadata.create_all(engine)
