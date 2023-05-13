import logging

from ..print_job import utils as print_job_utils
from ..print_order import models as print_order_models

from ...celery import app


logger = logging.getLogger(__name__)


@app.task
def create_printing_jobs_for_print_order(job_params):

    # *************************** #
    # *** Load job parameters *** #
    # *************************** #

    print_order_id = job_params.get('data', {}).get('print_order', {}).get('id', None)
    print_order_status = job_params.get('data', {}).get('print_order', {}).get('status', None)

    # ******************************** #
    # *** Check parameter validity *** #
    # ******************************** #

    if print_order_id is None:
        logger.error('Cannot create printing jobs. Print order id = {}'.format(print_order_id))
        return  
    
    if print_order_status != print_order_models.PrintOrder.STATUS_IN_PROGRESS:
        logger.error('Cannot create printing jobs. Print order status is "{}", expected {}'.format(print_order_status, print_order_models.PrintOrder.STATUS_IN_PROGRESS))
        return
    
    logger.info('Order #{} has been paid. Creating printer jobs for every unit of this order.'.format(print_order_id))

    print_order_units = print_order_models.OrderUnit.objects.filter(order=print_order_id)
    units = [print_job_utils.PrintOrderUnitPlaceholder.fromEntity(print_order_unit) for print_order_unit in print_order_units]

    end_at = print_job_utils.generate_print_jobs(units, fake=False)
