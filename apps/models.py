from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    oauth_token = models.CharField(max_length=200)
    oauth_secret = models.CharField(max_length=200)

class Document(models.Model):
    user = models.ForeignKey(User)
    description = models.CharField(max_length=1000, default="")
    is_public = models.BooleanField(default=False)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

    def get_user_documents(user):
        documents = Document.objects.filter(models.Q(user=user) | models.Q(is_public=True))
        return documents

