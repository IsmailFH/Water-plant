from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0018_remove_worker_worker_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driver',
            name='id_number',
            field=models.CharField(max_length=20),
        ),
    ]
