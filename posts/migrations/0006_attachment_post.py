# Generated by Django 4.0.4 on 2022-05-27 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_remove_post_social_networks_delete_socialnetwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='posts.post'),
        ),
    ]
