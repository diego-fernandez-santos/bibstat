# -*- coding: utf-8 -*-
from libstat.models import Section, Group, Cell, Row, SurveyTemplate


def default_template_from_survey_response(response):
    rows = []
    for observation in response.observations:
        variable = observation.variable
        rows.append(Row(description=variable.label,
                        explanation="",
                        cells=[Cell(variable_key=variable.key, types=["text"])]))

    return SurveyTemplate(
        sections=[
            Section(
                title="",
                groups=[
                    Group(
                        description="",
                        columns=1,
                        headers=[],
                        rows=rows
                    )
                ]
            )
        ]
    )


survey_template = SurveyTemplate(
    key="",
    target_year="",
    organization_name="",
    municipality="",
    municipality_code="",
    head_authority="",
    respondent_name="",
    respondent_email="",
    respondent_phone="",
    website="",
    sections=[
        Section(
            title=u"Frågor om biblioteksorganisationen",
            groups=[
                Group(
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="1. Vad heter du som fyller i enkäten?",
                            explanation="Kontaktuppgift, om vi har någon fråga om lämnade uppgifter.",
                            cells=[Cell(variable_key=u"Namn01", types=["text"])]
                        ),
                        Row(
                            description="2. Vad har du för e-postadress?",
                            explanation="Vi skickar länk till rapporten när den publiceras. E-postadressen valideras automatiskt så att du fyllt i en användbar e-postadress, det går därför inte att skriva två adresser i fältet.",
                            cells=[Cell(variable_key=u"Epost01", types=['email', 'required'])]
                        ),
                        Row(
                            description="3. Vänligen fyll i ditt telefonnummer, inklusive riktnummer.",
                            explanation="Används så att vi kan kontakta dig om vi har några frågor om de lämnade uppgifterna",
                            cells=[Cell(variable_key=u"Tele01", types=["text"])]
                        ),
                        Row(
                            description="4. Vänligen skriv in länk till en webbplats där vi kan nå den biblioteksplan eller annan plan som styr er verksamhet.",
                            explanation="",
                            cells=[Cell(variable_key=u"Plan01", types=["text"])]
                        )
                    ]
                ),
                # TODO Välja bibliotek (5)
                Group(
                    description="",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="6. Enkätens uppgifter avser totalt antal bemannade servicesställen:",
                            explanation="",
                            cells=[Cell(variable_key=u"BemanService01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="7. Hur många av de bemannade serviceställena är integrerade bibliotek? Folk- och skolbibliotek alternativt forsknings- och sjukhusbibliotek alternativt folk- och forskningsbibliotek?",
                            explanation="",
                            cells=[Cell(variable_key=u"Integrerad01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="8. Till de bemannade servicesställen som den här enkäten avser är det kanske också kopplat ett antal obemannade utlåningsställen där vidare låneregistrering inte sker. Antal obemannade utlåningsställen och utlån till sådana:",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal obemannade utlåningsställen där vidare låneregistrering inte sker",
                            explanation="",
                            cells=[Cell(variable_key=u"Obeman01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal utlån till servicesställen/institutioner där vidare lånregistrering inte sker under kalenderåret (inkl. institutionslån och depositioner)",
                            explanation="",
                            cells=[Cell(variable_key=u"ObemanLan01", types=['required', 'integer'])]
                        )
                    ]
                ),
                Group(
                    description="9. Hur många bokbussar, bokbilar och bokbusshållplatser administrerar de uppräknade biblioteksenheterna? Om ni köper tjänsten av ett annat bibliotek som sköter administrationen uppge värdet 0 för att omöjliggöra dubbelräkning på riksnivå. Ange 0 om frågan inte är aktuell för er.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal bokbussar",
                            explanation="",
                            cells=[Cell(variable_key=u"Bokbuss01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbusshållplatser inom kommunen",
                            explanation="",
                            cells=[Cell(variable_key=u"BokbussHP01", types=['required', 'integer'])]
                        ),
                        Row(
                            description="Antal bokbilar, transportfordon",
                            explanation="",
                            cells=[Cell(variable_key=u"Bokbil01", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="10. Antal personer som biblioteket förväntas betjäna. Exempelvis antal elever (skolbibliotek), antal anställda (myndighetsbibliotek), antal helårsekvivalenter (forskningsbibliotek). Uppgift om antal kommuninnevånare behöver inte lämnas av folkbibliotek.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal personer",
                            explanation="",
                            cells=[Cell(variable_key=u"Population01", types=['integer'])]
                        )
                    ]
                ),
            ]
        ),
        Section(
            title=u"Frågor om bemanning och personal",  # Personkomm variabel för comment
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet personal. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="11. Hur många årsverken avsattes för biblioteksverksamheten under kalenderåret?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal årsverken bibliotekarier och dokumentalister",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke01", types=['sum', 'numeric'],
                                        sum_siblings=["Arsverke02", "Arsverke03", "Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken biblioteksassistenter och lärarbibliotekarier",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke02", types=['sum', 'numeric'],
                                        sum_siblings=["Arsverke01", "Arsverke03", "Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken specialister inom IT, information eller ämnessakkunniga, fackkunniga",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke03", types=['sum', 'numeric'],
                                        sum_siblings=["Arsverke01", "Arsverke02", "Arsverke04"])]
                        ),
                        Row(
                            description="Antal årsverken övrig personal inklusive kvällspersonal studentvakter, chaufförer, vaktmästare",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke04", types=['sum', 'numeric'],
                                        sum_siblings=["Arsverke01", "Arsverke02", "Arsverke03"])]
                        ),
                        Row(
                            description="Totalt antal årsverken avsatt bemanning för biblioteksverksamhet",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke99", types=['sum', 'numeric'],
                                        sum_of=["Arsverke01", "Arsverke02", "Arsverke03", "Arsverke04"])]
                        ),
                        Row(
                            description="- varav antal av dessa ovanstående årsverken var särskilt avsatta för barn och unga",
                            explanation="",
                            cells=[Cell(variable_key=u"Arsverke05", types=['required', 'numeric'])]
                        )
                    ]
                ),
                Group(
                    description="12. Hur många personer arbetade inom biblioteksverksamheten 31 mars?",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Antal anställda kvinnor",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Personer01", types=['sum', 'integer'], sum_siblings=['Personer02'])]
                        ),
                        Row(
                            description="Antal anställda män",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Personer02", types=['sum', 'integer'], sum_siblings=['Personer01'])]
                        ),
                        Row(
                            description="Totalt antal anställda personer",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Personer99", types=['sum', 'integer'],
                                     sum_of=[u"Personer01", u"Personer02"])]
                        )
                    ]
                )
            ]
        ),
        Section(
            title=u"Frågor om ekonomi",  # TODO Koppla comment till Ekonomikomm
            comment=u"Här kan du lämna eventuella kommentarer till frågeområdet ekonomi. Vänligen skriv inga siffror här.",
            groups=[
                Group(
                    description="13. Vilka utgifter hade biblioteksverksamheten under kalenderåret? Antal hela kronor inklusive mervärdesskatt. Avrunda inte till tusental. Vänligen skriv uppgifterna utan punkt, mellanslag eller kommatecken.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Inköp av tryckta medier och audiovisuella medier",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift01", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Inköp av virtuella e-baserade media och databaslicenser (exklusive kostnader för biblioteksdatasystemet)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift02", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift03", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Lönekostnader personal",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift03", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift04", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Kostnader för personalens kompetensutveckling",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift04", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift05", u"Utgift06"])]
                        ),
                        Row(
                            description="Lokalkostnader",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift05", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift06"])]
                        ),
                        Row(
                            description="Övriga driftskostnader som inte ingår i punkterna ovan (inklusive kostnader för bibliotekssystemet)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift06", types=['sum', 'integer'],
                                        sum_siblings=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05"])]
                        ),
                        Row(
                            description="Totala driftskostnader för biblioteksverksamheten (summan av ovanstående)",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift99", types=['sum', 'integer'],
                                        sum_of=[u"Utgift01", u"Utgift02", u"Utgift03", u"Utgift04", u"Utgift05",
                                                u"Utgift06"])]
                        ),
                        Row(
                            description="Investeringsutgifter, inklusive kapitalkostnader för dessa",
                            explanation="",
                            cells=[Cell(variable_key=u"Utgift07", types=['integer'])]
                        )
                    ]
                ),
                Group(
                    description="14. Vilka egengenererade intäkter hade biblioteksverksamheten? Antal hela kronor. Avrunda inte till tusental.",
                    columns=1,
                    headers=[],
                    rows=[
                        Row(
                            description="Projektmedel som inte kommer från huvudmannen eller moderorganisationen samt sponsring och gåvor",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt01", types=['sum', 'integer'],
                                     sum_siblings=[u"Intakt02", u"Intakt03"])]
                        ),
                        Row(
                            description="Försäljning av bibliotekstjänster och personalresurser till andra huvudmän, organisationer och företag",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt02", types=['sum', 'integer'],
                                     sum_siblings=[u"Intakt01", u"Intakt03"])]
                        ),
                        Row(
                            description="Försenings- och reservationsutgifter eller intäkter av uthyrningsverksamhet samt försäljning av böcker och profilprodukter",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Intakt03", types=['sum', 'integer'],
                                     sum_siblings=[u"Intakt01", u"Intakt02"])]
                        ),
                        Row(
                            description="Totalt antal kronor egengenererade inkomster",
                            explanation="",
                            cells=[Cell(variable_key=u"Intakt99", types=['sum', 'integer'],
                                        sum_of=[u"Intakt01", u"Intakt02", u"Intakt03"])]
                        ),
                    ]
                )
            ]
        ),
        Section(
            title=u"Bestånd – nyförvärv",
            comment=u"",
            groups=[
                Group(
                    description="15. Hur stort var det fysiska mediebeståndet och det elektroniska titelbeståndet 31 december och hur många fysiska nyförvärv gjordes under kalenderåret uppdelat på olika medietyper? Om ni bara kan få fram fysiskt bestånd genom att räkna hyllmeter, använd omräkningstal 40 medier per hyllmeter om ni beräknar antal utifrån uppgift om hyllmeter.",
                    columns=3,
                    headers=[u"Fysiskt bestånd antal medier/ enheter/ kapslar 31 december", u"– varav antal fysiskt nyförvärv under hela kalenderåret", u"Tillgång till antal licensierade elektroniska titlar (poster)"],
                    rows=[
                        Row(
                            description="Totalt antal böcker och seriella publikationer",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand101", types=['sum', 'integer'], sum_siblings=['Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand201", types=['sum', 'integer'], sum_siblings=['Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand301", types=['sum', 'integer'], sum_siblings=['Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="- varav kursböcker, studielitteratur, läromedel, skolböcker",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand102", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand202", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand302", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Ljudböcker",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand103", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand203", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand303", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Talböcker, DAISY",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand104", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand204", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand304", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Periodika, tidskrifter, antal löpande titlar",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand105", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand205", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand305", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Tidningar, dagstidningar, veckotidningar, löpande titlar",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand106", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand206", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand306", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Musik",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand107", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand207", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand307", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Film, TV, radio",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand108", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand208", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand308", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        ),
                        Row(
                            description="Mikrografiska dokument, mikrofilm, mikrofiche",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand109", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand209", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand210','Bestand211','Bestand212','Bestand213']),
                                ]
                        ),
                        Row(
                            description="Bild, grafiska och kartografiska dokument, OH, presentationer, fotografier",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand110", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand210", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand310", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand311','Bestand312','Bestand313']),
                                ]
                        ),
                        Row(
                            description="Manuskript, artiklar, patent, konferenshandlingar, festskrifter, rapporter, musiktryck, noter",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand111", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand211", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand311", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand312','Bestand313']),
                                ]
                        ),
                        Row(
                            description="Interaktiva medier, CD-ROM, Tv-spel, interaktiva läromedel, konsolspel, dataspel",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand112", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand113']),
                                Cell(variable_key=u"Bestand212", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand213']),
                                Cell(variable_key=u"Bestand312", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand313']),
                                ]
                        ),
                        Row(
                            description="Övriga medietyper som inte ingår i ovanstående kategorier",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand113", types=['sum', 'integer'], sum_siblings=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112']),
                                Cell(variable_key=u"Bestand213", types=['sum', 'integer'], sum_siblings=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212']),
                                Cell(variable_key=u"Bestand313", types=['sum', 'integer'], sum_siblings=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312']),
                                ]
                        ),
                        Row(
                            description="Totalt antal",
                            explanation="",
                            cells=[
                                Cell(variable_key=u"Bestand199", types=['sum', 'integer'], sum_of=['Bestand101','Bestand102','Bestand103','Bestand104','Bestand105','Bestand106','Bestand107','Bestand108','Bestand109','Bestand110','Bestand111','Bestand112','Bestand113']),
                                Cell(variable_key=u"Bestand299", types=['sum', 'integer'], sum_of=['Bestand201','Bestand202','Bestand203','Bestand204','Bestand205','Bestand206','Bestand207','Bestand208','Bestand209','Bestand210','Bestand211','Bestand212','Bestand213']),
                                Cell(variable_key=u"Bestand399", types=['sum', 'integer'], sum_of=['Bestand301','Bestand302','Bestand303','Bestand304','Bestand305','Bestand306','Bestand307','Bestand308','Bestand310','Bestand311','Bestand312','Bestand313'])
                            ]
                        )
                    ]
                )
            ]
        ),
    ]
)