from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from operations import save_redis, get_redis, exist_redis

from typing import Callable, Dict, Union, Iterable, List

import uvicorn

app = FastAPI()


class Order(BaseModel):
    id: int
    item: str
    quantity: int
    price: float
    status: str


class SolutionData(BaseModel):
    orders: List[Order]
    criterion: str


# Validation

# ID
def get_order_id(order: Order) -> int:
    return order.id


def validate_ids(ids: Iterable[int]) -> bool:
    return len(set(ids)) == len(ids)


def validate_orders_id(orders: Iterable[Order]) -> bool:
    return validate_ids(list(map(get_order_id, orders)))


# Quantity
def get_order_quantity(order: Order) -> int:
    return order.quantity


def validate_quantity(quantity: int) -> bool:
    return quantity >= 0


def validate_orders_quatity(orders: Iterable[int]) -> bool:
    return all(map(validate_quantity, map(get_order_quantity, orders)))


# Price
def get_order_price(order: Order) -> float:
    return order.price


def validate_price(price: float) -> bool:
    return price >= 0


def validate_orders_price(orders: Iterable[int]) -> bool:
    return all(map(validate_price, map(get_order_price, orders)))


# Status
def get_order_status(order: Order) -> str:
    return order.status


def validate_status(status: str) -> bool:
    return status in ["completed", "pending", "canceled"]


def validate_orders_status(orders: Iterable[Order]) -> bool:
    return all(map(validate_status, map(get_order_status, orders)))


# Criterion
def validate_criterion(criterion: str) -> bool:
    return criterion == "all" or validate_status(criterion)


# Validate data
def validate(data: SolutionData) -> Union[Dict[str, str], None]:
    orders: Iterable[Order] = data.orders

    if not validate_orders_id(orders):
        return {"message": "There are two items with the same id"}

    if not validate_orders_quatity(orders):
        return {"message": "There is an item with negative quantity"}

    if not validate_orders_price(orders):
        return {"message": "There is an item with negative price"}

    if not validate_orders_status(orders):
        return {"message": "There is an item with bad status"}

    if not validate_criterion(data.criterion):
        return {"message": "Bad criterion"}


def wrapper(criterion: str) -> Callable[[Order], bool]:
    func: Callable[[Order], bool] = (
        lambda order: True if criterion == "all" else order.status == criterion
    )
    return func


def get_order_total_cost(order: Order):
    return order.quantity * order.price


def solve(data: SolutionData) -> float:
    orders: List[Order] = data.orders
    fn = wrapper(data.criterion)

    total = sum(map(get_order_total_cost, filter(fn, orders)))

    return total


def save_to_cache(orders: List[Order], total: float):
    ids = list(map(get_order_id, orders))
    ids.sort()
    save_redis(str(ids), total)


def retrive_from_cache(orders: List[Order]):
    ids = list(map(get_order_id, orders))
    ids.sort()
    if exist_redis(str(ids)):
        return get_redis(str(ids))


@app.post("/solution")
async def solution(data: SolutionData, response: Response):
    validation: Union[Dict[str, str], None] = validate(data)
    if validation:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return validation

    cache_value = retrive_from_cache(data.orders)
    if cache_value:
        return cache_value

    total = solve(data)
    save_to_cache(data.orders, total)
    return total
