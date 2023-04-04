import os
import json
import requests
from uuid import uuid4
from basicauth import encode


class Disbursement:
    def __init__(self):
        self.disbursements_primary_key = os.environ.get('DISBURSEMENT_PRIMARY_KEY')
        self.api_key_disbursements = os.environ.get('DISBURSEMENT_API_SECRET')
        self.disbursements_apiuser = os.environ.get('DISBURSEMENT_USER_ID')
        self.environment_mode = os.environ.get('MTN_ENVIRONMENT')
        self.callback_url = os.environ.get('CALLBACK_URL')
        self.base_url = os.environ.get('BASE_URL')
        

        if self.environment_mode == "sandbox":
            self.base_url = "https://sandbox.momodeveloper.mtn.com"

        # Generate Basic authorization key when in test mode
        if self.environment_mode == "sandbox":
            self.disbursements_apiuser = str(uuid4())

        # Create API user
        self.url = f"{self.base_url}/v1_0/apiuser"
        payload = json.dumps({
            "providerCallbackHost": os.environ.get('')
        })
        self.headers = {
            'X-Reference-Id': self.disbursements_apiuser,
            'Content-Type': 'application/json',
            'Ocp-Apim-Subscription-Key': self.disbursements_primary_key
        }
        response = requests.post(self.url, headers=self.headers, data=payload)

        # Auto-generate when in test mode
        if self.environment_mode == "sandbox":
            self.api_key_disbursements = str(response["apiKey"])

        # Create basic key for disbursements
        self.username, self.password = self.disbursements_apiuser, self.api_key_disbursements
        self.basic_authorisation_disbursements = str(encode(self.username, self.password))

    def authToken(self):
        url = f"{self.base_url}/disbursement/token/"
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.disbursements_primary_key,
            'Authorization': self.basic_authorisation_disbursements
        }
        response = requests.post(url, headers=headers, data=payload).json()
        return response

    def getBalance(self):
        url = f"{self.base_url}/disbursement/v1_0/account/balance"
        payload = {}
        headers = {
            'Ocp-Apim-Subscription-Key': self.disbursements_subkey,
            'Authorization':  "Bearer " + str(self.authToken()["access_token"]),
            'X-Target-Environment': self.environment_mode,
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        json_respon = response.json()
        return json_respon

    def transfer(self, amount, phone_number, external_id,payermessage='',payermessageNone=''):
        url = f"{self.base_url}/disbursement/v1_0/transfer"
        payload = json.dumps({
            "amount": str(amount),
            "currency": os.environ.get('CURRENCY'),
            "externalId": str(external_id),
            "payee": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": payermessage,
            "payeeNote": payermessageNone
        })
        
        headers = {
            'X-Reference-Id': str(uuid4()),
            'X-Target-Environment': self.environment_mode,
            'X-Callback-Url': self.callback_url,
            'Ocp-Apim-Subscription-Key': self.subscription_key,
            'Content-Type': 'application/json',
            'Authorization':  "Bearer " + str(self.authToken()["access_token"])
            }
        proxies = {
            "http": os.environ.get('QUOTAGUARDSTATIC_URL'),
            "https": os.environ.get('QUOTAGUARDSTATIC_URL')
            }
        response = requests.post(url, headers=headers, json=payload, proxies=proxies)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch data from API. Status code: {response.status_code}, Error: {response.text}")
    

    def getTransactionStatus(self,txn_ref):

        url = f"{self.base_url}/disbursement/v1_0/transfer/{txn_ref}"

        payload = {}

        headers = {
            'X-Reference-Id': str(uuid4()),
            'X-Target-Environment': self.environment_mode,
            'Ocp-Apim-Subscription-Key': self.disbursements_primary_key,
            'Content-Type': 'application/json',
            'Authorization':  "Bearer " + str(self.authToken()["access_token"])
        }

        proxies = {
            "http": os.environ.get('QUOTAGUARDSTATIC_URL'),
            "https": os.environ.get('QUOTAGUARDSTATIC_URL')
            }

        response = requests.request("GET", url, headers=headers, data=payload, proxies=proxies)
        returneddata = response.json()

        res = {
            "response": response.status_code,
            "ref": txn_ref,
            "data": returneddata
        }
        return res
