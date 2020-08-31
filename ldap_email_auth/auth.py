from django.contrib.auth import get_user_model
from django_auth_ldap.backend import LDAPBackend


User = get_user_model()


class ADLDAPBackend(LDAPBackend):
    """Override the normal get_or_create_user function to enforce
    use of the Active Directory account logon name field ``sAMAccountName``.
    Also sets the ``is_staff`` attribute to True by default.
    """
    def get_or_create_user(self, username, ldap_user):
        username = ldap_user.attrs['sAMAccountName'][0].lower()
        user, created = super(ADLDAPBackend, self).get_or_create_user(
            username, ldap_user)
        user.is_staff = True
        user.save()
        return user, created


class EmailBackend(object):
    """
    An authentication backend that will authenticate a user against Active
    Directory LDAP if it can't find an existing user entry in the database,
    and will also allow users to login with their email address instead of
    their username (if required).
    """
    def authenticate(self, username=None, password=None):
        """
        Attempt to authenticate a particular user. The username field is taken
        to be an email address and checked against LDAP if the user cannot
        be found.

        Always returns an instance of `django.contrib.auth.models.User` on
        success, otherwise returns None.
        """
        if password is None:
            return None
        try:
            user = User.objects.get(email__iexact=username)
            if user.check_password(password):
                return user
            else:
                try:
                    ldapauth = ADLDAPBackend()
                    return ldapauth.authenticate(username=user.username,
                                                 password=password)
                except:
                    return None
        except User.DoesNotExist:
            try:
                ldapauth = ADLDAPBackend()
                user = ldapauth.authenticate(username=username,
                                             password=password)
                if user is None:
                    return None

                first_name = user.first_name
                last_name = user.last_name
                email = user.email

                if email:
                    if User.objects.filter(email__iexact=email).count() > 1:
                        user.delete()
                    user = User.objects.get(email__iexact=email)
                    user.first_name, user.last_name = first_name, last_name
                    user.save()
                else:
                    user = User.objects.get(username=username)
                    user.first_name, user.last_name = first_name, last_name
                    user.save()
                return user
            except:
                return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
