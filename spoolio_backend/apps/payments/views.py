import math
from typing import Callable

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.db.models import F, Sum
from django.http import JsonResponse

import logging

from rest_framework.decorators import api_view

import stripe

from .. modeling_order import models as modeling_order_models
from .. print_order import models as print_order_models
from .. print_job import models as print_job_models
from .. store_order import models as store_order_models


logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_API_KEY

# * WHen checking price this is allowed difference (in cents)
EPSILON = 3


def check_print_order_amount(print_order_id: int, amount: float):

    try:
        obj = print_order_models.PrintOrder.objects.get(pk=print_order_id)

        total_price = float(obj.estimated_price) + \
            float(obj.shipping_method.price)

        # ! If rounding of number changes (here we use math.floor), make
        # ! sure same method is used on frontend price calculation
        total_price = math.floor(total_price * 100) / 100

        # * Stripe amount is measured x100
        stripe_amount = int(total_price * 100)

        if abs(amount - total_price) <= EPSILON:
            return True, stripe_amount, None
        return False, None, 'Estimated price and amount requested does not match'
    except ObjectDoesNotExist:
        return False, None, 'Print order with this id does not exist'


def check_modeling_order_amount(modeling_order_id: int, amount: float):
    print("Checking modeling order amounts!")
    try:
        obj = modeling_order_models.ModelingOrder.objects.get(
            pk=modeling_order_id)

        # ! Save tax percentage as constant or depending on country
        # total_price = float(obj.estimated_price) * 1.25
        total_price = float(obj.estimated_price)

        # ! If rounding of number changes (here we use math.floor), make
        # ! sure same method is used on frontend price calculation
        total_price = math.floor(total_price * 100) / 100

        # * Stripe amount is measured x100
        stripe_amount = int(total_price * 100)

        print("Frontend amount: {}, Backend amount: {}".format(amount, total_price))

        if abs(amount - total_price) <= EPSILON:
            return True, stripe_amount, None
        return False, None, 'Estimated price and amount requested does not match'
    except ObjectDoesNotExist:
        return False, None, 'Print order with this id does not exist'


def check_store_order_amount(store_order_id: int, amount: float):
    try:
        obj = store_order_models.StoreOrder.objects.get(pk=store_order_id)

        items_price = obj.items.aggregate(total_price=Sum(
            F('storeorderunit__quantity') * F('price')))['total_price']

        # ! Save tax percentage as constant or depending on country
        total_price = items_price * 1.25 + float(obj.shipping_method.price)

        # ! If rounding of number changes (here we use math.floor), make
        # ! sure same method is used on frontend price calculation
        total_price = math.floor(total_price * 100) / 100

        # * Stripe amount is measured x100
        stripe_amount = int(total_price * 100)

        if abs(amount - total_price) <= EPSILON:
            return True, stripe_amount, None
        return False, None, 'Estimated price and amount requested does not match'
    except ObjectDoesNotExist:
        return False, None, 'Print order with this id does not exist'


def update_order_status(order_id: int, order_type: str):

    order_not_found = False

    if order_type == 'printing':
        try:
            obj = print_order_models.PrintOrder.objects.get(pk=order_id)
            obj.status = print_order_models.PrintOrder.STATUS_IN_PROGRESS
            obj.save()
        except ObjectDoesNotExist:
            order_not_found = True
    elif order_type == 'modeling':
        try:
            obj = modeling_order_models.ModelingOrder.objects.get(pk=order_id)
            obj.status = modeling_order_models.ModelingOrder.STATUS_IN_PROGRESS
            obj.save()
        except ObjectDoesNotExist:
            order_not_found = True
    elif order_type == 'store':
        try:
            obj = store_order_models.StoreOrder.objects.get(pk=order_id)
            obj.status = store_order_models.StoreOrder.STATUS_IN_PROGRESS
            obj.save()
        except ObjectDoesNotExist:
            order_not_found = True
    else:
        raise Exception('Cannot update order [id={}] status. Order type {} not recognized.'.format(
            order_id, order_type))

    if order_not_found:
        send_mail(
            'Manual intervention needed',
            'Trying to update {} order no.{} status as payment has been just made, but this order has not been found in DB'.format(
                order_type, order_id),
            'bot@spoolio.net',
            ['spoolio.web@gmail.com'],
            fail_silently=False,
        )


@api_view(['POST'])
def create_payment(request):

    check_function: Callable[[int, float], (bool, str)] = None

    if request.data['service'] == 'printing':
        check_function = check_print_order_amount
    elif request.data['service'] == 'modeling':
        check_function = check_modeling_order_amount
    elif request.data['service'] == 'store':
        check_function = check_store_order_amount

    is_amount_ok, amount, message = check_function(
        request.data['id'], request.data['amount'])

    if not is_amount_ok:
        print("Amount not OK")
        return JsonResponse(data={'error': message}, status=400)

    try:
        # Create a PaymentIntent with the order amount and currency
        if request.data['service'] == 'printing':
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=request.data['currency'],
                automatic_payment_methods={
                    'enabled': False,
                },
                capture_method="manual",
                metadata={
                    'order_id': int(request.data['id']),
                    'service': request.data['service'],
                }
                # payment_method_types=['card'],
            )
        else:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=request.data['currency'],
                automatic_payment_methods={
                    'enabled': False,
                },
                metadata={
                    'order_id': int(request.data['id']),
                    'service': request.data['service'],
                }
                # payment_method_types=['card'],
            )

        return JsonResponse(data={
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(e)
        return JsonResponse(data={'error': str(e)}, status=403)


@api_view(['POST'])
def init_payment(request):

    try:
        # Create a PaymentIntent with the order amount and currency

        intent = stripe.PaymentIntent.create(
            amount=50,
            currency=request.data['currency'],
            automatic_payment_methods={
                'enabled': False,
            },
            capture_method="manual",
            metadata={
                'service': request.data['service'],
            }
            # payment_method_types=['card']
        )

        return JsonResponse(data={
            'intentId': intent['id'],
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(e)
        return JsonResponse(data={'error': str(e)}, status=403)


@api_view(['POST'])
def modify_payment(request):

    try:
        # Modify a PaymentIntent's amount, customer and metadata -> order_id

        client_secret = request.data['client_secret']
        order_id = request.data['order_id']

        try:
            obj = print_order_models.PrintOrder.objects.get(pk=order_id)

            total_price = float(obj.estimated_price) + \
                float(obj.shipping_method.price)

            # ! If rounding of number changes (here we use math.floor), make
            # ! sure same method is used on frontend price calculation
            total_price = math.floor(total_price * 100) / 100

            # * Stripe amount is measured x100
            stripe_amount = int(total_price * 100)

        except ObjectDoesNotExist:
            return JsonResponse(data={
                'error': 'Print order with this id does not exist'
            }, status=403)

        intent = stripe.PaymentIntent.modify(
            client_secret,
            amount=stripe_amount,
            metadata={"order_id": order_id},
        )

        return JsonResponse(data={
            'clientSecret': intent['client_secret']
        })
    except Exception as e:
        print(e)
        return JsonResponse(data={'error': str(e)}, status=403)


@api_view(['POST'])
def stripe_webhooks(request):

    event = request.data

    # ? See https://stripe.com/docs/webhooks/quickstart
    # ? if endpoint_secret is defined

    logger.info('Stripe webhook of type {} received'.format(event['type']))

    # Handle the event
    # if event['type'] == 'charge.succeeded':
    #    metadata = event['data']['object']['metadata']
    #    update_order_status(metadata.get('order_id'), metadata.get('service'))

    # Handle the event
    if event['type'] == 'payment_intent.amount_capturable_updated':
        status = event['data']['object']['status']
        intent_id = event['data']['object']['id']
        logger.info("ID: {} -- Payment Status: {}".format(intent_id, status))
        if status == "requires_capture":
            try:
                metadata = event['data']['object']['metadata']
                obj = print_order_models.PrintOrder.objects.get(
                    pk=metadata.get('order_id'))
                obj.payment_intent = intent_id
                obj.save()
            except ObjectDoesNotExist:
                order_not_found = True

    elif event['type'] == 'payment_intent.succeeded':
        metadata = event['data']['object']['metadata']

        print_job_models.PrintingJob.objects.filter(
            print_order_unit__order__pk=metadata.get('order_id')
        ).update(status=print_job_models.PrintingJob.STATUS_IN_QUEUE)

        update_order_status(metadata.get('order_id'), metadata.get('service'))

    elif event['type'] == 'payment_intent.canceled':
        metadata = event['data']['object']['metadata']

        print_job_models.PrintingJob.objects.filter(
            print_order_unit__order__pk=metadata.get('order_id')
        ).update(status=print_job_models.PrintingJob.STATUS_REJECTED)

    return JsonResponse({"success": True})
