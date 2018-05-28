import os
import pathlib

from lektor.pluginsystem import Plugin
from webassets import Environment, Bundle


webasset_env = Environment(
    directory='assets/static',
    url='/static',
)


def get_bundle_for(ext, filters=None):
    dirname = pathlib.Path('assets/static') / f'_{ext}'
    files = [
        str(f).replace('assets/static/', '')
        for f in dirname.rglob(f'**/*.{ext}')
    ]
    return Bundle(
        *files,
        filters=filters,
        output=f'css/pycascades.{ext}'
    )


class JadeTemplatePlugin(Plugin):
    name = "Jade Template Plugin"
    description = "Add Jade support to Jinja2 templates"

    def on_setup_env(self, **extra):
        css_bundle = get_bundle_for('css', filters='cssmin')
        #js_bundle = get_bundle_for('js', filters='uglifyjs')

        webasset_env.register('css_bundle', css_bundle)

        webasset_env.register('js_bundle', Bundle(
            "_js/misc/modernizr.js",
            "_js/angular/angular.js",
            "_js/angular/angular-animate.js",
            "_js/misc/angular-scroll.js",
            "_js/misc/angular-parallax.js",
            "_js/headroom/headroom.js",
            "_js/misc/instafeed.js",
            "_js/misc/ff.imghelpers.js",
            "_js/pycascades/pycascades.js",
            filters='jsmin',
            output="js/pycascades.js",
        ))

        self.env.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
        self.env.jinja_env.globals.update(
            CSS_URL=webasset_env['css_bundle'].urls()[0],
            JS_URL=webasset_env['js_bundle'].urls()[0],
        )
