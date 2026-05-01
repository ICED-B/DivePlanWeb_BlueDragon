import { createContext, useContext, HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

type TabsContextType = { active: string; setActive: (v: string) => void };
const TabsCtx = createContext<TabsContextType>({ active: '', setActive: () => {} });

interface TabsProps extends HTMLAttributes<HTMLDivElement> {
  value: string;
  onValueChange: (v: string) => void;
}

export function Tabs({ value, onValueChange, className, children, ...props }: TabsProps) {
  return (
    <TabsCtx.Provider value={{ active: value, setActive: onValueChange }}>
      <div className={cn('w-full', className)} {...props}>
        {children}
      </div>
    </TabsCtx.Provider>
  );
}

export function TabsList({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('flex gap-1 p-1 rounded-lg mb-4', className)}
      style={{ backgroundColor: 'var(--bg-muted)' }}
      {...props}
    />
  );
}

interface TabsTriggerProps extends HTMLAttributes<HTMLButtonElement> {
  value: string;
}

export function TabsTrigger({ value, className, children, ...props }: TabsTriggerProps) {
  const { active, setActive } = useContext(TabsCtx);
  const isActive = active === value;
  return (
    <button
      onClick={() => setActive(value)}
      className={cn(
        'px-4 py-2 text-sm font-medium rounded-md transition-all',
        isActive
          ? 'text-white'
          : 'hover:text-[var(--text)]',
        className
      )}
      style={
        isActive
          ? { backgroundColor: 'var(--accent)', color: 'var(--accent-fg)' }
          : { color: 'var(--text-muted)' }
      }
      {...(props as any)}
    >
      {children}
    </button>
  );
}

interface TabsContentProps extends HTMLAttributes<HTMLDivElement> {
  value: string;
}

export function TabsContent({ value, className, ...props }: TabsContentProps) {
  const { active } = useContext(TabsCtx);
  if (active !== value) return null;
  return <div className={cn('animate-fade-in', className)} {...props} />;
}
