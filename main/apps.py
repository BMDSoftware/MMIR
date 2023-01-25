from django.apps import AppConfig

from main.algorithmsPlugin import plugin_loader, plugin_register
import json
import sys




class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'



    def ready(self):
        if 'runserver' not in sys.argv:
            return True
        from .models import Algorithms
        with open("main/plugins/plugins_list.json") as file:
            data_plugins = json.load(file)
            # load the plugins
            print("Loading plugins ...")
            plugin_loader.load_plugins(data_plugins["plugins"])
            plugins_names = plugin_register.getAlgNames()
            print("add plugins to the db ...")
            for plugin in plugins_names:

                pg_db = Algorithms.objects.filter(name=plugin)
                if not pg_db:
                    newAlg = Algorithms(name=plugin)
                    newAlg.save()

            print("plugins added")
            # DELETE when is not in the plugin list
            db_Algs = Algorithms.objects.all()
            for db_al in db_Algs:
                if db_al.name not in plugins_names:
                    db_al.delete()

