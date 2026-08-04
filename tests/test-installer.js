'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const installer = path.join(root, 'bin', 'install.js');
const tempRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'rate-skill-installer-'));
const target = path.join(tempRoot, 'claude', 'skills', 'rate');

function run(args) {
  const result = spawnSync(process.execPath, [installer, ...args], {
    cwd: root,
    encoding: 'utf8',
  });

  assert.equal(
    result.status,
    0,
    `Installer failed.\nstdout:\n${result.stdout}\nstderr:\n${result.stderr}`
  );
  return result;
}

try {
  run(['--target', target, '--quiet']);
  assert.ok(fs.existsSync(path.join(target, 'SKILL.md')));
  assert.ok(fs.existsSync(path.join(target, 'scripts', 'check_rating.py')));
  assert.ok(fs.existsSync(path.join(target, '.rate-skill-install.json')));

  fs.writeFileSync(path.join(target, 'stale-file.txt'), 'remove me', 'utf8');
  run(['--target', target, '--quiet']);
  assert.equal(fs.existsSync(path.join(target, 'stale-file.txt')), false);

  run(['--target', target, '--verify', '--quiet']);

  run(['--target', target, '--uninstall', '--quiet']);
  assert.equal(fs.existsSync(target), false);

  console.log('Installer tests passed');
} finally {
  fs.rmSync(tempRoot, { recursive: true, force: true });
}
