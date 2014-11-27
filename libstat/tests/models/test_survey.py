# -*- coding: UTF-8 -*-
from datetime import timedelta

from libstat.tests import MongoTestCase
from libstat.models import OpenData, Survey, SurveyVersion


class SurveyModelTest(MongoTestCase):

    def test_can_not_update_status_to_invalid_value(self):
        survey = self._dummy_survey()

        try:
            survey.status = "some_invalid_status"
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_create_survey_with_valid_status(self):
        survey = self._dummy_survey(status="not_viewed")

        self.assertEquals(survey.status, "not_viewed")

    def test_can_not_create_survey_with_invalid_status(self):
        try:
            self._dummy_survey(status="some_invalid_status")
            self.assertTrue(False)
        except KeyError:
            pass

    def test_can_update_status_to_valid_value(self):
        survey = self._dummy_survey(status="not_viewed")

        survey.status = "initiated"

        self.assertEquals(survey.status, "initiated")

    def test_should_export_public_non_null_observations_to_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = self._dummy_observation(variable=variable, value="val1", _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish()
        survey.reload()

        open_data = OpenData.objects.all().get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.variable.key, "key1")
        self.assertEquals(open_data.value, "val1")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertEquals(open_data.date_created, open_data.date_modified)
        self.assertEquals(open_data.date_created, survey.published_at)

    def test_should_overwrite_value_and_date_modified_for_existing_openData(self):
        variable = self._dummy_variable(key=u"key1", is_public=True)
        observation = self._dummy_observation(variable=variable, value="old_value", _is_public=variable.is_public)
        library = self._dummy_library(name="lib1_name", sigel="lib1_sigel", library_type="folkbib")
        survey = self._dummy_survey(library=library, observations=[observation])

        survey.publish()
        survey.reload()

        for obs in survey.observations:
            if obs.variable.key == "key1":
                obs.value = "new_value"
        survey.save()
        survey.publish()

        data = OpenData.objects.all()
        self.assertEquals(len(data), 1)

        open_data = data.get(0)
        self.assertEquals(open_data.library_name, "lib1_name")
        self.assertEquals(open_data.target_group, "folkbib")
        self.assertEquals(open_data.value, "new_value")
        self.assertTrue(open_data.date_modified)
        self.assertTrue(open_data.date_created)
        self.assertNotEquals(open_data.date_created, open_data.date_modified)

    def test_should_get_observation_by_variable_key(self):
        observation1 = self._dummy_observation(variable=self._dummy_variable(key="key1"))
        observation2 = self._dummy_observation(variable=self._dummy_variable(key="key2"))
        observation3 = self._dummy_observation(variable=self._dummy_variable(key="key3"))
        survey = self._dummy_survey(observations=[
            observation1,
            observation2,
            observation3
        ])
        self.assertEquals(survey.observation_by_key("key2"), observation2)

    def test_should_store_version_when_updating_existing_object(self):
        library = self._dummy_library(name="lib1_old_name", city="lib1_old_city", sigel="lib1_sigel")
        survey = self._dummy_survey(status="initiated", library=library)

        survey.library.name = "lib1_new_name"
        survey.library.city = "lib1_new_city"
        survey.status = "controlled"
        survey = survey.save()

        self.assertEquals(survey.library.name, "lib1_new_name")
        self.assertEquals(survey.library.city, "lib1_new_city")
        self.assertEquals(survey.status, "controlled")

        versions = SurveyVersion.objects.filter(survey_response_id=survey.id)
        self.assertEquals(len(versions), 1)
        self.assertEquals(versions[0].survey_response_id, survey.id)
        self.assertEquals(versions[0].library.name, "lib1_old_name")
        self.assertEquals(versions[0].library.city, "lib1_old_city")
        self.assertEquals(versions[0].status, "initiated")

    def test_should_store_one_version_for_each_change(self):
        survey = self._dummy_survey()
        self.assertEquals(len(SurveyVersion.objects.all()), 0)

        survey.library.name = "new_name"
        survey.save()
        self.assertEquals(len(SurveyVersion.objects.all()), 1)

        survey.library.name = "newer_name"
        survey.save()
        self.assertEquals(len(SurveyVersion.objects.all()), 2)

    def test_should_store_version_when_updating_observations_for_existing_objects(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable=self._dummy_variable(key="key1"))
        ])
        self.assertEquals(len(SurveyVersion.objects.all()), 0)

        survey.observation_by_key("key1").value = "new_value"
        survey.save()

        self.assertEquals(len(SurveyVersion.objects.all()), 1)

    def test_should_not_store_version_when_creating_object(self):
        library = self._dummy_library()
        survey = self._dummy_survey(library=library)

        versions = SurveyVersion.objects.filter(survey_response_id=survey.id)
        self.assertEquals(len(versions), 0)

    def test_should_set_modified_date_when_updating_existing_object(self):
        survey = self._dummy_survey()
        survey.library.name = "new_name"
        survey.save().reload()

        self.assertTrue(survey.date_modified > survey.date_created)

    def test_should_not_set_modified_date_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        survey.notes = "new_notes"
        survey.save().reload()

        self.assertEquals(survey.date_modified, survey.date_created)

    def test_should_not_store_version_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=survey.id)), 0)

        survey.notes = "new_notes"
        survey.save()

        self.assertEquals(len(SurveyVersion.objects.filter(survey_response_id=survey.id)), 0)

    def test_should_flag_as_not_published_when_updating_existing_object(self):
        survey = self._dummy_survey()
        survey.library.name = "new_name"
        survey.save().reload()

        self.assertFalse(survey.is_published)

    def test_should_not_flag_as_not_published_when_updating_notes_in_existing_object(self):
        survey = self._dummy_survey()
        survey.publish()
        self.assertTrue(survey.is_published)

        survey.notes = "new_notes"
        survey.save()

        self.assertTrue(survey.is_published)

    def test_should_set_modified_date_when_creating_object(self):
        survey = self._dummy_survey()

        self.assertEquals(survey.date_modified, survey.date_created)


class SurveyPublishTest(MongoTestCase):

    def test_should_flag_new_object_as_not_published(self):
        survey = self._dummy_survey()

        self.assertFalse(survey.is_published)

    def test_should_set_published_date_but_not_modified_date_when_publishing(self):
        survey = self._dummy_survey()
        date_modified = survey.date_modified

        survey.publish()

        self.assertNotEquals(survey.published_at, None)
        self.assertEquals(survey.date_modified, date_modified)

    def test_should_flag_as_published_when_publishing(self):
        survey = self._dummy_survey()

        survey.publish()
        survey.reload()

        self.assertTrue(survey.is_published)

    def test_latest_version_published(self):
        library = self._dummy_library()
        survey = self._dummy_survey(library=library)

        survey.published_at = survey.date_modified + timedelta(hours=-1)
        self.assertFalse(survey.latest_version_published)

        survey.published_at = survey.date_modified
        self.assertTrue(survey.latest_version_published)

        survey.published_at = None
        self.assertFalse(survey.latest_version_published)

        survey.status = "submitted"
        self.assertFalse(survey.latest_version_published)

        survey.publish()
        self.assertTrue(survey.latest_version_published)

    def test_is_published(self):
        survey = self._dummy_survey()
        self.assertFalse(survey.is_published)

        survey.publish()
        self.assertTrue(survey.is_published)

    def test_creates_open_data_when_publishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(),
            self._dummy_observation()])
        self.assertEquals(len(OpenData.objects.all()), 0)

        survey.publish()
        self.assertEquals(len(OpenData.objects.all()), 2)

    def test_does_not_create_new_open_data_for_existing_open_data_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)

    def test_modifies_existing_open_data_that_has_changed_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].value, "old_value")

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].value, "new_value")

    def test_updates_date_modified_for_open_data_that_has_changed_when_republishing(self):
        survey = self._dummy_survey(observations=[
            self._dummy_observation(value="old_value")])
        survey.publish()

        self.assertEquals(OpenData.objects.all()[0].date_modified, OpenData.objects.all()[0].date_created)

        survey.observations[0].value = "new_value"
        survey.publish()

        self.assertTrue(OpenData.objects.all()[0].date_modified > OpenData.objects.all()[0].date_created)

    def test_does_not_update_date_modified_for_open_data_that_has_not_changed_when_republishing(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable1, value="old_value1"),
            self._dummy_observation(variable2, value="old_value2")])
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].date_modified,
                          OpenData.objects.filter(variable=variable2)[0].date_created)

        survey.observation_by_key("key1").value = "new_value1"
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].date_modified,
                          OpenData.objects.filter(variable=variable2)[0].date_created)

    def test_does_not_modify_existing_open_data_that_has_not_changed_when_republishing(self):
        variable1 = self._dummy_variable(key="key1")
        variable2 = self._dummy_variable(key="key2")
        survey = self._dummy_survey(observations=[
            self._dummy_observation(variable1, value="old_value1"),
            self._dummy_observation(variable2, value="old_value2")])
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].value, "old_value2")

        survey.observation_by_key("key1").value = "new_value1"
        survey.publish()

        self.assertEquals(OpenData.objects.filter(variable=variable2)[0].value, "old_value2")

    def test_sets_existing_open_data_as_inactive_when_revoking_publication(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.unpublish()

        self.assertFalse(OpenData.objects.all()[0].is_active)

    def test_sets_existing_open_data_as_active_when_publishing_after_revoking_publication(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.unpublish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertFalse(OpenData.objects.all()[0].is_active)

        survey.publish()

        self.assertEquals(len(OpenData.objects.all()), 1)
        self.assertTrue(OpenData.objects.all()[0].is_active)

    def test_revokes_publication_when_changing_status_from_published(self):
        survey = self._dummy_survey(observations=[self._dummy_observation()])
        survey.publish()

        self.assertTrue(survey.is_published)
        self.assertTrue(OpenData.objects.all()[0].is_active)

        survey.status = "submitted"

        self.assertFalse(survey.is_published)
        self.assertFalse(OpenData.objects.all()[0].is_active)
