import { AlertCircle, Inbox } from "lucide-react";

type ErrorBannerProps = {
  message: string | null;
};

type EmptyStateProps = {
  title: string;
  description: string;
};

type LoadingBlockProps = {
  className?: string;
  key?: unknown;
};

export function ErrorBanner({ message }: ErrorBannerProps) {
  if (!message) {
    return null;
  }
  return (
    <section className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <span>{message}</span>
    </section>
  );
}

export function EmptyState({ title, description }: EmptyStateProps) {
  return (
    <div className="flex h-full min-h-44 flex-col items-center justify-center rounded-md border border-dashed border-orange-200 bg-orange-50/60 px-4 py-8 text-center">
      <Inbox className="h-6 w-6 text-orange-400" aria-hidden="true" />
      <p className="mt-3 text-sm font-medium text-slate-800">{title}</p>
      <p className="mt-1 max-w-sm text-sm leading-6 text-slate-500">{description}</p>
    </div>
  );
}

export function LoadingBlock({ className = "h-40" }: LoadingBlockProps) {
  return <div className={`${className} animate-pulse rounded-md border border-orange-100 bg-white/80`} />;
}
