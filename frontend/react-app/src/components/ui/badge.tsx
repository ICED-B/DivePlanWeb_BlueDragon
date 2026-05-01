import { HTMLAttributes } from 'react';
import { cn } from '../../lib/utils';

type BadgeVariant = 'default' | 'accent' | 'success' | 'warning' | 'danger' | 'muted';

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant;
}

const variantStyles: Record<BadgeVariant, { bg: string; color: string }> = {
  default: { bg: 'var(--bg-hover)', color: 'var(--text)' },
  accent:  { bg: 'color-mix(in srgb, var(--accent) 20%, transparent)', color: 'var(--accent)' },
  success: { bg: 'color-mix(in srgb, var(--success) 20%, transparent)', color: 'var(--success)' },
  warning: { bg: 'color-mix(in srgb, var(--warning) 20%, transparent)', color: 'var(--warning)' },
  danger:  { bg: 'color-mix(in srgb, var(--danger) 20%, transparent)', color: 'var(--danger)' },
  muted:   { bg: 'var(--bg-muted)', color: 'var(--text-muted)' },
};

export function Badge({ className, variant = 'default', style, ...props }: BadgeProps) {
  const v = variantStyles[variant];
  return (
    <span
      className={cn('badge', className)}
      style={{ backgroundColor: v.bg, color: v.color, ...style }}
      {...props}
    />
  );
}
