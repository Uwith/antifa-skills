#!/usr/bin/env node

import { spawnSync } from "node:child_process";

const MAX_ATTEMPTS = 10;
const RETRY_DELAY_MS = 3000;
const RETRYABLE_ERROR = "HID Device Not Ready";

const args = process.argv.slice(2);

if (args.length === 0 || args.includes("--wrapper-help")) {
  console.log(`Usage: retry-dejaos.mjs <dejaos command> [options]

Retries only "${RETRYABLE_ERROR}" up to ${MAX_ATTEMPTS} attempts,
waiting ${RETRY_DELAY_MS / 1000} seconds between attempts.

Example:
  node retry-dejaos.mjs sync --project FaceLock`);
  process.exit(args.length === 0 ? 1 : 0);
}

function sleep(milliseconds) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, milliseconds);
}

for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt += 1) {
  console.error(`[dejaos retry] attempt ${attempt}/${MAX_ATTEMPTS}: dejaos ${args.join(" ")}`);

  const result = spawnSync("dejaos", args, {
    encoding: "utf8",
    env: process.env,
  });

  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);

  if (result.error) {
    console.error(`[dejaos retry] failed to launch dejaos: ${result.error.message}`);
    process.exit(1);
  }

  if (result.status === 0) process.exit(0);

  const output = `${result.stdout || ""}\n${result.stderr || ""}`;
  if (!output.includes(RETRYABLE_ERROR)) {
    console.error("[dejaos retry] non-retryable failure");
    process.exit(result.status || 1);
  }

  if (attempt < MAX_ATTEMPTS) {
    console.error(`[dejaos retry] HID not ready; retrying in ${RETRY_DELAY_MS / 1000}s`);
    sleep(RETRY_DELAY_MS);
  }
}

console.error(`[dejaos retry] device unavailable after ${MAX_ATTEMPTS} attempts`);
process.exit(1);
