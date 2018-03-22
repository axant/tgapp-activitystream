About activitystream
--------------------

activitystream is a Pluggable application for TurboGears2 for create a simple activity stream.

The activity stream is intended to be used as base layer for a **notification** system

Currently this pluggable works only with **ming** fell free to submit a pull request with *sqlalchemy* support

Installing
----------

activitystream can be installed both from pypi or from github::

    pip install activitystream

should just work for most of the users

Plugging activitystream
-----------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with activitystream::

    plug(base_config, 'activitystream')


ActionManager
-------------

When you want to create an activity you should do something like::

    from activitystream import ActionManager
    am = ActionManager()

    activity = am.create(
        actor=model.User.query.find().all()[0],
        verb='created',
        target=model.Post.query.find().all()[0],
        recipients=model.User.query.find().all()[1:3],
    )

Then you may want to notify the activity to the recipients.
It's up to you to choose how to dispatch them.

Fields Explanation
-------------------

- **actor**: reference to who is creating the activity
- **verb**: a string describing the action itself, for example 'created' or 'updated'
- **action_obj**: reference to ... I don't know
- **target**: reference to the subject of the activity
- **timestamp**: datetime of the creation of the activity
- **description**: string with a description of the activity
- **extra**: string that you can use for example to store a json with extra informations
- **recipients**: list of references to who is expected to receive
  a notification from this activity. references can be of different entities.

Not Seen (counter of unread notifications)
------------------------------------------

Add in your recipient model (probably your User model)::

    from datetime import datetime
    last_activity_seen = FieldProperty(s.DateTime, if_missing=datetime.utcnow())

then you can get the latest 10 notifications of a recipient with::

    recipient = model.User.query.find().all()[1]
    actions = am.get_by_recipient(recipient).limit(10).all()
    # and if you want a counter of unread notifications call
    count = am.count_not_seen_by_recipient(recipient)
    # you can check if the recipient have seen a notification with
    not_seen = actions[0].timestamp > recipient.last_activity_seen
    # don't forget to update your recipient when him reads his notifications
    recipient.last_activity_seen = datetime.utcnow()

Exposed Controllers
-------------------

if you don't like your urls to start with activitystream just ``plug`` with a new app_id

- **/activitystream/ajax_update_last_seen_of_a_recipient**: call this through ajax with ``_type``
  and ``_id`` of the recipient to update ``last_activity_seen``.
  should return a json with the last_activity_seen before the update

- **/activitystream/see**: updates ``last_activity_seen`` of the logged in user
  and redirects to the given ``target_link``

Notifications Rendering
-----------------------

This is up to you. I suggest to use ``tg.render_template`` with ``tg_cache``

adding in ``myproject.lib.helpers``::

    from activitystream import am
    from tg import render_template
    def notification_cache(n):
        return {
            'cache_key': n._id,  # this is really important
            'cache_expire': 604800,  # a week
            'cache_type': 'memory',
        }


and in the template where you want your notifications to being displayed::

    <py:for each="n in h.am.get_by_recipient(request.identity['user']).limit(10)">
      <li>${h.render_template(
        {'n': n, 'tg_cache': h.notification_cache(n)},
        'kajiki',
        'myproject.templates.notification'
      )}<hr/></li>
    </py:for>

meanwhile your ``myproject.templates.notification`` may look like::

    <a href="${h.plug_url('activitystream', '/see', params={'target_link': n.target_link})}">
      <img src="${n.actor.avatar_url}"/>
      <div class="content">
        <b>${n.actor.display_name}</b> ${_(n.verb)} <i>${n.target}</i>
        <div>${n.timestamp_since}</div>
      </div>
    </a>

if your notification needs to be rendered differently based on the recipient then you have to use
another caching strategy
