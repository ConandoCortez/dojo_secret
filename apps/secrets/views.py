from django.shortcuts import render, redirect
from .models import User, Secret
from django.contrib import messages
from django.db.models import Count
import bcrypt
# Create your views here.
def index(request):
    # User.objects.all().delete()
    # Secret.objects.all().delete()
    return render(request, 'secrets/index.html')

# Process for Login and registration
# look at models.py for verification of the different attributes
def process(request):
    # If the button that was pushed is register, it will validate the information
    if request.POST['button'] == 'register':
        register = request.POST
        user = User.objects.register(register)
        # Method returns a tuple and if it is false, it will also return an array containing errors
        if user[0] == False:
            for error in user[1]:
                messages.warning(request, error)
            return redirect('/')
        # If there are no errors, it will return True and the user object
        request.session['id'] = user[1].id
        return redirect('/success')
    # If the form button pushed was login, it will go through validation for the user
    if request.POST['button'] == 'login':
        user = User.objects.login(request.POST)
        # If the user does not exist or the password does not match the database, errors are returned
        if user[0] == False:
            for error in user[1]:
                messages.warning(request, error)
            return redirect('/')
        # If login was successful, the user object is returned
        else:
            request.session['id'] = user[1].id
            return redirect('/success')

def success(request):
    if request.session.get('id') == None:
        return render(request, 'secrets/index.html')
    try:
        context = {
            'user': User.objects.get(id = request.session['id']),
            'secrets': Secret.objects.annotate(numlike=Count('like')).order_by("-id")[:5],
            'messages': Secret.objects.all().order_by('-id'),
        }
    except User.DoesNotExist:
        messages.warning(request, 'User does not exist')
    return render(request, 'secrets/secrets.html', context)

# Post a secret message on the wall
def post(request, post_id):
    user = User.objects.get(id = request.session['id'])
    if request.POST['button'] == 'message':
        Secret.objects.create(message = request.POST['message'], user = user)
    elif request.POST['button'] == 'like':
        Secret.objects.like_post(request.session['id'], post_id)
    else:
        Secret.objects.like_post(request.session['id'], post_id)
        return redirect('/most_popular')
    return redirect('/success')

def delete(request,id):
    Secret.objects.get(id = id).delete()
    context = {
        'user': User.objects.get(id = request.session['id']),
        'messages': Secret.objects.all(),
    }
    if request.POST['button']=='delete2':
        return redirect('/most_popular')
    return redirect('/success')

def logout(request):
    request.session.pop('id')
    return redirect('/')

def most_popular(request):
    context = {
        'secrets': Secret.objects.annotate(numlike = Count('like')).order_by('-numlike'),
        'user': User.objects.get(id = request.session['id']),
    }
    return render(request, 'secrets/most_popular.html', context)
