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



class FilesModel(models.Model):
    connector_id = models.CharField(max_length=200,primary_key=True)
    filetype = models.CharField(max_length=50, null=True, blank=True)
    file = models.FileField(upload_to='uploads/')


class Connector(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    description = models.TextField(null=True,blank=True)
    connector_type = models.CharField(max_length=150,null=True,blank=True)
    parameters = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    files = models.ManyToManyField(FilesModel)
    date_created = models.DateField(default=timezone.now)
    time_created = models.TimeField(default=timezone.now)


    def __str__(self):
        return self.name + " : "+ str(self.connector_type)



 
class Transformer(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    transformer_type = models.CharField(max_length=200,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    last_modified = models.DateTimeField(default=timezone.now)
    is_public = models.CharField(max_length=20,null=True,blank=True,default='False')
    views = models.IntegerField(default=0,null=True,blank=True)
    code = models.TextField(null=True,blank=True,default='')

    def __str__(self):
        return   self.name

    def save(self, *args, **kwargs):
        self.views = self.views + 1
        super().save(*args, **kwargs)
 




class Task(models.Model):
    name = models.CharField(max_length=200,null=False,default='')
    description = models.TextField(null=True,blank=True)
    created_by=models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateField(default=timezone.now)
    time_created = models.TimeField(default=timezone.now)  
    source=models.ManyToManyField(Connector,  null=True, blank=True,related_name="connector_source")
    targets=models.ManyToManyField(Connector, null=True, blank=True)
    transformers=models.ManyToManyField(Transformer, null=True, blank=True)

    schedule_time = models.CharField(max_length=100,null=True,blank=True)
    minute_time = models.IntegerField(null=True,blank=True)
    daily_time = models.TimeField(null=True,blank=True)
    sun = models.CharField(max_length=100,null=True,blank=True)
    mon = models.CharField(max_length=100,null=True,blank=True)
    tue = models.CharField(max_length=100,null=True,blank=True)
    wed = models.CharField(max_length=100,null=True,blank=True)
    thu = models.CharField(max_length=100,null=True,blank=True)
    fri = models.CharField(max_length=100,null=True,blank=True)
    sat = models.CharField(max_length=100,null=True,blank=True) 
    weekly_time = models.TimeField(null=True,blank=True)
    status = models.CharField(max_length=50,blank=True,null=True,default='stopped')
    job_id = models.CharField(max_length=50,blank=True,null=True)
    last_run_date = models.DateField(default=timezone.now)
    last_run_time = models.TimeField(default=timezone.now )
    error = models.TextField(null=True,blank=True)

    def save(self, *args, **kwargs):
        # Update last_run_date and last_run_time fields to current date and time
        self.last_run_date = timezone.now().date()
        self.last_run_time = timezone.now().time()
        super().save(*args, **kwargs)
 

    def __str__(self):
        return self.status + " : "+ self.name

    def weekly_day(self):
        return ','.join(day for day in ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] if getattr(self, day))

    def get_transformers(self):
        return ', '.join( [x.description or x.name for x in self.transformers.all()])

    def get_targets(self):
        return ', '.join([ x.description or x.name for x in self.targets.all()])

    def get_sources(self):
        return ', '.join([x.description or x.name for x in self.source.all()])

    weekly_day = property(weekly_day)
    get_transformers = property(get_transformers)
    get_targets = property(get_targets)
    get_sources = property(get_sources)


class Logs(models.Model):
    name = models.CharField(max_length=200,null=False,default='') 
    task = models.CharField(max_length=200,null=False,default='')
    text = models.TextField(null=True,blank=True)

    def __str__(self):
        return self.task + " : "+ self.name

class Running_Jobs(models.Model):
    id = models.CharField(max_length=80,primary_key=True) 
    job = models.TextField(null=False,default='') 
    last_run_date = models.DateField(default=timezone.now)
    last_run_time = models.TimeField(default=timezone.now)

    def __str__(self):
        return self.id + " : "+ self.last_run_date

 


