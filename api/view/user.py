from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import requests 
import json, random, time
from django.db.models import Q

def myinfo(request):

    return HttpResponse("I am api_view_user_myinfo ! ")
