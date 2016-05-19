import oauth2 as oauth
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext

from urllib import parse

from apps.models import Document
from apps.models import Profile
from apps.forms import DocumentForm


logger = logging.getLogger(__name__)

consumer = oauth.Consumer(settings.TWITTER_TOKEN, settings.TWITTER_SECRET)
client = oauth.Client(consumer)

request_token_url = 'https://api.twitter.com/oauth/request_token'
access_token_url = 'https://api.twitter.com/oauth/access_token'
authenticate_url = 'https://api.twitter.com/oauth/authenticate'

def twitter_login(request):
    # Step 1. Get a request token from Twitter.
    resp, content = client.request(request_token_url, "GET")
    if resp['status'] != '200':
        raise Exception("Invalid response from Twitter.")

    # Step 2. Store the request token in a session for later use.
    request.session['request_token'] = dict(parse.parse_qsl(content.decode("utf-8"), False, True))

    # Step 3. Redirect the user to the authentication URL.
    url = "%s?oauth_token=%s" % (authenticate_url,
        request.session['request_token']['oauth_token'])

    return HttpResponseRedirect(url)

@login_required
def twitter_logout(request):
    # Log a user out using Django's logout function and redirect them
    # back to the homepage.
    logout(request)
    return HttpResponseRedirect('/')



def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@login_required
def list(request):

    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
            newdoc.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('apps.views.list'))
    else:
        form = DocumentForm()  # A empty, unbound form

    if request.user.is_authenticated():
        logger.info('authenticated user %s', request.user)
        documents = Document.objects.all()

    else:
        logger.info('anonymous user')
        documents = Document.objects.all()


    # Render list page with the documents and the form
    return render(
        request,
        'list.html',
        {'documents': documents, 'form': form}
    )


def twitter_authenticated(request):
    # Step 1. Use the request token in the session to build a new client.
    token = oauth.Token(request.session['request_token']['oauth_token'],
        request.session['request_token']['oauth_token_secret'])
    token.set_verifier(request.GET['oauth_verifier'])
    client = oauth.Client(consumer, token)

    # Step 2. Request the authorized access token from Twitter.
    resp, content = client.request(access_token_url, "GET")
    if resp['status'] != '200':
        print (content)
        raise Exception("Invalid response from Twitter.")

    access_token = dict(parse.parse_qsl(content.decode("utf-8"), False, True))

    # Step 3. Lookup the user or create them if they don't exist.
    try:
        user = User.objects.get(username=access_token['screen_name'])
    except User.DoesNotExist:
        user = User.objects.create_user(access_token['screen_name'],
            '%s@twitter.com' % access_token['screen_name'],
            access_token['oauth_token_secret'])

        # Save our permanent token and secret for later.
        profile = Profile()
        profile.user = user
        profile.oauth_token = access_token['oauth_token']
        profile.oauth_secret = access_token['oauth_token_secret']
        profile.save()

    # Authenticate the user and log them in using Django's pre-built
    # functions for these things.
    user = authenticate(username=access_token['screen_name'],
        password=access_token['oauth_token_secret'])

    login(request, user)

    return HttpResponseRedirect('/')