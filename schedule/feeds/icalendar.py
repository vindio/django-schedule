import vobject
import pytz
from django.conf import settings

from django.http import HttpResponse

EVENT_ITEMS = (
    ('uid', 'uid'),
    ('dtstart', 'start'),
    ('dtend', 'end'),
    ('summary', 'summary'),
    ('location', 'location'),
    ('last_modified', 'last_modified'),
    ('created', 'created'),
)

FREQNAMES = ['YEARLY','MONTHLY','WEEKLY','DAILY','HOURLY','MINUTELY','SECONDLY']

def reqstr(self):
    parts = ['FREQ='+FREQNAMES[self._freq]]
    if self._interval != 1:
        parts.append('INTERVAL='+str(self._interval))
    if self._wkst:
        parts.append('WKST='+str(self._wkst))
    if self._count:
        parts.append('COUNT='+str(self._count))

    for name, value in [
            ('BYSETPOS', self._bysetpos),
            ('BYMONTH', self._bymonth),
            ('BYMONTHDAY', self._bymonthday),
            ('BYYEARDAY', self._byyearday),
            ('BYWEEKNO', self._byweekno),
            ('BYWEEKDAY', self._byweekday),
            ('BYHOUR', self._byhour),
            ('BYMINUTE', self._byminute),
            ('BYSECOND', self._bysecond),
            ]:
        if value:
            parts.append(name+'='+','.join(str(v) for v in value))

    return ';'.join(parts)


class ICalendarFeed(object):

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        cal = vobject.iCalendar()
        tz = pytz.timezone(settings.TIME_ZONE)

        for item in self.items():

            event = cal.add('vevent')

            for vkey, key in EVENT_ITEMS:
                value = getattr(self, 'item_' + key)(item)
                if value:
                    event.add(vkey).value = value

            rule = item.get_rrule_object(tz)
            if rule:
                event.add('rrule').value = reqstr(rule)


        response = HttpResponse(cal.serialize())
        response['Content-Type'] = 'text/calendar'

        return response

    def items(self):
        return []

    def item_uid(self, item):
        pass

    def item_start(self, item):
        pass

    def item_end(self, item):
        pass

    def item_summary(self, item):
        return str(item)

    def item_location(self, item):
        pass

    def item_last_modified(self, item):
        pass

    def item_created(self, item):
        pass
