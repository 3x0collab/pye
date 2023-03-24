# Generated by Django 4.1.7 on 2023-03-23 17:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0006_alter_transformer_created_by'),
    ]

    operations = [
        migrations.CreateModel(
            name='Connector',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('connector_type', models.CharField(blank=True, max_length=150, null=True)),
                ('parameters', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_created', models.DateField(default=django.utils.timezone.now)),
                ('time_created', models.TimeField(default=django.utils.timezone.now)),
                ('last_run', models.DateTimeField(default=django.utils.timezone.now)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connector_source', to='customer.connector')),
                ('target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='connector_target', to='customer.connector')),
                ('transformers', models.ManyToManyField(blank=True, null=True, to='customer.transformer')),
            ],
        ),
    ]