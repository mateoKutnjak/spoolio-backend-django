
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filament', '0007_spool'),
        ('print_order', '0015_printorder_estimated_price_alter_printorder_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderunit',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderunit',
            name='infill',
        ),
        migrations.RemoveField(
            model_name='orderunit',
            name='material',
        ),
        migrations.AddField(
            model_name='orderunit',
            name='spool',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='filament.spool'),
        ),
    ]
