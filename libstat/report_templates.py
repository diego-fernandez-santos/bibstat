# -*- coding: utf-8 -*-
from libstat.models import Variable


class ReportTemplate():
    @property
    def all_variable_keys(self):
        variable_keys = []
        for group in self.groups:
            for row in group.rows:
                if row.variable_key:
                    if row.variable_key not in variable_keys:
                        variable_keys.append(row.variable_key)
                if row.variable_keys:
                    for variable_key in row.variable_keys:
                        if variable_key not in variable_keys:
                            variable_keys.append(variable_key)
        return variable_keys

    def __init__(self, *args, **kwargs):
        self.groups = kwargs.pop("groups", None)


class Group():
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop("title", None)
        self.extra = kwargs.pop("extra", None)
        self.rows = kwargs.pop("rows", None)


class Row():
    def compute(self, values):
        if None in values:
            return None
        try:
            return apply(self.computation, values)
        except ZeroDivisionError:
            return None

    def __init__(self, *args, **kwargs):
        self.variable_key = kwargs.pop("variable_key", None)
        self.variable_keys = kwargs.pop("variable_keys", None)
        self.computation = kwargs.pop("computation", None)
        self.description = kwargs.pop("description", None)
        self.is_sum = kwargs.pop("is_sum", False)
        self.label_only = kwargs.pop("label_only", False)

        if self.description is None and self.variable_key is not None:
            variables = Variable.objects.filter(key=self.variable_key)
            self.description = variables[0].question_part if len(variables) == 1 else None


def report_template_2014():
    return ReportTemplate(groups=[
        Group(title=u"Organisation",
              rows=[
                  Row(variable_key=u"BemanService01"),
                  Row(variable_key=u"Integrerad01"),
                  Row(variable_key=u"Obeman01"),
                  Row(variable_key=u"ObemanLan01"),
                  Row(variable_key=u"Bokbuss01"),
                  Row(variable_key=u"BokbussHP01"),
                  Row(variable_key=u"Bokbil01"),
                  Row(variable_key=u"Population01"),
                  Row(variable_key=u"Population02"),
                  Row(variable_key=u"Population03"),
                  Row(description=u"Antal bemannade serviceställen per 1000 invånare",
                      computation=(lambda a, b: a / (b / 1000)),
                      variable_keys=[u"BemanService01", u"Population01"]),
                  Row(description=u"Antal integrerade serviceställen",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Integrerad01", u"BemanService01"]),
                  Row(
                      description=u"Medelantal utlån per servicesställe där vidare låneregistrering inte sker",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"ObemanLan01", u"Obeman01"])
              ]),
        Group(title=u"Årsverken",
              rows=[
                  Row(variable_key=u"Arsverke01"),
                  Row(variable_key=u"Arsverke02"),
                  Row(variable_key=u"Arsverke03"),
                  Row(variable_key=u"Arsverke04"),
                  Row(variable_key=u"Arsverke99", is_sum=True),
                  Row(variable_key=u"Arsverke05"),
                  Row(description=u"Andel årsverken för barn och unga",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Arsverke05", u"Arsverke99"]),
                  Row(description=u"Andel åreverken med bibliotekariekompetens",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Arsverke01", u"Arsverke99"]),
                  Row(description=u"Antal  årsverken per 1000 invånare",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Arsverke99", u"Population01"]),
                  Row(description=u"Antal årsverken per personer i målgruppen",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Arsverke99", u"Population02"]),
                  Row(description=u"Antal fysiska besök per årsverke",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Besok01", u"Arsverke99"]),
                  Row(description=u"Antal aktiva låntagare per årsverke",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Aktiv99", u"Arsverke99"]),
              ]),
        Group(title=u"Personal",
              rows=[
                  Row(variable_key=u"Personer01"),
                  Row(variable_key=u"Personer02"),
                  Row(variable_key=u"Personer99", is_sum=True),
                  Row(description=u"Andel anställda kvinnor",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Personer01", u"Personer99"]),
                  Row(description=u"Antal årsverken per person",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Arsverke99", u"Personer99"]),
              ]),
        Group(title=u"Ekonomi",
              rows=[
                  Row(variable_key=u"Utgift01"),
                  Row(variable_key=u"Utgift02"),
                  Row(variable_key=u"Utgift03"),
                  Row(variable_key=u"Utgift04"),
                  Row(variable_key=u"Utgift05"),
                  Row(variable_key=u"Utgift06"),
                  Row(variable_key=u"Utgift99", is_sum=True),
                  Row(variable_key=u"Utgift07"),
                  Row(description=u"Mediekostnad per invånare",
                      computation=(lambda a, b, c: (a + b) / c),
                      variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  Row(description=u"Mediekostnad per personer i målgruppen",
                      computation=(lambda a, b, c: (a + b) / c),
                      variable_keys=[u"Utgift01", u"Utgift02", u"Population01"]),
                  Row(description=u"Total driftkostnad per invånare",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Utgift99", u"Population01"]),
                  Row(description=u"Total driftkostnad per personer i målgruppen",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Utgift99", u"Population02"]),
                  Row(description=u"Andel kostnader för medier av total driftkostnad",
                      computation=(lambda a, b, c: (a + b) / c),
                      variable_keys=[u"Utgift01", u"Utgift02", u"Utgift98"]),
                  Row(description=u"Andel kostnader för personal av total driftkostnader",
                      computation=(lambda a, b, c: (a + b) / c),
                      variable_keys=[u"Utgift03", u"Utgift04", u"Utgift99"]),
                  Row(description=u"Andel kostnad för e-medier av totala driftskostnader",
                      computation=(lambda a, b, c: a / (b + c)),
                      variable_keys=[u"Utgift02", u"Utgift01", u"Utgift02"]),
              ]),
        Group(title=u"Egengenererade intäkter",
              rows=[
                  Row(variable_key=u"Intakt01"),
                  Row(variable_key=u"Intakt02"),
                  Row(variable_key=u"Intakt03"),
                  Row(variable_key=u"Intakt99", is_sum=True),
                  Row(
                      description=u"Andel egengenererade intäkter i förhållande till de totala driftskostnaderna",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Intakt99", u"Utgift99"])
              ]),
        Group(title=u"Fysiskt bestånd",
              extra=u"Andel av totalt bestånd",
              rows=[
                  Row(variable_key=u"Bestand101",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand101", "Bestand199"]),
                  Row(variable_key=u"Bestand102",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand102", "Bestand199"]),
                  Row(variable_key=u"Bestand103",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand103", "Bestand199"]),
                  Row(variable_key=u"Bestand104",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand104", "Bestand199"]),
                  Row(variable_key=u"Bestand105",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand105", "Bestand199"]),
                  Row(variable_key=u"Bestand106",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand106", "Bestand199"]),
                  Row(variable_key=u"Bestand107",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand107", "Bestand199"]),
                  Row(variable_key=u"Bestand108",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand108", "Bestand199"]),
                  Row(variable_key=u"Bestand109",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand109", "Bestand199"]),
                  Row(variable_key=u"Bestand110",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand110", "Bestand199"]),
                  Row(variable_key=u"Bestand111",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand111", "Bestand199"]),
                  Row(variable_key=u"Bestand112",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand112", "Bestand199"]),
                  Row(variable_key=u"Bestand113",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand113", "Bestand199"]),
                  Row(variable_key=u"Bestand199", is_sum=True,
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand199", "Bestand199"]),
                  Row(description=u"Totalt fysiskt mediebestånd per invånare",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Bestand199", u"Population01"]),
                  Row(description=u"Antal  tryckta böcker per invånare i beståndet",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Bestand101", u"Population01"])
              ]),
        Group(title=u"Fysiskt nyförvärv",
              extra=u"Andel nyförvärv av motsvarande bestånd",
              rows=[
                  Row(variable_key=u"Bestand201",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand201", "Bestand299"]),
                  Row(variable_key=u"Bestand202",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand202", "Bestand299"]),
                  Row(variable_key=u"Bestand203",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand203", "Bestand299"]),
                  Row(variable_key=u"Bestand204",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand204", "Bestand299"]),
                  Row(variable_key=u"Bestand205",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand205", "Bestand299"]),
                  Row(variable_key=u"Bestand206",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand206", "Bestand299"]),
                  Row(variable_key=u"Bestand207",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand207", "Bestand299"]),
                  Row(variable_key=u"Bestand208",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand208", "Bestand299"]),
                  Row(variable_key=u"Bestand209",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand209", "Bestand299"]),
                  Row(variable_key=u"Bestand210",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand210", "Bestand299"]),
                  Row(variable_key=u"Bestand211",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand211", "Bestand299"]),
                  Row(variable_key=u"Bestand212",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand212", "Bestand299"]),
                  Row(variable_key=u"Bestand213",
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand213", "Bestand299"]),
                  Row(variable_key=u"Bestand299", is_sum=True,
                      computation=(lambda a, b: a / b),
                      variable_keys=["Bestand299", "Bestand299"]),
                  Row(description=u"Antal fysiska  nyförvärv per 1000 invånare (ej tidn.tidskr.)",
                      computation=(lambda a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11:
                                   (a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10) / (a11 / 1000)),
                      variable_keys=[u"Bestand101", u"Bestand103", u"Bestand104", u"Bestand107", u"Bestand108",
                                     u"Bestand109", u"Bestand110", u"Bestand111", u"Bestand112", u"Bestand113",
                                     u"Population01"])
              ]),
        Group(title=u"Elektroniskt titelbestånd",
              rows=[
                  Row(variable_key=u"Bestand301"),
                  Row(variable_key=u"Bestand302"),
                  Row(variable_key=u"Bestand303"),
                  Row(variable_key=u"Bestand304"),
                  Row(variable_key=u"Bestand305"),
                  Row(variable_key=u"Bestand306"),
                  Row(variable_key=u"Bestand307"),
                  Row(variable_key=u"Bestand308"),
                  Row(variable_key=u"Bestand310"),
                  Row(variable_key=u"Bestand311"),
                  Row(variable_key=u"Bestand312"),
                  Row(variable_key=u"Bestand313"),
                  Row(variable_key=u"Bestand399", is_sum=True),
                  Row(description=u"Andel e-bokstitlar av det totala elektroniska titelbeståndet",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Bestand301", u"Bestand399"])
              ]),
        Group(title=u"Barnmedier",
              rows=[
                  Row(variable_key=u"Barn01"),
                  Row(variable_key=u"Barn02"),
                  Row(variable_key=u"Barn03"),
                  Row(description=u"Antal bestånd barnböcker per barn",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Barn01", u"Population03"]),
                  Row(description=u"Andel tryckta barnmedier av motsvarande totalbestånd",
                      computation=(lambda a, b, c: a / (b + c)),
                      variable_keys=[u"Barn01", u"Bestand101", u"Bestand105"]),
                  Row(description=u"Andel nyförvärv tryckta barnmedier av motsvarande bestånd",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Barn01", u"Barn02"]),
                  Row(description=u"Andel nyförvärv tryckta barnmedier av motsvarande bestånd",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Barn03", u"Barn01"]),
                  Row(description=u"Antal barnutlån per barninvånare",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"Barn03", u"Population03"]),
              ]),
        Group(title=u"",
              rows=[
                  Row(variable_key=u"HCG01"),
                  Row(variable_key=u"Ref01"),
              ]),
        Group(title=u"Personer med läsnedsättning",
              rows=[
                  Row(variable_key=u"LasnedBest01"),
                  Row(variable_key=u"LasnedUtlan01"),
                  Row(description=u"Andel utlån av anpassade medier av motsvarande bestånd",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"LasnedUtlan01", u"LasnedBest01"]),
                  Row(description=u"Andel anpassade medier av totala fysiska beståndet ",
                      computation=(lambda a, b: a / b),
                      variable_keys=[u"LasnedBest01", u"Bestand399"]),
              ]),
        Group(title=u"Medier på olika språk",
              rows=[
                  Row(description=u"Titlar på svenska språket", label_only=True),
                  Row(variable_key=u"Titlar101"),
                  Row(variable_key=u"Titlar102"),
                  Row(variable_key=u"Titlar199", is_sum=True),
                  Row(description=u"Titlar på nationella minoritetsspråk", label_only=True),
                  Row(variable_key=u"Titlar201"),
                  Row(variable_key=u"Titlar202"),
                  Row(variable_key=u"Titlar299", is_sum=True),
                  Row(description=u"Titlar på utländska språk", label_only=True),
                  Row(variable_key=u"Titlar301"),
                  Row(variable_key=u"Titlar302"),
                  Row(variable_key=u"Titlar399", is_sum=True),
                  Row(description=u"Totalt antal titlar på olika medietyper", label_only=True),
                  Row(variable_key=u"Titlar497"),
                  Row(variable_key=u"Titlar498"),
                  Row(variable_key=u"Titlar499", is_sum=True),
              ]),

    ])
