import pandas as pd
from finops_analysis_platform.data_loader import GCSDataLoader
from finops_analysis_platform.config_manager import ConfigManager

def analyze_recommendations():
    """
    Loads and analyzes the cost recommendations data to identify key savings opportunities.
    """
    print("🚀 Analyzing Cost Recommendations...")

    # Load configuration
    config_manager = ConfigManager(config_path='config.yaml')

    # Load data
    gcs_config = config_manager.get('gcs', {})
    loader = GCSDataLoader(bucket_name=gcs_config.get('bucket_name'))
    data = loader.load_all_data()

    if 'recommendations' not in data:
        print("⚠️ No recommendations data found.")
        return

    df = data['recommendations']
    print(f"✅ Loaded {len(df)} recommendations.")

    # Analyze the data
    if 'Monthly savings' not in df.columns or 'Type' not in df.columns or 'Impact' not in df.columns:
        print("⚠️ Recommendations data is missing required columns ('Monthly savings', 'Type', 'Impact').")
        return

    # Group by recommendation type and impact
    savings_summary = df.groupby(['Type', 'Impact'])['Monthly savings'].sum().unstack(fill_value=0)

    print("\n" + "="*60)
    print("💰 Cost Savings Opportunities Summary")
    print("="*60)
    print(savings_summary.to_string(float_format="%.2f"))

    total_savings = df['Monthly savings'].sum()
    print("\n" + "="*60)
    print(f"Total Potential Monthly Savings: ${total_savings:,.2f}")
    print("="*60)

if __name__ == '__main__':
    analyze_recommendations()
