#!/bin/bash
set -x

update_catalog() {
    repo="https://github.com/notimetoidle/truenas-apps"
    branch="main"

    # https://github.com/truenas/middleware/blob/master/src/middlewared/middlewared/plugins/catalog/apps.py
    # https://github.com/truenas/middleware/blob/master/src/middlewared/middlewared/plugins/catalog/sync.py

    # These steps will not set CatalogService.SYNCED to true,
    # which is used by at least AppService.available (app.available).
    # When app.available is called the catalog gets overridden by the official one

    local_path=$(midclt call catalog.config | jq -rM .location)
    local_path="${local_path:-/mnt/.ix-apps/truenas_catalog}"
    midclt call catalog.update_git_repository "$local_path" "$repo" "$branch"
    midclt call catalog.get_feature_map false
    midclt call catalog.retrieve_recommended_apps false
    midclt call catalog.apps '{"cache": false, "cache_only": false, "retrieve_all_trains": true, "trains": []}' > /dev/null
    midclt call app.check_upgrade_alerts
}

update_catalog
