# Generated by Django 2.2.28 on 2022-05-06 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyProjects', '0002_alter_created_projects_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='created_projects',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]