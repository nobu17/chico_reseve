import json
from . import models


class ModelEncoder(json.JSONEncoder):
    def default(self, o):
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
                'created_at': o.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': o.updated_at.strftime('%Y-%m-%d %H:%M'),
                'seat_name': o.seat.name
            }
        return super(ModelEncoder, self).default(o)
