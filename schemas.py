from typing import Optional

from pydantic import UUID4, BaseModel


class MenuSchema(BaseModel):
    title: str
    description: str

    class Config:
        from_attributes = True


class SubmenuSchema(BaseModel):
    title: str
    description: Optional[str] = None
    dishes_count: Optional[int] = 0
    menu_id: Optional[str] = None

    class Config:
        from_attributes = True


class SubmenuSchema2(BaseModel):
    title: str
    description: Optional[str] = None
    dishes_count: Optional[int] = 0
    menu_id: Optional[UUID4] = None

    class Config:
        from_attributes = True


class DishSchema(BaseModel):
    price: str
    title: str
    description: str

    class Config:
        from_attributes = True


class DishesReturn(BaseModel):
    title: str
    description: Optional[str]
    price: str
    id: UUID4

    class Config:
        from_attributes = True
