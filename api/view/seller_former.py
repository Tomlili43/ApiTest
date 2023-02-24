from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import requests 
import json, random, time
from django.db.models import Q
from api.models.seller import DataSeller

#test post
def base_info(request):
    obj = json.loads(request.body.decode())
    print("objkeys",obj.keys())
    # print("valueType",type(obj['bylaws']))
    print(type(obj))

    return JsonResponse({"data":{"message":"Error"}})


def get_seller_list(request):
    # sellers = DataSeller.objects.filter().first()
    sellers = DataSeller.objects.all()
    data = []
    for seller in sellers:
        print(seller.company_name, seller.company_name_chinese)
        dist={}
        dist['key'] = seller.id
        dist['company_name'] = seller.company_name
        dist['company_name_abbreviation'] = seller.company_name_abbreviation
        dist['company_name_chinese'] = seller.company_name_chinese
        dist['description'] = seller.description
        dist['address'] = seller.address
        dist['in_degree'] = seller.in_degree
        dist['out_degree'] = seller.out_degree
        data.append(dist)

    print(data)
    print("datafromget_seller_listequest")
    

    return JsonResponse({"DataSeller":data})



