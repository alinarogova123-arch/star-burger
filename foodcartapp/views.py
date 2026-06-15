import json
import pprint

from django.http import JsonResponse
from rest_framework.response import Response
from django.templatetags.static import static
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
import phonenumbers


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
    address = order.get("address")
    first_name = order.get("firstname")
    last_name = order.get("lastname")
    phone_num = order.get("phonenumber")
    if not isinstance(first_name, str):
        return Response({"firstname": "Not a valid string."})
    if not first_name:
        return Response({"firstname": "Это поле не может быть пустым."})
    if not address:
        return Response({"address": "Это поле не может быть пустым."})
    if not last_name:
        return Response({"lastname": "Это поле не может быть пустым."})
    if not phone_num:
        return Response({"phonenumber": "Это поле не может быть пустым."})
    phone_num = phonenumbers.parse(phone_num, None)
    if not phonenumbers.is_possible_number(phone_num):
        return Response({"phonenumber": "Неверный формат номера"})
    if not phonenumbers.is_valid_number(phone_num):
        return Response({"phonenumber": "Неверный формат номера"})

    order_from_db, created = Order.objects.get_or_create(
        address=address,
        first_name=first_name,
        last_name=last_name,
        phone_num=phone_num,
    )

    products = order.get("products")

    try:
        for product in products:
            product_from_db = get_object_or_404(Product, id=product.get("product"))
            OrderProduct.objects.get_or_create(
                order=order_from_db,
                product=product_from_db,
                quantity=product.get("quantity")
                )
    except Exception as e:
        error = {"error": str(e)}
        return Response(error)
    if not products:
        error = {"error": "products is empty"}
        return Response(error)
    return Response({})
