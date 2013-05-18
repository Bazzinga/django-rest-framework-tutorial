from django.test import TestCase
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import json
import StringIO


class TestCreateSnippet(TestCase):
    def setUp(self):
        snippet_codes = ['foo = "bar"\n', 'print "hello, world"\n']
        self.code_snippets = {}
        for code in snippet_codes:
            snippet = Snippet(code=code)
            self.code_snippets[code] = snippet

    def test_snippet_creation(self):
        for code, snippet in self.code_snippets.iteritems():
            serializer = SnippetSerializer(snippet)
            data = serializer.data
            self.assertEqual(data['code'], code)
            self.assertEqual(data['language'], u'python')
            self.assertEqual(data['style'], u'friendly')

    def test_renderer(self):
        """The output of JSONRenderer must be the serializer data
        serialized in JSON.

        """
        for code, snippet in self.code_snippets.iteritems():
            serializer = SnippetSerializer(snippet)
            content = JSONRenderer().render(serializer.data)
            assert json.loads(content) == serializer.data


class TestTutorial(TestCase):
    def setUp(self):
        snippet = Snippet(code='foo = "bar"\n')
        snippet.save()

        self.snippet = Snippet(code='print "hello, world"\n')
        self.snippet.save()

        self.serializer = SnippetSerializer(self.snippet)

    def test_serializer(self):
        self.assertEquals(
            self.serializer.data, {
                'pk': 2, 'title': u'', 'code': u'print "hello, world"\n',
                'linenos': False, 'language': u'python', 'style': u'friendly'})

    def test_json_renderer(self):
        content = JSONRenderer().render(self.serializer.data)
        self.assertEquals(
            content,
            '{"pk": 2, "title": "", "code": "print \\"hello, world\\"\\n", '
            '"linenos": false, "language": "python", "style": "friendly"}')

    def test_stream(self):
        content = JSONRenderer().render(self.serializer.data)
        stream = StringIO.StringIO(content)
        data = JSONParser().parse(stream)

        serializer = SnippetSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        for attribute in ('title', 'code', 'linenos', 'language', 'style'):
            self.assertEquals(getattr(serializer.object, attribute),
                              getattr(self.snippet, attribute))

    def test_serialize_all(self):
        serializer = SnippetSerializer(Snippet.objects.all(), many=True)
        self.assertEquals(
            serializer.data,
            [{'pk': 1, 'title': u'', 'code': u'foo = "bar"\n',
              'linenos': False, 'language': u'python',
              'style': u'friendly'},
             {'pk': 2, 'title': u'', 'code': u'print "hello, world"\n',
              'linenos': False, 'language': u'python', 'style': u'friendly'}])
