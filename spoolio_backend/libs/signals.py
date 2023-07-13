from django.core.mail import send_mail

import logging.config


logger = logging.getLogger(__name__)


def print_order_pre_save_signal(sender, instance, raw, using, **kwargs):

    if raw:
        return

    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # * If order has just been created we will use
        # * different signal - for notifying user that
        # * order has been created
        pass
    else:
        try:
        
            if not obj.status == instance.status:
                logger.info('Sending email to {} because order status of instance {} with id {} changed ({}=>{})'.format(obj.user_profile.email or obj.user_profile.user.email, sender, obj.id, obj.status, instance.status))
            
                send_mail(
                    'Your order status has been changed',
                    '{} no {} status has been changed to {}'.format(sender.__name__, obj.id, instance.status),
                    'bot@spoolio.net',
                    [obj.user_profile.email or obj.user_profile.user.email],
                    fail_silently=False,
                )
        except Exception as e:
            logger.critical("Exception occurred while trying to send order status change email: {}".format(e))


def print_order_post_save_signal(sender, instance, created, raw, using, update_fields, **kwargs):

    if raw:
        return
    
    if created:
        send_mail(
            'Order has been created',
            '{} no {} has been created. STATUS={}'.format(sender.__name__, instance.id, instance.status),
            'bot@spoolio.net',
            ['info.ur3d@gmail.com'],
            fail_silently=False,
        )