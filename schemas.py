from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]


    class Config:
        from_attributes = True
        json_schema_extra = {
            'example': {
                "username": "mohirdev",
                "email": "mohirdev@gmail.com",
                "password": "password12345",
                "is_staff": False,
                "is_active": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str ='85915e7dd09745cbe8469e2927dfeaff51554e24ccfad05af749bd5303457977'


class LoginModel(BaseModel):
    username_or_email: str
    password: str


class OrderModel(BaseModel):
    id: Optional[int]
    quantity: int
    order_status: Optional[str] = "PENDING"
    user_id: Optional[int]
    product_id: int


    class Config:
        from_attributes = True
        json_schema_extra = {
            "exaple": {
                "quantity": 2
            }
        }


class OrderStatusModel(BaseModel):
    order_status: Optional[str] = "PENDING"

    class Config:
        from_attributes = True
        json_schema_extra = {
            "exaple": {
                "order_status": "PENDING"
            }
        }


class ProductModel(BaseModel):
    id: Optional[int]
    name: str
    price: int

    class Config:
        from_attributes = True
        json_schema_extra = {
            "exaple": {
                "name": "uzbekplov",
                "price": 50000
            }
        }


