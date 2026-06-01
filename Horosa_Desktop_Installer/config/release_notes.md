Release notes are now generated inline by `scripts/publish_github_release.sh`.

Current policy:

- no versioned release-note files are stored in the repository
- GitHub Release body is assembled from the current version, asset names, and a bilingual template
- if the wording needs to change, edit the embedded release-body template in `scripts/publish_github_release.sh`
