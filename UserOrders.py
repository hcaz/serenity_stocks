import time
from AtlasClient import getClient
from UserOrder import UserOrder

orders_collection = getClient().get_collection("serenity_stocks", "user_orders")
stocks_collection = getClient().get_collection("serenity_stocks", "stocks")

def get_open_orders(email: str):
    orders = []
    cursor = orders_collection.find({
        "email": email,
        "completed_at": None,
    })
    cursor = list(cursor)
    for document in cursor:
        orders.append(UserOrder(**document))
    return orders

def add_order(order: UserOrder):
    order_dict = order.dict()
    order_dict["created_at"] = time.time()
    result = orders_collection.insert_one(order_dict)
    print(result)
    return UserOrder(**order_dict)

def compute_open_orders():
    all_open_orders = orders_collection.find({
        "completed_at": None,
    })
    all_open_orders = list(all_open_orders)

    all_stocks = stocks_collection.find({})
    all_stocks = list(all_stocks)

    for order in all_open_orders:
        print(order)