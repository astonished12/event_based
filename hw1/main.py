import re
import click
import names
import random
from datetime import datetime, timedelta

FIELDS = {
    'patient-name': {
        'choices': [names.get_full_name() for _ in range(100)]
    },
    'DoB': {
        'min': '01-01-1900',
        'max': '31-12-2010'
    },
    'height': {
        'min': 1.50,
        'max': 2.50
    },
    'eye-color': {
        'choices': ['blue', 'green', 'brown', 'black', 'grey']
    },
    'heart-rate': {
        'min': 50,
        'max': 180
    }
}

@click.group()
def cli():
    pass

def get_random_pub(fields_config):
    pub = {} 

    pub['patient-name'] = random.choice(fields_config['patient-name']['choices'])

    min_dob = datetime.strptime(fields_config['DoB']['min'], '%d-%m-%Y')
    max_dob = datetime.strptime(fields_config['DoB']['max'], '%d-%m-%Y')
    max_delta_days = (max_dob - min_dob).days
    random_delta_days = random.randint(0, max_delta_days)
    pub['DoB'] = min_dob + timedelta(days=random_delta_days)

    min_height = fields_config['height']['min']
    max_height = fields_config['height']['max']
    max_delta_ height = max_height - min_height
    random_delta_height = random.random() * max_delta_height
    pub['height'] = round(float(min_height) + random_delta_height, 2)

    pub['eye-color'] = random.choice(fields_config['eye-color']['choices'])

    min_heart_rate = fields_config['heart-rate']['min']
    max_heart_rate = fields_config['heart-rate']['max']
    max_delta_heart_rate = max_heart_rate - min_heart_rate
    random_delta_heart_rate = random.randint(0, max_delta_heart_rate)
    pub['heart-rate'] = min_heart_rate + random_delta_heart_rate

    return pub


@cli.command('publish')
@click.option('-n', '--count', required=True, type=click.INT)
def publish(count):
    pubs = [get_random_pub(FIELDS) for _ in range(count)]

    print('patient-name,DoB,height,eye-color,heart-rate')
    for pub in pubs:
        print('{},{},{},{},{}'
              .format(pub['patient-name'], pub['DoB'].strftime('%d-%m-%Y'), 
                      pub['height'], pub['eye-color'], pub['heart-rate']))


@cli.command('subscribe')
@click.option('-n', '--count', required=True, type=click.INT)
@click.option('-f', '--field', required=True, multiple=True)
@click.option('-e', '--eq-field', required=True)
def subscribe(count, field, eq_field):
    fields_percentages = dict()
    eq_field_percentage = None

    escaped_fields_regex = '|'.join([re.escape(f) for f in FIELDS.keys()])
    field_regex = r'^({})=([1-9]?[0-9]0?)%$'.format(escaped_fields_regex)
    for f in field:
        assert re.match(field_regex, f), \
               'Wrong field {} format! Format: field-name=<0-100>%'.format(f)
        field_name, percent = f.split('=')
        percent = int(percent.replace('%', ''))
        fields_percentages[field_name] = percent

    assert re.match(field_regex, eq_field), \
           'Wrong equality field {} format! Format: field-name=<0-100>%'.format(eq_field)
    field_name, percent = eq_field.split('=')
    percent = int(percent.replace('%', ''))
    eq_field_percentage = (field_name, percent)

    print(fields_percentages)
    print(eq_field_percentage)

if __name__ == "__main__":
    cli()