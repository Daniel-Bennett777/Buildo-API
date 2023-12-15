from rest_framework import viewsets
from rest_framework.response import Response
from Buildoapi.models import RareUser, WorkOrder
from Buildoapi.views.rareusers import RareUserSerializer
from django.db.models import Q

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = RareUser.objects.filter(is_contractor=True)
    serializer_class = RareUserSerializer
    def list(self, request, *args, **kwargs):
        contractors = self.get_queryset()

        contractor_data = []
        for contractor in contractors:
            work_orders = WorkOrder.objects.filter(Q(contractor=contractor, status__status='in-progress') | Q(contractor=contractor, status__status='Complete'))

            contractor_info = {
                'id': contractor.id,
                'username': contractor.user.username,
                'qualifications': contractor.qualifications,
                'is_reviewable': work_orders.exists(),  # Determine if the "Review" button should be available
            }

            contractor_data.append(contractor_info)

        return Response(contractor_data)