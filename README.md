Zadanie 1 (termin realizacji do 26.03)
Implementacja systemu detekcji ruch (ang. motion detection) dla sekwencji wideo pochodzących np. ze strumienia z kamery online, plików video, itp.

Podstawowe funkcjonalności systemu:
· możliwość ustalenia źródła sekwencji video (strumień z kamery, plik video, itp.)

· wyświetlanie w czasie rzeczywistym sekwencji video

· określanie obszarów czułości (maski) w których ma działać detekcja ruchu

· informowanie o wystąpieniu ruchu w sposób wizualny (np. wyświetlany tekst, zaznaczenie kolorową ramką, itp.)

· możliwość określenia czułości systemu na pojawiający się ruch (zmiany), tak aby wyeliminować np. drobne zmian (padający deszcz lub śnieg, zmiany oświetlenia, itp.)

· możliwość włączenia trybu 'debug', w którym wizualizowane będą poszczególne etapy przetwarzania obrazu (np. konwersja z RGB/YUV na odcienie szarości, binaryzacja, wynik operacji odejmowania klatki bieżącej i referencyjnej, itd.)

Zachęcam też do rozbudowy systemu o dodatkowe funkcjonalności (zastrzegam sobie prawo podniesienie oceny końcowej z przedmiotu dla osób, które zrealizują najlepsze projekty). Implementacja powinna bazować na bibliotece OpenCV (https://opencv.org/), zalecany język programowania to Python.
Zadanie realizujemy w zespołach projektowych (3-4 osobowych, tych samych w których będą odbywały się ćwiczenia stacjonarne). 