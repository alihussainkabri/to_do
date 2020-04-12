from .models import *
import smtplib

def reminder(current_date,current_time):
    user_list = []
    user_task_dict = {}
    task = Task_add.objects.filter(date = current_date)
    for t in task:
        if t.user not in user_list:
            user_list.append(t.user)
    for user in user_list:
        user_task = Task_add.objects.filter(user=user,date=current_date)
        user_task_dict[user] = user_task
    
    for key,value in user_task_dict.items():
        if current_time == "20:00":
            return_status =  send_reminder(key,value,"Good Evening")
            upload = Reminder_data.objects.get_or_create(date=current_date,status ="All Email Sent")[0]
            upload.save()
        elif current_time == '09:00':
            return_status =  send_reminder(key,value,"Good Morning")


def send_reminder(key,value,status):
    v = []
    for va in value:
        v.append(va.title)
    user_email = key.email
    sender = "list2do52@gmail.com"
    subject = "TASK REMINDER LIST2DO"
    body = f"Hey {key.username} {status}! Forgot Task! Don't Worry\n\n\nBelow Mentioned Is Your Task List\n\n{v}"
    msg = f"Subject : {subject}\n\n\n{body}"
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender,'bolbmlktlvkvrvdq')
    server.sendmail(sender,user_email,msg)
    server.quit()
    return 'done'

def delete_past(past_date,current_time):
    print('hy')
    Task_add.objects.filter(date=past_date).delete()
    Verification.objects.filter(date=past_date).delete()
