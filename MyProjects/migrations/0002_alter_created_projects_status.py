# Generated by Django 4.0.3 on 2022-05-02 07:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyProjects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='created_projects',
            name='Status',
            field=models.TextField(default='MY_PROJECT', null=True),
        ),
    ]
