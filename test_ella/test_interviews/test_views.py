# -*- coding: utf-8 -*-
from datetime import datetime
import sys

import django
from django.contrib.auth.models import User

from ella.interviews.models import Question, Answer
# register interviews' urls
from ella.interviews import register 

from test_ella.test_interviews import InterviewTestCase
from test_ella import template_loader

from nose import tools


class InterviewViewTestCase(InterviewTestCase):
    def setUp(self):
        super(InterviewViewTestCase, self).setUp()
        self.templates = template_loader.templates


    def tearDown(self):
        super(InterviewViewTestCase, self).tearDown()
        template_loader.templates = {}

class TestViews(InterviewViewTestCase):
    def test_custom_detail_context(self):
        self.templates['page/object.html'] = ''

        r = self.client.get(self.interview.get_absolute_url())

        tools.assert_true('form' in r.context)
        tools.assert_true('interviewees' in r.context)
        tools.assert_equals([], r.context['interviewees'])

    def test_reply_raises_404_for_unauthorized_users(self):
        self.templates['404.html'] = ''
        u = User(username='my_user')
        u.set_password('secret')
        u.save()
        tools.assert_true(self.client.login(username='my_user', password='secret'))
        url = self.interview.get_absolute_url() + 'reply/'
        r = self.client.get(url)
        tools.assert_equals(404, r.status_code)

    def test_reply_raises_404_for_anonymous(self):
        self.templates['404.html'] = ''
        url = self.interview.get_absolute_url() + 'reply/'
        r = self.client.get(url)
        tools.assert_equals(404, r.status_code)

    def test_post_to_reply_works(self):
        # http://code.djangoproject.com/changeset/11821
        if django.VERSION < (1, 2) and sys.version_info > (2, 6, 4):
            raise self.SkipTest()

        self.templates['404.html'] = ''
        u = User(username='my_user')
        u.set_password('secret')
        u.save()
        self.interviewee.user = u
        self.interviewee.save()
        q = Question.objects.create(interview=self.interview, content='What ?')

        url = self.interview.get_absolute_url() + 'reply/' + str(q.pk) + '/'
        tools.assert_true(self.client.login(username='my_user', password='secret'))
        data = {'content': 'That !'}
        r = self.client.post(url, data)
        tools.assert_equals(302, r.status_code)

        tools.assert_equals(1, Answer.objects.all().count())
        a = Answer.objects.all()[0]
        tools.assert_equals(q, a.question)
        tools.assert_equals(data['content'], a.content)
        tools.assert_equals(self.interviewee, a.interviewee)


    def test_reply_lists_questions(self):
        # http://code.djangoproject.com/changeset/11821
        if django.VERSION < (1, 2) and sys.version_info > (2, 6, 4):
            raise self.SkipTest()

        self.templates['404.html'] = ''
        self.templates['page/reply.html'] = ''
        u = User(username='my_user')
        u.set_password('secret')
        u.save()
        self.interviewee.user = u
        self.interviewee.save()
        q = Question.objects.create(interview=self.interview, content='What ?')

        url = self.interview.get_absolute_url() + 'reply/'
        tools.assert_true(self.client.login(username='my_user', password='secret'))
        r = self.client.get(url)

        tools.assert_equals(200, r.status_code)
        tools.assert_equals([q], list(r.context['page'].object_list))

    def test_ask_works(self):
        self.templates['page/ask_preview.html'] = ''

        url = self.interview.get_absolute_url() + 'ask/'
        data = {'nickname': 'My nick', 'content': 'What ?'}
        r = self.client.post(url, data)

        tools.assert_equals(200, r.status_code)
        tools.assert_true('hash_field' in r.context)
        tools.assert_true('hash_value' in r.context)
        
        data[r.context['hash_field']] = r.context['hash_value']
        data[r.context['stage_field']] = '2'

        r = self.client.post(url, data)
        tools.assert_equals(302, r.status_code)

        tools.assert_equals(1, Question.objects.all().count())
        q = Question.objects.all()[0]
        tools.assert_equals(self.interview, q.interview)
        tools.assert_equals(data['content'], q.content)
        tools.assert_equals(data['nickname'], q.nickname)



