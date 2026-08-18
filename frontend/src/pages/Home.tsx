import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Button } from "../components/ui";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex min-h-svh flex-col items-center justify-center px-6 py-16">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="flex w-full max-w-md flex-col items-center text-center"
      >
        <span className="mb-4 rounded-full border border-base-border bg-base-surface px-4 py-1.5 text-sm text-ink-secondary">
          Swipe together, pick faster
        </span>
        <h1 className="mb-4 text-5xl font-semibold tracking-tight text-ink">
          Movie <span className="text-accent">Room</span>
        </h1>
        <p className="mb-10 text-lg leading-relaxed text-ink-secondary">
          Create a room, invite your people, and swipe through movies
          together. When everyone agrees, that's your match.
        </p>

        <div className="flex w-full flex-col gap-3">
          <Button className="w-full" onClick={() => navigate("/create")}>
            Create a Room
          </Button>
          <Button
            variant="secondary"
            className="w-full"
            onClick={() => navigate("/join")}
          >
            Join a Room
          </Button>
        </div>
      </motion.div>
    </div>
  );
}
