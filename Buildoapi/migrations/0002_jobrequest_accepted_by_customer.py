# Generated by Django 4.2.8 on 2024-01-20 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Buildoapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobrequest',
            name='accepted_by_customer',
            field=models.BooleanField(default=False),
        ),
    ]
