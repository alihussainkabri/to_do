# Generated by Django 3.0.2 on 2020-04-12 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('to_do_app', '0003_auto_20200411_2316'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reminder_data',
            name='file',
        ),
        migrations.AddField(
            model_name='reminder_data',
            name='status',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AlterField(
            model_name='verification',
            name='date',
            field=models.DateField(auto_now_add=True),
        ),
    ]