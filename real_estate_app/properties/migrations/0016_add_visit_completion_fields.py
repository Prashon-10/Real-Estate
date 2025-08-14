# Generated manually for visit completion functionality
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0015_remove_propertybooking_agent_completion_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='propertybooking',
            name='visit_completed',
            field=models.BooleanField(default=False, help_text='Whether the visit has been completed'),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='visit_completed_at',
            field=models.DateTimeField(blank=True, help_text='When the visit was completed', null=True),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='visit_completed_by',
            field=models.ForeignKey(blank=True, help_text='Agent who marked the visit as completed', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='completed_visits', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='can_book_after_visit',
            field=models.BooleanField(default=True, help_text='Whether customer can book after completing visit'),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='booking_deadline',
            field=models.DateTimeField(blank=True, help_text='Deadline for booking after visit completion', null=True),
        ),
    ]
