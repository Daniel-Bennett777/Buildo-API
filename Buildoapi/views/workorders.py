from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Buildoapi.models.work_order import WorkOrder
from Buildoapi.models.status import Status
from Buildoapi.models.user import RareUser
from django.utils import timezone
from Buildoapi.views.rareusers import RareUserSerializer

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    customer = RareUserSerializer(many=False)
    contractor = RareUserSerializer(many=False, required=False)
    status = StatusSerializer(many=False)

    class Meta:
        model = WorkOrder
        fields = '__all__'

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer

    def list(self, request):
        # get query parameters from request for specific user
        customer = self.request.query_params.get('customer', None)

        if customer is not None and customer == "current":
            work_orders = WorkOrder.objects.filter(customer__user=request.auth.user).order_by('-date_posted')
        else:
            # otherwise get all posts & filter by approved and dates in the past
            work_orders = WorkOrder.objects.filter(date_posted__lt=timezone.now()).order_by('-date_posted')
        for work_order in work_orders:
            work_order.date_posted = work_order.date_posted.strftime("%m-%d-%Y")

        serializer = WorkOrderSerializer(work_orders, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            work_order = WorkOrder.objects.get(pk=pk)
            serializer = WorkOrderSerializer(work_order, context={'request': request})
            return Response(serializer.data)
        except WorkOrder.DoesNotExist:
            return Response({"message": "Work order not found"}, status=status.HTTP_404_NOT_FOUND)
 
    def create(self, request):
        """Handle POST operations

        Returns
            Response -- JSON serialized work order instance
        """
        try:
            # Extract data from the request
            data = {
                "service_type": request.data.get("service_type"),
                "state_name": request.data.get("state_name"),
                "county_name": request.data.get("county_name"),
                "description": request.data.get("description"),
                "profile_image_url": request.data.get("profile_image_url"),
                # Add other fields as needed
            }

            rare_user = RareUser.objects.get(user=request.user.id)
            data["customer"] = rare_user  # Assign the RareUser instance directly

            # Set the status information
            status_instance = Status.objects.get(id=request.data.get("status"))
            data["status"] = status_instance  # Assign the Status instance directly

            # Create a WorkOrder instance
            work_order = WorkOrder.objects.create(**data)

            # Serialize the instance
            serializer = WorkOrderSerializer(work_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_400_BAD_REQUEST)