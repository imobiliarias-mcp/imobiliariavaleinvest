"""CLI tool to execute rental searches on Imobiliária Vale Invest."""

import argparse
import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.domain.criteria import RentalFilter
from scripts.domain.value_objects import ListingPrice
from scripts.providers.vale_invest import ValeInvestRentalProvider


def build_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(description="Search rental properties on Imobiliária Vale Invest.")
    parser.add_argument("--city", type=str, default="", help="City name (e.g. Timóteo, Coronel Fabriciano)")
    parser.add_argument("--neighborhood", type=str, default="", help="Neighborhood name")
    parser.add_argument("--bedrooms", type=int, default=0, help="Minimum number of bedrooms")
    parser.add_argument("--type", type=str, default="", help="Property type (e.g. apartamento, ponto, casa)")
    parser.add_argument("--max-price", type=float, default=0.0, help="Maximum rental price in BRL")
    parser.add_argument("--min-price", type=float, default=0.0, help="Minimum rental price in BRL")
    parser.add_argument("--page", type=int, default=1, help="Page index (1-based)")
    parser.add_argument("--page-size", type=int, default=12, help="Quantity per page")
    parser.add_argument("--sort-field", type=str, default="valor", help="Sort field (valor, recentes)")
    parser.add_argument("--sort-direction", type=str, default="crescente", help="Direction (crescente, decrescente)")
    return parser


def create_search_filter(arguments: argparse.Namespace) -> RentalFilter:
    """Translate command line arguments to domain RentalFilter."""
    working_filter = (
        RentalFilter()
        .with_page(arguments.page)
        .with_page_size(arguments.page_size)
        .with_sorting(arguments.sort_field, arguments.sort_direction)
    )
    if arguments.city:
        working_filter = working_filter.with_city(arguments.city)
    if arguments.neighborhood:
        working_filter = working_filter.with_neighborhood(arguments.neighborhood)
    if arguments.bedrooms > 0:
        working_filter = working_filter.with_bedrooms(arguments.bedrooms)
    if arguments.type:
        working_filter = working_filter.with_property_type(arguments.type)
    if arguments.max_price > 0.0:
        ceiling = ListingPrice(arguments.max_price)
        working_filter = working_filter.with_price_ceiling(ceiling)
    if arguments.min_price > 0.0 and arguments.max_price > 0.0:
        working_filter = working_filter.with_price_range(arguments.min_price, arguments.max_price)
    return working_filter


def display_results(result) -> None:
    """Print search summary and items to console."""
    total = result.total_count()
    returned = result.returned_count()
    print(f"\nResultados: {returned} exibidos de {total} encontrados na Imobiliária Vale Invest\n")
    print("-" * 75)
    for listing in result.listings():
        summary_line = listing.format_summary()
        print(summary_line)
    print("-" * 75)


def main() -> None:
    """Main execution function."""
    argument_parser = build_argument_parser()
    parsed_arguments = argument_parser.parse_args()
    search_filter = create_search_filter(parsed_arguments)
    provider = ValeInvestRentalProvider.create_default()
    search_result = provider.search_rentals(search_filter)
    display_results(search_result)


if __name__ == "__main__":
    main()
