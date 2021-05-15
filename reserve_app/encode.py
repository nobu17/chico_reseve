import json
import datetime
from . import models


class ModelEncoder(json.JSONEncoder):
    def default(self, o):
        # json encode is needed concern jst convert
        if isinstance(o, models.ReserveModel):
            return {
                'pk': o.pk,
                'start_date': o.start_date.strftime('%Y-%m-%d'),
                'start_time': o.start_time.strftime('%H:%M'),
                'number': o.number,
                'seat_used_number': o.seat_used_number,
                'memo': o.memo,
                'full_name': o.full_name,
                'tel': o.tel,
                'email': o.email,
                'created_at': o.created_at.astimezone(datetime.timezone(datetime.timedelta(hours=+9))).strftime('%Y-%m-%d %H:%M'),
                'updated_at': o.updated_at.astimezone(datetime.timezone(datetime.timedelta(hours=+9))).strftime('%Y-%m-%d %H:%M'),
                'seat_name': o.seat.name
            }
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
            
        return super(ModelEncoder, self).default(o)
