#!/bin/bash

die() {
  local _ret="${2:-1}"
  test "${_PRINT_HELP:-no}" = yes && print_help >&2
  echo "$1" >&2
  exit "${_ret}"
}

begins_with_short_option() {
  local first_option all_short_options='h'
  first_option="${1:0:1}"
  test "$all_short_options" = "${all_short_options/$first_option/}" && return 1 || return 0
}

# THE DEFAULTS INITIALIZATION - POSITIONALS
_positionals=()
# THE DEFAULTS INITIALIZATION - OPTIONALS

print_help() {
  printf '%s\n' "The general script's help msg"
  printf 'Usage: %s [-h|--help] <project>\n' "$0"
  printf '\t%s\n' "<project>: project to publish"
  printf '\t%s\n' "-h, --help: Prints help"
}

parse_commandline() {
  _positionals_count=0
  while test $# -gt 0; do
    _key="$1"
    case "$_key" in
    -h | --help)
      print_help
      exit 0
      ;;
    -h*)
      print_help
      exit 0
      ;;
    *)
      _last_positional="$1"
      _positionals+=("$_last_positional")
      _positionals_count=$((_positionals_count + 1))
      ;;
    esac
    shift
  done
}

handle_passed_args_count() {
  local _required_args_string="'project'"
  test "${_positionals_count}" -ge 1 || _PRINT_HELP=yes die "FATAL ERROR: Not enough positional arguments - we require exactly 1 (namely: $_required_args_string), but got only ${_positionals_count}." 1
  test "${_positionals_count}" -le 1 || _PRINT_HELP=yes die "FATAL ERROR: There were spurious positional arguments --- we expect exactly 1 (namely: $_required_args_string), but got ${_positionals_count} (the last one was: '${_last_positional}')." 1
}

assign_positional_args() {
  local _positional_name _shift_for=$1
  _positional_names="_arg_project "

  shift "$_shift_for"
  for _positional_name in ${_positional_names}; do
    test $# -gt 0 || break
    eval "$_positional_name=\${1}" || die "Error during argument parsing, possibly an Argbash bug." 1
    shift
  done
}

parse_commandline "$@"
# handle_passed_args_count
# assign_positional_args 1 "${_positionals[@]}"

trap 'catch $? $LINENO' ERR

catch() {
  echo "Error $1 occurred on line $2"
  exit 1
}

PROJECT=app
MAIN_PACKAGE=src

set -eux
python --version

source ./deployment/ci/py/scripts/common-init.sh

cp "$(pwd)/$PROJECT/app.yaml" "$(pwd)/$PROJECT/$MAIN_PACKAGE/"
python deployment/ci/py/ci_tools.py include-path-dependencies "$PROJECT/pyproject.toml"

[ -d "$(pwd)/${PROJECT}/alembic" ] && {
  tar czvf "$(pwd)/${PROJECT}/db-init.tar.gz" -C "$(pwd)/${PROJECT}" alembic alembic.ini --owner=0 --group=0
  mv "$(pwd)/${PROJECT}/db-init.tar.gz" "$(pwd)/$PROJECT/$MAIN_PACKAGE/"
}

bump_version() {
  poetry version prerelease
}

pushd $PROJECT

bump_version
NEW_VERSION=$(poetry version --short)

git checkout pyproject.toml
bump_version

git config user.name "${GITHUB_ACTOR}"
git config user.email "${GITHUB_ACTOR}@users.noreply.github.com"

git add pyproject.toml
git commit --allow-empty -m "[skip ci] === CI new version commit: ${PROJECT} ${NEW_VERSION} ==="

git push origin "${GITHUB_REF_NAME}"

git tag -a "${PROJECT}.${NEW_VERSION}" -m "${GITHUB_REF_NAME} - ${PROJECT} ${NEW_VERSION}"
git push origin --tags

echo "export PROJECT=${PROJECT}" > "publish.env"
echo "export PROJECT_VERSION=${NEW_VERSION}" >> "publish.env"

popd
