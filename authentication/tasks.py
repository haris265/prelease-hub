from celery import shared_task
from django.contrib.auth import get_user_model
from .utils import send_push_notification 

User = get_user_model()

@shared_task
def send_parking_reminder_task(user_id):
    try:
        user = User.objects.get(id=user_id)
        
        send_push_notification(
            user=user,
            title="Parking Time Up! 🚗",
            body="Your parking timer has expired. It's time to move your vehicle!",            
            data={"type": "parking_reminder"} 
        )
        user.parking_task_id = None
        user.save()
        return f"Reminder sent to {user.email}"
    except User.DoesNotExist:
        return "User not found"