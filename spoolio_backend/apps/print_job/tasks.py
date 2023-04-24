from datetime import datetime, timedelta

import logging

from ..print_job import models as print_job_models
from ..print_order import models as print_order_models
from ..printer import models as printer_models

from ...celery import app


logger = logging.getLogger(__name__)


@app.task
def create_printing_jobs_for_print_order(job_params):

    # *************************** #
    # *** Load job parameters *** #
    # *************************** #

    print_order_id = job_params.get('data', {}).get('print_order', {}).get('id', None)
    print_order_status = job_params.get('data', {}).get('print_order', {}).get('status', None)
    working_hours_start_hour = job_params.get('data', {}).get('working_hours', {}).get('start', {}).get('hours', None)
    working_hours_start_minute = job_params.get('data', {}).get('working_hours', {}).get('start', {}).get('minutes', None)
    working_hours_end_hour = job_params.get('data', {}).get('working_hours', {}).get('end', {}).get('hours', None)
    working_hours_end_minute = job_params.get('data', {}).get('working_hours', {}).get('end', {}).get('minutes', None)
    buffer_after_print_job_done_hour = job_params.get('data', {}).get('misc', {}).get('buffer_after_print_job_done', {}).get('hours', None)
    buffer_after_print_job_done_minutes = job_params.get('data', {}).get('misc', {}).get('buffer_after_print_job_done', {}).get('minutes', None)

    # ******************************** #
    # *** Check parameter validity *** #
    # ******************************** #

    if print_order_id is None:
        logger.error('Cannot create printing jobs. Print order id = {}'.format(print_order_id))
        return  
    
    if print_order_status != print_order_models.PrintOrder.STATUS_IN_PROGRESS:
        logger.error('Cannot create printing jobs. Print order status is "{}", expected {}'.format(print_order_status, print_order_models.PrintOrder.STATUS_IN_PROGRESS))
        return
    
    if working_hours_start_hour is None or working_hours_end_hour is None or working_hours_end_hour is None or working_hours_end_minute is None:
        logger.error('Cannot create printing jobs. Some working hours data is missing. {:02d}:{:02d} - {:02d}:{:02d}'.format(working_hours_start_hour, working_hours_start_minute, working_hours_end_hour, working_hours_end_minute))
        return

    if buffer_after_print_job_done_hour is None or buffer_after_print_job_done_minutes is None:
        logger.error('Cannot create printing jobs. Buffer after print job done data is missing: {:02d}:{:02d}'.format(buffer_after_print_job_done_hour, buffer_after_print_job_done_minutes))
        return
    
    logger.info('Order #{} has been paid. Creating printer jobs for every unit of this order.'.format(print_order_id))
    logger.info('   Working day (UTC time): {:02d}:{:02d} - {:02d}:{:02d}'.format(working_hours_start_hour, working_hours_start_minute, working_hours_end_hour, working_hours_end_minute))
    logger.info('   Time buffer after previous job is finished: {:02d}:{:02d}'.format(buffer_after_print_job_done_hour, buffer_after_print_job_done_minutes))

    buffer_after = timedelta(hours=buffer_after_print_job_done_hour, minutes=buffer_after_print_job_done_minutes)
    print_order_units = print_order_models.OrderUnit.objects.filter(order=print_order_id)

    logger.info('')
    logger.info('   Number of print units: {}'.format(len(print_order_units)))

    for unit in print_order_units:

        logger.info('')
        logger.info('   Unit #{} [material={}]'.format(unit.pk, unit.spool.material.name))

        last_printer_jobs = []
        printers = printer_models.Printer.objects.filter(available=True, type__supported_materials__in=[unit.spool.material])
        logger.info('   {} printers found that work with material={}'.format(len(printers), unit.spool.material.name))
        
        if not printers:
            return

        for printer in printers:

            # * Fetch newest printing job on priter with status 'in_queue' or 'in_progress'
            # *
            # * filter leaves only printing orders with 'in_queue' and 'in_progress' status
            # * order_by('end_at') orders printing jobs from oldest to newest
            # * last() fetches newest printing job or None if list is empty
            last_printer_job = print_job_models.PrintingJob.objects.filter(printer=printer, status__in=[print_job_models.PrintingJob.STATUS_IN_QUEUE, print_job_models.PrintingJob.STATUS_IN_PROGRESS]).order_by('end_at').last()
            
            if last_printer_job:
                logger.info('   Printer {} has last job #{} which ends at {}'.format(printer.name, last_printer_job.pk, last_printer_job.end_at))
            else:
                logger.info('   Printer {} has no "in_queue" or "in_progress" jobs'.format(printer.name))

            last_printer_jobs.append((last_printer_job, printer))

        # * Sort last job of every printer based on time it ends. Put empty printers with 
        # * last job == None at the beginning of the sorted list to be fetched first
        last_printer_jobs_sorted = sorted(last_printer_jobs, key=lambda item: (item[0] is not None and item[0].end_at is not None, item[0].end_at))

        # * Fetch printer job that ends first
        job_previous = last_printer_jobs_sorted[0][0] if len(last_printer_jobs_sorted) > 0 else None
        printer = last_printer_jobs_sorted[0][1] if len(last_printer_jobs_sorted) > 0 else None

        logger.info('')

        # * Determine end time of previous job to which new jobe will be appended
        if job_previous is None:
            # * Printer does not have any 'in_queue' or 'in_progress' jobs so current time
            # * is used as a 'dummy' printing job end time to indicate that printer has
            # * just finished his last job and can be used immediately (with taking weekends 
            # * into consideration)

            now = datetime.now()

            if now.isoweekday() in [1,2,3,4,5]:
                # ? Mon, Tue, Wed, Thu, Sun - add one day
                days_to_add = 0
            elif now.isoweekday() == 6:
                # ? Fri - add three days
                days_to_add = 2
            elif now.isoweekday() == 7:
                # ? Sat - add two days
                days_to_add = 1

            end_at_previous = datetime.now() + timedelta(days=days_to_add)

            logger.info('   Printer {} is available immediatelly (has no active printing jobs)'.format(printer.name))
            logger.info('   Because today weekday number is {}, we will add {} days.\n'.format(end_at_previous.isoweekday(), days_to_add))

        else:
            # * Printer has jobs in his job queue so last job ending time is used (if it
            # * in future). If last printing job ending is not in the future, use current
            # * time as last job ending time.

            now = datetime.now()

            if job_previous.end_at.timestamp() < now.timestamp():
                end_at_previous = now
            else:                
                end_at_previous = datetime.fromtimestamp(job_previous.end_at.timestamp())

            # ! This should not be on weekends or holiday 
            # ! and algorith below forbids that situation

            logger.info('   Printer {} will be available first at {} when job #{} ends'.format(printer.name, last_printer_job.end_at, last_printer_job.pk))

        # * Determine if job ends after working time
        working_day_start = end_at_previous.replace(hour=working_hours_start_hour, minute=working_hours_start_minute, second=0)
        working_time_end = end_at_previous.replace(hour=working_hours_end_hour, minute=working_hours_end_minute, second=0)

        if end_at_previous > working_day_start and end_at_previous < working_time_end:
            # * Job is done in middle of the working day. 
            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is middle of working day ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, working_hours_start_hour, working_hours_start_minute, working_hours_end_hour, working_hours_end_minute))

            if end_at_previous + buffer_after < working_time_end:
                logger.info('   Even considering time buffer, new job can be placed today')
                # * Job is done before end of the work day with BUFFER_AFTER taken into consideration.
                # * Add new job after this one in the same day

                start_at = end_at_previous + buffer_after
                end_at = start_at + timedelta(seconds=unit.estimated_time)

            else:
                # * When taking BUFFER_AFTER into consideration, job ends after working hours, so
                # * it is shifted for next working day
                logger.info('   Considering time buffer, new job cannot be placed today')

                # * Determine how much days to add for every possible weekday when job ends
                if end_at_previous.isoweekday() in [1,2,3,4,7]:
                    # ? Mon, Tue, Wed, Thu, Sun - add one day
                    days_to_add = 1
                elif end_at_previous.isoweekday() == 5:
                    # ? Fri - add three days
                    days_to_add = 3
                elif end_at_previous.isoweekday() == 6:
                    # ? Sat - add two days
                    days_to_add = 2

                logger.info('   Because today weekday number is {}, we will add {} days.\n'.format(end_at_previous.isoweekday(), days_to_add))

                start_at = end_at_previous + timedelta(days=days_to_add)
                start_at = start_at.replace(hour=working_hours_start_hour, minute=working_hours_start_minute)

        elif end_at_previous < working_day_start:

            # * Job is done before working day starts so it is placed in the same day
            # * right when working hours start

            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is before working day starts ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, working_hours_start_hour, working_hours_start_minute, working_hours_end_hour, working_hours_end_minute))

            start_at = end_at_previous.replace(hour=working_hours_start_hour, minute=working_hours_start_minute)

        elif end_at_previous > working_time_end:

            # * Job is done after working day ends so it is placed in the next working day
            # * right when working hours start

            logger.info('   Last job is done at {:02d}:{:02d}:{:02d} which is after working day ends ({:02d}:{:02d} - {:02d}:{:02d})'.format(end_at_previous.hour, end_at_previous.minute, end_at_previous.second, working_hours_start_hour, working_hours_start_minute, working_hours_end_hour, working_hours_end_minute))

            if end_at_previous.isoweekday() in [1,2,3,4,7]:
                # ? Mon, Tue, Wed, Thu, Sun - add one day
                days_to_add = 1
            elif end_at_previous.isoweekday() == 5:
                # ? Fri - add three days
                days_to_add = 3
            elif end_at_previous.isoweekday() == 6:
                # ? Sat - add two days
                days_to_add = 2

            start_at = end_at_previous + timedelta(days=days_to_add)
            start_at = start_at.replace(hour=working_hours_start_hour, minute=working_hours_start_minute)

        else:
            logger.error('Cannot create printing job for OrderUnit #{}. Cannot determine previous job ending time placement in working day'.format(unit.id))
            return

        end_at = start_at + timedelta(seconds=unit.estimated_time)

        # * Default status is 'in_queue'.
        job = print_job_models.PrintingJob.objects.create(
            print_order_unit=unit, 
            printer=printer,
            duration=unit.estimated_time,
            start_at=start_at,
            end_at=end_at)
        
        logger.info('')
        logger.info('Printing job #{} created for print order unit #{} on printer {}'.format(job.id, unit.id, printer.name))
        logger.info('   Printing starts at: {}'.format(job.start_at))
        logger.info('   Printing ends at: {}'.format(job.end_at))