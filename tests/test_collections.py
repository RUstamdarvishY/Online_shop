import pytest
from rest_framework import status
from model_bakery import baker
from mainapp.models import Collection


collection_url = '/collections/'

'''permissions are IsAdminOrReadOnly'''


class TestCollectionList:

    @pytest.mark.django_db
    def test_list_collections(self, api_client):
        baker.make(Collection)

        response = api_client.get(collection_url)

        assert response.status_code == status.HTTP_200_OK
        assert Collection.objects.count() > 0


class TestCollectionRetrieve:
    @pytest.mark.django_db
    def test_retrieve_collection(self, api_client):
        collection = baker.make(Collection)
        expected_json = {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0,
        }
        url = f'{collection_url}{collection.id}/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_json

    @pytest.mark.django_db
    def test_retrieve_collection_that_doesnt_exist(self, api_client):
        url = f'{collection_url}10/'

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCollectionCreate:
    @pytest.mark.django_db
    def test_create_collection(self, api_client, auth_user):
        auth_user(is_staff=True)
        baker.make(Collection, )

        response = api_client.post(collection_url, {'title': 'test'})

        assert response.data['title'] == 'test'
        assert response.status_code == status.HTTP_201_CREATED
        assert Collection.objects.count() > 0

    @pytest.mark.django_db
    def test_create_collection_with_invalid_data(self, api_client, auth_user):
        auth_user(is_staff=True)

        response = api_client.post(collection_url, data={'title': ''})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post(
            collection_url, data={'title': 'test'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_is_not_admin_returns_403(self, api_client, auth_user):
        auth_user(is_staff=False)

        response = api_client.post(
            collection_url, data={'title': 'test'})

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCollectionUpdate:
    @pytest.mark.django_db
    def test_update_collection(self, api_client, auth_user):
        auth_user(is_staff=True)
        old_collection = baker.make(Collection)
        new_collection = baker.prepare(Collection)
        new_data = {
            'id': old_collection.id,
            'title': new_collection.title,
            'products_count': 0,
        }
        url = f'{collection_url}{old_collection.id}/'

        response = api_client.put(url, new_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == new_data

    @pytest.mark.django_db
    def test_partially_update_collection(self, api_client, auth_user):
        auth_user(is_staff=True)
        collection = baker.make(Collection)
        new_data = {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0,
        }
        valid_field = new_data['title']
        url = f'{collection_url}{collection.id}/'

        response = api_client.patch(url, data={'title': valid_field})

        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == valid_field


class TestCollectionDelete:

    @pytest.mark.django_db
    def test_delete_collection(self, api_client, auth_user):
        auth_user(is_staff=True)
        collection = baker.make(Collection)
        url = f'{collection_url}{collection.id}/'

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Collection.objects.count() == 0
