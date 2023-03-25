from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    profile_pic= models.ImageField(upload_to='profile_pic/Customer/',null=True,blank=True)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=False)
    email = models.CharField(max_length=100,null=False,default='')
    profession = models.CharField(max_length=100,null=False,default='')
    rate = models.FloatField(default=30,null=False)
    hrs = models.IntegerField(default=40,null=False)
    email_notifications = models.BooleanField(default=False)
    sms_notifications = models.BooleanField(default=False)
    call_notifications = models.BooleanField(default=False)
    whatsapp_notifications = models.BooleanField(default=False)
    fb = models.CharField(max_length=100,null=False,default='')
    ig = models.CharField(max_length=100,null=False,default='')
    twitter = models.CharField(max_length=100,null=False,default='')
   
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_instance(self):
        return self
    def __str__(self):
        return self.user.first_name




class Connector(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    description = models.TextField(null=True,blank=True)
    connector_type = models.CharField(max_length=150,null=True,blank=True)
    parameters = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateField(default=timezone.now)
    time_created = models.TimeField(default=timezone.now)


    def __str__(self):
        return self.name + " : "+ self.connector_type




 
class Transformer(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    description = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(default=timezone.now)
    is_public = models.CharField(max_length=20,null=True,blank=True,default='False')
    views = models.IntegerField(default=0,null=True,blank=True)
    code = models.TextField(null=True,blank=True,default='')

    def __str__(self):
        return self.created_by.first_name + " : "+ self.name

    def save(self, *args, **kwargs):
        self.views = self.views + 1
        super().save(*args, **kwargs)
 




class Task(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    description = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateField(default=timezone.now)
    time_created = models.TimeField(default=timezone.now)
    last_run = models.DateTimeField(default=timezone.now)  
    source=models.ForeignKey(Connector, on_delete=models.CASCADE, null=True, blank=True,related_name="connector_source")
    target=models.ForeignKey(Connector, on_delete=models.CASCADE, null=True, blank=True,related_name="connector_target")
    transformers=models.ManyToManyField(Transformer, null=True, blank=True)

    def __str__(self):
        return self.created_by.first_name + " : "+ self.name

 



