from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response
from Buildoapi.models.work_order import WorkOrder
from Buildoapi.models.status import Status
from Buildoapi.models.user import RareUser
from django.utils import timezone
from Buildoapi.views.rareusers import RareUserSerializer
class IsContractor(permissions.BasePermission):
    """
    Custom permission to only allow contractors to perform certain actions.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user is a contractor
        return request.user.rareuser.is_contractor
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
    @action(detail=False, methods=['get'])
    def my_buildos(self, request):
        try:
        # Check if the user is a contractor
            contractor = RareUser.objects.get(user=request.user.id)

            if contractor.is_contractor == True:
                # Contractor's MyBuildos section: Show only accepted work orders
                accepted_work_orders = WorkOrder.objects.filter(contractor=contractor).order_by('-date_posted')

                for work_order in accepted_work_orders:
                    work_order.date_posted = work_order.date_posted.strftime("%m-%d-%Y")

                serializer = WorkOrderSerializer(accepted_work_orders, many=True, context={'request': request})
                return Response(serializer.data)

            return Response({"message": "Only contractors can view MyBuildos."}, status=status.HTTP_403_FORBIDDEN)

        except RareUser.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)

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
                "status": Status.objects.get(id=request.data.get("status"))
                # Add other fields as needed
            }

            rare_user = RareUser.objects.get(user=request.user.id)
            data["customer"] = rare_user  # Assign the RareUser instance directly

            # Create a WorkOrder instance
            work_order = WorkOrder.objects.create(**data)

            # Serialize the instance
            serializer = WorkOrderSerializer(work_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response({"message": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
    def destroy(self,request, pk=None):
        """Handle DELETE requests for a single post

        Returns:
            Response -- empty response body
        """
        try:
            work_order = WorkOrder.objects.get(pk=pk)
            if work_order.customer.user_id == request.user.id:
                work_order.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "You are not the author of this post."}, status=status.HTTP_403_FORBIDDEN)
        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Exception as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    def update(self,request, pk=None):
        """Handle PUT requests for a single post

        Returns:
            Response -- JSON serialized object
        """
        try:
            work_order = WorkOrder.objects.get(pk=pk)

            if work_order.customer.user_id == request.user.id:
                serializer = WorkOrderSerializer(data=request.data, partial=True)
                if serializer.is_valid():

                    work_order.status = Status.objects.get(pk=request.data["status"]["id"])
                    work_order.service_type = serializer.validated_data["service_type"]
                    work_order.state_name = serializer.validated_data["state_name"]
                    work_order.county_name = serializer.validated_data["county_name"]
                    work_order.description = serializer.validated_data["description"]
                    work_order.profile_image_url = serializer.validated_data["profile_image_url"]
                    # Save the changes to the work_order instance
                    work_order.save()
                    serializer = WorkOrderSerializer(work_order, context={"request": request})
                    return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "You are not the author of this Order."}, status=status.HTTP_403_FORBIDDEN)
        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['post'])
    @permission_classes([IsContractor])
    def accept_job(self, request, pk=None):
        try:
            work_order = WorkOrder.objects.get(pk=pk)
            contractor = RareUser.objects.get(user=request.user.id)

            if contractor.is_contractor is True:  # Ensure the job is not already accepted
                work_order.contractor = contractor
                in_progress_status = Status.objects.get(status='in-progress') # Update the status
                work_order.status = in_progress_status
                work_order.save()

                serializer = WorkOrderSerializer(work_order, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response({"message": "Only contractors can accept jobs."}, status=status.HTTP_403_FORBIDDEN)
        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Status.DoesNotExist:
            return Response({"message": "Status 'accepting-responses' not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
