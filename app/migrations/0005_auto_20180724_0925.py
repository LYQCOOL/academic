# Generated by Django 2.0.2 on 2018-07-24 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20180724_0844'),
    ]

    operations = [
        migrations.RenameField(
            model_name='relation',
            old_name='l_name',
            new_name='l_name_r',
        ),
        migrations.AddField(
            model_name='relation',
            name='l_name_exp',
            field=models.CharField(default=1, max_length=500, verbose_name='Description'),
            preserve_default=False,
        ),
    ]
