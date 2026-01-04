#!/usr/bin/env python3
"""
Rebuild NVD Status Analysis

This script regenerates the NVD status analysis files without a full build.
Useful for quick updates to status tracking and growth tables.

Usage:
    python data/scripts/rebuild_nvd_status.py
    
Output files:
    - web/data/nvd_status_analysis.json
    - web/data/growth_table.json
    - web/data/cna_vulnerability_mapping.json
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).parent
data_dir = script_dir.parent
project_root = data_dir.parent

sys.path.insert(0, str(data_dir))
sys.path.insert(0, str(project_root))


def main():
    """Rebuild NVD status analysis files"""
    print("🔄 Rebuilding NVD Status Analysis")
    print("=" * 50)
    
    try:
        from nvd_status_analysis import NVDStatusAnalyzer
        
        # Set up paths
        cache_dir = data_dir / 'cache'
        output_dir = project_root / 'web' / 'data'
        
        # Check for NVD data
        nvd_file = cache_dir / 'nvd.json'
        if not nvd_file.exists():
            print(f"❌ NVD cache file not found: {nvd_file}")
            print("   Run a full build first to download the data.")
            return 1
        
        # Create analyzer and generate analysis
        analyzer = NVDStatusAnalyzer(
            base_dir=project_root,
            cache_dir=cache_dir,
            data_dir=output_dir,
            quiet=False
        )
        
        results = analyzer.generate_all()
        
        if results:
            print("\n" + "=" * 50)
            print("✅ NVD status analysis rebuilt successfully!")
            print(f"📁 Output directory: {output_dir}")
            for name, path in results.items():
                print(f"   📄 {path.name}")
            return 0
        else:
            print("❌ Failed to generate NVD status analysis")
            return 1
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the project root.")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

