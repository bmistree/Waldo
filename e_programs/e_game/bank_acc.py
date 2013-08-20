from __future__ import with_statement
from threading import Thread, Lock

class BankUser():
    
    def __init__(self):
        self.balance = 0
        self.lock = Lock()

    def withdraw_amount(self, n):
        self.lock.acquire()
        try:
            self.balance -= n
        finally:
            self.lock.release()
        return self.balance

    def deposit_amount(self, n):
        self.lock.acquire()
        try:
            self.balance += n
        finally:
            self.lock.release()
        return self.balance
