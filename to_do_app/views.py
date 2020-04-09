from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from .models import User_details,Task_add,task_date,Verification
import datetime
from random import randint
import smtplib

# Create your views here.
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

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        user = User.objects.create_user(username=name,email=email,password=password)
        user.save()
        user_detail = User_details.objects.get_or_create(user = user,mobile=mobile,status = "not-verified")[0]
        user_detail.save()
        otp = randint(1000,9999)
        temp_user_id =User.objects.filter(username=user)[0].id
        verification_step = Verification.objects.get_or_create(user = User.objects.filter(username=user)[0],otp=otp,purpose = "signup")[0]
        verification_step.save()
        send_mail(temp_user_id)
        request.session['signup_pass'] = password
        request.session['temp_user_id'] = temp_user_id
        request.session['signup_email'] = email
        # msg = "Your Account Has Been Created Successfully! Please Fill Below Credentials To Login!"
        return redirect('/verification/')
    return render(request,'to_do_app/login.html',{'msg':msg})

def verification(request):
    if request.method == 'POST':
        o1 = request.POST['o1']
        o2 = request.POST['o2']
        o3 = request.POST['o3']
        o4 = request.POST['o4']
        otp = o1+o2+o3+o4
        temp_user_id = request.session.get('temp_user_id')
        print(temp_user_id)
        match = Verification.objects.get(user = User.objects.get(id=temp_user_id))
        if match.otp == otp:
            user_detail_upd = User_details.objects.get(user = User.objects.get(id=temp_user_id))
            user_detail_upd.status = "verified"
            user_detail_upd.save()
            user = Verification.objects.get(user=User.objects.get(id=temp_user_id)).delete()
            print('1')
            try:
                del request.session['signup_pass']
                del request.session['temp_user_id']
                del request.session['signup_email']
            except KeyError:
                pass
            msg = "Your Account Has Been Created Successfully! Please Fill Below Credentials To Login!"
            return render(request,'to_do_app/login.html',{'msg':msg})
        else:
            msg = "Please Enter Correct OTP"
            return render(request,'to_do_app/verification.html',{'msg':msg})

    return render(request,'to_do_app/verification.html')

def signout(request):
    logout(request)
    try:
        del request.session['user_id']
    except KeyError:
        pass
    msg = "You Have Been Logged Out Successfully!"
    return render(request,'to_do_app/login.html',{'msg':msg})

def page(request):
    d = {}
    l1 = []
    user = request.session.get('user_id')
    full_user = User.objects.get(id=user)
    dates = task_date.objects.filter(user=full_user).order_by('date')
    for date in dates:
        task = Task_add.objects.filter(user=full_user,date=date.date)
        if len(task) > 0:
            d[date.date] = task
    # print(d1)
    task_detail = Task_add.objects.filter(user=full_user)
    for t in task_detail:
        if t.status == 'deactivate':
            l1.append(t.class_name)
    return render(request,'to_do_app/index.html',{'d1':d,'l1':l1,'user':full_user})

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


def send_mail(user_id):
    sender = "list2do52@gmail.com"
    user_mail = User.objects.get(id=user_id)
    user_name = user_mail.username
    reciever = user_mail.email
    otp_model = Verification.objects.get(user=user_mail)
    otp = otp_model.otp
    subject = "OTP VERIFICATION LIST2DO"
    body = f"Hey {user_name} Thanks To Signup With Us\n\n\nEnter Below OTP In Website To Verify Your Identity\n{otp}"
    msg = f"Subject : {subject}\n\n\n{body}"
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(sender,'bolbmlktlvkvrvdq')
    server.sendmail(sender,reciever,msg)
    server.quit()