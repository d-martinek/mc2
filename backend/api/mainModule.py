from flask_pymongo import PyMongo
from bson import ObjectId
import datetime

class mainAlgorithm:
    def __init__(self, dbcollection, skole, fakulteti, zanimanja, odabir):
        self.collection = dbcollection
        self.skole = skole
        self.fakulteti = fakulteti
        self.zanimanja = zanimanja
        self.odabir = {
            "skolaId": str(odabir["skolaId"]),
            "fakultetId": str(odabir["fakultetId"]),
            "zanimanjeId": str(odabir["zanimanjeId"])
        }



    def dohvacanjePodataka(self):
        skola = {}
        fakultet = {}
        zanimanje = {}
        
        for i in self.skole:
            if str(i["_id"]) == self.odabir["skolaId"]:
                skola = i

        for i in self.fakulteti:
            if str(i["_id"]) == self.odabir["fakultetId"]:
                fakultet = i

        for i in self.zanimanja:
            if str(i["_id"]) == self.odabir["zanimanjeId"]:
                zanimanje = i

        return {
            "skola": skola,
            "fakultet": fakultet,
            "zanimanje": zanimanje
        }


    #preuzimanje potrebnih znanja za zanimanje i svih izlaznih znanja iz zadanog fakulteta
    def generiranje_znanja_skola(self):
        potrebnaZnanjaZanimanje = self.usporedba_znanja_fakultet()["filtriranaPotrebnaZnanja"]
        dobivenaZnanjaSkola = []

        for j in self.skole:
            if str(j["_id"]) == self.odabir["skolaId"]:
                for c in j["predmeti"]:
                    for d in c["dobivenaZnanja"]:
                        dobivenaZnanjaSkola.append(d["_id"])
                
        return potrebnaZnanjaZanimanje, dobivenaZnanjaSkola


    #preuzimanje potrebnih znanja za zanimanje i svih izlaznih znanja iz srednje škole
    def generiranje_znanja_fakultet(self):
        potrebnaZnanjaZanimanje = []
        dobivenaZnanjaFakultet = []

        for i in self.zanimanja:
            if str(i["_id"]) == self.odabir["zanimanjeId"]:
                for a in i["potrebnaZnanja"]:
                    potrebnaZnanjaZanimanje.append(a["_id"])
                

        for j in self.fakulteti:
            if str(j["_id"]) == self.odabir["fakultetId"]:
                for b in j["smjerovi"]:
                    for c in b["kolegiji"]:
                        for d in c["dobivenaZnanja"]:
                            dobivenaZnanjaFakultet.append(d["_id"])
                
        return potrebnaZnanjaZanimanje, dobivenaZnanjaFakultet


    #metoda za usporedbu potrebnih znanja iz zadanog zanimanja i dobivenih znanja u srednjoj školi
    def usporedba_znanja_skola(self):
        x, y = self.generiranje_znanja_skola()
        potrebnaZnanjaZanimanje = set(x)
        dobivenaZnanjaSkola = set(y)

        korisnaDobivenaZnanja = potrebnaZnanjaZanimanje.intersection(dobivenaZnanjaSkola)
        filtriranaPotrebnaZnanja = potrebnaZnanjaZanimanje.difference(dobivenaZnanjaSkola)

        return {
            "korisnaDobivenaZnanja": list(korisnaDobivenaZnanja),
            "filtriranaPotrebnaZnanja": list(filtriranaPotrebnaZnanja)
        }


    #metoda za usporedbu potrebnih znanja iz zadanog zanimanja i dobivenih znanja na fakultetu
    def usporedba_znanja_fakultet(self):
        x, y = self.generiranje_znanja_fakultet()
        potrebnaZnanjaZanimanje = set(x)
        dobivenaZnanjaFakultet = set(y)

        korisnaDobivenaZnanja = potrebnaZnanjaZanimanje.intersection(dobivenaZnanjaFakultet)
        filtriranaPotrebnaZnanja = potrebnaZnanjaZanimanje.difference(dobivenaZnanjaFakultet)

        return {
            "korisnaDobivenaZnanja": list(korisnaDobivenaZnanja),
            "filtriranaPotrebnaZnanja": list(filtriranaPotrebnaZnanja)
        }


    #metoda generira izlazni objekt/riječnik potreban za rad aplikacije
    def izlaz(self):
        
        izlazniObjekt = {
            "_id": ObjectId(),
            "userId": "",
            "skola": {
                "skolaId": self.odabir["skolaId"],
                "naziv": self.dohvacanjePodataka()["skola"]["naziv"],
                "korisnaDobivenaZnanja": self.usporedba_znanja_skola()["korisnaDobivenaZnanja"],
                "preporucenaZnanja": []
            },
            "fakultet": {
                "fakultetId": self.odabir["fakultetId"],
                "naziv": self.dohvacanjePodataka()["fakultet"]["naziv"],
                "korisnaDobivenaZnanja": self.usporedba_znanja_fakultet()["korisnaDobivenaZnanja"],
                "preporucenaZnanja": [],
            },
            "zanimanje": {
                "zanimanjeId": self.odabir["zanimanjeId"],
                "naziv": self.dohvacanjePodataka()["zanimanje"]["naziv"],
                "zaposljavanje": {
                    "tvrtke": [],
                    "ustanove": []
                },
                "minimalnaRazinaObrazovanja": self.dohvacanjePodataka()["zanimanje"]["minimalnaRazinaObrazovanja"],
                "preporucenaZnanja": []
            },
            "interesi": []
        }

        objektIzBaze = self.collection.find_one({
            'skola.skolaId' : izlazniObjekt['skola']['skolaId'],
            'fakultet.fakultetId' : izlazniObjekt['fakultet']['fakultetId'],
            'zanimanje.zanimanjeId' : izlazniObjekt['zanimanje']['zanimanjeId'],
            })

        if objektIzBaze:
            return objektIzBaze
        else:
            self.collection.save(izlazniObjekt)
            return izlazniObjekt