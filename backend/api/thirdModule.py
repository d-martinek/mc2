from bson import ObjectId

class thirdAlgorithm:
    def __init__(self, skole, fakulteti, zanimanja, odabir):
        self.skole = skole
        self.fakulteti = fakulteti
        self.zanimanja = zanimanja
        self.odabir = {
            "skolaId": odabir["skolaId"],
            "fakultetId": odabir["fakultetId"],
            "smjerId": odabir["smjerId"]
        }


    #metoda generira listu zanimanja uzimajući u obzir kategoriju zadanog fakulteta
    def filter_zanimanja(self):
        odabraniFakultetSmjerKategorija = ""
        filtriranaZanimanja = []

        for i in self.fakulteti:
            if str(i["_id"]) == self.odabir["fakultetId"]:
                for j in i['smjerovi']:
                    if str(j["_id"]) == self.odabir["smjerId"]:
                        odabraniFakultetSmjerKategorija = j["kategorija"]


        for i in self.zanimanja:
            if i["kategorija"] == odabraniFakultetSmjerKategorija:
                filtriranaZanimanja.append(i)
        
        return filtriranaZanimanja


    #usporedba potrebnih znanja svakog filtiranog zanimanja s izlaznim znanjima zadanog fakulteta
    def usporedba_zanimanja(self):
        dobivenaZnanjaFakulteta = []
        brojPoklapanja = []

        for i in self.fakulteti:
            if str(i["_id"]) == self.odabir["fakultetId"]:
                for a in i["smjerovi"]:
                    for b in a["kolegiji"]:
                        for c in b["dobivenaZnanja"]:
                            dobivenaZnanjaFakulteta.append(c["_id"])
        x = set(dobivenaZnanjaFakulteta)            
        
        for i in self.filter_zanimanja():
            potrebnaZnanjaZanimanje = []

            for j in i["potrebnaZnanja"]:
                potrebnaZnanjaZanimanje.append(j["_id"])
                
            y = set(potrebnaZnanjaZanimanje)

            zz = list(x.intersection(y))
            brojZnanja = len(zz)

            brojPoklapanja.append({
                "idZanimanja" : i["_id"],
                "brojIstihZnanja" : brojZnanja
            })

        return brojPoklapanja


    #sortiranje zanimanja po broju znanja koja se preklapaju sa znanjima zadanog fakulteta
    def sortiranje_zanimanja(self):
        def sortByKey(e):
            return e["brojIstihZnanja"]

        sortiranaZanimanja = self.usporedba_zanimanja()
        sortiranaZanimanja.sort(key=sortByKey, reverse = True)

        return sortiranaZanimanja
    

    #izlazni objekt/riječnik
    def izlaz(self):
        return {
            "listaZanimanja" : self.sortiranje_zanimanja(),
            "skolaId": self.odabir["skolaId"],
            "fakultetId": self.odabir["fakultetId"]
        }