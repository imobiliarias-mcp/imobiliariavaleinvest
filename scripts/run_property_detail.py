"""CLI tool to retrieve and display property details on Imobiliária Vale Invest."""

import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.exceptions import RentalSearchException
from scripts.domain.value_objects import PropertyCode
from scripts.providers.vale_invest import ValeInvestRentalProvider


def parse_arguments() -> argparse.Namespace:
    """Parse property code from CLI arguments."""
    parser = argparse.ArgumentParser(description="View full rental property details by code or ID.")
    parser.add_argument("code", type=str, help="Property ID or reference code (e.g. 78933085 or PT00028)")
    return parser.parse_args()


def main() -> None:
    """Main execution function."""
    arguments = parse_arguments()
    code_value_object = PropertyCode(arguments.code)
    provider = ValeInvestRentalProvider.create_default()
    try:
        property_detail = provider.get_property_detail(code_value_object)
    except RentalSearchException as error:
        print(f"Erro ao buscar imóvel: {error}", file=sys.stderr)
        sys.exit(1)
    formatted_view = property_detail.format_detailed_view()
    listing_data = property_detail.to_dictionary()
    print("\n" + "=" * 70)
    print(formatted_view)
    print(f"Link: {listing_data['url']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
