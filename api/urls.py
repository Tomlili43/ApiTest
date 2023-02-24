from django.urls import path

from api.view import user, seller

# app_name = 'api'
urlpatterns = [
    # http://localhost:5010/api/user/myinfo
    path('user/myinfo', user.myinfo, name='myinfo'),

    # http://localhost:5010/api/seller/get_seller_list
    path('seller/get_seller_list', seller.get_seller_list, name='get_seller_list'),

    # http://localhost:5010/local/seller/get_seller_list
    path('seller/get_seller_list', seller.get_seller_list, name='get_seller_list'),

    # http://localhost:5010/api/seller/set_seller_list
    path('seller/set_seller_list', seller.set_seller_list, name='set_seller_list'),

    # http://localhost:5010/api/seller/base_info
    path('seller/base_info', seller.base_info, name='base_info'),
]