import os

from django.contrib.auth.models import AnonymousUser, User
from django.core.files import File
from django.test import TestCase, RequestFactory

from .models import Document
from .views import list


class DocumentTests(TestCase):
    def setUp(self):
        """
        create two users: UserA, UserB
        create two documents for UserA: one public, one private
        """
        self.factory = RequestFactory()

        self.userA = User.objects.create_user(
            username='foo', email='raf@…', password='top_secret')
        self.userB = User.objects.create_user(
            username='bar', email='raf@…', password='top_secret')

        self.docPrivate = Document.objects.create(
            docfile=File(open(os.path.dirname(__file__) + '/../documents/test.txt')),
            description="test A",
            user=self.userA)
        self.docPublic = Document.objects.create(
            docfile=File(open(os.path.dirname(__file__) + '/../documents/test.txt')),
            description="test B",
            is_public=True,
            user=self.userA)


    def test_get_documents(self):
        """
        UserA should see his own documents
        UserB should see UserA's public document
        """
        doc = Document.objects.get(pk=self.docPrivate.pk)
        self.assertEqual(self.userA, doc.user)
        self.assertFalse(doc.is_public)

        doc = Document.objects.get(pk=self.docPublic.pk)
        self.assertEqual(self.userA, doc.user)
        self.assertTrue(doc.is_public)

        docs = Document.get_user_documents(self.userA)
        self.assertEqual(docs.count(), 2)

        docs = Document.get_user_documents(self.userB)
        self.assertEqual(docs.count(), 1)
        self.assertEqual(self.userA, docs.first().user)


    def test_list_view_anonymous(self):
        """
        The list view of an anonymous user session should
        return a 302 redirect.
        """
        request = self.factory.get('/apps/list')
        request.user = AnonymousUser()

        response = list(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response._headers['location'][1], '/login/?next=/apps/list')


    def test_list_view_authenticated(self):
        """
        The list view of an authenticated user should
        return a 200 ok.
        """
        request = self.factory.get('/apps/list')
        request.user = self.userA

        response = list(request)
        self.assertEqual(response.status_code, 200)


class AppsUrlTests(TestCase):
    def test_non_existent_url(self):
        """
        The detail view of an app should
        return a 404 not found.
        """
        response = self.client.get('apps/detail')
        self.assertEqual(response.status_code, 404)
