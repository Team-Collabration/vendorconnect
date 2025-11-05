 # chat/views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Message

User = get_user_model()

@login_required
def chat_room(request):
    """
    Render the chat page for the logged-in user.
    """
    return render(request, "chat_room.html", {"user": request.user})

@login_required
def chat_users(request):
    """
    Return a list of users the logged-in user can message
    Vendors see only suppliers, Suppliers see only vendors
    """
    print(f"Chat users request from: {request.user.username} (Type: {request.user.user_type})")
    
    current_user_type = request.user.user_type
    
    # Filter opposite user type
    if current_user_type == 'vendor':
        users = User.objects.filter(user_type='supplier').exclude(id=request.user.id)
        print(f"Found {users.count()} suppliers for vendor")
    elif current_user_type == 'supplier':
        users = User.objects.filter(user_type='vendor').exclude(id=request.user.id)
        print(f"Found {users.count()} vendors for supplier")
    else:
        # Fallback: exclude self
        users = User.objects.exclude(id=request.user.id)
        print(f"User type not set, showing all users: {users.count()}")
    
    # Convert to list of dictionaries
    users_list = []
    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": f"{user.first_name} {user.last_name}".strip() or user.username
        }
        users_list.append(user_data)
        print(f"  - {user.username} ({user.email})")
    
    return JsonResponse({"users": users_list})

@login_required
def chat_history(request, user_id):
    """
    Return JSON of all messages between logged-in user and selected recipient
    """
    print(f"Chat history request: {request.user.username} with user {user_id}")
    
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')
    
    print(f"Found {messages.count()} messages")
    
    # Mark received messages as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    msg_list = [
        {
            "sender": msg.sender.username,
            "sender_id": msg.sender.id,
            "receiver": msg.receiver.username,
            "receiver_id": msg.receiver.id,
            "text": msg.text,
            "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        for msg in messages
    ]
    return JsonResponse({"messages": msg_list})
