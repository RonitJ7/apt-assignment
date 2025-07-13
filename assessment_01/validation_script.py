import pandas as pd
import json
import sys
from typing import Dict, Any


def load_mapping(mapping_file: str) -> Dict[str, Any]:
    try:
        with open(mapping_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {mapping_file} not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {mapping_file}")
        sys.exit(1)


def validate_mapping_structure(mapping: Dict[str, Any]) -> bool:
    required_fields = {"open", "high", "low", "close", "volume"}

    mapped_fields = set()
    for orig_col, info in mapping.items():
        if isinstance(info, dict) and "mapping" in info:
            mapped_fields.add(info["mapping"])
        else:
            print(f"Warning: Invalid structure for {orig_col}")
            return False

    missing_fields = required_fields - mapped_fields
    if missing_fields:
        print(f"Error: Missing required fields: {missing_fields}")
        return False

    extra_fields = mapped_fields - required_fields - {"price"}  # price is optional
    if extra_fields:
        print(f"Warning: Unexpected fields: {extra_fields}")

    return True


def validate_data_integrity(df: pd.DataFrame, mapping: Dict[str, Any]) -> bool:
    """OHLC rules."""
    # Create reverse mapping
    reverse_mapping = {}
    for orig_col, info in mapping.items():
        if isinstance(info, dict) and "mapping" in info:
            reverse_mapping[info["mapping"]] = orig_col

    if not all(field in reverse_mapping for field in ["open", "high", "low", "close"]):
        print("Error: Cannot validate OHLC - missing required fields")
        return False

    high_col = reverse_mapping["high"]
    low_col = reverse_mapping["low"]
    open_col = reverse_mapping["open"]
    close_col = reverse_mapping["close"]

    violations = []

    # Check High >= Low
    high_low_violations = (df[high_col] < df[low_col]).sum()
    if high_low_violations > 0:
        violations.append(f"High < Low: {high_low_violations} violations")

    # Check High >= Open
    high_open_violations = (df[high_col] < df[open_col]).sum()
    if high_open_violations > 0:
        violations.append(f"High < Open: {high_open_violations} violations")

    # Check High >= Close
    high_close_violations = (df[high_col] < df[close_col]).sum()
    if high_close_violations > 0:
        violations.append(f"High < Close: {high_close_violations} violations")

    # Check Low <= Open
    low_open_violations = (df[low_col] > df[open_col]).sum()
    if low_open_violations > 0:
        violations.append(f"Low > Open: {low_open_violations} violations")

    # Check Low <= Close
    low_close_violations = (df[low_col] > df[close_col]).sum()
    if low_close_violations > 0:
        violations.append(f"Low > Close: {low_close_violations} violations")

    # Check volume magnitude
    volume_col = reverse_mapping.get("volume")
    if volume_col:
        vol_mean = df[volume_col].abs().mean()
        price_cols = [high_col, low_col, open_col, close_col]
        price_means = [df[col].abs().mean() for col in price_cols]
        max_price_mean = max(price_means)

        if vol_mean <= max_price_mean:
            violations.append(
                f"Volume magnitude sus low: {vol_mean:.2f} vs max price {max_price_mean:.2f}"
            )

    if violations:
        print("Data integrity violations found:")
        for violation in violations:
            print(f"  - {violation}")
        return False
    else:
        print(" All data integrity checks passed!")
        return True


def main():
    if len(sys.argv) != 3:
        print("Usage: python validate_mapping.py <data.csv> <mapping.json>")
        sys.exit(1)

    data_file = sys.argv[1]
    mapping_file = sys.argv[2]

    df = pd.read_csv(data_file)
    # print(f"Loaded data: {df.shape[0]} rows, {df.shape[1]} columns")

    # mapping
    mapping = load_mapping(mapping_file)
    print(f"Loaded mapping with {len(mapping)} field mappings")

    # Validate mapping
    structure_valid = validate_mapping_structure(mapping)

    if not structure_valid:
        print("Mapping structure validation failed!")
        sys.exit(1)

    print("####### Mapping structure is valid")

    data_valid = validate_data_integrity(df, mapping)

    if structure_valid and data_valid:
        print("\n ###### All validations passed! Mapping seems correct.")
        sys.exit(0)
    else:
        print("\n ###### Validation failed. Please review your mapping.")
        sys.exit(1)


if __name__ == "__main__":
    main()
