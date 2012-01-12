# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase

from ella.interviews.models import Interview, Interviewee

from test_ella.test_core import create_basic_categories

class InterviewTestCase(TestCase):
    def setUp(self):
        super(InterviewTestCase, self).setUp()
        create_basic_categories(self)

        self.interviewee = Interviewee(
                slug='interviewee1',
                name='Some Interviewee',
            )
        self.interviewee.save()

        now = datetime.now()
        day = timedelta(days=1)
        self.interview = Interview(
                category=self.category,
                title='First Interview',
                slug='first-interview',
                description='Some description',
                reply_from=now-day,
                reply_to=now+day,
                ask_from=now-day,
                ask_to=now+day,
                content='Some Text content',
                publish_from=datetime.now()
            )
        self.interview.save()
        self.interview.interviewees.add(self.interviewee)


