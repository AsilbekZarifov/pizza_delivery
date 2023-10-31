from fastapi import APIRouter
from fastapi_jwt_auth import AuthJWT
from models import User, Product, Order
from schemas import OrderStatusModel, OrderModel
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException


order_router = APIRouter(
    prefix='/order'
)
session = session(bind=engine)


@order_router.get('/')
async def welcome_page(Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    return {"message": "Bu order route sahifasi"}

@order_router.post('/make', status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        quantity=order.quantity,
        product_id=order.product_id

    )
    new_order.user = user
    session.add(new_order)
    session.commit()
    data = {
        "success": True,
        "code": 201,
        "message": "Order is created successfully",
        "data": {
                "id": new_order.id,
                "product": {
                    "id": new_order.product.id,
                    "name": new_order.product.name,
                    "price": new_order.product.price
                },
                "quantity": new_order.quantity,
                "order_status": new_order.order_status,
                "total_price": new_order.quantity * new_order.product.price
            }
    }

    return jsonable_encoder(data)

@order_router.get('/list')
async def list_all_order(Authorize: AuthJWT=Depends()):

    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username == current_user).first()

    if user.is_staff:
        orders = session.query(Order).all()
        custom_data = [
            {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product_id": order.product_id,
                "quantity": order.quantity,
                "order_status": order.order_status.value
            }
            for order in orders
        ]

        return jsonable_encoder(custom_data)

    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="ONLY SuperAdmin can see all orders")



@order_router.get('/{id}')
async def get_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    # get an order by id
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    user = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            custom_order = {
                    "id": order.id,
                    "user": {
                        "id": order.user.id,
                        "username": order.user.username,
                        "email": order.user.email
                    },
                    "product_id": order.product_id,
                    "quantity": order.quantity,
                    "order_status": order.order_status.value
                }

            return jsonable_encoder(custom_order)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Order with {id} ID is not found")

    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Only sper admin is allowed to this request ")

@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_orders(Authorize: AuthJWT=Depends()):
    # get a  user's orders
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")

    username = Authorize.get_jwt_subject()
    print(username)
    user = session.query(User).filter(User.username == username).first()

    # custom_data = [
    #     {
    #         "id": order.id,
    #         "user": {
    #             "id": order.user.id,
    #             "username": order.user.username,
    #             "email": order.user.email
    #         },
    #         "product": {
    #             "id": order.product.id,
    #             "name": order.product.name,
    #             "price": order.product.price
    #         },
    #         "quantity": order.quantity,
    #         "order_status": order.order_status.value
    #     }
    #     for order in user.orders
    # ]

    return jsonable_encoder(user.orders)

@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_specific_order(id:int, Authorize:AuthJWT=Depends()):

    """
        ## Get a specific order by the currently logged in user
        This returns an order by ID for the currently logged in user
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )

    subject=Authorize.get_jwt_subject()

    current_user=session.query(User).filter(User.username==subject).first()

    orders=current_user.orders

    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail='NO order with such id'
    )

@order_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_order(id: int, order: OrderModel, Authorize:AuthJWT=Depends()):
    """Updating user order by fields: quantity and product_id"""
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid Token'
        )
    subject=Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == subject).first()
    order_to_update = session.query(Order).filter(Order.id == id).first()
    if order_to_update.user !=current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not update other users's order")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    data = {
        "success": True,
        "code": 200,
        "message": "Sizning buyurtmangiz muvaffaqiaytli o'rgartirildi",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_Statsus": order.order_status
        }
    }

    return jsonable_encoder(data)


@order_router.patch('/order/update/{id}/')
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    """
        ## Update an order's status
        This is for updating an order's status and requires 'order_status' in str format

    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid Token'
                            )

    username = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()

        order_to_update.order_status = order.order_status

        session.commit()

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status,
        }

        return jsonable_encoder(response)


@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def update_order_status(id: int, Authorize: AuthJWT = Depends()):
    """
        ## Delete an Order
        This deletes an order by its ID

    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Invalid Token'
                            )

    order_to_delete = session.query(Order).filter(Order.id == id).first()

    session.delete(order_to_delete)

    session.commit()

    return order_to_delete