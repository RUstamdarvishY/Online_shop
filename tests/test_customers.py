import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import Customer


customer_url = '/customers/'

'''permissions are IsAdminUser (AllowAny for Posting)'''


class TestCustomerList:

    @pytest.mark.django_db
    def test_list_customers(self, api_client, auth_user):
        auth_user(is_staff=True)
        baker.make(Customer, birth_date='2020-10-14')

        response = api_client.get(customer_url)

        assert response.status_code == status.HTTP_200_OK
        assert Customer.objects.count() > 0


class TestCustomerRetrieve:
    @pytest.mark.django_db
    def test_retrieve_customer(self, api_client, auth_user):
        auth_user(is_staff=True)
        customer = baker.make(Customer, birth_date='2020-10-14')
        expected_json = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone,
            'birth_date': customer.birth_date,
            'user_id': customer.user_id
        }
        url = f'{customer_url}{customer.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_json

    @pytest.mark.django_db
    def test_retrieve_customer_that_doesnt_exist(self, api_client, auth_user):
        auth_user(is_staff=True)
        url = f'{customer_url}10/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCustomerCreate:
    @pytest.mark.django_db
    def test_create_customer_not_allowed_returns_405(self, api_client, auth_user):
        auth_user(is_staff=True)

        response = api_client.post(
            customer_url, data={'first_name': 'test'})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post(
            customer_url, data={'first_name': 'test'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_is_not_admin_returns_403(self, api_client, auth_user):
        auth_user(is_staff=False)

        response = api_client.post(
            customer_url, data={'first_name': 'test'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCustomerUpdate:
    @pytest.mark.django_db
    def test_update_customer(self, api_client, auth_user):
        auth_user(is_staff=True)
        old_customer = baker.make(Customer, birth_date='2020-12-14')
        new_customer = baker.prepare(Customer, birth_date='2010-10-16')
        new_data = {
            'id': old_customer.id,
            'first_name': new_customer.first_name,
            'last_name': new_customer.last_name,
            'email': new_customer.email,
            'phone': new_customer.phone,
            'birth_date': new_customer.birth_date,
            'user_id': old_customer.user_id
        }
        url = f'{customer_url}{old_customer.id}/'

        response = api_client.put(url, new_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == new_data

    @pytest.mark.django_db
    @pytest.mark.parametrize('field', ['first_name', 'last_name', 'email', 'phone', 'birth_date'])
    def test_partially_update_customer(self, api_client, auth_user, field):
        auth_user(is_staff=True)
        customer = baker.make(Customer, birth_date='2020-10-14')
        new_data = {
            'id': customer.id,
            'first_name': customer.first_name,
            'last_name': customer.last_name,
            'email': customer.email,
            'phone': customer.phone,
            'birth_date': customer.birth_date,
        }
        valid_field = new_data[field]
        url = f'{customer_url}{customer.id}/'

        response = api_client.patch(url, data={field: valid_field})

        assert response.status_code == status.HTTP_200_OK
        assert response.data[field] == valid_field


class TestCustomerDelete:

    @pytest.mark.django_db
    def test_delete_customer(self, api_client, auth_user):
        auth_user(is_staff=True)
        customer = baker.make(Customer, birth_date='2020-10-14')
        url = f'{customer_url}{customer.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Customer.objects.count() == 0
