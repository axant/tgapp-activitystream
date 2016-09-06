About activitystream
--------------------

activitystream is a Pluggable application for TurboGears2 for create a simple activity stream.

Installing
----------

activitystream can be installed both from pypi or from bitbucket::

    pip install activitystream

should just work for most of the users

Plugging activitystream
-----------------------

In your application *config/app_cfg.py* import **plug**::

    from tgext.pluggable import plug

Then at the *end of the file* call plug with activitystream::

    plug(base_config, 'activitystream')

You will be able to access the plugged application at
*http://localhost:8080/activitystream*.

Available Hooks
---------------

activitystream makes available a some hooks which will be
called during some actions to alter the default
behavior of the appplications:

Exposed Partials
----------------

activitystream exposes a bunch of partials which can be used
to render pieces of the blogging system anywhere in your
application:

Exposed Templates
-----------------

The templates used by registration and that can be replaced with
*tgext.pluggable.replace_template* are:

