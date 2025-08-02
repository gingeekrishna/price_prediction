#!/usr/bin/env python3
"""
Project Organization Verification Script
Verifies that all files are properly organized and accessible
"""

import os
import sys
from pathlib import Path

def check_directory_structure():
    """Verify the organized directory structure"""
    base_path = Path.cwd()
    
    expected_structure = {
        'config': ['.env.local', '.env.development', '.env.production'],
        'docker': ['docker-compose.local-ai.yml', 'docker-compose.development.yml', 'docker-compose.production.yml'],
        'docs': ['BEDROCK_INTEGRATION.md', 'BEDROCK_IMPLEMENTATION_SUMMARY.md', 'PROJECT_STRUCTURE.md'],
        'scripts': [
            'setup_development.sh', 'deploy_production.sh', 'health_check.sh',
            'run_tests.sh', 'setup_local_ai.sh', 'test_bedrock_integration.py',
            'build_faiss_index.py', 'train_model.py'
        ],
        'src/agents': [
            'bedrock_agent.py', 'mock_bedrock_agent.py', 'explainer_agent.py',
            'insight_agent.py', 'logger_agent.py', 'market_agent.py',
            'market_data_agent.py', 'model_agent.py'
        ]
    }
    
    print("🔍 Verifying Project Organization")
    print("=" * 50)
    
    all_good = True
    
    for directory, files in expected_structure.items():
        dir_path = base_path / directory
        print(f"\n📁 Checking {directory}/")
        
        if not dir_path.exists():
            print(f"  ❌ Directory {directory}/ not found")
            all_good = False
            continue
        
        for file_name in files:
            file_path = dir_path / file_name
            if file_path.exists():
                print(f"  ✅ {file_name}")
            else:
                print(f"  ❌ {file_name} - MISSING")
                all_good = False
    
    return all_good

def check_imports():
    """Check if imports still work after reorganization"""
    print("\n🐍 Checking Python Imports")
    print("=" * 50)
    
    import_tests = [
        ("src.agents.bedrock_agent", "BedrockAgent"),
        ("src.agents.mock_bedrock_agent", "MockBedrockAgent"),
        ("src.agents.explainer_agent", "ExplainerAgent"),
        ("src.api", "app"),
        ("src.model", "VehiclePriceModel"),
    ]
    
    all_imports_good = True
    
    for module_path, class_name in import_tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            getattr(module, class_name)
            print(f"  ✅ {module_path}.{class_name}")
        except Exception as e:
            print(f"  ❌ {module_path}.{class_name} - ERROR: {e}")
            all_imports_good = False
    
    return all_imports_good

def check_docker_configs():
    """Verify Docker configurations are accessible"""
    print("\n🐳 Checking Docker Configurations")
    print("=" * 50)
    
    docker_files = [
        'docker/docker-compose.local-ai.yml',
        'docker/docker-compose.development.yml',
        'docker/docker-compose.production.yml'
    ]
    
    all_docker_good = True
    
    for docker_file in docker_files:
        if Path(docker_file).exists():
            print(f"  ✅ {docker_file}")
        else:
            print(f"  ❌ {docker_file} - MISSING")
            all_docker_good = False
    
    return all_docker_good

def check_environment_configs():
    """Verify environment configurations"""
    print("\n⚙️ Checking Environment Configurations")
    print("=" * 50)
    
    env_files = [
        'config/.env.local',
        'config/.env.development',
        'config/.env.production'
    ]
    
    all_env_good = True
    
    for env_file in env_files:
        if Path(env_file).exists():
            print(f"  ✅ {env_file}")
        else:
            print(f"  ❌ {env_file} - MISSING")
            all_env_good = False
    
    return all_env_good

def main():
    """Main verification function"""
    print("🚀 Vehicle Price Prediction - Project Organization Verification")
    print("=" * 70)
    
    # Add src to Python path for imports
    src_path = Path.cwd() / 'src'
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    checks = [
        ("Directory Structure", check_directory_structure),
        ("Python Imports", check_imports),
        ("Docker Configurations", check_docker_configs),
        ("Environment Configurations", check_environment_configs),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ Error in {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for check_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status:<12} {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 PROJECT ORGANIZATION COMPLETE!")
        print("   All files are properly organized and accessible.")
        print("\n🚀 Ready for development and deployment!")
        print("\n📖 Quick Start:")
        print("   • Development: ./scripts/setup_development.sh")
        print("   • Local AI: docker-compose -f docker/docker-compose.local-ai.yml up")
        print("   • Production: ./scripts/deploy_production.sh")
        print("   • Tests: ./scripts/run_tests.sh")
        return 0
    else:
        print("⚠️ ORGANIZATION ISSUES DETECTED")
        print("   Some files may need to be moved or imports updated.")
        return 1

if __name__ == "__main__":
    exit(main())
