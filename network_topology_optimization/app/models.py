from django.db import models

class Query(models.Model):
    class Meta:
        app_label = 'app'  # Явное указание метки приложения
        
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed')
    ]
    
    query_id = models.UUIDField(primary_key=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    original_file1 = models.FileField(upload_to='uploads/')
    original_file2 = models.FileField(upload_to='uploads/')
    stage1_result = models.FileField(upload_to='results/', null=True)
    stage2_result = models.FileField(upload_to='results/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)