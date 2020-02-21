import bcrypt
from datetime import datetime as dt
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

    @property
    def authorized_users(self):
        return [self.pk]

    @property
    def access_token(self):
        if self._access_token is None:
            if self._access_token_id:
                self._access_token = AccessToken.get_by_id(self.access_token_id)
        return self._access_token

    @access_token.setter
    def access_token(self, token):
        if not isinstance(token, AccessToken):
            raise TypeError

        if token.pk is None:
            raise Exception('Token has not been saved')

        self.access_token_id = token.pk
        self._access_token = token

    @property 
    def refresh_token(self):
        pass

    def is_authorized(self, resource):
        return self.pk in resource.authorized_users

    def check_password(self, password):
        return bcrypt.checkpw(password.encode(), self.hash_password)

    def generate_access_token(self, refresh_token):
        if self.refresh_token == refresh_token:
            access_token = AccessToken()
            access_token.save()
            self.access_token = access_token
            return self.access_token
        return None

    def generate_refresh_token(self, password):
        if self.check_password(password):
            refresh_token = RefreshToken()
            refresh_token.save()
            self.refresh_token = refresh_token
            return refresh_token
        return None


class Token(RedisModel):
    lifetime = None 

    def __init__(self, lifetime=None):
        self.token = secrets.token_urlsafe()
        self.lifetime = lifetime or self.__class__.lifetime
        self.date_created = dt.now()
        self.date_expires = self.date_created + self.lifetime

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.token == other.token 

    def save(self):
        super().save(expire=self.lifetime.total_seconds())

    def is_expired(self):
        return dt.now() > self.date_expires 


class AccessToken(Token):
    lifetime = timedelta(days=1)


class RefreshToken(Token):
    lifetime = timedelta(days=8)


