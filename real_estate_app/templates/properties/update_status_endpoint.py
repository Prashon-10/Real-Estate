from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json
from .models import Property

@login_required
@require_POST
def update_property_status(request, pk):
    try:
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in [choice[0] for choice in Property.STATUS_CHOICES]:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        property_obj = Property.objects.get(pk=pk)
        
        # Check if the user is the agent of the property
        if request.user != property_obj.agent:
            return JsonResponse({'success': False, 'message': 'You can only update status of your own listings'})
        
        property_obj.status = status
        property_obj.save()
        
        return JsonResponse({
            'success': True, 
            'message': f'Property status updated to {property_obj.get_status_display()}',
            'status_display': property_obj.get_status_display()
        })
    except Property.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Property not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})