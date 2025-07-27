
from django.db import models
from django.contrib.auth.models import User

class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_url = models.URLField(blank=True, null=True)  # GCS URL
    video_url = models.URLField(blank=True, null=True)
    raw_text = models.TextField(blank=True, null=True)
    data_json = models.JSONField(blank=True, null=True)  # Extracted by Gemini
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WalletPass(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pass_type = models.CharField(max_length=50)  # e.g. 'receipt', 'shopping_list', 'insight'
    pass_id = models.CharField(max_length=128)
    pass_url = models.URLField()
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    response_json = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
