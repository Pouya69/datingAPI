# Generated by Django 3.0.5 on 2021-03-25 04:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0024_delete_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verifylink',
            name='user',
        ),
        migrations.DeleteModel(
            name='MyUser',
        ),
        migrations.DeleteModel(
            name='VerifyLink',
        ),
    ]
