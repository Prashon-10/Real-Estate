# Generated manually for dual confirmation system

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0016_add_visit_completion_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertybooking',
            name='agent_confirmed_completion',
            field=models.BooleanField(default=False, help_text='Whether the agent has confirmed the visit completion'),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='customer_confirmed_completion',
            field=models.BooleanField(default=False, help_text='Whether the customer has confirmed the visit completion'),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='agent_confirmation_at',
            field=models.DateTimeField(blank=True, help_text='When the agent confirmed the visit completion', null=True),
        ),
        migrations.AddField(
            model_name='propertybooking',
            name='customer_confirmation_at',
            field=models.DateTimeField(blank=True, help_text='When the customer confirmed the visit completion', null=True),
        ),
    ]
