from django.shortcuts import render,redirect
from django.contrib.auth.models import User,auth
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import time
from .models import ManagerRequest
# Create your views here.
def user(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        confirmpassword=request.POST.get('confirmpassword')
        
        errors = {}

        if username == '':
            print(errors)
            messages.error(request,"Username is null")
            errors['username'] ='username can not be null'
            print(errors)

        if email == '': 
            errors['email'] = 'email can not be null'
            messages.error(request,"email is null")

        if password == '':
            errors['password']  = 'password can not be null'
            messages.error(request,"password is null")
        else:
            try:
                validate_password(password)
            except ValidationError as e:
                errors['password']  = e.messages
                for m in e.messages:
                    messages.error(request, m)

        if confirmpassword == '':
            errors['confirm_password']  = 'confirm_password can not be null'
            messages.error(request,"Type the password again")
        
        print(errors)
        if errors:
            print('I AM ERRORS')
            return render(request,'reg.html', {"errors":errors, 'form_data': request.POST})
    
        if password==confirmpassword:
            if User.objects.filter(username=username).exists():
                messages.error(request,"Username already taken")
                # return redirect('register')
                return render(request,'reg.html', {"errors":errors, 'form_data': request.POST})
            elif User.objects.filter(email=email).exists():
                messages.error(request,"Email already taken")
                # return redirect('register')
                return render(request,'reg.html', {"errors":errors, 'form_data': request.POST})

            else:
                user_reg=User.objects.create_user(username=username,email=email,password=password)
                user_reg.save()
                messages.success(request,"Successfully created")
                user=auth.authenticate(username=username,password=password)
                if user is not None:
                    auth.login(request,user)
                    messages.success(request,"Login Success")

                return redirect('index')
        else:
            messages.error(request,"Password doesn't match")
            return render(request,'reg.html', {"errors":errors, 'form_data': request.POST})


    return render(request,'reg.html')

def login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=auth.authenticate(username=username,password=password)
        if user is not None:
            
            auth.login(request,user)
            messages.success(request,"Login Success")
            
            return redirect('index')
        else:
            messages.error(request,"Invalid credentials")
            return redirect('login')
        
        
    return render(request,'log.html')

def logout(request):
    auth.logout(request)
    return redirect('/')




def become_manager(request):

    user = request.user
    is_admin = user.is_superuser
    all_requests = ManagerRequest.objects.filter(sender__is_staff=False)

    if request.method=='POST':

        if is_admin:
            sender=request.POST.get('sender')
            requester = User.objects.filter(username=sender).first()
            # print(sender)
            # print(requester)
            # print(requester.is_staff)
            requester.is_staff=True
            requester.save()
            messages.success(request,"Approved")
            return redirect('manager_request')
        else:
            mail=request.POST.get('mail')
            proof=request.POST.get('proof')
            


            try:
                manager_request = ManagerRequest.objects.create(sender=user,mail=mail,proof=proof)

                if manager_request:
                    messages.success(request,"Message successfully sent")
                    return redirect('index')
            except:

                messages.error(request,"Something went wrong")
                return redirect('manager_request')

    if is_admin:
        return render(request, 'manager_request.html', {'all_requests':all_requests})

    else:
        return render(request, 'manager_request.html')
