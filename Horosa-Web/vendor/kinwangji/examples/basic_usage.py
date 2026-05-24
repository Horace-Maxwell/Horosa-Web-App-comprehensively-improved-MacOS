"""Basic usage example for the kinwangji package."""

from kinwangji import wanji_four_gua, display_pan, jq

# Example: Get Huangji position for a specific date and time
year, month, day, hour, minute = 2025, 6, 15, 10, 30

# Get the current solar term
solar_term = jq(year, month, day, hour, minute)
print(f"Solar term (節氣): {solar_term}")

# Get the four-gua configuration
result = wanji_four_gua(year, month, day, hour, minute)
for key, value in result.items():
    print(f"  {key}: {value}")

# Display the full pan (chart)
print("\n" + "=" * 60)
print(display_pan(year, month, day, hour, minute))
