# -*- coding: utf-8 -*-
"""Main Controller"""
from tg import TGController
from tg import expose, redirect, request

from activitystream import ActionManager


am = ActionManager()


class RootController(TGController):
    @expose()
    def see(self, _id, target_link):
        am.mark_as_seen(_id, request.identity['user'])
        return redirect(target_link)
