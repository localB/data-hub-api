from datahub.core.test_utils import AdminTestMixin


class TestLinkCompanyLink(AdminTestMixin):
    """
    Tests the 'Link Company with D&B' link on the change list.
    """

    def test_link_exists(self):
        """Test that the link exists for a user with the change company permission."""

    def test_link_does_not_exist_with_only_view_permission(self):
        """Test that the link does not exist for a user with only the view company permission."""


class TestSelectIDsViewGet(AdminTestMixin):
    """
    """


class TestSelectIDsViewPost(AdminTestMixin):
    """
    """
