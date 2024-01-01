
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
            contractor_id = request.data.get('contractor_id')  # Add this line to get the contractor_id from the request data

            # Use the new action to check if the review is allowed
            response = self.can_review_contractor(request)
            can_review = response.data.get('can_review', False)
            work_order_id = response.data.get('work_order_id')

            if not can_review:
                return Response({'message': 'Cannot review this contractor.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the authenticated user
            authenticated_user = RareUser.objects.get(user=request.user.id)

            # Check if the customer has already reviewed the contractor
            existing_review = Review.objects.filter(
                customer=authenticated_user,
                contractor__id=contractor_id
            ).exists()

            if existing_review:
                return Response({'message': 'You have already reviewed this contractor.'}, status=status.HTTP_400_BAD_REQUEST)

            # Use the work_order_id to retrieve the work_order
            work_order = WorkOrder.objects.get(pk=work_order_id)

            # Use these values to create the review
            Review.objects.create(
                customer=authenticated_user,
                contractor=work_order.contractor,
                rating=request.data.get('rating'),
                comment=request.data.get('comment'),
                profile_image_url=request.data.get('profile_image_url'),
            )

            return Response({'message': 'Review created successfully.'}, status=status.HTTP_201_CREATED)
    @action(detail=False, methods=['get'])
    def can_review_contractor(self, request):
        contractor_id = request.query_params.get('contractor_id')
        authenticated_user = RareUser.objects.get(user=request.user.id)

        try:
            work_order = WorkOrder.objects.filter(
                customer=authenticated_user,
                contractor__id=contractor_id,
                status__status__in=['in-progress', 'Complete']
            ).latest('date_posted')

            print("Can review: True")
            return Response({'can_review': True, 'work_order_id': work_order.id})
        except WorkOrder.DoesNotExist:
            print("Can review: False")
            return Response({'can_review': False, 'work_order_id': None})