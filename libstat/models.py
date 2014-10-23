# -*- coding: UTF-8 -*-
import logging

from mongoengine import *
from mongoengine import signals
from mongoengine.queryset import Q
from mongoengine.django.auth import User
from mongoengine.errors import DoesNotExist
from mongoengine.queryset.queryset import QuerySet
from django.conf import settings

from datetime import datetime

from libstat.utils import ISO8601_utc_format, SURVEY_RESPONSE_STATUSES, NOT_VIEWED, PUBLISHED


logger = logging.getLogger(__name__)

from libstat.utils import SURVEY_TARGET_GROUPS, targetGroups, VARIABLE_TYPES, rdfVariableTypes


class VariableQuerySet(QuerySet):
    is_draft_not_set_query = Q(is_draft=None)
    is_not_draft_query = Q(is_draft=False)
    public_query = Q(is_public=True)
    is_not_replaced_query = Q(replaced_by=None)

    def public_terms(self):
        return self.filter(self.public_query & (self.is_draft_not_set_query | self.is_not_draft_query))

    def public_term_by_key(self, key):
        if not key:
            raise DoesNotExist("No key value given")
        key_query = Q(key=key)
        return self.get(key_query & self.public_query & (self.is_draft_not_set_query | self.is_not_draft_query))

    def replaceable(self):
        return self.filter(self.is_not_replaced_query & (self.is_draft_not_set_query | self.is_not_draft_query))

    def surveyable(self):
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        active_to_not_set = Q(active_to=None)
        is_not_discontinued = Q(active_to__gt=today)
        return self.filter((active_to_not_set | is_not_discontinued) & self.is_not_replaced_query)


class VariableBase(Document):
    description = StringField(required=True)
    # Comment is a private field and should never be returned as open data
    comment = StringField()
    is_public = BooleanField(required=True, default=True)
    type = StringField(required=True, choices=VARIABLE_TYPES)
    target_groups = ListField(StringField(choices=SURVEY_TARGET_GROUPS), required=True)
    category = StringField()
    sub_category = StringField()

    # TODO: Inför frågor/delfrågor i termdokument och kör om importen
    question = StringField()
    question_part = StringField()
    summary_of = ListField()

    date_modified = DateTimeField()
    modified_by = ReferenceField(User)
    is_draft = BooleanField()

    # Only date-part of these fields is relevant,
    active_from = DateTimeField()
    active_to = DateTimeField()

    replaces = ListField(ReferenceField("Variable"))
    replaced_by = ReferenceField("Variable")

    meta = {
        'abstract': True,
    }

    @property
    def is_active(self):
        if self.is_draft:
            return False
        elif self._is_no_longer_active():
            return False
        elif self._is_not_yet_active():
            return False
        else:
            return True

    @property
    def state(self):
        if self.is_draft:
            return {u"state": u"draft", u"label": u"utkast"}
        elif self.replaced_by:
            return {u"state": u"replaced", u"label": u"ersatt"}
        elif self._is_no_longer_active():
            return {u"state": u"discontinued", u"label": u"avslutad"}
        elif self._is_not_yet_active():
            return {u"state": u"pending", u"label": u"vilande"}
        else:
            # Cannot use 'active' as state/css class, it's already a class in Bootstrap...
            return {u"state": u"current", u"label": u"aktiv"}

    def _is_no_longer_active(self):
        return self.active_to and datetime.utcnow().date() > self.active_to.date()

    def _is_not_yet_active(self):
        return self.active_from and datetime.utcnow().date() < self.active_from.date()


class Variable(VariableBase):
    key = StringField(required=True, unique=True)

    meta = {
        'collection': 'libstat_variables',
        'ordering': ['key'],
        'queryset_class': VariableQuerySet
    }

    @classmethod
    def store_version_and_update_date_modified(cls, sender, document, **kwargs):
        if document.id and not document.is_draft:
            changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []
            logger.debug(u"PRE_SAVE: Fields {} have changed, creating variable version from current version".format(
                changed_fields))
            query_set = Variable.objects.filter(pk=document.id)
            assert len(query_set) > 0  # Trigger lazy loading
            versions = query_set.clone_into(VariableVersion.objects)
            for v in versions:
                v.id = None
                v.variable_id = document.id
                v.save()

        document.date_modified = datetime.utcnow()

    @classmethod
    def post_delete_actions(cls, sender, document, **kwargs):
        if document.replaces:
            for replaced in document.replaces:
                if replaced.replaced_by and replaced.replaced_by.id == document.id:
                    replaced.active_to = None
                    replaced.save()
                    logger.debug(
                        u"POST_DELETE: Setting 'active_to' to None on replaced {} when deleting replacement".format(
                            replaced.id))

    @property
    def is_summary_auto_field(self):
        return len(self.summary_of) > 0 and not self.question and not self.question_part

    @property
    def label(self):
        if self.question and self.question_part:
            return [self.question, self.question_part]
        elif self.question:
            return self.question
        else:
            return self.description

    def replace_siblings(self, to_be_replaced=[], switchover_date=None, commit=False):
        """
            Important: If commit=False, make sure to use instance method
            'save_updated_self_and_modified_replaced(modified_siblings)'
            to ensure that siblings are not saved for draft variables and
            that all modifications are actually saved (no dirty transactions).
        """
        current_replacements = set(self.replaces)
        modified_siblings = set()
        siblings_to_replace = set()

        if to_be_replaced:
            # Ensure Variables to be replaced exist and are in the correct state
            for object_id in to_be_replaced:
                try:
                    variable = Variable.objects.get(pk=object_id)
                    if variable.replaced_by is not None and variable.replaced_by.id != self.id:
                        raise AttributeError(
                            u"Variable {} is already replaced by {}".format(object_id, variable.replaced_by.id))
                    siblings_to_replace.add(variable)
                except Exception as e:
                    logger.error(
                        u"Error while fetching Variable with id {} to be replaced by Variable {}: {}".format(object_id,
                                                                                                             self.id,
                                                                                                             e))
                    raise e

        siblings_to_release = current_replacements - siblings_to_replace

        # Release siblings that should no longer be replaced by this instance
        for to_release in siblings_to_release:
            if to_release.replaced_by:
                to_release.replaced_by = None
                to_release.active_to = None
                modified_siblings.add(to_release)

        # Replace sibling variables
        for to_replace in siblings_to_replace:
            """
                Nota bene: This modifies siblings for drafts as well as active variables.
                It is important to use the instance method 'save_updated_self_and_modified_replaced(modified_siblings)'
                to avoid saving siblings for draft variables.
            """
            if (not to_replace.replaced_by or to_replace.replaced_by.id != self.id
                or to_replace.active_to != switchover_date):
                to_replace.replaced_by = self
                to_replace.active_to = switchover_date if switchover_date else None
                modified_siblings.add(to_replace)

        # Update list of replaced on self
        self.replaces = list(siblings_to_replace)

        if commit:
            modified_siblings = self.save_updated_self_and_modified_replaced(modified_siblings)

        return modified_siblings

    def save_updated_self_and_modified_replaced(self, modified_siblings):
        """
            When updating both self and siblings with reference to self, we need to save self first
            and then update the reference in modified siblings before saving then. Otherwise transactions
            for siblings will be flagged as dirty (and never committed).
            If self is a draft, siblings will not be saved.
        """
        updated_siblings = []
        updated_instance = self.save()
        if not updated_instance.is_draft:
            for sibling in modified_siblings:
                if sibling.replaced_by and sibling.replaced_by.id == updated_instance.id:
                    sibling.replaced_by = updated_instance
                updated_siblings.append(sibling.save())
        return updated_siblings

    def target_groups__descriptions(self):
        display_names = []
        for tg in self.target_groups:
            display_names.append(targetGroups[tg])
        return display_names

    def to_dict(self, id_prefix=""):
        json_ld_dict = {u"@id": u"{}{}".format(id_prefix, self.key),
                        u"@type": [u"rdf:Property", u"qb:MeasureProperty"],
                        u"comment": self.description,
                        u"range": self.type_to_rdf_type(self.type)}

        if self.replaces:
            json_ld_dict[u"replaces"] = [replaced.key for replaced in self.replaces]

        if self.replaced_by:
            json_ld_dict[u"replacedBy"] = self.replaced_by.key

        if self.active_to or self.active_from:
            range_str = u"name=Giltighetstid;"
            if self.active_from:
                range_str += u" start={};".format(self.active_from.date())
            if self.active_to:
                range_str += u" end={};".format(self.active_to.date())

            json_ld_dict[u"valid"] = range_str

        return json_ld_dict

    def type_to_rdf_type(self, type):
        return rdfVariableTypes[type]

    def as_simple_dict(self):
        return {u'key': self.key, u'id': str(self.id), u'description': self.description}

    def is_deletable(self):
        if self.is_draft:
            return True

        # TODO: Check if Survey is referencing variable when Survey model has been updated.
        referenced_in_survey_response = Survey.objects.filter(observations__variable=str(self.id)).count() > 0
        referenced_in_open_data = OpenData.objects.filter(variable=str(self.id)).count() > 0

        return not referenced_in_survey_response and not referenced_in_open_data

    def __unicode__(self):
        return self.key


class VariableVersion(VariableBase):
    key = StringField(required=True)
    variable_id = ObjectIdField(required=True)

    meta = {
        'collection': 'libstat_variable_versions',
    }


class Cell(EmbeddedDocument):
    variable_key = StringField()
    required = BooleanField()
    previous_value = StringField()
    sum_of = ListField(StringField())
    sum_siblings = ListField(StringField())
    types = ListField(StringField())
    disabled = BooleanField()


class Row(EmbeddedDocument):
    description = StringField()
    explanation = StringField()
    cells = ListField(EmbeddedDocumentField(Cell))


class Group(EmbeddedDocument):
    description = StringField()
    rows = ListField(EmbeddedDocumentField(Row))
    headers = ListField(StringField())
    columns = IntField()


class Section(EmbeddedDocument):
    title = StringField()
    groups = ListField(EmbeddedDocumentField(Group))


class SurveyTemplate(Document):
    key = StringField()
    target_year = StringField()
    organization_name = StringField()
    municipality = StringField()
    municipality_code = StringField()
    head_authority = StringField()
    respondent_name = StringField()
    respondent_email = StringField()
    respondent_phone = StringField()
    website = StringField()
    sections = ListField(EmbeddedDocumentField(Section))

    def get_cell(self, variable_key):
        for section in self.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        if cell.variable_key == variable_key:
                            return cell
        return None


class SurveyResponseQuerySet(QuerySet):
    def by_year_or_group(self, sample_year=None, target_group=None):
        target_group_query = Q(target_group=target_group) if target_group else Q()
        sample_year_query = Q(sample_year=sample_year) if sample_year else Q()
        return self.filter(target_group_query & sample_year_query)

    def unpublished_by_year_or_group(self, sample_year=None, target_group=None):
        match_target_group = Q(target_group=target_group) if target_group else Q()
        match_sample_year = Q(sample_year=sample_year) if sample_year else Q()
        never_published = Q(published_at=None)
        changed_after_published = Q(_is_published=False)
        return self.filter(match_target_group & match_sample_year & (changed_after_published | never_published))


class SurveyObservation(EmbeddedDocument):
    variable = ReferenceField(Variable, required=True)
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField()
    # Storing variable key on observation to avoid having to fetch variables all the time.
    _source_key = StringField()
    disabled = BooleanField()
    # Public API Optimization and traceability (was this field public at the time of the survey?)
    _is_public = BooleanField(required=True, default=True)

    def __unicode__(self):
        return u"{0}: {1}".format(self.variable, self.value)

    @property
    def instance_id(self):
        return self._instance.id


class Library(Document):
    name = StringField()
    bibdb_id = StringField()
    sigel = StringField()
    email = EmailField()
    municipality_name = StringField()
    municipality_code = StringField()

    meta = {
        'collection': 'libstat_libraries'
    }


class LibrarySelection(Document):
    name = StringField(unique=True)
    sigels = ListField()


class SurveyMetadata(EmbeddedDocument):
    respondent_name = StringField()
    respondent_email = StringField()
    respondent_phone = StringField()
    website = StringField()
    survey_time_hours = IntField()
    survey_time_minutes = IntField()
    population_nation = LongField()
    population_0to14y = LongField()


class SurveyBase(Document):
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    metadata = EmbeddedDocumentField(SurveyMetadata)
    published_at = DateTimeField()
    published_by = ReferenceField(User)
    # True if this version is published, False otherwise. Flag needed to
    # optimize search for unpublished SurveyResponses.
    _is_published = BooleanField()
    date_created = DateTimeField(required=True, default=datetime.utcnow)
    created_by = ReferenceField(User)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)
    modified_by = ReferenceField(User)
    observations = ListField(EmbeddedDocumentField(SurveyObservation))
    status = StringField(choices=SURVEY_RESPONSE_STATUSES, default=NOT_VIEWED[0])
    library = ReferenceField(Library)

    meta = {
        'abstract': True,
    }

    def observation_by_key(self, key):
        hits = [obs for obs in self.observations if obs._source_key == key]
        return hits[0] if len(hits) > 0 else None

    def get_observation(self, key):
        hits = [obs for obs in self.observations if obs.variable.key == key]
        return hits[0] if len(hits) > 0 else None


class Survey(SurveyBase):
    # Both unique fields need to be in subclasses to enable proper indexing.
    library_name = StringField()
    sample_year = IntField()
    password = StringField()

    meta = {
        'collection': 'libstat_surveys',
        'queryset_class': SurveyResponseQuerySet,
    }

    @classmethod
    def store_version_and_update_date_modified(cls, sender, document, **kwargs):
        if document.id:
            if hasattr(document, "_action_publish"):
                document._is_published = True
            else:
                changed_fields = document.__dict__["_changed_fields"] if "_changed_fields" in document.__dict__ else []
                logger.info(
                    u"PRE SAVE: Fields {} have changed, creating survey response version from current version".format(
                        changed_fields))
                query_set = Survey.objects.filter(pk=document.id)
                assert len(query_set) > 0  # Trigger lazy loading
                versions = query_set.clone_into(SurveyVersion.objects)
                for v in versions:
                    v.id = None
                    v.survey_response_id = document.id
                    v.save()
                document.date_modified = datetime.utcnow()
                document._is_published = False
                # field modified_by is set in form
        else:
            # logger.debug("PRE SAVE: Creation of new object, setting modified date to value of creation date")
            document.date_modified = document.date_created
            document.modified_by = document.created_by
            if not hasattr(document, "_is_published"):
                document._is_published = False

    @property
    def latest_version_published(self):
        return self._is_published if self._is_published else (
            self.published_at != None and self.published_at >= self.date_modified)

    @property
    def is_published(self):
        return self._is_published if self._is_published else self.published_at != None

    def target_group__desc(self):
        return targetGroups[self.target_group]

    def publish(self, user=None):
        # TODO: Publishing date as a parameter to enable setting correct date for old data?
        logger.debug(u"Publishing SurveyResponse {}".format(self.id))
        publishing_date = datetime.utcnow()

        for obs in self.observations:
            # Only publish public observations that have a value
            if obs._is_public and obs.value != None:
                # TODO: Need to handle consequent publishes
                data_item = None
                existing = OpenData.objects.filter(library_name=self.library_name, sample_year=self.sample_year,
                                                   variable=obs.variable)
                if (len(existing) == 0):
                    data_item = OpenData(library_name=self.library_name, sample_year=self.sample_year,
                                         variable=obs.variable,
                                         target_group=self.target_group, date_created=publishing_date)
                    if self.library and self.library.bibdb_id:
                        data_item.library_id = self.library.bibdb_id
                else:
                    data_item = existing.get(0)

                data_item.value = obs.value
                data_item.date_modified = publishing_date
                data_item.save()

        self.status = PUBLISHED[0]
        self.published_at = publishing_date
        self.published_by = user

        # Custom attribute to handle pre-save actions
        self._action_publish = True

        self.save()

    def __unicode__(self):
        return u"{} {} {}".format(self.target_group, self.library_name, self.sample_year)


class SurveyVersion(SurveyBase):
    # Not unique to enable storage of multiple versions. Both fields need to be in subclasses to enable proper indexing.
    library_name = StringField(required=True)
    sample_year = IntField(required=True)
    survey_response_id = ObjectIdField(required=True)

    meta = {
        'collection': 'libstat_survey_versions',
        'ordering': ['-date_modified']
    }


class OpenData(Document):
    library_name = StringField(required=True, unique_with=['sample_year', 'variable'])
    library_id = StringField()  # TODO
    sample_year = IntField(required=True)
    target_group = StringField(required=True, choices=SURVEY_TARGET_GROUPS)
    variable = ReferenceField(Variable, required=True)
    # Need to allow None/null values to indicate invalid or missing responses in old data
    value = DynamicField()
    date_created = DateTimeField(required=True, default=datetime.utcnow)
    date_modified = DateTimeField(required=True, default=datetime.utcnow)

    meta = {
        'collection': 'libstat_open_data',
        'ordering': ['-date_modified']
    }

    def date_created_str(self):
        return self.date_created.strftime(ISO8601_utc_format)

    def date_modified_str(self):
        return self.date_modified.strftime(ISO8601_utc_format)

    def to_dict(self):
        _dict = {
            u"@id": str(self.id),
            u"@type": u"Observation",
            u"library": {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, self.library_name)},
            u"sampleYear": self.sample_year,
            u"targetGroup": targetGroups[self.target_group],
            self.variable.key: self.value,
            u"published": self.date_created_str(),
            u"modified": self.date_modified_str()
        }
        if self.library_id:
            _dict[u"library"] = {u"@id": u"{}/library/{}".format(settings.BIBDB_BASE_URL, self.library_id)}
        else:
            _dict[u"library"] = {u"name": self.library_name}
        return _dict

    def __unicode__(self):
        return u"{} {} {} {} {}".format(self.library_name, self.sample_year, self.target_group, self.variable.key,
                                        self.value)


signals.pre_save.connect(Survey.store_version_and_update_date_modified, sender=Survey)
signals.pre_save.connect(Variable.store_version_and_update_date_modified, sender=Variable)
Variable.register_delete_rule(Variable, "replaced_by", NULLIFY)
Variable.register_delete_rule(Variable, "replaces", PULL)
signals.post_delete.connect(Variable.post_delete_actions, sender=Variable)
