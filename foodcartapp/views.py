from django.http import JsonResponse
from django.templatetags.static import static

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import OrderItem, Product, Order


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


def is_error(data):
    fields = [
        'firstname',
        'lastname',
        'phonenumber',
        'address',
    ]
    for field in fields:
        if field not in data:
            return {
                'error': f'{field}: Обязательное поле.'
            }
        if not data[field]:
            return {
                'error': f'{field}: Это поле не может быть пустым.'
            }
        if isinstance(data[field], list):
            return {
                'error': f'{field}: Это поле не может быть списком.'
            }
    if 'products' not in data or not data['products'] or not isinstance(data['products'], list):
        return {
             'error': 'products key are not presented or not list'
         }
    try:
        for item in data['products']:
            id = item['product']
            product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return {
             'error': f'products: Недопустимый первичный ключ {id}'
         }
    
    phonenumber = (data['phonenumber']).lstrip('+')
    if phonenumber[:2] not in ['89', '79']:
        return {
             'error': f'phonenumber: Введен некорректный номер телефона: {phonenumber[:2]}.'
         }

    return {}


@api_view(['POST'])
def register_order(request):
    try:
        data = request.data
        error = is_error(data)
        if error:
            return Response(error, status=status.HTTP_404_NOT_FOUND)
        order = Order()
        order.customer_name = data['firstname']
        order.customer_last_name = data['lastname']
        order.customer_phone_number = data['phonenumber']
        order.customer_address = data['address']
        order.save()
        for item in data['products']:
            OrderItem.objects.create(
                order=order,
                product=Product.objects.get(id=item['product']),
                quantity=item['quantity'],
            )
     
        return Response({}, status=status.HTTP_200_OK)
    except ValueError:
        return Response({
            'error': 'Некорректные данные',
        })
