import os
import pathlib
from itertools import chain

from lektor.pluginsystem import Plugin
from webassets import Environment, Bundle

from lektor.db import Page
from lektor import build_programs as bp


webasset_env = Environment(
    directory='assets/static',
    url='/static',
)


@bp.buildprogram(Page)
class PageBuildProgram(bp.PageBuildProgram):

    def iter_child_sources(self):
        p_config = self.source.datamodel.pagination_config
        pagination_enabled = p_config.enabled
        child_sources = []

        # So this requires a bit of explanation:
        #
        # the basic logic is that if we have pagination enabled then we
        # need to consider two cases:
        #
        # 1. our build program has page_num = None which means that we
        #    are not yet pointing to a page.  In that case we want to
        #    iter over all children which will yield the pages.
        # 2. we are pointing to a page, then our child sources are the
        #    items that are shown on that page.
        #
        # In addition, attachments and pages excluded from pagination are
        # linked to the page with page_num = None.
        #
        # If pagination is disabled, all children and attachments are linked
        # to this page.
        all_children = self.source.children.include_hidden(True).include_undiscoverable(True)
        if pagination_enabled:
            if self.source.page_num is None:
                child_sources.append(self._iter_paginated_children())
                pq = p_config.get_pagination_query(self.source)
                child_sources.append(set(all_children) - set(pq))
                child_sources.append(self.source.attachments)
            else:
                child_sources.append(self.source.pagination.items)
        else:
            child_sources.append(all_children)
            child_sources.append(self.source.attachments)

        return chain(*child_sources)


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

        webasset_env.register('css_bundle', Bundle(
            "_css/skeleton/normalize.css",
            "_css/skeleton/skeleton.css",
            "_css/misc/ff.common.css",
            "_css/pycascades/pycascades.css",
            "_css/pycascades/pycascades.tito.css",
            "_css/pycascades/pycascades.content.css",
            "_css/pycascades/pycascades.home.css",
            "_css/pycascades/pycascades.news.css",
            "_css/pycascades/pycascades.about.css",
            "_css/pycascades/pycascades.venue.css",
            "_css/pycascades/pycascades.tickets.css",
            "_css/pycascades/pycascades.speakers.css",
            "_css/pycascades/pycascades.sponsors.css",
            "_css/pycascades/pycascades.talks.css",
            filters = 'cssmin',
            output = "css/pycascades.css",
        ))

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
