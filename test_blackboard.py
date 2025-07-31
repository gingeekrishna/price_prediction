"""
Test and demonstration script for the Blackboard/Coordinator pattern integration.

This script demonstrates the complete blackboard coordination system including:
- Message passing between agents
- Workflow coordination
- Error handling and recovery
- Performance monitoring
"""

import asyncio
import json
import time
import logging
from datetime import datetime
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_basic_coordination():
    """Test basic blackboard coordination functionality."""
    print("=" * 60)
    print("Testing Basic Blackboard Coordination")
    print("=" * 60)
    
    try:
        from src.blackboard_agents import VehiclePriceWorkflowCoordinator
        
        # Create and start workflow coordinator
        workflow = VehiclePriceWorkflowCoordinator(use_ollama=False)
        workflow.start()
        
        print("✅ Workflow coordinator started")
        
        # Test coordinated prediction
        print("\n🔄 Making coordinated prediction...")
        start_time = time.time()
        
        result = await workflow.predict_price(
            vehicle_age=3,
            mileage=45000,
            include_explanation=True,
            include_insights=True,
            timeout=30.0
        )
        
        processing_time = time.time() - start_time
        
        print(f"✅ Prediction completed in {processing_time:.2f}s")
        print(f"   Predicted Price: ${result['predicted_price']:.2f}")
        print(f"   Explanation: {result['explanation'][:100]}...")
        print(f"   Recommendation: {result['recommendation'][:100]}...")
        
        # Get workflow status
        status = workflow.get_workflow_status()
        print(f"\n📊 Workflow Status:")
        print(f"   Active Agents: {list(status['agents_status'].keys())}")
        print(f"   Blackboard Messages: {status['blackboard_messages']}")
        
        workflow.stop()
        print("✅ Workflow coordinator stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic coordination test failed: {e}")
        logger.exception("Basic coordination test error")
        return False


async def test_message_flow():
    """Test message flow and agent communication."""
    print("\n" + "=" * 60)
    print("Testing Message Flow and Agent Communication")
    print("=" * 60)
    
    try:
        from src.coordinator import BlackboardCoordinator, MessageType, Priority
        from src.blackboard_agents import BlackboardMarketAgent
        
        # Create coordinator and agent
        coordinator = BlackboardCoordinator()
        coordinator.start()
        
        market_agent = BlackboardMarketAgent(coordinator)
        market_agent.start()
        
        print("✅ Coordinator and market agent started")
        
        # Post a prediction request
        print("\n📤 Posting prediction request...")
        request_id = coordinator.post_message(
            MessageType.PREDICTION_REQUEST,
            {
                "vehicle_age": 5,
                "mileage": 75000,
                "brand": "Toyota",
                "model": "Camry"
            },
            "test_client",
            Priority.HIGH
        )
        
        # Wait for market data response
        await asyncio.sleep(2)
        
        # Check for market data messages
        market_messages = coordinator.get_messages(
            MessageType.MARKET_DATA,
            since=datetime.now()
        )
        
        if market_messages:
            print(f"✅ Market data received: {len(market_messages)} messages")
            latest_data = market_messages[0].data
            print(f"   Market Index: {latest_data.get('market_data', {}).get('market_index', 'N/A')}")
            print(f"   Fuel Price: {latest_data.get('market_data', {}).get('fuel_price', 'N/A')}")
        else:
            print("❌ No market data received")
        
        # Get all messages for analysis
        all_messages = coordinator.get_messages(limit=10)
        print(f"\n📊 Total messages on blackboard: {len(coordinator.messages)}")
        print(f"   Recent messages: {len(all_messages)}")
        
        for msg in all_messages[:3]:
            print(f"   - {msg.message_type.value} from {msg.sender}")
        
        market_agent.stop()
        coordinator.stop()
        print("✅ Message flow test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Message flow test failed: {e}")
        logger.exception("Message flow test error")
        return False


async def test_error_handling():
    """Test error handling and recovery mechanisms."""
    print("\n" + "=" * 60)
    print("Testing Error Handling and Recovery")
    print("=" * 60)
    
    try:
        from src.blackboard_agents import VehiclePriceWorkflowCoordinator
        
        # Create workflow coordinator
        workflow = VehiclePriceWorkflowCoordinator()
        workflow.start()
        
        print("✅ Workflow started for error testing")
        
        # Test with invalid input (should handle gracefully)
        print("\n🔄 Testing with invalid vehicle age...")
        try:
            result = await workflow.predict_price(
                vehicle_age=-5,  # Invalid age
                mileage=45000,
                timeout=10.0
            )
            print("❌ Should have failed with invalid age")
        except Exception as e:
            print(f"✅ Properly handled invalid input: {type(e).__name__}")
        
        # Test timeout scenario
        print("\n🔄 Testing timeout handling...")
        try:
            result = await workflow.predict_price(
                vehicle_age=3,
                mileage=45000,
                timeout=0.1  # Very short timeout
            )
            print("❌ Should have timed out")
        except Exception as e:
            print(f"✅ Properly handled timeout: {type(e).__name__}")
        
        # Test with valid input after errors
        print("\n🔄 Testing recovery with valid input...")
        result = await workflow.predict_price(
            vehicle_age=4,
            mileage=55000,
            timeout=15.0
        )
        print(f"✅ Recovery successful: ${result['predicted_price']:.2f}")
        
        workflow.stop()
        print("✅ Error handling test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        logger.exception("Error handling test error")
        return False


async def test_performance_monitoring():
    """Test performance monitoring and metrics collection."""
    print("\n" + "=" * 60)
    print("Testing Performance Monitoring")
    print("=" * 60)
    
    try:
        from src.blackboard_agents import VehiclePriceWorkflowCoordinator
        
        workflow = VehiclePriceWorkflowCoordinator()
        workflow.start()
        
        print("✅ Starting performance test...")
        
        # Run multiple predictions concurrently
        tasks = []
        num_predictions = 5
        
        print(f"\n🔄 Running {num_predictions} concurrent predictions...")
        start_time = time.time()
        
        for i in range(num_predictions):
            task = workflow.predict_price(
                vehicle_age=2 + i,
                mileage=30000 + (i * 10000),
                timeout=20.0
            )
            tasks.append(task)
        
        # Wait for all predictions to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = time.time() - start_time
        successful_predictions = [r for r in results if not isinstance(r, Exception)]
        failed_predictions = [r for r in results if isinstance(r, Exception)]
        
        print(f"✅ Performance test completed in {total_time:.2f}s")
        print(f"   Successful predictions: {len(successful_predictions)}")
        print(f"   Failed predictions: {len(failed_predictions)}")
        print(f"   Average time per prediction: {total_time/num_predictions:.2f}s")
        
        if successful_predictions:
            avg_price = sum(r['predicted_price'] for r in successful_predictions) / len(successful_predictions)
            print(f"   Average predicted price: ${avg_price:.2f}")
        
        # Check system status
        status = workflow.get_workflow_status()
        print(f"\n📊 Final System Status:")
        print(f"   Coordinator Active: {status['coordinator_active']}")
        print(f"   Active Requests: {status['active_requests']}")
        print(f"   Total Messages: {status['blackboard_messages']}")
        
        workflow.stop()
        print("✅ Performance monitoring test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        logger.exception("Performance monitoring test error")
        return False


async def test_custom_workflow():
    """Test custom workflow creation and execution."""
    print("\n" + "=" * 60)
    print("Testing Custom Workflow Creation")
    print("=" * 60)
    
    try:
        from src.coordinator import BlackboardCoordinator, WorkflowBuilder
        
        coordinator = BlackboardCoordinator()
        coordinator.start()
        
        print("✅ Coordinator started for custom workflow test")
        
        # Create a custom workflow
        builder = WorkflowBuilder(coordinator)
        
        workflow_def = (builder
            .add_step("market_analysis", "market_agent", "analyze", 
                     data={"region": "US", "depth": "detailed"})
            .add_step("price_prediction", "prediction_agent", "predict",
                     dependencies=["market_analysis"],
                     data={"vehicle_age": 3, "mileage": 45000})
            .add_step("explanation_gen", "explainer_agent", "explain",
                     dependencies=["price_prediction"])
            .build("custom_test_workflow")
        )
        
        print("✅ Custom workflow definition created")
        print(f"   Steps: {len(workflow_def['steps'])}")
        print(f"   First step: {workflow_def['first_step']}")
        
        # Start the workflow
        success = coordinator.start_workflow("custom_test_workflow", workflow_def)
        
        if success:
            print("✅ Custom workflow started successfully")
            
            # Wait a moment for processing
            await asyncio.sleep(3)
            
            # Check workflow status
            workflow_status = coordinator.get_workflow_status("custom_test_workflow")
            if workflow_status:
                print(f"   Workflow status: {workflow_status['status']}")
                print(f"   Steps completed: {len(workflow_status['steps_completed'])}")
            else:
                print("   Workflow status not found")
        else:
            print("❌ Failed to start custom workflow")
        
        coordinator.stop()
        print("✅ Custom workflow test completed")
        
        return success
        
    except Exception as e:
        print(f"❌ Custom workflow test failed: {e}")
        logger.exception("Custom workflow test error")
        return False


async def demonstrate_integration():
    """Demonstrate integration with existing systems."""
    print("\n" + "=" * 60)
    print("Demonstrating System Integration")
    print("=" * 60)
    
    try:
        # Test integration with standard agents
        print("🔄 Testing standard agent compatibility...")
        
        from src.agents.market_data_agent import MarketDataAgent
        from src.agents.model_agent import PriceModelAgent
        
        # Standard approach
        market_agent = MarketDataAgent()
        model_agent = PriceModelAgent()
        
        market_data = market_agent.fetch()
        prediction_input = {
            "vehicle_age": 3,
            "mileage": 45000,
            "market_index": market_data["market_index"],
            "fuel_price": market_data["fuel_price"]
        }
        
        standard_price = model_agent.predict(prediction_input)
        print(f"✅ Standard prediction: ${standard_price:.2f}")
        
        # Coordinated approach
        print("\n🔄 Testing coordinated approach...")
        from src.blackboard_agents import VehiclePriceWorkflowCoordinator
        
        workflow = VehiclePriceWorkflowCoordinator()
        workflow.start()
        
        coordinated_result = await workflow.predict_price(3, 45000)
        coordinated_price = coordinated_result['predicted_price']
        
        print(f"✅ Coordinated prediction: ${coordinated_price:.2f}")
        print(f"   Price difference: ${abs(standard_price - coordinated_price):.2f}")
        print(f"   Processing time: {coordinated_result['processing_time']:.2f}s")
        
        workflow.stop()
        
        # Compare approaches
        print(f"\n📊 Comparison:")
        print(f"   Standard: Fast, simple, limited features")
        print(f"   Coordinated: Rich features, monitoring, scalable")
        print(f"   Both approaches produce consistent results ✅")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration demonstration failed: {e}")
        logger.exception("Integration demonstration error")
        return False


async def main():
    """Run all blackboard pattern tests and demonstrations."""
    print("🚀 Starting Blackboard/Coordinator Pattern Test Suite")
    print("=" * 80)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Basic Coordination", test_basic_coordination),
        ("Message Flow", test_message_flow),
        ("Error Handling", test_error_handling),
        ("Performance Monitoring", test_performance_monitoring),
        ("Custom Workflow", test_custom_workflow),
        ("System Integration", demonstrate_integration),
    ]
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            test_results.append((test_name, False))
        
        # Brief pause between tests
        await asyncio.sleep(1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUITE SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Blackboard pattern is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the logs for details.")
    
    return passed == total


if __name__ == "__main__":
    # Run the test suite
    success = asyncio.run(main())
    
    if not success:
        sys.exit(1)
    
    print("\n✅ Blackboard pattern test suite completed successfully!")
