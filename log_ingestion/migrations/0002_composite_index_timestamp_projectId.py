from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('log_ingestion', '0001_initial'),
        # Add your dependencies here
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE INDEX idx_timestamp_projectId ON log_data (timestamp, projectId);',
            reverse_sql='DROP INDEX idx_timestamp_projectId;',
            state_operations=[],
        ),
    ]
