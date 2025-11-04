from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from openai import OpenAI, OpenAIError

# Use environment variable in production for safety:
# import os
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = OpenAI(api_key="your_open_ai_key")  # 🔒 Replace with your actual API key

@csrf_exempt
def chat_with_ai(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method. Use POST."}, status=400)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        user_type = data.get("user_type", "user").strip()

        if not user_message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        system_prompt = (
            f"You are an AI assistant for a vendor-supplier platform. "
            f"Help {user_type}s politely and clearly."
        )

        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = completion.choices[0].message.content
            return JsonResponse({"reply": reply})

        except OpenAIError as e:
            # Handle API-specific errors
            print("OpenAI API error:", str(e))
            return JsonResponse({"error": "OpenAI API error: " + str(e)}, status=500)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request."}, status=400)
    except Exception as e:
        # Catch-all for other unexpected errors
        print("Unexpected error in chat_with_ai:", str(e))
        return JsonResponse({"error": "Unexpected server error: " + str(e)}, status=500)
