from __future__ import print_function

import logging
import sys

import grpc
import service_bank_pb2_grpc

from service_bank_pb2 import BalanceRequest as getBalance
from service_bank_pb2 import PaymentOrderRequest as getPaymentOrder
from service_bank_pb2 import TransactionRequest as getTransaction
from service_bank_pb2 import CloseBankRequest as closeBank

ERROR_MESSAGE = -9

class ClientBank:
    def __init__(self, client_wallet, bank_stub):
        self.client = client_wallet
        self.stub = bank_stub
        self.orders = {}
        self.ordersCount = 1


    def balance(self):
        response = self.stub.Balance(getBalance(wallet = self.client))
        print(response.amount)


    def paymentOrder(self, value):
        response = self.stub.PaymentOrder(getPaymentOrder(wallet = self.client,
                                                          amount = value))
        if response.resultCode == 0:
            self.orders[self.ordersCount] = response.order
            print(self.ordersCount)
            self.ordersCount += 1
        else:
            print(response.resultCode)


    def transaction(self, value, op, receiverWallet):
        if op not in self.orders:
            print(ERROR_MESSAGE)
            return 1
        response = self.stub.Transaction(getTransaction(amount = value,
                                                        order = self.orders[op],
                                                        wallet = receiverWallet))
        print(response.returnValueOrCode)


    def closeBank(self):
        response = self.stub.CloseBank(closeBank())
        print(response.savedAccounts)


    def parser(self, str):
        message = str.split()

        if message[0] == 'S':
            self.balance()

        elif message[0] == 'O':
            self.paymentOrder(int(message[1]))

        elif message[0] == 'X':
            if int(message[2]) not in self.orders:
                print(ERROR_MESSAGE)
                return 1
            self.transaction(int(message[1]), int(message[2]), message[3])


        elif message[0] == 'F':
            self.closeBank()
            return 0

        return 1

def run(clientWallet, bankAddress):
    with grpc.insecure_channel(bankAddress) as channel:
        bankStub = service_bank_pb2_grpc.BankStub(channel)
        client = ClientBank(clientWallet, bankStub)
        for line in sys.stdin:
            response = client.parser(line)
            if response == 0:
                return


if __name__ == '__main__':
    logging.basicConfig()

    if len(sys.argv) != 3:
        print("Usage: python3 src/client_bank.py clientWallet bankAddress")
        sys.exit(0)

    clientWallet = sys.argv[1]
    bankAddress = sys.argv[2]

    run(clientWallet, bankAddress)