from django_auth_ldap.config import (LDAPSearch, GroupOfNamesType,
                                     LDAPSearchUnion)
import ldap
import os


# Obtain LDAP credentials from environment variables.
LDAP_SERVER_URI = os.environ['LDAP_SERVER_URI'] if os.environ.get('LDAP_SERVER_URI', False) else 'ldapserver'
LDAP_ACCESS_DN = os.environ['LDAP_ACCESS_DN'] if os.environ.get('LDAP_ACCESS_DN', False) else 'ldapserverdn'
LDAP_ACCESS_PASSWORD = os.environ['LDAP_ACCESS_PASSWORD'] if os.environ.get('LDAP_ACCESS_PASSWORD', False) else 'ldappassword'
LDAP_SEARCH_SCOPE = os.environ['LDAP_SEARCH_SCOPE'] if os.environ.get('LDAP_SEARCH_SCOPE', False) else 'ldapscope'

# LDAP settings.
AUTH_LDAP_SERVER_URI = LDAP_SERVER_URI
AUTH_LDAP_BIND_DN = LDAP_ACCESS_DN
AUTH_LDAP_BIND_PASSWORD = LDAP_ACCESS_PASSWORD
AUTH_LDAP_ALWAYS_UPDATE_USER = False
AUTH_LDAP_AUTHORIZE_ALL_USERS = True
AUTH_LDAP_FIND_GROUP_PERMS = False
AUTH_LDAP_MIRROR_GROUPS = False
AUTH_LDAP_CACHE_GROUPS = False
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 300
AUTH_LDAP_USER_SEARCH = LDAPSearchUnion(
    LDAPSearch('{}'.format(LDAP_SEARCH_SCOPE),
               ldap.SCOPE_SUBTREE,
               '(sAMAccountName=%(user)s)'),
    LDAPSearch('{}'.format(LDAP_SEARCH_SCOPE),
               ldap.SCOPE_SUBTREE,
               '(mail=%(user)s)'),
)
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    '{}'.format(LDAP_SEARCH_SCOPE),
    ldap.SCOPE_SUBTREE, '(objectClass=group)'
)
AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
}
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType(name_attr='cn')
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail',
}
