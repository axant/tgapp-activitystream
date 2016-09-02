# -*- coding: utf-8 -*-
"""Main Controller"""
from tg import TGController
from tg import expose


class RootController(TGController):
    @expose('activitystream.templates.index')
    def index(self):
        return dict()



