# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-02 15:29
from __future__ import unicode_literals

from django.db import migrations
from oauth2_provider.settings import oauth2_settings


SCOPES_MAPPING = {
    'internal-front-end': 'data-hub:internal-front-end',
    'mi': 'data-hub:mi',
    'public-omis-front-end': 'data-hub:public-omis-front-end',
}


def update_scopes(apps, schema_editor):
    OAuthApplicationScope = apps.get_model('oauth', 'OAuthApplicationScope')
    AccessToken = apps.get_model(oauth2_settings.ACCESS_TOKEN_MODEL)

    for app_scope in OAuthApplicationScope.objects.all():
        app_scope.scopes = [SCOPES_MAPPING.get(scope, scope) for scope in app_scope.scopes]
        app_scope.save()

    # Note: this does not handle tokens with multiple scopes, however no such tokens were in use
    # pre-SSO
    for old_scope, new_scope in SCOPES_MAPPING.items():
        AccessToken.objects.filter(scope=old_scope).update(scope=new_scope)


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(oauth2_settings.ACCESS_TOKEN_MODEL),
        ('oauth', '0002_add_scope_existing_apps'),
    ]

    operations = [
        migrations.RunPython(update_scopes, migrations.RunPython.noop, elidable=True),
    ]
