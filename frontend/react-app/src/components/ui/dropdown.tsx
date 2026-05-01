import { useState, useRef, useEffect, HTMLAttributes, ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../lib/utils';
import { ChevronDown } from 'lucide-react';

interface DropdownProps {
  trigger: ReactNode;
  children: ReactNode;
  align?: 'left' | 'right';
  className?: string;
}

export function Dropdown({ trigger, children, align = 'left', className }: DropdownProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} className={cn('relative', className)}>
      <div onClick={() => setOpen((p) => !p)}>{trigger}</div>
      {open && (
        <div
          className={cn(
            'absolute top-full mt-1 min-w-[180px] dropdown-content p-1 animate-fade-in z-50',
            align === 'right' ? 'right-0' : 'left-0'
          )}
        >
          <div onClick={() => setOpen(false)}>
            {children}
          </div>
        </div>
      )}
    </div>
  );
}

interface DropdownItemProps extends HTMLAttributes<HTMLDivElement> {
  icon?: ReactNode;
  danger?: boolean;
}

export function DropdownItem({ icon, danger, className, children, ...props }: DropdownItemProps) {
  return (
    <div
      className={cn(
        'dropdown-item flex items-center gap-2 px-3 py-2 text-sm',
        danger && 'hover:!text-[var(--danger)]',
        className
      )}
      {...props}
    >
      {icon && <span className="w-4 h-4 flex-shrink-0" style={{ color: 'var(--text-muted)' }}>{icon}</span>}
      {children}
    </div>
  );
}

export function DropdownSeparator() {
  return <div className="my-1 h-px" style={{ backgroundColor: 'var(--border)' }} />;
}

interface NavDropdownProps {
  label: string;
  icon?: ReactNode;
  children: ReactNode;
}

export function NavDropdown({ label, icon, children }: NavDropdownProps) {
  const [open, setOpen] = useState(false);
  const btnRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ top: 0, left: 0 });

  useEffect(() => {
    if (open && btnRef.current) {
      const rect = btnRef.current.getBoundingClientRect();
      setPos({ top: rect.bottom + 4, left: rect.left });
    }
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const updatePos = () => {
      if (btnRef.current) {
        const rect = btnRef.current.getBoundingClientRect();
        setPos({ top: rect.bottom + 4, left: rect.left });
      }
    };
    const handleOutside = (e: MouseEvent) => {
      if (
        btnRef.current && !btnRef.current.contains(e.target as Node) &&
        menuRef.current && !menuRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    window.addEventListener('scroll', updatePos, true);
    window.addEventListener('resize', updatePos);
    return () => {
      document.removeEventListener('mousedown', handleOutside);
      window.removeEventListener('scroll', updatePos, true);
      window.removeEventListener('resize', updatePos);
    };
  }, [open]);

  return (
    <>
      <button
        ref={btnRef}
        onClick={() => setOpen((p) => !p)}
        className={cn(
          'flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all',
          'hover:text-[var(--accent)]',
          open ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'
        )}
        style={{
          backgroundColor: open ? 'var(--bg-hover)' : 'transparent',
        }}
      >
        {icon && <span className="w-4 h-4">{icon}</span>}
        {label}
        <ChevronDown
          size={14}
          className="transition-transform"
          style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }}
        />
      </button>
      {open && createPortal(
        <div
          ref={menuRef}
          style={{ position: 'fixed', top: pos.top, left: pos.left, zIndex: 9999 }}
          className="min-w-[200px] dropdown-content p-1 animate-fade-in"
          onClick={() => setOpen(false)}
        >
          {children}
        </div>,
        document.body
      )}
    </>
  );
}
