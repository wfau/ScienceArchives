from rest_framework import serializers
from rest_framework.reverse import reverse
from queries.models import ExecuteSQL

class ExecuteSQLSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExecuteSQL
        fields = ['id', 'query', 'schema', ]

class ExecuteSQLStatusSerializer(serializers.HyperlinkedModelSerializer):
    result_url = serializers.SerializerMethodField()
    class Meta:
        model = ExecuteSQL
        fields = ['id', 'query', 'created', 'started', 'completed', 'current_status', 'results_error', 'result_url', 'num_rows']
    
    def get_result_url(self, obj):
        if obj.results_file:
            return reverse('api:result-detail', args=[obj.pk], request=self.context.get('request'))
        else:
            return None
