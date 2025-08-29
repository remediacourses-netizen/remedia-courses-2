from django.http import HttpResponse
from google_auth_oauthlib.flow import Flow
import os

def oauth2callback(request):
    code = request.GET.get('code')

    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "project_id": "remedia",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": ["https://remedia.kz/oauth2callback/"],
            }
        },
        scopes=['https://www.googleapis.com/auth/drive.file']
    )

    # 👇 ОБЯЗАТЕЛЬНО прописать redirect_uri
    flow.redirect_uri = "https://remedia.kz/oauth2callback"

    # 👇 меняем код на токен
    flow.fetch_token(code=code)

    credentials = flow.credentials
    refresh_token = credentials.refresh_token

    return HttpResponse(f'✅ Refresh token получен: {refresh_token}')

