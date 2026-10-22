import type { ComponentProps, ReactNode } from 'react'

type Size = 'icon' | 'default' | 'wide'

const SIZES: Record<Size, string> = {
  icon: 'p-0.5',
  default: 'px-4 py-2',
  wide: 'px-8 py-3 w-full',
}

const VARIANTS = {
  primary: 'bg-sea text-white',
  secondary: 'bg-white text-ink border border-sea',
  danger: 'bg-alert text-white',
}

export function Button({
  size = 'default',
  variant = 'primary',
  children,
  ...rest
}: ComponentProps<'button'> & { size?: Size; variant?: keyof typeof VARIANTS; children: ReactNode }) {
  return (
    <button className={`rounded ${SIZES[size]} ${VARIANTS[variant]}`} {...rest}>
      {children}
    </button>
  )
}

export function Icon({ name }: { name: string }) {
  return <svg aria-hidden="true" className="size-4" role="presentation" data-icon={name} />
}
