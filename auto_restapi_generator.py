from __future__ import print_function

import os
import re

from django.template.loader import get_template
from django.utils.six import iteritems


class AutoRESTApiGenerator(object):
    def processing(self, apps_and_models):
        """
            Iterates a dictionary of apps and models and creates all the necessary files to get up and running quickly.
        """
        for app_label, models_app in iteritems(apps_and_models):
            models, app = models_app
            models = list(models)
            model_names = [model.__name__ for model in models]
            self.create_directories(app)
            self.create_init_files(app, model_names, models)
            for model in models:
                model_attributes = self.model_attributes(app, model)
                self.create_files_from_templates(model_attributes)

    def create_directories(self, app):
        """
            If not already there, adds a directory for views and urls.
        """
        for folder_name in ["views", "urls"]:
            directory_path = "%s/%s" % (app.path, folder_name)
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)

    def create_init_files(self, app, model_names, models):
        """
            If not already there, creates a new init file in views and urls directory.  Init file imports from all
            of the files within the directory.
        """
        model_name_slugs = ["%s" % (self.camel_to_slug(model_name)) for model_name in model_names]
        model_names_dict = {self.camel_to_slug(model.__name__): self.camel_to_slug(self.model_name_plural(model)) for
                            model in models}
        for folder_name in ["views", "urls"]:
            file_path = "%s/%s/__init__.py" % (app.path, folder_name)
            template_path = "__init__%s" % folder_name
            self.create_file_from_template(file_path, template_path, {"app_label": app.label,
                                                                      "model_name_slugs": model_name_slugs,
                                                                      "model_names_dict": model_names_dict
                                                                      })

    def model_attributes(self, app, model):
        """
            Creates a dictionary of model attributes that will be used in the templates.
        """
        model_name = model.__name__
        return {
            'app_path': app.path,
            'app_label': app.label,
            'model_name': model_name,
            'model_name_slug': self.camel_to_slug(model_name),
        }

    def create_files_from_templates(self, model_attributes):
        """
            Determines the correct path to put each file and then calls create file method.
        """
        for folder_name in ["views", "urls"]:
            end_filename = folder_name
            if folder_name == "views":
                end_filename = folder_name[:-1]
            file_path = "%s/%s/%s_%s.py" % (model_attributes['app_path'],
                                            folder_name,
                                            model_attributes['model_name_slug'],
                                            end_filename)
            template_path = "%s" % (folder_name)
            self.create_file_from_template(file_path, template_path, model_attributes)

    def create_file_from_template(self, file_path, template_path, context_variables):
        """
            Takes template file and context variables and uses django's render method to create new file.
        """
        if os.path.exists(file_path):
            print("\033[91m" + file_path + " already exists.  Skipping." + "\033[0m")
            return
        with open(file_path, 'w') as new_file:
            new_file.write(get_template(template_path).render(context_variables))
            print("\033[92m" + "successfully create: " + file_path + "\033[0m")

    def camel_to_slug(self, name):
        """
            Helper method to convert camel case string (PumpernickelBread) to slug string (pumpernickel_bread)
        """
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name).title().replace(" ", "").replace("_", "")
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        slug = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
        return slug

    def model_name_plural(self, model):
        """
            Gets the pluralized version of a model.  Simply adds an 's' to model name if verbose_name_plural isn't set.
        """
        if isinstance(model._meta.verbose_name_plural, str):
            return model._meta.verbose_name_plural
        res_s = "%ss" % model.__name__
        if 'ys' == res_s[-2:]:
            res_s = res_s[:-2] + 'ies'

        return res_s
