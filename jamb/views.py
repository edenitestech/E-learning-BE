# jamb/views.py

from rest_framework import viewsets, permissions, filters
from .models import JAMBSubject, JAMBQuestion, Strategy
from .serializers import JAMBSubjectSerializer, JAMBQuestionSerializer, StrategySerializer

class JAMBSubjectViewSet(viewsets.ModelViewSet):
    queryset         = JAMBSubject.objects.all().order_by("name")
    serializer_class = JAMBSubjectSerializer
    filter_backends   = [filters.SearchFilter]
    search_fields     = ["name", "slug"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticatedOrReadOnly()]

class JAMBQuestionViewSet(viewsets.ModelViewSet):
    queryset         = JAMBQuestion.objects.select_related("subject").all().order_by("subject__name","id")
    serializer_class = JAMBQuestionSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

class StrategyViewSet(viewsets.ModelViewSet):
    queryset          = Strategy.objects.all().order_by("category")
    serializer_class  = StrategySerializer
    filter_backends   = [filters.SearchFilter]
    search_fields     = ["category"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticatedOrReadOnly()]