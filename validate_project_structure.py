#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Structure Validation Script
Kiểm tra và validate cấu trúc dự án để đảm bảo logic flow không có xung đột
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ProjectValidator:
    """Class để validate cấu trúc dự án"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.validation_results = {
            'timestamp': datetime.now().isoformat(),
            'total_files': 0,
            'total_directories': 0,
            'issues': [],
            'warnings': [],
            'recommendations': [],
            'file_conflicts': [],
            'dependency_conflicts': [],
            'structure_score': 0
        }
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate toàn bộ cấu trúc dự án"""
        print("🔍 Bắt đầu validation cấu trúc dự án...")
        
        # Đếm files và directories
        self._count_files_and_directories()
        
        # Kiểm tra conflicts
        self._check_file_conflicts()
        self._check_dependency_conflicts()
        self._check_naming_conventions()
        self._check_directory_structure()
        
        # Tính điểm structure
        self._calculate_structure_score()
        
        return self.validation_results
    
    def _count_files_and_directories(self):
        """Đếm số lượng files và directories"""
        file_count = 0
        dir_count = 0
        
        for root, dirs, files in os.walk(self.project_root):
            # Bỏ qua .venv và các thư mục ẩn khác
            if '.venv' in root or '__pycache__' in root:
                continue
                
            dir_count += len(dirs)
            file_count += len(files)
        
        self.validation_results['total_files'] = file_count
        self.validation_results['total_directories'] = dir_count
    
    def _check_file_conflicts(self):
        """Kiểm tra xung đột files"""
        print("📋 Kiểm tra xung đột files...")
        
        # Kiểm tra duplicate names
        file_names = {}
        for root, dirs, files in os.walk(self.project_root):
            if '.venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file in file_names:
                    self.validation_results['file_conflicts'].append({
                        'type': 'duplicate_name',
                        'file': file,
                        'locations': [file_names[file], os.path.join(root, file)]
                    })
                else:
                    file_names[file] = os.path.join(root, file)
        
        # Kiểm tra main entry points
        main_files = ['main.py', 'app.py', 'run.py', 'start.py']
        found_mains = []
        for main_file in main_files:
            if (self.project_root / main_file).exists():
                found_mains.append(main_file)
        
        if len(found_mains) > 1:
            self.validation_results['warnings'].append({
                'type': 'multiple_main_files',
                'files': found_mains,
                'message': 'Nhiều file main entry point có thể gây nhầm lẫn'
            })
    
    def _check_dependency_conflicts(self):
        """Kiểm tra xung đột dependencies"""
        print("📦 Kiểm tra xung đột dependencies...")
        
        requirements_files = list(self.project_root.glob("requirements*.txt"))
        if len(requirements_files) > 1:
            self.validation_results['dependency_conflicts'].append({
                'type': 'multiple_requirements',
                'files': [str(f) for f in requirements_files],
                'message': 'Nhiều file requirements có thể gây xung đột'
            })
        
        # Kiểm tra setup.py conflicts
        setup_files = list(self.project_root.glob("setup*.py"))
        if len(setup_files) > 1:
            self.validation_results['dependency_conflicts'].append({
                'type': 'multiple_setup',
                'files': [str(f) for f in setup_files],
                'message': 'Nhiều file setup có thể gây xung đột'
            })
    
    def _check_naming_conventions(self):
        """Kiểm tra naming conventions"""
        print("📝 Kiểm tra naming conventions...")
        
        # Kiểm tra Python files
        python_files = list(self.project_root.rglob("*.py"))
        for py_file in python_files:
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            # Kiểm tra naming convention
            if py_file.name != py_file.name.lower():
                self.validation_results['warnings'].append({
                    'type': 'naming_convention',
                    'file': str(py_file),
                    'message': 'Python file names should be lowercase'
                })
    
    def _check_directory_structure(self):
        """Kiểm tra cấu trúc thư mục"""
        print("📁 Kiểm tra cấu trúc thư mục...")
        
        # Kiểm tra các thư mục quan trọng
        important_dirs = ['config', 'modules', 'utils', 'tests', 'logs', 'output']
        missing_dirs = []
        
        for dir_name in important_dirs:
            if not (self.project_root / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self.validation_results['recommendations'].append({
                'type': 'missing_directories',
                'directories': missing_dirs,
                'message': 'Nên tạo các thư mục này để tổ chức tốt hơn'
            })
        
        # Kiểm tra archive directory
        if (self.project_root / 'archive').exists():
            self.validation_results['recommendations'].append({
                'type': 'archive_found',
                'message': 'Thư mục archive đã được tạo để tổ chức files'
            })
    
    def _calculate_structure_score(self):
        """Tính điểm cấu trúc"""
        score = 100
        
        # Trừ điểm cho các issues
        score -= len(self.validation_results['file_conflicts']) * 10
        score -= len(self.validation_results['dependency_conflicts']) * 15
        score -= len(self.validation_results['issues']) * 5
        score -= len(self.validation_results['warnings']) * 2
        
        # Cộng điểm cho recommendations được thực hiện
        if any(rec['type'] == 'archive_found' for rec in self.validation_results['recommendations']):
            score += 10
        
        self.validation_results['structure_score'] = max(0, min(100, score))
    
    def generate_report(self) -> str:
        """Tạo báo cáo validation"""
        report = []
        report.append("=" * 80)
        report.append("📊 PROJECT STRUCTURE VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"🕐 Timestamp: {self.validation_results['timestamp']}")
        report.append(f"📁 Total Files: {self.validation_results['total_files']}")
        report.append(f"📂 Total Directories: {self.validation_results['total_directories']}")
        report.append(f"⭐ Structure Score: {self.validation_results['structure_score']}/100")
        report.append("")
        
        # Issues
        if self.validation_results['issues']:
            report.append("❌ ISSUES:")
            for issue in self.validation_results['issues']:
                report.append(f"  - {issue}")
            report.append("")
        
        # File Conflicts
        if self.validation_results['file_conflicts']:
            report.append("⚠️ FILE CONFLICTS:")
            for conflict in self.validation_results['file_conflicts']:
                report.append(f"  - {conflict['type']}: {conflict['file']}")
                if 'locations' in conflict:
                    for loc in conflict['locations']:
                        report.append(f"    → {loc}")
            report.append("")
        
        # Dependency Conflicts
        if self.validation_results['dependency_conflicts']:
            report.append("📦 DEPENDENCY CONFLICTS:")
            for conflict in self.validation_results['dependency_conflicts']:
                report.append(f"  - {conflict['type']}: {conflict['message']}")
                if 'files' in conflict:
                    for file in conflict['files']:
                        report.append(f"    → {file}")
            report.append("")
        
        # Warnings
        if self.validation_results['warnings']:
            report.append("⚠️ WARNINGS:")
            for warning in self.validation_results['warnings']:
                report.append(f"  - {warning['message']}")
                if 'file' in warning:
                    report.append(f"    → {warning['file']}")
            report.append("")
        
        # Recommendations
        if self.validation_results['recommendations']:
            report.append("💡 RECOMMENDATIONS:")
            for rec in self.validation_results['recommendations']:
                report.append(f"  - {rec['message']}")
            report.append("")
        
        # Summary
        report.append("📋 SUMMARY:")
        if self.validation_results['structure_score'] >= 90:
            report.append("  ✅ Excellent project structure!")
        elif self.validation_results['structure_score'] >= 70:
            report.append("  ✅ Good project structure with minor issues")
        elif self.validation_results['structure_score'] >= 50:
            report.append("  ⚠️ Fair project structure, needs improvement")
        else:
            report.append("  ❌ Poor project structure, requires major cleanup")
        
        report.append("=" * 80)
        
        return "\n".join(report)

def main():
    """Main function"""
    print("🚀 Starting Project Structure Validation...")
    
    validator = ProjectValidator()
    results = validator.validate_structure()
    
    # In báo cáo
    report = validator.generate_report()
    print(report)
    
    # Lưu báo cáo
    report_file = Path("validation_report.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Báo cáo đã được lưu vào: {report_file}")
    
    # Lưu kết quả JSON
    json_file = Path("validation_results.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Kết quả chi tiết đã được lưu vào: {json_file}")
    
    return results['structure_score'] >= 70

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)