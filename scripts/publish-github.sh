#!/usr/bin/env bash
# Run only on the owner's already authenticated machine. No credentials are read
# from project files, and no authentication is attempted by this script.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OWNER="ForceMind"
REPO="ai-phone-ui"
TARGET="$OWNER/$REPO"
command -v git >/dev/null || { echo '需要安装 Git。' >&2; exit 1; }
command -v gh >/dev/null || { echo '需要安装 GitHub CLI，并先由你运行 gh auth login。' >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo 'GitHub CLI 尚未登录。请在你自己的终端授权；不要把令牌写入此项目。' >&2; exit 1; }
LOGIN="$(gh api user --jq '.login')"
[[ "$LOGIN" == "$OWNER" ]] || { echo "当前账户是 $LOGIN，而目标所有者应是 $OWNER；已停止。" >&2; exit 1; }
cd "$ROOT"
TMP="$(mktemp -d)"
trap 'rm -rf -- "$TMP"' EXIT
# A 404 is the only accepted missing-target result. Other failures are not treated
# as absence and must not lead to accidental repository creation.
if gh api "repos/$TARGET" >"$TMP/target.json" 2>"$TMP/lookup.err"; then
  echo "目标 $TARGET 已存在。为避免覆盖，停止；请由维护者核对现有仓库。" >&2
  exit 1
elif ! grep -q '(HTTP 404)' "$TMP/lookup.err"; then
  cat "$TMP/lookup.err" >&2
  echo '无法可靠确认目标状态，停止创建。' >&2
  exit 1
fi
if [[ ! -d "$ROOT/.git" ]]; then
  [[ -f "$ROOT/project-history.bundle" ]] || { echo '没有 .git 或 project-history.bundle；不能丢弃历史建空仓库。' >&2; exit 1; }
  git clone --quiet --no-checkout --branch main "$ROOT/project-history.bundle" "$TMP/history"
  mv "$TMP/history/.git" "$ROOT/.git"
  git read-tree HEAD  # Populate index only; never overwrite working files.
  git remote remove origin
  # Some ZIP extractors discard executable mode; restore this known tracked script.
  chmod +x "$ROOT/scripts/publish-github.sh"
fi
[[ "$(git rev-parse --show-toplevel)" == "$ROOT" ]] || { echo 'Git根目录不匹配。' >&2; exit 1; }
[[ "$(git branch --show-current)" == 'main' ]] || { echo '请先检查并切换到 main；脚本不会强制切分支。' >&2; exit 1; }
[[ -z "$(git status --porcelain)" ]] || { echo '存在未提交改动。请检查并提交后再发布；脚本不会stash/reset/clean。' >&2; exit 1; }
if git remote get-url origin >/dev/null 2>&1; then
  echo '已有origin，停止；不覆盖现有远端配置。' >&2; exit 1
fi
printf '即将创建私有仓库 %s，并推送当前 main 与已有标签。\n' "$TARGET"
# The user explicitly runs this script for the authorized repository creation.
if ! gh repo create "$TARGET" --private --source "$ROOT" --remote origin --push \
  --description 'Gesture-first AI phone UI: N9/Sailfish-inspired interaction, complete screen workbench, local-first prototype'; then
  echo '创建或推送失败。远端可能已创建；请先核对，脚本不会删除远端或重复执行。' >&2
  exit 1
fi
git push origin --tags
LOCAL="$(git rev-parse HEAD)"
REMOTE="$(git ls-remote origin refs/heads/main | cut -f1)"
[[ "$LOCAL" == "$REMOTE" ]] || { echo '远端HEAD与本地不一致，需人工检查。' >&2; exit 1; }
printf '已核对 main HEAD: %s\n' "$LOCAL"
echo '请读取实际Actions结果，再更新远端状态文档；此脚本不会声称CI或部署成功。'
