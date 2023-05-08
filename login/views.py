from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm
from .models import UserProfile
from django.views.generic import DetailView
from django.core.mail import send_mail, EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import generate_token
from django.views.decorators.csrf import ensure_csrf_cookie,csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import requires_csrf_token
from django.http import HttpResponseRedirect



def home(request):
    # Your existing code here

    # Check for any error messages
    error_messages = messages.get_messages(request)

    # Pass the error messages to the template context
    context = {'error_messages': error_messages}
    return render(request, "authentication/index.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            address = form.cleaned_data.get('address')
            profile = form.cleaned_data.get('profile')

            user = User.objects.create_user(
                username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = False
            user.save()

            user_profile = UserProfile.objects.create(
                user=user, address=address, profile=profile)

            messages.success(
                request, 'Your account has been successfully created, we sent you a confirmation email please confirm it to activate account')
            # welcome email
            subject = 'welcome to piyush garage'
            message = 'hello' + user.first_name+"welcome to piyush garage"
            from_email = 'piyushgaragevidisha@gmail.com'
            to_list = [user.email]
            send_mail(subject, message, from_email, to_list)
            # confirmation email
            current_site = get_current_site(request)
            email_subject = "confirm your email @ piyush 's garage"
            message2 = render_to_string('authentication/email_confirmation.html', {
                'name': user.first_name,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': generate_token.make_token(user)
            })
            email = EmailMessage(
                email_subject,
                message2,
                from_email,
                [user.email],

            )
            email.fails_silently = True
            email.send()
            return redirect('signin')

        else:
            print(form.errors)

    else:
        form = SignUpForm()

    return render(request, 'authentication/signup.html', {'form': form})


def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            fname = user.first_name
            # user = get_object_or_404(User)
            context = {'user': user}
            print(dir(user))
            return HttpResponseRedirect('home')
        else:
            messages.error(request, "Bad credentials,try again or create a account")
            return redirect('home')
    if request.session.get('logged_in'):
        user = request.user
        fname = user.first_name
        context = {'user': user}
        return render(request, "authentication/index.html", context)
    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    request.session['logged_in'] = False
    messages.success(request, "Logged out successfully")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')


def appointment(request):


    if request.method == "POST":
        username=request. POST.get('username');
        useremail=request. POST.get('useremail');
        service=request. POST.get('service');
        message=request. POST.get('message');
        date=request. POST.get('date');


# send an email
        subject = 'welcome to piyush garage'
        message = 'hello' + username+"your booking for "+service+"on "+date+"has been booked sucessfully"
        from_email = 'piyushgaragevidisha@gmail.com'
        to_list = [useremail,from_email]
        send_mail(subject, message, from_email, to_list)
        print(username)
        return render(request, 'appointment.html', {'username':username,'message':message,'useremail':useremail,'service':service,'date':date})
    else:
        return render(request, "authentication/index.html")
        
