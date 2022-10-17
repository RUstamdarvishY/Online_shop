import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import Product


product_url = '/products/'

'''permissions are AdminOrReadOnly'''


class TestProductList:

    @pytest.mark.django_db
    def test_list_products(self, api_client):
        baker.make(Product)

        response = api_client.get(product_url)

        assert response.status_code == status.HTTP_200_OK
        assert Product.objects.count() > 0


class TestProductRetrieve:
    @pytest.mark.django_db
    def test_retrieve_product(self, api_client):
        # pass description and inventory otherwise returns none which is invalid
        product = baker.make(Product, description='test', inventory=1)
        expected_json = {
            'id': product.id,
            'title': product.title,
            'description': product.description,
            'unit_price': product.unit_price,
            'inventory': product.inventory,
            'collection': product.collection.pk,
        }
        url = f'{product_url}{product.id}/'

        response = api_client.get(url)

        # don't check for unit price because of decimal errors
        assert response.data['id'] == expected_json['id']
        assert response.data['title'] == expected_json['title']
        assert response.data['description'] == expected_json['description']
        assert response.data['inventory'] == expected_json['inventory']
        assert response.data['collection'] == expected_json['collection']
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_retrieve_product_that_doesnt_exist(self, api_client):
        url = f'{product_url}1/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProductCreate:
    @pytest.mark.django_db
    def test_create_product(self, api_client, auth_user):
        auth_user(is_staff=True)
        product = baker.make(Product, description='test', inventory=1)
        expected_json = {
            'title': product.title,
            'description': product.description,
            'unit_price': product.unit_price,
            'inventory': product.inventory,
            'collection': product.collection.pk,
        }

        response = api_client.post(product_url, expected_json)

        # don't check for unit price because of decimal errors
        assert response.data['title'] == expected_json['title']
        assert response.data['description'] == expected_json['description']
        assert response.data['inventory'] == expected_json['inventory']
        assert response.data['collection'] == expected_json['collection']
        assert response.status_code == status.HTTP_201_CREATED
        assert Product.objects.count() > 0

    @pytest.mark.django_db
    def test_create_product_with_invalid_data(self, api_client, auth_user):
        auth_user(is_staff=True)

        response = api_client.post(product_url, data={'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post(product_url, data={'title': 'test'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_is_not_admin_returns_403(self, api_client, auth_user):
        auth_user(is_staff=False)

        response = api_client.post(product_url, data={'title': 'test'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProductUpdate:
    @pytest.mark.django_db
    def test_update_product(self, api_client, auth_user):
        auth_user(is_staff=True)
        old_product = baker.make(
            Product, description='test', inventory=1)
        new_product = baker.make(
            Product, description='test', inventory=1)
        new_data = {
            'id': old_product.id,
            'title': new_product.title,
            'description': new_product.description,
            'unit_price': new_product.unit_price,
            'inventory': new_product.inventory,
            'collection': old_product.collection.pk,
        }
        url = f'{product_url}{old_product.id}/'

        response = api_client.put(url, new_data)

        # don't check for unit price because of decimal errors
        assert response.data['id'] == new_data['id']
        assert response.data['title'] == new_data['title']
        assert response.data['description'] == new_data['description']
        assert response.data['inventory'] == new_data['inventory']
        assert response.data['collection'] == new_data['collection']
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    @pytest.mark.parametrize('field', ['title', 'description', 'inventory'])
    def test_partially_update_product(self, api_client, auth_user, field):
        auth_user(is_staff=True)
        product = baker.make(Product, description='test', inventory=1)
        new_data = {
            'title': product.title,
            'description': product.description,
            'unit_price': product.unit_price,
            'inventory': product.inventory,
            'collection': product.collection,
        }
        valid_field = new_data[field]
        url = f'{product_url}{product.id}/'

        response = api_client.patch(
            url, data={field: valid_field})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[field] == valid_field


class TestProductDelete:

    @ pytest.mark.django_db
    def test_delete_product(self, api_client, auth_user):
        auth_user(is_staff=True)
        product = baker.make(Product)
        url = f'{product_url}{product.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Product.objects.count() == 0
