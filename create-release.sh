#!/bin/bash
# Creates new package release in git.
# a skip-merge is about not merge master to release.

set -e
set -o pipefail

fail() {
    echo "Error: $*" 1>&2
    exit 1
}

current_branch=$(git rev-parse --abbrev-ref HEAD)
current_remote=$(git config --get remote.origin.url)

if [[ "$current_branch" != "release" ]]; then
    echo 'Current remote is ' $current_remote
    echo 'Current branch is ' $current_branch
    echo 'Do you want to checkout release? y/n'
    read -r check_release
    if [[ "$check_release" == "y" ]]; then
        git checkout release
    else
        echo "Please checkout to release branch first, then do other operations"
        exit 0
    fi
fi

echo 'Do you want to merge master to release? y/n'
read -r skip_merge

if [[ "$skip_merge" == "n" ]]; then
    echo 'Skip merge master to release'
else
    git merge master
fi

if ! git diff --quiet; then
    fail 'Make sure you have no uncommitted changes in your repository.'
fi

echo "Current git commit is: $(git describe)"

echo 'Enter new version (e.g. "1.8.0"): ' version
read -r version
if [[ ! "$version" =~ ^[1-9][0-9]*\.[0-9]+\.[0-9]+$ ]]; then
    fail 'Unexpected version format.'
fi

echo 'Enter new release number: '
read -r release
if [[ ! "$release" =~ ^[1-9][0-9]*$ ]]; then
    fail 'Unexpected release format.'
fi

sed -i 's/\(^Version:\s*\).*/\1'"$version"'/' pdc-client.spec
sed -i 's/\(^Release:\s*\).*/\1'"$release"'%{?dist}/' pdc-client.spec
sed -i 's/\(^__version__=\).*/\1'\'$version\''/' setup.py

tito tag --keep-version

echo Do a test build here

tito build --rpm --offline
