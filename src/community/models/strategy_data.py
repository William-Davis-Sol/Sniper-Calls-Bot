

#  This file is part of SniperCallsBot (https://github.com/Drakkar-Software/SniperCallsBot)

#  Copyright (c) 2023 Drakkar-Software, All rights reserved.
#
#  SniperCallsBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  SniperCallsBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with SniperCallsBot. If not, see <https://www.gnu.org/licenses/>.
import dataclasses
import src.constants as constants
import src.community.identifiers_provider as identifiers_provider
import SniperCallsbot_commons.dataclasses as commons_dataclasses
import SniperCallsbot_commons.enums as commons_enums


CATEGORY_NAME_TRANSLATIONS_BY_SLUG = {
    "coingecko-index": {"en": "Crypto Basket"}
}
FORCED_URL_PATH_BY_SLUG = {
    "coingecko-index": "features/crypto-basket",
}
DEFAULT_LOGO_NAME_BY_SLUG = {
    "coingecko-index": "crypto-basket.png",
}
AUTO_UPDATED_CATEGORIES = ["coingecko-index"]
DEFAULT_LOGO_NAME = "default_strategy.png"
EXTENSION_CATEGORIES = ["coingecko-index"]


@dataclasses.dataclass
class CategoryData(commons_dataclasses.FlexibleDataclass):
    slug: str = ""
    name_translations: dict = dataclasses.field(default_factory=dict)
    type: str = ""
    metadata: dict = dataclasses.field(default_factory=dict)

    def get_url(self) -> str:
        if self.metadata:
            external_links = self.metadata.get("external_link")
            if external_links:
                if blog_slug := external_links.get("blog"):
                    return f"{identifiers_provider.IdentifiersProvider.COMMUNITY_LANDING_URL}/en/blog/{blog_slug}"
                if features_slug := external_links.get("features"):
                    return f"{identifiers_provider.IdentifiersProvider.COMMUNITY_LANDING_URL}/features/{features_slug}"
        return ""

    def get_default_logo_url(self) -> str:
        return DEFAULT_LOGO_NAME_BY_SLUG.get(self.slug, DEFAULT_LOGO_NAME)

    def get_name(self, locale, default_locale=constants.DEFAULT_LOCALE):
        return CATEGORY_NAME_TRANSLATIONS_BY_SLUG.get(self.slug, self.name_translations).get(locale, default_locale)

    def is_auto_updated(self) -> bool:
        return self.slug in AUTO_UPDATED_CATEGORIES

@dataclasses.dataclass
class ResultsData(commons_dataclasses.FlexibleDataclass):
    profitability: dict = dataclasses.field(default_factory=dict)
    reference_market_profitability: dict = dataclasses.field(default_factory=dict)

    def _get_max(self):
        if not self.reference_market_profitability:
            return 0, "1m"
        max_unit = next(iter(self.reference_market_profitability))
        max_value = self.reference_market_profitability[max_unit]
        for unit, value in self.reference_market_profitability.items():
            if value > max_value:
                max_unit = unit
                max_value = value
        return max_value, max_unit

    def get_max_value(self):
        return self._get_max()[0]

    def get_max_unit(self):
        return self._get_max()[1]


@dataclasses.dataclass
class StrategyData(commons_dataclasses.FlexibleDataclass):
    id: str = ""
    slug: str = ""
    author_id: str = ""
    content: dict = dataclasses.field(default_factory=dict)
    category: CategoryData = dataclasses.field(default_factory=CategoryData.from_dict)
    results: ResultsData = dataclasses.field(default_factory=ResultsData.from_dict)
    logo_url: str = ""
    attributes: dict = dataclasses.field(default_factory=dict)
    visibility: str = ""
    metadata: str = ""

    def get_name(self, locale, default_locale=constants.DEFAULT_LOCALE):
        return self.content["name_translations"].get(locale, default_locale)

    def get_url(self) -> str:
        if path := FORCED_URL_PATH_BY_SLUG.get(self.category.slug):
            return f"{identifiers_provider.IdentifiersProvider.COMMUNITY_LANDING_URL}/{path}"
        return f"{identifiers_provider.IdentifiersProvider.COMMUNITY_URL}/strategies/{self.slug}"

    def get_product_url(self) -> str:
        return f"{identifiers_provider.IdentifiersProvider.COMMUNITY_URL}/strategies/{self.slug}"

    def get_risk(self) -> commons_enums.ProfileRisk:
        risk = self.attributes['risk'].upper()
        try:
            # use [] to access by name
            # https://docs.python.org/3/howto/enum.html#programmatic-access-to-enumeration-members-and-their-attributes
            return commons_enums.ProfileRisk[risk]
        except KeyError:
            return commons_enums.ProfileRisk.MODERATE

    def get_logo_url(self, prefix: str) -> str:
        if self.logo_url:
            return self.logo_url
        return f"{prefix}{self.category.get_default_logo_url()}"

    def is_auto_updated(self) -> bool:
        return self.category.is_auto_updated()

    def is_extension_only(self) -> bool:
        return self.category.slug in EXTENSION_CATEGORIES
