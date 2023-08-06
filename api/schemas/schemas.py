from pydantic import UUID4, BaseModel


class MenuSchema(BaseModel):
    title: str
    description: str
    submenus_count: int | None = 0
    dishes_count: int | None = 0

    class Config:
        from_attributes = True


class MenuSchemaWithID(MenuSchema):
    id: UUID4


class CreateMenu(MenuSchemaWithID):
    submenus_count: int | None = 0
    dishes_count: int | None = 0


class UpdateMenu(MenuSchemaWithID):
    submenus_count: int | None = 0
    dishes_count: int | None = 0


class SubmenuSchema(BaseModel):
    title: str
    description: str


class SubmenuSchema2(BaseModel):
    title: str
    description: str | None = None
    dishes_count: int | None = 0

    class Config:
        from_attributes = True


class SubmenuSchemaWithID(SubmenuSchema2):
    id: UUID4
    menu_id: UUID4


class CreateSubMenu(SubmenuSchema2):
    id: UUID4


class UpdateSubmenu(BaseModel):
    title: str
    description: str
    dishes_count: int | None = 0


class DishSchema(BaseModel):
    price: str
    title: str
    description: str

    class Config:
        from_attributes = True


class DishesReturn(BaseModel):
    id: UUID4
    title: str
    description: str | None
    price: str

    class Config:
        from_attributes = True


class DishesWithID(DishesReturn):
    id: UUID4
    submenu_id: UUID4


class CreateDish(BaseModel):
    id: UUID4
    price: str
    title: str
    description: str

    class Config:
        from_attributes = True


class UpdateDishes(BaseModel):
    id: UUID4
    price: str
    title: str
    description: str

    class Config:
        from_attributes = True
