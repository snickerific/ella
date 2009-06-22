
from south.db import db
from django.db import models

from ella.hacks import south

from ella.galleries.models import *

from ella.core.migrations.base.base_0002 import BasePublishableDataMigration, BasePublishableDataPlugin
from ella.core.migrations.base.base_0002 import alter_foreignkey_to_int, migrate_foreignkey


class Migration(BasePublishableDataMigration):
    models = dict.copy(BasePublishableDataMigration.models)
    models.update(
        {
            'galleries.gallery': {
                'Meta': {'_bases': ['ella.core.models.publishable.Publishable']},
                'content': ('models.TextField', ["_('Content')"], {'blank': 'True'}),
                'created': ('models.DateTimeField', ["_('Created')"], {'default': 'datetime.now', 'editable': 'False'}),
                'publishable_ptr': ('models.OneToOneField', ["orm['core.Publishable']"], {})
            },
        }
    )

class Plugin(BasePublishableDataPlugin):
    migration = Migration

    app_label = 'galleries'
    model = 'gallery'
    table = '%s_%s' % (app_label, model)

    publishable_uncommon_cols = {
        'description': 'description',
    }
    
    def alter_self_foreignkeys(self, orm):
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        alter_foreignkey_to_int('galleries_gallery', 'owner')
        alter_foreignkey_to_int('galleries_galleryitem', 'gallery')

    def move_self_foreignkeys(self, orm):
        # there is foreign key to authors called owner instead of ella's classic m2m rel
        # TODO migrate new gallery IDs to core_publishable_authors
        #migrate_foreignkey(self.app_label, self.model, 'core_publishable_authors', 'publishable_id', self.orm)
        # migrate new gallery IDs to galleryitem
        migrate_foreignkey(self.app_label, self.model, 'galleries_galleryitem', self.model, self.orm)

south.plugins.register("core", "0002_03_move_publishable_data", Plugin())