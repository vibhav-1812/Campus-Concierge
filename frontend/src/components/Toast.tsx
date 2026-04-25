import { useState, useCallback, useEffect } from 'react'
import { X, AlertCircle, AlertTriangle, Info } from 'lucide-react'

export type ToastVariant = 'error' | 'warning' | 'info'

export interface ToastState {
  id: number
  message: string
  variant: ToastVariant
}

const VARIANT_STYLES: Record<ToastVariant, string> = {
  error:
    'border-red-200 bg-red-50 text-red-900 shadow-red-100',
  warning:
    'border-amber-200 bg-amber-50 text-amber-950 shadow-amber-100',
  info: 'border-slate-200 bg-white text-slate-800 shadow-slate-200',
}

const VARIANT_ICONS: Record<ToastVariant, typeof AlertCircle> = {
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

export function useToast(autoDismissMs = 7000) {
  const [toast, setToast] = useState<ToastState | null>(null)

  const showToast = useCallback((message: string, variant: ToastVariant = 'error') => {
    setToast({ id: Date.now(), message, variant })
  }, [])

  const dismissToast = useCallback(() => setToast(null), [])

  useEffect(() => {
    if (!toast) return
    const t = window.setTimeout(dismissToast, autoDismissMs)
    return () => window.clearTimeout(t)
  }, [toast, dismissToast, autoDismissMs])

  return { toast, showToast, dismissToast }
}

interface ToastProps {
  toast: ToastState | null
  onDismiss: () => void
}

export function Toast({ toast, onDismiss }: ToastProps) {
  if (!toast) return null

  const Icon = VARIANT_ICONS[toast.variant]

  return (
    <div
      role="alert"
      className="pointer-events-none fixed inset-x-0 top-0 z-[100] flex justify-center px-4 pt-4 sm:pt-6"
    >
      <div
        className={`pointer-events-auto flex max-w-lg items-start gap-3 rounded-xl border px-4 py-3 shadow-xl ${VARIANT_STYLES[toast.variant]}`}
      >
        <Icon className="mt-0.5 h-5 w-5 shrink-0 opacity-90" aria-hidden />
        <p className="min-w-0 flex-1 text-sm leading-snug">{toast.message}</p>
        <button
          type="button"
          onClick={onDismiss}
          className="shrink-0 rounded-lg p-1 opacity-70 transition hover:bg-black/5 hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-vt-maroon/40"
          aria-label="Dismiss notification"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}
