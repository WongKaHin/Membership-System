from rest_framework import serializers
from .models import History

class ArticleSerializer(serializers.ModelSerializer):
  class Meta:
    model = History
    fields = ['ordid', 'memid', 'cdate', 'gpoint', 'c_amount', 'amount','appname']