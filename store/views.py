from store.permissions import FullDjangoModelPermissions, IsAdminOrReadOnly, ViewCustomerHistoryPermission
from store.pagination import DefaultPagination
from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404, render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework import status
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from web3 import Web3

from .serializers import (AddCartItemSerializer, CartItemSerializer, CartSerializer, CollectionSerializer,
                          CreateOrderSerializer, CustomerSerializer, OrderSerializer, ProductImageSerializer,
                          ProductSerializer, UpdateCartItemSerializer, UpdateOrderSerializer,
                          EmptySerializer, VerifyCryptoSerializer)
from .filters import ProductFilter
from .models import Cart, CartItem, Collection, Customer, Order, OrderItem, Product, ProductImage

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.prefetch_related('images').all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=kwargs['pk']):
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={
                                           'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == 'checkout':
            return EmptySerializer
        if self.action == 'verify_crypto_payment':
            return VerifyCryptoSerializer
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def checkout(self, request, pk=None):
        order = self.get_object()
        if order.payment_status == 'C':
            return Response({'error': 'This order has already been paid.'}, status=status.HTTP_400_BAD_REQUEST)
        if order.items.count() == 0:
            return Response({'error': 'This order has no items.'}, status=status.HTTP_400_BAD_REQUEST)

        stripe_line_items = []
        for item in order.items.all():
            stripe_line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(float(item.unit_price) * 100),
                    'product_data': {'name': item.product.title},
                },
                'quantity': item.quantity,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=stripe_line_items,
                mode='payment',
                success_url='http://127.0.0.1:8000/payment-success/',
                cancel_url='http://127.0.0.1:8000/payment-cancelled/',
                client_reference_id=str(order.id)
            )
            return Response({'checkout_url': checkout_session.url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['POST'], permission_classes=[IsAuthenticated])
    def verify_crypto_payment(self, request, pk=None):
        order = self.get_object()
        if order.payment_status == 'C':
            return Response({'error': 'This order has already been paid.'}, status=status.HTTP_400_BAD_REQUEST)
        tx_hash = request.data.get('tx_hash')
        if not tx_hash:
            return Response({'error': 'Transaction hash is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
            if not w3.is_connected():
                return Response({'error': 'Backend failed to connect to the blockchain.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            if receipt['status'] == 1:
                order.payment_status = 'C'
                order.save()
                return Response({'message': 'Cryptographic payment verified', 'tx_hash': tx_hash})
            else:
                return Response({'error': 'Transaction reverted on the blockchain.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Could not verify transaction on the blockchain.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def checkout_page(request, order_id):
    actual_order = get_object_or_404(Order, id=order_id)
    return render(request, 'checkout.html', {'order': actual_order})


class ProductImageViewSet(ModelViewSet):
    serializer_class = ProductImageSerializer

    def get_serializer_context(self): return {
        'product_id': self.kwargs['product_pk']}
    def get_queryset(self): return ProductImage.objects.filter(
        product_id=self.kwargs['product_pk'])


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = getattr(session, 'client_reference_id', None)
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                order.payment_status = 'C'
                order.save()
            except Order.DoesNotExist:
                pass

    return HttpResponse(status=200)
