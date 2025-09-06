"""
Automation Scripts for Production Deployment
Handles training, deployment, monitoring, and data pipeline automation
"""

import asyncio
import logging
import sys
from pathlib import Path
import click
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import settings
from app.services.orchestrator import PredictionOrchestrator
from app.data.data_pipeline import DataPipeline
from app.utils.monitoring import SystemMonitor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    """Vehicle Price Prediction Automation CLI"""
    pass

@cli.command()
@click.option('--data-path', default=None, help='Path to training data')
@click.option('--model-version', default=None, help='Model version to train')
@click.option('--validation-split', default=0.2, help='Validation split ratio')
def train(data_path, model_version, validation_split):
    """Train ML model with automated pipeline"""
    async def _train():
        try:
            logger.info("🚀 Starting automated training pipeline...")
            
            # Initialize orchestrator
            orchestrator = PredictionOrchestrator()
            await orchestrator.initialize()
            
            # Load training data
            if data_path:
                data = await orchestrator.data_pipeline.load_data_from_path(data_path)
            else:
                data = await orchestrator.data_pipeline.load_default_training_data()
            
            logger.info(f"📊 Loaded {len(data)} training samples")
            
            # Train model
            await orchestrator.ml_model.train(data)
            
            # Validate model
            validation_results = await orchestrator.ml_model.validate()
            logger.info(f"✅ Validation results: {validation_results}")
            
            # Update vector search index
            await orchestrator.vector_search.update_index(data)
            
            # Update RAG knowledge base
            await orchestrator.rag_engine.update_knowledge_base(data)
            
            logger.info("🎉 Training pipeline completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Training failed: {e}")
            sys.exit(1)
        finally:
            if 'orchestrator' in locals():
                await orchestrator.cleanup()
    
    asyncio.run(_train())

@cli.command()
@click.option('--environment', default='production', help='Deployment environment')
@click.option('--docker', is_flag=True, help='Deploy using Docker')
@click.option('--scale', default=1, help='Number of instances to deploy')
def deploy(environment, docker, scale):
    """Deploy application to production"""
    try:
        logger.info(f"🚀 Deploying to {environment} environment...")
        
        if docker:
            # Docker deployment
            import subprocess
            
            if environment == 'production':
                compose_file = 'docker-compose.yml'
            else:
                compose_file = f'docker-compose.{environment}.yml'
            
            # Build and deploy
            subprocess.run(['docker-compose', '-f', compose_file, 'build'], check=True)
            subprocess.run(['docker-compose', '-f', compose_file, 'up', '-d', '--scale', f'api={scale}'], check=True)
            
            logger.info(f"✅ Deployed {scale} instances using Docker")
        else:
            # Direct deployment
            logger.info("Direct deployment not implemented yet")
            
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--duration', default=3600, help='Monitoring duration in seconds')
@click.option('--interval', default=60, help='Check interval in seconds')
def monitor(duration, interval):
    """Monitor application health and performance"""
    async def _monitor():
        try:
            logger.info(f"📊 Starting monitoring for {duration} seconds...")
            
            monitor = SystemMonitor()
            await monitor.start_monitoring(duration, interval)
            
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            sys.exit(1)
    
    asyncio.run(_monitor())

@cli.command()
@click.option('--source', default=None, help='Data source path or URL')
@click.option('--format', default='csv', help='Data format (csv, json, parquet)')
@click.option('--schedule', default=None, help='Cron schedule for automated ingestion')
def ingest(source, format, schedule):
    """Ingest new data into the system"""
    async def _ingest():
        try:
            logger.info(f"📥 Starting data ingestion from {source}...")
            
            pipeline = DataPipeline()
            await pipeline.initialize()
            
            if schedule:
                # Schedule automated ingestion
                await pipeline.schedule_ingestion(source, format, schedule)
                logger.info(f"⏰ Scheduled data ingestion: {schedule}")
            else:
                # One-time ingestion
                data = await pipeline.ingest_data(source, format)
                logger.info(f"✅ Ingested {len(data)} records")
            
        except Exception as e:
            logger.error(f"❌ Data ingestion failed: {e}")
            sys.exit(1)
    
    asyncio.run(_ingest())

@cli.command()
def health():
    """Check system health"""
    async def _health():
        try:
            logger.info("🔍 Checking system health...")
            
            orchestrator = PredictionOrchestrator()
            await orchestrator.initialize()
            
            health_status = await orchestrator.health_check()
            
            print("\n=== SYSTEM HEALTH REPORT ===")
            print(f"Overall Status: {health_status['status']}")
            print(f"Version: {health_status['version']}")
            print(f"Uptime: {health_status['uptime_seconds']:.1f} seconds")
            print("\nService Status:")
            for service, status in health_status['services'].items():
                print(f"  {service}: {status}")
            
            if health_status['status'] != 'healthy':
                sys.exit(1)
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            sys.exit(1)
        finally:
            if 'orchestrator' in locals():
                await orchestrator.cleanup()
    
    asyncio.run(_health())

@cli.command()
@click.option('--backup-path', default=None, help='Backup destination path')
def backup(backup_path):
    """Backup models and data"""
    try:
        logger.info("💾 Starting backup process...")
        
        import shutil
        from datetime import datetime
        
        if not backup_path:
            backup_path = f"./backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup models
        models_dir = Path("./models")
        if models_dir.exists():
            shutil.copytree(models_dir, backup_dir / "models", dirs_exist_ok=True)
        
        # Backup vector database
        vector_db_dir = Path(settings.vector_db_path)
        if vector_db_dir.exists():
            shutil.copytree(vector_db_dir, backup_dir / "vector_db", dirs_exist_ok=True)
        
        # Backup configuration
        config_files = [".env", "app/config/settings.py"]
        for config_file in config_files:
            if Path(config_file).exists():
                shutil.copy2(config_file, backup_dir)
        
        logger.info(f"✅ Backup completed: {backup_path}")
        
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        sys.exit(1)

@cli.command()
@click.option('--backup-path', required=True, help='Backup source path')
def restore(backup_path):
    """Restore from backup"""
    try:
        logger.info(f"🔄 Restoring from backup: {backup_path}")
        
        import shutil
        
        backup_dir = Path(backup_path)
        if not backup_dir.exists():
            raise ValueError(f"Backup directory not found: {backup_path}")
        
        # Restore models
        models_backup = backup_dir / "models"
        if models_backup.exists():
            models_dir = Path("./models")
            if models_dir.exists():
                shutil.rmtree(models_dir)
            shutil.copytree(models_backup, models_dir)
        
        # Restore vector database
        vector_backup = backup_dir / "vector_db"
        if vector_backup.exists():
            vector_db_dir = Path(settings.vector_db_path)
            if vector_db_dir.exists():
                shutil.rmtree(vector_db_dir)
            shutil.copytree(vector_backup, vector_db_dir)
        
        logger.info("✅ Restore completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Restore failed: {e}")
        sys.exit(1)

@cli.command()
def setup():
    """Setup production environment"""
    async def _setup():
        try:
            logger.info("🔧 Setting up production environment...")
            
            # Create necessary directories
            directories = [
                "models",
                "logs", 
                "data",
                "backups",
                settings.vector_db_path,
                settings.knowledge_base_path
            ]
            
            for directory in directories:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"📁 Created directory: {directory}")
            
            # Initialize orchestrator
            orchestrator = PredictionOrchestrator()
            await orchestrator.initialize()
            
            # Run initial training if no model exists
            model_path = Path(settings.model_path)
            if not model_path.exists():
                logger.info("🏋️ No model found, training initial model...")
                await orchestrator.ml_model._train_initial_model()
            
            logger.info("✅ Production environment setup completed!")
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            sys.exit(1)
        finally:
            if 'orchestrator' in locals():
                await orchestrator.cleanup()
    
    asyncio.run(_setup())

if __name__ == '__main__':
    cli()
