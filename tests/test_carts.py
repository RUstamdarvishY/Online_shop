import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import Cart


cart_url = '/carts/'

'''permissions are AllowAny'''


class TestcartList:

    @pytest.mark.django_db
    def test_list_carts_unsupported_returns_405(self, api_client):
        baker.make(Cart)

        response = api_client.get(cart_url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestCartRetrieve:
    @pytest.mark.django_db
    def test_retrieve_cart(self, api_client):
        cart = baker.make(Cart)
        url = f'{cart_url}{cart.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert Cart.objects.count() > 0

    @pytest.mark.django_db
    def test_retrieve_cart_that_doesnt_exist(self, api_client):
        url = f'{cart_url}10/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCartCreate:
    @pytest.mark.django_db
    def test_create_cart(self, api_client):
        baker.make(Cart)

        response = api_client.post(cart_url)

        assert response.status_code == status.HTTP_201_CREATED
        assert Cart.objects.count() > 0


class TestCartUpdate:
    @pytest.mark.django_db
    def test_update_cart_unsupported_returns_405(self, api_client):
        cart = baker.make(Cart)
        url = f'{cart_url}{cart.id}/'

        response = api_client.put(url, {'created_at': '2020-01-01'})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_partially_update_unsupported_returns_405(self, api_client):
        cart = baker.make(Cart)
        url = f'{cart_url}{cart.id}/'

        response = api_client.patch(url, {'created_at': '2020-01-01'})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestCartDelete:

    @pytest.mark.django_db
    def test_delete_cart(self, api_client):
        cart = baker.make(Cart)
        url = f'{cart_url}{cart.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Cart.objects.count() == 0
