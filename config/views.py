from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow

def oauth2callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/drive.file'],
        redirect_uri='http://127.0.0.1:8000/oauth2callback'
    )
    flow.fetch_token(code=code)

    credentials = flow.credentials
    refresh_token = credentials.refresh_token

    # Сохрани токен где нужно, например в ENV или файл
    return HttpResponse(f'✅ Refresh token получен: {refresh_token}')