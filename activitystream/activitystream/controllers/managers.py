from tg import hooks
from tgext.pluggable import primary_key

from activitystream import model
from activitystream.model.ming_models import Action

# TODO move to lib


class ActionManager(object):

    def create(self, actor, verb, target=None, action_obj=None, *args, **kw):

        actor_id = primary_key(actor.__class__).name
        target_id = primary_key(target.__class__).name if target else ''
        action_obj_id = primary_key(action_obj.__class__).name if action_obj else ''

        a = model.provider.create(
            Action,
            dict(actor_type=actor.__class__.__name__,
                 actor_id=getattr(actor, actor_id),
                 verb=verb,
                 target_type=target.__class__.__name__ if target else None,
                 target_id=getattr(target, target_id, None),
                 action_obj_type=action_obj.__class__.__name__ if action_obj else None,
                 action_obj_id=getattr(action_obj, action_obj_id, None))
        )
        return a

    def get_actions(self, limit=None, order_by='timestamp', desc=True, **kwargs):
        action = model.provider.query(
            Action,
            limit=limit,
            order_by=order_by,
            desc=desc,
            **kwargs)

        hooks.notify('googleplusauth.on_login', args=(action))

        return action

    def actor(self, obj, **kwargs):
        """
        Stream of most recent actions where obj is the actor.
        Keyword arguments will be passed to Action.objects.filter
        """
        return obj.actor_actions.public(**kwargs)
