# Generated by Django 3.2.6 on 2021-08-10 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wallet', '0002_auto_20210810_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topuphistory',
            name='verified',
        ),
        migrations.AddField(
            model_name='topuphistory',
            name='status',
            field=models.CharField(choices=[('PENDING', 'PENDING'), ('VERIFIED', 'VERIFIED'), ('REJECTED', 'REJECTED')], default='PENDING', max_length=25, verbose_name='Top Up Status'),
        ),
    ]
