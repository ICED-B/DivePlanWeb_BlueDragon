import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import HttpBackend from 'i18next-http-backend';

// Namespaces:
//  translation — sdílené: nav, theme, lang, auth, common
//  home        — úvodní stránka
//  planner     — plánovač + kalkulačky
//  stats       — statistiky
//  data        — ponory, místa, výlety, plyny, vybavení
//  admin       — admin panel, logy
//  profile     — profil + jednotky

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'cs',
    supportedLngs: ['cs', 'en'],

    ns: ['translation', 'home', 'planner', 'stats', 'data', 'admin', 'profile'],
    defaultNS: 'translation',
    // fallbackNS ensures t('planner.title') found in planner.json even if not in translation.json
    fallbackNS: ['home', 'planner', 'stats', 'data', 'admin', 'profile'],

    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },

    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
      lookupLocalStorage: 'lang',
    },

    interpolation: {
      escapeValue: false,
    },

    react: {
      useSuspense: true,
    },
  });

export default i18n;
