import logging

from django.forms.models import model_to_dict

from .models import CostVariables as cost_variables
from .models import QuantityMultiplier as quantity_multiplier

logger = logging.getLogger(__name__)

def calculatePrice(material_cost, print_time):

    price_vars = model_to_dict(cost_variables.objects.get(pk=1))
    # q_perc = quantity_multiplier.objects.filter(quantity_min__gte=quantity).order_by('quantity_min')[0]
    q_perc = quantity_multiplier.objects.all().order_by('-quantity_min')

    print_cost = price_vars['material_markup']*material_cost + price_vars['print_hour_cost']*(print_time/3600)
    base_price = price_vars['price_margin']*print_cost + price_vars['post_process_cost']

    price_list = []
    for q_m in q_perc:
        unit_price = round(q_m.add_percentage*base_price, 2)
        pricing = {
            'unit_price': unit_price,
            'q_from': q_m.quantity_min,
            'q_to': q_m.quantity_max,
            'prep_cost': price_vars['prep_cost']
        }
        price_list.append(pricing)

    logger.info("PRICING OPTIONSS: {}".format(price_list))

    return price_list