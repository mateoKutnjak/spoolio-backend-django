from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

from google.oauth2 import id_token
from google.auth.transport import requests

from allauth.socialaccount.providers.oauth2.views import (
    OAuth2CallbackView,
    OAuth2LoginView,
)

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

class GoogleOAuth2AdapterIdToken(GoogleOAuth2Adapter):
    def complete_login(self, request, app, token, **kwargs):
        idinfo = id_token.verify_oauth2_token(token.token, requests.Request(), app.client_id)
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
        idinfo['id'] = idinfo['sub']
        extra_data = idinfo
        login = self.get_provider() \
            .sociallogin_from_response(request,
                                       extra_data)
        return login

oauth2_login = OAuth2LoginView.adapter_view(GoogleOAuth2AdapterIdToken)
oauth2_callback = OAuth2CallbackView.adapter_view(GoogleOAuth2AdapterIdToken)


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2AdapterIdToken # ! This class used as a FIX (see https://gonzafirewall.medium.com/google-oauth2-and-django-rest-auth-92b0d8f70575)
    client_class = OAuth2Client
