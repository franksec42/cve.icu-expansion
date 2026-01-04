#!/usr/bin/env python3
"""
Tests for NVD Status Analysis Module

Tests the NVD status analysis functionality including:
- Monthly status aggregation
- Quarterly breakdown
- Growth table generation
- Status delta calculations
"""

import json
import pytest
from pathlib import Path
from datetime import datetime


# Test fixtures for NVD status analysis
@pytest.fixture
def nvd_status_schema():
    """Schema for nvd_status_analysis.json"""
    return {
        "type": "object",
        "required": ["generated_at", "data_source", "metadata", "current_status"],
        "properties": {
            "generated_at": {"type": "string"},
            "data_source": {"type": "string"},
            "metadata": {
                "type": "object",
                "required": ["total_cves", "current_year"],
                "properties": {
                    "total_cves": {"type": "integer", "minimum": 0},
                    "current_year": {"type": "integer"},
                    "day_of_year": {"type": "integer"}
                }
            },
            "current_status": {
                "type": "object",
                "required": ["snapshot_date", "total_cves", "status_counts"],
                "properties": {
                    "snapshot_date": {"type": "string"},
                    "total_cves": {"type": "integer", "minimum": 0},
                    "status_counts": {"type": "object"},
                    "status_percentages": {"type": "object"}
                }
            },
            "monthly_status": {"type": "object"},
            "quarterly_breakdown": {"type": "object"},
            "growth_table": {"type": "array"},
            "recent_activity": {"type": "object"}
        }
    }


@pytest.fixture
def growth_table_schema():
    """Schema for growth_table.json"""
    return {
        "type": "object",
        "required": ["generated_at", "growth_table", "quarterly_breakdown"],
        "properties": {
            "generated_at": {"type": "string"},
            "growth_table": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["year", "q1", "q2", "q3", "q4", "total_actual", "cumulative"],
                    "properties": {
                        "year": {"type": "integer"},
                        "q1": {"type": "integer"},
                        "q2": {"type": "integer"},
                        "q3": {"type": "integer"},
                        "q4": {"type": "integer"},
                        "total_actual": {"type": "integer"},
                        "projection": {"type": "integer"},
                        "cumulative": {"type": "integer"},
                        "yoy_difference": {"type": "integer"},
                        "delta_percent": {"type": "number"},
                        "is_current_year": {"type": "boolean"},
                        "is_ytd": {"type": "boolean"}
                    }
                }
            },
            "quarterly_breakdown": {"type": "object"}
        }
    }


class TestNVDStatusAnalysisOutput:
    """Test NVD status analysis output files if they exist"""
    
    @pytest.fixture
    def web_data_dir(self):
        """Get path to web/data directory"""
        return Path(__file__).parent.parent / 'web' / 'data'
    
    def test_nvd_status_file_exists(self, web_data_dir):
        """Test that nvd_status_analysis.json exists after build"""
        nvd_status_file = web_data_dir / 'nvd_status_analysis.json'
        
        if not nvd_status_file.exists():
            pytest.skip("nvd_status_analysis.json not found - run build first")
        
        assert nvd_status_file.exists()
    
    def test_nvd_status_valid_json(self, web_data_dir):
        """Test that nvd_status_analysis.json is valid JSON"""
        nvd_status_file = web_data_dir / 'nvd_status_analysis.json'
        
        if not nvd_status_file.exists():
            pytest.skip("nvd_status_analysis.json not found - run build first")
        
        with open(nvd_status_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert 'generated_at' in data
    
    def test_nvd_status_has_required_fields(self, web_data_dir, nvd_status_schema):
        """Test that nvd_status_analysis.json has required fields"""
        nvd_status_file = web_data_dir / 'nvd_status_analysis.json'
        
        if not nvd_status_file.exists():
            pytest.skip("nvd_status_analysis.json not found - run build first")
        
        with open(nvd_status_file, 'r') as f:
            data = json.load(f)
        
        for field in nvd_status_schema['required']:
            assert field in data, f"Missing required field: {field}"
    
    def test_nvd_status_has_status_counts(self, web_data_dir):
        """Test that current_status has valid status counts"""
        nvd_status_file = web_data_dir / 'nvd_status_analysis.json'
        
        if not nvd_status_file.exists():
            pytest.skip("nvd_status_analysis.json not found - run build first")
        
        with open(nvd_status_file, 'r') as f:
            data = json.load(f)
        
        current_status = data.get('current_status', {})
        status_counts = current_status.get('status_counts', {})
        
        assert isinstance(status_counts, dict)
        
        # Should have at least some known status values
        known_statuses = ['Analyzed', 'Awaiting Analysis', 'Modified', 'Rejected']
        found_statuses = [s for s in known_statuses if s in status_counts]
        
        assert len(found_statuses) > 0, "No known NVD status values found"
    
    def test_growth_table_file_exists(self, web_data_dir):
        """Test that growth_table.json exists after build"""
        growth_file = web_data_dir / 'growth_table.json'
        
        if not growth_file.exists():
            pytest.skip("growth_table.json not found - run build first")
        
        assert growth_file.exists()
    
    def test_growth_table_valid_json(self, web_data_dir):
        """Test that growth_table.json is valid JSON"""
        growth_file = web_data_dir / 'growth_table.json'
        
        if not growth_file.exists():
            pytest.skip("growth_table.json not found - run build first")
        
        with open(growth_file, 'r') as f:
            data = json.load(f)
        
        assert isinstance(data, dict)
        assert 'growth_table' in data
    
    def test_growth_table_has_years(self, web_data_dir):
        """Test that growth_table has data for multiple years"""
        growth_file = web_data_dir / 'growth_table.json'
        
        if not growth_file.exists():
            pytest.skip("growth_table.json not found - run build first")
        
        with open(growth_file, 'r') as f:
            data = json.load(f)
        
        growth_table = data.get('growth_table', [])
        assert len(growth_table) > 10, "Growth table should have 10+ years"
        
        # Check structure of entries
        for entry in growth_table[:3]:  # Check first 3 entries
            assert 'year' in entry
            assert 'q1' in entry
            assert 'q2' in entry
            assert 'q3' in entry
            assert 'q4' in entry
            assert 'total_actual' in entry
            assert 'cumulative' in entry
    
    def test_quarterly_totals_match(self, web_data_dir):
        """Test that quarterly totals equal total_actual"""
        growth_file = web_data_dir / 'growth_table.json'
        
        if not growth_file.exists():
            pytest.skip("growth_table.json not found - run build first")
        
        with open(growth_file, 'r') as f:
            data = json.load(f)
        
        growth_table = data.get('growth_table', [])
        
        for entry in growth_table:
            quarterly_sum = entry['q1'] + entry['q2'] + entry['q3'] + entry['q4']
            
            # For current year (YTD), Q4 might be 0 or incomplete
            if not entry.get('is_current_year', False):
                assert quarterly_sum == entry['total_actual'], \
                    f"Year {entry['year']}: quarterly sum {quarterly_sum} != total {entry['total_actual']}"
    
    def test_cumulative_is_increasing(self, web_data_dir):
        """Test that cumulative totals are always increasing"""
        growth_file = web_data_dir / 'growth_table.json'
        
        if not growth_file.exists():
            pytest.skip("growth_table.json not found - run build first")
        
        with open(growth_file, 'r') as f:
            data = json.load(f)
        
        growth_table = data.get('growth_table', [])
        
        prev_cumulative = 0
        for entry in growth_table:
            assert entry['cumulative'] >= prev_cumulative, \
                f"Cumulative decreased at year {entry['year']}"
            prev_cumulative = entry['cumulative']
    
    def test_cna_mapping_file_exists(self, web_data_dir):
        """Test that cna_vulnerability_mapping.json exists"""
        cna_file = web_data_dir / 'cna_vulnerability_mapping.json'
        
        if not cna_file.exists():
            pytest.skip("cna_vulnerability_mapping.json not found - run build first")
        
        assert cna_file.exists()
    
    def test_cna_mapping_has_cnas(self, web_data_dir):
        """Test that CNA mapping has CNA entries"""
        cna_file = web_data_dir / 'cna_vulnerability_mapping.json'
        
        if not cna_file.exists():
            pytest.skip("cna_vulnerability_mapping.json not found - run build first")
        
        with open(cna_file, 'r') as f:
            data = json.load(f)
        
        assert 'total_cnas' in data
        assert data['total_cnas'] > 0
        assert 'cna_list' in data or 'top_50_cnas' in data


class TestNVDStatusAnalyzer:
    """Unit tests for NVDStatusAnalyzer class"""
    
    def test_get_quarter_q1(self):
        """Test quarter calculation for Q1 months"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        assert analyzer.get_quarter(1) == 1
        assert analyzer.get_quarter(2) == 1
        assert analyzer.get_quarter(3) == 1
    
    def test_get_quarter_q2(self):
        """Test quarter calculation for Q2 months"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        assert analyzer.get_quarter(4) == 2
        assert analyzer.get_quarter(5) == 2
        assert analyzer.get_quarter(6) == 2
    
    def test_get_quarter_q3(self):
        """Test quarter calculation for Q3 months"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        assert analyzer.get_quarter(7) == 3
        assert analyzer.get_quarter(8) == 3
        assert analyzer.get_quarter(9) == 3
    
    def test_get_quarter_q4(self):
        """Test quarter calculation for Q4 months"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        assert analyzer.get_quarter(10) == 4
        assert analyzer.get_quarter(11) == 4
        assert analyzer.get_quarter(12) == 4
    
    def test_parse_date_valid(self):
        """Test date parsing with valid ISO date"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        result = analyzer.parse_date('2024-01-15T10:30:00Z')
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15
    
    def test_parse_date_invalid(self):
        """Test date parsing with invalid date"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        result = analyzer.parse_date('not-a-date')
        assert result is None
    
    def test_parse_date_none(self):
        """Test date parsing with None"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / 'data'))
        from nvd_status_analysis import NVDStatusAnalyzer
        
        analyzer = NVDStatusAnalyzer(quiet=True)
        
        result = analyzer.parse_date(None)
        assert result is None

