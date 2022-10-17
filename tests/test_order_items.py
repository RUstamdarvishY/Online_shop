import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import OrderItem, Order


'''permissions are IsAuthenticated'''


@pytest.fixture
def get_orderitem_url():
    def do_get_orderitem_url(order_pk):
        orderitem_url = f'/orders/{order_pk}/items/'
        return orderitem_url
    return do_get_orderitem_url


class TestOrderItemList:

    @pytest.mark.django_db
    def test_list_orderitems(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        baker.make(OrderItem, order=order)

        response = api_client.get(get_orderitem_url(order.id))

        assert response.status_code == status.HTTP_200_OK
        assert OrderItem.objects.count() > 0


class TestOrderItemRetrieve:
    @pytest.mark.django_db
    def test_retrieve_orderitem(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        orderitem = baker.make(OrderItem, order=order)
        expected_json = {
            'id': orderitem.id,
            'order': orderitem.order,
            'product': orderitem.product,
            'quantity': orderitem.quantity
        }
        url = f'{get_orderitem_url(order.id)}{orderitem.id}/'

        response = api_client.get(url)

        assert response.data['id'] == expected_json['id']
        assert response.data['quantity'] == expected_json['quantity']
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_retrieve_orderitem_that_doesnt_exist(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        url = f'{get_orderitem_url(order.id)}100/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.django_db
    def test_retrieve_orderitem_for_order_that_doesnt_exist(self, api_client,
                                                            auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        orderitem = baker.make(OrderItem)
        url = f'{get_orderitem_url(10)}{orderitem.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestOrderItemCreate:
    @pytest.mark.django_db
    def test_create_orderitem(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        orderitem = baker.make(OrderItem, order=order)
        expected_json = {
            'id': orderitem.id,
            'order': orderitem.order,
            'product': orderitem.product,
            'quantity': orderitem.quantity
        }

        response = api_client.post(get_orderitem_url(order.id), expected_json)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    @pytest.mark.django_db
    def test_user_is_anonymous_returns_401(self, api_client, get_orderitem_url):
        order = baker.make(Order)

        response = api_client.post(get_orderitem_url(
            order.id), data={'quantity': 10})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestOrderItemUpdate:
    @pytest.mark.django_db
    def test_update_orderitem(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        old_orderitem = baker.make(OrderItem, order=order)
        new_orderitem = baker.make(OrderItem, order=order)
        new_data = {
            'id': old_orderitem.id,
            'order': new_orderitem.order,
            'product': new_orderitem.product,
            'quantity': new_orderitem.quantity
        }
        url = f'{get_orderitem_url(order.id)}{old_orderitem.id}/'

        response = api_client.put(url, new_data)

        assert response.data['id'] == new_data['id']
        assert response.data['quantity'] == new_data['quantity']
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_partially_update_orderitem_not_allowed_returns_405(self, api_client,
                                                                auth_user, get_orderitem_url):
        auth_user(is_staff=True)
        order = baker.make(Order)
        orderitem = baker.make(OrderItem, order=order)
        url = f'{get_orderitem_url(order.id)}{orderitem.id}/'

        response = api_client.patch(url, data={'quantity': 5})

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestOrderItemDelete:

    @ pytest.mark.django_db
    def test_delete_orderitem(self, api_client, auth_user, get_orderitem_url):
        auth_user(is_staff=False)
        order = baker.make(Order)
        orderitem = baker.make(OrderItem, order=order)
        url = f'{get_orderitem_url(order.id)}{orderitem.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert OrderItem.objects.count() == 0
