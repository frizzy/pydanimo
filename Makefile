SHELL := /bin/bash

tag:
	@git diff-index --quiet HEAD -- || (printf "\n\nUncommited changes. Please commit or stash changes before release.\n\n\n"; exit 1)
	@git diff-index --quiet origin/`git branch | grep \* | cut -d ' ' -f2` -- || (printf "\n\nCommits not push. Please push commits to include them in release.\n\n\n"; exit 1)

	@IFS=. version=(`jq -r '.version' package.json`) && \
	version_major=$${version[0]} && \
	version_minor=$${version[1]} && \
	version_patch=$${version[2]} && \
	current_version="$${version_major}.$${version_minor}.$${version_patch}" && \
	echo "Current version: $${current_version}" && \
	version_$l=$$(($$version_$l+1)) && \
	if [[ "${l}" == "major" ]]; then \
		version_minor=0 && \
		version_patch=0; \
	fi && \
	if [[ "${l}" == "minor" ]]; then \
		version_patch=0; \
	fi && \
	new_version="$${version_major}.$${version_minor}.$${version_patch}" && \
	echo "Updating version to: $${version_major}.$${version_minor}.$${version_patch}" && \
	sed -i.bak "s/\"version\": \"$${current_version}\"/\"version\": \"$${new_version}\"/g" package.json && \
	sed -i.bak "s/version=\"$${current_version}\",/version=\"$${new_version}\",/g" setup.py && \
	git add package.json && \
	git commit -m "[skip ci] Update version to $${new_version}" && \
	git push && \
	git tag "v$${new_version}" && \
	git push origin "v$${new_version}"