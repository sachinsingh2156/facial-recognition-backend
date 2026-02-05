# Generated manually for adding image_hash field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image_hash',
            field=models.CharField(blank=True, db_index=True, max_length=64, null=True),
        ),
    ]


