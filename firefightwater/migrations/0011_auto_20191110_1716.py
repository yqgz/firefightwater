# Generated by Django 2.2.4 on 2019-11-10 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firefightwater', '0010_auto_20191102_2337'),
    ]

    operations = [
        migrations.AddField(
            model_name='column',
            name='type',
            field=models.CharField(choices=[('text', 'text'), ('checkbox', 'checkbox'), ('checkbox', 'checkbox')], default='text', max_length=10, verbose_name='类型'),
        ),
        migrations.AddField(
            model_name='column',
            name='width',
            field=models.IntegerField(default=100, verbose_name='列宽度'),
        ),
        migrations.AlterField(
            model_name='column',
            name='aggregate',
            field=models.CharField(blank=True, choices=[('SUM', 'SUM'), ('MAX', 'MAX'), ('AVG', 'AVG')], max_length=10, null=True, verbose_name='合计方式'),
        ),
    ]
