# How to create a release
This document explains how to make a release of the idempotency library.

Run the following:

---
Run black and code analysis on the files to ensure everything is OK and no files have
changed.
- `make static-analysis`

---
Updated the version number for this release.

If this will ba a major release then run
- `make bump-major`

else if this is a minor release
- `make bump-minor`

else:
- `make bump-patch`

---
Now create the bundle zip package which will be placed in the `dist` folder
- `make bundle`

---
Test the release for potential errors
- `make release-test`

---
upload the release to pypi
- `make release`
