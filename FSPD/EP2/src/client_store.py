from __future__ import print_function
from ast import Return

import logging
import sys

import grpc

import service_store_pb2_grpc
import service_bank_pb2_grpc

from service_store_pb2 import PriceRequest as getPrice
from service_store_pb2 import SellRequest as getSell
from service_store_pb2 import CloseStoreRequest as closeStore

from service_bank_pb2 import BalanceRequest as getBalance
from service_bank_pb2 import PaymentOrderRequest as getPaymentOrder
from service_bank_pb2 import CloseBankRequest as closeBank

ERROR_MESSAGE = -9

class ClientStore:
    def __init__(self, client_wallet, store_stub, bank_stub):
        self.client = client_wallet
        self.storeStub = store_stub
        self.bankStub = bank_stub
        self.productPrice = -1

    def getProductPriceAndWalletsBalance(self):
        storeResponse = self.storeStub.Price(getPrice())
        bankResponse = self.bankStub.Balance(getBalance(wallet = self.client))
        self.productPrice = storeResponse.price

        print("%d %d" % (storeResponse.price, bankResponse.amount))

    def buyProduct(self):
        if self.productPrice < 0:
            print(ERROR_MESSAGE)
            return 1

        bankResponse = self.bankStub.PaymentOrder(
                                    getPaymentOrder(wallet = self.client,
                                                    amount = self.productPrice))
        if bankResponse.resultCode != 0:
            print(ERROR_MESSAGE)
            return 1

        storeResponse = self.storeStub.Sell(getSell(order = bankResponse.order))
        print(bankResponse.resultCode)
        print(storeResponse.returnValueOrCode)

    def closeStore(self):
        storeResponse = self.storeStub.CloseStore(closeStore())
        print(storeResponse.storeBalance)
        bankResponse = self.bankStub.CloseBank(closeBank())
        print(bankResponse.savedAccounts)

    def parser(self, str):
        message = str.split()

        if message[0] == 'P':
            self.getProductPriceAndWalletsBalance()
        elif  message[0] == 'C':
            self.buyProduct()
        elif message[0] == 'T':
            self.closeStore()
            return 0

        return 1

def run(clientWallet, bankAddress, storeAddress):
    storeChannel = grpc.insecure_channel(storeAddress)
    storeStub = service_store_pb2_grpc.StoreStub(storeChannel)

    bankChannel = grpc.insecure_channel(bankAddress)
    bankStub = service_bank_pb2_grpc.BankStub(bankChannel)

    client = ClientStore(clientWallet, storeStub, bankStub)
    for line in sys.stdin:
        response = client.parser(line)
        if response == 0:
            return


if __name__ == '__main__':
    logging.basicConfig()

    if len(sys.argv) != 4:
        print("Usage: ", end="")
        print("python3 src/client_store.py clientWallet bankAddress storeAddress")
        sys.exit(0)

    clientWallet = sys.argv[1]
    bankAddress = sys.argv[2]
    storeAddress = sys.argv[3]

    run(clientWallet, bankAddress, storeAddress)