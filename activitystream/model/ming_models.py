from datetime import datetime, timedelta

from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass

from activitystream import model
from activitystream.model import DBSession

from tg.i18n import ugettext as _, lazy_ugettext as l_


class Action(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'activity_stream_action'
        indexes = [
            (('actor_id', ), ('timestamp', -1)),
            ('actor_type', ),

        ]

    _id = FieldProperty(s.ObjectId)

    actor_type = FieldProperty(s.String)
    actor_id = FieldProperty(s.ObjectId)

    verb = FieldProperty(s.String)

    description = FieldProperty(s.String)
    extra = FieldProperty(s.String)

    target_type = FieldProperty(s.String)
    target_id = FieldProperty(s.ObjectId)

    action_obj_type = FieldProperty(s.String)
    action_obj_id = FieldProperty(s.ObjectId)

    timestamp = FieldProperty(s.DateTime, if_missing=datetime.utcnow)

    @property
    def timestamp_24_hh_mm(self):
        return datetime.strftime(self.timestamp, '%X')

    @property
    def actor(self, default=None):
        if not (self.actor_type and self.actor_id):
            return default
        return self.get_first(self.actor_type, self.actor_id)

    @property
    def target(self, default=None):
        if not (self.target_type and self.target_id):
            return default
        return self.get_first(self.target_type, self.target_id)

    @property
    def action_obj(self, default=None):
        if not (self.action_obj_type and self.action_obj_id):
            return default
        return self.get_first(self.action_obj_type, self.action_obj_id)

    @staticmethod
    def get_first(type_, id_):
        from tgext.pluggable import app_model, primary_key

        model_ = getattr(app_model, type_)
        primary_key_ = primary_key(model_)

        _, results = model.provider.query(
            model_,
            filters={primary_key_.name: id_})

        entity = next(iter(results), None)
        return str(entity)

    @property
    def timestamp_since(self):
        diff = datetime.utcnow() - self.timestamp

        minutes = diff.total_seconds() / 60

        if minutes <= 1:
            timestamp_since_ = _(u'less than 1 minute ago')
        elif minutes < 60:
            timestamp_since_ = _(u'about %s minutes ago') % int(minutes)
        elif 60 <= minutes < 119:
            timestamp_since_ = _(u'about 1 hour ago')
        elif minutes < 60 * 24:
            timestamp_since_ = _(u'about %s hours ago') % int(minutes/60)
        else:
            timestamp_since_ = datetime.strftime(self.timestamp, '%x')

        return timestamp_since_


    @classmethod
    def render_str(cls, action, **kw):
        '''

        <actor> <verb> <time>
        <actor> <verb> <target> <time>
        <actor> <verb> <action_object> <target> <time>
        '''

        timestamp_format = kw.get('timestamp_format', lambda t: datetime.strftime(t, '%x'))
        timestamp_since = None

        if kw.get('timestamp_since', False):
            timestamp_since = action.timestamp_since

        str_ = u'{actor} {verb} {action_object} {target} {time}'.format(
            actor=action.actor,
            verb=action.verb,
            target=action.target or '',
            action_object=action.action_obj or '',
            time=timestamp_since or timestamp_format(action.timestamp))

        return str_




'''
class Follow(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'activity_stream_follow'
        #indexes = [(('activated', ), ('code', ))]

    _id = FieldProperty(s.ObjectId)

    following_type = FieldProperty(s.String)
    following_id = FieldProperty(s.ObjectId)

    follower_type = FieldProperty(s.String)
    follower_id = FieldProperty(s.ObjectId)

    started = FieldProperty(s.DateTime, if_missing=datetime.utcnow())
'''
