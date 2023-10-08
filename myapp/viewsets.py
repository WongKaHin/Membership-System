from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import History
from .serializers import ArticleSerializer

class ArticleViewSet(viewsets.ModelViewSet):
  queryset = History.objects.all()
  serializer_class = ArticleSerializer
  permission_classes = (AllowAny,)