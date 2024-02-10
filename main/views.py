from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from .forms import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Profile, PasswordModel, CardModel, NoteModel
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import secrets
import string
from django.template.loader import render_to_string
from datetime import datetime
import calendar
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail

#Home view
def home(request):
    return render(request, "home.html")

#Forgot password view
def forgot_password(request):
    if request.GET.get("form_type") == "checkEmailForm":
        
        #Checks if email exist then send a verification code
        if User.objects.filter(email=request.GET.get("email")).exists():
            user = User.objects.get(email=request.GET.get("email"))
            profile = Profile.objects.get(user=user)
            profile.reset_code = ''.join(secrets.choice(string.digits) for i in range(6))
            profile.save()
            request.session['user_id'] = user.id
            send_mail("Dark Piglock", "Hello, " + user.username + "\n\n\nYour reset password code is: " + profile.reset_code, "darkshadogt@gmail.com", [user.email], fail_silently=True)
            return JsonResponse({'status':'success'})
        
        #If email does not exist, display an error message
        else:
            forgot_password_form_html = render_to_string("partials/reset/forgot_password_form.html", {'error':'No user found with that email'})
            return JsonResponse({'status':'error', 'forgot_password_form_html':forgot_password_form_html})
    return render(request, "forgot_password.html")

#Password verification view
def password_verification(request):
    user = User.objects.get(id=request.session.get('user_id'))
    profile = Profile.objects.get(user=user)
    if request.GET.get("form_type") == "verificationForm":
        
        #Checks if the verification code is correct
        if request.GET.get("verification_code") == profile.reset_code:
            profile.reset_code = ""
            profile.save()
            return JsonResponse({'status':'success', 'user_id':user.id})
        
        #If it is wrong, display an error message
        else:
            verification_form_html = render_to_string("partials/login_verification/verification_form.html", {'error': 'Incorrect Code'})
            return JsonResponse({'status':'error','verification_form_html':verification_form_html})
    
    #Sends new code to user
    elif request.GET.get("form_type") == "resendCodeForm":
        profile.reset_code = ''.join(secrets.choice(string.digits) for i in range(6))
        profile.save()
        send_mail("Dark Piglock", "Hello, " + user.username + "\n\n\nYour reset password code is: " + profile.reset_code, "darkshadogt@gmail.com", [user.email], fail_silently=True)
        verification_form_html = render_to_string("partials/login_verification/verification_form.html", {'error': 'Verification code sent'})
        return JsonResponse({'verification_form_html':verification_form_html})
    return render(request, "reset_verification.html")

#Reset Password View
def reset_password(request, user_id):
    user = User.objects.get(id=user_id)
    errors = []
    
    #Processes the reset password form
    if request.POST.get("form_type") == "resetForm":
        
        #Checks if the passwords match
        if request.POST.get("password1") == request.POST.get("password2"):
            #Checks if the password is strong enough
            try:
                validate_password(request.POST.get("password1"))
                user.set_password(request.POST.get("password1"))
                return JsonResponse({'status':'success'})

            #If the password is not strong enough, display an error message
            except ValidationError as e:
                errors.extend(e.messages)
                reset_password_form_html = render_to_string("partials/reset/reset_password_form.html", {'errors':errors}, request=request)
                return JsonResponse({'status':'error','reset_password_form_html':reset_password_form_html})
        
        #If the passwords do not match, display an error message
        else:
            errors.append("Passwords do not match.")
            reset_password_form_html = render_to_string("partials/reset/reset_password_form.html", {'errors':errors}, request=request)
            return JsonResponse({'status':'error','reset_password_form_html':reset_password_form_html})
    return render(request, "partials/reset/reset_password.html", {'user_id':user_id})

#Checks if the user logged in
def login_complete_required(view):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('login_complete'):
            # If login is not complete, redirect to login page
            return redirect('login')
        return view(request, *args, **kwargs)
    return wrapper

#Log in verification view
@login_complete_required
def login_verification(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    if request.GET.get("form_type") == "verificationForm":
        #Checks if the verification code is correct
        if request.GET.get("verification_code") == profile.verification_code:
            profile.verification_code = ""
            profile.save()
            request.session['login_complete'] = False
            login(request, user)
            return JsonResponse({'status':'success'})
        #If not, show an error message
        else:
            verification_form_html = render_to_string("partials/login_verification/verification_form.html", {'error': 'Incorrect Code'})
            return JsonResponse({'status':'error','verification_form_html':verification_form_html})
    #Sends a new code to user
    elif request.GET.get("form_type") == "resendCodeForm":
        profile.verification_code = ''.join(secrets.choice(string.digits) for i in range(6))
        profile.save()
        send_mail("Dark Piglock", "Hello, " + user.username + "\n\n\nYour verification code is: " + profile.verification_code, "darkshadogt@gmail.com", [user.email], fail_silently=True)
        verification_form_html = render_to_string("partials/login_verification/verification_form.html", {'error': 'Verification code sent'})
        return JsonResponse({'verification_form_html':verification_form_html})
    return render(request, "login_verification.html", {'user_id':user_id})

# Sign up view
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(username=form.cleaned_data['username'], email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            profile = Profile.objects.create(user=user)
            return JsonResponse({'status':'success'})
        else:
            sign_up_form_html = render_to_string("partials/signup/sign_up_form.html", {'form':form}, request=request)
            return JsonResponse({'status':'error', 'sign_up_form_html':sign_up_form_html})
    else:
        form = SignUpForm()
    return render(request, "signup.html", {'form':form})

#Log in view
def log_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["username"], password=form.cleaned_data["password"])
            profile = Profile.objects.get(user=user)
            
            #If user has two factor authentication on, send verification code
            if profile.two_factor_auth:
                profile.verification_code = ''.join(secrets.choice(string.digits) for i in range(6))
                profile.save()
                send_mail("Dark Piglock", "Hello, " + user.username + "\n\n\nYour verification code is: " + profile.verification_code, "darkshadogt@gmail.com", [user.email], fail_silently=True)
                #Set this to true so user can see the verification page
                request.session['login_complete'] = True
                return JsonResponse({'status':'verify', 'user_id':user.id})
            
            #If not, logs the user in   
            else:
                login(request, user)
                return JsonResponse({'status':'success'})
        else:
            log_in_form_html = render_to_string("partials/login/log_in_form.html", {'form':form}, request=request)
            return JsonResponse({'status':'error', 'log_in_form_html':log_in_form_html})
    else:
        form = LoginForm()
    return render(request, "login.html", {'form':form})

#Dashboard view
@login_required
def dashboard(request):
    #Retrieves the user passwords, notes, cards, and deleted items
    user_passwords = PasswordModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_notes = NoteModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=False)
    deleted_items = []
    deleted_items.extend(PasswordModel.objects.filter(user__username=request.user.username, is_deleted=True))
    deleted_items.extend(NoteModel.objects.filter(user__username=request.user.username, is_deleted=True))
    deleted_items.extend(CardModel.objects.filter(user__username=request.user.username, is_deleted=True))
    
    #Retrieves the user activity
    if request.GET.get("form_type") == "activityForm":
        labels, data = user_activity(request)
        return JsonResponse({'status':'success', 'labels':labels, 'data':data})
    
    return render(request, "dashboard.html", {'username':request.user.username, 'number_of_passwords':user_passwords.count(), 'number_of_notes':user_notes.count(), 'number_of_cards':user_cards.count(), 'number_of_deleted_items':len(deleted_items)})

#Retrieves the user activity
def user_activity(request):
    current_date = datetime.now()
    labels = []
    data = []

    #Retrieves the last six month
    for number in range(5, -1, -1):
        month = (current_date.month - number - 1) % 12 + 1
        passwords = PasswordModel.objects.filter(user__username=request.user.username, is_deleted=False, last_modified__month=month)
        notes = NoteModel.objects.filter(user__username=request.user.username, is_deleted=False, last_modified__month=month)
        cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=False, last_modified__month=month)
        label = calendar.month_abbr[month]
        labels.append(label)
        data.append(passwords.count() + notes.count() + cards.count())

    return labels, data

#Password view
@login_required
def passwords(request):
    addForm = addPasswordForm()

    #Checks if user searched anything, if not search_term is set to None
    if 'password_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['password_search_term']

    #Checks if user selected a search type
    if 'password_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['password_search_type']

    #Processes the search form
    if request.GET.get("form_type") == "searchForm":
        return search_password(request)

    #Pagination for passwords
    page = request.GET.get('page', 1)
    
    user_passwords = filter_passwords(request.user.username, search_term, search_type)
    paginator = Paginator(user_passwords, 6)

    try:
        user_passwords = paginator.page(page)
    except PageNotAnInteger:
        user_passwords = paginator.page(1)
    except EmptyPage:
        user_passwords = paginator.page(paginator.num_pages)

    #Processes the request to update the page
    if request.GET.get("form_type") == "page_updateForm":
        return password_update(request)
    
    #Processes the request to update the pagination
    elif request.GET.get("form_type") == "paginationForm":
        return password_pagination(request)
    
    #Processes the request to add a password
    elif request.POST.get("form_type") == "addPasswordForm":
        return add_password(request, page)
    
    #Processes the request to edit a password
    elif request.POST.get("form_type") == "editPasswordForm":
        return edit_password(request)

    #Processes the password deletion form
    elif request.GET.get("form_type") == "deletePasswordForm":
        return delete_password(request)
    
    return render(request, "passwords.html", {'addForm':addForm, 'username':request.user.username, 'user_passwords':user_passwords, 'search_term':search_term, 'search_type':search_type})

#Returns the filtered passwords
def filter_passwords(user, search_term=None, search_type=None):
    user_passwords = PasswordModel.objects.filter(user__username=user, is_deleted=False)
    user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]

    #Checks if user searched anything
    if search_term != None and search_type is None:
        user_passwords = PasswordModel.objects.filter(user__username=user, website_name__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    elif search_term != None and search_type == "website_name":
        user_passwords = PasswordModel.objects.filter(user__username=user, website_name__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    elif search_term != None and search_type == "username":
        user_passwords = PasswordModel.objects.filter(user__username=user, username__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    elif search_term != None and search_type == "email":
        user_passwords = PasswordModel.objects.filter(user__username=user, email__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    elif search_term != None and search_type == "website_url":
        user_passwords = PasswordModel.objects.filter(user__username=user, website_url__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    elif search_term != None and search_type == "description":
        user_passwords = PasswordModel.objects.filter(user__username=user, short_description__icontains=search_term, is_deleted=False)
        user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    return user_passwords

#Updates the page based on search
def search_password(request):
    if request.GET.get("search_term") != "":
        request.session['password_search_term'] = request.GET.get('search_term')
        request.session.save()
        search_term = request.session['password_search_term']
    else:
        search_term = None
        request.session['password_search_term'] = None
        request.session.save()
    if request.GET.get("search_type") != "":
        request.session['password_search_type'] = request.GET.get('search_type')
        request.session.save()
        search_type = request.session['password_search_type']
    else:
        search_type = None
        request.session['password_search_type'] = None
        request.session.save()
    
    user_passwords = filter_passwords(request.user.username, search_term, search_type)
    
    page = request.GET.get('page', 1)
    paginator = Paginator(user_passwords, 6)

    try:
        user_passwords = paginator.page(page)
    except PageNotAnInteger:
        user_passwords = paginator.page(1)
    except EmptyPage:
        user_passwords = paginator.page(paginator.num_pages)
    
    password_list_html = render_to_string("partials/passwords/password_list.html", {'user_passwords':user_passwords}, request=request)
    pagination_html = render_to_string("partials/passwords/password_pagination.html", {'user_passwords': user_passwords})
    return JsonResponse({'password_list_html': password_list_html, 'pagination_html': pagination_html})

#Adds a new password to the database
def add_password(request, page):
    #Checks if user searched anything, if not search_term is set to None
    if 'password_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['password_search_term']

    #Checks if user selected a search type
    if 'password_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['password_search_type']

    addForm = addPasswordForm(request.POST)
    if addForm.is_valid():
        new_password = PasswordModel(
            user = request.user,
            website_name = addForm.cleaned_data['website_name'],
            username = addForm.cleaned_data['username'],
            password = addForm.cleaned_data['password'],
            website_url = addForm.cleaned_data['website_url'],
            email = addForm.cleaned_data['email'],
            short_description = addForm.cleaned_data['short_description'],
            detailed_description = addForm.cleaned_data['detailed_description']
        )
        new_password.save()

        user_passwords = filter_passwords(request.user.username, search_term, search_type)
        paginator = Paginator(user_passwords, 6)

        try:
            user_passwords = paginator.page(page)
        except PageNotAnInteger:
            user_passwords = paginator.page(1)
        except EmptyPage:
            user_passwords = paginator.page(paginator.num_pages)

        password_list_html = render_to_string("partials/passwords/password_list.html", {'user_passwords':user_passwords}, request=request)
        add_password_form_html = render_to_string("partials/passwords/add_password_form.html", {'addForm':addPasswordForm()}, request=request)
        return JsonResponse({'status': 'success', 'password_list_html': password_list_html, 'page':page, 'add_password_form_html':add_password_form_html})
    else:
        add_password_form_html = render_to_string("partials/passwords/add_password_form.html", {'addForm':addForm}, request=request)
        return JsonResponse({'status': 'error', 'add_password_form_html':add_password_form_html})

#Edits the password information
def edit_password(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'password_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['password_search_term']

    #Checks if user selected a search type
    if 'password_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['password_search_type']

    page = request.POST.get("currentPage")
    editForm = editPasswordForm(request.POST, prefix=request.POST.get("password_id"))
    if not request.POST.get("editForm_password"):
        editForm.add_error(None, "Password is required.")
    if editForm.is_valid():
        edited_password = PasswordModel.objects.get(id=request.POST.get("password_id"))
        edited_password.website_name = editForm.cleaned_data['website_name']
        edited_password.username = editForm.cleaned_data['username']
        edited_password.password = request.POST.get('editForm_password')
        edited_password.website_url = editForm.cleaned_data['website_url']
        edited_password.email = editForm.cleaned_data['email']
        edited_password.short_description = editForm.cleaned_data['short_description']
        edited_password.detailed_description = editForm.cleaned_data['detailed_description']
        edited_password.save()

        user_passwords = filter_passwords(request.user.username, search_term, search_type)
        paginator = Paginator(user_passwords, 6)

        try:
            user_passwords = paginator.page(page)
        except PageNotAnInteger:
            user_passwords = paginator.page(1)
        except EmptyPage:
            user_passwords = paginator.page(paginator.num_pages)

        password_list_html = render_to_string("partials/passwords/password_list.html", {'user_passwords':user_passwords}, request=request)
        return JsonResponse({'status': 'success', 'password_list_html': password_list_html, 'page':page})
    else:
        password = PasswordModel.objects.get(id=request.POST.get("password_id"))
        edit_password_form_html = render_to_string("partials/passwords/edit_password_form.html", {'editForm':editForm, 'password':password}, request=request)
        return JsonResponse({'status': 'error', 'edit_password_form_html':edit_password_form_html, 'password_id':request.POST.get("password_id")})

#Deletes the password
def delete_password(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'password_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['password_search_term']

    #Checks if user selected a search type
    if 'password_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['password_search_type']

    page = request.GET.get("currentPage")
    password_to_delete = PasswordModel.objects.get(id=request.GET.get("password_to_delete_id"))
    password_to_delete.soft_delete()

    user_passwords = filter_passwords(request.user.username, search_term, search_type)
    paginator = Paginator(user_passwords, 6)

    try:
        user_passwords = paginator.page(page)
    except PageNotAnInteger:
        user_passwords = paginator.page(1)
    except EmptyPage:
        user_passwords = paginator.page(paginator.num_pages)

    password_list_html = render_to_string("partials/passwords/password_list.html", {'user_passwords':user_passwords}, request=request)
    pagination_html = render_to_string("partials/passwords/password_pagination.html", {'user_passwords': user_passwords})
    return JsonResponse({'password_list_html': password_list_html, 'pagination_html': pagination_html})

#Updates the pagination for password
def password_pagination(request):
    page = request.GET.get('page', 1)
    user_passwords = PasswordModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_passwords = [(password, editPasswordForm(prefix=str(password.id))) for password in user_passwords]
    paginator = Paginator(user_passwords, 6)

    try:
        user_passwords = paginator.page(page)
    except PageNotAnInteger:
        user_passwords = paginator.page(1)
    except EmptyPage:
        user_passwords = paginator.page(paginator.num_pages)
    pagination_html = render_to_string("partials/passwords/password_pagination.html", {'user_passwords': user_passwords})
    return JsonResponse({'pagination_html': pagination_html})

#Updates the password list based on page number
def password_update(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'password_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['password_search_term']

    #Checks if user selected a search type
    if 'password_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['password_search_type']

    page = request.GET.get('page', 1)
    user_passwords = filter_passwords(request.user.username, search_term, search_type)
    paginator = Paginator(user_passwords, 6)

    try:
        user_passwords = paginator.page(page)
    except PageNotAnInteger:
        user_passwords = paginator.page(1)
    except EmptyPage:
        user_passwords = paginator.page(paginator.num_pages)

    password_list_html = render_to_string("partials/passwords/password_list.html", {'user_passwords':user_passwords}, request=request)
    return JsonResponse({'password_list_html': password_list_html, 'page':page})

#Cards view
@login_required
def cards(request):
    addForm = addCardForm()
    user_cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]

    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    #Processes the search form
    if request.GET.get("form_type") == "searchForm":
        return search_card(request)
    
    #Pagination for cards
    page = request.GET.get('page', 1)
    
    user_cards = filter_cards(request.user.username, search_term, search_type)
    paginator = Paginator(user_cards, 4)
    try:
        user_cards = paginator.page(page)
    except PageNotAnInteger:
        user_cards = paginator.page(1)
    except EmptyPage:
        user_cards = paginator.page(paginator.num_pages)

    #Processes the request to update the page
    if request.GET.get("form_type") == "page_updateForm":
        return card_update(request)
    
    #Processes the request to update the pagination
    elif request.GET.get("form_type") == "paginationForm":
        return card_pagination(request)
    
    #Processes the request to add a card
    elif request.POST.get("form_type") == "addCardForm":
        return add_card(request, page)
    
    #Processes the request to edit a card
    elif request.POST.get("form_type") == "editCardForm":
        return edit_card(request)
    
    #Processes the card deletion form
    elif request.GET.get("form_type") == "deleteCardForm":
        return delete_card(request)
    
    return render(request, "cards.html", {'username':request.user.username, 'addForm':addForm, 'user_cards':user_cards, 'search_term':search_term, 'search_type':search_type})

#Returns the filtered cards
def filter_cards(user, search_term=None, search_type=None):
    user_cards = CardModel.objects.filter(user__username=user, is_deleted=False)
    user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]

    #Checks if user searched anything
    if search_term != None and search_type is None:
        user_cards = CardModel.objects.filter(user__username=user, card_brand__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    elif search_term != None and search_type == "card_number":
        user_cards = CardModel.objects.filter(user__username=user, card_number__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    elif search_term != None and search_type == "card_type":
        user_cards = CardModel.objects.filter(user__username=user, card_type__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    elif search_term != None and search_type == "name":
        user_cards = CardModel.objects.filter(user__username=user, cardholder_name__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    elif search_term != None and search_type == "date":
        user_cards = CardModel.objects.filter(user__username=user, expiration_date__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    elif search_term != None and search_type == "card_brand":
        user_cards = CardModel.objects.filter(user__username=user, card_brand__icontains=search_term, is_deleted=False)
        user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    return user_cards

#Updates the page based on search
def search_card(request):
    if request.GET.get("search_term") != "":
        request.session['card_search_term'] = request.GET.get('search_term')
        request.session.save()
        search_term = request.session['card_search_term']
    else:
        search_term = None
        request.session['card_search_term'] = None
        request.session.save()
    if request.GET.get("search_type") != "":
        request.session['card_search_type'] = request.GET.get('search_type')
        request.session.save()
        search_type = request.session['card_search_type']
    else:
        search_type = None
        request.session['card_search_type'] = None
        request.session.save()
    
    user_cards = filter_cards(request.user.username, search_term, search_type)
    page = request.GET.get('page', 1)
    paginator = Paginator(user_cards, 4)

    try:
        user_cards = paginator.page(page)
    except PageNotAnInteger:
        user_cards = paginator.page(1)
    except EmptyPage:
        user_cards = paginator.page(paginator.num_pages)
    
    card_list_html = render_to_string("partials/cards/card_list.html", {'user_cards':user_cards}, request=request)
    pagination_html = render_to_string("partials/cards/card_pagination.html", {'user_cards': user_cards})
    return JsonResponse({'card_list_html': card_list_html, 'pagination_html': pagination_html})

#Adds a new card to the database
def add_card(request, page):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    addForm = addCardForm(request.POST)
    if addForm.is_valid():
        card = CardModel(
            user = request.user,
            card_number = addForm.cleaned_data["card_number"],
            cardholder_name = addForm.cleaned_data["cardholder_name"],
            expiration_date = addForm.cleaned_data["expiration_date"],
            cvv = addForm.cleaned_data["cvv"],
            card_brand = addForm.cleaned_data["card_brand"],
            card_type = addForm.cleaned_data["card_type"]
        )
        card.save()

        user_cards = filter_cards(request.user.username, search_term, search_type)
        paginator = Paginator(user_cards, 4)

        try:
            user_cards = paginator.page(page)
        except PageNotAnInteger:
            user_cards = paginator.page(1)
        except EmptyPage:
            user_cards = paginator.page(paginator.num_pages)
        
        card_list_html = render_to_string("partials/cards/card_list.html", {'user_cards':user_cards}, request=request)
        add_card_form_html = render_to_string("partials/cards/add_card_form.html", {'addForm':addCardForm()}, request=request)
        return JsonResponse({'status': 'success', 'card_list_html': card_list_html, 'page':page, 'add_card_form_html':add_card_form_html})
    else:
        add_card_form_html = render_to_string("partials/cards/add_card_form.html", {'addForm':addForm}, request=request)
        return JsonResponse({'status': 'error', 'add_card_form_html':add_card_form_html})

#Edits the card information
def edit_card(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    page = request.POST.get("currentPage")
    editForm = editCardForm(request.POST, prefix=request.POST.get("card_id"))
    if not request.POST.get("editForm_cvv"):
        editForm.add_error(None, "CVV is required.")
    if request.POST.get("editForm_cvv") and len(request.POST.get("editForm_cvv")) < 3:
        editForm.add_error(None, "CVV must be 3 to 4 digits long.")
    if request.POST.get("editForm_cvv") and request.POST.get("editForm_cvv").isnumeric() == False:
        editForm.add_error(None, "CVV must be numeric.")
    if editForm.is_valid():
        edited_card = CardModel.objects.get(id=request.POST.get("card_id"))
        edited_card.card_number = editForm.cleaned_data['card_number']
        edited_card.cardholder_name = editForm.cleaned_data['cardholder_name']
        edited_card.expiration_date = editForm.cleaned_data['expiration_date']
        edited_card.cvv = request.POST.get('editForm_cvv')
        edited_card.card_brand = editForm.cleaned_data['card_brand']
        edited_card.card_type = editForm.cleaned_data['card_type']
        edited_card.save()
        
        user_cards = filter_cards(request.user.username, search_term, search_type)
        paginator = Paginator(user_cards, 4)

        try:
            user_cards = paginator.page(page)
        except PageNotAnInteger:
            user_cards = paginator.page(1)
        except EmptyPage:
            user_cards = paginator.page(paginator.num_pages)
        
        card_list_html = render_to_string("partials/cards/card_list.html", {'user_cards':user_cards}, request=request)
        return JsonResponse({'status': 'success', 'card_list_html': card_list_html, 'page':page, 'card_id':request.POST.get("card_id")})
    else:
        card = CardModel.objects.get(id=request.POST.get("card_id"))
        edit_card_form_html = render_to_string("partials/cards/edit_card_form.html", {'editForm':editForm, 'card':card}, request=request)
        return JsonResponse({'status': 'error', 'edit_card_form_html':edit_card_form_html, 'card_id':request.POST.get("card_id")})

#Deletes the card
def delete_card(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    page = request.GET.get("currentPage")
    card_to_delete = CardModel.objects.get(id=request.GET.get("card_to_delete_id"))
    card_to_delete.soft_delete()

    user_cards = filter_cards(request.user.username, search_term, search_type)
    paginator = Paginator(user_cards, 4)

    try:
        user_cards = paginator.page(page)
    except PageNotAnInteger:
        user_cards = paginator.page(1)
    except EmptyPage:
        user_cards = paginator.page(paginator.num_pages)
    
    card_list_html = render_to_string("partials/cards/card_list.html", {'user_cards':user_cards}, request=request)
    pagination_html = render_to_string("partials/cards/card_pagination.html", {'user_cards': user_cards})
    return JsonResponse({'card_list_html': card_list_html, 'pagination_html': pagination_html})

#Updates the pagination for card
def card_pagination(request):
    page = request.GET.get('page', 1)
    user_cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_cards = [(card, editCardForm(prefix=str(card.id))) for card in user_cards]
    paginator = Paginator(user_cards, 4)

    try:
        user_cards = paginator.page(page)
    except PageNotAnInteger:
        user_cards = paginator.page(1)
    except EmptyPage:
        user_cards = paginator.page(paginator.num_pages)
        
    pagination_html = render_to_string("partials/cards/card_pagination.html", {'user_cards': user_cards})
    return JsonResponse({'pagination_html': pagination_html})

#Updates the card list based on page number
def card_update(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    page = request.GET.get('page', 1)
    user_cards = filter_cards(request.user.username, search_term, search_type)
    paginator = Paginator(user_cards, 4)

    try:
        user_cards = paginator.page(page)
    except PageNotAnInteger:
        user_cards = paginator.page(1)
    except EmptyPage:
        user_cards = paginator.page(paginator.num_pages)

    card_list_html = render_to_string("partials/cards/card_list.html", {'user_cards':user_cards}, request=request)
    return JsonResponse({'card_list_html': card_list_html, 'page':page})

#Notes view
@login_required
def notes(request):
    addForm = addNoteForm()

    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    #Processes the search form
    if request.GET.get("form_type") == "searchForm":
        return search_note(request)

    #Pagination for cards
    page = request.GET.get('page', 1)
    user_notes = filter_notes(request.user.username, search_term, search_type)
    paginator = Paginator(user_notes, 6)
    try:
        user_notes = paginator.page(page)
    except PageNotAnInteger:
        user_notes = paginator.page(1)
    except EmptyPage:
        user_notes = paginator.page(paginator.num_pages)
        
    #Processes the request to update the page
    if request.GET.get("form_type") == "page_updateForm":
        return note_update(request)
    
    #Processes the request to update the pagination
    elif request.GET.get("form_type") == "paginationForm":
        return note_pagination(request)
    
    #Processes the request to add a note
    elif request.POST.get("form_type") == "addNoteForm":
        return add_note(request, page)

    #Processes the request to edit a note
    elif request.POST.get("form_type") == "editNoteForm":
        return edit_note(request)

    #Processes the note deletion form
    elif request.GET.get("form_type") == "deleteNoteForm":
        return delete_note(request)
    
    return render(request, "notes.html", {'username':request.user.username, 'addForm':addForm, 'user_notes':user_notes, 'search_term':search_term,'search_type':search_type})

#Returns the filtered notes
def filter_notes(user, search_term=None, search_type=None):
    user_notes = NoteModel.objects.filter(user__username=user, is_deleted=False)
    user_notes = [(note, editNoteForm(prefix=str(note.id))) for note in user_notes]

    #Checks if user searched anything
    if search_term != None and search_type is None:
        user_notes = NoteModel.objects.filter(user__username=user, title__icontains=search_term, is_deleted=False)
        user_notes = [(note, editNoteForm(prefix=str(note.id))) for note in user_notes]
    elif search_term != None and search_type == "title":
        user_notes = NoteModel.objects.filter(user__username=user, title__icontains=search_term, is_deleted=False)
        user_notes = [(note, editNoteForm(prefix=str(note.id))) for note in user_notes]
    elif search_term != None and search_type == "content":
        user_notes = NoteModel.objects.filter(user__username=user, content__icontains=search_term, is_deleted=False)
        user_notes = [(note, editNoteForm(prefix=str(note.id))) for note in user_notes]
    return user_notes

#Updates the page based on search
def search_note(request):
    if request.GET.get("search_term") != "":
        request.session['note_search_term'] = request.GET.get('search_term')
        request.session.save()
        search_term = request.session['note_search_term']
    else:
        search_term = None
        request.session['note_search_term'] = None
        request.session.save()
    if request.GET.get("search_type") != "":
        request.session['note_search_type'] = request.GET.get('search_type')
        request.session.save()
        search_type = request.session['note_search_type']
    else:
        search_type = None
        request.session['note_search_type'] = None
        request.session.save()
    
    user_notes = filter_notes(request.user.username, search_term, search_type)
    page = request.GET.get('page', 1)
    paginator = Paginator(user_notes, 6)

    try:
        user_notes = paginator.page(page)
    except PageNotAnInteger:
        user_notes = paginator.page(1)
    except EmptyPage:
        user_notes = paginator.page(paginator.num_pages)
    
    note_list_html = render_to_string("partials/notes/note_list.html", {'user_notes':user_notes}, request=request)
    pagination_html = render_to_string("partials/notes/note_pagination.html", {'user_notes': user_notes})
    return JsonResponse({'note_list_html': note_list_html, 'pagination_html': pagination_html})

#Adds a new note to the database
def add_note(request, page):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']

    addForm = addNoteForm(request.POST)
    if addForm.is_valid():
        note = NoteModel(
            user = request.user,
            title = addForm.cleaned_data["title"],
            content = addForm.cleaned_data["content"]
        )
        note.save()

        user_notes = filter_notes(request.user.username, search_term, search_type)
        paginator = Paginator(user_notes, 6)
        try:
            user_notes = paginator.page(page)
        except PageNotAnInteger:
            user_notes = paginator.page(1)
        except EmptyPage:
            user_notes = paginator.page(paginator.num_pages)
        
        note_list_html = render_to_string("partials/notes/note_list.html", {'user_notes':user_notes}, request=request)
        add_note_form_html = render_to_string("partials/notes/add_note_form.html", {'addForm':addNoteForm()}, request=request)
        return JsonResponse({'status': 'success', 'note_list_html': note_list_html, 'page':page, 'add_note_form_html':add_note_form_html})
    else:
        add_note_form_html = render_to_string("partials/notes/add_note_form.html", {'addForm':addForm}, request=request)
        return JsonResponse({'status': 'error', 'add_note_form_html':add_note_form_html})

#Edits the note information
def edit_note(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']
    
    page = request.POST.get("currentPage")
    editForm = editNoteForm(request.POST, prefix=request.POST.get("note_id"))
    if not request.POST.get("editForm_content"):
        editForm.add_error(None, "Description is required.")
    if editForm.is_valid():
        edited_note = NoteModel.objects.get(id=request.POST.get("note_id"))
        edited_note.title = editForm.cleaned_data['title']
        edited_note.content = request.POST.get('editForm_content')
        edited_note.save()
        
        user_notes = filter_notes(request.user.username, search_term, search_type)
        paginator = Paginator(user_notes, 6)
        try:
            user_notes = paginator.page(page)
        except PageNotAnInteger:
            user_notes = paginator.page(1)
        except EmptyPage:
            user_notes = paginator.page(paginator.num_pages)
        
        note_list_html = render_to_string("partials/notes/note_list.html", {'user_notes':user_notes}, request=request)
        return JsonResponse({'status': 'success', 'note_list_html': note_list_html, 'page':page})
    else:
        note = NoteModel.objects.get(id=request.POST.get("note_id"))
        edit_note_form_html = render_to_string("partials/notes/edit_note_form.html", {'editForm':editForm, 'note':note}, request=request)
        return JsonResponse({'status': 'error', 'edit_note_form_html':edit_note_form_html, 'note_id':request.POST.get("note_id")})

#Deletes the note
def delete_note(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']
    
    page = request.GET.get("currentPage")
    note_to_delete = NoteModel.objects.get(id=request.GET.get("note_to_delete_id"))
    note_to_delete.soft_delete()
        
    user_notes = filter_notes(request.user.username, search_term, search_type)
    paginator = Paginator(user_notes, 6)
    try:
        user_notes = paginator.page(page)
    except PageNotAnInteger:
        user_notes = paginator.page(1)
    except EmptyPage:
        user_notes = paginator.page(paginator.num_pages)
    
    note_list_html = render_to_string("partials/notes/note_list.html", {'user_notes':user_notes}, request=request)
    pagination_html = render_to_string("partials/notes/note_pagination.html", {'user_notes': user_notes})
    return JsonResponse({'note_list_html': note_list_html, 'pagination_html': pagination_html})

#Updates the pagination for note
def note_pagination(request):
    page = request.GET.get('page', 1)
    user_notes = NoteModel.objects.filter(user__username=request.user.username, is_deleted=False)
    user_notes = [(note, editNoteForm(prefix=str(note.id))) for note in user_notes]
    paginator = Paginator(user_notes, 6)

    try:
        user_notes = paginator.page(page)
    except PageNotAnInteger:
        user_notes = paginator.page(1)
    except EmptyPage:
        user_notes = paginator.page(paginator.num_pages)
    
    pagination_html = render_to_string("partials/notes/note_pagination.html", {'user_notes': user_notes})
    return JsonResponse({'pagination_html': pagination_html})

#Update the note list based on page number
def note_update(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'card_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['card_search_term']

    #Checks if user selected a search type
    if 'card_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['card_search_type']
    
    page = request.GET.get('page', 1)
    user_notes = filter_notes(request.user.username, search_term, search_type)
    paginator = Paginator(user_notes, 6)

    try:
        user_notes = paginator.page(page)
    except PageNotAnInteger:
        user_notes = paginator.page(1)
    except EmptyPage:
        user_notes = paginator.page(paginator.num_pages)
    note_list_html = render_to_string("partials/notes/note_list.html", {'user_notes':user_notes}, request=request)
    return JsonResponse({'note_list_html': note_list_html, 'page':page})

#History view
@login_required
def history(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['search_term']

    #Checks if user selected a search type
    if 'search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['search_type']

    #Processes the search form
    if request.GET.get("form_type") == "searchForm":
        return search_history(request)
    
    #Pagination for cards
    page = request.GET.get('page', 1)
    deletedItems = filter_history(request.user.username, search_term, search_type)
    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)
        
    #Processes the request to update the page
    if request.GET.get("form_type") == "page_updateForm":
        return history_update(request)
    
    #Processes the request to update the pagination
    elif request.GET.get("form_type") == "paginationForm":
        return history_pagination(request)
    
    #Recovers the deleted item
    elif request.GET.get("form_type") == "recoveryForm":
        return recover_history(request)

    #Permanently deletes the item
    elif request.GET.get("form_type") == "deletionForm":
        return delete_history(request)

    return render(request, "history.html", {'username':request.user.username, 'deletedItems':deletedItems, 'search_term':search_term,'search_type':search_type})

#Returns the filtered deleted items
def filter_history(user, search_term=None, search_type=None):
    deletedItems = []
    deletedItems.extend(PasswordModel.objects.filter(user__username=user, is_deleted=True))
    deletedItems.extend(NoteModel.objects.filter(user__username=user, is_deleted=True))
    deletedItems.extend(CardModel.objects.filter(user__username=user, is_deleted=True))

    #Checks search bar and search type
    if search_term != None and search_type is None or search_term != None and search_type == "all":
        deletedItems = []
        deletedItems.extend(PasswordModel.objects.filter(user__username=user, website_name__icontains=search_term, is_deleted=True))
        deletedItems.extend(NoteModel.objects.filter(user__username=user, title__icontains=search_term, is_deleted=True))
        deletedItems.extend(CardModel.objects.filter(user__username=user, card_brand__icontains=search_term, is_deleted=True))
    elif search_term != None and search_type == "passwords":
        deletedItems = []
        deletedItems.extend(PasswordModel.objects.filter(user__username=user, website_name__icontains=search_term, is_deleted=True))
    elif search_term != None and search_type == "notes":
        deletedItems = []
        deletedItems.extend(NoteModel.objects.filter(user__username=user, title__icontains=search_term, is_deleted=True))
    elif search_term != None and search_type == "cards":
        deletedItems = []
        deletedItems.extend(CardModel.objects.filter(user__username=user, card_brand__icontains=search_term, is_deleted=True))
    elif search_term is None and search_type is None or search_term is None and search_type == "all":
        deletedItems = []
        deletedItems.extend(PasswordModel.objects.filter(user__username=user, is_deleted=True))
        deletedItems.extend(NoteModel.objects.filter(user__username=user, is_deleted=True))
        deletedItems.extend(CardModel.objects.filter(user__username=user, is_deleted=True))
    elif search_term is None and search_type == "passwords":
        deletedItems = []
        deletedItems.extend(PasswordModel.objects.filter(user__username=user, is_deleted=True))
    elif search_term is None and search_type == "notes":
        deletedItems = []
        deletedItems.extend(NoteModel.objects.filter(user__username=user, is_deleted=True))
    elif search_term is None and search_type == "cards":
        deletedItems = []
        deletedItems.extend(CardModel.objects.filter(user__username=user, is_deleted=True))
    return deletedItems

#Updates the page based on search
def search_history(request):
    if request.GET.get("search_term") != "":
        request.session['history_search_term'] = request.GET.get('search_term')
        request.session.save()
        search_term = request.session['history_search_term']
    else:
        search_term = None
        request.session['history_search_term'] = None
        request.session.save()
    if request.GET.get("search_type") != "":
        request.session['history_search_type'] = request.GET.get('search_type')
        request.session.save()
        search_type = request.session['history_search_type']
    else:
        search_type = None
        request.session['history_search_type'] = None
        request.session.save()

    deletedItems = filter_history(request.user.username, search_term, search_type)
    page = request.GET.get("page", 1)
    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)
    
    history_list_html = render_to_string("partials/history/history_list.html", {'deletedItems':deletedItems}, request=request)
    pagination_html = render_to_string("partials/history/history_pagination.html", {'deletedItems':deletedItems})
    return JsonResponse({'history_list_html': history_list_html, 'pagination_html': pagination_html})

#Permanently deletes the item
def delete_history(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'history_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['history_search_term']

    #Checks if user selected a search type
    if 'history_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['history_search_type']

    if request.GET.get("item_type") == "password":
        password_to_delete = PasswordModel.objects.get(id=request.GET.get("password_id"))
        password_to_delete.delete()
    elif request.GET.get("item_type") == "note":
        note_to_delete = NoteModel.objects.get(id=request.GET.get("note_id"))
        note_to_delete.delete()
    elif request.GET.get("item_type") == "card":
        card_to_delete = CardModel.objects.get(id=request.GET.get("card_id"))
        card_to_delete.delete()
    
    page = request.GET.get("currentPage")
    deletedItems = filter_history(request.user.username, search_term, search_type)
    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)
    
    history_list_html = render_to_string("partials/history/history_list.html", {'deletedItems':deletedItems})
    pagination_html = render_to_string("partials/history/history_pagination.html", {'deletedItems':deletedItems})
    return JsonResponse({'history_list_html': history_list_html, 'pagination_html': pagination_html})

#Recovers the deleted item
def recover_history(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'history_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['history_search_term']

    #Checks if user selected a search type
    if 'history_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['history_search_type']

    if request.GET.get("item_type") == "password":
        password_to_recover = PasswordModel.objects.get(id=request.GET.get("password_id"))
        password_to_recover.recover()
    elif request.GET.get("item_type") == "note":
        note_to_recover = NoteModel.objects.get(id=request.GET.get("note_id"))
        note_to_recover.recover()
    elif request.GET.get("item_type") == "card":
        card_to_recover = CardModel.objects.get(id=request.GET.get("card_id"))
        card_to_recover.recover()

    page = request.GET.get("currentPage")
    deletedItems = filter_history(request.user.username, search_term, search_type)

    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)
    
    history_list_html = render_to_string("partials/history/history_list.html", {'deletedItems':deletedItems})
    pagination_html = render_to_string("partials/history/history_pagination.html", {'deletedItems':deletedItems})
    return JsonResponse({'history_list_html': history_list_html, 'pagination_html': pagination_html})

#Updates the pagination for history
def history_pagination(request):
    page = request.GET.get("page", 1)
    deletedItems = []
    deletedItems.extend(PasswordModel.objects.filter(user__username=request.user.username, is_deleted=True))
    deletedItems.extend(NoteModel.objects.filter(user__username=request.user.username, is_deleted=True))
    deletedItems.extend(CardModel.objects.filter(user__username=request.user.username, is_deleted=True))

    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)

    pagination_html = render_to_string("partials/history/history_pagination.html", {'deletedItems':deletedItems})
    return JsonResponse({'pagination_html': pagination_html})

#Update the history list based on page number
def history_update(request):
    #Checks if user searched anything, if not search_term is set to None
    if 'history_search_term' not in request.session:
        search_term = None
    else:
        search_term = request.session['history_search_term']

    #Checks if user selected a search type
    if 'history_search_type' not in request.session:
        search_type = None
    else:
        search_type = request.session['history_search_type']

    page = request.GET.get("page", 1)
    deletedItems = filter_history(request.user.username, search_term, search_type)
    paginator = Paginator(deletedItems, 6)
    try:
        deletedItems = paginator.page(page)
    except PageNotAnInteger:
        deletedItems = paginator.page(1)
    except EmptyPage:
        deletedItems = paginator.page(paginator.num_pages)
    history_list_html = render_to_string("partials/history/history_list.html", {'deletedItems':deletedItems}, request=request)
    return JsonResponse({'history_list_html': history_list_html, 'page':page})
    
#Password generator view
@login_required
def password_generator(request):
    if request.method == "POST":
        #Generate the password based on user selection
        characters = string.ascii_letters if request.POST["characters"] == "true" else ''
        characters += string.digits if request.POST["numbers"] == "true" else ''
        characters += string.punctuation if request.POST["special_characters"] == "true" else ''
        #If user didn't select any checkboxes, send an error
        if characters:
            password = ''.join(secrets.choice(characters) for num in range(int(request.POST["length"])))
            return JsonResponse({'password':password})
        else:
            return JsonResponse({'error':"Must select at least one option to generate password."})
    return render(request, "password_generator.html", {'username':request.user.username})

#Settings view
@login_required
def settings(request):
    two_factor_auth_enabled = Profile.objects.get(user__username=request.user.username).two_factor_auth

    #Sets the two factor authentication on or off 
    if request.GET.get("form_type") == "authForm":
        if request.GET.get("two_factor_auth") == "true":
            Profile.objects.filter(user__username=request.user.username).update(two_factor_auth=True)
        else:
            Profile.objects.filter(user__username=request.user.username).update(two_factor_auth=False)

    #Deletes all Password
    elif request.GET.get("form_type") == "deleteAllPasswordsForm":
        user_passwords = PasswordModel.objects.filter(user__username=request.user.username, is_deleted=False)
        user_passwords.delete()
        return JsonResponse({'success':"All passwords deleted."})
    
    #Deletes all Note
    elif request.GET.get("form_type") == "deleteAllNotesForm":
        user_notes = NoteModel.objects.filter(user__username=request.user.username, is_deleted=False)
        user_notes.delete()
        return JsonResponse({'success':"All notes deleted."})

    #Deletes all card
    elif request.GET.get("form_type") == "deleteAllCardsForm":
        user_cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=False)
        user_cards.delete()
        return JsonResponse({'success':"All cards deleted."})

    #Delete all deleted items
    elif request.GET.get("form_type") == "deleteAllTrashForm":
        user_passwords = PasswordModel.objects.filter(user__username=request.user.username, is_deleted=True)
        user_passwords.delete()
        user_notes = NoteModel.objects.filter(user__username=request.user.username, is_deleted=True)
        user_notes.delete()
        user_cards = CardModel.objects.filter(user__username=request.user.username, is_deleted=True)
        user_cards.delete()
        return JsonResponse({'success':"All trash deleted."})
    
    #User updates their profile information
    elif request.method == "POST":
        errors = []
        username = request.POST.get("username")
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        email = request.POST.get("email")

        #If user submits form with nothing, continue
        if not username and not old_password and not new_password1 and not new_password2 and not email:
            return JsonResponse({'status':'success'})

        #Check if user inputted the current password
        if not old_password:
            errors.append("Current password cannot be empty.")

        # Check if the old password is correct
        if not request.user.check_password(old_password):
            errors.append("Incorrect current password.")

        #If user does not want to change password
        if new_password1 and new_password2:
            # Check if the new passwords match
            if new_password1 != new_password2:
                errors.append("New passwords do not match.")
        else:
            if new_password1 or new_password2:
                errors.append("New passwords cannot be empty.")

        # Validate the email address
        if email:
            try:
                validate_email(email)
            except ValidationError as e:
                errors.append("Enter a valid email.")

        if errors:
            error_notification_html = render_to_string("partials/settings/error_notification.html", {'error_list':errors})
            return JsonResponse({'status':'error', 'error':error_notification_html})
        else:
            if username:
                #Changes the user's username
                request.user.username = username
                request.user.save()

            if new_password1:
                #Changes the user's password
                request.user.set_password(new_password1)
                request.user.save()

            if email:
                #Changes the user's email
                request.user.email = email
                request.user.save()

            update_session_auth_hash(request, request.user)
            return JsonResponse({'status':"success"})
        
    return render(request, "settings.html", {'username':request.user.username, 'email':request.user.email, '2FA':two_factor_auth_enabled})

#Log out view
@login_required
def log_out(request):
    logout(request)
    return redirect("login")