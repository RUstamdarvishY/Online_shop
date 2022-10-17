from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from django.contrib.auth.models import User
from mainapp.models import Collection, Product, Customer, Cart, CartItem, Order, OrderItem
from mainapp.serializers import AddCartItemSerializer, CollectionSerializer, CreateOrderSerializer, ProductSerializer, CustomerSerializer, CartSerializer, CartItemSerializer, UpdateCartItemSerializer, OrderSerializer, OrderItemSerializer, UpdateOrderSerializer


class CollectionViewSet(ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.annotate(
        products_count=Count('product')).all()

    def destroy(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        product = Product.objects.filter(collection=collection).count()
        if product > 0:
            return Response({'error': 'Нельзя удалить раздел т.к. к нему привязан один или больше продуктов'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price']

    def destroy(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        orderitems = OrderItem.objects.filter(product=product).count()
        if orderitems > 0:
            return Response({'error': 'Нельзя удалить продукт т.к. этот продукт есть в существующих заказах'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerViewSet(ModelViewSet):
    http_method_names = ['get', 'put', 'patch', 'delete']
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()
    permission_classes = [IsAdminUser]

    '''geting currently logged in user'''
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        customer = Customer.objects.filter(user=user).first()
        order = Order.objects.filter(customer=customer).count()
        if order > 0:
            return Response({'error': 'Нельзя удалить клиента у которого есть незавершенный заказ'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartViewSet(RetrieveModelMixin, CreateModelMixin, DestroyModelMixin, GenericViewSet):
    serializer_class = CartSerializer
    '''use prefetch_related because of duplicate queries on items and products'''
    queryset = Cart.objects.prefetch_related('items__product').all()


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch',
                         'delete']  # list of allowed methods

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    '''after creating an order returns order object, not cart_id'''

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,
                                           context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()

        customer_id = Customer.objects.only(
            'id').get(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)

    def destroy(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        if order.orderitems.count() > 0:
            return Response({'error': 'Нельзя удалить заказ в котором есть отдельные заказаные товары, сначала удалите товары из заказа'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderItemViewSet(ModelViewSet):
    http_method_names = ['get', 'put',
                         'delete', 'head', 'options']

    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order_id=self.kwargs['order_pk'])
