from concurrent import futures
import threading
import secrets
import logging
import sys

import grpc
import service_store_pb2
import service_store_pb2_grpc
import service_bank_pb2_grpc

from service_store_pb2 import PriceReply as setPrice
from service_store_pb2 import SellReply as setSell
from service_store_pb2 import CloseStoreReply as closeStore

from service_bank_pb2 import BalanceRequest as getBalance
from service_bank_pb2 import TransactionRequest as getTransaction

ERROR_MESSAGE = -9

class Store(service_store_pb2_grpc.StoreServicer):
    def __init__(self, product_price, name_wallet, bank_stub, stop_event):
        self.price = product_price
        self.wallet = name_wallet
        self.bankStub = bank_stub
        self.stopEvent = stop_event

        res = self.bankStub.Balance(getBalance(wallet = self.wallet))
        self.balance = res.amount

    def Price(self, request, context):
        return setPrice(price = self.price)

    def Sell(self, request, context):
        res = self.bankStub.Transaction(getTransaction(amount = self.price,
                                                       order = request.order,
                                                       wallet = self.wallet))
        if res.returnValueOrCode < 0:
            return setSell(returnValueOrCode = ERROR_MESSAGE)
        else:
            self.balance = res.returnValueOrCode
            return setSell(returnValueOrCode = res.returnValueOrCode)

    def CloseStore(self, request, context):
        self.stopEvent.set()
        return closeStore(storeBalance = self.balance)

def serve(price, port, wallet, bankAddress):
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    channel = grpc.insecure_channel(bankAddress)
    bankStub = service_bank_pb2_grpc.BankStub(channel)
    store = Store(price, wallet, bankStub, stop_event)

    service_store_pb2_grpc.add_StoreServicer_to_server(store, server)

    server.add_insecure_port('[::]:'+str(port))
    server.start()
    stop_event.wait()
    #server.wait_for_termination()
    server.stop(1)


if __name__ == '__main__':
    logging.basicConfig()

    if len(sys.argv) != 5:
        print("Usage: python3 src/server_store.py price port wallet bankAddress")
        sys.exit(0)

    price = int(sys.argv[1])
    port = int(sys.argv[2])
    wallet = sys.argv[3]
    bankAddress = sys.argv[4]

    serve(price, port, wallet, bankAddress)
