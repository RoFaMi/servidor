import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import redirect
from google_auth_oauthlib.flow import Flow


CLIENT_ID = "675374222720-gp05mb27hv32742mbchtte1e6q06ailr.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI = "http://127.0.0.1:5008/chatbot/"

def google_login(request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/userinfo.profile"],
    )
    flow.redirect_uri = REDIRECT_URI
    
    print("Redirect URI en la solicitud:", request.build_absolute_uri())
    authorization_url, _ = flow.authorization_url(prompt='consent')
    print("URL de autorización generada:", authorization_url)
    return redirect(authorization_url)

def google_callback(request):
    # Verificar si hay 'state' y 'code' en los parámetros de la solicitud
    state = request.GET.get('state')
    code = request.GET.get('code')

    if not state or not code:
        # Si no hay state o code, redirigir al inicio o a otro lugar
        return JsonResponse({"error": "Missing authorization parameters"}, status=400)  # Ajusta esto según tus necesidades

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uris": [REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        },
        scopes=["https://www.googleapis.com/auth/userinfo.profile"],
    )
    flow.redirect_uri = REDIRECT_URI

    try:
        # Procesar el código recibido desde Google
        flow.fetch_token(authorization_response=request.build_absolute_uri())
        credentials = flow.credentials

        # Obtener información del usuario desde la API de Google
        response = requests.get(
            "https://people.googleapis.com/v1/people/me?personFields=names",
            headers={"Authorization": f"Bearer {credentials.token}"},
        )
        user_data = response.json()
        user_name = user_data.get("names", [{}])[0].get("displayName", "Usuario")

        # Aquí puedes guardar la sesión del usuario o redirigir al dashboard
        return JsonResponse({"message": f"Hola, {user_name}! ¿En qué puedo ayudarte hoy?"})
    except Exception as e:
        # Manejar errores de autenticación
        return JsonResponse({"error": f"Error al procesar la autenticación: {str(e)}"})


def chat_view(request):
    return render(request, 'chatbot/chat.html')

@csrf_exempt
def send_notification(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get("message")
        time = data.get("time")

        # Enviar mensaje a través de WebSocket
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications",  # Grupo de WebSocket
            {
                "type": "notify",
                "message": message,
                "time": time,
            }
        )
        return JsonResponse({"status": "success", "message": "Notificación enviada correctamente"})
    return JsonResponse({"status": "error", "message": "Método no permitido"}, status=405)
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        user_message = request.POST.get('message')
        rasa_response = requests.post('http://localhost:5005/webhooks/rest/webhook', json={"sender": "user", "message": user_message})
        
        bot_response = rasa_response.json()
        if len(bot_response) > 0:
            return JsonResponse({'response': bot_response[0]['text']})
        else:
            return JsonResponse({'response': 'Lo siento, no pude obtener una respuesta.'})

    return JsonResponse({'response': 'Método no permitido'}, status=405)
