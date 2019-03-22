import re
import click
import math
import names
import random
from datetime import datetime, timedelta
from pprint import pprint
from collections import namedtuple


FIELDS = {
    'patient-name': {
        'choices': [names.get_full_name() for _ in range(100)],
    },
    'DoB': {
        'min': '01-01-1900',
        'max': '31-12-2010',
        'ops': [],
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
OPS = ['=', '!=', '<', '>', '>=', '<=']


def get_random_name():
    return random.choice(FIELDS['patient-name']['choices'])


def get_random_dob():
    min_dob = datetime.strptime(FIELDS['DoB']['min'], '%d-%m-%Y')
    max_dob = datetime.strptime(FIELDS['DoB']['max'], '%d-%m-%Y')
    max_delta_days = (max_dob - min_dob).days
    random_delta_days = random.randint(0, max_delta_days)
    return min_dob + timedelta(days=random_delta_days)


def get_random_height():
    min_height = FIELDS['height']['min']
    max_height = FIELDS['height']['max']
    max_delta_height = max_height - min_height
    random_delta_height = random.random() * max_delta_height
    return round(float(min_height) + random_delta_height, 2)


def get_random_eye_color():
    return random.choice(FIELDS['eye-color']['choices'])


def get_random_heart_rate():
    min_heart_rate = FIELDS['heart-rate']['min']
    max_heart_rate = FIELDS['heart-rate']['max']
    max_delta_heart_rate = max_heart_rate - min_heart_rate
    random_delta_heart_rate = random.randint(0, max_delta_heart_rate)
    return min_heart_rate + random_delta_heart_rate


def get_random_pub():
    pub = {} 
    pub['patient-name'] = get_random_name()
    pub['DoB'] = get_random_dob()
    pub['height'] = get_random_height()
    pub['eye-color'] = get_random_eye_color()
    pub['heart-rate'] = get_random_heart_rate()
    return pub


FIELD_RANDOM_FUNC = {
    'patient-name': get_random_name,
    'DoB': get_random_dob,
    'height': get_random_height,
    'eye-color': get_random_eye_color,
    'heart-rate': get_random_heart_rate
    }


Constraint = namedtuple('Constraint', 'field, op, value')


def get_random_constraint(field):
    random_op = random.choice(OPS)
    random_value = FIELD_RANDOM_FUNC[field]()
    return Constraint(field, random_op, random_value)


def get_random_subs(count, fields_percentages, eq_field_percentage):
    subs = []
    constraints = {f: [] for f in FIELDS}

    fields_needed = {field: math.floor(float(percent) / 100 * count)
                     for field, percent in fields_percentages.items()}
    eq_field, eq_percent = eq_field_percentage

    for f_needed in fields_percentages:
        count_field_needed = fields_needed[f_needed]
        while count_field_needed != 0:
            con = get_random_constraint(field=f_needed)
            constraints[f_needed].append(con)
            count_field_needed -= 1
    
    for f_unneeded in set(FIELDS) - set(fields_needed):
        count_field_unneeded = random.randint(0, count)
        while count_field_unneeded != 0:
            con = get_random_constraint(field=f_unneeded)
            constraints[f_unneeded].append(con)
            count_field_unneeded -= 1

    count_eq_field_needed = math.floor(float(eq_percent) / 100 * len(constraints[eq_field]))
    for idx, con in enumerate(constraints[eq_field]):
        if count_eq_field_needed != 0:
            new_con = Constraint(con.field, '=', con.value)
            count_eq_field_needed -= 1
        else:
            op = random.choice(list(set(OPS) - set(['='])))
            new_con = Constraint(con.field, op, con.value)
        constraints[eq_field][idx] = new_con
        

    def lget(l, i):
        try:
            return l[i]
        except IndexError:
            return None

    def constraint_exists(l, con):
        for c in l:
            if c.field == con.field:
                return True
        return False

    all_constraints = []

    for cons in constraints.values():
        all_constraints += cons

    for idx, con in enumerate(all_constraints):
        sub_pos = idx % count
        sub = lget(subs, sub_pos)
        sub = sub or []
        exists = True
        if not sub:
            sub = []
            exists = False
        if constraint_exists(sub, con):
            continue
        sub.append(con)
        if not exists:
            subs.append(sub)
        else:
            subs[sub_pos] = sub

    return subs


@click.group()
def cli():
    pass

@cli.command('publish')
@click.option('-n', '--count', required=True, type=click.INT)
def publish(count):
    pubs = [get_random_pub() for _ in range(count)]

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
    
    subs = get_random_subs(count, fields_percentages, eq_field_percentage)

    for sub in subs:
        sub_str = ';'.join(['({}{}{})'.format(con.field, con.op, con.value) for con in sub])
        print(sub_str)

if __name__ == "__main__":
    cli()