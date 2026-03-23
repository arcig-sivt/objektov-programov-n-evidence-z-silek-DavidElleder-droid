from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional



class StavZasilky(Enum):
    REGISTROVANA = "registrovana"
    PREVZATA = "prevzata"
    NA_CESTE = "na_ceste"
    DORUCENA = "dorucena"
    VRACENA = "vracena"
    ZTRACENA = "ztracena"


@dataclass(frozen=True)
class HistorickyZaznam:
    cas: datetime
    stav: StavZasilky
    poznamka: Optional[str] = None


@dataclass
class Zasilka:
    id_zasilky:str
    odesilatel:str
    prijemce:str
    vychozi_misto:str
    cilove_misto:str
    hmotnost: float
    stav:StavZasilky = StavZasilky.REGISTROVANA
    historie: list[HistorickyZaznam] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.id_zasilky.strip():
            raise ValueError("ID zásilky nesmí být prázdné.")
        if not self.odesilatel.strip():
            raise ValueError("Odesílatel nesmí být prázdný.")
        if not self.prijemce.strip():
            raise ValueError("Příjemce nesmí být prázdný.")
        if not self.vychozi_misto.strip():
            raise ValueError("Výchozí místo nesmí být prázdné.")
        if not self.cilove_misto.strip():
            raise ValueError("Cílové místo nesmí být prázdné.")
        if self.hmotnost <= 0:
            raise ValueError("Hmotnost musí být kladná.")
        
        if not self.historie:
            self._pridej_do_historie(self.stav, "Zásilka byla registrována.")
        
    def _pridej_do_historie(self, stav: StavZasilky, poznamka: Optional[str] = None) -> None:
        self.historie.append(HistorickyZaznam(cas=datetime.now(), stav=stav, poznamka=poznamka))

    def zmen_stav(self, novy_stav: StavZasilky, poznamka: Optional[str] = None) -> None:
        if self.stav == novy_stav:
            print(f"Zásilka {self.id_zasilky} už je ve stavu {novy_stav.value}. Nelze změnit na stejný stav.")
        
        povolene_zmeny: dict[StavZasilky, list[StavZasilky]] = {
            StavZasilky.REGISTROVANA: [StavZasilky.PREVZATA, StavZasilky.ZTRACENA],
            StavZasilky.PREVZATA: [StavZasilky.NA_CESTE, StavZasilky.VRACENA, StavZasilky.ZTRACENA],    # převzata dopravcem od odesilatele
            StavZasilky.NA_CESTE: [StavZasilky.DORUCENA, StavZasilky.VRACENA, StavZasilky.ZTRACENA],    # na ceste k prijemci
            StavZasilky.DORUCENA: [],                                                                   # prebrana prijemcem // finalni stav
            StavZasilky.VRACENA: [],                                                                    # finalni stav
            StavZasilky.ZTRACENA: []                                                                    # finalni stav                          
        }
        
        if novy_stav not in povolene_zmeny[self.stav]:
            print(f"Nelze zmenit stav zasilky {self.id_zasilky} z '{self.stav.value}' na '{novy_stav.value}'")
        
        self.stav = novy_stav
        self._pridej_do_historie(novy_stav, poznamka)

    def info(self) -> dict[str, str | float]:
        return {
            "id_zasilky": self.id_zasilky,
            "odesilatel": self.odesilatel,
            "prijemce": self.prijemce,
            "vychozi_misto": self.vychozi_misto,
            "cilove_misto": self.cilove_misto,
            "hmotnost": self.hmotnost,
            "stav": self.stav.value
        }
    

class EvidenceZasilek:
    def __init__(self) -> None:
        self.zasilky: dict[str, Zasilka] = {}

    def registruj_zasilku(
            self,
            id_zasilky: str,
            odesilatel: str,
            prijemce: str,
            vychozi_misto: str,
            cilove_misto: str,
            hmotnost: float
            ) -> None:
        if id_zasilky in self.zasilky:
            print (f"Zásilka s ID '{id_zasilky}' již existuje.")
        
        nova_zasilka = Zasilka(
            id_zasilky=id_zasilky,
            odesilatel=odesilatel,
            prijemce=prijemce,
            vychozi_misto=vychozi_misto,
            cilove_misto=cilove_misto,
            hmotnost=hmotnost
        )
        self.zasilky[id_zasilky] = nova_zasilka

    def zasilka_prevzata(self, id_zasilky: str, poznamka: Optional[str] = None) -> None:
        zasilka = self._najdi_zasilku(id_zasilky)
        zasilka.zmen_stav(StavZasilky.PREVZATA, poznamka)

    def zasilka_ztracena(self, id_zasilky: str, poznamka: Optional[str] = None) -> None:
        zasilka = self._najdi_zasilku(id_zasilky)
        zasilka.zmen_stav(StavZasilky.ZTRACENA, poznamka)

    def zasilka_na_ceste(self, id_zasilky: str, poznamka: Optional[str] = None) -> None:
        zasilka = self._najdi_zasilku(id_zasilky)
        zasilka.zmen_stav(StavZasilky.NA_CESTE, poznamka)

    def zasilka_dorucena(self, id_zasilky: str, poznamka: Optional[str] = None) -> None:
        zasilka = self._najdi_zasilku(id_zasilky)
        zasilka.zmen_stav(StavZasilky.DORUCENA, poznamka)

    def zasilka_vracena(self, id_zasilky: str, poznamka: Optional[str] = None) -> None:
        zasilka = self._najdi_zasilku(id_zasilky)
        zasilka.zmen_stav(StavZasilky.VRACENA, poznamka)

    def historie_zasilky(self, id_zasilky: str) -> list[HistorickyZaznam]:
        zasilka = self._najdi_zasilku(id_zasilky)
        return list (zasilka.historie)
    
    def zasilka_info(self, id_zasilky: str) -> dict[str, str | float]:
        zasilka = self._najdi_zasilku(id_zasilky)
        return zasilka.info()
    
    def _najdi_zasilku(self, id_zasilky: str) -> Zasilka:
        zasilka = self.zasilky.get(id_zasilky)
        if zasilka is None:
            print (f"Zásilka s ID '{id_zasilky}' neexistuje.")
        return zasilka
    