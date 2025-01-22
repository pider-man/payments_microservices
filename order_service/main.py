"""
FastAPI application for Order Service
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from bson import ObjectId
from datetime import datetime
from typing import Optional, List
import uvicorn

from shared.models.order import (
    OrderCreate,
    OrderResponse,
    OrderUpdate,
    OrderStatus,
)
from shared.utils.responses import (
    APIResponse,
    validation_exception_handler,
    http_exception_handler,
    general_exception_handler
)
from database import db
from config import settings
from user_service import verify_user_token


@asynccontextmanager
async def lifespan(app_: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting up...")
    await db.connect_db()

    yield  # Server is running and handling requests

    # Shutdown
    print("Shutting down...")
    await db.close_db()

app = FastAPI(
    title="Order Service",
    version="1.0.0",
    description="Order management microservice",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


async def get_current_user(authorization: str = Header(...)):
    """
    Verify user token and get current user information.
    """
    scheme, token = authorization.split()
    if scheme.lower() != 'bearer':
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    return await verify_user_token(token)


@app.post("/orders/createOrder", response_model=OrderResponse, status_code=201)
async def create_order(
        order: OrderCreate,
        current_user: dict = Depends(get_current_user)
):
    """
    Create a new order
    """
    database = await db.get_database()
    total_amount = sum(item.price_per_unit * item.quantity for item in order.items)
    order_dict = order.model_dump()
    order_dict.update({
        "status": OrderStatus.PENDING,
        "total_amount": total_amount,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "user_id": current_user["id"]
    })

    result = await database.orders.insert_one(order_dict)
    order_dict["id"] = str(result.inserted_id)

    return OrderResponse(**order_dict)


@app.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: str,
        current_user: dict = Depends(get_current_user)
):
    """
    Get order by ID.
    """
    database = await db.get_database()
    order = await database.orders.find_one({
        "_id": ObjectId(order_id),
        "user_id": current_user["id"]
    })

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    order["id"] = str(order.pop("_id"))
    return OrderResponse(**order)


@app.put("/orders/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: str,
    order_update: OrderUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update order status or shipping address.
    """
    database = await db.get_database()

    # Get existing order
    order = await database.orders.find_one({
        "_id": ObjectId(order_id),
        "user_id": current_user["id"]
    })

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Update order
    update_data = order_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.now()

    await database.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )

    # Get updated order
    updated_order = await database.orders.find_one({"_id": ObjectId(order_id)})
    updated_order["id"] = str(updated_order.pop("_id"))

    return OrderResponse(**updated_order)


@app.get("/orders/", response_model=List[OrderResponse])
async def list_orders(
    current_user: dict = Depends(get_current_user),
    status: Optional[OrderStatus] = None
):
    """
    List all orders for the current user, optionally filtered by status.
    """
    database = await db.get_database()

    # Build query
    query = {"user_id": current_user["id"]}
    if status:
        query["status"] = status

    # Fetch orders
    orders = []
    async for order in database.orders.find(query):
        order["id"] = str(order.pop("_id"))
        orders.append(OrderResponse(**order))

    return orders

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.service_port, reload=True)
