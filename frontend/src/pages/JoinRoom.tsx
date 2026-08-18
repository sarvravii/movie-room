import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { joinRoom } from "../api/rooms";
import { useSession } from "../lib/session";
import { Button, Card, ErrorText, TextInput } from "../components/ui";

export default function JoinRoom() {
  const navigate = useNavigate();
  const { setSession } = useSession();
  const [searchParams] = useSearchParams();

  const [code, setCode] = useState(searchParams.get("code")?.toUpperCase() ?? "");
  const [name, setName] = useState("");

  const mutation = useMutation({
    mutationFn: () => joinRoom(code.trim().toUpperCase(), name.trim()),
    onSuccess: (room) => {
      setSession({
        userId: room.user_id,
        displayName: name.trim(),
        roomCode: room.code,
      });
      navigate(`/room/${room.code}`);
    },
  });

  const canSubmit = code.trim().length > 0 && name.trim().length > 0 && !mutation.isPending;

  const errorMessage =
    mutation.error && "response" in mutation.error
      ? (mutation.error as { response?: { status?: number } }).response?.status === 404
        ? "No room found with that code."
        : (mutation.error as { response?: { status?: number } }).response?.status === 409
          ? "You've already joined this room — head to the lobby."
          : "Couldn't join the room. Please try again."
      : null;

  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-md"
      >
        <Link to="/" className="mb-6 inline-block text-sm text-ink-secondary hover:text-ink">
          ← Back
        </Link>

        <Card>
          <h1 className="mb-2 text-3xl font-semibold text-ink">Join a Room</h1>
          <p className="mb-8 text-ink-secondary">
            Enter the room code your friend shared with you.
          </p>

          <form
            className="flex flex-col gap-6"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSubmit) mutation.mutate();
            }}
          >
            <div className="flex flex-col gap-2">
              <label htmlFor="code" className="text-sm font-medium text-ink-secondary">
                Room code
              </label>
              <TextInput
                id="code"
                placeholder="e.g. 84R5AD"
                value={code}
                onChange={(e) => setCode(e.target.value.toUpperCase())}
                className="text-center font-mono text-lg tracking-[0.3em] uppercase"
                maxLength={10}
                autoFocus
              />
            </div>

            <div className="flex flex-col gap-2">
              <label htmlFor="name" className="text-sm font-medium text-ink-secondary">
                Your name
              </label>
              <TextInput
                id="name"
                placeholder="e.g. Nate"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>

            {errorMessage && <ErrorText>{errorMessage}</ErrorText>}

            <Button type="submit" disabled={!canSubmit} className="w-full">
              {mutation.isPending ? "Joining…" : "Join Room"}
            </Button>
          </form>
        </Card>
      </motion.div>
    </div>
  );
}
