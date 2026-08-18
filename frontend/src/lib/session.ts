import {
  createContext,
  createElement,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";

export interface SessionState {
  userId: number;
  displayName: string;
  roomCode: string;
}

interface SessionContextValue {
  session: SessionState | null;
  setSession: (session: SessionState) => void;
  clearSession: () => void;
}

const STORAGE_KEY = "movieroom.session";

const SessionContext = createContext<SessionContextValue | undefined>(undefined);

function loadStoredSession(): SessionState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as SessionState;
  } catch {
    return null;
  }
}

export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSessionState] = useState<SessionState | null>(loadStoredSession);

  const setSession = (next: SessionState) => {
    setSessionState(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  };

  const clearSession = () => {
    setSessionState(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const value = useMemo(() => ({ session, setSession, clearSession }), [session]);

  return createElement(SessionContext.Provider, { value }, children);
}

export function useSession(): SessionContextValue {
  const ctx = useContext(SessionContext);
  if (!ctx) {
    throw new Error("useSession must be used within a SessionProvider");
  }
  return ctx;
}
