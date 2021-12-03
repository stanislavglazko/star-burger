import math

from geopy import distance as geopy_distance

from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from restaurateur.views import get_coords
from .models import OrderItem, Product, Order, RestaurantMenuItem


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ['id', 'products', 'firstname', 'lastname', 'phonenumber', 'address']


def get_restaraunts():
    restaurants = set()
    restaurant_menu_items = RestaurantMenuItem.objects.all()
    for item in restaurant_menu_items:
        restaurants.add(item.restaurant)
    return restaurants, restaurant_menu_items


@transaction.atomic
@api_view(['POST'])
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    restaurants, restaurant_menu_items = get_restaraunts()

    order = Order.objects.create(
        firstname=serializer.validated_data['firstname'],
        lastname=serializer.validated_data['lastname'],
        phonenumber=serializer.validated_data['phonenumber'],
        address=serializer.validated_data['address'],
    )

    for product in serializer.validated_data['products']:
        current_restaurants = set()
        for rm_item in restaurant_menu_items:
            if product['product'] == rm_item.product:
                current_restaurants.add(rm_item.restaurant)

        OrderItem.objects.create(
            order=order,
            product=product['product'],
            quantity=product['quantity'],
            cost=product['product'].price * product['quantity'],
        )

        restaurants = restaurants & current_restaurants

    order.available_restaurants.add(*restaurants)
    order.restaurant = restaurants.pop()
    order.save()

    serializer = OrderSerializer(order)

    return Response(serializer.data, status=status.HTTP_200_OK)
