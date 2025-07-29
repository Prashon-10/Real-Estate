from .models import PropertyMessage

def unread_message_count(request):
    """
    Context processor to add unread message count to all templates
    """
    if request.user.is_authenticated and hasattr(request.user, 'is_agent') and request.user.is_agent():
        unread_count = PropertyMessage.objects.filter(
            property__agent=request.user,
            read=False
        ).count()
        return {'unread_message_count': unread_count}
    return {'unread_message_count': 0}
