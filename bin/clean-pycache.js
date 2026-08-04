#!/usr/bin/env node
"use strict";

// Removes __pycache__/*.pyc from rate/ before packing. Exists because npm's
// "files" array does not reliably re-apply .npmignore recursively inside a
// wholesale-included directory (verified: a stray local __pycache__ from
// running the Python test suite still showed up in `npm pack --dry-run`
// output with only .npmignore in place). Runs as the "prepack" script so it
// fires automatically before `npm pack` / `npm publish`, regardless of what
// the maintainer's working tree happens to have on disk.

const fs = require("fs");
const path = require("path");

const root = path.join(__dirname, "..", "rate");

function removePycache(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      if (entry.name === "__pycache__") {
        fs.rmSync(full, { recursive: true, force: true });
      } else {
        removePycache(full);
      }
    }
  }
}

removePycache(root);
