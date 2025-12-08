#!/usr/bin/env python3
"""
Seed script for Latin verbs with multiple tenses (Praesens, Imperfectum, Perfectum, Futurum):
habere (to have), esse (to be), velle (to want),
scandere (to climb), natare (to swim), ire (to go), currere (to run),
canere (to sing), saltare (to dance), posse (to be able to/can),
lavare (to wash), rogare (to ask), amare (to love), videre (to see),
audire (to hear), dicere (to say), facere (to do/make), venire (to come),
scribere (to write), legere (to read), dare (to give), capere (to take),
ambulare (to walk)
"""

from app import create_app, db
from app.models import Entry, Language, List


def seed_extended_latin_verbs():
    app = create_app()

    with app.app_context():
        verbs_data = [
            # HABERE - to have (2nd conjugation)
            {
                "name": "habere - to have (Praesens)",
                "conjugations": [
                    ("habeo", "I have"),
                    ("habes", "you have"),
                    ("habet", "he/she/it has"),
                    ("habemus", "we have"),
                    ("habetis", "you (plural) have"),
                    ("habent", "they have"),
                ],
            },
            {
                "name": "habere - to have (Imperfectum)",
                "conjugations": [
                    ("habebam", "I had / I was having"),
                    ("habebas", "you had / you were having"),
                    ("habebat", "he/she/it had / was having"),
                    ("habebamus", "we had / we were having"),
                    ("habebatis", "you (plural) had / were having"),
                    ("habebant", "they had / they were having"),
                ],
            },
            {
                "name": "habere - to have (Perfectum)",
                "conjugations": [
                    ("habui", "I have had / I had"),
                    ("habuisti", "you have had / you had"),
                    ("habuit", "he/she/it has had / had"),
                    ("habuimus", "we have had / we had"),
                    ("habuistis", "you (plural) have had / had"),
                    ("habuerunt", "they have had / they had"),
                ],
            },
            {
                "name": "habere - to have (Futurum)",
                "conjugations": [
                    ("habebo", "I will have"),
                    ("habebis", "you will have"),
                    ("habebit", "he/she/it will have"),
                    ("habebimus", "we will have"),
                    ("habebitis", "you (plural) will have"),
                    ("habebunt", "they will have"),
                ],
            },
            # ESSE - to be (irregular)
            {
                "name": "esse - to be (Praesens)",
                "conjugations": [
                    ("sum", "I am"),
                    ("es", "you are"),
                    ("est", "he/she/it is"),
                    ("sumus", "we are"),
                    ("estis", "you (plural) are"),
                    ("sunt", "they are"),
                ],
            },
            {
                "name": "esse - to be (Imperfectum)",
                "conjugations": [
                    ("eram", "I was"),
                    ("eras", "you were"),
                    ("erat", "he/she/it was"),
                    ("eramus", "we were"),
                    ("eratis", "you (plural) were"),
                    ("erant", "they were"),
                ],
            },
            {
                "name": "esse - to be (Perfectum)",
                "conjugations": [
                    ("fui", "I have been / I was"),
                    ("fuisti", "you have been / you were"),
                    ("fuit", "he/she/it has been / was"),
                    ("fuimus", "we have been / we were"),
                    ("fuistis", "you (plural) have been / were"),
                    ("fuerunt", "they have been / they were"),
                ],
            },
            {
                "name": "esse - to be (Futurum)",
                "conjugations": [
                    ("ero", "I will be"),
                    ("eris", "you will be"),
                    ("erit", "he/she/it will be"),
                    ("erimus", "we will be"),
                    ("eritis", "you (plural) will be"),
                    ("erunt", "they will be"),
                ],
            },
            # VELLE - to want (irregular)
            {
                "name": "velle - to want (Praesens)",
                "conjugations": [
                    ("volo", "I want"),
                    ("vis", "you want"),
                    ("vult", "he/she/it wants"),
                    ("volumus", "we want"),
                    ("vultis", "you (plural) want"),
                    ("volunt", "they want"),
                ],
            },
            {
                "name": "velle - to want (Imperfectum)",
                "conjugations": [
                    ("volebam", "I wanted / I was wanting"),
                    ("volebas", "you wanted / you were wanting"),
                    ("volebat", "he/she/it wanted / was wanting"),
                    ("volebamus", "we wanted / we were wanting"),
                    ("volebatis", "you (plural) wanted / were wanting"),
                    ("volebant", "they wanted / they were wanting"),
                ],
            },
            {
                "name": "velle - to want (Perfectum)",
                "conjugations": [
                    ("volui", "I have wanted / I wanted"),
                    ("voluisti", "you have wanted / you wanted"),
                    ("voluit", "he/she/it has wanted / wanted"),
                    ("voluimus", "we have wanted / we wanted"),
                    ("voluistis", "you (plural) have wanted / wanted"),
                    ("voluerunt", "they have wanted / they wanted"),
                ],
            },
            {
                "name": "velle - to want (Futurum)",
                "conjugations": [
                    ("volam", "I will want"),
                    ("voles", "you will want"),
                    ("volet", "he/she/it will want"),
                    ("volemus", "we will want"),
                    ("voletis", "you (plural) will want"),
                    ("volent", "they will want"),
                ],
            },
            # SCANDERE - to climb (3rd conjugation)
            {
                "name": "scandere - to climb (Praesens)",
                "conjugations": [
                    ("scando", "I climb"),
                    ("scandis", "you climb"),
                    ("scandit", "he/she/it climbs"),
                    ("scandimus", "we climb"),
                    ("scanditis", "you (plural) climb"),
                    ("scandunt", "they climb"),
                ],
            },
            {
                "name": "scandere - to climb (Imperfectum)",
                "conjugations": [
                    ("scandebam", "I was climbing"),
                    ("scandebas", "you were climbing"),
                    ("scandebat", "he/she/it was climbing"),
                    ("scandebamus", "we were climbing"),
                    ("scandebatis", "you (plural) were climbing"),
                    ("scandebant", "they were climbing"),
                ],
            },
            {
                "name": "scandere - to climb (Perfectum)",
                "conjugations": [
                    ("scandi", "I have climbed / I climbed"),
                    ("scandisti", "you have climbed / you climbed"),
                    ("scandit", "he/she/it has climbed / climbed"),
                    ("scandimus", "we have climbed / we climbed"),
                    ("scandistis", "you (plural) have climbed / climbed"),
                    ("scanderunt", "they have climbed / they climbed"),
                ],
            },
            {
                "name": "scandere - to climb (Futurum)",
                "conjugations": [
                    ("scandam", "I will climb"),
                    ("scandes", "you will climb"),
                    ("scandet", "he/she/it will climb"),
                    ("scandemus", "we will climb"),
                    ("scandetis", "you (plural) will climb"),
                    ("scandent", "they will climb"),
                ],
            },
            # NATARE - to swim (1st conjugation)
            {
                "name": "natare - to swim (Praesens)",
                "conjugations": [
                    ("nato", "I swim"),
                    ("natas", "you swim"),
                    ("natat", "he/she/it swims"),
                    ("natamus", "we swim"),
                    ("natatis", "you (plural) swim"),
                    ("natant", "they swim"),
                ],
            },
            {
                "name": "natare - to swim (Imperfectum)",
                "conjugations": [
                    ("natabam", "I was swimming"),
                    ("natabas", "you were swimming"),
                    ("natabat", "he/she/it was swimming"),
                    ("natabamus", "we were swimming"),
                    ("natabatis", "you (plural) were swimming"),
                    ("natabant", "they were swimming"),
                ],
            },
            {
                "name": "natare - to swim (Perfectum)",
                "conjugations": [
                    ("natavi", "I have swum / I swam"),
                    ("natavisti", "you have swum / you swam"),
                    ("natavit", "he/she/it has swum / swam"),
                    ("natavimus", "we have swum / we swam"),
                    ("natavistis", "you (plural) have swum / swam"),
                    ("nataverunt", "they have swum / they swam"),
                ],
            },
            {
                "name": "natare - to swim (Futurum)",
                "conjugations": [
                    ("natabo", "I will swim"),
                    ("natabis", "you will swim"),
                    ("natabit", "he/she/it will swim"),
                    ("natabimus", "we will swim"),
                    ("natabitis", "you (plural) will swim"),
                    ("natabunt", "they will swim"),
                ],
            },
            # IRE - to go (irregular)
            {
                "name": "ire - to go (Praesens)",
                "conjugations": [
                    ("eo", "I go"),
                    ("is", "you go"),
                    ("it", "he/she/it goes"),
                    ("imus", "we go"),
                    ("itis", "you (plural) go"),
                    ("eunt", "they go"),
                ],
            },
            {
                "name": "ire - to go (Imperfectum)",
                "conjugations": [
                    ("ibam", "I was going"),
                    ("ibas", "you were going"),
                    ("ibat", "he/she/it was going"),
                    ("ibamus", "we were going"),
                    ("ibatis", "you (plural) were going"),
                    ("ibant", "they were going"),
                ],
            },
            {
                "name": "ire - to go (Perfectum)",
                "conjugations": [
                    ("ivi", "I have gone / I went"),
                    ("ivisti", "you have gone / you went"),
                    ("ivit", "he/she/it has gone / went"),
                    ("ivimus", "we have gone / we went"),
                    ("ivistis", "you (plural) have gone / went"),
                    ("iverunt", "they have gone / they went"),
                ],
            },
            {
                "name": "ire - to go (Futurum)",
                "conjugations": [
                    ("ibo", "I will go"),
                    ("ibis", "you will go"),
                    ("ibit", "he/she/it will go"),
                    ("ibimus", "we will go"),
                    ("ibitis", "you (plural) will go"),
                    ("ibunt", "they will go"),
                ],
            },
            # CURRERE - to run (3rd conjugation)
            {
                "name": "currere - to run (Praesens)",
                "conjugations": [
                    ("curro", "I run"),
                    ("curris", "you run"),
                    ("currit", "he/she/it runs"),
                    ("currimus", "we run"),
                    ("curritis", "you (plural) run"),
                    ("currunt", "they run"),
                ],
            },
            {
                "name": "currere - to run (Imperfectum)",
                "conjugations": [
                    ("currebam", "I was running"),
                    ("currebas", "you were running"),
                    ("currebat", "he/she/it was running"),
                    ("currebamus", "we were running"),
                    ("currebatis", "you (plural) were running"),
                    ("currebant", "they were running"),
                ],
            },
            {
                "name": "currere - to run (Perfectum)",
                "conjugations": [
                    ("cucurri", "I have run / I ran"),
                    ("cucurristi", "you have run / you ran"),
                    ("cucurrit", "he/she/it has run / ran"),
                    ("cucurrimus", "we have run / we ran"),
                    ("cucurristis", "you (plural) have run / ran"),
                    ("cucurrerunt", "they have run / they ran"),
                ],
            },
            {
                "name": "currere - to run (Futurum)",
                "conjugations": [
                    ("curram", "I will run"),
                    ("curres", "you will run"),
                    ("curret", "he/she/it will run"),
                    ("curremus", "we will run"),
                    ("curretis", "you (plural) will run"),
                    ("current", "they will run"),
                ],
            },
            # CANERE - to sing (3rd conjugation)
            {
                "name": "canere - to sing (Praesens)",
                "conjugations": [
                    ("cano", "I sing"),
                    ("canis", "you sing"),
                    ("canit", "he/she/it sings"),
                    ("canimus", "we sing"),
                    ("canitis", "you (plural) sing"),
                    ("canunt", "they sing"),
                ],
            },
            {
                "name": "canere - to sing (Imperfectum)",
                "conjugations": [
                    ("canebam", "I was singing"),
                    ("canebas", "you were singing"),
                    ("canebat", "he/she/it was singing"),
                    ("canebamus", "we were singing"),
                    ("canebatis", "you (plural) were singing"),
                    ("canebant", "they were singing"),
                ],
            },
            {
                "name": "canere - to sing (Perfectum)",
                "conjugations": [
                    ("cecini", "I have sung / I sang"),
                    ("cecinisti", "you have sung / you sang"),
                    ("cecinit", "he/she/it has sung / sang"),
                    ("cecinimus", "we have sung / we sang"),
                    ("cecinistis", "you (plural) have sung / sang"),
                    ("cecinerunt", "they have sung / they sang"),
                ],
            },
            {
                "name": "canere - to sing (Futurum)",
                "conjugations": [
                    ("canam", "I will sing"),
                    ("canes", "you will sing"),
                    ("canet", "he/she/it will sing"),
                    ("canemus", "we will sing"),
                    ("canetis", "you (plural) will sing"),
                    ("canent", "they will sing"),
                ],
            },
            # SALTARE - to dance (1st conjugation)
            {
                "name": "saltare - to dance (Praesens)",
                "conjugations": [
                    ("salto", "I dance"),
                    ("saltas", "you dance"),
                    ("saltat", "he/she/it dances"),
                    ("saltamus", "we dance"),
                    ("saltatis", "you (plural) dance"),
                    ("saltant", "they dance"),
                ],
            },
            {
                "name": "saltare - to dance (Imperfectum)",
                "conjugations": [
                    ("saltabam", "I was dancing"),
                    ("saltabas", "you were dancing"),
                    ("saltabat", "he/she/it was dancing"),
                    ("saltabamus", "we were dancing"),
                    ("saltabatis", "you (plural) were dancing"),
                    ("saltabant", "they were dancing"),
                ],
            },
            {
                "name": "saltare - to dance (Perfectum)",
                "conjugations": [
                    ("saltavi", "I have danced / I danced"),
                    ("saltavisti", "you have danced / you danced"),
                    ("saltavit", "he/she/it has danced / danced"),
                    ("saltavimus", "we have danced / we danced"),
                    ("saltavistis", "you (plural) have danced / danced"),
                    ("saltaverunt", "they have danced / they danced"),
                ],
            },
            {
                "name": "saltare - to dance (Futurum)",
                "conjugations": [
                    ("saltabo", "I will dance"),
                    ("saltabis", "you will dance"),
                    ("saltabit", "he/she/it will dance"),
                    ("saltabimus", "we will dance"),
                    ("saltabitis", "you (plural) will dance"),
                    ("saltabunt", "they will dance"),
                ],
            },
            # POSSE - to be able to/can (irregular)
            {
                "name": "posse - to be able to/can (Praesens)",
                "conjugations": [
                    ("possum", "I can/am able"),
                    ("potes", "you can/are able"),
                    ("potest", "he/she/it can/is able"),
                    ("possumus", "we can/are able"),
                    ("potestis", "you (plural) can/are able"),
                    ("possunt", "they can/are able"),
                ],
            },
            {
                "name": "posse - to be able to/can (Imperfectum)",
                "conjugations": [
                    ("poteram", "I could/was able"),
                    ("poteras", "you could/were able"),
                    ("poterat", "he/she/it could/was able"),
                    ("poteramus", "we could/were able"),
                    ("poteratis", "you (plural) could/were able"),
                    ("poterant", "they could/were able"),
                ],
            },
            {
                "name": "posse - to be able to/can (Perfectum)",
                "conjugations": [
                    ("potui", "I have been able / I could"),
                    ("potuisti", "you have been able / you could"),
                    ("potuit", "he/she/it has been able / could"),
                    ("potuimus", "we have been able / we could"),
                    ("potuistis", "you (plural) have been able / could"),
                    ("potuerunt", "they have been able / they could"),
                ],
            },
            {
                "name": "posse - to be able to/can (Futurum)",
                "conjugations": [
                    ("potero", "I will be able"),
                    ("poteris", "you will be able"),
                    ("poterit", "he/she/it will be able"),
                    ("poterimus", "we will be able"),
                    ("poteritis", "you (plural) will be able"),
                    ("poterunt", "they will be able"),
                ],
            },
            # LAVARE - to wash (1st conjugation)
            {
                "name": "lavare - to wash (Praesens)",
                "conjugations": [
                    ("lavo", "I wash"),
                    ("lavas", "you wash"),
                    ("lavat", "he/she/it washes"),
                    ("lavamus", "we wash"),
                    ("lavatis", "you (plural) wash"),
                    ("lavant", "they wash"),
                ],
            },
            {
                "name": "lavare - to wash (Imperfectum)",
                "conjugations": [
                    ("lavabam", "I was washing"),
                    ("lavabas", "you were washing"),
                    ("lavabat", "he/she/it was washing"),
                    ("lavabamus", "we were washing"),
                    ("lavabatis", "you (plural) were washing"),
                    ("lavabant", "they were washing"),
                ],
            },
            {
                "name": "lavare - to wash (Perfectum)",
                "conjugations": [
                    ("lavi", "I have washed / I washed"),
                    ("lavisti", "you have washed / you washed"),
                    ("lavit", "he/she/it has washed / washed"),
                    ("lavimus", "we have washed / we washed"),
                    ("lavistis", "you (plural) have washed / washed"),
                    ("laverunt", "they have washed / they washed"),
                ],
            },
            {
                "name": "lavare - to wash (Futurum)",
                "conjugations": [
                    ("lavabo", "I will wash"),
                    ("lavabis", "you will wash"),
                    ("lavabit", "he/she/it will wash"),
                    ("lavabimus", "we will wash"),
                    ("lavabitis", "you (plural) will wash"),
                    ("lavabunt", "they will wash"),
                ],
            },
            # ROGARE - to ask (1st conjugation)
            {
                "name": "rogare - to ask (Praesens)",
                "conjugations": [
                    ("rogo", "I ask"),
                    ("rogas", "you ask"),
                    ("rogat", "he/she/it asks"),
                    ("rogamus", "we ask"),
                    ("rogatis", "you (plural) ask"),
                    ("rogant", "they ask"),
                ],
            },
            {
                "name": "rogare - to ask (Imperfectum)",
                "conjugations": [
                    ("rogabam", "I was asking"),
                    ("rogabas", "you were asking"),
                    ("rogabat", "he/she/it was asking"),
                    ("rogabamus", "we were asking"),
                    ("rogabatis", "you (plural) were asking"),
                    ("rogabant", "they were asking"),
                ],
            },
            {
                "name": "rogare - to ask (Perfectum)",
                "conjugations": [
                    ("rogavi", "I have asked / I asked"),
                    ("rogavisti", "you have asked / you asked"),
                    ("rogavit", "he/she/it has asked / asked"),
                    ("rogavimus", "we have asked / we asked"),
                    ("rogavistis", "you (plural) have asked / asked"),
                    ("rogaverunt", "they have asked / they asked"),
                ],
            },
            {
                "name": "rogare - to ask (Futurum)",
                "conjugations": [
                    ("rogabo", "I will ask"),
                    ("rogabis", "you will ask"),
                    ("rogabit", "he/she/it will ask"),
                    ("rogabimus", "we will ask"),
                    ("rogabitis", "you (plural) will ask"),
                    ("rogabunt", "they will ask"),
                ],
            },
            # AMARE - to love (1st conjugation)
            {
                "name": "amare - to love (Praesens)",
                "conjugations": [
                    ("amo", "I love"),
                    ("amas", "you love"),
                    ("amat", "he/she/it loves"),
                    ("amamus", "we love"),
                    ("amatis", "you (plural) love"),
                    ("amant", "they love"),
                ],
            },
            {
                "name": "amare - to love (Imperfectum)",
                "conjugations": [
                    ("amabam", "I was loving"),
                    ("amabas", "you were loving"),
                    ("amabat", "he/she/it was loving"),
                    ("amabamus", "we were loving"),
                    ("amabatis", "you (plural) were loving"),
                    ("amabant", "they were loving"),
                ],
            },
            {
                "name": "amare - to love (Perfectum)",
                "conjugations": [
                    ("amavi", "I have loved / I loved"),
                    ("amavisti", "you have loved / you loved"),
                    ("amavit", "he/she/it has loved / loved"),
                    ("amavimus", "we have loved / we loved"),
                    ("amavistis", "you (plural) have loved / loved"),
                    ("amaverunt", "they have loved / they loved"),
                ],
            },
            {
                "name": "amare - to love (Futurum)",
                "conjugations": [
                    ("amabo", "I will love"),
                    ("amabis", "you will love"),
                    ("amabit", "he/she/it will love"),
                    ("amabimus", "we will love"),
                    ("amabitis", "you (plural) will love"),
                    ("amabunt", "they will love"),
                ],
            },
            # VIDERE - to see (2nd conjugation)
            {
                "name": "videre - to see (Praesens)",
                "conjugations": [
                    ("video", "I see"),
                    ("vides", "you see"),
                    ("videt", "he/she/it sees"),
                    ("videmus", "we see"),
                    ("videtis", "you (plural) see"),
                    ("vident", "they see"),
                ],
            },
            {
                "name": "videre - to see (Imperfectum)",
                "conjugations": [
                    ("videbam", "I was seeing"),
                    ("videbas", "you were seeing"),
                    ("videbat", "he/she/it was seeing"),
                    ("videbamus", "we were seeing"),
                    ("videbatis", "you (plural) were seeing"),
                    ("videbant", "they were seeing"),
                ],
            },
            {
                "name": "videre - to see (Perfectum)",
                "conjugations": [
                    ("vidi", "I have seen / I saw"),
                    ("vidisti", "you have seen / you saw"),
                    ("vidit", "he/she/it has seen / saw"),
                    ("vidimus", "we have seen / we saw"),
                    ("vidistis", "you (plural) have seen / saw"),
                    ("viderunt", "they have seen / they saw"),
                ],
            },
            {
                "name": "videre - to see (Futurum)",
                "conjugations": [
                    ("videbo", "I will see"),
                    ("videbis", "you will see"),
                    ("videbit", "he/she/it will see"),
                    ("videbimus", "we will see"),
                    ("videbitis", "you (plural) will see"),
                    ("videbunt", "they will see"),
                ],
            },
            # AUDIRE - to hear (4th conjugation)
            {
                "name": "audire - to hear (Praesens)",
                "conjugations": [
                    ("audio", "I hear"),
                    ("audis", "you hear"),
                    ("audit", "he/she/it hears"),
                    ("audimus", "we hear"),
                    ("auditis", "you (plural) hear"),
                    ("audiunt", "they hear"),
                ],
            },
            {
                "name": "audire - to hear (Imperfectum)",
                "conjugations": [
                    ("audiebam", "I was hearing"),
                    ("audiebas", "you were hearing"),
                    ("audiebat", "he/she/it was hearing"),
                    ("audiebamus", "we were hearing"),
                    ("audiebatis", "you (plural) were hearing"),
                    ("audiebant", "they were hearing"),
                ],
            },
            {
                "name": "audire - to hear (Perfectum)",
                "conjugations": [
                    ("audivi", "I have heard / I heard"),
                    ("audivisti", "you have heard / you heard"),
                    ("audivit", "he/she/it has heard / heard"),
                    ("audivimus", "we have heard / we heard"),
                    ("audivistis", "you (plural) have heard / heard"),
                    ("audiverunt", "they have heard / they heard"),
                ],
            },
            {
                "name": "audire - to hear (Futurum)",
                "conjugations": [
                    ("audiam", "I will hear"),
                    ("audies", "you will hear"),
                    ("audiet", "he/she/it will hear"),
                    ("audiemus", "we will hear"),
                    ("audietis", "you (plural) will hear"),
                    ("audient", "they will hear"),
                ],
            },
            # DICERE - to say (3rd conjugation)
            {
                "name": "dicere - to say (Praesens)",
                "conjugations": [
                    ("dico", "I say"),
                    ("dicis", "you say"),
                    ("dicit", "he/she/it says"),
                    ("dicimus", "we say"),
                    ("dicitis", "you (plural) say"),
                    ("dicunt", "they say"),
                ],
            },
            {
                "name": "dicere - to say (Imperfectum)",
                "conjugations": [
                    ("dicebam", "I was saying"),
                    ("dicebas", "you were saying"),
                    ("dicebat", "he/she/it was saying"),
                    ("dicebamus", "we were saying"),
                    ("dicebatis", "you (plural) were saying"),
                    ("dicebant", "they were saying"),
                ],
            },
            {
                "name": "dicere - to say (Perfectum)",
                "conjugations": [
                    ("dixi", "I have said / I said"),
                    ("dixisti", "you have said / you said"),
                    ("dixit", "he/she/it has said / said"),
                    ("diximus", "we have said / we said"),
                    ("dixistis", "you (plural) have said / said"),
                    ("dixerunt", "they have said / they said"),
                ],
            },
            {
                "name": "dicere - to say (Futurum)",
                "conjugations": [
                    ("dicam", "I will say"),
                    ("dices", "you will say"),
                    ("dicet", "he/she/it will say"),
                    ("dicemus", "we will say"),
                    ("dicetis", "you (plural) will say"),
                    ("dicent", "they will say"),
                ],
            },
            # FACERE - to do/make (3rd conjugation -io)
            {
                "name": "facere - to do/make (Praesens)",
                "conjugations": [
                    ("facio", "I do/make"),
                    ("facis", "you do/make"),
                    ("facit", "he/she/it does/makes"),
                    ("facimus", "we do/make"),
                    ("facitis", "you (plural) do/make"),
                    ("faciunt", "they do/make"),
                ],
            },
            {
                "name": "facere - to do/make (Imperfectum)",
                "conjugations": [
                    ("faciebam", "I was doing/making"),
                    ("faciebas", "you were doing/making"),
                    ("faciebat", "he/she/it was doing/making"),
                    ("faciebamus", "we were doing/making"),
                    ("faciebatis", "you (plural) were doing/making"),
                    ("faciebant", "they were doing/making"),
                ],
            },
            {
                "name": "facere - to do/make (Perfectum)",
                "conjugations": [
                    ("feci", "I have done/made / I did/made"),
                    ("fecisti", "you have done/made / you did/made"),
                    ("fecit", "he/she/it has done/made / did/made"),
                    ("fecimus", "we have done/made / we did/made"),
                    ("fecistis", "you (plural) have done/made / did/made"),
                    ("fecerunt", "they have done/made / they did/made"),
                ],
            },
            {
                "name": "facere - to do/make (Futurum)",
                "conjugations": [
                    ("faciam", "I will do/make"),
                    ("facies", "you will do/make"),
                    ("faciet", "he/she/it will do/make"),
                    ("faciemus", "we will do/make"),
                    ("facietis", "you (plural) will do/make"),
                    ("facient", "they will do/make"),
                ],
            },
            # VENIRE - to come (4th conjugation)
            {
                "name": "venire - to come (Praesens)",
                "conjugations": [
                    ("venio", "I come"),
                    ("venis", "you come"),
                    ("venit", "he/she/it comes"),
                    ("venimus", "we come"),
                    ("venitis", "you (plural) come"),
                    ("veniunt", "they come"),
                ],
            },
            {
                "name": "venire - to come (Imperfectum)",
                "conjugations": [
                    ("veniebam", "I was coming"),
                    ("veniebas", "you were coming"),
                    ("veniebat", "he/she/it was coming"),
                    ("veniebamus", "we were coming"),
                    ("veniebatis", "you (plural) were coming"),
                    ("veniebant", "they were coming"),
                ],
            },
            {
                "name": "venire - to come (Perfectum)",
                "conjugations": [
                    ("veni", "I have come / I came"),
                    ("venisti", "you have come / you came"),
                    ("venit", "he/she/it has come / came"),
                    ("venimus", "we have come / we came"),
                    ("venistis", "you (plural) have come / came"),
                    ("venerunt", "they have come / they came"),
                ],
            },
            {
                "name": "venire - to come (Futurum)",
                "conjugations": [
                    ("veniam", "I will come"),
                    ("venies", "you will come"),
                    ("veniet", "he/she/it will come"),
                    ("veniemus", "we will come"),
                    ("venietis", "you (plural) will come"),
                    ("venient", "they will come"),
                ],
            },
            # SCRIBERE - to write (3rd conjugation)
            {
                "name": "scribere - to write (Praesens)",
                "conjugations": [
                    ("scribo", "I write"),
                    ("scribis", "you write"),
                    ("scribit", "he/she/it writes"),
                    ("scribimus", "we write"),
                    ("scribitis", "you (plural) write"),
                    ("scribunt", "they write"),
                ],
            },
            {
                "name": "scribere - to write (Imperfectum)",
                "conjugations": [
                    ("scribebam", "I was writing"),
                    ("scribebas", "you were writing"),
                    ("scribebat", "he/she/it was writing"),
                    ("scribebamus", "we were writing"),
                    ("scribebatis", "you (plural) were writing"),
                    ("scribebant", "they were writing"),
                ],
            },
            {
                "name": "scribere - to write (Perfectum)",
                "conjugations": [
                    ("scripsi", "I have written / I wrote"),
                    ("scripsisti", "you have written / you wrote"),
                    ("scripsit", "he/she/it has written / wrote"),
                    ("scripsimus", "we have written / we wrote"),
                    ("scripsistis", "you (plural) have written / wrote"),
                    ("scripserunt", "they have written / they wrote"),
                ],
            },
            {
                "name": "scribere - to write (Futurum)",
                "conjugations": [
                    ("scribam", "I will write"),
                    ("scribes", "you will write"),
                    ("scribet", "he/she/it will write"),
                    ("scribemus", "we will write"),
                    ("scribetis", "you (plural) will write"),
                    ("scribent", "they will write"),
                ],
            },
            # LEGERE - to read (3rd conjugation)
            {
                "name": "legere - to read (Praesens)",
                "conjugations": [
                    ("lego", "I read"),
                    ("legis", "you read"),
                    ("legit", "he/she/it reads"),
                    ("legimus", "we read"),
                    ("legitis", "you (plural) read"),
                    ("legunt", "they read"),
                ],
            },
            {
                "name": "legere - to read (Imperfectum)",
                "conjugations": [
                    ("legebam", "I was reading"),
                    ("legebas", "you were reading"),
                    ("legebat", "he/she/it was reading"),
                    ("legebamus", "we were reading"),
                    ("legebatis", "you (plural) were reading"),
                    ("legebant", "they were reading"),
                ],
            },
            {
                "name": "legere - to read (Perfectum)",
                "conjugations": [
                    ("legi", "I have read / I read"),
                    ("legisti", "you have read / you read"),
                    ("legit", "he/she/it has read / read"),
                    ("legimus", "we have read / we read"),
                    ("legistis", "you (plural) have read / read"),
                    ("legerunt", "they have read / they read"),
                ],
            },
            {
                "name": "legere - to read (Futurum)",
                "conjugations": [
                    ("legam", "I will read"),
                    ("leges", "you will read"),
                    ("leget", "he/she/it will read"),
                    ("legemus", "we will read"),
                    ("legetis", "you (plural) will read"),
                    ("legent", "they will read"),
                ],
            },
            # DARE - to give (1st conjugation, irregular)
            {
                "name": "dare - to give (Praesens)",
                "conjugations": [
                    ("do", "I give"),
                    ("das", "you give"),
                    ("dat", "he/she/it gives"),
                    ("damus", "we give"),
                    ("datis", "you (plural) give"),
                    ("dant", "they give"),
                ],
            },
            {
                "name": "dare - to give (Imperfectum)",
                "conjugations": [
                    ("dabam", "I was giving"),
                    ("dabas", "you were giving"),
                    ("dabat", "he/she/it was giving"),
                    ("dabamus", "we were giving"),
                    ("dabatis", "you (plural) were giving"),
                    ("dabant", "they were giving"),
                ],
            },
            {
                "name": "dare - to give (Perfectum)",
                "conjugations": [
                    ("dedi", "I have given / I gave"),
                    ("dedisti", "you have given / you gave"),
                    ("dedit", "he/she/it has given / gave"),
                    ("dedimus", "we have given / we gave"),
                    ("dedistis", "you (plural) have given / gave"),
                    ("dederunt", "they have given / they gave"),
                ],
            },
            {
                "name": "dare - to give (Futurum)",
                "conjugations": [
                    ("dabo", "I will give"),
                    ("dabis", "you will give"),
                    ("dabit", "he/she/it will give"),
                    ("dabimus", "we will give"),
                    ("dabitis", "you (plural) will give"),
                    ("dabunt", "they will give"),
                ],
            },
            # CAPERE - to take (3rd conjugation -io)
            {
                "name": "capere - to take (Praesens)",
                "conjugations": [
                    ("capio", "I take"),
                    ("capis", "you take"),
                    ("capit", "he/she/it takes"),
                    ("capimus", "we take"),
                    ("capitis", "you (plural) take"),
                    ("capiunt", "they take"),
                ],
            },
            {
                "name": "capere - to take (Imperfectum)",
                "conjugations": [
                    ("capiebam", "I was taking"),
                    ("capiebas", "you were taking"),
                    ("capiebat", "he/she/it was taking"),
                    ("capiebamus", "we were taking"),
                    ("capiebatis", "you (plural) were taking"),
                    ("capiebant", "they were taking"),
                ],
            },
            {
                "name": "capere - to take (Perfectum)",
                "conjugations": [
                    ("cepi", "I have taken / I took"),
                    ("cepisti", "you have taken / you took"),
                    ("cepit", "he/she/it has taken / took"),
                    ("cepimus", "we have taken / we took"),
                    ("cepistis", "you (plural) have taken / took"),
                    ("ceperunt", "they have taken / they took"),
                ],
            },
            {
                "name": "capere - to take (Futurum)",
                "conjugations": [
                    ("capiam", "I will take"),
                    ("capies", "you will take"),
                    ("capiet", "he/she/it will take"),
                    ("capiemus", "we will take"),
                    ("capietis", "you (plural) will take"),
                    ("capient", "they will take"),
                ],
            },
            # AMBULARE - to walk (1st conjugation) - NEW
            {
                "name": "ambulare - to walk (Praesens)",
                "conjugations": [
                    ("ambulo", "I walk"),
                    ("ambulas", "you walk"),
                    ("ambulat", "he/she/it walks"),
                    ("ambulamus", "we walk"),
                    ("ambulatis", "you (plural) walk"),
                    ("ambulant", "they walk"),
                ],
            },
            {
                "name": "ambulare - to walk (Imperfectum)",
                "conjugations": [
                    ("ambulabam", "I was walking"),
                    ("ambulabas", "you were walking"),
                    ("ambulabat", "he/she/it was walking"),
                    ("ambulabamus", "we were walking"),
                    ("ambulabatis", "you (plural) were walking"),
                    ("ambulabant", "they were walking"),
                ],
            },
            {
                "name": "ambulare - to walk (Perfectum)",
                "conjugations": [
                    ("ambulavi", "I have walked / I walked"),
                    ("ambulavisti", "you have walked / you walked"),
                    ("ambulavit", "he/she/it has walked / walked"),
                    ("ambulavimus", "we have walked / we walked"),
                    ("ambulavistis", "you (plural) have walked / walked"),
                    ("ambulaverunt", "they have walked / they walked"),
                ],
            },
            {
                "name": "ambulare - to walk (Futurum)",
                "conjugations": [
                    ("ambulabo", "I will walk"),
                    ("ambulabis", "you will walk"),
                    ("ambulabit", "he/she/it will walk"),
                    ("ambulabimus", "we will walk"),
                    ("ambulabitis", "you (plural) will walk"),
                    ("ambulabunt", "they will walk"),
                ],
            },
        ]

        # Old list names (without tense) that should also be deleted
        old_list_names = [
            "habere - to have",
            "esse - to be",
            "velle - to want",
            "scandere - to climb",
            "natare - to swim",
            "ire - to go",
            "currere - to run",
            "canere - to sing",
            "saltare - to dance",
            "posse - to be able to/can",
            "lavare - to wash",
            "rogare - to ask",
            "amare - to love",
            "videre - to see",
            "audire - to hear",
            "dicere - to say",
            "facere - to do/make",
            "venire - to come",
            "scribere - to write",
            "legere - to read",
            "dare - to give",
            "capere - to take",
            "ambulare - to walk",
        ]

        # Get or create Latijn language
        latin_language = Language.query.filter_by(code="la").first()
        if not latin_language:
            print("Latijn language not found, creating it...")
            latin_language = Language(name="Latijn", code="la")
            db.session.add(latin_language)
            db.session.commit()

        # Get or create Engels language
        english_language = Language.query.filter_by(code="en").first()
        if not english_language:
            print("Engels language not found, creating it...")
            english_language = Language(name="Engels", code="en")
            db.session.add(english_language)
            db.session.commit()

        # Check if lists already exist (both new and old names)
        list_names = [verb["name"] for verb in verbs_data]
        all_names_to_check = list_names + old_list_names
        existing_lists = List.query.filter(List.name.in_(all_names_to_check)).all()

        if existing_lists:
            print(
                f"Found {len(existing_lists)} existing list(s). Deleting them first..."
            )
            for lst in existing_lists:
                db.session.delete(lst)
            db.session.commit()

        total_conjugations = 0

        # Create lists and entries for each verb
        for verb_data in verbs_data:
            print(f"Creating list for '{verb_data['name']}'...")

            verb_list = List(
                name=verb_data["name"],
                source_language=latin_language,
                target_language=english_language,
            )
            db.session.add(verb_list)
            db.session.flush()

            for latin, english in verb_data["conjugations"]:
                entry = Entry(
                    list_id=verb_list.id,
                    source_word=latin,
                    target_word=english,
                    entry_type="verb",
                )
                db.session.add(entry)
                total_conjugations += 1

        # Commit all changes
        db.session.commit()

        print(f"\nSuccessfully seeded {len(verbs_data)} Latin verb lists:")
        for verb_data in verbs_data:
            print(
                f"  - {verb_data['name']}: {len(verb_data['conjugations'])} conjugations"
            )
        print(
            f"\nTotal: {len(verbs_data)} lists with {total_conjugations} verb conjugations"
        )


if __name__ == "__main__":
    seed_extended_latin_verbs()
