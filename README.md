# AnnApp

Aplikacja Anieli do komponowania muzyki: pięciolinia, pianino, 20 instrumentów, pełna notacja, eksport PDF i MusicXML.

Działa w przeglądarce na tablecie, telefonie i komputerze. Na iPadzie: Safari → Udostępnij → „Do ekranu początkowego”.

Dźwięki: Salamander Grand Piano (Alexander Holm, CC BY 3.0), FluidR3 GM (Frank Wen).

## Odczyt nut ze zdjęcia (serwer)

Folder `omr-server/` to mały serwer, który zamienia zdjęcie nut na MusicXML przy pomocy [homr](https://github.com/liebharc/homr) (AGPL-3.0).
Plik `render.yaml` opisuje usługę `annapp-omr` na Render (Docker, 2 GB RAM, Frankfurt). Strona wysyła zdjęcia na `https://annapp-omr.onrender.com/api/convert`.
