from datetime import datetime

from activitystream import model
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from pymongo import DESCENDING

from tg.i18n import ugettext as _
from tgext.pluggable import instance_primary_key


def get_first(type_, id_):
    model_ = model.provider.get_entity(type_)
    primary_field_ = model.provider.get_primary_field(model_)
    return model.provider.get_obj(
        model_,
        {primary_field_: id_}
    )


class Action(MappedClass):
    class __mongometa__:
        session = model.DBSession
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
        entity = get_first(self.actor_type, self.actor_id)
        return getattr(entity, 'as_str', str(entity))

    @property
    def target(self, default=None):
        if not (self.target_type and self.target_id):
            return default
        entity = get_first(self.target_type, self.target_id)
        return getattr(entity, 'as_str', str(entity))

    @property
    def target_link(self):
        entity = get_first(self.target_type, self.target_id)
        return getattr(entity, 'as_link', None)

    @property
    def action_obj(self, default=None):
        if not (self.action_obj_type and self.action_obj_id):
            return default
        return get_first(self.action_obj_type, self.action_obj_id)

    @property
    def timestamp_since(self):
        diff = datetime.utcnow() - self.timestamp

        minutes = diff.total_seconds() / 60

        if minutes <= 1:
            timestamp_since_ = _(u'less than 1 minute ago')
        elif int(minutes) == 1:
            timestamp_since_ = _(u'about 1 minute ago')
        elif minutes < 60:
            timestamp_since_ = _(u'about %s minutes ago') % int(minutes)
        elif 60 <= minutes < 119:
            timestamp_since_ = _(u'about 1 hour ago')
        elif minutes < 60 * 24:
            timestamp_since_ = _(u'about %s hours ago') % int(minutes/60)
        else:
            timestamp_since_ = datetime.strftime(self.timestamp, '%x')

        return timestamp_since_

    @property
    def recipients(self):
        return Recipient.query.find({'action_id': self._id})

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


class Recipient(MappedClass):
    class __mongometa__:
        session = model.DBSession
        name = 'activity_stream_recipients'
        indexes = [
            (('recipient_id', ), ('seen', )),
            ('action_id', ),
        ]

    _id = FieldProperty(s.ObjectId)

    recipient_id = FieldProperty(s.ObjectId)
    recipient_type = FieldProperty(s.String)

    action_id = ForeignIdProperty(Action)
    action = RelationProperty(Action)

    seen = FieldProperty(s.Bool, if_missing=False)

    @property
    def recipient(self, default=None):
        if not (self.recipient_type and self.recipient_id):
            return default
        return get_first(self.recipient_type, self.recipient_id)

    @classmethod
    def not_seen(cls, recipient):
        return cls.query.find({'recipient_id': instance_primary_key(recipient),
                               'seen': False}).sort('_id', DESCENDING)
        # sorting on _id should be enough and I can't sort on action.timestamp
