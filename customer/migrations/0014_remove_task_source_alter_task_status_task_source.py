# Generated by Django 4.1.7 on 2023-04-12 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0013_alter_task_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='source',
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(blank=True, default='stop', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='source',
            field=models.ManyToManyField(blank=True, null=True, related_name='connector_source', to='customer.connector'),
        ),
    ]