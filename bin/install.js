#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const packageRoot = path.resolve(__dirname, '..');
const sourceDir = path.join(packageRoot, 'rate');
const packageJson = JSON.parse(
  fs.readFileSync(path.join(packageRoot, 'package.json'), 'utf8')
);

function printHelp() {
  console.log(`Install the /rate skill for Claude Code.

Usage:
  npx -y github:Mrsavage92/rate-skill
  npx -y github:Mrsavage92/rate-skill -- --verify
  npx -y github:Mrsavage92/rate-skill -- --uninstall

Options:
  --target <path>  Override the install directory
  --verify         Verify an existing installation without changing it
  --uninstall      Remove the installed skill
  --quiet          Suppress non-error output
  -h, --help       Show this help

Default destination:
  ~/.claude/skills/rate
`);
}

function parseArgs(argv) {
  const options = {
    target: process.env.RATE_SKILL_TARGET || null,
    verify: false,
    uninstall: false,
    quiet: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    switch (arg) {
      case '--target':
        i += 1;
        if (!argv[i]) {
          throw new Error('--target requires a path');
        }
        options.target = argv[i];
        break;
      case '--verify':
        options.verify = true;
        break;
      case '--uninstall':
        options.uninstall = true;
        break;
      case '--quiet':
        options.quiet = true;
        break;
      case '-h':
      case '--help':
        options.help = true;
        break;
      default:
        throw new Error(`Unknown option: ${arg}`);
    }
  }

  if (options.verify && options.uninstall) {
    throw new Error('--verify and --uninstall cannot be used together');
  }

  return options;
}

function defaultTarget() {
  return path.join(os.homedir(), '.claude', 'skills', 'rate');
}

function assertSafeTarget(target) {
  const resolved = path.resolve(target);
  const parsed = path.parse(resolved);
  const home = path.resolve(os.homedir());

  if (resolved === parsed.root || resolved === home) {
    throw new Error(`Refusing to operate on unsafe target: ${resolved}`);
  }

  return resolved;
}

function verifyDirectory(directory) {
  const required = [
    'SKILL.md',
    path.join('scripts', 'check_rating.py'),
    path.join('tests', 'run_tests.py'),
  ];

  const missing = required.filter(
    (relativePath) => !fs.existsSync(path.join(directory, relativePath))
  );

  if (missing.length > 0) {
    throw new Error(
      `Incomplete /rate installation at ${directory}. Missing: ${missing.join(', ')}`
    );
  }
}

function removeIfExists(target) {
  fs.rmSync(target, { recursive: true, force: true });
}

function install(target, quiet) {
  verifyDirectory(sourceDir);

  const parent = path.dirname(target);
  const token = `${process.pid}-${Date.now()}`;
  const staging = path.join(parent, `.rate-installing-${token}`);
  const backup = path.join(parent, `.rate-previous-${token}`);
  const updating = fs.existsSync(target);

  fs.mkdirSync(parent, { recursive: true });
  removeIfExists(staging);
  removeIfExists(backup);

  try {
    fs.cpSync(sourceDir, staging, { recursive: true, force: true });
    removeIfExists(path.join(staging, '.last-prompt.txt'));

    fs.writeFileSync(
      path.join(staging, '.rate-skill-install.json'),
      `${JSON.stringify(
        {
          package: packageJson.name,
          version: packageJson.version,
          installedAt: new Date().toISOString(),
          source: 'github:Mrsavage92/rate-skill',
        },
        null,
        2
      )}\n`,
      'utf8'
    );

    verifyDirectory(staging);

    if (updating) {
      fs.renameSync(target, backup);
    }

    try {
      fs.renameSync(staging, target);
    } catch (error) {
      if (updating && fs.existsSync(backup) && !fs.existsSync(target)) {
        fs.renameSync(backup, target);
      }
      throw error;
    }

    removeIfExists(backup);
    verifyDirectory(target);
  } finally {
    removeIfExists(staging);
    if (fs.existsSync(backup) && fs.existsSync(target)) {
      removeIfExists(backup);
    }
  }

  if (!quiet) {
    console.log(`${updating ? 'Updated' : 'Installed'} /rate at ${target}`);
    console.log('Restart Claude Code or run /reload-plugins, then use: /rate <target>');
    console.log('Update later by running the same npx command again.');
  }
}

function uninstall(target, quiet) {
  if (!fs.existsSync(target)) {
    if (!quiet) {
      console.log(`/rate is not installed at ${target}`);
    }
    return;
  }

  removeIfExists(target);
  if (!quiet) {
    console.log(`Removed /rate from ${target}`);
  }
}

function main() {
  try {
    const options = parseArgs(process.argv.slice(2));
    if (options.help) {
      printHelp();
      return;
    }

    const target = assertSafeTarget(options.target || defaultTarget());

    if (options.verify) {
      verifyDirectory(target);
      if (!options.quiet) {
        console.log(`/rate installation verified at ${target}`);
      }
      return;
    }

    if (options.uninstall) {
      uninstall(target, options.quiet);
      return;
    }

    install(target, options.quiet);
  } catch (error) {
    console.error(`rate-skill: ${error.message}`);
    process.exitCode = 1;
  }
}

main();
