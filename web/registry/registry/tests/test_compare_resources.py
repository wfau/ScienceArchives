from lxml import etree

from vo_registry.resources import ResourceRepo


class TestForDeletedRecords:
    def test_new_resources_dir_isnt_missing_old_resources(self):
        new_repo = ResourceRepo(path="new_resources")
        main_repo = ResourceRepo()
        new_ids = {resource.identifier for resource in new_repo.resources.values()}
        main_ids = {resource.identifier for resource in main_repo.resources.values()}
        diff = main_ids - new_ids
        assert len(diff) == 0, f"Identifiers removed! {diff}"

    def test_timestamp_updated_for_modified_resources(self):
        new_repo = ResourceRepo(path="new_resources")
        main_repo = ResourceRepo()
        main_ids = {resource.identifier for resource in main_repo.resources.values()}
        for main_id in main_ids:
            main_resource = etree.tostring(main_repo.get(main_id))
            new_resource = etree.tostring(new_repo.get(main_id))
            if main_resource != new_resource:
                main_updated = main_repo.resources[main_id].updated
                new_updated = new_repo.resources[main_id].updated
                assert new_updated > main_updated
