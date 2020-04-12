from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .models import User_details,Task_add,task_date,Verification
from django.contrib.auth.decorators import login_required
import datetime
from random import randint
import smtplib
import threading
import time
from .advanced import reminder,delete_past

start_date = str(datetime.datetime.now()).split()[0]
next_day = str(datetime.datetime.today() + datetime.timedelta(days=1))
next_day = next_day.split()[0]
upcoming_start = str(datetime.datetime.today() + datetime.timedelta(days=2))
upcoming_start = upcoming_start.split()[0]
past_data_start = str(datetime.datetime.today() - datetime.timedelta(days=4))
past_data_start = past_data_start.split()[0]
past_data_end = str(datetime.datetime.today() - datetime.timedelta(days=1))
past_data_end = past_data_end.split()[0]

def run():
    global start_date,next_day,upcoming_start,past_data_start,past_data_end
    while True:
        current_date = str(datetime.datetime.now()).split()[0]
        current_time = str(datetime.datetime.now()).split()[1][0:5]
        if current_time == "08:30" or current_time == "16:30":
            time.sleep(55)
            reminder(current_date,current_time)
        elif current_time == '00:03':
            time.sleep(50)
            past_date = str(datetime.datetime.today() - datetime.timedelta(days=3))
            past_date = past_date.split()[0]
            past_data_start = str(datetime.datetime.today() - datetime.timedelta(days=4))
            past_data_start = past_data_start.split()[0]
            past_data_end = str(datetime.datetime.today() - datetime.timedelta(days=1))
            past_data_end = past_data_end.split()[0]
            next_day = str(datetime.datetime.today() + datetime.timedelta(days=1))
            next_day = next_day.split()[0]
            upcoming_start = str(datetime.datetime.today() + datetime.timedelta(days=2))
            upcoming_start = upcoming_start.split()[0]
            start_date = current_date
            delete_past(past_date,current_time)
t1 = threading.Thread(target=run)
t1.start()

def index(request):
    return render(request,'to_do_app/base.html')

def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        username = User.objects.get(email=email)
        auth = authenticate(request,username=username.username,password=password)
        if auth:
            user_check = User_details.objects.get(user=User.objects.get(username = auth))
            if user_check.status == "verified":
                login(request,auth)
                user = User.objects.get(username = auth)
                request.session['user_id'] = user.id
                return redirect('/index/')
            else:
                msg = 'your account is not verified yet!'
                return render(request,'to_do_app/login.html',{'msg':msg})
        else:
            msg = 'please provide valid credentials!'
            return render(request,'to_do_app/login.html',{'msg':msg})
    return render(request,'to_do_app/login.html')

def forgot(request):
    forgot_user = ""
    if request.method == 'POST':
        email = request.POST['email']
        try:
            forgot_user = User.objects.get(email=email)
        except Exception as e:
            pass
        if forgot_user:
            otp = randint(1000,9999)
            forgot_verification = Verification.objects.get_or_create(email=email,otp=otp,purpose="Forgot")[0]
            forgot_verification.save()
            return_value = send_mail(email,"forgot")
            if return_value == "done":
                msg = "Forgot"
                return render(request,'to_do_app/verification.html',{'msg':msg,'email':email})
            else:
                msg = "Process Not Complete"
                Verification.objects.filter(email=email)[0].delete()
                return render(request,'to_do_app/login.html',{'msg':msg})
        else :
            msg = "No User Found With This Email"
            return render(request,'to_do_app/login.html',{'msg':msg})

def forgot1(request):
    if request.method == 'POST':
        o1 = request.POST['o1']
        o2 = request.POST['o2']
        o3 = request.POST['o3']
        o4 = request.POST['o4']
        email = request.POST['email']
        otp_get = Verification.objects.filter(email=email)[0]
        otp = o1+o2+o3+o4
        if otp_get.otp == otp:
            return render(request,'to_do_app/password.html',{'otp':otp,'email':email})
        else:
            msg = "Process Not Complete"
            Verification.objects.filter(email=email)[0].delete()
            return render(request,'to_do_app/login.html',{'msg':msg})
            
def forgot2(request):
    if request.method == 'POST':
        p1 = request.POST['p1']
        p2 = request.POST['p2']
        otp = request.POST['otp']
        email = request.POST['email']
        if p1 == p2:
            otp_get = Verification.objects.filter(email=email)[0]
            if otp_get.otp == otp:
                u1 = User.objects.get(email=email)
                u1.set_password(p1)
                u1.save()
                Verification.objects.filter(email=email)[0].delete()
                msg = "Your Password Reset Successfully"
                return render(request,'to_do_app/login.html',{'msg':msg})
            else:
                msg = "Incorrect OTP Please Go to Login Page Again and Try Again"
                Verification.objects.filter(email=email)[0].delete()
                return render(request,'to_do_app/login.html',{'msg':msg})
        else:
            msg = "Password Doesnot Matches"
            Verification.objects.filter(email=email)[0].delete()
            return render(request,'to_do_app/login.html',{'msg':msg})
def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        otp = randint(1000,9999)
        verification_step = Verification.objects.get_or_create(email=email,otp=otp,purpose = "signup")[0]
        verification_step.save()
        return_value = send_mail(email,"none")
        if return_value == 'done':
            request.session['signup_pass'] = password
            request.session['signup_email'] = email
            request.session['signup_mobile'] = mobile
            request.session['signup_name'] = name
            # msg = "Your Account Has Been Created Successfully! Please Fill Below Credentials To Login!"
            return redirect('/verification/')
        else:
            msg = "OTP VERIFICATION PROCESS FAILS DUE TO AN ERROR PLEASE TRY LATER BY GOING TO SIGNUP PAGE!"
            Verification.objects.filter(email=email).delete()
            return render(request,'to_do_app/login.html',{'msg':msg})
    return render(request,'to_do_app/login.html',{'msg':msg})

def verification(request):
    if request.method == 'POST':
        o1 = request.POST['o1']
        o2 = request.POST['o2']
        o3 = request.POST['o3']
        o4 = request.POST['o4']
        otp = o1+o2+o3+o4
        signup_email = request.session.get('signup_email')
        signup_name = request.session.get('signup_name')
        signup_pass = request.session.get('signup_pass')
        signup_mobile = request.session.get('signup_mobile')
        match = Verification.objects.get(email=signup_email)
        if match.otp == otp:
            user = User.objects.create_user(username=signup_name,email=signup_email,password=signup_pass)
            user.save()
            user_detail = User_details.objects.get_or_create(user = user,mobile=signup_mobile,status = "verified")[0]
            user_detail.save()
            verification_delete = Verification.objects.get(email=signup_email).delete()
            try:
                del request.session['signup_pass']
                del request.session['signup_mobile']
                del request.session['signup_name']
                del request.session['signup_email']
            except KeyError:
                pass
            msg = "Your Account Has Been Created Successfully! Please Fill Below Credentials To Login!"
            return render(request,'to_do_app/login.html',{'msg':msg})
        else:
            msg = "PROCESS NOT COMPLETE DUE TO INCORRECT OTP PLEASE GO AGAIN TO SIGNUP PAGE AND CONTINUE!"
            Verification.objects.get(email=signup_email).delete()
            return render(request,'to_do_app/verification.html',{'msg':msg})

    return render(request,'to_do_app/verification.html')

@login_required
def signout(request):
    logout(request)
    try:
        del request.session['user_id']
    except KeyError:
        pass
    msg = "You Have Been Logged Out Successfully!"
    return render(request,'to_do_app/login.html',{'msg':msg})

@login_required
def page(request):
    global start_date,upcoming_start,next_day
    d = {}
    l1 = []
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    task_detail = Task_add.objects.filter(user=full_user)
    for t in task_detail:
        if t.status == 'deactivate':
            l1.append(t.class_name)
    if len(task_detail) > 0:
        today = Task_add.objects.filter(user=full_user,date=start_date)
        d["Today"] = today
        next = Task_add.objects.filter(user=full_user,date=next_day)
        d["Tomorrow"] = next
        upcoming_end =Task_add.objects.filter(user=full_user).order_by('-date')[0].date
        upcoming = Task_add.objects.filter(user=full_user,date__range=[upcoming_start,upcoming_end])
        d["Upcoming"] = upcoming
        past = Task_add.objects.filter(user=full_user,date__range=[past_data_start,past_data_end])
        d["Past Tasks"] = past
    else:
        d = {}
    return render(request,'to_do_app/index.html',{'d1':d,'l1':l1,'user':full_user})


@login_required
def add_task(request):
    if request.method == 'POST':
        title = request.POST['title']
        date = request.POST['date']
        content = request.POST['content']
        user = request.session.get('user_id')
        full_user = User.objects.get(id=user)
        class_name = f"{user}-{date}"
        task_creation = Task_add.objects.get_or_create(user=full_user,title=title,content=content,date=date,class_name=class_name)[0]
        task_creation.save()
        task_date_add = task_date.objects.get_or_create(user=full_user,date = date)[0]
        task_date_add.save()
        task_add_update = Task_add.objects.get(user=full_user,class_name=class_name)
        task_id1 = task_add_update.task_id
        class_name = f"{user}-{task_id1}"
        task_add_update.class_name = class_name
        task_add_update.save()

        Task_add.objects.filter(user=full_user)
        return redirect('/index/')


def ajax_status(request):
    status = request.GET.get('status', None)
    class_name = request.GET.get('class_name', None)
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    task_add_update = Task_add.objects.get(user=full_user,class_name=class_name)
    task_add_update.status = status
    task_add_update.save()
    data = {
        'status_return' : 'user status updated successfully'
    }
    return JsonResponse(data)

def ajax_status_reactivate(request):
    status = request.GET.get('status', None)
    class_name = request.GET.get('class_name', None)
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    task_add_update = Task_add.objects.get(user=full_user,class_name=class_name)
    task_add_update.status = status
    task_add_update.save()
    data1 = {
        'status_return' : 'user status activated successfully'
    }
    return JsonResponse(data1)

def ajax_status_delete(request):
    class_name = request.GET.get('class_name', None)
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    task_add_update = Task_add.objects.get(user=full_user,class_name=class_name).delete()
    data2 = {
        'status_return' : 'user task deleted successfully successfully'
    }
    return JsonResponse(data2)

def ajax_task_details(request):
    class_name = request.GET.get('class_name', None)
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    task_add_update = Task_add.objects.get(user=full_user,class_name=class_name)
    data3 = {
        'title' : task_add_update.title,
        'content' : task_add_update.content
    }

    return JsonResponse(data3)


def send_mail(email,note):
    sender = "list2do52@gmail.com"
    reciever = email
    otp_model = Verification.objects.filter(email=email)[0]

    otp = otp_model.otp
    subject = "OTP VERIFICATION LIST2DO"
    if note == "forgot":
        body = f"Hey {email} Forgot Password! Don't Worry\n\n\nEnter Below OTP In Website To Verify Your Identity\n{otp}"    
    else:
        body = f"Hey {email} Thanks To Signup With Us\n\n\nEnter Below OTP In Website To Verify Your Identity\n{otp}"
    msg = f"Subject : {subject}\n\n\n{body}"
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender,'bolbmlktlvkvrvdq')
    server.sendmail(sender,reciever,msg)
    server.quit()
    return 'done'