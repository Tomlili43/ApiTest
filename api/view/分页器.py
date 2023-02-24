def get_seller_list(request):
    # Set up Pagination
    # page 是当前页面
    # pageSize 当前页面大小
    page = request.GET.get('current')
    pageSize = request.GET.get('pageSize')
    
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
