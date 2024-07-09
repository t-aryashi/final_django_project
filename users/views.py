
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from .models import MenuItem
from django.http import HttpResponseRedirect
from django.urls import reverse

def home(request):
    return render(request, 'users/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('menu')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


from django.contrib.auth.decorators import login_required

@login_required
def menu(request):
    return render(request, 'users/menu.html')

import logging

logger = logging.getLogger(__name__)

@login_required
def menu_view(request):
    query = request.GET.get('q')
    if query:
        menu_items = MenuItem.objects.filter(name__icontains=query)
    else:
        menu_items = MenuItem.objects.all()

    logger.debug(f"Menu items: {menu_items}")  # Logging debug statement

    return render(request, 'users/menu.html', {'menu_items': menu_items, 'query': query})




from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        # Logic to add the item to the cart goes here
        # For now, just redirect back to the menu page
        return HttpResponseRedirect(reverse('menu'))
    
# views.py
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, MenuItem

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        menu_item_id = request.POST.get('item_id')
        menu_item = MenuItem.objects.get(id=menu_item_id)
        user = request.user

        cart, created = Cart.objects.get_or_create(user=user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart')

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    item_count = cart_items.count()
    return render(request, 'users/cart.html', {'cart_items': cart_items, 'item_count': item_count})


from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CartItem

@login_required
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if 'quantity' in request.POST:
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()
    return redirect('cart')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, MenuItem, Order, OrderItem

@login_required
def order_summary(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)

    return render(request, 'users/order_summary.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })

@login_required
def confirm_order(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        return redirect('cart')

    total_amount = sum(item.menu_item.price * item.quantity for item in cart_items)
    order = Order.objects.create(user=request.user, total_amount=total_amount)
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            menu_item=cart_item.menu_item,
            quantity=cart_item.quantity
        )
    cart_items.delete()

    return redirect('confirmation')

@login_required
def confirmation(request):
    return render(request, 'users/confirmation.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from .models import Cart, CartItem, MenuItem, Order, OrderItem

@login_required
def user_profile(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')
    return render(request, 'users/profile.html', {'user': user, 'orders': orders})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserChangeForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})