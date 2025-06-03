# jamb/views.py

import random
from rest_framework import viewsets
from django.shortcuts import get_object_or_404

from .models import JAMBSubject, JAMBQuestion, Strategy
from .serializers import (
    JAMBSubjectSerializer,
    JAMBQuestionSerializer,
    StrategySerializer,
)


class JAMBSubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/jamb/subjects/
    GET /api/jamb/subjects/{slug}/
    """
    queryset = JAMBSubject.objects.all()
    serializer_class = JAMBSubjectSerializer
    lookup_field = "slug"  # retrieve by slug instead of numeric ID


class JAMBQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/jamb/questions/?subject=<slug>&count=<n>
    GET /api/jamb/questions/{pk}/
    """
    queryset = JAMBQuestion.objects.all()
    serializer_class = JAMBQuestionSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        subject_slug = self.request.query_params.get("subject", None)

        if subject_slug:
            subject = get_object_or_404(JAMBSubject, slug=subject_slug)
            qs = qs.filter(subject=subject)

            # if a ?count=<n> parameter is given, return a random subset
            count_param = self.request.query_params.get("count", None)
            try:
                count = int(count_param) if count_param is not None else None
            except ValueError:
                count = None

            if count:
                all_qs = list(qs)
                random.shuffle(all_qs)
                return all_qs[:count]

        return qs


class StrategyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/jamb/strategies/
    GET /api/jamb/strategies/{pk}/
    """
    queryset = Strategy.objects.all()
    serializer_class = StrategySerializer
