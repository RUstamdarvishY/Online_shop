from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, CreateModelMixin
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models.aggregates import Count
from mainapp.permissions import IsAdminOrReadOnly
from mainapp.pagination import DefaultPagination
from mainapp.filters import ProductFilter
from mainapp.models import Collection, Product, Customer, Cart, CartItem, Order, OrderItem
from mainapp.serializers import AddCartItemSerializer, CollectionSerializer, CreateOrderSerializer, ProductSerializer, CustomerSerializer, CartSerializer, CartItemSerializer, UpdateCartItemSerializer, OrderSerializer, OrderItemSerializer, UpdateOrderSerializer


class CollectionViewSet(ModelViewSet):
    serializer_class = CollectionSerializer
    queryset = Collection.objects.annotate(
        products_count=Count('product')).all()
    permission_classes = [IsAdminOrReadOnly]

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
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
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
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [AllowAny()]
        return [IsAdminUser()]

    def destroy(self, request, pk):
        customer = Customer.objects.filter(pk=pk).first()
        order = Order.objects.filter(customer=customer).count()
        if order > 0:
            return Response({'error': 'Нельзя удалить клиента у которого есть незавершенный заказ'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        customer.delete()
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
        return [AllowAny()]

    '''after creating an order returns order object, not cart_id'''

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data,
                                           context={'customer_id': self.request.customer.id})
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

        customer_id = Customer.objects.get(
            'customer_id').get(customer_id=self.request.customer.id)
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
    permission_classes = [AllowAny()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return OrderItem.objects.all()
        return OrderItem.objects.filter(order_id=self.kwargs['order_pk'])
