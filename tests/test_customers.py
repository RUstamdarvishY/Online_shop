import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import Customer, Address


customer_url = '/customers/'

'''permissions are IsAdminUser (AllowAny for Posting)'''


class TestCustomerList:

    @pytest.mark.django_db
    def test_list_customers_for_admin(self, api_client, auth_user):
        auth_user(is_staff=True)
        baker.make(Customer)

        response = api_client.get(customer_url)

        assert response.status_code == status.HTTP_200_OK
        assert Customer.objects.count() > 0

    @pytest.mark.django_db
    def test_list_customers_returns_405(self, api_client):
        baker.make(Customer)

        response = api_client.get(customer_url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCustomerRetrieve:
    @pytest.mark.django_db
    def test_retrieve_customer_for_admin(self, api_client, auth_user):
        auth_user(is_staff=True)
        customer = baker.make(Customer)
        expected_json = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone,
            'address': customer.address,
        }
        url = f'{customer_url}{customer.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == expected_json['id']
        assert response.data['first_name'] == expected_json['first_name']
        assert response.data['last_name'] == expected_json['last_name']
        assert response.data['email'] == expected_json['email']
        assert response.data['phone'] == expected_json['phone']

    @pytest.mark.django_db
    def test_retrieve_customer_that_doesnt_exist(self, api_client, auth_user):
        auth_user(is_staff=True)
        url = f'{customer_url}161232/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_retrive_customer_returns_405(self, api_client):
        customer = baker.make(Customer)

        url = f'{customer_url}{customer.id}/'
        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCustomerCreate:
    @pytest.mark.django_db
    def test_create_customer(self, api_client):
        address = baker.make(Address)
        customer = baker.make(Customer, address=address)
        expected_json = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone,
            'address': address,
        }
        url = f'{customer_url}{customer.id}/'

        response = api_client.post(url, expected_json)

        assert response.data == expected_json
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.django_db
    def test_create_customer_with_invalid_data(self, api_client):
        customer = baker.make(Customer)
        expected_json = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': '123abc',
            'phone': customer.phone,
            'address': customer.address,
        }

        url = f'{customer_url}{customer.id}/'

        response = api_client.post(url, expected_json)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCustomerUpdate:
    @pytest.mark.django_db
    def test_update_customer_for_admin(self, api_client, auth_user):
        auth_user(is_staff=True)
        address = baker.make(Address)
        old_customer = baker.make(Customer)
        new_customer = baker.prepare(Customer)
        new_data = {
            'id': old_customer.id,
            'first_name': new_customer.first_name,
            'last_name': new_customer.last_name,
            'email': new_customer.email,
            'phone': new_customer.phone,
            'address': address,
        }
        url = f'{customer_url}{old_customer.id}/'

        response = api_client.put(url, new_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == new_data

    @pytest.mark.django_db
    def test_update_customer(self, api_client):
        old_customer = baker.make(Customer)
        new_customer = baker.prepare(Customer)
        new_data = {
            'id': old_customer.id,
            'first_name': new_customer.first_name,
            'last_name': new_customer.last_name,
            'email': new_customer.email,
            'phone': new_customer.phone,
            'address': new_customer.address,
        }
        url = f'{customer_url}{old_customer.id}/'

        response = api_client.put(url, new_data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.django_db
    @pytest.mark.parametrize('field', ['first_name', 'last_name', 'email'])
    def test_partially_update_customer_for_admin(self, api_client, auth_user, field):
        auth_user(is_staff=True)
        customer = baker.make(Customer)
        new_data = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'address': customer.address,
        }
        valid_field = new_data[field]
        url = f'{customer_url}{customer.id}/'

        response = api_client.patch(url, data={field: valid_field})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[field] == valid_field


class TestCustomerDelete:

    @pytest.mark.django_db
    def test_delete_customer_for_admin(self, api_client, auth_user):
        auth_user(is_staff=True)
        customer = baker.make(Customer)
        url = f'{customer_url}{customer.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Customer.objects.count() == 0

    @pytest.mark.django_db
    def test_delete_customer_with_order_returns_405(self, api_client, auth_user):
        pass

    @pytest.mark.django_db
    def test_delete_customer(self, api_client):
        customer = baker.make(Customer)
        url = f'{customer_url}{customer.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Customer.objects.count() == 1
