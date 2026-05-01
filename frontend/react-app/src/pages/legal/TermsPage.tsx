import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { FileText } from 'lucide-react';
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
      <Section title="1. O aplikaci">
        <p><strong>DivePlanWeb</strong> je nekomerční webová aplikace s otevřeným zdrojovým kódem, vyvíjená jako součást diplomové práce. Slouží k evidenci, analýze a plánování potápěčských ponorů a je poskytována zdarma.</p>
        <p>Aplikace není komerční a není oficiálně napojena na žádného výrobce potápěčského vybavení ani softwaru (Suunto, Garmin, Subsurface apod.). Běh webové aplikace je uzpůsoben pro cloudovou službu MS Azure a lokální hostování.</p>
      </Section>
      <Section title="2. Přijetí podmínek">
        <p>Registrací nebo používáním aplikace uživatel souhlasí s těmito Podmínkami použití. Pokud s podmínkami nesouhlasíte, aplikaci nepoužívejte.</p>
      </Section>
      <Section title="3. Účel a rozsah využití">
        <p>Aplikace je určena pro <strong>osobní, vzdělávací a nekomerční použití</strong>. DivePlanWeb umožňuje evidenci a analýzu ponorů, plánování s výpočtem deka/CNS%/OTU, statistiky a správu vybavení.</p>
      </Section>
      <Section title="4. Fiktivní a vymyšlené osobní údaje">
        <p>Aplikaci lze plně využívat <strong>bez zadávání skutečných osobních údajů</strong>. Uživatel může uvádět vymyšlené nebo testovací údaje (přezdívka, fiktivní e-mail, vymyšlená jména).</p>
        <p>Uživatel je odpovědný za svá data, která vkládá do aplikace. Autor projektu nezodpovídá za obsah zadaný uživateli.</p>
      </Section>
      <Section title="5. Registrace a zabezpečení účtu">
        <ul className="list-disc list-inside space-y-1">
          <li>Registrace vyžaduje pouze přihlašovací jméno a heslo (ostatní údaje jsou nepovinné)</li>
          <li>Hesla jsou nikdy neukládána v plaintextu — používá se bezpečné hashování (pbkdf2:sha256)</li>
          <li>Po přihlášení systém vydává JWT access token a refresh token s omezenou platností</li>
          <li>Aplikace podporuje token blacklist — odvolání tokenů při odhlášení nebo změně hesla</li>
          <li>Přístup k datům je řízen rolemi uživatelů (běžný uživatel, administrátor)</li>
        </ul>
      </Section>
      <Section title="6. Omezení použití">
        <p>Uživatel se zavazuje, že nebude používat aplikaci k nezákonným účelům, pokoušet se o neoprávněný přístup k účtům jiných uživatelů ani záměrně narušovat provoz aplikace.</p>
      </Section>
      <Section title="7. Výpočty a plánování ponorů">
        <p>Výsledky kalkulaček, plánovacích algoritmů a NDL/deko tabulek mají <strong>pouze informativní charakter</strong>. Výsledky nemohou nahradit certifikovaný výcvik potápěče. Před každým reálným ponorem je nutné plán ověřit s kvalifikovaným instruktorem.</p>
        <p>Autor projektu nenese odpovědnost za škody vzniklé použitím výsledků aplikace při reálném potápění.</p>
      </Section>
      <Section title="8. Záruky a odpovědnost">
        <p>Aplikace je poskytována <strong>„tak jak je" (as is)</strong>, bez záruk jakéhokoli druhu. Autor nenese odpovědnost za chyby, výpadky, ztrátu dat ani škody vzniklé používáním aplikace. Uživatel používá aplikaci na vlastní riziko.</p>
      </Section>
      <Section title="9. Duševní vlastnictví">
        <p>Projekt je zveřejněn jako open-source pod licencí <strong>MIT</strong> (zdrojový kód) a <strong>Creative Commons Attribution 4.0</strong> (dokumentace). Loga a názvy třetích stran jsou ochrannými známkami jejich vlastníků.</p>
      </Section>
      <Section title="10. Ochrana osobních údajů">
        <p>Zpracování osobních údajů je popsáno v <Link to="/privacy" style={{ color: 'var(--accent)' }} className="hover:underline">Zásadách ochrany osobních údajů</Link>.</p>
      </Section>
      <Section title="11. Kontakt">
        <p><strong>Autor projektu DivePlanWeb:</strong> Jan Hronek</p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Verze 2.1 | Datum aktualizace: 9. března 2026</p>
      </Section>
    </>
  );
}

function ContentEN() {
  return (
    <>
      <Section title="1. About the Application">
        <p><strong>DivePlanWeb</strong> is a non-commercial, open-source web application developed as part of a diploma thesis. It is designed for recording, analyzing, and planning scuba dives, and is provided free of charge.</p>
        <p>It is not commercially affiliated with any manufacturer of diving equipment or software (e.g., Suunto, Garmin, Subsurface). The web application is designed to run on Microsoft Azure cloud services and local hosting.</p>
      </Section>
      <Section title="2. Acceptance of Terms">
        <p>By registering or using the application, you agree to these Terms of Use. If you do not agree, please do not use the application.</p>
      </Section>
      <Section title="3. Purpose and Scope of Use">
        <p>The application is intended for <strong>personal, educational, and non-commercial use</strong>. DivePlanWeb provides dive logging, planning with decompression/CNS%/OTU calculations, statistics, and equipment management.</p>
      </Section>
      <Section title="4. Fictitious and Invented Personal Data">
        <p>The application can be fully used <strong>without providing real personal information</strong>. Users may register and use the application with invented or test data (nickname, fictional email, made-up names).</p>
        <p>Users are responsible for the data they enter into the application. The project author is not responsible for user-submitted content.</p>
      </Section>
      <Section title="5. Registration and Account Security">
        <ul className="list-disc list-inside space-y-1">
          <li>Registration requires only a username and password (all other fields are optional)</li>
          <li>Passwords are never stored in plaintext — secure hashing is used (pbkdf2:sha256)</li>
          <li>Upon login, the system issues a JWT access token and refresh token with limited lifespan</li>
          <li>The application supports a token blacklist — tokens are revoked on logout or password change</li>
          <li>Data access is controlled by user roles (standard user, administrator)</li>
        </ul>
      </Section>
      <Section title="6. Prohibited Use">
        <p>Users agree not to use the application for unlawful purposes, attempt unauthorized access to other users' accounts, or intentionally disrupt the operation of the application.</p>
      </Section>
      <Section title="7. Dive Calculations and Planning">
        <p>The results of calculators, planning algorithms, and NDL/decompression tables are for <strong>informational purposes only</strong>. Results cannot replace certified diver training. Every real dive plan must be verified with a qualified instructor.</p>
        <p>The author bears no responsibility for damages resulting from the use of the application's results in real diving situations.</p>
      </Section>
      <Section title="8. Warranties and Liability">
        <p>The application is provided <strong>"as is"</strong> without warranties of any kind. The author assumes no responsibility for errors, outages, data loss, or damages arising from use. Users use the application at their own risk.</p>
      </Section>
      <Section title="9. Intellectual Property">
        <p>The project is published as open-source under the <strong>MIT License</strong> (source code) and <strong>Creative Commons Attribution 4.0</strong> (documentation). Logos and names of third parties are trademarks of their respective owners.</p>
      </Section>
      <Section title="10. Privacy">
        <p>The processing of personal data is described in the <Link to="/privacy" style={{ color: 'var(--accent)' }} className="hover:underline">Privacy Policy</Link>.</p>
      </Section>
      <Section title="11. Contact">
        <p><strong>DivePlanWeb project author:</strong> Jan Hronek</p>
        <p className="text-xs mt-2" style={{ color: 'var(--text-muted)' }}>Version 2.1 | Last updated: March 9, 2026</p>
      </Section>
    </>
  );
}

export default function TermsPage() {
  const { t, i18n } = useTranslation();
  return (
    <PageContainer>
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold flex items-center gap-3 mb-8" style={{ color: 'var(--text)' }}>
          <FileText style={{ color: 'var(--accent)' }} size={28} />
          {t('common.terms_of_use')}
        </h1>
        <div className="card p-6">
          {i18n.language === 'cs' ? <ContentCS /> : <ContentEN />}
        </div>
      </div>
    </PageContainer>
  );
}
