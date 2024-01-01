from rest_framework import viewsets
from rest_framework.response import Response
from Buildoapi.models import RareUser, WorkOrder
from Buildoapi.views.rareusers import RareUserSerializer
from django.db.models import Q

class ContractorViewSet(viewsets.ModelViewSet):
    queryset = RareUser.objects.filter(is_contractor=True)
    serializer_class = RareUserSerializer

    def list(self, request, pk=None, *args, **kwargs):
        current_user = request.user if request.user.is_authenticated else None
        contractors = self.get_queryset()

        # Retrieve all work orders for the current user
        work_orders = WorkOrder.objects.filter(
            Q(customer__user=current_user) | Q(contractor__user=current_user),
            status__status__in=['in-progress', 'Complete']
        )

        contractor_data = []
        for contractor in contractors:
            is_reviewable = self.is_reviewable(current_user, contractor, work_orders)

            contractor_info = {
                'id': contractor.id,
                'username': contractor.user.username,
                'full_name': f'{contractor.user.first_name} {contractor.user.last_name}',
                'qualifications': contractor.qualifications,
                'profile_image_url': contractor.profile_image_url,
                'bio': contractor.bio,
                'created_on': contractor.created_on,
                'state_name': contractor.state_name,
                'county_name': contractor.county_name,
                'is_reviewable': is_reviewable,
            }
            contractor_data.append(contractor_info)

        return Response(contractor_data)

    def is_reviewable(self, current_user, contractor, work_orders):
        # Check if there are any work orders for the current user and contractor
        return work_orders.filter(
            Q(customer__user=current_user, contractor=contractor) |
            Q(contractor__user=current_user, customer=contractor),
        ).exists()