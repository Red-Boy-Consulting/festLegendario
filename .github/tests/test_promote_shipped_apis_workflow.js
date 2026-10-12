// Copyright (c) Microsoft. All rights reserved.

const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { mkdtempSync, readFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const { join, resolve } = require('node:path');
const { describe, it } = require('node:test');

const workflow = readFileSync(resolve(__dirname, '../workflows/promote-shipped-apis.yml'), 'utf8');
const steps = workflow.split(/^      - name: /m);
const step = (name) => {
  const result = steps.find((value) => value.startsWith(`${name}\n`));
  assert.ok(result, `Missing workflow step: ${name}`);
  return result;
};

describe('Promote shipped APIs authentication', () => {
  it('uses App authentication only when both credentials are present', () => {
    const configuration = step('Check GitHub App configuration');
    assert.match(configuration, /APP_ID: \$\{\{ secrets\.GHA_TOKEN_PROVIDER_APP_ID \}\}/);
    assert.match(configuration, /APP_PRIVATE_KEY: \$\{\{ secrets\.GHA_TOKEN_PROVIDER_PEM \}\}/);
    const script = configuration.split('        run: |\n')[1].replace(/^          /gm, '');
    const directory = mkdtempSync(join(tmpdir(), 'promote-apis-test-'));
    try {
      for (const [appId, privateKey, expected] of [
        ['', '', 'false'],
        ['test-app', '', 'false'],
        ['', 'test-key', 'false'],
        ['test-app', 'test-key', 'true'],
      ]) {
        const output = join(directory, `output-${appId}-${privateKey}`);
        const result = spawnSync('bash', ['-e', '-c', script], {
          encoding: 'utf8',
          env: { ...process.env, APP_ID: appId, APP_PRIVATE_KEY: privateKey, GITHUB_OUTPUT: output },
        });
        assert.equal(result.status, 0, result.stderr);
        assert.equal(readFileSync(output, 'utf8'), `configured=${expected}\n`);
        assert.ok(!result.stdout.includes('test-app') && !result.stdout.includes('test-key'));
      }
    } finally {
      rmSync(directory, { recursive: true, force: true });
    }
    for (const name of ['Generate GitHub App token', 'Get GitHub App user ID']) {
      assert.match(step(name), /if: steps\.app-config\.outputs\.configured == 'true'/);
    }
    assert.doesNotMatch(step('Generate GitHub App token'), /continue-on-error:/);
  });

  it('grants the fallback token the required repository permissions', () => {
    assert.match(workflow, /permissions:\n      contents: write\n      pull-requests: write/);
    assert.match(step('Generate GitHub App token'), /permission-contents: write\n          permission-pull-requests: write/);
  });

  it('uses the selected token for checkout, git, and all PR operations', () => {
    for (const name of ['Checkout code', 'Configure git', 'Check for existing PR', 'Create new PR']) {
      assert.match(step(name), /(?:token|GH_TOKEN): \$\{\{ steps\.app-token\.outputs\.token \|\| github\.token \}\}/);
    }
    assert.match(step('Checkout code'), /fetch-depth: 0/);
  });

  it('configures a valid identity for either bot', () => {
    const configuration = step('Configure git');
    assert.match(configuration, /steps\.app-token\.outputs\.app-slug/);
    assert.match(configuration, /steps\.get-user-id\.outputs\.user-id/);
    assert.match(configuration, /\|\| 'github-actions\[bot\]'/);
    assert.match(configuration, /\|\| '41898282\+github-actions\[bot\]@users\.noreply\.github\.com'/);
    assert.match(configuration, /git config user\.name "\$env:GIT_USER_NAME"/);
    assert.match(configuration, /git config user\.email "\$env:GIT_USER_EMAIL"/);
  });

  it('runs regression tests when the promotion workflow changes', () => {
    const testsWorkflow = readFileSync(resolve(__dirname, '../workflows/github-automation-tests.yml'), 'utf8');
    assert.equal(testsWorkflow.match(/- "\.github\/workflows\/promote-shipped-apis\.yml"/g).length, 2);
  });
});
