interface ErrorAlertProps {
  message: string
  onDismiss?: () => void
}

export default function ErrorAlert({ message, onDismiss }: ErrorAlertProps) {
  if (!message) return null

  return (
    <div className="animate-slide-up flex items-start gap-3 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
      <svg
        className="mt-0.5 h-5 w-5 shrink-0 text-red-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p className="flex-1">{message}</p>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="shrink-0 text-red-300 hover:text-white"
          aria-label="Dismiss"
        >
          ✕
        </button>
      )}
    </div>
  )
}
