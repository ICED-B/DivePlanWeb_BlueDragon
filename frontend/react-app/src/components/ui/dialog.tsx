import { useEffect, HTMLAttributes, MouseEvent } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '../../lib/utils';
import { X } from 'lucide-react';

interface DialogProps {
  open: boolean;
  onClose: () => void;
  children: React.ReactNode;
  className?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const sizeClasses = {
  sm:   'max-w-sm',
  md:   'max-w-lg',
  lg:   'max-w-2xl',
  xl:   'max-w-4xl',
  full: 'max-w-[95vw]',
};

export function Dialog({ open, onClose, children, className, size = 'md' }: DialogProps) {
  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [open, onClose]);

  // Prevent body scroll when open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  if (!open) return null;

  const handleBackdrop = (e: MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget) onClose();
  };

  return createPortal(
    <div
      className="fixed inset-0 flex items-center justify-center p-4 animate-fade-in"
      style={{ backgroundColor: 'rgba(0,0,0,0.65)', zIndex: 100, backdropFilter: 'blur(2px)' }}
      onClick={handleBackdrop}
    >
      <div
        className={cn(
          'card w-full max-h-[90vh] overflow-y-auto animate-fade-in',
          sizeClasses[size],
          className
        )}
      >
        {children}
      </div>
    </div>,
    document.body
  );
}

interface DialogHeaderProps extends HTMLAttributes<HTMLDivElement> {
  onClose?: () => void;
  title?: string;
}

export function DialogHeader({ onClose, title, children, className, ...props }: DialogHeaderProps) {
  return (
    <div
      className={cn('flex items-center justify-between mb-4 pb-4', className)}
      style={{ borderBottom: '1px solid var(--border)' }}
      {...props}
    >
      <div className="flex-1">
        {title && <h2 className="text-xl font-semibold" style={{ color: 'var(--text)' }}>{title}</h2>}
        {children}
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="btn-ghost p-1.5 rounded-md ml-4 flex-shrink-0"
          style={{ color: 'var(--text-muted)' }}
        >
          <X size={18} />
        </button>
      )}
    </div>
  );
}

export function DialogContent({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('', className)} {...props} />;
}

export function DialogFooter({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn('flex items-center justify-end gap-3 mt-6 pt-4', className)}
      style={{ borderTop: '1px solid var(--border)' }}
      {...props}
    />
  );
}
