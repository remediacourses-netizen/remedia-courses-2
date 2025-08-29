from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
from django.conf import settings
import os

def oauth2callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "project_id": "remedia",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": ["http://remedia.kz/oauth2callback"],
            }
        },
        scopes=['https://www.googleapis.com/auth/drive.file']
    )

    flow.fetch_token(code=code)

    credentials = flow.credentials
    refresh_token = credentials.refresh_token

    return HttpResponse(f'✅ Refresh token получен: {refresh_token}')
