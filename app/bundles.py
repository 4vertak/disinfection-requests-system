import os

from flask_assets import Bundle

from .functions import recursive_flatten_iterator


def get_bundle(route, tpl, ext, paths, type=False):
    if route and tpl and ext:
        return {
            'instance': Bundle(*paths, output=get_path(route, tpl, ext, type), filters=get_filter(ext)),
            'name': get_filename(route, tpl, ext, type),
            'dir': os.getcwd()
        }


def register_bundle(assets, bundle):
    assets.register(bundle['name'], bundle['instance'])
    return f" Bundle {bundle['name']} registered successfully!"


def register_bundles(assets, bundles):
    for x in recursive_flatten_iterator(bundles):
        for bundle in x:
            register_bundle(assets, bundle)


def get_filename(route, tpl, ext, type):
    if type:
        return f"{route}_{tpl}_{ext}_defer"
    else:
        return f"{route}_{tpl}_{ext}"


def get_path(route, tpl, ext, type):
    if type:
        return f"gen/{route}/{tpl}/defer.{ext}"
    else:
        return f"gen/{route}/{tpl}/main.{ext}"


def get_filter(ext):
    return f"{ext}min"


bundles = {
    "application": {
        "index": {
            "js": [get_bundle('application', 'index', 'js', ['js/app.js', 'js/libs/bootstrap.bundle.min.js'])]
        },
        "all": {
            "css": [get_bundle('application', 'all', 'css', ['css/blocks/table.css', 'css/blocks/dashboard.css'])],
            "js": [get_bundle('application', 'all', 'js', ['js/libs/bootstrap.bundle.min.js', 'js/blocks/js_table.js', 'js/libs/fontawesome.all.min.js', 'js/blocks/js_functions.js', 'js/blocks/js_declensionWordApp.js', 'js/app.js'])]
        },
        "dashboard": {
            "css": [get_bundle('application', 'dashboard', 'css', ['css/blocks/dashboard.css'])],
            "js": [get_bundle('application', 'dashboard', 'js', ['js/libs/bootstrap.bundle.min.js','js/blocks/js_table.js', 'js/libs/fontawesome.all.min.js', 'js/blocks/js_functions.js', 'js/blocks/js_declensionWordApp.js', 'js/app.js', 'js/libs/chart.min.js', 'js/blocks/js_charts.js'])]
        },
        "create": {
            "js": [get_bundle('application', 'create', 'js', ['js/libs/bootstrap.bundle.min.js','js/app.js', 'js/blocks/js_create_update.js'])]
        },
        "update": {
            "js": [get_bundle('application', 'update', 'js', ['js/libs/bootstrap.bundle.min.js','js/app.js', 'js/blocks/js_create_update.js'])]
        },
        "add_entry": {
            "css": [get_bundle('application', 'add_entry', 'css', ['css/blocks/checkbox.css'])],
            "js": [get_bundle('application', 'add_entry', 'js', ['js/libs/bootstrap.bundle.min.js','js/app.js', 'js/blocks/js_functions.js', 'js/blocks/js_add_entry.js'])]
        },
        "admin": {
            "css": [get_bundle('application', 'admin', 'css', ['css/blocks/table.css', 'css/blocks/dashboard.css'])],
            "js": [get_bundle('application', 'admin', 'js', ['js/libs/bootstrap.bundle.min.js','js/blocks/js_table.js', 'js/libs/fontawesome.all.min.js', 'js/blocks/js_functions.js','js/blocks/js_declensionWord.js',  'js/app.js', 'js/libs/chart.min.js', 'js/blocks/js_charts.js'])]
        },
        "users": {
            "css": [get_bundle('application', 'users', 'css', ['css/blocks/table.css', 'css/blocks/dashboard.css'])],
            "js": [get_bundle('application', 'users', 'js', ['js/libs/bootstrap.bundle.min.js','js/blocks/js_table.js', 'js/libs/fontawesome.all.min.js','js/blocks/js_functions.js', 'js/blocks/js_declensionWordUsers.js',  'js/app.js', 'js/blocks/js_for_admin.js'])]
        }
        
        
    },
    "user": {
        "login": {
            "js": [get_bundle('user', 'login', 'js', ['js/libs/bootstrap.bundle.min.js','js/app.js'])]
        },
        "register": {
            "js": [get_bundle('user', 'register', 'js', ['js/libs/bootstrap.bundle.min.js','js/blocks/js_register.js', 'js/app.js'])]
        },
        "update": {
            "js": [get_bundle('user', 'update', 'js', ['js/libs/bootstrap.bundle.min.js','js/blocks/js_update.js', 'js/blocks/js_register.js', 'js/app.js'])]
        }
    }
}
