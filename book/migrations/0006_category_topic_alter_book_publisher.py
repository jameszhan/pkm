# Generated by Django 4.1.7 on 2023-09-10 04:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0005_publisher_alias'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='topic',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='publisher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='books', to='book.publisher'),
        ),
    ]