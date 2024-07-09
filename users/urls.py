from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup, name='signup'),
    path('menu/', views.menu_view, name='menu'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('update_cart_item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('order_summary/', views.order_summary, name='order_summary'),
    path('confirm_order/', views.confirm_order, name='confirm_order'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
]

