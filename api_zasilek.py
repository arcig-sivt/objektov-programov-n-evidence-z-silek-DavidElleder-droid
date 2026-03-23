from evidence_zasilek import EvidenceZasilek, StavZasilky
from typing import Optional



def main() -> None:
    evidence = EvidenceZasilek()

    try:
        evidence.registruj_zasilku(
            id_zasilky="Z123",
            odesilatel="Jan Novak",
            prijemce="Petr Svoboda",
            vychozi_misto="Praha",
            cilove_misto="Brno",
            hmotnost=2.5
        )

        evidence.zasilka_prevzata("Z123")
        evidence.zasilka_na_ceste("Z123")
        evidence.zasilka_vracena("Z123")  #finalni stav

        
        if evidence.zasilky["Z123"].stav == StavZasilky.DORUCENA:
            print("Zásilka je doručena")

        if evidence.zasilky["Z123"].stav == StavZasilky.ZTRACENA:
            print("Zasilka je ztracena")
        
        if evidence.zasilky["Z123"].stav == StavZasilky.VRACENA:
            print("Zasilka je vracena")

    except Exception as e:
        print("chyba")
        


main()