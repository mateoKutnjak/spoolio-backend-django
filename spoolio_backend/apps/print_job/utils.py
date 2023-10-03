from datetime import datetime, time, timedelta
import logging
import pytz
from typing import Dict, List

from django.conf import settings

from ..filament import models as filament_models
from ..print_job import models as print_job_models
from ..printer import models as printer_models


logger = logging.getLogger(__name__)


class PrintOrderUnitPlaceholder:

    def __init__(self, quantity, estimated_time, material_id, model_dimensions, length_unit, id=None) -> None:
        self.quantity = quantity
        self.estimated_time = estimated_time
        self.material_id = material_id
        self.model_dimensions = model_dimensions
        self.length_unit = length_unit
        self.id = id

    def hasId(self) -> bool:
        return self.id is not None
    
    @staticmethod
    def fromEntity(entity):
        return PrintOrderUnitPlaceholder(
            quantity=entity.quantity, 
            estimated_time=entity.estimated_time, 
            material_id=entity.spool.material.id, 
            model_dimensions=entity.model_dimensions,
            length_unit=entity.length_unit,
            id=entity.id)


def findFirstAvailablePrinterForMaterial(material_id: int, last_job_ending_time_dict: Dict[printer_models.Printer, datetime]) -> printer_models.Printer:

    supported_pairs = []

    logger.info('material_id={}'.format(material_id))

    for printer, ending_time in last_job_ending_time_dict.items():
        logger.debug(printer.type.printing_method.supported_materials.all())
        if printer.type.printing_method.supported_materials.filter(pk=material_id):
            supported_pairs.append((printer, ending_time,))

    if not supported_pairs:
        return None, None, 'There is not a printer that supports material with id = {}'.format(material_id)

    logger.debug('supported_pairs = {}'.format(supported_pairs))

    sorted_supported_pairs = sorted(supported_pairs, key=lambda x: x[1])
    logger.debug('sorted supported_pairs = {}'.format(supported_pairs))

    first_available_printer = sorted_supported_pairs[0][0]
    first_available_ending_time = sorted_supported_pairs[0][1]
    
    return first_available_printer, first_available_ending_time, None


def generate_print_jobs(units: List[PrintOrderUnitPlaceholder], fake: bool) -> datetime:
    
    working_hours_start = time(settings.WORKING_HOURS_START_HOUR, settings.WORKING_HOURS_START_MINUTE)
    working_hours_end = time(settings.WORKING_HOURS_END_HOUR, settings.WORKING_HOURS_END_MINUTE)
    buffer_after_job = timedelta(hours=settings.BUFFER_AFTER_PRINT_JOB_DONE_HOUR, minutes=settings.BUFFER_AFTER_PRINT_JOB_DONE_MINUTE)

    available_printers = printer_models.Printer.objects.filter(available=True)

    if not available_printers:
        logger.warn('No available printers')
        return None, 'No printers available'
    
    # * Saves pairs (printer, datetime_when_available)
    printer_last_jobs_ending_time = {}

    for available_printer in available_printers:
        last_printer_job = print_job_models.PrintingJob.objects.filter(printer=available_printer, status__in=[print_job_models.PrintingJob.STATUS_IN_QUEUE, print_job_models.PrintingJob.STATUS_IN_PROGRESS]).order_by('end_at').last()

        now = pytz.UTC.localize(datetime.now())

        if last_printer_job is None:
            ending_time = now
        elif last_printer_job.end_at < now:
            ending_time = now
        else:
            ending_time = last_printer_job.end_at
        
        printer_last_jobs_ending_time[available_printer] = ending_time

    logger.debug('\n -> Printers and when they are available:\n') 
    for printer, ending_time in printer_last_jobs_ending_time.items():
        logger.info(' -> -> {} --- {}'.format(printer.name, ending_time))
    logger.debug('\n')

    # * Keeps track of latest ending time of all print jobs
    last_end_at = pytz.UTC.localize(datetime.fromtimestamp(1))

    for unit in units:

        logger.info('')
        logger.info('Unit: {}'.format(unit))
        logger.info('Material ID: {}'.format(unit.material_id))
        quantity = unit.quantity

        while quantity > 0:

            # Get first available printer and ending time
            printer, last_job_end_at, error_message = findFirstAvailablePrinterForMaterial(unit.material_id, printer_last_jobs_ending_time)

            if error_message:
                return None, error_message
            
            # Get unit quantity for the printer
            job_quantity = fillPrinterSurface(unit, printer, quantity)
            quantity -= job_quantity

            job_duration = job_quantity*unit.estimated_time

            logger.info('Job Quantity = {}/{}'.format(job_quantity, unit.quantity))

            logger.info('First available printer for material {} is {} which is available {}'.format(unit.material_id, printer, last_job_end_at))

            start_at = firstTimeAvailableFrom(last_job_end_at, working_hours_start, working_hours_end, buffer_after_job)
            if start_at.date() == now.date() and now.hour > 12:
                start_at = (start_at + timedelta(days=1)).replace(hour=working_hours_start.hour, minute=working_hours_start.minute, second=0)
            
            end_at = start_at + timedelta(seconds=job_duration)

            logger.info('New job can start at {} and will end at {} -- duration = {}'.format(start_at, end_at, job_duration))
            
            if not fake:
                job = print_job_models.PrintingJob.objects.create(
                    print_order_unit_id=unit.id, 
                    printer=printer,
                    duration=job_duration,
                    start_at=start_at,
                    end_at=end_at)
                
                logger.info('')
                logger.info('Printing job #{} created for print order unit #{} on printer {}'.format(job.id, unit.id, printer.name))

            printer_last_jobs_ending_time[printer] = end_at

            logger.info('New dummy printer ending times = {}'.format(printer_last_jobs_ending_time))

            if last_end_at < end_at:
                last_end_at = end_at

    # * Returning most recent ending time of a print job
    return last_end_at, None

def fillPrinterSurface(unit: PrintOrderUnitPlaceholder, printer: printer_models.Printer, quantity: int):

    job_quantity = 0
    len_multiplier = 1
    len_unit = unit.length_unit
    surface_size = parse_vector(printer.type.max_print_size)

    unit_size = parse_vector(unit.model_dimensions)
    if len_unit == 'inches':
        len_multiplier = 25.4

    unit_size['x'] = unit_size['x']*len_multiplier + 20  # 10mms on each side 
    unit_size['y'] = unit_size['y']*len_multiplier + 20

    axis_orders =[['x', 'y'], ['y','x']]

    for axis_order in axis_orders:
        job_q = (surface_size['x']//unit_size[axis_order[0]])*(surface_size['y']//unit_size[axis_order[1]])
        if job_q > job_quantity:
            job_quantity = job_q

    # Return number of objects that fit on printer
    return min(job_quantity, quantity)


def firstTimeAvailableFrom(time: datetime, daytimeBoundStart: time, daytimeBoundEnd: time, buffer: timedelta):

    comparison = compareToDaytimeBounds((time + buffer).time(), daytimeBoundStart, daytimeBoundEnd)

    if comparison == 'inside':

        if time.isoweekday() in [1,2,3,4,5]:
            # * For working day return same day + buffer
            return time + buffer
        elif time.isoweekday() in [6]:
            # * For saturday return monday with daytimeBoundStart
            return (time + timedelta(days=2)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        elif time.isoweekday() in [7]:
            # * For sunday return monday with daytimeBoundStart
            return (time + timedelta(days=1)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        else:
            raise Exception('datetime.isoweekday() value of {} not handled'.format(time.isoweekday()))
        
    elif comparison == 'before':

        if time.isoweekday() in [1,2,3,4,5]:
            # * Ending before day starts. Put as first thing in the day
            return time.replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        elif time.isoweekday() in [6]:
            # * Ending in saturday. Add two days
            return (time + timedelta(days=2)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        elif time.isoweekday() in [7]:
            # * Ending in sunday. Add one day
            return (time + timedelta(days=1)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        else:
            raise Exception('datetime.isoweekday() value of {} not handled'.format(time.isoweekday()))
        
    elif comparison == 'after':

        if time.isoweekday() in [1,2,3,4,7]:
            # ! Mon, Tue, Wen, Thu, Sun
            # * Ending after day ends. Add as first thing tomorrow
            return (time + timedelta(days=1)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        elif time.isoweekday() in [5]:
            # * Ending after friday ends. Add as first thing in monday (add 3 days, reset to working hours start)
            return (time + timedelta(days=3)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        elif time.isoweekday() in [6]:
            # * Ending after saturday ends. Add as first thing in monday (add 2 days, reset to working hours start)
            return (time + timedelta(days=2)).replace(hour=daytimeBoundStart.hour, minute=daytimeBoundStart.minute, second=0) + buffer
        else:
            raise Exception('datetime.isoweekday() value of {} not handled'.format(time.isoweekday()))
        
    else:
        raise Exception('Unknown return value {} for daytime bounds comparison'.format(comparison))
    

def compareToDaytimeBounds(value: time, boundLower: time, boundUpper: time):
    if value < boundLower:
        return 'before'
    if value > boundUpper:
        return 'after'
    return 'inside'


def parse_vector(vec_raw: str):
    vec = {
        'x': None,
        'y': None,
        'z': None
    }
    if vec_raw is None:
        return None
    
    vec_split = vec_raw.split(',')
    if len(vec_split) != 3:
        return None
    
    try:
        vec['x'] = float(vec_split[0])
        vec['y'] = float(vec_split[1])
        vec['z'] = float(vec_split[2])
                      
    except ValueError:
        return None
    
    return vec