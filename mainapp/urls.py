from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from mainapp.views import CollectionViewSet, OrderViewSet, OrderItemViewSet, ProductViewSet, CustomerViewSet, CartViewSet, CartItemViewSet

router = DefaultRouter()

router.register('collections', CollectionViewSet)
router.register('products', ProductViewSet, basename='products')
router.register('customers', CustomerViewSet)
router.register('carts', CartViewSet)
router.register('orders', OrderViewSet, basename='orders')


carts_router = NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-items')

orders_router = NestedDefaultRouter(router, 'orders', lookup='order')
orders_router.register('items', OrderItemViewSet, basename='order-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(carts_router.urls)),
    path('', include(orders_router.urls)),
]
