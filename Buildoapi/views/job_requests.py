from rest_framework import serializers
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from Buildoapi.models.job_request import JobRequest
from Buildoapi.models.work_order import WorkOrder
from Buildoapi.models.user import RareUser
from Buildoapi.models.request_status import RequestStatus

class JobRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRequest
        fields = '__all__'

class JobRequestViewSet(viewsets.ModelViewSet):
    queryset = JobRequest.objects.all()
    serializer_class = JobRequestSerializer

    @action(detail=False, methods=['post'])
    def create_job_request(self, request, pk=None):
        try:
            
            contractor = RareUser.objects.get(user=request.user.id)

            if contractor.is_contractor is True:
                # Use work_order_id from request data
                work_order_id = request.data.get('work_order')
                work_order = WorkOrder.objects.get(pk=work_order_id)
                job_request = JobRequest.objects.create(
                    contractor=contractor,
                    customer=work_order.customer,
                    work_order=work_order,
                    request_status=RequestStatus.objects.get(id=request.data.get("request_status")),
                    contractor_cellphone=request.data.get('contractor_cellphone')
                )

                serializer = JobRequestSerializer(job_request, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response({"message": "Only contractors can create job requests."}, status=status.HTTP_403_FORBIDDEN)
        except WorkOrder.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def accept_contractor(self, request, pk=None):
        try:
            job_request = JobRequest.objects.get(pk=pk)

            # Check if the user making the request is the assigned customer
            if request.user.id != job_request.customer.user.id:
                return Response({"message": "You are not authorized to accept this job request."}, status=status.HTTP_403_FORBIDDEN)

            # Update the accepted_by_customer field to True
            job_request.accepted_by_customer = True
            job_request.save()

            return Response({"message": "Job request accepted by the customer."}, status=status.HTTP_200_OK)

        except JobRequest.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['post'])
    def cancel_request(self, request, pk=None):
        try:
            job_request = JobRequest.objects.get(pk=pk)

            # Check if the user making the request is the assigned contractor
            if request.user.id != job_request.contractor.user.id:
                return Response({"message": "You are not authorized to cancel this job request."}, status=status.HTTP_403_FORBIDDEN)

            # Cancel the job request
            job_request.delete()

            return Response({"message": "Job request canceled successfully."}, status=status.HTTP_200_OK)

        except JobRequest.DoesNotExist as ex:
            return Response({"message": ex.args[0]}, status=status.HTTP_404_NOT_FOUND)