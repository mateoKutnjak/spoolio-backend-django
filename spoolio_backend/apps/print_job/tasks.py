import logging

from ..print_job import utils as print_job_utils
from ..print_order import models as print_order_models

from ... celery import app
from ... libs import channels as channels_utils


logger = logging.getLogger(__name__)


@app.task
def create_printing_jobs_for_print_order(job_params):

    # *************************** #
    # *** Load job parameters *** #
    # *************************** #

    print_order_id = job_params.get('data', {}).get(
        'print_order', {}).get('id', None)
    print_order_status = job_params.get('data', {}).get(
        'print_order', {}).get('status', None)

    # ******************************** #
    # *** Check parameter validity *** #
    # ******************************** #

    if print_order_id is None:
        logger.error(
            'Cannot create printing jobs. Print order id = {}'.format(print_order_id))
        return

    # if print_order_status != print_order_models.PrintOrder.STATUS_IN_PROGRESS:
    #    logger.error('Cannot create printing jobs. Print order status is "{}", expected {}'.format(print_order_status, print_order_models.PrintOrder.STATUS_IN_PROGRESS))
    #    return

    logger.info('Order #{} has been paid. Creating printer jobs for every unit of this order.'.format(
        print_order_id))

    print_order_units = print_order_models.OrderUnit.objects.filter(
        order=print_order_id)
    units = [print_job_utils.PrintOrderUnitPlaceholder.fromEntity(
        print_order_unit) for print_order_unit in print_order_units]

    end_at, ids, error_message = print_job_utils.generate_print_jobs(
        units, fake=False)

    if error_message:
        logger.error(error_message)


@app.task
def print_job_ending_time_estimation(job_params):

    # ************************************************ #
    # *** Check websocket communication parameters *** #
    # ************************************************ #

    channel_group_name = job_params.get('meta', {}).get(
        'django_channels', {}).get('channel_group_name', None)

    if not channel_group_name:
        channels_utils.channels_group_send_error(
            'Celery task stopped. Parameter "channel_group_name" missing')
        return

    # ********************************* #
    # *** Check required parameters *** #
    # ********************************* #

    raw_units = job_params.get('data', {}).get('units')
    logger.info('RAW UNITS: {}'.format(raw_units))

    if raw_units is None:
        channels_utils.channels_group_send_error(
            'Celery task stopped. Parameter units is missing', channel_group_name)
        return

    units = [print_job_utils.PrintOrderUnitPlaceholder(
        quantity=u['quantity'],
        material_id=u['material_id'],
        estimated_time=u['estimated_time'],
        model_dimensions=u['model_dimensions'],
        length_unit=u['length_unit']) for u in raw_units]

    # ************************************** #
    # *** Estimate print job ending time *** #
    # ************************************** #

    estimated_ending_time, ids, error_message = print_job_utils.generate_print_jobs(
        units, fake=False)

    if error_message:
        channels_utils.channels_group_send_error(
            error_message, channel_group_name)
        return

    # ************************************* #
    # *** Send result to channels layer *** #
    # ************************************* #

    channels_utils.channels_group_send_data(
        data={
            "estimated_ending_time": estimated_ending_time.isoformat(),
            "job_ids": ids
        },
        channel_group_name=channel_group_name
    )
