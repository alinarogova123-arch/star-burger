import json
import pprint

from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view


from .models import Product
from .models import Order
from .models import OrderProduct


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
            } if product.category else None,
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


@api_view(['POST'])
def register_order(request):
    order = request.data
    # pprint.pprint(order)
    order_from_db, created = Order.objects.get_or_create(
        address=order.get("address"),
        first_name=order.get("firstname"),
        last_name=order.get("lastname"),
        phone_num=order.get("phonenumber"),
    )
    for product in order.get("products"):
        product_from_db = get_object_or_404(Product, id=product.get("product"))
        OrderProduct.objects.get_or_create(
            order=order_from_db,
            product=product_from_db,
            quantity=product.get("quantity")
            )

    return Response({})
