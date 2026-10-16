# Copilot instructions for netbox-ztp

## Project overview

This repository is a NetBox plugin for zero-touch provisioning. It is not a standalone app: the plugin is installed inside a NetBox environment and contributes models, views, navigation, jobs, and API endpoints.

The core architecture is split across a few areas:

- `netbox_ztp/models.py`: the database models (`SourceDevice`, `OnboardedDevice`, `SoftwareAssignment`, `ZTPLog`). These inherit from NetBox's `PrimaryModel` and follow NetBox conventions for object pages, permissions, and URLs.
- `netbox_ztp/views/*.py`: object list/detail/create/edit/delete views using NetBox's generic view classes and `register_model_view()`.
- `netbox_ztp/forms/` and `netbox_ztp/filters.py`: forms and filtersets for model CRUD and list filtering.
- `netbox_ztp/navigation.py`: plugin menu entries for the UI.
- `netbox_ztp/jobs/`: runtime automation hooks for ARP collection and onboarding logic; some pieces are still stubbed and are not full implementations yet.
- `netbox_ztp/api/`: REST API serializers, viewsets, and router definitions for plugin data.
- `netbox_ztp/migrations/`: Django migration history for the plugin schema. Do not hand-edit migration history; add new migrations if schema changes are required.

## Repo-specific build, lint, and validation commands

This repo is configured for Python tooling via `pyproject.toml`, but it does not define a dedicated project test script or full CI workflow in-repo.

Use these commands when validating changes locally:

```bash
# Syntax check for the plugin package
python3 -m compileall netbox_ztp

# Lint the plugin package
ruff check netbox_ztp

# Formatting check
ruff format --check netbox_ztp

# Build the package metadata/dist artifact (if build is installed)
python3 -m build
```

When the plugin is running inside a NetBox development environment, a single Django test can be executed with the NetBox test runner, for example:

```bash
python3 manage.py test netbox_ztp.tests.<ModuleName>.<TestCaseName>
```

There is no checked-in test suite in this repository itself, so syntax checking and linting are the main local validation signals unless NetBox is available in the surrounding environment.

## NetBox plugin conventions to follow

- Keep plugin models compatible with NetBox's `PrimaryModel` base class and its permissions/URL patterns.
- Use `get_absolute_url()` and `reverse('plugins:netbox_ztp:...')` for model URLs when a plugin page should resolve to a plugin object detail page.
- Prefer NetBox view registration patterns already used in the repo (`@register_model_view(...)`) instead of inventing custom URL declarations.
- Add or update plugin API serializers when a model must be used through NetBox's API or delete flows that trigger serializer resolution.
- Keep `__str__` methods simple, stable, and side-effect free; avoid expensive or recursive DB access during UI rendering.
- Keep plugin config in the plugin config object (`NetBoxZTPConfig` in `netbox_ztp/__init__.py`) and follow the default settings pattern already used by the project.
- When introducing schema changes, generate a Django migration instead of editing migration files by hand.

## Deployment and runtime context

The plugin is enabled in a NetBox instance using `PLUGINS` and `PLUGINS_CONFIG`, as described in `README.md`:

```python
PLUGINS = [
    "netbox_ztp",
]

PLUGINS_CONFIG = {
    "netbox_ztp": {
        "arp_scan_interval": 300,
        "default_ssh_username": "ztp",
        "default_ssh_password": "ZTPzerodayPassword",
    },
}
```

The plugin's runtime flow is described in the README and centers on:

1. scanning source-device ARP tables,
2. identifying unknown devices,
3. SSH onboarding with the configured default credentials,
4. reconciling known serial numbers and rendered config,
5. logging results and repeating on the configured interval.

## Existing repo conventions from the docs

- The plugin is organized around source-device monitoring and onboarding workflows, not general-purpose app logic.
- It is a plugin package under `netbox_ztp/` with NetBox integration points rather than a self-contained service.
- The README is the source of truth for the user-facing workflow, default credentials, and plugin setup steps.
- `pyproject.toml` defines Python packaging and Ruff config; follow those settings instead of introducing alternate tooling conventions.
