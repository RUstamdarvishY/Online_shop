import pytest
from uuid import uuid4
from rest_framework import status
from model_bakery import baker
from mainapp.models import CartItem, Cart


'''permissions are AllowAny'''


@pytest.fixture
def get_cartitem_url():
    def do_get_cartitem_url(cart_pk):
        cartitem_url = f'/carts/{cart_pk}/items/'
        return cartitem_url
    return do_get_cartitem_url


class TestCartItemList:

    @pytest.mark.django_db
    def test_list_cartitems(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        baker.make(CartItem, cart=cart)

        response = api_client.get(get_cartitem_url(cart.id))

        assert response.status_code == status.HTTP_200_OK
        assert CartItem.objects.count() > 0


class TestCartItemRetrieve:
    @pytest.mark.django_db
    def test_retrieve_cartitem(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        expected_json = {
            'id': cartitem.id,
            'cart': cartitem.cart,
            'product': cartitem.product,
            'quantity': cartitem.quantity
        }
        url = f'{get_cartitem_url(cart.id)}{cartitem.id}/'

        response = api_client.get(url)

        assert response.data['id'] == expected_json['id']
        assert response.data['quantity'] == expected_json['quantity']
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_retrieve_cartitem_that_doesnt_exist(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        url = f'{get_cartitem_url(cart.id)}100/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_retrieve_cartitem_for_cart_that_doesnt_exist(self, api_client,
                                                          get_cartitem_url):

        cartitem = baker.make(CartItem)
        url = f'{get_cartitem_url(uuid4())}{cartitem.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCartItemCreate:
    @pytest.mark.django_db
    def test_create_cartitem(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        expected_json = {
            'product_id': cartitem.product.pk,
            'quantity': cartitem.quantity
        }

        response = api_client.post(get_cartitem_url(cart.id), expected_json)

        # multiply expected_json by 2 because of stacking of duplicate records for response data quantity field
        assert response.data['quantity'] == expected_json['quantity'] * 2
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_create_invalid_cartitem(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        expected_json = {
            'product_id': cartitem.product.pk,
            'quantity': -1
        }

        response = api_client.post(get_cartitem_url(cart.id), expected_json)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCartItemUpdate:
    @pytest.mark.django_db
    def test_update_cartitem_unsupported_returns_405(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        url = f'{get_cartitem_url(cart.id)}{cartitem.id}/'

        response = api_client.put(url, {'quantity': cartitem.quantity})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_partially_update_cartitem(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        url = f'{get_cartitem_url(cart.id)}{cartitem.id}/'

        response = api_client.patch(url, {'quantity': cartitem.quantity})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['quantity'] == cartitem.quantity


class TestCartItemDelete:

    @ pytest.mark.django_db
    def test_delete_cartitem(self, api_client, get_cartitem_url):
        cart = baker.make(Cart)
        cartitem = baker.make(CartItem, cart=cart)
        url = f'{get_cartitem_url(cart.id)}{cartitem.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert CartItem.objects.count() == 0
