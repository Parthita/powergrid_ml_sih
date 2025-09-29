import pandas as pd

def apply_feature_engineering(df):
    """
    Apply feature engineering to the input DataFrame.
    - One-hot encode categorical features
    - Create domain signals (estimate deltas)
    """
    # Define categorical features 
    # Added 'State' to handle potential location data like 'Maharashtra'
    categorical_features = ['ProjectType', 'Terrain', 'WeatherImpact', 'DemandSupply', 'State', 'Vendor', 'Type_x_Terrain', 'Season', 'Season_x_Terrain']

    # Estimate deltas as features when estimated and raw exist
    if 'EstimatedCost' in df.columns and 'TotalCost' in df.columns:
        df['EstCost_to_TotalCost_Ratio'] = (df['EstimatedCost'] / df['TotalCost']).replace([float('inf'), -float('inf')], 0)
        df['EstCost_Delta'] = (df['TotalCost'] - df['EstimatedCost'])
    if 'EstimatedTimeline' in df.columns and 'Timeline' in df.columns:
        df['EstTimeline_to_Timeline_Ratio'] = (df['EstimatedTimeline'] / df['Timeline']).replace([float('inf'), -float('inf')], 0)
        df['EstTimeline_Delta'] = (df['Timeline'] - df['EstimatedTimeline'])

    # Numeric composites and non-linearities
    if 'MaterialAvailabilityIndex' in df.columns:
        df['MaterialShortage'] = 1.0 - df['MaterialAvailabilityIndex']
        df['MaterialShortage2'] = df['MaterialShortage'] ** 2
    if 'ResourceUtilization' in df.columns:
        df['UtilizationGap'] = 1.0 - df['ResourceUtilization']
        df['UtilizationGap2'] = df['UtilizationGap'] ** 2
    if 'VendorOnTimeRate' in df.columns:
        df['VendorDelayRisk'] = 1.0 - df['VendorOnTimeRate']
    if 'VendorAvgDelay' in df.columns and 'HindranceCounts' in df.columns:
        df['Delay_x_Hindrance'] = df['VendorAvgDelay'] * df['HindranceCounts']
    if 'PermitVariance' in df.columns and 'RegulatoryPermitDays' in df.columns:
        df['PermitVolatilityIndex'] = df['PermitVariance'] / (df['RegulatoryPermitDays'] + 1e-6)

    # Interaction features (coarse)
    if 'ProjectType' in df.columns and 'Terrain' in df.columns:
        df['Type_x_Terrain'] = df['ProjectType'].astype(str) + '|' + df['Terrain'].astype(str)
    if 'StartMonth' in df.columns and 'Terrain' in df.columns:
        df['Season'] = ((df['StartMonth'] % 12) // 3).map({0:'Q1',1:'Q2',2:'Q3',3:'Q4'})
        df['Season_x_Terrain'] = df['Season'].astype(str) + '|' + df['Terrain'].astype(str)

    # One-hot encode categorical features that exist in the dataframe
    df_encoded = pd.get_dummies(df, columns=[col for col in categorical_features if col in df.columns], dummy_na=True)

    return df_encoded

class FeatureEngineer:
    """
    A simple FeatureEngineer class.
    In a real-world scenario, this would be more complex,
    handling feature scaling, encoding, and more.
    """
    def __init__(self):
        pass

    def fit_transform(self, df):
        return apply_feature_engineering(df)

    def transform(self, df):
        return apply_feature_engineering(df)
