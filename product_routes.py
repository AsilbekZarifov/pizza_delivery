from fastapi import APIRouter
from fastapi_jwt_auth import AuthJWT
from models import User, Product
from schemas import ProductModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException


product_router = APIRouter(
    prefix='/product'
)
session = session(bind=engine)

@product_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, Authorize: AuthJWT=Depends()):

    # create a new product endpoint
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        new_product = Product(
            name=product.name,
            price=product.price
        )

        session.add(new_product)
        session.commit()
        data = {
            "success": True,
            "code": 201,
            "message": "Product is created successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price
            }
        }
        return jsonable_encoder(data)

    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can add new product")




@product_router.get('/list', status_code=status.HTTP_200_OK)
async def list_all_product(id: ProductModel, Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        products = session.query(Product).all()
        product_data = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]
        return jsonable_encoder(product_data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can see all products")


@product_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_product_by_id(id: int, Authorize: AuthJWT=Depends()):
    # get an order by id
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:

            product_data = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }

            return jsonable_encoder(product_data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with {id} ID is not found")


    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only super admin is allowed to this request")


@product_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(id: int, Authorize: AuthJWT=Depends()):
    # delete an order by id
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            session.delete(product)
            session.commit()
            data = {
                "success": True,
                "code": 204,
                "message": f"Product with ID {id} is has been deleted",
                "data": None
            }

            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with {id} ID is not found")

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Super admin can deleted")


@product_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_product_by_id(id: int, update_data: ProductModel, Authorize: AuthJWT=Depends()):
    # update an order by id
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            for key, value in update_data.dict(exclude_unset=True).items():
                setattr(product, key, value)
            session.commit()
            data = {
                "success": True,
                "code": 204,
                "message": f"Product with ID {id} is has been updated",
                "data": {
                    "product_id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Product with {id} ID is not found")

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only Super admin can updated")


