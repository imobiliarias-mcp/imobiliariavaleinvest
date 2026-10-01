"""CLI tool to query and display search facets on Imobiliária Vale Invest."""

import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from scripts.providers.vale_invest import ValeInvestRentalProvider


def print_section(title: str, items: tuple[str, ...]) -> None:
    """Print an item collection section to stdout."""
    print(f"\n--- {title} ({len(items)}) ---")
    for item in items[:25]:
        print(f"  • {item}")
    if len(items) > 25:
        print(f"  ... e mais {len(items) - 25} itens")


def main() -> None:
    """Main execution function."""
    provider = ValeInvestRentalProvider.create_default()
    facets = provider.get_facets()
    cities = facets.city_names()
    neighborhoods = facets.neighborhood_names()
    types = facets.property_types()

    print("\n" + "=" * 65)
    print("Taxonomia e Localidades - Imobiliária Vale Invest")
    print("=" * 65)
    print_section("Cidades", cities)
    print_section("Tipos de Imóveis", types)
    print_section("Bairros", neighborhoods)
    print("\n" + "=" * 65 + "\n")


if __name__ == "__main__":
    main()
