import logging
from time import sleep

import requests
from schedule import Scheduler

from settings import REQUESTS

def build_logging():
    logging.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s',
                       level=logging.DEBUG, filename='schedule.log')


build_logging()

schedule = Scheduler()

def _get_urls(request_description):
    return [request_description.get('template', '').format(**arg) \
        for arg in request_description.get('args', [])] \
            or request.get('template')


def _get_request_args(request_description):
    return [{'args': [url,], 'kwargs': {'auth': request_description.get('auth')}} \
        for url in _get_urls(request_description)]


def _get_request(request_type):
    return requests.__dict__[request_type]


def execute(request_type, request_args):
    request = _get_request(request_type)
    for request_arg in request_args:
        try:
            response = request(*request_arg.get('args', []), **request_arg.get('kwargs', {}))
            logging.info('Request {} finish with parametrs: {}. Status: {}'\
                        .format(request_type, request_args, response.status_code))
        except:
            logging.error('Reauest {} error with parametrs: {}.'.format(request_type, request_args))


def _get_period(period, interval):
    if isinstance(interval, dict):
        for at, time in interval.items():
            yield getattr(schedule.every(), period).at(time)\
                  if at else getattr(schedule.every(), period)
    else:
        yield getattr(schedule.every(interval), period)


def _get_periods(request_schedule):
    for period, interval in request_schedule.items():
        yield from _get_period(period, interval)


def _build_periods(request_type, request_description):
    request_args = _get_request_args(request_description)
    for period in _get_periods(request_description.get('schedule', {})):
        period.do(execute, request_type, request_args)


def _build_request_type_periods(request_type, request_descriptions):
    for request_description in request_descriptions:
        _build_periods(request_type, request_description)


def build_schedule(settings):
    for request_type, request_descriptions in settings.items():
        _build_request_type_periods(request_type, request_descriptions)


if __name__ == '__main__':
    build_schedule(REQUESTS)
    logging.info('Start with schedule: {}.'.format(schedule.jobs))
    while True:
        schedule.run_pending()
        sleep(1)
