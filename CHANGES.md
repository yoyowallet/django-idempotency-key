# Changes Log

This file lists the changes made to the Django idempotency key package.

## Tags
Tags may be specified for each release as an indicator for the changes that were made
for the reader can see at a glance.

**[Security updates]** - Some dependant packages required security updates and required
updating.

**[Dropped support]** - Support for required package version(s) have been dropped.

**[Added support]** - Support for required package versions(s) have been added.

**[Bug fixes]** - Some bugs have been fixed in this release.

**[New features]** - There are new features in this release.

**[Breaking changes]** - There are changes that break existing compatibility.

---
# 1.2.0
  **[Dropped support]**

  **[Added support]**

- Dropped support for Python 3.6
- Added support for Django 3.2 and 4.0
- Added support for Python 3.7 to 3.10
- Moved to poetry for package management
- Added pre-commit triggers

---
# 1.1.1
- Fixed a problem with packaging on release where the new locks folder was missing.

---
# 1.1.0
  **[Security updates]**

  **[Dropped support]**

  **[Added support]**

  **[New features]**

  **[Breaking changes]**

- The following classes have moved to a new namespace and need to be changed in your
settings and code where appropriate.
<pre>
  idempotency_key.locks.IdempotencyKeyLock    -> <strong>idempotency_key.locks.basic.IdempotencyKeyLock</strong>

  idempotency_key.locks.ThreadLock            -> <strong>idempotency_key.locks.basic.ThreadLock</strong>

  idempotency_key.locks.MultiProcessRedisLock -> <strong>idempotency_key.locks.redis.MultiProcessRedisLock</strong>
</pre>

- Drop support for Django (1.9, 1.10, 1.11)
  - 1.11 was dropped because of security issues and is near to end of life support.

- Added support for Django (2.2)

- Added testing with django rest framework (3.10, 3.11)

- Added optional flag so that clients can choose to use idempotency keys on an API that
  is used to expect it.

- Updated packages with security issues:
  Django (>=2.x)
  bleach (>=3.1.4)
  urllib3 (>=1.24.2)

---
# 1.0.3

- Initial release (as an Alpha)
