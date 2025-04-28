from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ManagerRequest(models.Model):

    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now=True)
    mail = models.TextField(null=True,blank=True)
    proof = models.FileField(null=True,blank=True,upload_to='proof')

    def __str__(self):
        return str(self.sender)+ ' | ' + str(self.time_sent)