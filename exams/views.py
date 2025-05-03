# exams/views.py

from rest_framework import viewsets, permissions
from .models import PastQuestion
from .serializers import PastQuestionSerializer

class PastQuestionViewSet(viewsets.ModelViewSet):
    queryset = PastQuestion.objects.all().order_by("-year")
    serializer_class = PastQuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["exam_type", "year", "subject"]
    search_fields    = ["subject"]

