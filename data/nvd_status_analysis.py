#!/usr/bin/env python3
"""
NVD Status Analysis Module
Tracks NVD vulnerability status changes over time for operational insights.

Generates:
- Monthly status aggregation (Analyzed, Awaiting Analysis, Modified, etc.)
- Daily/Weekly status deltas
- Quarterly CVE breakdown
- Growth table with cumulative totals and projections

This module fulfills the NVD statistics requirements for tracking:
- Status distribution changes over time
- Quarterly aggregations with projections
- Year-over-year comparisons with delta calculations
"""

import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


class NVDStatusAnalyzer:
    """Analyzes NVD vulnerability status for operational tracking"""
    
    # Known NVD vulnerability status values
    VALID_STATUSES = [
        'Analyzed',
        'Awaiting Analysis', 
        'Modified',
        'Rejected',
        'Received',
        'Undergoing Analysis',
        'Deferred'
    ]
    
    def __init__(self, base_dir=None, cache_dir=None, data_dir=None, quiet=False):
        self.quiet = quiet
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.cache_dir = Path(cache_dir) if cache_dir else self.base_dir / 'data' / 'cache'
        self.data_dir = Path(data_dir) if data_dir else self.base_dir / 'web' / 'data'
        self.current_year = datetime.now().year
        self.current_date = datetime.now(timezone.utc)
        
        # Data storage
        self.nvd_data = None
        
    def load_nvd_data(self):
        """Load NVD data from cache"""
        nvd_file = self.cache_dir / 'nvd.json'
        
        if not nvd_file.exists():
            print(f"❌ NVD cache file not found: {nvd_file}")
            return None
        
        if not self.quiet:
            print(f"📂 Loading NVD data from {nvd_file}...")
        
        with open(nvd_file, 'r', encoding='utf-8') as f:
            self.nvd_data = json.load(f)
        
        if not self.quiet:
            print(f"✅ Loaded {len(self.nvd_data):,} CVE records")
        
        return self.nvd_data
    
    def parse_date(self, date_str):
        """Parse ISO date string to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None
    
    def get_quarter(self, month):
        """Get quarter number from month (1-4)"""
        return (month - 1) // 3 + 1
    
    def generate_monthly_status_analysis(self):
        """
        Generate monthly aggregation of CVE status distribution.
        
        Output format:
        {
            "2024-01": {
                "Analyzed": 1500,
                "Awaiting Analysis": 2971,
                "Modified": 2485,
                "Rejected": 672,
                "Received": 180,
                "Undergoing Analysis": 31
            },
            ...
        }
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return {}
        
        if not self.quiet:
            print("📊 Generating monthly status analysis...")
        
        # Monthly status counts by last modified date
        monthly_status = defaultdict(lambda: defaultdict(int))
        
        # Track CVEs by their current status and last modified month
        for cve_record in self.nvd_data:
            try:
                cve = cve_record.get('cve', {})
                cve_id = cve.get('id', '')
                
                if not cve_id.startswith('CVE-'):
                    continue
                
                # Get status
                status = cve.get('vulnStatus', 'Unknown')
                
                # Get last modified date for status tracking
                last_modified = cve.get('lastModified') or cve.get('published')
                mod_date = self.parse_date(last_modified)
                
                if mod_date:
                    month_key = mod_date.strftime('%Y-%m')
                    monthly_status[month_key][status] += 1
                    
            except Exception:
                continue
        
        # Convert to regular dict and sort by date
        result = {}
        for month in sorted(monthly_status.keys()):
            result[month] = dict(monthly_status[month])
        
        if not self.quiet:
            print(f"✅ Generated monthly status for {len(result)} months")
        
        return result
    
    def generate_current_status_snapshot(self):
        """
        Generate current snapshot of all CVE statuses.
        
        Output format:
        {
            "snapshot_date": "2024-01-15",
            "status_counts": {
                "Analyzed": 150000,
                "Awaiting Analysis": 2971,
                ...
            },
            "status_percentages": {...}
        }
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return {}
        
        if not self.quiet:
            print("📊 Generating current status snapshot...")
        
        status_counts = defaultdict(int)
        total = 0
        
        for cve_record in self.nvd_data:
            try:
                cve = cve_record.get('cve', {})
                cve_id = cve.get('id', '')
                
                if not cve_id.startswith('CVE-'):
                    continue
                
                status = cve.get('vulnStatus', 'Unknown')
                status_counts[status] += 1
                total += 1
                
            except Exception:
                continue
        
        # Calculate percentages
        status_percentages = {}
        for status, count in status_counts.items():
            status_percentages[status] = round((count / total * 100), 2) if total > 0 else 0
        
        result = {
            'snapshot_date': self.current_date.strftime('%Y-%m-%d'),
            'total_cves': total,
            'status_counts': dict(status_counts),
            'status_percentages': status_percentages
        }
        
        if not self.quiet:
            print(f"✅ Generated status snapshot with {total:,} CVEs")
        
        return result
    
    def generate_quarterly_breakdown(self):
        """
        Generate quarterly CVE breakdown by year.
        
        Output format:
        {
            "2024": {"Q1": 8500, "Q2": 9200, "Q3": 9800, "Q4": 8700, "total": 36200},
            "2023": {"Q1": 7200, "Q2": 8100, "Q3": 8500, "Q4": 8900, "total": 32700}
        }
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return {}
        
        if not self.quiet:
            print("📊 Generating quarterly breakdown...")
        
        quarterly_counts = defaultdict(lambda: {'Q1': 0, 'Q2': 0, 'Q3': 0, 'Q4': 0})
        
        for cve_record in self.nvd_data:
            try:
                cve = cve_record.get('cve', {})
                cve_id = cve.get('id', '')
                
                if not cve_id.startswith('CVE-'):
                    continue
                
                # Skip rejected CVEs
                status = cve.get('vulnStatus', '')
                if 'Rejected' in status:
                    continue
                
                # Get published date
                pub_date_str = cve.get('published')
                pub_date = self.parse_date(pub_date_str)
                
                if pub_date and pub_date.year >= 1999:
                    year = str(pub_date.year)
                    quarter = f"Q{self.get_quarter(pub_date.month)}"
                    quarterly_counts[year][quarter] += 1
                    
            except Exception:
                continue
        
        # Calculate totals and format
        result = {}
        for year in sorted(quarterly_counts.keys()):
            q_data = quarterly_counts[year]
            result[year] = {
                'Q1': q_data['Q1'],
                'Q2': q_data['Q2'],
                'Q3': q_data['Q3'],
                'Q4': q_data['Q4'],
                'total': sum(q_data.values())
            }
        
        if not self.quiet:
            print(f"✅ Generated quarterly breakdown for {len(result)} years")
        
        return result
    
    def generate_growth_table(self):
        """
        Generate comprehensive growth table with cumulative totals, projections, and deltas.
        
        Output format matching the user's requirement:
        [
            {
                "year": 2024,
                "q1": 8500, "q2": 9200, "q3": 9800, "q4": 8700,
                "total_actual": 36200,
                "projection": 38000,
                "cumulative": 340000,
                "cumulative_projection": 342000,
                "yoy_difference": 5200,
                "delta_percent": 16.8
            },
            ...
        ]
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return []
        
        if not self.quiet:
            print("📊 Generating growth table...")
        
        # Get quarterly data first
        quarterly = self.generate_quarterly_breakdown()
        
        # Calculate day of year for projection
        day_of_year = self.current_date.timetuple().tm_yday
        days_in_year = 366 if self.current_year % 4 == 0 else 365
        
        # Build growth table
        growth_table = []
        cumulative = 0
        prev_year_total = 0
        
        for year_str in sorted(quarterly.keys()):
            year = int(year_str)
            q_data = quarterly[year_str]
            
            total_actual = q_data['total']
            cumulative += total_actual
            
            # Calculate projection for current year
            projection = total_actual
            is_current_year = (year == self.current_year)
            
            if is_current_year and day_of_year < days_in_year:
                # Annualize based on YTD
                projection = int(total_actual * days_in_year / day_of_year)
            
            # Calculate YoY difference and delta
            yoy_difference = total_actual - prev_year_total if prev_year_total > 0 else 0
            delta_percent = round((yoy_difference / prev_year_total * 100), 1) if prev_year_total > 0 else 0
            
            entry = {
                'year': year,
                'q1': q_data['Q1'],
                'q2': q_data['Q2'],
                'q3': q_data['Q3'],
                'q4': q_data['Q4'],
                'total_actual': total_actual,
                'projection': projection,
                'total_projection': projection if is_current_year else total_actual,
                'cumulative': cumulative,
                'cumulative_projection': cumulative + (projection - total_actual) if is_current_year else cumulative,
                'yoy_difference': yoy_difference,
                'delta_percent': delta_percent,
                'is_current_year': is_current_year,
                'is_ytd': is_current_year
            }
            
            growth_table.append(entry)
            prev_year_total = total_actual
        
        if not self.quiet:
            print(f"✅ Generated growth table with {len(growth_table)} years")
        
        return growth_table
    
    def generate_status_delta(self, days_back=30):
        """
        Generate status changes over the last N days.
        
        Useful for tracking recent NVD activity.
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return {}
        
        if not self.quiet:
            print(f"📊 Generating {days_back}-day status delta...")
        
        cutoff_date = self.current_date - timedelta(days=days_back)
        
        status_counts = defaultdict(int)
        new_cves = 0
        modified_cves = 0
        
        for cve_record in self.nvd_data:
            try:
                cve = cve_record.get('cve', {})
                cve_id = cve.get('id', '')
                
                if not cve_id.startswith('CVE-'):
                    continue
                
                # Check if modified in the period
                last_modified = self.parse_date(cve.get('lastModified'))
                published = self.parse_date(cve.get('published'))
                
                if last_modified and last_modified >= cutoff_date:
                    status = cve.get('vulnStatus', 'Unknown')
                    status_counts[status] += 1
                    
                    if published and published >= cutoff_date:
                        new_cves += 1
                    else:
                        modified_cves += 1
                    
            except Exception:
                continue
        
        result = {
            'period_days': days_back,
            'period_start': cutoff_date.strftime('%Y-%m-%d'),
            'period_end': self.current_date.strftime('%Y-%m-%d'),
            'total_activity': sum(status_counts.values()),
            'new_cves': new_cves,
            'modified_cves': modified_cves,
            'status_breakdown': dict(status_counts)
        }
        
        if not self.quiet:
            print(f"✅ Generated delta: {result['total_activity']:,} CVEs with activity")
        
        return result
    
    def generate_cna_vulnerability_mapping(self):
        """
        Generate mapping of CNAs to their assigned vulnerabilities.
        
        Output includes:
        - Per-CNA monthly assignment counts
        - Top CNAs by volume
        - CNA activity trends
        """
        if not self.nvd_data:
            self.load_nvd_data()
        
        if not self.nvd_data:
            return {}
        
        if not self.quiet:
            print("📊 Generating CNA vulnerability mapping...")
        
        cna_monthly = defaultdict(lambda: defaultdict(int))
        cna_total = defaultdict(int)
        cna_cves = defaultdict(list)
        
        for cve_record in self.nvd_data:
            try:
                cve = cve_record.get('cve', {})
                cve_id = cve.get('id', '')
                
                if not cve_id.startswith('CVE-'):
                    continue
                
                # Skip rejected CVEs
                status = cve.get('vulnStatus', '')
                if 'Rejected' in status:
                    continue
                
                # Get CNA (source identifier)
                source_id = cve.get('sourceIdentifier', 'Unknown')
                
                # Get published date
                pub_date = self.parse_date(cve.get('published'))
                
                if pub_date:
                    month_key = pub_date.strftime('%Y-%m')
                    cna_monthly[source_id][month_key] += 1
                
                cna_total[source_id] += 1
                
                # Store first 10 CVE IDs per CNA for reference
                if len(cna_cves[source_id]) < 10:
                    cna_cves[source_id].append(cve_id)
                    
            except Exception:
                continue
        
        # Build CNA list with monthly breakdown
        cna_list = []
        for cna, total in sorted(cna_total.items(), key=lambda x: x[1], reverse=True):
            cna_list.append({
                'cna': cna,
                'total_cves': total,
                'monthly_counts': dict(cna_monthly[cna]),
                'sample_cves': cna_cves[cna]
            })
        
        result = {
            'generated_at': self.current_date.isoformat(),
            'total_cnas': len(cna_list),
            'total_cves': sum(cna_total.values()),
            'top_50_cnas': cna_list[:50],
            'cna_list': cna_list
        }
        
        if not self.quiet:
            print(f"✅ Generated CNA mapping for {len(cna_list)} CNAs")
        
        return result
    
    def generate_all(self):
        """Generate all NVD status analysis files"""
        print("\n📊 Generating NVD Status Analysis")
        print("=" * 50)
        
        results = {}
        
        # Ensure data is loaded
        self.load_nvd_data()
        
        if not self.nvd_data:
            print("❌ No NVD data available")
            return None
        
        # 1. Monthly status analysis
        monthly_status = self.generate_monthly_status_analysis()
        
        # 2. Current status snapshot
        status_snapshot = self.generate_current_status_snapshot()
        
        # 3. Quarterly breakdown
        quarterly = self.generate_quarterly_breakdown()
        
        # 4. Growth table
        growth_table = self.generate_growth_table()
        
        # 5. Recent activity delta (30 days and 7 days)
        delta_30 = self.generate_status_delta(30)
        delta_7 = self.generate_status_delta(7)
        
        # 6. CNA vulnerability mapping
        cna_mapping = self.generate_cna_vulnerability_mapping()
        
        # Compile comprehensive analysis
        analysis = {
            'generated_at': self.current_date.isoformat(),
            'data_source': 'NVD',
            'metadata': {
                'total_cves': len(self.nvd_data),
                'current_year': self.current_year,
                'day_of_year': self.current_date.timetuple().tm_yday
            },
            'current_status': status_snapshot,
            'monthly_status': monthly_status,
            'quarterly_breakdown': quarterly,
            'growth_table': growth_table,
            'recent_activity': {
                'last_7_days': delta_7,
                'last_30_days': delta_30
            },
            'cna_mapping_summary': {
                'total_cnas': cna_mapping.get('total_cnas', 0),
                'top_10_cnas': cna_mapping.get('top_50_cnas', [])[:10]
            }
        }
        
        # Save main analysis file
        output_file = self.data_dir / 'nvd_status_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"✅ Generated {output_file.name}")
        results['nvd_status_analysis'] = output_file
        
        # Save growth table separately for easy access
        growth_file = self.data_dir / 'growth_table.json'
        growth_data = {
            'generated_at': self.current_date.isoformat(),
            'growth_table': growth_table,
            'quarterly_breakdown': quarterly
        }
        with open(growth_file, 'w') as f:
            json.dump(growth_data, f, indent=2)
        
        print(f"✅ Generated {growth_file.name}")
        results['growth_table'] = growth_file
        
        # Save CNA vulnerability mapping
        cna_file = self.data_dir / 'cna_vulnerability_mapping.json'
        with open(cna_file, 'w') as f:
            json.dump(cna_mapping, f, indent=2)
        
        print(f"✅ Generated {cna_file.name}")
        results['cna_vulnerability_mapping'] = cna_file
        
        print("=" * 50)
        print("✅ All NVD status analysis files generated!")
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate NVD status analysis")
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet mode')
    parser.add_argument('--output', help='Custom output directory')
    
    args = parser.parse_args()
    
    analyzer = NVDStatusAnalyzer(quiet=args.quiet)
    
    if args.output:
        analyzer.data_dir = Path(args.output)
    
    analyzer.generate_all()


if __name__ == '__main__':
    main()

