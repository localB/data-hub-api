from unittest import mock

import pytest

from datahub.core.constants import (
    InvestmentBusinessActivity as InvestmentBusinessActivityConstant,
    InvestmentType as InvestmentTypeConstant,
    Sector as SectorConstant,
)
from datahub.investment.project.gva_utils import get_gross_value_added_message
from datahub.investment.project.test.factories import (
    GVAMultiplierFactory,
    InvestmentProjectFactory,
)
from datahub.metadata.test.factories import SectorFactory


pytestmark = pytest.mark.django_db


class TestGrossValueAddedCalculator:
    """Test for Gross Value Added Calculator."""

    @pytest.mark.parametrize(
        'investment_type,sector,business_activities,multiplier_value',
        (
            (
                InvestmentTypeConstant.fdi.value.id,
                None,
                [],
                None,
            ),
            (
                InvestmentTypeConstant.fdi.value.id,
                None,
                [
                    InvestmentBusinessActivityConstant.retail.value.id,
                ],
                0.0581,
            ),
            (
                InvestmentTypeConstant.fdi.value.id,
                SectorConstant.renewable_energy_wind.value.id,
                [InvestmentBusinessActivityConstant.retail.value.id],
                0.0581,
            ),
            (
                InvestmentTypeConstant.fdi.value.id,
                SectorConstant.renewable_energy_wind.value.id,
                [],
                0.0325,
            ),
            (
                InvestmentTypeConstant.fdi.value.id,
                SectorConstant.aerospace_assembly_aircraft.value.id,
                [],
                0.0621,
            ),
            (
                InvestmentTypeConstant.fdi.value.id,
                SectorConstant.renewable_energy_wind.value.id,
                [
                    InvestmentBusinessActivityConstant.retail.value.id,
                    InvestmentBusinessActivityConstant.other.value.id,
                ],
                0.0581,
            ),
            (
                InvestmentTypeConstant.commitment_to_invest.value.id,
                SectorConstant.renewable_energy_wind.value.id,
                [],
                None,
            ),
            (
                InvestmentTypeConstant.non_fdi.value.id,
                None,
                [
                    InvestmentBusinessActivityConstant.retail.value.id,
                ],
                None,
            ),
        ),
    )
    def test_set_gva_multiplier(
        self,
        investment_type,
        sector,
        business_activities,
        multiplier_value,
    ):
        """Test the GVA Multiplier correctly gets set on an investment project."""
        project = InvestmentProjectFactory(
            sector_id=sector,
            business_activities=business_activities,
            investment_type_id=investment_type,
        )
        if not multiplier_value:
            assert project.gva_multiplier is None
        else:
            assert project.gva_multiplier.multiplier == multiplier_value

    def test_no_investment_sector_linking_sector_to_fdi_sic_grouping_returns_none(self):
        """
        Tests that when there is no link between a dit sector and an
        fdi sic grouping None is returned.
        """
        new_sector = SectorFactory(parent=None)
        project = InvestmentProjectFactory(
            sector_id=new_sector.id,
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            business_activities=[],
        )
        assert project.gva_multiplier is None

    def test_no_gva_multiplier_for_financial_year(self):
        """Test when a GVA Multiplier is not present for a financial year."""
        with mock.patch(
            'datahub.investment.project.gva_utils.'
            'GrossValueAddedCalculator._get_gva_multiplier_financial_year',
        ) as mock_get_financial_year:
            mock_get_financial_year.return_value = 1980
            project = InvestmentProjectFactory(
                sector_id=SectorConstant.renewable_energy_wind.value.id,
                business_activities=[],
                investment_type_id=InvestmentTypeConstant.fdi.value.id,
                foreign_equity_investment=1000,
            )
        assert project.gva_multiplier is None

    @pytest.mark.parametrize(
        'foreign_equity_investment,multiplier_value,expected_gross_value_added',
        (
            (1, 1, 1),
            (None, 1, None),
            (100000, 0.0581, 5810),
            (130000000, 0.4537, 58981000),
            (10000000, 0.0621, 621000),
            (111000, 0.0621, 6893),
            (12625500, 0.0581, 733542),
            (296000, 0.0581, 17198),
            (7002180, 0.0386, 270284),
            (287732, 0.3939, 113338),
            (1800000, 0.0264, 47520),
            (28000, 0.021, 588),
            (8907560, 0.9526, 8485342),
            (16717, 0.0853, 1426),
        ),
    )
    def test_calculate_gva(
        self,
        foreign_equity_investment,
        multiplier_value,
        expected_gross_value_added,
    ):
        """Test calculate GVA."""
        gva_multiplier = GVAMultiplierFactory(
            multiplier=multiplier_value,
            financial_year=1980,
        )

        with mock.patch(
            'datahub.investment.project.gva_utils.GrossValueAddedCalculator._get_gva_multiplier',
        ) as mock_get_multiplier:
            mock_get_multiplier.return_value = gva_multiplier
            project = InvestmentProjectFactory(
                foreign_equity_investment=foreign_equity_investment,
                investment_type_id=InvestmentTypeConstant.fdi.value.id,
                sector_id=SectorConstant.renewable_energy_wind.value.id,
            )

        assert project.gross_value_added == expected_gross_value_added


class TestGrossValueAddedMessage:
    """Tests for get Gross Value Added message."""

    def test_gross_value_added_message_for_none_fdi_project(self):
        """Test no message is returned for an FDI project."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.non_fdi.value.id,
        )
        assert not get_gross_value_added_message(project)

    def test_gross_value_added_message_when_gross_value_added_is_set(self):
        """Test no message is returned if the project has a GVA."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            foreign_equity_investment=1000,
            sector_id=SectorConstant.renewable_energy_wind.value.id,
        )
        project.gross_value_added = 100
        assert not get_gross_value_added_message(project)

    def test_gross_value_added_message_when_no_foreign_equity_investment(self):
        """Tests a message is returned when the project has no value for foreign equity."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            sector_id=SectorConstant.renewable_energy_wind.value.id,
        )
        assert (
            str(get_gross_value_added_message(project))
            == 'Add Foreign equity investment value and click "Save" to calculate GVA'
        )

    def test_gross_value_added_message_when_client_cannot_provide_foreign_investment(self):
        """Tests no message is returned when the client cannot provide foreign investment."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            sector_id=SectorConstant.renewable_energy_wind.value.id,
            client_cannot_provide_foreign_investment=True,
        )
        assert not get_gross_value_added_message(project)

    def test_gross_value_added_message_when_no_sector(self):
        """Tests a message is returned when there is no sector assigned."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            foreign_equity_investment=1000,
            sector_id=None,
            business_activities=[],
        )
        assert (
            str(get_gross_value_added_message(project))
            == 'Add Primary sector (investment project summary) to calculate GVA'
        )

    def test_gross_value_added_message_when_no_sector_and_no_foreign_equity_investment(self):
        """Tests a message is returned when there is no sector and no foreign equity investment."""
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            sector_id=None,
        )
        assert (
            str(get_gross_value_added_message(project))
            == (
                'Add Foreign equity investment value and Primary sector '
                '(investment project summary) to calculate GVA'
            )
        )

    def test_gross_value_added_message_when_gross_value_added_not_populated(self):
        """
        Tests no message is returned when all criteria has been meet
        but no gross value added value.
        """
        project = InvestmentProjectFactory(
            investment_type_id=InvestmentTypeConstant.fdi.value.id,
            foreign_equity_investment=1000,
            sector_id=SectorConstant.renewable_energy_wind.value.id,
            business_activities=[],
        )
        project.gross_value_added = None
        assert not get_gross_value_added_message(project)
