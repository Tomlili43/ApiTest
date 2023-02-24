from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
import requests 
import json, random, time
from django.db.models import Q
from django.core import serializers
from api.models.seller import DataSeller
import json

# Import Pagination Stuff
from django.core.paginator import Paginator

#test post
def base_info(request):
    obj = json.loads(request.body.decode())
    print("objkeys",obj.keys())
    print(type(request))

    return JsonResponse({"data":{"message":"success"}})


def get_seller_list(request):
    # Set up Pagination
    # page 是当前页面
    # pageSize 当前页面大小
    # page = request.GET.get('current')
    # pageSize = request.GET.get('pageSize')
    page = 1
    pageSize = 20
    
    # 引入分页器
    p = Paginator(DataSeller.objects.all(), pageSize)
    # 总条数
    total = p.count
    pageCurrent = p.page(page)
    #尝试 全部数据 一次性处理 取代for 循环  
    # data1 = serializers.serialize(pageCurrent.object_list)
    # data1 = data1.getvalue()
    data = []
    for seller in pageCurrent.object_list:
        dist={}
        dist['name'] = seller.name
        data.append(dist)
    return JsonResponse({
        "data":data,
        "total":total,
        "pageSize":pageSize,
        "success":True
    })

def set_seller_list(request):
    #对应文件名字
    file_object = request.FILES.get("file")
    print(type(file_object))
    print(request.FILES.items())
    for filename, file in request.FILES.items():
        print("filename, file")
        print(filename, file)
        print('----------')
   
      
    # obj = json.loads(request.body.decode())
    # print("objkeys",obj.keys())
    return JsonResponse({"data":{"message":"Win"}})
    



   
