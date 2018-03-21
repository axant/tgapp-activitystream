About activitystream
--------------------

activitystream is a Pluggable application for TurboGears2 for create a simple activity stream.

The activity stream is intended to be used as base layer for a **notification** system

Currently this pluggable works only with *ming* fell free to submit a pull request with *sqlalchemy* support

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

Assuming the third user wants to know if it have notifications not yet seen::

    u3 = model.User.query.find().all()[2]
    [r.action for r in am.not_seen(u3).all()]
    # And if you want to mark a notification as seen just set the flag to True
    am.not_seen(u3).first().seen = True
    # please remember that if you're testing in a tgshell you need to flush the session


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
  Them are actually stored in an other model
