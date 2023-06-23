from django.core import serializers
from management.models import Schedulefix

def get_schedule_data():
    # Schedulefix 모델 데이터 가져오기
    schedules = Schedulefix.objects.all()

    # JSON 형식으로 변환
    schedule_data = serializers.serialize('json', schedules)

    return schedule_data