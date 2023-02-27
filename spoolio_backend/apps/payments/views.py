import json
from typing import Callable

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from rest_framework.decorators import api_view

import stripe

from .. print_order import models as print_order_models

stripe.api_key = 'sk_test_51MUVqECWTJUk8OjZT2a80T7zFcODaz7NUzYjbTY6I0ExlSGtltbkqe2PSzOwddIANkxcJsEtlASmlkXLVPiIQpXh00jLrQTUSt'


def check_print_order_amount(print_order_id: int, amount: float):

    try:
        obj = print_order_models.PrintOrder.objects.get(pk=print_order_id)
    
        if amount == float(obj.estimated_price) * 100:
            return True, None
        return False, 'Estimated price and amount requested does not match'
    except ObjectDoesNotExist:
        return False, 'Print order with this id does not exist'
    

def check_modeling_order_amount(modeling_order_id: int, amount: float):
    raise NotImplementedError()


def check_store_order_amount(store_order_id: int, amount: float):
    raise NotImplementedError()


@api_view(['POST'])
def create_payment(request):

    check_function: Callable[[int, float], (bool, str)] = None

    if request.data['service'] == 'printing':
        check_function = check_print_order_amount
    elif request.data['service'] == 'modeling':
        check_function = check_modeling_order_amount
    elif request.data['service'] == 'store':
        check_function = check_store_order_amount

    is_amount_ok, message = check_function(request.data['id'], request.data['amount'])

    if not is_amount_ok:
        return JsonResponse(data={'error': message}, status=400)

    try:
        # data = json.loads(request.data)
        # Create a PaymentIntent with the order amount and currency
        
        intent = stripe.PaymentIntent.create(
            amount=request.data['amount'], # calculate_order_amount(data['items']),
            currency=request.data['currency'],
            automatic_payment_methods={
                'enabled': True,
            },
            # payment_method_types=['card'],
        )
        return JsonResponse(data={
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(e)
        return JsonResponse(data={'error': str(e)}, status=403) #, 403
    