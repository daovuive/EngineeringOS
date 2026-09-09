#!/usr/bin/env bash
set -Eeuo pipefail

fail() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

if [[ "${1:-}" == "--help" ]]; then
  printf 'Usage: bash %s [http://127.0.0.1:8081]\n' "$0"
  exit 0
fi

[[ $# -le 1 ]] || fail "Provide at most one argument: the EOS URL."
[[ $EUID -ne 0 ]] || fail "Run as your normal user, not with sudo bash."

if [[ -z "${WSL_DISTRO_NAME:-}" ]] &&
   ! grep -qi microsoft /proc/sys/kernel/osrelease; then
  fail "This installer is intended for WSL."
fi

source /etc/os-release
case "${ID:-}" in
  ubuntu|debian) ;;
  *) fail "This script supports Ubuntu/Debian in WSL." ;;
esac

export EOS_BASE_URL="${1:-}"
if [[ -n "$EOS_BASE_URL" ]]; then
  case "$EOS_BASE_URL" in
    http://*|https://*) ;;
    *) fail "The URL must begin with http:// or https://." ;;
  esac
fi

TOOL_DIR="$HOME/.local/share/eos-webui-testing"
MARKER="$TOOL_DIR/.managed-by-eos-test-setup"

if [[ -e "$TOOL_DIR" && ! -f "$MARKER" ]]; then
  fail "$TOOL_DIR already exists without this script's marker."
fi

mkdir -p "$TOOL_DIR/logs" "$TOOL_DIR/tests"
touch "$MARKER"

LOG_FILE="$TOOL_DIR/logs/setup-$(date +%Y%m%d-%H%M%S)-$$.log"
exec > >(tee -a "$LOG_FILE") 2>&1

trap 'rc=$?; printf "\nStopped at line %s, exit %s.\nLog: %s\n" \
  "$LINENO" "$rc" "$LOG_FILE" >&2; exit "$rc"' ERR

printf '\n[1/6] Installing system prerequisites...\n'
sudo -v
sudo apt-get update
sudo apt-get install -y curl ca-certificates git xz-utils

printf '\n[2/6] Installing/loading nvm...\n'
export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
  INSTALLER="$(mktemp /tmp/eos-nvm.XXXXXX)"
  trap 'rm -f -- "$INSTALLER"' EXIT
  curl -fSL --retry 3 \
    https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.7/install.sh \
    -o "$INSTALLER"
  PROFILE="$HOME/.bashrc" bash "$INSTALLER"
fi

# Load nvm directly: non-interactive .bashrc may return early.
set +u
source "$NVM_DIR/nvm.sh" --no-use
nvm install --lts
nvm alias default 'lts/*'
nvm use --lts
set -u

[[ "$(node -p 'process.platform')" == "linux" ]] ||
  fail "Node must be the Linux installation inside WSL."

printf '\n[3/6] Preparing the isolated test workspace...\n'
cd "$TOOL_DIR"

# Existing configuration/test files are preserved on subsequent runs.
if [[ ! -e package.json ]]; then
  cat > package.json <<'PACKAGE'
{
  "name": "eos-webui-testing",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "test": "playwright test --config=playwright.config.cjs",
    "report": "playwright show-report --host 127.0.0.1"
  }
}
PACKAGE
fi

if [[ ! -e playwright.config.cjs ]]; then
  cat > playwright.config.cjs <<'CONFIG'
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.cjs',
  timeout: 30000,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  use: {
    browserName: 'chromium',
    headless: true,
    viewport: { width: 1536, height: 1024 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure'
  }
});
CONFIG
fi

if [[ ! -e tests/environment.spec.cjs ]]; then
  cat > tests/environment.spec.cjs <<'TESTS'
const { test, expect } = require('@playwright/test');

test('Chromium can render and interact with a page', async ({ page }, info) => {
  await page.setContent(
    '<h1>Browser ready</h1><label>Message<input></label>'
  );
  await page.getByLabel('Message').fill('EOS browser test');
  await expect(page.getByLabel('Message')).toHaveValue('EOS browser test');

  await info.attach('browser-smoke', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png'
  });
});

test('EOS responds and displays its application page', async ({ page }, info) => {
  test.skip(
    !process.env.EOS_BASE_URL,
    'No EOS URL supplied; browser-only check.'
  );

  const response = await page.goto(process.env.EOS_BASE_URL, {
    waitUntil: 'domcontentloaded'
  });

  expect(response?.ok()).toBeTruthy();
  await expect(page.locator('body')).toContainText(
    /EngineeringOS|Engineering OS/i
  );

  await info.attach('eos-webui', {
    body: await page.screenshot({ fullPage: true }),
    contentType: 'image/png'
  });
});
TESTS
fi

printf '\n[4/6] Installing Playwright...\n'
if [[ -f package-lock.json ]]; then
  # Reuse locked dependency versions on subsequent runs.
  npm ci
else
  npm install --save-dev --save-exact @playwright/test
fi

printf '\n[5/6] Installing Chromium and its system dependencies...\n'
npx --no-install playwright install --with-deps chromium

printf '\nInstalled versions:\n'
node --version
npm --version
npx --no-install playwright --version

printf '\n[6/6] Running smoke tests...\n'
if npm test; then
  TEST_EXIT=0
else
  TEST_EXIT=$?
fi

printf '\nWorkspace: %s\n' "$TOOL_DIR"
printf 'Setup log: %s\n' "$LOG_FILE"
printf 'HTML report: %s/playwright-report/index.html\n' "$TOOL_DIR"

printf '\nTo rerun from a new terminal:\n'
printf '  source "%s/nvm.sh"\n' "$NVM_DIR"
printf '  cd "%s"\n' "$TOOL_DIR"
printf '  npm test\n'

printf '\nTo check a running EOS instance:\n'
printf '  EOS_BASE_URL=http://127.0.0.1:8081 npm test\n'

printf '\nTo open the report server:\n'
printf '  npm run report\n'

if [[ "$TEST_EXIT" -eq 0 ]]; then
  printf '\nPASS: requested smoke tests completed.\n'
else
  printf '\nFAIL: inspect the report. Installation may still be complete.\n'
fi

printf 'These checks do not replace functional EOS workflow tests.\n'
exit "$TEST_EXIT"
