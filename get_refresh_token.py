# get_refresh_token.py

from google_auth_oauthlib.flow import Flow
# 1. Укажите путь к вашему client_secret.json
CLIENT_SECRETS_FILE = 'client_secret.json'

# 2. Укажите нужные разрешения
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def main():
    flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/drive.file'],
    redirect_uri='http://127.0.0.1:8000/oauth2callback'  # точно так же, как в Google Cloud
)

    # 3. Получите URL для авторизации
    auth_url, _ = flow.authorization_url(prompt='consent')
    print(auth_url)
    
    print('1. Пожалуйста, перейдите по этой ссылке:')
    print(auth_url)
    print('\n2. Авторизуйтесь под вашим аккаунтом Google')
    print('3. Скопируйте полученный код и вставьте ниже')
    
    # 4. Вставьте полученный код
    code = input('Введите код авторизации: ')
    
    # 5. Получите токены
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    print('\n✅ Успешно! Ваш refresh token:')
    print(credentials.refresh_token)
    print('\n⚠️ Сохраните этот токен в безопасном месте!')

if __name__ == '__main__':
    main()