# coding: utf8
import datetime
import json
from collections import defaultdict

from django.http.response import HttpResponse

from sentry.models.event import Event
from sentry.models.group import Group


def get_yesterday_log_info(limit=10):
    """
    获取昨天的日志统计信息
    {
        count: xxx,
        groups: [
            {'id': xx, 'title': xx, 'count': xx},
            ...
        ]
    }
    """
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    groups = Event.objects.filter(datetime__gt=yesterday).values_list('group', flat=True)
    all_count = 0
    group_sumary = defaultdict(lambda: 0)
    for group in groups:
        all_count += 1
        group_sumary[group] += 1
    group_sumary_list = sorted(group_sumary.items(), key=lambda x: x[1], reverse=True)
    result = {'count': all_count, 'groups': []}
    for item in group_sumary_list[:limit]:
        title = Group.objects.filter(id=item[0]).values_list('message', flat=True)[0]
        result['groups'].append({'id': item[0], 'title': title, 'count': item[1]})
    return result


def get_daily_info(request):
    limit = int(request.GET.get('limit', 10))
    infos = get_yesterday_log_info(limit)
    return HttpResponse(content=json.dumps(infos), content_type='application/json')
