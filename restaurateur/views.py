import requests

from geopy import distance as geopy_distance

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Order, Product, Restaurant
from distance.models import PlaceCoords

from star_burger.settings import APIKEY


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coords(place_address):
    try:
        place_coords = PlaceCoords.objects.get(address=place_address)
        return place_coords.lon, place_coords.lat
    except PlaceCoords.DoesNotExist:
        place_address_lon, place_address_lat = fetch_coordinates(
            APIKEY,
            place_address,
            )
        PlaceCoords.objects.create(
            address=place_address,
            date_of_calculate_coords=timezone.now(),
            lon=place_address_lon,
            lat=place_address_lat,
            )
        return place_address_lon, place_address_lat


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.get_cost().prefetch_related('available_restaurants')
    for order in orders:
        order.restaurants_and_distance = []
        order_address_lon, order_address_lat = get_coords(order.address)
        for restaurant in order.available_restaurants.all():
            restaurant_lon, restaurant_lat = get_coords(restaurant.address)
            distance_between_order_and_restaurant = round(geopy_distance.distance(
                (order_address_lat,  order_address_lon),
                (restaurant_lat, restaurant_lon)).km)
            order.restaurants_and_distance.append((restaurant.name, distance_between_order_and_restaurant))
        order.restaurants_and_distance = sorted(order.restaurants_and_distance, key=lambda x: x[1])

    return render(request, template_name='order_items.html', context={
        'order_items': orders,
    })
