#!/usr/bin/env bash
# MediaForge release updater (macOS/Linux)
# Moves the 0.0.2 release tag to the current HEAD commit and refreshes the
# GitHub release notes. Run this after every code update so the in-app
# updater offers the latest code to users.
#
# Usage: ./update_release.sh [--notes-file path/to/notes.md]
# If no notes file is given, the existing release notes are kept and only
# the tag is moved and the release is marked Latest.
set -euo pipefail

TAG='0.0.2'
REMOTE='origin'
NOTES_FILE=''

while [ $# -gt 0 ]; do
    case "$1" in
        --notes-file)
            NOTES_FILE="$2"
            shift 2
            ;;
        *)
            echo "Fel: okänt argument: $1" >&2
            exit 1
            ;;
    esac
done

fail() {
    echo "Fel: $1" >&2
    exit 1
}

command -v git >/dev/null 2>&1 || fail 'git saknas i PATH.'

ROOT="$(git rev-parse --show-toplevel)" || fail 'Kunde inte hitta Git-repot.'
cd "$ROOT"
BRANCH="$(git symbolic-ref --quiet --short HEAD)" || fail 'Frikopplad HEAD stöds inte.'
[ "$BRANCH" != main ] && [ "$BRANCH" != master ] || fail 'Release från main/master är spärrad.'

[ -z "$(git status --porcelain)" ] || fail 'Arbetskopian har ocommitade ändringar. Committa eller stash:a först.'

HEAD="$(git rev-parse HEAD)"
echo "HEAD: $HEAD"

git fetch "$REMOTE" "$BRANCH"
REMOTE_TIP="$(git rev-parse FETCH_HEAD)"
[ "$HEAD" = "$REMOTE_TIP" ] || fail "HEAD ($HEAD) skiljer sig från origin/$BRANCH ($REMOTE_TIP). Pusha först."

OLD_TAG="$(git ls-remote "$REMOTE" "refs/tags/$TAG" | awk '{print $1}')"
if [ "$OLD_TAG" = "$HEAD" ]; then
    echo "Taggen $TAG pekar redan på HEAD. Inget att göra."
else
    git push --force "$REMOTE" "$HEAD:refs/tags/$TAG"
    echo "Taggen $TAG flyttad till $HEAD"
fi

command -v gh >/dev/null 2>&1 || fail 'gh saknas i PATH; release kunde inte uppdateras.'
if [ -n "$NOTES_FILE" ]; then
    [ -f "$NOTES_FILE" ] || fail "Anteckningsfilen hittas inte: $NOTES_FILE"
    gh release edit "$TAG" --latest --notes-file "$NOTES_FILE"
else
    gh release edit "$TAG" --latest
fi

echo 'Klart. GitHub-releasen är nu uppdaterad.'
