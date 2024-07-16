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
    customer = RareUserSerializer(many=False, required=False)
    contractor = RareUserSerializer(many=False, required=False)
    status = StatusSerializer(many=False)
    

    class Meta:
        model = WorkOrder
        fields = '__all__'
        extra_kwargs = {
            'profile_image': {'required': False}
        }

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
            try:
                # Extract and validate data from the request
                service_type = request.data.get("service_type")
                state_name = request.data.get("state_name")
                county_name = request.data.get("county_name")
                description = request.data.get("description")
                status_id = request.data.get("status")

                if not (service_type and state_name and county_name and description and status_id):
                    return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

                status_instance = Status.objects.get(id=status_id)
                rare_user = RareUser.objects.get(user=request.user.id)

                profile_image = request.FILES.get('profile_image')
                if not profile_image:
                    return Response({"message": "Profile image is required."}, status=status.HTTP_400_BAD_REQUEST)

                # Create a WorkOrder instance
                work_order = WorkOrder.objects.create(
                    service_type=service_type,
                    state_name=state_name,
                    county_name=county_name,
                    description=description,
                    status=status_instance,
                    customer=rare_user,
                    profile_image=profile_image
                )

                # Serialize the instance
                serializer = WorkOrderSerializer(work_order)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Status.DoesNotExist:
                return Response({"message": "Invalid status ID."}, status=status.HTTP_400_BAD_REQUEST)
            except RareUser.DoesNotExist:
                return Response({"message": "User not found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as ex:
                return Response({"message": str(ex)}, status=status.HTTP_400_BAD_REQUEST)
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
                else:
                    print(serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message": "You are not the author of this Order."}, status=status.HTTP_403_FORBIDDEN)
        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def mark_complete(self, request, pk=None):
        work_order = self.get_object()
        
        # Check if the user making the request is the assigned contractor
        if request.user.id != work_order.contractor.user.id:
            return Response({"message": "You are not authorized to mark this job as complete."}, status=status.HTTP_403_FORBIDDEN)

        # Update the status to 'Complete' (you need to define this status in your models)
        work_order.status = Status.objects.get(status='Complete')
        work_order.save()

        return Response({"message": "Job marked as complete."}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def decommit_work_order(self, request, pk=None):
        try:
            work_order = self.get_object()

            # Check if the user making the request is the assigned contractor
            if request.user.id != work_order.contractor.user.id:
                return Response({"message": "You are not authorized to decommit this job."}, status=status.HTTP_403_FORBIDDEN)

            # Update the status to 'Accepting Responses' (you need to define this status in your models)
            work_order.status = Status.objects.get(status='accepting-responses')
            work_order.contractor = None  # Remove the contractor assignment
            work_order.save()

            serializer = WorkOrderSerializer(work_order, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
        except Status.DoesNotExist:
            return Response({"message": "Status 'accepting-responses' not found."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)