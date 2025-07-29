from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, Max, Count
from django.utils import timezone
from properties.models import Property
from .models import ChatRoom, ChatMessage
from django.core.paginator import Paginator


@login_required
def agent_chat_overview(request):
    """Agent overview of all properties and their conversations"""
    # Get all properties owned by the agent
    properties = Property.objects.filter(agent=request.user).annotate(
        conversation_count=Count('chatrooms'),
        last_activity=Max('chatrooms__messages__timestamp')
    ).order_by('-last_activity')
    
    # Calculate statistics
    total_properties = properties.count()
    total_conversations = ChatRoom.objects.filter(property__agent=request.user).count()
    unread_count = ChatMessage.objects.filter(
        room__property__agent=request.user,
        read=False
    ).exclude(sender=request.user).count()
    
    # Active today (conversations with messages today)
    today = timezone.now().date()
    active_today = ChatRoom.objects.filter(
        property__agent=request.user,
        messages__timestamp__date=today
    ).distinct().count()
    
    # Add additional data to properties
    for prop in properties:
        prop.has_unread_messages = ChatMessage.objects.filter(
            room__property=prop,
            read=False
        ).exclude(sender=request.user).exists()
    
    context = {
        'properties': properties,
        'total_properties': total_properties,
        'total_conversations': total_conversations,
        'unread_count': unread_count,
        'active_today': active_today,
    }
    return render(request, 'chat/agent_chat_list.html', context)


@login_required
def unread_counts(request):
    """Get unread message counts for agent dashboard"""
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if hasattr(request.user, 'is_agent') and request.user.is_agent():
            # Get unread counts grouped by property and customer
            unread_messages = ChatMessage.objects.filter(
                room__property__agent=request.user,
                read=False
            ).exclude(sender=request.user).values(
                'room__property__id',
                'room__customer__id'
            ).annotate(count=Count('id'))
            
            counts = {}
            for item in unread_messages:
                key = f"{item['room__property__id']}_{item['room__customer__id']}"
                counts[key] = item['count']
            
            return JsonResponse({'success': True, 'counts': counts})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def property_chat(request, property_id):
    """
    Main chat interface for a property between customer and agent
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    # Determine the other participant
    if request.user == property_obj.agent:
        # Agent viewing - show all customer conversations
        chat_rooms = ChatRoom.objects.filter(
            property=property_obj,
            agent=request.user
        ).select_related('customer').annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time')
        
        # If specific customer_id is provided, show that conversation
        customer_id = request.GET.get('customer_id')
        if customer_id:
            try:
                specific_customer = ChatRoom.objects.get(
                    property=property_obj,
                    agent=request.user,
                    customer_id=customer_id
                ).customer
                current_chat = ChatRoom.objects.get(
                    property=property_obj,
                    customer=specific_customer,
                    agent=request.user
                )
                messages_list = current_chat.messages.all().order_by('timestamp')
                
                # Mark messages as read for agent
                unread_messages = messages_list.filter(read=False).exclude(sender=request.user)
                unread_messages.update(read=True)
                
                return render(request, 'chat/agent_chat_detail.html', {
                    'property': property_obj,
                    'chat_rooms': chat_rooms,
                    'current_chat': current_chat,
                    'messages': messages_list,
                    'other_user': specific_customer
                })
            except ChatRoom.DoesNotExist:
                pass
        
        return render(request, 'chat/agent_chat_list.html', {
            'property': property_obj,
            'chat_rooms': chat_rooms
        })
    
    else:
        # Customer viewing - create or get chat room with agent
        chat_room, created = ChatRoom.objects.get_or_create(
            property=property_obj,
            customer=request.user,
            agent=property_obj.agent
        )
        
        messages_list = chat_room.messages.all().order_by('timestamp')
        
        # Mark agent messages as read for customer
        unread_messages = messages_list.filter(read=False).exclude(sender=request.user)
        unread_messages.update(read=True)
        
        return render(request, 'chat/customer_chat.html', {
            'property': property_obj,
            'chat_room': chat_room,
            'messages': messages_list,
            'other_user': property_obj.agent
        })


@login_required
@require_POST
def send_message(request, property_id):
    """
    Send a message in a property chat
    """
    property_obj = get_object_or_404(Property, id=property_id)
    content = request.POST.get('message', '').strip()
    
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'})
        messages.error(request, 'Message cannot be empty')
        return redirect('chat:property_chat', property_id=property_id)
    
    # Determine the chat room
    if request.user == property_obj.agent:
        # Agent sending - need customer_id
        customer_id = request.POST.get('customer_id')
        if not customer_id:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Customer ID required'})
            messages.error(request, 'Customer ID required')
            return redirect('chat:property_chat', property_id=property_id)
        
        chat_room = get_object_or_404(ChatRoom, 
            property=property_obj,
            agent=request.user,
            customer_id=customer_id
        )
    else:
        # Customer sending
        chat_room, created = ChatRoom.objects.get_or_create(
            property=property_obj,
            customer=request.user,
            agent=property_obj.agent
        )
    
    # Create the message
    message = ChatMessage.objects.create(
        room=chat_room,
        sender=request.user,
        content=content
    )
    
    # Update chat room timestamp
    chat_room.save()  # This updates the updated_at field
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_id': message.sender.id,
                'timestamp': message.timestamp.isoformat(),
                'is_mine': message.sender == request.user
            }
        })
    
    # Redirect back to chat
    if request.user == property_obj.agent:
        return redirect('chat:property_chat', property_id=property_id) + f'?customer_id={chat_room.customer.id}'
    else:
        return redirect('chat:property_chat', property_id=property_id)


@login_required
def get_messages(request, property_id):
    """
    Get messages for a property chat (AJAX endpoint)
    """
    property_obj = get_object_or_404(Property, id=property_id)
    
    if request.user == property_obj.agent:
        customer_id = request.GET.get('customer_id')
        if not customer_id:
            return JsonResponse({'success': False, 'error': 'Customer ID required'})
        
        try:
            chat_room = ChatRoom.objects.get(
                property=property_obj,
                agent=request.user,
                customer_id=customer_id
            )
        except ChatRoom.DoesNotExist:
            return JsonResponse({'success': True, 'messages': []})
    else:
        try:
            chat_room = ChatRoom.objects.get(
                property=property_obj,
                customer=request.user,
                agent=property_obj.agent
            )
        except ChatRoom.DoesNotExist:
            return JsonResponse({'success': True, 'messages': []})
    
    messages_list = chat_room.messages.all().order_by('timestamp')
    
    # Mark unread messages as read
    unread_messages = messages_list.filter(read=False).exclude(sender=request.user)
    unread_messages.update(read=True)
    
    messages_data = [{
        'id': msg.id,
        'content': msg.content,
        'sender_name': msg.sender.get_full_name() or msg.sender.username,
        'sender_id': msg.sender.id,
        'timestamp': msg.timestamp.isoformat(),
        'is_mine': msg.sender == request.user,
        'read': msg.read
    } for msg in messages_list]
    
    return JsonResponse({
        'success': True,
        'messages': messages_data
    })


@login_required
def chat_list(request):
    """
    List all chat rooms for the current user
    """
    if request.user.is_agent():
        # Agent - show all chats across all properties
        chat_rooms = ChatRoom.objects.filter(
            agent=request.user
        ).select_related('property', 'customer').annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time')
    else:
        # Customer - show all chats
        chat_rooms = ChatRoom.objects.filter(
            customer=request.user
        ).select_related('property', 'agent').annotate(
            last_message_time=Max('messages__timestamp')
        ).order_by('-last_message_time')
    
    return render(request, 'chat/chat_list.html', {
        'chat_rooms': chat_rooms
    })
