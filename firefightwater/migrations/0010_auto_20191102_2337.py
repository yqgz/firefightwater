# Generated by Django 2.2.4 on 2019-11-02 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firefightwater', '0009_moduletable_have'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='aggregate',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='合计方式'),
        ),
        migrations.AddField(
            model_name='table',
            name='total',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='合计'),
        ),
    ]
