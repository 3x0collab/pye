# Generated by Django 4.1.7 on 2023-03-31 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0008_connector_created_by_connector_date_created_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='target',
        ),
        migrations.AddField(
            model_name='task',
            name='target',
            field=models.ManyToManyField(blank=True, null=True, to='customer.connector'),
        ),
    ]