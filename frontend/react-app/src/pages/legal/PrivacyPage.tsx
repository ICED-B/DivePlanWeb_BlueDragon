import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';
import { PageContainer } from '../../components/Layout';

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-6">
      <h2 className="text-lg font-semibold mb-2" style={{ color: 'var(--accent)' }}>{title}</h2>
      <div className="text-sm space-y-2" style={{ color: 'var(--text)' }}>{children}</div>
    </section>
  );
}

function ContentCS() {
  return (
    <>
      <Section title="1. Úvod">
        <p><strong>DivePlanWeb</strong> je nekomerční webová aplikace s otevřeným zdrojovým kódem vyvíjená jako součást diplomové práce. Slouží k evidenci, analýze a plánování potápěčských ponorů a je poskytována zdarma.</p>
        <p>Aplikace <strong>není určena pro komerční provoz</strong>. Autor projektu je fyzická osoba — tvůrce diplomové práce.</p>
      </Section>
      <Section title="2. Kdo zpracovává data">
        <p>Správcem dat je <strong>autor projektu DivePlanWeb</strong> (fyzická osoba): Jan Hronek</p>
        <p>Projekt je nekomerční a open-source. Webová aplikace je samostatný projekt provozovaný lokálně nebo prostřednictvím cloudové služby Microsoft Azure. Autor nevystupuje jako komerční subjekt ani provozovatel platformy ve smyslu obchodního práva.</p>
      </Section>
      <Section title="3. Jaká data aplikace sbírá">
        <p><strong>Registrační a profilové údaje:</strong></p>
        <ul className="list-disc list-inside space-y-1">
          <li>Přihlašovací jméno (login) — povinné</li>
          <li>Heslo — ukládáno výhradně jako bezpečný hash (nikdy v plaintextu)</li>
          <li>E-mailová adresa, jméno, příjmení, telefon — nepovinné</li>
        </ul>
        <p className="mt-2"><strong>Data o ponorech</strong> zadávaná uživatelem: záznamy ponorů, vybavení, lahve, plynné směsi, buddies, tagy, certifikace, zařízení, fotografie.</p>
        <p><strong>Technická data:</strong> auditní záznamy administrátorských akcí, odvolané JWT tokeny (bezpečnostní blacklist).</p>
      </Section>
      <Section title="4. Fiktivní a vymyšlené údaje">
        <p>Uživatelé <strong>nejsou povinni zadávat skutečné osobní údaje</strong>. Aplikaci lze plně používat s vymyšlenými nebo testovacími údaji (přezdívka jako login, fiktivní e-mail, vymyšlená jména apod.).</p>
        <p>Autor projektu neověřuje, zda jsou zadané osobní údaje skutečné nebo fiktivní. Zadávané osobní údaje mohou být fiktivní a uživatelé sami zodpovídají za jimi sdílená data.</p>
      </Section>
      <Section title="5. Účel zpracování dat">
        <p>Data zadaná uživatelem jsou zpracovávána výhradně za účelem poskytování funkcí aplikace, ověření identity při přihlášení a zabezpečení přístupu k účtu.</p>
        <p>Data <strong>nejsou</strong> zpracovávána pro komerční účely, reklamu, profilování ani sdílena s třetími stranami.</p>
      </Section>
      <Section title="6. Souhlas se zpracováním">
        <p>Registrací a používáním aplikace uživatel souhlasí se zpracováním jím zadaných dat v rozsahu a za účely popsanými v těchto Zásadách.</p>
        <p>Zadávání osobních údajů je <strong>dobrovolné</strong> — lze použít fiktivní data. Při smazání účtu mohou být data odstraněna nebo anonymizována.</p>
      </Section>
      <Section title="7. Zabezpečení dat">
        <ul className="list-disc list-inside space-y-1">
          <li>Hesla — bezpečný hash (pbkdf2:sha256), nikdy v plaintextu</li>
          <li>JWT autentizace s blacklistem tokenů</li>
          <li>RBAC — přístup ke správě dat dle role</li>
          <li>Rate limiting, CORS politika, validace vstupů, auditní logování</li>
        </ul>
      </Section>
      <Section title="8. Sdílení dat s třetími stranami">
        <p>DivePlanWeb <strong>nesdílí data s třetími stranami</strong> za účelem reklamy nebo marketingu. Data mohou být technicky zpracovávána cloudovými službami (Microsoft Azure). Aplikace nepoužívá Google Analytics, Facebook Pixel ani podobné sledovací nástroje.</p>
      </Section>
      <Section title="9. Cookies a sledování">
        <p>DivePlanWeb <strong>nepoužívá analytické cookies</strong> ani sledovací technologie třetích stran. Aplikace používá <code>localStorage</code> v prohlížeči pouze pro JWT tokeny a nastavení tématu/jazyka.</p>
      </Section>
      <Section title="10. Odpovědnost">
        <p>Aplikace je poskytována <strong>„tak jak je"</strong> bez záruk. Autor nenese odpovědnost za ztrátu dat, škody způsobené výpočty ani za obsah zadaný uživateli. Výsledky kalkulaček mají pouze informativní charakter.</p>
      </Section>
      <Section title="11. Kontakt">
        <p><strong>Autor projektu DivePlanWeb:</strong> Jan Hronek</p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Verze 2.1 | Datum aktualizace: 9. března 2026</p>
        <p className="text-xs mt-1" style={{ color: 'var(--text-subtle)' }}>Tyto Zásady jsou součástí open-source projektu DivePlanWeb. Nejsou právním dokumentem. Pro komerční nasazení se doporučuje právní konzultace.</p>
      </Section>
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
        Viz také: <Link to="/terms" style={{ color: 'var(--accent)' }} className="hover:underline">Podmínky použití</Link>
      </p>
    </>
  );
}

function ContentEN() {
  return (
    <>
      <Section title="1. Introduction">
        <p><strong>DivePlanWeb</strong> is a non-commercial, open-source web application developed as part of a diploma thesis. It is designed for recording, analyzing, and planning scuba dives, and is provided free of charge.</p>
        <p>The application is <strong>not intended for commercial use</strong>. The project author is an individual — the creator of this diploma thesis.</p>
      </Section>
      <Section title="2. Data Controller">
        <p>The data controller is the <strong>author of the DivePlanWeb project</strong> (individual): Jan Hronek</p>
        <p>This project is non-commercial and open-source. The web application is a standalone project hosted locally or via Microsoft Azure cloud services. The author does not act as a commercial entity or platform operator.</p>
      </Section>
      <Section title="3. What Data the Application Collects">
        <p><strong>Registration and Profile Data:</strong></p>
        <ul className="list-disc list-inside space-y-1">
          <li>Username (login) — required</li>
          <li>Password — stored exclusively as a secure hash (never in plaintext)</li>
          <li>Email address, first/last name, phone number — optional</li>
        </ul>
        <p className="mt-2"><strong>Dive records</strong> entered by the user: dive logs, equipment, cylinders, gas mixes, buddies, tags, certifications, devices, photos.</p>
        <p><strong>Technical data:</strong> audit records of administrator actions, revoked JWT tokens (security blacklist).</p>
      </Section>
      <Section title="4. Fictitious and Invented Data">
        <p>Users are <strong>not required to provide real personal information</strong>. The application can be fully used with invented or test data (a nickname as login, a fictional email, made-up names, etc.).</p>
        <p>The project author does not verify whether submitted data is real or fictitious. Entered personal data may be fictitious, and users are solely responsible for the data they share.</p>
      </Section>
      <Section title="5. Purpose of Data Processing">
        <p>Data entered by the user is processed solely for providing application features, verifying identity during login, and securing access to the user account.</p>
        <p>Data is <strong>not</strong> processed for commercial purposes, advertising, profiling, or shared with third parties.</p>
      </Section>
      <Section title="6. Consent to Data Processing">
        <p>By registering and using the application, the user consents to the processing of their submitted data as described in this Policy.</p>
        <p>Providing personal information is <strong>voluntary</strong> — fictitious data may be used. Upon account deletion, data may be removed or anonymized.</p>
      </Section>
      <Section title="7. Data Security">
        <ul className="list-disc list-inside space-y-1">
          <li>Passwords — secure hash (pbkdf2:sha256), never in plaintext</li>
          <li>JWT authentication with token blacklist</li>
          <li>RBAC — access to data management based on user role</li>
          <li>Rate limiting, CORS policy, input validation, audit logging</li>
        </ul>
      </Section>
      <Section title="8. Sharing Data with Third Parties">
        <p>DivePlanWeb <strong>does not share data with third parties</strong> for advertising or marketing. Data may technically be processed by cloud services (Microsoft Azure). The application does not use Google Analytics, Facebook Pixel, or similar tracking tools.</p>
      </Section>
      <Section title="9. Cookies and Tracking">
        <p>DivePlanWeb <strong>does not use analytical cookies</strong> or third-party tracking technologies. The application uses browser <code>localStorage</code> only for JWT tokens and theme/language preferences.</p>
      </Section>
      <Section title="10. Liability">
        <p>The application is provided <strong>"as is"</strong> without warranties. The author assumes no responsibility for data loss, damages from calculations, or user-submitted content. Calculator results are for informational purposes only.</p>
      </Section>
      <Section title="11. Contact">
        <p><strong>DivePlanWeb project author:</strong> Jan Hronek</p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Version 2.1 | Last updated: March 9, 2026</p>
        <p className="text-xs mt-1" style={{ color: 'var(--text-subtle)' }}>This Policy is part of the open-source DivePlanWeb project. It is not a legal document. Legal consultation is recommended for any commercial deployment.</p>
      </Section>
      <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
        See also: <Link to="/terms" style={{ color: 'var(--accent)' }} className="hover:underline">Terms of Use</Link>
      </p>
    </>
  );
}

export default function PrivacyPage() {
  const { t, i18n } = useTranslation();
  return (
    <PageContainer>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold flex items-center gap-3 mb-8" style={{ color: 'var(--text)' }}>
          <Shield style={{ color: 'var(--accent)' }} size={28} />
          {t('common.privacy_policy')}
        </h1>
        <div className="card p-6">
          {i18n.language === 'cs' ? <ContentCS /> : <ContentEN />}
        </div>
      </div>
    </PageContainer>
  );
}
