from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Avg,Max,Min,Count,Sum, F

import json, os, time, mimetypes

from loguru import logger

from api.models.borrower import Borrower, BorrowerIndex, BorrowerAmount
from api.models.user import User
from api.models.file import File
from api.models.lender import Lender
from api.models.application import Application

from api.models.data.seller_month import DataSellerMonth

from api.view.util import Status, UserRole, FILE_PATH, WEB_SERVER, BorrowerAmountStatus


def get_borrower_from_id(request):  
    borrowerId = request.GET.get('borrower_id')
    if borrowerId == None or borrowerId == 'undefined':
        borrowerId = request.session["borrower_id"]

    borrower = Borrower.objects.filter(id = borrowerId).first()
    data = {}

    data = borrower.toJson()

    for attrName in ['br_hk', 'br_cn', 'policy_cn', 'director_hk', 'director_cn']:
        listDoc = []
        if data[attrName] == None or data[attrName] == "":
            data[attrName] = listDoc
            continue

        for key, value in data[attrName].items():
            listDoc.append({
                'uid': attrName + "__" + key,
                'name': value,
                'status': 'done',
                'url': WEB_SERVER + "api/borrower/download_file?file_id=" + attrName + "__" + key,                
            })
        data[attrName] = listDoc

    borrowerAmount = BorrowerAmount.objects.filter(borrower = borrower).first()
    #data.update(borrowerAmount.toDict())

    #计算剩余贷款额度
    querySetApplication = Application.objects.filter(borrower = borrower)
    loaned_amount = 0
    for application in querySetApplication:
        if application.status not in {'UNAPPROVED', 'UNACCEPTED', 'REPAID', 'LOAN_SETTLEMENT', 'CLOSED', 'CANCELLED'}:
            if application.status == 'CREATED':    #这时amount_approved会是0，所以需要用amount
                loaned_amount = loaned_amount + application.amount
            else: 
                loaned_amount = loaned_amount + application.amount_approved

    available_amount = borrowerAmount.amount_limit - loaned_amount
    data["available_amount"] = str(round(available_amount, 2)) 
    data["loaned_amount"] = str(round(loaned_amount, 2)) 
       
    data["amount_limit"] = str(round(borrowerAmount.amount_limit, 2)) 

    data["amount_monthly_ratio"] = str(round(borrowerAmount.amount_monthly_ratio, 2))
    data["monthly_revenue"] = getMonthAvgRevenue(borrower)
    data["currency"] = borrowerAmount.currency

    data["duration"] = borrowerAmount.duration
    data["annual_interest_rate"] = str(round(borrowerAmount.annual_interest_rate, 3))
    data["penalty_annual_interest_rate"] = str(round(borrowerAmount.penalty_annual_interest_rate, 3))

    data["status_lender"] = borrowerAmount.status
    data["remark_lender"] = borrowerAmount.remark

    return JsonResponse({"data": data})

def get_borrower(request):  
    username = request.session["username"]
    user = User.objects.filter(username = username).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    data = {}
    borrower = Borrower.objects.filter(user = user).first()
    if (borrower == None):
        data = {
            'key': 0,

            'br_hk': '',
            'br_cn': '',
            'policy_cn': '',

            'director_hk': '',
            'director_cn': '',

            'name_cn': '',  
            'credit_code_cn': '',
            'address_cn': '',

            'name_hk': '',  
            'br_code_hk': '',
            'address_hk': '',

            'lear_name': '',
            'lear_nationality': '',
            'lear_country_code': '+852',
            'lear_mobile': '',
            'lear_email': '',
            'lear_address': '',

            'shareholder_person_cn': '',
            'shareholder_company_cn': '',

            'director_person_cn': '',
            'director_company_cn': '',

            'shareholder_person_hk': '',
            'shareholder_company_hk': '',

            'director_person_hk': '',
            'director_company_hk': '',

            'contact': '',

            'shop': '',

            'finance_type': '',

            'status': '',
            'remark': '',
        }         
    else:
        data = borrower.toJson()

    for attrName in ['br_hk', 'br_cn', 'policy_cn', 'director_hk', 'director_cn']:
        listDoc = []
        if data[attrName] == None or data[attrName] == "":
            data[attrName] = listDoc
            continue

        for key, value in data[attrName].items():
            listDoc.append({
                'uid': attrName + "__" + key,
                'name': value,
                'status': 'done',
                'url': WEB_SERVER + "api/borrower/download_file?file_id=" + attrName + "__" + key,                
            })
        data[attrName] = listDoc

    return JsonResponse({"data": data})

def base_info(request):
    #logger.info(request)
    obj = json.loads(request.body.decode())

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    if (borrower == None):
        borrower = Borrower(
            user = user,

            name_cn = obj["name_cn"],
            credit_code_cn = obj["credit_code_cn"],
            address_cn = obj["address_cn"],

            name_hk = obj["name_hk"],
            br_code_hk = obj["br_code_hk"],
            address_hk = obj["address_hk"],           
        )
        
        borrower.save()

        #BorrowerIndex
        cbIndex = BorrowerIndex()
        cbIndex.borrower = borrower
        cbIndex.past_three_month_cashflow = 0

        cbIndex.history_apply_times = 0
        cbIndex.history_apply_approval_times = 0
        cbIndex.history_default_times = 0
        cbIndex.history_default_ratio = 0
        cbIndex.history_default_money_ratio = 0

        cbIndex.save()

    else:
        borrower.name_cn = obj["name_cn"]
        borrower.credit_code_cn = obj["credit_code_cn"]
        borrower.address_cn = obj["address_cn"]

        borrower.name_hk = obj["name_hk"]
        borrower.br_code_hk = obj["br_code_hk"]
        borrower.address_hk = obj["address_hk"]

        borrower.save()

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def company_info(request):
    obj = json.loads(request.body.decode())
    #logger.info(obj)
    #{'lear_name': 'd', 'lear_nationality': 'ss', 'lear_country_code': '+852', 'lear_mobile': '93646309', 'lear_email': 'ddd2@dd.com', 'lear_address': 'ddd'}

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    
    for attrName in ['lear_name', 'lear_nationality', 'lear_email', 'lear_address', 
                    'shareholder_person_cn', 'shareholder_company_cn',
                    'director_person_cn', 'director_company_cn',
                    'shareholder_person_hk', 'shareholder_company_hk',
                    'director_person_hk', 'director_company_hk']:
        if attrName in obj:
            setattr(borrower, attrName, obj[attrName])

    if "lear_country_code" in obj and "lear_mobile" in obj:
        borrower.lear_mobile = obj["lear_country_code"] + "-" + obj["lear_mobile"]

    borrower.save()

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def contact_info(request):
    obj = json.loads(request.body.decode())
    #{'contact': [{'name': 'a', 'name_english': 'a', 'position': 'a', 'phone': 'a', 'email': 'a'}, {'name': 'b', 'name_english': 'b', 'position': 'b', 'phone': 'b', 'email': 'b'}]}

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    if 'contact' in obj:
        borrower.contact = obj['contact']

    borrower.save()

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def shop_info(request):
    obj = json.loads(request.body.decode())
    #{'shop': [{'name': 'a', 'name_english': 'a', 'position': 'a', 'phone': 'a', 'email': 'a'}, {'name': 'b', 'name_english': 'b', 'position': 'b', 'phone': 'b', 'email': 'b'}]}

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    if 'shop' in obj:
        borrower.shop = obj['shop']

    borrower.save()

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def full(request):
    obj = json.loads(request.body.decode())
    #logger.info(obj)

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    if borrower.status == None or borrower.status == "":
        borrower.status = Status.CREATED
        borrower.save() 

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def upload_file(request):
    #logger.info(request)

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()
    print("==================================")
    path = FILE_PATH + "/" + str(borrower.id)
    if (os.path.exists(path) == False):
        os.makedirs(path)

    fileID = None
    for attrName, file in request.FILES.items():
        file = request.FILES[attrName]
        content = file.read()

        objFile = File()
        objFile.name = file.name
        objFile.content = content
        objFile.save()
        
        attrValue = getattr(borrower, attrName)
        if attrValue == None:
            attrValue = {}
        attrValue[str(objFile.id)] = file.name
        setattr(borrower, attrName, attrValue)

        fileID = attrName + "__" + str(objFile.id)

        f = open(path + "/" + str(objFile.id) + "-" + file.name, "wb")
        f.write(content)
        f.close()

    borrower.save()

    data = {
        "uid": fileID,
        "url": WEB_SERVER + "api/borrower/download_file?file_id=" + fileID,
    }
    return JsonResponse({"data": data})

def delete_file(request):
    #logger.info(request)

    strFileID = request.GET.get('file_id')
    if strFileID == None or strFileID == 'undefined':
        return JsonResponse({"data":{"message":"Error"}})
    
    attrName = strFileID.split("__")[0]
    fileID = strFileID.split("__")[1]

    user = User.objects.filter(username = request.session["username"]).first()
    if (user == None):
        return JsonResponse({"data":{"message":"Error"}})

    borrower = Borrower.objects.filter(user = user).first()

    File.objects.filter(id=fileID).delete()

    attrValue = getattr(borrower, attrName)
    if fileID in attrValue:
        del attrValue[fileID]
    setattr(borrower, attrName, attrValue)

    borrower.save()

    data = {"data":{"message":"Ok"}}
    return JsonResponse(data)

def download_file(request):
    #logger.info(request)

    strFileID = request.GET.get('file_id')
    if strFileID == None or strFileID == 'undefined':
        return JsonResponse({"data":{"message":"Error"}})

    attrName = strFileID.split("__")[0]
    fileID = strFileID.split("__")[1]

    #user = User.objects.filter(username = request.session["username"]).first()
    #if (user == None):
    #    return JsonResponse({"data":{"message":"Error"}})

    objFile = File.objects.filter(id=fileID).first()
    if (objFile == None):
        return JsonResponse({"data":{"message":"Error"}})

    content_type = mimetypes.guess_type(objFile.name)

    response = HttpResponse(content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % objFile.name # force browser to download file
    response.write(objFile.content)
    return response
    #return HttpResponse(objFile.content, content_type=content_type)

def getMonthAvgRevenue(borrower):
    sellerId = None
    if borrower.shop != None and len(borrower.shop) > 0:
        sellerId = borrower.shop[0]["id"]

    if sellerId == None:
        return 0

    month = DataSellerMonth.objects.filter(seller_id = sellerId).aggregate(Avg("revenue"))
    avgRevenue = month['revenue__avg']

    return round(avgRevenue, 2)

def getAllItem(request):
    user = User.objects.filter(username = request.session["username"]).first()
    if user.role == UserRole.LENDER:
        lender = Lender.objects.filter(user = user).first()
        listBorrower = Borrower.objects.filter(lender_id_assign = lender.id)
    else:
        listBorrower = Borrower.objects.all()

    listItem = []
    for borrower in listBorrower:
        borrowerAmount = BorrowerAmount.objects.filter(borrower = borrower).first()
        if borrowerAmount == None:
            lender = Lender.objects.filter(id = borrower.lender_id_assign).first()
            borrowerAmount = BorrowerAmount(
                borrower = borrower,
                lender = lender,

                amount_monthly_ratio = 1,
                amount_limit = 0,
                currency = 'USD',

                duration = 30,
                annual_interest_rate = 0.12,
                penalty_annual_interest_rate = 0.18,

                status = BorrowerAmountStatus.NORMAL,
                remark = "",
            )
            borrowerAmount.save()

        dictBorrower = borrower.toJson()
        dictBorrower["borrower_amount"] = borrowerAmount.toDict()

        dictBorrower["borrower_amount"]["amount_monthly_ratio"] = str(round(dictBorrower["borrower_amount"]["amount_monthly_ratio"], 2))
        dictBorrower["borrower_amount"]["annual_interest_rate"] = str(round(dictBorrower["borrower_amount"]["annual_interest_rate"], 3))
        dictBorrower["borrower_amount"]["penalty_annual_interest_rate"] = str(round(dictBorrower["borrower_amount"]["penalty_annual_interest_rate"], 3))

        dictBorrower["borrower_amount"]["monthly_revenue"] = int(getMonthAvgRevenue(borrower))

        listItem.append(dictBorrower)

    return listItem

def get_list(request):
    current = request.GET.get('current')
    pageSize = request.GET.get('pageSize')

    listItem = getAllItem(request)

    result = {}
    result['data'] = listItem
    
    result["total"] = len(listItem)
    result["success"] = True
    result["pageSize"] = pageSize
    result["current"] = current

    return JsonResponse(result)  

def update(request):
    obj = json.loads(request.body.decode())
    
    if ("remark" not in obj):
        obj["remark"] = ''

    # borrower = Borrower.objects.get(id = obj["key"])

    if "finance_type" in obj:
        borrower.finance_type = obj["finance_type"]

    if "amount_monthly_ratio" in obj:
        borrowerAmount = BorrowerAmount.objects.filter(borrower = borrower).first()

        borrowerAmount.amount_monthly_ratio = float(obj["amount_monthly_ratio"])
        borrowerAmount.amount_limit = borrowerAmount.amount_monthly_ratio * getMonthAvgRevenue(borrower)
        borrowerAmount.currency = obj["currency"]

        borrowerAmount.duration = int(obj["duration"])
        borrowerAmount.annual_interest_rate = float(obj["annual_interest_rate"])
        borrowerAmount.penalty_annual_interest_rate = float(obj["penalty_annual_interest_rate"])

        borrowerAmount.status = obj["status_lender"]
        borrowerAmount.remark = obj["remark_lender"]

        borrowerAmount.save()

    if "status" in obj: 
        borrower.status = obj["status"]

    borrower.save()

    return JsonResponse(obj)

def delete(request):    
    content = json.loads(request.body.decode())
    listID = content['key']

    for id in listID:
        Borrower.objects.get(id = id).delete()

    listItem = getAllItem()
    
    result = {}
    result['list'] = listItem
    result['pagination'] = len(listItem)

    return JsonResponse(result) 