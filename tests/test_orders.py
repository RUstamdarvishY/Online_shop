import pytest
from uuid import uuid4
from rest_framework import status
from model_bakery import baker
from mainapp.models import Order, Cart, CartItem, OrderItem


order_url = '/orders/'

'''permissions are AllowAny (for PATCH, DELETE - IsAdmin)'''


class TestOrderList:
    @pytest.mark.django_db
    def test_list_orders(self, api_client, auth_user):
        auth_user(is_staff=True)
        baker.make(Order)

        response = api_client.get(order_url)

        assert response.status_code == status.HTTP_200_OK
        assert Order.objects.count() > 0


class TestOrderRetrieve:
    @pytest.mark.django_db
    def test_retrieve_order(self, api_client, auth_user):
        auth_user(is_staff=True)  # to view al orders
        order = baker.make(Order)
        url = f'{order_url}{order.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == order.id

    @pytest.mark.django_db
    def test_retrieve_order_that_doesnt_exist(self, api_client, auth_user):
        auth_user(is_staff=True)
        url = f'{order_url}10/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrderCreate:
    @pytest.mark.django_db
    def test_create_order(self, api_client, auth_user):
        auth_user(is_staff=False)
        items = baker.make(CartItem, _quantity=3)
        cart = baker.make(Cart, id=uuid4(), items=items)

        response = api_client.post(order_url, {'cart_id': cart.id})

        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() > 0
        assert Cart.objects.count() == 0

    @pytest.mark.django_db
    def test_create_order_cart_id_doesnt_exist(self, api_client, auth_user):
        auth_user(is_staff=False)

        response = api_client.post(order_url, {'cart_id': uuid4()})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_cart_is_empty(self, api_client, auth_user):
        auth_user(is_staff=False)
        cart = baker.make(Cart, id=uuid4())

        response = api_client.post(order_url, {'cart_id': cart.id})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_create_order_with_invalid_data(self, api_client, auth_user):
        auth_user(is_staff=False)

        response = api_client.post(order_url, data={'cart_id': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post(
            order_url, data={'cart_id': 'test'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrderUpdate:
    @pytest.mark.django_db
    def test_update_order_not_allowed_returns_405(self, api_client, auth_user):
        auth_user(is_staff=True)
        order = baker.make(Order)
        url = f'{order_url}{order.id}/'

        response = api_client.put(url, {'payment_status': ''})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_partially_update_order(self, api_client, auth_user):
        auth_user(is_staff=True)
        order = baker.make(Order)
        url = f'{order_url}{order.id}/'

        response = api_client.patch(
            url, data={'payment_status': 'P'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['payment_status'] == 'P'


class TestOrderDelete:
    @pytest.mark.django_db
    def test_delete_order(self, api_client, auth_user):
        auth_user(is_staff=True)
        order = baker.make(Order)
        url = f'{order_url}{order.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Order.objects.count() == 0

    @pytest.mark.django_db
    def test_user_is_not_admin_returns_403(self, api_client, auth_user):
        auth_user(is_staff=False)
        order = baker.make(Order)
        url = f'{order_url}{order.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    def test_delete_order_with_order_items(self, api_client, auth_user):
        auth_user(is_staff=True)
        order = baker.make(Order)
        baker.make(OrderItem, order=order, _quantity=10)
        
        url = f'{order_url}{order.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert Order.objects.count() == 1