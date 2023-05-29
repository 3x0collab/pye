# Generated by Django 4.1.7 on 2023-04-07 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0010_rename_target_task_targets'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='daily_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='minute_time',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='schedule_time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='weekly_day',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='weekly_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('last_run_date', models.DateField(default=django.utils.timezone.now)),
                ('last_run_time', models.TimeField(default=django.utils.timezone.now)),
                ('status', models.CharField(blank=True, default='StandBy', max_length=50, null=True)),
                ('logs', models.TextField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('tasks', models.ManyToManyField(blank=True, null=True, to='customer.task')),
            ],
        ),
    ]