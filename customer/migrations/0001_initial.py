# Generated by Django 3.0.5 on 2023-03-06 12:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_pic', models.ImageField(blank=True, null=True, upload_to='profile_pic/Customer/')),
                ('address', models.CharField(max_length=40)),
                ('mobile', models.CharField(max_length=20)),
                ('email', models.CharField(default='', max_length=100)),
                ('profession', models.CharField(default='', max_length=100)),
                ('rate', models.FloatField(default=30)),
                ('hrs', models.IntegerField(default=40)),
                ('email_notifications', models.BooleanField(default=False)),
                ('sms_notifications', models.BooleanField(default=False)),
                ('call_notifications', models.BooleanField(default=False)),
                ('whatsapp_notifications', models.BooleanField(default=False)),
                ('fb', models.CharField(default='', max_length=100)),
                ('ig', models.CharField(default='', max_length=100)),
                ('twitter', models.CharField(default='', max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
