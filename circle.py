import os
import requests

import uuid
import base64
import codecs
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256

api_key = "<API-KEY>"
token_ids = {"USDC": "7adb2b7d-c9cd-5164-b2d4-b73b088274dc"}

entity = "ENTITY-SECRET"

class Circle:
    def __init__(self, key, entity):
        self.api_key = key
        self.entity = entity
        self.wallet_set = "WALLET-SET"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        url = "https://api.circle.com/v1/w3s/config/entity"

        self.app_ID = requests.get(url, headers=self.headers).json()["data"]["appId"]

        print(f"app ID: {self.app_ID}")

    def generate_uuid(self):
        return str(uuid.uuid4())

    def get_public_key(self):
        url = "https://api.circle.com/v1/w3s/config/entity/publicKey"
        return requests.get(url, headers=self.headers).json()["data"]["publicKey"]

    def generate_entity(self):
        public_key_string = self.get_public_key()

        entity_secret = bytes.fromhex(self.entity)

        if len(entity_secret) != 32:
            print("invalid entity secret")
            exit(1)

        public_key = RSA.importKey(public_key_string)

        # noinspection PyTypeChecker
        cipher_rsa = PKCS1_OAEP.new(key=public_key, hashAlgo=SHA256)
        encrypted_data = cipher_rsa.encrypt(entity_secret)

        encrypted_data_base64 = base64.b64encode(encrypted_data)

        self.secret = codecs.encode(entity_secret, 'hex').decode()
        self.cipher_text = encrypted_data_base64.decode()

        print("Hex encoded entity secret:", self.secret)
        print("Entity secret ciphertext:", self.cipher_text)



    def generate_wallet_set(self, name):
        url = "https://api.circle.com/v1/w3s/developer/walletSets"

        payload = {
            "idempotencyKey": self.generate_uuid(),
            "entitySecretCipherText": self.cipher_text,
            "name": name
        }

        return requests.post(url, json=payload, headers=self.headers).json()

    def create_wallet(self):
        url = "https://api.circle.com/v1/w3s/developer/wallets"

        payload = {
            "idempotencyKey": self.generate_uuid(),
            "entitySecretCipherText": self.cipher_text,
            "blockchains": ["MATIC-MUMBAI"],
            "count": 1,
            "walletSetId": self.wallet_set
        }

        return requests.post(url, json=payload, headers=self.headers).json()["data"]["wallets"][0]["id"]

    def send(self, wallet_id, amount):
        url = "https://api.circle.com/v1/w3s/developer/transactions/transfer"

        payload = {
            "idempotencyKey": self.generate_uuid(),
            "entitySecretCipherText": self.cipher_text,
            "amounts": [str(amount)],
            "destinationAddress": "0x508fd37c3a86fabf3a89893c163dba1271867d6d",
            "feeLevel": "HIGH",
            "tokenId": token_ids["USDC"],
            "walletId": wallet_id
        }

        response = requests.post(url, json=payload, headers=self.headers)

        print(response.text)

    def get_balance(self, wallet_id):
        total = 0
        balance = requests.get(f"https://api.circle.com/v1/w3s/wallets/{wallet_id}/balances", headers=self.headers).json()["data"]["tokenBalances"]
        for i in range(0, len(balance)):
            if balance[i]["token"]["id"] in list(token_ids.values()):
                total += float(balance[i]["amount"])

        return total

    def get_total(self):
        total = 0
        balances = requests.get("https://api.circle.com/v1/w3s/wallets", headers=self.headers).json()["data"]["wallets"]
        for i in range(0, len(balances)):
            total += self.get_balance(balances[i].get('id'))

        return total
