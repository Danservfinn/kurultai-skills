#!/usr/bin/env python3
"""
Market Sizing Calculator
Computes TAM, SAM, SOM for startup market analysis

TAM = Total Addressable Market
SAM = Serviceable Addressable Market
SOM = Serviceable Obtainable Market
"""

import argparse
import json
from typing import Dict, Any


def format_currency(value: float) -> str:
    """Format large numbers with appropriate suffixes"""
    if value >= 1e12:
        return f"${value/1e12:.2f}T"
    elif value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    else:
        return f"${value:,.0f}"


def calculate_market_sizing(
    total_market_population: float,
    target_customer_percent: float,
    addressable_customer_percent: float,
    obtainable_customer_percent: float,
    annual_spend_per_customer: float
) -> Dict[str, Any]:
    """
    Calculate TAM, SAM, SOM using bottom-up approach

    Args:
        total_market_population: Total potential customers globally
        target_customer_percent: % of total market that matches your target segment (0-100)
        addressable_customer_percent: % of target segment within your geographic/service reach (0-100)
        obtainable_customer_percent: % of addressable market realistically capturable (0-100)
        annual_spend_per_customer: Average annual revenue per customer
    """

    tam_customers = total_market_population * (target_customer_percent / 100)
    tam_revenue = tam_customers * annual_spend_per_customer

    sam_customers = tam_customers * (addressable_customer_percent / 100)
    sam_revenue = sam_customers * annual_spend_per_customer

    som_customers = sam_customers * (obtainable_customer_percent / 100)
    som_revenue = sam_customers * annual_spend_per_customer

    return {
        "tam": {
            "customers": tam_customers,
            "revenue": tam_revenue,
            "description": "Total market demand for a product or service"
        },
        "sam": {
            "customers": sam_customers,
            "revenue": sam_revenue,
            "description": "Segment of the TAM targeted by your products and services within your geographical reach"
        },
        "som": {
            "customers": som_customers,
            "revenue": som_revenue,
            "description": "Portion of SAM that you can capture in the near term"
        },
        "assumptions": {
            "total_market_population": total_market_population,
            "target_segment_percent": target_customer_percent,
            "addressable_percent": addressable_customer_percent,
            "obtainable_percent": obtainable_customer_percent,
            "annual_spend_per_customer": annual_spend_per_customer
        }
    }


def print_market_sizing_report(result: Dict[str, Any]):
    """Pretty print the market sizing analysis"""

    print("\n" + "="*60)
    print("MARKET SIZING ANALYSIS")
    print("="*60)

    print(f"\n📊 TOTAL ADDRESSABLE MARKET (TAM)")
    print(f"   {result['tam']['description']}")
    print(f"   Customers: {result['tam']['customers']:,.0f}")
    print(f"   Revenue:   {format_currency(result['tam']['revenue'])}")

    print(f"\n🎯 SERVICEABLE ADDRESSABLE MARKET (SAM)")
    print(f"   {result['sam']['description']}")
    print(f"   Customers: {result['sam']['customers']:,.0f}")
    print(f"   Revenue:   {format_currency(result['sam']['revenue'])}")

    print(f"\n✅ SERVICEABLE OBTAINABLE MARKET (SOM)")
    print(f"   {result['som']['description']}")
    print(f"   Customers: {result['som']['customers']:,.0f}")
    print(f"   Revenue:   {format_currency(result['som']['revenue'])}")

    print(f"\n📐 ASSUMPTIONS")
    print(f"   Total market population:       {result['assumptions']['total_market_population']:,.0f}")
    print(f"   Target segment %:              {result['assumptions']['target_segment_percent']:.1f}%")
    print(f"   Addressable % (geography):     {result['assumptions']['addressable_percent']:.1f}%")
    print(f"   Obtainable % (realistic):      {result['assumptions']['obtainable_percent']:.1f}%")
    print(f"   Annual spend per customer:     {format_currency(result['assumptions']['annual_spend_per_customer'])}")

    # Calculate funnel percentages
    tam_to_sam = (result['sam']['revenue'] / result['tam']['revenue']) * 100
    sam_to_som = (result['som']['revenue'] / result['sam']['revenue']) * 100
    tam_to_som = (result['som']['revenue'] / result['tam']['revenue']) * 100

    print(f"\n📈 FUNNEL ANALYSIS")
    print(f"   TAM → SAM:  {tam_to_sam:.1f}% of total market")
    print(f"   SAM → SOM:  {sam_to_som:.1f}% of addressable market")
    print(f"   TAM → SOM:  {tam_to_som:.1f}% of total market")

    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Calculate market size (TAM/SAM/SOM)')
    parser.add_argument('--population', type=float, required=True,
                        help='Total market population (e.g., 1000000)')
    parser.add_argument('--target-percent', type=float, required=True,
                        help='Target customer segment %% (0-100)')
    parser.add_argument('--addressable-percent', type=float, required=True,
                        help='Addressable market %% within geography (0-100)')
    parser.add_argument('--obtainable-percent', type=float, required=True,
                        help='Obtainable market %% realistically capturable (0-100)')
    parser.add_argument('--annual-spend', type=float, required=True,
                        help='Annual spend per customer (e.g., 100)')
    parser.add_argument('--json', action='store_true',
                        help='Output as JSON')

    args = parser.parse_args()

    result = calculate_market_sizing(
        total_market_population=args.population,
        target_customer_percent=args.target_percent,
        addressable_customer_percent=args.addressable_percent,
        obtainable_customer_percent=args.obtainable_percent,
        annual_spend_per_customer=args.annual_spend
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_market_sizing_report(result)


if __name__ == "__main__":
    main()
