# payment/paystack.py
import hmac
import hashlib
import requests

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException

class PaystackException(APIException):
    status_code = status.HTTP_502_BAD_GATEWAY
    default_detail = 'Error communicating with Paystack.'
    default_code = 'paystack_error'

def initialize_transaction(email: str, amount: int, metadata: dict = None):
    """
    Initialize a Paystack transaction.
    :param email: Customer email
    :param amount: Amount in kobo
    :param metadata: arbitrary dict, e.g. {'order_id': 123}
    """
    url = settings.PAYSTACK_INITIALIZE_URL
    payload = {
        'email': email,
        'amount': amount,
        'metadata': metadata or {}
    }
    headers = {
        'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code != 200:
        raise PaystackException(detail=f"Init failed: {resp.text}")
    body = resp.json()
    if not body.get('status'):
        raise PaystackException(detail=body.get('message'))
    data = body['data']
    return data['authorization_url'], data['reference']

def verify_transaction(reference: str):
    """
    Verify a Paystack transaction. Returns the 'data' dict on success.
    """
    url = f"{settings.PAYSTACK_VERIFY_URL}{reference}"
    headers = {'Authorization': f'Bearer {settings.PAYSTACK_SECRET_KEY}'}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise PaystackException(detail=f"Verify failed: {resp.text}")
    body = resp.json()
    if not body.get('data', {}).get('status') == 'success':
        raise PaystackException(detail='Transaction not successful.')
    return body['data']

def validate_webhook_signature(request):
    """
    Raises PaystackException if signature mismatch.
    """
    signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE', '')
    secret = settings.PAYSTACK_WEBHOOK_SECRET.encode()
    computed = hmac.new(secret, msg=request.body, digestmod=hashlib.sha512).hexdigest()
    if not hmac.compare_digest(computed, signature):
        raise PaystackException(detail='Invalid webhook signature.', code='signature_mismatch')
