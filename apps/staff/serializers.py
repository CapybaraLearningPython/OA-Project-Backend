from rest_framework import serializers
from django.core.validators import FileExtensionValidator

class StaffUploadSerializer(serializers.Serializer):
    file = serializers.FileField(
        validators=[FileExtensionValidator(['xls', 'xlsx'])],
        error_messages={'required':'请上传正确格式的文件，仅支持.xls和.xlsx格式！'}
    )