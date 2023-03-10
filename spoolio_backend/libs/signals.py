from django.core.mail import send_mail

import logging.config


logger = logging.getLogger(__name__)


def send_email_on_order_status_change(sender, instance, using, **kwargs):

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