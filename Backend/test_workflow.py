#!/usr/bin/env python3
"""
Test script for the updated NewStock workflow with improved Phoenix tracing.
This script demonstrates the new tracing setup and tests the workflow.
"""

import os
import asyncio
import dotenv
from phoenix.otel import register
from openinference.instrumentation.llama_index import LlamaIndexInstrumentor
from llama_index.core.workflow import Workflow, step, Context, StartEvent, StopEvent

# Load environment variables
dotenv.load_dotenv()

OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
PHOENIX_PROJECT_NAME = os.getenv("PHOENIX_PROJECT_NAME")

# Register Phoenix tracer
tracer_provider = register(
    endpoint=OTEL_ENDPOINT,
    project_name=PHOENIX_PROJECT_NAME,
    auto_instrument=True
)

# Instrument LlamaIndex
LlamaIndexInstrumentor().instrument(tracer_provider=tracer_provider)

# Test workflow
class TestWorkflow(Workflow):
    @step
    async def test_step(self, ctx: Context, ev: StartEvent) -> StopEvent:
        """Test step to verify tracing is working"""
        print("Test workflow step executed")
        return StopEvent(result="Test workflow completed successfully")

async def test_workflow():
    """Test the workflow with tracing"""
    print("Starting test workflow with Phoenix tracing...")
    
    workflow = TestWorkflow()
    result = await workflow.run()
    
    print(f"Workflow result: {result}")
    print("Test completed!")

async def test_newstock_workflow():
    """Test the actual NewStock workflow"""
    print("Testing NewStock workflow...")
    
    # Import the actual workflow
    from app.workflows.NewStock_workflow import run_new_stock_workflow
    
    # Test with a simple company query
    test_query = "Test Company"
    test_user_id = "test_user_123"
    test_message_id = "test_msg_456"
    
    try:
        handler = await run_new_stock_workflow(test_query, test_user_id, test_message_id)
        result = await handler
        
        print(f"NewStock workflow result: {result}")
        print("NewStock workflow test completed!")
        
    except Exception as e:
        print(f"Error testing NewStock workflow: {e}")

async def test_workflow_import():
    """Test importing the workflow module to verify tracing setup"""
    print("Testing workflow import and tracing setup...")
    
    try:
        # Import the workflow module to trigger tracing setup
        from app.workflows.NewStock_workflow import NewStockWorkflow
        print("✓ NewStockWorkflow imported successfully")
        print("✓ Tracing setup completed during import")
        
    except Exception as e:
        print(f"✗ Error importing workflow: {e}")

async def main():
    """Main test function"""
    print("=== Phoenix Tracing Test Suite ===")
    print(f"OTEL Endpoint: {OTEL_ENDPOINT}")
    print(f"Phoenix Project: {PHOENIX_PROJECT_NAME}")
    print()
    
    # Test workflow import and tracing setup
    await test_workflow_import()
    print()
    
    # Test basic workflow
    await test_workflow()
    print()
    
    # Test NewStock workflow (commented out to avoid API calls in test)
    # await test_newstock_workflow()

if __name__ == "__main__":
    asyncio.run(main())
