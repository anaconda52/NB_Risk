# Generated by Django 4.1.5 on 2023-04-21 01:36

from django.db import migrations, models
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0084_staging'),
        ('nb_risk', '0002_vulnerability_cvssaccesscomplexity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Control',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('category', models.CharField(default='Preventive', max_length=100)),
                ('risk', models.ManyToManyField(blank=True, to='nb_risk.risk')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
