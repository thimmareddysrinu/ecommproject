from django.urls import path 
from django.contrib.auth import views as auth_views
from .views import *

app_name='ecomapp'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('category/', CategoryView.as_view(), name='allproducts'),
    path('details/<slug:slug>/', ProductdetailView.as_view(), name='productdetail'),
    path('addtocart/<int:pro_id>/', AddtocartView.as_view(), name='addtocart'),
    path('mycart/', MycartView.as_view(), name='mycart'),
    path('managecart/<int:cp_id>/<int:cp_action>/',
         ManagecartView, name='managecart'),
    path('mycheckout/', MycheckView.as_view(), name='mycheckout'),
    path('customerregis/', CustomerregisView.as_view(), name='customerregis'),
    path('logout/', CustomerlogoutView.as_view(), name='customerlogout'),
    path('login/', Customerloginview.as_view(), name='Customerloginview'),
    path('profile/', profileView.as_view(), name='profile'),
    path('profile/order-<int:pk>', OrderdetailView.as_view(), name='idsdeatail'),
    path('search/', SearchView.as_view(), name='search'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='passwordforgot'),
    path("password-reset/<email>/<token>/",PasswordResetView.as_view(), name="passwordreset"),


    #payment 
     path("razorpay/",Razorpay.as_view(), name="razorpayrequest"),


   
   #password reset
#    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='forgotpassword.html'), name='forgotpassword'),

#    path('password_sent/', auth_views.PasswordResetDoneView.as_view( template_name='reset_password_sent.html'),name='password_done'),

#    path('confirmreset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view( template_name='confirmreset.html'),name='password_confirm'),

#    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view( template_name='completereset.html'),name='password_complete'),
   
   





]
