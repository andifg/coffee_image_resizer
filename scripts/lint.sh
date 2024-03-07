#!/usr/bin/env bash
GIT_ROOT=$(git rev-parse --show-toplevel)

set -e

pushd "${GIT_ROOT}" > /dev/null


printf "Lint code with mypy \n" && \
mypy resize tests --disallow-untyped-defs && \
printf "Lint production code with pylint \n" && \
pylint resize &&\
printf "Lint test code with pylint \n" && \
pylint tests



SUCCESS=$?

popd > /dev/null

exit $SUCCESS