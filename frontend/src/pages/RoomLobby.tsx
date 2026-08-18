import { useState } from "react";
import { Navigate, useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { getRoom } from "../api/rooms";
import { useSession } from "../lib/session";
import { Button, Card } from "../components/ui";

export default function RoomLobby() {
  const { roomCode } = useParams<{ roomCode: string }>();
  const { session } = useSession();
  const navigate = useNavigate();
  const [copied, setCopied] = useState(false);

  const query = useQuery({
    queryKey: ["room", roomCode],
    queryFn: () => getRoom(roomCode!),
    enabled: Boolean(roomCode),
    refetchInterval: 3000,
  });

  if (!roomCode) {
    return <Navigate to="/" replace />;
  }

  // No local session for this room (e.g. a shared link opened fresh) -> send
  // them through the join flow with the code pre-filled.
  if (!session || session.roomCode.toUpperCase() !== roomCode.toUpperCase()) {
    return <Navigate to={`/join?code=${roomCode}`} replace />;
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(roomCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard API can fail (permissions, non-secure context) — not worth surfacing an error for
    }
  };

  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Card className="flex flex-col items-center text-center">
          <p className="mb-2 text-sm font-medium uppercase tracking-wide text-ink-secondary">
            Room code
          </p>

          <button
            onClick={handleCopy}
            className="mb-1 flex items-center gap-3 rounded-xl px-4 py-2 font-mono text-4xl font-bold tracking-[0.2em] text-accent transition-colors hover:bg-accent-subtle"
            title="Click to copy"
          >
            {roomCode}
          </button>
          <p className="mb-8 text-sm text-ink-muted">
            {copied ? "Copied!" : "Click the code to copy"}
          </p>

          {query.data && (
            <p className="mb-1 text-lg text-ink">
              <span className="font-semibold text-accent">{query.data.member_count}</span>{" "}
              {query.data.member_count === 1 ? "person" : "people"} in the room
            </p>
          )}
          {query.data && (
            <p className="mb-8 text-sm text-ink-secondary">Genre: {query.data.genre}</p>
          )}

          <Button
            className="w-full"
            onClick={() => navigate(`/room/${roomCode}/swipe`)}
          >
            Start Swiping
          </Button>
        </Card>
      </motion.div>
    </div>
  );
}
