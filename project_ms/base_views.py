from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from permissions.utils import has_model_permission


class ProtectedModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)

        action_map = {
            "GET": "view",
            "POST": "add",
            "PUT": "change",
            "PATCH": "change",
            "DELETE": "delete",
        }

        action = action_map.get(request.method)
        model = self.get_queryset().model

        if not has_model_permission(request.user, model, action):
            raise PermissionDenied("Permission denied.")
        
    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
