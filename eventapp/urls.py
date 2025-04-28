from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
     path('about/',views.about,name='about'),
      path('events/',views.event_list,name='event_list'),

        path('contact/',views.contact,name='contact'),

        path('event/<int:event_id>/', views.event_detail, name='event_detail'),
        path('book/<int:event_id>/', views.book_event, name='book_event'),
        path('booking_success/<int:booking_id>/', views.booking_success, name='booking_success'),
        path('my_orders/', views.my_orders, name='my_orders'),
        path("cancel-booking/<int:booking_id>/", views.cancel_booking, name="cancel_booking"),

        path("manager/orders/", views.manager_orders, name="manager_orders"),  # 管理员接单页面
        path("manager/order/<int:booking_id>/", views.manager_order_detail, name="manager_order_detail"),  # 订单详情
        path("assign_order/<int:booking_id>/", views.assign_order, name="assign_order"),  # 抢单
        path("manager/my_orders/", views.my_assigned_orders, name="my_assigned_orders"),  # 管理员管理的订单
        path("confirm_quote/<int:booking_id>/", views.confirm_quote, name="confirm_quote"),  # 确认报价
        path("release_order/<int:booking_id>/", views.release_order, name="release_order"),  # 释放订单

        path("booking/<int:booking_id>/pay/", views.pay_order, name="pay_order")
]
