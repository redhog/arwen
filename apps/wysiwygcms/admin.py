# -*- coding: utf-8 -*-
import django.contrib.admin
import wysiwygcms.models

django.contrib.admin.site.register(wysiwygcms.models.Node)
django.contrib.admin.site.register(wysiwygcms.models.NodeVersion)
