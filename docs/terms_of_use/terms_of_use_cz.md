# Podmínky použití — DivePlanWeb

**Verze:** 2.1
**Datum aktualizace:** 9. března 2026


## 1. O aplikaci

**DivePlanWeb** je nekomerční webová aplikace s otevřeným zdrojovým kódem (open-source),
vyvíjená jako součást diplomové práce. Slouží k evidenci, analýze a plánování
potápěčských ponorů.

Aplikace je poskytována **zdarma** a není komerční. Není oficiálně napojena na žádného
výrobce potápěčského vybavení ani softwaru (např. Suunto, Garmin, Subsurface apod.).
Běh webové aplikace je uzpůsoben pro cloudovou službu MS Azure a lokální hostování.


## 2. Přijetí podmínek

Registrací nebo používáním aplikace uživatel souhlasí s těmito Podmínkami použití.
Pokud s podmínkami nesouhlasíte, aplikaci nepoužívejte.


## 3. Účel a rozsah využití

Aplikace je určena pro **osobní, vzdělávací a nekomerční použití**.

DivePlanWeb umožňuje:
- Registraci a přihlášení uživatele
- Evidenci a analýzu ponorů (potápěčský deník — logbook)
- Plánování ponorů s výpočtem deka, CNS%, OTU a spotřeby plynu
- Generování statistik a přehledů
- Správu vybavení a servisních záznamů
- Správu uživatelských účtů a rolí (RBAC) — pro administrátory


## 4. Fiktivní a vymyšlené osobní údaje

Aplikaci lze plně využívat **bez zadávání skutečných osobních údajů**.
Uživatel může při registraci a používání aplikace uvádět vymyšlené nebo testovací údaje
(přezdívka, fiktivní e-mail, vymyšlená jména a záznamy ponorů).

Uživatel je odpovědný za svá data, která vkládá do aplikace. Autor projektu nezodpovídá za obsah zadaný uživateli.


## 5. Registrace, přihlášení a zabezpečení účtu

- Registrace vyžaduje pouze přihlašovací jméno a heslo (ostatní údaje jsou nepovinné)
- Hesla jsou **nikdy neukládána v plaintextu** — používá se bezpečné hashování (pbkdf2:sha256)
- Po přihlášení systém vydává **JWT access token** a **refresh token**
- Access token má omezenou platnost (přibližně 15 minut)
- Refresh token slouží k obnově přístupu bez opětovného přihlášení
- Aplikace podporuje **token blacklist** — odvolání tokenů při odhlášení nebo změně hesla
- Přístup k datům je řízen **rolemi uživatelů**: běžný uživatel, administrátor
- Uživatel je odpovědný za ochranu svých přihlašovacích údajů a bezpečnost svého zařízení


## 6. Omezení použití

Uživatel se zavazuje, že nebude:

- Používat aplikaci k nezákonným účelům
- Nahrávat nebo zpracovávat obsah chráněný autorským právem bez oprávnění
- Pokoušet se o neoprávněný přístup k účtům jiných uživatelů nebo k systému
- Záměrně narušovat provoz aplikace (DoS útoky, exploitování zranitelností)
- Vydávat se za jinou osobu nebo subjekt


## 7. Výpočty a plánování ponorů

Výsledky kalkulaček, plánovacích algoritmů a NDL/deko tabulek mají **pouze informativní charakter**.

Uživatel bere na vědomí, že:
- Výpočty jsou aproximace — skutečné podmínky se mohou lišit
- Výsledky **nemohou nahradit certifikovaný výcvik** potápěče
- Před každým reálným ponorem je nutné plán ověřit s kvalifikovaným instruktorem
- Autor projektu nenese odpovědnost za škody vzniklé použitím výsledků aplikace při reálném potápění


## 8. Záruky a odpovědnost

Aplikace je poskytována **„tak jak je" (as is)**, bez záruk jakéhokoli druhu.

Autor **nenese odpovědnost** za:
- Chyby, výpadky nebo ztrátu dat
- Nesprávné výpočty způsobené chybnými vstupními daty
- Škody vzniklé používáním nebo nemožností použití aplikace
- Obsah, data a soubory zadané uživateli

Uživatel používá aplikaci **na vlastní riziko**.


## 9. Duševní vlastnictví

- Veškerý zdrojový kód, návrhy a dokumentace projektu DivePlanWeb jsou dílem autora
- Projekt je zveřejněn jako open-source pod licencí **MIT** (zdrojový kód)
  a **Creative Commons Attribution 4.0** (dokumentace)
- Uživatel smí kód studovat, kopírovat a upravovat pro nekomerční účely dle podmínek licence MIT
- Loga a názvy třetích stran (Suunto, Garmin apod.) jsou ochrannými známkami jejich vlastníků
  a nejsou součástí tohoto projektu


## 10. Ochrana osobních údajů

Zpracování osobních údajů je popsáno samostatně v dokumentu:
[**Zásady ochrany osobních údajů**](privacy_policy_cz.md)


## 11. Změny podmínek

Autor si vyhrazuje právo tyto podmínky kdykoli upravit.
Datum poslední revize je uvedeno v záhlaví dokumentu.
Pokračující používání aplikace po změně podmínek znamená souhlas s novou verzí.


## 12. Rozhodné právo

Na tyto podmínky se vztahuje právní řád **České republiky**.


## 13. Kontakt

**Autor projektu DivePlanWeb:**
Jan Hronek


*Tento dokument není právním poradenstvím. Pro komerční nasazení projektu
se doporučuje právní konzultace s odborníkem na internetové právo a GDPR.*
