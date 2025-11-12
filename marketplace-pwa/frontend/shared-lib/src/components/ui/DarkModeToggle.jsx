import React, { useEffect, useState } from "react";
import ToggleSwitch from "./toggle-switch";

const getInitialMode = () => {
  if (typeof window === "undefined") return "light";
  const stored = localStorage.getItem("theme");
  if (stored) return stored;
  if (window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
  return "light";
};

export default function DarkModeToggle() {
  const [mode, setMode] = useState(getInitialMode);

  useEffect(() => {
    // Try to find Storybook's preview iframe
    const iframe = document.querySelector("iframe#storybook-preview-iframe");
    // If not found, use the main document or parent <html>
    const html =
      iframe?.contentDocument?.documentElement || document.documentElement;
    //
    if (mode === "dark") {
      html.classList.add("dark");
    } else {
      html.classList.remove("dark");
    }
    localStorage.setItem("theme", mode);
  }, [mode]);

  return (
    <div className="flex items-center gap-2">
      <ToggleSwitch
        checked={mode === "dark"}
        onChange={(e) => setMode(e.target.checked ? "dark" : "light")}
        label={mode === "dark" ? "Dark Mode" : "Light Mode"}
        className="px-3 py-1"
      />
    </div>
  );
}
