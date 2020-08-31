from __future__ import unicode_literals


VERSION = (0, 1, 1, 'final')


def get_version(version=None):
    if version is None:
        version = VERSION

    assert version[3] in ('alpha', 'beta', 'rc', 'final')

    # Now build the two parts of the version number:
    # main = X.Y.Z
    #  | {a|b|c}N - for alpha, beta and rc releases

    parts = 3
    main = '.'.join('{0}'.format(x) for x in version[:parts])

    sub = ''
    if version[3] != 'final':  # Don't add suffix for final versions.
        mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
        sub = '{}'.format(mapping[version[3]])

    # see http://bugs.python.org/issue11638 - .encode('ascii')
    return '{0}{1}'.format(main, sub)


def remove_(attrs=list()):
    cleanattrs = list()
    for attr in attrs:
        if attr[0] != "_":
            cleanattrs.append(attr)
    return cleanattrs


def ldap_default_settings(exclude=list(), includeauth=True):
    """Convenience function to insert additional variables into the
    parent project settings.
    """
    import sys
    import ldap_settings
    frame = sys._getframe(1)
    global_scope = frame.f_globals
    attrs = list()
    attrs = set(remove_(dir(ldap_settings))) - set(exclude)
    for attr in attrs:
        global_scope[attr] = ldap_settings.__getattribute__(attr)
