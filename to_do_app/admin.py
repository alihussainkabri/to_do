from django.contrib import admin
from .models import User,User_details,Task_add,task_date,Verification,Reminder_data
# Register your models here.
admin.site.register(User_details)
admin.site.register(Task_add)
admin.site.register(task_date)
admin.site.register(Verification)
admin.site.register(Reminder_data)