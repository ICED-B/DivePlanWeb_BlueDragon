# Zásady ochrany osobních údajů — DivePlanWeb

**Verze:** 2.1
**Datum aktualizace:** 9. března 2026


## 1. Úvod

Tyto Zásady ochrany osobních údajů popisují, jak aplikace **DivePlanWeb** nakládá
s informacemi zadávanými uživateli.

DivePlanWeb je **nekomerční webová aplikace s otevřeným zdrojovým kódem (open-source)**,
vyvíjená jako součást diplomové práce. Slouží k evidenci, analýze a plánování
potápěčských ponorů a je poskytována zdarma.

Aplikace **není určena pro komerční provoz**. Autor projektu je fyzická osoba —
tvůrce diplomové práce.


## 2. Kdo zpracovává data

Správcem dat je **autor projektu DivePlanWeb** (fyzická osoba): **Jan Hronek**

Projekt je nekomerční a open-source. Webová aplikace je samostatný projekt provozovaný
lokálně nebo prostřednictvím cloudové služby Microsoft Azure. Autor nevystupuje jako
komerční subjekt ani provozovatel platformy ve smyslu obchodního práva.


## 3. Jaká data aplikace sbírá

Aplikace ukládá pouze data, která uživatel sám zadá při registraci a používání:

### Registrační a profilové údaje
- **Přihlašovací jméno (login)** — povinné
- **Heslo** — ukládáno výhradně jako bezpečný hash (nikdy v plaintextu)
- **E-mailová adresa** — nepovinné
- **Jméno a příjmení** — nepovinné
- **Telefonní číslo** — nepovinné

### Data o ponorech (zadávaná uživatelem)
- Záznamy ponorů (datum, hloubka, čas, teplota, lokality, poznámky)
- Data o vybavení, lahvích, plynných směsích
- Buddies, tagy, certifikace, zařízení
- Fotografie a soubory (volitelně)

### Technická data
- Auditní záznamy administrátorských akcí (nikoli chování uživatelů)
- Odvolané JWT tokeny (bezpečnostní blacklist)


## 4. Fiktivní a vymyšlené údaje

Uživatelé **nejsou povinni zadávat skutečné osobní údaje**.
Aplikaci lze plně používat s vymyšlenými nebo testovacími údaji
(přezdívka jako login, fiktivní e-mail, vymyšlená jména apod.).

Autor projektu neověřuje, zda jsou zadané osobní údaje skutečné nebo fiktivní.
Zadávané osobní údaje mohou být fiktivní a uživatelé sami zodpovídají za jimi sdílená data.


## 5. Účel zpracování dat

Data zadaná uživatelem jsou zpracovávána výhradně za účelem:

- Poskytování funkcí aplikace (deník ponorů, plánovač, statistiky)
- Ověření identity při přihlášení (autentizace)
- Zabezpečení přístupu k uživatelskému účtu

Data **nejsou** zpracovávána pro komerční účely, reklamu, profilování ani sdílena s třetími stranami.


## 6. Souhlas se zpracováním

Registrací a používáním aplikace uživatel souhlasí se zpracováním jím zadaných dat
v rozsahu a za účely popsanými v těchto Zásadách.

Uživatel bere na vědomí, že:
- Zadávání osobních údajů je **dobrovolné** — lze použít fiktivní data
- Poskytnutá data mohou být uložena na serverech provozovatele
- Při smazání účtu mohou být data odstraněna nebo anonymizována


## 7. Zabezpečení dat

Aplikace implementuje tato bezpečnostní opatření:

- **Hesla** jsou ukládána jako bezpečný hash (pbkdf2:sha256) — nikdy v plaintextu
- **JWT autentizace** — přístup pouze pro přihlášené uživatele s platným tokenem
- **Token blacklist** — odvolání tokenů při odhlášení nebo změně hesla
- **RBAC** — přístup ke správě dat dle role (uživatel / administrátor)
- **Rate limiting** — ochrana před brute-force útoky
- **CORS politika** — omezení přístupu z neautorizovaných domén
- **Validace vstupů** — ověření všech zadávaných dat
- **Auditní logování** — zaznamenání administrátorských operací


## 8. Sdílení dat s třetími stranami

DivePlanWeb **nesdílí data s třetími stranami** za účelem reklamy, marketingu ani prodeje.

Data mohou být technicky zpracovávána cloudovými službami použitými pro provoz aplikace
(Microsoft Azure — servery, databáze, úložiště). Tyto služby jsou smluvně vázány
povinností chránit data dle standardů GDPR.

Aplikace **nepoužívá Google Analytics, Facebook Pixel ani podobné sledovací nástroje**.


## 9. Cookies a sledování

DivePlanWeb **nepoužívá analytické cookies ani sledovací technologie** třetích stran.

Aplikace používá úložiště prohlížeče pro technicky nezbytné účely:
- **`sessionStorage`**: JWT tokeny (přihlašovací stav) — data se smažou při zavření záložky nebo prohlížeče
- **`localStorage`**: nastavení tématu a jazyka — data zůstávají zachována mezi relacemi

Tato data jsou uložena pouze v prohlížeči uživatele a nejsou odesílána třetím stranám.


## 10. Doba uchovávání dat

Data jsou uchovávána po dobu existence uživatelského účtu.
Po smazání účtu mohou být data smazána nebo anonymizována dle technických možností.

Projekt je akademického charakteru, ukládaná data slouží primárně k akademickým výzkumným účelům.


## 11. Odpovědnost

Aplikace je poskytována **„tak jak je" (as is)** bez záruk jakéhokoli druhu.

Autor **nenese odpovědnost** za:
- Ztrátu dat způsobenou technickou chybou nebo výpadkem
- Škody vzniklé nesprávným použitím plánovacích výpočtů při reálném potápění
- Obsah zadaný uživateli do aplikace

Výsledky kalkulaček a plánovacích algoritmů mají **pouze informativní charakter**
a nemohou nahradit certifikovaný výcvik ani posouzení instruktora.

## 12. Změny těchto Zásad

Autor si vyhrazuje právo tyto Zásady kdykoli aktualizovat.
Datum poslední aktualizace je uvedeno v záhlaví dokumentu.
Pokračující používání aplikace po změně Zásad znamená souhlas s novou verzí.


## 13. Kontakt

**Autor projektu DivePlanWeb:**
Jan Hronek


*Tyto Zásady jsou součástí open-source projektu DivePlanWeb — diplomové práce.
Nejsou právním dokumentem. Pro komerční nasazení se doporučuje právní konzultace.*
