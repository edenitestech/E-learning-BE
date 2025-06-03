# jamb/views.py

from rest_framework import viewsets, permissions, filters
from .models import JAMBSubject, JAMBQuestion, Strategy
from .serializers import (
    JAMBSubjectSerializer,
    JAMBQuestionSerializer,
    StrategySerializer,
)

class JAMBSubjectViewSet(viewsets.ModelViewSet):
    """
    list/create JAMBSubject, retrieve/update/delete.
    """
    queryset = JAMBSubject.objects.all().order_by("name")
    serializer_class = JAMBSubjectSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "slug"]


class JAMBQuestionViewSet(viewsets.ModelViewSet):
    """
    list/create JAMBQuestion, retrieve/update/delete.
    Only authenticated users may create/update; everyone can read.
    """
    queryset = JAMBQuestion.objects.select_related("subject").all().order_by("subject__name", "id")
    serializer_class = JAMBQuestionSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]


class StrategyViewSet(viewsets.ModelViewSet):
    """
    list/create Strategy, retrieve/update/delete.
    """
    queryset = Strategy.objects.all().order_by("category")
    serializer_class = StrategySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["category"]
