import { createContext, useContext, useEffect, useState } from 'react';

export type Theme = 'ocean' | 'light' | 'gray';

type ThemeContextType = {
  theme: Theme;
  setTheme: (t: Theme) => void;
};

const ThemeContext = createContext<ThemeContextType>({
  theme: 'ocean',
  setTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

export const ThemeProvider = ({ children }: { children: React.ReactNode }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme') as Theme | null;
    return saved ?? 'ocean';
  });

  const setTheme = (t: Theme) => {
    setThemeState(t);
    localStorage.setItem('theme', t);
  };

  useEffect(() => {
    const root = document.documentElement;
    // Remove all theme attributes first
    root.removeAttribute('data-theme');
    // Apply the selected theme (default/ocean has no data-theme attribute needed,
    // but we set it for clarity)
    if (theme === 'ocean') {
      // default CSS vars already cover ocean theme
      root.removeAttribute('data-theme');
    } else {
      root.setAttribute('data-theme', theme);
    }
  }, [theme]);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
