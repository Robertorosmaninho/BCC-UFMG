from concurrent import futures
import threading
import secrets
import logging
import sys

import grpc
import service_bank_pb2_grpc

from service_bank_pb2 import BalanceReply as setBalance
from service_bank_pb2 import PaymentOrderReply as setPaymentOrder
from service_bank_pb2 import TransactionReply as setTransaction
from service_bank_pb2 import CloseBankReply as closeBankWithMessage


class Bank(service_bank_pb2_grpc.BankServicer):
    def __init__(self, wallets_file, stop_event):
        self.wallets = {}
        self.orders = {}
        self.stopEvent = stop_event
        self.walletsFile = wallets_file
        with open(self.walletsFile) as f:
            for line in f:
                (wallet, balance) = line.split()
                self.wallets[wallet] = int(balance)

    def Balance(self, request, context):
        if request.wallet not in self.wallets:
            return setBalance(amount = -1)
        else:
            return setBalance(amount = self.wallets[request.wallet])

    def PaymentOrder(self, request, context):
        if request.wallet not in self.wallets:
            return setPaymentOrder(resultCode = -1, order = b'')
        elif request.amount > self.wallets[request.wallet]:
            return setPaymentOrder(resultCode = -2, order = b'')
        else:
            self.wallets[request.wallet] -= request.amount
            orderVec = secrets.token_bytes(32)
            self.orders[orderVec] = request.amount
            return setPaymentOrder(resultCode = 0, order = orderVec)

    def Transaction(self, request, context):
        if request.wallet not in self.wallets:
            return setTransaction(returnValueOrCode = -1)
        elif request.order not in self.orders:
            return setTransaction(returnValueOrCode = -2)
        elif request.amount != self.orders[request.order]:
            return setTransaction(returnValueOrCode = -3)
        else:
            del self.orders[request.order]
            self.wallets[request.wallet] += request.amount
            return setTransaction(
                returnValueOrCode = self.wallets[request.wallet])

    def CloseBank(self, request, context):
        with open(self.walletsFile, "w") as f:
            for wallet, amount in self.wallets.items():
                f.write('%s %s\n' % (wallet, str(amount)))

        self.stopEvent.set()
        return closeBankWithMessage(savedAccounts = len(self.wallets))


def serve(port, walletsFile):
    stop_event = threading.Event()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_bank_pb2_grpc.add_BankServicer_to_server(
                                Bank(walletsFile, stop_event), server)
    server.add_insecure_port('[::]:'+str(port))
    server.start()
    stop_event.wait()
    #server.wait_for_termination()
    server.stop(1)


if __name__ == '__main__':
    logging.basicConfig()

    if len(sys.argv) != 3:
        print("Usage: python3 src/server_bank.py port walletsFile")
        sys.exit(0)

    port = int(sys.argv[1])
    walletsFile = sys.argv[2]

    serve(port, walletsFile)
