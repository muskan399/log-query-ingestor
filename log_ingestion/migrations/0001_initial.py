# Generated by Django 4.2.7 on 2023-11-19 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogEntry',
            fields=[
                ('level', models.CharField(max_length=50)),
                ('message', models.TextField()),
                ('resourceId', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField()),
                ('traceId', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('spanId', models.CharField(max_length=50)),
                ('commit', models.CharField(max_length=50)),
                ('parentResourceId', models.CharField(blank=True, max_length=50, null=True)),
                ('projectId', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'log_data',
            },
        ),
    ]
