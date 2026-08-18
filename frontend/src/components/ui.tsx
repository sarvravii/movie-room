import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode } from "react";

export function Card({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <div
      className={`rounded-xl2 border border-base-border bg-base-surface p-8 shadow-panel ${className}`}
    >
      {children}
    </div>
  );
}

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base =
    "inline-flex items-center justify-center rounded-xl px-6 py-3 text-base font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";
  const variants = {
    primary: "bg-accent text-white hover:bg-accent-hover active:bg-accent-active",
    secondary:
      "bg-base-raised text-ink border border-base-border hover:border-accent/60",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
}

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  const { className = "", ...rest } = props;
  return (
    <input
      className={`w-full rounded-xl border border-base-border bg-base-raised px-4 py-3 text-ink placeholder:text-ink-muted outline-none transition-colors focus:border-accent ${className}`}
      {...rest}
    />
  );
}

export function ErrorText({ children }: { children: ReactNode }) {
  return <p className="text-sm text-red-400">{children}</p>;
}
