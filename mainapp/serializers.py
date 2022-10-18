from rest_framework import serializers
from django.core.validators import ValidationError
from django.db import transaction
from mainapp.models import Collection, Product, Customer, Cart, CartItem, Order, OrderItem, Address


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ('id', 'title', 'products_count')


class ProductSerializer(serializers.ModelSerializer):
    collection = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all())

    class Meta:
        model = Product
        fields = ('id', 'title', 'description',
                  'unit_price', 'inventory', 'collection')


class AddressSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'street', 'house', 'korpus', 'flat')


class CustomerSerializer(serializers.ModelSerializer):
    address = AddressSerialzer()

    class Meta:
        model = Customer
        fields = ('id', 'first_name', 'last_name',
                  'email', 'phone', 'address')

    def create(self, validated_data):
        with transaction.atomic():
            address = Address.objects.create(**validated_data['address'])
            customer = Customer.objects.create(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                email=validated_data['email'],
                phone=validated_data['phone'],
                address=address,
            )
            return customer

    def update(self, instance, validated_data):
        pass

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'unit_price')


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price')

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ('id', 'product', 'quantity', 'total_price')


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price')

    def get_total_price(self, cart: CartItem):
        return sum([item.quantity * item.product.unit_price
                    for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total_price')


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise ValidationError("Этот товар не существует")
        return value

    '''if user adds the same product doesn't stack duplicate records 
           and just increases quantity'''

    def save(self, *args, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'quantity')


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ('quantity',)


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'customer', 'payment_status',
                  'placed_at', 'orderitems')


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise ValidationError('Не существует корзины с данным ID')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise ValidationError('Пустая корзина')
        return cart_id

    '''converts cart and cart items to order and order items 
    objects and deletes cart object afterwards'''

    def save(self, **kwargs):
        with transaction.atomic():
            customer = Customer.objects.get(id=self.context['customer_id'])
            order = Order.objects.create(customer=customer)

            cart_items = CartItem.objects.select_related('product')\
                .filter(cart_id=self.validated_data['cart_id'])

            order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity)
                           for item in cart_items]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']
