# -*- coding: UTF-8 -*-
import json
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.conf import settings

from libstat.models import Variable
from libstat.tests import MongoTestCase
from libstat.views.apis import data_context, term_context
from libstat.tests.utils import _dummy_variable, _dummy_open_data


class OpenDataApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("data_api"))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(data[u"@context"], data_context)

    def test_should_not_filter_by_date_unless_requested(self):
        _dummy_open_data(library_id="1")
        _dummy_open_data(library_id="2")
        _dummy_open_data(library_id="3")

        response = self.client.get(reverse("data_api"))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 3)

    def test_should_filter_data_by_from_date(self):
        _dummy_open_data(library_id="11070", date_modified=datetime(2014, 06, 05, 11, 14, 01))

        response = self.client.get(u"{}?from_date=2014-06-04".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/11070".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_to_date(self):
        _dummy_open_data(library_id="81", date_modified=datetime(2014, 06, 02, 11, 14, 01))

        response = self.client.get(u"{}?to_date=2014-06-03".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/81".format(settings.BIBDB_BASE_URL))

    def test_should_filter_data_by_date_range(self):
        _dummy_open_data(library_id="323", date_modified=datetime(2014, 06, 03, 11, 14, 01))

        response = self.client.get(
            u"{}?from_date=2014-06-02T15:28:31.000&to_date=2014-06-04T11:14:00.000".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"library"][u"@id"],
                          u"{}/library/323".format(settings.BIBDB_BASE_URL))

    def test_should_limit_results(self):
        _dummy_open_data(library_id="1")
        _dummy_open_data(library_id="2")
        _dummy_open_data(library_id="3")

        response = self.client.get(u"{}?limit=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 2)

    def test_should_limit_results_with_offset(self):
        _dummy_open_data(library_id="1")
        _dummy_open_data(library_id="2")
        _dummy_open_data(library_id="3")

        response = self.client.get(u"{}?limit=2&offset=2".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)

    def test_should_filter_by_term_key(self):
        variable = _dummy_variable(key=u"folk6")
        _dummy_open_data(variable=variable)

        response = self.client.get(u"{}?term=folk6".format(reverse("data_api")))
        data = json.loads(response.content)

        self.assertEquals(len(data[u"observations"]), 1)
        self.assertEquals(data[u"observations"][0][u"folk6"], 1)

    def test_should_return_empty_result_if_unknown_term(self):
        response = self.client.get(u"{}?term=hej".format(reverse("data_api")))
        data = json.loads(response.content)
        self.assertEquals(len(data[u"observations"]), 0)


class ObservationApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        obs = _dummy_open_data()

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        obs = _dummy_open_data()

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))
        data = json.loads(response.content)

        self.assertEqual(data[u"@context"][u"@vocab"], u"{}/def/terms/".format(settings.API_BASE_URL)),
        self.assertEquals(data[u"@context"][u"@base"], u"{}/data/".format(settings.API_BASE_URL))

    def test_should_return_one_observation(self):
        variable = _dummy_variable(key=u"folk5")
        obs = _dummy_open_data(variable=variable, sample_year=2013)

        response = self.client.get(reverse("observation_api", kwargs={"observation_id": str(obs.id)}))
        data = json.loads(response.content)

        self.assertEqual(data[u"@id"], str(obs.id))
        self.assertEqual(data[u"@type"], u"Observation")
        self.assertEqual(data[u"folk5"], obs.value)
        self.assertEqual(data[u"library"], {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, obs.library_id)})
        self.assertEqual(data[u"sampleYear"], obs.sample_year)
        self.assertEqual(data[u"published"], obs.date_created_str())
        self.assertEqual(data[u"modified"], obs.date_modified_str())

    def test_should_return_404_if_observation_not_found(self):
        response = self.client.get(reverse("observation_api", kwargs={"observation_id": "12323873982375a8c0g"}))

        self.assertEqual(response.status_code, 404)


class TermsApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        response = self.client.get(reverse("terms_api"))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)

        self.assertEquals(data[u"@context"], term_context)

    def test_should_contain_hardcoded_terms(self):
        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]

        self.assertTrue(u"library" in ids)
        self.assertTrue(u"sampleYear" in ids)
        self.assertTrue(u"targetGroup" in ids)
        self.assertTrue(u"modified" in ids)
        self.assertTrue(u"published" in ids)
        self.assertTrue(u"Observation" in ids)

    def test_should_return_all_variables(self):
        _dummy_variable(key=u"folk5")

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]

        self.assertTrue(u"folk5" in ids)

    def test_should_not_return_variable_drafts(self):
        _dummy_variable(key=u"69", is_draft=True)

        response = self.client.get(reverse("terms_api"))
        data = json.loads(response.content)
        ids = [term[u"@id"] for term in data[u"terms"]]

        self.assertFalse(u"Folk69" in ids)


class TermApiTest(MongoTestCase):

    def test_response_should_return_jsonld(self):
        _dummy_variable(key=u"folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))

        self.assertEqual(response["Content-Type"], "application/ld+json")

    def test_response_should_contain_context(self):
        _dummy_variable(key=u"folk5")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
        data = json.loads(response.content)

        self.assertEqual(data[u"@context"][u"xsd"], u"http://www.w3.org/2001/XMLSchema#")
        self.assertEqual(data[u"@context"][u"rdf"], u"http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        self.assertEqual(data[u"@context"][u"rdfs"], u"http://www.w3.org/2000/01/rdf-schema#")
        self.assertEqual(data[u"@context"][u"qb"], u"http://purl.org/linked-data/cube#")
        self.assertEqual(data[u"@context"][u"@language"], u"sv")
        self.assertEqual(data[u"@context"][u"label"], u"rdfs:label")
        self.assertEqual(data[u"@context"][u"range"], {u"@id": u"rdfs:range", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"comment"], u"rdfs:comment")
        self.assertEqual(data[u"@context"][u"subClassOf"], {u"@id": u"rdfs:subClassOf", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"replaces"], {u"@id": u"dcterms:replaces", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"replacedBy"], {u"@id": u"dcterms:isReplacedBy", u"@type": u"@id"})
        self.assertEqual(data[u"@context"][u"valid"], {u"@id": u"dcterms:valid", u"@type": u"dcterms:Period"})

    def test_should_return_one_term(self):
        _dummy_variable(key=u"folk5", description=u"some description", type="integer")

        response = self.client.get(reverse("term_api", kwargs={"term_key": "folk5"}))
        data = json.loads(response.content)

        self.assertEquals(len(data), 6)
        self.assertEquals(data[u"@context"], term_context)
        self.assertEquals(data[u"@id"], u"folk5"),
        self.assertEquals(data[u"@type"], [u"rdf:Property", u"qb:MeasureProperty"]),
        self.assertEquals(data[u"comment"], u"some description"),
        self.assertEquals(data[u"range"], u"xsd:integer")
        self.assertEquals(data[u"isDefinedBy"], "")

    def test_should_return_404_if_term_not_found(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "foo"}))
        self.assertEqual(response.status_code, 404)

    def test_should_return_404_if_term_is_draft(self):
        response = self.client.get(reverse("term_api", kwargs={"term_key": "Folk69"}))
        self.assertEqual(response.status_code, 404)


class ReplaceableVariablesApiTest(MongoTestCase):

    def setUp(self):
        self.url = reverse("replaceable_variables_api")
        self.client.login(username="admin", password="admin")

        # v = Variable(key=u"Folk28",
        #              description=u"Totalt antal anställda personer som är bibliotekarier och som är män 1 mars.",
        #              type="integer", is_public=True, target_groups=["public"])
        # self.active_public = v.save()
        # v2 = Variable(key=u"Forsk21", description=u"Antal anställda manliga bibliotekarier och dokumentalister.",
        #               type="integer", is_public=True, is_draft=True, target_groups=["research"])
        # self.draft = v2.save()
        # v3 = Variable(key=u"Sjukhus104",
        #               description=u"Totalt antal fjärrutlån under kalenderåret - summering av de angivna delsummorna",
        #               type="integer", is_public=True, replaced_by=v, target_groups=["hospital"])
        # self.already_replaced = v3.save()
        # v4 = Variable(key=u"Skol10", description=u"Postort", type="string", is_public=False, target_groups=["school"])
        # self.active_private = v4.save()

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_replaceable_variables_as_json(self):
        var1 = _dummy_variable(key=u"key_1")
        _dummy_variable(key=u"key_2", is_draft=True)
        _dummy_variable(key=u"key_3", replaced_by=var1)
        var4 = _dummy_variable(key=u"key_4")

        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "key_1",
                                  "id": str(var1.id),
                                  "description": var1.description},
                                 {"key": "key_4",
                                  "id": str(var4.id),
                                  "description": var4.description}])

    def test_should_filter_replaceables_by_key(self):
        var = _dummy_variable(key=u"Folk28")

        response = self.client.get("{}?q=fo".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk28",
                                  "id": str(var.id),
                                  "description": var.description}])

    def test_should_filter_replaceables_by_description(self):
        var = _dummy_variable(key=u"Skol10", description=u"Postort", type="string")
        response = self.client.get("{}?q=post".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Skol10",
                                  "id": str(var.id),
                                  "description": var.description}])


class SurveyableVariablesApiTest(MongoTestCase):

    def setUp(self):
        v = Variable(key=u"Folk12", description=u"Antal bemannade filialer", type="integer", is_public=True,
                     target_groups=["public"])
        self.active_without_dates = v.save()

        v1 = Variable(key=u"Folk10", description=u"Antal bemannade servicesställen", type="integer", is_public=True,
                      target_groups=["public"],
                      active_from=datetime(2010, 1, 1).date())
        self.active_with_from_date = v1.save()

        v3 = Variable(key=u"Folk31", description=u"Antal årsverken totalt", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_from=datetime.utcnow().date(), active_to=(datetime.utcnow() + timedelta(days=1)).date())
        self.active_with_date_range = v3.save()

        v2 = Variable(key=u"Folk35", description=u"Antal årsverken övrig personal", type="decimal", is_public=True,
                      target_groups=["public"],
                      active_to=datetime(2014, 6, 1).date())
        self.discontinued = v2.save()

        v5 = Variable(key=u"Folk20", description=u"Text övriga utlåningsställen", type="string", is_public=False,
                      target_groups=["public"],
                      active_from=(datetime.utcnow() + timedelta(days=90)).date())
        self.pending = v5.save()

        v4 = Variable(key=u"Folk69", description=u"Totalt nyförvärv AV-medier", type="integer", is_public=True,
                      target_groups=["public"],
                      is_draft=True)
        self.draft = v4.save()

        v6 = Variable(key=u"Folk80", description=u"Nyförvärv musik under kalanderåret.", type="integer", is_public=True,
                      target_groups=["public"],
                      replaced_by=self.draft)
        self.replaced = v6.save()

        self.url = reverse("surveyable_variables_api")
        self.client.login(username="admin", password="admin")

    def test_view_requires_admin_login(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.login(username="library_user", password="secret")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 302)

        self.client.logout()
        self.client.login(username="admin", password="admin")
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)

    def test_should_return_active_pending_and_draft_variables_as_json(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk10", "id": str(self.active_with_from_date.id)},
                                 {"key": "Folk12", "id": str(self.active_without_dates.id)},
                                 {"key": "Folk20", "id": str(self.pending.id)},
                                 {"key": "Folk31", "id": str(self.active_with_date_range.id)},
                                 {"key": "Folk69", "id": str(self.draft.id)}])

    def test_should_filter_surveyable_by_key(self):
        response = self.client.get("{}?q=Folk1".format(self.url))
        self.assertEquals(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEquals(data, [{"key": "Folk10", "id": str(self.active_with_from_date.id)},
                                 {"key": "Folk12", "id": str(self.active_without_dates.id)}])
