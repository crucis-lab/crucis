"""Explicit local clock observations; timer resolution is not accuracy (DLV-08/09)."""
import datetime
from decimal import Decimal
from . import api
from .model import ExecutionError, known, unknown, number
from .schema import validate_value


class WallClock:
    def now(self, context):
        value = {'time_type': 'utc_instant',
            'value': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z'),
            'precision': 'fractional_second', 'clock': unknown('s3.clock_identity_unestablished'),
            'uncertainty_seconds': unknown('s3.clock_accuracy_unestablished')}
        return api.CallResult('completed', api.ClockReading(known(value), unknown(), api.RecordDelta()))


def require_before(deadline, reading):
    """An upper bound on current UTC must be strictly before the deadline."""
    validate_value(deadline, 'K(Time)')
    if deadline.get('state') == 'not_applicable':
        if deadline['rule']['name'] != 's3.no_absolute_deadline':
            raise ExecutionError('s3.deadline_nonapplicability_uninterpreted')
        return
    if deadline.get('state') != 'known' or not isinstance(reading, api.ClockReading) or reading.value.get('state') != 'known':
        raise ExecutionError('s3.deadline_validity_unestablished')
    end, current = deadline['value'], reading.value['value']
    for value in (end, current):
        validate_value(value, 'Time')
        if value['time_type'] != 'utc_instant' or value['uncertainty_seconds']['state'] != 'known':
            raise ExecutionError('s3.comparable_clock_bound_unestablished')
        bound = value['uncertainty_seconds']['value']
        if bound['number_type'] == 'nonfinite' or Decimal(bound['text']) < 0:
            raise ExecutionError('s3.clock_error_bound_invalid')
    def seconds(value):
        instant = datetime.datetime.fromisoformat(value['value'].replace('Z', '+00:00'))
        epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
        delta = instant - epoch
        return Decimal(delta.days * 86400 + delta.seconds) + Decimal(delta.microseconds) / Decimal(1000000)
    if seconds(current) + Decimal(current['uncertainty_seconds']['value']['text']) >= seconds(end) - Decimal(end['uncertainty_seconds']['value']['text']):
        raise ExecutionError('s3.deadline_expired_or_uncertain')
