
from rest_framework import viewsets, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Buildoapi.models import Review, WorkOrder, RareUser, Rating
from Buildoapi.views.rareusers import RareUserSerializer


class ReviewSerializer(serializers.ModelSerializer):
    customer = RareUserSerializer()
    contractor = RareUserSerializer()
    contractor_username = serializers.SerializerMethodField()
    customer_username = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = '__all__'

    def get_contractor_username(self, obj):
        contractor = obj.contractor
        if contractor:
            return contractor.user.username
        return None
    def get_customer_username(self,obj):
        customer= obj.customer
        if customer: 
            return customer.user.username
    def get_author(self, obj):
        author = obj.customer  # Assuming 'customer' is a RareUser instance
        if author:
            return author.user.get_full_name()
        return None
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    @action(detail=True, methods=['get'])
    def check_work_order_status(self, request, pk=None):
        review = self.get_object()
        work_order_status = self.get_work_order_status(review)
        return Response({'work_order_status': work_order_status})

    def get_work_order_status(self, review):
        # Assuming that a Review is associated with a Contractor
        contractor = review.contractor

        if contractor:
            work_order_status = WorkOrder.objects.filter(contractor=contractor).first().status.status
            return work_order_status

        return 'Unknown'
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Modify the response to include the contractor's username
        response_data = serializer.data
        for review_data in response_data:
            review_data['contractor_username'] = review_data.get('contractor_username', None)

        return Response(response_data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ReviewSerializer(instance)
        return Response(serializer.data)
    def create(self, request, *args, **kwargs):
        work_order_id = request.data.get('work_order_id')
        work_order = WorkOrder.objects.get(pk=work_order_id)

        # Get the authenticated user
        authenticated_user = RareUser.objects.get(user=request.user.id)

        # Check if the work order has a customer and if it matches the authenticated user
        if work_order.customer_id == authenticated_user.id:
            # Check if the work order status is 'in-progress' or 'Complete' before allowing the review
            if work_order.status.status in ['in-progress', 'Complete']:
                # Get the customer and contractor explicitly from the work order
                customer_id = work_order.customer_id
                contractor_id = work_order.contractor_id
                customer = RareUser.objects.get(pk=customer_id)
                contractor = RareUser.objects.get(pk=contractor_id)
                rating_value = request.data.get('rating')
                rating = Rating.objects.get(value=rating_value)
                # Use these values to create the review
                Review.objects.create(
                    customer=customer,
                    contractor=contractor,
                    rating=rating,  # Adjust as needed based on your request data
                    comment=request.data.get('comment'),  # Adjust as needed based on your request data
                    profile_image_url=request.data.get('profile_image_url'),  # Adjust as needed based on your request data
                )

                return Response({'message': 'Review created successfully.'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Cannot review until the work order is in progress or complete.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Cannot review a work order without a matching contractor.'}, status=status.HTTP_400_BAD_REQUEST)