"""Deprecated command/API alias for Geo-Strategy and Mind-owned Notebook."""
import sys
import geo_strategy_acquisition as implementation

if __name__ == "__main__":
    implementation.main()
else:
    sys.modules[__name__] = implementation
