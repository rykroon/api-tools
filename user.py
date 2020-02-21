import bcrypt
from datetime import datetime, timedelta
import secrets

from models import MongoModel, RedisModel

class User(MongoModel):
    def __init__(self, password):
        self.salt = bcrypt.gensalt()
        self.hash_password = bcrypt.hashpw(password.encode(), self.salt)
        self.access_token_id = None 
        self.refresh_token_id = None
        self._access_token = None
        self._refresh_token = None

    def __getstate__(self):
        self._access_token = None
        self._refresh_token = None
        return self.__dict__

    @property
    def authorized_users(self):
        return [self.pk]

    @property
    def access_token(self):
        if self._access_token is None:
            if self.access_token_id:
                self._access_token = AccessToken.get_by_id(self.access_token_id)
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        if not isinstance(token, AccessToken):
            raise TypeError

        if token.pk is None:
            token.save()

        self.access_token_id = token.pk
        self._access_token = token

    @property 
    def refresh_token(self):
        if self._refresh_token is None:
            if self.refresh_token_id:
                self._refresh_token = RefreshToken.get_by_id(self.refresh_token_id)
        return self._refresh_token

    @refresh_token.setter
    def refresh_token(self, token):
        if not isinstance(token, RefreshToken):
            raise TypeError

        if token.pk is None:
            token.save()

        self.refresh_token_id = token.pk
        self._refresh_token = token

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.hash_password)

    def generate_access_token(self, refresh_token, lifetime=None):
        if self.refresh_token is None:
            return None

        if self.refresh_token == refresh_token:
            if not refresh_token.is_expired():
                self.access_token = AccessToken(lifetime=lifetime)
                return self.access_token
        return None

    def generate_refresh_token(self, password, lifetime=None):
        if self.check_password(password):
            self.refresh_token = RefreshToken(lifetime=lifetime)
            return self.refresh_token
        return None

    def is_authorized(self, resource):
        return self.pk in resource.authorized_users


class Token:

    def __init__(self, user, lifetime):
        """
            :param lifetime: the lifetime of the token
            :type lifetime: timedelta
        """
        self.token = secrets.token_urlsafe()
        self.lifetime = lifetime
        self.date_created = datetime.now()
        self.date_expires = self.date_created + self.lifetime

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.token == other.token 

    

    def is_expired(self):
        return datetime.now() > self.date_expires 


class AccessToken(Token, RedisModel):
    lifetime = timedelta(hours=2)

    def save(self):
        super().save(expire=self.lifetime.total_seconds())


class RefreshToken(Token,):
    lifetime = timedelta(days=21)
