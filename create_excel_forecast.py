#!/usr/bin/env python3
"""
Script to generate AI Data Center Investment Forecast Excel Report
Creates comprehensive comparison table from major institutions
"""

import pandas as pd
from datetime import datetime

def create_forecast_excel():
    """Create Excel file with AI data center investment forecasts"""

    # Main forecast comparison data
    forecast_data = [
        {
            'Institution': 'Goldman Sachs',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': '$405B',
            '2026 Forecast ($B)': '>$500B',
            '2027-2030 Cumulative ($B)': '$5,000B (through 2030)',
            'Key Investment Focus': 'Hyperscaler capex, power infrastructure, grid upgrades',
            'Primary Reasoning': 'AI workload explosion driving 165% power demand increase; grid capacity constraints; hyperscaler dominance',
            'Geographic Focus': 'United States (primary), Global',
            'Power/Infrastructure Investment': '$720B for grid through 2030',
            'Data Quality': 'High - Quarterly tracking, proprietary hyperscaler data'
        },
        {
            'Institution': 'Morgan Stanley',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': '$300-405B',
            '2026 Forecast ($B)': 'Not specified',
            '2027-2030 Cumulative ($B)': '$3,000-7,500B (potential)',
            'Key Investment Focus': 'Data center capex, semiconductors, grid, AI infrastructure',
            'Primary Reasoning': '$1.5T financing gap; power shortage of 45GW in US; alternative funding needed beyond corporate balance sheets',
            'Geographic Focus': 'United States (primary), Global',
            'Power/Infrastructure Investment': '65GW power demand (2025-2028)',
            'Data Quality': 'High - Infrastructure finance expertise, comprehensive analysis'
        },
        {
            'Institution': 'McKinsey',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': 'Not specified annually',
            '2026 Forecast ($B)': 'Not specified',
            '2027-2030 Cumulative ($B)': '$6,700B by 2030',
            'Key Investment Focus': '60% chips ($3.1T), 25% energy ($1.3T), 15% construction ($800B)',
            'Primary Reasoning': 'AI data center capacity growing from 44GW (2025) to 156GW (2030); 22% CAGR; fundamental cooling technology shift',
            'Geographic Focus': 'Global (US & China 80% of growth)',
            'Power/Infrastructure Investment': 'US power needs: 25GW→80+GW',
            'Data Quality': 'High - Comprehensive market modeling, detailed breakdowns'
        },
        {
            'Institution': 'IDC',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': '>$120B',
            '2026 Forecast ($B)': 'Not specified',
            '2027-2030 Cumulative ($B)': '$758B by 2029',
            'Key Investment Focus': 'AI compute and storage hardware infrastructure',
            'Primary Reasoning': '166% YoY growth in AI hardware spending (Q2 2025); cloud providers driving infrastructure expansion',
            'Geographic Focus': 'Global',
            'Power/Infrastructure Investment': 'Focus on hardware, not infrastructure',
            'Data Quality': 'Very High - Quarterly tracking, specific hardware focus'
        },
        {
            'Institution': 'Gartner',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': '$333-489B',
            '2026 Forecast ($B)': '>$2,000B (total AI)',
            '2027-2030 Cumulative ($B)': 'Server: $200B by 2028',
            'Key Investment Focus': 'Data center systems, GenAI, AI-optimized servers',
            'Primary Reasoning': '46.8% growth in data center systems; AI-optimized servers to triple traditional servers by 2027; GenAI spending growing 76.4%',
            'Geographic Focus': 'Global',
            'Power/Infrastructure Investment': 'Power demand: 448 TWh→980 TWh',
            'Data Quality': 'High - Broad IT market coverage, established methodology'
        },
        {
            'Institution': 'IEA',
            'Report Year': '2024-2025',
            '2024-2025 Annual ($B)': '$320B (tech companies)',
            '2026 Forecast ($B)': 'Not specified',
            '2027-2030 Cumulative ($B)': 'Not specified',
            'Key Investment Focus': 'Energy infrastructure, power generation, renewable integration',
            'Primary Reasoning': 'Data center electricity to double by 2030 (415→945 TWh); 15% annual growth; US & China drive 80% of energy demand growth',
            'Geographic Focus': 'Global (detailed regional breakdown)',
            'Power/Infrastructure Investment': 'Core focus: 450 TWh renewable, 175 TWh gas, 175 TWh nuclear',
            'Data Quality': 'High - Government data access, energy expertise'
        }
    ]

    # Detailed year-by-year projections where available
    yearly_projections = [
        {
            'Institution': 'Goldman Sachs',
            'Year': 2024,
            'Investment ($B)': 'Not specified',
            'Notes': 'Baseline year'
        },
        {
            'Institution': 'Goldman Sachs',
            'Year': 2025,
            'Investment ($B)': 405,
            'Notes': '70% YoY growth, hyperscaler capex'
        },
        {
            'Institution': 'Goldman Sachs',
            'Year': 2026,
            'Investment ($B)': 527,
            'Notes': 'Wall Street consensus estimate'
        },
        {
            'Institution': 'Goldman Sachs',
            'Year': 2027,
            'Investment ($B)': 'Not specified',
            'Notes': 'Part of $1.15T cumulative (2025-2027)'
        },
        {
            'Institution': 'Goldman Sachs',
            'Year': 2030,
            'Investment ($B)': 'Not specified',
            'Notes': '$5T total infrastructure through 2030'
        },
        {
            'Institution': 'Morgan Stanley',
            'Year': 2025,
            'Investment ($B)': '300-405',
            'Notes': 'Hyperscaler capex, revised upward'
        },
        {
            'Institution': 'Morgan Stanley',
            'Year': 2029,
            'Investment ($B)': 'Not specified',
            'Notes': '$3T cumulative through 2029'
        },
        {
            'Institution': 'Morgan Stanley',
            'Year': 2030,
            'Investment ($B)': 'Not specified',
            'Notes': 'Up to $7.5T funding capacity'
        },
        {
            'Institution': 'McKinsey',
            'Year': 2025,
            'Investment ($B)': 'Not specified',
            'Notes': '82 GW capacity (44 GW AI)'
        },
        {
            'Institution': 'McKinsey',
            'Year': 2030,
            'Investment ($B)': 6700,
            'Notes': '$6.7T cumulative; 219 GW capacity (156 GW AI)'
        },
        {
            'Institution': 'IDC',
            'Year': 2024,
            'Investment ($B)': 120,
            'Notes': 'AI compute/storage, doubled YoY'
        },
        {
            'Institution': 'IDC',
            'Year': 2025,
            'Investment ($B)': 'Q2: 82',
            'Notes': '166% YoY growth in Q2 alone'
        },
        {
            'Institution': 'IDC',
            'Year': 2028,
            'Investment ($B)': 200,
            'Notes': 'AI infrastructure spending'
        },
        {
            'Institution': 'IDC',
            'Year': 2029,
            'Investment ($B)': 758,
            'Notes': 'AI infrastructure market total'
        },
        {
            'Institution': 'Gartner',
            'Year': 2024,
            'Investment ($B)': 333.4,
            'Notes': 'Data center systems spending'
        },
        {
            'Institution': 'Gartner',
            'Year': 2025,
            'Investment ($B)': 489.5,
            'Notes': 'Data center systems (46.8% growth)'
        },
        {
            'Institution': 'Gartner',
            'Year': 2026,
            'Investment ($B)': 2000,
            'Notes': 'Total AI spending (broader than infrastructure)'
        },
        {
            'Institution': 'Gartner',
            'Year': 2028,
            'Investment ($B)': 200,
            'Notes': 'Server spending specifically'
        },
        {
            'Institution': 'IEA',
            'Year': 2024,
            'Investment ($B)': 230,
            'Notes': 'Major tech companies (Meta, Amazon, Alphabet, Microsoft)'
        },
        {
            'Institution': 'IEA',
            'Year': 2025,
            'Investment ($B)': 320,
            'Notes': '39% growth from 2024'
        }
    ]

    # Investment breakdown by category (McKinsey model)
    category_breakdown = [
        {
            'Investment Category': 'Computing Hardware (Chips, Servers, GPUs)',
            'Percentage of Total': '60%',
            'Estimated Investment through 2030 ($B)': '$3,100B',
            'Key Components': 'AI accelerators, GPUs, TPUs, custom ASICs, HBM memory, networking',
            'Primary Vendors': 'NVIDIA, AMD, Intel, Google, AWS, Microsoft',
            'Growth Drivers': 'AI model training, inference scaling, higher compute density'
        },
        {
            'Investment Category': 'Energy & Cooling Infrastructure',
            'Percentage of Total': '25%',
            'Estimated Investment through 2030 ($B)': '$1,300B',
            'Key Components': 'Power generation, transmission, cooling systems, electrical equipment',
            'Primary Vendors': 'Vertiv, Schneider Electric, Eaton, utility companies',
            'Growth Drivers': 'Power density increases, grid expansion, liquid cooling adoption'
        },
        {
            'Investment Category': 'Facilities & Construction',
            'Percentage of Total': '15%',
            'Estimated Investment through 2030 ($B)': '$800B',
            'Key Components': 'Land acquisition, building construction, site development, security',
            'Primary Vendors': 'Data center developers, construction firms, real estate',
            'Growth Drivers': 'Capacity expansion, geographic diversification, edge computing'
        }
    ]

    # Key assumptions and drivers
    drivers_risks = [
        {
            'Factor Type': 'Driver',
            'Factor': 'AI/ML Workload Growth',
            'Impact Level': 'Very High',
            'Timeline': '2024-2030',
            'Description': 'Exponential growth in generative AI, LLM training, and inference workloads',
            'Institutional Consensus': 'All institutions agree - primary driver'
        },
        {
            'Factor Type': 'Driver',
            'Factor': 'Hyperscaler Expansion',
            'Impact Level': 'Very High',
            'Timeline': '2024-2030',
            'Description': 'AWS, Azure, GCP, Meta investing $300-500B+ annually',
            'Institutional Consensus': 'Goldman Sachs, Morgan Stanley, Gartner emphasize'
        },
        {
            'Factor Type': 'Driver',
            'Factor': 'Compute Density Increases',
            'Impact Level': 'High',
            'Timeline': '2024-2028',
            'Description': 'Next-gen GPUs and AI accelerators requiring more power per rack',
            'Institutional Consensus': 'McKinsey, Gartner, IDC highlight'
        },
        {
            'Factor Type': 'Constraint',
            'Factor': 'Power Availability',
            'Impact Level': 'Very High',
            'Timeline': '2025-2030',
            'Description': 'Grid capacity insufficient; 5-10 year lead times for new generation',
            'Institutional Consensus': 'All institutions flag as critical constraint'
        },
        {
            'Factor Type': 'Constraint',
            'Factor': 'Cooling Technology',
            'Impact Level': 'High',
            'Timeline': '2024-2027',
            'Description': 'Traditional air cooling inadequate; shift to liquid/immersion cooling',
            'Institutional Consensus': 'McKinsey, Gartner emphasize'
        },
        {
            'Factor Type': 'Risk',
            'Factor': 'Financing Gap',
            'Impact Level': 'High',
            'Timeline': '2025-2028',
            'Description': '$1.5T gap requiring alternative funding beyond corporate balance sheets',
            'Institutional Consensus': 'Morgan Stanley quantifies; others imply'
        },
        {
            'Factor Type': 'Risk',
            'Factor': 'Utilization Uncertainty',
            'Impact Level': 'Medium',
            'Timeline': '2026-2030',
            'Description': 'AI demand may not match infrastructure supply, ROI concerns',
            'Institutional Consensus': 'Goldman Sachs warns; Morgan Stanley notes'
        },
        {
            'Factor Type': 'Risk',
            'Factor': 'Supply Chain Bottlenecks',
            'Impact Level': 'Medium',
            'Timeline': '2024-2026',
            'Description': 'Semiconductor capacity, cooling equipment, electrical infrastructure',
            'Institutional Consensus': 'IDC, Gartner mention'
        },
        {
            'Factor Type': 'Risk',
            'Factor': 'Regulatory Constraints',
            'Impact Level': 'Medium',
            'Timeline': '2025-2030',
            'Description': 'Environmental regulations, permitting delays, carbon targets',
            'Institutional Consensus': 'IEA emphasizes; Morgan Stanley notes'
        }
    ]

    # Regional investment distribution
    regional_data = [
        {
            'Region': 'United States',
            'Share of Global Growth': '40-45%',
            'Power Demand Growth (GW)': '25→80+ by 2030',
            'Energy Growth (TWh)': '+240 (130% increase)',
            'Key Markets': 'Virginia, Texas, Ohio, Oregon',
            'Primary Drivers': 'Hyperscaler HQs, cloud market maturity',
            'Constraints': 'Grid capacity, permitting delays'
        },
        {
            'Region': 'China',
            'Share of Global Growth': '35-40%',
            'Power Demand Growth (GW)': 'Rapid acceleration',
            'Energy Growth (TWh)': '+175 (170% increase)',
            'Key Markets': 'Beijing, Shanghai, Shenzhen',
            'Primary Drivers': 'Government AI strategy, domestic chip push',
            'Constraints': 'Energy independence, technology access'
        },
        {
            'Region': 'Europe',
            'Share of Global Growth': '10-15%',
            'Power Demand Growth (GW)': 'Moderate growth',
            'Energy Growth (TWh)': '+45 (70% increase)',
            'Key Markets': 'Ireland, Netherlands, Germany, Nordics',
            'Primary Drivers': 'Data sovereignty, renewable energy',
            'Constraints': 'High energy costs, strict regulations'
        },
        {
            'Region': 'Asia-Pacific (ex-China)',
            'Share of Global Growth': '5-10%',
            'Power Demand Growth (GW)': 'Selective growth',
            'Energy Growth (TWh)': 'Limited data',
            'Key Markets': 'Singapore, India, Japan',
            'Primary Drivers': 'Regional cloud markets, AI adoption',
            'Constraints': 'Power infrastructure, land availability'
        },
        {
            'Region': 'Middle East',
            'Share of Global Growth': '2-5%',
            'Power Demand Growth (GW)': 'Emerging',
            'Energy Growth (TWh)': 'Limited data',
            'Key Markets': 'UAE, Saudi Arabia',
            'Primary Drivers': 'Sovereign AI investments, energy abundance',
            'Constraints': 'Cooling (heat), talent availability'
        }
    ]

    # Create Excel writer
    timestamp = datetime.now().strftime('%Y%m%d')
    filename = '/home/user/test-repo/ai_investment_forecasts.xlsx'

    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        # Sheet 1: Main Forecast Comparison
        df_main = pd.DataFrame(forecast_data)
        df_main.to_excel(writer, sheet_name='Forecast Comparison', index=False)

        # Sheet 2: Yearly Projections
        df_yearly = pd.DataFrame(yearly_projections)
        df_yearly.to_excel(writer, sheet_name='Year-by-Year Projections', index=False)

        # Sheet 3: Investment Category Breakdown
        df_categories = pd.DataFrame(category_breakdown)
        df_categories.to_excel(writer, sheet_name='Investment Categories', index=False)

        # Sheet 4: Drivers and Risks
        df_drivers = pd.DataFrame(drivers_risks)
        df_drivers.to_excel(writer, sheet_name='Drivers and Risks', index=False)

        # Sheet 5: Regional Distribution
        df_regional = pd.DataFrame(regional_data)
        df_regional.to_excel(writer, sheet_name='Regional Distribution', index=False)

        # Format all sheets
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 80)
                worksheet.column_dimensions[column_letter].width = adjusted_width

            # Bold header row
            for cell in worksheet[1]:
                cell.font = cell.font.copy(bold=True)

    print(f"✓ Excel file created successfully: {filename}")
    print(f"\nSheets included:")
    print("  1. Forecast Comparison - Main institutional forecasts")
    print("  2. Year-by-Year Projections - Annual investment estimates")
    print("  3. Investment Categories - Spending breakdown (chips, energy, construction)")
    print("  4. Drivers and Risks - Key factors affecting investments")
    print("  5. Regional Distribution - Geographic investment patterns")

if __name__ == '__main__':
    create_forecast_excel()
