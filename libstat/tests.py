# -*- coding: UTF-8 -*-
from django.test.simple import DjangoTestSuiteRunner
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime
import json

from libstat.models import Variable, OpenData

"""
    Test case and test runner for use with Mongoengine
""" 
class MongoEngineTestRunner(DjangoTestSuiteRunner):
    def setup_databases(self):
        pass
        
    def teardown_databases(self, *args):
        pass
 
class MongoTestCase(TestCase):
    mongodb_name = 'test_%s' % settings.MONGODB_NAME
    
    def _fixture_setup(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name)
        
#     def _fixture_teardown(self):
#         pass
    
    def _post_teardown(self):
        from mongoengine.connection import get_connection, disconnect
        connection = get_connection()
        connection.drop_database(self.mongodb_name)
        disconnect()

"""
    Model class test cases
"""
class OpenDataTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v.save()
        publishing_date = datetime(2014, 06, 03, 15, 28, 31)
        d = OpenData(library="Kld1", sample_year=2013, target_group="public", variable=v, value=6, date_created=publishing_date, date_modified=publishing_date)
        d.save()
        
    def test_should_transform_object_to_dict(self):
       object = OpenData.objects.first()
       openDataAsDict = {
            u"folk5": 6, 
            u"library": u"Kld1",
            u"sampleYear": 2013,
            u"targetGroup": u"public",
            u"published": "2014-06-03T15:28:31Z",
            u"modified": "2014-06-03T15:28:31Z" 
       }
       self.assertEquals(object.to_dict(), openDataAsDict)
       
       
class VariableTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v.save()
    
    def test_should_transform_object_to_dict(self):
        object = Variable.objects.first()
        expectedVariableDict = {
            u"@id": u"{}/def/terms#folk5".format(settings.API_BASE_URL),
            u"@type": u"xsd:integer",
            u"label": u"Antal bemannade serviceställen, sammanräknat"
        }
        self.assertEqual(object.to_dict(), expectedVariableDict)
    
"""
    API test cases
"""
class OpenDataApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v.save()
        
        date1 = datetime(2014, 06, 02, 17, 57, 16)
        d1 = OpenData(library="Lu", sample_year=2013, target_group="public", variable=v, value=7, date_created=date1, date_modified=date1)
        d1.save()
        
        date1 = datetime(2014, 06, 03, 15, 28, 31)
        d1 = OpenData(library="Kld1", sample_year=2013, target_group="public", variable=v, value=6, date_created=date1, date_modified=date1)
        d1.save()
        
        date2 = datetime(2014, 06, 04, 11, 14, 01)
        d2 = OpenData(library="Ga", sample_year=2013, target_group="public", variable=v, value=9, date_created=date2, date_modified=date2)
        d2.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("data_api"))
        self.assertEqual(response["Content-Type"], "application/json")
        
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)
        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms#".format(settings.API_BASE_URL))
        self.assertEqual(data[u"@context"][u"observations"], u"@graph")
    
    def test_should_not_filter_by_date_unless_requested(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        response = self.client.get(u"{}?from_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"], u"Ga")
    
    def test_should_filter_data_by_to_date(self):
        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"], u"Lu")
        
    def test_should_filter_data_by_date_range(self):
        response = self.client.get(u"{}?from_date=2014-06-03&to_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"], u"Kld1")
    
    def test_should_limit_results(self):
        response = self.client.get(u"{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 2)
        
    def test_should_limit_results_with_offset(self):
        response = self.client.get(u"{}?limit=2&offset=2".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 1)

        
class TermsApiTest(MongoTestCase):
    def setUp(self):
        v = Variable(key=u"folk5", alias=u"folk5", description=u"Antal bemannade serviceställen, sammanräknat", is_public=True, type="xsd:integer", target_groups=["public"])
        v.save()
    
    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("terms_api"))
        self.assertEqual(response["Content-Type"], "application/json")
    
    def test_response_should_contain_context(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"index"], {u"@container": u"@index", u"@id": u"@graph"})
        self.assertEqual(data[u"@context"][u"xsd"], u"http://www.w3.org/2001/XMLSchema#")
        
    def test_should_contain_hardcoded_terms(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        self.assertTrue(u"library" in data[u"index"])
        self.assertTrue(u"sampleYear" in data[u"index"])
        self.assertTrue(u"targetGroup" in data[u"index"])
        self.assertTrue(u"modified" in data[u"index"])
        self.assertTrue(u"published" in data[u"index"])
    
    def test_should_return_all_variables(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        self.assertTrue(u"folk5" in data[u"index"])
    