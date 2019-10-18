from __future__ import print_function

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from ...auto_restapi_generator import AutoRESTApiGenerator


class Command(BaseCommand):
    args = "appname"
    help = ("Automaticle generate RESTApi [views, urls] for given app"
            "\n\nExample use: python manage.py app_name"
            "\n\nSee for more info: https://github.com/nsmalimov/auto_restapi_django_plugin")

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('apps_name', nargs='+')

    def handle(self, *args, **options):
        ingredients = self.parse_bake_options(options["apps_name"])
        autoRESTApiGenerator = AutoRESTApiGenerator()
        autoRESTApiGenerator.processing(ingredients)

    def parse_bake_options(self, apps_and_models):
        """
            Parses command line options to determine in which what apps we should create restapi.
        """
        apps_and_models_to_bake = {}
        for app_and_model in apps_and_models:
            app_and_model_names = app_and_model.split(':')
            app_label = app_and_model_names[0]
            app, models = self.get_app_and_models(app_label)
            apps_and_models_to_bake[app_label] = (models, app)
        return apps_and_models_to_bake

    def get_app_and_models(self, app_label):
        """
            Gets the app and models when given app_label
        """
        try:
            app = apps.get_app_config(app_label)
        except:
            raise CommandError("%s is ImproperlyConfigured - did you remember to add %s to settings.INSTALLED_APPS?" %
                               (app_label, app_label))

        models = app.get_models()
        return (app, models)
